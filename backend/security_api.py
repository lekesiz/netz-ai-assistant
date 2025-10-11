"""
Security API endpoints for NETZ AI
Handles authentication, API key management, and security monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from pydantic import BaseModel, validator
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json

from security_middleware import (
    security_manager, verify_token, verify_api_key,
    hash_password, verify_password, validate_email,
    audit_logger, SecureRequest, limiter
)

router = APIRouter(prefix="/api/security", tags=["security"])


class LoginRequest(SecureRequest):
    """Login request model"""
    email: str
    password: str
    
    @validator('email')
    def validate_email_format(cls, v):
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class ApiKeyCreateRequest(SecureRequest):
    """API key creation request"""
    name: str
    permissions: List[str] = ["read"]
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Name must be between 3 and 50 characters')
        return v
    
    @validator('permissions')
    def validate_permissions(cls, v):
        allowed = {"read", "write", "admin"}
        for perm in v:
            if perm not in allowed:
                raise ValueError(f'Invalid permission: {perm}')
        return v


class ChangePasswordRequest(SecureRequest):
    """Change password request"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password_strength(cls, v, values):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current')
        return v


# Admin credentials (should be in secure storage in production)
ADMIN_USERS = {
    "admin@netzinformatique.fr": {
        "password_hash": hash_password("changeme123"),  # Change in production!
        "permissions": ["read", "write", "admin"],
        "name": "Admin User"
    }
}


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: LoginRequest, req: Request):
    """Admin login endpoint"""
    user_data = ADMIN_USERS.get(request.email)
    
    if not user_data or not verify_password(request.password, user_data["password_hash"]):
        # Log failed attempt
        client_ip = req.client.host if req.client else "unknown"
        security_manager.track_failed_attempt(client_ip)
        audit_logger.log_event("failed_login", request.email, {"ip": client_ip})
        
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    token = security_manager.generate_jwt_token(request.email, user_data["permissions"])
    
    # Log successful login
    audit_logger.log_event("successful_login", request.email, {})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 86400,  # 24 hours
        "user": {
            "email": request.email,
            "name": user_data["name"],
            "permissions": user_data["permissions"]
        }
    }


@router.post("/api-keys")
async def create_api_key(
    request: ApiKeyCreateRequest,
    current_user: Dict = Depends(verify_token)
):
    """Create a new API key (requires admin permission)"""
    if "admin" not in current_user.get("permissions", []):
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    # Generate new API key
    api_key = security_manager.generate_api_key(request.name, request.permissions)
    
    # Log API key creation
    audit_logger.log_event("api_key_created", current_user["user_id"], {
        "key_name": request.name,
        "permissions": request.permissions
    })
    
    return {
        "api_key": api_key,
        "name": request.name,
        "permissions": request.permissions,
        "created_at": datetime.utcnow().isoformat()
    }


@router.get("/api-keys")
async def list_api_keys(current_user: Dict = Depends(verify_token)):
    """List all API keys (requires admin permission)"""
    if "admin" not in current_user.get("permissions", []):
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    # Return sanitized API key list (without actual keys)
    keys = []
    for key, data in security_manager.api_keys.items():
        keys.append({
            "key_prefix": f"{key[:8]}...",  # Show only prefix
            "name": data["name"],
            "permissions": data["permissions"],
            "created_at": data.get("created_at", "unknown"),
            "last_used": data.get("last_used", "never")
        })
    
    return {"api_keys": keys}


@router.delete("/api-keys/{key_prefix}")
async def revoke_api_key(
    key_prefix: str,
    current_user: Dict = Depends(verify_token)
):
    """Revoke an API key (requires admin permission)"""
    if "admin" not in current_user.get("permissions", []):
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    # Find and remove key by prefix
    key_to_remove = None
    for key in security_manager.api_keys:
        if key.startswith(key_prefix):
            key_to_remove = key
            break
    
    if not key_to_remove:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key_data = security_manager.api_keys.pop(key_to_remove)
    security_manager._save_api_keys()
    
    # Log revocation
    audit_logger.log_event("api_key_revoked", current_user["user_id"], {
        "key_name": key_data["name"]
    })
    
    return {"message": "API key revoked successfully"}


@router.post("/change-password")
@limiter.limit("3/hour")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict = Depends(verify_token)
):
    """Change user password"""
    email = current_user["user_id"]
    user_data = ADMIN_USERS.get(email)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not verify_password(request.current_password, user_data["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password incorrect")
    
    # Update password
    user_data["password_hash"] = hash_password(request.new_password)
    
    # In production, save to secure storage
    # For now, just update in memory
    
    # Log password change
    audit_logger.log_event("password_changed", email, {})
    
    return {"message": "Password changed successfully"}


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    event_type: Optional[str] = None,
    current_user: Dict = Depends(verify_token)
):
    """Get security audit logs (requires admin permission)"""
    if "admin" not in current_user.get("permissions", []):
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    logs = []
    try:
        with open(audit_logger.log_file, "r") as f:
            for line in f:
                try:
                    log = json.loads(line.strip())
                    if not event_type or log.get("event_type") == event_type:
                        logs.append(log)
                except:
                    continue
    except FileNotFoundError:
        pass
    
    # Return most recent logs
    logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
    
    return {"logs": logs}


@router.get("/blocked-ips")
async def get_blocked_ips(current_user: Dict = Depends(verify_token)):
    """Get list of blocked IPs (requires admin permission)"""
    if "admin" not in current_user.get("permissions", []):
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    return {"blocked_ips": list(security_manager.blocked_ips)}


@router.post("/blocked-ips/{ip}/unblock")
async def unblock_ip(
    ip: str,
    current_user: Dict = Depends(verify_token)
):
    """Unblock an IP address (requires admin permission)"""
    if "admin" not in current_user.get("permissions", []):
        raise HTTPException(status_code=403, detail="Admin permission required")
    
    if ip in security_manager.blocked_ips:
        security_manager.blocked_ips.remove(ip)
        
        # Log unblock
        audit_logger.log_event("ip_unblocked", current_user["user_id"], {"ip": ip})
        
        return {"message": f"IP {ip} unblocked successfully"}
    else:
        raise HTTPException(status_code=404, detail="IP not found in blocked list")


@router.get("/security-stats")
async def get_security_stats(current_user: Dict = Depends(verify_token)):
    """Get security statistics"""
    # Count recent events
    event_counts = {}
    recent_events = []
    
    try:
        with open(audit_logger.log_file, "r") as f:
            cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
            for line in f:
                try:
                    log = json.loads(line.strip())
                    if log.get("timestamp", "") > cutoff:
                        recent_events.append(log)
                        event_type = log.get("event_type", "unknown")
                        event_counts[event_type] = event_counts.get(event_type, 0) + 1
                except:
                    continue
    except FileNotFoundError:
        pass
    
    return {
        "stats": {
            "blocked_ips": len(security_manager.blocked_ips),
            "api_keys_active": len(security_manager.api_keys),
            "events_24h": len(recent_events),
            "event_breakdown": event_counts,
            "failed_attempts": sum(len(attempts) for attempts in security_manager.failed_attempts.values())
        }
    }


@router.post("/test-security")
@limiter.limit("1/minute")
async def test_security(request: Request):
    """Test endpoint to verify security is working"""
    client_ip = request.client.host if request.client else "unknown"
    
    return {
        "message": "Security test successful",
        "client_ip": client_ip,
        "rate_limit": "1/minute",
        "security_headers": "enabled",
        "authentication": "available"
    }


# Include router in main app
def include_security_routes(app):
    """Include security routes in main app"""
    app.include_router(router)