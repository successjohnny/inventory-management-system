import csv
import io

from models import Product


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