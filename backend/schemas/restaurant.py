from pydantic import BaseModel
from typing import List, Optional


class RestaurantListItem(BaseModel):
    id: int
    name: str
    cuisine: str
    address: Optional[str]
    city: Optional[str]
    avg_rating: Optional[float]
    review_count: Optional[int]
    pricing_tier: Optional[str]
    photo: Optional[str]


class RestaurantResponse(BaseModel):
    id: int
    name: str
    cuisine: str
    address: Optional[str]
    description: Optional[str]
    hours: Optional[str]
    contact_phone: Optional[str]
    photos: Optional[str]
    avg_rating: Optional[float]
    review_count: Optional[int]

class ReviewItem(BaseModel):
    review_id: int
    user_name: str
    rating: int
    comment: Optional[str]
    photo: Optional[str]
    created_at: Optional[str]


class RestaurantDetailResponse(BaseModel):
    id: int
    name: str
    cuisine: str
    address: str
    city: str
    description: Optional[str]
    hours: Optional[str]
    contact_phone: Optional[str]
    pricing_tier: Optional[str]
    amenities: Optional[str]
    photos: List[str]
    avg_rating: Optional[float]
    review_count: Optional[int]
    reviews: List[ReviewItem]

class RestaurantCreate(BaseModel):
    name: str
    cuisine: str
    address: str
    city: str

    contact_phone: Optional[str] = None
    description: Optional[str] = None
    hours: Optional[str] = None
    pricing_tier: Optional[str] = None
    amenities: Optional[str] = None

RestaurantDetailResponse.model_rebuild()