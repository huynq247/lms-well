from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional

from app.core.database import get_database
from app.core.auth import get_current_user, get_teacher_or_admin_user, User, UserRole, get_assigned_content_ids
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse, CourseFilter
)
from app.schemas.lesson import (
    LessonCreate, LessonUpdate, LessonResponse
)
from app.schemas.common import (
    ReorderRequest, PaginationParams, PaginatedResponse, MessageResponse
)
from app.crud import CourseCRUD, LessonCRUD
from app.utils.url_validator import url_validator

router = APIRouter(prefix="/courses", tags=["Courses"])

# Course endpoints
@router.get("/status")
async def get_courses_status(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get courses service status and basic stats"""
    try:
        course_crud = CourseCRUD(db)
        courses = await course_crud.get_courses(
            PaginationParams(page=1, size=1), 
            CourseFilter()
        )
        if courses["items"]:
            course = courses["items"][0]
            return {
                "service": "content-service",
                "status": "healthy",
                "sample_course": {
                    "id": str(course.id),
                    "title": course.title,
                    "instructor_id": course.instructor_id,
                    "is_active": course.is_active
                },
                "total_courses": courses["total"],
                "message": "Service is operational"
            }
        return {
            "service": "content-service",
            "status": "healthy", 
            "message": "No courses found"
        }
    except Exception as e:
        return {
            "service": "content-service",
            "status": "error",
            "error": str(e)
        }

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new course"""
    course_crud = CourseCRUD(db)
    
    # TODO: Get instructor name from auth service
    instructor_name = f"Instructor {course.instructor_id}"
    
    try:
        db_course = await course_crud.create_course(course, instructor_name)
        return CourseResponse(**db_course.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating course: {str(e)}"
        )

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get course by ID"""
    course_crud = CourseCRUD(db)
    course = await course_crud.get_course(course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return CourseResponse(**course.dict())

@router.get("/")
async def get_courses(
    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=50),  # Reduced max size for performance
    search: Optional[str] = Query(None, max_length=100),
    instructor_id: Optional[int] = Query(None),
    is_published: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get courses with role-based filtering"""
    try:
        course_crud = CourseCRUD(db)
        
        pagination = PaginationParams(page=page, size=size, search=search)
        
        # Role-based filtering
        if current_user.role == UserRole.STUDENT:
            # Students can see:
            # 1. Their assigned courses
            # 2. Public courses (is_public=True AND is_published=True)
            assigned_course_ids = await get_assigned_content_ids(current_user.id, "course")
            
            # Get assigned courses
            assigned_filters = CourseFilter(
                instructor_id=instructor_id,
                is_published=is_published,
                is_active=is_active,
                course_ids=assigned_course_ids if assigned_course_ids else []
            )
            assigned_result = await course_crud.get_courses(pagination, assigned_filters)
            
            # Get public courses
            public_filters = CourseFilter(
                instructor_id=instructor_id,
                is_published=True,  # Public courses must be published
                is_active=True,
            )
            # Fetch public courses separately
            public_courses_cursor = db["courses"].find({
                "is_public": True,
                "is_published": True,
                "is_active": True
            })
            public_courses = await public_courses_cursor.to_list(length=None)
            
            # Merge results (avoid duplicates)
            assigned_ids = {str(c.id) for c in assigned_result["items"]}
            all_courses = list(assigned_result["items"])
            
            for pub_course in public_courses:
                if str(pub_course["_id"]) not in assigned_ids:
                    # Convert to Course object
                    from app.models.content import Course
                    course_obj = Course(**pub_course)
                    all_courses.append(course_obj)
            
            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                all_courses = [
                    c for c in all_courses
                    if search_lower in c.title.lower() or 
                       (c.description and search_lower in c.description.lower())
                ]
            
            result = {
                "items": all_courses,
                "total": len(all_courses),
                "page": page,
                "size": size,
                "pages": (len(all_courses) + size - 1) // size,
                "has_next": page * size < len(all_courses),
                "has_prev": page > 1
            }
        else:  # TEACHER or ADMIN - can see all courses
            filters = CourseFilter(
                instructor_id=instructor_id,
                is_published=is_published,
            is_active=is_active
        )
        
        result = await course_crud.get_courses(pagination, filters)
        
        # Manual serialization to avoid Pydantic issues
        courses_response = []
        for course in result["items"]:
            courses_response.append({
                "id": str(course.id),
                "title": course.title,
                "description": course.description,
                "instructor_id": course.instructor_id,
                "instructor_name": course.instructor_name,
                "estimated_duration": course.estimated_duration,
                "is_published": course.is_published,
                "is_active": course.is_active,
                "is_public": getattr(course, 'is_public', False),
                "total_lessons": course.total_lessons,
                "created_at": course.created_at.isoformat() if course.created_at else None,
                "updated_at": course.updated_at.isoformat() if course.updated_at else None
            })
        
        return {
            "items": courses_response,
            "total": result["total"],
            "page": result["page"], 
            "size": result["size"],
            "pages": result["pages"],
            "has_next": result["has_next"],
            "has_prev": result["has_prev"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update course"""
    course_crud = CourseCRUD(db)
    
    updated_course = await course_crud.update_course(course_id, course_update)
    if not updated_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or no changes made"
        )
    
    return CourseResponse(**updated_course.dict())

@router.delete("/{course_id}", response_model=MessageResponse)
async def delete_course(
    course_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Soft delete course"""
    course_crud = CourseCRUD(db)
    
    success = await course_crud.delete_course(course_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return MessageResponse(message="Course deleted successfully")

@router.get("/instructor/{instructor_id}", response_model=List[CourseResponse])
async def get_courses_by_instructor(
    instructor_id: int,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all courses by instructor"""
    course_crud = CourseCRUD(db)
    courses = await course_crud.get_courses_by_instructor(instructor_id)
    
    return [CourseResponse(**course.dict()) for course in courses]

# Lesson endpoints
@router.post("/{course_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: str,
    lesson: LessonCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new lesson for a course"""
    # Verify course exists
    course_crud = CourseCRUD(db)
    course = await course_crud.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Set course_id from URL
    lesson.course_id = course_id
    
    lesson_crud = LessonCRUD(db)
    
    try:
        db_lesson = await lesson_crud.create_lesson(lesson)
        return LessonResponse(**db_lesson.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating lesson: {str(e)}"
        )

@router.get("/{course_id}/lessons", response_model=List[LessonResponse])
async def get_lessons_by_course(
    course_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all lessons for a course"""
    # Verify course exists
    course_crud = CourseCRUD(db)
    course = await course_crud.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    lesson_crud = LessonCRUD(db)
    lessons = await lesson_crud.get_lessons_by_course(course_id)
    
    return [LessonResponse(**lesson.dict()) for lesson in lessons]

@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get lesson by ID"""
    lesson_crud = LessonCRUD(db)
    lesson = await lesson_crud.get_lesson(lesson_id)
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    return LessonResponse(**lesson.dict())

@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: str,
    lesson_update: LessonUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update lesson"""
    lesson_crud = LessonCRUD(db)
    
    updated_lesson = await lesson_crud.update_lesson(lesson_id, lesson_update)
    if not updated_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found or no changes made"
        )
    
    return LessonResponse(**updated_lesson.dict())

@router.delete("/lessons/{lesson_id}", response_model=MessageResponse)
async def delete_lesson(
    lesson_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Soft delete lesson"""
    lesson_crud = LessonCRUD(db)
    
    success = await lesson_crud.delete_lesson(lesson_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    return MessageResponse(message="Lesson deleted successfully")

@router.put("/{course_id}/lessons/reorder", response_model=MessageResponse)
async def reorder_lessons(
    course_id: str,
    reorder_request: ReorderRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Reorder lessons in a course"""
    # Verify course exists
    course_crud = CourseCRUD(db)
    course = await course_crud.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    lesson_crud = LessonCRUD(db)
    success = await lesson_crud.reorder_lessons(course_id, reorder_request.items)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reordering lessons"
        )
    
    return MessageResponse(message="Lessons reordered successfully")

@router.post("/{course_id}/lessons/{lesson_id}/assign", response_model=MessageResponse)
async def assign_existing_lesson_to_course(
    course_id: str,
    lesson_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Assign an existing lesson to a course (creates a copy)"""
    # Verify course exists
    course_crud = CourseCRUD(db)
    course = await course_crud.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Verify lesson exists
    lesson_crud = LessonCRUD(db)
    original_lesson = await lesson_crud.get_lesson(lesson_id)
    if not original_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Check if lesson is already assigned to this course
    if original_lesson.course_id == course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lesson is already assigned to this course"
        )
    
    try:
        # Create a copy of the lesson for the new course
        # Get the highest order number in the target course
        existing_lessons = await lesson_crud.get_lessons_by_course(course_id)
        max_order = max([lesson.order for lesson in existing_lessons], default=0)
        
        # Create lesson copy with new course_id and incremented order
        lesson_copy = LessonCreate(
            course_id=course_id,
            title=f"{original_lesson.title} (Copy)",
            content=original_lesson.content,
            order=max_order + 1,
            duration=original_lesson.duration,
            image_url=original_lesson.image_url,
            video_url=original_lesson.video_url,
            is_published=False,  # Start as unpublished for review
            instructor_id=original_lesson.instructor_id
        )
        
        await lesson_crud.create_lesson(lesson_copy)
        
        return MessageResponse(message=f"Lesson '{original_lesson.title}' successfully assigned to course")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning lesson to course: {str(e)}"
        )
