from __future__ import annotations

import json
import os

from kafka import KafkaConsumer

from database import get_database
from services.restaurant_worker_service import process_restaurant_event


def main() -> None:
    servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    consumer = KafkaConsumer(
        "restaurant.created",
        "restaurant.updated",
        "restaurant.deleted",
        "restaurant.claimed",
        bootstrap_servers=[s.strip() for s in servers.split(",") if s.strip()],
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id=os.getenv("KAFKA_RESTAURANT_WORKER_GROUP", "restaurant-worker"),
    )
    db = get_database()
    for message in consumer:
        process_restaurant_event(db, message.topic, message.value)


if __name__ == "__main__":
    main()
