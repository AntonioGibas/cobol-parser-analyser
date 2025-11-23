import json
import os

# --- KONFIGURACIJA ---
JCL_JSON = os.path.join("output", "jcl_analysis.json")
COBOL_JSON = os.path.join("output", "analysis_results.json")
HTML_OUTPUT = os.path.join("output", "graph.html")

def ucitaj_json(putanja):
    if os.path.exists(putanja):
        with open(putanja, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def generiraj_html_graf():
    print("--- Generiranje Grafa ---")
    
    jcl_data = ucitaj_json(JCL_JSON)
    cobol_data = ucitaj_json(COBOL_JSON)
    
    if not jcl_data:
        print("GRESKA: Nema JCL podataka. Pokreni parse_jcl.py prvo.")
        return

    # Mapa za brzi dohvat COBOL detalja (npr. opis programa)
    cobol_map = {item['program_id']: item for item in cobol_data}

    # --- IZGRADNJA MERMAID SINTAKSE ---
    mermaid_lines = ["graph TD"]
    
    # Definiranje stilova
    mermaid_lines.append("    classDef program fill:#f9f,stroke:#333,stroke-width:2px;")
    mermaid_lines.append("    classDef file fill:#ccf,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5;")
    mermaid_lines.append("    classDef report fill:#efe,stroke:#333,stroke-width:1px;")

    # Skupovi da izbjegnemo duplikate definicija
    nodes = set()
    links = set()

    for job in jcl_data:
        filename = job.get('filename', 'Unknown Job')
        # Kreiramo subgraph za svaki JCL Job
        mermaid_lines.append(f"    subgraph {filename}")
        
        for step in job['steps']:
            pgm = step['program']
            step_name = step['step_name']
            
            # Jedinstveni ID za cvor programa u grafu (npr. STEP01_CMPINIT)
            pgm_node_id = f"{step_name}_{pgm}".replace(".", "_").replace("-", "_")
            
            # Dodaj program cvor
            if pgm_node_id not in nodes:
                # Pokusaj naci dodatne info iz COBOL analize
                extra_info = ""
                if pgm in cobol_map:
                    copys = len(cobol_map[pgm]['copybooks'])
                    extra_info = f"<br/>(Copybooks: {copys})"
                
                label = f"[{step_name}<br/><b>{pgm}</b>{extra_info}]"
                mermaid_lines.append(f"    {pgm_node_id}{label}:::program")
                nodes.add(pgm_node_id)

            # Obrada datasetova (INPUT/OUTPUT)
            for ds in step['datasets']:
                dsn = ds['dsn']
                dd_name = ds['dd_name']
                
                # Ciscenje imena za ID cvora
                ds_node_id = dsn.replace(".", "_").replace("&", "").replace("(", "").replace(")", "")
                
                # Odredjivanje tipa cvora (File ili Report)
                node_style = "file"
                if "REPORT" in dsn or "SYSOUT" in dsn:
                    node_style = "report"
                    ds_label = f"({dsn})" # Zaobljeni rubovi za report
                else:
                    ds_label = f"[({dsn})]" # Baza oblik za file
                
                # Dodaj file cvor ako ne postoji
                if dsn not in nodes:
                    mermaid_lines.append(f"    {ds_node_id}{ds_label}:::{node_style}")
                    nodes.add(dsn) # Koristimo ime kao kljuc za set, ne ID

                # LOGIKA SMJERA STRELICE (Heuristika po DD imenu)
                # Ako DD ime pocinje s IN (npr INFL), onda FILE -> PROGRAM
                # Ako DD ime pocinje s OUT (npr OUTFL), onda PROGRAM -> FILE
                if dd_name.startswith("IN"):
                    link = f"    {ds_node_id} -->|{dd_name}| {pgm_node_id}"
                else:
                    link = f"    {pgm_node_id} -->|{dd_name}| {ds_node_id}"
                
                mermaid_lines.append(link)
        
        mermaid_lines.append("    end") # Kraj subgrapha

    # Spajanje linija
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
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        <style>
            body {{ font-family: sans-serif; margin: 20px; background: #f4f4f9; }}
            h1 {{ color: #333; }}
            .diagram-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
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
    
    print(f"Graf uspesno generiran: {HTML_OUTPUT}")
    print("Otvori ovu datoteku u svom pregledniku!")

if __name__ == "__main__":
    generiraj_html_graf()