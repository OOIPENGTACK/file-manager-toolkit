"""
AI assistance disclosure:
As stipulated by CS50 that it is reasonable to use AI-based software for the final project,
ChatGPT was used as a development aid for discussing Python features,
edge cases, and general design ideas. The program logic, structure,
and final code were written and verified by me.
"""

from pathlib import Path
import sys


def validate_directory(path: Path) -> None:
    """Ensure path exists and is a directory."""
    if not path.exists():
        sys.exit(f"Path does not exist: {path}")
    if not path.is_dir():
        sys.exit(f"Not a directory: {path}")


def collect_files(root: Path, recursive: bool = False) -> list[Path]:
    """Return list of file paths to process."""
    if recursive:
        return [p for p in root.rglob("*") if p.is_file()]
    return [p for p in root.glob("*") if p.is_file()]
