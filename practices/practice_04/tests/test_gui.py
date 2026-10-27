from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import taskhub.gui as gui
import taskhub.storage as storage_module
from taskhub.gui import TaskController, TaskForm, TaskHubWindow
from taskhub.models import Task
from taskhub.storage import Storage


@pytest.fixture
def controller_catalog(tmp_path: Path) -> tuple[TaskController, list[Task]]:
    tasks = [
        Task.new("Сделать Практику", tags=["учеба"]),
        Task.new("Straße", tags=["работа"]),
        Task.new("A B", tags=["учеба"]),
        Task.new("[demo]", tags=["учеба"]),
        Task.new("Практика готова", tags=["учеба"]),
    ]
    tasks[-1].status = "done"
    storage = Storage(tmp_path)
    storage.save_tasks(tasks)
    return TaskController(storage), tasks


@pytest.mark.parametrize(
    ("filters", "indices"),
    [
        ({}, [0, 1, 2, 3, 4]),
        ({"search": "ПРАК"}, [0, 4]),
        ({"search": "STRASSE"}, [1]),
        ({"search": " "}, [0, 2, 4]),
        ({"search": "[demo]"}, [3]),
        ({"tag": "учеба"}, [0, 2, 3, 4]),
        ({"tag": "уч"}, []),
        ({"status": "todo", "tag": "учеба", "search": "прак"}, [0]),
        ({"search": "missing"}, []),
    ],
)
def test_controller_list_tasks_preserves_storage_behavior(
    controller_catalog: tuple[TaskController, list[Task]],
    filters: dict[str, str],
    indices: list[int],
) -> None:
    controller, tasks = controller_catalog

    assert [task.id for task in controller.list_tasks(**filters)] == [
        tasks[index].id for index in indices
    ]


def test_controller_list_tasks_is_read_only(
    controller_catalog: tuple[TaskController, list[Task]],
) -> None:
    controller, _ = controller_catalog
    original = controller.storage.path.read_bytes()
    history = {
        path.name: path.read_bytes() for path in controller.storage.history_dir.glob("*.json")
    }

    controller.list_tasks(search="прак")

    assert controller.storage.path.read_bytes() == original
    assert {
        path.name: path.read_bytes() for path in controller.storage.history_dir.glob("*.json")
    } == history


