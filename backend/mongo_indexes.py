"""Create indexes including TTL on sessions.expires_at."""

from pymongo import ASCENDING, DESCENDING

import mongo_collections as C


def ensure_indexes(db) -> None:
    db[C.USERS].create_index("email", unique=True)
    db[C.SESSIONS].create_index("expires_at", expireAfterSeconds=0)
    db[C.SESSIONS].create_index([("user_id", ASCENDING)])
    db[C.RESTAURANTS].create_index([("name", ASCENDING)])
    db[C.RESTAURANTS].create_index([("cuisine", ASCENDING)])
    db[C.RESTAURANTS].create_index([("city", ASCENDING)])
    db[C.REVIEWS].create_index([("restaurant_id", ASCENDING)])
    db[C.REVIEWS].create_index([("user_id", ASCENDING)])
    db[C.FAVOURITES].create_index(
        [("user_id", ASCENDING), ("restaurant_id", ASCENDING)], unique=True
    )
    db[C.USER_PREFERENCES].create_index("user_id", unique=True)
    db[C.ACTIVITY_LOGS].create_index([("created_at", DESCENDING)])
    db[C.PHOTOS].create_index([("restaurant_id", ASCENDING)])
    db[C.PHOTOS].create_index([("review_id", ASCENDING)])
