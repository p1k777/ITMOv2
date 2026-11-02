# Tasks

Все команды ниже выполняются из practices/practice_04.
Контракт: specs/task-search/spec.md; подход: design.md.

## 1. Поисковая выборка Storage через TDD

- [x] 1.1 Добавить в tests/test_search.py unit-тесты подстроки, регистра
  кириллицы/латиницы, поиска только по title, буквальных пробелов и символов,
  AND с status/tag, отсутствия совпадений; проверить Straße/STRASSE для отличия
  casefold от lower, отсутствие канонической нормализации на полных последовательностях
  `"\u0439"` и `"\u0438\u0306"` в обоих направлениях, транслитерации и замены ё/е.
  Проверить эквивалентность отсутствующего search, None и пустой строки,
  в том числе с фильтрами, а также старых позиционных и именованных вызовов;
  запустить `.venv/bin/python -m pytest -q tests/test_search.py` и увидеть
  падение из-за отсутствующего параметра search.
- [x] 1.2 Закрепить сигнатуру Storage.list_tasks(status=None, tag=None, search=None)
  с типами из design, добавив search последним необязательным параметром;
  реализовать фильтрацию через casefold без записи и сортировки,
  вычисляя casefold запроса один раз, без дополнительной Unicode-нормализации
  и преобразования title;
  кратко описать параметр в docstring. Проверка: unit-тесты из 1.1 зелёные,
  tests/test_storage.py проходит со старыми вызовами метода.

## 2. CLI-поиск и совместимость через TDD

- [x] 2.1 Добавить CLI-тесты с CliRunner в tests/test_search.py: --search,
  все фильтры вместе, пустой вывод с кодом 0, пустой/отсутствующий запрос,
  ошибка значения `list --search`, сохранение точного формата и порядка;
  проверить Straße/STRASSE и отсутствие канонической нормализации в обоих
  направлениях, а также совпадение выбранных ID и порядка с результатом Storage
  при одинаковых search/status/tag;
  отдельно проверить прежнюю автоинициализацию отсутствующего файла.
  Проверка: новые тесты падают из-за неизвестной CLI-опции.
- [x] 2.2 Добавить строковую опцию --search в app.py, передать её в Storage;
  обновить help/docstring и пример поиска в PROJECT_README.md.
  Проверка: CLI-тесты 2.1 зелёные, `list --help` содержит опцию,
  документированный пример соответствует проверенному вызову CliRunner.
- [x] 2.3 Добавить тест неизменности байтов существующего tasks.json,
  состава и содержимого истории после успешного, пустого и безрезультатного
  поиска. Проверка: `.venv/bin/python -m pytest -q tests/test_search.py`
  проходит; данные для тестов изолированы во временных каталогах.

## 3. Интеграционная проверка

- [x] 3.1 Запустить `.venv/bin/python -m pytest -q` и
  `.venv/bin/python tools/lint.py`; проверить, что проходят также старые
  CLI, edit, undo и MCP-тесты. Зафиксировать фактический итог команд
  и отличать прежние предупреждения от новых ошибок.
- [x] 3.2 Просмотреть итоговый diff и сопоставить каждое требование со
  сценариями/тестами: проверка завершена, когда для каждого есть
  наблюдаемый результат, изменения локальны, а JSON-схема, зависимости
  и MCP-интерфейс не изменились. Отдельно проверить по diff соблюдение границ ошибок:
  существующий путь загрузки и обработка ошибок сохранены, не добавлены новая
  валидация, преобразование title через str() или пропуск повреждённых записей.

## Workflow follow-up

- Провести независимое ревью реализации и приёмку человеком.
- После приёмки выполнить `/opsx-sync search-by-name`, проверить main spec,
  затем `/opsx-archive search-by-name`.

## Verification results

- Storage RED: 14 failed из-за отсутствующего параметра search;
  GREEN после реализации: 15 passed вместе с tests/test_storage.py.
- CLI RED: 13 failed, 14 passed до добавления опции;
  GREEN после реализации: 27 passed.
- `.venv/bin/python -m pytest -q tests/test_search.py`: 39 passed.
- `.venv/bin/python -m pytest -q`: 59 passed, включая прежние CLI, edit, undo и MCP.
- 554 предупреждения полного запуска — существующий DeprecationWarning
  datetime.utcnow() из models.py:14; новые тесты увеличивают число его вызовов.
- `.venv/bin/python tools/lint.py`: taskhub-lint: ok.

Сопоставление требований с tests/test_search.py:

- Case-insensitive title substring search: test_storage_search и test_cli_search;
  кириллица, латиница, Straße/STRASSE, литеральные символы и границы Unicode.
- Backward-compatible Storage search API: test_storage_disabled_search_and_old_calls,
  test_cli_search и test_cli_search_combines_filters.
- Search combines with existing filters: test_storage_search_combines_filters
  и test_cli_search_combines_filters; исключаются задачи с неверным title/status/tag.
- No matches is a successful empty result: test_cli_search,
  test_cli_search_empty_storage и test_storage_search_empty_storage.
- Missing or empty query preserves selection: test_storage_disabled_search_and_old_calls,
  test_cli_disabled_search и test_cli_search_missing_value.
- Search preserves output and stored state: test_cli_search,
  test_cli_search_combines_filters, test_search_preserves_stored_state
  и test_cli_search_empty_storage.

Итоговый diff проверен: реализация ограничена app.py, storage.py,
tests/test_search.py и PROJECT_README.md; в этом файле отмечены задачи и результаты.
Модель, схема, зависимости, MCP-интерфейс, загрузка, запись и undo не изменены
в рамках реализации; новая валидация, str(title) и пропуск записей не добавлены.
