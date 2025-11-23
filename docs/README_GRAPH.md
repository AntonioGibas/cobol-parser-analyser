# src/generate_graph.py - Visualization Engine (Extensive Documentation)

## 1. Overview and Architecture
This module is the final stage of the pipeline. It consumes the structured analysis data (JSON) and transforms it into interactive HTML flowcharts. It achieves **maximum flexibility** by separating the graph syntax generation logic from the HTML presentation layer using Jinja2 templating.

## 2. Dependencies and Templating
The module relies on services and the templating engine:

* **Templating Engine:** **Jinja2** is used to load HTML templates from the `templates/` directory. This ensures that visual styling (colors, layout structure) can be changed by editing HTML files only.
* **I/O Service:** `src/services/data_io.py` is used to reliably read the COBOL and JCL metadata JSON files.

## 3. Public Function: `pokreni_generator_grafa`

This function is the primary interface, responsible for loading data, initializing the Jinja2 environment, and generating both system and internal flow reports.

| Parameter | Purpose | Execution Logic |
| :--- | :--- | :--- |
| `jcl_json` | Path to the resolved JCL analysis data. | Determines overall system flow and dataset nodes. |
| `cobol_json` | Path to the COBOL structural metadata. | Used to determine Copybook count and generate internal flow links. |
| `templates_dir` | Path to the Jinja2 templates folder (e.g., `templates/`). | Used to initialize the Jinja2 environment. |

## 4. Generated Reports

The generator produces two types of reports in the `output/` directory:

### A. Main System Flow (`graph.html`)
* **Purpose:** Visualizes the entire job architecture, showing how JCL steps link programs and dataset files.
* **Features:** Program nodes include a clickable link ("Interni Tok") to the dedicated internal flow diagram.

### B. Internal Execution Flow (`internal/internal_PGM.html`)
* **Purpose:** Provides a detailed flowchart of the `PERFORM` call hierarchy within a single COBOL program (e.g., `CMPINIT`).
* **Content:** Displays the program's `ENTRY` point linked to all the paragraphs it performs (e.g., `CMPINIT ENTRY` $\rightarrow$ `TOP-WRITE-PARA`).

## 5. Helper Functions

* `safe_id(text)`: Converts arbitrary text (like DSNs or program IDs) into a safe, alphanumeric string suitable for Mermaid node identifiers.
* `_generate_internal_flow(...)`: The private function dedicated to rendering the internal `PERFORM` graph using the Jinja2 template.