"""
Performance Optimization System for NETZ AI
Implements caching, preloading, and response optimization
"""

import time
import hashlib
import json
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
import threading
from collections import deque, defaultdict
import logging

logger = logging.getLogger(__name__)

class InMemoryCache:
    """High-performance in-memory cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.access_count = defaultdict(int)
        self.access_times = defaultdict(deque)
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self.cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                if time.time() < expiry:
                    self.access_count[key] += 1
                    self.access_times[key].append(time.time())
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        with self.lock:
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            expiry = time.time() + (ttl or self.default_ttl)
            self.cache[key] = (value, expiry)
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self.cache:
            return
        
        # Find LRU key
        lru_key = None
        oldest_access = float('inf')
        
        for key in self.cache:
            last_access = self.access_times[key][-1] if self.access_times[key] else 0
            if last_access < oldest_access:
                oldest_access = last_access
                lru_key = key
        
        if lru_key:
            del self.cache[lru_key]
            del self.access_count[lru_key]
            del self.access_times[lru_key]
    
    def _periodic_cleanup(self) -> None:
        """Clean up expired items periodically"""
        while True:
            time.sleep(300)  # Every 5 minutes
            with self.lock:
                expired_keys = []
                current_time = time.time()
                
                for key, (_, expiry) in self.cache.items():
                    if current_time > expiry:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.cache[key]
                    if key in self.access_count:
                        del self.access_count[key]
                    if key in self.access_times:
                        del self.access_times[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_hits = sum(self.access_count.values())
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "total_hits": total_hits,
                "hit_rate": total_hits / max(1, total_hits + len(self.cache)),
                "top_accessed": sorted(self.access_count.items(), key=lambda x: x[1], reverse=True)[:10]
            }

class ResponseOptimizer:
    """Optimize response generation and delivery"""
    
    def __init__(self):
        self.response_times = deque(maxlen=1000)
        self.model_performance = defaultdict(lambda: {"times": deque(maxlen=100), "errors": 0})
    
    def track_response_time(self, model: str, duration: float) -> None:
        """Track response time for analytics"""
        self.response_times.append(duration)
        self.model_performance[model]["times"].append(duration)
    
    def track_error(self, model: str) -> None:
        """Track model errors"""
        self.model_performance[model]["errors"] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.response_times:
            return {"average": 0, "p95": 0, "p99": 0}
        
        sorted_times = sorted(self.response_times)
        n = len(sorted_times)
        
        return {
            "average": sum(sorted_times) / n,
            "median": sorted_times[n // 2],
            "p95": sorted_times[int(n * 0.95)] if n > 20 else sorted_times[-1],
            "p99": sorted_times[int(n * 0.99)] if n > 100 else sorted_times[-1],
            "min": sorted_times[0],
            "max": sorted_times[-1],
            "total_requests": n
        }
    
    def get_model_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get per-model statistics"""
        stats = {}
        for model, data in self.model_performance.items():
            times = list(data["times"])
            if times:
                stats[model] = {
                    "average_time": sum(times) / len(times),
                    "error_rate": data["errors"] / max(1, len(times) + data["errors"]),
                    "request_count": len(times) + data["errors"]
                }
        return stats
    
    def should_use_cache(self, query: str) -> bool:
        """Determine if query should use cache"""
        # Cache common queries
        cache_patterns = [
            "qu'est-ce que", "what is", "qui est", "who is",
            "liste", "list", "combien", "how many",
            "prix", "price", "tarif", "cost"
        ]
        
        query_lower = query.lower()
        return any(pattern in query_lower for pattern in cache_patterns)

class ModelPreloader:
    """Preload and warm up models for faster response"""
    
    def __init__(self):
        self.preloaded_models = set()
        self.warm_queries = [
            "Bonjour",
            "Hello",
            "Merhaba",
            "Qu'est-ce que NETZ?",
            "Liste des services",
            "Prix de formation"
        ]
    
    async def preload_model(self, model_id: str) -> bool:
        """Preload a specific model"""
        try:
            import ollama
            
            # Pull model if not available
            logger.info(f"Preloading model: {model_id}")
            
            # Warm up with sample queries
            for query in self.warm_queries:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ollama.generate(
                        model=model_id,
                        prompt=query,
                        options={"num_predict": 50}
                    )
                )
            
            self.preloaded_models.add(model_id)
            logger.info(f"Successfully preloaded: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to preload {model_id}: {e}")
            return False
    
    async def preload_all_models(self, model_ids: List[str]) -> Dict[str, bool]:
        """Preload multiple models concurrently"""
        tasks = [self.preload_model(model_id) for model_id in model_ids]
        results = await asyncio.gather(*tasks)
        
        return {model_id: success for model_id, success in zip(model_ids, results)}

