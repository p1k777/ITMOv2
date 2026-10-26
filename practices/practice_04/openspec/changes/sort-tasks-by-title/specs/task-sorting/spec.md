# Spec Delta

## Purpose

Позволяет пользователю упорядочить отфильтрованный список задач по названию,
не меняя сохранённые данные и привычное поведение вызовов без сортировки.

## ADDED Requirements

### Requirement: Stable case-insensitive title ordering

Команда `list` SHALL принимать `--sort title` и выводить выбранные задачи
по возрастанию `title.casefold()`. При одинаковых ключах SHALL сохраняться
исходный относительный порядок. Сравнение SHALL использовать порядок Unicode
без локали, дополнительной нормализации и преобразования некорректных типов title.

#### Scenario: Mixed-case titles
- **GIVEN** задачи Zulu, alpha, Beta в указанном порядке
- **WHEN** пользователь вызывает `list --sort title`
- **THEN** строки следуют в порядке alpha, Beta, Zulu и код выхода равен 0

#### Scenario: Equal casefold keys
- **GIVEN** задачи Straße, STRASSE, strasse с разными id в указанном порядке
- **WHEN** пользователь вызывает `list --sort title`
- **THEN** все три задачи сохраняют исходный относительный порядок

#### Scenario: Cyrillic titles
- **GIVEN** задачи Яблоко, банан, Арбуз в указанном порядке
- **WHEN** пользователь вызывает `list --sort title`
- **THEN** строки следуют в порядке Арбуз, банан, Яблоко

### Requirement: Optional sorting preserves existing selection

Без `--sort` команда SHALL сохранять исходный порядок выбранных задач.
Сортировка SHALL изменять только порядок результата после применения
существующих status/tag/search-фильтров, сохраняя их семантику и состав выборки.

#### Scenario: Omitted sorting
- **GIVEN** задачи Zulu, alpha, Beta в указанном порядке
- **WHEN** пользователь вызывает `list` без `--sort`
- **THEN** строки следуют в порядке Zulu, alpha, Beta

#### Scenario: Combined filters and sorting
- **GIVEN** задачи «Практика Я», «Практика Б» со статусом todo и тегом учеба
- **AND** задачи «Практика А» со статусом done и тегом учеба,
  «Практика В» со статусом todo и тегом работа, «Иное» со статусом todo и тегом учеба
- **WHEN** пользователь вызывает
  `list --status todo --tag учеба --search практика --sort title`
- **THEN** вывод содержит только «Практика Б», «Практика Я» в указанном порядке
- **AND** без `--sort` та же выборка следует в исходном порядке «Практика Я», «Практика Б»

### Requirement: Sorting option errors precede storage access

Единственное допустимое значение `--sort` SHALL быть точной строкой `title`.
Неподдерживаемое значение (включая пустую строку) и отсутствие значения
SHALL давать ненулевой код, диагностику в stderr и пустой stdout.
При таких ошибках команда SHALL не создавать и не менять хранилище или историю.
Точный текст диагностики и конкретный ненулевой код не фиксируются.

#### Scenario: Unsupported value
- **GIVEN** tasks.json отсутствует либо уже существует вместе с историей
- **WHEN** пользователь вызывает `list --sort priority`, `list --sort Title`
  или `list --sort ""`
- **THEN** код ненулевой, stdout пуст и stderr содержит диагностику
- **AND** состояние хранилища и истории сохраняется

#### Scenario: Missing value
- **GIVEN** tasks.json и история отсутствуют
- **WHEN** пользователь вызывает `list --sort` без значения
- **THEN** код ненулевой, stdout пуст и stderr содержит диагностику
- **AND** tasks.json и история не создаются

### Requirement: Sorting preserves output and persistence

Сортировка SHALL сохранять формат `<id> [status] title (due=... tags=...)`
без дополнительных строк. Пустой результат SHALL давать код 0 и пустой stdout.
При существующем хранилище SHALL сохраняться байты tasks.json, наличие,
состав и содержимое истории undo. При отсутствии tasks.json SHALL сохраняться
прежняя автоинициализация пустого хранилища без snapshots.

#### Scenario: Sorted output without writes
- **GIVEN** tasks.json с задачами, due и тегами, а также история undo
- **WHEN** пользователь вызывает `list --sort title`
- **THEN** каждая строка сохраняет прежние поля и формат, код выхода равен 0
- **AND** tasks.json и snapshots истории побайтно не изменились

#### Scenario: Empty result
- **GIVEN** существующее пустое хранилище либо фильтры не выбирают ни одной задачи
- **WHEN** пользователь вызывает `list --sort title` с соответствующими фильтрами
- **THEN** stdout пуст, код выхода равен 0 и сохранённое состояние не изменилось

#### Scenario: Initial sorted listing
- **GIVEN** tasks.json и история отсутствуют
- **WHEN** пользователь вызывает `list --sort title`
- **THEN** создаётся пустое хранилище версии 1, stdout пуст, код выхода равен 0
- **AND** история не создаётся
