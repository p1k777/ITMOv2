# Research: Сортировка задач (backend)

**Date**: 2026-11-01
**Feature**: specs/001-tasks-sort-back/spec.md

## Decision: Сортировка реализуется через `sorted()` с key-функцией

**Rationale**: Стандартный Python `sorted()` — стабильный (Timsort), поддерживает `reverse` и `key`. Не требует внешних зависимостей. Подходит для задачи: отсортировать список задач по одному полю, сохраняя исходный порядок при равных ключах.

**Alternatives considered**:
- Ручная сортировка с компаратором — больше кода, те же инварианты.
- Использование `functools.cmp_to_key` — ненужно, `key` покрывает все случаи.

## Decision: Ключ сортировки строится через лямбду, в зависимости от `sort_by`

**Rationale**: Каждое поле требует специальной обработки:
- `title` — `casefold()` для игнорирования регистра
- `status` — маппинг "todo" < "done"
- `due_date` — `None` в конец/начало
- `created_at` — лексикография ISO-строк
- `tags` — первый тег, `None` в конец/начало

Ключ возвращается как кортеж `(primary_key, index)` для стабильности.

## Decision: Валидация параметров в `list_tasks`

**Rationale**: FR-013 требует выбрасывать `ValueError` при недопустимом `sort_by`/`sort_order`. Реализуется через `if sort_by not in VALID_SORT_BY: raise ValueError(...)`.

## Decision: `list_tasks` не ловит исключения

**Rationale**: FR-014 требует propagates исключений из `json.load`. Текущая реализация в `storage.py` уже не ловит исключения в `list_tasks` — только в GUI (`gui.py:363`).

## Decision: Атомарная запись через `tmp.replace()`

**Rationale**: Уже реализовано в `_write()`. Не требует блокировок — `os.replace()` атомарна на POSIX.

## Decision: Тестирование через pytest с временным хранилищем

**Rationale**: Конституция требует тестов без зависимости от реального `tasks.json`. Используются `tmp_path` фикстуры.

## Decision: GUI не предоставляет сортировку по `created_at`

**Rationale**: Колонки GUI: Название, Статус, Срок, Теги. `created_at` недоступен в интерфейсе (Out of Scope).

## Decision: Состояние "без сортировки" = `sort_by=None`, `sort_order="asc"`

**Rationale**: Согласовано с GUI-спекой (002). При `sort_by=None` сортировка не применяется.