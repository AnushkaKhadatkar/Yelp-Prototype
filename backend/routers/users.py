from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os

from database import get_db
from models.user import User
from schemas.user import UserProfileResponse, UserProfileUpdate
from services.auth_service import get_current_user

from models.user_preference import UserPreference
from schemas.preference import PreferenceResponse, PreferenceUpdate

from models.favourite import Favourite
from models.restaurant import Restaurant

router = APIRouter(prefix="/users", tags=["Users"])


# ---------------- GET PROFILE ----------------

@router.get("/profile", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


# ---------------- UPDATE PROFILE ----------------

@router.put("/profile")
def update_profile(
    update_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully",
        "updated_user": {
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "about": current_user.about,
            "city": current_user.city,
            "state": current_user.state,
            "country": current_user.country,
            "languages": current_user.languages,
            "gender": current_user.gender,
        }
    }


# ---------------- UPLOAD PROFILE PICTURE ----------------

@router.post("/profile/picture")
def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.profile_pic = file_path
    db.commit()

    return {
        "message": "Profile picture uploaded",
        "image_url": file_path
    }

@router.get("/preferences", response_model=PreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prefs = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id
    ).first()

    if not prefs:
        return PreferenceResponse()

    return {
        "cuisines": prefs.cuisines,
        "price_range": prefs.price_range,
        "location": prefs.preferred_locations,
        "dietary_needs": prefs.dietary_needs,
        "ambiance": prefs.ambiance,
        "sort_preference": prefs.sort_preference,
    }

@router.put("/preferences")
def update_preferences(
    update_data: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prefs = db.query(UserPreference).filter(
        UserPreference.user_id == current_user.id
    ).first()

    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)

    for field, value in update_data.dict(exclude_unset=True).items():
        if field == "location":
            setattr(prefs, "preferred_locations", value)
        else:
            setattr(prefs, field, value)

    db.commit()
    db.refresh(prefs)

    return {
        "message": "Preferences updated successfully",
        "preferences": {
            "cuisines": prefs.cuisines,
            "price_range": prefs.price_range,
            "location": prefs.preferred_locations,
            "dietary_needs": prefs.dietary_needs,
            "ambiance": prefs.ambiance,
            "sort_preference": prefs.sort_preference,
        }
    }

#FAVOURITES
@router.get("/favourites")
def get_favourites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    favourites = (
        db.query(Restaurant)
        .join(Favourite, Favourite.restaurant_id == Restaurant.id)
        .filter(Favourite.user_id == current_user.id)
        .all()
    )

    return [
        {
            "id": r.id,
            "name": r.name,
            "cuisine": r.cuisine,
            "city": r.city,
            "pricing_tier": r.price_tier,
            "avg_rating": r.avg_rating,
            "photo": r.photos.split(",")[0] if r.photos else None
        }
        for r in favourites
    ]

@router.post("/favourites/{restaurant_id}")
def add_favourite(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Favourite).filter(
        Favourite.user_id == current_user.id,
        Favourite.restaurant_id == restaurant_id
    ).first()

    if existing:
        return {"message": "Already in favourites"}

    favourite = Favourite(
        user_id=current_user.id,
        restaurant_id=restaurant_id
    )

    db.add(favourite)
    db.commit()

    return {"message": "Added to favourites"}

@router.delete("/favourites/{restaurant_id}")
def remove_favourite(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    favourite = db.query(Favourite).filter(
        Favourite.user_id == current_user.id,
        Favourite.restaurant_id == restaurant_id
    ).first()

    if not favourite:
        return {"message": "Not in favourites"}

    db.delete(favourite)
    db.commit()

    return {"message": "Removed from favourites"}

