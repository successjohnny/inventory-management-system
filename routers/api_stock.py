from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import StockMovementCreate
from services.inventory_service import process_stock_movement


router = APIRouter(
    prefix="/api/stock-movements",
    tags=["Stock Movements API"],
)


@router.post(
    "/{product_id}",
    status_code=201,
)
def create_stock_movement(
    product_id: int,
    movement_data: StockMovementCreate,
    db: Session = Depends(get_db),
):
    error = process_stock_movement(
        db,
        product_id,
        movement_data.movement_type,
        movement_data.quantity,
        movement_data.note or "",
    )

    if error == "product_not_found":
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if error == "insufficient_stock":
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available.",
        )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error,
        )

    return {
        "message": "Stock movement created successfully."
    }