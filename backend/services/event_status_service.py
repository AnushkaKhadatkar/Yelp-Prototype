from __future__ import annotations

from datetime import datetime
from typing import Any

from pymongo.database import Database

import mongo_collections as C


def create_event_status(
    db: Database,
    *,
    event_id: str,
    entity_type: str,
    entity_id: int | None,
    status: str = "processing",
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    db[C.EVENT_STATUS].update_one(
        {"_id": event_id},
        {
            "$set": {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "status": status,
                "result": result,
                "error": error,
                "updated_at": datetime.utcnow(),
            },
            "$setOnInsert": {"created_at": datetime.utcnow()},
        },
        upsert=True,
    )


def mark_saved(
    db: Database,
    *,
    event_id: str,
    result: dict[str, Any] | None = None,
) -> None:
    db[C.EVENT_STATUS].update_one(
        {"_id": event_id},
        {
            "$set": {
                "status": "saved",
                "result": result,
                "error": None,
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=False,
    )


def mark_failed(db: Database, *, event_id: str, error: str) -> None:
    db[C.EVENT_STATUS].update_one(
        {"_id": event_id},
        {
            "$set": {
                "status": "failed",
                "error": error,
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=False,
    )


def get_event_status(db: Database, event_id: str) -> dict[str, Any] | None:
    doc = db[C.EVENT_STATUS].find_one({"_id": event_id})
    if not doc:
        return None
    return {
        "eventId": doc["_id"],
        "status": doc.get("status", "processing"),
        "result": doc.get("result"),
        "error": doc.get("error"),
        "entity_type": doc.get("entity_type"),
        "entity_id": doc.get("entity_id"),
    }
