from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database
from app.models.assignment import Assignment
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentFilter, AssignmentStatus
)
from app.schemas.common import PaginatedResponse, PaginationParams, get_pagination_params
from app.utils.crud import AssignmentCRUD, assignment_to_response
from app.utils.external_services import AuthServiceClient, ContentServiceClient
from app.utils.auth import get_current_user_from_request, enforce_role_based_access

router = APIRouter(prefix="/assignments", tags=["assignments"])

auth_client = AuthServiceClient()
content_client = ContentServiceClient()


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment: AssignmentCreate,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Create a new assignment with course validation"""
    assignment_crud = AssignmentCRUD(db)
    
    try:
        print(f"📝 Creating assignment: {assignment.dict()}")
        
        # Get auth token from request headers
        auth_token = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.split(" ")[1]
        
        print(f"🔑 Auth token: {auth_token[:20]}..." if auth_token else "No auth token")
        
        # Validate course exists if content_type is course
        if assignment.content_type == "course":
            print(f"🎓 Validating course: {assignment.content_id}")
            course_data = await content_client.get_course_details(assignment.content_id, auth_token)
            print(f"✅ Course data: {course_data}")
            if not course_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Course with ID {assignment.content_id} not found"
                )
            # Update assignment with course title if not provided
            if not assignment.content_title or assignment.content_title == "":
                assignment.content_title = course_data.get("title", "Unknown Course")
        
        # Validate users exist (enable when needed)
        # instructor_valid = await auth_client.validate_user(assignment.instructor_id)
        # if not instructor_valid:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Instructor with ID {assignment.instructor_id} not found"
        #     )
        
        # student_valid = await auth_client.validate_user(assignment.student_id)
        # if not student_valid:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Student with ID {assignment.student_id} not found"
        #     )
        
        # Create assignment
        print(f"💾 Creating assignment in database...")
        db_assignment = await assignment_crud.create_assignment(assignment)
        print(f"✅ Assignment created with ID: {db_assignment.id}")
        return assignment_to_response(db_assignment)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error creating assignment: {str(e)}")
        print(f"📋 Full traceback:\n{error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating assignment: {str(e)}"
        )


@router.get("/status")
async def get_assignments_status(db: AsyncSession = Depends(get_database)):
    """Get assignments service status and basic stats"""
    try:
        from sqlalchemy import select
        result = await db.execute(select(Assignment).limit(1))
        assignment = result.scalar_one_or_none()
        
        if assignment:
            return {
                "service": "assignment-service",
                "status": "healthy",
                "sample_assignment": {
                    "id": assignment.id,
                    "title": assignment.title,
                    "status": assignment.status,
                    "created_at": assignment.created_at.isoformat() if assignment.created_at else None
                },
                "message": "Service is operational"
            }
        else:
            return {
                "service": "assignment-service", 
                "status": "healthy",
                "message": "No assignments found"
            }
    except Exception as e:
        return {
            "service": "assignment-service",
            "status": "error", 
            "error": str(e)
        }


@router.get("/{assignment_id}")
async def get_assignment(
    assignment_id: int,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Get assignment by ID with role-based access control"""
    assignment_crud = AssignmentCRUD(db)
    
    # Get current user for access control
    current_user = await get_current_user_from_request(request)
    
    assignment = await assignment_crud.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check access permissions
    if current_user.role == "STUDENT":
        # Student can only see assignments assigned to them
        if assignment.student_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own assignments"
            )
    elif current_user.role == "TEACHER":
        # Teacher can only see assignments they created
        if assignment.instructor_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view assignments you created"
            )
    # ADMIN can see everything (no additional check needed)
    
    # Get auth token
    auth_token = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        auth_token = auth_header.split(" ")[1]
    
    # Convert assignment using utility function
    assignment_response = assignment_to_response(assignment)
    
    # Add course progress if it's a course assignment
    if assignment.content_type == "course":
        progress = await content_client.get_course_progress(
            assignment.content_id, 
            assignment.student_id, 
            auth_token
        )
        if progress:
            assignment_response.course_progress_percentage = progress.get("progress_percentage", 0.0)
            assignment_response.total_lessons = progress.get("total_lessons", 0)
            assignment_response.completed_lessons = progress.get("completed_lessons", 0)
    
    return assignment_response


@router.get("/")
async def get_assignments(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    student_id: Optional[int] = Query(None),
    instructor_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_database)
):
    """Get assignments with role-based access control"""
    try:
        assignment_crud = AssignmentCRUD(db)
        
        # Get auth token
        auth_token = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.split(" ")[1]
        
        # Get current user and enforce role-based access
        current_user = await get_current_user_from_request(request)
        access_filters = enforce_role_based_access(
            current_user, 
            student_id=student_id, 
            instructor_id=instructor_id
        )
        
        # Create filter and pagination with enforced access
        assignment_filter = AssignmentFilter(
            student_id=access_filters["student_id"],
            instructor_id=access_filters["instructor_id"]
        )
        pagination = PaginationParams(page=page, size=size)
        
        assignments, total = await assignment_crud.get_assignments(assignment_filter, pagination)
        
        # Use assignment_to_response for proper serialization with supporting decks
        items = []
        for assignment in assignments:
            # Convert to AssignmentResponse using our helper function
            assignment_response = assignment_to_response(assignment)
            item = assignment_response.dict()
            
            # Add course progress if it's a course assignment
            if assignment.content_type == "course":
                progress = await content_client.get_course_progress(
                    assignment.content_id, 
                    assignment.student_id, 
                    auth_token
                )
                if progress:
                    item.update({
                        "course_progress_percentage": progress.get("progress_percentage", 0.0),
                        "total_lessons": progress.get("total_lessons", 0),
                        "completed_lessons": progress.get("completed_lessons", 0)
                    })
            
            items.append(item)
        
        # Return properly formatted response for frontend/testing
        return {
            "assignments": items,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.get("/instructors/{instructor_id}", response_model=List[AssignmentResponse])
async def get_instructor_assignments(
    instructor_id: int,
    status_filter: Optional[AssignmentStatus] = Query(None),
    db: AsyncSession = Depends(get_database)
):
    """Get assignments for a specific instructor"""
    assignment_crud = AssignmentCRUD(db)
    
    try:
        assignments = await assignment_crud.get_instructor_assignments(instructor_id)
        return assignments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting instructor assignments: {str(e)}"
        )


@router.get("/students/{student_id}", response_model=List[AssignmentResponse])
async def get_student_assignments(
    student_id: int,
    status_filter: Optional[AssignmentStatus] = Query(None),
    db: AsyncSession = Depends(get_database)
):
    """Get assignments for a specific student"""
    assignment_crud = AssignmentCRUD(db)
    
    try:
        assignments = await assignment_crud.get_student_assignments(student_id, status_filter)
        return assignments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting student assignments: {str(e)}"
        )


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_update: AssignmentUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update an assignment"""
    assignment_crud = AssignmentCRUD(db)
    
    assignment = await assignment_crud.update_assignment(assignment_id, assignment_update)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return assignment


@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Delete an assignment"""
    assignment_crud = AssignmentCRUD(db)
    
    deleted = await assignment_crud.delete_assignment(assignment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return {"message": "Assignment deleted successfully"}
