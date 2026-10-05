import pytest

from services.inventory_ai import (
    build_inventory_ai_prompt,
    generate_ai_inventory_analysis,
    get_ai_model,
)


def test_build_inventory_ai_prompt_includes_inventory_facts():
    insights = {
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

    prompt = build_inventory_ai_prompt(insights)

    assert "2" in prompt
    assert "12" in prompt
    assert "500000" in prompt
    assert "Laptop" in prompt
    assert "low-stock" in prompt


def test_build_inventory_ai_prompt_requires_grounded_analysis():
    insights = {
        "total_products": 0,
        "total_items": 0,
        "total_inventory_value": 0,
        "low_stock_count": 0,
        "low_stock_products": [],
        "recommendations": [],
    }

    prompt = build_inventory_ai_prompt(insights)

    assert "Use only the facts provided" in prompt
    assert "Do not invent products" in prompt
    assert "quantities" in prompt
    assert "inventory values" in prompt


def test_generate_ai_inventory_analysis_uses_client():
    class FakeResponse:
        output_text = (
            "Laptop should be reviewed for restocking."
        )

    class FakeResponses:
        def __init__(self):
            self.request = None

        def create(self, **kwargs):
            self.request = kwargs
            return FakeResponse()

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()

    insights = {
        "total_products": 1,
        "total_items": 2,
        "total_inventory_value": 400000,
        "low_stock_count": 1,
        "low_stock_products": [
            {
                "name": "Laptop",
                "quantity": 2,
                "low_stock_level": 3,
            },
        ],
        "recommendations": [],
    }

    client = FakeClient()

    analysis = generate_ai_inventory_analysis(
        insights,
        client=client,
        model="test-model",
    )

    assert analysis == (
        "Laptop should be reviewed for restocking."
    )

    assert client.responses.request["model"] == "test-model"

    assert (
        "Laptop"
        in client.responses.request["input"]
    )


def test_generate_ai_inventory_analysis_skips_empty_inventory():
    class FakeResponses:
        def create(self, **kwargs):
            raise AssertionError(
                "AI client should not be called for empty inventory."
            )

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()

    insights = {
        "total_products": 0,
        "total_items": 0,
        "total_inventory_value": 0,
        "low_stock_count": 0,
        "low_stock_products": [],
        "recommendations": [],
    }

    analysis = generate_ai_inventory_analysis(
        insights,
        client=FakeClient(),
        model="test-model",
    )

    assert analysis == (
        "No inventory data is available for AI analysis."
    )


def test_generate_ai_inventory_analysis_handles_empty_response():
    class FakeResponse:
        output_text = ""

    class FakeResponses:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()

    insights = {
        "total_products": 1,
        "total_items": 5,
        "total_inventory_value": 100000,
        "low_stock_count": 0,
        "low_stock_products": [],
        "recommendations": [],
    }

    analysis = generate_ai_inventory_analysis(
        insights,
        client=FakeClient(),
        model="test-model",
    )

    assert analysis == (
        "AI analysis did not return any content."
    )


def test_get_ai_model_uses_environment_variable(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-inventory-model",
    )

    assert get_ai_model() == "test-inventory-model"


def test_get_ai_model_requires_configuration(
    monkeypatch,
):
    monkeypatch.delenv(
        "OPENAI_MODEL",
        raising=False,
    )

    with pytest.raises(KeyError):
        get_ai_model()