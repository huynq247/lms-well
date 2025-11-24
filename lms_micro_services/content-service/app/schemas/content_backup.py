from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.content import PyObjectId

# Course Schemas
class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    estimated_duration: Optional[int] = Field(None, ge=0, description="Minutes")
    is_published: bool = Field(default=False)

class CourseCreate(CourseBase):
    instructor_id: int = Field(..., description="ID from Auth Service")

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    estimated_duration: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None

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

# Lesson Schemas
class LessonBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = Field(None, max_length=10000)
    order: int = Field(..., ge=1, description="Lesson order in course")
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = Field(None, ge=0, description="Minutes")

    @validator('image_url', 'video_url')
    def validate_urls(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class LessonCreate(LessonBase):
    course_id: str = Field(..., description="Course ID")

class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, max_length=10000)
    order: Optional[int] = Field(None, ge=1)
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

    @validator('image_url', 'video_url')
    def validate_urls(cls, v):
        if v and not v.startswith(('http://', 'https://', '')):
            raise ValueError('URL must start with http:// or https://')
        return v

class LessonResponse(LessonBase):
    id: str = Field(..., description="Lesson ID")
    course_id: str
    image_url_valid: Optional[bool] = None
    video_url_valid: Optional[bool] = None
    last_url_check: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Deck Schemas
class DeckBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    is_published: bool = Field(default=False)

    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return [tag.lower().strip() for tag in v if tag.strip()]

class DeckCreate(DeckBase):
    instructor_id: int = Field(..., description="ID from Auth Service")

class DeckUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None

    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
            return [tag.lower().strip() for tag in v if tag.strip()]
        return v

class DeckResponse(DeckBase):
    id: str = Field(..., description="Deck ID")
    instructor_id: int
    instructor_name: Optional[str] = None
    total_flashcards: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Flashcard Schemas
class FlashcardBase(BaseModel):
    front: str = Field(..., min_length=1, max_length=1000)
    back: str = Field(..., min_length=1, max_length=2000)
    order: int = Field(..., ge=1, description="Flashcard order in deck")
    front_image_url: Optional[str] = None
    back_image_url: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    
    # NEW VOCABULARY FIELDS (Optional)
    wordclass: Optional[str] = Field(None, max_length=50, description="Word class (noun, verb, adjective, etc.)")
    definition: Optional[str] = Field(None, max_length=2000, description="Detailed definition of the word/concept")
    example: Optional[str] = Field(None, max_length=1000, description="Usage example or sentence")

    @validator('front_image_url', 'back_image_url')
    def validate_image_urls(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class FlashcardCreate(FlashcardBase):
    deck_id: str = Field(..., description="Deck ID")

class FlashcardUpdate(BaseModel):
    front: Optional[str] = Field(None, min_length=1, max_length=1000)
    back: Optional[str] = Field(None, min_length=1, max_length=2000)
    order: Optional[int] = Field(None, ge=1)
    front_image_url: Optional[str] = None
    back_image_url: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    is_active: Optional[bool] = None
    
    # NEW VOCABULARY FIELDS (Optional for updates)
    wordclass: Optional[str] = Field(None, max_length=50, description="Word class (noun, verb, adjective, etc.)")
    definition: Optional[str] = Field(None, max_length=2000, description="Detailed definition of the word/concept")
    example: Optional[str] = Field(None, max_length=1000, description="Usage example or sentence")

    @validator('front_image_url', 'back_image_url')
    def validate_image_urls(cls, v):
        if v and not v.startswith(('http://', 'https://', '')):
            raise ValueError('URL must start with http:// or https://')
        return v

class FlashcardResponse(FlashcardBase):
    id: str = Field(..., description="Flashcard ID")
    deck_id: str
    front_image_valid: Optional[bool] = None
    back_image_valid: Optional[bool] = None
    last_url_check: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Reorder Schemas
class ReorderRequest(BaseModel):
    items: List[dict] = Field(..., description="List of {id, order} items")

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Items list cannot be empty')
        
        orders = [item.get('order') for item in v]
        if len(set(orders)) != len(orders):
            raise ValueError('All order values must be unique')
        
        for item in v:
            if 'id' not in item or 'order' not in item:
                raise ValueError('Each item must have id and order fields')
            if not isinstance(item['order'], int) or item['order'] < 1:
                raise ValueError('Order must be a positive integer')
        
        return v

# Pagination Schemas
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = Field(None, max_length=100)

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

# Search and Filter Schemas
class CourseFilter(BaseModel):
    instructor_id: Optional[int] = None
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None

class DeckFilter(BaseModel):
    instructor_id: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None

# Response Schemas
class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

class URLValidationResponse(BaseModel):
    url: str
    is_valid: bool
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    error: Optional[str] = None
