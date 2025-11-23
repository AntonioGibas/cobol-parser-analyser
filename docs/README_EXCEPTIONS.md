# src/exceptions.py - Custom Exception Definitions

## 1. Overview and Architectural Value
This module defines a custom hierarchy of exception classes for the entire pipeline. This implementation fulfills the final architectural goal of replacing generic `try...except Exception` blocks with specific, meaningful exceptions.

### Why Custom Exceptions?
* **Precision:** Allows developers to precisely catch and handle specific failure types (e.g., distinguishing between a configuration error and a parsing syntax error).
* **Diagnostics:** Greatly improves the log files, making troubleshooting faster by linking the failure directly to the component that raised the error (e.g., `CobolParsingError` vs. `JclParsingError`).

## 2. Exception Hierarchy

The defined exceptions create a clear structure, inherited from Python's base `Exception` class:

| Class Name | Base Class | Purpose and Usage |
| :--- | :--- | :--- |
| `ConfigurationError` | `Exception` | Intended to be raised when there are critical issues loading application settings (e.g., missing keys in `config.yaml`). |
| `ParsingError` | `Exception` | Acts as the generic parent for all parsing-related failures. Catching this covers both COBOL and JCL failures simultaneously. |
| `CobolParsingError` | `ParsingError` | Specifically raised within `src/cobol_parser.py` when COBOL processing fails (e.g., directory existence check). |
| `JclParsingError` | `ParsingError` | Specifically raised within `src/parse_jcl.py` when JCL logic fails (e.g., during PROC expansion). |
| `GraphGenerationError` | `Exception` | Intended to be raised when graph generation logic fails (e.g., invalid Mermaid syntax generated). |