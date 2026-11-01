"""Tests for GUI task sorting feature (002-tasks-sort-gui)."""
import sys
import tkinter as tk
from unittest.mock import patch, MagicMock

import pytest

from taskhub.gui import TaskController, TaskHubWindow
from taskhub.storage import Storage
from taskhub.models import Task


@pytest.fixture
def temp_storage(tmp_path):
    storage = Storage(tmp_path)
    storage.init()
    return storage


@pytest.fixture
def test_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def controller(temp_storage):
    return TaskController(temp_storage)


@pytest.fixture
def window(test_root, controller):
    return TaskHubWindow(test_root, controller)


def _add_tasks(storage: Storage, titles: list[str]) -> list[Task]:
    tasks = []
    for title in titles:
        task = Task.new(title)
        storage.add_task(task)
        tasks.append(task)
    return tasks


def _heading_text(tree, column: str) -> str:
    return tree.heading(column, "text")


def _simulate_click(window: TaskHubWindow, column: str) -> None:
    """Simulate a click on a column heading."""
    window._on_heading_click(column)


# === US1 Tests: Sort by column click with visual indicator ===


def test_sort_state_defaults(test_root, controller):
    """T008: TaskHubWindow.sort_state defaults to sort_by=None, sort_order='asc'."""
    window = TaskHubWindow(test_root, controller)
    assert window.sort_state.sort_by is None
    assert window.sort_state.sort_order == "asc"


def test_heading_cursor_hand2(test_root, controller, tmp_path):
    """T009: All column headings have cursor='hand2'."""
    _add_tasks(controller.storage, ["Test", "Another"])
    window = TaskHubWindow(test_root, controller)
    cursor = str(window.tree.cget("cursor"))
    assert cursor == "hand2", f"Tree cursor is {cursor}, expected 'hand2'"


def test_click_title_triggers_asc(test_root, controller, tmp_path):
    """T010: Click on 'Название' triggers list_tasks with sort_by='title', sort_order='asc'."""
    _add_tasks(controller.storage, ["Charlie", "Alpha", "Bravo"])
    window = TaskHubWindow(test_root, controller)

    with patch.object(controller, "list_tasks", wraps=controller.list_tasks) as mock_list:
        _simulate_click(window, "title")
        mock_list.assert_called_once()
        call_kwargs = mock_list.call_args.kwargs
        assert call_kwargs["sort_by"] == "title"
        assert call_kwargs["sort_order"] == "asc"


def test_heading_shows_up_arrow_asc(test_root, controller, tmp_path):
    """T011: Heading shows 'Название ▲' after asc sort."""
    _add_tasks(controller.storage, ["Test", "Another"])
    window = TaskHubWindow(test_root, controller)
    _simulate_click(window, "title")
    text = _heading_text(window.tree, "title")
    assert "▲" in text, f"Heading text is '{text}', expected '▲'"


def test_second_click_shows_down_arrow(test_root, controller, tmp_path):
    """T012: Second click on same heading shows '▼'."""
    _add_tasks(controller.storage, ["Test", "Another"])
    window = TaskHubWindow(test_root, controller)
    _simulate_click(window, "title")  # asc
    _simulate_click(window, "title")  # desc
    text = _heading_text(window.tree, "title")
    assert "▼" in text, f"Heading text is '{text}', expected '▼'"


def test_third_click_removes_arrow(test_root, controller, tmp_path):
    """T013: Third click removes arrow, calls with sort_by=None."""
    _add_tasks(controller.storage, ["Test", "Another"])
    window = TaskHubWindow(test_root, controller)
    _simulate_click(window, "title")  # asc
    _simulate_click(window, "title")  # desc
    _simulate_click(window, "title")  # None (reset)

    text = _heading_text(window.tree, "title")
    assert "▲" not in text and "▼" not in text, (
        f"Heading text is '{text}', expected no arrow"
    )


def test_click_different_column_moves_arrow(test_root, controller, tmp_path):
    """T014: Click different column moves arrow, previous loses arrow."""
    _add_tasks(controller.storage, ["Test", "Another"])
    window = TaskHubWindow(test_root, controller)
    _simulate_click(window, "title")  # sort by title asc

    _simulate_click(window, "status")  # sort by status asc

    title_text = _heading_text(window.tree, "title")
    status_text = _heading_text(window.tree, "status")
    assert "▲" not in title_text, f"Title heading still has arrow: '{title_text}'"
    assert "▲" in status_text, f"Status heading missing arrow: '{status_text}'"


# === US2 Tests: Sort persistence on filter change ===


def test_apply_filters_preserves_sort(test_root, controller, tmp_path):
    """T020: apply_filters() preserves sort_state."""
    _add_tasks(controller.storage, ["Task A", "Task B"])
    window = TaskHubWindow(test_root, controller)
    _simulate_click(window, "title")  # sort by title asc

    # Apply filter
    window.search_var.set("Task")
    window.apply_filters()

    assert window.sort_state.sort_by == "title"
    assert window.sort_state.sort_order == "asc"


def test_reset_filters_preserves_sort(test_root, controller, tmp_path):
    """T021: reset_filters() preserves sort_state."""
    _add_tasks(controller.storage, ["Task A", "Task B"])
    window = TaskHubWindow(test_root, controller)
    _simulate_click(window, "title")  # sort by title asc

    window.search_var.set("Test")
    window.reset_filters()

    assert window.sort_state.sort_by == "title"
    assert window.sort_state.sort_order == "asc"


def test_filter_apply_calls_list_tasks_with_sort(test_root, controller, tmp_path):
    """T022: After sort + filter apply, controller.list_tasks called with sort params."""
    _add_tasks(controller.storage, ["Charlie", "Alpha", "Bravo"])
    window = TaskHubWindow(test_root, controller)
    _simulate_click(window, "title")  # sort by title asc

    with patch.object(controller, "list_tasks", wraps=controller.list_tasks) as mock_list:
        window.search_var.set("Char")
        window.apply_filters()
        call_kwargs = mock_list.call_args.kwargs
        assert call_kwargs["sort_by"] == "title"
        assert call_kwargs["sort_order"] == "asc"


# === US3 Tests: Empty task list handling ===


def test_click_heading_empty_list_no_error(test_root, controller, tmp_path):
    """T025: Clicking heading on empty task list does not raise."""
    window = TaskHubWindow(test_root, controller)
    _simulate_click(window, "title")
    _simulate_click(window, "status")
    _simulate_click(window, "due")
    _simulate_click(window, "tags")


def test_heading_clickable_empty_list(test_root, controller, tmp_path):
    """T026: Heading remains clickable (cursor='hand2') with zero tasks."""
    window = TaskHubWindow(test_root, controller)
    cursor = str(window.tree.cget("cursor"))
    assert cursor == "hand2"


def test_sort_state_updates_empty_list(test_root, controller, tmp_path):
    """T027: Sort state updates on empty list, table stays empty."""
    window = TaskHubWindow(test_root, controller)
    _simulate_click(window, "title")
    assert window.sort_state.sort_by == "title"
    assert window.sort_state.sort_order == "asc"
    assert len(window.tree.get_children()) == 0
