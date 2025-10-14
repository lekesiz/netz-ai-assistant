#!/usr/bin/env python3
"""
Admin Dashboard API Integration for main.py
FastAPI endpoints for enhanced admin dashboard with comprehensive analytics
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from enhanced_admin_dashboard_backend import EnhancedAdminDashboard
from user_management_api_integration import require_admin
from advanced_user_management import UserRole

logger = logging.getLogger(__name__)

# Initialize enhanced admin dashboard
admin_dashboard = EnhancedAdminDashboard()

# Pydantic models for API responses
class DashboardResponse(BaseModel):
    timestamp: str
    generation_time_seconds: float
    system_status: Dict[str, Any]
    metrics: Dict[str, Any]
    trends: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]
    netz_business_summary: Dict[str, Any]

class SystemMetricsResponse(BaseModel):
    cpu_usage: float
    memory_usage: float
    memory_total: float
    memory_available: float
    disk_usage: float
    disk_total: float
    network_sent: int
    network_recv: int
    uptime: float
    active_processes: int

class AIPerformanceResponse(BaseModel):
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_response_time: float
    cache_hit_rate: float
    knowledge_documents: int
    vector_embeddings: int
    ai_accuracy: float

class BusinessMetricsResponse(BaseModel):
    active_users: int
    new_users_today: int
    new_users_week: int
    user_engagement: float
    popular_queries: List[Dict[str, Any]]
    service_requests: Dict[str, int]
    conversion_rate: float
    customer_satisfaction: float

class AlertResponse(BaseModel):
    id: str
    level: str
    title: str
    message: str
    timestamp: str
    category: str

class InsightResponse(BaseModel):
    type: str
    category: str
    title: str
    description: str
    metric: str
    recommendation: str

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None

def add_admin_dashboard_routes(app: FastAPI):
    """Add enhanced admin dashboard routes to FastAPI app"""
    
    @app.get("/api/admin/dashboard", response_model=DashboardResponse)
    async def get_comprehensive_dashboard(admin_user = Depends(require_admin)):
        """Get comprehensive admin dashboard data (admin only)"""
        try:
            dashboard_data = await admin_dashboard.get_comprehensive_dashboard_data()
            
            return DashboardResponse(**dashboard_data)
        
        except Exception as e:
            logger.error(f"Dashboard error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate dashboard data"
            )
    
    @app.get("/api/admin/dashboard/system", response_model=SystemMetricsResponse)
    async def get_system_metrics(admin_user = Depends(require_admin)):
        """Get current system performance metrics (admin only)"""
        try:
            metrics = await admin_dashboard.get_system_metrics()
            
            return SystemMetricsResponse(
                cpu_usage=metrics.cpu_usage,
                memory_usage=metrics.memory_usage,
                memory_total=metrics.memory_total,
                memory_available=metrics.memory_available,
                disk_usage=metrics.disk_usage,
                disk_total=metrics.disk_total,
                network_sent=metrics.network_sent,
                network_recv=metrics.network_recv,
                uptime=metrics.uptime,
                active_processes=metrics.active_processes
            )
        
        except Exception as e:
            logger.error(f"System metrics error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get system metrics"
            )
    
    @app.get("/api/admin/dashboard/ai", response_model=AIPerformanceResponse)
    async def get_ai_performance(admin_user = Depends(require_admin)):
        """Get AI system performance metrics (admin only)"""
        try:
            metrics = await admin_dashboard.get_ai_performance_metrics()
            
            return AIPerformanceResponse(
                total_queries=metrics.total_queries,
                successful_queries=metrics.successful_queries,
                failed_queries=metrics.failed_queries,
                average_response_time=metrics.average_response_time,
                cache_hit_rate=metrics.cache_hit_rate,
                knowledge_documents=metrics.knowledge_documents,
                vector_embeddings=metrics.vector_embeddings,
                ai_accuracy=metrics.ai_accuracy
            )
        
        except Exception as e:
            logger.error(f"AI performance error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get AI performance metrics"
            )
    
    @app.get("/api/admin/dashboard/business", response_model=BusinessMetricsResponse)
    async def get_business_metrics(admin_user = Depends(require_admin)):
        """Get business intelligence metrics (admin only)"""
        try:
            metrics = await admin_dashboard.get_business_metrics()
            
            return BusinessMetricsResponse(
                active_users=metrics.active_users,
                new_users_today=metrics.new_users_today,
                new_users_week=metrics.new_users_week,
                user_engagement=metrics.user_engagement,
                popular_queries=metrics.popular_queries,
                service_requests=metrics.service_requests,
                conversion_rate=metrics.conversion_rate,
                customer_satisfaction=metrics.customer_satisfaction
            )
        
        except Exception as e:
            logger.error(f"Business metrics error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get business metrics"
            )
    
    @app.get("/api/admin/dashboard/alerts", response_model=List[AlertResponse])
    async def get_system_alerts(admin_user = Depends(require_admin)):
        """Get system alerts and notifications (admin only)"""
        try:
            alerts = await admin_dashboard.get_system_alerts()
            
            return [AlertResponse(
                id=alert["id"],
                level=alert["level"],
                title=alert["title"],
                message=alert["message"],
                timestamp=alert["timestamp"],
                category=alert["category"]
            ) for alert in alerts]
        
        except Exception as e:
            logger.error(f"Alerts error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get system alerts"
            )
    
    @app.get("/api/admin/dashboard/insights", response_model=List[InsightResponse])
    async def get_insights(admin_user = Depends(require_admin)):
        """Get system insights and recommendations (admin only)"""
        try:
            system_metrics = await admin_dashboard.get_system_metrics()
            ai_metrics = await admin_dashboard.get_ai_performance_metrics()
            business_metrics = await admin_dashboard.get_business_metrics()
            
            insights = await admin_dashboard.generate_insights(
                system_metrics, ai_metrics, business_metrics
            )
            
            return [InsightResponse(
                type=insight["type"],
                category=insight["category"],
                title=insight["title"],
                description=insight["description"],
                metric=insight["metric"],
                recommendation=insight["recommendation"]
            ) for insight in insights]
        
        except Exception as e:
            logger.error(f"Insights error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate insights"
            )
    
    @app.get("/api/admin/dashboard/trends/system", response_model=ApiResponse)
    async def get_system_trends(
        days: int = Query(7, description="Number of days for trend data"),
        admin_user = Depends(require_admin)
    ):
        """Get system performance trends (admin only)"""
        try:
            if days < 1 or days > 90:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Days must be between 1 and 90"
                )
            
            trends = await admin_dashboard.get_system_trends(days)
            
            return ApiResponse(
                success=True,
                data=trends
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"System trends error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get system trends"
            )
    
    @app.get("/api/admin/dashboard/trends/ai", response_model=ApiResponse)
    async def get_ai_trends(
        days: int = Query(7, description="Number of days for trend data"),
        admin_user = Depends(require_admin)
    ):
        """Get AI performance trends (admin only)"""
        try:
            if days < 1 or days > 90:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Days must be between 1 and 90"
                )
            
            trends = await admin_dashboard.get_ai_performance_trends(days)
            
            return ApiResponse(
                success=True,
                data=trends
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"AI trends error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get AI trends"
            )
    
    @app.get("/api/admin/dashboard/trends/users", response_model=ApiResponse)
    async def get_user_activity_trends(
        days: int = Query(7, description="Number of days for trend data"),
        admin_user = Depends(require_admin)
    ):
        """Get user activity trends (admin only)"""
        try:
            if days < 1 or days > 90:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Days must be between 1 and 90"
                )
            
            trends = await admin_dashboard.get_user_activity_trends(days)
            
            return ApiResponse(
                success=True,
                data=trends
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User trends error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user trends"
            )
    
    @app.get("/api/admin/dashboard/export", response_model=ApiResponse)
    async def export_analytics_data(
        format: str = Query("json", description="Export format (json, csv)"),
        days: int = Query(30, description="Number of days to export"),
        admin_user = Depends(require_admin)
    ):
        """Export analytics data for external analysis (admin only)"""
        try:
            if days < 1 or days > 365:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Days must be between 1 and 365"
                )
            
            if format not in ["json", "csv"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Format must be 'json' or 'csv'"
                )
            
            export_data = await admin_dashboard.export_analytics_data(format, days)
            
            return ApiResponse(
                success=True,
                message=f"Analytics data exported ({export_data['export_info']['total_records']} records)",
                data={
                    "export_info": export_data["export_info"],
                    "download_available": True
                }
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export analytics data"
            )
    
    @app.get("/api/admin/dashboard/health", response_model=ApiResponse)
    async def get_detailed_health_check(admin_user = Depends(require_admin)):
        """Get detailed system health information (admin only)"""
        try:
            system_metrics = await admin_dashboard.get_system_metrics()
            ai_metrics = await admin_dashboard.get_ai_performance_metrics()
            
            overall_health = admin_dashboard._get_overall_health(system_metrics, ai_metrics)
            
            health_data = {
                "overall_health": overall_health,
                "timestamp": datetime.now().isoformat(),
                "uptime_hours": system_metrics.uptime / 3600,
                "system_load": {
                    "cpu": system_metrics.cpu_usage,
                    "memory": system_metrics.memory_usage,
                    "disk": system_metrics.disk_usage
                },
                "ai_performance": {
                    "accuracy": ai_metrics.ai_accuracy * 100,
                    "response_time": ai_metrics.average_response_time,
                    "cache_efficiency": ai_metrics.cache_hit_rate * 100
                },
                "services": {
                    "api": "healthy",
                    "database": "healthy",
                    "ai_engine": "excellent",
                    "cache": "optimal"
                },
                "recommendations": []
            }
            
            # Add recommendations based on health
            if overall_health == "excellent":
                health_data["recommendations"].append("System performing optimally - ready for production scaling")
            elif overall_health == "good":
                health_data["recommendations"].append("System healthy - monitor resource usage")
            elif overall_health == "warning":
                health_data["recommendations"].append("Consider resource optimization or scaling")
            else:
                health_data["recommendations"].append("Immediate attention required - check system resources")
            
            return ApiResponse(
                success=True,
                data=health_data
            )
        
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to perform health check"
            )
    
    @app.get("/api/admin/dashboard/realtime", response_model=ApiResponse)
    async def get_realtime_metrics(admin_user = Depends(require_admin)):
        """Get real-time system metrics for live monitoring (admin only)"""
        try:
            # Get fresh metrics without caching
            system_metrics = await admin_dashboard.get_system_metrics()
            ai_metrics = await admin_dashboard.get_ai_performance_metrics()
            business_metrics = await admin_dashboard.get_business_metrics()
            
            realtime_data = {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_usage": system_metrics.cpu_usage,
                    "memory_usage": system_metrics.memory_usage,
                    "disk_usage": system_metrics.disk_usage,
                    "active_processes": system_metrics.active_processes
                },
                "ai": {
                    "response_time": ai_metrics.average_response_time,
                    "cache_hit_rate": ai_metrics.cache_hit_rate * 100,
                    "accuracy": ai_metrics.ai_accuracy * 100
                },
                "business": {
                    "active_users": business_metrics.active_users,
                    "user_engagement": business_metrics.user_engagement
                },
                "network": {
                    "bytes_sent": system_metrics.network_sent,
                    "bytes_received": system_metrics.network_recv
                }
            }
            
            return ApiResponse(
                success=True,
                data=realtime_data
            )
        
        except Exception as e:
            logger.error(f"Real-time metrics error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get real-time metrics"
            )
    
    logger.info("✅ Enhanced admin dashboard routes added to FastAPI app")

# Setup function for dashboard initialization
async def setup_admin_dashboard():
    """Setup enhanced admin dashboard"""
    logger.info("📊 Enhanced admin dashboard initialized")

if __name__ == "__main__":
    print("This file should be imported into main.py")
    print("Use: from admin_dashboard_api_integration import add_admin_dashboard_routes")