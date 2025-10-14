#!/usr/bin/env python3
"""
User Management API Integration for main.py
FastAPI endpoints for user authentication and management
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from advanced_user_management import AdvancedUserManagement, UserRole, UserStatus

logger = logging.getLogger(__name__)

# Initialize user management system
user_mgmt = AdvancedUserManagement()
security = HTTPBearer()

# Pydantic models for API requests/responses
class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class UserStatusUpdateRequest(BaseModel):
    status: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    status: str
    created_at: str
    last_login: Optional[str] = None

class AuthResponse(BaseModel):
    success: bool
    user_id: str
    session_id: str
    jwt_token: str
    user_info: Dict[str, Any]

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None

# Dependency to get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    user_id = user_mgmt.verify_jwt_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = user_mgmt.users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status.value}"
        )
    
    return user

# Dependency to require admin privileges
async def require_admin(current_user = Depends(get_current_user)):
    """Require admin privileges"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def add_user_management_routes(app: FastAPI):
    """Add user management routes to FastAPI app"""
    
    @app.post("/api/auth/register", response_model=ApiResponse)
    async def register_user(request: UserCreateRequest, http_request: Request):
        """Register new user account"""
        try:
            # Validate role
            try:
                role = UserRole(request.role)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role"
                )
            
            result = await user_mgmt.create_user(
                username=request.username,
                email=request.email,
                password=request.password,
                role=role
            )
            
            if result["success"]:
                return ApiResponse(
                    success=True,
                    message="User registered successfully",
                    data={"user_id": result["user_id"]}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    @app.post("/api/auth/login", response_model=AuthResponse)
    async def login_user(request: UserLoginRequest, http_request: Request):
        """Authenticate user and create session"""
        try:
            client_ip = http_request.client.host
            user_agent = http_request.headers.get("user-agent", "")
            
            result = await user_mgmt.authenticate_user(
                username=request.username,
                password=request.password,
                ip_address=client_ip,
                user_agent=user_agent
            )
            
            if result["success"]:
                return AuthResponse(**result)
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=result["error"]
                )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
    
    @app.post("/api/auth/logout", response_model=ApiResponse)
    async def logout_user(current_user = Depends(get_current_user)):
        """Logout user and invalidate session"""
        try:
            # Find user's active session
            user_sessions = [s for s in user_mgmt.sessions.values() 
                           if s.user_id == current_user.id and s.is_active]
            
            if user_sessions:
                session_id = user_sessions[0].session_id
                result = await user_mgmt.logout_user(session_id)
                
                return ApiResponse(
                    success=True,
                    message="Logged out successfully"
                )
            else:
                return ApiResponse(
                    success=True,
                    message="No active session found"
                )
        
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )
    
    @app.get("/api/auth/me", response_model=UserResponse)
    async def get_current_user_info(current_user = Depends(get_current_user)):
        """Get current user information"""
        return UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            role=current_user.role.value,
            status=current_user.status.value,
            created_at=current_user.created_at.isoformat(),
            last_login=current_user.last_login.isoformat() if current_user.last_login else None
        )
    
    @app.put("/api/auth/profile", response_model=ApiResponse)
    async def update_user_profile(request: UserUpdateRequest, current_user = Depends(get_current_user)):
        """Update user profile"""
        try:
            updates = {}
            if request.email is not None:
                updates["email"] = request.email
            if request.preferences is not None:
                updates["preferences"] = request.preferences
            if request.metadata is not None:
                updates["metadata"] = request.metadata
            
            result = await user_mgmt.update_user_profile(current_user.id, updates)
            
            if result["success"]:
                return ApiResponse(
                    success=True,
                    message="Profile updated successfully",
                    data={"updated_fields": result["updated_fields"]}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Profile update failed"
            )
    
    @app.put("/api/auth/password", response_model=ApiResponse)
    async def change_password(request: PasswordChangeRequest, current_user = Depends(get_current_user)):
        """Change user password"""
        try:
            result = await user_mgmt.change_user_password(
                user_id=current_user.id,
                current_password=request.current_password,
                new_password=request.new_password
            )
            
            if result["success"]:
                return ApiResponse(
                    success=True,
                    message="Password changed successfully"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed"
            )
    
    @app.get("/api/auth/analytics", response_model=ApiResponse)
    async def get_user_analytics(current_user = Depends(get_current_user)):
        """Get user analytics"""
        try:
            result = await user_mgmt.get_user_analytics(current_user.id)
            
            if result["success"]:
                return ApiResponse(
                    success=True,
                    data=result["analytics"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["error"]
                )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analytics retrieval failed"
            )
    
    # Admin endpoints
    @app.get("/api/admin/users", response_model=ApiResponse)
    async def list_users(
        role: Optional[str] = None,
        status: Optional[str] = None,
        admin_user = Depends(require_admin)
    ):
        """List all users (admin only)"""
        try:
            filter_role = UserRole(role) if role else None
            filter_status = UserStatus(status) if status else None
            
            result = await user_mgmt.list_users(filter_role, filter_status)
            
            return ApiResponse(
                success=True,
                data={
                    "total_users": result["total_users"],
                    "users": result["users"]
                }
            )
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role or status filter"
            )
        except Exception as e:
            logger.error(f"List users error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list users"
            )
    
    @app.put("/api/admin/users/{user_id}/status", response_model=ApiResponse)
    async def update_user_status(
        user_id: str,
        request: UserStatusUpdateRequest,
        admin_user = Depends(require_admin)
    ):
        """Update user status (admin only)"""
        try:
            try:
                new_status = UserStatus(request.status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid status"
                )
            
            result = await user_mgmt.update_user_status(
                user_id=user_id,
                new_status=new_status,
                admin_user_id=admin_user.id
            )
            
            if result["success"]:
                return ApiResponse(
                    success=True,
                    message=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"]
                )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Status update error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Status update failed"
            )
    
    @app.get("/api/admin/analytics/{user_id}", response_model=ApiResponse)
    async def get_user_analytics_admin(user_id: str, admin_user = Depends(require_admin)):
        """Get analytics for any user (admin only)"""
        try:
            result = await user_mgmt.get_user_analytics(user_id)
            
            if result["success"]:
                return ApiResponse(
                    success=True,
                    data=result["analytics"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["error"]
                )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Admin analytics error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analytics retrieval failed"
            )
    
    @app.get("/api/admin/stats", response_model=ApiResponse)
    async def get_system_stats(admin_user = Depends(require_admin)):
        """Get system statistics (admin only)"""
        try:
            stats = await user_mgmt.get_system_stats()
            
            return ApiResponse(
                success=True,
                data=stats
            )
        
        except Exception as e:
            logger.error(f"System stats error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get system stats"
            )
    
    logger.info("✅ User management routes added to FastAPI app")

# Example usage function
async def setup_user_management():
    """Setup user management system"""
    # Create admin user if needed
    await user_mgmt.create_admin_user()
    logger.info("🔐 User management system initialized")

if __name__ == "__main__":
    # This file is meant to be imported, not run directly
    print("This file should be imported into main.py")
    print("Use: from user_management_api_integration import add_user_management_routes")