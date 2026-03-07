from pydantic import BaseModel
from typing import Optional


class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    rating: int
    comment: Optional[str]
    created_at: Optional[str]