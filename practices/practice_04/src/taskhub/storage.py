from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from .models import Task


DEFAULT_DB = "tasks.json"


class Storage:
    """Simple JSON-file storage with minimal schema and safe reads/writes."""

    def __init__(self, root: Path):
        self.root = root
        self.path = self.root / DEFAULT_DB

    def init(self) -> None:
        if not self.root.exists():
            self.root.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"version": 1, "tasks": []})

    def load(self) -> dict:
        if not self.path.exists():
            self.init()
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(self.path)

    def save_tasks(self, tasks: List[Task]) -> None:
        data = {"version": 1, "tasks": [t.to_dict() for t in tasks]}
        self._write(data)

    def list_tasks(self, status: Optional[str] = None, tag: Optional[str] = None) -> List[Task]:
        data = self.load()
        tasks = [Task(**t) for t in data.get("tasks", [])]
        if status:
            tasks = [t for t in tasks if t.status == status]
        if tag:
            tasks = [t for t in tasks if tag in t.tags]
        return tasks

    def add_task(self, task: Task) -> Task:
        data = self.load()
        tasks = [Task(**t) for t in data.get("tasks", [])]
        tasks.append(task)
        self.save_tasks(tasks)
        return task

    def mark_done(self, task_id: str) -> Optional[Task]:
        data = self.load()
        tasks = [Task(**t) for t in data.get("tasks", [])]
        found: Optional[Task] = None
        for t in tasks:
            if t.id == task_id:
                t.status = "done"
                found = t
                break
        if found:
            self.save_tasks(tasks)
        return found
