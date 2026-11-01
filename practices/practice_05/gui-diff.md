# GUI Diff: tasks-sort-gui (before → after)

## Summary
Выравнивание контракта между `002-tasks-sort-gui` и `001-tasks-sort-back` после уточнения, что фичи должны работать вместе.

## Changes

### 1. Functional Requirements

**FR-005** (изменён):
- Before: "При клике на колонку, отсортированную "desc", сортировка сбрасывается (возвращается порядок из файла)"
- After: "При клике на колонку, отсортированную "desc", сортировка сбрасывается — GUI передаёт в backend `sort_by=None` (без сортировки), `sort_order=asc` (по умолчанию), задачи возвращаются в порядке из файла"

**FR-008** (изменён):
- Before: "В заголовке неотсортированной колонки стрелка отсутствует"
- After: "В заголовке колонки без сортировки (sort_by=None) стрелка отсутствует"

**FR-009** (изменён):
- Before: "При изменении сортировки таблица обновляется (refresh) с новыми параметрами sort_by и sort_order"
- After: "При изменении сортировки таблица обновляется (refresh) через вызов `controller.list_tasks(status, tag, search, sort_by, sort_order)` с новыми параметрами sort_by и sort_order"

**FR-011** (изменён):
- Before: "При нажатии "Применить" (фильтры) текущая сортировка сохраняется"
- After: "При нажатии "Применить" (фильтры) текущая сортировка сохраняется, sort_by/sort_order передаются вместе с фильтрами"

**FR-012** (изменён):
- Before: "При нажатии "Сбросить" (фильтры) текущая сортировка сохраняется"
- After: "При нажатии "Сбросить" (фильтры) текущая сортировка сохраняется, sort_by/sort_order передаются вместе с пустыми фильтрами"

**FR-017** (добавлен):
- "GUI не предоставляет интерфейс для сортировки по `created_at` — доступные колонки: Название (title), Статус (status), Срок (due_date), Теги (tags)"

### 2. Key Entities

**SortState** (изменён):
- Before: "Состояние сортировки GUI — текущая колонка (title/status/due_date/tags/None) и направление (asc/desc/без сортировки)"
- After: "Состояние сортировки GUI — текущая колонка (title/status/due_date/tags/None) и направление (asc/desc/без сортировки). Состояние "без сортировки" соответствует `sort_by=None` при вызове backend."

**Column** (изменён):
- Before: "Колонка таблицы — отображаемое название и соответствующее поле сортировки backend"
- After: "Колонка таблицы — отображаемое название и соответствующее поле сортировки backend (Название → title, Статус → status, Срок → due_date, Теги → tags)"

### 3. New section: Backend Contract

Добавлен раздел `## Backend Contract *(integration with 001-tasks-sort-back)*` с описанием вызова `controller.list_tasks(status, tag, search, sort_by, sort_order)`, допустимыми значениями `sort_by` и `sort_order`, и правилом применения сортировки после фильтрации.

### 4. Assumptions

Добавлен пункт: "Состояние "без сортировки" в GUI соответствует `sort_by=None` в вызове backend `list_tasks`"

### 5. Clarifications

Добавлен второй вопрос-ответ:
- Q: Как соотносится состояние GUI "без сортировки" с параметром `sort_by` backend? → A: "Без сортировки" в GUI соответствует `sort_by=None` при вызове `list_tasks`; `sort_order` по умолчанию "asc"

### 6. Checklist Notes

Обновлён раздел Notes: добавлена информация о кросс-спец выравнивании (GUI "без сортировки" → `sort_by=None`, `sort_order=asc` default, `created_at` excluded from GUI (FR-017)).
