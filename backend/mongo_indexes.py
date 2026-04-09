"""MongoDB indexes for Yelp backend."""

from pymongo.database import Database

import mongo_collections as C


def ensure_indexes(db: Database) -> None:
    db[C.USERS].create_index("email", unique=True)
    db[C.SESSIONS].create_index("expires_at", expireAfterSeconds=0)
    db[C.REVIEWS].create_index([("restaurant_id", 1), ("created_at", -1)])
    db[C.RESTAURANTS].create_index([("name", "text"), ("description", "text")])
    db[C.FAVOURITES].create_index([("user_id", 1), ("restaurant_id", 1)], unique=True)
    db[C.EVENT_STATUS].create_index([("entity_type", 1), ("entity_id", 1), ("updated_at", -1)])
