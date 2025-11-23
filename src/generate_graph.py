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

def sanitize_id(text):
    """
    Pretvara tekst u siguran ID za Mermaid (samo slova, brojevi i _).
    Sve ostalo (tocke, povlake, razmaci) postaje donja crta.
    """
    if not text: return "UNKNOWN"
    # Zamijeni sve sto NIJE slovo ili broj sa donjom crtom
    clean = re.sub(r'[^a-zA-Z0-9]', '_', text)
    # Ukloni visestruke donje crte (npr __ -> _)
    clean = re.sub(r'_+', '_', clean)
    # Ukloni donju crtu s kraja ili pocetka
    return clean.strip('_')

def generiraj_html_graf():
    print("--- Generiranje Grafa (v2 - Robustan) ---")
    
    jcl_data = ucitaj_json(JCL_JSON)
    cobol_data = ucitaj_json(COBOL_JSON)
    
    if not jcl_data:
        print("GRESKA: Nema JCL podataka. Pokreni parse_jcl.py prvo.")
        return

    # Mapa za brzi dohvat COBOL detalja
    cobol_map = {item['program_id']: item for item in cobol_data}

    # --- IZGRADNJA MERMAID SINTAKSE ---
    mermaid_lines = ["graph TD"]
    
    # Definiranje stilova
    mermaid_lines.append("    classDef program fill:#f9f,stroke:#333,stroke-width:2px,color:black;")
    mermaid_lines.append("    classDef file fill:#ccf,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5,color:black;")
    mermaid_lines.append("    classDef report fill:#efe,stroke:#333,stroke-width:1px,color:black;")

    nodes = set()

    for job in jcl_data:
        filename = job.get('filename', 'Unknown Job')
        # Koristimo navodnike za ime subgrapha da izbjegnemo greske s tockama
        mermaid_lines.append(f'    subgraph "{filename}"')
        
        for step in job['steps']:
            pgm = step['program']
            step_name = step['step_name']
            
            # 1. Siguran ID za cvor programa
            # Kombiniramo step i program da bude jedinstven
            pgm_node_id = sanitize_id(f"PGM_{step_name}_{pgm}")
            
            if pgm_node_id not in nodes:
                extra_info = ""
                if pgm in cobol_map:
                    copys = len(cobol_map[pgm]['copybooks'])
                    extra_info = f"<br/>(Copybooks: {copys})"
                
                # Labela moze sadrzavati cudne znakove jer je u navodnicima i zagradama
                label = f"[{step_name}<br/><b>{pgm}</b>{extra_info}]"
                mermaid_lines.append(f"    {pgm_node_id}{label}:::program")
                nodes.add(pgm_node_id)

            # 2. Obrada datasetova
            for ds in step['datasets']:
                dsn = ds['dsn']
                dd_name = ds['dd_name']
                
                # Siguran ID za file (npr. Z26069_CHAMPION_DATA)
                ds_node_id = sanitize_id(f"FILE_{dsn}")
                
                # Odredjivanje stila
                node_style = "file"
                ds_label_shape = f"[({dsn})]" # Default: Database oblik
                
                if "REPORT" in dsn or "SYSOUT" in dsn:
                    node_style = "report"
                    ds_label_shape = f"({dsn})" # Report: Zaobljeni oblik

                if ds_node_id not in nodes:
                    mermaid_lines.append(f"    {ds_node_id}{ds_label_shape}:::{node_style}")
                    nodes.add(ds_node_id)

                # 3. Kreiranje veze
                # Koristimo obicne strelice da smanjimo sansu za gresku
                if dd_name.startswith("IN"):
                    # File ulazi u Program
                    mermaid_lines.append(f"    {ds_node_id} -->|{dd_name}| {pgm_node_id}")
                else:
                    # Program pise u File
                    mermaid_lines.append(f"    {pgm_node_id} -->|{dd_name}| {ds_node_id}")
        
        mermaid_lines.append("    end")

    mermaid_content = "\n".join(mermaid_lines)

    # --- GENERIRANJE HTML-a ---
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>COBOL Flow Analysis</title>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ 
                startOnLoad: true, 
                theme: 'default',
                securityLevel: 'loose',
                flowchart: {{ useMaxWidth: false }}
            }});
        </script>
        <style>
            body {{ font-family: sans-serif; margin: 20px; background: #f4f4f9; }}
            h1 {{ color: #333; }}
            .diagram-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); overflow: auto; }}
        </style>
    </head>
    <body>
        <h1>Analiza Toka Podataka (COBOL/JCL)</h1>
        <p>Generirano iz statičke analize koda.</p>
        <div class="diagram-container">
            <pre class="mermaid">
{mermaid_content}
            </pre>
        </div>
    </body>
    </html>
    """

    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"Graf uspjesno generiran: {HTML_OUTPUT}")

if __name__ == "__main__":
    generiraj_html_graf()