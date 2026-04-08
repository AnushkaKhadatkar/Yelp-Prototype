from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from database import get_db
import mongo_collections as C
from mongo_utils import log_activity, next_id
from schemas.owner import OwnerCreate
from schemas.user import UserLogin
from services.auth_service import (
    authenticate_user,
    create_access_token,
    get_token_ttl_seconds,
    hash_password,
)
from services.kafka_bus import publish_event

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
    publish_event(
        "user.created",
        {
            "eventId": f"user-created-{uid}",
            "user_id": uid,
            "email": owner_data.email,
            "name": owner_data.name,
            "role": "owner",
        },
    )
    log_activity(db, user_id=uid, action="owner_signup", resource="users")
    return {"message": "Owner created successfully", "owner_id": uid}


@router.post("/login")
def owner_login(
    payload: UserLogin,
    db: Database = Depends(get_db),
):
    user = authenticate_user(db, payload.email, payload.password)
    if user.role != "owner":
        raise HTTPException(status_code=401, detail="Not an owner account")

    access_token = create_access_token(
        db, data={"sub": str(user.id), "role": user.role}
    )
    log_activity(db, user_id=user.id, action="owner_login", resource="sessions")
    return {
        "token": access_token,
        "owner_id": user.id,
        "role": user.role,
        "expiresIn": get_token_ttl_seconds(),
    }
