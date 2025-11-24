from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from fastapi import Query

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and size"""
        return (self.page - 1) * self.size

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size")
) -> PaginationParams:
    """Get pagination parameters from query"""
    return PaginationParams(page=page, size=size)

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        pagination: PaginationParams
    ) -> "PaginatedResponse[T]":
        """Create paginated response"""
        pages = (total + pagination.size - 1) // pagination.size
        
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=pages,
            has_next=pagination.page < pages,
            has_prev=pagination.page > 1
        )

class APIResponse(BaseModel):
    """Standard API response"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None
