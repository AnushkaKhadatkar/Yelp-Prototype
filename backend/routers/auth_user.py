from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from database import get_db
import mongo_collections as C
from mongo_utils import log_activity, next_id
from schemas.user import UserCreate, UserLogin
from services.auth_service import (
    authenticate_user,
    create_access_token,
    get_token_ttl_seconds,
    hash_password,
)
from services.kafka_bus import publish_event

router = APIRouter(prefix="/auth/user", tags=["Auth - User"])


@router.post("/signup")
def signup(user_data: UserCreate, db: Database = Depends(get_db)):
    normalized_email = user_data.email.strip().lower()
    if db[C.USERS].find_one({"email": normalized_email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    uid = next_id(db, "users")
    hashed_pw = hash_password(user_data.password)
    db[C.USERS].insert_one(
        {
            "_id": uid,
            "name": user_data.name,
            "email": normalized_email,
            "password_hash": hashed_pw,
            "role": "user",
        }
    )
    publish_event(
        "user.created",
        {"eventId": f"user-created-{uid}", "user_id": uid, "email": normalized_email, "name": user_data.name, "role": "user"},
    )
    log_activity(db, user_id=uid, action="user_signup", resource="users")
    return {"message": "User created successfully", "user_id": uid}


@router.post("/login")
def login(
    payload: UserLogin,
    db: Database = Depends(get_db),
):
    user = authenticate_user(db, payload.email, payload.password)
    access_token = create_access_token(
        db, data={"sub": str(user.id), "role": user.role}
    )
    log_activity(db, user_id=user.id, action="user_login", resource="sessions")
    return {
        "token": access_token,
        "user_id": user.id,
        "role": user.role,
        "expiresIn": get_token_ttl_seconds(),
    }
