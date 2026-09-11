from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import joinedload

from database import Base, engine, SessionLocal
from models import Product, StockMovement


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(
    request: Request,
    search: str = "",
    error: str = "",
):
    db = SessionLocal()

    # Get all products for dashboard statistics
    all_products = db.query(Product).all()

    # Get stock movements together with their products
    movements = db.query(StockMovement).options(
        joinedload(StockMovement.product)
    ).all()

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
            "movements": movements,
            "error": error,
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
    # Remove unnecessary spaces
    name = name.strip()
    category = category.strip()

    # Validate product name
    if not name:
        return RedirectResponse(
            url="/?error=name_required",
            status_code=303,
        )

    # Validate price
    if price <= 0:
        return RedirectResponse(
            url="/?error=invalid_price",
            status_code=303,
        )

    # Validate quantity
    if quantity < 0:
        return RedirectResponse(
            url="/?error=invalid_quantity",
            status_code=303,
        )

    # Validate low stock level
    if low_stock_level < 0:
        return RedirectResponse(
            url="/?error=invalid_low_stock",
            status_code=303,
        )

    # Validate category
    if not category:
        return RedirectResponse(
            url="/?error=category_required",
            status_code=303,
        )

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

    return RedirectResponse(
        url="/",
        status_code=303,
    )


@app.get("/edit-product/{product_id}")
def edit_product(
    request: Request,
    product_id: int,
    error: str = "",
):
    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="edit_product.html",
        context={
            "product": product,
            "error": error,
        },
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
    # Remove unnecessary spaces
    name = name.strip()
    category = category.strip()

    # Validate product name
    if not name:
        return RedirectResponse(
            url=f"/edit-product/{product_id}?error=name_required",
            status_code=303,
        )

    # Validate price
    if price <= 0:
        return RedirectResponse(
            url=f"/edit-product/{product_id}?error=invalid_price",
            status_code=303,
        )

    # Validate quantity
    if quantity < 0:
        return RedirectResponse(
            url=f"/edit-product/{product_id}?error=invalid_quantity",
            status_code=303,
        )

    # Validate low stock level
    if low_stock_level < 0:
        return RedirectResponse(
            url=f"/edit-product/{product_id}?error=invalid_low_stock",
            status_code=303,
        )

    # Validate category
    if not category:
        return RedirectResponse(
            url=f"/edit-product/{product_id}?error=category_required",
            status_code=303,
        )

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        db.close()

        return RedirectResponse(
            url="/",
            status_code=303,
        )

    product.name = name
    product.price = price
    product.quantity = quantity
    product.low_stock_level = low_stock_level
    product.category = category

    db.commit()
    db.close()

    return RedirectResponse(
        url="/",
        status_code=303,
    )


@app.post("/stock-movement/{product_id}")
def stock_movement(
    product_id: int,
    movement_type: str = Form(...),
    quantity: int = Form(...),
    note: str = Form(""),
):
    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product and quantity > 0:

        if movement_type == "IN":

            product.quantity += quantity

        elif movement_type == "OUT":

            if quantity > product.quantity:
                db.close()

                return RedirectResponse(
                    url=(
                        f"/edit-product/"
                        f"{product_id}"
                        f"?error=insufficient_stock"
                    ),
                    status_code=303,
                )

            product.quantity -= quantity

        else:
            db.close()

            return RedirectResponse(
                url=f"/edit-product/{product_id}",
                status_code=303,
            )

        movement = StockMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity,
            note=note,
        )

        db.add(movement)
        db.commit()

    db.close()

    return RedirectResponse(
        url="/",
        status_code=303,
    )


@app.get("/delete-product/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product:
        db.delete(product)
        db.commit()

    db.close()

    return RedirectResponse(
        url="/",
        status_code=303,
    )