import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from api_security import require_api_token
from database import get_db
from models import Product


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
