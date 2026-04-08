from __future__ import annotations

import json
import os
from typing import Any

try:
    from kafka import KafkaProducer
except Exception:  # pragma: no cover
    KafkaProducer = None

_producer = None


def kafka_enabled() -> bool:
    return os.getenv("KAFKA_ENABLED", "false").lower() in {"1", "true", "yes"}


def _get_producer():
    global _producer
    if _producer is not None:
        return _producer
    if not kafka_enabled() or KafkaProducer is None:
        return None
    servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    _producer = KafkaProducer(
        bootstrap_servers=[s.strip() for s in servers.split(",") if s.strip()],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    return _producer


def publish_event(topic: str, payload: dict[str, Any]) -> bool:
    producer = _get_producer()
    if producer is None:
        return False
    producer.send(topic, payload)
    producer.flush()
    return True
