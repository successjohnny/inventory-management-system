import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from auth_config import get_session_secret
from routers import products, stock, api_products, api_stock, auth


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=get_session_secret(),
    session_cookie="inventory_session",
    same_site="lax",
    https_only=os.getenv("SESSION_HTTPS_ONLY", "false").lower() == "true",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(stock.router)
app.include_router(api_products.router)
app.include_router(api_stock.router)