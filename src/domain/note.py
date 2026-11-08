"""Доменная сущность заметки."""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .exceptions import NoteNotFoundError


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_date(value: str) -> datetime:
    instant = datetime.fromisoformat(value.removesuffix("Z") + "+00:00" if value.endswith("Z") else value)
    return instant if instant.tzinfo is not None else instant.replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class Note:
    id: str
    title: str
    body: str
    created_at: str
    updated_at: str

    @classmethod
    def create(cls, title: str, body: str) -> "Note":
        now = utc_now()
        return cls(uuid4().hex, title, body, now, now)


def find_index(notes: list[Note], note_id: str) -> int:
    for index, note in enumerate(notes):
        if note.id == note_id:
            return index
    raise NoteNotFoundError(f"Заметка с ID {note_id} не найдена. Проверьте ID командой note list.")
