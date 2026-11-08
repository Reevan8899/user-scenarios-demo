"""Проверки SC-003, FR-003 и UR-003."""

import pytest

from src.domain.exceptions import StorageError, ValidationError
from src.scenarios.add_note import add_note
from src.scenarios.search_notes import search_notes


def test_search_finds_matches_in_title_and_body(storage):
    first = add_note("План поездки", "Билеты", storage)
    second = add_note("Билеты", "Подтвердить план", storage)
    add_note("Список", "Книги", storage)
    assert search_notes(" ПЛАн ", storage) == [first, second]


def test_search_returns_empty_for_no_matches(storage):
    add_note("Тема", "Текст", storage)
    assert search_notes("облако", storage) == []


@pytest.mark.parametrize("query", ["", " \t"])
def test_search_rejects_empty_query(storage, query):
    with pytest.raises(ValidationError, match="запрос пуст"):
        search_notes(query, storage)


def test_search_reports_storage_error(storage):
    storage.path.write_text("{}", encoding="utf-8")
    with pytest.raises(StorageError, match="Не удалось прочитать"):
        search_notes("план", storage)
