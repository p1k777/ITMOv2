# Contract: Сортировка задач в GUI TaskHub

## Интерфейс: GUI → Backend (через TaskController)

GUI вызывает метод `TaskController.list_tasks()` с seguintes параметрами:

```
controller.list_tasks(
    status: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
) -> List[Task]
```

### Параметры сортировки

| Параметр | Тип | Допустимые значения | Значение по умолчанию |
|----------|-----|---------------------|----------------------|
| `sort_by` | `str \| None` | "title", "status", "due_date", "tags", None | None |
| `sort_order` | `str` | "asc", "desc" | "asc" |

### Маппинг колонок GUI

| Заголовок GUI | `sort_by` |
|---------------|-----------|
| Название | "title" |
| Статус | "status" |
| Срок | "due_date" |
| Теги | "tags" |

### Состояние "без сортировки"

`sort_by=None` → сортировка не применяется, задачи возвращаются в порядке из файла. `sort_order` игнорируется (по умолчанию "asc").

### Порядок операций

1. Фильтрация (status, tag, search) — применяется первыми
2. Сортировка (sort_by, sort_order) — применяется после фильтрации
3. Возврат отсортированного списка — не меняет порядок в tasks.json

## Интерфейс: GUI (внутренний)

### TaskHubWindow.sort_state

Атрибут экземпляра `TaskHubWindow`, хранящий текущее состояние сортировки.

### Обработчик клика на заголовок колонки

При клике на заголовок колонки `column`:
1. Если `column == sort_state.sort_by`:
   - asc → desc
   - desc → None (сброс сортировки)
   - None → asc
2. Иначе:
   - `sort_state.sort_by = column`
   - `sort_state.sort_order = "asc"`
3. Обновить индикаторы в заголовках (стрелка ▲/▼ на активной колонке, без стрелки на остальных)
4. Вызвать `refresh()` с новыми параметрами sort_by/sort_order

### Метод refresh() с сортировкой

```
refresh() → вызывает controller.list_tasks(status, tag, search, sort_by, sort_order)
```

## Интерфейс: CLI

CLI-контракты не изменяются. Команда `list` работает без параметров сортировки.
