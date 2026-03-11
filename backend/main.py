from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base

from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.restaurants import router as restaurants_router
from routers.reviews import router as reviews_router
from routers.owners import router as owners_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Yelp Prototype API")

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

# Include routers ONLY ONCE
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(restaurants_router)
app.include_router(reviews_router)
app.include_router(owners_router)


@app.get("/")
def root():
    return {"message": "Yelp Backend is Running"}