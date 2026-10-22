from math import ceil
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Query as SQLAlchemyQuery
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement

from api_security import require_api_token
from database import get_db
from models import Product, StockMovement

from schemas import (
    ProductCreate,
    ProductListResponse,
    ProductUpdate,
    ProductResponse,
    StockMovementResponse,
    StockMovementListResponse,
)

from services.product_service import (
    create_product,
    update_product,
    validate_product,
    delete_product,
)


# ==========================================
# PRODUCT API DATA TYPES
# ==========================================

ProductSortField = Literal[
    "name",
    "price",
    "quantity",
    "category",
]

SortOrder = Literal[
    "asc",
    "desc",
]


# ==========================================
# API ROUTER CONFIGURATION
# ==========================================

router: APIRouter = APIRouter(
    prefix="/api/products",
    tags=["Products API"],
    dependencies=[Depends(require_api_token)],
)


# ==========================================
# LIST PRODUCTS
# ==========================================


@router.get(
    "/",
    response_model=ProductListResponse,
    summary="List products",
    description=(
        "Return a paginated list of inventory products. "
        "Products can be searched by name, filtered by category "
        "and stock status, and sorted by name, price, quantity, "
        "or category."
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
        description=("Case-insensitive partial search on the product name."),
    ),
    category: str | None = Query(
        default=None,
        description=("Case-insensitive exact match on product category."),
    ),
    low_stock: bool | None = Query(
        default=None,
        description=(
            "Filter products by stock status. Use true for "
            "products whose quantity is less than or equal "
            "to their low-stock level, or false for products "
            "above their low-stock level."
        ),
    ),
    sort_by: ProductSortField | None = Query(
        default=None,
        description=(
            "Field used to sort products. Supported values are "
            "name, price, quantity, and category."
        ),
    ),
    sort_order: SortOrder = Query(
        default="asc",
        description=("Sort direction. Supported values are asc and desc."),
    ),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    """
    Return a paginated, filtered, and sorted product list.

    Returns:
        ProductListResponse:
            Products and pagination information.
    """

    query: SQLAlchemyQuery = db.query(Product)

    # ======================================
    # SEARCH BY PRODUCT NAME
    # ======================================

    if search is not None:
        search_value: str = search.strip()

        if search_value:
            query = query.filter(Product.name.ilike(f"%{search_value}%"))

    # ======================================
    # FILTER BY CATEGORY
    # ======================================

    if category is not None:
        category_value: str = category.strip()

        if category_value:
            query = query.filter(func.lower(Product.category) == category_value.lower())

    # ======================================
    # FILTER BY STOCK STATUS
    # ======================================

    if low_stock is True:
        query = query.filter(Product.quantity <= Product.low_stock_level)

    elif low_stock is False:
        query = query.filter(Product.quantity > Product.low_stock_level)

    # ======================================
    # PAGINATION CALCULATIONS
    # ======================================

    total_items: int = query.count()

    total_pages: int = ceil(total_items / page_size) if total_items > 0 else 0

    # ======================================
    # SELECT SORT COLUMN
    # ======================================

    sort_column: ColumnElement | InstrumentedAttribute[int] | None = None

    if sort_by == "name":
        sort_column = func.lower(Product.name)

    elif sort_by == "price":
        sort_column = Product.price

    elif sort_by == "quantity":
        sort_column = Product.quantity

    elif sort_by == "category":
        sort_column = func.lower(Product.category)

    # ======================================
    # APPLY SORT ORDER
    # ======================================

    if sort_column is not None:
        if sort_order == "desc":
            query = query.order_by(
                sort_column.desc(),
                Product.id.asc(),
            )

        else:
            query = query.order_by(
                sort_column.asc(),
                Product.id.asc(),
            )

    else:
        query = query.order_by(Product.id.asc())

    # ======================================
    # FETCH PAGINATED PRODUCTS
    # ======================================

    offset: int = (page - 1) * page_size

    products: list[Product] = query.offset(offset).limit(page_size).all()

    # Construct the response using the
    # existing Pydantic response schema.
    response: ProductListResponse = ProductListResponse(
        items=[ProductResponse.model_validate(product) for product in products],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )

    return response


# ==========================================
# GET SINGLE PRODUCT
# ==========================================


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product",
    description=("Return a single inventory product using its product ID."),
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> Product:
    """
    Return one product by its ID.

    Raises:
        HTTPException:
            If the product does not exist.
    """

    product: Product | None = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


# ==========================================
# GET PRODUCT STOCK MOVEMENTS
# ==========================================


@router.get(
    "/{product_id}/stock-movements",
    response_model=StockMovementListResponse,
    summary="Get product stock movements",
    description=(
        "Return a paginated stock movement history for a "
        "specific product, ordered from newest to oldest."
    ),
)
def get_product_stock_movements(
    product_id: int,
    page: int = Query(
        default=1,
        ge=1,
        description="Page number starting from 1.",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description=("Number of stock movements returned per page."),
    ),
    db: Session = Depends(get_db),
) -> StockMovementListResponse:
    """
    Return paginated stock movement history.
    """

    product: Product | None = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    query: SQLAlchemyQuery = db.query(StockMovement).filter(
        StockMovement.product_id == product_id
    )

    total_items: int = query.count()

    total_pages: int = ceil(total_items / page_size) if total_items > 0 else 0

    offset: int = (page - 1) * page_size

    movements: list[StockMovement] = (
        query.order_by(
            StockMovement.created_at.desc(),
            StockMovement.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

    response: StockMovementListResponse = StockMovementListResponse(
        items=[
            StockMovementResponse.model_validate(movement) for movement in movements
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )

    return response


# ==========================================
# CREATE PRODUCT
# ==========================================


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
) -> Product:
    """
    Create a new inventory product.
    """

    result: Product | str = create_product(
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


# ==========================================
# UPDATE PRODUCT
# ==========================================


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
) -> Product:
    """
    Update an existing product.
    """

    error: str | None = validate_product(
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

    result: Product | str = update_product(
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


# ==========================================
# DELETE PRODUCT
# ==========================================


@router.delete(
    "/{product_id}",
    status_code=204,
    summary="Delete product",
    description=("Delete an inventory product using its product ID."),
)
def delete_product_api(
    product_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a product using its ID.

    Returns:
        None:
            Successful deletion produces HTTP 204.
    """

    error: str | None = delete_product(
        db,
        product_id,
    )

    if error == "product_not_found":
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return None
