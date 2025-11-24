from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# Deck Schemas
class DeckBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    is_published: bool = Field(default=False)
    is_active: bool = Field(default=True)

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

# Search and Filter Schemas
class DeckFilter(BaseModel):
    instructor_id: Optional[int] = None
    lesson_id: Optional[str] = None
    course_id: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None
    deck_ids: Optional[list[str]] = None  # For filtering by specific deck IDs
    include_public: Optional[bool] = None  # For students to see public + assigned decks
