---
name: tdd-guide
description: Use ONLY to help implement or change features in practices/practice_04 TaskHub via TDD. Trigger on keywords: pytest, tests, clip, CLI, taskhub.
---

# TDD Guide for TaskHub (Practice 04)

Use this skill to drive a minimal TDD workflow for new or changed CLI behavior in TaskHub.

Scope
- Project: practices/practice_04
- Features: CLI commands (e.g., clip), storage behavior, small refactors

Workflow
1. Identify acceptance: e.g., Web Clip To Task
   - Input: URL like https://example.com
   - Expected: a new task with text "Title (https://example.com)"
2. Add/adjust tests under practices/practice_04/tests using pytest and Typer's CliRunner
3. Implement the minimum code to satisfy failing tests (src/taskhub/app.py)
4. Run tests: `pytest -q`
5. Iterate until green, then refactor small duplication if needed

Commands (from repo root)
- export PYTHONPATH=practices/practice_04/src
- python -m taskhub.app add "Title (URL)"
- pytest -q

Notes
- Keep changes minimal and local to practices/practice_04
- Prefer app-level tests for CLI behavior; unit tests for storage
