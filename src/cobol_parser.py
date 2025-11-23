import os
import json
import logging
from src.config.regex_patterns import COBOL_PATTERNS, IGNORED_PERFORMS

class CobolParser:
    def __init__(self, logger=None):
        self.logger = logger if logger else logging.getLogger(__name__)
        self.patterns = COBOL_PATTERNS
        self.ignored_performs = IGNORED_PERFORMS

    def parse_content(self, filename, content):
        rezultat = {
            "filename": filename,
            "program_id": "UNKNOWN",
            "copybooks": [],
            "calls": [],
            "performs": [],
            "status": "OK"
        }

        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('*') or line.startswith('/'):
                continue

            if rezultat["program_id"] == "UNKNOWN":
                match = self.patterns["program_id"].search(line)
                if match: rezultat["program_id"] = match.group(1)

            match_copy = self.patterns["copy"].search(line)
            if match_copy: rezultat["copybooks"].append(match_copy.group(1))

            match_call = self.patterns["call"].search(line)
            if match_call: rezultat["calls"].append(match_call.group(1))

            match_perform = self.patterns["perform"].search(line)
            if match_perform:
                p_name = match_perform.group(1).upper()
                if p_name not in self.ignored_performs and p_name not in rezultat["performs"]:
                    rezultat["performs"].append(p_name)

        if rezultat["program_id"] == "UNKNOWN":
            self.logger.warning(f"[{filename}] UPOZORENJE: Nije pronadjen PROGRAM-ID.")
            rezultat["status"] = "WARNING: No ID"

        return rezultat

def pokreni_cobol_parser(source_dir, output_file, logger):
    logger.info(f"--- POCETAK COBOL PARSERA ---")
    logger.info(f"Izvor: {source_dir}")
    
    parser = CobolParser(logger)
    
    svi_podaci = []
    valid_extensions = (".cbl", ".cob", ".txt")

    if not os.path.exists(source_dir):
        logger.error(f"GRESKA: Direktorij {source_dir} ne postoji!")
        return

    for filename in os.listdir(source_dir):
        if filename.lower().endswith(valid_extensions):
            filepath = os.path.join(source_dir, filename)
            try:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
                except UnicodeDecodeError:
                    logger.warning(f"[{filename}] Encoding fallback na latin-1.")
                    with open(filepath, 'r', encoding='latin-1') as f: content = f.read()

                podaci = parser.parse_content(filename, content)
                svi_podaci.append(podaci)
                logger.info(f"[{filename}] Parsirano uspjesno (ID: {podaci['program_id']})")

            except Exception as e:
                logger.error(f"[{filename}] KRITICNA GRESKA: {str(e)}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(svi_podaci, f, indent=4)

    logger.info(f"COBOL analiza zavrsena. Rezultati: {output_file}")