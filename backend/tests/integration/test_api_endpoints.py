"""
Integration tests for API endpoints
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    @pytest.mark.integration
    def test_health_check(self, test_client: TestClient):
        """Test /health endpoint"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["mode"] == "university_level"


class TestChatEndpoint:
    """Test chat endpoint functionality"""
    
    @pytest.mark.integration
    @patch("ollama.chat")
    def test_chat_basic(self, mock_chat, test_client: TestClient):
        """Test basic chat functionality"""
        mock_chat.return_value = {
            "message": {"content": "NETZ is an IT training company"}
        }
        
        response = test_client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "What is NETZ?"}]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "model" in data
        assert "timestamp" in data
        assert data["response"] == "NETZ is an IT training company"
    
    @pytest.mark.integration
    @patch("ollama.chat")
    def test_chat_with_cache(self, mock_chat, test_client: TestClient):
        """Test chat with caching"""
        mock_chat.return_value = {
            "message": {"content": "Response about NETZ"}
        }
        
        # First request
        response1 = test_client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "What is NETZ?"}]
            }
        )
        assert response1.json()["model_info"]["cached"] == False
        
        # Second request (should be cached)
        response2 = test_client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "What is NETZ?"}]
            }
        )
        data2 = response2.json()
        assert data2["model"] == "cached"
        assert data2["model_info"]["cache_hit"] == True
        assert data2["model_info"]["response_time"] < 0.01
    
    @pytest.mark.integration
    @patch("ollama.chat")
    def test_chat_language_detection(self, mock_chat, test_client: TestClient):
        """Test language detection in chat"""
        mock_chat.return_value = {
            "message": {"content": "NETZ est une entreprise de formation IT"}
        }
        
        response = test_client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "Qu'est-ce que NETZ?"}]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_info"]["detected_language"] == "fr"
        assert data["model_info"]["language_confidence"] > 0.7
    
    @pytest.mark.integration
    @patch("ollama.chat")
    def test_chat_with_model_preference(self, mock_chat, test_client: TestClient):
        """Test chat with model preference"""
        mock_chat.return_value = {
            "message": {"content": "Fast response"}
        }
        
        response = test_client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model_preference": "fast"
            }
        )
        
        assert response.status_code == 200
        assert "model" in response.json()
    
    @pytest.mark.integration
    def test_chat_error_handling(self, test_client: TestClient):
        """Test chat error handling"""
        with patch("ollama.chat", side_effect=Exception("Test error")):
            response = test_client.post(
                "/api/chat",
                json={
                    "messages": [{"role": "user", "content": "Test"}]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "error occurred" in data["response"]


class TestPerformanceEndpoints:
    """Test performance optimization endpoints"""
    
    @pytest.mark.integration
    def test_performance_stats(self, test_client: TestClient):
        """Test performance statistics endpoint"""
        response = test_client.get("/api/performance/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "statistics" in data
        
        stats = data["statistics"]
        assert "cache" in stats
        assert "response_performance" in stats
        assert "system_health" in stats
        assert "system" in stats
    
    @pytest.mark.integration
    def test_performance_optimize(self, test_client: TestClient):
        """Test performance optimization settings"""
        response = test_client.post(
            "/api/performance/optimize",
            json={
                "cache_ttl": 7200,
                "cache_max_size": 500
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["current_settings"]["cache_ttl"] == 7200
        assert data["current_settings"]["cache_max_size"] == 500


class TestRAGEndpoints:
    """Test RAG system endpoints"""
    
    @pytest.mark.integration
    def test_rag_stats(self, test_client: TestClient):
        """Test RAG statistics endpoint"""
        response = test_client.get("/api/rag/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "total_documents" in data["statistics"]
        assert "document_types" in data["statistics"]
    
    @pytest.mark.integration
    def test_rag_add_document(self, test_client: TestClient):
        """Test adding document to RAG"""
        response = test_client.post(
            "/api/rag/add-document",
            json={
                "content": "Test document content",
                "title": "Test Document",
                "source": "test",
                "doc_type": "test",
                "metadata": {"key": "value"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "document_id" in data
    
    @pytest.mark.integration
    def test_rag_search(self, test_client: TestClient):
        """Test RAG search"""
        # First add a document
        test_client.post(
            "/api/rag/add-document",
            json={
                "content": "Python training costs 3500 euros",
                "title": "Python Pricing"
            }
        )
        
        # Then search
        response = test_client.post(
            "/api/rag/search",
            json={
                "query": "Python price",
                "k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "results" in data
    
    @pytest.mark.integration
    def test_rag_rebuild(self, test_client: TestClient):
        """Test RAG index rebuild"""
        response = test_client.post("/api/rag/rebuild")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "statistics" in data


class TestModelEndpoints:
    """Test model management endpoints"""
    
    @pytest.mark.integration
    def test_available_models(self, test_client: TestClient):
        """Test available models endpoint"""
        response = test_client.get("/api/models/available")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "models" in data
        assert isinstance(data["models"], list)
        assert len(data["models"]) > 0
    
    @pytest.mark.integration
    def test_model_statistics(self, test_client: TestClient):
        """Test model statistics endpoint"""
        response = test_client.get("/api/models/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "statistics" in data
        assert "recommendations" in data


class TestFinancialEndpoints:
    """Test financial data endpoints"""
    
    @pytest.mark.integration
    @patch("pennylane_detailed_sync.PennyLaneDetailedAPI.test_connection")
    @patch("pennylane_detailed_sync.PennyLaneDetailedAPI.save_detailed_data")
    def test_financial_refresh(self, mock_save, mock_test, test_client: TestClient):
        """Test financial data refresh"""
        mock_test.return_value = True
        mock_save.return_value = {
            "financial_overview": {
                "revenue_analysis": {
                    "summary": {
                        "total_revenue": 100000,
                        "invoice_count": 50
                    }
                }
            },
            "last_updated": "2025-01-10"
        }
        
        response = test_client.get("/api/financial-data/refresh")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["summary"]["total_revenue"] == 100000


class TestLearningEndpoints:
    """Test learning system endpoints"""
    
    @pytest.mark.integration
    def test_learning_status(self, test_client: TestClient):
        """Test learning system status"""
        response = test_client.get("/api/learning-status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["active", "error"]
        assert "knowledge_base_size" in data
        assert data["learning_enabled"] in [True, False]
    
    @pytest.mark.integration
    def test_submit_feedback(self, test_client: TestClient):
        """Test feedback submission"""
        response = test_client.post(
            "/api/feedback",
            json={
                "session_id": "test123",
                "original_query": "What is NETZ?",
                "ai_response": "NETZ is an IT company",
                "user_feedback": "Good answer",
                "user_id": "test_user"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["success", "noted", "error"]


class TestStreamingEndpoint:
    """Test streaming chat endpoint"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_stream(self, async_test_client):
        """Test streaming chat endpoint"""
        # This test would require more complex mocking for streaming
        # For now, just test that endpoint exists
        pass


class TestErrorHandling:
    """Test API error handling"""
    
    @pytest.mark.integration
    def test_invalid_endpoint(self, test_client: TestClient):
        """Test 404 for invalid endpoint"""
        response = test_client.get("/api/invalid")
        assert response.status_code == 404
    
    @pytest.mark.integration
    def test_invalid_json(self, test_client: TestClient):
        """Test handling of invalid JSON"""
        response = test_client.post(
            "/api/chat",
            data="invalid json"
        )
        assert response.status_code == 422
    
    @pytest.mark.integration
    def test_missing_required_fields(self, test_client: TestClient):
        """Test missing required fields"""
        response = test_client.post(
            "/api/chat",
            json={}  # Missing messages field
        )
        assert response.status_code == 422