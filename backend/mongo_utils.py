"""Helpers: sequences, restaurant stats, user namespace for Depends()."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import Any, Optional

from pymongo.database import Database
from pymongo import ReturnDocument

import mongo_collections as C


def ensure_counter_from_max(db: Database, collection_name: str, counter_key: str) -> None:
    coll = db[collection_name]
    doc = coll.find_one(sort=[("_id", -1)], projection={"_id": 1})
    seq = int(doc["_id"]) if doc else 0
    db[C.COUNTERS].update_one(
        {"_id": counter_key},
        {"$max": {"seq": seq}},
        upsert=True,
    )


def ensure_all_counters(db: Database) -> None:
    for coll, key in (
        (C.USERS, "users"),
        (C.RESTAURANTS, "restaurants"),
        (C.REVIEWS, "reviews"),
        (C.FAVOURITES, "favourites"),
    ):
        ensure_counter_from_max(db, coll, key)


def next_id(db: Database, counter_key: str) -> int:
    doc = db[C.COUNTERS].find_one_and_update(
        {"_id": counter_key},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])


def user_doc_to_namespace(doc: dict) -> SimpleNamespace:
    u = SimpleNamespace()
    u.id = doc["_id"]
    u.name = doc.get("name")
    u.email = doc.get("email")
    u.password_hash = doc.get("password_hash")
    u.role = doc.get("role", "user")
    u.phone = doc.get("phone")
    u.about = doc.get("about")
    u.city = doc.get("city")
    u.state = doc.get("state")
    u.country = doc.get("country")
    u.languages = doc.get("languages")
    u.gender = doc.get("gender")
    u.profile_pic = doc.get("profile_pic")
    u.restaurant_location = doc.get("restaurant_location")
    u.created_at = doc.get("created_at")
    u.updated_at = doc.get("updated_at")
    return u


def recalc_restaurant_stats(db: Database, restaurant_id: int) -> None:
    pipeline = [
        {"$match": {"restaurant_id": restaurant_id}},
        {
            "$group": {
                "_id": None,
                "avg": {"$avg": "$rating"},
                "cnt": {"$sum": 1},
            }
        },
    ]
    agg = list(db[C.REVIEWS].aggregate(pipeline))
    if not agg:
        avg_rating = 0.0
        review_count = 0
    else:
        a = agg[0]
        avg_rating = round(float(a["avg"]), 1) if a.get("avg") is not None else 0.0
        review_count = int(a["cnt"])
    db[C.RESTAURANTS].update_one(
        {"_id": restaurant_id},
        {"$set": {"avg_rating": avg_rating, "review_count": review_count}},
    )


def log_activity(
    db: Database,
    *,
    user_id: Optional[int],
    action: str,
    resource: Optional[str] = None,
    meta: Optional[dict] = None,
) -> None:
    db[C.ACTIVITY_LOGS].insert_one(
        {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "meta": meta or {},
            "created_at": datetime.utcnow(),
        }
    )


def restaurant_doc_to_detail_dict(doc: dict, reviews_list: list) -> dict[str, Any]:
    photos = doc.get("photos") or ""
    return {
        "id": doc["_id"],
        "name": doc.get("name"),
        "cuisine": doc.get("cuisine"),
        "address": doc.get("address"),
        "city": doc.get("city"),
        "state": doc.get("state"),
        "zip_code": doc.get("zip_code"),
        "description": doc.get("description"),
        "hours": doc.get("hours"),
        "contact_phone": doc.get("contact_phone"),
        "contact_email": doc.get("contact_email"),
        "pricing_tier": doc.get("price_tier"),
        "ambiance": doc.get("ambiance"),
        "amenities": doc.get("amenities"),
        "photos": photos.split(",") if photos else [],
        "avg_rating": doc.get("avg_rating", 0),
        "review_count": doc.get("review_count", 0),
        "reviews": reviews_list,
    }
