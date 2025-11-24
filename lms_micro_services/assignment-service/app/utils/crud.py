from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import json

from app.models.assignment import Assignment, Progress, StudySession
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, ProgressUpdate, 
    StudySessionStart, StudySessionUpdate, StudySessionEnd,
    AssignmentFilter, PaginationParams, ContentType, AssignmentStatus,
    AssignmentResponse
)

logger = logging.getLogger(__name__)


def assignment_to_response(assignment: Assignment) -> AssignmentResponse:
    """Convert Assignment model to AssignmentResponse with proper JSON parsing"""
    # Parse supporting decks JSON fields
    supporting_decks = None
    supporting_deck_titles = None
    
    if assignment.supporting_decks:
        try:
            supporting_decks = json.loads(assignment.supporting_decks)
            # Handle double-encoded JSON strings
            if isinstance(supporting_decks, str):
                supporting_decks = json.loads(supporting_decks)
        except (json.JSONDecodeError, TypeError):
            supporting_decks = None
    
    if assignment.supporting_deck_titles:
        try:
            supporting_deck_titles = json.loads(assignment.supporting_deck_titles)
            # Handle double-encoded JSON strings
            if isinstance(supporting_deck_titles, str):
                supporting_deck_titles = json.loads(supporting_deck_titles)
        except (json.JSONDecodeError, TypeError):
            supporting_deck_titles = None
    
    # Create response object
    return AssignmentResponse(
        id=assignment.id,
        instructor_id=assignment.instructor_id,
        student_id=assignment.student_id,
        content_type=ContentType(assignment.content_type),
        content_id=assignment.content_id,
        content_title=assignment.content_title,
        title=assignment.title,
        description=assignment.description,
        instructions=assignment.instructions,
        status=AssignmentStatus(assignment.status),
        assigned_at=assignment.assigned_at,
        due_date=assignment.due_date,
        completed_at=assignment.completed_at,
        is_active=assignment.is_active,
        supporting_decks=supporting_decks,
        supporting_deck_titles=supporting_deck_titles,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at
    )


