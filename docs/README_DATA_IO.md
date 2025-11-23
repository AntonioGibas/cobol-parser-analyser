# src/services/data_io.py - Data I/O Abstraction Service (Extensive Documentation)

## 1. Overview and Architectural Value
This module serves as the **single interface** for all file read/write operations (JSON and YAML) within the pipeline. Its primary architectural purpose is **decoupling**, implementing the "Global I/O Abstraction" concept.

### Why Abstraction?
* **Change Resistance:** If the system needs to save metadata to a database (e.g., PostgreSQL) instead of JSON files, only the functions within `data_io.py` need to be modified. The parsers and graph generator remain entirely untouched.
* **Centralized File Management:** All file system checks and encoding are handled in one place.

## 2. Core Functions

### Function: `read_json(file_path)`
This function provides a safe way to retrieve structured data.

| Logic | Detail |
| :--- | :--- |
| **Input:** | `file_path` (string) |
| **Safeguards:** | Checks if the file exists. Catches `json.JSONDecodeError` and returns an empty list `[]` if the file is corrupted. |
| **Returns:** | The loaded JSON data structure, or `[]` if the file is missing or corrupted. |

### Function: `write_json(data, file_path)`
This function persists analysis results to the disk.

| Logic | Detail |
| :--- | :--- |
| **Directory Management:** | Automatically checks if the parent directory (e.g., `metadata/COBOL/`) exists. If it does not, it creates the necessary directory structure using `os.makedirs` before writing. |
| **Formatting:** | Writes the JSON output with `indent=4` for human-readable formatting. |

### Function: `load_yaml_config(file_path)`
This function centralizes the startup configuration loading.

* **Used By:** `run_pipeline.py`.
* **Action:** Safely loads the `config.yaml` file using the external `yaml` library.