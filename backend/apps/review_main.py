"""Review microservice: review CRUD and review photo uploads."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.common import add_cors
from routers.reviews import router as reviews_router

app = FastAPI(title="Yelp Review Service")
add_cors(app)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(reviews_router)


@app.get("/")
def root():
    return {"service": "review", "message": "Yelp Review Service"}
