from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database
from app.utils.crud import AssignmentCRUD, ProgressCRUD, StudySessionCRUD

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_database)
):
    """Get general analytics summary"""
    try:
        assignment_crud = AssignmentCRUD(db)
        progress_crud = ProgressCRUD(db)
        
        # Get basic stats
        total_assignments = await assignment_crud.count_all(db)
        
        return {
            "status": "success",
            "total_assignments": total_assignments,
            "total_students": 0,  # TODO: implement when user service is available
            "total_instructors": 0,  # TODO: implement when user service is available
            "completion_rate": 0.0,  # TODO: implement when progress tracking is complete
            "message": "Analytics summary data"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching analytics summary: {str(e)}",
            "total_assignments": 0,
            "total_students": 0,
            "total_instructors": 0,
            "completion_rate": 0.0
        }


@router.get("/instructors/{instructor_id}/dashboard")
async def get_instructor_dashboard(
    instructor_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get dashboard data for an instructor"""
    assignment_crud = AssignmentCRUD(db)
    progress_crud = ProgressCRUD(db)
    session_crud = StudySessionCRUD(db)
    
    try:
        # Get instructor's assignments overview
        assignments_stats = await assignment_crud.get_instructor_statistics(db, instructor_id)
        
        return {
            "instructor_id": instructor_id,
            "assignments": {
                "total": assignments_stats["total_assignments"],
                "pending": assignments_stats["pending_assignments"], 
                "in_progress": assignments_stats["in_progress_assignments"],
                "completed": assignments_stats["completed_assignments"],
                "completion_rate": assignments_stats["completion_rate"]
            },
            "summary": f"Managing {assignments_stats['total_assignments']} assignments with {assignments_stats['completion_rate']:.1f}% completion rate"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching instructor dashboard: {str(e)}"
        )


@router.get("/students/{student_id}/summary")
async def get_student_progress_summary(
    student_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get progress summary for a student"""
    progress_crud = ProgressCRUD(db)
    session_crud = StudySessionCRUD(db)
    
    try:
        # Get study session summary
        session_summary = await progress_crud.get_student_session_summary(db, student_id)
        
        return {
            "student_id": student_id,
            "study_activity": {
                "total_sessions": session_summary["total_sessions"],
                "total_study_time": session_summary["total_study_time"],
                "items_studied": session_summary["total_items_studied"],
                "average_session_duration": session_summary["average_session_duration"],
                "study_streak": session_summary["study_streak"]
            },
            "summary": f"Completed {session_summary['total_sessions']} study sessions with {session_summary['study_streak']} day streak"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching student summary: {str(e)}"
        )


@router.get("/assignments/{assignment_id}/statistics")
async def get_assignment_statistics(
    assignment_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get detailed statistics for an assignment"""
    assignment_crud = AssignmentCRUD(db)
    progress_crud = ProgressCRUD(db)
    session_crud = StudySessionCRUD(db)
    
    try:
        # Get assignment details
        assignment = await assignment_crud.get_assignment(assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        return {
            "assignment_id": assignment_id,
            "assignment_details": {
                "title": assignment.title,
                "content_type": assignment.content_type,
                "assigned_at": assignment.assigned_at,
                "due_date": assignment.due_date,
                "status": assignment.status
            },
            "summary": f"Assignment '{assignment.title}' - Status: {assignment.status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching assignment statistics: {str(e)}"
        )


@router.get("/learning-data")
async def get_learning_analytics(
    instructor_id: Optional[int] = Query(None),
    student_id: Optional[int] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_database)
):
    """Get learning analytics data"""
    assignment_crud = AssignmentCRUD(db)
    progress_crud = ProgressCRUD(db)
    session_crud = StudySessionCRUD(db)
    
    try:
        # Get analytics based on filters
        analytics_data = await session_crud.get_learning_analytics(
            db,
            instructor_id=instructor_id,
            student_id=student_id,
            days=days
        )
        
        return {
            "period": f"Last {days} days",
            "filters": {
                "instructor_id": instructor_id,
                "student_id": student_id
            },
            "metrics": {
                "total_assignments": analytics_data["total_assignments"],
                "completed_assignments": analytics_data["completed_assignments"],
                "completion_rate": analytics_data["completion_rate"],
                "total_sessions": analytics_data["total_sessions"],
                "total_study_time": analytics_data["total_study_time"],
                "average_study_time": analytics_data["average_study_time"],
                "engagement_score": analytics_data["engagement_score"]
            },
            "insights": analytics_data["insights"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching learning analytics: {str(e)}"
        )
