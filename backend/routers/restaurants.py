# backend/routers/restaurants.py

from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated
from sqlalchemy import or_
import os
import shutil

from database import get_db
from models.restaurant import Restaurant
from models.review import Review
from models.user import User
from schemas.restaurant import (
    RestaurantListItem,
    RestaurantDetailResponse
)
from services.auth_service import get_current_user

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


# -----------------------
# GET ALL RESTAURANTS
# -----------------------
@router.get("", response_model=List[RestaurantListItem])
def get_restaurants(
    name: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    zip: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Restaurant)

    if name:
        query = query.filter(Restaurant.name.ilike(f"%{name}%"))

    if cuisine:
        query = query.filter(Restaurant.cuisine == cuisine)

    if keyword:
        query = query.filter(
            or_(
                Restaurant.name.ilike(f"%{keyword}%"),
                Restaurant.description.ilike(f"%{keyword}%"),
                Restaurant.amenities.ilike(f"%{keyword}%")
            )
        )

    if city:
        query = query.filter(Restaurant.city.ilike(f"%{city}%"))

    if zip:
        query = query.filter(Restaurant.zip_code == zip)

    restaurants = query.all()

    return [
        {
            "id": r.id,
            "name": r.name,
            "cuisine": r.cuisine,
            "address": r.address,
            "city": r.city,
            "avg_rating": r.avg_rating,
            "review_count": r.review_count,
            "pricing_tier": r.price_tier,
            "photo": r.photos.split(",")[0] if r.photos else None
        }
        for r in restaurants
    ]


# -----------------------
# GET RESTAURANT DETAILS
# -----------------------
@router.get("/{restaurant_id}", response_model=RestaurantDetailResponse)
def get_restaurant_details(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        return {"detail": "Restaurant not found"}

    reviews_query = (
        db.query(Review, User)
        .join(User, Review.user_id == User.id)
        .filter(Review.restaurant_id == restaurant_id)
        .all()
    )

    reviews_list = [
        {
            "review_id": review.id,
            "user_name": user.name,
            "rating": review.rating,
            "comment": review.comment,
            "photo": review.photos,
            "created_at": review.created_at.isoformat() if review.created_at else None,
        }
        for review, user in reviews_query
    ]

    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "cuisine": restaurant.cuisine,
        "address": restaurant.address,
        "city": restaurant.city,
        "description": restaurant.description,
        "hours": restaurant.hours,
        "contact_phone": restaurant.contact_phone,
        "pricing_tier": restaurant.price_tier,
        "amenities": restaurant.amenities,
        "photos": restaurant.photos.split(",") if restaurant.photos else [],
        "avg_rating": restaurant.avg_rating,
        "review_count": restaurant.review_count,
        "reviews": reviews_list
    }


# -----------------------
# CREATE RESTAURANT
# -----------------------
@router.post("")
def create_restaurant(
    name: str = Form(...),
    cuisine: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    contact_phone: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    hours: Optional[str] = Form(None),
    pricing_tier: Optional[str] = Form(None),
    amenities: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_restaurant = Restaurant(
        name=name,
        cuisine=cuisine,
        address=address,
        city=city,
        contact_phone=contact_phone,
        description=description,
        hours=hours,
        price_tier=pricing_tier,
        amenities=amenities,
        owner_id=current_user.id,
        avg_rating=0,
        review_count=0
    )

    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)

    return {
        "message": "Restaurant created successfully",
        "restaurant_id": new_restaurant.id
    }

### RESTAURANT PHOTO
@router.post("/{restaurant_id}/photos")
def upload_restaurant_photos(
    restaurant_id: int,
    photos: List[UploadFile] = File(...),
    # photos: Annotated[List[UploadFile], File(...)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

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

    return {
        "message": "Photos uploaded successfully",
        "photos": all_photos
    }