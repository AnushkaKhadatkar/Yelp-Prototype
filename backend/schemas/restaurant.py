from pydantic import BaseModel
from typing import Optional


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