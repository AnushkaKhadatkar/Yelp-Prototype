import os
import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo.database import Database

import mongo_collections as C
from database import get_db
from mongo_utils import user_doc_to_namespace

load_dotenv()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False,
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/user/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(db: Database, data: dict) -> str:
    """Issue JWT and persist server-side session (jti) with TTL-backed expires_at."""
    jti = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode["jti"] = jti
    to_encode["exp"] = expire
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    db[C.SESSIONS].insert_one(
        {
            "_id": jti,
            "user_id": int(data["sub"]),
            "expires_at": expire,
        }
    )
    return token


def authenticate_user(db: Database, email: str, password: str) -> SimpleNamespace:
    doc = db[C.USERS].find_one({"email": email})
    if not doc or not verify_password(password, doc.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return user_doc_to_namespace(doc)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if user_id is None or jti is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    sess = db[C.SESSIONS].find_one({"_id": jti})
    if not sess:
        raise credentials_exception

    doc = db[C.USERS].find_one({"_id": int(user_id)})
    if doc is None:
        raise credentials_exception

    return user_doc_to_namespace(doc)


def decode_token_jti(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("jti")
    except JWTError:
        return None
