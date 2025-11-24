from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate, UserListResponse, MessageResponse
from app.utils.crud import UserCRUD
from app.models.user import UserRole
from app.api.auth import get_admin_user, get_teacher_or_admin_user

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get list of users (Admin only)"""
    user_crud = UserCRUD(db)
    
    users = user_crud.get_users(skip=skip, limit=limit, role=role, is_active=is_active)
    total = user_crud.count_users(role=role, is_active=is_active)
    
    return {
        "users": users,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.get("/my-students", response_model=UserListResponse)
async def get_my_students(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    current_user: User = Depends(get_teacher_or_admin_user),
    db: Session = Depends(get_db)
):
    """Get students created by current teacher (Teacher/Admin only)"""
    user_crud = UserCRUD(db)
    users = user_crud.get_users_created_by(current_user.id, skip=skip, limit=limit)
    
    # Count total for pagination
    total_students = len(user_crud.get_users_created_by(current_user.id))
    
    return {
        "users": users,
        "total": total_students,
        "page": skip // limit + 1,  # Calculate page number
        "size": limit
    }


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (Admin only)"""
    user_crud = UserCRUD(db)
    user = user_crud.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_teacher_or_admin_user),
    db: Session = Depends(get_db)
):
    """Create new user (Teacher/Admin only)"""
    user_crud = UserCRUD(db)
    
    # Teachers can only create STUDENT accounts - compare by value
    if current_user.role == UserRole.TEACHER and user.role.value != UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teachers can only create student accounts"
        )
    
    # Check if username already exists
    if user_crud.is_username_taken(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if user_crud.is_email_taken(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    try:
        # Pass current user ID as created_by if they are teacher/admin
        created_by_id = current_user.id if current_user.role in [UserRole.TEACHER, UserRole.ADMIN] else None
        db_user = user_crud.create_user(user, created_by_user_id=created_by_id)
        return db_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user (Admin only)"""
    user_crud = UserCRUD(db)
    
    # Check if user exists
    existing_user = user_crud.get_user(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if username is being changed and is available
    if user_update.username and user_update.username != existing_user.username:
        if user_crud.is_username_taken(user_update.username, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Check if email is being changed and is available
    if user_update.email and user_update.email != existing_user.email:
        if user_crud.is_email_taken(user_update.email, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
    
    # Update user
    updated_user = user_crud.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )
    
    return updated_user

@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Soft delete user (Admin only)"""
    user_crud = UserCRUD(db)
    
    # Check if user exists
    user = user_crud.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Soft delete user
    success = user_crud.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )
    
    return {"message": f"User {user.username} has been deactivated"}

@router.post("/{user_id}/activate", response_model=MessageResponse)
async def activate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Activate user (Admin only)"""
    user_crud = UserCRUD(db)
    
    user = user_crud.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active"
        )
    
    # Activate user
    user_update = UserUpdate(is_active=True)
    updated_user = user_crud.update_user(user_id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error activating user"
        )
    
    return {"message": f"User {user.username} has been activated"}

@router.post("/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate user (Admin only)"""
    user_crud = UserCRUD(db)
    
    user = user_crud.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already inactive"
        )
    
    # Deactivate user
    success = user_crud.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deactivating user"
        )
    
    return {"message": f"User {user.username} has been deactivated"}
