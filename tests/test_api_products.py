from models import Product


def test_get_products(client):
    test_client, db = client

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=110,
        low_stock_level=5,
        category="Electronics",
        supplier="Merabgold Associates Services",
    )

    db.add(product)
    db.commit()

    response = test_client.get("/api/products/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["name"] == "Laptop"
    assert data[0]["price"] == 200000
    assert data[0]["quantity"] == 110

    assert "normalized_name" not in data[0]

def test_get_product_by_id(client):
    test_client, db = client

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=110,
        low_stock_level=5,
        category="Electronics",
        supplier="Merabgold Associates Services",
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    response = test_client.get(
        f"/api/products/{product.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product.id
    assert data["name"] == "Laptop"
    assert data["quantity"] == 110

    assert "normalized_name" not in data

def test_get_product_not_found(client):
    test_client, db = client

    response = test_client.get(
        "/api/products/999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found"

def test_create_product_api(client):
    test_client, db = client

    response = test_client.post(
        "/api/products/",
        json={
            "name": "Keyboard",
            "price": 2500,
            "quantity": 30,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "ABC Supplies",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Keyboard"
    assert data["price"] == 2500
    assert data["quantity"] == 30
    assert data["category"] == "Electronics"
    assert data["supplier"] == "ABC Supplies"

    assert "normalized_name" not in data

def test_create_duplicate_product_api(client):
    test_client, db = client

    first_response = test_client.post(
        "/api/products/",
        json={
            "name": "Keyboard",
            "price": 2500,
            "quantity": 30,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "ABC Supplies",
        },
    )

    assert first_response.status_code == 201

    second_response = test_client.post(
        "/api/products/",
        json={
            "name": "keyboard",
            "price": 3000,
            "quantity": 20,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "Another Supplier",
        },
    )

    assert second_response.status_code == 400

    data = second_response.json()

    assert data["detail"] == "duplicate_product"

def test_create_product_negative_price(client):
    test_client, db = client

    response = test_client.post(
        "/api/products/",
        json={
            "name": "Invalid Product",
            "price": -5000,
            "quantity": 10,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 422

def test_create_product_negative_quantity(client):
    test_client, db = client

    response = test_client.post(
        "/api/products/",
        json={
            "name": "Invalid Product",
            "price": 5000,
            "quantity": -10,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 422

def test_create_product_negative_low_stock_level(client):
    test_client, db = client

    response = test_client.post(
        "/api/products/",
        json={
            "name": "Invalid Product",
            "price": 5000,
            "quantity": 10,
            "low_stock_level": -5,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 422

def test_get_product_stock_movements(client):
    test_client, db = client

    # Create the first product.
    first_product = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
            "supplier": "Supplier A",
        },
    )

    assert first_product.status_code == 201

    first_product_id = first_product.json()["id"]

    # Create a second product.
    second_product = test_client.post(
        "/api/products/",
        json={
            "name": "Mouse",
            "price": 5000,
            "quantity": 20,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "Supplier B",
        },
    )

    assert second_product.status_code == 201

    second_product_id = second_product.json()["id"]

    # Record a movement for the first product.
    first_movement = test_client.post(
        f"/api/stock-movements/{first_product_id}",
        json={
            "movement_type": "IN",
            "quantity": 5,
            "note": "Laptop shipment",
        },
    )

    assert first_movement.status_code == 201

    # Record a movement for the second product.
    second_movement = test_client.post(
        f"/api/stock-movements/{second_product_id}",
        json={
            "movement_type": "OUT",
            "quantity": 3,
            "note": "Mouse sale",
        },
    )

    assert second_movement.status_code == 201

    # Retrieve only the first product's history.
    response = test_client.get(
        f"/api/products/{first_product_id}/stock-movements"
    )

    assert response.status_code == 200

    movements = response.json()

    assert len(movements) == 1

    assert movements[0]["product_id"] == first_product_id
    assert movements[0]["movement_type"] == "IN"
    assert movements[0]["quantity"] == 5
    assert movements[0]["note"] == "Laptop shipment"


def test_get_product_stock_movements_empty(client):
    test_client, db = client

    response = test_client.post(
        "/api/products/",
        json={
            "name": "Keyboard",
            "price": 10000,
            "quantity": 15,
            "low_stock_level": 4,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 201

    product_id = response.json()["id"]

    history_response = test_client.get(
        f"/api/products/{product_id}/stock-movements"
    )

    assert history_response.status_code == 200
    assert history_response.json() == []


def test_get_product_stock_movements_not_found(client):
    test_client, db = client

    response = test_client.get(
        "/api/products/9999/stock-movements"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Product not found"

def test_update_product_api(client):
    test_client, db = client

    create_response = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
            "supplier": "Supplier A",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    response = test_client.put(
        f"/api/products/{product_id}",
        json={
            "name": "Gaming Laptop",
            "price": 350000,
            "low_stock_level": 5,
            "category": "Computers",
            "supplier": "Supplier B",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Gaming Laptop"
    assert data["price"] == 350000
    assert data["low_stock_level"] == 5
    assert data["category"] == "Computers"
    assert data["supplier"] == "Supplier B"

    # Product quantity must remain unchanged.
    assert data["quantity"] == 10


def test_update_product_not_found(client):
    test_client, db = client

    response = test_client.put(
        "/api/products/9999",
        json={
            "name": "Missing Product",
            "price": 5000,
            "low_stock_level": 2,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product_invalid_price(client):
    test_client, db = client

    response = test_client.put(
        "/api/products/9999",
        json={
            "name": "Invalid Product",
            "price": -5000,
            "low_stock_level": 2,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 422


def test_update_product_duplicate_name(client):
    test_client, db = client

    first = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
        },
    )

    second = test_client.post(
        "/api/products/",
        json={
            "name": "Mouse",
            "price": 5000,
            "quantity": 20,
            "low_stock_level": 5,
            "category": "Electronics",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    second_id = second.json()["id"]

    response = test_client.put(
        f"/api/products/{second_id}",
        json={
            "name": "Laptop",
            "price": 6000,
            "low_stock_level": 5,
            "category": "Electronics",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "duplicate_product"

def test_delete_product_api(client):
    test_client, db = client

    create_response = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    delete_response = test_client.delete(
        f"/api/products/{product_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = test_client.get(
        f"/api/products/{product_id}"
    )

    assert get_response.status_code == 404


def test_delete_product_not_found(client):
    test_client, db = client

    response = test_client.delete(
        "/api/products/9999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_delete_product_removes_stock_movements(client):
    test_client, db = client

    create_response = test_client.post(
        "/api/products/",
        json={
            "name": "Keyboard",
            "price": 10000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    movement_response = test_client.post(
        f"/api/stock-movements/{product_id}",
        json={
            "movement_type": "IN",
            "quantity": 5,
            "note": "New shipment",
        },
    )

    assert movement_response.status_code == 201

    delete_response = test_client.delete(
        f"/api/products/{product_id}"
    )

    assert delete_response.status_code == 204

    history_response = test_client.get(
        "/api/stock-movements/"
    )

    assert history_response.status_code == 200
    assert history_response.json() == []