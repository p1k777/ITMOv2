---
name: lint-check
description: Run TaskHub project linter and pytest for practices/practice_04. Trigger on keywords: lint, style guide, pre-commit, validation.
---

# Skill: lint-check (practice_04)

Purpose
- Run the project linter and tests for practices/practice_04.
- Ensure STYLE_GUIDE invariants and green tests before committing or presenting.

How to run (agent)
1. Prefer project venv at practices/practice_04/.venv. If missing, create it and install pytest, typer.
2. Execute linter: tools/lint.py
3. Execute tests: pytest -q

Commands
- bash practices/practice_04/.opencode/skills/lint-check/run_lint.sh

Success criteria
- Linter exits 0 (prints "taskhub-lint: ok").
- Pytest exits 0.

Notes
- This skill is project-local (under practices/practice_04/.opencode/skills). Add this path to skills search if needed, or call the script directly.
