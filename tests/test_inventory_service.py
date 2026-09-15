from sqlalchemy.exc import SQLAlchemyError

from services.inventory_service import process_stock_movement
from services.product_service import create_product
from models import Product, StockMovement


def test_stock_in(db_session):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = process_stock_movement(
        db_session,
        product.id,
        "IN",
        5,
        "New delivery",
    )

    assert result is None
    assert product.quantity == 15


def test_stock_out(db_session):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = process_stock_movement(
        db_session,
        product.id,
        "OUT",
        3,
        "Customer purchase",
    )

    assert result is None
    assert product.quantity == 7


def test_insufficient_stock(db_session):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = process_stock_movement(
        db_session,
        product.id,
        "OUT",
        15,
        "Customer purchase",
    )

    assert result == "insufficient_stock"
    assert product.quantity == 10


def test_invalid_movement_quantity(db_session):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = process_stock_movement(
        db_session,
        product.id,
        "IN",
        0,
        "Invalid delivery",
    )

    assert result == "invalid_movement_quantity"
    assert product.quantity == 10


def test_invalid_movement_type(db_session):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = process_stock_movement(
        db_session,
        product.id,
        "INVALID",
        5,
        "Invalid movement",
    )

    assert result == "invalid_movement_type"
    assert product.quantity == 10


def test_stock_movement_history(db_session):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = process_stock_movement(
        db_session,
        product.id,
        "IN",
        5,
        "New delivery",
    )

    assert result is None

    movement = db_session.query(
        StockMovement
    ).filter(
        StockMovement.product_id == product.id
    ).first()

    assert movement is not None
    assert movement.product_id == product.id
    assert movement.movement_type == "IN"
    assert movement.quantity == 5
    assert movement.note == "New delivery"
    assert movement.created_at is not None


def test_failed_stock_movement_creates_no_history(db_session):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = process_stock_movement(
        db_session,
        product.id,
        "OUT",
        15,
        "Customer purchase",
    )

    assert result == "insufficient_stock"
    assert product.quantity == 10

    movements = db_session.query(
        StockMovement
    ).filter(
        StockMovement.product_id == product.id
    ).all()

    assert movements == []


def test_invalid_movement_type_creates_no_history(
    db_session,
):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = process_stock_movement(
        db_session,
        product.id,
        "INVALID",
        5,
        "Invalid movement",
    )

    assert result == "invalid_movement_type"
    assert product.quantity == 10

    movements = db_session.query(
        StockMovement
    ).filter(
        StockMovement.product_id == product.id
    ).all()

    assert movements == []


def test_invalid_movement_quantity_creates_no_history(
    db_session,
):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = process_stock_movement(
        db_session,
        product.id,
        "IN",
        0,
        "Invalid delivery",
    )

    assert result == "invalid_movement_quantity"
    assert product.quantity == 10

    movements = db_session.query(
        StockMovement
    ).filter(
        StockMovement.product_id == product.id
    ).all()

    assert movements == []

def test_stock_movement_product_not_found(db_session):
    result = process_stock_movement(
        db_session,
        999,
        "IN",
        5,
        "New delivery",
    )

    assert result == "product_not_found"

    movements = db_session.query(
        StockMovement
    ).all()

    assert movements == []

def test_stock_movement_transaction_rollback(
    db_session,
    monkeypatch,
):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    def failed_commit():
        raise SQLAlchemyError("Database failure")

    monkeypatch.setattr(
        db_session,
        "commit",
        failed_commit,
    )

    result = process_stock_movement(
        db_session,
        product.id,
        "IN",
        5,
        "New delivery",
    )

    assert result == "stock_movement_failed"

    db_session.expire_all()

    refreshed_product = db_session.query(
        Product
    ).filter(
        Product.id == product.id
    ).first()

    assert refreshed_product.quantity == 10

    movements = db_session.query(
        StockMovement
    ).filter(
        StockMovement.product_id == product.id
    ).all()

    assert movements == []