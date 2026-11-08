"""SC-004: Редактирование заметки. Реализует FR-004 и UR-004."""

from dataclasses import replace

from src.domain.note import Note, find_index, utc_now
from src.infrastructure.storage import NoteStorage
from src.scenarios.add_note import validate_body, validate_title


def edit_note(
    note_id: str,
    storage: NoteStorage,
    title: str | None = None,
    body: str | None = None,
) -> Note:
    """Обновляет переданные поля и дату, сохраняя ID и дату создания."""
    if title is None and body is None:
        return storage.get(note_id)

    with storage.transaction() as notes:
        index = find_index(notes, note_id)
        original = notes[index]
        updated = replace(
            original,
            title=original.title if title is None else validate_title(title),
            body=original.body if body is None else validate_body(body),
            updated_at=utc_now(),
        )
        notes[index] = updated
    return updated
