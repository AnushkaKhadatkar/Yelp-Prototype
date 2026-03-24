from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from models.user import User
from schemas.owner import OwnerCreate
from services.auth_service import hash_password, authenticate_user, create_access_token

router = APIRouter(prefix="/auth/owner", tags=["Auth - Owner"])


@router.post("/signup")
def owner_signup(owner_data: OwnerCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == owner_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(owner_data.password)

    new_owner = User(
        name=owner_data.name,
        email=owner_data.email,
        password_hash=hashed_pw,
        role="owner",
        restaurant_location=owner_data.restaurant_location
    )

    db.add(new_owner)
    db.commit()
    db.refresh(new_owner)

    return {"message": "Owner created successfully"}


@router.post("/login")
def owner_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if user.role != "owner":
        raise HTTPException(status_code=401, detail="Not an owner account")

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }