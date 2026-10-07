from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Union

from .models import ISO_FORMAT

REQUIRED_FIELDS = ("id", "title", "status", "created_at")
STATUSES = ("todo", "done")


def _parse_date(value: str, field: str, issues: list[str]) -> None:
    try:
        datetime.strptime(value, ISO_FORMAT)
    except (TypeError, ValueError):
        issues.append(f"invalid {field}: {value!r}")


def validate_file(path: Union[str, Path]) -> dict:
    """Check tasks.json integrity.

    Returns {"ok": bool, "issues": [...], "counts": {...}}.
    Raises FileNotFoundError if the file is missing,
    ValueError on broken JSON.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"not found: {p} (run init?)")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"broken JSON in {p}: {e}")

    issues: list[str] = []
    if not isinstance(data, dict):
        return {"ok": False, "issues": ["root must be an object"], "counts": {}}
    if data.get("version") != 1:
        issues.append("version must be 1")
    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        issues.append("tasks must be a list")
        return {"ok": False, "issues": issues, "counts": {}}

    seen: set[str] = set()
    for i, t in enumerate(tasks):
        where = f"tasks[{i}]"
        if not isinstance(t, dict):
            issues.append(f"{where} must be an object")
            continue
        for f in REQUIRED_FIELDS:
            if f not in t:
                issues.append(f"{where} missing field: {f}")
        if t.get("status") not in STATUSES:
            issues.append(f"{where} invalid status: {t.get('status')!r}")
        if "created_at" in t:
            _parse_date(t["created_at"], "created_at", issues)
        if t.get("due_date") is not None:
            _parse_date(t["due_date"], "due_date", issues)
        tid = t.get("id")
        if tid is not None:
            if tid in seen:
                issues.append(f"duplicate id: {tid}")
            seen.add(tid)

    counts = {
        "total": len(tasks),
        "todo": sum(1 for t in tasks if isinstance(t, dict) and t.get("status") == "todo"),
        "done": sum(1 for t in tasks if isinstance(t, dict) and t.get("status") == "done"),
    }
    return {"ok": not issues, "issues": issues, "counts": counts}
