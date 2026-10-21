
import os

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TypedDict

from dotenv import load_dotenv


# ==========================================
# ENVIRONMENT CONFIGURATION
# ==========================================

# Return type: bool
# Load environment variables before importing
# application modules that depend on them.
environment_loaded: bool = load_dotenv()


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
    api_reports,
    api_insights,
    auth,
    browser_insights,
    browser_reports,
)


# ==========================================
# HEALTH RESPONSE DATA TYPE
# ==========================================

class HealthResponse(TypedDict):
    """
    Define the structure of the health-check response.

    status: str
        Application health status.

    database: str
        Database connection status.
    """

    status: str
    database: str


# ==========================================
# APPLICATION LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    """
    Validate application configuration on startup.

    Parameters:
        app (FastAPI):
            The FastAPI application instance.

    Returns:
        AsyncIterator[None]:
            An asynchronous lifespan iterator.

    The application runs while execution is
    suspended at the yield statement.
    """

    # Validate the API token configuration.
    get_api_token()

    yield


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app: FastAPI = FastAPI(
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

# Data type: str
# Read the HTTPS-only configuration from the environment.
session_https_setting: str = os.getenv(
    "SESSION_HTTPS_ONLY",
    "false",
)

# Data type: bool
# Convert the environment setting to a boolean.
session_https_only: bool = (
    session_https_setting.lower() == "true"
)

# Data type: str
# Retrieve the validated session secret.
session_secret: str = get_session_secret()

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="inventory_session",
    same_site="lax",
    https_only=session_https_only,
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
) -> HealthResponse:
    """
    Verify application and database availability.

    Parameters:
        db (Session):
            SQLAlchemy database session supplied
            through FastAPI dependency injection.

    Returns:
        HealthResponse:
            A dictionary containing two string fields:
            status and database.

    Raises:
        HTTPException:
            HTTP 503 when the database is unavailable.
    """

    try:
        db.execute(text("SELECT 1"))

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc

    # Data type: HealthResponse
    response: HealthResponse = {
        "status": "healthy",
        "database": "connected",
    }

    return response


# ==========================================
# BROWSER ROUTES
# ==========================================

app.include_router(auth.router)

app.include_router(products.router)

app.include_router(stock.router)

app.include_router(browser_insights.router)

app.include_router(browser_reports.router)


# ==========================================
# REST API ROUTES
# ==========================================

app.include_router(api_products.router)

app.include_router(api_stock.router)

app.include_router(api_reports.router)

app.include_router(api_insights.router)