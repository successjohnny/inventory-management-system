from models import Product


def test_get_inventory_insights(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=200000,
            quantity=2,
            low_stock_level=3,
            category="Electronics",
            supplier="Supplier A",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=10000,
            quantity=10,
            low_stock_level=4,
            category="Electronics",
            supplier="Supplier B",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get("/api/insights")

    assert response.status_code == 200

    assert response.json() == {
        "total_products": 2,
        "total_items": 12,
        "total_inventory_value": 500000,
        "low_stock_count": 1,
        "low_stock_products": [
            {
                "name": "Laptop",
                "quantity": 2,
                "low_stock_level": 3,
            },
        ],
        "recommendations": [
            {
                "type": "low_stock",
                "product": "Laptop",
                "message": (
                    "Laptop is at or below its low-stock level. "
                    "Review this product for restocking."
                ),
            },
        ],
    }


def test_missing_token_blocks_inventory_insights(
    client,
    monkeypatch,
):
    test_client, _ = client

    monkeypatch.setenv(
        "API_TOKEN",
        "test-api-token-for-inventory-tests-123456789",
    )

    response = test_client.get("/api/insights")

    assert response.status_code == 401


def test_invalid_token_blocks_inventory_insights(
    client,
    monkeypatch,
):
    test_client, _ = client

    monkeypatch.setenv(
        "API_TOKEN",
        "test-api-token-for-inventory-tests-123456789",
    )

    response = test_client.get(
        "/api/insights",
        headers={
            "Authorization": "Bearer incorrect-token",
        },
    )

    assert response.status_code == 401


def test_get_inventory_insights_empty_inventory(
    api_client,
):
    test_client, _ = api_client

    response = test_client.get("/api/insights")

    assert response.status_code == 200

    assert response.json() == {
        "total_products": 0,
        "total_items": 0,
        "total_inventory_value": 0,
        "low_stock_count": 0,
        "low_stock_products": [],
        "recommendations": [],
    }
