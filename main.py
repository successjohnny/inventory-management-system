from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import Base, engine, SessionLocal
from models import Product

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")



@app.get("/")
def home(request: Request):
    db = SessionLocal()

    products = db.query(Product).all()

    total_products = len(products)
    total_items = sum(product.quantity for product in products)

    categories = set(product.category for product in products)
    total_categories = len(categories)

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "products": products,
            "total_products": total_products,
            "total_items": total_items,
            "total_categories": total_categories,
        },
    )


@app.post("/add-product")
def add_product(
    name: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    category: str = Form(...),
):
    db = SessionLocal()

    product = Product(
        name=name,
        price=price,
        quantity=quantity,
        category=category,
    )

    db.add(product)
    db.commit()

    db.close()

    return RedirectResponse(url="/", status_code=303)