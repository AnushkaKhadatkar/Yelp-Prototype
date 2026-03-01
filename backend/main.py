from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from fastapi.staticfiles import StaticFiles
from routers.auth import router as auth_router
from fastapi import Depends
from services.auth_service import get_current_user

# Create all tables (will create when models are defined)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Yelp Prototype API")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(auth_router)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Yelp Backend is Running"}

from services.auth_service import get_current_user

@app.get("/protected")
def protected_route(current_user = Depends(get_current_user)):
    return {"message": f"Hello {current_user.name}"}