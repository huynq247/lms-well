from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """MongoDB database manager for Content Service"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database = None
        
    async def connect_to_database(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(
                settings.mongodb_url,
                maxPoolSize=10,
                minPoolSize=1,
                maxIdleTimeMS=30000,
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            self.database = self.client[settings.mongodb_db_name]
            
            logger.info(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")
            
            # Create indexes for better performance
            await self._create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise e
        except Exception as e:
            logger.error(f"❌ Unexpected database error: {e}")
            raise e
    
    async def close_database_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("📊 MongoDB connection closed")
    
    async def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Courses collection indexes
            await self.database.courses.create_index("instructor_id")
            await self.database.courses.create_index("title")
            await self.database.courses.create_index([("title", "text"), ("description", "text")])
            
            # Lessons collection indexes
            await self.database.lessons.create_index("course_id")
            await self.database.lessons.create_index([("course_id", 1), ("order", 1)])
            
            # Decks collection indexes
            await self.database.decks.create_index("instructor_id")
            await self.database.decks.create_index("title")
            await self.database.decks.create_index([("title", "text"), ("description", "text")])
            
            # Flashcards collection indexes
            await self.database.flashcards.create_index("deck_id")
            await self.database.flashcards.create_index([("deck_id", 1), ("order", 1)])
            
            logger.info("📊 Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create indexes: {e}")
    
    async def get_database_stats(self):
        """Get database statistics for monitoring"""
        try:
            stats = await self.database.command("dbStats")
            collections_stats = {}
            
            for collection_name in ["courses", "lessons", "decks", "flashcards"]:
                try:
                    collection_stats = await self.database.command("collStats", collection_name)
                    collections_stats[collection_name] = {
                        "count": collection_stats.get("count", 0),
                        "size": collection_stats.get("size", 0)
                    }
                except:
                    collections_stats[collection_name] = {"count": 0, "size": 0}
            
            return {
                "database": settings.mongodb_db_name,
                "total_size": stats.get("dataSize", 0),
                "collections": collections_stats
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return None

# Global database manager instance
db_manager = DatabaseManager()

async def get_database():
    """Get database instance"""
    return db_manager.database

async def check_database_health():
    """Check database health for monitoring"""
    try:
        await db_manager.client.admin.command('ping')
        return True
    except:
        return False
