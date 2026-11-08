"""SC-004: Редактирование заметки. Реализует FR-004 и UR-004."""

from src.domain.note import Note
from src.infrastructure.storage import NoteStorage


def edit_note(note_id: str, storage: NoteStorage, title: str | None = None, body: str | None = None) -> Note:
    # TODO: Найти запись, проверить переданные поля, обновить дату и сохранить.
    raise NotImplementedError("Сценарий SC-004 ещё не реализован")
