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


def test_cli_clip(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    res = runner.invoke(app, ["init"]) 
    assert res.exit_code == 0

    url = "https://example.com"
    res = runner.invoke(app, ["clip", "--url", url])
    assert res.exit_code == 0
    task_id = res.stdout.strip()
    assert len(task_id) > 0

    res = runner.invoke(app, ["list"]) 
    assert res.exit_code == 0
    out = res.stdout
    assert "(https://example.com)" in out
