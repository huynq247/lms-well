from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database
from app.schemas.assignment import ProgressUpdate, ProgressResponse
from app.schemas.common import APIResponse
from app.utils.crud import ProgressCRUD

router = APIRouter(prefix="/progress", tags=["progress"])


@router.put("/assignments/{assignment_id}", response_model=ProgressResponse)
async def update_progress(
    assignment_id: int,
    progress_update: ProgressUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update progress for an assignment"""
    progress_crud = ProgressCRUD(db)
    
    try:
        progress = await progress_crud.update_progress(assignment_id, progress_update)
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating progress: {str(e)}"
        )


@router.get("/assignments/{assignment_id}", response_model=ProgressResponse)
async def get_assignment_progress(
    assignment_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get progress for a specific assignment"""
    progress_crud = ProgressCRUD(db)
    
    progress = await progress_crud.get_progress_by_assignment(assignment_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this assignment"
        )
    
    return progress


@router.get("/students/{student_id}")
async def get_student_overall_progress(
    student_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get overall progress for a student across all assignments"""
    progress_crud = ProgressCRUD(db)
    
    try:
        progress_summary = await progress_crud.get_student_progress_summary(student_id)
        return {
            "student_id": student_id,
            "total_assignments": progress_summary["total_assignments"],
            "completed_assignments": progress_summary["completed_assignments"],
            "in_progress_assignments": progress_summary["in_progress_assignments"],
            "overall_completion_rate": progress_summary["overall_completion_rate"],
            "average_progress": progress_summary["average_progress"],
            "assignments": progress_summary["assignments"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching student progress: {str(e)}"
        )


@router.post("/assignments/{assignment_id}/complete")
async def mark_assignment_complete(
    assignment_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Mark an assignment as complete"""
    progress_crud = ProgressCRUD(db)
    
    try:
        success = await progress_crud.mark_assignment_complete(assignment_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        return APIResponse(
            message="Assignment marked as complete",
            data={"assignment_id": assignment_id, "status": "completed"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking assignment complete: {str(e)}"
        )
