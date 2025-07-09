import chromadb
from chromadb.config import Settings
import os
from logger_config import get_logger

logger = get_logger(__name__)

class VectorDatabase:
    def __init__(self, persist_directory="./chroma_db"):
        """Initialize ChromaDB client with persistent storage"""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize Chroma client with persistent storage
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get collection
        self.collection_name = "file_contents"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Connected to existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "File contents and metadata"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def add_document(self, document_id: str, content: str, metadata: dict = None):
        """Add a document to the vector database"""
        try:
            if metadata is None:
                metadata = {}
            
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[document_id]
            )
            logger.info(f"Added document to vector DB: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding document to vector DB: {e}")
            return False
    
    def search_documents(self, query: str, n_results: int = 5):
        """Search for similar documents"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            logger.info(f"Search completed for query: '{query}' - Found {len(results['documents'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return None
    
    def get_document(self, document_id: str):
        """Get a specific document by ID"""
        try:
            result = self.collection.get(ids=[document_id])
            if result['documents']:
                return {
                    'id': document_id,
                    'content': result['documents'][0],
                    'metadata': result['metadatas'][0] if result['metadatas'] else {}
                }
            return None
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            return None
    
    def delete_document(self, document_id: str):
        """Delete a document from the vector database"""
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"Deleted document from vector DB: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def list_documents(self):
        """List all documents in the collection"""
        try:
            result = self.collection.get()
            documents = []
            for i, doc_id in enumerate(result['ids']):
                documents.append({
                    'id': doc_id,
                    'content': result['documents'][i] if i < len(result['documents']) else '',
                    'metadata': result['metadatas'][i] if i < len(result['metadatas']) else {}
                })
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def get_collection_info(self):
        """Get information about the collection"""
        try:
            count = self.collection.count()
            return {
                'name': self.collection_name,
                'count': count,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None

# Initialize global vector database instance
vector_db = VectorDatabase()
