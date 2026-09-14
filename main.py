from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import products, stock


app = FastAPI()


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


app.include_router(products.router)
app.include_router(stock.router)