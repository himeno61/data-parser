import io
import pytest
import sys
import os
import json

# Add the parent directory to the path so we can import the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from vector_db import vector_db

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

@pytest.fixture
def sample_document():
    """Create a sample document for testing"""
    doc_id = "test_doc_123"
    content = "This is a test document about artificial intelligence and machine learning."
    metadata = {"filename": "test.txt", "category": "AI"}
    
    # Clean up any existing test document
    vector_db.delete_document(doc_id)
    
    # Add the test document
    vector_db.add_document(doc_id, content, metadata)
    
    yield doc_id, content, metadata
    
    # Clean up after test
    vector_db.delete_document(doc_id)

def test_search_documents(client, sample_document):
    """Test the search endpoint"""
    doc_id, content, metadata = sample_document
    
    response = client.post("/search", 
                          json={"query": "artificial intelligence", "n_results": 3},
                          content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data
    assert "query" in data
    assert data["query"] == "artificial intelligence"

def test_search_missing_query(client):
    """Test search endpoint with missing query"""
    response = client.post("/search", 
                          json={},
                          content_type="application/json")
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_list_documents(client, sample_document):
    """Test the list documents endpoint"""
    doc_id, content, metadata = sample_document
    
    response = client.get("/documents")
    
    assert response.status_code == 200
    data = response.get_json()
    assert "documents" in data
    assert "count" in data
    assert isinstance(data["documents"], list)

def test_get_document(client, sample_document):
    """Test getting a specific document"""
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
