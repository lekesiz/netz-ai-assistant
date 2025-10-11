"""
Unit tests for Lightweight RAG System
"""

import pytest
import json
from pathlib import Path
from lightweight_rag import (
    Document, EmbeddingGenerator, NumpyVectorStore,
    LightweightRAG, get_rag_system
)


class TestDocument:
    """Test Document dataclass"""
    
    @pytest.mark.unit
    def test_document_creation(self):
        """Test creating a document"""
        doc = Document(
            id="test123",
            content="Test content",
            metadata={"key": "value"},
            embedding=[0.1, 0.2, 0.3]
        )
        
        assert doc.id == "test123"
        assert doc.content == "Test content"
        assert doc.metadata["key"] == "value"
        assert doc.embedding == [0.1, 0.2, 0.3]


class TestEmbeddingGenerator:
    """Test embedding generation functionality"""
    
    @pytest.fixture
    def generator(self):
        """Create embedding generator instance"""
        return EmbeddingGenerator()
    
    @pytest.mark.unit
    def test_generate_embedding(self, generator):
        """Test single embedding generation"""
        text = "Python training at NETZ costs 3500 euros"
        embedding = generator.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == generator.dimension
        assert all(isinstance(x, float) for x in embedding)
        
        # Check normalization (unit vector)
        import numpy as np
        norm = np.linalg.norm(embedding)
        assert norm == pytest.approx(1.0, rel=1e-5)
    
    @pytest.mark.unit
    def test_embedding_consistency(self, generator):
        """Test that same text produces same embedding"""
        text = "Test consistency"
        embedding1 = generator.generate_embedding(text)
        embedding2 = generator.generate_embedding(text)
        
        assert embedding1 == embedding2
    
    @pytest.mark.unit
    def test_embedding_difference(self, generator):
        """Test that different texts produce different embeddings"""
        text1 = "Python programming"
        text2 = "Excel spreadsheet"
        
        embedding1 = generator.generate_embedding(text1)
        embedding2 = generator.generate_embedding(text2)
        
        assert embedding1 != embedding2
    
    @pytest.mark.unit
    def test_batch_generate(self, generator):
        """Test batch embedding generation"""
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = generator.batch_generate(texts)
        
        assert len(embeddings) == 3
        assert all(len(emb) == generator.dimension for emb in embeddings)


class TestNumpyVectorStore:
    """Test numpy-based vector store"""
    
    @pytest.fixture
    def store(self, temp_dir):
        """Create a test vector store"""
        return NumpyVectorStore(str(temp_dir))
    
    @pytest.mark.unit
    def test_add_documents(self, store):
        """Test adding documents to store"""
        docs = [
            Document("1", "Python training", {"type": "service"}),
            Document("2", "Excel training", {"type": "service"}),
            Document("3", "Company info", {"type": "info"})
        ]
        
        store.add_documents(docs)
        
        assert len(store.index['documents']) == 3
        assert len(store.index['embeddings']) == 3
        assert len(store.index['ids']) == 3
    
    @pytest.mark.unit
    def test_search(self, store):
        """Test vector search functionality"""
        # Add test documents
        docs = [
            Document("1", "Python programming training advanced", {"type": "service"}),
            Document("2", "Excel spreadsheet training basic", {"type": "service"}),
            Document("3", "JavaScript web development", {"type": "service"})
        ]
        store.add_documents(docs)
        
        # Search for Python-related content
        results = store.search("Python coding course", k=2)
        
        assert len(results) == 2
        assert results[0][0].id == "1"  # Most relevant should be Python doc
        assert results[0][1] > results[1][1]  # First result should have higher score
    
    @pytest.mark.unit
    def test_delete_documents(self, store):
        """Test document deletion"""
        docs = [
            Document("1", "Doc 1", {}),
            Document("2", "Doc 2", {}),
            Document("3", "Doc 3", {})
        ]
        store.add_documents(docs)
        
        # Delete doc 2
        store.delete(["2"])
        
        assert len(store.index['documents']) == 2
        assert "2" not in store.index['ids']
        assert "1" in store.index['ids']
        assert "3" in store.index['ids']
    
    @pytest.mark.unit
    def test_persistence(self, store, temp_dir):
        """Test index persistence"""
        # Add document
        doc = Document("1", "Test persistence", {})
        store.add_documents([doc])
        
        # Create new store instance with same path
        store2 = NumpyVectorStore(str(temp_dir))
        
        # Should load existing index
        assert len(store2.index['documents']) == 1
        assert store2.index['documents']['1'].content == "Test persistence"


