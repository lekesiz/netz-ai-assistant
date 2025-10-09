import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np
from sentence_transformers import SentenceTransformer
import hashlib
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self, qdrant_url: str = "localhost:6333"):
        """Initialize data ingestion pipeline"""
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.collection_name = "netz_documents"
        self.vector_size = 384  # Size for MiniLM model
        
        # Create collection if it doesn't exist
        self._create_collection()
    
    def _create_collection(self):
        """Create Qdrant collection for documents"""
        collections = self.qdrant_client.get_collections()
        if not any(col.name == self.collection_name for col in collections.collections):
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into chunks for embedding"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def process_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a single document and prepare for ingestion"""
        logger.info(f"Processing: {file_path.name}")
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.txt', '.md']:
            text = file_path.read_text(encoding='utf-8', errors='ignore')
        else:
            logger.warning(f"Unsupported file type: {file_path.suffix}")
            return []
        
        if not text:
            return []
        
        # Create chunks
        chunks = self.chunk_text(text)
        
        # Prepare documents
        documents = []
        for i, chunk in enumerate(chunks):
            doc_id = hashlib.md5(f"{file_path.name}_{i}".encode()).hexdigest()
            
            documents.append({
                "id": doc_id,
                "text": chunk,
                "metadata": {
                    "source": str(file_path),
                    "filename": file_path.name,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_type": file_path.suffix,
                    "ingested_at": datetime.now().isoformat()
                }
            })
        
        return documents
    
    def ingest_documents(self, documents: List[Dict[str, Any]]):
        """Ingest documents into Qdrant"""
        if not documents:
            return
        
        # Extract texts for embedding
        texts = [doc["text"] for doc in documents]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        
        # Prepare points for Qdrant
        points = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            points.append(
                PointStruct(
                    id=i,
                    vector=embedding.tolist(),
                    payload={
                        "text": doc["text"],
                        "metadata": doc["metadata"]
                    }
                )
            )
        
        # Upload to Qdrant
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Ingested {len(points)} document chunks")
    
    def ingest_directory(self, directory_path: str, file_patterns: List[str] = ["*.pdf", "*.txt"]):
        """Ingest all matching files from a directory"""
        path = Path(directory_path)
        all_documents = []
        
        for pattern in file_patterns:
            for file_path in path.rglob(pattern):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    docs = self.process_document(file_path)
                    all_documents.extend(docs)
        
        if all_documents:
            self.ingest_documents(all_documents)
            logger.info(f"Total documents processed: {len(all_documents)}")
        else:
            logger.warning("No documents found to process")
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        # Generate query embedding
        query_vector = self.encoder.encode(query).tolist()
        
        # Search in Qdrant
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        # Format results
        results = []
        for hit in search_result:
            results.append({
                "text": hit.payload["text"],
                "metadata": hit.payload["metadata"],
                "score": hit.score
            })
        
        return results

# Example usage
if __name__ == "__main__":
    # Initialize ingestion pipeline
    ingestion = DataIngestion()
    
    # Test with a specific directory
    netz_docs_path = "/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Diğer bilgisayarlar/Mon ordinateur/Commun/1. NETZ INFORMATIQUE/1.5 DOCUMENTS ADMINISTRATIFS/KBIS"
    
    if os.path.exists(netz_docs_path):
        print(f"Ingesting documents from: {netz_docs_path}")
        ingestion.ingest_directory(netz_docs_path, ["*.pdf"])
        
        # Test search
        results = ingestion.search("NETZ INFORMATIQUE SIREN")
        print(f"\nSearch results for 'NETZ INFORMATIQUE SIREN':")
        for i, result in enumerate(results):
            print(f"\n{i+1}. Score: {result['score']:.3f}")
            print(f"   Source: {result['metadata']['filename']}")
            print(f"   Text: {result['text'][:200]}...")
    else:
        print(f"Path not found: {netz_docs_path}")