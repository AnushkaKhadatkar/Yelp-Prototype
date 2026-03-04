# backend/routers/restaurants.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_

from database import get_db
from models.restaurant import Restaurant
from schemas.restaurant import RestaurantListItem

from models.review import Review
from models.user import User
from schemas.restaurant import RestaurantDetailResponse, ReviewItem

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


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

    # JOIN reviews with users
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