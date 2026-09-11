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
def home(request: Request, search: str = ""):
    db = SessionLocal()

    # Get all products for dashboard statistics
    all_products = db.query(Product).all()

    # Get products to display in the table
    if search:
        products = db.query(Product).filter(
            Product.name.ilike(f"%{search}%")
        ).all()
    else:
        products = all_products

    # Dashboard statistics
    total_products = len(all_products)

    total_items = sum(
        product.quantity
        for product in all_products
    )

    categories = set(
        product.category
        for product in all_products
    )

    total_categories = len(categories)

    low_stock_products = sum(
        1
        for product in all_products
        if product.quantity <= product.low_stock_level
    )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "products": products,
            "total_products": total_products,
            "total_items": total_items,
            "total_categories": total_categories,
            "low_stock_products": low_stock_products,
        },
    )



@app.post("/add-product")
def add_product(
    name: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    low_stock_level: int = Form(...),
    category: str = Form(...),
):
    db = SessionLocal()

    product = Product(
        name=name,
        price=price,
        quantity=quantity,
        low_stock_level=low_stock_level,
        category=category,
    )

    db.add(product)
    db.commit()

    db.close()

    return RedirectResponse(url="/", status_code=303)


@app.get("/edit-product/{product_id}")
def edit_product(request: Request, product_id: int):
    db = SessionLocal()

    product = db.query(Product).filter(Product.id == product_id).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="edit_product.html",
        context={"product": product},
    )


@app.post("/edit-product/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    low_stock_level: int = Form(...),
    category: str = Form(...),
):
    db = SessionLocal()

    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        product.name = name
        product.price = price
        product.quantity = quantity
        product.low_stock_level = low_stock_level
        product.category = category

        db.commit()

    db.close()

    return RedirectResponse(url="/", status_code=303)

@app.get("/delete-product/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()

    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        db.delete(product)
        db.commit()

    db.close()

    return RedirectResponse(url="/", status_code=303)