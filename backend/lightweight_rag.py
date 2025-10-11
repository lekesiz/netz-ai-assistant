"""
Lightweight RAG System without Docker
Uses ChromaDB for vector storage and SQLite for metadata
"""

import os
import json
import hashlib
import sqlite3
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import numpy as np
from dataclasses import dataclass
import logging
import pickle

# Try ChromaDB first, fallback to FAISS if needed
try:
    import chromadb
    from chromadb.config import Settings
    VECTOR_DB = "chromadb"
except ImportError:
    try:
        import faiss
        VECTOR_DB = "faiss"
    except ImportError:
        VECTOR_DB = "numpy"  # Fallback to pure numpy

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Document structure for RAG"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    timestamp: Optional[datetime] = None

class EmbeddingGenerator:
    """Generate embeddings locally without external APIs"""
    
    def __init__(self):
        self.embedding_cache = {}
        self.dimension = 384  # Standard dimension for lightweight models
        
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using local method"""
        # Check cache first
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.embedding_cache:
            return self.embedding_cache[text_hash]
        
        # Simple but effective embedding using TF-IDF-like approach
        words = text.lower().split()
        embedding = np.zeros(self.dimension)
        
        # Word frequency based embedding
        for i, word in enumerate(words[:self.dimension]):
            # Simple hash-based position
            position = hash(word) % self.dimension
            # TF component
            embedding[position] += 1.0 / (1.0 + i)  # Position-weighted
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        result = embedding.tolist()
        self.embedding_cache[text_hash] = result
        return result
    
    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [self.generate_embedding(text) for text in texts]

class VectorStore:
    """Abstract vector store interface"""
    
    def add_documents(self, documents: List[Document]) -> None:
        raise NotImplementedError
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        raise NotImplementedError
    
    def delete(self, doc_ids: List[str]) -> None:
        raise NotImplementedError

class ChromaVectorStore(VectorStore):
    """ChromaDB-based vector store"""
    
    def __init__(self, path: str):
        self.client = chromadb.PersistentClient(
            path=path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection = self.client.get_or_create_collection(
            name="netz_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_generator = EmbeddingGenerator()
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to ChromaDB"""
        if not documents:
            return
        
        # Generate embeddings
        texts = [doc.content for doc in documents]
        embeddings = self.embedding_generator.batch_generate(texts)
        
        # Prepare data for ChromaDB
        ids = [doc.id for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Convert results to Document objects
        documents = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                doc = Document(
                    id=results['ids'][0][i],
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    embedding=results['embeddings'][0][i] if results.get('embeddings') else None
                )
                score = results['distances'][0][i] if results.get('distances') else 0
                documents.append((doc, 1 - score))  # Convert distance to similarity
        
        return documents
    
    def delete(self, doc_ids: List[str]) -> None:
        """Delete documents by IDs"""
        if doc_ids:
            self.collection.delete(ids=doc_ids)

class NumpyVectorStore(VectorStore):
    """Pure numpy-based vector store (no external dependencies)"""
    
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.mkdir(exist_ok=True)
        self.index_file = self.path / "index.pkl"
        self.embedding_generator = EmbeddingGenerator()
        self.load_index()
    
    def load_index(self):
        """Load or create index"""
        if self.index_file.exists():
            with open(self.index_file, 'rb') as f:
                self.index = pickle.load(f)
        else:
            self.index = {
                'documents': {},
                'embeddings': [],
                'ids': []
            }
    
    def save_index(self):
        """Save index to disk"""
        with open(self.index_file, 'wb') as f:
            pickle.dump(self.index, f)
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to numpy store"""
        for doc in documents:
            # Generate embedding
            embedding = self.embedding_generator.generate_embedding(doc.content)
            
            # Add to index
            self.index['documents'][doc.id] = doc
            self.index['embeddings'].append(embedding)
            self.index['ids'].append(doc.id)
        
        self.save_index()
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search using cosine similarity"""
        if not self.index['embeddings']:
            return []
        
        # Generate query embedding
        query_embedding = np.array(self.embedding_generator.generate_embedding(query))
        
        # Calculate cosine similarities
        embeddings_matrix = np.array(self.index['embeddings'])
        similarities = np.dot(embeddings_matrix, query_embedding)
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:k]
        
        # Return documents with scores
        results = []
        for idx in top_indices:
            doc_id = self.index['ids'][idx]
            doc = self.index['documents'][doc_id]
            score = similarities[idx]
            results.append((doc, float(score)))
        
        return results
    
    def delete(self, doc_ids: List[str]) -> None:
        """Delete documents by IDs"""
        # Rebuild index without deleted documents
        new_documents = {}
        new_embeddings = []
        new_ids = []
        
        for i, doc_id in enumerate(self.index['ids']):
            if doc_id not in doc_ids:
                new_documents[doc_id] = self.index['documents'][doc_id]
                new_embeddings.append(self.index['embeddings'][i])
                new_ids.append(doc_id)
        
        self.index = {
            'documents': new_documents,
            'embeddings': new_embeddings,
            'ids': new_ids
        }
        self.save_index()

