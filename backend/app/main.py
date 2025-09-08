from fastapi import FastAPI
from app.core.config import settings
from app.routers import health, auth, orders, stocks, trades, users

def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)
    app.include_router(health.router, prefix=settings.API_V1_STR)
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    app.include_router(orders.router, prefix=settings.API_V1_STR)
    app.include_router(stocks.router, prefix=settings.API_V1_STR)
    app.include_router(trades.router, prefix=settings.API_V1_STR)
    app.include_router(users.router, prefix=settings.API_V1_STR)
    return app

app = create_app()