#!/usr/bin/env python3
"""
Migrate Lab 1 MySQL (same schema as SQLAlchemy models) into MongoDB collections.
Preserves integer _id values. Password hashes are copied as-is (bcrypt).

Usage (from repo root or backend/):
  export DATABASE_URL=mysql+pymysql://user:pass@host:3306/yelp_db
  export MONGODB_URI=mongodb://localhost:27017
  export MONGODB_DB_NAME=yelp_db
  python scripts/migrate_mysql_to_mongo.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from pymongo import MongoClient
from sqlalchemy.engine.url import make_url

import mongo_collections as C

load_dotenv()


def mysql_conn_params():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is required (MySQL URL)")
    u = make_url(url)
    return {
        "host": u.host or "localhost",
        "port": u.port or 3306,
        "user": u.username or "",
        "password": u.password or "",
        "database": u.database or "yelp_db",
        "charset": "utf8mb4",
    }


def main():
    import pymysql

    params = mysql_conn_params()
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "yelp_db")

    my = pymysql.connect(**params)
    mc = MongoClient(mongo_uri)
    db = mc[db_name]

    cur = my.cursor(pymysql.cursors.DictCursor)

    # Clear target collections (idempotent re-run)
    for name in (
        C.USER_PREFERENCES,
        C.FAVOURITES,
        C.REVIEWS,
        C.RESTAURANTS,
        C.USERS,
        C.COUNTERS,
    ):
        db[name].delete_many({})

    cur.execute("SELECT * FROM users ORDER BY id")
    for row in cur.fetchall():
        doc = {
            "_id": int(row["id"]),
            "name": row["name"],
            "email": row["email"],
            "password_hash": row["password_hash"],
            "phone": row.get("phone"),
            "about": row.get("about"),
            "city": row.get("city"),
            "state": row.get("state"),
            "country": row.get("country"),
            "languages": row.get("languages"),
            "gender": row.get("gender"),
            "profile_pic": row.get("profile_pic"),
            "restaurant_location": row.get("restaurant_location"),
            "role": row.get("role") or "user",
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }
        db[C.USERS].insert_one(doc)

    cur.execute("SELECT * FROM restaurants ORDER BY id")
    for row in cur.fetchall():
        ar = row.get("avg_rating")
        doc = {
            "_id": int(row["id"]),
            "name": row["name"],
            "cuisine": row["cuisine"],
            "address": row.get("address"),
            "city": row.get("city"),
            "state": row.get("state"),
            "zip_code": row.get("zip_code"),
            "description": row.get("description"),
            "contact_phone": row.get("contact_phone"),
            "contact_email": row.get("contact_email"),
            "price_tier": row.get("price_tier"),
            "ambiance": row.get("ambiance"),
            "amenities": row.get("amenities"),
            "hours": row.get("hours"),
            "photos": row.get("photos"),
            "owner_id": int(row["owner_id"]) if row.get("owner_id") is not None else None,
            "avg_rating": float(ar) if ar is not None else 0.0,
            "review_count": int(row.get("review_count") or 0),
            "created_at": row.get("created_at"),
        }
        db[C.RESTAURANTS].insert_one(doc)

    cur.execute("SELECT * FROM reviews ORDER BY id")
    for row in cur.fetchall():
        doc = {
            "_id": int(row["id"]),
            "user_id": int(row["user_id"]),
            "restaurant_id": int(row["restaurant_id"]),
            "rating": int(row["rating"]),
            "comment": row.get("comment"),
            "photos": row.get("photos"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }
        db[C.REVIEWS].insert_one(doc)

    cur.execute("SELECT * FROM favourites ORDER BY id")
    for row in cur.fetchall():
        doc = {
            "_id": int(row["id"]),
            "user_id": int(row["user_id"]),
            "restaurant_id": int(row["restaurant_id"]),
            "created_at": row.get("created_at"),
        }
        db[C.FAVOURITES].insert_one(doc)

    cur.execute("SELECT * FROM user_preferences ORDER BY id")
    for row in cur.fetchall():
        doc = {
            "user_id": int(row["user_id"]),
            "cuisines": row.get("cuisines"),
            "price_range": row.get("price_range"),
            "preferred_locations": row.get("preferred_locations"),
            "dietary_needs": row.get("dietary_needs"),
            "ambiance": row.get("ambiance"),
            "sort_preference": row.get("sort_preference"),
        }
        db[C.USER_PREFERENCES].insert_one(doc)

    cur.close()
    my.close()

    # Counters for next_id()
    def max_id(collection):
        m = db[collection].find_one(sort=[("_id", -1)], projection={"_id": 1})
        return int(m["_id"]) if m else 0

    db[C.COUNTERS].insert_one({"_id": "users", "seq": max_id(C.USERS)})
    db[C.COUNTERS].insert_one({"_id": "restaurants", "seq": max_id(C.RESTAURANTS)})
    db[C.COUNTERS].insert_one({"_id": "reviews", "seq": max_id(C.REVIEWS)})
    db[C.COUNTERS].insert_one({"_id": "favourites", "seq": max_id(C.FAVOURITES)})

    print(
        "Migration complete:",
        f"users={db[C.USERS].count_documents({})},",
        f"restaurants={db[C.RESTAURANTS].count_documents({})},",
        f"reviews={db[C.REVIEWS].count_documents({})},",
        f"favourites={db[C.FAVOURITES].count_documents({})},",
        f"preferences={db[C.USER_PREFERENCES].count_documents({})}.",
    )


if __name__ == "__main__":
    main()
