from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from app.models.content import Course, Lesson, Deck, Flashcard, PyObjectId
from app.schemas.content import (
    CourseCreate, CourseUpdate, CourseFilter,
    LessonCreate, LessonUpdate,
    DeckCreate, DeckUpdate, DeckFilter,
    FlashcardCreate, FlashcardUpdate,
    PaginationParams
)
import logging

logger = logging.getLogger(__name__)

class CourseCRUD:
    """CRUD operations for courses"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.courses
    
    async def create_course(self, course_data: CourseCreate, instructor_name: Optional[str] = None) -> Course:
        """Create a new course"""
        course_dict = course_data.dict()
        course_dict["instructor_name"] = instructor_name
        course_dict["is_active"] = True  # Ensure is_active is set
        course_dict["is_published"] = False  # Default unpublished
        course_dict["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(course_dict)
        course_dict["_id"] = result.inserted_id
        
        return Course(**course_dict)
    
    async def get_course(self, course_id: str) -> Optional[Course]:
        """Get course by ID"""
        try:
            course_data = await self.collection.find_one({"_id": ObjectId(course_id)})
            if course_data:
                return Course(**course_data)
            return None
        except Exception as e:
            logger.error(f"Error getting course {course_id}: {e}")
            return None
    
    async def get_courses(
        self, 
        pagination: PaginationParams,
        filters: Optional[CourseFilter] = None
    ) -> Dict[str, Any]:
        """Get courses with pagination and filtering"""
        
        # Build query
        query = {}
        if filters:
            if filters.instructor_id is not None:
                query["instructor_id"] = filters.instructor_id
            if filters.is_published is not None:
                query["is_published"] = filters.is_published
            if filters.is_active is not None:
                query["is_active"] = filters.is_active
        
        # Add search if provided
        if pagination.search:
            query["$text"] = {"$search": pagination.search}
        
        # Calculate pagination
        skip = (pagination.page - 1) * pagination.size
        
        # Get total count and courses
        total = await self.collection.count_documents(query)
        
        cursor = self.collection.find(query).skip(skip).limit(pagination.size)
        courses_data = await cursor.to_list(length=pagination.size)
        
        courses = [Course(**course_data) for course_data in courses_data]
        
        return {
            "items": courses,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": (total + pagination.size - 1) // pagination.size,
            "has_next": pagination.page * pagination.size < total,
            "has_prev": pagination.page > 1
        }
    
    async def update_course(self, course_id: str, course_update: CourseUpdate) -> Optional[Course]:
        """Update course"""
        try:
            update_data = course_update.dict(exclude_unset=True)
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.collection.update_one(
                    {"_id": ObjectId(course_id)},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    return await self.get_course(course_id)
            
            return None
        except Exception as e:
            logger.error(f"Error updating course {course_id}: {e}")
            return None
    
    async def delete_course(self, course_id: str) -> bool:
        """Soft delete course (set is_active=False)"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(course_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deleting course {course_id}: {e}")
            return False
    
    async def get_courses_by_instructor(self, instructor_id: int) -> List[Course]:
        """Get all courses by instructor"""
        try:
            cursor = self.collection.find({"instructor_id": instructor_id, "is_active": True})
            courses_data = await cursor.to_list(length=None)
            return [Course(**course_data) for course_data in courses_data]
        except Exception as e:
            logger.error(f"Error getting courses for instructor {instructor_id}: {e}")
            return []
    
    async def update_course_lesson_count(self, course_id: str):
        """Update total_lessons count for a course"""
        try:
            lesson_count = await self.db.lessons.count_documents({
                "course_id": ObjectId(course_id),
                "is_active": True
            })
            
            await self.collection.update_one(
                {"_id": ObjectId(course_id)},
                {"$set": {"total_lessons": lesson_count, "updated_at": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Error updating lesson count for course {course_id}: {e}")

class LessonCRUD:
    """CRUD operations for lessons"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.lessons
    
    async def create_lesson(self, lesson_data: LessonCreate) -> Lesson:
        """Create a new lesson"""
        lesson_dict = lesson_data.dict()
        lesson_dict["course_id"] = ObjectId(lesson_dict["course_id"])
        lesson_dict["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(lesson_dict)
        lesson_dict["_id"] = result.inserted_id
        
        # Update course lesson count
        course_crud = CourseCRUD(self.db)
        await course_crud.update_course_lesson_count(lesson_data.course_id)
        
        return Lesson(**lesson_dict)
    
    async def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """Get lesson by ID"""
        try:
            lesson_data = await self.collection.find_one({"_id": ObjectId(lesson_id)})
            if lesson_data:
                return Lesson(**lesson_data)
            return None
        except Exception as e:
            logger.error(f"Error getting lesson {lesson_id}: {e}")
            return None
    
    async def get_lessons_by_course(self, course_id: str) -> List[Lesson]:
        """Get all lessons for a course, ordered by order field"""
        try:
            cursor = self.collection.find({
                "course_id": ObjectId(course_id),
                "is_active": True
            }).sort("order", 1)
            
            lessons_data = await cursor.to_list(length=None)
            return [Lesson(**lesson_data) for lesson_data in lessons_data]
        except Exception as e:
            logger.error(f"Error getting lessons for course {course_id}: {e}")
            return []
    
    async def update_lesson(self, lesson_id: str, lesson_update: LessonUpdate) -> Optional[Lesson]:
        """Update lesson"""
        try:
            update_data = lesson_update.dict(exclude_unset=True)
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.collection.update_one(
                    {"_id": ObjectId(lesson_id)},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    return await self.get_lesson(lesson_id)
            
            return None
        except Exception as e:
            logger.error(f"Error updating lesson {lesson_id}: {e}")
            return None
    
    async def delete_lesson(self, lesson_id: str) -> bool:
        """Soft delete lesson"""
        try:
            # Get lesson to find course_id for updating count
            lesson = await self.get_lesson(lesson_id)
            if not lesson:
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(lesson_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                # Update course lesson count
                course_crud = CourseCRUD(self.db)
                await course_crud.update_course_lesson_count(str(lesson.course_id))
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting lesson {lesson_id}: {e}")
            return False
    
    async def reorder_lessons(self, course_id: str, lesson_orders: List[Dict[str, Any]]) -> bool:
        """Reorder lessons in a course"""
        try:
            # Update each lesson's order
            for item in lesson_orders:
                await self.collection.update_one(
                    {"_id": ObjectId(item["id"]), "course_id": ObjectId(course_id)},
                    {"$set": {"order": item["order"], "updated_at": datetime.utcnow()}}
                )
            
            return True
        except Exception as e:
            logger.error(f"Error reordering lessons for course {course_id}: {e}")
            return False

class DeckCRUD:
    """CRUD operations for decks"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.decks
    
    async def create_deck(self, deck_data: DeckCreate, instructor_name: Optional[str] = None) -> Deck:
        """Create a new deck"""
        deck_dict = deck_data.dict()
        deck_dict["instructor_name"] = instructor_name
        deck_dict["is_active"] = True  # Ensure is_active is set
        deck_dict["is_published"] = False  # Default unpublished
        deck_dict["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(deck_dict)
        deck_dict["_id"] = result.inserted_id
        
        return Deck(**deck_dict)
    
    async def get_deck(self, deck_id: str) -> Optional[Deck]:
        """Get deck by ID"""
        try:
            deck_data = await self.collection.find_one({"_id": ObjectId(deck_id)})
            if deck_data:
                return Deck(**deck_data)
            return None
        except Exception as e:
            logger.error(f"Error getting deck {deck_id}: {e}")
            return None
    
    async def get_decks(
        self,
        pagination: PaginationParams,
        filters: Optional[DeckFilter] = None
    ) -> Dict[str, Any]:
        """Get decks with pagination and filtering"""
        
        # Build query
        query = {}
        if filters:
            if filters.instructor_id is not None:
                query["instructor_id"] = filters.instructor_id
            if filters.category:
                query["category"] = filters.category
            if filters.tags:
                query["tags"] = {"$in": filters.tags}
            if filters.is_published is not None:
                query["is_published"] = filters.is_published
            if filters.is_active is not None:
                query["is_active"] = filters.is_active
        
        # Add search if provided
        if pagination.search:
            query["$text"] = {"$search": pagination.search}
        
        # Calculate pagination
        skip = (pagination.page - 1) * pagination.size
        
        # Get total count and decks
        total = await self.collection.count_documents(query)
        
        cursor = self.collection.find(query).skip(skip).limit(pagination.size)
        decks_data = await cursor.to_list(length=pagination.size)
        
        decks = [Deck(**deck_data) for deck_data in decks_data]
        
        return {
            "items": decks,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": (total + pagination.size - 1) // pagination.size,
            "has_next": pagination.page * pagination.size < total,
            "has_prev": pagination.page > 1
        }
    
    async def update_deck(self, deck_id: str, deck_update: DeckUpdate) -> Optional[Deck]:
        """Update deck"""
        try:
            update_data = deck_update.dict(exclude_unset=True)
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.collection.update_one(
                    {"_id": ObjectId(deck_id)},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    return await self.get_deck(deck_id)
            
            return None
        except Exception as e:
            logger.error(f"Error updating deck {deck_id}: {e}")
            return None
    
    async def delete_deck(self, deck_id: str) -> bool:
        """Soft delete deck"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(deck_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deleting deck {deck_id}: {e}")
            return False
    
    async def get_decks_by_instructor(self, instructor_id: int) -> List[Deck]:
        """Get all decks by instructor"""
        try:
            cursor = self.collection.find({"instructor_id": instructor_id, "is_active": True})
            decks_data = await cursor.to_list(length=None)
            return [Deck(**deck_data) for deck_data in decks_data]
        except Exception as e:
            logger.error(f"Error getting decks for instructor {instructor_id}: {e}")
            return []
    
    async def update_deck_flashcard_count(self, deck_id: str):
        """Update total_flashcards count for a deck"""
        try:
            flashcard_count = await self.db.flashcards.count_documents({
                "deck_id": ObjectId(deck_id),
                "is_active": True
            })
            
            await self.collection.update_one(
                {"_id": ObjectId(deck_id)},
                {"$set": {"total_flashcards": flashcard_count, "updated_at": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Error updating flashcard count for deck {deck_id}: {e}")

class FlashcardCRUD:
    """CRUD operations for flashcards"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.flashcards
    
    async def create_flashcard(self, flashcard_data: FlashcardCreate) -> Flashcard:
        """Create a new flashcard"""
        flashcard_dict = flashcard_data.dict()
        flashcard_dict["deck_id"] = ObjectId(flashcard_dict["deck_id"])
        flashcard_dict["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(flashcard_dict)
        flashcard_dict["_id"] = result.inserted_id
        
        # Update deck flashcard count
        deck_crud = DeckCRUD(self.db)
        await deck_crud.update_deck_flashcard_count(flashcard_data.deck_id)
        
        return Flashcard(**flashcard_dict)
    
    async def get_flashcard(self, flashcard_id: str) -> Optional[Flashcard]:
        """Get flashcard by ID"""
        try:
            flashcard_data = await self.collection.find_one({"_id": ObjectId(flashcard_id)})
            if flashcard_data:
                return Flashcard(**flashcard_data)
            return None
        except Exception as e:
            logger.error(f"Error getting flashcard {flashcard_id}: {e}")
            return None
    
    async def get_flashcards_by_deck(self, deck_id: str) -> List[Flashcard]:
        """Get all flashcards for a deck, ordered by order field"""
        try:
            logger.info(f"Getting flashcards for deck_id: {deck_id}")
            
            # Convert deck_id to ObjectId since that's how it's stored in database
            try:
                deck_object_id = ObjectId(deck_id)
                cursor = self.collection.find({
                    "deck_id": deck_object_id,
                    "is_active": True
                }).sort("order", 1)
                
                flashcards_data = await cursor.to_list(length=None)
                logger.info(f"Found {len(flashcards_data)} flashcards with ObjectId deck_id")
                
            except Exception as oid_error:
                logger.warning(f"Invalid ObjectId format for {deck_id}: {oid_error}")
                flashcards_data = []
            
            # If still no results, try with string deck_id for backwards compatibility
            if not flashcards_data:
                logger.info("Trying with string deck_id for backwards compatibility")
                cursor = self.collection.find({
                    "deck_id": deck_id,
                    "is_active": True
                }).sort("order", 1)
                flashcards_data = await cursor.to_list(length=None)
                logger.info(f"Found {len(flashcards_data)} flashcards with string deck_id")
            
            return [Flashcard(**flashcard_data) for flashcard_data in flashcards_data]
        except Exception as e:
            logger.error(f"Error getting flashcards for deck {deck_id}: {e}")
            return []
    
    async def update_flashcard(self, flashcard_id: str, flashcard_update: FlashcardUpdate) -> Optional[Flashcard]:
        """Update flashcard"""
        try:
            update_data = flashcard_update.dict(exclude_unset=True)
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                
                result = await self.collection.update_one(
                    {"_id": ObjectId(flashcard_id)},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    return await self.get_flashcard(flashcard_id)
            
            return None
        except Exception as e:
            logger.error(f"Error updating flashcard {flashcard_id}: {e}")
            return None
    
    async def delete_flashcard(self, flashcard_id: str) -> bool:
        """Soft delete flashcard"""
        try:
            # Get flashcard to find deck_id for updating count
            flashcard = await self.get_flashcard(flashcard_id)
            if not flashcard:
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(flashcard_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                # Update deck flashcard count
                deck_crud = DeckCRUD(self.db)
                await deck_crud.update_deck_flashcard_count(str(flashcard.deck_id))
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting flashcard {flashcard_id}: {e}")
            return False
    
    async def reorder_flashcards(self, deck_id: str, flashcard_orders: List[Dict[str, Any]]) -> bool:
        """Reorder flashcards in a deck"""
        try:
            # Update each flashcard's order
            for item in flashcard_orders:
                await self.collection.update_one(
                    {"_id": ObjectId(item["id"]), "deck_id": ObjectId(deck_id)},
                    {"$set": {"order": item["order"], "updated_at": datetime.utcnow()}}
                )
            
            return True
        except Exception as e:
            logger.error(f"Error reordering flashcards for deck {deck_id}: {e}")
            return False
