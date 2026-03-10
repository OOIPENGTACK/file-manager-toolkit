"""
AI assistance disclosure:
As stipulated by CS50 that it is reasonable to use AI-based software for the final project,
ChatGPT was used as a development aid for discussing Python features,
edge cases, and general design ideas. The program logic, structure,
and final code were written and verified by me.
"""

import argparse
from pathlib import Path
from deduplicate import run_dedup
from bulk_print import run_bulk_print
from csv_merge import run_csv_merge
import logging


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    parser = argparse.ArgumentParser(description="A simple file manager toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add dedup_parser branch
    dedup_parser = subparsers.add_parser("dedup", help="Find and delete duplicate files")
    dedup_parser.add_argument("directory", help="Target directory (quote paths containing spaces)")
    dedup_parser.add_argument("-r", "--recursive", action="store_true",
                              help="Search subdirectories")
    dedup_parser.add_argument("-n", "--dry-run", action="store_true",
                              help="Preview duplicate files without deleting")
    dedup_parser.add_argument("-f", "--force", action="store_true",
                              help="Delete without confirmation")

    # Add batch-print parser branch
    print_parser = subparsers.add_parser(
        "print", help="Batch-print files (PDF, DOCX, etc.) — Windows only")
    print_parser.add_argument("directory", help="Target directory (quote paths containing spaces)")
    print_parser.add_argument("-r", "--recursive", action="store_true",
                              help="Search subdirectories")
    print_parser.add_argument("-n", "--dry-run", action="store_true",
                              help="Preview without executing")
    print_parser.add_argument("-f", "--force", action="store_true",
                              help="Print without confirmation")

    # Add CSV-merge parser branch
    csv_parser = subparsers.add_parser("csv_merge", help="Merge CSVs")
    csv_parser.add_argument("directory", help="Target directory (quote paths containing spaces)")
    csv_parser.add_argument("--header-row", type=int, default=1,
                            help="Row number containing column headers (1-based, default: 1)")
    csv_parser.add_argument("-n", "--dry-run", action="store_true",
                            help="Preview CSV files without merging")
    csv_parser.add_argument("-o", "--output", type=Path,
                            help="Output CSV filename (default: merged.csv)")
    csv_parser.add_argument("-f", "--force", action="store_true",
                            help="Merge CSVs without confirmation")

    args = parser.parse_args()

    if args.command == "dedup":
        run_dedup(
            directory=Path(args.directory),
            recursive=args.recursive,
            dry_run=args.dry_run,
            force=args.force,
        )

    elif args.command == "print":
        run_bulk_print(
            directory=Path(args.directory),
            recursive=args.recursive,
            dry_run=args.dry_run,
            force=args.force,
        )

    elif args.command == "csv_merge":
        run_csv_merge(
            directory=Path(args.directory),
            dry_run=args.dry_run,
            output=args.output,
            force=args.force,
            header_row=args.header_row
        )


if __name__ == "__main__":
    main()
