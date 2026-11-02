# Implementation Plan: Сортировка задач (backend)

**Branch**: `001-tasks-sort-back` | **Date**: 2026-11-01 | **Spec**: specs/001-tasks-sort-back/spec.md

**Input**: Feature specification from `/specs/001-tasks-sort-back/spec.md`

## Summary

Расширить метод `Storage.list_tasks()` параметрами `sort_by` и `sort_order` для сортировки задач по одному из пяти полей: title, status, due_date, created_at, tags. Сортировка применяется после фильтрации, не изменяет `tasks.json`, стабильна при равных ключах. Реализация через `sorted()` с key-функцией, без новых зависимостей.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Typer (CLI), pytest (тесты), Tkinter (GUI), стандартная библиотека

**Storage**: JSON-файл `tasks.json` в корне репозитория, формат `{ "version": 1, "tasks": [...] }`

**Testing**: pytest, фикстуры с `tmp_path`

**Target Platform**: Локальный десктоп (Linux/macOS), оффлайн

**Project Type**: Desktop app + CLI (TaskHub)

**Performance Goals**: Сортировка 1000 задач — менее 1 секунды

**Constraints**: Оффлайн, без сетевых вызовов, без новых зависимостей, линии кода до 100 символов

**Scale/Scope**: Локальное хранилище, до сотен задач

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Stable Data Contract and Durable Writes

- [x] `tasks.json` имеет форму `{ "version": 1, "tasks": [...] }` — не изменяется
- [x] Сортировка не добавляет поля в Task — только читает существующие
- [x] Запись идет через `save_tasks()` → `_write()` → атомарная замена
- [x] Undo не затронут — сортировка read-only

### II. Shared Core and Thin Interfaces

- [x] Сортировка реализуется в `storage.py` (shared core)
- [x] GUI делегирует через `controller.list_tasks()` — не реализует сортировку самостоятельно
- [x] CLI не получает параметры сортировки — контракты не изменяются

### III. Test-First Development (NON-NEGOTIABLE)

- [x] Тесты добавлены в `tests/test_storage.py`
- [x] Используются временные хранилища (`tmp_path`)
- [x] Покрываются: основные сценарии, граничные случаи, ошибка валидации

### IV. Contract and End-to-End Verification

- [x] Контракт `list_tasks()` задекларирован в `contracts/list_tasks.md`
- [x] CLI-вывод не изменяется (формат `<id> [status] title (due=... tags=...)`)
- [x] Ошибки CLI дают ненулевой код выхода

### V. Local Simplicity and Controlled Scope

- [x] Без сетевых вызовов, MCP, плагинов
- [x] Без новых зависимостей
- [x] Изменения только в `practices/practice_04/`
- [x] Минимальные правки: добавление параметров в существующий метод

## Project Structure

### Documentation (this feature)

```text
specs/001-tasks-sort-back/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── list_tasks.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/taskhub/
├── app.py               # CLI (Typer): init/add/list/done/edit/undo
├── gui.py               # Desktop UI (Tkinter/ttk) поверх модели и Storage
├── storage.py           # JSON-хранилище задач (tasks.json) + история/undo
├── models.py            # Модель Task и сериализация
└── validate.py          # Валидация данных

tests/
├── conftest.py          # sys.path для src/
├── test_storage.py      # unit-тесты хранилища (сортировка)
├── test_cli_basic.py    # базовые CLI-тесты (init/add/list/undo)
└── test_edit.py         # CLI-тесты команды edit (+ undo)
```

**Structure Decision**: Используется существующая структура проекта. Изменения только в `src/taskhub/storage.py` ( добавление параметров и логики сортировки) и `tests/test_storage.py` (тесты для сортировки).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Нет | — | — |

Все валидации конституции пройдены без нарушений. Фича read-only, не изменяет данные, не добавляет зависимостей, не меняет контракты CLI.
