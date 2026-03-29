from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db


@asynccontextmanager
async def lifespan_init_db(_: FastAPI) -> AsyncGenerator[None, None]:
    """Run SQLAlchemy create_all once per process at startup (idempotent)."""
    init_db()
    yield


def add_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
