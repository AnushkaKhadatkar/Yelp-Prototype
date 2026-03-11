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

from schemas.owner import OwnerRestaurantResponse
from schemas.owner import OwnerProfileResponse

router = APIRouter(prefix="/owner", tags=["Owner"])


# =====================================================
# GET OWNER PROFILE
# =====================================================

@router.get("/profile", response_model=OwnerProfileResponse)
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


@router.post("/restaurants", response_model=OwnerRestaurantResponse)
def create_owner_restaurant(
    name: str = Form(...),
    cuisine: str = Form(...),
    description: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    hours: Optional[str] = Form(None),
    pricing_tier: Optional[str] = Form(None),
    amenities: Optional[str] = Form(None),
    photos: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    photo_paths = []

    if photos:
        for photo in photos:
            file_path = os.path.join(upload_dir, photo.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            photo_paths.append(photo.filename)

    restaurant = Restaurant(
        name=name,
        cuisine=cuisine,
        description=description,
        address=address,
        city=city,
        contact_phone=contact_phone,
        contact_email=contact_email,
        hours=hours,
        price_tier=pricing_tier,
        amenities=amenities,
        photos=",".join(photo_paths) if photo_paths else None,
        owner_id=current_user.id,
        avg_rating=0,
        review_count=0
    )

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "cuisine": restaurant.cuisine,
        "description": restaurant.description,
        "address": restaurant.address,
        "city": restaurant.city,
        "contact_phone": restaurant.contact_phone,
        "contact_email": restaurant.contact_email,
        "hours": restaurant.hours,
        "pricing_tier": restaurant.price_tier,
        "amenities": restaurant.amenities,
        "photos": photo_paths,
        "avg_rating": restaurant.avg_rating,
        "review_count": restaurant.review_count
    }

@router.post("/restaurants/{restaurant_id}/claim", response_model=OwnerRestaurantResponse)
def claim_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    if restaurant.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You already own this restaurant")

    if restaurant.owner_id is not None:
        raise HTTPException(status_code=409, detail="Restaurant already claimed")

    restaurant.owner_id = current_user.id
    db.commit()
    db.refresh(restaurant)

    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "cuisine": restaurant.cuisine,
        "description": restaurant.description,
        "address": restaurant.address,
        "city": restaurant.city,
        "contact_phone": restaurant.contact_phone,
        "contact_email": restaurant.contact_email,
        "hours": restaurant.hours,
        "pricing_tier": restaurant.price_tier,
        "amenities": restaurant.amenities,
        "photos": restaurant.photos.split(",") if restaurant.photos else [],
        "avg_rating": restaurant.avg_rating,
        "review_count": restaurant.review_count
    }