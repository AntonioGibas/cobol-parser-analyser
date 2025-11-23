# run_pipeline.py (The Orchestrator)

## Overview
This is the main entry point for the COBOL Static Analysis Pipeline. Its primary role is orchestration, ensuring that all parsing, analysis, and generation steps are executed sequentially and correctly.

## Responsibilities
* **Initialization:** Sets up the execution environment, including creating output and metadata directories if they do not exist.
* **Logging:** Manages the creation of a unique, timestamped session folder within `execution_logs/`.
* **Dependency Injection:** Initializes and passes individual logger objects and file paths to the core modules.
* **Execution Flow:** Calls `cobol_parser`, `parse_jcl`, and `generate_graph` in the correct order.

## Key Configuration Variables
| Variable | Purpose | Output Location |
| :--- | :--- | :--- |
| `BASE_LOG_DIR` | Root folder for all log files. | `execution_logs/log_DD-MM-YYYY_.../` |
| `METADATA_DIR` | Root folder for structured JSON analysis results. | `metadata/` |
| `OUTPUT_DIR` | Root folder for final reports and HTML graphs. | `output/` |
| `COBOL_JSON` | Full path to the final COBOL structure JSON. | `metadata/COBOL/analysis_results.json` |
| `GRAPH_HTML` | Full path to the main system flowchart (Mermaid). | `output/graph.html` |