import threading
import time
import os
from logger_config import get_logger
from vector_db import vector_db

logger = get_logger(__name__)

def process_file(path):
    logger.info(f"Starting file processing: {path}")
    
    try:
        # Read file content
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract filename and create document ID
        filename = os.path.basename(path)
        document_id = f"file_{filename}_{int(time.time())}"
        
        # Create metadata
        metadata = {
            'filename': filename,
            'file_path': path,
            'upload_time': time.time(),
            'file_size': os.path.getsize(path)
        }
        
        # Add to vector database
        success = vector_db.add_document(document_id, content, metadata)
        
        if success:
            logger.info(f"Successfully processed and stored file: {filename}")
        else:
            logger.error(f"Failed to store file in vector database: {filename}")
            
    except Exception as e:
        logger.error(f"Error processing file {path}: {e}")
    
    logger.info(f"Completed file processing: {os.path.basename(path)}")

def process_file_background(path):
    logger.info(f"Queuing file for background processing: {os.path.basename(path)}")
    thread = threading.Thread(target=process_file, args=(path,), daemon=True)
    thread.start()