class TestLightweightRAG:
    """Test main RAG system"""
    
    @pytest.fixture
    def rag(self, temp_dir):
        """Create a test RAG instance"""
        return LightweightRAG(storage_path=str(temp_dir))
    
    @pytest.mark.unit
    def test_add_document(self, rag):
        """Test adding a single document"""
        doc_id = rag.add_document(
            content="Python training costs 3500 euros",
            title="Python Pricing",
            source="catalog",
            doc_type="service"
        )
        
        assert doc_id is not None
        assert len(doc_id) == 32  # MD5 hash length
        
        # Verify in stats
        stats = rag.get_stats()
        assert stats["total_documents"] == 1
    
    @pytest.mark.unit
    def test_add_knowledge_base(self, rag):
        """Test adding structured knowledge base"""
        knowledge = {
            "services": {
                "python": "Advanced Python training",
                "excel": "Excel mastery course"
            },
            "pricing": [
                {"service": "Python", "price": 3500},
                {"service": "Excel", "price": 1200}
            ]
        }
        
        added_count = rag.add_knowledge_base(knowledge)
        assert added_count == 4  # 2 services + 2 pricing items
        
        stats = rag.get_stats()
        assert stats["total_documents"] == 4
    
    @pytest.mark.unit
    def test_search(self, rag):
        """Test RAG search functionality"""
        # Add test documents
        rag.add_document("Python advanced training for data science", "Python DS")
        rag.add_document("Excel VBA macro programming", "Excel VBA")
        rag.add_document("Company founded in 2016 by Mikail", "Company Info")
        
        # Search for Python
        results = rag.search("Python programming", k=2)
        
        assert len(results) <= 2
        if results:
            assert "Python" in results[0]["content"]
            assert results[0]["score"] > 0
    
    @pytest.mark.unit
    def test_get_context_for_query(self, rag):
        """Test context extraction for queries"""
        # Add documents
        rag.add_document("Python costs 3500 euros for 70 hours", "Python Price")
        rag.add_document("Excel costs 1200 euros for 35 hours", "Excel Price")
        
        context = rag.get_context_for_query("What are the training prices?")
        
        assert "Python" in context
        assert "Excel" in context
        assert "3500" in context
        assert "1200" in context
    
    @pytest.mark.unit
    def test_filter_by_type(self, rag):
        """Test filtering search results by document type"""
        # Add mixed documents
        rag.add_document("Service info", "Service", doc_type="service")
        rag.add_document("Company info", "Company", doc_type="info")
        rag.add_document("Financial data", "Finance", doc_type="financial")
        
        # Search with filter
        service_results = rag.search("info", k=10, filter_type="service")
        
        assert all(r["metadata"]["type"] == "service" for r in service_results)
    
    @pytest.mark.unit
    def test_metadata_persistence(self, rag):
        """Test that metadata is persisted correctly"""
        metadata = {
            "author": "Test User",
            "version": "1.0",
            "tags": ["test", "sample"]
        }
        
        doc_id = rag.add_document(
            content="Test document",
            title="Test",
            metadata=metadata
        )
        
        # Search and verify metadata
        results = rag.search("Test document", k=1)
        assert results[0]["metadata"]["author"] == "Test User"
        assert results[0]["metadata"]["tags"] == ["test", "sample"]
    
    @pytest.mark.unit
    def test_singleton_pattern(self):
        """Test RAG singleton pattern"""
        rag1 = get_rag_system()
        rag2 = get_rag_system()
        assert rag1 is rag2
    
    @pytest.mark.unit
    def test_empty_search(self, rag):
        """Test searching empty RAG"""
        results = rag.search("Any query", k=5)
        assert isinstance(results, list)
        assert len(results) == 0
    
    @pytest.mark.unit
    def test_duplicate_content(self, rag):
        """Test handling duplicate content"""
        content = "Duplicate content test"
        
        id1 = rag.add_document(content, "Doc 1")
        id2 = rag.add_document(content, "Doc 2")
        
        # Same content should produce same ID
        assert id1 == id2
        
        # Should only have one document
        stats = rag.get_stats()
        assert stats["total_documents"] == 1