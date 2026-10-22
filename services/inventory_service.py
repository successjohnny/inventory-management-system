from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import Product, StockMovement


# ==========================================
# PROCESS STOCK MOVEMENT
# ==========================================


def process_stock_movement(
    db: Session,
    product_id: int,
    movement_type: str,
    quantity: int,
    note: str,
) -> str | None:
    """
    Process a stock movement safely.

    Parameters:
        db (Session):
            SQLAlchemy database session.

        product_id (int):
            Unique identifier of the product.

        movement_type (str):
            Stock movement direction.
            Expected values are "IN" or "OUT".

        quantity (int):
            Number of units to add or remove.

        note (str):
            Description of the stock movement.

    Returns:
        None:
            Stock movement completed successfully.

        str:
            Error code when the operation fails.
    """

    # ======================================
    # FIND PRODUCT
    # ======================================

    # Data type: Product | None
    product: Product | None = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        return "product_not_found"

    # ======================================
    # VALIDATE QUANTITY
    # ======================================

    if quantity <= 0:
        return "invalid_movement_quantity"

    # ======================================
    # VALIDATE MOVEMENT TYPE
    # ======================================

    if movement_type not in ("IN", "OUT"):
        return "invalid_movement_type"

    # ======================================
    # PROCESS STOCK IN
    # ======================================

    if movement_type == "IN":
        product.quantity += quantity

    # ======================================
    # PROCESS STOCK OUT
    # ======================================

    elif movement_type == "OUT":
        if quantity > product.quantity:
            return "insufficient_stock"

        product.quantity -= quantity

    # ======================================
    # CLEAN MOVEMENT NOTE
    # ======================================

    # Data type: str
    note = note.strip()

    # ======================================
    # CREATE MOVEMENT HISTORY
    # ======================================

    # Data type: StockMovement
    movement: StockMovement = StockMovement(
        product_id=product_id,
        movement_type=movement_type,
        quantity=quantity,
        note=note,
    )

    db.add(movement)

    # ======================================
    # SAVE DATABASE TRANSACTION
    # ======================================

    try:
        db.commit()

    except SQLAlchemyError:
        # Roll back database changes when
        # the transaction fails.
        db.rollback()

        return "stock_movement_failed"

    return None
