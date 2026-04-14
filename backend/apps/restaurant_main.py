"""Restaurant + AI microservice."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.common import add_cors, lifespan_init_db
from routers.auth_common import router as auth_common_router
from routers.restaurants import router as restaurants_router
from routers.ai_assistant import router as ai_assistant_router

app = FastAPI(title="Yelp Restaurant Service", lifespan=lifespan_init_db)
add_cors(app)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(auth_common_router)
app.include_router(restaurants_router)
app.include_router(ai_assistant_router)


@app.get("/")
def root():
    return {"service": "restaurant", "message": "Yelp Restaurant Service"}
