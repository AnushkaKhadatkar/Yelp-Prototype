from __future__ import annotations

import json
import os
import sys
import time
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
        api_version_auto_timeout_ms=30000,
    )
    return _producer


def publish_event(topic: str, payload: dict[str, Any]) -> bool:
    # #region agent log
    def _agent(message: str, data: dict, hypothesis_id: str) -> None:
        print(
            json.dumps(
                {
                    "sessionId": "8d5b23",
                    "hypothesisId": hypothesis_id,
                    "location": "services/kafka_bus.py:publish_event",
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

    producer = _get_producer()
    if producer is None:
        _agent(
            "kafka_publish_skipped",
            {"topic": topic, "reason": "no_producer_or_disabled"},
            "H6",
        )
        return False
    try:
        producer.send(topic, payload)
        producer.flush()
        _agent(
            "kafka_publish_ok",
            {"topic": topic, "keys": list(payload.keys())},
            "H6",
        )
        return True
    except Exception as e:
        _agent(
            "kafka_publish_error",
            {"topic": topic, "error": str(e)},
            "H6",
        )
        return False
