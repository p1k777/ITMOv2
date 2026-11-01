# Data Model: Сортировка задач (backend)

**Date**: 2026-11-01
**Feature**: specs/001-tasks-sort-back/spec.md

## Сущности

### Task (существующая)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `str` | UUID4 |
| `title` | `str` | Название задачи |
| `status` | `str` | "todo" \| "done" |
| `created_at` | `str` | ISO UTC, формат `%Y-%m-%dT%H:%M:%S.%fZ` |
| `due_date` | `Optional[str]` | ISO UTC, опционально |
| `tags` | `List[str]` | Список строк |

### SortCriterion

| Значение | Поле сортировки | Обработка |
|----------|-----------------|-----------|
| `"title"` | `Task.title` | casefold, кириллица |
| `"status"` | `Task.status` | "todo" < "done" |
| `"due_date"` | `Task.due_date` | None → конец (asc) / начало (desc) |
| `"created_at"` | `Task.created_at` | Лексикография ISO-строк |
| `"tags"` | `Task.tags[0]` | casefold, None → конец (asc) / начало (desc) |
| `None` | — | Сортировка не применяется |

### SortDirection

| Значение | Описание |
|----------|----------|
| `"asc"` | По возрастанию (по умолчанию) |
| `"desc"` | По убыванию |

## Отношения

- `Storage.list_tasks()` принимает `sort_by: Optional[SortCriterion]` и `sort_order: Optional[SortDirection]`
- `Storage.list_tasks()` возвращает `List[Task]` в отсортированном порядке
- `TaskController.list_tasks()` делегирует `Storage.list_tasks()` (GUI)
- `Storage.list_tasks()` не изменяет `tasks.json`

## Валидация

- `sort_by` должен быть одним из: `"title"`, `"status"`, `"due_date"`, `"created_at"`, `"tags"`, `None`
- `sort_order` должен быть `"asc"` или `"desc"`
- При недопустимом значении → `ValueError`
- Пустой список → возвращается `[]` без ошибок
- Повреждённый `tasks.json` → propagates исключение из `json.load`

## Состояния

| Состояние | Действие |
|-----------|----------|
| `sort_by=None` | Сортировка не применяется, порядок из файла |
| `sort_by="title"`, `sort_order="asc"` | Алфавитно по названию |
| `sort_by="title"`, `sort_order="desc"` | Обратный алфавиту |
| `sort_by="status"`, `sort_order="asc"` | "todo" перед "done" |
| `sort_by="status"`, `sort_order="desc"` | "done" перед "todo" |
| `sort_by="due_date"`, `sort_order="asc"` | По дате, None в конце |
| `sort_by="due_date"`, `sort_order="desc"` | По дате, None в начале |
| `sort_by="created_at"`, `sort_order="asc"` | По дате создания |
| `sort_by="created_at"`, `sort_order="desc"` | Обратно по дате создания |
| `sort_by="tags"`, `sort_order="asc"` | По первому тегу, None в конце |
| `sort_by="tags"`, `sort_order="desc"` | По первому тегу, None в начале |