from math import ceil
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from api_security import require_api_token
from database import get_db
from models import Product, StockMovement

from schemas import (
    ProductCreate,
    ProductListResponse,
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
    response_model=ProductListResponse,
    summary="List products",
    description=(
        "Return a paginated list of inventory products. "
        "Products can be filtered by name, category, and "
        "low-stock status and sorted by name, price, "
        "quantity, or category. "
        "Use the page and page_size query parameters to "
        "control pagination."
    ),
)
def get_products(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number starting from 1.",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of products returned per page.",
    ),
    search: str | None = Query(
        default=None,
        description=(
            "Case-insensitive partial search by product name."
        ),
    ),
    category: str | None = Query(
        default=None,
        description=(
            "Case-insensitive filter by product category."
        ),
    ),
    low_stock: bool | None = Query(
        default=None,
        description=(
            "Filter products by low-stock status. "
            "A product is low stock when its quantity is "
            "less than or equal to its low-stock level."
        ),
    ),
    sort_by: Literal[
        "name",
        "price",
        "quantity",
        "category",
    ] | None = Query(
        default=None,
        description=(
            "Product field used for sorting."
        ),
    ),
    sort_order: Literal[
        "asc",
        "desc",
    ] = Query(
        default="asc",
        description=(
            "Sort direction: ascending or descending."
        ),
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Product)

    if search:
        search_value = search.strip().lower()

        if search_value:
            query = query.filter(
                func.lower(Product.name).contains(
                    search_value
                )
            )

    if category:
        category_value = category.strip().lower()

        if category_value:
            query = query.filter(
                func.lower(Product.category)
                == category_value
            )

    if low_stock is True:
        query = query.filter(
            Product.quantity <= Product.low_stock_level
        )

    elif low_stock is False:
        query = query.filter(
            Product.quantity > Product.low_stock_level
        )

    total_items = query.count()

    total_pages = (
        ceil(total_items / page_size)
        if total_items > 0
        else 0
    )

    offset = (page - 1) * page_size

    sort_columns = {
        "name": func.lower(Product.name),
        "price": Product.price,
        "quantity": Product.quantity,
        "category": func.lower(Product.category),
    }

    if sort_by:
        sort_column = sort_columns[sort_by]

        if sort_order == "desc":
            order_by = sort_column.desc()
        else:
            order_by = sort_column.asc()

        products = (
            query
            .order_by(
                order_by,
                Product.id.asc(),
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )

    else:
        products = (
            query
            .order_by(Product.id.asc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

    return {
        "items": products,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
    }


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