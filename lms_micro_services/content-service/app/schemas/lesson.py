from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

# Lesson Schemas
class LessonBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = Field(None, max_length=10000)
    order: int = Field(..., ge=1, description="Lesson order in course")
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = Field(None, ge=0, description="Minutes")
    is_published: Optional[bool] = Field(default=False, description="Whether lesson is published")

    @validator('image_url', 'video_url')
    def validate_urls(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class LessonCreate(LessonBase):
    course_id: str = Field(..., description="Course ID")
    instructor_id: Optional[int] = Field(None, description="Instructor ID")

class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, max_length=10000)
    order: Optional[int] = Field(None, ge=1)
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None

    @validator('image_url', 'video_url')
    def validate_urls(cls, v):
        if v and not v.startswith(('http://', 'https://', '')):
            raise ValueError('URL must start with http:// or https://')
        return v

class LessonResponse(LessonBase):
    id: str = Field(..., description="Lesson ID")
    course_id: str
    instructor_id: Optional[int] = None
    image_url_valid: Optional[bool] = None
    video_url_valid: Optional[bool] = None
    last_url_check: Optional[datetime] = None
    is_published: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
