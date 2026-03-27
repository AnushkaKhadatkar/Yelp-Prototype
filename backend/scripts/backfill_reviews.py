import random
from sqlalchemy import func

import os
import sys

# Allow running as `python scripts/backfill_reviews.py`
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal
from models.restaurant import Restaurant
from models.review import Review
from models.user import User


REVIEW_PHRASES = [
    "Amazing food and great service.",
    "Really enjoyed it — would come back.",
    "Good spot. Solid value for the price.",
    "The ambience was nice and the staff were friendly.",
    "Tasty food! Portions were generous.",
    "Overall a good experience.",
]


def main():
    db = SessionLocal()
    try:
        user_ids = [u.id for u in db.query(User.id).all()]
        if not user_ids:
            # Create a simple fallback user so we can attach reviews.
            # (Passwords/auth aren’t needed for seeded reviews.)
            u = User(
                name="Seed User",
                email=f"seed{random.randint(1000, 9999)}@example.com",
                password_hash="seed",
                role="user",
            )
            db.add(u)
            db.commit()
            db.refresh(u)
            user_ids = [u.id]

        restaurants = db.query(Restaurant).all()
        created = 0

        for r in restaurants:
            # Determine whether restaurant has any reviews
            existing_count = (
                db.query(func.count(Review.id))
                .filter(Review.restaurant_id == r.id)
                .scalar()
            ) or 0

            if existing_count == 0:
                # Create 1–3 initial reviews so avg_rating isn't always extreme
                num = random.randint(1, 3)
                chosen_users = random.sample(user_ids, min(num, len(user_ids)))
                ratings = []
                for uid in chosen_users:
                    rating = random.randint(3, 5)
                    ratings.append(rating)
                    db.add(
                        Review(
                            user_id=uid,
                            restaurant_id=r.id,
                            rating=rating,
                            comment=random.choice(REVIEW_PHRASES),
                        )
                    )
                    created += 1

                db.flush()

            # Recompute stats from DB (covers both newly created and preexisting)
            stats = (
                db.query(func.avg(Review.rating), func.count(Review.id))
                .filter(Review.restaurant_id == r.id)
                .first()
            )
            avg = round(float(stats[0]), 1) if stats and stats[0] is not None else 0.0
            cnt = int(stats[1]) if stats and stats[1] is not None else 0
            r.avg_rating = avg
            r.review_count = cnt

        db.commit()
        print(f"Backfill complete. Created {created} review(s).")
    finally:
        db.close()


if __name__ == "__main__":
    main()

