"""Restaurant owner microservice: auth_owner + owners."""
from fastapi import FastAPI

from apps.common import add_cors, lifespan_init_db
from routers.auth_common import router as auth_common_router
from routers.auth_owner import router as auth_owner_router
from routers.owners import router as owners_router

app = FastAPI(title="Yelp Owner Service", lifespan=lifespan_init_db)
add_cors(app)
app.include_router(auth_common_router)
app.include_router(auth_owner_router)
app.include_router(owners_router)


@app.get("/")
def root():
    return {"service": "owner", "message": "Yelp Owner Service"}
