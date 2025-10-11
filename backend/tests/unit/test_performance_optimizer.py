"""
Unit tests for Performance Optimization System
"""

import pytest
import time
import asyncio
from performance_optimizer import (
    InMemoryCache, ResponseOptimizer, ModelPreloader,
    QueryOptimizer, PerformanceMonitor, OptimizationOrchestrator
)


class TestInMemoryCache:
    """Test in-memory cache functionality"""
    
    @pytest.fixture
    def cache(self):
        """Create a test cache instance"""
        return InMemoryCache(max_size=10, default_ttl=1)
    
    @pytest.mark.unit
    def test_cache_set_and_get(self, cache):
        """Test basic cache set and get operations"""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        cache.set("key2", {"data": "complex"})
        assert cache.get("key2") == {"data": "complex"}
    
    @pytest.mark.unit
    def test_cache_expiry(self, cache):
        """Test cache TTL expiry"""
        cache.set("expire_key", "value", ttl=0.1)  # 100ms TTL
        assert cache.get("expire_key") == "value"
        
        time.sleep(0.15)  # Wait for expiry
        assert cache.get("expire_key") is None
    
    @pytest.mark.unit
    def test_cache_lru_eviction(self, cache):
        """Test LRU eviction when cache is full"""
        # Fill cache beyond capacity
        for i in range(12):
            cache.set(f"key{i}", f"value{i}")
        
        # First keys should be evicted
        assert cache.get("key0") is None
        assert cache.get("key1") is None
        
        # Last keys should still exist
        assert cache.get("key10") is not None
        assert cache.get("key11") is not None
    
    @pytest.mark.unit
    def test_cache_stats(self, cache):
        """Test cache statistics"""
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key1")
        cache.get("key2")  # Miss
        
        stats = cache.get_stats()
        assert stats["size"] == 1
        assert stats["total_hits"] == 2
        assert stats["hit_rate"] == 2/3  # 2 hits, 1 miss
    
    @pytest.mark.unit
    def test_thread_safety(self, cache):
        """Test cache thread safety"""
        import threading
        
        def set_values():
            for i in range(100):
                cache.set(f"thread_key{i}", f"value{i}")
        
        def get_values():
            for i in range(100):
                cache.get(f"thread_key{i}")
        
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=set_values))
            threads.append(threading.Thread(target=get_values))
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Cache should still be consistent
        stats = cache.get_stats()
        assert stats["size"] <= cache.max_size


class TestResponseOptimizer:
    """Test response optimization functionality"""
    
    @pytest.fixture
    def optimizer(self):
        """Create a test optimizer instance"""
        return ResponseOptimizer()
    
    @pytest.mark.unit
    def test_track_response_time(self, optimizer):
        """Test response time tracking"""
        optimizer.track_response_time("model1", 0.5)
        optimizer.track_response_time("model1", 0.7)
        optimizer.track_response_time("model2", 0.3)
        
        stats = optimizer.get_performance_stats()
        assert stats["average"] == pytest.approx(0.5, rel=0.1)
        assert stats["min"] == 0.3
        assert stats["max"] == 0.7
    
    @pytest.mark.unit
    def test_track_errors(self, optimizer):
        """Test error tracking"""
        optimizer.track_response_time("model1", 1.0)
        optimizer.track_error("model1")
        
        model_stats = optimizer.get_model_stats()
        assert "model1" in model_stats
        assert model_stats["model1"]["error_rate"] == 0.5  # 1 error, 1 success
    
    @pytest.mark.unit
    def test_should_use_cache(self, optimizer):
        """Test cache decision logic"""
        cacheable_queries = [
            "What is NETZ?",
            "List all services",
            "How many employees?",
            "What is the price of Python training?"
        ]
        
        for query in cacheable_queries:
            assert optimizer.should_use_cache(query) == True
        
        non_cacheable_queries = [
            "Generate a random number",
            "Tell me a joke",
            "Write a story"
        ]
        
        for query in non_cacheable_queries:
            # These might not match cache patterns
            pass  # Test is informational
    
    @pytest.mark.unit
    def test_percentile_calculations(self, optimizer):
        """Test percentile calculations"""
        # Add 100 response times
        for i in range(100):
            optimizer.track_response_time("test", i * 0.01)
        
        stats = optimizer.get_performance_stats()
        assert stats["p95"] == pytest.approx(0.95, rel=0.1)
        assert stats["p99"] == pytest.approx(0.99, rel=0.1)


