from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException
from pymongo.database import Database

import mongo_collections as C
from mongo_utils import recalc_restaurant_stats
from services.event_status_service import mark_failed, mark_saved


def process_review_event(db: Database, event_type: str, payload: dict[str, Any]) -> None:
    event_id = payload["eventId"]
    try:
        if event_type == "review.created":
            restaurant = db[C.RESTAURANTS].find_one({"_id": payload["restaurant_id"]})
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found")

            db[C.REVIEWS].insert_one(
                {
                    "_id": payload["review_id"],
                    "user_id": payload["user_id"],
                    "restaurant_id": payload["restaurant_id"],
                    "rating": payload["rating"],
                    "comment": payload.get("comment"),
                    "photos": payload.get("photos"),
                    "created_at": datetime.utcnow(),
                }
            )
            recalc_restaurant_stats(db, payload["restaurant_id"])
            mark_saved(
                db,
                event_id=event_id,
                result={"review_id": payload["review_id"], "restaurant_id": payload["restaurant_id"]},
            )
            return

        if event_type == "review.updated":
            review = db[C.REVIEWS].find_one({"_id": payload["review_id"]})
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            patch = payload.get("patch", {})
            if patch:
                db[C.REVIEWS].update_one({"_id": payload["review_id"]}, {"$set": patch})
            recalc_restaurant_stats(db, review["restaurant_id"])
            mark_saved(db, event_id=event_id, result={"review_id": payload["review_id"]})
            return

        if event_type == "review.deleted":
            review = db[C.REVIEWS].find_one({"_id": payload["review_id"]})
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            db[C.REVIEWS].delete_one({"_id": payload["review_id"]})
            recalc_restaurant_stats(db, review["restaurant_id"])
            mark_saved(db, event_id=event_id, result={"review_id": payload["review_id"]})
            return

        raise ValueError(f"Unsupported event_type: {event_type}")
    except Exception as e:
        mark_failed(db, event_id=event_id, error=str(e))
        raise
