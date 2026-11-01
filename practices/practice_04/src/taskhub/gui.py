from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from typing import Callable, List, Optional

from .models import ISO_FORMAT, Task, SortState
from .storage import Storage
from .validate import validate_file


def _load_tk():
    import tkinter as tk
    from tkinter import ttk

    return tk, ttk


class TaskController:
    """Expose TaskHub operations to the desktop UI without widget dependencies."""

    def __init__(self, storage: Storage):
        self.storage = storage

    def list_tasks(
        self,
        status: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> List[Task]:
        """Return the current storage-order selection for the given filters."""
        return self.storage.list_tasks(
            status=status, tag=tag, search=search,
            sort_by=sort_by, sort_order=sort_order,
        )

    def add_task(
        self,
        title: str,
        due_date: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> Task:
        """Validate GUI input and persist one new todo task."""
        normalized_title = self._title(title)
        normalized_due = due_date or None
        if normalized_due is not None:
            self._due_date(normalized_due)
        task = Task.new(
            normalized_title,
            due_date=normalized_due,
            tags=[tag] if tag else [],
        )
        return self.storage.add_task(task)

    def mark_done(self, task_id: str) -> Optional[Task]:
        """Complete the task identified by ID, or return None if it disappeared."""
        return self.storage.mark_done(task_id)

    def edit_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        due_date: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> Optional[Task]:
        """Validate and persist only explicitly supplied edit fields."""
        if title is None and due_date is None and tag is None:
            raise ValueError("Выберите поля для изменения")
        normalized_title = self._title(title) if title is not None else None
        if due_date is not None:
            if not due_date:
                raise ValueError("Очистка срока не поддерживается")
            self._due_date(due_date)
        tags = None if tag is None else ([tag] if tag else [])
        return self.storage.edit_task(
            task_id,
            title=normalized_title,
            due_date=due_date,
            tags=tags,
        )

    def undo(self, steps: int = 1) -> int:
        """Undo one to three changes in the shared storage history."""
        if not 1 <= steps <= 3:
            raise ValueError("Количество шагов должно быть от 1 до 3")
        return self.storage.undo(steps)

    def validate_tasks(self) -> dict:
        """Validate the complete file without initializing or changing it."""
        return validate_file(self.storage.path)

    @staticmethod
    def _title(title: str) -> str:
        normalized = title.strip()
        if not normalized:
            raise ValueError("Введите название задачи")
        return normalized

    @staticmethod
    def _due_date(value: str) -> None:
        try:
            parsed = datetime.strptime(value, ISO_FORMAT)
        except (TypeError, ValueError):
            raise ValueError("Используйте формат YYYY-MM-DDTHH:MM:SS.ffffffZ") from None
        if parsed.strftime(ISO_FORMAT) != value:
            raise ValueError("Используйте формат YYYY-MM-DDTHH:MM:SS.ffffffZ")


class TaskForm:
    """Shared Tk form for adding a task or editing explicitly selected fields."""

    def __init__(
        self,
        parent,
        controller: TaskController,
        on_saved: Callable[[Task], None],
        task: Optional[Task] = None,
    ):
        self.tk, self.ttk = _load_tk()
        self.controller = controller
        self.on_saved = on_saved
        self.task = task
        self.window = self.tk.Toplevel(parent)
        self.window.title("Изменить задачу" if task else "Добавить задачу")
        self.window.transient(parent)
        self.window.protocol("WM_DELETE_WINDOW", self.cancel)
        self._build()
        self.window.grab_set()

    def _build(self) -> None:
        frame = self.ttk.Frame(self.window, padding=12)
        frame.grid(sticky="nsew")
        frame.columnconfigure(1, weight=1)
        self.title_var = self.tk.StringVar(value=self.task.title if self.task else "")
        self.due_var = self.tk.StringVar(value=(self.task.due_date or "") if self.task else "")
        self.tag_var = self.tk.StringVar()
        self.error_var = self.tk.StringVar()

        self.change_title_var = self.tk.BooleanVar(value=False)
        self.change_due_var = self.tk.BooleanVar(value=False)
        self.change_tag_var = self.tk.BooleanVar(value=False)
        self._field_row(frame, 0, "Название", "title")
        self._field_row(frame, 1, "Срок", "due")
        self.due_hint = self.ttk.Label(
            frame,
            text="UTC: YYYY-MM-DDTHH:MM:SS.ffffffZ",
        )
        self.due_hint.grid(row=2, column=1, sticky="w", pady=(0, 8))
        self._field_row(frame, 3, "Тег", "tag")
        if self.task:
            self.ttk.Label(frame, text="Заменить все теги").grid(
                row=4, column=1, sticky="w", pady=(0, 8)
            )

        self.ttk.Label(frame, textvariable=self.error_var, foreground="#a40000").grid(
            row=5, column=0, columnspan=3, sticky="w"
        )
        buttons = self.ttk.Frame(frame)
        buttons.grid(row=6, column=0, columnspan=3, sticky="e", pady=(8, 0))
        self.ttk.Button(buttons, text="Сохранить", command=self.save).pack(
            side="left", padx=(0, 4)
        )
        self.ttk.Button(buttons, text="Отмена", command=self.cancel).pack(side="left")
        self.toggle_edit_fields()

    def _field_row(self, frame, row: int, label: str, field: str) -> None:
        self.ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8))
        variable = getattr(self, f"{field}_var")
        entry = self.ttk.Entry(frame, textvariable=variable, width=38)
        entry.grid(row=row, column=1, sticky="ew", pady=3)
        setattr(self, f"{field}_entry", entry)
        if self.task:
            change_variable = getattr(self, f"change_{field}_var")
            self.ttk.Checkbutton(
                frame,
                text="Изменить",
                variable=change_variable,
                command=self.toggle_edit_fields,
            ).grid(row=row, column=2, padx=(8, 0))

    def toggle_edit_fields(self) -> None:
        if not self.task:
            return
        for field in ("title", "due", "tag"):
            enabled = getattr(self, f"change_{field}_var").get()
            getattr(self, f"{field}_entry").configure(
                state="normal" if enabled else "disabled"
            )

    def save(self) -> None:
        self.error_var.set("")
        try:
            if self.task:
                changed = self.controller.edit_task(
                    self.task.id,
                    title=self.title_var.get() if self.change_title_var.get() else None,
                    due_date=self.due_var.get() if self.change_due_var.get() else None,
                    tag=self.tag_var.get() if self.change_tag_var.get() else None,
                )
                if changed is None:
                    self.error_var.set("Задача не найдена. Обновите список")
                    return
                saved = changed
            else:
                saved = self.controller.add_task(
                    self.title_var.get(),
                    due_date=self.due_var.get(),
                    tag=self.tag_var.get(),
                )
        except ValueError as error:
            self.error_var.set(str(error))
            return
        except (OSError, TypeError, KeyError) as error:
            self.error_var.set(f"Ошибка сохранения: {error}")
            return
        self.window.grab_release()
        self.window.destroy()
        self.on_saved(saved)

    def cancel(self) -> None:
        self.window.grab_release()
        self.window.destroy()


