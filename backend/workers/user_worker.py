from __future__ import annotations

import json
import os
from datetime import datetime

from kafka import KafkaConsumer

from database import get_database
import mongo_collections as C


def main() -> None:
    # #region agent log
    import sys

    def _agent(msg: str, data: dict, hid: str) -> None:
        line = json.dumps(
            {
                "sessionId": "8d5b23",
                "hypothesisId": hid,
                "location": "workers/user_worker.py:main",
                "message": msg,
                "data": data,
                "timestamp": int(__import__("time").time() * 1000),
            },
            ensure_ascii=False,
        )
        print(line, file=sys.stderr, flush=True)

    # #endregion

    servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    _agent("user_worker_connecting", {"bootstrap": servers}, "H4")
    consumer = KafkaConsumer(
        "user.created",
        "user.updated",
        bootstrap_servers=[s.strip() for s in servers.split(",") if s.strip()],
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id=os.getenv("KAFKA_USER_WORKER_GROUP", "user-worker"),
        api_version_auto_timeout_ms=30000,
    )
    db = get_database()
    _agent("user_worker_consume_loop", {}, "H4")
    for message in consumer:
        payload = message.value
        db[C.ACTIVITY_LOGS].insert_one(
            {
                "user_id": payload.get("user_id"),
                "action": f"kafka_{message.topic.replace('.', '_')}",
                "resource": "users",
                "meta": {"topic": message.topic, "payload": payload},
                "created_at": datetime.utcnow(),
            }
        )
        _agent("user_event_consumed", {"topic": message.topic, "user_id": payload.get("user_id")}, "H5")


if __name__ == "__main__":
    main()
