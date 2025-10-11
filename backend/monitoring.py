"""
Monitoring and observability for NETZ AI
"""

import time
import psutil
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import json
import logging
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import aiofiles

from config import settings


# Metrics
request_count = Counter(
    "netz_ai_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "netz_ai_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"]
)

active_requests = Gauge(
    "netz_ai_active_requests",
    "Number of active requests"
)

model_inference_duration = Histogram(
    "netz_ai_model_inference_seconds",
    "Model inference duration in seconds",
    ["model"]
)

cache_hits = Counter(
    "netz_ai_cache_hits_total",
    "Total number of cache hits"
)

cache_misses = Counter(
    "netz_ai_cache_misses_total",
    "Total number of cache misses"
)

error_count = Counter(
    "netz_ai_errors_total",
    "Total number of errors",
    ["error_type"]
)

# System metrics
system_cpu_usage = Gauge("netz_ai_cpu_usage_percent", "CPU usage percentage")
system_memory_usage = Gauge("netz_ai_memory_usage_percent", "Memory usage percentage")
system_disk_usage = Gauge("netz_ai_disk_usage_percent", "Disk usage percentage")


class HealthChecker:
    """System health checker"""
    
    def __init__(self):
        self.checks: Dict[str, callable] = {}
        self.last_check_results: Dict[str, dict] = {}
        self.check_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check"""
        self.checks[name] = check_func
    
    async def run_checks(self) -> Dict[str, dict]:
        """Run all health checks"""
        results = {}
        
        for name, check_func in self.checks.items():
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                duration = time.time() - start_time
                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "duration_ms": round(duration * 1000, 2),
                    "timestamp": datetime.utcnow().isoformat(),
                    "details": result if isinstance(result, dict) else None
                }
            except Exception as e:
                duration = time.time() - start_time
                results[name] = {
                    "status": "unhealthy",
                    "duration_ms": round(duration * 1000, 2),
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
            
            # Store in history
            self.check_history[name].append(results[name])
        
        self.last_check_results = results
        return results
    
    def get_overall_health(self) -> str:
        """Get overall system health status"""
        if not self.last_check_results:
            return "unknown"
        
        unhealthy_checks = [
            name for name, result in self.last_check_results.items()
            if result["status"] == "unhealthy"
        ]
        
        if not unhealthy_checks:
            return "healthy"
        elif len(unhealthy_checks) < len(self.last_check_results) / 2:
            return "degraded"
        else:
            return "unhealthy"


class MetricsCollector:
    """Collect and aggregate system metrics"""
    
    def __init__(self):
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.custom_metrics: Dict[str, Any] = {}
    
    def collect_system_metrics(self) -> dict:
        """Collect system resource metrics"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_available_mb": memory.available / 1024 / 1024,
            "disk_usage_percent": disk.percent,
            "disk_free_gb": disk.free / 1024 / 1024 / 1024,
            "load_average": psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0, 0, 0],
            "process_count": len(psutil.pids()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update Prometheus gauges
        system_cpu_usage.set(cpu_percent)
        system_memory_usage.set(memory.percent)
        system_disk_usage.set(disk.percent)
        
        # Store in history
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                self.metrics_history[key].append({
                    "value": value,
                    "timestamp": metrics["timestamp"]
                })
        
        return metrics
    
    def add_custom_metric(self, name: str, value: Any):
        """Add a custom metric"""
        self.custom_metrics[name] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_metrics_summary(self) -> dict:
        """Get summary of all metrics"""
        system_metrics = self.collect_system_metrics()
        
        # Calculate averages from history
        averages = {}
        for metric_name, history in self.metrics_history.items():
            if history and metric_name != "timestamp":
                values = [h["value"] for h in history if isinstance(h, dict) and "value" in h]
                if values:
                    averages[f"{metric_name}_avg"] = sum(values) / len(values)
        
        return {
            "current": system_metrics,
            "averages": averages,
            "custom": self.custom_metrics
        }


class RequestLogger:
    """Log and analyze API requests"""
    
    def __init__(self):
        self.request_log: deque = deque(maxlen=10000)
        self.slow_queries: deque = deque(maxlen=100)
        self.error_log: deque = deque(maxlen=1000)
    
    def log_request(self, request: Request, response: Response, duration: float):
        """Log a request"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "request_id": request.headers.get("x-request-id")
        }
        
        self.request_log.append(log_entry)
        
        # Track slow queries
        if duration > 1.0:  # Queries taking more than 1 second
            self.slow_queries.append(log_entry)
        
        # Track errors
        if response.status_code >= 400:
            self.error_log.append(log_entry)
    
    def get_statistics(self) -> dict:
        """Get request statistics"""
        if not self.request_log:
            return {"message": "No requests logged yet"}
        
        recent_requests = list(self.request_log)[-1000:]  # Last 1000 requests
        
        # Calculate statistics
        total_requests = len(recent_requests)
        durations = [r["duration_ms"] for r in recent_requests]
        status_codes = [r["status_code"] for r in recent_requests]
        
        # Group by endpoint
        endpoint_stats = defaultdict(lambda: {"count": 0, "total_duration": 0})
        for req in recent_requests:
            endpoint = req["path"]
            endpoint_stats[endpoint]["count"] += 1
            endpoint_stats[endpoint]["total_duration"] += req["duration_ms"]
        
        # Calculate averages
        for stats in endpoint_stats.values():
            stats["avg_duration_ms"] = stats["total_duration"] / stats["count"]
        
        return {
            "total_requests": total_requests,
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "success_rate": sum(1 for s in status_codes if s < 400) / len(status_codes) * 100,
            "error_count": len(self.error_log),
            "slow_query_count": len(self.slow_queries),
            "endpoints": dict(endpoint_stats)
        }


# Global instances
health_checker = HealthChecker()
metrics_collector = MetricsCollector()
request_logger = RequestLogger()


# Health check functions
async def check_ollama_health() -> dict:
    """Check Ollama service health"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.ollama_host}/api/tags", timeout=5)
            return {
                "available": response.status_code == 200,
                "models": len(response.json().get("models", [])) if response.status_code == 200 else 0
            }
    except Exception:
        return {"available": False, "error": "Cannot connect to Ollama"}


