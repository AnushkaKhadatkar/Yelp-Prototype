from __future__ import annotations

import json
import os

from kafka import KafkaConsumer

from database import get_database
from services.review_worker_service import process_review_event


def main() -> None:
    servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    consumer = KafkaConsumer(
        "review.created",
        "review.updated",
        "review.deleted",
        bootstrap_servers=[s.strip() for s in servers.split(",") if s.strip()],
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id=os.getenv("KAFKA_REVIEW_WORKER_GROUP", "review-worker"),
    )
    db = get_database()
    for message in consumer:
        process_review_event(db, message.topic, message.value)


if __name__ == "__main__":
    main()
