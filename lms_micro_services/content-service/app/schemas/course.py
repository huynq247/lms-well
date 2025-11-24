from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Course Schemas
class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    estimated_duration: Optional[int] = Field(None, ge=0, description="Minutes")
    is_published: bool = Field(default=False)
    is_public: bool = Field(default=False, description="Whether course is publicly accessible")

class CourseCreate(CourseBase):
    instructor_id: int = Field(..., description="ID from Auth Service")

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    estimated_duration: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None

class CourseResponse(CourseBase):
    id: str = Field(..., description="Course ID")
    instructor_id: int
    instructor_name: Optional[str] = None
    total_lessons: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Search and Filter Schemas
class CourseFilter(BaseModel):
    instructor_id: Optional[int] = None
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None
    course_ids: Optional[list[str]] = None  # For filtering by specific course IDs
