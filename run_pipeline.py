import os
import logging
import datetime
import sys
from src.cobol_parser import pokreni_cobol_parser
from src.parse_jcl import pokreni_jcl_parser
from src.generate_graph import pokreni_generator_grafa

BASE_LOG_DIR = "execution_logs"
METADATA_DIR = "metadata"
OUTPUT_DIR = "output"

SOURCE_DIR = os.path.join("base", "source")
JCL_DIR = os.path.join("base", "JCL")

COBOL_JSON = os.path.join(METADATA_DIR, "COBOL", "analysis_results.json")
JCL_JSON = os.path.join(METADATA_DIR, "JCL", "jcl_analysis.json")
GRAPH_HTML = os.path.join(OUTPUT_DIR, "graph.html")
INTERNAL_GRAPH_DIR = os.path.join(OUTPUT_DIR) 

def setup_custom_logger(name, session_dir, script_name):
    filename = f"log_{script_name}.txt"
    filepath = os.path.join(session_dir, filename)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
    
    handler = logging.FileHandler(filepath)
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger

def main():
    # Kreiranje esencijalnih foldera
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(os.path.join(METADATA_DIR, "COBOL")): os.makedirs(os.path.join(METADATA_DIR, "COBOL"))
    if not os.path.exists(os.path.join(METADATA_DIR, "JCL")): os.makedirs(os.path.join(METADATA_DIR, "JCL"))

    # Kreiranje jedinstvenog foldera za ovu sesiju logiranja
    now = datetime.datetime.now()
    timestamp_filename = now.strftime("%d-%m-%Y_%H-%M-%S")
    LOG_SESSION_FOLDER = f"log_{timestamp_filename}"
    LOG_SESSION_DIR = os.path.join(BASE_LOG_DIR, LOG_SESSION_FOLDER)
    os.makedirs(LOG_SESSION_DIR)

    print(f"--- POKRETANJE PIPELINE-A: {timestamp_filename} ---")

    logger_cobol = setup_custom_logger('cobol_logger', LOG_SESSION_DIR, 'cobol_parser')
    pokreni_cobol_parser(SOURCE_DIR, COBOL_JSON, logger_cobol)

    logger_jcl = setup_custom_logger('jcl_logger', LOG_SESSION_DIR, 'jcl_parser')
    pokreni_jcl_parser(JCL_DIR, JCL_JSON, logger_jcl)

    logger_graph = setup_custom_logger('graph_logger', LOG_SESSION_DIR, 'graph_generator')
    pokreni_generator_grafa(JCL_JSON, COBOL_JSON, GRAPH_HTML, INTERNAL_GRAPH_DIR, logger_graph)

    print("\n--- CIKLUS ZAVRSEN ---")

if __name__ == "__main__":
    main()