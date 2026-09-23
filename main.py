import os

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from api_security import get_api_token
from auth_config import get_session_secret
from database import get_db

from routers import (
    products,
    stock,
    api_products,
    api_stock,
    auth,
)


# ==========================================
# APPLICATION LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Validate required application configuration
    when the FastAPI application starts.
    """

    get_api_token()

    yield


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Inventory Management System API",
    description=(
        "REST API for managing inventory products and stock movements. "
        "The API supports product creation, retrieval, updating and deletion, "
        "as well as stock-in and stock-out operations with movement history. "
        "Protected API endpoints require bearer-token authentication."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ==========================================
# SESSION MIDDLEWARE
# ==========================================

app.add_middleware(
    SessionMiddleware,
    secret_key=get_session_secret(),
    session_cookie="inventory_session",
    same_site="lax",
    https_only=(
        os.getenv(
            "SESSION_HTTPS_ONLY",
            "false",
        ).lower() == "true"
    ),
)


# ==========================================
# STATIC FILES
# ==========================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get(
    "/health",
    tags=["System"],
    summary="Check application health",
    description=(
        "Check whether the application is running and can "
        "successfully communicate with the database."
    ),
)
def health_check(
    db: Session = Depends(get_db),
):
    """
    Verify application and database availability.
    """

    try:
        db.execute(text("SELECT 1"))

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

    return {
        "status": "healthy",
        "database": "connected",
    }


# ==========================================
# BROWSER ROUTES
# ==========================================

app.include_router(auth.router)

app.include_router(products.router)

app.include_router(stock.router)


# ==========================================
# REST API ROUTES
# ==========================================

app.include_router(api_products.router)

app.include_router(api_stock.router)