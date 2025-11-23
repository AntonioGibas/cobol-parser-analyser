# src/parse_jcl.py - JCL Source Analyzer (Extensive Documentation)

## 1. Overview and Purpose
This module analyzes JCL (Job Control Language) source files to establish the operational flow and resource dependencies of the entire system. It transforms complex JCL syntax, including procedure calls and variable substitution, into a simple, linear list of executable steps.

## 2. Core Functionality and Architecture
The JCL Parser's main challenge is correctly resolving the execution order before the graph can be generated.

* **Extraction:** Identifies Job Steps (`STEP01`), executed Programs (`EXEC PGM=...`), and Data Definitions (`DD`).
* **PROC Expansion:** The parser detects JCL Procedures (PROCs, defined between `PROC` and `PEND`) and expands them, replacing the single PROC call with its multiple constituent steps. For example, the `UNOSC` PROC call is expanded into multiple `CMPROC` steps.
* **Variable Resolution:** Resolves symbolic parameters (e.g., substituting `&RLE` with values like `MIDLANE`) during PROC expansion to determine the final, concrete Dataset Names (DSNs).
* **Error Handling:** Utilizes the custom exception `JclParsingError`.

## 3. Function: `parsiraj_jcl_sadrzaj(sadrzaj, filename)`
This internal function contains the core parsing logic and operates in two sequential passes:

1.  **Pass 1 (PROC Identification):** Scans the file to identify and store the structure of all defined JCL PROCs (e.g., `UNOSC`).
2.  **Pass 2 (Job Execution Flow):** Scans the main job stream, expanding any detected PROC calls by substituting parameters to create the final, executed list of steps.

## 4. Public Function: `pokreni_jcl_parser`
This function is the entry point for the pipeline orchestrator (`run_pipeline.py`).

| Parameter | Purpose | Execution Logic |
| :--- | :--- | :--- |
| `jcl_dir` | The directory containing the JCL source files (e.g., `base/JCL`). | **Critical Check:** If the directory is missing, it raises a `JclParsingError`. |
| `output_file` | The full path where the final JSON output (`jcl_analysis.json`) should be written. | Writing handled by the `data_io` service. |
| `logger` | The logging instance for session tracking. | [cite_start]Logs the number of steps successfully parsed per JCL file (e.g., "Parsirano 6 koraka" [cite: 176]). |

## 5. JSON Output Example
The generated `jcl_analysis.json` file shows the result of the expansion, which is essential for the final graph (e.g., how `STEP02.STEP1` uses `Z26069.MIDLANE` and writes to `Z26069.CHAMPS.VSAM`).

```json
{
    "filename": "CHAMPS01.txt",
    "steps": [
        // ... (REINIT step) ...
        {
            "step_name": "STEP02.STEP1",
            "program": "CMPROC",
            "datasets": [
                { "dd_name": "INFL1", "dsn": "Z26069.MIDLANE" },
                { "dd_name": "OUTFL1", "dsn": "Z26069.CHAMPS.VSAM" }
                // ... more datasets ...
            ]
        },
        // ... (STEP03.STEP1, STEP04.STEP1, etc.) ...
    ]
}