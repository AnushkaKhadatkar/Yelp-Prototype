import os
import shutil
import uuid
from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pymongo.database import Database

from database import get_db
import mongo_collections as C
from mongo_utils import next_id, restaurant_doc_to_detail_dict
from schemas.restaurant import RestaurantDetailResponse
from services.event_status_service import create_event_status
from services.auth_service import get_current_user
from services.kafka_bus import publish_event
from services.restaurant_worker_service import process_restaurant_event

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

_SEARCH_FALLBACK_CUISINE = {
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


def _review_entry(db: Database, review: dict) -> dict:
    user = db[C.USERS].find_one({"_id": review["user_id"]})
    user_name = user.get("name") if user else ""
    photos = review.get("photos") or ""
    ca = review.get("created_at")
    return {
        "review_id": review["_id"],
        "user_id": review["user_id"],
        "user_name": user_name,
        "rating": review.get("rating"),
        "comment": review.get("comment"),
        "photo": photos,
        "photos": photos.split(",") if photos else [],
        "created_at": ca.isoformat() if hasattr(ca, "isoformat") and ca else None,
    }


def _list_restaurants_query(
    db: Database,
    *,
    name: Optional[str],
    search_term_value: Optional[str],
    cuisine: Optional[str],
    city: Optional[str],
    zip_code: Optional[str],
):
    conds: list = []
    if name:
        conds.append({"name": {"$regex": name, "$options": "i"}})
    if search_term_value:
        st = search_term_value
        conds.append(
            {
                "$or": [
                    {"name": {"$regex": st, "$options": "i"}},
                    {"description": {"$regex": st, "$options": "i"}},
                    {"cuisine": {"$regex": st, "$options": "i"}},
                    {"amenities": {"$regex": st, "$options": "i"}},
                ]
            }
        )
    if cuisine and cuisine != "All":
        conds.append({"cuisine": cuisine})
    if city:
        conds.append({"city": {"$regex": city, "$options": "i"}})
    if zip_code:
        conds.append({"zip_code": zip_code})

    if not conds:
        return list(db[C.RESTAURANTS].find({}))
    if len(conds) == 1:
        return list(db[C.RESTAURANTS].find(conds[0]))
    return list(db[C.RESTAURANTS].find({"$and": conds}))


@router.get("")
def get_restaurants(
    search: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    zip: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=100),
    db: Database = Depends(get_db),
):
    search_term_value = search or keyword
    restaurants = _list_restaurants_query(
        db,
        name=name,
        search_term_value=search_term_value,
        cuisine=cuisine,
        city=city,
        zip_code=zip,
    )

    if (
        not restaurants
        and search_term_value
        and not cuisine
        and not name
    ):
        inferred = _infer_cuisine_from_text(search_term_value)
        if inferred:
            restaurants = _list_restaurants_query(
                db,
                name=None,
                search_term_value=None,
                cuisine=inferred,
                city=city,
                zip_code=zip,
            )

    total = len(restaurants)
    start = (page - 1) * limit
    end = start + limit
    rows = restaurants[start:end]
    result = []
    for restaurant in rows:
        rid = restaurant["_id"]
        revs = list(db[C.REVIEWS].find({"restaurant_id": rid}))
        reviews_list = [_review_entry(db, r) for r in revs]
        photos = restaurant.get("photos") or ""
        ar = restaurant.get("avg_rating")
        result.append(
            {
                "id": rid,
                "name": restaurant.get("name"),
                "cuisine": restaurant.get("cuisine"),
                "address": restaurant.get("address"),
                "city": restaurant.get("city"),
                "description": restaurant.get("description"),
                "hours": restaurant.get("hours"),
                "contact_phone": restaurant.get("contact_phone"),
                "pricing_tier": restaurant.get("price_tier"),
                "amenities": restaurant.get("amenities"),
                "photo": photos.split(",")[0] if photos else None,
                "avg_rating": float(ar) if ar is not None else 0,
                "review_count": restaurant.get("review_count", 0),
            }
        )
    return {"restaurants": result, "total": total, "page": page, "limit": limit}


@router.get("/{restaurant_id}", response_model=RestaurantDetailResponse)
def get_restaurant_details(restaurant_id: int, db: Database = Depends(get_db)):
    restaurant = db[C.RESTAURANTS].find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    revs = list(
        db[C.REVIEWS]
        .find({"restaurant_id": restaurant_id})
        .sort("created_at", -1)
        .limit(10)
    )
    reviews_list = [_review_entry(db, r) for r in revs]
    detail = restaurant_doc_to_detail_dict(restaurant, reviews_list)
    detail["createdAt"] = (
        restaurant.get("created_at").isoformat()
        if restaurant.get("created_at") and hasattr(restaurant.get("created_at"), "isoformat")
        else None
    )
    detail["contact"] = detail.get("contact_phone")
    return detail


@router.post("", status_code=202)
def create_restaurant(
    name: str = Form(...),
    cuisine: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(...),
    contact_phone: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    hours: Optional[str] = Form(None),
    pricing_tier: Optional[str] = Form(None),
    ambiance: Optional[str] = Form(None),
    amenities: Optional[str] = Form(None),
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
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
        "address": address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "contact_phone": contact_phone,
        "contact_email": contact_email,
        "description": description,
        "hours": hours,
        "pricing_tier": pricing_tier,
        "ambiance": ambiance,
        "amenities": amenities,
        "photos": None,
        "owner_id": current_user.id,
    }
    if not publish_event("restaurant.created", payload):
        process_restaurant_event(db, "restaurant.created", payload)
    return {"message": "Restaurant queued", "restaurant_id": rid, "eventId": event_id}


@router.put("/{restaurant_id}", status_code=202)
def update_restaurant(
    restaurant_id: int,
    name: Optional[str] = Form(None),
    cuisine: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    contact: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    hours: Optional[str] = Form(None),
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    restaurant = db[C.RESTAURANTS].find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    patch = {}
    if name is not None:
        patch["name"] = name
    if cuisine is not None:
        patch["cuisine"] = cuisine
    if address is not None:
        patch["address"] = address
    if city is not None:
        patch["city"] = city
    if contact is not None:
        patch["contact_phone"] = contact
    if description is not None:
        patch["description"] = description
    if hours is not None:
        patch["hours"] = hours
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


@router.delete("/{restaurant_id}", status_code=202)
def delete_restaurant(
    restaurant_id: int,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    restaurant = db[C.RESTAURANTS].find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    event_id = str(uuid.uuid4())
    create_event_status(
        db,
        event_id=event_id,
        entity_type="restaurant",
        entity_id=restaurant_id,
        status="processing",
    )
    payload = {"eventId": event_id, "restaurant_id": restaurant_id}
    if not publish_event("restaurant.deleted", payload):
        process_restaurant_event(db, "restaurant.deleted", payload)
    return {"message": "Restaurant delete queued", "eventId": event_id}


@router.post("/{restaurant_id}/photos")
def upload_restaurant_photos(
    restaurant_id: int,
    photos: Annotated[List[UploadFile], File()],
    db: Database = Depends(get_db),
):
    restaurant = db[C.RESTAURANTS].find_one({"_id": restaurant_id})
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

    existing = (restaurant.get("photos") or "").split(",") if restaurant.get("photos") else []
    existing = [p for p in existing if p]
    all_photos = existing + photo_paths
    db[C.RESTAURANTS].update_one(
        {"_id": restaurant_id},
        {"$set": {"photos": ",".join(all_photos)}},
    )
    return {"message": "Photos uploaded successfully", "photos": all_photos}
