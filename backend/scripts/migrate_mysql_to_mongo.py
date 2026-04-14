#!/usr/bin/env python3
"""
Migrate Lab 1 MySQL (same schema as SQLAlchemy models) into MongoDB collections.
Preserves integer _id values. Password hashes are copied as-is (bcrypt).

Connection (pick one):

  A) DATABASE_URL:
     export DATABASE_URL=mysql+pymysql://user:pass@127.0.0.1:3307/yelp_db
     Use the host port you mapped (often 3307 if MySQL is in Docker; not always 3306).

  B) MYSQL_* (avoids URL-encoding special characters in passwords):
     export MYSQL_HOST=127.0.0.1
     export MYSQL_PORT=3307
     export MYSQL_USER=yelp
     export MYSQL_PASSWORD=yelppass
     export MYSQL_DATABASE=yelp_db

  Then:
     export MONGODB_URI=mongodb://127.0.0.1:27017
     export MONGODB_DB_NAME=yelp_db
     python scripts/migrate_mysql_to_mongo.py

If MySQL has no rows, load data first:

     cd backend && python seed_data.py --fresh

(Uses DATABASE_URL or MYSQL_* from .env; defaults: 15 users, 60 restaurants.) Or minimal SQL:

     mysql ... < scripts/mysql_lab1_minimal_seed.sql

Or: python scripts/migrate_mysql_to_mongo.py --allow-empty  (clears Mongo and leaves it empty)
"""

from __future__ import annotations

import argparse
import os
import sys

_backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_scripts = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _backend)
sys.path.insert(0, _scripts)

from dotenv import load_dotenv
from pymongo import MongoClient

import mongo_collections as C
from mysql_env import mysql_conn_params

load_dotenv()


def _mysql_count(cur, table: str) -> int | None:
    """Return row count, or None if table is missing."""
    from pymysql.err import ProgrammingError

    try:
        cur.execute(f"SELECT COUNT(*) AS c FROM `{table}`")
        row = cur.fetchone()
        if not row:
            return 0
        return int(row["c"] if isinstance(row, dict) else row[0])
    except ProgrammingError:
        return None


def main():
    import pymysql
    from pymysql.err import OperationalError

    parser = argparse.ArgumentParser(description="Copy Lab 1 MySQL data into MongoDB.")
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Run even if MySQL has no users (will clear Mongo target collections).",
    )
    args = parser.parse_args()

    params = mysql_conn_params()
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "yelp_db")

    try:
        my = pymysql.connect(**params)
    except OperationalError as e:
        code = e.args[0] if e.args else None
        if code == 1045:
            print(
                "MySQL login failed (access denied). Check:\n"
                "  - User/password match the server (try the same values you use in MySQL Workbench).\n"
                "  - Port: Docker Compose often maps MySQL to host port 3307 — use "
                "127.0.0.1:3307 in DATABASE_URL or MYSQL_PORT=3307.\n"
                "  - If the DB only exists inside Docker, start that container first.\n"
                "  - For special characters in the password, use MYSQL_HOST / MYSQL_USER / "
                "MYSQL_PASSWORD instead of DATABASE_URL.\n",
                file=sys.stderr,
            )
        elif code == 2003:
            print(
                "Cannot reach MySQL (connection refused). Check MYSQL_HOST/MYSQL_PORT "
                "and that the MySQL server is running.\n",
                file=sys.stderr,
            )
        raise

    cur = my.cursor(pymysql.cursors.DictCursor)

    tables = ("users", "restaurants", "reviews", "favourites", "user_preferences")
    counts = {t: _mysql_count(cur, t) for t in tables}
    print(
        f"MySQL source {params['user']}@{params['host']}:{params['port']}/{params['database']} — row counts:",
        ", ".join(f"{t}={counts[t]}" for t in tables),
    )

    if counts["users"] is None:
        print(
            "\nMySQL tables are missing. Create schema + sample data, e.g. (adjust host/port/user/pass):\n"
            "  mysql -h 127.0.0.1 -P 3307 -uyelp -pyelppass yelp_db < scripts/mysql_lab1_minimal_seed.sql\n"
            "  or:  bash scripts/load-mysql-sample.sh   (from repo root, MySQL in Docker)\n",
            file=sys.stderr,
        )
        cur.close()
        my.close()
        raise SystemExit(1)

    if (counts["users"] or 0) == 0 and not args.allow_empty:
        print(
            "\nMySQL has no users — nothing to migrate (would wipe Mongo for no benefit).\n"
            "Load data, then re-run:\n"
            "  cd backend && python seed_data.py --fresh\n"
            "  mysql -h 127.0.0.1 -P 3307 -uyelp -pyelppass yelp_db < scripts/mysql_lab1_minimal_seed.sql\n"
            "  or:  bash scripts/load-mysql-sample.sh\n"
            "Or force an empty migration:  python scripts/migrate_mysql_to_mongo.py --allow-empty\n",
            file=sys.stderr,
        )
        cur.close()
        my.close()
        raise SystemExit(1)

    mc = MongoClient(mongo_uri)
    db = mc[db_name]

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
