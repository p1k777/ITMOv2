import json
from pathlib import Path

import pytest

from taskhub.validate import validate_file


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _valid_doc():
    return {
        "version": 1,
        "tasks": [
            {
                "id": "a1",
                "title": "A",
                "status": "todo",
                "created_at": "2026-01-01T00:00:00.000000Z",
                "due_date": None,
                "tags": ["x"],
            }
        ],
    }


def test_validate_ok(tmp_path: Path):
    p = _write(tmp_path / "tasks.json", _valid_doc())
    res = validate_file(p)
    assert res["ok"] is True
    assert res["issues"] == []


def test_validate_duplicate_ids(tmp_path: Path):
    doc = _valid_doc()
    doc["tasks"].append({**doc["tasks"][0], "title": "B"})
    p = _write(tmp_path / "tasks.json", doc)
    res = validate_file(p)
    assert res["ok"] is False
    assert any("duplicate id" in i for i in res["issues"])


def test_validate_bad_due_date(tmp_path: Path):
    doc = _valid_doc()
    doc["tasks"][0]["due_date"] = "tomorrow"
    p = _write(tmp_path / "tasks.json", doc)
    res = validate_file(p)
    assert res["ok"] is False
    assert any("due_date" in i for i in res["issues"])


def test_validate_bad_status(tmp_path: Path):
    doc = _valid_doc()
    doc["tasks"][0]["status"] = "later"
    p = _write(tmp_path / "tasks.json", doc)
    res = validate_file(p)
    assert res["ok"] is False
    assert any("status" in i for i in res["issues"])


def test_validate_bad_schema(tmp_path: Path):
    p = _write(tmp_path / "tasks.json", {"version": 2})
    res = validate_file(p)
    assert res["ok"] is False


def test_validate_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        validate_file(tmp_path / "nope.json")


def test_validate_broken_json(tmp_path: Path):
    p = tmp_path / "tasks.json"
    p.write_text("{oops", encoding="utf-8")
    with pytest.raises(ValueError):
        validate_file(p)
