import os
import re
import json
import logging
import datetime

# --- KONFIGURACIJA ---
SOURCE_DIR = os.path.join("base", "source")
OUTPUT_DIR = "output"
LOG_FILE = os.path.join(OUTPUT_DIR, "error_log.txt")
JSON_FILE = os.path.join(OUTPUT_DIR, "analysis_results.json")

# Osiguraj da output direktorij postoji
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- POSTAVKE LOGIRANJA ---
# Brišemo stari log prije novog testa
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# --- LOGIKA PARSERA (REGEX) ---
def parse_content(filename, content):
    rezultat = {
        "filename": filename,
        "program_id": "UNKNOWN",
        "copybooks": [],
        "calls": [],
        "performs": [],
        "status": "OK"
    }
    
    rx_program_id = re.compile(r"PROGRAM-ID\.\s+([\w-]+)", re.IGNORECASE)
    rx_copy = re.compile(r"COPY\s+([\w-]+)", re.IGNORECASE)
    rx_call = re.compile(r"CALL\s+['\"]([\w-]+)['\"]", re.IGNORECASE)
    # Ignoriramo 'UNTIL', 'VARYING', 'THRU' da smanjimo šum
    rx_perform = re.compile(r"PERFORM\s+([\w-]+)", re.IGNORECASE)
    ignored_performs = ['UNTIL', 'VARYING', 'THROUGH', 'THRU', 'TIMES']

    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('*') or line.startswith('/'):
            continue

        # Traži Program ID
        if rezultat["program_id"] == "UNKNOWN":
            match = rx_program_id.search(line)
            if match:
                rezultat["program_id"] = match.group(1)

        # Traži COPY
        match_copy = rx_copy.search(line)
        if match_copy:
            rezultat["copybooks"].append(match_copy.group(1))

        # Traži CALL
        match_call = rx_call.search(line)
        if match_call:
            rezultat["calls"].append(match_call.group(1))

        # Traži PERFORM
        match_perform = rx_perform.search(line)
        if match_perform:
            p_name = match_perform.group(1).upper()
            if p_name not in ignored_performs:
                if p_name not in rezultat["performs"]:
                    rezultat["performs"].append(p_name)

    # --- TESTNA LOGIKA: Provjera kvalitete ---
    if rezultat["program_id"] == "UNKNOWN":
        logging.warning(f"[{filename}] UPOZORENJE: Nije pronadjen PROGRAM-ID.")
        rezultat["status"] = "WARNING: No ID"

    if not rezultat["copybooks"] and not rezultat["performs"] and not rezultat["calls"]:
        logging.warning(f"[{filename}] UPOZORENJE: Datoteka izgleda prazno ili parser ne prepoznaje strukturu.")
        rezultat["status"] = "WARNING: Empty structure"

    return rezultat

# --- GLAVNA FUNKCIJA ZA TESTIRANJE ---
def pokreni_testove():
    logging.info(f"--- POCETAK TESTIRANJA: {datetime.datetime.now()} ---")
    logging.info(f"Citam datoteke iz: {SOURCE_DIR}")

    uspjesno = 0
    neuspjesno = 0
    svi_podaci = []

    valid_extensions = (".cbl", ".cob", ".txt")

    if not os.path.exists(SOURCE_DIR):
        logging.error(f"GRESKA: Direktorij {SOURCE_DIR} ne postoji!")
        return

    for filename in os.listdir(SOURCE_DIR):
        if filename.lower().endswith(valid_extensions):
            filepath = os.path.join(SOURCE_DIR, filename)
            try:
                # Pokušaj čitanja s UTF-8
                content = ""
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    logging.warning(f"[{filename}] Encoding nije UTF-8, pokusavam latin-1...")
                    with open(filepath, 'r', encoding='latin-1') as f:
                        content = f.read()

                # Parsiranje
                podaci = parse_content(filename, content)
                svi_podaci.append(podaci)
                uspjesno += 1
                logging.info(f"[{filename}] OK - ID: {podaci['program_id']}")

            except Exception as e:
                neuspjesno += 1
                logging.error(f"[{filename}] KRITICNA GRESKA: {str(e)}")
    
    # Spremanje JSON rezultata
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(svi_podaci, f, indent=4)

    logging.info("-" * 30)
    logging.info(f"TEST ZAVRSEN.")
    logging.info(f"Uspjesno obradjeno: {uspjesno}")
    logging.info(f"Greske pri citanju: {neuspjesno}")
    logging.info(f"Detaljan log je spremljen u: {LOG_FILE}")
    logging.info(f"JSON podaci su spremljeni u: {JSON_FILE}")

if __name__ == "__main__":
    pokreni_testove()