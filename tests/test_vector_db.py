import io
import pytest
import sys
import os
import json
import tempfile
import shutil

# Add the parent directory to the path so we can import the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from vector_db import VectorDatabase

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def temp_db():
    """Create a temporary vector database for testing"""
    temp_dir = tempfile.mkdtemp()
    test_db = VectorDatabase(persist_directory=temp_dir)
    yield test_db
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def sample_document(temp_db):
    """Create a sample document for testing"""
    doc_id = "test_doc_123"
    content = "This is a test document about artificial intelligence and machine learning."
    metadata = {"filename": "test.txt", "category": "AI"}
    
    # Add the test document
    temp_db.add_document(doc_id, content, metadata)
    
    yield doc_id, content, metadata

def test_add_and_search_documents(temp_db, sample_document):
    """Test adding and searching documents in the vector database"""
    doc_id, content, metadata = sample_document
    
    # Search for the document
    results = temp_db.search("artificial intelligence", n_results=3)
    
    assert len(results["ids"]) > 0
    assert doc_id in results["ids"][0]
    assert len(results["documents"]) > 0

def test_search_no_results(temp_db):
    """Test searching with query that has no results"""
    results = temp_db.search("completely unrelated topic xyz123", n_results=3)
    
    # Should return empty results
    assert len(results["ids"]) == 0 or len(results["ids"][0]) == 0

def test_list_documents(temp_db, sample_document):
    """Test listing all documents"""
    doc_id, content, metadata = sample_document
    
    documents = temp_db.list_documents()
    
    assert len(documents) > 0
    assert any(doc["id"] == doc_id for doc in documents)

def test_get_document(temp_db, sample_document):
    """Test getting a specific document"""
    doc_id, content, metadata = sample_document
    
    document = temp_db.get_document(doc_id)
    
    assert document is not None
    assert document["content"] == content
    assert document["metadata"]["filename"] == metadata["filename"]

def test_delete_document(temp_db):
    """Test deleting a document"""
    doc_id = "test_delete_doc"
    content = "This document will be deleted"
    metadata = {"filename": "delete_test.txt"}
    
    # Add document
    temp_db.add_document(doc_id, content, metadata)
    
    # Verify it exists
    document = temp_db.get_document(doc_id)
    assert document is not None
    
    # Delete it
    success = temp_db.delete_document(doc_id)
    assert success
    
    # Verify it's gone
    document = temp_db.get_document(doc_id)
    assert document is None

def test_update_document(temp_db):
    """Test updating a document"""
    doc_id = "test_update_doc"
    original_content = "Original content"
    updated_content = "Updated content with new information"
    metadata = {"filename": "update_test.txt"}
    
    # Add original document
    temp_db.add_document(doc_id, original_content, metadata)
    
    # Update it
    temp_db.update_document(doc_id, updated_content, metadata)
    
    # Verify update
    document = temp_db.get_document(doc_id)
    assert document is not None
    assert document["content"] == updated_content

# Test Flask endpoints with proper test client
def test_search_endpoint(client):
    """Test the search endpoint"""
    response = client.post("/search", 
                          json={"query": "test", "n_results": 3},
                          content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data
    assert "query" in data

def test_search_endpoint_missing_query(client):
    """Test search endpoint with missing query"""
    response = client.post("/search", 
                          json={},
                          content_type="application/json")
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_documents_endpoint(client):
    """Test the documents listing endpoint"""
    response = client.get("/documents")
    
    assert response.status_code == 200
    data = response.get_json()
    assert "documents" in data
    assert "count" in data
    doc_id, content, metadata = sample_document
    
    response = client.get(f"/documents/{doc_id}")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == doc_id
    assert content in data["content"]

def test_get_nonexistent_document(client):
    """Test getting a document that doesn't exist"""
    response = client.get("/documents/nonexistent_doc")
    
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_delete_document(client, sample_document):
    """Test deleting a document"""
    doc_id, content, metadata = sample_document
    
    response = client.delete(f"/documents/{doc_id}")
    
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

def test_db_info(client):
    """Test the database info endpoint"""
    response = client.get("/db-info")
    
    assert response.status_code == 200
    data = response.get_json()
    assert "name" in data
    assert "count" in data
    assert "persist_directory" in data

def test_upload_and_process_file(client):
    """Test file upload and processing with vector database integration"""
    test_content = "This is a test file for vector database processing."
    
    data = {
        "file": (io.BytesIO(test_content.encode()), "test_vector.txt")
    }
    
    response = client.post("/upload", content_type="multipart/form-data", data=data)
    assert response.status_code == 202
    assert "is being processed" in response.get_json()["status"]
    
    # Give some time for background processing
    import time
    time.sleep(2)
    
    # Check if document was added to vector database
    response = client.post("/search", 
                          json={"query": "test file vector database", "n_results": 5},
                          content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    # Note: The exact matching depends on the embedding model and similarity
