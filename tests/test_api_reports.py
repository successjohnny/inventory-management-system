import csv
import io
from datetime import datetime, timezone

from models import Product, StockMovement


def test_export_inventory_csv(api_client):
    test_client, db = api_client

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=10,
        low_stock_level=3,
        category="Electronics",
        supplier="Test Supplier",
    )

    db.add(product)
    db.commit()

    response = test_client.get(
        "/api/reports/inventory.csv"
    )

    assert response.status_code == 200

    assert response.headers["content-type"].startswith(
        "text/csv"
    )

    assert (
        "attachment"
        in response.headers["content-disposition"]
    )

    reader = csv.DictReader(
        io.StringIO(response.text)
    )

    rows = list(reader)

    assert len(rows) == 1

    row = rows[0]

    assert row["name"] == "Laptop"
    assert row["price"] == "200000"
    assert row["quantity"] == "10"
    assert row["low_stock_level"] == "3"
    assert row["category"] == "Electronics"
    assert row["supplier"] == "Test Supplier"


def test_export_inventory_csv_empty(api_client):
    test_client, _ = api_client

    response = test_client.get(
        "/api/reports/inventory.csv"
    )

    assert response.status_code == 200

    reader = csv.DictReader(
        io.StringIO(response.text)
    )

    rows = list(reader)

    assert rows == []

    assert reader.fieldnames == [
        "id",
        "name",
        "price",
        "quantity",
        "low_stock_level",
        "category",
        "supplier",
    ]


def test_export_stock_movements_csv(api_client):
    test_client, db = api_client

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=10,
        low_stock_level=3,
        category="Electronics",
        supplier="Test Supplier",
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    movement = StockMovement(
        product_id=product.id,
        movement_type="IN",
        quantity=5,
        note="New shipment",
    )

    db.add(movement)
    db.commit()

    response = test_client.get(
        "/api/reports/stock-movements.csv"
    )

    assert response.status_code == 200

    assert response.headers["content-type"].startswith(
        "text/csv"
    )

    assert (
        "attachment"
        in response.headers["content-disposition"]
    )

    reader = csv.DictReader(
        io.StringIO(response.text)
    )

    rows = list(reader)

    assert len(rows) == 1

    row = rows[0]

    assert row["product_id"] == str(product.id)
    assert row["movement_type"] == "IN"
    assert row["quantity"] == "5"
    assert row["note"] == "New shipment"
    assert row["created_at"]


def test_export_stock_movements_csv_empty(api_client):
    test_client, _ = api_client

    response = test_client.get(
        "/api/reports/stock-movements.csv"
    )

    assert response.status_code == 200

    reader = csv.DictReader(
        io.StringIO(response.text)
    )

    rows = list(reader)

    assert rows == []

    assert reader.fieldnames == [
        "id",
        "product_id",
        "movement_type",
        "quantity",
        "note",
        "created_at",
    ]


def test_export_stock_movements_csv_filters_by_start_date(
    api_client,
):
    test_client, db = api_client

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=10,
        low_stock_level=3,
        category="Electronics",
        supplier="Test Supplier",
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    old_movement = StockMovement(
        product_id=product.id,
        movement_type="IN",
        quantity=5,
        note="Old shipment",
        created_at=datetime(
            2026,
            9,
            1,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    recent_movement = StockMovement(
        product_id=product.id,
        movement_type="IN",
        quantity=10,
        note="Recent shipment",
        created_at=datetime(
            2026,
            9,
            20,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    db.add_all(
        [
            old_movement,
            recent_movement,
        ]
    )
    db.commit()

    response = test_client.get(
        "/api/reports/stock-movements.csv"
        "?start_date=2026-09-10"
    )

    assert response.status_code == 200

    reader = csv.DictReader(
        io.StringIO(response.text)
    )

    rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["note"] == "Recent shipment"


def test_export_stock_movements_csv_filters_by_end_date(
    api_client,
):
    test_client, db = api_client

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=10,
        low_stock_level=3,
        category="Electronics",
        supplier="Test Supplier",
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    included_movement = StockMovement(
        product_id=product.id,
        movement_type="IN",
        quantity=5,
        note="Included shipment",
        created_at=datetime(
            2026,
            9,
            10,
            23,
            59,
            tzinfo=timezone.utc,
        ),
    )

    later_movement = StockMovement(
        product_id=product.id,
        movement_type="IN",
        quantity=10,
        note="Later shipment",
        created_at=datetime(
            2026,
            9,
            11,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    db.add_all(
        [
            included_movement,
            later_movement,
        ]
    )
    db.commit()

    response = test_client.get(
        "/api/reports/stock-movements.csv"
        "?end_date=2026-09-10"
    )

    assert response.status_code == 200

    reader = csv.DictReader(
        io.StringIO(response.text)
    )

    rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["note"] == "Included shipment"


def test_export_stock_movements_csv_rejects_invalid_date_range(
    api_client,
):
    test_client, _ = api_client

    response = test_client.get(
        "/api/reports/stock-movements.csv"
        "?start_date=2026-09-20"
        "&end_date=2026-09-10"
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "start_date cannot be later than end_date."
    )

def test_export_stock_movements_csv_rejects_invalid_date_format(
    api_client,
):
    test_client, _ = api_client

    response = test_client.get(
        "/api/reports/stock-movements.csv"
        "?start_date=not-a-date"
    )

    assert response.status_code == 422


def test_get_inventory_summary(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=200000,
            quantity=10,
            low_stock_level=3,
            category="Electronics",
            supplier="Supplier A",
        ),
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=5000,
            quantity=2,
            low_stock_level=5,
            category="Electronics",
            supplier="Supplier B",
        ),
        Product(
            name="Office Chair",
            normalized_name="office chair",
            price=80000,
            quantity=8,
            low_stock_level=8,
            category="Furniture",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/reports/summary"
    )

    assert response.status_code == 200

    assert response.json() == {
        "total_products": 3,
        "total_items": 20,
        "total_categories": 2,
        "low_stock_products": 2,
    }


def test_get_inventory_summary_empty(api_client):
    test_client, _ = api_client

    response = test_client.get(
        "/api/reports/summary"
    )

    assert response.status_code == 200

    assert response.json() == {
        "total_products": 0,
        "total_items": 0,
        "total_categories": 0,
        "low_stock_products": 0,
    }
