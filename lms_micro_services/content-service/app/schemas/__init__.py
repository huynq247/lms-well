# Import all schemas from separate modules
from .course import (
    CourseBase, CourseCreate, CourseUpdate, CourseResponse, CourseFilter
)
from .lesson import (
    LessonBase, LessonCreate, LessonUpdate, LessonResponse
)
from .deck import (
    DeckBase, DeckCreate, DeckUpdate, DeckResponse, DeckFilter
)
from .flashcard import (
    FlashcardBase, FlashcardCreate, FlashcardUpdate, FlashcardResponse
)
from .common import (
    ReorderRequest, PaginationParams, PaginatedResponse,
    MessageResponse, ErrorResponse, URLValidationResponse
)

# Re-export all schemas for backward compatibility
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
    "MessageResponse", "ErrorResponse", "URLValidationResponse"
]
