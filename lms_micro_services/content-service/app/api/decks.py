from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional

from app.core.database import get_database
from app.core.auth import get_current_user, get_teacher_or_admin_user, User, UserRole, get_assigned_content_ids
from app.schemas.deck import (
    DeckCreate, DeckUpdate, DeckResponse, DeckFilter
)
from app.schemas.flashcard import (
    FlashcardCreate, FlashcardUpdate, FlashcardResponse
)
from app.schemas.common import (
    ReorderRequest, PaginationParams, PaginatedResponse, MessageResponse
)
from app.crud import DeckCRUD, FlashcardCRUD

router = APIRouter(prefix="/decks", tags=["Decks & Flashcards"])

@router.get("/debug/instructor/{instructor_id}", response_model=List[dict])
async def debug_decks_by_instructor(
    instructor_id: int,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Debug endpoint to see decks by instructor"""
    cursor = db.decks.find({"instructor_id": instructor_id})
    decks_data = await cursor.to_list(length=None)
    for deck in decks_data:
        deck["_id"] = str(deck["_id"])
    return decks_data

@router.get("/debug/all-decks", response_model=List[dict])
async def debug_all_decks(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Debug endpoint to see all decks with their instructor_id"""
    cursor = db.decks.find({})
    decks_data = await cursor.to_list(length=None)
    for deck in decks_data:
        deck["_id"] = str(deck["_id"])
    return decks_data

# Deck endpoints
@router.post("/", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
async def create_deck(
    deck: DeckCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new deck"""
    deck_crud = DeckCRUD(db)
    
    # TODO: Get instructor name from auth service
    instructor_name = f"Instructor {deck.instructor_id}"
    
    try:
        db_deck = await deck_crud.create_deck(deck, instructor_name)
        return DeckResponse(**db_deck.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating deck: {str(e)}"
        )

@router.get("/debug/flashcards", response_model=List[dict])
async def debug_flashcards(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Debug endpoint to see all flashcards in database"""
    cursor = db.flashcards.find({})
    flashcards_data = await cursor.to_list(length=None)
    # Convert ObjectId to string for JSON serialization
    for flashcard in flashcards_data:
        flashcard["_id"] = str(flashcard["_id"])
        if "deck_id" in flashcard:
            flashcard["deck_id"] = str(flashcard["deck_id"])
    return flashcards_data

@router.get("/debug/decks", response_model=List[dict])
async def debug_decks(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Debug endpoint to see all decks in database"""
    cursor = db.decks.find({})
    decks_data = await cursor.to_list(length=None)
    # Convert ObjectId to string for JSON serialization
    for deck in decks_data:
        deck["_id"] = str(deck["_id"])
        if "lesson_id" in deck:
            deck["lesson_id"] = str(deck["lesson_id"])
    return decks_data

@router.get("/debug/deck/{deck_id}/flashcards")
async def debug_deck_flashcards(
    deck_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Debug endpoint to see flashcards for specific deck with different query methods"""
    from bson import ObjectId
    
    # Try both ObjectId and string queries
    result = {
        "deck_id_searched": deck_id,
        "flashcards_with_objectid": [],
        "flashcards_with_string": [],
        "all_flashcards": []
    }
    
    # Query with ObjectId
    try:
        cursor = db.flashcards.find({"deck_id": ObjectId(deck_id)})
        flashcards_data = await cursor.to_list(length=None)
        for flashcard in flashcards_data:
            flashcard["_id"] = str(flashcard["_id"])
            flashcard["deck_id"] = str(flashcard["deck_id"])
        result["flashcards_with_objectid"] = flashcards_data
    except Exception as e:
        result["objectid_error"] = str(e)
    
    # Query with string
    try:
        cursor = db.flashcards.find({"deck_id": deck_id})
        flashcards_data = await cursor.to_list(length=None)
        for flashcard in flashcards_data:
            flashcard["_id"] = str(flashcard["_id"])
            if "deck_id" in flashcard:
                flashcard["deck_id"] = str(flashcard["deck_id"])
        result["flashcards_with_string"] = flashcards_data
    except Exception as e:
        result["string_error"] = str(e)
    
    # Get all flashcards to see their deck_id format
    try:
        cursor = db.flashcards.find({})
        flashcards_data = await cursor.to_list(length=None)
        for flashcard in flashcards_data:
            flashcard["_id"] = str(flashcard["_id"])
            if "deck_id" in flashcard:
                flashcard["deck_id"] = str(flashcard["deck_id"])
        result["all_flashcards"] = flashcards_data
    except Exception as e:
        result["all_error"] = str(e)
    
    return result

@router.get("/raw/{deck_id}/flashcards")
async def get_raw_flashcards(
    deck_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Raw flashcards without model conversion"""
    from bson import ObjectId
    cursor = db.flashcards.find({"deck_id": ObjectId(deck_id)})
    flashcards_data = await cursor.to_list(length=None)
    # Convert ObjectId to string for JSON serialization
    for flashcard in flashcards_data:
        flashcard["_id"] = str(flashcard["_id"])
        flashcard["deck_id"] = str(flashcard["deck_id"])
    return {"raw_count": len(flashcards_data), "flashcards": flashcards_data}

@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(
    deck_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get deck by ID"""
    deck_crud = DeckCRUD(db)
    deck = await deck_crud.get_deck(deck_id)
    
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    return DeckResponse(**deck.dict())

@router.get("/", response_model=PaginatedResponse)
async def get_decks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=100),
    instructor_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    is_published: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get decks with role-based filtering"""
    deck_crud = DeckCRUD(db)
    
    pagination = PaginationParams(page=page, size=size, search=search)
    
    # Parse tags from comma-separated string
    tag_list = None
    if tags:
        tag_list = [tag.strip().lower() for tag in tags.split(",") if tag.strip()]
    
    # Role-based filtering
    if current_user.role == UserRole.STUDENT:
        # Students can see: assigned decks + public decks
        assigned_deck_ids = await get_assigned_content_ids(current_user.id, "deck")
        
        if assigned_deck_ids:
            # Student has assignments - show assigned decks + public decks
            filters = DeckFilter(
                instructor_id=instructor_id,
                category=category,
                tags=tag_list,
                is_published=True,  # Only published decks
                is_active=is_active,
                deck_ids=assigned_deck_ids,
                include_public=True  # Include both assigned and public decks
            )
        else:
            # Student has no assignments - show only public decks
            filters = DeckFilter(
                instructor_id=instructor_id,
                category=category,
                tags=tag_list,
                is_published=True,  # Only published/public decks
                is_active=is_active,
                include_public=True  # This ensures we get public decks even with no assignments
            )
    else:  # TEACHER or ADMIN - can see all decks
        filters = DeckFilter(
            instructor_id=instructor_id,
            category=category,
            tags=tag_list,
            is_published=is_published,
            is_active=is_active
        )
    
    result = await deck_crud.get_decks(pagination, filters)
    
    # Convert decks to response format
    decks_response = [DeckResponse(**deck.dict()) for deck in result["items"]]
    result["items"] = decks_response
    
    return PaginatedResponse(**result)

@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: str,
    deck_update: DeckUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update deck"""
    deck_crud = DeckCRUD(db)
    
    updated_deck = await deck_crud.update_deck(deck_id, deck_update)
    if not updated_deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found or no changes made"
        )
    
    return DeckResponse(**updated_deck.dict())

@router.delete("/{deck_id}", response_model=MessageResponse)
async def delete_deck(
    deck_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Soft delete deck"""
    deck_crud = DeckCRUD(db)
    
    success = await deck_crud.delete_deck(deck_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    return MessageResponse(message="Deck deleted successfully")

@router.get("/instructor/{instructor_id}", response_model=List[DeckResponse])
async def get_decks_by_instructor(
    instructor_id: int,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all decks by instructor"""
    deck_crud = DeckCRUD(db)
    decks = await deck_crud.get_decks_by_instructor(instructor_id)
    
    return [DeckResponse(**deck.dict()) for deck in decks]

# Flashcard endpoints
@router.post("/{deck_id}/flashcards", response_model=FlashcardResponse, status_code=status.HTTP_201_CREATED)
async def create_flashcard(
    deck_id: str,
    flashcard: FlashcardCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new flashcard for a deck"""
    # Verify deck exists
    deck_crud = DeckCRUD(db)
    deck = await deck_crud.get_deck(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Set deck_id from URL
    flashcard.deck_id = deck_id
    
    flashcard_crud = FlashcardCRUD(db)
    
    try:
        db_flashcard = await flashcard_crud.create_flashcard(flashcard)
        return FlashcardResponse(**db_flashcard.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating flashcard: {str(e)}"
        )

@router.get("/{deck_id}/flashcards", response_model=List[FlashcardResponse])
async def get_flashcards_by_deck(
    deck_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all flashcards for a deck"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"API: Getting flashcards for deck: {deck_id}")
    
    # Verify deck exists
    deck_crud = DeckCRUD(db)
    deck = await deck_crud.get_deck(deck_id)
    if not deck:
        logger.warning(f"API: Deck {deck_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    logger.info(f"API: Deck found: {deck.title}")
    
    # Bypass CRUD and query database directly to avoid model conversion issues
    from bson import ObjectId
    cursor = db.flashcards.find({"deck_id": ObjectId(deck_id)}).sort("order", 1)
    flashcards_data = await cursor.to_list(length=None)
    
    logger.info(f"API: Found {len(flashcards_data)} raw flashcards")
    
    # Convert raw data directly to FlashcardResponse
    flashcard_responses = []
    for flashcard_data in flashcards_data:
        try:
            # Convert ObjectId fields to strings
            flashcard_data["id"] = str(flashcard_data.pop("_id"))
            flashcard_data["deck_id"] = str(flashcard_data["deck_id"])
            
            # Ensure required fields exist with defaults
            if "is_active" not in flashcard_data:
                flashcard_data["is_active"] = True
            if "front_image_valid" not in flashcard_data:
                flashcard_data["front_image_valid"] = None
            if "back_image_valid" not in flashcard_data:
                flashcard_data["back_image_valid"] = None
            if "last_url_check" not in flashcard_data:
                flashcard_data["last_url_check"] = None
            if "updated_at" not in flashcard_data:
                flashcard_data["updated_at"] = None
            
            # NEW VOCABULARY FIELDS (with defaults for existing flashcards)
            if "wordclass" not in flashcard_data:
                flashcard_data["wordclass"] = None
            if "definition" not in flashcard_data:
                flashcard_data["definition"] = None
            if "example" not in flashcard_data:
                flashcard_data["example"] = None
            
            # Convert date strings to datetime objects if needed for validation
            if "created_at" in flashcard_data and isinstance(flashcard_data["created_at"], str):
                from datetime import datetime
                flashcard_data["created_at"] = datetime.fromisoformat(flashcard_data["created_at"].replace('Z', '+00:00'))
            
            flashcard_response = FlashcardResponse(**flashcard_data)
            flashcard_responses.append(flashcard_response)
        except Exception as e:
            logger.error(f"Error converting flashcard data to response: {e}")
            logger.error(f"Problematic data: {flashcard_data}")
    
    logger.info(f"API: Successfully converted {len(flashcard_responses)} flashcards")
    return flashcard_responses

@router.get("/debug/flashcards", response_model=List[dict])
async def debug_flashcards(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Debug endpoint to see all flashcards in database"""
    cursor = db.flashcards.find({})
    flashcards_data = await cursor.to_list(length=None)
    # Convert ObjectId to string for JSON serialization
    for flashcard in flashcards_data:
        flashcard["_id"] = str(flashcard["_id"])
        if "deck_id" in flashcard:
            flashcard["deck_id"] = str(flashcard["deck_id"])
    return flashcards_data

@router.get("/flashcards/{flashcard_id}", response_model=FlashcardResponse)
async def get_flashcard(
    flashcard_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get flashcard by ID"""
    flashcard_crud = FlashcardCRUD(db)
    flashcard = await flashcard_crud.get_flashcard(flashcard_id)
    
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    return FlashcardResponse(**flashcard.dict())

@router.put("/flashcards/{flashcard_id}", response_model=FlashcardResponse)
async def update_flashcard(
    flashcard_id: str,
    flashcard_update: FlashcardUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update flashcard"""
    flashcard_crud = FlashcardCRUD(db)
    
    updated_flashcard = await flashcard_crud.update_flashcard(flashcard_id, flashcard_update)
    if not updated_flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found or no changes made"
        )
    
    return FlashcardResponse(**updated_flashcard.dict())

@router.delete("/flashcards/{flashcard_id}", response_model=MessageResponse)
async def delete_flashcard(
    flashcard_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Soft delete flashcard"""
    flashcard_crud = FlashcardCRUD(db)
    
    success = await flashcard_crud.delete_flashcard(flashcard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    return MessageResponse(message="Flashcard deleted successfully")

@router.put("/{deck_id}/flashcards/reorder", response_model=MessageResponse)
async def reorder_flashcards(
    deck_id: str,
    reorder_request: ReorderRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Reorder flashcards in a deck"""
    # Verify deck exists
    deck_crud = DeckCRUD(db)
    deck = await deck_crud.get_deck(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    flashcard_crud = FlashcardCRUD(db)
    success = await flashcard_crud.reorder_flashcards(deck_id, reorder_request.items)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reordering flashcards"
        )
    
    return MessageResponse(message="Flashcards reordered successfully")
