from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ----------------------------
# OWNER SIGNUP
# ----------------------------

class OwnerCreate(BaseModel):
    name: str
    email: str
    password: str
    restaurant_location: Optional[str] = None


# ----------------------------
# OWNER BASIC RESPONSE
# ----------------------------

class OwnerResponse(BaseModel):
    id: int
    name: str
    email: str
    restaurant_location: Optional[str]


# ----------------------------
# OWNER DASHBOARD RESTAURANT
# ----------------------------

class OwnerRestaurantResponse(BaseModel):
    id: int
    name: str
    cuisine: str
    city: Optional[str]
    avg_rating: Optional[float]


# ----------------------------
# OWNER PROFILE RESPONSE
# ----------------------------

class OwnerProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    restaurants: List[OwnerRestaurantResponse]


# Required for Pydantic v2
OwnerCreate.model_rebuild()
OwnerResponse.model_rebuild()
OwnerRestaurantResponse.model_rebuild()
OwnerProfileResponse.model_rebuild()

class OwnerReviewItem(BaseModel):
    review_id: int
    user_name: str
    rating: int
    comment: str
    created_at: datetime


class OwnerRestaurantReviewsResponse(BaseModel):
    restaurant_id: int
    restaurant_name: str
    reviews: List[OwnerReviewItem]


OwnerReviewItem.model_rebuild()
OwnerRestaurantReviewsResponse.model_rebuild()