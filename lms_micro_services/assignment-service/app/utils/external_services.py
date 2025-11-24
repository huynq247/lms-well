import httpx
import logging
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """Client for Auth Service integration"""
    
    def __init__(self):
        self.base_url = settings.auth_service_url
        self.timeout = 10.0
    
    async def validate_user(self, user_id: int) -> bool:
        """Validate if user exists in Auth Service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/users/{user_id}")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to validate user {user_id} with Auth Service: {e}")
            # For development, return True to avoid blocking
            return True
    
    async def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information from Auth Service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/users/{user_id}")
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.warning(f"Failed to get user info for {user_id} from Auth Service: {e}")
            return None
    
    async def validate_instructor_role(self, user_id: int) -> bool:
        """Validate if user has instructor role"""
        try:
            user_info = await self.get_user_info(user_id)
            if user_info:
                return user_info.get("role") in ["admin", "teacher"]
            return False
        except Exception as e:
            logger.warning(f"Failed to validate instructor role for {user_id}: {e}")
            # For development, return True to avoid blocking
            return True
    
    async def validate_student_role(self, user_id: int) -> bool:
        """Validate if user has student role"""
        try:
            user_info = await self.get_user_info(user_id)
            if user_info:
                return user_info.get("role") in ["student", "admin"]
            return False
        except Exception as e:
            logger.warning(f"Failed to validate student role for {user_id}: {e}")
            # For development, return True to avoid blocking
            return True


class ContentServiceClient:
    """Client for Content Service integration"""
    
    def __init__(self):
        self.base_url = settings.content_service_url
        self.timeout = 10.0
    
    async def get_course_details(self, course_id: str, auth_token: str = None) -> Optional[Dict[str, Any]]:
        """Get course details with authentication"""
        try:
            headers = {}
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
                
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/courses/{course_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Course {course_id} not found")
                    return None
                else:
                    logger.error(f"Error fetching course: {response.status_code}")
                    return None
        except Exception as e:
            logger.warning(f"Failed to get course {course_id} from Content Service: {e}")
            return None
    
    async def get_course_progress(self, course_id: str, student_id: int, auth_token: str = None) -> Optional[Dict[str, Any]]:
        """Get course progress for student"""
        try:
            headers = {}
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
                
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get course lessons to calculate progress
                response = await client.get(
                    f"{self.base_url}/api/v1/lessons/",
                    params={"course_id": course_id},
                    headers=headers
                )
                if response.status_code == 200:
                    lessons_data = response.json()
                    total_lessons = lessons_data.get("total", 0)
                    # TODO: Implement actual lesson completion tracking
                    # For now, return basic structure
                    return {
                        "total_lessons": total_lessons,
                        "completed_lessons": 0,  # Will be implemented later
                        "progress_percentage": 0.0
                    }
                return None
        except Exception as e:
            logger.warning(f"Failed to get course progress for course {course_id}, student {student_id}: {e}")
            return None

    async def get_content(self, content_type: str, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content information from Content Service"""
        try:
            endpoint_map = {
                "course": f"/api/v1/courses/{content_id}",
                "deck": f"/api/v1/decks/{content_id}"
            }
            
            endpoint = endpoint_map.get(content_type)
            if not endpoint:
                logger.error(f"Unknown content type: {content_type}")
                return None
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Content {content_type} {content_id} not found")
                    return None
                else:
                    logger.error(f"Error fetching content: {response.status_code}")
                    return None
        except Exception as e:
            logger.warning(f"Failed to get content {content_type} {content_id} from Content Service: {e}")
            # For development, return mock data to avoid blocking
            return {
                "id": content_id,
                "title": f"Mock {content_type.title()}",
                "description": f"Mock {content_type} for development"
            }
    
    async def get_course_lessons(self, course_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get lessons for a course"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/courses/{course_id}/lessons")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("items", [])
                return None
        except Exception as e:
            logger.warning(f"Failed to get lessons for course {course_id}: {e}")
            return []
    
    async def get_deck_flashcards(self, deck_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get flashcards for a deck"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/decks/{deck_id}/flashcards")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("items", [])
                return None
        except Exception as e:
            logger.warning(f"Failed to get flashcards for deck {deck_id}: {e}")
            return []
    
    async def get_content_item_count(self, content_type: str, content_id: str) -> int:
        """Get total number of items in content (lessons for course, flashcards for deck)"""
        try:
            if content_type == "course":
                lessons = await self.get_course_lessons(content_id)
                return len(lessons) if lessons else 0
            elif content_type == "deck":
                flashcards = await self.get_deck_flashcards(content_id)
                return len(flashcards) if flashcards else 0
            else:
                return 0
        except Exception as e:
            logger.warning(f"Failed to get item count for {content_type} {content_id}: {e}")
            return 1  # Return 1 as fallback to avoid division by zero


# Service health checker
class ServiceHealthChecker:
    """Check health of external services"""
    
    @staticmethod
    async def check_auth_service() -> bool:
        """Check if Auth Service is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.auth_service_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    @staticmethod
    async def check_content_service() -> bool:
        """Check if Content Service is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.content_service_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    @staticmethod
    async def get_services_status() -> Dict[str, bool]:
        """Get status of all external services"""
        return {
            "auth_service": await ServiceHealthChecker.check_auth_service(),
            "content_service": await ServiceHealthChecker.check_content_service()
        }
