from __future__ import annotations

import json
from pathlib import Path
import shutil
import time
from typing import List, Optional

from .models import Task


DEFAULT_DB = "tasks.json"
HISTORY_DIR = ".taskhub/history"


class Storage:
    """Simple JSON-file storage with minimal schema and safe reads/writes."""

    def __init__(self, root: Path):
        self.root = root
        self.path = self.root / DEFAULT_DB
        self.history_dir = self.root / HISTORY_DIR

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
        # Snapshot current state before overwriting (if any)
        self._snapshot_current()
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

    # ---- history / undo ----
    def _snapshot_current(self) -> None:
        """Save a pre-image of tasks.json into the history ring (max 3)."""
        if not self.path.exists():
            return
        try:
            self.history_dir.mkdir(parents=True, exist_ok=True)
            ts = int(time.time() * 1000)
            snap = self.history_dir / f"{ts}.json"
            shutil.copyfile(self.path, snap)
            # prune older snapshots, keep latest 3
            snaps = sorted(self.history_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            for old in snaps[3:]:
                try:
                    old.unlink()
                except Exception:
                    pass
        except Exception:
            # History must not block write path
            pass

    def undo(self, steps: int = 1) -> int:
        """Restore from history by N steps. Returns number of steps undone.

        Raises ValueError if not enough history.
        """
        if steps < 1:
            raise ValueError("steps must be >= 1")
        snaps = sorted(self.history_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if len(snaps) < steps:
            raise ValueError("no history to undo")
        undone = 0
        for i in range(steps):
            snap = sorted(self.history_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not snap:
                break
            latest = snap[0]
            # restore atomically
            tmp = self.path.with_suffix(".tmp")
            shutil.copyfile(latest, tmp)
            tmp.replace(self.path)
            try:
                latest.unlink()
            except Exception:
                pass
            undone += 1
        return undone
