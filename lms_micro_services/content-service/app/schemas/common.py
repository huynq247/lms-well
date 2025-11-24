from pydantic import BaseModel, Field, validator
from typing import Optional, List

# Reorder Schemas
class ReorderRequest(BaseModel):
    items: List[dict] = Field(..., description="List of {id, order} items")

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Items list cannot be empty')
        
        orders = [item.get('order') for item in v]
        if len(set(orders)) != len(orders):
            raise ValueError('All order values must be unique')
        
        for item in v:
            if 'id' not in item or 'order' not in item:
                raise ValueError('Each item must have id and order fields')
            if not isinstance(item['order'], int) or item['order'] < 1:
                raise ValueError('Order must be a positive integer')
        
        return v

# Pagination Schemas
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = Field(None, max_length=100)

class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

# Response Schemas
class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

class URLValidationResponse(BaseModel):
    url: str
    is_valid: bool
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    error: Optional[str] = None