class LightweightRAG:
    """Main RAG system orchestrator"""
    
    def __init__(self, storage_path: str = "./rag_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize vector store
        if VECTOR_DB == "chromadb":
            self.vector_store = ChromaVectorStore(str(self.storage_path / "chroma"))
        else:
            self.vector_store = NumpyVectorStore(str(self.storage_path / "numpy"))
        
        # Initialize SQLite for metadata
        self.db_path = self.storage_path / "metadata.db"
        self.init_metadata_db()
        
        logger.info(f"Initialized RAG with {VECTOR_DB} backend")
    
    def init_metadata_db(self):
        """Initialize SQLite database for metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT,
                source TEXT,
                doc_type TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                results TEXT,
                timestamp TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_document(self, content: str, title: str = "", source: str = "", 
                    doc_type: str = "text", metadata: Dict = None) -> str:
        """Add a single document to RAG"""
        doc_id = hashlib.md5(content.encode()).hexdigest()
        
        # Create document
        doc = Document(
            id=doc_id,
            content=content,
            metadata={
                "title": title,
                "source": source,
                "type": doc_type,
                **(metadata or {})
            },
            timestamp=datetime.now()
        )
        
        # Add to vector store
        self.vector_store.add_documents([doc])
        
        # Add to metadata DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO documents 
            (id, title, source, doc_type, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, title, source, doc_type,
            datetime.now(), datetime.now(),
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        return doc_id
    
    def add_knowledge_base(self, knowledge_dict: Dict[str, Any]) -> int:
        """Add structured knowledge base to RAG"""
        added_count = 0
        
        for category, items in knowledge_dict.items():
            if isinstance(items, dict):
                for key, value in items.items():
                    content = f"{category} - {key}: {json.dumps(value, ensure_ascii=False)}"
                    self.add_document(
                        content=content,
                        title=f"{category}/{key}",
                        source="knowledge_base",
                        doc_type="knowledge",
                        metadata={"category": category, "key": key}
                    )
                    added_count += 1
            elif isinstance(items, list):
                for i, item in enumerate(items):
                    content = f"{category}: {json.dumps(item, ensure_ascii=False)}"
                    self.add_document(
                        content=content,
                        title=f"{category}[{i}]",
                        source="knowledge_base",
                        doc_type="knowledge",
                        metadata={"category": category, "index": i}
                    )
                    added_count += 1
        
        return added_count
    
    def search(self, query: str, k: int = 5, filter_type: str = None) -> List[Dict]:
        """Search for relevant documents"""
        # Vector search
        results = self.vector_store.search(query, k=k)
        
        # Filter by type if specified
        if filter_type:
            results = [(doc, score) for doc, score in results 
                      if doc.metadata.get('type') == filter_type]
        
        # Log query
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO queries (query, results, timestamp)
            VALUES (?, ?, ?)
        """, (
            query,
            json.dumps([doc.id for doc, _ in results]),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'id': doc.id,
                'content': doc.content,
                'score': score,
                'metadata': doc.metadata
            })
        
        return formatted_results
    
    def get_context_for_query(self, query: str, max_tokens: int = 2000) -> str:
        """Get relevant context for a query"""
        results = self.search(query, k=10)
        
        context = "Relevant information:\n\n"
        current_tokens = 0
        
        for result in results:
            content = result['content']
            # Simple token estimation (1 token ≈ 4 characters)
            content_tokens = len(content) // 4
            
            if current_tokens + content_tokens > max_tokens:
                break
            
            context += f"- {content}\n"
            current_tokens += content_tokens
        
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get document count
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        # Get query count
        cursor.execute("SELECT COUNT(*) FROM queries")
        query_count = cursor.fetchone()[0]
        
        # Get document types
        cursor.execute("SELECT doc_type, COUNT(*) FROM documents GROUP BY doc_type")
        doc_types = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_documents": doc_count,
            "total_queries": query_count,
            "document_types": doc_types,
            "vector_store": VECTOR_DB,
            "storage_path": str(self.storage_path)
        }

# Singleton instance
_rag_instance = None

def get_rag_system() -> LightweightRAG:
    """Get singleton RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = LightweightRAG()
    return _rag_instance

# Example usage
if __name__ == "__main__":
    # Initialize RAG
    rag = get_rag_system()
    
    # Add sample documents
    doc_id = rag.add_document(
        content="NETZ Informatique offers Python training for 3500€",
        title="Python Training",
        source="pricing",
        doc_type="service"
    )
    print(f"Added document: {doc_id}")
    
    # Search
    results = rag.search("Python training price", k=3)
    print("\nSearch results:")
    for result in results:
        print(f"- {result['content']} (score: {result['score']:.2f})")
    
    # Get stats
    stats = rag.get_stats()
    print(f"\nRAG Stats: {json.dumps(stats, indent=2)}")