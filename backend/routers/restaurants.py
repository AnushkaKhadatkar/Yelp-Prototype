import os
import shutil
from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pymongo.database import Database

from database import get_db
import mongo_collections as C
from mongo_utils import next_id, restaurant_doc_to_detail_dict
from schemas.restaurant import RestaurantDetailResponse
from services.auth_service import get_current_user

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


@router.get("", response_model=List[RestaurantDetailResponse])
def get_restaurants(
    search: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    zip: Optional[str] = Query(None),
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

    result = []
    for restaurant in restaurants:
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
                "photos": photos.split(",") if photos else [],
                "avg_rating": float(ar) if ar is not None else 0,
                "review_count": restaurant.get("review_count", 0),
                "reviews": reviews_list,
            }
        )
    return result


@router.get("/{restaurant_id}", response_model=RestaurantDetailResponse)
def get_restaurant_details(restaurant_id: int, db: Database = Depends(get_db)):
    restaurant = db[C.RESTAURANTS].find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    revs = list(db[C.REVIEWS].find({"restaurant_id": restaurant_id}))
    reviews_list = [_review_entry(db, r) for r in revs]
    return restaurant_doc_to_detail_dict(restaurant, reviews_list)


@router.post("")
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
    db[C.RESTAURANTS].insert_one(
        {
            "_id": rid,
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
            "price_tier": pricing_tier,
            "ambiance": ambiance,
            "amenities": amenities,
            "photos": None,
            "owner_id": current_user.id,
            "avg_rating": 0.0,
            "review_count": 0,
            "created_at": datetime.utcnow(),
        }
    )
    return {"message": "Restaurant created successfully", "restaurant_id": rid}


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
