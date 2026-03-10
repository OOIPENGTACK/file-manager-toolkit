"""
AI assistance disclosure:
As stipulated by CS50 that it is reasonable to use AI-based software for the final project,
ChatGPT was used as a development aid for discussing Python features,
edge cases, and general design ideas. The program logic, structure,
and final code were written and verified by me.
"""

from collections import defaultdict
from pathlib import Path
import hashlib
import logging
from utils import validate_directory, collect_files


logger = logging.getLogger(__name__)


# -------------------------------------------------
# Step 1: Group files by size (cheap pre-filter)
# -------------------------------------------------
def group_by_size(files: list[Path]) -> dict[int, list[Path]]:
    """
    Group files by file size.

    Files with different sizes cannot be duplicates, so this reduces
    the number of files that need to be hashed.
    """
    size_map = defaultdict(list)

    for path in files:
        size_map[path.stat().st_size].append(path)

    return size_map


# -------------------------------------------------
# Step 2: Hash file contents (expensive but precise)
# -------------------------------------------------
def hash_file(path: Path, chunk_size: int = 8192) -> str:
    """
    Return SHA-256 hash of a file.

    The file is read in chunks to avoid loading large files into memory.
    Files with the same hash are assumed to have identical content.
    """
    h = hashlib.sha256()

    with path.open("rb") as f:
        # Read the file chunk-by-chunk until EOF (b"")
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)

    return h.hexdigest()


# -------------------------------------------------
# Step 3: Detect duplicates by hashing same-size files
# -------------------------------------------------
def find_duplicates(size_groups: dict[int, list[Path]]) -> dict[str, list[Path]]:
    """
    Return a mapping of:
        file_hash -> list of files with identical content

    Only hashes groups where there are at least 2 files.
    """
    dupes = defaultdict(list)

    for group in size_groups.values():
        # Skip groups that cannot contain duplicates
        if len(group) < 2:
            continue

        for path in group:
            file_hash = hash_file(path)
            dupes[file_hash].append(path)

    # Keep only hashes that map to multiple files (true duplicates)
    return {h: paths for h, paths in dupes.items() if len(paths) > 1}


# -------------------------------------------------
# Heuristic: Penalize filenames that look like copies
# -------------------------------------------------
def filename_penalty(path: Path) -> int:
    """
    Return a penalty score based on filename patterns.

    Filenames that look like copies (e.g. 'copy', '(1)', 'backup')
    receive higher penalties and are more likely to be deleted.
    """
    name = path.name.lower()
    penalties = ["copy", "duplicate", "dup", "backup", "bak", "(1)", "(2)", "(3)"]

    # Each substring match adds 1 penalty point
    return sum(p in name for p in penalties)


# -------------------------------------------------
# Step 4: Decide which duplicate to keep
# -------------------------------------------------
def select_duplicates(dupes: dict[str, list[Path]]) -> list[Path]:
    """
    Decide which files to delete among each duplicate group.

    Sorting criteria (in order of importance):
    1. Filename penalty (prefer "original-looking" names)
    2. Shorter path (files closer to root often feel more canonical)
    3. Modification time (older files preferred)
    """
    to_delete = []

    for paths in dupes.values():
        # Sort by:
        # 1. filename penalty (lower is better)
        # 2. shorter path (originals often live higher)
        # 3. modification time (oldest first)
        paths_sorted = sorted(paths, key=lambda p: (
            filename_penalty(p), len(str(p)), p.stat().st_mtime))

        # Keep the best candidate, delete the rest
        to_delete.extend(paths_sorted[1:])

    return to_delete


# -------------------------------------------------
# Step 5: Report duplicates (dry-run friendly)
# -------------------------------------------------
def report_duplicates(files: list[Path], dry_run: bool = True) -> None:
    """Print what would be deleted (or is being deleted)."""
    if not files:
        logger.info("No duplicate files found.")
        return

    mode = "Preview (Dry-Run Mode)" if dry_run else "Deleting Files"
    action = "would be deleted" if dry_run else "are being deleted"

    print(f"\033[4;1m{mode}\033[0m\n")
    print(f"The following files {action}:\n")

    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    print()


# -------------------------------------------------
# Step 6: Delete files (after confirmation)
# -------------------------------------------------
def delete_files(files: list[Path]) -> None:
    """Delete duplicate files and report success/failure."""
    success = []
    failed = []

    for path in files:
        try:
            path.unlink()
        except FileNotFoundError:
            logger.warning("File not found: %s", path)
            failed.append(path)
        except PermissionError:
            logger.warning("Permission denied: %s", path)
            failed.append(path)
        except IsADirectoryError:
            logger.warning("Directory encountered, skipped: %s", path)
            failed.append(path)
        except OSError as e:
            logger.error("Error deleting %s: %s", path, e)
            failed.append(path)
        else:
            logger.info("Deleted: %s", path)
            success.append(path)

    print()

    # Print summary for successful deletion
    if success:
        print(f"\033[4;1mSuccess\033[0m\n")
        for i, path in enumerate(success, start=1):
            print(f"{i}. {path}")
        print()

    # Print summary for failed deletion
    if failed:
        print(f"\033[4;1mFailed\033[0m\n")
        for i, path in enumerate(failed, start=1):
            print(f"{i}. {path}")
        print()


# -------------------------------------------------
# Entry point for the `dedup` CLI command
# -------------------------------------------------
def run_dedup(directory: Path, recursive: bool, dry_run: bool, force: bool) -> None:
    """
    High-level workflow:
    1. Validate directory
    2. Collect files
    3. Detect duplicates
    4. Report
    5. Optionally delete
    """
    validate_directory(directory)

    paths = collect_files(directory, recursive)
    size_groups = group_by_size(paths)
    dupes = find_duplicates(size_groups)
    files = select_duplicates(dupes)

    # Deterministic output order
    files.sort()

    report_duplicates(files, dry_run)

    if dry_run or not files:
        return

    if not force:
        confirm = input("Proceed with deletion? (y/n): ").strip().lower()
        if confirm != "y":
            print("Deletion cancelled.")
            return

    delete_files(files)
