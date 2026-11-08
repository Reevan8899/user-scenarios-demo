"""SC-005: Удаление заметки. Реализует FR-005 и UR-005."""

from src.infrastructure.storage import NoteStorage


def delete_note(note_id: str, storage: NoteStorage) -> None:
    # TODO: Найти заметку по ID, удалить и атомарно сохранить оставшиеся записи.
    raise NotImplementedError("Сценарий SC-005 ещё не реализован")
