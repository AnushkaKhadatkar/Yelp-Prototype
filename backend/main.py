from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db

from routers.users import router as users_router
from routers.restaurants import router as restaurants_router
from routers.reviews import router as reviews_router
from routers.owners import router as owners_router
from routers.auth_user import router as auth_user_router
from routers.auth_owner import router as auth_owner_router
from routers.ai_assistant import router as ai_assistant_router


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    yield


app = FastAPI(title="Yelp Prototype API", lifespan=_lifespan)

# Static uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users_router)
app.include_router(restaurants_router)
app.include_router(reviews_router)
app.include_router(owners_router)
app.include_router(auth_user_router)
app.include_router(auth_owner_router)
app.include_router(ai_assistant_router)

@app.get("/")
def root():
    return {"message": "Yelp Backend is Running"}
