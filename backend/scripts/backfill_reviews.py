"""Optional: add seed reviews in MongoDB when restaurants have none."""

import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pymongo import MongoClient

import mongo_collections as C
from mongo_utils import next_id, recalc_restaurant_stats

REVIEW_PHRASES = [
    "Amazing food and great service.",
    "Really enjoyed it — would come back.",
    "Good spot. Solid value for the price.",
    "The ambience was nice and the staff were friendly.",
    "Tasty food! Portions were generous.",
    "Overall a good experience.",
]


def main():
    from dotenv import load_dotenv

    load_dotenv()
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "yelp_db")
    db = MongoClient(uri)[db_name]

    user_ids = [d["_id"] for d in db[C.USERS].find({}, {"_id": 1})]
    if not user_ids:
        uid = next_id(db, "users")
        db[C.USERS].insert_one(
            {
                "_id": uid,
                "name": "Seed User",
                "email": f"seed{random.randint(1000, 9999)}@example.com",
                "password_hash": "$2b$12$placeholderNotForLogin",
                "role": "user",
            }
        )
        user_ids = [uid]

    created = 0
    for r in db[C.RESTAURANTS].find({}):
        rid = r["_id"]
        existing_count = db[C.REVIEWS].count_documents({"restaurant_id": rid})
        if existing_count == 0:
            num = random.randint(1, 3)
            chosen = random.sample(user_ids, min(num, len(user_ids)))
            for uid in chosen:
                rev_id = next_id(db, "reviews")
                db[C.REVIEWS].insert_one(
                    {
                        "_id": rev_id,
                        "user_id": uid,
                        "restaurant_id": rid,
                        "rating": random.randint(3, 5),
                        "comment": random.choice(REVIEW_PHRASES),
                    }
                )
                created += 1
            recalc_restaurant_stats(db, rid)

    print(f"Backfill complete. Created {created} review(s).")


if __name__ == "__main__":
    main()
