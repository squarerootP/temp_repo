import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(BASE_DIR, "graph_log.txt")
logging.basicConfig(level=logging.INFO, filename=log_path, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
def _log(message: str):
    logging.info(message.strip())