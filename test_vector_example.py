#!/usr/bin/env python3
"""
Example script demonstrating ChromaDB vector database usage
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_vector_database():
    """Test the vector database functionality"""
    
    print("🚀 Testing Vector Database Integration")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.json()}")
    
    # Test database info
    print("\n2. Getting database info...")
    response = requests.get(f"{BASE_URL}/db-info")
    if response.status_code == 200:
        info = response.json()
        print(f"Database: {info['name']}")
        print(f"Documents: {info['count']}")
        print(f"Location: {info['persist_directory']}")
    
    # Upload a test file
    print("\n3. Uploading a test file...")
    test_content = """
    Artificial Intelligence (AI) is transforming the world. 
    Machine learning algorithms can process vast amounts of data 
    to find patterns and make predictions. Natural language processing 
    enables computers to understand and generate human language.
    """
    
    files = {'file': ('ai_article.txt', test_content)}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    print(f"Upload response: {response.json()}")
    
    # Wait for processing
    print("\n4. Waiting for file processing...")
    time.sleep(5)
    
    # Search for documents
    print("\n5. Searching for documents...")
    search_queries = [
        "artificial intelligence",
        "machine learning algorithms",
        "natural language processing",
        "data patterns"
    ]
    
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        response = requests.post(
            f"{BASE_URL}/search",
            json={"query": query, "n_results": 3},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"Found {results['count']} results:")
            
            for i, result in enumerate(results['results'][:2]):  # Show first 2 results
                print(f"  {i+1}. Score: {result.get('distance', 'N/A')}")
                print(f"     Content: {result['content'][:100]}...")
                print(f"     Metadata: {result['metadata']}")
        else:
            print(f"Search failed: {response.status_code}")
    
    # List all documents
    print("\n6. Listing all documents...")
    response = requests.get(f"{BASE_URL}/documents")
    if response.status_code == 200:
        docs = response.json()
        print(f"Total documents: {docs['count']}")
        for doc in docs['documents'][:3]:  # Show first 3
            print(f"  - ID: {doc['id']}")
            print(f"    Filename: {doc['metadata'].get('filename', 'Unknown')}")
            print(f"    Size: {doc['metadata'].get('file_size', 'Unknown')} bytes")
    
    print("\n✅ Vector database test completed!")

if __name__ == "__main__":
    try:
        test_vector_database()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure your Flask app is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
