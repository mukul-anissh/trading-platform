from fastapi import FastAPI
from app.core.config import settings
from app.routes import health, auth

def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)
    app.include_router(health.router, prefix=settings.API_V1_STR)
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    return app

app = create_app()