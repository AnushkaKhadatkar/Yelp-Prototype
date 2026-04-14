from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException
from pymongo.database import Database

import mongo_collections as C
from services.event_status_service import mark_failed, mark_saved


def process_restaurant_event(db: Database, event_type: str, payload: dict[str, Any]) -> None:
    event_id = payload["eventId"]
    try:
        if event_type == "restaurant.created":
            db[C.RESTAURANTS].insert_one(
                {
                    "_id": payload["restaurant_id"],
                    "name": payload["name"],
                    "cuisine": payload.get("cuisine"),
                    "address": payload.get("address"),
                    "city": payload.get("city"),
                    "state": payload.get("state"),
                    "zip_code": payload.get("zip_code"),
                    "contact_phone": payload.get("contact_phone"),
                    "contact_email": payload.get("contact_email"),
                    "description": payload.get("description"),
                    "hours": payload.get("hours"),
                    "price_tier": payload.get("pricing_tier"),
                    "ambiance": payload.get("ambiance"),
                    "amenities": payload.get("amenities"),
                    "photos": payload.get("photos"),
                    "owner_id": payload.get("owner_id"),
                    "avg_rating": 0.0,
                    "review_count": 0,
                    "created_at": datetime.utcnow(),
                }
            )
            mark_saved(db, event_id=event_id, result={"restaurant_id": payload["restaurant_id"]})
            return

        if event_type == "restaurant.updated":
            patch = payload.get("patch", {})
            db[C.RESTAURANTS].update_one({"_id": payload["restaurant_id"]}, {"$set": patch})
            mark_saved(db, event_id=event_id, result={"restaurant_id": payload["restaurant_id"]})
            return

        if event_type == "restaurant.deleted":
            db[C.RESTAURANTS].delete_one({"_id": payload["restaurant_id"]})
            mark_saved(db, event_id=event_id, result={"restaurant_id": payload["restaurant_id"]})
            return

        if event_type == "restaurant.claimed":
            restaurant = db[C.RESTAURANTS].find_one({"_id": payload["restaurant_id"]})
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found")
            db[C.RESTAURANTS].update_one(
                {"_id": payload["restaurant_id"]},
                {"$set": {"owner_id": payload["owner_id"]}},
            )
            mark_saved(db, event_id=event_id, result={"restaurant_id": payload["restaurant_id"]})
            return

        raise ValueError(f"Unsupported event_type: {event_type}")
    except Exception as e:
        mark_failed(db, event_id=event_id, error=str(e))
        raise
