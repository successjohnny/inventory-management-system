from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from browser_security import (
    get_csrf_token,
    require_admin,
    require_csrf,
)
from database import get_db
from models import Product, StockMovement
from services.error_messages import ERROR_MESSAGES
from services.product_service import (
    create_product,
    update_product,
    validate_product,
    delete_product,
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
    redirect = require_admin(request)
    if redirect is not None:
        return redirect

    all_products = db.query(Product).all()

    movements = (
        db.query(StockMovement)
        .options(joinedload(StockMovement.product))
        .all()
    )

    normalized_search = search.strip().lower()

    if normalized_search:
        products = (
            db.query(Product)
            .filter(
                Product.normalized_name.ilike(
                    f"%{normalized_search}%"
                )
            )
            .all()
        )
    else:
        products = all_products

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "products": products,
            "total_products": len(all_products),
            "total_items": sum(
                product.quantity for product in all_products
            ),
            "total_categories": len({
                product.category for product in all_products
            }),
            "low_stock_products": sum(
                1
                for product in all_products
                if product.quantity <= product.low_stock_level
            ),
            "movements": movements,
            "error": ERROR_MESSAGES.get(error, error),
            "search": search,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/add-product")
def add_product(
    request: Request,
    name: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    low_stock_level: int = Form(...),
    category: str = Form(...),
    supplier: str = Form(""),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)
    if redirect is not None:
        return redirect

    require_csrf(request, csrf_token)

    error = validate_product(
        name, price, low_stock_level, category
    )

    if error:
        return RedirectResponse(
            url=f"/?error={error}",
            status_code=303,
        )

    if quantity < 0:
        return RedirectResponse(
            url="/?error=invalid_quantity",
            status_code=303,
        )

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

    return RedirectResponse(url="/", status_code=303)


@router.get("/edit-product/{product_id}")
def edit_product(
    request: Request,
    product_id: int,
    error: str = "",
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)
    if redirect is not None:
        return redirect

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

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
            "error": ERROR_MESSAGES.get(error, error),
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/edit-product/{product_id}")
def update_product_route(
    request: Request,
    product_id: int,
    name: str = Form(...),
    price: int = Form(...),
    low_stock_level: int = Form(...),
    category: str = Form(...),
    supplier: str = Form(""),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)
    if redirect is not None:
        return redirect

    require_csrf(request, csrf_token)

    error = validate_product(
        name, price, low_stock_level, category
    )

    if error:
        return RedirectResponse(
            url=f"/edit-product/{product_id}?error={error}",
            status_code=303,
        )

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
            url=f"/edit-product/{product_id}?error={result}",
            status_code=303,
        )

    return RedirectResponse(url="/", status_code=303)


@router.post("/delete-product/{product_id}")
def delete_product_route(
    request: Request,
    product_id: int,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)
    if redirect is not None:
        return redirect

    require_csrf(request, csrf_token)

    error = delete_product(db, product_id)

    if error == "product_not_found":
        return RedirectResponse(
            url="/?error=product_not_found",
            status_code=303,
        )

    return RedirectResponse(url="/", status_code=303)