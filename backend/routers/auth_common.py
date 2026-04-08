from fastapi import APIRouter, Depends, Header, HTTPException
from pymongo.database import Database

import mongo_collections as C
from database import get_db
from services.auth_service import (
    create_access_token,
    decode_token_payload,
    decode_token_jti,
    get_token_ttl_seconds,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return authorization.replace("Bearer ", "", 1).strip()


@router.post("/logout")
def logout(
    db: Database = Depends(get_db),
    authorization: str | None = Header(None),
):
    token = _bearer_token(authorization)
    jti = decode_token_jti(token)
    if not jti:
        raise HTTPException(status_code=401, detail="Invalid token")
    db[C.SESSIONS].delete_one({"_id": jti})
    return {"message": "Logged out"}


@router.post("/refresh")
def refresh(
    db: Database = Depends(get_db),
    authorization: str | None = Header(None),
):
    token = _bearer_token(authorization)
    payload = decode_token_payload(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    role = payload.get("role")
    jti = payload.get("jti")
    if user_id is None or role is None or jti is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    sess = db[C.SESSIONS].find_one({"_id": jti})
    if not sess:
        raise HTTPException(status_code=401, detail="Session expired")

    db[C.SESSIONS].delete_one({"_id": jti})
    new_token = create_access_token(db, data={"sub": str(user_id), "role": role})
    return {"token": new_token, "expiresIn": get_token_ttl_seconds()}
