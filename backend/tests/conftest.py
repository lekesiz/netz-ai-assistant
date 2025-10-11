"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
import tempfile
import shutil
from pathlib import Path
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_api import app
from lightweight_rag import LightweightRAG
from performance_optimizer import OptimizationOrchestrator
from language_detection_system import LanguageDetectionSystem
from enhanced_knowledge_base import EnhancedKnowledgeBase


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_test_client() -> AsyncGenerator:
    """Create an async test client."""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_ollama():
    """Mock Ollama responses."""
    with patch("ollama.chat") as mock_chat, \
         patch("ollama.generate") as mock_generate:
        
        # Default chat response
        mock_chat.return_value = {
            "message": {
                "content": "Test response from mock Ollama"
            }
        }
        
        # Default generate response
        mock_generate.return_value = {
            "response": "Generated text"
        }
        
        yield {
            "chat": mock_chat,
            "generate": mock_generate
        }


@pytest.fixture
def mock_rag(temp_dir):
    """Create a mock RAG instance with temporary storage."""
    rag = LightweightRAG(storage_path=str(temp_dir))
    
    # Add some test documents
    rag.add_document(
        content="Python training costs 3500 euros",
        title="Python Training",
        source="test",
        doc_type="service"
    )
    
    rag.add_document(
        content="Excel training costs 1200 euros",
        title="Excel Training", 
        source="test",
        doc_type="service"
    )
    
    return rag


@pytest.fixture
def mock_optimizer():
    """Create a mock optimization orchestrator."""
    optimizer = OptimizationOrchestrator()
    optimizer.cache.cache.clear()  # Clear any existing cache
    return optimizer


@pytest.fixture
def language_detector():
    """Create a language detection instance."""
    return LanguageDetectionSystem()


@pytest.fixture
def knowledge_base():
    """Create a knowledge base instance."""
    return EnhancedKnowledgeBase()


@pytest.fixture
def sample_messages():
    """Sample chat messages for testing."""
    return {
        "english": [{"role": "user", "content": "What is NETZ?"}],
        "french": [{"role": "user", "content": "Qu'est-ce que NETZ?"}],
        "turkish": [{"role": "user", "content": "NETZ nedir?"}],
        "mixed": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Bonjour!"},
            {"role": "user", "content": "Merhaba"}
        ]
    }


@pytest.fixture
def mock_pennylane_data():
    """Mock PennyLane financial data."""
    return {
        "financial_overview": {
            "revenue_analysis": {
                "status": "success",
                "summary": {
                    "total_revenue": 119386.85,
                    "invoice_count": 142,
                    "average_invoice": 840.75
                },
                "customer_analysis": {
                    "Client A": {
                        "total_revenue": 15000,
                        "invoice_count": 10
                    },
                    "Client B": {
                        "total_revenue": 12000,
                        "invoice_count": 8
                    }
                },
                "service_analysis": {
                    "Python Training": {
                        "total_revenue": 19000,
                        "invoice_count": 5
                    },
                    "Excel Training": {
                        "total_revenue": 35815.85,
                        "invoice_count": 28
                    }
                }
            }
        },
        "last_updated": "2025-01-10T12:00:00"
    }


@pytest.fixture
def mock_web_search():
    """Mock web search results."""
    with patch("web_search_integration.WebSearchEngine.search") as mock_search:
        mock_search.return_value = {
            "status": "success",
            "query": "test query",
            "results": [
                {
                    "title": "Test Result 1",
                    "url": "https://example.com/1",
                    "snippet": "This is a test result",
                    "source": "Mock Search"
                }
            ]
        }
        yield mock_search


@pytest.fixture
def performance_metrics():
    """Sample performance metrics for testing."""
    return {
        "response_times": [0.1, 0.2, 0.15, 0.3, 0.25],
        "cache_hits": 10,
        "cache_misses": 5,
        "error_count": 1
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    # Reset any singleton instances to avoid test interference
    from lightweight_rag import _rag_instance
    from performance_optimizer import OptimizationOrchestrator
    
    # Clear RAG instance
    import lightweight_rag
    lightweight_rag._rag_instance = None
    
    # Clear optimizer instance
    OptimizationOrchestrator._instance = None
    
    yield


@pytest.fixture
def env_vars():
    """Set and restore environment variables for tests."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["PENNYLANE_API_KEY"] = "test_key"
    os.environ["PENNYLANE_COMPANY_ID"] = "test_company"
    
    yield os.environ
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)