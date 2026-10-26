# Spec Delta

## Purpose

Позволяет пользователю находить задачи по части названия в существующем
списке, сочетая текстовый поиск с фильтрами статуса и тега.

## ADDED Requirements

### Requirement: Case-insensitive title substring search

`list` SHALL принимать строковую опцию `--search`. CLI и Storage SHALL искать
буквальное вхождение `search.casefold()` в `title.casefold()`, включая кириллицу
и пробелы, без дополнительной Unicode-нормализации, транслитерации и замены ё/е.
Контракт предполагает корректные данные с `title: str`; некорректные типы вне контракта.
Обработка ошибок загрузки SHALL сохраняться без новой валидации, `str(title)`
и пропуска повреждённых записей. Автоинициализация определена ниже.

#### Scenario: Cyrillic substring in a title
- **GIVEN** задачи «Сделать Практику» и «Купить хлеб»
- **WHEN** пользователь вызывает `list --search "прак"`
- **THEN** вывод содержит только задачу «Сделать Практику»

#### Scenario: Latin case and title-only matching
- **GIVEN** задача «Hello World» и задача «Other» с тегом `hello`
- **WHEN** пользователь вызывает `list --search "HELLO"`
- **THEN** вывод содержит только задачу «Hello World»

#### Scenario: Casefold expansion
- **GIVEN** задача «Straße»
- **WHEN** пользователь вызывает `list --search "STRASSE"`
- **THEN** вывод содержит эту задачу

#### Scenario: No canonical normalization
- **GIVEN** задачи с названиями `"\u0439"` (предсоставленная й)
  и `"\u0438\u0306"` (и + U+0306), записанными здесь через Unicode escapes
- **WHEN** пользователь ищет полную последовательность `"\u0438\u0306"`
- **THEN** вывод содержит только задачу со вторым названием
- **WHEN** пользователь ищет полную последовательность `"\u0439"`
- **THEN** вывод содержит только задачу с первым названием

#### Scenario: No transliteration or letter substitution
- **GIVEN** задачи «ёлка» и «Практика»
- **WHEN** пользователь вызывает `list --search "елка"`
- **THEN** stdout пуст и код выхода равен 0
- **WHEN** пользователь вызывает `list --search "praktika"`
- **THEN** stdout пуст и код выхода равен 0

#### Scenario: Literal spaces and special characters
- **GIVEN** задачи «A B», «AB», «[demo]» и «demo»
- **WHEN** пользователь вызывает `list --search " "`
- **THEN** вывод содержит только задачу «A B»
- **WHEN** пользователь вызывает `list --search "[demo]"`
- **THEN** вывод содержит только задачу «[demo]»

### Requirement: Backward-compatible Storage search API

`Storage.list_tasks` SHALL поддерживать параметры `status=None, tag=None, search=None`
в указанном порядке. `search` SHALL быть последним необязательным параметром
типа `Optional[str]`. Значения `None` и `""` SHALL отключать поисковый фильтр,
сохраняя действие status/tag. Старые позиционные и именованные вызовы SHALL
сохранять прежнюю выборку и порядок. При одинаковых данных и фильтрах Storage
и CLI SHALL выбирать одинаковые задачи в одинаковом порядке.

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
- **WHEN** поиск выполняется через `Storage.list_tasks` и команду `list`
- **THEN** идентификаторы выбранных задач и их относительный порядок совпадают

### Requirement: Search combines with existing filters

Поиск SHALL объединяться с заданными `--status` и `--tag` по AND.
Семантика существующих фильтров SHALL сохраняться.

#### Scenario: All three filters
- **GIVEN** задачи с разными названиями, статусами и тегами
- **WHEN** пользователь вызывает `list --search "практика" --status todo --tag учеба`
- **THEN** вывод содержит только задачи с подстрокой «практика» в названии,
  статусом `todo` и тегом `учеба`

### Requirement: No matches is a successful empty result

При отсутствии совпадений команда SHALL завершаться с кодом 0
и пустым stdout, без поясняющих сообщений.

#### Scenario: Non-matching query or empty storage
- **GIVEN** хранилище пусто либо ни одно название не содержит «несуществующее»
- **WHEN** пользователь вызывает `list --search "несуществующее"`
- **THEN** stdout пуст и код выхода равен 0

### Requirement: Missing or empty query preserves selection

Без `--search` и при `--search ""` команда SHALL возвращать прежнюю выборку,
учитывая заданные фильтры. Опция `--search` без значения SHALL давать
ненулевой код выхода как ошибка аргументов CLI.

#### Scenario: Omitted and empty query
- **GIVEN** существующий список задач
- **WHEN** пользователь сравнивает `list`, `list --search ""`
  и варианты этих вызовов с одинаковыми `--status` и `--tag`
- **THEN** соответствующие пары возвращают одинаковый stdout и код 0

#### Scenario: Missing option value
- **WHEN** пользователь вызывает `list --search` без значения
- **THEN** команда сообщает об ошибке аргументов и возвращает ненулевой код

### Requirement: Search preserves output and stored state

Поиск SHALL сохранять исходный относительный порядок задач и формат
`<id> [status] title (due=... tags=...)`. При существующем хранилище
команда SHALL оставлять его содержимое и историю undo неизменными.
При отсутствующем файле SHALL сохраняться прежняя автоинициализация списка.

#### Scenario: Ordered output without writes
- **GIVEN** существующий tasks.json с несколькими совпадениями и история undo
- **WHEN** пользователь выполняет поиск
- **THEN** совпадения следуют в прежнем относительном порядке и формате
- **AND** байты tasks.json, состав и содержимое snapshots истории не изменились

#### Scenario: Initial listing without a storage file
- **GIVEN** tasks.json и история отсутствуют
- **WHEN** пользователь вызывает `list --search "прак"`
- **THEN** создаётся прежнее пустое хранилище, stdout пуст, код выхода 0
- **AND** snapshots истории не создаются
