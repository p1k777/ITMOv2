# Spec Delta

## MODIFIED Requirements

### Requirement: Backward-compatible Storage search API

`Storage.list_tasks` SHALL поддерживать параметры `status=None, tag=None, search=None`
в указанном порядке. `search` SHALL быть последним необязательным параметром
типа `Optional[str]`. Значения `None` и `""` SHALL отключать поисковый фильтр,
сохраняя действие status/tag. Старые позиционные и именованные вызовы SHALL
сохранять прежнюю выборку и порядок. При одинаковых данных и фильтрах Storage
и CLI SHALL выбирать одинаковые задачи; их порядок SHALL совпадать без `--sort`.

#### Scenario: Existing positional and keyword calls
- **GIVEN** задачи с разными статусами и тегами
- **WHEN** вызываются `list_tasks("todo", "учеба")`
  и `list_tasks(status="todo", tag="учеба")`
- **THEN** оба вызова возвращают прежнюю выборку задач со статусом `todo`
  и тегом `учеба` в исходном порядке

#### Scenario: Disabled search in Storage
- **GIVEN** существующий список задач
- **WHEN** сравниваются вызовы без search, с `search=None` и с `search=""`,
  в том числе с одинаковыми status/tag
- **THEN** соответствующие вызовы возвращают одинаковые задачи в одинаковом порядке

#### Scenario: Storage and CLI select the same tasks
- **GIVEN** одинаковое хранилище и одинаковые значения search/status/tag
- **WHEN** поиск выполняется через `Storage.list_tasks` и команду `list` без `--sort`
- **THEN** идентификаторы выбранных задач и их относительный порядок совпадают

#### Scenario: Sorted CLI preserves Storage selection
- **GIVEN** одинаковое хранилище и одинаковые значения search/status/tag
- **WHEN** поиск выполняется через `Storage.list_tasks` и команду `list --sort title`
- **THEN** состав выбранных задач совпадает, но CLI упорядочивает их по названию
- **AND** Storage сохраняет исходный порядок

### Requirement: Search preserves output and stored state

Поиск SHALL сохранять исходный относительный порядок задач без `--sort` и формат
`<id> [status] title (due=... tags=...)`. При `--sort title` порядок SHALL
определяться контрактом сортировки. При существующем хранилище команда SHALL
оставлять его содержимое и историю undo неизменными.
При отсутствующем файле SHALL сохраняться прежняя автоинициализация списка.

#### Scenario: Ordered output without writes
- **GIVEN** существующий tasks.json с несколькими совпадениями и история undo
- **WHEN** пользователь выполняет поиск без `--sort`
- **THEN** совпадения следуют в прежнем относительном порядке и формате
- **AND** байты tasks.json, состав и содержимое snapshots истории не изменились

#### Scenario: Initial listing without a storage file
- **GIVEN** tasks.json и история отсутствуют
- **WHEN** пользователь вызывает `list --search "прак"`
- **THEN** создаётся прежнее пустое хранилище, stdout пуст, код выхода 0
- **AND** snapshots истории не создаются

#### Scenario: Sorted search without writes
- **GIVEN** существующий tasks.json с несколькими совпадениями и история undo
- **WHEN** пользователь выполняет `list --search "прак" --sort title`
- **THEN** совпадения упорядочены по названию, а формат строк сохранён
- **AND** байты tasks.json, состав и содержимое snapshots истории не изменились
