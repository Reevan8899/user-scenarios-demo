"""Проверяет связь описаний SC с docstring модулей и тестов."""

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADING = re.compile(r"^## (SC-[0-9]{3})[ \t]*$", re.MULTILINE)
MODULE = re.compile(r"^\*\*Модуль\*\* — \[`(src/scenarios/[a-z_]+\.py)`\]\(\.\./\1\)[ \t]*$", re.MULTILINE)
TEST = re.compile(r"^\*\*Тесты\*\* — \[`(tests/test_[a-z_]+\.py)`\]\(\.\./\1\)[ \t]*$", re.MULTILINE)


def check_docstring(relative_path: str, scenario: str) -> str | None:
    path = ROOT / relative_path
    if not path.is_file():
        return f"{scenario}: отсутствует файл {relative_path}"
    try:
        syntax = ast.parse(path.read_text(encoding="utf-8"), filename=relative_path)
    except (SyntaxError, UnicodeError) as error:
        return f"{scenario}: не удалось прочитать {relative_path}: {error}"
    if not re.search(rf"\b{scenario}\b", ast.get_docstring(syntax) or ""):
        return f"{scenario}: в docstring файла {relative_path} нет ID сценария"
    return None


def main() -> int:
    text = (ROOT / "docs" / "scenarios.md").read_text(encoding="utf-8")
    headings = list(HEADING.finditer(text))
    if not headings:
        print("В docs/scenarios.md нет заголовков сценариев.")
        return 1

    seen_ids = set()
    seen_modules = set()
    problems = []
    for index, heading in enumerate(headings):
        scenario = heading[1]
        if scenario in seen_ids:
            problems.append(f"{scenario}: дублирующийся ID")
        seen_ids.add(scenario)
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[heading.end():end]
        module = MODULE.search(section)
        if not module:
            problems.append(f"{scenario}: отсутствует ссылка на модуль сценария")
            continue

        if module[1] in seen_modules:
            problems.append(f"{scenario}: модуль {module[1]} уже назначен другому сценарию")
        seen_modules.add(module[1])
        expected_test = f"tests/test_{Path(module[1]).stem}.py"
        test = TEST.search(section)
        if not test or test[1] != expected_test:
            problems.append(f"{scenario}: укажите ссылку на {expected_test}")
        for relative_path in (module[1], expected_test):
            if problem := check_docstring(relative_path, scenario):
                problems.append(problem)

    if problems:
        print("\n".join(problems))
        return 1
    print(f"Проверено сценариев: {len(seen_ids)}. Для каждого найдены модуль, тестовый файл и ID в docstring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
