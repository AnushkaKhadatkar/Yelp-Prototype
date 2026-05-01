import os
import shutil
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from pymongo.database import Database

from database import get_db
import mongo_collections as C
from mongo_utils import next_id
from schemas.review import ReviewCreate, ReviewUpdate
from services.event_status_service import create_event_status, get_event_status
from services.auth_service import get_current_user
from services.kafka_bus import publish_event
from services.review_worker_service import process_review_event

router = APIRouter(tags=["Reviews"])


def _public_review_upload_base(request: Request) -> str:
    explicit = os.getenv("REVIEW_PUBLIC_BASE_URL")
    if explicit:
        return explicit.rstrip("/")
    return "http://127.0.0.1:8004"


@router.post("/restaurants/{restaurant_id}/reviews", status_code=202)
def create_review(
    restaurant_id: int,
    review_data: ReviewCreate,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rid = next_id(db, "reviews")
    event_id = str(uuid.uuid4())
    create_event_status(
        db,
        event_id=event_id,
        entity_type="review",
        entity_id=rid,
        status="processing",
    )
    payload = {
        "eventId": event_id,
        "review_id": rid,
        "restaurant_id": restaurant_id,
        "user_id": current_user.id,
        "rating": review_data.rating,
        "comment": review_data.comment,
        "photos": None,
    }
    if not publish_event("review.created", payload):
        process_review_event(db, "review.created", payload)
    return {
        "message": "Review queued",
        "review_id": rid,
        "eventId": event_id,
        "date": datetime.utcnow().isoformat(),
    }


@router.put("/reviews/{review_id}", status_code=202)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    review = db[C.REVIEWS].find_one({"_id": review_id})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    patch = review_data.model_dump(exclude_unset=True)
    event_id = str(uuid.uuid4())
    create_event_status(
        db,
        event_id=event_id,
        entity_type="review",
        entity_id=review_id,
        status="processing",
    )
    payload = {"eventId": event_id, "review_id": review_id, "patch": patch}
    if not publish_event("review.updated", payload):
        process_review_event(db, "review.updated", payload)
    return {"message": "Review update queued", "review_id": review_id, "eventId": event_id}


@router.post("/reviews/{review_id}/photos")
def upload_review_photos(
    review_id: int,
    request: Request,
    photos: List[UploadFile] = File(...),
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    review = db[C.REVIEWS].find_one({"_id": review_id})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    photo_paths = []
    for photo in photos:
        _, ext = os.path.splitext(photo.filename or "")
        safe_name = f"review-{review_id}-{uuid.uuid4().hex}{ext or '.jpg'}"
        file_path = os.path.join(upload_dir, safe_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_paths.append(f"{_public_review_upload_base(request)}/uploads/{safe_name}")

    db[C.REVIEWS].update_one(
        {"_id": review_id},
        {"$set": {"photos": ",".join(photo_paths)}},
    )
    return {"message": "Review photos uploaded successfully", "photos": photo_paths}


@router.delete("/reviews/{review_id}", status_code=202)
def delete_review(
    review_id: int,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    review = db[C.REVIEWS].find_one({"_id": review_id})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    event_id = str(uuid.uuid4())
    create_event_status(
        db,
        event_id=event_id,
        entity_type="review",
        entity_id=review_id,
        status="processing",
    )
    payload = {"eventId": event_id, "review_id": review_id}
    if not publish_event("review.deleted", payload):
        process_review_event(db, "review.deleted", payload)
    return {"message": "Review delete queued", "eventId": event_id}


@router.get("/events/status/{event_id}")
def event_status(
    event_id: str,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    status_doc = get_event_status(db, event_id)
    if not status_doc:
        raise HTTPException(status_code=404, detail="Event not found")
    return {
        "eventId": status_doc["eventId"],
        "status": status_doc["status"],
        "result": status_doc.get("result"),
        "error": status_doc.get("error"),
    }


@router.get("/reviews/{review_id}/status")
def review_status(
    review_id: int,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    status_doc = db[C.EVENT_STATUS].find_one(
        {"entity_type": "review", "entity_id": review_id}, sort=[("updated_at", -1)]
    )
    if not status_doc:
        raise HTTPException(status_code=404, detail="Status not found")
    return {"review_id": review_id, "status": status_doc.get("status", "processing")}


@router.get("/restaurants/{restaurant_id}/reviews")
def get_reviews_by_restaurant(
    restaurant_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Database = Depends(get_db),
):
    skip = (page - 1) * limit
    total = db[C.REVIEWS].count_documents({"restaurant_id": restaurant_id})
    rows = (
        db[C.REVIEWS]
        .find({"restaurant_id": restaurant_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    out = []
    for r in rows:
        user = db[C.USERS].find_one({"_id": r["user_id"]})
        st = db[C.EVENT_STATUS].find_one(
            {"entity_type": "review", "entity_id": r["_id"]}, sort=[("updated_at", -1)]
        )
        photos = r.get("photos") or ""
        out.append(
            {
                "id": r["_id"],
                "user_name": user.get("name") if user else "",
                "rating": r.get("rating"),
                "comment": r.get("comment"),
                "photos": photos.split(",") if photos else [],
                "date": r.get("created_at").isoformat() if r.get("created_at") else None,
                "status": st.get("status", "saved") if st else "saved",
            }
        )
    return {"reviews": out, "total": total, "page": page, "limit": limit}
