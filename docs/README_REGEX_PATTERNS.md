# src/config/regex_patterns.py - Centralized COBOL Patterns (Extensive Documentation)

## 1. Overview and Architectural Value
This module serves as the central repository for all regular expressions used by the `CobolParser`. This implementation achieved the **"Tvrdo kodirani Regex"** architectural improvement by separating parsing rules from the Python class logic.

### Why Centralize Patterns?
* **Change Resistance:** If COBOL syntax changes (e.g., a new style of `COPY` statement is introduced), only this single file needs to be updated. The core `CobolParser` class remains untouched.
* **Clarity:** Provides a single, clear location for auditing and reviewing all parsing rules.

## 2. Configuration Details

This file defines two main elements: the `COBOL_PATTERNS` dictionary and the `IGNORED_PERFORMS` list.

### Dictionary: `COBOL_PATTERNS`
Sadrži sve kompilirane regularne izraze:

| Key | Purpose | Example Match Target |
| :--- | :--- | :--- |
| `program_id` | Locates the program's primary identifier. | `PROGRAM-ID. VSAMLST` |
| `copy` | Detects and extracts the name of external copybooks. | `COPY CHAMPS` |
| `call` | Detects external program calls (calls to other programs). | `CALL 'SUBPGM'` |
| `perform` | Detects the paragraph/section name targeted by a `PERFORM` statement. | `PERFORM WRITE-VSAM` |

### List: `IGNORED_PERFORMS`
* **Purpose:** Contains keywords that follow the `PERFORM` verb but are part of the command's syntax rather than the target procedure name (e.g., `UNTIL`, `THRU`). These keywords are filtered out by the `CobolParser` to ensure only valid paragraph names are extracted.

## 3. Modification Guide
* **Updating a Pattern:** To modify how the parser detects `COPY` statements, simply update the regex string associated with the `"copy"` key in the `COBOL_PATTERNS` dictionary.
* **Adding an Ignore Word:** To exclude a new COBOL reserved word from the `PERFORM` list, append it to the `IGNORED_PERFORMS` list.