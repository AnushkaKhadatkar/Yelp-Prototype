"""
Seed MySQL with Faker-generated users, restaurants, and reviews (original Lab 1 volumes).

Uses the same connection as migrate_mysql_to_mongo.py (DATABASE_URL or MYSQL_* in .env).

  cd backend
  export MYSQL_HOST=127.0.0.1 MYSQL_PORT=3307 MYSQL_USER=yelp MYSQL_PASSWORD=yelppass MYSQL_DATABASE=yelp_db
  python seed_data.py --fresh

Then copy to MongoDB:

  export MONGODB_URI=mongodb://127.0.0.1:27017
  python scripts/migrate_mysql_to_mongo.py

--fresh     Truncate app tables first (use when replacing the 2-row minimal SQL seed).
--users N   Default 15.
--restaurants N  Default 60.

All seeded users share password SEED_USER_PASSWORD (default: password123).
"""

from __future__ import annotations

import argparse
import os
import random
import sys

import pymysql
from faker import Faker
from passlib.context import CryptContext

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
from mysql_env import mysql_conn_params

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False,
)


def _clip(s: str, max_len: int) -> str:
    s = str(s)
    return s[:max_len] if len(s) > max_len else s


def _truncate_all(cur) -> None:
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in (
        "reviews",
        "favourites",
        "user_preferences",
        "restaurants",
        "users",
    ):
        try:
            cur.execute(f"TRUNCATE TABLE `{table}`")
        except pymysql.err.ProgrammingError:
            pass
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed MySQL with demo Yelp data.")
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Truncate users/restaurants/reviews (etc.) before inserting.",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=15,
        help="Number of users (default 15).",
    )
    parser.add_argument(
        "--restaurants",
        type=int,
        default=60,
        help="Number of restaurants (default 60).",
    )
    args = parser.parse_args()

    seed_pw = os.getenv("SEED_USER_PASSWORD", "password123")
    password_hash = pwd_context.hash(seed_pw)

    params = mysql_conn_params()
    conn = pymysql.connect(**params)
    cur = conn.cursor()

    if args.fresh:
        _truncate_all(cur)
        conn.commit()

    fake = Faker()
    cuisines = ["Italian", "Chinese", "Mexican", "Indian", "Japanese", "American"]
    cities = ["San Jose", "San Francisco", "New York", "Los Angeles", "Chicago"]
    states = ["CA", "NY", "IL", "TX"]
    price_tiers = ["$", "$$", "$$$", "$$$$"]
    ambiance_list = ["casual", "fine dining", "romantic", "family-friendly"]
    amenities_list = ["wifi", "outdoor seating", "parking", "pet-friendly"]
    review_phrases = [
        "Amazing food!",
        "Would definitely come back.",
        "Service was slow but food was great.",
        "Highly recommend!",
        "Not worth the price.",
        "Loved the ambiance.",
        "Great for family dinners.",
        "Best place in town!",
        "Decent experience.",
        "Could be better.",
    ]

    user_ids: list[int] = []
    for _ in range(args.users):
        cur.execute(
            """
            INSERT INTO users (name, email, password_hash, city, state, country, role)
            VALUES (%s, %s, %s, %s, %s, %s, 'user')
            """,
            (
                _clip(fake.name(), 100),
                _clip(fake.unique.email(), 150),
                password_hash,
                random.choice(cities),
                random.choice(states),
                "USA",
            ),
        )
        user_ids.append(cur.lastrowid)

    restaurant_ids: list[int] = []
    for _ in range(args.restaurants):
        city = random.choice(cities)
        state = random.choice(states)
        cur.execute(
            """
            INSERT INTO restaurants
            (name, cuisine, address, city, state, zip_code, description,
             contact_phone, contact_email, price_tier, ambiance, amenities, hours)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                _clip(fake.company(), 150),
                _clip(random.choice(cuisines), 100),
                _clip(fake.address(), 255),
                city,
                state,
                _clip(fake.zipcode(), 20),
                fake.text(max_nb_chars=120),
                _clip(fake.phone_number(), 20),
                _clip(fake.email(), 150),
                random.choice(price_tiers),
                _clip(random.choice(ambiance_list), 255),
                _clip(random.choice(amenities_list), 255),
                "9 AM - 10 PM",
            ),
        )
        restaurant_ids.append(cur.lastrowid)

    for r_id in restaurant_ids:
        num_reviews = random.randint(3, 8)
        selected_users = random.sample(user_ids, min(num_reviews, len(user_ids)))
        ratings: list[int] = []
        for user_id in selected_users:
            rating = random.randint(1, 5)
            ratings.append(rating)
            cur.execute(
                """
                INSERT INTO reviews (user_id, restaurant_id, rating, comment)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, r_id, rating, random.choice(review_phrases)),
            )
        avg_rating = round(sum(ratings) / len(ratings), 1)
        cur.execute(
            """
            UPDATE restaurants
            SET avg_rating = %s, review_count = %s
            WHERE id = %s
            """,
            (avg_rating, len(ratings), r_id),
        )

    conn.commit()
    cur.close()
    conn.close()

    print(
        f"Seed complete: {args.users} users, {args.restaurants} restaurants, "
        f"3–8 reviews each. All users' password: {seed_pw!r}"
    )


if __name__ == "__main__":
    main()
