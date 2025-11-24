from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    """Custom ObjectId type for Pydantic v2"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if isinstance(v, ObjectId):
            return str(v)
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        field_schema.update(type="string", format="objectid")
        return field_schema

class Course(BaseModel):
    """Course model for MongoDB"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    instructor_id: int = Field(..., description="ID from Auth Service")
    instructor_name: Optional[str] = Field(None, description="Cached instructor name")
    
    # Content metadata
    total_lessons: int = Field(default=0, ge=0)
    estimated_duration: Optional[int] = Field(None, ge=0, description="Minutes")
    
    # Status and visibility
    is_active: bool = Field(default=True)
    is_published: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "title": "Python Fundamentals",
                "description": "Learn the basics of Python programming",
                "instructor_id": 1,
                "instructor_name": "John Teacher",
                "estimated_duration": 120,
                "is_published": True
            }
        }
    )

class Lesson(BaseModel):
    """Lesson model for MongoDB"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = Field(None, max_length=10000, description="Lesson content/description")
    
    # Course relationship
    course_id: PyObjectId = Field(..., description="Course ObjectId")
    instructor_id: Optional[int] = Field(None, description="Instructor ID")
    order: int = Field(..., ge=1, description="Lesson order in course")
    
    # Media URLs
    image_url: Optional[str] = Field(None, description="Lesson image URL")
    video_url: Optional[str] = Field(None, description="Lesson video URL")
    
    # URL validation status
    image_url_valid: Optional[bool] = Field(None)
    video_url_valid: Optional[bool] = Field(None)
    last_url_check: Optional[datetime] = None
    
    # Content metadata
    duration: Optional[int] = Field(None, ge=0, description="Lesson duration in minutes")
    
    # Status
    is_published: bool = Field(default=False, description="Whether lesson is published")
    is_active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @validator('image_url', 'video_url')
    def validate_urls(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "title": "Introduction to Variables",
                "content": "Learn about variables in Python programming",
                "course_id": "6507f1f77bcf86cd99439011",
                "order": 1,
                "image_url": "https://example.com/lesson1.jpg",
                "video_url": "https://youtube.com/watch?v=abc123",
                "duration": 15
            }
        }
    )

class Deck(BaseModel):
    """Flashcard deck model for MongoDB"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    instructor_id: int = Field(..., description="ID from Auth Service")
    instructor_name: Optional[str] = Field(None, description="Cached instructor name")
    
    # Content metadata
    total_flashcards: int = Field(default=0, ge=0)
    
    # Categories and tags
    category: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    
    # Status and visibility
    is_active: bool = Field(default=True)
    is_published: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return [tag.lower().strip() for tag in v if tag.strip()]
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "title": "Python Vocabulary",
                "description": "Essential Python programming terms",
                "instructor_id": 1,
                "instructor_name": "John Teacher",
                "category": "Programming",
                "tags": ["python", "vocabulary", "basics"],
                "is_published": True
            }
        }
    )

class Flashcard(BaseModel):
    """Flashcard model for MongoDB"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    front: str = Field(..., min_length=1, max_length=1000, description="Front side content")
    back: str = Field(..., min_length=1, max_length=2000, description="Back side content")
    
    # Deck relationship
    deck_id: PyObjectId = Field(..., description="Deck ObjectId")
    order: int = Field(..., ge=1, description="Flashcard order in deck")
    
    # Media URLs
    front_image_url: Optional[str] = Field(None, description="Front side image URL")
    back_image_url: Optional[str] = Field(None, description="Back side image URL")
    
    # URL validation status
    front_image_valid: Optional[bool] = Field(None)
    back_image_valid: Optional[bool] = Field(None)
    last_url_check: Optional[datetime] = None
    
    # Learning metadata
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    
    # NEW VOCABULARY FIELDS (Optional)
    wordclass: Optional[str] = Field(None, max_length=50, description="Word class (noun, verb, adjective, etc.)")
    definition: Optional[str] = Field(None, max_length=2000, description="Detailed definition of the word/concept")
    example: Optional[str] = Field(None, max_length=1000, description="Usage example or sentence")
    
    # Status
    is_active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @validator('front_image_url', 'back_image_url')
    def validate_image_urls(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "front": "What is a variable in Python?",
                "back": "A variable is a name that refers to a value stored in memory",
                "deck_id": "6507f1f77bcf86cd99439012",
                "order": 1,
                "front_image_url": "https://example.com/variable-front.jpg",
                "difficulty": "easy"
            }
        }
    )