def test_import_gui_does_not_import_tk_or_create_storage(tmp_path: Path) -> None:
    code = (
        "import json, sys; import taskhub.gui; "
        "print(json.dumps({'tk': 'tkinter' in sys.modules}))"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(result.stdout) == {"tk": False}
    assert not (tmp_path / "tasks.json").exists()


@pytest.fixture
def tk_root():
    try:
        import tkinter as tk
    except ImportError as error:
        pytest.skip(f"Tk window is unavailable: {error}")
    try:
        root = tk.Tk()
    except tk.TclError as error:
        pytest.skip(f"Tk window is unavailable: {error}")
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def task_window(tk_root, tmp_path: Path) -> tuple[TaskHubWindow, Storage, list[Task]]:
    tasks = [
        Task.new("Первое", tags=["учеба", "python"]),
        Task.new("Второе", due_date="2026-10-28T12:00:00.000000Z"),
        Task.new("Готово", tags=["учеба"]),
    ]
    tasks[-1].status = "done"
    storage = Storage(tmp_path)
    storage.save_tasks(tasks)
    window = TaskHubWindow(tk_root, TaskController(storage))
    tk_root.update()
    return window, storage, tasks


def test_window_shows_path_and_storage_order(task_window) -> None:
    window, storage, tasks = task_window

    assert window.path_var.get() == str(storage.path.resolve())
    assert str(window.tree.cget("selectmode")) == "browse"
    assert window.tree.cget("yscrollcommand")
    assert window.tree.get_children() == tuple(task.id for task in tasks)
    assert window.tree.item(tasks[0].id, "values") == (
        "Первое",
        "todo",
        "-",
        "учеба, python",
    )
    assert window.status_var.get() == "Показано задач: 3"


def test_window_apply_refresh_and_reset_filters(task_window) -> None:
    window, storage, tasks = task_window
    window.search_var.set("готов")
    window.status_filter_var.set("done")
    window.tag_filter_var.set("учеба")

    window.apply_filters()

    assert window.tree.get_children() == (tasks[-1].id,)
    window.search_var.set("черновик")
    added = storage.add_task(Task.new("Еще готово", tags=["учеба"]))
    storage.mark_done(added.id)
    window.refresh()
    assert len(window.tree.get_children()) == 2
    assert not window.tree.selection()

    window.reset_filters()

    assert window.search_var.get() == ""
    assert window.status_filter_var.get() == "Все"
    assert window.tag_filter_var.get() == ""
    assert len(window.tree.get_children()) == 4


def test_window_distinguishes_empty_results(task_window) -> None:
    window, _, _ = task_window
    window.search_var.set("missing")
    window.apply_filters()
    assert window.status_var.get() == "Ничего не найдено"

    window.controller.storage.save_tasks([])
    window.reset_filters()
    assert window.status_var.get() == "Нет задач"


def test_window_read_error_clears_previous_rows(task_window) -> None:
    window, storage, _ = task_window
    storage.path.write_text("{broken", encoding="utf-8")

    window.refresh()

    assert window.tree.get_children() == ()
    assert window.status_var.get().startswith("Ошибка чтения:")
    assert str(window.add_button.cget("state")) == "disabled"
    assert str(window.edit_button.cget("state")) == "disabled"
    assert str(window.done_button.cget("state")) == "disabled"
    assert str(window.undo_button.cget("state")) == "disabled"
    assert str(window.validate_button.cget("state")) == "normal"


def test_first_window_load_initializes_without_history(tk_root, tmp_path: Path) -> None:
    storage = Storage(tmp_path)

    TaskHubWindow(tk_root, TaskController(storage))

    assert json.loads(storage.path.read_text(encoding="utf-8")) == {
        "version": 1,
        "tasks": [],
    }
    assert not storage.history_dir.exists()


def test_main_uses_resolved_working_directory(monkeypatch, tmp_path: Path) -> None:
    class Root:
        def mainloop(self) -> None:
            pass

    class TkModule:
        class TclError(Exception):
            pass

        @staticmethod
        def Tk() -> Root:
            return Root()

    seen = {}

    class Window:
        def __init__(self, root, controller) -> None:
            seen["root"] = root
            seen["storage"] = controller.storage

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(gui, "_load_tk", lambda: (TkModule, object()))
    monkeypatch.setattr(gui, "TaskHubWindow", Window)

    assert gui.main() == 0
    assert seen["storage"].root == tmp_path.resolve()


def test_main_tk_import_error_does_not_create_storage(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    def fail_tk():
        raise ImportError("no _tkinter")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(gui, "_load_tk", fail_tk)

    assert gui.main() == 1
    assert "Не удалось запустить TaskHub UI" in capsys.readouterr().err
    assert not (tmp_path / "tasks.json").exists()


def test_controller_add_normalizes_ui_fields(tmp_path: Path) -> None:
    controller = TaskController(Storage(tmp_path))

    plain = controller.add_task("  Сделать практику  ", due_date="", tag="")
    detailed = controller.add_task(
        "Со сроком", due_date="2026-10-28T12:00:00.000000Z", tag="учеба"
    )

    assert plain.title == "Сделать практику"
    assert plain.due_date is None
    assert plain.tags == []
    assert detailed.tags == ["учеба"]
    assert Storage(tmp_path).list_tasks() == [plain, detailed]


@pytest.mark.parametrize(
    ("title", "due_date", "message"),
    [
        ("   ", None, "Введите название задачи"),
        ("Задача", "завтра", "YYYY-MM-DDTHH:MM:SS.ffffffZ"),
        ("Задача", "2026-10-28T12:00:00Z", "YYYY-MM-DDTHH:MM:SS.ffffffZ"),
    ],
)
def test_controller_add_rejects_invalid_input_without_writing(
    tmp_path: Path, title: str, due_date: str | None, message: str
) -> None:
    storage = Storage(tmp_path)
    storage.init()
    before = storage.path.read_bytes()
    controller = TaskController(storage)

    with pytest.raises(ValueError, match=message):
        controller.add_task(title, due_date=due_date)

    assert storage.path.read_bytes() == before
    assert not storage.history_dir.exists()


def test_controller_edit_selected_fields_and_preserves_others(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    original = storage.add_task(
        Task.new(
            "Старое",
            due_date="2026-10-28T12:00:00.000000Z",
            tags=["учеба", "python"],
        )
    )
    controller = TaskController(storage)

    renamed = controller.edit_task(original.id, title="  Новое  ")
    retagged = controller.edit_task(original.id, tag="работа")
    cleared = controller.edit_task(original.id, tag="")

    assert renamed is not None
    assert renamed.title == "Новое"
    assert renamed.due_date == original.due_date
    assert renamed.tags == ["учеба", "python"]
    assert renamed.id == original.id
    assert renamed.created_at == original.created_at
    assert retagged is not None and retagged.tags == ["работа"]
    assert cleared is not None and cleared.tags == []


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({}, "Выберите поля для изменения"),
        ({"title": "  "}, "Введите название задачи"),
        ({"due_date": ""}, "Очистка срока не поддерживается"),
        ({"due_date": "tomorrow"}, "YYYY-MM-DDTHH:MM:SS.ffffffZ"),
    ],
)
def test_controller_edit_rejects_noop_and_invalid_fields(
    tmp_path: Path, fields: dict[str, str], message: str
) -> None:
    storage = Storage(tmp_path)
    task = storage.add_task(Task.new("Исходная"))
    before = storage.path.read_bytes()
    history = list(storage.history_dir.glob("*.json"))

    with pytest.raises(ValueError, match=message):
        TaskController(storage).edit_task(task.id, **fields)

    assert storage.path.read_bytes() == before
    assert list(storage.history_dir.glob("*.json")) == history


def test_controller_mutations_use_id_and_report_missing(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    first = storage.add_task(Task.new("Одинаково"))
    second = storage.add_task(Task.new("Одинаково"))
    controller = TaskController(storage)

    assert controller.mark_done(second.id).id == second.id
    assert controller.mark_done("missing") is None
    assert controller.edit_task("missing", title="Новое") is None
    reloaded = Storage(tmp_path).list_tasks()
    assert reloaded[0].id == first.id and reloaded[0].status == "todo"
    assert reloaded[1].id == second.id and reloaded[1].status == "done"


def test_controller_propagates_write_errors(monkeypatch, tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    controller = TaskController(storage)

    def fail_write(task: Task) -> Task:
        raise OSError("disk full")

    monkeypatch.setattr(storage, "add_task", fail_write)

    with pytest.raises(OSError, match="disk full"):
        controller.add_task("Задача")


def test_add_form_saves_optional_values_and_closes(tk_root, tmp_path: Path) -> None:
    controller = TaskController(Storage(tmp_path))
    saved = []
    form = TaskForm(tk_root, controller, saved.append)
    form.title_var.set("  Новая  ")
    form.due_var.set("2026-10-28T12:00:00.000000Z")
    form.tag_var.set("учеба")

    form.save()

    assert not form.window.winfo_exists()
    task = controller.list_tasks()[0]
    assert (task.title, task.due_date, task.tags) == (
        "Новая",
        "2026-10-28T12:00:00.000000Z",
        ["учеба"],
    )
    assert saved == [task]


def test_add_form_keeps_values_after_validation_error(tk_root, tmp_path: Path) -> None:
    controller = TaskController(Storage(tmp_path))
    form = TaskForm(tk_root, controller, lambda task: None)
    form.title_var.set("   ")
    form.due_var.set("завтра")

    form.save()

    assert form.window.winfo_exists()
    assert form.title_var.get() == "   "
    assert form.due_var.get() == "завтра"
    assert form.error_var.get() == "Введите название задачи"
    assert not controller.storage.path.exists()
    form.cancel()


def test_form_cancel_does_not_write(tk_root, tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    storage.init()
    before = storage.path.read_bytes()
    form = TaskForm(tk_root, TaskController(storage), lambda task: None)
    form.title_var.set("Не сохранять")

    form.cancel()

    assert storage.path.read_bytes() == before
    assert not storage.history_dir.exists()


def test_edit_form_changes_only_checked_fields(tk_root, tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    task = storage.add_task(
        Task.new(
            "Старое",
            due_date="2026-10-28T12:00:00.000000Z",
            tags=["учеба", "python"],
        )
    )
    form = TaskForm(tk_root, TaskController(storage), lambda changed: None, task=task)
    assert "YYYY-MM-DDTHH:MM:SS.ffffffZ" in form.due_hint.cget("text")
    assert str(form.title_entry.cget("state")) == "disabled"
    form.change_title_var.set(True)
    form.toggle_edit_fields()
    form.title_var.set("  Новое  ")

    form.save()

    changed = Storage(tmp_path).list_tasks()[0]
    assert changed.title == "Новое"
    assert changed.due_date == task.due_date
    assert changed.tags == ["учеба", "python"]


@pytest.mark.parametrize(("tag", "expected"), [("работа", ["работа"]), ("", [])])
def test_edit_form_replaces_or_clears_all_tags(
    tk_root, tmp_path: Path, tag: str, expected: list[str]
) -> None:
    storage = Storage(tmp_path)
    task = storage.add_task(Task.new("Задача", tags=["учеба", "python"]))
    form = TaskForm(tk_root, TaskController(storage), lambda changed: None, task=task)
    form.change_tag_var.set(True)
    form.toggle_edit_fields()
    form.tag_var.set(tag)

    form.save()

    assert Storage(tmp_path).list_tasks()[0].tags == expected


def test_edit_form_reports_noop_and_missing_task(tk_root, tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    task = storage.add_task(Task.new("Задача"))
    form = TaskForm(tk_root, TaskController(storage), lambda changed: None, task=task)

    form.save()
    assert form.error_var.get() == "Выберите поля для изменения"
    storage.save_tasks([])
    form.change_title_var.set(True)
    form.toggle_edit_fields()
    form.title_var.set("Новое")
    form.save()

    assert form.window.winfo_exists()
    assert form.error_var.get() == "Задача не найдена. Обновите список"
    form.cancel()


def test_window_selection_controls_edit_and_done(task_window, tk_root) -> None:
    window, _, tasks = task_window
    assert str(window.add_button.cget("state")) == "normal"
    assert str(window.edit_button.cget("state")) == "disabled"
    assert str(window.done_button.cget("state")) == "disabled"

    window.tree.selection_set(tasks[0].id)
    window.tree.event_generate("<<TreeviewSelect>>")
    tk_root.update()
    assert str(window.edit_button.cget("state")) == "normal"
    assert str(window.done_button.cget("state")) == "normal"

    window.tree.selection_set(tasks[-1].id)
    window.tree.event_generate("<<TreeviewSelect>>")
    tk_root.update()
    assert str(window.edit_button.cget("state")) == "normal"
    assert str(window.done_button.cget("state")) == "disabled"


def test_window_add_closes_form_before_filtered_refresh(task_window) -> None:
    window, storage, _ = task_window
    window.status_filter_var.set("done")
    window.apply_filters()
    window.open_add()
    form = window.current_form
    form.title_var.set("Новая todo")
    form.save()

    assert not form.window.winfo_exists()
    assert all(task.title != "Новая todo" for task in window.tasks.values())
    assert any(task.title == "Новая todo" for task in Storage(storage.root).list_tasks())


def test_window_done_uses_selected_id_and_keeps_filters(task_window, tk_root) -> None:
    window, storage, tasks = task_window
    window.status_filter_var.set("todo")
    window.apply_filters()
    window.tree.selection_set(tasks[1].id)
    window.tree.event_generate("<<TreeviewSelect>>")
    tk_root.update()

    window.mark_selected_done()

    assert tasks[1].id not in window.tree.get_children()
    assert window.active_filters == ("todo", None, None)
    assert Storage(storage.root).list_tasks(status="done")[0].id == tasks[1].id
    assert str(window.done_button.cget("state")) == "disabled"


def test_window_done_reports_disappeared_task(task_window, tk_root) -> None:
    window, storage, tasks = task_window
    window.tree.selection_set(tasks[0].id)
    window.tree.event_generate("<<TreeviewSelect>>")
    tk_root.update()
    storage.save_tasks([])

    window.mark_selected_done()

    assert window.status_var.get() == "Задача не найдена. Обновите список"


def test_controller_undo_three_restores_add_done_edit(monkeypatch, tmp_path: Path) -> None:
    ticks = iter((1.0, 2.0, 3.0, 4.0))
    monkeypatch.setattr(storage_module.time, "time", lambda: next(ticks))
    storage = Storage(tmp_path)
    storage.init()
    controller = TaskController(storage)
    task = controller.add_task("Задача")
    controller.mark_done(task.id)
    controller.edit_task(task.id, title="Новая")

    assert controller.undo(3) == 3
    assert controller.list_tasks() == []


@pytest.mark.parametrize("steps", [0, 4])
def test_controller_undo_rejects_steps_before_storage(monkeypatch, steps: int) -> None:
    storage = Storage(Path("unused"))
    called = False

    def undo(value: int) -> int:
        nonlocal called
        called = True
        return value

    monkeypatch.setattr(storage, "undo", undo)

    with pytest.raises(ValueError, match="от 1 до 3"):
        TaskController(storage).undo(steps)
    assert called is False


def test_window_undo_defaults_to_one_and_keeps_filters(
    task_window, monkeypatch
) -> None:
    window, storage, _ = task_window
    ticks = iter((5.0, 6.0))
    monkeypatch.setattr(storage_module.time, "time", lambda: next(ticks))
    added = storage.add_task(Task.new("Откатить", tags=["учеба"]))
    window.status_filter_var.set("todo")
    window.tag_filter_var.set("учеба")
    window.apply_filters()
    assert added.id in window.tree.get_children()
    assert window.undo_steps_var.get() == "1"

    window.undo_changes()

    assert window.active_filters == ("todo", "учеба", None)
    assert added.id not in window.tree.get_children()
    assert window.status_var.get() == "Отменено изменений: 1"


def test_window_undo_reports_insufficient_history(task_window) -> None:
    window, storage, _ = task_window
    for snapshot in storage.history_dir.glob("*.json"):
        snapshot.unlink()

    window.undo_changes()

    assert window.status_var.get() == "Ошибка undo: no history to undo"


def test_controller_validation_does_not_initialize_or_change_files(tmp_path: Path) -> None:
    storage = Storage(tmp_path)
    controller = TaskController(storage)
    with pytest.raises(FileNotFoundError):
        controller.validate_tasks()
    assert not storage.path.exists()

    task = storage.add_task(Task.new("Задача"))
    before = storage.path.read_bytes()
    history = {path.name: path.read_bytes() for path in storage.history_dir.glob("*.json")}
    report = controller.validate_tasks()
    assert report == {
        "ok": True,
        "issues": [],
        "counts": {"total": 1, "todo": 1, "done": 0},
    }
    assert task.id in storage.path.read_text(encoding="utf-8")
    assert storage.path.read_bytes() == before
    assert {
        path.name: path.read_bytes() for path in storage.history_dir.glob("*.json")
    } == history


def test_window_validation_reports_whole_file_despite_filters(task_window) -> None:
    window, _, _ = task_window
    window.status_filter_var.set("todo")
    window.apply_filters()

    window.validate_tasks()

    report = window.validation_report.get("1.0", "end-1c")
    assert "Проверка: успешно" in report
    assert "Всего: 3" in report
    assert "todo: 2" in report
    assert "done: 1" in report
    assert str(window.validation_report.cget("state")) == "disabled"
    window.validation_window.destroy()


def test_window_validation_shows_all_issues(task_window) -> None:
    window, storage, _ = task_window
    storage.path.write_text(
        json.dumps(
            {
                "version": 2,
                "tasks": [
                    {
                        "id": "same",
                        "title": "A",
                        "status": "todo",
                        "created_at": "bad",
                        "due_date": "bad",
                    },
                    {
                        "id": "same",
                        "title": "B",
                        "status": "done",
                        "created_at": "2026-01-01T00:00:00.000000Z",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    window.validate_tasks()

    report = window.validation_report.get("1.0", "end-1c")
    assert "version must be 1" in report
    assert "invalid created_at" in report
    assert "invalid due_date" in report
    assert "duplicate id" in report
    window.validation_window.destroy()


@pytest.mark.parametrize("content", [None, "{broken"])
def test_window_validation_reports_read_errors(tk_root, tmp_path: Path, content) -> None:
    storage = Storage(tmp_path)
    if content is not None:
        storage.path.write_text(content, encoding="utf-8")
    window = TaskHubWindow(tk_root, TaskController(storage))
    if content is None:
        storage.path.unlink()

    window.validate_tasks()

    assert window.status_var.get().startswith("Ошибка проверки:")
    assert not storage.path.exists() if content is None else storage.path.read_text() == content


def test_window_recovers_after_external_file_fix(task_window) -> None:
    window, storage, tasks = task_window
    valid = storage.path.read_bytes()
    storage.path.write_text("{broken", encoding="utf-8")
    window.refresh()
    storage.path.write_bytes(valid)

    assert window.refresh() is True
    assert window.tree.get_children() == tuple(task.id for task in tasks)
    assert str(window.add_button.cget("state")) == "normal"
    assert str(window.undo_button.cget("state")) == "normal"


def test_form_preserves_input_on_write_failure(tk_root, monkeypatch, tmp_path: Path) -> None:
    controller = TaskController(Storage(tmp_path))
    form = TaskForm(tk_root, controller, lambda task: None)
    form.title_var.set("Новая")
    form.due_var.set("2026-10-28T12:00:00.000000Z")
    form.tag_var.set("учеба")
    monkeypatch.setattr(
        controller.storage,
        "add_task",
        lambda task: (_ for _ in ()).throw(OSError("disk full")),
    )

    form.save()

    assert form.window.winfo_exists()
    assert form.title_var.get() == "Новая"
    assert form.due_var.get() == "2026-10-28T12:00:00.000000Z"
    assert form.tag_var.get() == "учеба"
    assert form.error_var.get() == "Ошибка сохранения: disk full"
    form.cancel()


def test_successful_form_write_with_failed_refresh_stays_closed(
    task_window, monkeypatch
) -> None:
    window, storage, _ = task_window
    window.open_add()
    form = window.current_form
    form.title_var.set("Сохранено")
    monkeypatch.setattr(
        window.controller,
        "list_tasks",
        lambda **filters: (_ for _ in ()).throw(OSError("read failed")),
    )

    form.save()

    assert not form.window.winfo_exists()
    assert any(task.title == "Сохранено" for task in Storage(storage.root).list_tasks())
    assert window.status_var.get() == (
        "Изменение сохранено, но список не удалось обновить: read failed"
    )


def test_done_and_undo_failures_are_not_reported_as_success(
    task_window, tk_root, monkeypatch
) -> None:
    window, _, tasks = task_window
    window.tree.selection_set(tasks[0].id)
    window.tree.event_generate("<<TreeviewSelect>>")
    tk_root.update()
    monkeypatch.setattr(
        window.controller,
        "mark_done",
        lambda task_id: (_ for _ in ()).throw(OSError("write failed")),
    )
    window.mark_selected_done()
    assert window.status_var.get() == "Ошибка сохранения: write failed"

    monkeypatch.setattr(
        window.controller,
        "undo",
        lambda steps: (_ for _ in ()).throw(OSError("undo failed")),
    )
    window.undo_changes()
    assert window.status_var.get() == "Ошибка undo: undo failed"


def test_validation_remains_available_when_table_is_broken(task_window) -> None:
    window, storage, _ = task_window
    storage.path.write_text("{broken", encoding="utf-8")
    window.refresh()

    window.validate_button.invoke()

    assert window.status_var.get().startswith("Ошибка проверки:")
