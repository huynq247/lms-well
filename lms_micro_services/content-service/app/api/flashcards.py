from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional

from app.core.database import get_database
from app.schemas.flashcard import (
    FlashcardCreate, FlashcardUpdate, FlashcardResponse
)
from app.schemas.common import (
    PaginationParams, PaginatedResponse, MessageResponse
)
from app.crud import FlashcardCRUD

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])

@router.post("/", response_model=FlashcardResponse, status_code=status.HTTP_201_CREATED)
async def create_flashcard(
    flashcard: FlashcardCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new flashcard"""
    print(f"🔍 Received flashcard creation request: {flashcard}")
    print(f"📊 Flashcard dict: {flashcard.dict()}")
    
    flashcard_crud = FlashcardCRUD(db)
    
    try:
        db_flashcard = await flashcard_crud.create_flashcard(flashcard)
        response = FlashcardResponse(**db_flashcard.dict())
        print(f"✅ Created flashcard response: {response}")
        return response
    except Exception as e:
        print(f"❌ Error creating flashcard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating flashcard: {str(e)}"
        )

@router.get("/", response_model=List[FlashcardResponse])
async def get_flashcards(
    deck_id: Optional[str] = Query(None, description="Filter by deck ID"),
    skip: int = Query(0, ge=0, description="Number of flashcards to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of flashcards to return"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get flashcards with optional filtering"""
    flashcard_crud = FlashcardCRUD(db)
    
    try:
        if deck_id:
            # Get flashcards for specific deck
            flashcards = await flashcard_crud.get_flashcards_by_deck(deck_id)
            # Apply pagination manually
            flashcards = flashcards[skip:skip+limit]
        else:
            # Get all flashcards (need to implement this method)
            # For now, return empty list if no deck_id specified
            flashcards = []
        
        return [FlashcardResponse(**flashcard.dict()) for flashcard in flashcards]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving flashcards: {str(e)}"
        )

@router.get("/{flashcard_id}", response_model=FlashcardResponse)
async def get_flashcard(
    flashcard_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific flashcard by ID"""
    flashcard_crud = FlashcardCRUD(db)
    
    flashcard = await flashcard_crud.get_flashcard(flashcard_id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    return FlashcardResponse(**flashcard.dict())

@router.put("/{flashcard_id}", response_model=FlashcardResponse)
async def update_flashcard(
    flashcard_id: str,
    flashcard_update: FlashcardUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a flashcard"""
    flashcard_crud = FlashcardCRUD(db)
    
    # Check if flashcard exists
    existing_flashcard = await flashcard_crud.get_flashcard(flashcard_id)
    if not existing_flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    try:
        updated_flashcard = await flashcard_crud.update_flashcard(flashcard_id, flashcard_update)
        return FlashcardResponse(**updated_flashcard.dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating flashcard: {str(e)}"
        )

@router.delete("/{flashcard_id}", response_model=MessageResponse)
async def delete_flashcard(
    flashcard_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a flashcard"""
    flashcard_crud = FlashcardCRUD(db)
    
    # Check if flashcard exists
    flashcard = await flashcard_crud.get_flashcard(flashcard_id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    
    try:
        await flashcard_crud.delete_flashcard(flashcard_id)
        return MessageResponse(message="Flashcard deleted successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting flashcard: {str(e)}"
        )
