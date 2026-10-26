#!/usr/bin/env python3
"""
TaskHub linter for practice_04.

Checks a subset of STYLE_GUIDE.md rules specific to this project:
- tasks.json write contract in storage.py (atomic replace, utf-8, indent=2, ensure_ascii=False,
  snapshot before write, constants)
- models.py Task shape and time/uuid helpers
- app.py CLI output/exit code patterns for list/done/undo
- line length <= 100 for src/ and tests/

Exit code:
- 0 if all checks pass
- 1 if any issue is found
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Determine practice directory as the parent of tools/
PRACTICE_DIR = Path(__file__).resolve().parents[1]
SRC = PRACTICE_DIR / "src"
TESTS = PRACTICE_DIR / "tests"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def check_line_length(paths: list[Path], max_len: int = 100) -> list[str]:
    issues: list[str] = []
    for p in paths:
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
            if len(line) > max_len and "lint: allow-long" not in line:
                issues.append(f"LINE-LENGTH {p}:{i} length={len(line)} > {max_len}")
    return issues


def check_storage(storage_path: Path) -> list[str]:
    issues: list[str] = []
    code = read_text(storage_path)
    if not code:
        return [f"MISSING {storage_path}"]

    # Constants
    if 'DEFAULT_DB = "tasks.json"' not in code:
        issues.append("STORAGE constants: DEFAULT_DB must be 'tasks.json'")
    if 'HISTORY_DIR = ".taskhub/history"' not in code:
        issues.append("STORAGE constants: HISTORY_DIR must be '.taskhub/history'")

    # Write pipeline: snapshot before json.dump, tmp.replace
    idx_snapshot = code.find("_snapshot_current(")
    idx_dump = code.find("json.dump(")
    if idx_snapshot == -1:
        issues.append("STORAGE: _snapshot_current() must be called before write")
    if idx_dump == -1:
        issues.append("STORAGE: json.dump must be used to write data")
    if idx_snapshot != -1 and idx_dump != -1 and not (idx_snapshot < idx_dump):
        issues.append("STORAGE: snapshot must happen before json.dump (pre-image)")
    if ".tmp" not in code or "tmp.replace(self.path)" not in code:
        issues.append("STORAGE: must write to .tmp and replace atomically")

    # JSON dump options
    if not re.search(r"json\.dump\([^)]*ensure_ascii\s*=\s*False", code):
        issues.append("STORAGE: json.dump must set ensure_ascii=False")
    if not re.search(r"json\.dump\([^)]*indent\s*=\s*2", code):
        issues.append("STORAGE: json.dump must set indent=2")

    # Undo behavior: limit 3 snapshots and error message
    if "no history to undo" not in code:
        issues.append("STORAGE: undo must raise 'no history to undo' on insufficient history")
    if not re.search(r"for old in snaps\[3:\]:", code):
        issues.append("STORAGE: history ring must prune to latest 3 snapshots")

    return issues


def check_models(models_path: Path) -> list[str]:
    issues: list[str] = []
    code = read_text(models_path)
    if not code:
        return [f"MISSING {models_path}"]

    # ISO format with Z
    if 'ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"' not in code:
        issues.append("MODELS: ISO_FORMAT must end with 'Z'")
    if "datetime.utcnow().strftime(ISO_FORMAT)" not in code:
        issues.append("MODELS: now_iso must use UTC and ISO_FORMAT")

    # Task dataclass fields
    expected_fields = ["id:", "title:", "status:", "created_at:", "due_date:", "tags:"]
    for fld in expected_fields:
        if fld not in code:
            issues.append(f"MODELS: Task must define field {fld.split(':')[0]}")

    # tags default_factory
    if "tags: List[str] = field(default_factory=list)" not in code:
        issues.append("MODELS: tags must use default_factory=list")

    # status default todo
    if 'status: str = "todo"' not in code:
        issues.append('MODELS: status default must be "todo"')

    # UUID4 in Task.new
    if "uuid.uuid4()" not in code:
        issues.append("MODELS: Task.new must use uuid.uuid4() for id")

    return issues


def check_app(app_path: Path) -> list[str]:
    issues: list[str] = []
    code = read_text(app_path)
    if not code:
        return [f"MISSING {app_path}"]

    # list output format markers: look for f-string with [{t.status}] and (due=... tags=...)
    list_fmt_ok = any(
        ("typer.echo(f\"" in line or "typer.echo(f'" in line)
        and "[{t.status}]" in line
        and "(due=" in line
        and "tags=" in line
        for line in code.splitlines()
    )
    if not list_fmt_ok:
        issues.append(
            "APP: list output must include status in brackets and '(due=... tags=...)' section"
        )

    # undo prints exact prefix
    if 'typer.echo(f"undo: ok (' not in code:
        issues.append("APP: undo must print 'undo: ok (N)'")

    # done error exit code
    if "raise typer.Exit(code=1)" not in code:
        issues.append("APP: error paths must exit with non-zero via typer.Exit(code=1)")

    return issues


def gather_py_files() -> list[Path]:
    return [
        p
        for base in (SRC, TESTS)
        for p in base.rglob("*.py")
        if p.is_file()
    ]


def main() -> int:
    issues: list[str] = []
    py_files = gather_py_files()
    issues += check_line_length(py_files, max_len=100)
    issues += check_storage(SRC / "taskhub" / "storage.py")
    issues += check_models(SRC / "taskhub" / "models.py")
    issues += check_app(SRC / "taskhub" / "app.py")

    if issues:
        print("taskhub-lint: FAIL")
        for msg in issues:
            print(f" - {msg}")
        return 1
    print("taskhub-lint: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
