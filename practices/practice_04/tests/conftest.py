import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]

# Make src/ importable as top-level packages (taskhub)
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

"""Pytest configuration for the raw project."""
