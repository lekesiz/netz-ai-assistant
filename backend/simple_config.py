"""
Simplified configuration for NETZ AI
"""

import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Settings:
    """Application settings"""
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"
    
    # Security - with defaults
    jwt_secret: str = os.getenv("JWT_SECRET", "development-secret-key-change-in-production")
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@netzinformatique.fr")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "changeme123")
    
    # PennyLane
    pennylane_api_key: Optional[str] = os.getenv("PENNYLANE_API_KEY")
    pennylane_company_id: Optional[str] = os.getenv("PENNYLANE_COMPANY_ID")
    
    # Ollama
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Storage
    rag_storage_path: Path = Path("./rag_storage")
    upload_path: Path = Path("./uploads")
    log_path: Path = Path("./logs")
    
    # Feature flags
    enable_rag: bool = True
    enable_caching: bool = True
    enable_security: bool = True
    
    def __post_init__(self):
        """Create directories after initialization"""
        for path in [self.rag_storage_path, self.upload_path, self.log_path]:
            path.mkdir(parents=True, exist_ok=True)

# Create settings instance
settings = Settings()