class AssignmentCRUD:
    """CRUD operations for Assignment model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_assignment(self, assignment_data: AssignmentCreate) -> Assignment:
        """Create a new assignment"""
        import json
        
        # Convert supporting decks to JSON strings if provided
        supporting_decks_json = None
        supporting_deck_titles_json = None
        
        if assignment_data.supporting_decks:
            supporting_decks_json = json.dumps(assignment_data.supporting_decks)
        
        if assignment_data.supporting_deck_titles:
            supporting_deck_titles_json = json.dumps(assignment_data.supporting_deck_titles)
        
        # Create assignment
        db_assignment = Assignment(
            instructor_id=assignment_data.instructor_id,
            student_id=assignment_data.student_id,
            content_type=assignment_data.content_type.value,
            content_id=assignment_data.content_id,
            content_title=assignment_data.content_title,
            title=assignment_data.title,
            description=assignment_data.description,
            instructions=assignment_data.instructions,
            due_date=assignment_data.due_date,
            supporting_decks=supporting_decks_json,
            supporting_deck_titles=supporting_deck_titles_json
        )
        
        self.db.add(db_assignment)
        await self.db.flush()
        
        # Create initial progress record
        progress = Progress(
            assignment_id=db_assignment.id,
            total_items=0,  # Will be updated when content is analyzed
            completed_items=0,
            completion_percentage=0.0
        )
        
        self.db.add(progress)
        await self.db.commit()
        await self.db.refresh(db_assignment)
        
        return db_assignment
    
    async def get_assignment(self, assignment_id: int) -> Optional[Assignment]:
        """Get assignment by ID"""
        stmt = select(Assignment).where(Assignment.id == assignment_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_assignments(
        self, 
        filters: AssignmentFilter, 
        pagination: PaginationParams
    ) -> tuple[List[Assignment], int]:
        """Get assignments with filters and pagination - SIMPLIFIED VERSION"""
        logger.info(f"🔍 Getting assignments with pagination: offset={pagination.offset}, size={pagination.size}")
        
        try:
            # Simple query without relationships to avoid lazy loading issues
            stmt = select(Assignment).where(Assignment.is_active == True)
            
            # Apply only basic filters to avoid complexity
            if filters.student_id:
                stmt = stmt.where(Assignment.student_id == filters.student_id)
            
            if filters.instructor_id:
                stmt = stmt.where(Assignment.instructor_id == filters.instructor_id)
            
            # Order and paginate
            stmt = stmt.order_by(Assignment.created_at.desc()).offset(pagination.offset).limit(pagination.size)
            
            # Execute query - explicitly avoid loading relationships
            result = await self.db.execute(stmt)
            assignments = result.scalars().all()
            
            # Convert to list immediately to avoid lazy loading
            assignment_list = []
            for assignment in assignments:
                # Access all fields to trigger immediate loading, avoiding relationships
                assignment_dict = {
                    'id': assignment.id,
                    'instructor_id': assignment.instructor_id,
                    'student_id': assignment.student_id,
                    'content_type': assignment.content_type,
                    'content_id': assignment.content_id,
                    'content_title': assignment.content_title,
                    'title': assignment.title,
                    'description': assignment.description,
                    'instructions': assignment.instructions,
                    'assigned_at': assignment.assigned_at,
                    'due_date': assignment.due_date,
                    'completed_at': assignment.completed_at,
                    'status': assignment.status,
                    'is_active': assignment.is_active,
                    'created_at': assignment.created_at,
                    'updated_at': assignment.updated_at
                }
                assignment_list.append(assignment)
            
            total = len(assignment_list)
            
            logger.info(f"✅ Found {len(assignment_list)} assignments")
            return assignment_list, total
            
        except Exception as e:
            logger.error(f"❌ Error getting assignments: {e}")
            raise
    
    # Alias for backward compatibility
    async def list_assignments(
        self, 
        pagination: PaginationParams,
        assignment_filter: AssignmentFilter
    ) -> tuple[List[Assignment], int]:
        """Alias for get_assignments method"""
        return await self.get_assignments(assignment_filter, pagination)
    
    async def update_assignment(
        self, 
        assignment_id: int, 
        assignment_data: AssignmentUpdate
    ) -> Optional[Assignment]:
        """Update assignment"""
        # Get assignment
        assignment = await self.get_assignment(assignment_id)
        if not assignment:
            return None
        
        # Update fields
        update_data = assignment_data.model_dump(exclude_unset=True)
        if update_data:
            if 'status' in update_data:
                update_data['status'] = update_data['status'].value
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            stmt = update(Assignment).where(Assignment.id == assignment_id).values(**update_data)
            await self.db.execute(stmt)
            await self.db.commit()
            await self.db.refresh(assignment)
        
        return assignment
    
    async def delete_assignment(self, assignment_id: int) -> bool:
        """Soft delete assignment"""
        stmt = update(Assignment).where(Assignment.id == assignment_id).values(
            is_active=False,
            updated_at=datetime.utcnow()
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_student_assignments(self, student_id: int, status_filter: Optional[str] = None) -> List[Assignment]:
        """Get all assignments for a student"""
        stmt = select(Assignment).where(
            and_(Assignment.student_id == student_id, Assignment.is_active == True)
        )
        
        if status_filter:
            stmt = stmt.where(Assignment.status == status_filter.value)
            
        stmt = stmt.order_by(Assignment.assigned_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_recent_assignments(self, limit: int = 50) -> List[Assignment]:
        """Get recent assignments"""
        stmt = select(Assignment).where(Assignment.is_active == True).order_by(
            Assignment.assigned_at.desc()
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_instructor_assignments(self, instructor_id: int) -> List[Assignment]:
        """Get all assignments for an instructor"""
        stmt = select(Assignment).where(
            and_(Assignment.instructor_id == instructor_id, Assignment.is_active == True)
        ).order_by(Assignment.assigned_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_assignments_by_instructor(
        self, 
        instructor_id: int, 
        pagination: PaginationParams
    ) -> tuple[List[Assignment], int]:
        """Get assignments by instructor"""
        filters = AssignmentFilter(instructor_id=instructor_id)
        return await self.get_assignments(filters, pagination)
    
    async def get_assignments_by_student(
        self, 
        student_id: int, 
        pagination: PaginationParams
    ) -> tuple[List[Assignment], int]:
        """Get assignments by student"""
        filters = AssignmentFilter(student_id=student_id)
        return await self.get_assignments(filters, pagination)
    
    async def count_all(self, db: AsyncSession) -> int:
        """Count total number of assignments"""
        try:
            stmt = select(func.count(Assignment.id)).where(Assignment.is_active == True)
            result = await db.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error counting assignments: {e}")
            return 0


class ProgressCRUD:
    """CRUD operations for Progress model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_progress(self, assignment_id: int) -> Optional[Progress]:
        """Get progress by assignment ID"""
        stmt = select(Progress).where(Progress.assignment_id == assignment_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_progress(
        self, 
        assignment_id: int, 
        progress_data: ProgressUpdate
    ) -> Optional[Progress]:
        """Update progress"""
        # Get or create progress
        progress = await self.get_progress(assignment_id)
        if not progress:
            # Create new progress record
            progress = Progress(assignment_id=assignment_id)
            self.db.add(progress)
            await self.db.flush()
        
        # Update fields
        update_data = progress_data.model_dump(exclude_unset=True)
        if update_data:
            # Calculate completion percentage
            if 'completed_items' in update_data or 'total_items' in update_data:
                total = update_data.get('total_items', progress.total_items)
                completed = update_data.get('completed_items', progress.completed_items)
                if total > 0:
                    update_data['completion_percentage'] = (completed / total) * 100.0
                else:
                    update_data['completion_percentage'] = 0.0
            
            # Set last accessed
            update_data['last_accessed'] = datetime.utcnow()
            update_data['updated_at'] = datetime.utcnow()
            
            # Set started_at if not set
            if not progress.started_at:
                update_data['started_at'] = datetime.utcnow()
            
            stmt = update(Progress).where(Progress.assignment_id == assignment_id).values(**update_data)
            await self.db.execute(stmt)
            await self.db.commit()
            await self.db.refresh(progress)
        
        return progress
    
    async def mark_assignment_complete(self, assignment_id: int) -> tuple[Optional[Assignment], Optional[Progress]]:
        """Mark assignment as completed"""
        # Update assignment status
        assignment_stmt = update(Assignment).where(Assignment.id == assignment_id).values(
            status='completed',
            completed_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await self.db.execute(assignment_stmt)
        
        # Update progress to 100%
        progress_stmt = update(Progress).where(Progress.assignment_id == assignment_id).values(
            completion_percentage=100.0,
            completed_items=Progress.total_items,
            last_accessed=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await self.db.execute(progress_stmt)
        
        await self.db.commit()
        
        # Return updated records
        assignment = await AssignmentCRUD(self.db).get_assignment(assignment_id)
        progress = await self.get_progress(assignment_id)
        
        return assignment, progress
    
    async def get_student_progress_summary(self, student_id: int) -> Dict[str, Any]:
        """Get overall progress summary for a student"""
        # Get all assignments for student
        stmt = select(Assignment).where(
            and_(Assignment.student_id == student_id, Assignment.is_active == True)
        )
        result = await self.db.execute(stmt)
        assignments = result.scalars().all()
        
        if not assignments:
            return {
                'student_id': student_id,
                'total_assignments': 0,
                'completed_assignments': 0,
                'in_progress_assignments': 0,
                'total_study_time_minutes': 0,
                'completion_rate': 0.0
            }
        
        # Calculate statistics
        total_assignments = len(assignments)
        completed_assignments = len([a for a in assignments if a.status == 'completed'])
        in_progress_assignments = len([a for a in assignments if a.status == 'in_progress'])
        
        # Get total study time
        study_time_stmt = select(func.sum(StudySession.duration_minutes)).where(
            StudySession.student_id == student_id
        )
        study_time_result = await self.db.execute(study_time_stmt)
        total_study_time = study_time_result.scalar() or 0
        
        completion_rate = (completed_assignments / total_assignments) * 100.0 if total_assignments > 0 else 0.0
        
        return {
            'student_id': student_id,
            'total_assignments': total_assignments,
            'completed_assignments': completed_assignments,
            'in_progress_assignments': in_progress_assignments,
            'total_study_time_minutes': total_study_time,
            'completion_rate': completion_rate
        }


class StudySessionCRUD:
    """CRUD operations for StudySession model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def start_session(
        self, 
        assignment_id: int, 
        student_id: int, 
        session_data: StudySessionStart
    ) -> StudySession:
        """Start a new study session"""
        # End any active sessions for this assignment
        await self._end_active_sessions(assignment_id, student_id)
        
        # Create new session
        session = StudySession(
            assignment_id=assignment_id,
            student_id=student_id,
            session_notes=session_data.session_notes,
            is_active=True
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def update_session(
        self, 
        session_id: int, 
        session_data: StudySessionUpdate
    ) -> Optional[StudySession]:
        """Update study session progress"""
        session = await self.get_session(session_id)
        if not session or not session.is_active:
            return None
        
        # Update fields
        update_data = session_data.model_dump(exclude_unset=True)
        if update_data:
            # Calculate session progress
            if 'items_completed' in update_data and 'items_studied' in update_data:
                items_studied = update_data.get('items_studied', session.items_studied)
                items_completed = update_data.get('items_completed', session.items_completed)
                if items_studied > 0:
                    update_data['session_progress'] = (items_completed / items_studied) * 100.0
            
            update_data['updated_at'] = datetime.utcnow()
            
            stmt = update(StudySession).where(StudySession.id == session_id).values(**update_data)
            await self.db.execute(stmt)
            await self.db.commit()
            await self.db.refresh(session)
        
        return session
    
    async def end_session(
        self, 
        session_id: int, 
        session_data: StudySessionEnd
    ) -> Optional[StudySession]:
        """End study session"""
        session = await self.get_session(session_id)
        if not session or not session.is_active:
            return None
        
        # Calculate duration  
        ended_at = datetime.utcnow()
        
        # Handle timezone-aware vs naive datetime
        started_at = session.started_at
        if hasattr(started_at, 'tzinfo') and started_at.tzinfo is not None:
            # If started_at has timezone, make ended_at timezone-aware too
            from datetime import timezone
            ended_at = ended_at.replace(tzinfo=timezone.utc)
        
        duration_minutes = int((ended_at - started_at).total_seconds() / 60)
        
        # Update session
        update_data = {
            'ended_at': ended_at,
            'duration_minutes': duration_minutes,
            'is_active': False,
            'updated_at': ended_at
        }
        
        # Add optional fields
        if hasattr(session_data, 'items_studied') and session_data.items_studied:
            update_data['items_studied'] = session_data.items_studied
        if hasattr(session_data, 'session_notes') and session_data.session_notes:
            update_data['session_notes'] = session_data.session_notes
        if hasattr(session_data, 'items_details') and session_data.items_details:
            update_data['items_details'] = session_data.items_details
        
        stmt = update(StudySession).where(StudySession.id == session_id).values(**update_data)
        await self.db.execute(stmt)
        
        # Update progress table with session count and study time
        await self._update_progress_from_session(session.assignment_id, duration_minutes)
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def get_session(self, session_id: int) -> Optional[StudySession]:
        """Get session by ID"""
        stmt = select(StudySession).where(StudySession.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_student_sessions(
        self, 
        student_id: int, 
        pagination: PaginationParams
    ) -> tuple[List[StudySession], int]:
        """Get study sessions for a student"""
        # Count total
        count_stmt = select(func.count()).where(StudySession.student_id == student_id)
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()
        
        # Get sessions
        stmt = select(StudySession).where(StudySession.student_id == student_id).order_by(
            StudySession.created_at.desc()
        ).offset(pagination.offset).limit(pagination.size)
        
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        
        return list(sessions), total
    
    async def _end_active_sessions(self, assignment_id: int, student_id: int):
        """End any active sessions for assignment"""
        stmt = update(StudySession).where(
            and_(
                StudySession.assignment_id == assignment_id,
                StudySession.student_id == student_id,
                StudySession.is_active == True
            )
        ).values(
            is_active=False,
            ended_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await self.db.execute(stmt)
    
    async def _update_progress_from_session(self, assignment_id: int, duration_minutes: int):
        """Update progress table with session data"""
        # Increment session count and study time
        stmt = update(Progress).where(Progress.assignment_id == assignment_id).values(
            sessions_count=Progress.sessions_count + 1,
            total_study_time_minutes=Progress.total_study_time_minutes + duration_minutes,
            updated_at=datetime.utcnow()
        )
        await self.db.execute(stmt)


# Analytics Extensions for CRUD Classes
class AnalyticsExtension:
    """Extension methods for analytics across all CRUD classes"""
    
    @staticmethod
    async def get_instructor_statistics(db: AsyncSession, instructor_id: int) -> Dict[str, Any]:
        """Get instructor assignment statistics"""
        # Count assignments by status
        total_stmt = select(func.count(Assignment.id)).where(Assignment.instructor_id == instructor_id)
        pending_stmt = select(func.count(Assignment.id)).where(
            and_(Assignment.instructor_id == instructor_id, Assignment.status == "pending")
        )
        in_progress_stmt = select(func.count(Assignment.id)).where(
            and_(Assignment.instructor_id == instructor_id, Assignment.status == "in_progress")
        )
        completed_stmt = select(func.count(Assignment.id)).where(
            and_(Assignment.instructor_id == instructor_id, Assignment.status == "completed")
        )
        
        total = (await db.execute(total_stmt)).scalar() or 0
        pending = (await db.execute(pending_stmt)).scalar() or 0
        in_progress = (await db.execute(in_progress_stmt)).scalar() or 0
        completed = (await db.execute(completed_stmt)).scalar() or 0
        
        completion_rate = (completed / total if total > 0 else 0) * 100
        
        return {
            "total_assignments": total,
            "pending_assignments": pending,
            "in_progress_assignments": in_progress,
            "completed_assignments": completed,
            "completion_rate": round(completion_rate, 2)
        }
    
    @staticmethod
    async def get_student_session_summary(db: AsyncSession, student_id: int) -> Dict[str, Any]:
        """Get study session summary for student"""
        stmt = select(
            func.count(StudySession.id),
            func.sum(StudySession.duration_minutes),
            func.sum(StudySession.items_studied),
            func.avg(StudySession.duration_minutes)
        ).where(StudySession.student_id == student_id)
        
        result = await db.execute(stmt)
        total_sessions, total_time, total_items, avg_duration = result.first() or (0, 0, 0, 0)
        
        # Calculate study streak (consecutive days with sessions)
        streak_stmt = select(func.date(StudySession.started_at)).where(
            StudySession.student_id == student_id
        ).distinct().order_by(func.date(StudySession.started_at).desc()).limit(30)
        
        dates_result = await db.execute(streak_stmt)
        session_dates = [row[0] for row in dates_result.fetchall()]
        
        study_streak = 0
        if session_dates:
            current_date = session_dates[0]
            for date in session_dates:
                if (current_date - date).days <= 1:
                    study_streak += 1
                    current_date = date
                else:
                    break
        
        return {
            "total_sessions": total_sessions or 0,
            "total_study_time": total_time or 0,
            "total_items_studied": total_items or 0,
            "average_session_duration": round(avg_duration or 0, 2),
            "study_streak": study_streak
        }
    
    @staticmethod
    async def get_learning_analytics(
        db: AsyncSession, 
        instructor_id: Optional[int] = None,
        student_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive learning analytics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Base query for assignments
        assignment_query = select(Assignment).where(Assignment.assigned_at >= cutoff_date)
        
        if instructor_id:
            assignment_query = assignment_query.where(Assignment.instructor_id == instructor_id)
        if student_id:
            assignment_query = assignment_query.where(Assignment.student_id == student_id)
        
        # Get assignments
        result = await db.execute(assignment_query)
        assignments = result.scalars().all()
        
        total_assignments = len(assignments)
        completed_assignments = len([a for a in assignments if a.status == "completed"])
        completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
        
        # Get session data
        session_query = select(
            func.count(StudySession.id),
            func.sum(StudySession.duration_minutes),
            func.avg(StudySession.duration_minutes)
        ).where(StudySession.started_at >= cutoff_date)
        
        if student_id:
            session_query = session_query.where(StudySession.student_id == student_id)
        elif instructor_id:
            session_query = session_query.join(Assignment).where(Assignment.instructor_id == instructor_id)
        
        session_result = await db.execute(session_query)
        total_sessions, total_study_time, avg_study_time = session_result.first() or (0, 0, 0)
        
        # Calculate engagement score (0-100)
        engagement_score = min(100, (completion_rate + (avg_study_time or 0) / 60 * 10))
        
        return {
            "period_days": days,
            "total_assignments": total_assignments,
            "completed_assignments": completed_assignments,
            "completion_rate": round(completion_rate, 2),
            "total_sessions": total_sessions or 0,
            "total_study_time": total_study_time or 0,
            "average_study_time": round(avg_study_time or 0, 2),
            "engagement_score": round(engagement_score, 2),
            "insights": [
                f"Completion rate: {completion_rate:.1f}%",
                f"Total study time: {total_study_time or 0:.0f} minutes",
                f"Average session: {avg_study_time or 0:.1f} minutes",
                f"Engagement score: {engagement_score:.1f}/100"
            ]
        }


# Add analytics methods to existing CRUD classes
AssignmentCRUD.get_instructor_statistics = AnalyticsExtension.get_instructor_statistics
ProgressCRUD.get_student_session_summary = AnalyticsExtension.get_student_session_summary  
StudySessionCRUD.get_learning_analytics = AnalyticsExtension.get_learning_analytics
