from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from upload_worker import process_file_background
from logger_config import setup_logger
from vector_db import vector_db

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

@app.route("/search", methods=["POST"])
def search_documents():
    """Search documents in the vector database"""
    logger.info("Search endpoint called")
    
    data = request.get_json()
    if not data or 'query' not in data:
        logger.warning("Search request missing query")
        return jsonify({"error": "Query is required"}), 400
    
    query = data['query']
    n_results = data.get('n_results', 5)
    
    logger.info(f"Searching for: '{query}' with {n_results} results")
    
    results = vector_db.search_documents(query, n_results)
    
    if results is None:
        return jsonify({"error": "Search failed"}), 500
    
    # Format results for response
    formatted_results = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            result = {
                'content': doc,
                'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else None,
                'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else None
            }
            formatted_results.append(result)
    
    return jsonify({
        "query": query,
        "results": formatted_results,
        "count": len(formatted_results)
    })

@app.route("/documents", methods=["GET"])
def list_documents():
    """List all documents in the vector database"""
    logger.info("List documents endpoint called")
    
    documents = vector_db.list_documents()
    return jsonify({
        "documents": documents,
        "count": len(documents)
    })

@app.route("/documents/<document_id>", methods=["GET"])
def get_document(document_id):
    """Get a specific document by ID"""
    logger.info(f"Get document endpoint called for ID: {document_id}")
    
    document = vector_db.get_document(document_id)
    
    if document is None:
        return jsonify({"error": "Document not found"}), 404
    
    return jsonify(document)

@app.route("/documents/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    """Delete a document from the vector database"""
    logger.info(f"Delete document endpoint called for ID: {document_id}")
    
    success = vector_db.delete_document(document_id)
    
    if success:
        return jsonify({"message": f"Document {document_id} deleted successfully"})
    else:
        return jsonify({"error": "Failed to delete document"}), 500

@app.route("/db-info", methods=["GET"])
def get_db_info():
    """Get information about the vector database"""
    logger.info("Database info endpoint called")
    
    info = vector_db.get_collection_info()
    
    if info is None:
        return jsonify({"error": "Failed to get database info"}), 500
    
    return jsonify(info)
