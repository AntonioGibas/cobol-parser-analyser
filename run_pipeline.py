import os
import logging
import datetime
import sys

from src.cobol_parser import pokreni_cobol_parser
from src.parse_jcl import pokreni_jcl_parser
from src.generate_graph import pokreni_generator_grafa
from src.services.data_io import load_yaml_config

CONFIG_FILE = "config.yaml"

def setup_custom_logger(name, session_dir, script_name):
    log_dir = session_dir
    filename = f"log_{script_name}.txt"
    filepath = os.path.join(log_dir, filename)
    
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
    config = load_yaml_config(CONFIG_FILE) 

    LOG_ROOT = config['paths']['log_root']
    METADATA_ROOT = config['paths']['metadata_root']
    OUTPUT_ROOT = config['paths']['output_root']

    TEMPLATES_DIR = config['templates']['templates_dir']
    MAIN_TEMPLATE = config['templates']['main_graph']
    INTERNAL_TEMPLATE = config['templates']['internal_flow']
    
    SOURCE_DIR = config['paths']['source_dir']
    JCL_DIR = config['paths']['jcl_dir']
    
    COBOL_META_DIR = config['structure']['cobol_metadata_dir']
    JCL_META_DIR = config['structure']['jcl_metadata_dir']

    # KREIRANJE FINALNIH PUTANJA
    COBOL_JSON = os.path.join(METADATA_ROOT, COBOL_META_DIR, config['filenames']['cobol_json'])
    JCL_JSON = os.path.join(METADATA_ROOT, JCL_META_DIR, config['filenames']['jcl_json'])
    GRAPH_HTML = os.path.join(OUTPUT_ROOT, config['filenames']['main_graph'])
    INTERNAL_GRAPH_DIR = OUTPUT_ROOT

    # 1. Osiguravanje mapa
    if not os.path.exists(OUTPUT_ROOT): os.makedirs(OUTPUT_ROOT)
    if not os.path.exists(os.path.join(METADATA_ROOT, COBOL_META_DIR)): os.makedirs(os.path.join(METADATA_ROOT, COBOL_META_DIR))
    if not os.path.exists(os.path.join(METADATA_ROOT, JCL_META_DIR)): os.makedirs(os.path.join(METADATA_ROOT, JCL_META_DIR))

    # 2. Setup log sesije
    now = datetime.datetime.now()
    timestamp_filename = now.strftime("%d-%m-%Y_%H-%M-%S")
    LOG_SESSION_FOLDER = f"log_{timestamp_filename}"
    LOG_SESSION_DIR = os.path.join(LOG_ROOT, LOG_SESSION_FOLDER)
    os.makedirs(LOG_SESSION_DIR)

    print(f"--- POKRETANJE PIPELINE-A: {timestamp_filename} ---")

    # 3. Pozivi modula
    logger_cobol = setup_custom_logger('cobol_logger', LOG_SESSION_DIR, 'cobol_parser')
    pokreni_cobol_parser(SOURCE_DIR, COBOL_JSON, logger_cobol)

    logger_jcl = setup_custom_logger('jcl_logger', LOG_SESSION_DIR, 'jcl_parser')
    pokreni_jcl_parser(JCL_DIR, JCL_JSON, logger_jcl)

    logger_graph = setup_custom_logger('graph_logger', LOG_SESSION_DIR, 'graph_generator')
    pokreni_generator_grafa(JCL_JSON, COBOL_JSON, GRAPH_HTML, INTERNAL_GRAPH_DIR, TEMPLATES_DIR, MAIN_TEMPLATE, INTERNAL_TEMPLATE, logger_graph)

    print("\n--- CIKLUS ZAVRSEN ---")

if __name__ == "__main__":
    main()