def check_disk_space() -> dict:
    """Check disk space availability"""
    disk = psutil.disk_usage('/')
    return {
        "healthy": disk.percent < 90,
        "usage_percent": disk.percent,
        "free_gb": round(disk.free / 1024 / 1024 / 1024, 2)
    }


def check_memory() -> dict:
    """Check memory usage"""
    memory = psutil.virtual_memory()
    return {
        "healthy": memory.percent < 90,
        "usage_percent": memory.percent,
        "available_mb": round(memory.available / 1024 / 1024, 2)
    }


async def check_redis_health() -> dict:
    """Check Redis connectivity"""
    if not settings.enable_caching:
        return {"available": False, "reason": "Caching disabled"}
    
    try:
        import redis.asyncio as redis
        r = redis.from_url(settings.get_redis_url())
        await r.ping()
        await r.close()
        return {"available": True}
    except Exception:
        return {"available": False, "error": "Cannot connect to Redis"}


# Register default health checks
health_checker.register_check("ollama", check_ollama_health)
health_checker.register_check("disk_space", check_disk_space)
health_checker.register_check("memory", check_memory)
health_checker.register_check("redis", check_redis_health)


@asynccontextmanager
async def track_request_duration(request: Request):
    """Context manager to track request duration"""
    start_time = time.time()
    active_requests.inc()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        active_requests.dec()
        
        # Update metrics
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)


async def monitoring_middleware(request: Request, call_next):
    """Middleware to track all requests"""
    start_time = time.time()
    active_requests.inc()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Update metrics
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        # Log request
        request_logger.log_request(request, response, duration)
        
        # Add timing header
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        error_count.labels(error_type=type(e).__name__).inc()
        raise
        
    finally:
        active_requests.dec()


def setup_monitoring(app: FastAPI):
    """Set up monitoring for the FastAPI app"""
    app.middleware("http")(monitoring_middleware)
    
    @app.get("/metrics", tags=["monitoring"])
    async def prometheus_metrics():
        """Prometheus metrics endpoint"""
        return Response(content=generate_latest(), media_type="text/plain")
    
    @app.get("/health", tags=["monitoring"])
    async def health_check():
        """Health check endpoint"""
        results = await health_checker.run_checks()
        overall_health = health_checker.get_overall_health()
        
        status_code = 200 if overall_health == "healthy" else 503
        
        return JSONResponse(
            content={
                "status": overall_health,
                "timestamp": datetime.utcnow().isoformat(),
                "checks": results
            },
            status_code=status_code
        )
    
    @app.get("/ready", tags=["monitoring"])
    async def readiness_check():
        """Readiness check endpoint"""
        # Simple check - just verify the app is running
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    
    @app.get("/stats", tags=["monitoring"])
    async def system_stats():
        """System statistics endpoint"""
        return {
            "system_metrics": metrics_collector.get_metrics_summary(),
            "request_stats": request_logger.get_statistics(),
            "health": health_checker.get_overall_health(),
            "timestamp": datetime.utcnow().isoformat()
        }


# Logging configuration
def setup_logging():
    """Configure structured logging"""
    log_format = {
        "json": '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s"}',
        "text": '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format=log_format.get(settings.log_format, log_format["text"]),
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set up error logger
    error_handler = logging.FileHandler(settings.error_log_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format.get(settings.log_format)))
    
    logging.getLogger().addHandler(error_handler)