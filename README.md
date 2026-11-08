# User Scenarios Demo

[![Scenario tests](https://github.com/Reevan8899/user-scenarios-demo/actions/workflows/test.yml/badge.svg?branch=main&event=push)](https://github.com/Reevan8899/user-scenarios-demo/actions/workflows/test.yml)

Учебный консольный менеджер заметок для практической работы № 6. У каждой пользовательской цели есть сценарий, модуль, задача и тесты.

- [Пять пользовательских сценариев](docs/scenarios.md)
- [Матрица трассируемости](docs/traceability.md)
- [Задачи по сценариям](https://github.com/Reevan8899/user-scenarios-demo/issues?q=label%3Ascenario)

## Установка и запуск

Нужен Python 3.10 или новее. Из корня репозитория в активном виртуальном окружении выполните `python -m pip install -e .`.

```sh
note --help
note add --title "План" --body "Купить билеты"
note list
note search --query "БИЛЕТЫ"
note edit ID --body "Забронировать билеты"
note delete ID
```

Подставьте ID из вывода `note list`. Команды `note add` и `note edit ID` без флагов запрашивают поля. `note delete ID` удаляет заметку после ответа «да». По умолчанию данные хранятся в `~/.notes.json`. Для отдельного файла задайте переменную `NOTE_STORAGE`.

## Проверка

```sh
python -m pip install -r requirements.txt
python -m pytest -v --cov=src.scenarios --cov-report=term-missing
python scripts/check_scenarios.py
```

CI запускает тесты на `push` и `pull_request`, выводит покрытие по модулям и проверяет, что ссылки из документации ведут к модулю и тестовому файлу с тем же ID сценария.
