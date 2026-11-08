"""Проверки SC-004, FR-004, UR-004 и NFR-002."""

import pytest

from src.domain.exceptions import NoteNotFoundError, StorageError, ValidationError
from src.domain.note import Note
from src.scenarios.edit_note import edit_note


@pytest.fixture
def original(storage):
    note = Note("target", "Тема", "Текст", "2020-01-01T00:00:00+00:00", "2020-01-01T00:00:00+00:00")
    storage.save_all([note])
    return note


@pytest.mark.parametrize("fields", [{"title": "Новая"}, {"body": "Новый"}, {"title": "Новая", "body": "Новый"}])
def test_edit_changes_only_supplied_fields(storage, original, fields):
    updated = edit_note(original.id, storage, **fields)
    assert (updated.id, updated.created_at) == (original.id, original.created_at)
    assert updated.updated_at > original.updated_at
    assert updated.title == fields.get("title", original.title)
    assert updated.body == fields.get("body", original.body)
    assert storage.load_all() == [updated]


def test_edit_without_values_preserves_timestamp(storage, original):
    assert edit_note(original.id, storage) == original
    assert storage.load_all() == [original]


def test_edit_rejects_unknown_id(storage):
    with pytest.raises(NoteNotFoundError, match="не найдена"):
        edit_note("missing", storage, title="Новая")


def test_edit_rejects_invalid_input_without_saving(storage, original):
    with pytest.raises(ValidationError, match="Тело заметки обязательно"):
        edit_note(original.id, storage, title="Новая", body=" ")
    assert storage.load_all() == [original]


def test_failed_edit_preserves_previous_file(storage, original, failed_replace):
    failed_replace()
    with pytest.raises(StorageError, match="Не удалось сохранить"):
        edit_note(original.id, storage, title="Новая")
    assert storage.load_all() == [original]
