# backend/routers/restaurants.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_

from database import get_db
from models.restaurant import Restaurant
from schemas.restaurant import RestaurantListItem

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