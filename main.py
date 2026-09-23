import os

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from api_security import get_api_token
from auth_config import get_session_secret

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