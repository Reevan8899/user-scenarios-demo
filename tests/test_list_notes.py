"""Проверки SC-002, FR-002 и UR-002."""

import pytest

from src.domain.exceptions import StorageError
from src.domain.note import Note
from src.scenarios.list_notes import list_notes


def test_list_empty_storage(storage):
    assert list_notes(storage) == []


def test_list_sorts_by_creation_instant_without_rewriting_storage(storage):
    old = Note("old", "Старая", "A", "2026-11-08T13:30:00", "2026-11-08T18:30:00")
    new = Note("new", "Новая", "Б", "2026-11-08T15:00:00+01:00", "2026-11-08T15:00:00+01:00")
    storage.save_all([old, new])
    assert list_notes(storage) == [new, old]
    assert storage.load_all() == [old, new]


def test_list_reports_storage_error(storage):
    storage.path.write_text("{}", encoding="utf-8")
    with pytest.raises(StorageError, match="Не удалось прочитать"):
        list_notes(storage)
