from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


products = [
    {
        "name": "Laptop",
        "price": 200000,
        "quantity": 20,
        "category": "Electronics",
    },
    {
        "name": "Mouse",
        "price": 2000,
        "quantity": 50,
        "category": "Electronics",
    },
    {
        "name": "Keyboard",
        "price": 2500,
        "quantity": 30,
        "category": "Electronics",
    },
]


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"products": products},
    )