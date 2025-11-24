# DEPRECATED: This file is kept for backward compatibility
# Please import schemas from their respective modules instead:
# - from app.schemas.course import CourseBase, CourseCreate, etc.
# - from app.schemas.lesson import LessonBase, LessonCreate, etc.
# - from app.schemas.deck import DeckBase, DeckCreate, etc.
# - from app.schemas.flashcard import FlashcardBase, FlashcardCreate, etc.
# - from app.schemas.common import PaginationParams, MessageResponse, etc.

# Re-export everything from __init__ for backward compatibility
from . import *

# Import PyObjectId which is used by schemas
from app.models.content import PyObjectId

__all__ = [
    # Course schemas
    "CourseBase", "CourseCreate", "CourseUpdate", "CourseResponse", "CourseFilter",
    
    # Lesson schemas
    "LessonBase", "LessonCreate", "LessonUpdate", "LessonResponse",
    
    # Deck schemas
    "DeckBase", "DeckCreate", "DeckUpdate", "DeckResponse", "DeckFilter",
    
    # Flashcard schemas
    "FlashcardBase", "FlashcardCreate", "FlashcardUpdate", "FlashcardResponse",
    
    # Common schemas
    "ReorderRequest", "PaginationParams", "PaginatedResponse",
    "MessageResponse", "ErrorResponse", "URLValidationResponse",
    
    # Model types
    "PyObjectId"
]
