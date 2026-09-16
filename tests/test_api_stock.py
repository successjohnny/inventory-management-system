def create_test_product(test_client):
    response = test_client.post(
        "/api/products/",
        json={
            "name": "Test Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_stock_in(client):
    test_client, db = client

    product_id = create_test_product(test_client)

    response = test_client.post(
        f"/api/stock-movements/{product_id}",
        json={
            "movement_type": "IN",
            "quantity": 5,
            "note": "New shipment",
        },
    )

    assert response.status_code == 201

    assert response.json() == {
        "message": "Stock movement created successfully."
    }

    product_response = test_client.get(
        f"/api/products/{product_id}"
    )

    assert product_response.status_code == 200
    assert product_response.json()["quantity"] == 15


def test_stock_out(client):
    test_client, db = client

    product_id = create_test_product(test_client)

    response = test_client.post(
        f"/api/stock-movements/{product_id}",
        json={
            "movement_type": "OUT",
            "quantity": 4,
            "note": "Customer order",
        },
    )

    assert response.status_code == 201

    assert response.json() == {
        "message": "Stock movement created successfully."
    }

    product_response = test_client.get(
        f"/api/products/{product_id}"
    )

    assert product_response.status_code == 200
    assert product_response.json()["quantity"] == 6


def test_stock_out_insufficient_stock(client):
    test_client, db = client

    product_id = create_test_product(test_client)

    response = test_client.post(
        f"/api/stock-movements/{product_id}",
        json={
            "movement_type": "OUT",
            "quantity": 20,
            "note": "Large order",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Not enough stock available."
    )


def test_stock_movement_product_not_found(client):
    test_client, db = client

    response = test_client.post(
        "/api/stock-movements/9999",
        json={
            "movement_type": "IN",
            "quantity": 5,
            "note": "Test movement",
        },
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Product not found"


def test_stock_movement_zero_quantity(client):
    test_client, db = client

    product_id = create_test_product(test_client)

    response = test_client.post(
        f"/api/stock-movements/{product_id}",
        json={
            "movement_type": "IN",
            "quantity": 0,
            "note": "Invalid movement",
        },
    )

    assert response.status_code == 422


def test_stock_movement_negative_quantity(client):
    test_client, db = client

    product_id = create_test_product(test_client)

    response = test_client.post(
        f"/api/stock-movements/{product_id}",
        json={
            "movement_type": "IN",
            "quantity": -5,
            "note": "Invalid movement",
        },
    )

    assert response.status_code == 422


def test_stock_movement_invalid_type(client):
    test_client, db = client

    product_id = create_test_product(test_client)

    response = test_client.post(
        f"/api/stock-movements/{product_id}",
        json={
            "movement_type": "INVALID",
            "quantity": 5,
            "note": "Invalid movement",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "invalid_movement_type"
    )