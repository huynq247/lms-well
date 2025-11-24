"""
CRUD modules for content service

This package contains separate CRUD classes for each content type,
providing better organization and maintainability compared to the
monolithic crud.py file.
"""

from .course_crud import CourseCRUD
from .lesson_crud import LessonCRUD
from .deck_crud import DeckCRUD
from .flashcard_crud import FlashcardCRUD

__all__ = [
    "CourseCRUD",
    "LessonCRUD", 
    "DeckCRUD",
    "FlashcardCRUD"
]
