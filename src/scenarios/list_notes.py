"""SC-002: Просмотр списка заметок. Реализует FR-002 и UR-002."""

from src.domain.note import Note, parse_date
from src.infrastructure.storage import NoteStorage


def list_notes(storage: NoteStorage) -> list[Note]:
    """Возвращает снимок списка от новых записей к старым."""
    return sorted(storage.load_all(), key=lambda note: parse_date(note.created_at), reverse=True)
