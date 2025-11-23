# src/generate_graph.py

## Overview
This module acts as the visualization engine, combining structural data (COBOL JSON) and flow data (JCL JSON) into human-readable HTML diagrams using the Mermaid.js library.

## Responsibilities
* **System Graph (Main):** Creates `graph.html`, showing the high-level data flow (programs as nodes, datasets as nodes, connected by DD names).
    * **Features:** Displays Copybook count on program nodes and adds a link to the internal flow diagram.
* **Internal Flow Graph (Detail):** Creates separate HTML files (e.g., `internal/internal_CMPROC.html`) for each COBOL program.
    * **Features:** Visualizes the `PERFORM` hierarchy extracted from the COBOL source, showing program entry point to the called paragraphs.
* **Sanitization:** Ensures all program IDs and dataset names are converted into valid, syntax-safe Mermaid node IDs.

## Key Function
* `pokreni_generator_grafa(jcl_json, cobol_json, html_output_main, html_output_internal_dir, logger)`: Main entry point for graph generation.