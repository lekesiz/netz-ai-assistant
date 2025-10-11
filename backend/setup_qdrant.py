#!/usr/bin/env python3
"""
Qdrant setup script for NETZ AI Project
Initializes the vector database and creates necessary collections
"""

import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import time
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantSetup:
    def __init__(self):
        self.client = None
        self.encoder = None
        
    def wait_for_qdrant(self, url="localhost:6333", max_retries=30):
        """Wait for Qdrant to be available"""
        logger.info(f"Waiting for Qdrant at {url}...")
        
        for i in range(max_retries):
            try:
                self.client = QdrantClient(url=url)
                # Test connection
                self.client.get_collections()
                logger.info("✅ Qdrant is ready!")
                return True
            except Exception as e:
                logger.info(f"Attempt {i+1}/{max_retries}: Qdrant not ready yet...")
                time.sleep(2)
        
        logger.error("❌ Qdrant failed to start")
        return False
    
    def create_collection(self, collection_name="netz_documents"):
        """Create the main collection for NETZ documents"""
        try:
            # Initialize encoder to get vector size
            logger.info("Loading embedding model...")
            self.encoder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            vector_size = self.encoder.get_sentence_embedding_dimension()
            
            # Check if collection exists
            collections = self.client.get_collections().collections
            if any(col.name == collection_name for col in collections):
                logger.info(f"Collection '{collection_name}' already exists")
                return True
            
            # Create collection
            logger.info(f"Creating collection '{collection_name}'...")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Collection '{collection_name}' created successfully")
            
            # Add sample data
            self.add_sample_data(collection_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def add_sample_data(self, collection_name):
        """Add sample data to test the collection"""
        sample_docs = [
            {
                "text": "NETZ Informatique est une entreprise spécialisée dans les services IT et la formation professionnelle à Haguenau.",
                "metadata": {"type": "company_info", "language": "fr"}
            },
            {
                "text": "Nos services incluent: support informatique, développement web, formation Excel, Python, et AutoCAD.",
                "metadata": {"type": "services", "language": "fr"}
            },
            {
                "text": "Contact: 03 88 06 25 25, email: contact@netz-informatique.fr, adresse: 67500 Haguenau",
                "metadata": {"type": "contact", "language": "fr"}
            }
        ]
        
        logger.info("Adding sample data...")
        points = []
        
        for i, doc in enumerate(sample_docs):
            # Generate embedding
            vector = self.encoder.encode(doc["text"]).tolist()
            
            points.append(PointStruct(
                id=i,
                vector=vector,
                payload={
                    "text": doc["text"],
                    "metadata": doc["metadata"]
                }
            ))
        
        # Upload points
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        logger.info(f"✅ Added {len(sample_docs)} sample documents")
    
    def verify_setup(self, collection_name="netz_documents"):
        """Verify the setup is working correctly"""
        try:
            # Check collection info
            info = self.client.get_collection(collection_name)
            logger.info(f"Collection '{collection_name}' info:")
            logger.info(f"  - Vectors count: {info.vectors_count}")
            logger.info(f"  - Points count: {info.points_count}")
            
            # Test search
            if self.encoder is None:
                self.encoder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            
            test_query = "services informatiques"
            query_vector = self.encoder.encode(test_query).tolist()
            
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=3
            )
            
            logger.info(f"\nTest search for '{test_query}':")
            for i, hit in enumerate(results):
                logger.info(f"  {i+1}. Score: {hit.score:.3f} - {hit.payload['text'][:50]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting NETZ AI Qdrant Setup")
    
    setup = QdrantSetup()
    
    # Wait for Qdrant
    if not setup.wait_for_qdrant():
        logger.error("Setup failed: Qdrant not available")
        return False
    
    # Create collection
    if not setup.create_collection():
        logger.error("Setup failed: Could not create collection")
        return False
    
    # Verify setup
    if not setup.verify_setup():
        logger.error("Setup failed: Verification failed")
        return False
    
    logger.info("✨ Qdrant setup completed successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Run data ingestion scripts to load real data")
    logger.info("2. Start main.py instead of simple_api.py")
    logger.info("3. The RAG system will be fully operational")
    
    return True

if __name__ == "__main__":
    main()