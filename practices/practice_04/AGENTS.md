# Среда агента

Проект на ранней стадии (сырой). Ниже — операционные инструкции для агента: где искать код, какие файлы править и какие команды запускать. Подключения к внешним источникам и автоматизации будут добавлены позже.

Структура проекта

```
practices/practice_04/
├── AGENTS.md                 # Правила работы агента (этот файл)
├── opencode.json             # Конфигурация агента и раннера
├── pyproject.toml            # Зависимости (runtime/dev), pytest конфиг
├── README.md                 # Краткий гайд по проекту
├── PROJECT_README.md         # Описание варианта и план фич
├── reflection.md             # Рефлексия (домашка)
├── .gitignore
├── src/
│   └── taskhub/
│       ├── app.py           # CLI (Typer): init/add/list/done
│       ├── storage.py       # JSON-хранилище задач (tasks.json)
│       ├── models.py        # Модель Task и сериализация
│       
└── tests/
    ├── conftest.py          # sys.path для src/
    ├── test_storage.py      # unit-тесты хранилища
    ├── test_cli_basic.py    # базовые CLI-тесты
```

Входные точки (правьте здесь)
- src/taskhub/app.py — CLI.
- src/taskhub/storage.py — операции с JSON-хранилищем (tasks.json).
- src/taskhub/models.py — модель Task, сериализация.
- tests/** — авто‑проверки (pytest).

Поиск кода (glob/grep)
- Glob: practices/practice_04/src/**/*.py
- Glob: practices/practice_04/tests/**/*.py

Команды запуска
- Тесты: `pytest -q` (из корня репозитория)
- CLI локально:
  - `export PYTHONPATH=practices/practice_04/src`
  - `python -m taskhub.app init`
  - `python -m taskhub.app add "Title" --tag demo`
  - `python -m taskhub.app list`

Шаги и проверки: Фича A (Web Clip To Task)
1. Извлечь title страницы через Playwright MCP (navigate + document.title). При ошибке — остановиться.
2. Сформировать строку: "<title> (<url>)".
3. Добавить задачу через CLI:
   - export PYTHONPATH=practices/practice_04/src
   - python -m taskhub.app clip --url <url> --title "<title>"
4. Проверка: `pytest -q` зелёный; `list` содержит "<title> (<url>)".

Шаги и проверки: Фича B (валидация и линт)
1. Добавить команду `task validate`, проверяющую целостность `tasks.json` (схема, даты, дубли id).
2. Позже добавить автоматизации (например, pre-commit), чтобы запускать форматирование, тесты и `task validate`.
3. Проверка: `pytest -q` зелёный; `task validate` печатает `validation: ok` при успехе и ненулевой код выхода при ошибке.

Политики
- Не вносить изменения вне `practices/practice_04/` без явных указаний.
- Не добавлять внешние зависимости без согласования.
- Сохранять минимальные и точечные правки; при добавлении команд — покрывать тестами.

Ожидаемый вывод (stdout)
- import-gsheet: печатает число импортированных задач, например `1`.
- list: вывод формата `<id> [status] title (due=... tags=...)`.
- validate: `validation: ok` при успехе; при ошибке — список нарушений.

Что делает агент
1. Читает AGENTS.md и настраивает окружение проекта.
2. После правок запускает `pytest -q` и возвращает отчёт.
3. Выполняет команды CLI и проверяет ожидаемый вывод.

Примечания
- Конкретные подключения и автоматизации будут добавлены после реализации фич.
