from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request
from pydantic import BaseModel
import httpx

class UserInfo(BaseModel):
    user_id: int
    username: str
    role: str

async def get_current_user_from_request(request: Request) -> UserInfo:
    """Extract and validate user from JWT token in request"""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    # Validate token with auth service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "http://auth-service:8001/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Error: {response.status_code}: Invalid or expired token"
                )
            
            user_data = response.json()
            return UserInfo(
                user_id=user_data["id"],
                username=user_data["username"],
                role=user_data["role"]
            )
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

def enforce_role_based_access(
    user_info: UserInfo,
    student_id: Optional[int] = None,
    instructor_id: Optional[int] = None
) -> Dict[str, Any]:
    """Enforce role-based access control and return appropriate filters"""
    
    if user_info.role == "ADMIN":
        # Admin can see everything
        return {
            "student_id": student_id,
            "instructor_id": instructor_id
        }
    
    elif user_info.role == "TEACHER":
        # Teacher can only see their own assignments (as instructor)
        return {
            "student_id": student_id,
            "instructor_id": user_info.user_id  # Force to current teacher's ID
        }
    
    elif user_info.role == "STUDENT":
        # Student can only see assignments assigned to them
        return {
            "student_id": user_info.user_id,  # Force to current student's ID
            "instructor_id": None  # Don't filter by instructor for students
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role"
        )
