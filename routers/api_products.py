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
)
def get_products(
    db: Session = Depends(get_db),
):
    products = db.query(Product).all()

    return products


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@router.get(
    "/{product_id}/stock-movements",
    response_model=list[StockMovementResponse],
)
def get_product_stock_movements(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

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