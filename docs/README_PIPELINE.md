# run_pipeline.py - Pipeline Orchestrator (Extensive Documentation)

## 1. Overview and Project Entry Point
This script is the **single entry point** for the entire COBOL Static Analysis project. Its primary responsibility is orchestration: setting up the environment, managing configuration, and calling the parsing/generation modules in the correct sequential order.

## 2. Architectural Role and Configuration
The script is designed to be highly maintainable by relying entirely on configuration and services:

* **Configuration:** Loads all paths (`SOURCE_DIR`, `OUTPUT_ROOT`, etc.) and structural names from `config.yaml` via the `load_yaml_config` service.
* **Setup:** Ensures all necessary output directories (`output/`, `metadata/COBOL/`, etc.) exist before the analysis begins.
* **Sequencing:** Manages the three critical phases of the analysis (COBOL, JCL, Graph).

## 3. Core Function: `setup_custom_logger`
This utility function handles the entire logging process, ensuring auditability and clarity.

| Logic | Detail |
| :--- | :--- |
| **Output:** | Creates a fully configured logger instance that writes messages to both the console and a file. |
| **File Naming:** | Generates a unique, timestamped directory (`execution_logs/log_DD-MM-YYYY...`) for the current session to group all logs together. |
| **Log Files:** | Creates separate log files for each module (`log_cobol_parser.txt`, `log_jcl_parser.txt`, etc.) within the session directory. |

## 4. Execution Flow (`main` function)

The pipeline executes the three decoupled phases sequentially:

| Phase | Module Called | Input Data | Output Data |
| :--- | :--- | :--- | :--- |
| **1. COBOL Parsing** | `pokreni_cobol_parser` | Raw COBOL Source | `analysis_results.json` |
| **2. JCL Parsing** | `pokreni_jcl_parser` | Raw JCL Source | `jcl_analysis.json` |
| **3. Graph Generation** | `pokreni_generator_grafa` | `analysis_results.json` + `jcl_analysis.json` | `graph.html` (Main Flow) and Internal HTML reports |

## 5. Execution Command

The entire pipeline is initiated from the project root:
```bash
python run_pipeline.py