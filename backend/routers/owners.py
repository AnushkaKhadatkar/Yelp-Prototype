from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil

from database import get_db
from models.user import User
from models.restaurant import Restaurant
from services.auth_service import get_current_user
from pydantic import BaseModel


router = APIRouter(prefix="/owner", tags=["Owner"])


# =====================================================
# GET OWNER PROFILE
# =====================================================

@router.get("/profile")
def get_owner_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    restaurants = db.query(Restaurant).filter(
        Restaurant.owner_id == current_user.id
    ).all()

    return {
        "owner": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email
        },
        "restaurants": [
            {
                "id": r.id,
                "name": r.name,
                "cuisine": r.cuisine,
                "city": r.city,
                "avg_rating": r.avg_rating
            }
            for r in restaurants
        ]
    }


# =====================================================
# UPDATE OWNER PROFILE
# =====================================================

class OwnerProfileUpdate(BaseModel):
    name: str
    email: str


@router.put("/profile")
def update_owner_profile(
    data: OwnerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    current_user.name = data.name
    current_user.email = data.email

    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated successfully"}


# =====================================================
# UPDATE OWNER RESTAURANT
# =====================================================

@router.put("/restaurant/{restaurant_id}")
def update_owner_restaurant(
    restaurant_id: int,
    name: str = Form(...),
    cuisine: str = Form(...),
    description: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    hours: Optional[str] = Form(None),
    pricing_tier: Optional[str] = Form(None),
    amenities: Optional[str] = Form(None),
    ambiance: Optional[str] = Form(None),
    photos: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Role check
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Ownership enforcement
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update fields
    restaurant.name = name
    restaurant.cuisine = cuisine
    restaurant.description = description
    restaurant.address = address
    restaurant.city = city
    restaurant.state = state
    restaurant.zip_code = zip_code
    restaurant.contact_phone = contact_phone
    restaurant.contact_email = contact_email
    restaurant.hours = hours
    restaurant.price_tier = pricing_tier
    restaurant.amenities = amenities
    restaurant.ambiance = ambiance

    # Handle photo uploads (append, do not replace)
    if photos:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        photo_paths = []

        for photo in photos:
            file_path = os.path.join(upload_dir, photo.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            photo_paths.append(photo.filename)

        existing_photos = restaurant.photos.split(",") if restaurant.photos else []
        all_photos = existing_photos + photo_paths
        restaurant.photos = ",".join(all_photos)

    db.commit()
    db.refresh(restaurant)

    return {"message": "Restaurant updated successfully"}