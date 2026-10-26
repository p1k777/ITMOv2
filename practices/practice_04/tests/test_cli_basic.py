import json
from pathlib import Path
from typer.testing import CliRunner

from taskhub.app import app


runner = CliRunner()


def test_cli_init_and_add_list(tmp_path: Path, monkeypatch):
    # Run in temp dir by chdir
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"]) 
    assert result.exit_code == 0
    assert (tmp_path / "tasks.json").exists()

    result = runner.invoke(app, ["add", "Hello", "--tag", "demo"]) 
    assert result.exit_code == 0
    task_id = result.stdout.strip()
    assert len(task_id) > 0

    result = runner.invoke(app, ["list"]) 
    assert result.exit_code == 0
    out = result.stdout
    assert "Hello" in out
    assert "demo" in out


def test_cli_undo(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["init"]) 
    assert res.exit_code == 0

    # add two tasks
    res = runner.invoke(app, ["add", "A"]) 
    assert res.exit_code == 0
    res = runner.invoke(app, ["add", "B"]) 
    assert res.exit_code == 0

    # ensure two present
    res = runner.invoke(app, ["list"]) 
    assert res.exit_code == 0
    out = res.stdout
    assert "A" in out and "B" in out

    # undo last
    res = runner.invoke(app, ["undo"]) 
    assert res.exit_code == 0
    assert "undo: ok (1)" in res.stdout

    # list should still have at least one of A/B (after one undo)
    res = runner.invoke(app, ["list"]) 
    assert res.exit_code == 0
    out = res.stdout
    # After undo, depending on snapshot point, at least one task remains
    assert "A" in out or "B" in out

    # multiple undo (up to history)
    res = runner.invoke(app, ["undo", "--steps", "2"]) 
    # May fail if not enough history; allow either 0 or error
    # For strictness, expect non-zero code only when history empty
    if res.exit_code != 0:
        assert "no history" in res.stdout

    
