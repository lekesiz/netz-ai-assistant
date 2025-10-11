"""
Security Middleware and Utilities for NETZ AI
Implements authentication, rate limiting, input validation, and security headers
"""

import time
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple, Any
from functools import wraps
import re
import ipaddress
from collections import defaultdict
import logging
import json
from pathlib import Path

from fastapi import HTTPException, Request, Response, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
import bleach
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

# Security configuration
SECURITY_CONFIG = {
    "jwt_secret": None,  # Will be loaded from environment
    "jwt_algorithm": "HS256",
    "jwt_expiration_hours": 24,
    "api_key_header": "X-API-Key",
    "rate_limit_per_minute": 60,
    "rate_limit_per_hour": 1000,
    "max_request_size": 10 * 1024 * 1024,  # 10MB
    "allowed_origins": ["http://localhost:3000", "http://localhost:3001"],
    "blocked_ips": set(),
    "suspicious_patterns": [
        r"<script",
        r"javascript:",
        r"onclick",
        r"onerror",
        r"eval\(",
        r"expression\(",
        r"vbscript:",
        r"onload",
        r"alert\(",
        r"document\.",
        r"window\.",
        r"\.\.\/",  # Path traversal
        r"union.*select",  # SQL injection
        r"drop.*table",
        r"insert.*into",
        r"select.*from",
        r"--",  # SQL comment
        r"\/\*.*\*\/",  # SQL block comment
        r"\x00",  # Null byte
        r"%00",  # URL encoded null
    ]
}


