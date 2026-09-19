import pytest

from models import Product, StockMovement


TEST_API_TOKEN = "test-only-api-token-for-inventory-security-2026"


PRODUCT_DATA = {
    "name": "Protected Laptop",
    "price": 200000,
    "quantity": 10,
    "low_stock_level": 3,
    "category": "Electronics",
    "supplier": "Test Supplier",
}


@pytest.fixture
def configured_client(client, monkeypatch):
    """
    Configure an API token without automatically
    authenticating the test client.
    """

    test_client, db = client

    monkeypatch.setenv(
        "API_TOKEN",
        TEST_API_TOKEN,
    )

    return test_client, db


def test_missing_token_blocks_product_listing(configured_client):
    test_client, db = configured_client

    response = test_client.get("/api/products/")

    assert response.status_code == 401


def test_invalid_token_blocks_product_listing(configured_client):
    test_client, db = configured_client

    response = test_client.get(
        "/api/products/",
        headers={
            "Authorization": "Bearer incorrect-token",
        },
    )

    assert response.status_code == 401


def test_missing_token_blocks_product_creation(configured_client):
    test_client, db = configured_client

    response = test_client.post(
        "/api/products/",
        json=PRODUCT_DATA,
    )

    assert response.status_code == 401
    assert db.query(Product).count() == 0


def test_invalid_token_blocks_product_creation(configured_client):
    test_client, db = configured_client

    response = test_client.post(
        "/api/products/",
        json=PRODUCT_DATA,
        headers={
            "Authorization": "Bearer incorrect-token",
        },
    )

    assert response.status_code == 401
    assert db.query(Product).count() == 0


def test_missing_token_blocks_stock_listing(configured_client):
    test_client, db = configured_client

    response = test_client.get("/api/stock-movements/")

    assert response.status_code == 401


def test_missing_token_blocks_stock_creation(configured_client):
    test_client, db = configured_client

    response = test_client.post(
        "/api/stock-movements/9999",
        json={
            "movement_type": "IN",
            "quantity": 5,
            "note": "Unauthorized movement",
        },
    )

    assert response.status_code == 401
    assert db.query(StockMovement).count() == 0


def test_valid_token_allows_product_creation(api_client):
    test_client, db = api_client

    response = test_client.post(
        "/api/products/",
        json=PRODUCT_DATA,
    )

    assert response.status_code == 201
    assert db.query(Product).count() == 1


def test_valid_token_allows_product_listing(api_client):
    test_client, db = api_client

    response = test_client.get("/api/products/")

    assert response.status_code == 200
    assert response.json() == []

def test_invalid_token_cannot_modify_existing_stock(
    configured_client,
):
    """
    An invalid API token must not modify inventory
    or create a stock movement.
    """

    test_client, db = configured_client

    product = Product(
        name="Protected Stock Product",
        normalized_name="protected stock product",
        price=100,
        quantity=10,
        low_stock_level=2,
        category="Testing",
        supplier="Test Supplier",
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    response = test_client.post(
        f"/api/stock-movements/{product.id}",
        json={
            "movement_type": "OUT",
            "quantity": 5,
            "note": "Unauthorized stock removal",
        },
        headers={
            "Authorization": "Bearer incorrect-token",
        },
    )

    assert response.status_code == 401

    db.refresh(product)

    assert product.quantity == 10
    assert db.query(StockMovement).count() == 0