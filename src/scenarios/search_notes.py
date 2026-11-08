"""SC-003: Поиск заметок. Реализует FR-003 и UR-003."""

from src.domain.note import Note
from src.infrastructure.storage import NoteStorage


def search_notes(query: str, storage: NoteStorage) -> list[Note]:
    # TODO: Проверить запрос, отобрать совпадения в заголовке и тексте.
    raise NotImplementedError("Сценарий SC-003 ещё не реализован")
