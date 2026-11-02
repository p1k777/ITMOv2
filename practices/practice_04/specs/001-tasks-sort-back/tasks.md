---

description: "Task list for sorting tasks backend"
---

# Tasks: Сортировка задач (backend)

**Input**: Design documents from `/specs/001-tasks-sort-back/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/list_tasks.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Настройка проекта и базовой структуры

- [ ] T001 [P] [US1] Добавить параметры `sort_by` и `sort_order` в метод `Storage.list_tasks()` в `src/taskhub/storage.py`
- [ ] T002 [P] [US1] Добавить валидацию значений `sort_by` и `sort_order` в `src/taskhub/storage.py` с выбрасыванием `ValueError` при недопустимых значениях
- [ ] T003 [P] [US1] Добавить документацию к `Storage.list_tasks()` в `src/taskhub/storage.py` с описанием параметров и поведения

## Phase 2: Foundational (Блокирующие задачи)

**Purpose**: Настройка базовой инфраструктуры для сортировки

- [ ] T004 [P] [US1] Добавить тесты для сортировки в `tests/test_storage.py` с использованием `tmp_path`
- [ ] T005 [P] [US1] Написать тесты для обработки ошибок валидации в `tests/test_storage.py`
- [ ] T006 [P] [US1] Добавить проверку на стабильность сортировки в тесты в `tests/test_storage.py`

## Phase 3: User Story 1 - Сортировка задач по выбранному полю (Priority: P1) 🎯 MVP

**Goal**: Создать возможность сортировки задач по полям: title, status, due_date, created_at, tags

**Independent Test**: Запустить тесты в `tests/test_storage.py` и проверить, что сортировка работает для всех полей и сценариев из спецификации

### Implementation for User Story 1

- [ ] T007 [US1] Реализовать сортировку по полю `title` с casefold для кириллицы в `src/taskhub/storage.py`
- [ ] T008 [US1] Реализовать сортировку по полю `status` с маппингом "todo" < "done" в `src/taskhub/storage.py`
- [ ] T009 [US1] Реализовать сортировку по полю `due_date` с обработкой `None` в `src/taskhub/storage.py`
- [ ] T100 [US1] Реализовать сортировку по полю `created_at` с лексикографией ISO-строк в `src/taskhub/storage.py`
- [ ] T101 [US1] Реализовать сортировку по полю `tags` с обработкой `None` в `src/taskhub/storage.py`
- [ ] T102 [US1] Добавить обработку исключений при повреждённом `tasks.json` в `src/taskhub/storage.py`
- [ ] T103 [US1] Добавить проверку на стабильность сортировки в `src/taskhub/storage.py`

## Phase 4: Польша и Кросс-Каттинг (Cross-Cutting Concerns)

**Purpose**: Улучшения и проверки

- [ ] T104 [P] [US1] Добавить документацию для сортировки в `docs/sort.md`
- [ ] T105 [P] [US1] Проверить производительность сортировки 1000 задач в `tests/performance.py`
- [ ] T106 [P] [US1] Проверить корректность работы с пустым списком задач в `tests/test_storage.py`
- [ ] T107 [P] [US1] Проверить корректность обработки одинаковых значений в `tests/test_storage.py`

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Зависит от наличия `src/taskhub/storage.py` с базовыми методами
- **Foundational (Phase 2)**: Зависит от завершения Phase 1
- **User Story 1 (Phase 3)**: Зависит от завершения Phase 2
- **Polish (Phase 4)**: Зависит от завершения User Story 1

### User Story Dependencies

- **User Story 1 (P1)**: Все задачи в Phase 3 и 4 зависят от реализации в Phase 2

### Parallel Opportunities

- T001, T002, T003, T004, T005, T006 — можно выполнять параллельно
- T007, T008, T009, T100, T101, T102, T103 — можно выполнять параллельно в рамках User Story 1
- T104, T105, T106, T107 — можно выполнять параллельно

### Parallel Example: User Story 1

```bash
# Реализация основных полей сортировки:
T007, T008, T009, T100, T101

# Тесты:
T004, T005, T106, T107
```