import os
import re
import json

def parsiraj_jcl_sadrzaj(sadrzaj, filename):
    lines = sadrzaj.splitlines()
    defined_procs = {}
    proc_definition_lines = set()

    rx_proc_def = re.compile(r"//(\w+)\s+PROC", re.IGNORECASE)
    rx_proc_end = re.compile(r"//\s*PEND", re.IGNORECASE)
    rx_dd = re.compile(r"//(\w+)\s+DD\s+.*DSN=([A-Z0-9\.\&\(\)\-]+)", re.IGNORECASE)
    rx_exec_inner = re.compile(r"//(\w+)\s+EXEC\s+PGM=([\w]+)", re.IGNORECASE)

    # 1. PROLAZ - DEFINICIJE
    current_proc_name = None
    current_proc_steps = []

    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("//*"): continue

        match_proc = rx_proc_def.match(line)
        if match_proc:
            current_proc_name = match_proc.group(1)
            current_proc_steps = []
            proc_definition_lines.add(i)
            continue
        
        if current_proc_name and rx_proc_end.match(line):
            defined_procs[current_proc_name] = current_proc_steps
            current_proc_name = None
            proc_definition_lines.add(i)
            continue

        if current_proc_name:
            proc_definition_lines.add(i)
            match_exec = rx_exec_inner.match(line)
            if match_exec:
                new_step = {"step_name": match_exec.group(1), "program": match_exec.group(2), "datasets": []}
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if next_line.startswith("//*"): 
                        proc_definition_lines.add(j); j += 1; continue
                    if " EXEC " in next_line or " PEND" in next_line: break
                    match_dd = rx_dd.match(next_line)
                    if match_dd:
                        proc_definition_lines.add(j)
                        new_step["datasets"].append({"dd_name": match_dd.group(1), "dsn": match_dd.group(2)})
                    j += 1
                current_proc_steps.append(new_step)

    # 2. PROLAZ - IZVRŠAVANJE
    final_steps = []
    rx_exec_main = re.compile(r"//(\w+)\s+EXEC\s+(?:PGM=|PROC=)?([\w]+)(.*)", re.IGNORECASE)
    
    def resolve_vars(text, params):
        if not text: return text
        for key, val in params.items():
            text = text.replace(f"&{key}.", val).replace(f"&{key}", val)
        return text

    i = 0
    while i < len(lines):
        if i in proc_definition_lines: i += 1; continue 
        line = lines[i].strip()
        if not line or line.startswith("//*"): i += 1; continue

        match_exec = rx_exec_main.match(line)
        if match_exec:
            step_name, target, raw_params = match_exec.group(1), match_exec.group(2), match_exec.group(3)
            params = {}
            if raw_params:
                for p in raw_params.split(','):
                    if '=' in p: k, v = p.split('='); params[k.strip()] = v.strip()

            if target in defined_procs:
                for t_step in defined_procs[target]:
                    exp_step = {"step_name": f"{step_name}.{t_step['step_name']}", "program": t_step['program'], "datasets": []}
                    for ds in t_step['datasets']:
                        exp_step['datasets'].append({"dd_name": ds['dd_name'], "dsn": resolve_vars(ds['dsn'], params)})
                    final_steps.append(exp_step)
            else:
                new_step = {"step_name": step_name, "program": target, "datasets": []}
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if " EXEC " in next_line: break
                    match_dd = rx_dd.match(next_line)
                    if match_dd: new_step["datasets"].append({"dd_name": match_dd.group(1), "dsn": match_dd.group(2)})
                    j += 1
                final_steps.append(new_step)
        i += 1
    return final_steps

def pokreni_jcl_parser(jcl_dir, output_file, logger):
    logger.info(f"--- POCETAK JCL PARSERA ---")
    
    if not os.path.exists(jcl_dir):
        logger.error(f"GRESKA: {jcl_dir} ne postoji.")
        return

    svi_jcl_podaci = []
    for filename in os.listdir(jcl_dir):
        if filename.endswith(".txt") or filename.endswith(".jcl"):
            try:
                path = os.path.join(jcl_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    steps = parsiraj_jcl_sadrzaj(f.read(), filename)
                
                if steps:
                    svi_jcl_podaci.append({"filename": filename, "steps": steps})
                    logger.info(f"[{filename}] Parsirano {len(steps)} koraka.")
            except Exception as e:
                logger.error(f"[{filename}] GRESKA: {str(e)}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(svi_jcl_podaci, f, indent=4)
    logger.info(f"JCL analiza zavrsena. Rezultati: {output_file}")