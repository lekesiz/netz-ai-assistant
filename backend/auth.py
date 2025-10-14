#!/usr/bin/env python3
"""
NETZ AI Authentication System
JWT-based authentication with role-based access control
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import uuid
from pydantic import BaseModel, EmailStr

# Security configuration
SECRET_KEY = "netz-ai-jwt-secret-change-in-production"  # Load from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# User models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: str
    full_name: str
    company: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

# In-memory user storage (replace with database in production)
users_db: Dict[str, Dict] = {
    "admin@netzinformatique.fr": {
        "id": "admin-001",
        "email": "admin@netzinformatique.fr",
        "full_name": "NETZ Admin",
        "company": "NETZ Informatique",
        "role": "admin",
        "is_active": True,
        "hashed_password": pwd_context.hash("admin123"),
        "created_at": datetime.utcnow(),
        "last_login": None
    }
}

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    return users_db.get(email)

def create_user(user_data: UserCreate) -> Dict:
    """Create new user"""
    if user_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_id = str(uuid.uuid4())
    user_dict = {
        "id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "company": user_data.company,
        "role": "user",
        "is_active": True,
        "hashed_password": get_password_hash(user_data.password),
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    users_db[user_data.email] = user_dict
    return user_dict

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user with email and password"""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    
    # Update last login
    user["last_login"] = datetime.utcnow()
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

async def get_current_active_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Get current active user"""
    return current_user

async def get_admin_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Get current user if admin"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Auth endpoints for FastAPI
def login_user(login_data: UserLogin) -> TokenResponse:
    """Login user and return tokens"""
    user = authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user["email"], "role": user["role"]}
    )
    
    # Prepare user data for response (without sensitive info)
    user_response = {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "company": user["company"],
        "role": user["role"],
        "last_login": user["last_login"].isoformat() if user["last_login"] else None
    }
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

def register_user(user_data: UserCreate) -> TokenResponse:
    """Register new user and return tokens"""
    user = create_user(user_data)
    
    # Auto-login after registration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user["email"], "role": user["role"]}
    )
    
    # Prepare user data for response
    user_response = {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "company": user["company"],
        "role": user["role"],
        "last_login": None
    }
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

def refresh_access_token(refresh_token: str) -> TokenResponse:
    """Refresh access token using refresh token"""
    payload = verify_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    email = payload.get("sub")
    user = get_user_by_email(email)
    
    if not user or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    # Prepare user data for response
    user_response = {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "company": user["company"],
        "role": user["role"],
        "last_login": user["last_login"].isoformat() if user["last_login"] else None
    }
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,  # Keep existing refresh token
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

# Test function
def test_auth_system():
    """Test authentication system"""
    print("🧪 Testing NETZ Auth System...")
    
    # Test user creation
    try:
        user_data = UserCreate(
            email="test@example.com",
            password="testpass123",
            full_name="Test User",
            company="Test Company"
        )
        result = register_user(user_data)
        print(f"✅ User registration: {result.user['email']}")
    except Exception as e:
        print(f"❌ User registration failed: {e}")
    
    # Test login
    try:
        login_data = UserLogin(email="test@example.com", password="testpass123")
        result = login_user(login_data)
        print(f"✅ User login: {result.token_type} token generated")
    except Exception as e:
        print(f"❌ User login failed: {e}")
    
    print("🎉 Auth system test completed!")

if __name__ == "__main__":
    test_auth_system()