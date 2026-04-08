from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)



class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str
    user_id: int
    role: str

class UserProfileResponse(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    phone: Optional[str] = None
    about: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    languages: Optional[str] = None
    gender: Optional[str] = None
    profile_pic: Optional[str] = None
    createdAt: Optional[str] = None


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    about: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    languages: Optional[str] = None
    gender: Optional[str] = None


class UserReviewHistoryItem(BaseModel):
    review_id: int
    restaurant_id: int
    restaurant_name: str
    rating: int
    comment: Optional[str]
    created_at: Optional[str]


class UserRestaurantHistoryItem(BaseModel):
    id: int
    name: str
    cuisine: str
    address: Optional[str]
    city: Optional[str]
    created_at: Optional[str]


class UserHistoryResponse(BaseModel):
    reviews: List[UserReviewHistoryItem]
    restaurants_added: List[UserRestaurantHistoryItem]