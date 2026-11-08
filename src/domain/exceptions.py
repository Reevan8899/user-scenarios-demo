class DomainError(Exception):
    """Ошибка приложения, которую можно показать пользователю."""


class ValidationError(DomainError, ValueError):
    """Введённые данные не удовлетворяют правилам сценария."""


class NoteNotFoundError(DomainError):
    """В хранилище нет заметки с указанным ID."""


class StorageError(DomainError):
    """Хранилище недоступно или имеет неверный формат."""
