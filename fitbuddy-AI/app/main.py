from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_db
from .routes import router


settings = get_settings()


app = FastAPI(

    title=settings.app_name,

    description=(
        "AI-powered general wellness "
        "and workout-plan generator."
    ),

    version="1.0.0"

)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


app.include_router(router)


@app.on_event("startup")
def startup():

    init_db()


@app.get("/health")
def health():

    return {

        "status": "ok",

        "application":
            settings.app_name

    }