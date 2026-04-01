from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.database import Database

from database import get_db
import mongo_collections as C
from mongo_utils import log_activity, next_id
from schemas.owner import OwnerCreate
from services.auth_service import (
    authenticate_user,
    create_access_token,
    decode_token_jti,
    hash_password,
)

router = APIRouter(prefix="/auth/owner", tags=["Auth - Owner"])


@router.post("/signup")
def owner_signup(owner_data: OwnerCreate, db: Database = Depends(get_db)):
    if db[C.USERS].find_one({"email": owner_data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    uid = next_id(db, "users")
    hashed_pw = hash_password(owner_data.password)
    db[C.USERS].insert_one(
        {
            "_id": uid,
            "name": owner_data.name,
            "email": owner_data.email,
            "password_hash": hashed_pw,
            "role": "owner",
            "restaurant_location": owner_data.restaurant_location,
        }
    )
    log_activity(db, user_id=uid, action="owner_signup", resource="users")
    return {"message": "Owner created successfully"}


@router.post("/login")
def owner_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user.role != "owner":
        raise HTTPException(status_code=401, detail="Not an owner account")

    access_token = create_access_token(
        db, data={"sub": str(user.id), "role": user.role}
    )
    log_activity(db, user_id=user.id, action="owner_login", resource="sessions")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
    }


@router.post("/logout")
def owner_logout(
    db: Database = Depends(get_db),
    authorization: str | None = Header(None),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.replace("Bearer ", "", 1).strip()
    jti = decode_token_jti(token)
    if jti:
        db[C.SESSIONS].delete_one({"_id": jti})
    return {"message": "Logged out"}
