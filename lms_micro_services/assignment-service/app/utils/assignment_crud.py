from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_, func, update, delete
from typing import List, Optional, Tuple
from datetime import datetime

from app.models.assignment import Assignment, Progress, StudySession, AssignmentStatus
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentFilter, PaginationParams
)


class AssignmentCRUD:
    """CRUD operations for assignments"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_assignment(self, assignment_data: AssignmentCreate, content_title: str) -> Assignment:
        """Create a new assignment"""
        
        # Create assignment
        assignment = Assignment(
            title=assignment_data.title,
            description=assignment_data.description,
            instructions=assignment_data.instructions,
            instructor_id=assignment_data.instructor_id,
            student_id=assignment_data.student_id,
            content_type=assignment_data.content_type,
            content_id=assignment_data.content_id,
            content_title=content_title,
            due_date=assignment_data.due_date,
            status=AssignmentStatus.PENDING
        )
        
        self.db.add(assignment)
        await self.db.flush()
        
        # Create initial progress record
        progress = Progress(
            assignment_id=assignment.id,
            total_items=0,  # Will be updated when content details are fetched
            completed_items=0,
            completion_percentage=0.0
        )
        
        self.db.add(progress)
        await self.db.commit()
        await self.db.refresh(assignment)
        
        return assignment
    
    async def get_assignment(self, assignment_id: int) -> Optional[Assignment]:
        """Get assignment by ID"""
        result = await self.db.execute(
            select(Assignment)
            .options(selectinload(Assignment.progress))
            .where(Assignment.id == assignment_id)
        )
        return result.scalar_one_or_none()
    
    async def list_assignments(
        self, 
        pagination: PaginationParams,
        assignment_filter: AssignmentFilter
    ) -> Tuple[List[Assignment], int]:
        """List assignments with filtering and pagination"""
        
        # Build base query
        query = select(Assignment).options(selectinload(Assignment.progress))
        
        # Apply filters
        conditions = []
        
        if assignment_filter.student_id:
            conditions.append(Assignment.student_id == assignment_filter.student_id)
        
        if assignment_filter.instructor_id:
            conditions.append(Assignment.instructor_id == assignment_filter.instructor_id)
        
        if assignment_filter.content_type:
            conditions.append(Assignment.content_type == assignment_filter.content_type)
        
        if assignment_filter.status:
            conditions.append(Assignment.status == assignment_filter.status)
        
        if assignment_filter.due_before:
            conditions.append(Assignment.due_date <= assignment_filter.due_before)
        
        if assignment_filter.due_after:
            conditions.append(Assignment.due_date >= assignment_filter.due_after)
        
        # Add active filter by default
        conditions.append(Assignment.is_active == True)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count(Assignment.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.size)
        query = query.order_by(Assignment.created_at.desc())
        
        # Execute query
        result = await self.db.execute(query)
        assignments = result.scalars().all()
        
        return assignments, total
    
    async def update_assignment(
        self, 
        assignment_id: int, 
        assignment_update: AssignmentUpdate
    ) -> Optional[Assignment]:
        """Update an assignment"""
        
        # Get existing assignment
        assignment = await self.get_assignment(assignment_id)
        if not assignment:
            return None
        
        # Update fields
        update_data = assignment_update.model_dump(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            
            await self.db.execute(
                update(Assignment)
                .where(Assignment.id == assignment_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            # Refresh assignment
            await self.db.refresh(assignment)
        
        return assignment
    
    async def delete_assignment(self, assignment_id: int) -> bool:
        """Soft delete an assignment"""
        
        result = await self.db.execute(
            update(Assignment)
            .where(Assignment.id == assignment_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        
        await self.db.commit()
        return result.rowcount > 0
    
    async def mark_assignment_complete(self, assignment_id: int) -> Optional[Assignment]:
        """Mark assignment as completed"""
        
        assignment = await self.get_assignment(assignment_id)
        if not assignment:
            return None
        
        await self.db.execute(
            update(Assignment)
            .where(Assignment.id == assignment_id)
            .values(
                status=AssignmentStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        
        await self.db.commit()
        await self.db.refresh(assignment)
        
        return assignment


class ProgressCRUD:
    """CRUD operations for progress tracking"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_progress(self, assignment_id: int) -> Optional[Progress]:
        """Get progress for an assignment"""
        result = await self.db.execute(
            select(Progress).where(Progress.assignment_id == assignment_id)
        )
        return result.scalar_one_or_none()
    
    async def update_progress(
        self, 
        assignment_id: int, 
        completed_items: int,
        total_items: int,
        progress_details: Optional[str] = None
    ) -> Optional[Progress]:
        """Update assignment progress"""
        
        completion_percentage = (completed_items / total_items * 100) if total_items > 0 else 0
        
        # Update or create progress
        progress = await self.get_progress(assignment_id)
        if progress:
            await self.db.execute(
                update(Progress)
                .where(Progress.assignment_id == assignment_id)
                .values(
                    completed_items=completed_items,
                    total_items=total_items,
                    completion_percentage=completion_percentage,
                    last_accessed=datetime.utcnow(),
                    progress_details=progress_details,
                    updated_at=datetime.utcnow()
                )
            )
        else:
            progress = Progress(
                assignment_id=assignment_id,
                completed_items=completed_items,
                total_items=total_items,
                completion_percentage=completion_percentage,
                last_accessed=datetime.utcnow(),
                progress_details=progress_details
            )
            self.db.add(progress)
        
        await self.db.commit()
        
        # If assignment is complete, update assignment status
        if completion_percentage >= 100:
            await self.db.execute(
                update(Assignment)
                .where(Assignment.id == assignment_id)
                .values(
                    status=AssignmentStatus.COMPLETED,
                    completed_at=datetime.utcnow()
                )
            )
            await self.db.commit()
        
        return await self.get_progress(assignment_id)


