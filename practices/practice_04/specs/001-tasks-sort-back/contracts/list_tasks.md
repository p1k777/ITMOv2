# Contract: Storage.list_tasks()

**Date**: 2026-11-01
**Feature**: specs/001-tasks-sort-back/spec.md

## Сигнатура

```python
def list_tasks(
    self,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
) -> List[Task]:
```

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| `status` | `Optional[str]` | `None` | Фильтр по статусу: "todo" или "done" |
| `tag` | `Optional[str]` | `None` | Фильтр по тегу |
| `search` | `Optional[str]` | `None` | Поиск по названию (casefold) |
| `sort_by` | `Optional[str]` | `None` | Поле сортировки |
| `sort_order` | `Optional[str]` | `"asc"` | Направление сортировки |

## Возвращаемое значение

`List[Task]` — отфильтрованный и отсортированный список задач.

## Порядок операций

1. `load()` — чтение `tasks.json`
2. Фильтрация: `status` → `tag` → `search`
3. Сортировка: `sort_by` → `sort_order`

## Валидация

| Условие | Действие |
|---------|----------|
| `sort_by` не в `{"title", "status", "due_date", "created_at", "tags", None}` | `ValueError` |
| `sort_order` не в `{"asc", "desc"}` | `ValueError` |
| `tasks.json` повреждён | Propagates исключение из `json.load` |

## Контракт с GUI (002-tasks-sort-gui)

GUI вызывает `controller.list_tasks(status, tag, search, sort_by, sort_order)`:
- `sort_by` ∈ `{"title", "status", "due_date", "tags", None}`
- `sort_order` ∈ `{"asc", "desc"}`
- Состояние GUI "без сортировки" → `sort_by=None`, `sort_order="asc"`
- `created_at` не передаётся из GUI

## Контракт с CLI

CLI не передаёт параметры сортировки. Команда `list` вызывает `list_tasks()` без `sort_by`/`sort_order`.

## Примеры

```python
# Без сортировки
storage.list_tasks()  # → порядок из файла

# По названию, возрастание
storage.list_tasks(sort_by="title", sort_order="asc")

# По статусу, убывание
storage.list_tasks(status="todo", sort_by="status", sort_order="desc")
```