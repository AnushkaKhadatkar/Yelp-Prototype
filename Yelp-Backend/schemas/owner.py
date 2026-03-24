from pydantic import BaseModel
from typing import Optional, List, Dict
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

class RestaurantBrief(BaseModel):
    id: int
    name: str
    cuisine: Optional[str] = None
    city: Optional[str] = None
    avg_rating: Optional[float] = None

class OwnerProfileResponse(BaseModel):
    owner: dict
    restaurants: List[RestaurantBrief]


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



class DashboardReviewItem(BaseModel):
    review_id: int
    restaurant_name: str
    rating: int
    comment: str
    created_at: datetime


class OwnerDashboardResponse(BaseModel):
    total_review_count: int
    avg_rating: float
    ratings_distribution: Dict[int, int]
    recent_reviews: List[DashboardReviewItem]


