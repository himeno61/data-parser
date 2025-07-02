from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from upload_worker import process_file_background

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024 * 1024  # 1GB max

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    process_file_background(file_path)
    return jsonify({"status": f"File {filename} is being processed"}), 202

@app.route("/health", methods=["GET"])
def health():
    print("Health check endpoint hit")
    return jsonify({"status": "ok"})
