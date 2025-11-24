from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database
from app.schemas.assignment import (
    StudySessionCreate, StudySessionStart, StudySessionUpdate, StudySessionEnd, StudySessionResponse
)
from app.schemas.common import PaginatedResponse, PaginationParams, APIResponse
from app.utils.crud import StudySessionCRUD

router = APIRouter(prefix="/sessions", tags=["study-sessions"])


@router.post("/assignments/{assignment_id}/start", response_model=StudySessionResponse, status_code=201)
async def start_study_session(
    assignment_id: int,
    student_id: int = Query(..., description="Student ID"),
    db: AsyncSession = Depends(get_database)
):
    """Start a new study session for an assignment"""
    session_crud = StudySessionCRUD(db)
    
    try:
        session_data = StudySessionStart(
            session_notes=None
        )
        
        session = await session_crud.start_session(assignment_id, student_id, session_data)
        return session
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting study session: {str(e)}"
        )


@router.put("/{session_id}/progress", response_model=StudySessionResponse)
async def update_session_progress(
    session_id: int,
    session_update: StudySessionUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update study session progress"""
    session_crud = StudySessionCRUD(db)
    
    try:
        session = await session_crud.update_session(session_id, session_update)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study session not found"
            )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating session progress: {str(e)}"
        )


@router.post("/{session_id}/end")
async def end_study_session(
    session_id: int,
    session_end: StudySessionEnd,
    db: AsyncSession = Depends(get_database)
):
    """End a study session"""
    session_crud = StudySessionCRUD(db)
    
    try:
        session = await session_crud.end_session(session_id, session_end)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study session not found"
            )
        
        return APIResponse(
            message="Study session ended successfully",
            data={
                "session_id": session_id,
                "items_studied": session_end.items_studied,
                "status": "completed"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ending study session: {str(e)}"
        )


@router.get("/students/{student_id}", response_model=PaginatedResponse)
async def get_student_session_history(
    student_id: int,
    pagination: PaginationParams = Depends(),
    assignment_id: int = None,
    db: AsyncSession = Depends(get_database)
):
    """Get study session history for a student"""
    session_crud = StudySessionCRUD(db)
    
    try:
        sessions, total = await session_crud.get_student_sessions(
            student_id=student_id,
            assignment_id=assignment_id,
            pagination=pagination
        )
        
        return PaginatedResponse.create(sessions, total, pagination)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching session history: {str(e)}"
        )


@router.get("/{session_id}", response_model=StudySessionResponse)
async def get_session_details(
    session_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get details of a specific study session"""
    session_crud = StudySessionCRUD(db)
    
    session = await session_crud.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found"
        )
    
    return session
