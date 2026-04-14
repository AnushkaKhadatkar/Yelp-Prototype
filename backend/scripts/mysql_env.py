"""Shared MySQL connection settings for seed_data and migrate_mysql_to_mongo."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url

load_dotenv()


def mysql_conn_params() -> dict:
    """Prefer MYSQL_* if MYSQL_HOST and MYSQL_USER are set; else DATABASE_URL."""
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    if host and user is not None:
        port = int(os.getenv("MYSQL_PORT") or "3306")
        return {
            "host": host,
            "port": port,
            "user": user,
            "password": os.getenv("MYSQL_PASSWORD") or "",
            "database": os.getenv("MYSQL_DATABASE") or "yelp_db",
            "charset": "utf8mb4",
        }

    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit(
            "Set MySQL connection: DATABASE_URL (mysql+pymysql://...) or "
            "MYSQL_HOST, MYSQL_USER, and optionally MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DATABASE. "
            "See backend/.env.example."
        )
    u = make_url(url)
    return {
        "host": u.host or "localhost",
        "port": u.port or 3306,
        "user": u.username or "",
        "password": u.password or "",
        "database": u.database or "yelp_db",
        "charset": "utf8mb4",
    }
