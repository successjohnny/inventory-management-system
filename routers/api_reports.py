
import csv
import io
from datetime import date, datetime, time, timedelta, timezone
from typing import TypedDict

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm import Query as SQLAlchemyQuery

from api_security import require_api_token
from database import get_db
from models import Product, StockMovement
from schemas import ProductResponse


# ==========================================
# REPORT DATA TYPES
# ==========================================

class InventorySummary(TypedDict):
    total_products: int
    total_items: int
    total_categories: int
    low_stock_products: int


class CategorySummary(TypedDict):
    category: str
    total_products: int
    total_items: int


class ProductValuation(TypedDict):
    id: int
    name: str
    price: int
    quantity: int
    inventory_value: int


class InventoryValuation(TypedDict):
    total_inventory_value: int
    products: list[ProductValuation]


class SupplierSummary(TypedDict):
    supplier: str
    total_products: int
    total_items: int
    inventory_value: int


class CategoryValuation(TypedDict):
    category: str
    total_products: int
    total_items: int
    inventory_value: int


# ==========================================
# API ROUTER
# ==========================================

router: APIRouter = APIRouter(
    prefix="/api/reports",
    tags=["Reports API"],
    dependencies=[Depends(require_api_token)],
)


# ==========================================
# EXPORT INVENTORY CSV
# ==========================================

