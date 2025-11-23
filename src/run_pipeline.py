import os
import logging
import datetime
import sys
from src.cobol_parser import pokreni_cobol_parser
from src.parse_jcl import pokreni_jcl_parser
from src.generate_graph import pokreni_generator_grafa

BASE_LOG_DIR = "execution_logs"
SOURCE_DIR = os.path.join("base", "source")
JCL_DIR = os.path.join("base", "JCL")

METADATA_DIR = "metadata"
OUTPUT_DIR = "output"

COBOL_JSON = os.path.join(METADATA_DIR, "COBOL", "analysis_results.json")
JCL_JSON = os.path.join(METADATA_DIR, "JCL", "jcl_analysis.json")
GRAPH_HTML = os.path.join(OUTPUT_DIR, "graph.html")

def setup_custom_logger(name, folder, script_name, timestamp):
    log_dir = os.path.join(BASE_LOG_DIR, folder)
    filename = f"log_{script_name}_{timestamp}.txt"
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
    now = datetime.datetime.now()
    timestamp_filename = now.strftime("%d-%m-%Y_%H-%M-%S")
    
    print(f"--- POKRETANJE PIPELINE-A: {timestamp_filename} ---")

    logger_cobol = setup_custom_logger('cobol_logger', 'COBOL', 'cobol_parser', timestamp_filename)
    pokreni_cobol_parser(SOURCE_DIR, COBOL_JSON, logger_cobol)

    logger_jcl = setup_custom_logger('jcl_logger', 'JCL', 'jcl_parser', timestamp_filename)
    pokreni_jcl_parser(JCL_DIR, JCL_JSON, logger_jcl)

    logger_graph = setup_custom_logger('graph_logger', 'graph', 'graph_generator', timestamp_filename)
    pokreni_generator_grafa(JCL_JSON, COBOL_JSON, GRAPH_HTML, logger_graph)

    print("\n--- CIKLUS ZAVRSEN ---")

if __name__ == "__main__":
    main()