import json
import os
import shutil
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, File, Request, UploadFile
from pymongo.database import Database

from database import get_db
import mongo_collections as C
from schemas.preference import PreferenceResponse, PreferenceUpdate
from schemas.user import UserHistoryResponse, UserProfileResponse, UserProfileUpdate
from services.auth_service import get_current_user
from services.kafka_bus import publish_event

router = APIRouter(prefix="/users", tags=["Users"])


def _public_user_upload_base(request: Request) -> str:
    # Prefer explicit public base URL for stable media links in Docker/local.
    explicit = os.getenv("USER_PUBLIC_BASE_URL")
    if explicit:
        return explicit.rstrip("/")
    # Fallback to direct local service port.
    return "http://127.0.0.1:8001"


def _repair_profile_pic_if_missing(db: Database, current_user) -> str | None:
    profile_pic = getattr(current_user, "profile_pic", None)
    if not profile_pic:
        return None

    marker = "/uploads/"
    if marker not in profile_pic:
        return profile_pic

    filename = profile_pic.split(marker, 1)[1].strip("/")
    if not filename:
        return None

    file_path = os.path.join("uploads", filename)
    if os.path.exists(file_path):
        return profile_pic

    # Self-heal stale URLs after container/image resets:
    # pick latest existing file for this user, else clear broken URL.
    user_prefix = f"user-{current_user.id}-"
    try:
        candidates = [
            f for f in os.listdir("uploads")
            if f.startswith(user_prefix)
        ]
    except FileNotFoundError:
        candidates = []

    if candidates:
        candidates.sort(key=lambda f: os.path.getmtime(os.path.join("uploads", f)), reverse=True)
        repaired = f"http://127.0.0.1:8001/uploads/{candidates[0]}"
        db[C.USERS].update_one({"_id": current_user.id}, {"$set": {"profile_pic": repaired}})
        return repaired

    db[C.USERS].update_one({"_id": current_user.id}, {"$set": {"profile_pic": None}})
    return None


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    created_at = (
        current_user.created_at.isoformat()
        if hasattr(current_user.created_at, "isoformat") and current_user.created_at
        else None
    )
    profile_pic = _repair_profile_pic_if_missing(db, current_user)
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "about": current_user.about,
        "city": current_user.city,
        "country": current_user.country,
        "languages": current_user.languages,
        "gender": current_user.gender,
        "profile_pic": profile_pic,
        "createdAt": created_at,
    }


