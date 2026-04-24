import os
import shutil
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
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
from services.event_status_service import create_event_status
from services.kafka_bus import publish_event
from services.restaurant_worker_service import process_restaurant_event

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
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "profile_pic": current_user.profile_pic,
        "restaurant_details": [
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


@router.post("/profile/picture")
def upload_owner_profile_picture(
    request: Request,
    file: UploadFile = File(...),
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Not an owner")

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    _, ext = os.path.splitext(file.filename or "")
    safe_name = f"owner-{current_user.id}-{uuid.uuid4().hex}{ext or '.jpg'}"
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    image_url = f"{request.base_url}uploads/{safe_name}"

    db[C.USERS].update_one(
        {"_id": current_user.id},
        {"$set": {"profile_pic": image_url, "updated_at": datetime.utcnow()}},
    )
    return {"message": "Owner profile picture uploaded", "image_url": image_url}


@router.put("/restaurant/{restaurant_id}", status_code=202)
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

    event_id = str(uuid.uuid4())
    create_event_status(
        db,
        event_id=event_id,
        entity_type="restaurant",
        entity_id=restaurant_id,
        status="processing",
    )
    payload = {"eventId": event_id, "restaurant_id": restaurant_id, "patch": patch}
    if not publish_event("restaurant.updated", payload):
        process_restaurant_event(db, "restaurant.updated", payload)
    return {"message": "Restaurant update queued", "restaurant_id": restaurant_id, "eventId": event_id}


@router.post("/restaurants", status_code=202)
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
    event_id = str(uuid.uuid4())
    create_event_status(
        db,
        event_id=event_id,
        entity_type="restaurant",
        entity_id=rid,
        status="processing",
    )
    payload = {
        "eventId": event_id,
        "restaurant_id": rid,
        "name": name,
        "cuisine": cuisine,
        "description": description,
        "address": address,
        "city": city,
        "contact_phone": contact_phone,
        "contact_email": contact_email,
        "hours": hours,
        "pricing_tier": pricing_tier,
        "amenities": amenities,
        "photos": ",".join(photo_paths) if photo_paths else None,
        "owner_id": current_user.id,
    }
    if not publish_event("restaurant.created", payload):
        process_restaurant_event(db, "restaurant.created", payload)
    return {"message": "Restaurant queued", "restaurant_id": rid, "eventId": event_id}


@router.post("/restaurants/{restaurant_id}/claim", status_code=202)
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

    event_id = str(uuid.uuid4())
    create_event_status(
        db,
        event_id=event_id,
        entity_type="restaurant",
        entity_id=restaurant_id,
        status="processing",
    )
    payload = {"eventId": event_id, "restaurant_id": restaurant_id, "owner_id": current_user.id}
    if not publish_event("restaurant.claimed", payload):
        process_restaurant_event(db, "restaurant.claimed", payload)
    return {"message": "Restaurant claim queued", "eventId": event_id}



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
