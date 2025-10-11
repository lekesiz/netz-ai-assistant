"""
Production configuration management for NETZ AI
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_log_level: str = "info"
    environment: str = "development"
    debug: bool = False
    
    # Security
    jwt_secret: str
    admin_email: str
    admin_password: str
    allowed_origins: List[str] = []
    cors_allow_credentials: bool = True
    
    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    ollama_timeout: int = 300
    model_preload: List[str] = []
    
    # Database
    database_url: str = "sqlite:///./netz_ai.db"
    database_pool_size: int = 20
    database_max_overflow: int = 40
    database_echo: bool = False
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    
    # Rate Limiting
    rate_limit_per_minute: int = 30
    rate_limit_per_hour: int = 1000
    login_rate_limit_per_minute: int = 5
    api_rate_limit_per_minute: int = 60
    
    # Storage
    rag_storage_path: Path = Path("./rag_storage")
    upload_path: Path = Path("./uploads")
    log_path: Path = Path("./logs")
    max_upload_size_mb: int = 10
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    enable_tracing: bool = False
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831
    
    # Email
    sendgrid_api_key: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: str = "noreply@netzinformatique.fr"
    
    # External Services
    pennylane_api_key: Optional[str] = None
    pennylane_company_id: Optional[str] = None
    serper_api_key: Optional[str] = None
    brave_search_api_key: Optional[str] = None
    google_analytics_id: Optional[str] = None
    sentry_dsn: Optional[str] = None
    
    # Feature Flags
    enable_rag: bool = True
    enable_caching: bool = True
    enable_security: bool = True
    enable_analytics: bool = True
    enable_web_search: bool = True
    enable_learning_mode: bool = True
    enable_admin_api: bool = True
    enable_auto_backup: bool = True
    
    # Performance
    cache_ttl: int = 3600
    cache_max_size: int = 1000
    request_timeout: int = 60
    response_timeout: int = 120
    max_concurrent_requests: int = 100
    
    # Backup
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"
    backup_retention_days: int = 30
    backup_path: Path = Path("/backups/netz_ai")
    s3_backup_bucket: Optional[str] = None
    
    # SSL/TLS
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None
    force_https: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: Path = Path("./logs/api.log")
    log_max_size_mb: int = 100
    log_backup_count: int = 10
    error_log_file: Path = Path("./logs/error.log")
    access_log_file: Path = Path("./logs/access.log")
    
    # Deployment
    container_name: str = "netz-ai-api"
    k8s_namespace: str = "production"
    k8s_replica_count: int = 3
    lb_health_path: str = "/health"
    lb_ready_path: str = "/ready"
    
    # Maintenance
    maintenance_mode: bool = False
    maintenance_message: str = "System under maintenance. Please try again later."
    maintenance_allowed_ips: List[str] = ["127.0.0.1", "10.0.0.0/8"]
    
    @field_validator("allowed_origins", mode="before")
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("model_preload", mode="before")
    def parse_model_preload(cls, v):
        if isinstance(v, str):
            return [model.strip() for model in v.split(",")]
        return v
    
    @field_validator("maintenance_allowed_ips", mode="before")
    def parse_maintenance_ips(cls, v):
        if isinstance(v, str):
            return [ip.strip() for ip in v.split(",")]
        return v
    
    @field_validator("jwt_secret")
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError("JWT secret must be at least 32 characters long")
        return v
    
    def create_directories(self):
        """Create necessary directories"""
        for path_attr in ["rag_storage_path", "upload_path", "log_path", "backup_path"]:
            path = getattr(self, path_attr)
            path.mkdir(parents=True, exist_ok=True)
        
        # Create log file directories
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.error_log_file.parent.mkdir(parents=True, exist_ok=True)
        self.access_log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        protocol = "rediss" if self.redis_ssl else "redis"
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def get_database_config(self) -> dict:
        """Get database configuration for SQLAlchemy"""
        config = {
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "echo": self.database_echo,
        }
        
        if self.database_url.startswith("postgresql"):
            config.update({
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            })
        
        return config
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment.lower() == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Create directories on startup
settings.create_directories()


# Convenience exports
IS_PRODUCTION = settings.is_production()
IS_DEVELOPMENT = settings.is_development()