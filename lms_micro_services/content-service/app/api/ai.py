from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any

from app.core.database import get_database
from app.core.auth import get_current_user, User, UserRole
from app.services.gemini_service import get_gemini_service
from app.schemas.deck import DeckCreate, DeckResponse
from app.schemas.flashcard import FlashcardCreate
from app.crud import DeckCRUD, FlashcardCRUD
from pydantic import BaseModel

class FlashcardGenerationRequest(BaseModel):
    topic: str
    quantity: int = 10
    language: str = "vietnamese"
    deck_name: str
    deck_description: str = ""

class FlashcardGenerationResponse(BaseModel):
    message: str
    deck_id: str
    flashcards_count: int
    deck: DeckResponse

class SingleFlashcardRequest(BaseModel):
    word_or_topic: str
    language: str = "english"  # english, vietnamese, etc.
    card_type: str = "vocabulary"  # vocabulary, grammar, pronunciation, etc.
    difficulty: str = "medium"  # easy, medium, hard
    include_pronunciation: bool = True
    include_examples: bool = True
    include_synonyms: bool = True

class SingleFlashcardResponse(BaseModel):
    question: str
    answer: str
    pronunciation: str = ""
    examples: List[str] = []
    synonyms: List[str] = []
    explanation: str = ""
    difficulty: str
    tags: List[str] = []

router = APIRouter(prefix="/ai", tags=["AI Features"])

@router.post("/generate-flashcards", response_model=FlashcardGenerationResponse)
async def generate_flashcards_with_ai(
    request: FlashcardGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Tạo flashcards tự động bằng Gemini AI
    Chỉ admin mới có thể sử dụng tính năng này
    """
    
    # Kiểm tra quyền admin
    gemini_service = get_gemini_service()
    if not gemini_service.verify_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có thể sử dụng tính năng tạo flashcards tự động"
        )
    
    try:
        # Tạo flashcards bằng Gemini AI
        flashcards_data = await gemini_service.generate_flashcards(
            topic=request.topic,
            quantity=request.quantity,
            language=request.language
        )
        
        if not flashcards_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể tạo flashcards cho chủ đề này"
            )
        
        # Tạo mô tả deck nếu không có
        deck_description = request.deck_description
        if not deck_description:
            deck_description = await gemini_service.generate_deck_description(
                request.deck_name, flashcards_data
            )
        
        # Tạo deck mới
        deck_crud = DeckCRUD(db)
        deck_create = DeckCreate(
            title=request.deck_name,
            description=deck_description,
            instructor_id=current_user.id
        )
        
        created_deck = await deck_crud.create_deck(deck_create, current_user.username)
        
        # Tạo flashcards cho deck
        flashcard_crud = FlashcardCRUD(db)
        created_flashcards = []
        
        for i, flashcard_data in enumerate(flashcards_data):
            flashcard_create = FlashcardCreate(
                deck_id=str(created_deck.id),  # Convert ObjectId to string
                front=flashcard_data.get("question", ""),
                back=flashcard_data.get("answer", ""),
                order=i + 1,
                definition=flashcard_data.get("explanation", ""),
                difficulty=flashcard_data.get("difficulty", "medium"),
                example=flashcard_data.get("examples", [""])[0] if flashcard_data.get("examples") else ""
            )
            
            flashcard = await flashcard_crud.create_flashcard(flashcard_create)
            created_flashcards.append(flashcard)
        
        return FlashcardGenerationResponse(
            message=f"Đã tạo thành công {len(created_flashcards)} flashcards cho chủ đề '{request.topic}'",
            deck_id=str(created_deck.id),  # Convert ObjectId to string
            flashcards_count=len(created_flashcards),
            deck=created_deck
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống: {str(e)}"
        )

@router.post("/generate-deck-description")
async def generate_deck_description(
    deck_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Tạo mô tả cho deck bằng AI
    Chỉ admin mới có thể sử dụng
    """
    
    # Kiểm tra quyền admin
    gemini_service = get_gemini_service()
    if not gemini_service.verify_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có thể sử dụng tính năng AI"
        )
    
    try:
        description = await gemini_service.generate_deck_description(deck_name, [])
        return {"description": description}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi tạo mô tả: {str(e)}"
        )

@router.post("/generate-single-flashcard", response_model=SingleFlashcardResponse)
async def generate_single_flashcard(
    request: SingleFlashcardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Tạo chi tiết một flashcard bằng Gemini AI
    Đặc biệt hữu ích cho từ vựng tiếng Anh
    Chỉ admin mới có thể sử dụng
    """
    
    # Kiểm tra quyền admin
    gemini_service = get_gemini_service()
    if not gemini_service.verify_admin_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có thể sử dụng tính năng tạo flashcard AI"
        )
    
    try:
        # Tạo flashcard chi tiết bằng Gemini AI
        flashcard_data = await gemini_service.generate_single_flashcard(
            word_or_topic=request.word_or_topic,
            language=request.language,
            card_type=request.card_type,
            difficulty=request.difficulty,
            include_pronunciation=request.include_pronunciation,
            include_examples=request.include_examples,
            include_synonyms=request.include_synonyms
        )
        
        return SingleFlashcardResponse(**flashcard_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống: {str(e)}"
        )
