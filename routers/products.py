from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Product, StockMovement
from services.error_messages import ERROR_MESSAGES
from services.product_service import (
    create_product,
    update_product,
    validate_product,
)


router = APIRouter()


templates = Jinja2Templates(directory="templates")


@router.get("/")
def home(
    request: Request,
    search: str = "",
    error: str = "",
    db: Session = Depends(get_db),
):
    # Get all products for dashboard statistics
    all_products = db.query(Product).all()

    # Get stock movements together with their products
    movements = (
        db.query(StockMovement)
        .options(joinedload(StockMovement.product))
        .all()
    )

    # Normalize the search text
    normalized_search = search.strip().lower()

    # Search products using normalized_name
    if normalized_search:
        products = db.query(Product).filter(
            Product.normalized_name.ilike(
                f"%{normalized_search}%"
            )
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
            "error": ERROR_MESSAGES.get(error, error),
            "search": search,
        },
    )


@router.post("/add-product")
def add_product(
    name: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    low_stock_level: int = Form(...),
    category: str = Form(...),
    supplier: str = Form(""),
    db: Session = Depends(get_db),
):
    # Validate product information
    error = validate_product(
        name,
        price,
        low_stock_level,
        category,
    )

    if error:
        return RedirectResponse(
            url=f"/?error={error}",
            status_code=303,
        )

    # Validate quantity
    if quantity < 0:
        return RedirectResponse(
            url="/?error=invalid_quantity",
            status_code=303,
        )

    # Create the product
    result = create_product(
        db,
        name,
        price,
        quantity,
        low_stock_level,
        category,
        supplier,
    )

    if isinstance(result, str):
        return RedirectResponse(
            url=f"/?error={result}",
            status_code=303,
        )

    return RedirectResponse(
        url="/",
        status_code=303,
    )


@router.get("/edit-product/{product_id}")
def edit_product(
    request: Request,
    product_id: int,
    error: str = "",
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        return RedirectResponse(
            url="/?error=product_not_found",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_product.html",
        context={
            "product": product,
            "error": error,
        },
    )


@router.post("/edit-product/{product_id}")
def update_product_route(
    product_id: int,
    name: str = Form(...),
    price: int = Form(...),
    low_stock_level: int = Form(...),
    category: str = Form(...),
    supplier: str = Form(""),
    db: Session = Depends(get_db),
):
    # Validate product information
    error = validate_product(
        name,
        price,
        low_stock_level,
        category,
    )

    if error:
        return RedirectResponse(
            url=(
                f"/edit-product/"
                f"{product_id}"
                f"?error={error}"
            ),
            status_code=303,
        )

    # Update the product
    result = update_product(
        db,
        product_id,
        name,
        price,
        low_stock_level,
        category,
        supplier,
    )

    if isinstance(result, str):
        return RedirectResponse(
            url=(
                f"/edit-product/"
                f"{product_id}"
                f"?error={result}"
            ),
            status_code=303,
        )

    return RedirectResponse(
        url="/",
        status_code=303,
    )


@router.get("/delete-product/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product:
        db.delete(product)
        db.commit()

    return RedirectResponse(
        url="/",
        status_code=303,
    )