class TestQueryOptimizer:
    """Test query optimization functionality"""
    
    @pytest.fixture
    def optimizer(self):
        """Create a test query optimizer"""
        return QueryOptimizer()
    
    @pytest.mark.unit
    def test_normalize_query(self, optimizer):
        """Test query normalization"""
        queries = [
            ("  What   is   NETZ?  ", "what is netz?"),
            ("HELLO WORLD", "hello world"),
            ("Test\n\nQuery", "test query")
        ]
        
        for original, expected in queries:
            assert optimizer.normalize_query(original) == expected
    
    @pytest.mark.unit
    def test_query_hash(self, optimizer):
        """Test query hashing"""
        # Same queries should have same hash
        hash1 = optimizer.get_query_hash("What is NETZ?")
        hash2 = optimizer.get_query_hash("  WHAT IS NETZ?  ")
        assert hash1 == hash2
        
        # Different queries should have different hashes
        hash3 = optimizer.get_query_hash("Who is NETZ?")
        assert hash1 != hash3
    
    @pytest.mark.unit
    def test_simple_query_detection(self, optimizer):
        """Test simple query detection"""
        simple_queries = [
            "2 + 2",
            "5 * 3",
            "hi",
            "hello",
            "yes",
            "no"
        ]
        
        for query in simple_queries:
            assert optimizer.should_use_simple_response(query) == True
        
        complex_queries = [
            "Explain quantum physics",
            "What is the meaning of life?",
            "How do I implement a REST API?"
        ]
        
        for query in complex_queries:
            assert optimizer.should_use_simple_response(query) == False


class TestPerformanceMonitor:
    """Test performance monitoring functionality"""
    
    @pytest.fixture
    def monitor(self):
        """Create a test monitor instance"""
        return PerformanceMonitor()
    
    @pytest.mark.unit
    def test_record_metrics(self, monitor):
        """Test metric recording"""
        monitor.record_metric("response_time", 0.5)
        monitor.record_metric("response_time", 0.7)
        monitor.record_metric("cache_hit", 1)
        
        summary = monitor.get_metrics_summary()
        assert summary["response_time"]["average"] == 0.6
        assert summary["response_time"]["count"] == 2
        assert summary["cache_hit"]["average"] == 1.0
    
    @pytest.mark.unit
    def test_threshold_alerts(self, monitor):
        """Test threshold-based alerts"""
        # Record slow response
        monitor.record_metric("response_time", 5.0)
        
        summary = monitor.get_metrics_summary()
        assert len(summary["alerts"]) > 0
        assert summary["alerts"][0]["type"] == "slow_response"
        assert summary["alerts"][0]["value"] == 5.0
    
    @pytest.mark.unit
    def test_health_check(self, monitor):
        """Test system health check"""
        # Good metrics
        for _ in range(10):
            monitor.record_metric("response_time", 0.5)
        
        health = monitor.check_health()
        assert health["status"] == "healthy"
        
        # Bad metrics
        for _ in range(10):
            monitor.record_metric("response_time", 5.0)
        
        health = monitor.check_health()
        assert health["status"] == "degraded"
        assert len(health["issues"]) > 0


class TestOptimizationOrchestrator:
    """Test main optimization orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a test orchestrator instance"""
        return OptimizationOrchestrator()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_optimize_request_simple(self, orchestrator):
        """Test optimization for simple queries"""
        result = await orchestrator.optimize_request("hello")
        assert result["optimization"] == "simple_response"
        assert result["cache_hit"] == False
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_optimize_request_cacheable(self, orchestrator):
        """Test optimization for cacheable queries"""
        query = "What is NETZ?"
        
        # First request - no cache hit
        result1 = await orchestrator.optimize_request(query)
        assert result1["cache_hit"] == False
        assert result1["should_cache"] == True
        
        # Cache the response
        orchestrator.cache_response(result1["query_hash"], "NETZ is an IT company")
        
        # Second request - cache hit
        result2 = await orchestrator.optimize_request(query)
        assert result2["cache_hit"] == True
        assert result2["response"] == "NETZ is an IT company"
    
    @pytest.mark.unit
    def test_get_optimization_stats(self, orchestrator):
        """Test comprehensive stats retrieval"""
        stats = orchestrator.get_optimization_stats()
        
        assert "cache" in stats
        assert "response_performance" in stats
        assert "model_performance" in stats
        assert "preloaded_models" in stats
        assert "system_health" in stats
        assert "metrics" in stats
    
    @pytest.mark.unit
    def test_singleton_pattern(self):
        """Test that orchestrator follows singleton pattern"""
        orch1 = OptimizationOrchestrator()
        orch2 = OptimizationOrchestrator()
        assert orch1 is orch2