class SecurityManager:
    """Central security management class"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = SECURITY_CONFIG["blocked_ips"].copy()
        self.api_keys = self._load_api_keys()
        self.jwt_secret = self._load_jwt_secret()
        
    def _load_api_keys(self) -> Dict[str, Dict]:
        """Load API keys from secure storage"""
        api_keys_file = Path("api_keys.json")
        if api_keys_file.exists():
            try:
                with open(api_keys_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load API keys: {e}")
        
        # Default API keys (should be replaced in production)
        return {
            "demo-key-123": {
                "name": "Demo User",
                "permissions": ["read"],
                "rate_limit_multiplier": 1
            }
        }
    
    def _load_jwt_secret(self) -> str:
        """Load JWT secret from environment or generate"""
        import os
        secret = os.environ.get("JWT_SECRET")
        if not secret:
            secret = secrets.token_hex(32)
            logger.warning("JWT_SECRET not found in environment, using generated secret")
        return secret
    
    def generate_api_key(self, name: str, permissions: List[str] = None) -> str:
        """Generate a new API key"""
        api_key = f"netz-{secrets.token_hex(16)}"
        self.api_keys[api_key] = {
            "name": name,
            "permissions": permissions or ["read"],
            "created_at": datetime.utcnow().isoformat(),
            "rate_limit_multiplier": 1
        }
        self._save_api_keys()
        return api_key
    
    def _save_api_keys(self):
        """Save API keys to secure storage"""
        try:
            with open("api_keys.json", "w") as f:
                json.dump(self.api_keys, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate API key and return metadata"""
        return self.api_keys.get(api_key)
    
    def generate_jwt_token(self, user_id: str, permissions: List[str] = None) -> str:
        """Generate JWT token for user"""
        payload = {
            "user_id": user_id,
            "permissions": permissions or ["read"],
            "exp": datetime.utcnow() + timedelta(hours=SECURITY_CONFIG["jwt_expiration_hours"]),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=SECURITY_CONFIG["jwt_algorithm"])
    
    def validate_jwt_token(self, token: str) -> Optional[Dict]:
        """Validate JWT token and return payload"""
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[SECURITY_CONFIG["jwt_algorithm"]]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Expired JWT token")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    def track_failed_attempt(self, ip: str):
        """Track failed authentication attempts"""
        self.failed_attempts[ip].append(time.time())
        
        # Clean old attempts
        cutoff = time.time() - 3600  # 1 hour
        self.failed_attempts[ip] = [t for t in self.failed_attempts[ip] if t > cutoff]
        
        # Block if too many attempts
        if len(self.failed_attempts[ip]) > 5:
            self.block_ip(ip)
    
    def block_ip(self, ip: str):
        """Block an IP address"""
        self.blocked_ips.add(ip)
        logger.warning(f"Blocked IP: {ip}")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
    
    def validate_input(self, text: str) -> Tuple[bool, Optional[str]]:
        """Validate input for security threats"""
        # Check for suspicious patterns
        for pattern in SECURITY_CONFIG["suspicious_patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Suspicious pattern detected: {pattern}"
        
        # Additional checks
        if len(text) > 100000:  # 100KB text limit
            return False, "Input too large"
        
        return True, None


# Global security manager instance
security_manager = SecurityManager()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


class SecureRequest(BaseModel):
    """Base model for secure requests with validation"""
    
    @validator('*', pre=True)
    def validate_input(cls, v):
        if isinstance(v, str):
            # Basic input sanitization
            v = bleach.clean(v, strip=True)
            
            # Check for security threats
            is_valid, error = security_manager.validate_input(v)
            if not is_valid:
                raise ValueError(f"Security validation failed: {error}")
        
        return v


# Authentication dependencies
security_scheme = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> Dict:
    """Verify JWT token"""
    token = credentials.credentials
    payload = security_manager.validate_jwt_token(token)
    
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    
    return payload


async def verify_api_key(request: Request) -> Dict:
    """Verify API key from headers"""
    api_key = request.headers.get(SECURITY_CONFIG["api_key_header"])
    
    if not api_key:
        raise HTTPException(status_code=403, detail="API key required")
    
    key_data = security_manager.validate_api_key(api_key)
    if not key_data:
        # Track failed attempt
        client_ip = get_remote_address(request)
        security_manager.track_failed_attempt(client_ip)
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return key_data


async def verify_api_key_optional(request: Request) -> Optional[Dict]:
    """Optionally verify API key (for public endpoints with higher limits for authenticated users)"""
    api_key = request.headers.get(SECURITY_CONFIG["api_key_header"])
    
    if api_key:
        return security_manager.validate_api_key(api_key)
    
    return None


# Security middleware functions
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response


async def ip_blocking_middleware(request: Request, call_next):
    """Block requests from blocked IPs"""
    client_ip = get_remote_address(request)
    
    if security_manager.is_ip_blocked(client_ip):
        raise HTTPException(status_code=403, detail="Access denied")
    
    response = await call_next(request)
    return response


async def request_size_limit_middleware(request: Request, call_next):
    """Limit request body size"""
    content_length = request.headers.get("content-length")
    
    if content_length and int(content_length) > SECURITY_CONFIG["max_request_size"]:
        raise HTTPException(status_code=413, detail="Request too large")
    
    response = await call_next(request)
    return response


# Input validation utilities
def sanitize_html(html: str) -> str:
    """Sanitize HTML input"""
    return bleach.clean(
        html,
        tags=["p", "br", "strong", "em", "u", "a"],
        attributes={"a": ["href", "title"]},
        strip=True
    )


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
    return bool(re.match(pattern, url))


def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"{salt}:{password_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hash_hex = password_hash.split(":")
        password_check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        return password_check.hex() == hash_hex
    except Exception:
        return False


# CORS configuration helper
def get_cors_config() -> Dict:
    """Get CORS configuration"""
    return {
        "allow_origins": SECURITY_CONFIG["allowed_origins"],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
        "expose_headers": ["X-Total-Count", "X-Page-Count"]
    }


# SQL injection prevention
def sanitize_sql_param(param: str) -> str:
    """Sanitize parameter for SQL queries"""
    # Remove dangerous characters
    sanitized = re.sub(r"[;'\"\\\x00\n\r\x1a]", "", param)
    # Limit length
    return sanitized[:100]


# File upload security
def validate_file_upload(filename: str, content_type: str, max_size: int = 10 * 1024 * 1024) -> Tuple[bool, Optional[str]]:
    """Validate file upload"""
    # Allowed extensions
    allowed_extensions = {".txt", ".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg"}
    allowed_content_types = {
        "text/plain", "application/pdf", "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/png", "image/jpeg"
    }
    
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        return False, f"File extension not allowed: {ext}"
    
    # Check content type
    if content_type not in allowed_content_types:
        return False, f"Content type not allowed: {content_type}"
    
    # Sanitize filename
    if re.search(r"[/\\]", filename):
        return False, "Invalid filename"
    
    return True, None


# Example usage in API endpoints
def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from request context
            request = kwargs.get("request")
            if not request:
                raise HTTPException(status_code=500, detail="Request context not found")
            
            # Check API key or JWT
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # JWT auth
                token = auth_header.split(" ")[1]
                payload = security_manager.validate_jwt_token(token)
                if not payload or permission not in payload.get("permissions", []):
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
            else:
                # API key auth
                api_key = request.headers.get(SECURITY_CONFIG["api_key_header"])
                if not api_key:
                    raise HTTPException(status_code=403, detail="Authentication required")
                
                key_data = security_manager.validate_api_key(api_key)
                if not key_data or permission not in key_data.get("permissions", []):
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Audit logging
class AuditLogger:
    """Security audit logging"""
    
    def __init__(self, log_file: str = "security_audit.log"):
        self.log_file = log_file
    
    def log_event(self, event_type: str, user: str, details: Dict):
        """Log security event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user": user,
            "details": details
        }
        
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")


# Global audit logger
audit_logger = AuditLogger()


if __name__ == "__main__":
    # Test security functions
    print("Testing security module...")
    
    # Generate API key
    api_key = security_manager.generate_api_key("test_user", ["read", "write"])
    print(f"Generated API key: {api_key}")
    
    # Generate JWT
    jwt_token = security_manager.generate_jwt_token("user123", ["read"])
    print(f"Generated JWT: {jwt_token}")
    
    # Validate JWT
    payload = security_manager.validate_jwt_token(jwt_token)
    print(f"JWT payload: {payload}")
    
    # Test password hashing
    password_hash = hash_password("test_password")
    print(f"Password hash: {password_hash}")
    print(f"Password valid: {verify_password('test_password', password_hash)}")
    
    # Test input validation
    is_valid, error = security_manager.validate_input("<script>alert('xss')</script>")
    print(f"XSS test - Valid: {is_valid}, Error: {error}")
    
    print("\nSecurity module test complete!")