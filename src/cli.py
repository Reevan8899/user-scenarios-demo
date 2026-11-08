"""Интерактивные команды для пользовательских сценариев SC-001–SC-005."""

import argparse
import os
import sys

from src.domain.exceptions import DomainError, ValidationError
from src.domain.note import Note
from src.infrastructure.storage import NoteStorage
from src.scenarios.add_note import add_note, validate_title
from src.scenarios.delete_note import delete_note
from src.scenarios.edit_note import edit_note
from src.scenarios.list_notes import list_notes
from src.scenarios.search_notes import search_notes


class NoteParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValidationError("Неверная команда или параметры. Выполните note --help.")


def _parser() -> NoteParser:
    parser = NoteParser(prog="note", description="Консольный менеджер заметок.")
    commands = parser.add_subparsers(dest="command", required=True, title="команды")
    add = commands.add_parser("add", help="Добавить заметку")
    add.add_argument("--title", help="Заголовок")
    add.add_argument("--body", help="Текст заметки")
    commands.add_parser("list", help="Показать все заметки")
    search = commands.add_parser("search", help="Найти заметки")
    search.add_argument("--query", required=True, help="Подстрока для поиска")
    edit = commands.add_parser("edit", help="Изменить заметку")
    edit.add_argument("id", help="ID заметки")
    edit.add_argument("--title", help="Новый заголовок")
    edit.add_argument("--body", help="Новый текст")
    delete = commands.add_parser("delete", help="Удалить заметку с подтверждением")
    delete.add_argument("id", help="ID заметки")
    return parser


def _ask_title() -> str:
    while True:
        try:
            return validate_title(input("Заголовок: "))
        except ValidationError as error:
            print(f"Ошибка: {error}", file=sys.stderr)


def _print_notes(notes: list[Note], empty_message: str) -> None:
    if not notes:
        print(empty_message)
        return
    print("ID | Заголовок | Дата создания")
    for note in notes:
        print(f"{note.id} | {note.title} | {note.created_at}")


def _edit(args: argparse.Namespace, storage: NoteStorage) -> None:
    title, body = args.title, args.body
    if title is None and body is None:
        storage.get(args.id)
        title = input("Новый заголовок (Enter для пропуска): ") or None
        body = input("Новый текст (Enter для пропуска): ") or None
    note = edit_note(args.id, storage, title=title, body=body)
    if title is None and body is None:
        print("Изменения не внесены.")
    else:
        print(f"Заметка обновлена. ID: {note.id}")


def _delete(note_id: str, storage: NoteStorage) -> None:
    note = storage.get(note_id)
    if input(f"Удалить «{note.title}»? Введите «да»: ").strip().casefold() != "да":
        print("Удаление отменено.")
        return
    delete_note(note_id, storage)
    print(f"Заметка удалена. ID: {note_id}")


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        storage = NoteStorage(os.environ.get("NOTE_STORAGE", "~/.notes.json"))
        match args.command:
            case "add":
                title = _ask_title() if args.title is None else validate_title(args.title)
                body = input("Текст: ") if args.body is None else args.body
                note = add_note(title, body, storage)
                print(f"Заметка создана. ID: {note.id}")
            case "list":
                _print_notes(list_notes(storage), "Заметок пока нет.")
            case "search":
                _print_notes(search_notes(args.query, storage), "Ничего не найдено.")
            case "edit":
                _edit(args, storage)
            case "delete":
                _delete(args.id, storage)
    except DomainError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    except EOFError:
        print("Операция отменена.")
    except KeyboardInterrupt:
        print("\nОперация отменена.")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
