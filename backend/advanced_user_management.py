#!/usr/bin/env python3
"""
Advanced User Management System for NETZ AI
Comprehensive user authentication, authorization, and management features
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import secrets
import jwt
from dataclasses import dataclass
from enum import Enum
import bcrypt
from pathlib import Path

from lightweight_rag import LightweightRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User role definitions"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"

class UserStatus(Enum):
    """User status definitions"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

@dataclass
class User:
    """User data structure"""
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    preferences: Dict[str, Any] = None

@dataclass
class Session:
    """User session data structure"""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True

class AdvancedUserManagement:
    """Advanced user management system with authentication and authorization"""
    
    def __init__(self):
        self.rag = LightweightRAG()
        self.users = {}
        self.sessions = {}
        self.jwt_secret = secrets.token_urlsafe(32)
        self.storage_path = Path("./user_data")
        self.storage_path.mkdir(exist_ok=True)
        self.load_user_data()
        
    def generate_user_id(self) -> str:
        """Generate unique user ID"""
        return secrets.token_urlsafe(16)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def generate_jwt_token(self, user_id: str, expires_in_hours: int = 24) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user ID"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    async def create_user(self, username: str, email: str, password: str, 
                         role: UserRole = UserRole.USER) -> Dict[str, Any]:
        """Create new user account"""
        logger.info(f"🔐 Creating new user: {username}")
        
        # Validate input
        if not username or not email or not password:
            return {"success": False, "error": "Username, email, and password are required"}
        
        if len(password) < 8:
            return {"success": False, "error": "Password must be at least 8 characters"}
        
        # Check if user already exists
        if any(user.username == username or user.email == email for user in self.users.values()):
            return {"success": False, "error": "Username or email already exists"}
        
        # Create user
        user_id = self.generate_user_id()
        password_hash = self.hash_password(password)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            metadata={},
            preferences={
                "theme": "light",
                "language": "fr",
                "notifications": True
            }
        )
        
        self.users[user_id] = user
        await self.save_user_data()
        
        # Add user creation to knowledge base
        user_info = f"Nouvel utilisateur créé: {username} ({email}) avec le rôle {role.value}"
        self.rag.add_document(
            content=user_info,
            title=f"Création utilisateur {username}",
            source="user_management",
            doc_type="user_action",
            metadata={"user_id": user_id, "action": "create_user"}
        )
        
        logger.info(f"✅ User created successfully: {username}")
        return {
            "success": True,
            "user_id": user_id,
            "message": "User created successfully"
        }
    
    async def authenticate_user(self, username: str, password: str, 
                              ip_address: str = "", user_agent: str = "") -> Dict[str, Any]:
        """Authenticate user and create session"""
        logger.info(f"🔑 Authenticating user: {username}")
        
        # Find user by username or email
        user = None
        for u in self.users.values():
            if u.username == username or u.email == username:
                user = u
                break
        
        if not user:
            return {"success": False, "error": "Invalid username or password"}
        
        if user.status != UserStatus.ACTIVE:
            return {"success": False, "error": f"Account is {user.status.value}"}
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            return {"success": False, "error": "Invalid username or password"}
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        session = Session(
            session_id=session_id,
            user_id=user.id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session_id] = session
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        # Generate JWT token
        jwt_token = self.generate_jwt_token(user.id)
        
        await self.save_user_data()
        
        # Add login to knowledge base
        login_info = f"Connexion utilisateur: {user.username} depuis {ip_address}"
        self.rag.add_document(
            content=login_info,
            title=f"Connexion {user.username}",
            source="user_management",
            doc_type="user_action",
            metadata={"user_id": user.id, "action": "login", "ip": ip_address}
        )
        
        logger.info(f"✅ User authenticated successfully: {username}")
        return {
            "success": True,
            "user_id": user.id,
            "session_id": session_id,
            "jwt_token": jwt_token,
            "user_info": {
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "preferences": user.preferences
            }
        }
    
    async def validate_session(self, session_id: str) -> Optional[User]:
        """Validate user session"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        if not session.is_active or datetime.utcnow() > session.expires_at:
            session.is_active = False
            return None
        
        return self.users.get(session.user_id)
    
    async def logout_user(self, session_id: str) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        session = self.sessions.get(session_id)
        if not session:
            return {"success": False, "error": "Invalid session"}
        
        session.is_active = False
        user = self.users.get(session.user_id)
        
        if user:
            logger.info(f"🚪 User logged out: {user.username}")
            
            # Add logout to knowledge base
            logout_info = f"Déconnexion utilisateur: {user.username}"
            self.rag.add_document(
                content=logout_info,
                title=f"Déconnexion {user.username}",
                source="user_management",
                doc_type="user_action",
                metadata={"user_id": user.id, "action": "logout"}
            )
        
        await self.save_user_data()
        return {"success": True, "message": "User logged out successfully"}
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile information"""
        user = self.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Update allowed fields
        allowed_fields = ["email", "preferences", "metadata"]
        updated_fields = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                if field == "email":
                    # Check if email already exists
                    if any(u.email == value and u.id != user_id for u in self.users.values()):
                        return {"success": False, "error": "Email already exists"}
                    user.email = value
                elif field == "preferences":
                    user.preferences.update(value)
                elif field == "metadata":
                    user.metadata.update(value)
                updated_fields.append(field)
        
        if updated_fields:
            await self.save_user_data()
            
            # Add update to knowledge base
            update_info = f"Profil mis à jour pour {user.username}: {', '.join(updated_fields)}"
            self.rag.add_document(
                content=update_info,
                title=f"Mise à jour profil {user.username}",
                source="user_management",
                doc_type="user_action",
                metadata={"user_id": user.id, "action": "update_profile"}
            )
            
            logger.info(f"✅ Profile updated for user: {user.username}")
            return {"success": True, "updated_fields": updated_fields}
        
        return {"success": False, "error": "No valid fields to update"}
    
    async def change_user_password(self, user_id: str, current_password: str, 
                                  new_password: str) -> Dict[str, Any]:
        """Change user password"""
        user = self.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Verify current password
        if not self.verify_password(current_password, user.password_hash):
            return {"success": False, "error": "Current password is incorrect"}
        
        # Validate new password
        if len(new_password) < 8:
            return {"success": False, "error": "New password must be at least 8 characters"}
        
        # Update password
        user.password_hash = self.hash_password(new_password)
        await self.save_user_data()
        
        # Add password change to knowledge base
        password_info = f"Mot de passe changé pour {user.username}"
        self.rag.add_document(
            content=password_info,
            title=f"Changement mot de passe {user.username}",
            source="user_management",
            doc_type="user_action",
            metadata={"user_id": user.id, "action": "change_password"}
        )
        
        logger.info(f"🔒 Password changed for user: {user.username}")
        return {"success": True, "message": "Password changed successfully"}
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get user analytics and activity"""
        user = self.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Count user sessions
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
        active_sessions = [s for s in user_sessions if s.is_active]
        
        # Calculate activity metrics
        total_sessions = len(user_sessions)
        days_since_creation = (datetime.utcnow() - user.created_at).days
        avg_sessions_per_week = (total_sessions / max(days_since_creation / 7, 1)) if days_since_creation > 0 else 0
        
        analytics = {
            "user_info": {
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "status": user.status.value,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            "activity_metrics": {
                "total_sessions": total_sessions,
                "active_sessions": len(active_sessions),
                "days_since_creation": days_since_creation,
                "avg_sessions_per_week": round(avg_sessions_per_week, 2)
            },
            "preferences": user.preferences,
            "metadata": user.metadata
        }
        
        return {"success": True, "analytics": analytics}
    
    async def list_users(self, filter_role: Optional[UserRole] = None, 
                        filter_status: Optional[UserStatus] = None) -> Dict[str, Any]:
        """List all users with optional filtering"""
        users_list = []
        
        for user in self.users.values():
            # Apply filters
            if filter_role and user.role != filter_role:
                continue
            if filter_status and user.status != filter_status:
                continue
            
            users_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "status": user.status.value,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            })
        
        return {
            "success": True,
            "total_users": len(users_list),
            "users": users_list
        }
    
    async def update_user_status(self, user_id: str, new_status: UserStatus, 
                               admin_user_id: str) -> Dict[str, Any]:
        """Update user status (admin only)"""
        admin_user = self.users.get(admin_user_id)
        if not admin_user or admin_user.role != UserRole.ADMIN:
            return {"success": False, "error": "Admin privileges required"}
        
        user = self.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        old_status = user.status
        user.status = new_status
        await self.save_user_data()
        
        # Add status change to knowledge base
        status_info = f"Statut utilisateur changé par {admin_user.username}: {user.username} {old_status.value} → {new_status.value}"
        self.rag.add_document(
            content=status_info,
            title=f"Changement statut {user.username}",
            source="user_management",
            doc_type="admin_action",
            metadata={
                "user_id": user.id,
                "admin_id": admin_user_id,
                "action": "change_status",
                "old_status": old_status.value,
                "new_status": new_status.value
            }
        )
        
        logger.info(f"👤 User status changed: {user.username} → {new_status.value}")
        return {"success": True, "message": f"User status changed to {new_status.value}"}
    
    async def create_admin_user(self) -> Dict[str, Any]:
        """Create default admin user for system setup"""
        logger.info("🔧 Creating default admin user...")
        
        admin_username = "admin"
        admin_email = "admin@netzinformatique.fr"
        admin_password = "NETZ2025!Admin"
        
        # Check if admin already exists
        if any(user.role == UserRole.ADMIN for user in self.users.values()):
            return {"success": False, "message": "Admin user already exists"}
        
        result = await self.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            role=UserRole.ADMIN
        )
        
        if result["success"]:
            logger.info("✅ Default admin user created")
            logger.info(f"   Username: {admin_username}")
            logger.info(f"   Email: {admin_email}")
            logger.info(f"   Password: {admin_password}")
            logger.info("   ⚠️ Change password after first login!")
        
        return result
    
    async def save_user_data(self):
        """Save user and session data to storage"""
        # Save users
        users_data = {}
        for user_id, user in self.users.items():
            users_data[user_id] = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password_hash": user.password_hash,
                "role": user.role.value,
                "status": user.status.value,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "metadata": user.metadata,
                "preferences": user.preferences
            }
        
        with open(self.storage_path / "users.json", 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
        
        # Save sessions
        sessions_data = {}
        for session_id, session in self.sessions.items():
            sessions_data[session_id] = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "is_active": session.is_active
            }
        
        with open(self.storage_path / "sessions.json", 'w', encoding='utf-8') as f:
            json.dump(sessions_data, f, ensure_ascii=False, indent=2)
    
    def load_user_data(self):
        """Load user and session data from storage"""
        # Load users
        users_file = self.storage_path / "users.json"
        if users_file.exists():
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            for user_id, data in users_data.items():
                user = User(
                    id=data["id"],
                    username=data["username"],
                    email=data["email"],
                    password_hash=data["password_hash"],
                    role=UserRole(data["role"]),
                    status=UserStatus(data["status"]),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    last_login=datetime.fromisoformat(data["last_login"]) if data["last_login"] else None,
                    metadata=data.get("metadata", {}),
                    preferences=data.get("preferences", {})
                )
                self.users[user_id] = user
        
        # Load sessions
        sessions_file = self.storage_path / "sessions.json"
        if sessions_file.exists():
            with open(sessions_file, 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
            
            for session_id, data in sessions_data.items():
                session = Session(
                    session_id=data["session_id"],
                    user_id=data["user_id"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    expires_at=datetime.fromisoformat(data["expires_at"]),
                    ip_address=data["ip_address"],
                    user_agent=data["user_agent"],
                    is_active=data["is_active"]
                )
                self.sessions[session_id] = session
        
        logger.info(f"📚 Loaded {len(self.users)} users and {len(self.sessions)} sessions")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        active_sessions = len([s for s in self.sessions.values() if s.is_active])
        total_users = len(self.users)
        users_by_role = {}
        users_by_status = {}
        
        for user in self.users.values():
            role = user.role.value
            status = user.status.value
            users_by_role[role] = users_by_role.get(role, 0) + 1
            users_by_status[status] = users_by_status.get(status, 0) + 1
        
        return {
            "total_users": total_users,
            "active_sessions": active_sessions,
            "users_by_role": users_by_role,
            "users_by_status": users_by_status,
            "system_health": "Excellent" if total_users > 0 else "No users"
        }

async def main():
    """Main function to demonstrate user management system"""
    logger.info("🚀 NETZ Advanced User Management System")
    
    user_mgmt = AdvancedUserManagement()
    
    # Create admin user if none exists
    await user_mgmt.create_admin_user()
    
    # Demo: Create a test user
    result = await user_mgmt.create_user(
        username="testuser",
        email="test@netzinformatique.fr",
        password="TestPassword123",
        role=UserRole.USER
    )
    
    if result["success"]:
        print(f"✅ Test user created: {result['user_id']}")
        
        # Demo: Authenticate user
        auth_result = await user_mgmt.authenticate_user(
            username="testuser",
            password="TestPassword123",
            ip_address="127.0.0.1",
            user_agent="Test Client"
        )
        
        if auth_result["success"]:
            print(f"🔑 User authenticated: {auth_result['session_id']}")
            
            # Demo: Get user analytics
            analytics = await user_mgmt.get_user_analytics(result['user_id'])
            if analytics["success"]:
                print(f"📊 User analytics retrieved")
    
    # Get system stats
    stats = await user_mgmt.get_system_stats()
    print(f"\n📈 SYSTEM STATISTICS:")
    print(f"   Total Users: {stats['total_users']}")
    print(f"   Active Sessions: {stats['active_sessions']}")
    print(f"   Users by Role: {stats['users_by_role']}")
    print(f"   System Health: {stats['system_health']}")
    
    return user_mgmt

if __name__ == "__main__":
    asyncio.run(main())