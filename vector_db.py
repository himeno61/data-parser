import numpy as np
import json
import os
import pickle
from typing import List, Dict, Any, Optional
import faiss
from sklearn.feature_extraction.text import TfidfTransformer
import logging

logger = logging.getLogger(__name__)

class VectorDatabase:
    """Vector database using FAISS for efficient similarity search."""
    
    def __init__(self, persist_directory: str = "vector_db"):
        self.persist_directory = persist_directory
        self.documents = []
        self.metadata = []
        self.document_ids = []
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.index = None
        self.dimension = 1000  # TF-IDF max_features
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Load existing data if available
        self._load_data()
        
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]] = None, ids: List[str] = None):
        """Add documents to the FAISS vector database."""
        if metadata is None:
            metadata = [{}] * len(documents)
        
        if ids is None:
            ids = [f"doc_{len(self.documents) + i}" for i in range(len(documents))]
        
        # Add to existing documents
        self.documents.extend(documents)
        self.metadata.extend(metadata)
        self.document_ids.extend(ids)
        
        # Rebuild FAISS index with all documents
        self._rebuild_index()
        
        # Persist the data
        self._save_data()
        
        logger.info(f"Added {len(documents)} documents to FAISS vector database")
        
    def _rebuild_index(self):
        """Rebuild FAISS index for all documents."""
        if not self.documents:
            return
            
        # Create TF-IDF vectors
        tfidf_vectors = self.vectorizer.fit_transform(self.documents)
        
        # Convert sparse matrix to dense for FAISS
        vectors = tfidf_vectors.toarray().astype(np.float32)
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(vectors.shape[1])  # Inner Product (cosine similarity)
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)
        
        # Add vectors to index
        self.index.add(vectors)
        
        logger.info(f"Rebuilt FAISS index for {len(self.documents)} documents")
        
    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """Query the FAISS vector database for similar documents."""
        if not self.documents or self.index is None:
            return {
                "documents": [],
                "metadata": [],
                "ids": [],
                "distances": []
            }
        
        # Transform query using the same vectorizer
        query_vector = self.vectorizer.transform([query_text]).toarray().astype(np.float32)
        
        # Normalize query vector
        faiss.normalize_L2(query_vector)
        
        # Search in FAISS index
        n_results = min(n_results, len(self.documents))
        scores, indices = self.index.search(query_vector, n_results)
        
        # Convert to lists and filter valid results
        scores = scores[0].tolist()
        indices = indices[0].tolist()
        
        # Filter out invalid indices and low scores
        valid_results = [(idx, score) for idx, score in zip(indices, scores) 
                        if idx != -1 and score > 0.01]
        
        results = {
            "documents": [self.documents[idx] for idx, _ in valid_results],
            "metadata": [self.metadata[idx] for idx, _ in valid_results],
            "ids": [self.document_ids[idx] for idx, _ in valid_results],
            "distances": [1 - score for _, score in valid_results]  # Convert similarity to distance
        }
        
        logger.info(f"FAISS query returned {len(results['documents'])} results")
        return results
        
    def get_document_count(self) -> int:
        """Get the number of documents in the database."""
        return len(self.documents)
        
    def delete_by_id(self, doc_id: str) -> bool:
        """Delete a document by its ID."""
        try:
            index = self.document_ids.index(doc_id)
            del self.documents[index]
            del self.metadata[index]
            del self.document_ids[index]
            
            # Rebuild index after deletion
            self._rebuild_index()
            self._save_data()
            
            logger.info(f"Deleted document with ID: {doc_id}")
            return True
        except ValueError:
            logger.warning(f"Document with ID {doc_id} not found")
            return False
            
    def clear(self):
        """Clear all documents from the database."""
        self.documents = []
        self.metadata = []
        self.document_ids = []
        self.index = None
        self._save_data()
        logger.info("Cleared all documents from FAISS vector database")
        
    def _save_data(self):
        """Save data and FAISS index to disk for persistence."""
        try:
            # Save document data
            data = {
                "documents": self.documents,
                "metadata": self.metadata,
                "document_ids": self.document_ids
            }
            
            data_file = os.path.join(self.persist_directory, "data.json")
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save vectorizer
            vectorizer_file = os.path.join(self.persist_directory, "vectorizer.pkl")
            with open(vectorizer_file, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            # Save FAISS index
            if self.index is not None:
                index_file = os.path.join(self.persist_directory, "faiss.index")
                faiss.write_index(self.index, index_file)
            
            logger.debug(f"Saved FAISS data to {self.persist_directory}")
        except Exception as e:
            logger.error(f"Error saving FAISS data: {e}")
            
    def _load_data(self):
        """Load data and FAISS index from disk if they exist."""
        data_file = os.path.join(self.persist_directory, "data.json")
        vectorizer_file = os.path.join(self.persist_directory, "vectorizer.pkl")
        index_file = os.path.join(self.persist_directory, "faiss.index")
        
        try:
            # Load document data
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                self.documents = data.get("documents", [])
                self.metadata = data.get("metadata", [])
                self.document_ids = data.get("document_ids", [])
            
            # Load vectorizer
            if os.path.exists(vectorizer_file):
                with open(vectorizer_file, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            
            # Load FAISS index
            if os.path.exists(index_file) and self.documents:
                self.index = faiss.read_index(index_file)
                logger.info(f"Loaded FAISS index with {len(self.documents)} documents")
            elif self.documents:
                # If we have documents but no index, rebuild it
                self._rebuild_index()
                
        except Exception as e:
            logger.error(f"Error loading FAISS data: {e}")
            # Reset to empty state on error
            self.documents = []
            self.metadata = []
            self.document_ids = []
            self.index = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        stats = {
            "document_count": len(self.documents),
            "has_index": self.index is not None,
            "index_size": self.index.ntotal if self.index else 0,
            "vector_dimension": self.dimension,
            "persist_directory": self.persist_directory
        }
        return stats
