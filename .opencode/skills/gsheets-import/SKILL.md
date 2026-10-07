---
name: gsheets-import
description: Use ONLY when asked to import tasks from Google Sheets into practices/practice_04 TaskHub. Trigger on: google sheets, sheet_id, gid, range, import.
---

# Google Sheets Import

Use this skill to import rows from a public Google Sheet into TaskHub (practices/practice_04).

Inputs expected
- sheet_id: document ID from the Sheets URL
- gid: worksheet/tab ID (defaults to 0 if missing)
- range: optional A1 range (e.g., A:D or A2:D100)

Workflow
1. Build a public CSV export URL (public sheets only):
   - https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}
2. Use Playwright MCP to download the CSV to a temp file.
3. Parse CSV rows and map to [title, due, tags]:
   - title required; due (YYYY-MM-DD) and tags (comma-separated) optional
4. For each row, call CLI to add a task.

CLI commands
- If running OpenCode from repo root:
  - export PYTHONPATH=practices/practice_04/src
  - python -m taskhub.app add "<title>" --tag <tag>
- If running OpenCode from practices/practice_04:
  - export PYTHONPATH=./src
  - python -m taskhub.app add "<title>" --tag <tag>

Notes
- Sheet must be public; otherwise request a public link.
- Print a short summary: number of tasks imported.
- Helper script (optional): .opencode/skills/gsheets-import/scripts/download_csv.sh to fetch CSV when MCP is unavailable.
