import os
import re
import json

# Putanja do JCL datoteka
JCL_DIR = os.path.join("base", "JCL")
OUTPUT_FILE = os.path.join("output", "jcl_analysis.json")

def parsiraj_jcl_sadrzaj(sadrzaj, naziv_datoteke):
    steps = []
    current_step = None
    
    # Regexi za JCL
    # Hvata: //STEP01 EXEC PGM=CMPINIT ili EXEC PROC=UNOSC
    rx_exec = re.compile(r"//(\w+)\s+EXEC\s+(?:PGM|PROC)=([\w]+)", re.IGNORECASE)
    
    # Hvata: //INFL DD DSN=Z26069.DATA
    rx_dd = re.compile(r"//(\w+)\s+DD\s+.*DSN=([\w\.]+)", re.IGNORECASE)

    lines = sadrzaj.splitlines()
    
    for linija in lines:
        linija = linija.strip()
        
        # Ignoriraj komentare
        if linija.startswith("//*"):
            continue

        # 1. Detekcija novog koraka (STEP)
        match_exec = rx_exec.match(linija)
        if match_exec:
            # Ako smo imali otvoreni step, spremimo ga
            if current_step:
                steps.append(current_step)
            
            step_name = match_exec.group(1)
            program_name = match_exec.group(2)
            
            current_step = {
                "step_name": step_name,
                "program": program_name,
                "datasets": []
            }
            
        # 2. Detekcija datasetova (DD DSN=...) unutar trenutnog koraka
        if current_step:
            match_dd = rx_dd.match(linija)
            if match_dd:
                dd_name = match_dd.group(1)
                dsn = match_dd.group(2).rstrip(',') # Micanje zareza s kraja
                
                current_step["datasets"].append({
                    "dd_name": dd_name,
                    "dsn": dsn
                })

    # Spremi zadnji korak
    if current_step:
        steps.append(current_step)
        
    return steps

def analiziraj_jcl_direktorij():
    if not os.path.exists(JCL_DIR):
        print(f"GRESKA: Direktorij {JCL_DIR} ne postoji.")
        return

    svi_jcl_podaci = []
    print(f"--- Analiza JCL datoteka u: {JCL_DIR} ---")

    for filename in os.listdir(JCL_DIR):
        if filename.endswith(".txt") or filename.endswith(".jcl"):
            filepath = os.path.join(JCL_DIR, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            jcl_steps = parsiraj_jcl_sadrzaj(content, filename)
            
            if jcl_steps:
                svi_jcl_podaci.append({
                    "filename": filename,
                    "steps": jcl_steps
                })
                print(f"[{filename}] Pronadjeno koraka: {len(jcl_steps)}")
                for step in jcl_steps:
                    print(f"  - STEP: {step['step_name']} -> PGM: {step['program']}")

    # Spremanje rezultata
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(svi_jcl_podaci, f, indent=4)
    
    print(f"\nRezultati spremljeni u: {OUTPUT_FILE}")

if __name__ == "__main__":
    analiziraj_jcl_direktorij()