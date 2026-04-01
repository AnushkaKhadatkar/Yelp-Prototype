import os
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from pymongo.database import Database

from database import get_db
import mongo_collections as C
from mongo_utils import next_id
from schemas.owner import (
    OwnerDashboardResponse,
    OwnerRestaurantResponse,
    OwnerRestaurantReviewsResponse,
    OwnerReviewItem,
    DashboardReviewItem,
)
from services.auth_service import get_current_user

router = APIRouter(prefix="/owner", tags=["Owner"])


@router.get("/profile")
def get_owner_profile(
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    restaurants = list(db[C.RESTAURANTS].find({"owner_id": current_user.id}))
    return {
        "owner": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
        },
        "restaurants": [
            {
                "id": r["_id"],
                "name": r.get("name"),
                "cuisine": r.get("cuisine"),
                "city": r.get("city"),
                "avg_rating": r.get("avg_rating"),
            }
            for r in restaurants
        ],
    }


class OwnerProfileUpdate(BaseModel):
    name: str
    email: str


@router.put("/profile")
def update_owner_profile(
    data: OwnerProfileUpdate,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    db[C.USERS].update_one(
        {"_id": current_user.id},
        {"$set": {"name": data.name, "email": data.email, "updated_at": datetime.utcnow()}},
    )
    return {"message": "Profile updated successfully"}


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
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    restaurant = db[C.RESTAURANTS].find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.get("owner_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    patch = {
        "name": name,
        "cuisine": cuisine,
        "description": description,
        "address": address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "contact_phone": contact_phone,
        "contact_email": contact_email,
        "hours": hours,
        "price_tier": pricing_tier,
        "amenities": amenities,
        "ambiance": ambiance,
    }

    if photos:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        photo_paths = []
        for photo in photos:
            file_path = os.path.join(upload_dir, photo.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            photo_paths.append(photo.filename)
        existing = (restaurant.get("photos") or "").split(",") if restaurant.get("photos") else []
        existing = [p for p in existing if p]
        all_photos = existing + photo_paths
        patch["photos"] = ",".join(all_photos)

    db[C.RESTAURANTS].update_one({"_id": restaurant_id}, {"$set": patch})
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
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
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

    rid = next_id(db, "restaurants")
    db[C.RESTAURANTS].insert_one(
        {
            "_id": rid,
            "name": name,
            "cuisine": cuisine,
            "description": description,
            "address": address,
            "city": city,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "hours": hours,
            "price_tier": pricing_tier,
            "amenities": amenities,
            "photos": ",".join(photo_paths) if photo_paths else None,
            "owner_id": current_user.id,
            "avg_rating": 0.0,
            "review_count": 0,
            "created_at": datetime.utcnow(),
        }
    )
    doc = db[C.RESTAURANTS].find_one({"_id": rid})
    return {
        "id": doc["_id"],
        "name": doc.get("name"),
        "cuisine": doc.get("cuisine"),
        "description": doc.get("description"),
        "address": doc.get("address"),
        "city": doc.get("city"),
        "contact_phone": doc.get("contact_phone"),
        "contact_email": doc.get("contact_email"),
        "hours": doc.get("hours"),
        "pricing_tier": doc.get("price_tier"),
        "amenities": doc.get("amenities"),
        "photos": photo_paths,
        "avg_rating": doc.get("avg_rating"),
        "review_count": doc.get("review_count"),
    }


@router.post("/restaurants/{restaurant_id}/claim", response_model=OwnerRestaurantResponse)
def claim_restaurant(
    restaurant_id: int,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    restaurant = db[C.RESTAURANTS].find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.get("owner_id") == current_user.id:
        raise HTTPException(status_code=400, detail="You already own this restaurant")
    if restaurant.get("owner_id") is not None:
        raise HTTPException(status_code=409, detail="Restaurant already claimed")

    db[C.RESTAURANTS].update_one(
        {"_id": restaurant_id}, {"$set": {"owner_id": current_user.id}}
    )
    doc = db[C.RESTAURANTS].find_one({"_id": restaurant_id})
    ph = doc.get("photos") or ""
    return {
        "id": doc["_id"],
        "name": doc.get("name"),
        "cuisine": doc.get("cuisine"),
        "description": doc.get("description"),
        "address": doc.get("address"),
        "city": doc.get("city"),
        "contact_phone": doc.get("contact_phone"),
        "contact_email": doc.get("contact_email"),
        "hours": doc.get("hours"),
        "pricing_tier": doc.get("price_tier"),
        "amenities": doc.get("amenities"),
        "photos": ph.split(",") if ph else [],
        "avg_rating": doc.get("avg_rating"),
        "review_count": doc.get("review_count"),
    }


@router.get("/restaurants/{restaurant_id}/reviews", response_model=OwnerRestaurantReviewsResponse)
def get_owner_restaurant_reviews(
    restaurant_id: int,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    restaurant = db[C.RESTAURANTS].find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.get("owner_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    reviews = list(db[C.REVIEWS].find({"restaurant_id": restaurant_id}))
    review_list = []
    for review in reviews:
        user = db[C.USERS].find_one({"_id": review["user_id"]})
        review_list.append(
            OwnerReviewItem(
                review_id=review["_id"],
                user_name=user.get("name") if user else "",
                rating=review.get("rating"),
                comment=review.get("comment"),
                created_at=review.get("created_at"),
            )
        )

    return OwnerRestaurantReviewsResponse(
        restaurant_id=restaurant["_id"],
        restaurant_name=restaurant.get("name"),
        reviews=review_list,
    )


@router.get("/dashboard", response_model=OwnerDashboardResponse)
def owner_dashboard(
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    restaurants = list(db[C.RESTAURANTS].find({"owner_id": current_user.id}))
    restaurant_ids = [r["_id"] for r in restaurants]

    if not restaurant_ids:
        return OwnerDashboardResponse(
            total_review_count=0,
            avg_rating=0.0,
            ratings_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            recent_reviews=[],
            sentiment_summary="No reviews yet.",
        )

    match = {"restaurant_id": {"$in": restaurant_ids}}
    total_reviews = db[C.REVIEWS].count_documents(match)

    pipeline_avg = [
        {"$match": match},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}}},
    ]
    agg = list(db[C.REVIEWS].aggregate(pipeline_avg))
    avg_rating = round(float(agg[0]["avg"]), 2) if agg and agg[0].get("avg") else 0.0

    ratings_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for row in db[C.REVIEWS].aggregate(
        [
            {"$match": match},
            {"$group": {"_id": "$rating", "c": {"$sum": 1}}},
        ]
    ):
        r = row["_id"]
        if r in ratings_distribution:
            ratings_distribution[r] = int(row["c"])

    recent = list(
        db[C.REVIEWS]
        .find(match)
        .sort("created_at", -1)
        .limit(5)
    )
    recent_reviews = []
    for review in recent:
        rest = db[C.RESTAURANTS].find_one({"_id": review["restaurant_id"]})
        recent_reviews.append(
            DashboardReviewItem(
                review_id=review["_id"],
                restaurant_name=rest.get("name") if rest else "",
                rating=review.get("rating"),
                comment=review.get("comment"),
                created_at=review.get("created_at"),
            )
        )

    comments = [r.get("comment") for r in db[C.REVIEWS].find(match)]
    all_comments = " ".join([c for c in comments if c])
    if not all_comments:
        sentiment_summary = "No reviews available yet."
    else:
        sentiment_summary = (
            f"Overall sentiment appears positive based on {total_reviews} reviews."
        )

    return OwnerDashboardResponse(
        total_review_count=total_reviews,
        avg_rating=avg_rating,
        ratings_distribution=ratings_distribution,
        recent_reviews=recent_reviews,
        sentiment_summary=sentiment_summary,
    )
