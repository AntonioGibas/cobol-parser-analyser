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

def _generate_internal_flow(program_data, output_path):
    pgm = program_data['program_id']
    performs = program_data['performs']
    
    if not performs:
        return 

    lines = ["graph TD"]
    lines.append("    classDef entry fill:#f9f,stroke:#333,stroke-width:2px,color:black;")
    lines.append("    classDef step fill:#fff,stroke:#333,stroke-width:1px,color:black;")
    
    # Glavni ulaz programa
    pgm_id = safe_id(pgm)
    lines.append(f'    {pgm_id}["{safe_label(pgm)} ENTRY"]:::entry')
    
    # Povezivanje ulaza sa svim PERFORMS pozivima
    for perform in performs:
        perform_id = safe_id(f"{pgm}_{perform}")
        lines.append(f'    {perform_id}["{safe_label(perform)}"]')
        lines.append(f'    {pgm_id} --> {perform_id}:::step')
    
    mermaid_content = "\n".join(lines)
    
    html = f"""
    <!DOCTYPE html><html><head><script type='module'>import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose' }});</script></head><body style='background:#f4f4f9; font-family:sans-serif;'><h2>Internal Flow: {pgm}</h2><p><a href='../graph.html'>&lt;&lt; Natrag na glavni graf</a></p><div style='background:white; padding:20px; border-radius:8px;'><pre class='mermaid'>\n{mermaid_content}\n</pre></div></body></html>
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def pokreni_generator_grafa(jcl_json, cobol_json, html_output_main, html_output_internal_dir, logger):
    logger.info("--- POCETAK GENERIRANJA GRAFA ---")
    
    jcl_data = ucitaj_json(jcl_json)
    cobol_data = ucitaj_json(cobol_json)
    
    if not jcl_data:
        logger.error("GRESKA: Nema JCL podataka.")
        return

    cobol_map = {item['program_id']: item for item in cobol_data}
    
    # 1. Priprema i kreiranje interne mape
    internal_dir = os.path.join(html_output_internal_dir, "internal")
    if not os.path.exists(internal_dir):
        os.makedirs(internal_dir)
        
    # GENERIRANJE INTERNIH GRAFOVA
    for program_data in cobol_data:
        pgm = program_data['program_id']
        internal_file_path = os.path.join(internal_dir, f"internal_{safe_id(pgm)}.html")
        _generate_internal_flow(program_data, internal_file_path)
        logger.info(f"Interni graf generiran za {pgm}: {internal_file_path}")
        
    # 2. Glavni JCL graf
    lines = ["graph TD"]
    lines.append("    classDef program fill:#f9f,stroke:#333,stroke-width:2px,color:black;")
    lines.append("    classDef file fill:#ccf,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5,color:black;")
    lines.append("    classDef report fill:#efe,stroke:#333,stroke-width:1px,color:black;")

    generated_nodes = set()

    for job in jcl_data:
        filename = job.get('filename', 'UNKNOWN')
        job_id = safe_id(f"JOB_{filename}")
        lines.append(f'    subgraph {job_id} ["{safe_label(filename)}"]')
        
        for step in job['steps']:
            pgm = step['program']
            step_name = step['step_name']
            
            pgm_id = safe_id(f"PGM_{step_name}_{pgm}")
            
            if pgm_id not in generated_nodes:
                extra = ""
                if pgm in cobol_map:
                    cnt = len(cobol_map[pgm]['copybooks'])
                    # DODANA LOGIKA: Linkanje na interni graf
                    internal_file_name = f"internal/internal_{safe_id(pgm)}.html"
                    extra = f'<br/>(Copybooks: {cnt})<br/>[[{internal_file_name} Interni Tok]]'

                else:
                    extra = ""
                    
                lbl = f'["{safe_label(step_name)}<br/><b>{safe_label(pgm)}</b>{extra}"]'
                lines.append(f"    {pgm_id}{lbl}:::program")
                generated_nodes.add(pgm_id)

            for ds in step['datasets']:
                dsn = ds['dsn']
                dd_name = ds['dd_name']
                ds_id = safe_id(f"FILE_{dsn}")
                style, shape_o, shape_c = ("report", "(", ")") if "REPORT" in dsn or "SYSOUT" in dsn else ("file", "[(", ")]")

                if ds_id not in generated_nodes:
                    safe_dsn = safe_label(dsn)
                    lines.append(f'    {ds_id}{shape_o}"{safe_dsn}"{shape_c}:::{style}')
                    generated_nodes.add(ds_id)

                arrow = f'    {ds_id} -->|"{safe_label(dd_name)}"| {pgm_id}' if dd_name.startswith("IN") else f'    {pgm_id} -->|"{safe_label(dd_name)}"| {ds_id}'
                lines.append(arrow)
        lines.append("    end")
    
    mermaid_content = "\n".join(lines)
    
    html = f"""
    <!DOCTYPE html><html><head><script type='module'>import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose' }});</script></head><body style='background:#f4f4f9; font-family:sans-serif;'><h2>COBOL Flow</h2><div style='background:white; padding:20px; border-radius:8px;'><pre class='mermaid'>\n{mermaid_content}\n</pre></div></body></html>
    """

    with open(html_output_main, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Glavni graf generiran: {html_output_main}")
    logger.info("Generiranje grafova zavrseno.")