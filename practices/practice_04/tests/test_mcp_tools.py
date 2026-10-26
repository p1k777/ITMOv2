import sys
from pathlib import Path

MCP_DIR = Path(__file__).resolve().parents[1] / "mcp"
if str(MCP_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_DIR))

import server  # noqa: E402


def test_mcp_init_and_list_empty(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    res = server.init_storage()
    assert res["ok"] is True
    res = server.list_tasks()
    assert res["ok"] is True
    assert res["tasks"] == []


def test_mcp_add_and_list(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    server.init_storage()
    res = server.add_task("Hello", tag="demo")
    assert res["ok"] is True
    task_id = res["id"]
    assert len(task_id) > 0

    res = server.list_tasks()
    assert res["ok"] is True
    assert any(t["title"] == "Hello" for t in res["tasks"])


def test_mcp_done_and_filter(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    server.init_storage()
    task_id = server.add_task("A")["id"]
    res = server.mark_done(task_id)
    assert res == {"ok": True, "id": task_id}

    res = server.list_tasks(status="done")
    assert [t["id"] for t in res["tasks"]] == [task_id]


def test_mcp_done_missing(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    server.init_storage()
    res = server.mark_done("no-such-id")
    assert res["ok"] is False


def test_mcp_edit_and_undo(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    server.init_storage()
    task_id = server.add_task("A")["id"]
    res = server.edit_task(task_id, title="B")
    assert res == {"ok": True, "id": task_id}

    res = server.undo_tasks()
    assert res == {"ok": True, "undone": 1}

    res = server.list_tasks()
    assert [t["title"] for t in res["tasks"]] == ["A"]


def test_mcp_undo_empty(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    server.init_storage()
    res = server.undo_tasks()
    assert res["ok"] is False