class TaskHubWindow:
    """Single-window Tk adapter for browsing and changing TaskHub data."""

    COLUMN_TO_FIELD: dict[str, str] = {
        "title": "title",
        "status": "status",
        "due": "due_date",
        "tags": "tags",
    }

    def __init__(self, root, controller: TaskController):
        self.tk, self.ttk = _load_tk()
        self.root = root
        self.controller = controller
        self.active_filters: tuple[Optional[str], Optional[str], Optional[str]] = (
            None,
            None,
            None,
        )
        self.sort_state: SortState = SortState()
        self.tasks: dict[str, Task] = {}
        self.loaded = False
        self.current_form: Optional[TaskForm] = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        self.root.title("TaskHub")
        self.root.minsize(720, 420)
        frame = self.ttk.Frame(self.root, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        self.path_var = self.tk.StringVar(value=str(self.controller.storage.path.resolve()))
        self.ttk.Label(frame, textvariable=self.path_var).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        filters = self.ttk.Frame(frame)
        filters.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        filters.columnconfigure(1, weight=1)
        self.search_var = self.tk.StringVar()
        self.status_filter_var = self.tk.StringVar(value="Все")
        self.tag_filter_var = self.tk.StringVar()
        self.ttk.Label(filters, text="Поиск").grid(row=0, column=0, padx=(0, 4))
        self.ttk.Entry(filters, textvariable=self.search_var).grid(
            row=0, column=1, sticky="ew", padx=(0, 8)
        )
        self.ttk.Label(filters, text="Статус").grid(row=0, column=2, padx=(0, 4))
        self.status_filter = self.ttk.Combobox(
            filters,
            textvariable=self.status_filter_var,
            values=("Все", "todo", "done"),
            state="readonly",
            width=7,
        )
        self.status_filter.grid(row=0, column=3, padx=(0, 8))
        self.ttk.Label(filters, text="Тег").grid(row=0, column=4, padx=(0, 4))
        self.ttk.Entry(filters, textvariable=self.tag_filter_var, width=14).grid(
            row=0, column=5, padx=(0, 8)
        )
        self.ttk.Button(filters, text="Применить", command=self.apply_filters).grid(
            row=0, column=6, padx=(0, 4)
        )
        self.ttk.Button(filters, text="Сбросить", command=self.reset_filters).grid(
            row=0, column=7
        )

        table = self.ttk.Frame(frame)
        table.grid(row=2, column=0, columnspan=2, sticky="nsew")
        table.columnconfigure(0, weight=1)
        table.rowconfigure(0, weight=1)
        columns = ("title", "status", "due", "tags")
        self.tree = self.ttk.Treeview(
            table, columns=columns, show="headings", selectmode="browse",
            cursor="hand2",
        )
        headings = ("Название", "Статус", "Срок", "Теги")
        widths = (280, 80, 210, 180)
        for column, heading, width in zip(columns, headings, widths):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, minwidth=60)
            self.tree.heading(
                column,
                command=lambda c=column: self._on_heading_click(c),
            )
        scrollbar = self.ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self._sync_actions)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        footer = self.ttk.Frame(frame)
        footer.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.add_button = self.ttk.Button(footer, text="Добавить", command=self.open_add)
        self.add_button.pack(side="left", padx=(0, 4))
        self.edit_button = self.ttk.Button(
            footer, text="Изменить", command=self.open_edit, state="disabled"
        )
        self.edit_button.pack(side="left", padx=(0, 4))
        self.done_button = self.ttk.Button(
            footer,
            text="Выполнено",
            command=self.mark_selected_done,
            state="disabled",
        )
        self.done_button.pack(side="left", padx=(0, 4))
        self.ttk.Button(footer, text="Обновить", command=self.refresh).pack(
            side="left", padx=(0, 4)
        )
        self.undo_steps_var = self.tk.StringVar(value="1")
        self.undo_steps = self.ttk.Combobox(
            footer,
            textvariable=self.undo_steps_var,
            values=("1", "2", "3"),
            state="readonly",
            width=3,
        )
        self.undo_steps.pack(side="left", padx=(4, 4))
        self.undo_button = self.ttk.Button(
            footer, text="Отменить изменения", command=self.undo_changes
        )
        self.undo_button.pack(side="left", padx=(0, 4))
        self.validate_button = self.ttk.Button(
            footer, text="Проверить данные", command=self.validate_tasks
        )
        self.validate_button.pack(side="left", padx=(0, 4))
        self.status_var = self.tk.StringVar()
        self.ttk.Label(footer, textvariable=self.status_var).pack(side="right")

    def apply_filters(self) -> None:
        status = self.status_filter_var.get()
        self.active_filters = (
            None if status == "Все" else status,
            self.tag_filter_var.get() or None,
            self.search_var.get() or None,
        )
        self.refresh()

    def reset_filters(self) -> None:
        self.search_var.set("")
        self.status_filter_var.set("Все")
        self.tag_filter_var.set("")
        self.active_filters = (None, None, None)
        self.refresh()

    def refresh(self) -> bool:
        status, tag, search = self.active_filters
        sort_by, sort_order = self.sort_state
        try:
            tasks = self.controller.list_tasks(
                status=status, tag=tag, search=search,
                sort_by=sort_by, sort_order=sort_order,
            )
        except (OSError, ValueError, TypeError, KeyError) as error:
            self.loaded = False
            self._replace_rows([])
            self.status_var.set(f"Ошибка чтения: {error}")
            return False
        self.loaded = True
        self._replace_rows(tasks)
        self._update_sort_indicators(sort_by, sort_order)
        if tasks:
            self.status_var.set(f"Показано задач: {len(tasks)}")
        elif any(value is not None for value in self.active_filters):
            self.status_var.set("Ничего не найдено")
        else:
            self.status_var.set("Нет задач")
        return True

    def _replace_rows(self, tasks: List[Task]) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tasks = {task.id: task for task in tasks}
        for task in tasks:
            self.tree.insert(
                "",
                "end",
                iid=task.id,
                values=(
                    task.title,
                    task.status,
                    task.due_date or "-",
                    ", ".join(task.tags),
                ),
            )
        self._sync_actions()

    def _on_heading_click(self, column: str) -> None:
        """Handle heading click: cyclic toggle asc → desc → None (reset)."""
        field = self.COLUMN_TO_FIELD.get(column, column)

        if self.sort_state.sort_by == field:
            if self.sort_state.sort_order == "asc":
                self.sort_state = SortState(field, "desc")
            elif self.sort_state.sort_order == "desc":
                self.sort_state = SortState(None, "asc")
            else:
                self.sort_state = SortState(field, "asc")
        else:
            self.sort_state = SortState(field, "asc")

        self.refresh()

    def _update_sort_indicators(self, sort_by: Optional[str], sort_order: Optional[str]) -> None:
        """Update heading text with arrows for active sort column."""
        columns = ("title", "status", "due", "tags")
        headings = ("Название", "Статус", "Срок", "Теги")

        for column, heading in zip(columns, headings):
            if sort_by == column:
                if sort_order == "asc":
                    self.tree.heading(column, text=f"{heading} ▲")
                else:
                    self.tree.heading(column, text=f"{heading} ▼")
            else:
                self.tree.heading(column, text=heading)

    def _selected_task(self) -> Optional[Task]:
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tasks.get(selection[0])

    def _sync_actions(self, event=None) -> None:
        selected = self._selected_task() if self.loaded else None
        self.add_button.configure(state="normal" if self.loaded else "disabled")
        self.edit_button.configure(state="normal" if selected else "disabled")
        can_complete = selected is not None and selected.status == "todo"
        self.done_button.configure(state="normal" if can_complete else "disabled")
        self.undo_button.configure(state="normal" if self.loaded else "disabled")

    def open_add(self) -> None:
        if self.loaded:
            self.current_form = TaskForm(self.root, self.controller, self._after_write)

    def open_edit(self) -> None:
        selected = self._selected_task()
        if self.loaded and selected is not None:
            self.current_form = TaskForm(
                self.root,
                self.controller,
                self._after_write,
                task=selected,
            )

    def _after_write(self, task: Task) -> None:
        self.current_form = None
        if not self.refresh():
            detail = self.status_var.get().removeprefix("Ошибка чтения: ")
            self.status_var.set(f"Изменение сохранено, но список не удалось обновить: {detail}")

    def mark_selected_done(self) -> None:
        selected = self._selected_task()
        if not self.loaded or selected is None or selected.status != "todo":
            return
        try:
            changed = self.controller.mark_done(selected.id)
        except (OSError, ValueError, TypeError, KeyError) as error:
            self.status_var.set(f"Ошибка сохранения: {error}")
            return
        if changed is None:
            self.status_var.set("Задача не найдена. Обновите список")
            return
        if not self.refresh():
            detail = self.status_var.get().removeprefix("Ошибка чтения: ")
            self.status_var.set(f"Изменение сохранено, но список не удалось обновить: {detail}")

    def undo_changes(self) -> None:
        if not self.loaded:
            return
        try:
            undone = self.controller.undo(int(self.undo_steps_var.get()))
        except (OSError, ValueError, TypeError, KeyError) as error:
            self.status_var.set(f"Ошибка undo: {error}")
            return
        if self.refresh():
            self.status_var.set(f"Отменено изменений: {undone}")
        else:
            detail = self.status_var.get().removeprefix("Ошибка чтения: ")
            self.status_var.set(f"Откат выполнен, но список не удалось обновить: {detail}")

    def validate_tasks(self) -> None:
        try:
            report = self.controller.validate_tasks()
        except (OSError, ValueError, TypeError, KeyError) as error:
            self.status_var.set(f"Ошибка проверки: {error}")
            return
        lines = ["Проверка: успешно" if report["ok"] else "Проверка: найдены проблемы"]
        labels = (("total", "Всего"), ("todo", "todo"), ("done", "done"))
        for key, label in labels:
            if key in report["counts"]:
                lines.append(f"{label}: {report['counts'][key]}")
        if report["issues"]:
            lines.append("")
            lines.append("Проблемы:")
            lines.extend(f"- {issue}" for issue in report["issues"])
        self._show_validation_report("\n".join(lines))
        self.status_var.set(lines[0])

    def _show_validation_report(self, content: str) -> None:
        self.validation_window = self.tk.Toplevel(self.root)
        self.validation_window.title("Проверка данных")
        frame = self.ttk.Frame(self.validation_window, padding=12)
        frame.grid(sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self.validation_window.columnconfigure(0, weight=1)
        self.validation_window.rowconfigure(0, weight=1)
        self.validation_report = self.tk.Text(frame, width=72, height=18, wrap="word")
        scrollbar = self.ttk.Scrollbar(
            frame, orient="vertical", command=self.validation_report.yview
        )
        self.validation_report.configure(yscrollcommand=scrollbar.set)
        self.validation_report.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.validation_report.insert("1.0", content)
        self.validation_report.configure(state="disabled")


def main() -> int:
    """Launch TaskHub in the current directory, reporting Tk startup failures."""
    try:
        tk, _ = _load_tk()
    except ImportError as error:
        print(f"Не удалось запустить TaskHub UI: {error}", file=sys.stderr)
        return 1
    try:
        root = tk.Tk()
    except tk.TclError as error:
        print(f"Не удалось запустить TaskHub UI: {error}", file=sys.stderr)
        return 1
    controller = TaskController(Storage(Path.cwd().resolve()))
    TaskHubWindow(root, controller)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
