from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, TokenResponse
from services.auth_service import hash_password, authenticate_user, create_access_token

router = APIRouter(prefix="/auth/user", tags=["Auth"])


# ----------------- SIGNUP -----------------

@router.post("/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_pw = hash_password(user_data.password)

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_pw,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id
    }


# ----------------- LOGIN -----------------

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return {
    "access_token": access_token,
    "token_type": "bearer",
    "token": access_token,
    "user_id": user.id,
    "role": user.role
}