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