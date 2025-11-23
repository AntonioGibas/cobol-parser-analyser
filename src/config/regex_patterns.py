import re

COBOL_PATTERNS = {
    "program_id": re.compile(r"PROGRAM-ID\.\s+([\w-]+)", re.IGNORECASE),
    "copy": re.compile(r"COPY\s+([\w-]+)", re.IGNORECASE),
    "call": re.compile(r"CALL\s+['\"]([\w-]+)['\"]", re.IGNORECASE),
    "perform": re.compile(r"PERFORM\s+([\w-]+)", re.IGNORECASE)
}

IGNORED_PERFORMS = ['UNTIL', 'VARYING', 'THROUGH', 'THRU', 'TIMES']