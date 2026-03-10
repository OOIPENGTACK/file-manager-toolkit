![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Cross--platform-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)
# File Manager Toolkit
## Overview

The **File Manager Toolkit** is a command-line utility written in Python that provides several practical file management operations commonly needed in day-to-day workflows. The toolkit is designed as a single CLI program with multiple subcommands, allowing users to perform different tasks without switching tools or scripts.

Currently, the toolkit supports three main features:

1. **File Deduplication** – Detect and optionally delete duplicate files based on file content.
2. **Bulk Printing** – Send multiple supported files to the default printer in one operation (Windows only).
3. **CSV Merging** – Merge multiple CSV files into a single consolidated CSV with configurable header handling.

This project was built as a CS50x Final Project and focuses on clean program structure, defensive programming, and real-world usability rather than theoretical algorithms alone.

---
## Design Goals and Philosophy

Several guiding principles shaped the design of this project:

**Safety first**: All destructive actions (deleting files, printing, merging) support a dry-run mode and require confirmation unless explicitly overridden.

**Single responsibility per module**: Each major feature is implemented in its own file, improving readability and maintainability.

**User-friendly CLI design**: The program uses subcommands and flags similar to standard UNIX tools, making it intuitive to use.

**Graceful failure handling**: Errors in one file should not crash the entire operation.

These goals influenced both the code structure and the specific design decisions explained below.


---

## Project Structure
```
File Manager Toolkit
│
├── main.py # CLI entry point and argument parsing
├── deduplicate.py # Duplicate file detection and deletion
├── bulk_print.py # Bulk printing logic (Windows only)
├── csv_merge.py # CSV merging logic
├── utils.py # Shared helper functions
└── README.md
```

---

## main.py

`main.py` is the entry point of the application. It defines the command-line interface using Python’s `argparse` module.

The program is structured around subcommands, allowing the user to run:

- `dedup` – for file deduplication

- `print` – for bulk printing

- `csv_merge` – for CSV merging

Each subcommand has its own arguments and flags, such as `--recursive`, `--dry-run`, and `--force`. The CLI also explicitly informs users when paths containing spaces must be quoted, improving usability.

The role of `main.py` is orchestration only — it parses arguments and delegates actual work to the corresponding module.

---

## utils.py

`utils.py` contains helper functions shared across multiple modules:

- `validate_directory`: Ensures the provided path exists and is a directory before any operation begins. If validation fails, the program exits early with a clear message.

- `collect_files`: Gathers files from a directory, either non-recursively or recursively using `Path.glob` and `Path.rglob`. Centralizing this logic avoids duplication and ensures consistent behavior across features.

Keeping shared logic in `utils.py` improves code reuse and reduces coupling between modules.

---

## deduplicate.py

This module implements file deduplication based on **file content**, not filenames. The process works in several stages:

1. **Grouping by file size** – Files with different sizes cannot be duplicates, so this acts as an optimization.
2. **Hashing file contents** – Files of the same size are hashed using SHA-256 to generate a reliable fingerprint.
3. **Duplicate detection** – Files with identical hashes are considered duplicates.
4. **Selection logic** – When duplicates are found, heuristics are applied to decide which file to keep.

Several heuristics are combined to make a reasonable choice:
- Filename penalties for words like “copy” or “backup”

- Shorter file paths are favored

- Older files are preferred over newer ones

This approach is not perfect, but it mirrors how a human might identify “original” files and works well in practice.

---

## bulk_print.py

`bulk_print.py` allows users to send multiple files to the default system printer in one operation. Supported file types include PDFs, documents, images, spreadsheets, and CSV files.

Important design notes:

- **Windows only**: Printing relies on `os.startfile(..., "print")`, which is only available on Windows.

- **Print job submission vs. completion**: The program logs success when a print job is successfully submitted to the OS, not when it physically prints. This distinction is explicitly reflected in logging and output messages.

- **Rate limiting**: A small delay is introduced between print jobs to prevent overwhelming the print spooler.

The module includes dry-run previews and confirmation prompts to avoid accidental printing

---

## csv_merge.py

This module merges multiple CSV files into a single output file. It was designed to handle real-world CSV inconsistencies safely.

Key features include:

- **Custom header row selection** – Users can specify which row contains column headers.

- **Pre-validation of CSV structure** – Files where the header row exceeds total rows are skipped.

- **Graceful error handling** – Corrupt or unreadable CSV files do not crash the merge.

- **Stable sorting** – The merged output is sorted by the first column using a stable sort to preserve relative order.

The merging logic uses pandas for reliability while carefully guarding against edge cases such as empty files or malformed data.

---

## Example Usage

```bash
python main.py dedup "C:\Users\Name\Downloads" --recursive --dry-run
python main.py print "C:\Users\Name\Downloads" --recursive --dry-run
python main.py csv_merge "C:\Users\Name\Downloads" --header-row 2 -o combined.csv
```
---

## Conclusion

The File Manager Toolkit demonstrates how multiple practical utilities can be combined into a cohesive, user-friendly command-line application. It emphasizes defensive programming, modular design, and thoughtful user interaction.

Rather than focusing on a single algorithm, this project showcases how real-world tools must balance correctness, safety, and usability — a lesson that strongly aligns with the goals of CS50.

---

## Installation & Requirements

### Requirements
- Python 3.10+

- Required libraries:
  - `pandas` (for CSV merging): Pandas is ideal for merging CSVs by rows and columns and handling messy data better than basic parsing. [**READMORE**](https://pandas.pydata.org/docs/reference/index.html)

Install dependencies:
```bash
pip install pandas
```
