"""SC-002: Просмотр списка заметок. Реализует FR-002 и UR-002."""

from src.domain.note import Note
from src.infrastructure.storage import NoteStorage


def list_notes(storage: NoteStorage) -> list[Note]:
    # TODO: Загрузить заметки, отсортировать по дате создания от новых к старым.
    raise NotImplementedError("Сценарий SC-002 ещё не реализован")
