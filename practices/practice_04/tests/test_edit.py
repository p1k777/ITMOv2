from pathlib import Path
from typer.testing import CliRunner

from taskhub.app import app


runner = CliRunner()


def _add(monkeypatch, tmp_path: Path, title="A"):
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["init"])
    assert res.exit_code == 0
    res = runner.invoke(app, ["add", title])
    assert res.exit_code == 0
    return res.stdout.strip()


def test_cli_edit_title(tmp_path: Path, monkeypatch):
    task_id = _add(monkeypatch, tmp_path, "A")
    res = runner.invoke(app, ["edit", task_id, "--title", "B"])
    assert res.exit_code == 0
    assert task_id in res.stdout

    res = runner.invoke(app, ["list"])
    assert res.exit_code == 0
    assert "B" in res.stdout
    assert "A" not in res.stdout


def test_cli_edit_due_and_tag(tmp_path: Path, monkeypatch):
    task_id = _add(monkeypatch, tmp_path, "A")
    res = runner.invoke(
        app, ["edit", task_id, "--due", "2026-01-01T00:00:00.000000Z",
              "--tag", "demo"]
    )
    assert res.exit_code == 0

    res = runner.invoke(app, ["list"])
    assert res.exit_code == 0
    assert "2026-01-01" in res.stdout
    assert "demo" in res.stdout


def test_cli_edit_not_found(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["init"])
    assert res.exit_code == 0
    res = runner.invoke(app, ["edit", "no-such-id", "--title", "X"])
    assert res.exit_code != 0


def test_cli_edit_undo(tmp_path: Path, monkeypatch):
    task_id = _add(monkeypatch, tmp_path, "A")
    res = runner.invoke(app, ["edit", task_id, "--title", "B"])
    assert res.exit_code == 0

    res = runner.invoke(app, ["undo"])
    assert res.exit_code == 0
    assert "undo: ok (1)" in res.stdout

    res = runner.invoke(app, ["list"])
    assert res.exit_code == 0
    assert "A" in res.stdout
