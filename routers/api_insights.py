from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api_security import require_api_token
from database import get_db
from models import Product
from services.inventory_insights import build_inventory_insights


router = APIRouter(
    prefix="/api/insights",
    tags=["Inventory Insights API"],
    dependencies=[Depends(require_api_token)],
)


@router.get(
    "",
    summary="Get inventory insights",
    description=(
        "Return structured inventory statistics, low-stock "
        "information, and inventory recommendations."
    ),
)
def get_inventory_insights(
    db: Session = Depends(get_db),
):
    """
    Return structured insights for the current inventory.
    """

    products = (
        db.query(Product)
        .order_by(Product.id.asc())
        .all()
    )

    return build_inventory_insights(products)
