from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

# Flashcard Schemas
class FlashcardBase(BaseModel):
    front: str = Field(..., min_length=1, max_length=1000)
    back: str = Field(..., min_length=1, max_length=2000)
    order: int = Field(..., ge=1, description="Flashcard order in deck")
    front_image_url: Optional[str] = None
    back_image_url: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    
    # VOCABULARY FIELDS (Optional)
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
    
    # VOCABULARY FIELDS (Optional for updates)
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