@router.put("/profile")
def update_profile(
    update_data: UserProfileUpdate,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    raw = {k: v for k, v in update_data.model_dump(exclude_unset=True).items()}
    if not raw:
        return {"message": "No changes", "updated_user": {}}

    raw["updated_at"] = datetime.utcnow()
    db[C.USERS].update_one({"_id": current_user.id}, {"$set": raw})
    publish_event(
        "user.updated",
        {
            "eventId": f"user-updated-{current_user.id}-{int(datetime.utcnow().timestamp())}",
            "user_id": current_user.id,
            "changed_fields": raw,
        },
    )
    doc = db[C.USERS].find_one({"_id": current_user.id})
    return {
        "message": "Profile updated successfully",
        "updated_user": {
            "name": doc.get("name"),
            "email": doc.get("email"),
            "phone": doc.get("phone"),
            "about": doc.get("about"),
            "city": doc.get("city"),
            "state": doc.get("state"),
            "country": doc.get("country"),
            "languages": doc.get("languages"),
            "gender": doc.get("gender"),
        },
    }


@router.post("/profile/picture")
def upload_profile_picture(
    request: Request,
    file: UploadFile = File(...),
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    _, ext = os.path.splitext(file.filename or "")
    safe_name = f"user-{current_user.id}-{int(datetime.utcnow().timestamp())}{ext or '.jpg'}"
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    image_url = f"{_public_user_upload_base(request)}/uploads/{safe_name}"

    db[C.USERS].update_one(
        {"_id": current_user.id}, {"$set": {"profile_pic": image_url}}
    )
    return {"message": "Profile picture uploaded", "image_url": image_url}


def parse_list(val: Any):
    if not val:
        return []
    if isinstance(val, list):
        return val
    try:
        return json.loads(val)
    except Exception:
        return [v.strip() for v in str(val).split(",") if v.strip()]


@router.get("/preferences", response_model=PreferenceResponse)
def get_preferences(
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    prefs = db[C.USER_PREFERENCES].find_one({"user_id": current_user.id})
    if not prefs:
        return PreferenceResponse()

    return {
        "cuisines": parse_list(prefs.get("cuisines")),
        "price_range": prefs.get("price_range"),
        "location": prefs.get("preferred_locations"),
        "dietary_needs": parse_list(prefs.get("dietary_needs")),
        "ambiance": parse_list(prefs.get("ambiance")),
        "sort_preference": prefs.get("sort_preference"),
    }


@router.put("/preferences")
def update_preferences(
    update_data: PreferenceUpdate,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing = db[C.USER_PREFERENCES].find_one({"user_id": current_user.id})
    patch: dict = {}
    data = update_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        if field == "location":
            patch["preferred_locations"] = value
        elif isinstance(value, list):
            patch[field] = json.dumps(value)
        else:
            patch[field] = value

    if existing:
        db[C.USER_PREFERENCES].update_one(
            {"user_id": current_user.id}, {"$set": patch}
        )
        prefs = db[C.USER_PREFERENCES].find_one({"user_id": current_user.id})
    else:
        patch["user_id"] = current_user.id
        db[C.USER_PREFERENCES].insert_one(patch)
        prefs = db[C.USER_PREFERENCES].find_one({"user_id": current_user.id})

    return {
        "message": "Preferences updated successfully",
        "preferences": {
            "cuisines": prefs.get("cuisines"),
            "price_range": prefs.get("price_range"),
            "location": prefs.get("preferred_locations"),
            "dietary_needs": prefs.get("dietary_needs"),
            "ambiance": prefs.get("ambiance"),
            "sort_preference": prefs.get("sort_preference"),
        },
    }


@router.get("/favourites")
def get_favourites(
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    favs = list(
        db[C.FAVOURITES].find({"user_id": current_user.id})
    )
    out = []
    for f in favs:
        r = db[C.RESTAURANTS].find_one({"_id": f["restaurant_id"]})
        if not r:
            continue
        photos = r.get("photos") or ""
        out.append(
            {
                "id": r["_id"],
                "name": r.get("name"),
                "cuisine": r.get("cuisine"),
                "city": r.get("city"),
                "pricing_tier": r.get("price_tier"),
                "avg_rating": r.get("avg_rating"),
                "photo": photos.split(",")[0] if photos else None,
            }
        )
    return out


@router.post("/favourites/{restaurant_id}")
def add_favourite(
    restaurant_id: int,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing = db[C.FAVOURITES].find_one(
        {"user_id": current_user.id, "restaurant_id": restaurant_id}
    )
    if existing:
        return {"message": "Already in favourites", "restaurant_id": restaurant_id}

    from mongo_utils import next_id

    fid = next_id(db, "favourites")
    db[C.FAVOURITES].insert_one(
        {
            "_id": fid,
            "user_id": current_user.id,
            "restaurant_id": restaurant_id,
        }
    )
    return {"message": "Added to favourites", "restaurant_id": restaurant_id}



@router.delete("/favourites/{restaurant_id}")
def remove_favourite(
    restaurant_id: int,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db[C.FAVOURITES].delete_one(
        {"user_id": current_user.id, "restaurant_id": restaurant_id}
    )
    return {"message": "Removed from favourites", "restaurant_id": restaurant_id}


@router.get("/history", response_model=UserHistoryResponse)
def get_user_history(
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    review_results = list(
        db[C.REVIEWS].find({"user_id": current_user.id}).sort("created_at", -1)
    )
    reviews = []
    for review in review_results:
        restaurant = db[C.RESTAURANTS].find_one({"_id": review["restaurant_id"]})
        if not restaurant:
            continue
        ca = review.get("created_at")
        reviews.append(
            {
                "review_id": review["_id"],
                "restaurant_id": restaurant["_id"],
                "restaurant_name": restaurant.get("name"),
                "rating": review.get("rating"),
                "comment": review.get("comment"),
                "created_at": ca.isoformat() if hasattr(ca, "isoformat") else None,
            }
        )

    restaurants_added = []
    for r in db[C.RESTAURANTS].find({"owner_id": current_user.id}):
        ca = r.get("created_at")
        restaurants_added.append(
            {
                "id": r["_id"],
                "name": r.get("name"),
                "cuisine": r.get("cuisine"),
                "address": r.get("address"),
                "city": r.get("city"),
                "created_at": ca.isoformat() if hasattr(ca, "isoformat") else None,
            }
        )

    return UserHistoryResponse(reviews=reviews, restaurants_added=restaurants_added)
