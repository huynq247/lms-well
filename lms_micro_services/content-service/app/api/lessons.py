from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional

from app.core.database import get_database
from app.core.auth import get_current_user, get_teacher_or_admin_user, User, UserRole, get_assigned_content_ids
from app.schemas.lesson import (
    LessonCreate, LessonUpdate, LessonResponse
)
from app.schemas.common import (
    PaginationParams, PaginatedResponse, MessageResponse
)
from app.crud import LessonCRUD

router = APIRouter(prefix="/lessons", tags=["Lessons"])

@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson: LessonCreate,
    current_user: User = Depends(get_teacher_or_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new lesson"""
    lesson_crud = LessonCRUD(db)
    
    # Add instructor_id to lesson
    lesson_dict = lesson.dict()
    lesson_dict["instructor_id"] = current_user.id
    lesson_create = LessonCreate(**lesson_dict)
    
    created_lesson = await lesson_crud.create_lesson(lesson_create)
    return LessonResponse(**created_lesson.dict())

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get lesson by ID with role-based access"""
    lesson_crud = LessonCRUD(db)
    lesson = await lesson_crud.get_lesson(lesson_id)
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Role-based access control
    if current_user.role == UserRole.STUDENT:
        # Students can only access assigned lessons
        assigned_lesson_ids = await get_assigned_content_ids(current_user.id, "lesson")
        if lesson_id not in assigned_lesson_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. This lesson is not assigned to you."
            )
    elif current_user.role == UserRole.TEACHER:
        # Teachers can only access their own lessons or assigned ones
        if lesson.instructor_id != current_user.id:
            assigned_lesson_ids = await get_assigned_content_ids(current_user.id, "lesson")
            if lesson_id not in assigned_lesson_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You can only access your own lessons or assigned ones."
                )
    # ADMIN can access all lessons
    
    return LessonResponse(**lesson.dict())

@router.get("/", response_model=PaginatedResponse)
async def get_lessons(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=100),
    course_id: Optional[str] = Query(None),
    instructor_id: Optional[int] = Query(None),
    is_published: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get lessons with role-based filtering"""
    lesson_crud = LessonCRUD(db)
    
    pagination_dict = {"page": page, "size": size, "search": search}
    
    # Role-based filtering
    filters = {}
    
    if current_user.role == UserRole.STUDENT:
        # Students can only see assigned lessons
        assigned_lesson_ids = await get_assigned_content_ids(current_user.id, "lesson")
        if not assigned_lesson_ids:
            # No assigned lessons - return empty result
            return PaginatedResponse(
                items=[],
                total=0,
                page=page,
                size=size,
                pages=0,
                has_next=False,
                has_prev=False
            )
        filters["lesson_ids"] = assigned_lesson_ids
        filters["is_published"] = True  # Only published lessons
    elif current_user.role == UserRole.TEACHER:
        # Teachers see all lessons, but can optionally filter by instructor_id
        if instructor_id:
            filters["instructor_id"] = instructor_id
    # ADMIN sees all lessons - no additional filtering needed
    
    # Apply common filters
    if course_id:
        filters["course_id"] = course_id
    if is_published is not None:
        filters["is_published"] = is_published
    if is_active is not None:
        filters["is_active"] = is_active
    
    result = await lesson_crud.get_lessons(pagination_dict, filters)
    
    # Convert lessons to response format
    lessons_response = [LessonResponse(**lesson.dict()) for lesson in result["items"]]
    result["items"] = lessons_response
    
    return PaginatedResponse(**result)

@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: str,
    lesson_update: LessonUpdate,
    current_user: User = Depends(get_teacher_or_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update lesson"""
    lesson_crud = LessonCRUD(db)
    
    # Check if lesson exists and user has permission
    lesson = await lesson_crud.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Only lesson owner or admin can update
    if current_user.role == UserRole.TEACHER and lesson.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own lessons"
        )
    
    updated_lesson = await lesson_crud.update_lesson(lesson_id, lesson_update)
    if not updated_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    return LessonResponse(**updated_lesson.dict())

@router.delete("/{lesson_id}", response_model=MessageResponse)
async def delete_lesson(
    lesson_id: str,
    current_user: User = Depends(get_teacher_or_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete lesson"""
    lesson_crud = LessonCRUD(db)
    
    # Check if lesson exists and user has permission
    lesson = await lesson_crud.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Only lesson owner or admin can delete
    if current_user.role == UserRole.TEACHER and lesson.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own lessons"
        )
    
    success = await lesson_crud.delete_lesson(lesson_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    return MessageResponse(message="Lesson deleted successfully")

@router.get("/course/{course_id}", response_model=List[LessonResponse])
async def get_lessons_by_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all lessons for a specific course with role-based access"""
    lesson_crud = LessonCRUD(db)
    lessons = await lesson_crud.get_lessons_by_course(course_id)
    
    # Role-based filtering
    if current_user.role == UserRole.STUDENT:
        # Students can only see assigned lessons
        assigned_lesson_ids = await get_assigned_content_ids(current_user.id, "lesson")
        lessons = [lesson for lesson in lessons if str(lesson.id) in assigned_lesson_ids]
    elif current_user.role == UserRole.TEACHER:
        # Teachers can see all lessons in the course
        pass  # No additional filtering needed
    # ADMIN can see all lessons
    
    return [LessonResponse(**lesson.dict()) for lesson in lessons]
