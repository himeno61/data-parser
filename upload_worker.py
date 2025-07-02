import threading
import time
import os

def process_file(path):
    print(f"Processing file: {path}")
    time.sleep(3)  # Simulate heavy processing
    print(f"Done processing: {os.path.basename(path)}")

def process_file_background(path):
    thread = threading.Thread(target=process_file, args=(path,), daemon=True)
    thread.start()
