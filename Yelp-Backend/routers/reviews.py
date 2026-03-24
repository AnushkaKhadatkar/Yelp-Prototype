from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import func

from database import get_db
from models.review import Review
from models.restaurant import Restaurant
from models.user import User
from schemas.review import ReviewCreate, ReviewUpdate
from services.auth_service import get_current_user

import os
import shutil

router = APIRouter(tags=["Reviews"])


# ---------------------------------------
# CREATE REVIEW
# ---------------------------------------
@router.post("/restaurants/{restaurant_id}/reviews")
def create_review(
    restaurant_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    new_review = Review(
        user_id=current_user.id,
        restaurant_id=restaurant_id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # Recalculate avg_rating and review_count
    stats = db.query(
        func.avg(Review.rating),
        func.count(Review.id)
    ).filter(
        Review.restaurant_id == restaurant_id
    ).first()

    restaurant.avg_rating = round(float(stats[0]), 1) if stats[0] else 0
    restaurant.review_count = stats[1]

    db.commit()

    return {"message": "Review created successfully"}

### UPDATE REVIEW 

@router.put("/reviews/{review_id}")
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(Review).filter(
        Review.id == review_id
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if review_data.rating is not None:
        review.rating = review_data.rating

    if review_data.comment is not None:
        review.comment = review_data.comment

    db.commit()

    # Recalculate rating
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == review.restaurant_id
    ).first()

    stats = db.query(
        func.avg(Review.rating),
        func.count(Review.id)
    ).filter(
        Review.restaurant_id == review.restaurant_id
    ).first()

    restaurant.avg_rating = round(float(stats[0]), 1) if stats[0] else 0
    restaurant.review_count = stats[1]

    db.commit()

    return {"message": "Review updated successfully"}


@router.post("/reviews/{review_id}/photos")
def upload_review_photos(
    review_id: int,                      # ✅ FIXED
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(Review).filter(
        Review.id == review_id
    ).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Only review owner can upload photo
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    photo_paths = []

    for photo in photos:
        file_path = os.path.join(upload_dir, photo.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        photo_paths.append(photo.filename)

    review.photos = ",".join(photo_paths)

    db.commit()
    db.refresh(review)

    return {
        "message": "Review photos uploaded successfully",
        "photos": photo_paths
    }
@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    restaurant_id = review.restaurant_id
    db.delete(review)
    db.commit()
    # Recalculate avg_rating
    stats = db.query(func.avg(Review.rating), func.count(Review.id)).filter(Review.restaurant_id == restaurant_id).first()
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    restaurant.avg_rating = round(float(stats[0]), 1) if stats[0] else 0
    restaurant.review_count = stats[1]
    db.commit()
    return {"message": "Review deleted successfully"}