class QueryOptimizer:
    """Optimize queries for better performance"""
    
    def __init__(self):
        self.query_cache = InMemoryCache(max_size=500, default_ttl=1800)
        self.embedding_cache = {}
    
    def normalize_query(self, query: str) -> str:
        """Normalize query for better caching"""
        # Remove extra spaces
        normalized = " ".join(query.split())
        # Lowercase for common patterns
        normalized = normalized.lower().strip()
        return normalized
    
    def get_query_hash(self, query: str) -> str:
        """Get hash for query caching"""
        normalized = self.normalize_query(query)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def should_use_simple_response(self, query: str) -> bool:
        """Determine if query needs simple response"""
        simple_patterns = [
            r"^\d+\s*[\+\-\*/]\s*\d+$",  # Math
            r"^(hi|hello|bonjour|merhaba)$",  # Greetings
            r"^(yes|no|oui|non|evet|hayır)$",  # Simple answers
        ]
        
        import re
        query_lower = query.lower().strip()
        return any(re.match(pattern, query_lower) for pattern in simple_patterns)

class PerformanceMonitor:
    """Monitor and report performance metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: {"count": 0, "total_time": 0})
        self.alerts = []
        self.thresholds = {
            "response_time": 3.0,  # seconds
            "error_rate": 0.05,    # 5%
            "cache_hit_rate": 0.3  # 30%
        }
    
    def record_metric(self, metric_name: str, value: float) -> None:
        """Record a metric value"""
        self.metrics[metric_name]["count"] += 1
        self.metrics[metric_name]["total_time"] += value
        
        # Check thresholds
        if metric_name == "response_time" and value > self.thresholds["response_time"]:
            self.alerts.append({
                "type": "slow_response",
                "value": value,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {}
        
        for metric, data in self.metrics.items():
            if data["count"] > 0:
                summary[metric] = {
                    "average": data["total_time"] / data["count"],
                    "count": data["count"],
                    "total": data["total_time"]
                }
        
        summary["alerts"] = self.alerts[-10:]  # Last 10 alerts
        return summary
    
    def check_health(self) -> Dict[str, Any]:
        """Check system health based on metrics"""
        health = {"status": "healthy", "issues": []}
        
        # Check response time
        if "response_time" in self.metrics:
            avg_response = self.metrics["response_time"]["total_time"] / max(1, self.metrics["response_time"]["count"])
            if avg_response > self.thresholds["response_time"]:
                health["status"] = "degraded"
                health["issues"].append(f"High average response time: {avg_response:.2f}s")
        
        return health

class OptimizationOrchestrator:
    """Main orchestrator for all optimization components"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.cache = InMemoryCache()
            self.response_optimizer = ResponseOptimizer()
            self.model_preloader = ModelPreloader()
            self.query_optimizer = QueryOptimizer()
            self.performance_monitor = PerformanceMonitor()
            self.initialized = True
    
    async def optimize_request(self, query: str, model: str = None) -> Dict[str, Any]:
        """Main optimization entry point"""
        start_time = time.time()
        
        # Check if simple response
        if self.query_optimizer.should_use_simple_response(query):
            return {
                "optimization": "simple_response",
                "cache_hit": False,
                "response_time": time.time() - start_time
            }
        
        # Check cache
        query_hash = self.query_optimizer.get_query_hash(query)
        cached_response = self.cache.get(query_hash)
        
        if cached_response and self.response_optimizer.should_use_cache(query):
            response_time = time.time() - start_time
            self.performance_monitor.record_metric("cache_hit", 1)
            self.performance_monitor.record_metric("response_time", response_time)
            
            return {
                "response": cached_response,
                "optimization": "cached",
                "cache_hit": True,
                "response_time": response_time
            }
        
        # No cache hit
        self.performance_monitor.record_metric("cache_miss", 1)
        
        return {
            "optimization": "none",
            "cache_hit": False,
            "query_hash": query_hash,
            "should_cache": self.response_optimizer.should_use_cache(query)
        }
    
    def cache_response(self, query_hash: str, response: str, ttl: int = None) -> None:
        """Cache a response"""
        self.cache.set(query_hash, response, ttl)
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        return {
            "cache": self.cache.get_stats(),
            "response_performance": self.response_optimizer.get_performance_stats(),
            "model_performance": self.response_optimizer.get_model_stats(),
            "preloaded_models": list(self.model_preloader.preloaded_models),
            "system_health": self.performance_monitor.check_health(),
            "metrics": self.performance_monitor.get_metrics_summary()
        }

# Singleton accessor
def get_optimization_orchestrator() -> OptimizationOrchestrator:
    """Get the singleton optimization orchestrator"""
    return OptimizationOrchestrator()

# Example usage
if __name__ == "__main__":
    async def test_optimization():
        orchestrator = get_optimization_orchestrator()
        
        # Test optimization
        result = await orchestrator.optimize_request("What is NETZ?")
        print("Optimization result:", result)
        
        # Cache a response
        if not result["cache_hit"]:
            orchestrator.cache_response(result["query_hash"], "NETZ is an IT company...")
        
        # Get stats
        stats = orchestrator.get_optimization_stats()
        print("\nOptimization stats:", json.dumps(stats, indent=2))
        
        # Preload models
        models = ["mistral:latest", "llama3.2:latest"]
        preload_results = await orchestrator.model_preloader.preload_all_models(models)
        print("\nModel preload results:", preload_results)
    
    asyncio.run(test_optimization())