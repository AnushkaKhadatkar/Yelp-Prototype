"""MongoDB connection (Lab 2). Replaces SQLAlchemy SessionLocal."""

import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "yelp_db")

_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client


def get_database() -> Database:
    return get_mongo_client()[MONGODB_DB_NAME]


def get_db():
    """FastAPI dependency: yields PyMongo Database."""
    db = get_database()
    yield db
