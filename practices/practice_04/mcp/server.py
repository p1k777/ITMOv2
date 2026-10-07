#!/usr/bin/env python3
"""TaskHub MCP server (stdio).

Exposes TaskHub storage operations as tools: init, list, add,
mark_done, edit, undo, plus validate_tasks for tasks.json integrity.
Run via OpenCode `mcp.taskhub` entry or directly:
`<venv>/bin/python practices/practice_04/mcp/server.py`.

Paths resolve from the server working directory (workspace root).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Make src/ importable regardless of cwd (same trick as tests/conftest.py)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.server.mcpserver import MCPServer  # noqa: E402

from taskhub.models import Task  # noqa: E402
from taskhub.storage import Storage  # noqa: E402
from taskhub.validate import validate_file  # noqa: E402

mcp = MCPServer("taskhub")


def _storage(root: str = ".") -> Storage:
    st = Storage(Path(root))
    st.init()
    return st


@mcp.tool(description="Initialize tasks.json storage. Returns its path.")
def init_storage(root: str = ".") -> dict:
    """Create tasks.json if missing."""
    st = _storage(root)
    return {"ok": True, "path": str(st.path)}


@mcp.tool(description="List tasks, optionally filtered by status and tag.")
def list_tasks(
    status: Optional[str] = None,
    tag: Optional[str] = None,
    root: str = ".",
) -> dict:
    """Return {ok, tasks} with serialized tasks."""
    st = _storage(root)
    tasks = [t.to_dict() for t in st.list_tasks(status=status, tag=tag)]
    return {"ok": True, "tasks": tasks}


@mcp.tool(description="Add a task with optional due date and tag.")
def add_task(
    title: str,
    due: Optional[str] = None,
    tag: Optional[str] = None,
    root: str = ".",
) -> dict:
    """Add a task. Returns {ok, id}."""
    st = _storage(root)
    task = Task.new(title=title, due_date=due, tags=[tag] if tag else [])
    st.add_task(task)
    return {"ok": True, "id": task.id}


@mcp.tool(description="Mark a task as done by id.")
def mark_done(task_id: str, root: str = ".") -> dict:
    """Mark done. Returns {ok, id} or {ok: False, error}."""
    st = _storage(root)
    t = st.mark_done(task_id)
    if not t:
        return {"ok": False, "error": f"not found: {task_id}"}
    return {"ok": True, "id": t.id}


@mcp.tool(description="Edit task fields (title, due date, tag) by id.")
def edit_task(
    task_id: str,
    title: Optional[str] = None,
    due: Optional[str] = None,
    tag: Optional[str] = None,
    root: str = ".",
) -> dict:
    """Edit a task. Omitted fields stay unchanged."""
    st = _storage(root)
    tags = [tag] if tag is not None else None
    t = st.edit_task(task_id, title=title, due_date=due, tags=tags)
    if not t:
        return {"ok": False, "error": f"not found: {task_id}"}
    return {"ok": True, "id": t.id}


@mcp.tool(description="Undo last N modifications to tasks.json (max 3).")
def undo_tasks(steps: int = 1, root: str = ".") -> dict:
    """Undo history steps. Returns {ok, undone} or {ok: False, error}."""
    st = _storage(root)
    try:
        undone = st.undo(steps=steps)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "undone": undone}


@mcp.tool(description="Validate tasks.json integrity: schema, dates, duplicate ids.")
def validate_tasks(path: str = "tasks.json") -> dict:
    """Check a tasks.json file. Returns {ok, issues, counts}.

    Raises an error when the file is missing or holds broken JSON.
    """
    return validate_file(path)


if __name__ == "__main__":
    mcp.run()
