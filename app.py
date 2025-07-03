from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from upload_worker import process_file_background
from logger_config import setup_logger

# Set up logging
logger = setup_logger(__name__)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024 * 1024  # 1GB max

logger.info("Flask application starting up")

@app.route("/upload", methods=["POST"])
def upload_file():
    logger.info("Upload endpoint called")
    
    if "file" not in request.files:
        logger.warning("Upload request missing file part")
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        logger.warning("Upload request with empty filename")
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    
    logger.info(f"File saved: {filename} at {file_path}")
    
    process_file_background(file_path)
    logger.info(f"Started background processing for file: {filename}")
    
    return jsonify({"status": f"File {filename} is being processed"}), 202

@app.route("/health", methods=["GET"])
def health():
    logger.info("Health check endpoint accessed")
    return jsonify({"status": "ok"})
