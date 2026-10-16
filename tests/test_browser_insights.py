import json

from models import AIAnalysis, Product


def add_test_product(db):
    """
    Add one low-stock product for AI insight tests.
    """

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=850000,
        quantity=2,
        low_stock_level=3,
        category="Electronics",
        supplier="Test Supplier",
    )

    db.add(product)
    db.commit()

    return product


def test_successful_ai_analysis_is_saved(
    authenticated_client,
    monkeypatch,
):
    """
    A successful AI analysis should be stored
    in the analysis history table.
    """

    test_client, db = authenticated_client

    add_test_product(db)

    generated_analysis = (
        "Inventory Health\n"
        "Laptop is currently low in stock."
    )

    monkeypatch.setattr(
        "routers.browser_insights.generate_ai_inventory_analysis",
        lambda insights, *, client, model: generated_analysis,
    )

    monkeypatch.setattr(
        "routers.browser_insights.OpenAI",
        lambda api_key: object(),
    )

    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "pytest-openai-key",
    )

    monkeypatch.setenv(
        "OPENAI_MODEL",
        "pytest-model",
    )

    response = test_client.post(
        "/ai-insights",
        data={
            "csrf_token": test_client.csrf_token,
        },
    )

    assert response.status_code == 200

    saved_analysis = db.query(AIAnalysis).one()

    assert saved_analysis.analysis == generated_analysis
    assert saved_analysis.created_at is not None

    snapshot = json.loads(
        saved_analysis.inventory_snapshot
    )

    assert snapshot["total_products"] == 1
    assert snapshot["total_items"] == 2
    assert snapshot["low_stock_count"] == 1


def test_failed_ai_analysis_is_not_saved(
    authenticated_client,
    monkeypatch,
):
    """
    A failed AI request must not create
    an analysis history record.
    """

    test_client, db = authenticated_client

    add_test_product(db)

    def raise_ai_error(
        insights,
        *,
        client,
        model,
    ):
        raise RuntimeError(
            "Simulated AI failure"
        )

    monkeypatch.setattr(
        "routers.browser_insights.generate_ai_inventory_analysis",
        raise_ai_error,
    )

    monkeypatch.setattr(
        "routers.browser_insights.OpenAI",
        lambda api_key: object(),
    )

    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "pytest-openai-key",
    )

    monkeypatch.setenv(
        "OPENAI_MODEL",
        "pytest-model",
    )

    response = test_client.post(
        "/ai-insights",
        data={
            "csrf_token": test_client.csrf_token,
        },
    )

    assert response.status_code == 503

    assert db.query(AIAnalysis).count() == 0

def test_database_failure_rolls_back_ai_analysis(
    authenticated_client,
    monkeypatch,
):
    """
    A database failure while saving AI history
    should roll back the transaction.
    """

    test_client, db = authenticated_client

    add_test_product(db)

    monkeypatch.setattr(
        "routers.browser_insights.generate_ai_inventory_analysis",
        lambda insights, *, client, model: (
            "Inventory analysis generated."
        ),
    )

    monkeypatch.setattr(
        "routers.browser_insights.OpenAI",
        lambda api_key: object(),
    )

    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "pytest-openai-key",
    )

    monkeypatch.setenv(
        "OPENAI_MODEL",
        "pytest-model",
    )

    rollback_called = False

    original_rollback = db.rollback

    def track_rollback():
        nonlocal rollback_called

        rollback_called = True
        original_rollback()

    monkeypatch.setattr(
        db,
        "rollback",
        track_rollback,
    )

    def fail_commit():
        raise RuntimeError(
            "Simulated database failure"
        )

    monkeypatch.setattr(
        db,
        "commit",
        fail_commit,
    )

    response = test_client.post(
        "/ai-insights",
        data={
            "csrf_token": test_client.csrf_token,
        },
    )

    assert response.status_code == 500

    assert response.json()["detail"] == (
        "AI analysis was generated but could not be saved."
    )

    assert rollback_called is True