"""
Authentication and authorization utilities for Content Service
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import httpx
from enum import Enum

from app.core.config import get_settings

settings = get_settings()
security = HTTPBearer()

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER" 
    STUDENT = "STUDENT"

class User:
    def __init__(self, id: int, username: str, email: str, role: UserRole, **kwargs):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        for key, value in kwargs.items():
            setattr(self, key, value)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token with auth service"""
    token = credentials.credentials
    
    print(f"🔧 Content-service received token: {token[:50]}...")
    
    try:
        # Validate token with auth service
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{settings.auth_service_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                print(f"Auth service returned: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user_data = response.json()
            return {
                "sub": str(user_data["id"]),
                "username": user_data["username"],
                "role": user_data["role"]
            }
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service timeout"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth service connection error: {str(e)}"
        )
    except Exception as e:
        print(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token_payload: Dict[str, Any] = Depends(verify_token)) -> User:
    """Get current user from token payload"""
    try:
        print(f"🔧 Getting current user from payload: {token_payload}")
        
        user_id = int(token_payload.get("sub"))
        username = token_payload.get("username")
        email = token_payload.get("email") 
        role = token_payload.get("role")
        
        print(f"🔧 Extracted: user_id={user_id}, username={username}, email={email}, role={role}")
        
        if not all([user_id, username, role]):
            print(f"🔧 Missing required fields: user_id={user_id}, username={username}, role={role}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = User(
            id=user_id,
            username=username,
            email=email or f"{username}@example.com",  # Email might be missing
            role=UserRole(role)
        )
        
        print(f"🔧 Created user object: {user.username} (role: {user.role})")
        return user
        
    except (ValueError, KeyError) as e:
        print(f"Token payload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

def require_role(*allowed_roles: UserRole):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Role-based dependencies
def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Require admin privileges"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def get_teacher_or_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Require teacher or admin privileges"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher or admin privileges required"
        )
    return current_user

def get_student_user(current_user: User = Depends(get_current_user)) -> User:
    """Require student privileges"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student privileges required"
        )
    return current_user

async def get_assigned_content_ids(user_id: int, content_type: str) -> list[str]:
    """Get assigned content IDs for a student from assignment service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8004/api/assignments/students/{user_id}"
            )
            if response.status_code == 200:
                assignments = response.json()
                return [
                    assignment["content_id"] 
                    for assignment in assignments 
                    if assignment["content_type"] == content_type
                ]
            return []
    except Exception as e:
        print(f"Error fetching assignments: {e}")
        return []
