---
name: gsheets-import
description: Use ONLY when asked to import tasks from Google Sheets into practices/practice_04 TaskHub. Trigger on keywords: google sheets, sheet_id, gid, range, import-gsheet, csv export.
---

# Google Sheets Import

Use this skill to import rows from a Google Sheet into the TaskHub tasks.json in practices/practice_04.

Inputs expected
- sheet_id: the document ID from sheets URL.
- gid: the worksheet/tab ID (defaults to 0 if not provided).
- range: optional A1 range (e.g., A:D or A2:D100). If not provided, import all columns and rows.

Workflow
1. If the sheet is public, build the CSV export URL:
   - https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}
2. Fetch the CSV using the Browser MCP (Playwright) and produce a local CSV file.
3. Parse rows into [title, due, tags] columns:
   - title is required; due (YYYY-MM-DD) and tags (comma-separated) are optional.
4. For each row, call the CLI:
   - export PYTHONPATH=practices/practice_04/src
   - python -m taskhub.app add "<title>" --tag <tag1> (repeat for tags as needed)

Notes
- If the sheet is not public, request a public link or a CSV export file instead.
- Keep outputs concise: print how many tasks were imported.
