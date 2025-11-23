import json
import os
import re

def ucitaj_json(putanja):
    if os.path.exists(putanja):
        with open(putanja, 'r', encoding='utf-8') as f: return json.load(f)
    return []

def safe_id(text):
    if not text: return "UNKNOWN"
    clean = re.sub(r'[^a-zA-Z0-9]', '_', text)
    return re.sub(r'_+', '_', clean).strip('_')

def safe_label(text):
    if not text: return ""
    return text.replace('"', "'").replace('[', '(').replace(']', ')')

def pokreni_generator_grafa(jcl_json, cobol_json, html_output, logger):
    logger.info("--- POCETAK GENERIRANJA GRAFA ---")
    
    jcl_data = ucitaj_json(jcl_json)
    cobol_data = ucitaj_json(cobol_json)
    
    if not jcl_data:
        logger.error("GRESKA: Nema JCL podataka.")
        return

    cobol_map = {item['program_id']: item for item in cobol_data}
    lines = ["graph TD", "    classDef program fill:#f9f,stroke:#333,stroke-width:2px,color:black;", "    classDef file fill:#ccf,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5,color:black;", "    classDef report fill:#efe,stroke:#333,stroke-width:1px,color:black;"]
    generated_nodes = set()

    for job in jcl_data:
        filename = job.get('filename', 'UNKNOWN')
        job_id = safe_id(f"JOB_{filename}")
        lines.append(f'    subgraph {job_id} ["{safe_label(filename)}"]')
        
        for step in job['steps']:
            pgm, step_name = step['program'], step['step_name']
            pgm_id = safe_id(f"PGM_{step_name}_{pgm}")
            
            if pgm_id not in generated_nodes:
                extra = f"<br/>(Copybooks: {len(cobol_map[pgm]['copybooks'])})" if pgm in cobol_map else ""
                lines.append(f"    {pgm_id}[\"{safe_label(step_name)}<br/><b>{safe_label(pgm)}</b>{extra}\"]:::program")
                generated_nodes.add(pgm_id)

            for ds in step['datasets']:
                dsn, dd_name = ds['dsn'], ds['dd_name']
                ds_id = safe_id(f"FILE_{dsn}")
                style, shape_o, shape_c = ("report", "(", ")") if "REPORT" in dsn or "SYSOUT" in dsn else ("file", "[(", ")]")

                if ds_id not in generated_nodes:
                    lines.append(f'    {ds_id}{shape_o}"{safe_label(dsn)}"{shape_c}:::{style}')
                    generated_nodes.add(ds_id)

                arrow = f'    {ds_id} -->|"{safe_label(dd_name)}"| {pgm_id}' if dd_name.startswith("IN") else f'    {pgm_id} -->|"{safe_label(dd_name)}"| {ds_id}'
                lines.append(arrow)
        lines.append("    end")

    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(f"<!DOCTYPE html><html><head><script type='module'>import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose' }});</script></head><body style='background:#f4f4f9; font-family:sans-serif;'><h2>COBOL Flow</h2><div style='background:white; padding:20px; border-radius:8px;'><pre class='mermaid'>\n" + "\n".join(lines) + "\n</pre></div></body></html>")
    
    logger.info(f"Graf generiran: {html_output}")