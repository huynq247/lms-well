from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class ContentType(enum.Enum):
    """Types of content that can be assigned"""
    COURSE = "course"
    DECK = "deck"


class AssignmentStatus(enum.Enum):
    """Assignment status options"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Assignment(Base):
    """Assignment model"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    
    # Content reference
    content_type = Column(String(20), nullable=False)  # Changed from Enum to String
    content_id = Column(String(24), nullable=False)  # MongoDB ObjectId
    content_title = Column(String(200), nullable=False)
    
    # Supporting content (for course assignments with flashcard decks)
    supporting_decks = Column(Text, nullable=True)  # JSON string of deck IDs
    supporting_deck_titles = Column(Text, nullable=True)  # JSON string of deck titles
    
    # Assignment details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    
    # Timing
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(20), default="pending")  # Changed from Enum to String
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    progress = relationship("Progress", back_populates="assignment", uselist=False)
    study_sessions = relationship("StudySession", back_populates="assignment")


class Progress(Base):
    """Progress tracking model"""
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False, unique=True)
    
    # Progress metrics
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    
    # Study metrics
    total_study_time_minutes = Column(Integer, default=0)
    sessions_count = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    # Progress details (JSON-like text field for flexibility)
    progress_details = Column(Text, nullable=True)  # Store JSON string of detailed progress
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assignment = relationship("Assignment", back_populates="progress")


class StudySession(Base):
    """Study session tracking model"""
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, nullable=False, index=True)
    
    # Session timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Session progress
    items_studied = Column(Integer, default=0)
    items_completed = Column(Integer, default=0)
    session_progress = Column(Float, default=0.0)
    
    # Session details
    session_notes = Column(Text, nullable=True)
    items_details = Column(Text, nullable=True)  # JSON string of items studied
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assignment = relationship("Assignment", back_populates="study_sessions")
