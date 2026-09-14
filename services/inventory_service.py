from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import Product, StockMovement


def process_stock_movement(
    db: Session,
    product_id,
    movement_type,
    quantity,
    note,
):
    """
    Process a stock movement safely.

    Returns:
        None when successful.
        An error code when validation fails.
    """

    # Find the product
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        return "product_not_found"

    # Validate movement quantity
    if quantity <= 0:
        return "invalid_movement_quantity"

    # Validate movement type
    if movement_type not in ("IN", "OUT"):
        return "invalid_movement_type"

    # Stock In
    if movement_type == "IN":
        product.quantity += quantity

    # Stock Out
    elif movement_type == "OUT":

        if quantity > product.quantity:
            return "insufficient_stock"

        product.quantity -= quantity

    # Clean the note
    note = note.strip()

    # Create movement history record
    movement = StockMovement(
        product_id=product_id,
        movement_type=movement_type,
        quantity=quantity,
        note=note,
    )

    db.add(movement)

    # Save both the quantity change
    # and movement history together.
    try:
        db.commit()

    except SQLAlchemyError:
        # Undo all changes made during
        # this transaction.
        db.rollback()

        return "stock_movement_failed"

    return None