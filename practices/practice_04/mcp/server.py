#!/usr/bin/env python3
"""TaskHub validate-tasks MCP server (stdio).

Exposes one tool, validate_tasks, that checks tasks.json integrity
(schema, dates, duplicate ids). Run via OpenCode `mcp.taskhub` entry
or directly: `<venv>/bin/python practices/practice_04/mcp/server.py`.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make src/ importable regardless of cwd (same trick as tests/conftest.py)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.server.mcpserver import MCPServer  # noqa: E402

from taskhub.validate import validate_file  # noqa: E402

mcp = MCPServer("taskhub")


@mcp.tool(description="Validate tasks.json integrity: schema, dates, duplicate ids.")
def validate_tasks(path: str = "tasks.json") -> dict:
    """Check a tasks.json file. Returns {ok, issues, counts}.

    Raises an error when the file is missing or holds broken JSON.
    """
    return validate_file(path)


if __name__ == "__main__":
    mcp.run()
