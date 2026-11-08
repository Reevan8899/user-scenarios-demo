"""SC-001: Добавление заметки. Реализует FR-001 и UR-001."""

from src.domain.note import Note
from src.infrastructure.storage import NoteStorage

TITLE_MAX = 100
BODY_MAX = 10_000


def validate_title(title: str) -> str:
    # TODO: нормализовать заголовок и проверить границы длины.
    raise NotImplementedError("Валидация заголовка не реализована")


def validate_body(body: str) -> str:
    # TODO: нормализовать тело и проверить границы длины.
    raise NotImplementedError("Валидация текста не реализована")


def add_note(title: str, body: str, storage: NoteStorage) -> Note:
    # TODO: Проверить заголовок и тело, создать Note и сохранить под блокировкой.
    raise NotImplementedError("Сценарий SC-001 ещё не реализован")
