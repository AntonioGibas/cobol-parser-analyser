import json
import os
import re

# --- KONFIGURACIJA ---
JCL_JSON = os.path.join("output", "jcl_analysis.json")
COBOL_JSON = os.path.join("output", "analysis_results.json")
HTML_OUTPUT = os.path.join("output", "graph.html")

def ucitaj_json(putanja):
    if os.path.exists(putanja):
        with open(putanja, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def safe_id(text):
    """Kreira siguran ID za Mermaid cvorove (samo slova, brojevi i _)"""
    if not text: return "UNKNOWN"
    # Zamijeni sve sto nije alfanumerik sa _
    clean = re.sub(r'[^a-zA-Z0-9]', '_', text)
    # Ukloni visestruke donje crte
    clean = re.sub(r'_+', '_', clean)
    return clean.strip('_')

def safe_label(text):
    """Cisti tekst za prikaz u labeli (mice navodnike i opasne znakove)"""
    if not text: return ""
    # Zamijeni navodnike i zagrade koji mogu slomiti Mermaid sintaksu
    clean = text.replace('"', "'").replace('[', '(').replace(']', ')')
    return clean

def generiraj_html_graf():
    print("--- Generiranje Grafa (v3 - Final) ---")
    
    jcl_data = ucitaj_json(JCL_JSON)
    cobol_data = ucitaj_json(COBOL_JSON)
    
    if not jcl_data:
        print("GRESKA: Nema JCL podataka.")
        return

    cobol_map = {item['program_id']: item for item in cobol_data}

    # --- MERMAID HEADER ---
    lines = ["graph TD"]
    
    # --- DEFINICIJA KLASE ---
    # Definiramo stilove eksplicitno
    lines.append("    classDef program fill:#f9f,stroke:#333,stroke-width:2px,color:black;")
    lines.append("    classDef file fill:#ccf,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5,color:black;")
    lines.append("    classDef report fill:#efe,stroke:#333,stroke-width:1px,color:black;")

    generated_nodes = set()

    for job in jcl_data:
        filename = job.get('filename', 'UNKNOWN')
        job_id = safe_id(f"JOB_{filename}")
        
        # Subgraph sa sigurnim ID-em i naslovom u navodnicima
        lines.append(f'    subgraph {job_id} ["{safe_label(filename)}"]')
        
        for step in job['steps']:
            pgm = step['program']
            step_name = step['step_name']
            
            # 1. Program Node
            pgm_id = safe_id(f"PGM_{step_name}_{pgm}")
            
            if pgm_id not in generated_nodes:
                extra = ""
                if pgm in cobol_map:
                    cnt = len(cobol_map[pgm]['copybooks'])
                    extra = f"<br/>(Copybooks: {cnt})"
                
                # Labela
                lbl = f'["{safe_label(step_name)}<br/><b>{safe_label(pgm)}</b>{extra}"]'
                lines.append(f"    {pgm_id}{lbl}:::program")
                generated_nodes.add(pgm_id)

            # 2. Dataset Nodes
            for ds in step['datasets']:
                dsn = ds['dsn']
                dd_name = ds['dd_name']
                
                ds_id = safe_id(f"FILE_{dsn}")
                
                # Odredi oblik cvora
                if "REPORT" in dsn or "SYSOUT" in dsn:
                    # Report (zaobljeno) - sintaksa: id(Label)
                    shape_open, shape_close = "(", ")"
                    style = "report"
                else:
                    # File (baza) - sintaksa: id[(Label)]
                    shape_open, shape_close = "[(", ")]"
                    style = "file"

                if ds_id not in generated_nodes:
                    # Pazimo da labela nema zagrade koje bi zbunile sintaksu
                    safe_dsn = safe_label(dsn)
                    lines.append(f'    {ds_id}{shape_open}"{safe_dsn}"{shape_close}:::{style}')
                    generated_nodes.add(ds_id)

                # 3. Veze
                safe_dd = safe_label(dd_name)
                if dd_name.startswith("IN"):
                    lines.append(f'    {ds_id} -->|"{safe_dd}"| {pgm_id}')
                else:
                    lines.append(f'    {pgm_id} -->|"{safe_dd}"| {ds_id}')
        
        lines.append("    end")

    mermaid_content = "\n".join(lines)

    # --- HTML TEMPLATE ---
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>COBOL Flow</title>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose' }});
        </script>
    </head>
    <body style="background:#f4f4f9; font-family:sans-serif;">
        <h2>Analiza Toka (COBOL/JCL)</h2>
        <div style="background:white; padding:20px; border-radius:8px;">
            <pre class="mermaid">
{mermaid_content}
            </pre>
        </div>
    </body>
    </html>
    """

    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Graf spreman: {HTML_OUTPUT}")

if __name__ == "__main__":
    generiraj_html_graf()