"""User / reviewer microservice: auth_user + users."""
from fastapi import FastAPI

from apps.common import add_cors, lifespan_init_db
from routers.auth_user import router as auth_user_router
from routers.users import router as users_router

app = FastAPI(title="Yelp User Service", lifespan=lifespan_init_db)
add_cors(app)
app.include_router(auth_user_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"service": "user", "message": "Yelp User Service"}
