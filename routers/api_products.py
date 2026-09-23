from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_security import require_api_token
from database import get_db
from models import Product, StockMovement

from schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    StockMovementResponse,
)

from services.product_service import (
    create_product,
    update_product,
    validate_product,
    delete_product,
)


router = APIRouter(
    prefix="/api/products",
    tags=["Products API"],
    dependencies=[Depends(require_api_token)],
)


@router.get(
    "/",
    response_model=list[ProductResponse],
    summary="List products",
    description=(
        "Return all products currently stored in the inventory."
    ),
)
def get_products(
    db: Session = Depends(get_db),
):
    products = db.query(Product).all()

    return products


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product",
    description=(
        "Return a single inventory product using its product ID."
    ),
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@router.get(
    "/{product_id}/stock-movements",
    response_model=list[StockMovementResponse],
    summary="Get product stock movements",
    description=(
        "Return the stock movement history for a specific product. "
        "The newest movements are returned first."
    ),
)
def get_product_stock_movements(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    movements = (
        db.query(StockMovement)
        .filter(
            StockMovement.product_id == product_id
        )
        .order_by(
            StockMovement.created_at.desc(),
            StockMovement.id.desc(),
        )
        .all()
    )

    return movements


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=201,
    summary="Create product",
    description=(
        "Create a new inventory product with its initial quantity, "
        "price, category, supplier and low-stock level."
    ),
)
def create_product_api(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    result = create_product(
        db,
        product_data.name,
        product_data.price,
        product_data.quantity,
        product_data.low_stock_level,
        product_data.category,
        product_data.supplier or "",
    )

    if isinstance(result, str):
        raise HTTPException(
            status_code=400,
            detail=result,
        )

    return result


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
    description=(
        "Update an existing product's name, price, category, "
        "supplier and low-stock level."
    ),
)
def update_product_api(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    error = validate_product(
        product_data.name,
        product_data.price,
        product_data.low_stock_level,
        product_data.category,
    )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error,
        )

    result = update_product(
        db,
        product_id,
        product_data.name,
        product_data.price,
        product_data.low_stock_level,
        product_data.category,
        product_data.supplier or "",
    )

    if result == "product_not_found":
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if isinstance(result, str):
        raise HTTPException(
            status_code=400,
            detail=result,
        )

    return result


@router.delete(
    "/{product_id}",
    status_code=204,
    summary="Delete product",
    description=(
        "Delete an inventory product using its product ID."
    ),
)
def delete_product_api(
    product_id: int,
    db: Session = Depends(get_db),
):
    error = delete_product(
        db,
        product_id,
    )

    if error == "product_not_found":
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return None