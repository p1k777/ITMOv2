"""End-to-end tests for GUI task sorting.

Chain covered by every test: column click → TaskHubWindow → TaskController
→ Storage.list_tasks() → refreshed Treeview rows and heading indicators.
"""

import pytest
from taskhub.gui import TaskController, TaskHubWindow
from taskhub.storage import Storage
from taskhub.models import Task


@pytest.fixture
def window(tmp_path):
    root = _make_root()
    storage = Storage(tmp_path)
    storage.init()
    win = TaskHubWindow(root, storage.controller if False else None)
    root.destroy()
    return None


def _make_root():
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()
    return root


def _add_tasks(storage: Storage, titles: list[str]):
    tasks = []
    for title in titles:
        task = Task.new(title)
        storage.add_task(task)
        tasks.append(task)
    return tasks


def _row_titles(window: TaskHubWindow) -> list[str]:
    titles = []
    for iid in window.tree.get_children():
        titles.append(window.tasks[iid].title)
    return titles


def _heading(window: TaskHubWindow, column: str) -> str:
    return window.tree.heading(column, "text")


def test_e2e_title_asc_updates_rows_and_arrow(tmp_path):
    """Click 'Название' should sort rows ascending and show '▲'."""
    root = _make_root()
    try:
        storage = Storage(tmp_path)
        storage.init()
        _add_tasks(storage, ["Charlie", "Alpha", "Bravo"])
        win = TaskHubWindow(root, TaskController(storage))

        win._on_heading_click("title")

        assert _row_titles(win) == ["Alpha", "Bravo", "Charlie"]
        assert "▲" in _heading(win, "title")
    finally:
        root.destroy()


def test_e2e_title_desc_updates_rows_and_arrow(tmp_path):
    """Second click on 'Название' should sort descending and show '▼'."""
    root = _make_root()
    try:
        storage = Storage(tmp_path)
        storage.init()
        _add_tasks(storage, ["Charlie", "Alpha", "Bravo"])
        win = TaskHubWindow(
            root,
            TaskController(storage),
        )

        win._on_heading_click("title")  # asc
        win._on_heading_click("title")  # desc

        assert _row_titles(win) == ["Charlie", "Bravo", "Alpha"]
        assert "▼" in _heading(win, "title")
    finally:
        root.destroy()


def test_e2e_title_none_restores_original_order(tmp_path):
    """Third click on 'Название' should restore file order and drop the arrow."""
    root = _make_root()
    try:
        storage = Storage(tmp_path)
        storage.init()
        _add_tasks(storage, ["Charlie", "Alpha", "Bravo"])
        win = TaskHubWindow(
            root,
            TaskController(storage),
        )

        win._on_heading_click("title")  # asc
        win._on_heading_click("title")  # desc
        win._on_heading_click("title")  # reset

        assert _row_titles(win) == ["Charlie", "Alpha", "Bravo"]
        assert "▲" not in _heading(win, "title") and "▼" not in _heading(win, "title")
    finally:
        root.destroy()


def test_e2e_due_date_none_sorts_last_asc(tmp_path):
    """Tasks without due_date go last when sorting by 'Срок' ascending."""
    root = _make_root()
    try:
        storage = Storage(tmp_path)
        storage.init()
        _add_tasks(storage, ["A", "B", "C"])
        win = TaskHubWindow(
            root,
            TaskController(storage),
        )
        # Manually set due dates to get a controlled dataset without GUI form.
        all_tasks = list(storage.list_tasks())
        all_tasks[0].due_date = "2026-02-01T00:00:00.000000Z"
        all_tasks[1].due_date = None
        all_tasks[2].due_date = "2026-01-15T00:00:00.000000Z"
        storage.save_tasks(all_tasks)
        win.refresh()

        win._on_heading_click("due")

        # asc: 2026-01-15 (C), 2026-02-01 (A), None (B) last
        assert _row_titles(win) == ["C", "A", "B"]
        assert "▲" in _heading(win, "due")
    finally:
        root.destroy()


def test_e2e_empty_table_no_error_and_state_set(tmp_path):
    """Clicking headings on an empty table must not raise and must set sort state."""
    root = _make_root()
    try:
        storage = Storage(tmp_path)
        storage.init()
        win = TaskHubWindow(
            root,
            TaskController(storage),
        )

        win._on_heading_click("title")
        win._on_heading_click("status")
        win._on_heading_click("due")
        win._on_heading_click("tags")

        assert _row_titles(win) == []
        assert win.sort_state.sort_by == "tags"
        assert win.sort_state.sort_order == "asc"
    finally:
        root.destroy()


def test_e2e_sort_persists_after_filter_apply(tmp_path):
    """Applying a filter must keep the current sort_by and sort_order."""
    root = _make_root()
    try:
        storage = Storage(tmp_path)
        storage.init()
        _add_tasks(storage, ["Task A", "Task B", "Other"])
        win = TaskHubWindow(
            root,
            TaskController(storage),
        )

        win._on_heading_click("title")  # sort by title asc
        win.search_var.set("Task")
        win.apply_filters()

        assert _row_titles(win) == ["Task A", "Task B"]
        assert win.sort_state.sort_by == "title"
        assert win.sort_state.sort_order == "asc"
        assert "▲" in _heading(win, "title")
    finally:
        root.destroy()
