# Back Diff: tasks-sort-back (before → after)

## Summary
Выравнивание контракта между `001-tasks-sort-back` и `002-tasks-sort-gui` после уточнения, что фичи должны работать вместе.

## Changes

### 1. New section: Frontend Contract

Добавлен раздел `## Frontend Contract *(integration with 002-tasks-sort-gui)*` с описанием вызова `controller.list_tasks(status, tag, search, sort_by, sort_order)` со стороны GUI, допустимыми значениями `sort_by` и `sort_order`, правилом применения сортировки после фильтрации, и явно указанным исключением `created_at` из интерфейса GUI.

### 2. Clarifications

Добавлен четвёртый вопрос-ответ:
- Q: Какие значения `sort_by` и `sort_order` передаёт GUI в `list_tasks`, и как соотносится состояние GUI "без сортировки" с backend-параметром `sort_by=None`? → A: GUI передаёт `sort_by` ∈ {"title", "status", "due_date", "tags", None}, `sort_order` ∈ {"asc", "desc"}; состояние GUI "без сортировки" соответствует `sort_by=None`, `sort_order="asc"` (по умолчанию)

### 3. Checklist Notes

Обновлён раздел Notes: добавлена информация о кросс-спец выравнивании (`## Frontend Contract` section added (references 002-tasks-sort-gui); GUI "без сортировки" → `sort_by=None`; `sort_order=asc` default).
