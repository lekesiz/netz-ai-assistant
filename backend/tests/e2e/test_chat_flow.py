"""
End-to-end tests for complete chat flows
"""

import pytest
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestCompleteUserJourney:
    """Test complete user interactions"""
    
    @pytest.mark.e2e
    @pytest.mark.slow
    @patch("ollama.chat")
    def test_multilingual_conversation(self, mock_chat, test_client: TestClient):
        """Test a full multilingual conversation"""
        # Mock different responses for different languages
        def mock_response(model, messages, **kwargs):
            content = messages[-1]["content"]
            if "What is" in content:
                return {"message": {"content": "NETZ is an IT training company"}}
            elif "Qu'est-ce" in content:
                return {"message": {"content": "NETZ est une entreprise de formation IT"}}
            elif "nedir" in content:
                return {"message": {"content": "NETZ bir IT eğitim şirketidir"}}
            return {"message": {"content": "Default response"}}
        
        mock_chat.side_effect = mock_response
        
        # English query
        response_en = test_client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "What is NETZ?"}]}
        )
        assert response_en.status_code == 200
        assert "IT training company" in response_en.json()["response"]
        
        # French query
        response_fr = test_client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Qu'est-ce que NETZ?"}]}
        )
        assert response_fr.status_code == 200
        assert "formation IT" in response_fr.json()["response"]
        
        # Turkish query
        response_tr = test_client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "NETZ nedir?"}]}
        )
        assert response_tr.status_code == 200
        assert "IT eğitim" in response_tr.json()["response"]
    
    @pytest.mark.e2e
    @patch("ollama.chat")
    def test_knowledge_enhancement_flow(self, mock_chat, test_client: TestClient):
        """Test knowledge enhancement through document addition"""
        mock_chat.return_value = {"message": {"content": "Based on the information..."}}
        
        # First query - before adding specific knowledge
        response1 = test_client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "What is the price of React training?"}]}
        )
        initial_response = response1.json()["response"]
        
        # Add specific pricing to RAG
        add_response = test_client.post(
            "/api/rag/add-document",
            json={
                "content": "React training costs 2800 euros for 50 hours including Redux and Next.js",
                "title": "React Training Price",
                "doc_type": "service"
            }
        )
        assert add_response.status_code == 200
        
        # Second query - after adding knowledge
        response2 = test_client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "What is the price of React training?"}]}
        )
        
        # Response should now include the specific pricing
        # (In real scenario, RAG context would be included)
        assert response2.status_code == 200
    
    @pytest.mark.e2e
    @patch("ollama.chat")
    def test_performance_optimization_journey(self, mock_chat, test_client: TestClient):
        """Test performance optimization through caching"""
        mock_chat.return_value = {"message": {"content": "NETZ offers Python training"}}
        
        # Get initial performance stats
        stats1 = test_client.get("/api/performance/stats")
        initial_cache_size = stats1.json()["statistics"]["cache"]["size"]
        
        # Make several identical queries
        query = {"messages": [{"role": "user", "content": "Tell me about Python training"}]}
        
        # First query - slow
        start_time = time.time()
        response1 = test_client.post("/api/chat", json=query)
        first_time = time.time() - start_time
        
        # Subsequent queries - should be cached
        response_times = []
        for _ in range(3):
            start_time = time.time()
            response = test_client.post("/api/chat", json=query)
            response_times.append(time.time() - start_time)
            assert response.json()["model_info"]["cache_hit"] == True
        
        # Check performance improvement
        avg_cached_time = sum(response_times) / len(response_times)
        assert avg_cached_time < first_time * 0.1  # Cached should be 10x faster
        
        # Verify cache stats updated
        stats2 = test_client.get("/api/performance/stats")
        final_cache_size = stats2.json()["statistics"]["cache"]["size"]
        assert final_cache_size > initial_cache_size
    
    @pytest.mark.e2e
    @patch("ollama.chat")
    @patch("web_search_integration.WebSearchEngine.search")
    def test_web_search_integration(self, mock_search, mock_chat, test_client: TestClient):
        """Test chat with web search integration"""
        # Mock web search results
        mock_search.return_value = {
            "status": "success",
            "results": [{
                "title": "Latest IT Training Trends 2025",
                "snippet": "AI and cloud computing are top trends",
                "url": "https://example.com"
            }]
        }
        
        # Mock chat response
        mock_chat.return_value = {
            "message": {"content": "Based on recent trends, AI and cloud are popular"}
        }
        
        # Query that should trigger web search
        response = test_client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "What are the latest IT training trends?"}],
                "enable_web_search": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_info"]["web_search_performed"] == True
    
    @pytest.mark.e2e
    def test_system_health_monitoring(self, test_client: TestClient):
        """Test system health monitoring flow"""
        # Check initial health
        health1 = test_client.get("/health")
        assert health1.json()["status"] == "healthy"
        
        # Get performance stats
        perf_stats = test_client.get("/api/performance/stats")
        assert perf_stats.json()["statistics"]["system_health"]["status"] == "healthy"
        
        # Get RAG stats
        rag_stats = test_client.get("/api/rag/stats")
        assert rag_stats.json()["status"] == "success"
        
        # Get learning status
        learning_status = test_client.get("/api/learning-status")
        assert learning_status.json()["learning_enabled"] == True
    
    @pytest.mark.e2e
    @patch("ollama.chat")
    def test_feedback_learning_cycle(self, mock_chat, test_client: TestClient):
        """Test feedback and learning cycle"""
        mock_chat.return_value = {"message": {"content": "Initial response"}}
        
        # Initial query
        chat_response = test_client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "What services does NETZ offer?"}]}
        )
        
        # Submit feedback
        feedback_response = test_client.post(
            "/api/feedback",
            json={
                "session_id": "test_session",
                "original_query": "What services does NETZ offer?",
                "ai_response": chat_response.json()["response"],
                "user_feedback": "Missing information about new cloud computing course",
                "user_id": "test_user"
            }
        )
        
        assert feedback_response.status_code == 200
        assert feedback_response.json()["status"] in ["success", "noted"]
    
    @pytest.mark.e2e
    def test_rag_lifecycle(self, test_client: TestClient):
        """Test complete RAG lifecycle"""
        # 1. Check initial state
        initial_stats = test_client.get("/api/rag/stats")
        initial_count = initial_stats.json()["statistics"]["total_documents"]
        
        # 2. Add multiple documents
        documents = [
            {
                "content": "JavaScript training: 2500 euros for beginners",
                "title": "JS Basic",
                "doc_type": "service"
            },
            {
                "content": "Advanced React with TypeScript: 3200 euros",
                "title": "React Advanced",
                "doc_type": "service"
            },
            {
                "content": "Company offers 24/7 support",
                "title": "Support Info",
                "doc_type": "info"
            }
        ]
        
        for doc in documents:
            response = test_client.post("/api/rag/add-document", json=doc)
            assert response.status_code == 200
        
        # 3. Search for specific content
        search_response = test_client.post(
            "/api/rag/search",
            json={"query": "JavaScript React training prices", "k": 5}
        )
        
        results = search_response.json()["results"]
        assert len(results) > 0
        assert any("JavaScript" in r["content"] for r in results)
        
        # 4. Filter by type
        service_search = test_client.post(
            "/api/rag/search",
            json={"query": "training", "filter_type": "service", "k": 10}
        )
        
        service_results = service_search.json()["results"]
        assert all(r["metadata"]["type"] == "service" for r in service_results)
        
        # 5. Verify final state
        final_stats = test_client.get("/api/rag/stats")
        final_count = final_stats.json()["statistics"]["total_documents"]
        assert final_count >= initial_count + len(documents)
    
    @pytest.mark.e2e
    @patch("ollama.chat")
    def test_model_selection_flow(self, mock_chat, test_client: TestClient):
        """Test dynamic model selection"""
        mock_chat.return_value = {"message": {"content": "Response"}}
        
        # Get available models
        models_response = test_client.get("/api/models/available")
        available_models = models_response.json()["models"]
        assert len(available_models) > 0
        
        # Test different query types
        queries = [
            {
                "content": "Write Python code for sorting",
                "preference": "coding"
            },
            {
                "content": "Explain quantum computing",
                "preference": "accurate"
            },
            {
                "content": "Hi there!",
                "preference": "fast"
            }
        ]
        
        for query_info in queries:
            response = test_client.post(
                "/api/chat",
                json={
                    "messages": [{"role": "user", "content": query_info["content"]}],
                    "model_preference": query_info["preference"]
                }
            )
            assert response.status_code == 200
            # Model should be selected based on preference
            assert "model" in response.json()
    
    @pytest.mark.e2e
    def test_concurrent_requests(self, test_client: TestClient):
        """Test handling concurrent requests"""
        import concurrent.futures
        
        def make_request(query):
            return test_client.post(
                "/api/chat",
                json={"messages": [{"role": "user", "content": query}]}
            )
        
        queries = [
            "What is NETZ?",
            "List all services",
            "Training prices",
            "Contact information",
            "Company history"
        ]
        
        with patch("ollama.chat") as mock_chat:
            mock_chat.return_value = {"message": {"content": "Concurrent response"}}
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, q) for q in queries]
                responses = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            # All requests should succeed
            assert all(r.status_code == 200 for r in responses)
            assert len(responses) == len(queries)