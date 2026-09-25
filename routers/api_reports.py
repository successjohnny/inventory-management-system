import csv
import io
from datetime import date, datetime, time, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from api_security import require_api_token
from database import get_db
from models import Product, StockMovement


router = APIRouter(
    prefix="/api/reports",
    tags=["Reports API"],
    dependencies=[Depends(require_api_token)],
)


@router.get(
    "/inventory.csv",
    summary="Export inventory CSV",
    description=(
        "Export the current product inventory as a CSV file."
    ),
)
def export_inventory_csv(
    db: Session = Depends(get_db),
):
    """
    Export the current product inventory as CSV.
    """

    products = (
        db.query(Product)
        .order_by(Product.id.asc())
        .all()
    )

    output = io.StringIO()

    fieldnames = [
        "id",
        "name",
        "price",
        "quantity",
        "low_stock_level",
        "category",
        "supplier",
    ]

    writer = csv.DictWriter(
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

    headers = {
        "Content-Disposition": (
            'attachment; filename="inventory.csv"'
        ),
    }

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers,
    )


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
):
    """
    Export the stock movement history as CSV.

    When start_date is supplied, only movements on or after
    that date are exported.

    When end_date is supplied, only movements on or before
    that date are exported.

    Newest stock movements are exported first.
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

    query = db.query(StockMovement)

    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            time.min,
            tzinfo=timezone.utc,
        )

        query = query.filter(
            StockMovement.created_at >= start_datetime
        )

    if end_date is not None:
        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )

        query = query.filter(
            StockMovement.created_at < end_datetime
        )

    stock_movements = (
        query
        .order_by(
            StockMovement.created_at.desc(),
            StockMovement.id.desc(),
        )
        .all()
    )

    output = io.StringIO()

    fieldnames = [
        "id",
        "product_id",
        "movement_type",
        "quantity",
        "note",
        "created_at",
    ]

    writer = csv.DictWriter(
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

    headers = {
        "Content-Disposition": (
            'attachment; filename="stock-movements.csv"'
        ),
    }

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers,
    )


@router.get(
    "/summary",
    summary="Get inventory summary",
    description=(
        "Return summary statistics for the current inventory."
    ),
)
def get_inventory_summary(
    db: Session = Depends(get_db),
):
    """
    Return summary statistics for the current inventory.
    """

    products = db.query(Product).all()

    return {
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