@router.get(
    "/inventory.csv",
    summary="Export inventory CSV",
    description=(
        "Export the current product inventory as a CSV file."
    ),
)
def export_inventory_csv(
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Export the current product inventory as CSV.
    """

    products: list[Product] = (
        db.query(Product)
        .order_by(Product.id.asc())
        .all()
    )

    output: io.StringIO = io.StringIO()

    fieldnames: list[str] = [
        "id",
        "name",
        "price",
        "quantity",
        "low_stock_level",
        "category",
        "supplier",
    ]

    writer: csv.DictWriter = csv.DictWriter(
        output,
        fieldnames=fieldnames,
    )

    writer.writeheader()

    for product in products:
        writer.writerow(
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": product.quantity,
                "low_stock_level": product.low_stock_level,
                "category": product.category,
                "supplier": product.supplier or "",
            }
        )

    output.seek(0)

    headers: dict[str, str] = {
        "Content-Disposition": (
            'attachment; filename="inventory.csv"'
        ),
    }

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers,
    )


# ==========================================
# EXPORT STOCK MOVEMENTS CSV
# ==========================================

@router.get(
    "/stock-movements.csv",
    summary="Export stock movements CSV",
    description=(
        "Export the stock movement history as a CSV file. "
        "Results can optionally be filtered by start date "
        "and end date."
    ),
)
def export_stock_movements_csv(
    start_date: date | None = Query(
        default=None,
        description=(
            "Export stock movements on or after this date."
        ),
    ),
    end_date: date | None = Query(
        default=None,
        description=(
            "Export stock movements on or before this date."
        ),
    ),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """
    Export the stock movement history as CSV.

    Dates are inclusive.
    Newest movements are exported first.
    """

    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "start_date cannot be later than end_date."
            ),
        )

    query: SQLAlchemyQuery = db.query(StockMovement)

    if start_date is not None:
        start_datetime: datetime = datetime.combine(
            start_date,
            time.min,
            tzinfo=timezone.utc,
        )

        query = query.filter(
            StockMovement.created_at >= start_datetime
        )

    if end_date is not None:
        end_datetime: datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )

        query = query.filter(
            StockMovement.created_at < end_datetime
        )

    stock_movements: list[StockMovement] = (
        query
        .order_by(
            StockMovement.created_at.desc(),
            StockMovement.id.desc(),
        )
        .all()
    )

    output: io.StringIO = io.StringIO()

    fieldnames: list[str] = [
        "id",
        "product_id",
        "movement_type",
        "quantity",
        "note",
        "created_at",
    ]

    writer: csv.DictWriter = csv.DictWriter(
        output,
        fieldnames=fieldnames,
    )

    writer.writeheader()

    for movement in stock_movements:
        writer.writerow(
            {
                "id": movement.id,
                "product_id": movement.product_id,
                "movement_type": movement.movement_type,
                "quantity": movement.quantity,
                "note": movement.note or "",
                "created_at": movement.created_at.isoformat(),
            }
        )

    output.seek(0)

    headers: dict[str, str] = {
        "Content-Disposition": (
            'attachment; filename="stock-movements.csv"'
        ),
    }

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers,
    )


# ==========================================
# INVENTORY SUMMARY
# ==========================================

@router.get(
    "/summary",
    summary="Get inventory summary",
    description=(
        "Return summary statistics for the current inventory."
    ),
)
def get_inventory_summary(
    db: Session = Depends(get_db),
) -> InventorySummary:
    """
    Return summary statistics for the current inventory.
    """

    products: list[Product] = db.query(Product).all()

    summary: InventorySummary = {
        "total_products": len(products),
        "total_items": sum(
            product.quantity
            for product in products
        ),
        "total_categories": len(
            {
                product.category
                for product in products
            }
        ),
        "low_stock_products": sum(
            1
            for product in products
            if product.quantity
            <= product.low_stock_level
        ),
    }

    return summary


# ==========================================
# LOW STOCK REPORT
# ==========================================

@router.get(
    "/low-stock",
    response_model=list[ProductResponse],
    summary="Get low-stock report",
    description=(
        "Return products whose current quantity is less than "
        "or equal to their configured low-stock level."
    ),
)
def get_low_stock_report(
    db: Session = Depends(get_db),
) -> list[Product]:
    """
    Return all products currently at or below
    their configured low-stock level.
    """

    products: list[Product] = (
        db.query(Product)
        .filter(
            Product.quantity
            <= Product.low_stock_level
        )
        .order_by(Product.id.asc())
        .all()
    )

    return products


# ==========================================
# CATEGORY SUMMARY REPORT
# ==========================================

@router.get(
    "/categories",
    summary="Get category summary report",
    description=(
        "Return inventory statistics grouped by product category."
    ),
)
def get_category_summary_report(
    db: Session = Depends(get_db),
) -> list[CategorySummary]:
    """
    Return product counts and total item quantities
    grouped by category.
    """

    results: list[tuple[str, int, int]] = (
        db.query(
            Product.category,
            func.count(Product.id).label("total_products"),
            func.sum(Product.quantity).label("total_items"),
        )
        .group_by(Product.category)
        .order_by(Product.category.asc())
        .all()
    )

    report: list[CategorySummary] = [
        {
            "category": category,
            "total_products": total_products,
            "total_items": total_items,
        }
        for category, total_products, total_items in results
    ]

    return report


# ==========================================
# INVENTORY VALUATION REPORT
# ==========================================

@router.get(
    "/valuation",
    summary="Get inventory valuation report",
    description=(
        "Return the monetary value of each product in inventory "
        "and the total value of all inventory."
    ),
)
def get_inventory_valuation_report(
    db: Session = Depends(get_db),
) -> InventoryValuation:
    """
    Return product-level inventory valuations
    and the total value of all inventory.
    """

    products: list[Product] = (
        db.query(Product)
        .order_by(Product.id.asc())
        .all()
    )

    product_valuations: list[ProductValuation] = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity,
            "inventory_value": (
                product.price * product.quantity
            ),
        }
        for product in products
    ]

    valuation: InventoryValuation = {
        "total_inventory_value": sum(
            product["inventory_value"]
            for product in product_valuations
        ),
        "products": product_valuations,
    }

    return valuation


# ==========================================
# SUPPLIER SUMMARY REPORT
# ==========================================

@router.get(
    "/suppliers",
    summary="Get supplier summary report",
    description=(
        "Return inventory statistics and valuation "
        "grouped by product supplier."
    ),
)
def get_supplier_summary_report(
    db: Session = Depends(get_db),
) -> list[SupplierSummary]:
    """
    Return product counts, total item quantities,
    and inventory values grouped by supplier.
    """

    results: list[tuple[str, int, int, int]] = (
        db.query(
            Product.supplier,
            func.count(Product.id).label(
                "total_products"
            ),
            func.sum(Product.quantity).label(
                "total_items"
            ),
            func.sum(
                Product.price * Product.quantity
            ).label("inventory_value"),
        )
        .filter(Product.supplier.isnot(None))
        .group_by(Product.supplier)
        .order_by(Product.supplier.asc())
        .all()
    )

    report: list[SupplierSummary] = [
        {
            "supplier": supplier,
            "total_products": total_products,
            "total_items": total_items,
            "inventory_value": inventory_value,
        }
        for (
            supplier,
            total_products,
            total_items,
            inventory_value,
        ) in results
    ]

    return report


# ==========================================
# CATEGORY VALUATION REPORT
# ==========================================

@router.get(
    "/category-valuations",
    summary="Get category inventory valuation report",
    description=(
        "Return inventory statistics and valuation "
        "grouped by product category."
    ),
)
def get_category_valuation_report(
    db: Session = Depends(get_db),
) -> list[CategoryValuation]:
    """
    Return product counts, total item quantities,
    and inventory values grouped by category.
    """

    results: list[tuple[str, int, int, int]] = (
        db.query(
            Product.category,
            func.count(Product.id).label(
                "total_products"
            ),
            func.sum(Product.quantity).label(
                "total_items"
            ),
            func.sum(
                Product.price * Product.quantity
            ).label("inventory_value"),
        )
        .group_by(Product.category)
        .order_by(Product.category.asc())
        .all()
    )

    report: list[CategoryValuation] = [
        {
            "category": category,
            "total_products": total_products,
            "total_items": total_items,
            "inventory_value": inventory_value,
        }
        for (
            category,
            total_products,
            total_items,
            inventory_value,
        ) in results
    ]

    return report