class StudySessionCRUD:
    """CRUD operations for study sessions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def start_session(
        self, 
        assignment_id: int, 
        student_id: int,
        session_notes: Optional[str] = None
    ) -> StudySession:
        """Start a new study session"""
        
        session = StudySession(
            assignment_id=assignment_id,
            student_id=student_id,
            session_notes=session_notes,
            started_at=datetime.utcnow()
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def end_session(
        self, 
        session_id: int,
        session_notes: Optional[str] = None,
        items_details: Optional[str] = None
    ) -> Optional[StudySession]:
        """End a study session"""
        
        session = await self.get_session(session_id)
        if not session or not session.is_active:
            return None
        
        ended_at = datetime.utcnow()
        duration_minutes = int((ended_at - session.started_at).total_seconds() / 60)
        
        await self.db.execute(
            update(StudySession)
            .where(StudySession.id == session_id)
            .values(
                ended_at=ended_at,
                duration_minutes=duration_minutes,
                is_active=False,
                session_notes=session_notes or session.session_notes,
                items_details=items_details,
                updated_at=datetime.utcnow()
            )
        )
        
        await self.db.commit()
        return await self.get_session(session_id)
    
    async def get_session(self, session_id: int) -> Optional[StudySession]:
        """Get study session by ID"""
        result = await self.db.execute(
            select(StudySession).where(StudySession.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def list_student_sessions(
        self, 
        student_id: int,
        pagination: PaginationParams
    ) -> Tuple[List[StudySession], int]:
        """List study sessions for a student"""
        
        # Count query
        count_result = await self.db.execute(
            select(func.count(StudySession.id))
            .where(StudySession.student_id == student_id)
        )
        total = count_result.scalar()
        
        # Data query
        result = await self.db.execute(
            select(StudySession)
            .where(StudySession.student_id == student_id)
            .order_by(StudySession.started_at.desc())
            .offset(pagination.offset)
            .limit(pagination.size)
        )
        
        sessions = result.scalars().all()
        return sessions, total
