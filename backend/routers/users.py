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

