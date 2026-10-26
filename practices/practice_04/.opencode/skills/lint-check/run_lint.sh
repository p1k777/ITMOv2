#!/usr/bin/env bash
set -euo pipefail

# Resolve practice dir relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRACTICE_DIR="$(cd "$SCRIPT_DIR/../../../" && pwd)"

VENVDIR="$PRACTICE_DIR/.venv"
PY="python3"

if [ -x "$VENVDIR/bin/python" ]; then
  PY="$VENVDIR/bin/python"
else
  echo "[lint-check] Creating venv at $VENVDIR"
  python3 -m venv "$VENVDIR"
  PY="$VENVDIR/bin/python"
  "$PY" -m pip install -q --upgrade pip
  "$PY" -m pip install -q pytest typer || true
fi

echo "[lint-check] Running linter"
"$PY" "$PRACTICE_DIR/tools/lint.py"

echo "[lint-check] Running tests"
"$PY" -m pytest -q

echo "[lint-check] OK"
