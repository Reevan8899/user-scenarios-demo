"""Проверки SC-005, FR-005, UR-005 и NFR-002."""

import pytest

from src.domain.exceptions import NoteNotFoundError, StorageError
from src.scenarios.add_note import add_note
from src.scenarios.delete_note import delete_note


def test_delete_removes_only_selected_note(storage):
    first = add_note("Первая", "Текст", storage)
    second = add_note("Вторая", "Текст", storage)
    delete_note(first.id, storage)
    assert storage.load_all() == [second]


def test_delete_unknown_id_does_not_change_data(storage):
    first = add_note("Первая", "Текст", storage)
    with pytest.raises(NoteNotFoundError, match="не найдена"):
        delete_note("missing", storage)
    assert storage.load_all() == [first]


def test_failed_delete_keeps_note(storage, failed_replace):
    note = add_note("Первая", "Текст", storage)
    failed_replace()
    with pytest.raises(StorageError, match="Не удалось сохранить"):
        delete_note(note.id, storage)
    assert storage.load_all() == [note]
