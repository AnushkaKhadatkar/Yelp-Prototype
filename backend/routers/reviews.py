import os
import shutil
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pymongo.database import Database

from database import get_db
import mongo_collections as C
from mongo_utils import next_id, recalc_restaurant_stats
from schemas.review import ReviewCreate, ReviewUpdate
from services.auth_service import get_current_user

router = APIRouter(tags=["Reviews"])


@router.post("/restaurants/{restaurant_id}/reviews")
def create_review(
    restaurant_id: int,
    review_data: ReviewCreate,
    db: Database = Depends(get_db),
    current_user=Depends(get_current_user),
):
    restaurant = db[C.RESTAURANTS].find_one({"_id": restaurant_id})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    rid = next_id(db, "reviews")
    db[C.REVIEWS].insert_one(
        {
            "_id": rid,
            "user_id": current_user.id,
            "restaurant_id": restaurant_id,
            "rating": review_data.rating,
            "comment": review_data.comment,
            "photos": None,
            "created_at": datetime.utcnow(),
        }
    )
    recalc_restaurant_stats(db, restaurant_id)
    return {"message": "Review created successfully", "review_id": rid}


@router.put("/reviews/{review_id}")
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
    if patch:
        db[C.REVIEWS].update_one({"_id": review_id}, {"$set": patch})

    recalc_restaurant_stats(db, review["restaurant_id"])
    return {"message": "Review updated successfully"}


@router.post("/reviews/{review_id}/photos")
def upload_review_photos(
    review_id: int,
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
        file_path = os.path.join(upload_dir, photo.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photo_paths.append(photo.filename)

    db[C.REVIEWS].update_one(
        {"_id": review_id},
        {"$set": {"photos": ",".join(photo_paths)}},
    )
    return {"message": "Review photos uploaded successfully", "photos": photo_paths}


@router.delete("/reviews/{review_id}")
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
    restaurant_id = review["restaurant_id"]
    db[C.REVIEWS].delete_one({"_id": review_id})
    recalc_restaurant_stats(db, restaurant_id)
    return {"message": "Review deleted successfully"}
