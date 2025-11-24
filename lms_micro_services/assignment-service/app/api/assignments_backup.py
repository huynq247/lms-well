from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_database
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentFilter,
    PaginationParams, PaginatedResponse, MessageResponse, ContentType, AssignmentStatus
)
from app.utils.crud import AssignmentCRUD
from app.utils.external_services import AuthServiceClient, ContentServiceClient

router = APIRouter(prefix="/assignments", tags=["Assignments"])

# Dependency to get external service clients
async def get_auth_client():
    return AuthServiceClient()

async def get_content_client():
    return ContentServiceClient()


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment: AssignmentCreate,
    db: AsyncSession = Depends(get_database),
    auth_client: AuthServiceClient = Depends(get_auth_client),
    content_client: ContentServiceClient = Depends(get_content_client)
):
    """Create a new assignment"""
    assignment_crud = AssignmentCRUD(db)
    
    try:
        # Validate instructor and student exist
        instructor = await auth_client.get_user(assignment.instructor_id)
        if not instructor or instructor.get('role') not in ['admin', 'teacher']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid instructor ID or insufficient permissions"
            )
        
        student = await auth_client.get_user(assignment.student_id)
        if not student or student.get('role') != 'student':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid student ID"
            )
        
        # Validate content exists
        content = await content_client.get_content(assignment.content_type, assignment.content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content not found: {assignment.content_type} {assignment.content_id}"
            )
        
        # Create assignment
        db_assignment = await assignment_crud.create_assignment(assignment)
        return AssignmentResponse.model_validate(db_assignment)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating assignment: {str(e)}"
        )
            
        
        if not student_valid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {assignment.student_id} not found"
            )
        
        # Create assignment
        db_assignment = await assignment_crud.create_assignment(assignment, content_data['title'])
        return db_assignment
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating assignment: {str(e)}"
        )


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get assignment by ID"""
    assignment_crud = AssignmentCRUD(db)
    
    assignment = await assignment_crud.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return assignment


@router.get("/", response_model=PaginatedResponse)
async def list_assignments(
    pagination: PaginationParams = Depends(),
    assignment_filter: AssignmentFilter = Depends(),
    db: AsyncSession = Depends(get_database)
):
    """List assignments with filtering and pagination"""
    assignment_crud = AssignmentCRUD(db)
    
    assignments, total = await assignment_crud.list_assignments(
        pagination=pagination,
        assignment_filter=assignment_filter
    )
    
    return PaginatedResponse.create(assignments, total, pagination)


@router.get("/instructors/{instructor_id}", response_model=PaginatedResponse)
async def get_instructor_assignments(
    instructor_id: int,
    pagination: PaginationParams = Depends(),
    status_filter: Optional[AssignmentStatus] = Query(None),
    db: AsyncSession = Depends(get_database)
):
    """Get assignments for a specific instructor"""
    assignment_crud = AssignmentCRUD(db)
    
    filter_data = AssignmentFilter(
        instructor_id=instructor_id,
        status=status_filter
    )
    
    assignments, total = await assignment_crud.list_assignments(
        pagination=pagination,
        assignment_filter=filter_data
    )
    
    return PaginatedResponse.create(assignments, total, pagination)


@router.get("/students/{student_id}", response_model=PaginatedResponse)
async def get_student_assignments(
    student_id: int,
    pagination: PaginationParams = Depends(),
    status_filter: Optional[AssignmentStatus] = Query(None),
    db: AsyncSession = Depends(get_database)
):
    """Get assignments for a specific student"""
    assignment_crud = AssignmentCRUD(db)
    
    filter_data = AssignmentFilter(
        student_id=student_id,
        status=status_filter
    )
    
    assignments, total = await assignment_crud.list_assignments(
        pagination=pagination,
        assignment_filter=filter_data
    )
    
    return PaginatedResponse.create(assignments, total, pagination)


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


@router.delete("/{assignment_id}", response_model=MessageResponse)
async def delete_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Delete an assignment"""
    assignment_crud = AssignmentCRUD(db)
    
    success = await assignment_crud.delete_assignment(assignment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return MessageResponse(message="Assignment deleted successfully")
