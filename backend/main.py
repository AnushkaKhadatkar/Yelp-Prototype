from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo.errors import PyMongoError

from database import MONGODB_DB_NAME, get_database
from mongo_indexes import ensure_indexes
from mongo_utils import ensure_all_counters

from routers.auth_user import router as auth_user_router
from routers.auth_common import router as auth_common_router
from routers.users import router as users_router
from routers.restaurants import router as restaurants_router
from routers.reviews import router as reviews_router
from routers.owners import router as owners_router
from routers.auth_owner import router as auth_owner_router
from routers.ai_assistant import router as ai_assistant_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_database()
    ensure_indexes(db)
    ensure_all_counters(db)
    yield


app = FastAPI(title="Yelp Prototype API", lifespan=lifespan)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_user_router)
app.include_router(auth_common_router)
app.include_router(users_router)
app.include_router(restaurants_router)
app.include_router(reviews_router)
app.include_router(owners_router)
app.include_router(auth_owner_router)
app.include_router(ai_assistant_router)


@app.get("/")
def root():
    return {"message": "Yelp Backend is Running"}


@app.get("/health/db")
def health_db():
    """Ping MongoDB (uses same URI as the app). Does not expose MONGODB_URI."""
    try:
        get_database().command("ping")
    except PyMongoError as e:
        return JSONResponse(
            status_code=503,
            content={"ok": False, "db": MONGODB_DB_NAME, "error": str(e)},
        )
    return {"ok": True, "db": MONGODB_DB_NAME}
