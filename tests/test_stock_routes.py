from models import Product, StockMovement


def create_product(db):
    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=100000,
        quantity=10,
        low_stock_level=5,
        category="Electronics",
        supplier="ABC Electronics",
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def test_stock_in(client):
    test_client, db = client

    product = create_product(db)

    response = test_client.post(
        f"/stock-movement/{product.id}",
        data={
            "movement_type": "IN",
            "quantity": "5",
            "note": "New stock received",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    db.refresh(product)

    assert product.quantity == 15

    movement = db.query(StockMovement).filter(
        StockMovement.product_id == product.id
    ).first()

    assert movement is not None
    assert movement.movement_type == "IN"
    assert movement.quantity == 5
    assert movement.note == "New stock received"


def test_stock_out(client):
    test_client, db = client

    product = create_product(db)

    response = test_client.post(
        f"/stock-movement/{product.id}",
        data={
            "movement_type": "OUT",
            "quantity": "4",
            "note": "Customer sale",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    db.refresh(product)

    assert product.quantity == 6

    movement = db.query(StockMovement).filter(
        StockMovement.product_id == product.id
    ).first()

    assert movement is not None
    assert movement.movement_type == "OUT"
    assert movement.quantity == 4
    assert movement.note == "Customer sale"


def test_stock_out_insufficient_stock(client):
    test_client, db = client

    product = create_product(db)

    response = test_client.post(
        f"/stock-movement/{product.id}",
        data={
            "movement_type": "OUT",
            "quantity": "20",
            "note": "Large order",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == f"/edit-product/{product.id}?error=insufficient_stock"
    )

    db.refresh(product)

    assert product.quantity == 10

    movement = db.query(StockMovement).filter(
        StockMovement.product_id == product.id
    ).first()

    assert movement is None


def test_stock_invalid_quantity(client):
    test_client, db = client

    product = create_product(db)

    response = test_client.post(
        f"/stock-movement/{product.id}",
        data={
            "movement_type": "IN",
            "quantity": "0",
            "note": "Invalid movement",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == f"/edit-product/{product.id}?error=invalid_movement_quantity"
    )

    db.refresh(product)

    assert product.quantity == 10


def test_stock_product_not_found(client):
    test_client, db = client

    response = test_client.post(
        "/stock-movement/9999",
        data={
            "movement_type": "IN",
            "quantity": "5",
            "note": "Test movement",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == "/?error=product_not_found"
    )