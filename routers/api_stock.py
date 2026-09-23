from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session, joinedload

from api_security import require_api_token
from database import get_db
from models import StockMovement
from schemas import (
    StockMovementCreate,
    StockMovementResponse,
)
from services.inventory_service import (
    process_stock_movement,
)


router = APIRouter(
    prefix="/api/stock-movements",
    tags=["Stock Movements API"],
    dependencies=[Depends(require_api_token)],
)


@router.get(
    "/",
    response_model=list[StockMovementResponse],
    summary="List stock movements",
    description=(
        "Return the complete stock movement history. "
        "The newest stock movements are returned first."
    ),
)
def get_stock_movements(
    db: Session = Depends(get_db),
):
    """
    Return all stock movements.

    Newest stock movements are returned first.
    """

    movements = (
        db.query(StockMovement)
        .options(
            joinedload(
                StockMovement.product
            )
        )
        .order_by(
            StockMovement.created_at.desc(),
            StockMovement.id.desc(),
        )
        .all()
    )

    return movements


@router.post(
    "/{product_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Create stock movement",
    description=(
        "Create a stock IN or OUT movement for a product. "
        "Stock IN increases the product quantity, while stock OUT "
        "decreases it. Stock OUT is rejected when there is "
        "insufficient inventory."
    ),
)
def create_stock_movement(
    product_id: int,
    movement: StockMovementCreate,
    db: Session = Depends(get_db),
):
    """
    Create a stock IN or OUT movement for a product.
    """

    error = process_stock_movement(
        db,
        product_id,
        movement.movement_type,
        movement.quantity,
        movement.note or "",
    )

    if error == "product_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if error == "insufficient_stock":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock available.",
        )

    if error == "invalid_movement_type":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_movement_type",
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return {
        "message": (
            "Stock movement created successfully."
        )
    }