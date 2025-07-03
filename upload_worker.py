import threading
import time
import os
from logger_config import get_logger

logger = get_logger(__name__)

def process_file(path):
    logger.info(f"Starting file processing: {path}")
    time.sleep(3)  # Simulate heavy processing
    logger.info(f"Completed file processing: {os.path.basename(path)}")

def process_file_background(path):
    logger.info(f"Queuing file for background processing: {os.path.basename(path)}")
    thread = threading.Thread(target=process_file, args=(path,), daemon=True)
    thread.start()
