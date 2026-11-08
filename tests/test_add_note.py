"""Проверки SC-001, FR-001, UR-001, NFR-002 и NFR-004."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from uuid import UUID

import pytest

from src.domain.exceptions import StorageError, ValidationError
from src.infrastructure.storage import NoteStorage
from src.scenarios.add_note import BODY_MAX, TITLE_MAX, add_note, validate_body, validate_title


def test_validate_title_normalizes():
    assert validate_title("  План  ") == "План"


def test_validate_title_empty():
    with pytest.raises(ValidationError, match="Заголовок обязателен"):
        validate_title("")


def test_validate_title_whitespace_only():
    with pytest.raises(ValidationError, match="Заголовок обязателен"):
        validate_title(" \t ")


def test_validate_title_too_long():
    with pytest.raises(ValidationError, match="Максимум 100"):
        validate_title("я" * (TITLE_MAX + 1))


def test_validate_title_inclusive_limit():
    title = "я" * TITLE_MAX
    assert validate_title(f" {title} ") == title


def test_validate_body_normalizes():
    assert validate_body("\n Текст \n") == "Текст"


def test_validate_body_empty():
    with pytest.raises(ValidationError, match="Тело заметки обязательно"):
        validate_body("")


def test_validate_body_whitespace_only():
    with pytest.raises(ValidationError, match="Тело заметки обязательно"):
        validate_body(" \n ")


def test_validate_body_too_long():
    with pytest.raises(ValidationError, match="Максимум 10000"):
        validate_body("я" * (BODY_MAX + 1))


def test_validate_body_inclusive_limit():
    body = "я" * BODY_MAX
    assert validate_body(f" {body} ") == body


def test_add_note_returns_uuid_and_dates(storage):
    note = add_note("Тема", "Текст", storage)
    assert UUID(note.id).hex == note.id
    assert datetime.fromisoformat(note.created_at).tzinfo is not None
    assert note.updated_at == note.created_at


def test_add_note_persists_for_another_instance(storage):
    note = add_note("Тема", "Текст", storage)
    assert NoteStorage(storage.path).load_all() == [note]


def test_add_note_preserves_earlier_notes(storage):
    first = add_note("Первая", "Текст", storage)
    second = add_note("Вторая", "Текст", storage)
    assert storage.load_all() == [first, second]
    assert first.id != second.id


def test_add_note_returns_normalized_fields(storage):
    note = add_note(" Тема ", " Текст ", storage)
    assert (note.title, note.body) == ("Тема", "Текст")


def test_invalid_input_keeps_existing_data(storage):
    previous = add_note("Тема", "Текст", storage)
    with pytest.raises(ValidationError):
        add_note("Новая", " ", storage)
    assert storage.load_all() == [previous]


def test_storage_failure_leaves_previous_file(storage, failed_replace):
    previous = add_note("Тема", "Текст", storage)
    failed_replace()
    with pytest.raises(StorageError, match="Не удалось сохранить"):
        add_note("Новая", "Текст", storage)
    assert storage.load_all() == [previous]
    assert list(storage.path.parent.glob(".notes-*.tmp")) == []


def test_corrupt_json_is_not_overwritten(storage):
    storage.path.write_text("[broken", encoding="utf-8")
    with pytest.raises(StorageError, match="Не удалось прочитать"):
        add_note("Тема", "Текст", storage)
    assert storage.path.read_text(encoding="utf-8") == "[broken"


def test_concurrent_creates_preserve_every_note(storage):
    def create(index):
        return add_note(str(index), "Текст", NoteStorage(storage.path)).id

    with ThreadPoolExecutor(max_workers=3) as pool:
        ids = set(pool.map(create, range(6)))
    assert len(ids) == 6
    assert {note.id for note in storage.load_all()} == ids
