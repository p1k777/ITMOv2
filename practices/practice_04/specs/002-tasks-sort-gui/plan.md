# Implementation Plan: Сортировка задач в GUI TaskHub

**Branch**: `002-tasks-sort-gui` | **Date**: 2026-11-01 | **Spec**: `specs/002-tasks-sort-gui/spec.md`

**Input**: Feature specification from `specs/002-tasks-sort-gui/spec.md`

## Summary

Добавить сортировку задач в Tkinter/ttk GUI по клику на заголовках колонок таблицы. Заголовки кликабельны (cursor="hand2"), визуальный индикатор направления сортировки (▲ asc / ▼ desc) в тексте заголовка, циклическое переключение asc → desc → без сортировки. GUI делегирует сортировку backend через `controller.list_tasks(status, tag, search, sort_by, sort_order)`. Сортировка влияет только на отображение, не меняя порядок в файле.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Tkinter (standard library), typer (CLI, existing), pytest (tests, existing). Не добавляются новые внешние зависимости.

**Storage**: `tasks.json` через `Storage`クラсс (существующий), атомарная запись через tmp.replace()

**Testing**: pytest

**Target Platform**: Десктоп (Tkinter), локальный запуск

**Project Type**: desktop-app

**Performance Goals**: Обновление таблицы после сортировки менее чем за 1 секунду

**Constraints**: Офлайн-приложение, без сетевых вызовов, без MCP/плагинов, CLI-контракты не изменяются, сортировка не меняет порядок задач в файле, строки ≤ 100 символов, snake_case, type annotations

**Scale/Scope**: Маленькое десктопное приложение, 4 колонки таблицы (Название, Статус, Срок, Теги)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Stable Data Contract and Durable Writes | Pass | Сортировка не меняет tasks.json (FR-013), запись через существующий атомарный путь storage |
| II | Shared Core and Thin Interfaces | Pass | GUI вызывает существующий `controller.list_tasks`, бизнес-логика сортировки в backend (001) |
| III | Test-First Development (NON-NEGOTIABLE) | Pass | Требуются тесты для первичного сценария и граничных случаев |
| IV | Contract and End-to-End Verification | Pass | Контракт `controller.list_tasks(status, tag, search, sort_by, sort_order)` зафиксирован в Backend Contract |
| V | Local Simplicity and Controlled Scope | Pass | Нет новых зависимостей, офлайн, Tkinterのみ |

## Project Structure

### Documentation (this feature)

```text
specs/002-tasks-sort-gui/
├── spec.md              # Feature specification (already exists)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── sorting-contract.md  # Phase 1 output
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/taskhub/
├── gui.py          # Tkinter/ttk UI — добавить сортировку заголовков
├── app.py          # CLI — без изменений
├── storage.py      # JSON-хранилище — без изменений
├── models.py       # Модель Task — без изменений
└── validate.py     # Валидация — без изменений

tests/
├── test_gui_sort.py      # Новые тесты сортировки GUI
└── (существующие тесты без изменений)
```

**Structure Decision**: Одиночный проект (DEFAULT). Добавление сортировки в существующий `src/taskhub/gui.py`, новые тесты в `tests/`. Никаких новых каталогов или пакетов.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
