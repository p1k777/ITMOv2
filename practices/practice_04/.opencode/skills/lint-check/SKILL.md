---
name: lint-check
description: Fix TaskHub lint/style violations via TDD loop for practices/practice_04. Trigger on keywords: lint, style guide, pre-commit, validation.
---

# Skill: lint-check (practice_04)

Project-local skill: drives the model (not a script) to fix
`tools/lint.py` violations in product code per `STYLE_GUIDE.md`,
then verifies with tests. Runner script is only an entrypoint;
all fixing decisions are made by the agent following this playbook.

## When to use

- `tools/lint.py` reports FAIL after an edit in `practices/practice_04/`.
- User asks to run the linter, check style, or prepare code for commit.
- Before presenting/merging work in `practices/practice_04`.

## Inputs

- Linter: `python3 practices/practice_04/tools/lint.py` (check-only,
  never auto-fixes; exit 1 on any violation).
- Style contract: `practices/practice_04/STYLE_GUIDE.md`.
- Tests: `python3 -m pytest -q` (from repo root).
- Venv: `practices/practice_04/.venv` (create + install `pytest`,
  `typer` if missing). Quick entrypoint:
  `bash practices/practice_04/.opencode/skills/lint-check/run_lint.sh`.

## Workflow (TDD loop)

1. Diagnose: run `lint.py`, collect the full issue list. Do not edit
   code yet.
2. Classify each issue and fix product code (never the linter):
   - Mechanics (trailing whitespace, missing EOF newline): fix
     directly in place.
   - Line length (>100 chars): rewrap by hand. Split call args one
     per line or extract a helper; keep the change minimal.
   - Contract violations (`STORAGE`/`MODELS`/`APP` prefixes): fix the
     product code to satisfy the `STYLE_GUIDE.md` invariant
     (snapshot before write, `indent=2`, `ISO_FORMAT`, CLI output
     format, non-zero exits). If the invariant itself looks wrong,
     stop and ask the user instead of forcing the code.
3. Hard rule: editing `tools/lint.py` (or adding `lint: allow-long`)
   to make checks pass is forbidden. Only product code changes.
4. Verify: re-run `lint.py` until `taskhub-lint: ok`, then run
   `pytest -q` until green. One fix iteration = one minimal edit,
   then re-check (red → green → refactor if needed).

## Success criteria

- `lint.py` exits 0 (`taskhub-lint: ok`).
- `pytest -q` exits 0 (all `practices/practice_04/tests` green).
- Diff touches only `practices/practice_04/` product/test code;
  no new dependencies.

## Failure handling

- Contract check still red after a fix attempt: stop, report the
  rule from `STYLE_GUIDE.md` and the conflicting code, ask the user.
- Tests red after lint is green: treat as normal TDD — write/adjust
  the failing case first, then minimal implementation.
