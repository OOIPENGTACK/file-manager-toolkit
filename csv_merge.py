"""
AI assistance disclosure:
As stipulated by CS50 that it is reasonable to use AI-based software for the final project,
ChatGPT was used as a development aid for discussing Python features,
edge cases, and general design ideas. The program logic, structure,
and final code were written and verified by me.
"""

from utils import validate_directory, collect_files
from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError, ParserError
import logging


logger = logging.getLogger(__name__)


# ----------------
# Count CSV lines
# ----------------
def get_line_count(path: Path) -> int:
    with path.open(encoding="utf-8", errors="ignore") as f:
        return sum(1 for _ in f)


# -----------------------------------------------
# Read CSV files collected from target directory
# -----------------------------------------------
def csv_read(files: list[Path], header_row: int) -> tuple[list[pd.DataFrame], list[Path]]:
    """
    Read CSV files into pandas DataFrames.

    Returns:
        frames  : list of successfully read DataFrames in the same order as `success`
        success : list of CSV Paths that were successfully read
    """
    frames = []
    success = []

    if header_row < 1:
        raise ValueError("header_row must be >= 1")

    skiprows = header_row - 1

    # Sort for deterministic processing order
    for path in sorted(files):
        try:
            line_count = get_line_count(path)

            if header_row > line_count:
                logger.warning(
                    "Header row %d exceeds total rows (%d) in %s — skipped",
                    header_row,
                    line_count,
                    path,
                )
                continue

            # Use python engine for more tolerant parsing (e.g. commas inside cells)
            df = pd.read_csv(path, skiprows=skiprows, header=0, engine="python", encoding="utf-8")

            if df.empty:
                logger.warning("CSV has headers only, no data: %s", path)
                continue

        except FileNotFoundError:
            logger.warning("File not found: %s", path)
        except PermissionError:
            logger.warning("Permission denied: %s", path)
        except EmptyDataError:
            logger.warning("Empty CSV skipped: %s", path)
        except ParserError:
            logger.warning("File could not be parsed: %s", path)
        except Exception as e:
            # Catch-all to prevent one bad file from crashing the entire merge
            logger.warning("Unexpected error reading %s: %s", path, e)
        else:
            logger.info("CSV read: %s (%d rows)", path, len(df))
            frames.append(df)
            success.append(path)

    return frames, success


# ----------------------------
# Preview / dry-run reporting
# ----------------------------
def report_csv(files: list[Path], dry_run: bool = True) -> None:
    """
    Display which CSV files will be merged.

    In dry-run mode, this acts as a preview without performing any merge.
    """
    if not files:
        logger.info("No valid CSV files to merge.")
        return

    mode = "Preview (Dry-Run Mode)" if dry_run else "Merging CSV(s)"
    action = "would be merged" if dry_run else "are being merged"

    print(f"\033[4;1m{mode}\033[0m\n")
    print(f"The following CSV(s) {action}:\n")

    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    print()


# ----------------------------
# Command entry point
# ----------------------------
def run_csv_merge(directory: Path, dry_run: bool, force: bool, output: Path | None, header_row: int = 1) -> None:
    """
    Orchestrate the CSV merge process:
    - validate directory
    - discover CSV files
    - preview merge (dry-run)
    - merge and write output CSV
    """
    validate_directory(directory)

    # Collect only .csv files in the target directory
    csv_files = [p for p in collect_files(directory) if p.suffix.lower() == ".csv"]

    if not csv_files:
        logger.warning("No CSV files found in directory.")
        return

    print()

    # Read CSV files into DataFrames
    try:
        logger.info("Using header row: %d", header_row)
        frames, success = csv_read(csv_files, header_row)
    except ValueError as e:
        logger.error(str(e))
        return

    if not frames:
        return

    print()

    # Show preview before merging
    report_csv(success, dry_run)

    if dry_run:
        return

    # Safety confirmation unless --force is provided
    if not force:
        confirm = input("Proceed with merging? (y/n): ").strip().lower()
        if confirm != "y":
            print("Merging cancelled.")
            return

    # Concatenate DataFrames, auto-aligning columns
    merged = pd.concat(frames, ignore_index=True, sort=False)

    # Sort rows by the first column if at least one column exists
    if merged.columns.size > 0:
        merged = merged.sort_values(by=merged.columns[0], kind="stable")

    # Determine output path
    if output is None:
        output = directory / "merged.csv"
    elif output.suffix.lower() != ".csv":
        output = output.with_suffix(".csv")

    # Resolve relative paths against the target directory
    if not output.is_absolute():
        output = directory / output

    # Fail safely if output directory does not exist
    if not output.parent.exists():
        logger.error("Output directory does not exist: %s", output.parent)
        return

    # Write merged CSV to disk
    merged.to_csv(output, index=False)

    # Final summary logs
    logger.info("Merged CSV written to %s (%d rows)", output, len(merged))
    logger.info("Merged %d CSV(s), skipped %d", len(success), len(csv_files) - len(success))

    print()
