"""SC-005: Удаление заметки. Реализует FR-005 и UR-005."""

from src.domain.note import find_index
from src.infrastructure.storage import NoteStorage


def delete_note(note_id: str, storage: NoteStorage) -> None:
    """Удаляет одну запись по ID после подтверждения на уровне CLI."""
    with storage.transaction() as notes:
        del notes[find_index(notes, note_id)]
