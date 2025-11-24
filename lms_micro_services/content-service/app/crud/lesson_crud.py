from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from app.models.content import Lesson, PyObjectId
from app.schemas.lesson import (
    LessonCreate, LessonUpdate
)
import logging

logger = logging.getLogger(__name__)

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
        lesson_dict["is_active"] = True
        
        # Set default values if not provided
        if "is_published" not in lesson_dict:
            lesson_dict["is_published"] = False
        
        result = await self.collection.insert_one(lesson_dict)
        lesson_dict["_id"] = result.inserted_id
        
        # Update course lesson count
        from .course_crud import CourseCRUD
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
    
    async def get_lessons(self, pagination: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get lessons with pagination and filters"""
        try:
            # Build base query
            query = {}
            
            # Apply filters
            if filters.get("is_active") is not None:
                query["is_active"] = filters["is_active"]
            if filters.get("is_published") is not None:
                query["is_published"] = filters["is_published"]
            if filters.get("course_id"):
                query["course_id"] = ObjectId(filters["course_id"])
            if filters.get("instructor_id"):
                query["instructor_id"] = filters["instructor_id"]
            if filters.get("lesson_ids"):
                query["_id"] = {"$in": [ObjectId(lesson_id) for lesson_id in filters["lesson_ids"]]}
            if filters.get("search"):
                query["$or"] = [
                    {"title": {"$regex": filters["search"], "$options": "i"}},
                    {"content": {"$regex": filters["search"], "$options": "i"}}
                ]
            
            # Get total count
            total = await self.collection.count_documents(query)
            
            # Build cursor with pagination
            cursor = self.collection.find(query).sort("created_at", -1)
            
            # Apply pagination
            page = pagination.get("page", 1)
            size = pagination.get("size", 20)
            skip = (page - 1) * size
            
            cursor = cursor.skip(skip).limit(size)
            
            lessons_data = await cursor.to_list(length=None)
            lessons = [Lesson(**lesson_data) for lesson_data in lessons_data]
            
            # Calculate pages and pagination info
            pages = (total + size - 1) // size
            has_next = page < pages
            has_prev = page > 1
            
            return {
                "items": lessons,
                "total": total,
                "page": page,
                "size": size,
                "pages": pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        except Exception as e:
            logger.error(f"Error getting lessons with filters: {e}")
            return {
                "items": [],
                "total": 0,
                "page": 1,
                "size": 20,
                "pages": 0,
                "has_next": False,
                "has_prev": False
            }
    
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
                from .course_crud import CourseCRUD
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
