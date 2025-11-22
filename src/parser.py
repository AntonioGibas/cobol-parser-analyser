import re
import os

def analiziraj_cobol_kod(sadrzaj):
    """
    Analizira tekst COBOL koda i vraća strukturu.
    """
    rezultat = {
        "program_id": "UNKNOWN",
        "copybooks": [],
        "calls": [],      # Vanjski pozivi
        "performs": []    # Interne procedure
    }
    
    # Regex uzorci
    rx_program_id = re.compile(r"PROGRAM-ID\.\s+([\w-]+)", re.IGNORECASE)
    rx_copy = re.compile(r"COPY\s+([\w-]+)", re.IGNORECASE)
    rx_call = re.compile(r"CALL\s+['\"]([\w-]+)['\"]", re.IGNORECASE)
    rx_perform = re.compile(r"PERFORM\s+([\w-]+)", re.IGNORECASE)
    
    lines = sadrzaj.splitlines()
    for linija in lines:
        linija = linija.strip()
        # Ignoriraj komentare i prazne linije
        if not linija or linija.startswith('*') or linija.startswith('/'):
            continue
            
        # 1. Traži ID programa
        if rezultat["program_id"] == "UNKNOWN":
            match = rx_program_id.search(linija)
            if match:
                rezultat["program_id"] = match.group(1)
        
        # 2. Traži COPY (zavisnosti)
        match_copy = rx_copy.search(linija)
        if match_copy:
            copy_name = match_copy.group(1)
            if copy_name not in rezultat["copybooks"]:
                rezultat["copybooks"].append(copy_name)

        # 3. Traži CALL (vanjski pozivi)
        match_call = rx_call.search(linija)
        if match_call:
            call_name = match_call.group(1)
            if call_name not in rezultat["calls"]:
                rezultat["calls"].append(call_name)
                
        # 4. Traži PERFORM (interne procedure)
        match_perform = rx_perform.search(linija)
        if match_perform:
            proc_name = match_perform.group(1)
            # Filtriramo ključne riječi
            keywords = ['UNTIL', 'VARYING', 'THROUGH', 'THRU', 'TIMES']
            if proc_name.upper() not in keywords:
                if proc_name not in rezultat["performs"]:
                    rezultat["performs"].append(proc_name)

    return rezultat

def generiraj_izvjestaj(input_dir):
    """
    Prolazi kroz mapu base/source i analizira kod.
    """
    if not os.path.exists(input_dir):
        print(f"Greska: Direktorij '{input_dir}' ne postoji!")
        print("Provjeri jesi li u dobroj mapi ili je li putanja tocna.")
        return

    print(f"--- Analiza mape: {input_dir} ---\n")
    print(f"{'PROGRAM':<15} | {'COPYBOOKS':<20} | {'PERFORMS (TOP 3)'}")
    print("-" * 65)

    # Podržane ekstenzije (dodali smo .txt)
    valid_extensions = (".cbl", ".cob", ".txt")

    pronadjeno_datoteka = 0

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(valid_extensions):
            pronadjeno_datoteka += 1
            putanja = os.path.join(input_dir, filename)
            
            try:
                with open(putanja, 'r', encoding='utf-8') as f:
                    sadrzaj = f.read()
            except UnicodeDecodeError:
                # Fallback ako utf-8 ne radi (često kod legacy koda)
                with open(putanja, 'r', encoding='latin-1') as f:
                    sadrzaj = f.read()
                
            podaci = analiziraj_cobol_kod(sadrzaj)
            
            # Priprema ispisa
            p_id = podaci['program_id'] if podaci['program_id'] != "UNKNOWN" else filename
            copy_str = ", ".join(podaci['copybooks'])
            perf_str = ", ".join(podaci['performs'][:3])
            if len(podaci['performs']) > 3:
                perf_str += "..."
                
            print(f"{p_id:<15} | {copy_str:<20} | {perf_str}")
    
    if pronadjeno_datoteka == 0:
        print("Nisu pronadjene datoteke s ekstenzijama .cbl, .cob ili .txt!")

if __name__ == "__main__":
    # Sada ciljamo tvoju novu putanju
    path_to_source = os.path.join("base", "source")
    generiraj_izvjestaj(path_to_source)