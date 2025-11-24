from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from app.models.content import Course, PyObjectId
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseFilter
)
from app.schemas.common import (
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
            if filters.course_ids is not None:
                from bson import ObjectId
                query["_id"] = {"$in": [ObjectId(course_id) for course_id in filters.course_ids]}
        
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
