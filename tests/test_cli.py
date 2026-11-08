"""Интеграционные проверки команд SC-001–SC-005 в отдельных процессах."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def run_cli(tmp_path):
    path = tmp_path / "notes.json"
    env = dict(os.environ, NOTE_STORAGE=str(path), PYTHONIOENCODING="utf-8")

    def run(*args, answers="", expect=0):
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", *args], cwd=ROOT, env=env,
            input=answers, encoding="utf-8", capture_output=True, timeout=10,
        )
        assert result.returncode == expect, (result.stdout, result.stderr)
        return result

    return run, path


def test_cli_note_lifecycle(run_cli):
    run, path = run_cli
    assert "Заметок пока нет" in run("list").stdout
    created = run("add", "--title", "Задача", "--body", "В понедельник")
    note_id = created.stdout.strip().split()[-1]
    assert note_id in run("list").stdout
    assert note_id in run("search", "--query", "ПОНЕДЕЛЬ").stdout
    assert "Заметка обновлена" in run("edit", note_id, "--title", "Новая задача").stdout
    assert "Новая задача" in run("list").stdout
    assert "Удаление отменено" in run("delete", note_id, answers="нет\n").stdout
    assert note_id in run("list").stdout
    assert "Заметка удалена" in run("delete", note_id, answers="да\n").stdout
    assert "Заметок пока нет" in run("list").stdout
    assert json.loads(path.read_text(encoding="utf-8")) == []


def test_cli_interactive_add_retries_empty_title(run_cli):
    run, path = run_cli
    result = run("add", answers="\n Тема \n Текст \n")
    assert result.stdout.count("Заголовок:") == 2
    assert "Заголовок обязателен" in result.stderr
    note, = json.loads(path.read_text(encoding="utf-8"))
    assert (note["title"], note["body"]) == ("Тема", "Текст")


def test_cli_interactive_edit_enter_skips_fields(run_cli):
    run, path = run_cli
    run("add", "--title", "Тема", "--body", "Текст")
    original, = json.loads(path.read_text(encoding="utf-8"))
    assert "Изменения не внесены" in run("edit", original["id"], answers="\n\n").stdout
    assert json.loads(path.read_text(encoding="utf-8")) == [original]
    run("edit", original["id"], answers="\nНовый текст\n")
    updated, = json.loads(path.read_text(encoding="utf-8"))
    assert updated["title"] == original["title"] and updated["body"] == "Новый текст"


def test_cli_eof_cancels_input_and_delete(run_cli):
    run, path = run_cli
    assert "Операция отменена" in run("add").stdout
    assert not path.exists()
    created = run("add", "--title", "Тема", "--body", "Текст")
    note_id = created.stdout.strip().split()[-1]
    assert "Операция отменена" in run("delete", note_id).stdout
    assert note_id in run("list").stdout


@pytest.mark.parametrize("command", ["edit", "delete"])
def test_cli_unknown_id_is_reported_before_prompt(run_cli, command):
    run, _ = run_cli
    result = run(command, "unknown", expect=2)
    assert "не найдена" in result.stderr and result.stdout == ""


def test_cli_validation_and_no_results(run_cli):
    run, path = run_cli
    assert "Тело заметки обязательно" in run("add", "--title", "Тема", "--body", "", expect=2).stderr
    assert not path.exists()
    assert "запрос пуст" in run("search", "--query", " ", expect=2).stderr
    assert "Ничего не найдено" in run("search", "--query", "слово").stdout


def test_cli_syntax_and_storage_errors_are_localized(run_cli):
    run, path = run_cli
    assert "Консольный менеджер заметок" in run("--help").stdout
    assert "Выполните note --help" in run("search", expect=2).stderr
    path.write_text("[broken", encoding="utf-8")
    assert "Проверьте формат JSON" in run("list", expect=2).stderr
