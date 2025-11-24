from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    """Content type enumeration"""
    COURSE = "course"
    DECK = "deck"


class AssignmentStatus(str, Enum):
    """Assignment status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


# Assignment Schemas
class AssignmentBase(BaseModel):
    """Base assignment schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    instructions: Optional[str] = Field(None, max_length=2000)
    content_type: ContentType
    content_id: str = Field(..., description="MongoDB ObjectId of course or deck")
    content_title: str = Field(..., max_length=200)
    due_date: Optional[datetime] = None
    supporting_decks: Optional[List[str]] = Field(None, description="Supporting deck IDs for course assignments")
    supporting_deck_titles: Optional[List[str]] = Field(None, description="Supporting deck titles for display")


class AssignmentCreate(AssignmentBase):
    """Schema for creating assignments"""
    student_id: int = Field(..., gt=0)
    instructor_id: int = Field(..., gt=0)
    # Course validation will be handled in API layer


class AssignmentUpdate(BaseModel):
    """Schema for updating assignments"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    instructions: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    status: Optional[AssignmentStatus] = None
    is_active: Optional[bool] = None


class AssignmentResponse(AssignmentBase):
    """Schema for assignment responses"""
    id: int
    instructor_id: int
    instructor_name: Optional[str] = None
    student_id: int
    student_name: Optional[str] = None
    status: AssignmentStatus
    assigned_at: datetime
    completed_at: Optional[datetime] = None
    is_active: bool
    # Course progress fields
    course_progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    total_lessons: Optional[int] = Field(None, ge=0)
    completed_lessons: Optional[int] = Field(None, ge=0)
    
    # Supporting content for display
    supporting_decks: Optional[List[str]] = None
    supporting_deck_titles: Optional[List[str]] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Progress Schemas
class ProgressBase(BaseModel):
    """Base progress schema"""
    total_items: int = Field(0, ge=0)
    completed_items: int = Field(0, ge=0)
    completion_percentage: float = Field(0.0, ge=0.0, le=100.0)


class ProgressUpdate(ProgressBase):
    """Schema for updating progress"""
    progress_details: Optional[str] = None
    items_studied: Optional[int] = Field(None, ge=0)


class ProgressResponse(ProgressBase):
    """Schema for progress responses"""
    id: int
    assignment_id: int
    total_study_time_minutes: int
    sessions_count: int
    started_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    progress_details: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Study Session Schemas
class StudySessionCreate(BaseModel):
    """Schema for creating a study session"""
    assignment_id: int = Field(..., gt=0)
    student_id: int = Field(..., gt=0)
    session_notes: Optional[str] = Field(None, max_length=500)


class StudySessionStart(BaseModel):
    """Schema for starting a study session"""
    session_notes: Optional[str] = Field(None, max_length=500)


class StudySessionUpdate(BaseModel):
    """Schema for updating study session"""
    items_studied: Optional[int] = Field(None, ge=0)
    items_completed: Optional[int] = Field(None, ge=0)
    session_notes: Optional[str] = Field(None, max_length=500)
    items_details: Optional[str] = None


class StudySessionEnd(BaseModel):
    """Schema for ending study session"""
    items_studied: int = Field(0, ge=0, description="Number of items studied in this session")
    session_notes: Optional[str] = Field(None, max_length=500)
    items_details: Optional[str] = None


class StudySessionResponse(BaseModel):
    """Schema for study session responses"""
    id: int
    assignment_id: int
    student_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    items_studied: int
    items_completed: int
    session_progress: float
    session_notes: Optional[str] = None
    items_details: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Analytics Schemas
class CompletionStatistics(BaseModel):
    """Completion statistics schema"""
    total_assignments: int
    completed_assignments: int
    in_progress_assignments: int
    overdue_assignments: int
    completion_rate: float
    average_completion_time_days: Optional[float] = None


class StudentProgressSummary(BaseModel):
    """Student progress summary schema"""
    student_id: int
    total_assignments: int
    completed_assignments: int
    in_progress_assignments: int
    total_study_time_minutes: int
    average_session_duration_minutes: Optional[float] = None
    completion_rate: float
    recent_activity: List[dict] = []


class InstructorDashboard(BaseModel):
    """Instructor dashboard schema"""
    instructor_id: int
    total_assignments: int
    active_students: int
    completion_statistics: CompletionStatistics
    recent_submissions: List[dict] = []
    top_performers: List[dict] = []


# Filter and Pagination Schemas
class AssignmentFilter(BaseModel):
    """Assignment filtering schema"""
    student_id: Optional[int] = None
    instructor_id: Optional[int] = None
    content_type: Optional[ContentType] = None
    status: Optional[AssignmentStatus] = None
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    items: List[dict] = []
    total: int = 0
    page: int = 1
    size: int = 20
    pages: int = 0
    
    @classmethod
    def create(cls, items: List, total: int, pagination: PaginationParams):
        pages = (total + pagination.size - 1) // pagination.size
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=pages
        )


# Utility Schemas
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
