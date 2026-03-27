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

_SEARCH_FALLBACK_CUISINE = {
    # Common food keywords → likely cuisine bucket in our dataset
    "burger": "American",
    "burgers": "American",
    "bbq": "American",
    "barbecue": "American",
    "steak": "American",
    "wings": "American",
    "taco": "Mexican",
    "tacos": "Mexican",
    "burrito": "Mexican",
    "burritos": "Mexican",
    "pizza": "Italian",
    "pasta": "Italian",
    "ramen": "Japanese",
    "sushi": "Japanese",
    "curry": "Indian",
    "biryani": "Indian",
    "dumpling": "Chinese",
    "dumplings": "Chinese",
    "dim sum": "Chinese",
}


def _infer_cuisine_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    t = text.lower().strip()
    for k, v in _SEARCH_FALLBACK_CUISINE.items():
        if k in t:
            return v
    return None


# -----------------------
# GET ALL RESTAURANTS
# -----------------------
@router.get("", response_model=List[RestaurantDetailResponse])
def get_restaurants(
    search: Optional[str] = Query(None),
    name: Optional[str] = Query(None),   
    cuisine: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    zip: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Restaurant)

    # Explicit name filter (frontend may send `name`)
    if name:
        query = query.filter(Restaurant.name.ilike(f"%{name}%"))

    search_term_value = search or keyword

    if search_term_value:
        search_term = f"%{search_term_value}%"
        query = query.filter(
            or_(
            Restaurant.name.ilike(search_term),
            Restaurant.description.ilike(search_term),
            Restaurant.cuisine.ilike(search_term),
            Restaurant.amenities.ilike(search_term)
            )
        )

    if cuisine and cuisine != "All":
        query = query.filter(Restaurant.cuisine == cuisine)

    if city:
        query = query.filter(Restaurant.city.ilike(f"%{city}%"))

    if zip:
        query = query.filter(Restaurant.zip_code == zip)

    restaurants = query.all()

    # If the user's keyword produced no direct matches, do a small, user-friendly fallback:
    # infer a cuisine bucket from common food words (e.g., "burger" → American).
    if (
        not restaurants
        and search_term_value
        and not cuisine
        and not name
    ):
        inferred_cuisine = _infer_cuisine_from_text(search_term_value)
        if inferred_cuisine:
            fallback_query = db.query(Restaurant).filter(Restaurant.cuisine == inferred_cuisine)
            if city:
                fallback_query = fallback_query.filter(Restaurant.city.ilike(f"%{city}%"))
            if zip:
                fallback_query = fallback_query.filter(Restaurant.zip_code == zip)
            restaurants = fallback_query.all()

    result = []

    for restaurant in restaurants:

        reviews_query = (
            db.query(Review, User)
            .join(User, Review.user_id == User.id)
            .filter(Review.restaurant_id == restaurant.id)
            .all()
        )

        reviews_list = [
            {
                "review_id": review.id,
                "user_id": review.user_id,
                "user_name": user.name,
                "rating": review.rating,
                "comment": review.comment,
                "photo": review.photos,
                "photos": review.photos.split(",") if review.photos else [],
                "created_at": review.created_at.isoformat() if review.created_at else None,
            }
            for review, user in reviews_query
        ]

        result.append({
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
            "avg_rating": float(restaurant.avg_rating) if restaurant.avg_rating else 0,
            "review_count": restaurant.review_count,
            "reviews": reviews_list
        })

    return result

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
            "user_id": review.user_id,
            "user_name": user.name,
            "rating": review.rating,
            "comment": review.comment,
            "photo": review.photos,
            "photos": review.photos.split(",") if review.photos else [],
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
    "state": restaurant.state,
    "zip_code": restaurant.zip_code,
    "description": restaurant.description,
    "hours": restaurant.hours,
    "contact_phone": restaurant.contact_phone,
    "contact_email": restaurant.contact_email,
    "pricing_tier": restaurant.price_tier,
    "ambiance": restaurant.ambiance,
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
    # REQUIRED
    name: str = Form(...),
    cuisine: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(...),

    # OPTIONAL
    contact_phone: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    hours: Optional[str] = Form(None),
    pricing_tier: Optional[str] = Form(None),
    ambiance: Optional[str] = Form(None),
    amenities: Optional[str] = Form(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_restaurant = Restaurant(
        name=name,
        cuisine=cuisine,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        contact_phone=contact_phone,
        contact_email=contact_email,
        description=description,
        hours=hours,
        price_tier=pricing_tier,
        ambiance=ambiance,
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
    photos: Annotated[List[UploadFile], File()],
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
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