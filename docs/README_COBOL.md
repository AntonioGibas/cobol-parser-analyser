# src/cobol_parser.py

## Overview
This module performs static analysis on COBOL source files (`.txt` or `.cbl`) to extract structural information required for graphing and documentation.

## Responsibilities
* **Parsing:** Reads COBOL files from `base/source/`.
* **Extraction:** Identifies the Program's structural elements:
    * `PROGRAM-ID` (Program Name)
    * `COPY` statements (External dependencies, e.g., Copybooks)
    * `PERFORM` statements (Internal procedure calls)
* **Output:** Generates `analysis_results.json` containing the structural data for all processed programs.
* **Error Handling:** Logs errors related to file encoding (e.g., UnicodeDecodeError) and warnings for missing `PROGRAM-ID`.

## Key Function
* `pokreni_cobol_parser(source_dir, output_file, logger)`: Main entry point for COBOL processing.