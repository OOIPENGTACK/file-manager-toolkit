"""
AI assistance disclosure:
As stipulated by CS50 that it is reasonable to use AI-based software for the final project,
ChatGPT was used as a development aid for discussing Python features,
edge cases, and general design ideas. The program logic, structure,
and final code were written and verified by me.
"""

from utils import validate_directory, collect_files
from pathlib import Path
import logging
import os
import sys
import time


# File types that Windows can reasonably handle via the shell "print" verb
# (this is intentionally conservative)
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".jpg", ".png", ".csv", ".xlsx"}

# Delay between print submissions to avoid overwhelming the print spooler
PRINT_DELAY_SECONDS = 2

logger = logging.getLogger(__name__)


# ----------------------------
# Preview / dry-run reporting
# ----------------------------
def report_files(files: list[Path], dry_run: bool = True) -> None:
    """
    Display which files would be sent to the default printer.

    In dry-run mode, this acts as a preview without submitting print jobs.
    """
    if not files:
        logger.info("No files available for printing.")
        return

    mode = "Preview (Dry-Run Mode)" if dry_run else "Printing Files"
    action = "would be printed" if dry_run else "are being printed"

    print(f"\033[4;1m{mode}\033[0m\n")
    print(f"The following files {action}:\n")

    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    print()


# ----------------------------
# Core printing logic
# ----------------------------
def bulk_print(files: list[Path]) -> None:
    """
    Submit print jobs to the system's default printer.

    Note:
    - This uses Windows Shell (os.startfile with the 'print' verb)
    - Success means the print command was accepted by Windows
    - It does NOT guarantee physical printing or printer availability
    """
    success = []
    failed = []

    for path in files:
        try:
            # Ask Windows to open the file using its associated application
            # and invoke the application's "print" action
            os.startfile(path, "print")

        except FileNotFoundError:
            logger.warning("File not found: %s", path)
            failed.append(path)

        except PermissionError:
            logger.warning("Permission denied: %s", path)
            failed.append(path)

        except OSError as e:
            # Covers shell-level or application-level failures
            logger.error("Error printing %s: %s", path, e)
            failed.append(path)

        except ValueError as e:
            # Raised if the 'print' verb is not supported
            logger.error("Invalid argument: %s", e)
            failed.append(path)

        except Exception as e:
            # Defensive catch-all to prevent one bad file from stopping the batch
            logger.exception("Unexpected error while printing %s", path)
            failed.append(path)

        else:
            # At this point, Windows accepted the print request
            logger.info("Print job submitted: %s", path)
            success.append(path)

            # Throttle submissions to avoid overwhelming the print spooler
            time.sleep(PRINT_DELAY_SECONDS)

    print()

    # ----------------------------
    # Summary output
    # ----------------------------
    if success:
        print(f"\033[4;1mPrint Jobs Submitted\033[0m\n")
        for i, path in enumerate(success, start=1):
            print(f"{i}. {path}")
        print()

    if failed:
        print(f"\033[4;1mFailed\033[0m\n")
        for i, path in enumerate(failed, start=1):
            print(f"{i}. {path}")
        print()


# ----------------------------
# Command entry point
# ----------------------------
def run_bulk_print(directory: Path, recursive: bool, dry_run: bool, force: bool) -> None:
    """
    Orchestrate the bulk printing workflow:
    - validate directory
    - collect files (optionally recursive)
    - filter printable file types
    - preview (dry-run)
    - submit print jobs
    """
    # This implementation relies on Windows Shell features
    if sys.platform != "win32":
        sys.exit("bulk_print is currently supported on Windows only.")

    validate_directory(directory)

    # Discover files and filter by allowed extensions
    files = collect_files(directory, recursive)
    to_print = [f for f in files if f.suffix.lower() in ALLOWED_EXTENSIONS]
    to_print.sort()

    # Show preview before printing
    report_files(to_print, dry_run)

    if dry_run or not to_print:
        return

    # Safety confirmation unless --force is provided
    if not force:
        confirm = input("Proceed with printing? (y/n): ").strip().lower()
        if confirm != "y":
            print("Printing cancelled.")
            return

    bulk_print(to_print)
