"""SC-003: Поиск заметок. Реализует FR-003 и UR-003."""

from src.domain.exceptions import ValidationError
from src.domain.note import Note
from src.infrastructure.storage import NoteStorage


def search_notes(query: str, storage: NoteStorage) -> list[Note]:
    """Находит подстроку в заголовке или тексте без учёта регистра."""
    needle = query.strip().casefold()
    if not needle:
        raise ValidationError("Поисковый запрос пуст. Укажите слово через --query.")
    return [note for note in storage.load_all() if needle in note.title.casefold() or needle in note.body.casefold()]
