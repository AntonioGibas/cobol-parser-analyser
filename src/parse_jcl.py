import os
import re
import json

JCL_DIR = os.path.join("base", "JCL")
OUTPUT_FILE = os.path.join("output", "jcl_analysis.json")

def parsiraj_jcl_sadrzaj(sadrzaj, filename):
    lines = sadrzaj.splitlines()
    
    # Spremnici
    defined_procs = {}   # Ovdje pamtimo definicije PROC-a (npr. UNOSC)
    final_steps = []     # Ovdje idu stvarni koraci koji se izvrsavaju
    
    # Varijable za praćenje stanja
    current_proc_name = None
    current_proc_steps = []
    
    # Regexi
    # 1. Definicija PROC-a: //UNOSC PROC RLE=
    rx_proc_def = re.compile(r"//(\w+)\s+PROC", re.IGNORECASE)
    # 2. Kraj PROC-a: // PEND
    rx_proc_end = re.compile(r"//\s*PEND", re.IGNORECASE)
    # 3. EXEC naredba (hvata i PGM=... i samo ime procedure)
    # Grupa 1: Ime koraka, Grupa 2: Sto se izvrsava (PGM ili PROC), Grupa 3: Parametri
    rx_exec = re.compile(r"//(\w+)\s+EXEC\s+(?:PGM=)?([\w]+)(.*)", re.IGNORECASE)
    # 4. DD naredba (sada podrzava tocke, &, zagrade)
    rx_dd = re.compile(r"//(\w+)\s+DD\s+.*DSN=([A-Z0-9\.\&\(\)\-]+)", re.IGNORECASE)

    # Pomoćna funkcija za zamjenu varijabli (npr. &RLE -> MIDLANE)
    def resolve_vars(text, params):
        for key, val in params.items():
            # Zamijeni &KEY sa vrijednoscu (npr &RLE sa MIDLANE)
            text = text.replace(f"&{key}", val)
            # Takodjer zamijeni i verziju s tockom (npr &RLE..REPORT -> MIDLANE.REPORT)
            text = text.replace(f"&{key}.", val)
        return text

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if line.startswith("//*") or not line: continue # Skip komentari

        # --- A. DETEKCIJA DEFINICIJE PROC-a ---
        match_proc = rx_proc_def.match(line)
        if match_proc:
            current_proc_name = match_proc.group(1)
            current_proc_steps = [] # Resetiramo listu koraka za ovaj proc
            continue
            
        if line.startswith("//") and "PEND" in line and current_proc_name:
            defined_procs[current_proc_name] = current_proc_steps
            current_proc_name = None
            continue

        # --- B. OBRADA KORAKA (Bilo unutar PROC-a ili u glavnom dijelu) ---
        match_exec = rx_exec.match(line)
        if match_exec:
            step_name = match_exec.group(1)
            target = match_exec.group(2) # Ime programa ili procedure
            raw_params = match_exec.group(3) # npr. ,RLE=MIDLANE
            
            # Parsiranje parametara u dictionary
            params = {}
            if raw_params:
                parts = raw_params.split(',')
                for p in parts:
                    if '=' in p:
                        k, v = p.split('=')
                        params[k.strip()] = v.strip()

            # Logika: Je li ovo poziv spremljene procedure?
            if target in defined_procs:
                # EKSPANZIJA PROCEDURE
                proc_template = defined_procs[target]
                for template_step in proc_template:
                    # Kopiramo korak
                    expanded_step = {
                        "step_name": f"{step_name}.{template_step['step_name']}", # npr. STEP02.STEP1
                        "program": template_step['program'],
                        "datasets": []
                    }
                    # Kopiramo i resolvamo datasetove
                    for ds in template_step['datasets']:
                        resolved_dsn = resolve_vars(ds['dsn'], params)
                        expanded_step['datasets'].append({
                            "dd_name": ds['dd_name'],
                            "dsn": resolved_dsn
                        })
                    final_steps.append(expanded_step)
            
            else:
                # OBICNI KORAK (EXEC PGM=...)
                new_step = {
                    "step_name": step_name,
                    "program": target,
                    "datasets": []
                }
                
                # Citaj DD linije dok ne dodje novi EXEC ili kraj
                while i < len(lines):
                    next_line = lines[i].strip()
                    # Ako je komentar ili prazno, preskoci ali ne prekidaj loop
                    if next_line.startswith("//*"):
                        i += 1; continue
                    
                    # Ako krece novi korak, break
                    if " EXEC " in next_line or next_line.startswith("// PEND"):
                        break
                        
                    match_dd = rx_dd.match(next_line)
                    if match_dd:
                        dd_name = match_dd.group(1)
                        dsn = match_dd.group(2)
                        new_step['datasets'].append({"dd_name": dd_name, "dsn": dsn})
                    
                    i += 1
                
                # Ako smo unutar PROC definicije, spremaj u template, inace u final
                if current_proc_name:
                    current_proc_steps.append(new_step)
                else:
                    final_steps.append(new_step)

    return final_steps

def analiziraj_jcl_direktorij():
    if not os.path.exists(JCL_DIR):
        print(f"GRESKA: {JCL_DIR} ne postoji.")
        return

    svi_jcl_podaci = []
    print(f"--- Napredna Analiza JCL-a: {JCL_DIR} ---")

    for filename in os.listdir(JCL_DIR):
        if filename.endswith(".txt") or filename.endswith(".jcl"):
            path = os.path.join(JCL_DIR, filename)
            with open(path, 'r', encoding='utf-8') as f:
                steps = parsiraj_jcl_sadrzaj(f.read(), filename)
            
            if steps:
                svi_jcl_podaci.append({"filename": filename, "steps": steps})
                print(f"[{filename}] Generirano {len(steps)} koraka.")
                for s in steps:
                    # Prikazi samo bitno za provjeru
                    inputs = [d['dsn'] for d in s['datasets'] if 'IN' in d['dd_name']]
                    outputs = [d['dsn'] for d in s['datasets'] if 'OUT' in d['dd_name']]
                    print(f"  > {s['step_name']} ({s['program']})")
                    if inputs: print(f"    IN: {inputs}")
                    if outputs: print(f"    OUT: {outputs}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(svi_jcl_podaci, f, indent=4)
    print(f"\nRezultati: {OUTPUT_FILE}")

if __name__ == "__main__":
    analiziraj_jcl_direktorij()