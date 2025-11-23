import os
import re
import json

JCL_DIR = os.path.join("base", "JCL")
OUTPUT_FILE = os.path.join("output", "jcl_analysis.json")

def parsiraj_jcl_sadrzaj(sadrzaj, filename):
    lines = sadrzaj.splitlines()
    
    # 1. Prvi prolaz: Pronađi definicije PROC-a (Templates)
    defined_procs = {}
    current_proc_name = None
    current_proc_steps = []
    
    # Regex za početak PROC-a (npr. //UNOSC PROC RLE=)
    rx_proc_def = re.compile(r"//(\w+)\s+PROC", re.IGNORECASE)
    # Regex za kraj PROC-a
    rx_proc_end = re.compile(r"//\s*PEND", re.IGNORECASE)
    # Regex za DD unutar PROC-a
    rx_dd = re.compile(r"//(\w+)\s+DD\s+.*DSN=([A-Z0-9\.\&\(\)\-]+)", re.IGNORECASE)
    # Regex za EXEC unutar PROC-a
    rx_exec_inner = re.compile(r"//(\w+)\s+EXEC\s+PGM=([\w]+)", re.IGNORECASE)

    # Pomoćna varijabla da znamo koje linije preskočiti u drugom prolazu
    proc_definition_lines = set()

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("//*"): continue

        # Početak definicije
        match_proc = rx_proc_def.match(line)
        if match_proc:
            current_proc_name = match_proc.group(1)
            current_proc_steps = []
            proc_definition_lines.add(i)
            continue
        
        # Kraj definicije
        if current_proc_name and rx_proc_end.match(line):
            defined_procs[current_proc_name] = current_proc_steps
            current_proc_name = None
            proc_definition_lines.add(i)
            continue

        # Ako smo unutar definicije, skupljamo korake
        if current_proc_name:
            proc_definition_lines.add(i)
            match_exec = rx_exec_inner.match(line)
            
            if match_exec:
                step_name = match_exec.group(1)
                program = match_exec.group(2)
                
                # Kreiraj novi korak u predlošku
                new_step = {"step_name": step_name, "program": program, "datasets": []}
                
                # Čitaj DD linije unaprijed
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if next_line.startswith("//*"): 
                        proc_definition_lines.add(j)
                        j += 1
                        continue
                    
                    if " EXEC " in next_line or " PEND" in next_line:
                        break
                    
                    match_dd = rx_dd.match(next_line)
                    if match_dd:
                        proc_definition_lines.add(j)
                        new_step["datasets"].append({
                            "dd_name": match_dd.group(1),
                            "dsn": match_dd.group(2)
                        })
                    j += 1
                current_proc_steps.append(new_step)

    # ---------------------------------------------------------
    # 2. Drugi prolaz: Izvršavanje (Main Execution Flow)
    final_steps = []
    
    rx_exec_main = re.compile(r"//(\w+)\s+EXEC\s+(?:PGM=|PROC=)?([\w]+)(.*)", re.IGNORECASE)
    
    def resolve_vars(text, params):
        """Zamjenjuje varijable &RLE s vrijednostima."""
        if not text: return text
        for key, val in params.items():
            # Prvo zamijeni verziju s točkom (npr &RLE. -> MIDLANE)
            text = text.replace(f"&{key}.", val)
            # Zatim običnu verziju (npr &RLE -> MIDLANE)
            text = text.replace(f"&{key}", val)
        return text

    i = 0
    while i < len(lines):
        if i in proc_definition_lines:
            i += 1
            continue
            
        line = lines[i].strip()
        if not line or line.startswith("//*"):
            i += 1
            continue

        match_exec = rx_exec_main.match(line)
        if match_exec:
            step_name = match_exec.group(1)
            target = match_exec.group(2) # Ime programa ili procedure
            raw_params = match_exec.group(3)
            
            # Parsiranje parametara (npr. RLE=MIDLANE)
            params = {}
            if raw_params:
                parts = raw_params.split(',')
                for p in parts:
                    if '=' in p:
                        k, v = p.split('=')
                        params[k.strip()] = v.strip()

            # SLUČAJ A: Poziv spremljene procedure (npr. EXEC UNOSC)
            if target in defined_procs:
                template = defined_procs[target]
                for t_step in template:
                    expanded_step = {
                        "step_name": f"{step_name}.{t_step['step_name']}",
                        "program": t_step['program'],
                        "datasets": []
                    }
                    for ds in t_step['datasets']:
                        resolved_dsn = resolve_vars(ds['dsn'], params)
                        expanded_step['datasets'].append({
                            "dd_name": ds['dd_name'],
                            "dsn": resolved_dsn
                        })
                    final_steps.append(expanded_step)

            # SLUČAJ B: Običan program (npr. EXEC PGM=CMPINIT)
            else:
                # Provjera da nije sistemski utility (IDCAMS) ako ga želimo ignorirati, 
                # ili ga ostavimo. Ovdje ga ostavljamo.
                new_step = {
                    "step_name": step_name,
                    "program": target,
                    "datasets": []
                }
                # Čitaj DD za ovaj korak
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if " EXEC " in next_line: break # Novi korak
                    
                    match_dd = rx_dd.match(next_line)
                    if match_dd:
                        new_step["datasets"].append({
                            "dd_name": match_dd.group(1),
                            "dsn": match_dd.group(2)
                        })
                    j += 1
                final_steps.append(new_step)
        
        i += 1

    return final_steps

def analiziraj_jcl_direktorij():
    if not os.path.exists(JCL_DIR):
        print(f"GRESKA: {JCL_DIR} ne postoji.")
        return

    svi_jcl_podaci = []
    print(f"--- Napredna Analiza JCL-a (v3): {JCL_DIR} ---")

    for filename in os.listdir(JCL_DIR):
        if filename.endswith(".txt") or filename.endswith(".jcl"):
            path = os.path.join(JCL_DIR, filename)
            with open(path, 'r', encoding='utf-8') as f:
                steps = parsiraj_jcl_sadrzaj(f.read(), filename)
            
            if steps:
                svi_jcl_podaci.append({"filename": filename, "steps": steps})
                print(f"[{filename}] Procesiran. Ukupno izvršnih koraka: {len(steps)}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(svi_jcl_podaci, f, indent=4)
    print(f"\nRezultati: {OUTPUT_FILE}")

if __name__ == "__main__":
    analiziraj_jcl_direktorij()