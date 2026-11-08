"""SC-001: Добавление заметки. Реализует FR-001, UR-001 и NFR-004."""

from src.domain.exceptions import ValidationError
from src.domain.note import Note
from src.infrastructure.storage import NoteStorage

TITLE_MAX = 100
BODY_MAX = 10_000


def _validate(text: str, maximum: int, required: str, too_long: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValidationError(required)
    if len(cleaned) > maximum:
        raise ValidationError(too_long)
    return cleaned


def validate_title(title: str) -> str:
    return _validate(title, TITLE_MAX, "Заголовок обязателен.", f"Заголовок слишком длинный. Максимум {TITLE_MAX} символов.")


def validate_body(body: str) -> str:
    return _validate(body, BODY_MAX, "Тело заметки обязательно.", f"Тело заметки слишком длинное. Максимум {BODY_MAX} символов.")


def add_note(title: str, body: str, storage: NoteStorage) -> Note:
    """Проверяет поля, создаёт заметку и сохраняет её атомарно."""
    note = Note.create(validate_title(title), validate_body(body))
    with storage.transaction() as notes:
        notes.append(note)
    return note
