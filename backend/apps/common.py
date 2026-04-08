from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import get_database
from mongo_indexes import ensure_indexes
from mongo_utils import ensure_all_counters


@asynccontextmanager
async def lifespan_init_db(_: FastAPI) -> AsyncGenerator[None, None]:
    """Ensure Mongo indexes and counters once per process at startup."""
    db = get_database()
    ensure_indexes(db)
    ensure_all_counters(db)
    yield


def add_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
