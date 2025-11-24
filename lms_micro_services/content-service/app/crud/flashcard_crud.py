from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
from app.models.content import Flashcard, PyObjectId
from app.schemas.flashcard import (
    FlashcardCreate, FlashcardUpdate
)
import logging

logger = logging.getLogger(__name__)

class FlashcardCRUD:
    """CRUD operations for flashcards"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.flashcards
    
    async def create_flashcard(self, flashcard_data: FlashcardCreate) -> Flashcard:
        """Create a new flashcard"""
        logger.info(f"Creating flashcard with data: {flashcard_data}")
        
        flashcard_dict = flashcard_data.dict()
        logger.info(f"Flashcard dict before processing: {flashcard_dict}")
        
        flashcard_dict["deck_id"] = ObjectId(flashcard_dict["deck_id"])
        flashcard_dict["created_at"] = datetime.utcnow()
        
        logger.info(f"Final flashcard dict to insert: {flashcard_dict}")
        
        result = await self.collection.insert_one(flashcard_dict)
        flashcard_dict["_id"] = result.inserted_id
        
        logger.info(f"Inserted flashcard with ID: {result.inserted_id}")
        
        # Update deck flashcard count
        from .deck_crud import DeckCRUD
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
        """Get all flashcards for a deck"""
        try:
            logger.info(f"Getting flashcards for deck: {deck_id}")
            
            # Debug: Check if deck exists
            deck_exists = await self.db.decks.find_one({"_id": ObjectId(deck_id)})
            logger.info(f"Deck exists: {deck_exists is not None}")
            
            # Debug: Count all flashcards
            total_flashcards = await self.collection.count_documents({})
            logger.info(f"Total flashcards in collection: {total_flashcards}")
            
            # Debug: Count flashcards for this deck (both ways)
            count_with_objectid = await self.collection.count_documents({"deck_id": ObjectId(deck_id)})
            count_with_string = await self.collection.count_documents({"deck_id": deck_id})
            logger.info(f"Flashcards with ObjectId deck_id: {count_with_objectid}")
            logger.info(f"Flashcards with string deck_id: {count_with_string}")
            
            # Use ObjectId for query - don't filter by is_active since field might not exist
            cursor = self.collection.find({
                "deck_id": ObjectId(deck_id)
                # Remove is_active filter since older flashcards might not have this field
            }).sort("order", 1)  # Sort by order instead of created_at
            
            flashcards_data = await cursor.to_list(length=None)
            logger.info(f"Found {len(flashcards_data)} flashcards for deck {deck_id}")
            
            # Try to create Flashcard objects, but handle errors gracefully
            flashcards = []
            for flashcard_data in flashcards_data:
                try:
                    # Ensure is_active field exists with default value
                    if "is_active" not in flashcard_data:
                        flashcard_data["is_active"] = True
                    
                    # Convert string dates to datetime objects if needed
                    if "created_at" in flashcard_data and isinstance(flashcard_data["created_at"], str):
                        from datetime import datetime
                        flashcard_data["created_at"] = datetime.fromisoformat(flashcard_data["created_at"].replace('Z', '+00:00'))
                    if "updated_at" in flashcard_data and isinstance(flashcard_data["updated_at"], str):
                        from datetime import datetime
                        flashcard_data["updated_at"] = datetime.fromisoformat(flashcard_data["updated_at"].replace('Z', '+00:00'))
                    
                    # deck_id should already be ObjectId from query, but ensure it's PyObjectId for model
                    if "deck_id" in flashcard_data:
                        flashcard_data["deck_id"] = PyObjectId(flashcard_data["deck_id"])
                    
                    flashcard = Flashcard(**flashcard_data)
                    flashcards.append(flashcard)
                except Exception as e:
                    logger.error(f"Error creating Flashcard object from data {flashcard_data}: {e}")
                    # Print the actual data for debugging
                    logger.error(f"Problematic data keys: {list(flashcard_data.keys())}")
                    for key, value in flashcard_data.items():
                        logger.error(f"  {key}: {type(value).__name__} = {value}")
            
            logger.info(f"Successfully created {len(flashcards)} Flashcard objects")
            return flashcards
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
                from .deck_crud import DeckCRUD
                deck_crud = DeckCRUD(self.db)
                await deck_crud.update_deck_flashcard_count(str(flashcard.deck_id))
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting flashcard {flashcard_id}: {e}")
            return False
    
    async def delete_flashcards_by_deck(self, deck_id: str):
        """Soft delete all flashcards in a deck"""
        try:
            await self.collection.update_many(
                {"deck_id": ObjectId(deck_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Error deleting flashcards for deck {deck_id}: {e}")
    
    async def get_random_flashcards(self, deck_id: str, limit: int = 10) -> List[Flashcard]:
        """Get random flashcards from a deck for study"""
        try:
            pipeline = [
                {"$match": {"deck_id": ObjectId(deck_id), "is_active": True}},
                {"$sample": {"size": limit}}
            ]
            
            cursor = self.collection.aggregate(pipeline)
            flashcards_data = await cursor.to_list(length=None)
            
            return [Flashcard(**flashcard_data) for flashcard_data in flashcards_data]
        except Exception as e:
            logger.error(f"Error getting random flashcards for deck {deck_id}: {e}")
            return []
    
    async def search_flashcards(self, query: str, deck_id: Optional[str] = None) -> List[Flashcard]:
        """Search flashcards by content"""
        try:
            search_filter = {
                "is_active": True,
                "$or": [
                    {"front": {"$regex": query, "$options": "i"}},
                    {"back": {"$regex": query, "$options": "i"}}
                ]
            }
            
            if deck_id:
                search_filter["deck_id"] = ObjectId(deck_id)
            
            cursor = self.collection.find(search_filter).sort("created_at", 1)
            flashcards_data = await cursor.to_list(length=None)
            
            return [Flashcard(**flashcard_data) for flashcard_data in flashcards_data]
        except Exception as e:
            logger.error(f"Error searching flashcards with query '{query}': {e}")
            return []
