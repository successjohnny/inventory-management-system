import pytest
from fastapi import HTTPException
from models import Product
from routers.api_insights import get_ai_client


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


def test_get_ai_inventory_insights(
    api_client,
    monkeypatch,
):
    test_client, db = api_client

    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-inventory-model",
    )

    class FakeResponse:
        output_text = (
            "Laptop should be reviewed for restocking."
        )

    class FakeResponses:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()

    def override_ai_client():
        return FakeClient()

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=2,
        low_stock_level=3,
        category="Electronics",
        supplier="Supplier A",
    )

    db.add(product)
    db.commit()

    test_client.app.dependency_overrides[
        get_ai_client
    ] = override_ai_client

    try:
        response = test_client.get(
            "/api/insights/ai"
        )
    finally:
        test_client.app.dependency_overrides.pop(
            get_ai_client,
            None,
        )

    assert response.status_code == 200

    data = response.json()

    assert data["insights"]["total_products"] == 1
    assert data["insights"]["total_items"] == 2

    assert data["insights"][
        "total_inventory_value"
    ] == 400000

    assert data["insights"]["low_stock_count"] == 1

    assert data["ai_analysis"] == (
        "Laptop should be reviewed for restocking."
    )


def test_get_ai_client_requires_api_key(
    monkeypatch,
):
    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_ai_client()

    assert exc_info.value.status_code == 503

    assert exc_info.value.detail == (
        "AI inventory analysis is temporarily "
        "unavailable."
    )


def test_get_ai_client_uses_configured_api_key(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-only-openai-api-key",
    )

    captured = {}

    class FakeOpenAI:
        def __init__(self, *, api_key):
            captured["api_key"] = api_key

    monkeypatch.setattr(
        "routers.api_insights.OpenAI",
        FakeOpenAI,
        raising=False,
    )

    client = get_ai_client()

    assert isinstance(client, FakeOpenAI)

    assert captured["api_key"] == (
        "test-only-openai-api-key"
    )


def test_missing_token_blocks_ai_inventory_insights(
    client,
    monkeypatch,
):
    test_client, _ = client

    monkeypatch.setenv(
        "API_TOKEN",
        "test-api-token-for-inventory-tests-123456789",
    )

    class FailingAIClient:
        def __init__(self):
            raise AssertionError(
                "AI client should not be created "
                "for an unauthenticated request."
            )

    test_client.app.dependency_overrides[
        get_ai_client
    ] = FailingAIClient

    try:
        response = test_client.get(
            "/api/insights/ai"
        )
    finally:
        test_client.app.dependency_overrides.pop(
            get_ai_client,
            None,
        )

    assert response.status_code == 401


def test_invalid_token_blocks_ai_inventory_insights(
    client,
    monkeypatch,
):
    test_client, _ = client

    monkeypatch.setenv(
        "API_TOKEN",
        "test-api-token-for-inventory-tests-123456789",
    )

    class FailingAIClient:
        def __init__(self):
            raise AssertionError(
                "AI client should not be created "
                "for an invalid API token."
            )

    test_client.app.dependency_overrides[
        get_ai_client
    ] = FailingAIClient

    try:
        response = test_client.get(
            "/api/insights/ai",
            headers={
                "Authorization": "Bearer incorrect-token",
            },
        )
    finally:
        test_client.app.dependency_overrides.pop(
            get_ai_client,
            None,
        )

    assert response.status_code == 401


def test_ai_inventory_insights_handles_ai_failure(
    api_client,
    monkeypatch,
):
    test_client, db = api_client

    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-inventory-model",
    )

    class FailingResponses:
        def create(self, **kwargs):
            raise RuntimeError(
                "Simulated AI provider failure."
            )

    class FailingClient:
        def __init__(self):
            self.responses = FailingResponses()

    def override_ai_client():
        return FailingClient()

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=2,
        low_stock_level=3,
        category="Electronics",
        supplier="Supplier A",
    )

    db.add(product)
    db.commit()

    test_client.app.dependency_overrides[
        get_ai_client
    ] = override_ai_client

    try:
        response = test_client.get(
            "/api/insights/ai"
        )
    finally:
        test_client.app.dependency_overrides.pop(
            get_ai_client,
            None,
        )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "AI inventory analysis is temporarily "
            "unavailable."
        )
    }


def test_ai_inventory_insights_handles_missing_model(
    api_client,
    monkeypatch,
):
    test_client, db = api_client

    monkeypatch.delenv(
        "OPENAI_MODEL",
        raising=False,
    )

    class FakeResponses:
        def create(self, **kwargs):
            raise AssertionError(
                "AI request should not be made "
                "without a configured model."
            )

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()

    def override_ai_client():
        return FakeClient()

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=2,
        low_stock_level=3,
        category="Electronics",
        supplier="Supplier A",
    )

    db.add(product)
    db.commit()

    test_client.app.dependency_overrides[
        get_ai_client
    ] = override_ai_client

    try:
        response = test_client.get(
            "/api/insights/ai"
        )
    finally:
        test_client.app.dependency_overrides.pop(
            get_ai_client,
            None,
        )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "AI inventory analysis is temporarily "
            "unavailable."
        )
    }


def test_ai_inventory_insights_handles_missing_api_key(
    client,
    monkeypatch,
):
    test_client, _ = client

    monkeypatch.setenv(
        "API_TOKEN",
        "test-api-token-for-inventory-tests-123456789",
    )

    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )

    response = test_client.get(
        "/api/insights/ai",
        headers={
            "Authorization": (
                "Bearer "
                "test-api-token-for-inventory-tests-123456789"
            ),
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "AI inventory analysis is temporarily "
            "unavailable."
        )
    }
