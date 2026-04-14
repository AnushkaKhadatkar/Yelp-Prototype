from __future__ import annotations

import json
import os
import sys
import time

from kafka import KafkaConsumer

from database import get_database
from services.restaurant_worker_service import process_restaurant_event


def main() -> None:
    # #region agent log
    def _agent(message: str, data: dict, hypothesis_id: str) -> None:
        print(
            json.dumps(
                {
                    "sessionId": "8d5b23",
                    "hypothesisId": hypothesis_id,
                    "location": "workers/restaurant_worker.py:main",
                    "message": message,
                    "data": data,
                    "timestamp": int(time.time() * 1000),
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
            flush=True,
        )

    # #endregion

    servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    _agent("restaurant_worker_start", {"bootstrap": servers}, "H4")
    consumer = KafkaConsumer(
        "restaurant.created",
        "restaurant.updated",
        "restaurant.deleted",
        "restaurant.claimed",
        bootstrap_servers=[s.strip() for s in servers.split(",") if s.strip()],
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id=os.getenv("KAFKA_RESTAURANT_WORKER_GROUP", "restaurant-worker"),
        api_version_auto_timeout_ms=30000,
    )
    db = get_database()
    _agent(
        "restaurant_worker_subscribed",
        {
            "topics": [
                "restaurant.created",
                "restaurant.updated",
                "restaurant.deleted",
                "restaurant.claimed",
            ]
        },
        "H4",
    )
    for message in consumer:
        _agent(
            "restaurant_message_received",
            {"topic": message.topic},
            "H5",
        )
        process_restaurant_event(db, message.topic, message.value)
        _agent("restaurant_worker_processed", {"topic": message.topic}, "H5")


if __name__ == "__main__":
    main()
