# src/parse_jcl.py

## Overview
This module analyzes JCL files to determine the operational flow, connecting programs to the data resources they utilize. This is critical for generating the system-level graph.

## Responsibilities
* **Execution Flow:** Extracts `STEP` names and executed programs (`EXEC PGM=...`).
* **PROC Expansion:** Parses JCL procedures (PROCs, e.g., `UNOSC`) and expands them into explicit steps at runtime.
* **Variable Resolution:** Resolves symbolic parameters (e.g., substituting `&RLE` with `MIDLANE` in dataset names).
* **Dataset Mapping:** Maps logical DD names (e.g., `INFL1`) to physical datasets (DSNs, e.g., `Z26069.MIDLANE`).
* **Output:** Generates `jcl_analysis.json`, which lists all sequential execution steps and associated datasets.

## Key Function
* `pokreni_jcl_parser(jcl_dir, output_file, logger)`: Main entry point for JCL processing.