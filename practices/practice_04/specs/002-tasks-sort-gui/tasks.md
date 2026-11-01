# Tasks: Сортировка задач в GUI TaskHub

**Input**: Design documents from `/specs/002-tasks-sort-gui/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per Constitution Principle III (Test-First Development, NON-NEGOTIABLE). Write tests FIRST, ensure they FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Verify project structure matches plan.md (src/taskhub/gui.py exists, tests/ directory exists)
- [X] T002 [P] Confirm pytest and existing tests pass (`pytest -q` from `practices/practice_04/`)
- [X] T003 [P] Confirm linter passes (`python3 tools/lint.py` from `practices/practice_04/`)

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add `sort_state` attribute to `TaskHubWindow.__init__` in `src/taskhub/gui.py` — default `sort_by=None`, `sort_order="asc"` per data-model.md default state
- [X] T005 [P] Add column-to-backend-field mapping constant in `src/taskhub/gui.py` — `"Название"→"title"`, `"Статус"→"status"`, `"Срок"→"due_date"`, `"Теги"→"tags"` per data-model.md mapping
- [X] T006 Extend `TaskController.list_tasks` in `src/taskhub/gui.py` to accept `sort_by: Optional[str] = None` and `sort_order: str = "asc"` parameters per contracts/sorting-contract.md signature
- [X] T007 [P] Add heading click binding for all 4 Treeview columns in `src/taskhub/gui.py` `_build()` — columns: title, status, due, tags

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

## Phase 3: User Story 1 - Сортировка задач кликом по заголовку колонки с визуальным индикатором (Priority: P1) 🎯 MVP

**Goal**: Пользователь кликает на заголовок колонки, задачи сортируются, отображается стрелка ▲/▼, циклическое переключение asc → desc → без сортировки, индикатор перемещается при смене колонки.

**Independent Test**: Открыть GUI с задачами, кликнуть на заголовке "Название", проверить что задачи перестроились по алфавиту и появилась "Название ▲". Кликнуть снова — проверить переключение на ▼. Кликнуть на другую колонку — проверить перемещение индикатора.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Unit test: `TaskHubWindow.sort_state` defaults to `sort_by=None`, `sort_order="asc"` in `tests/test_gui_sort.py`
- [X] T009 [P] [US1] Unit test: column heading text includes cursor="hand2" for all 4 columns in `tests/test_gui_sort.py`
- [X] T010 [P] [US1] Integration test: click heading "Название" triggers `controller.list_tasks` with `sort_by="title"`, `sort_order="asc"` in `tests/test_gui_sort.py`
- [X] T011 [P] [US1] Integration test: heading shows "Название ▲" after asc sort in `tests/test_gui_sort.py`
- [X] T012 [P] [US1] Integration test: second click on same heading shows "Название ▼" in `tests/test_gui_sort.py`
- [X] T013 [P] [US1] Integration test: third click on same heading removes arrow, calls with `sort_by=None` in `tests/test_gui_sort.py`
- [X] T014 [P] [US1] Integration test: click different column moves arrow, previous column loses arrow in `tests/test_gui_sort.py`

### Implementation for User Story 1

- [X] T015 [P] [US1] Implement `_on_heading_click(column)` handler in `src/taskhub/gui.py` — cyclic toggle asc→desc→None per data-model.md state transitions
- [X] T016 [P] [US1] Implement `_update_sort_indicators(active_column, direction)` in `src/taskhub/gui.py` — sets heading text with " ▲" / " ▼" per FR-007, removes arrow per FR-008
- [X] T017 [US1] Modify `refresh()` in `src/taskhub/gui.py` to pass `sort_by`, `sort_order` to `controller.list_tasks()` per contracts/sorting-contract.md
- [X] T018 [US1] Configure `cursor="hand2"` on all 4 column headings in `src/taskhub/gui.py` `_build()` per FR-001
- [X] T019 [US1] Bind heading click events (`<Button-1>`) to `_on_heading_click` for all 4 columns in `src/taskhub/gui.py` per FR-002

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

## Phase 4: User Story 2 - Сохранение сортировки при смене фильтров (Priority: P2)

**Goal**: При применении или сбросе фильтров (поиск, статус, тег) текущая сортировка сохраняется. Пользователь не теряет выбранный порядок сортировки при изменении фильтров.

**Independent Test**: Отсортировать задачи по "Срок", применить фильтр по статусу "todo", проверить что сортировка по "Срок" сохранилась.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T020 [P] [US2] Integration test: `apply_filters()` preserves `sort_state.sort_by` and `sort_state.sort_order` in `tests/test_gui_sort.py`
- [X] T021 [P] [US2] Integration test: `reset_filters()` preserves `sort_state.sort_by` and `sort_state.sort_order` in `tests/test_gui_sort.py`
- [X] T022 [P] [US2] Integration test: after sort + filter apply, `controller.list_tasks` called with current sort parameters in `tests/test_gui_sort.py`

### Implementation for User Story 2

- [X] T023 [US2] Modify `apply_filters()` in `src/taskhub/gui.py` to preserve existing `sort_state` values per FR-011
- [X] T024 [US2] Modify `reset_filters()` in `src/taskhub/gui.py` to preserve existing `sort_state` values per FR-012

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

## Phase 5: User Story 3 - Работа с пустым списком задач (Priority: P3)

**Goal**: При пустом списке задач заголовки колонок остаются кликабельными, приложение не выдаёт ошибок при клике на заголовок, состояние сортировки устанавливается.

**Independent Test**: Открыть приложение без задач, кликнуть на любой заголовок колонки, убедиться что приложение не выдаёт ошибку.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T025 [P] [US3] Unit test: clicking heading on empty task list does not raise exception in `tests/test_gui_sort.py`
- [X] T026 [P] [US3] Unit test: heading remains clickable (cursor="hand2") with zero tasks in `tests/test_gui_sort.py`
- [X] T027 [P] [US3] Integration test: sort state updates on empty list, table stays empty in `tests/test_gui_sort.py`

### Implementation for User Story 3

- [X] T028 [US3] Ensure `_on_heading_click` handles empty task list without error in `src/taskhub/gui.py` per FR-016
- [X] T029 [US3] Ensure `refresh()` with empty tasks and sort parameters does not crash in `src/taskhub/gui.py` per FR-016

**Checkpoint**: All user stories should now be independently functional

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T030 [P] Run `pytest -q` from `practices/practice_04/` — all tests must pass including new GUI sort tests
- [X] T031 [P] Run `python3 tools/lint.py` from `practices/practice_04/` — no lint violations
- [X] T032 [P] Verify CLI contracts unchanged (app.py, storage.py, models.py not modified) per FR-014
- [X] T033 [P] Verify no new external dependencies added per FR-015
- [X] T034 [P] Verify `tasks.json` file order unchanged after sort operations per FR-013
- [X] T035 [P] Run quickstart.md validation scenarios 1-7 manually to confirm end-to-end behavior

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Constitution Principle III)
- Foundation tasks before story tasks
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003)
- All Foundational tasks marked [P] can run in parallel (T005, T007)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test: TaskHubWindow.sort_state defaults in tests/test_gui_sort.py" (T008)
Task: "Unit test: column heading cursor='hand2' in tests/test_gui_sort.py" (T009)
Task: "Integration test: click heading triggers list_tasks with sort_by='title' in tests/test_gui_sort.py" (T010)
Task: "Integration test: heading shows 'Название ▲' after asc sort in tests/test_gui_sort.py" (T011)
Task: "Integration test: second click shows 'Название ▼' in tests/test_gui_sort.py" (T012)
Task: "Integration test: third click removes arrow, calls with sort_by=None in tests/test_gui_sort.py" (T013)
Task: "Integration test: click different column moves arrow in tests/test_gui_sort.py" (T014)

# Launch implementation tasks for User Story 1 (dependent on tests):
Task: "Implement _on_heading_click(column) handler in src/taskhub/gui.py" (T015)
Task: "Implement _update_sort_indicators in src/taskhub/gui.py" (T016)
Task: "Modify refresh() to pass sort_by, sort_order in src/taskhub/gui.py" (T017)
Task: "Configure cursor='hand2' on all 4 column headings in src/taskhub/gui.py" (T018)
Task: "Bind heading click events in src/taskhub/gui.py" (T019)
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently — click headings, verify arrows, cyclic switching
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (P1)
   - Developer B: User Story 2 (P2)
   - Developer C: User Story 3 (P3)
3. Stories complete and integrate independently

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD per Constitution Principle III)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
