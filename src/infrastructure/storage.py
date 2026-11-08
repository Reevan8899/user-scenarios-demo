"""Совместимое с практической № 5 JSON-хранилище с атомарной записью."""

import json
import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

from filelock import FileLock, Timeout

from src.domain.exceptions import StorageError
from src.domain.note import Note, find_index, parse_date


class NoteStorage:
    def __init__(self, path: str | Path = "~/.notes.json") -> None:
        self.path = Path(path).expanduser().resolve()
        self._lock = FileLock(self.path.with_name(f"{self.path.name}.lock"), timeout=2, mode=0o600)

    def load_all(self) -> list[Note]:
        try:
            with self.path.open(encoding="utf-8") as stream:
                records = json.load(stream)
            if not isinstance(records, list):
                raise ValueError("Expected a list of notes")
            notes = []
            for record in records:
                if not isinstance(record, dict) or not all(isinstance(value, str) for value in record.values()):
                    raise ValueError("Expected a record with string fields")
                note = Note(**record)
                parse_date(note.created_at)
                parse_date(note.updated_at)
                notes.append(note)
            return notes
        except FileNotFoundError:
            return []
        except (OSError, TypeError, ValueError) as error:
            raise StorageError("Не удалось прочитать заметки. Проверьте формат JSON и права доступа.") from error

    def get(self, note_id: str) -> Note:
        notes = self.load_all()
        return notes[find_index(notes, note_id)]

    def _replace_file(self, notes: list[Note]) -> None:
        fd, temporary_name = tempfile.mkstemp(dir=self.path.parent, prefix=".notes-", suffix=".tmp")
        temporary = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump([asdict(note) for note in notes], stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)

    @contextmanager
    def _write_access(self) -> Iterator[None]:
        try:
            with self._lock:
                yield
        except Timeout as error:
            raise StorageError("Хранилище занято. Повторите команду позже.") from error
        except OSError as error:
            raise StorageError("Не удалось сохранить заметки. Проверьте права доступа и свободное место.") from error

    def save_all(self, notes: list[Note]) -> None:
        with self._write_access():
            self._replace_file(notes)

    @contextmanager
    def transaction(self) -> Iterator[list[Note]]:
        """Под одной блокировкой читает и сохраняет данные при успехе."""
        with self._write_access():
            notes = self.load_all()
            yield notes
            self._replace_file(notes)
