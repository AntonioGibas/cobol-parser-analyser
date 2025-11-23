# src/cobol_parser.py - COBOL Source Analyzer (Extensive Documentation)

## 1. Overview and Architecture
This module is the core of the COBOL static analysis. It extracts structural metadata and is designed for **high change resistance** by completely separating its logic from configuration and I/O handling.

The parser is capable of successfully processing COBOL source files using standard extensions like `.cbl`, `.cob`, and `.txt`.

## 2. Dependencies and Abstraction
This module relies on the following services and configuration files:

* **Configuration:** `src/config/regex_patterns.py` (Loads all regex patterns and keywords, ensuring easy modification of parsing rules without changing business logic).
* **I/O Service:** `src/services/data_io.py` (Handles writing the final analysis JSON output).
* **Error Handling:** `src/exceptions.py` (Utilizes the custom exception `CobolParsingError` for precise error diagnostics).

## 3. Class: CobolParser

The parsing logic is encapsulated in this class, facilitating pattern loading and unit testing.

### Method: `__init__(self, logger)`
* **Purpose:** Initializes the parser instance.
* **Key Action:** Loads the `COBOL_PATTERNS` dictionary and `IGNORED_PERFORMS` list from `src/config/regex_patterns.py`.

### Method: `parse_content(self, filename, content)`
* **Purpose:** Iterates line-by-line over the file content to perform extraction using pre-compiled regular expressions.
* **Returns:** A dictionary containing the structured metadata for a single program.
* **Extracted Metadata:**
    * `program_id`: The program's main identifier (e.g., `CMPROC`).
    * `copybooks`: External dependencies declared via `COPY` (e.g., `CHAMPS`, `DETALJ01`).
    * `calls`: External program calls (currently focused on literal strings).
    * `performs`: Internal procedure calls found via `PERFORM` (e.g., `WRITE-VSAM`, `TOP-WRITE-PARA`).
    * `status`: Logs warnings if `PROGRAM-ID` is missing.

## 4. Public Function: `pokreni_cobol_parser`

This function is the entry point for the pipeline orchestrator (`run_pipeline.py`).

| Parameter | Purpose | Exception Handling |
| :--- | :--- | :--- |
| `source_dir` | The directory containing the COBOL source files (e.g., `base/source`). | **Critical Check:** If the directory is missing, it raises a `CobolParsingError`. |
| `output_file` | The full path for the final `analysis_results.json`. | Writing handled by `write_json` service. |
| `logger` | The logging instance for session tracking. | |

## 5. JSON Output Example
[cite_start]A successful run generates the `analysis_results.json` file[cite: 78]. A typical entry for a program includes:

```json
{
    "filename": "CMPINIT.txt",
    "program_id": "CMPINIT",
    "copybooks": ["CHAMPS"],
    "calls": [],
    "performs": ["TOP-WRITE-PARA", "MID-WRITE-PARA", "BOT-WRITE-PARA", "JGL-WRITE-PARA"],
    "status": "OK"
}