"""User / reviewer microservice: auth_user + users."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.common import add_cors, lifespan_init_db
from routers.auth_common import router as auth_common_router
from routers.auth_user import router as auth_user_router
from routers.users import router as users_router

app = FastAPI(title="Yelp User Service", lifespan=lifespan_init_db)
add_cors(app)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(auth_common_router)
app.include_router(auth_user_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"service": "user", "message": "Yelp User Service"}
