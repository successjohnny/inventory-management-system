"""Tests for the administrator Reports Dashboard and its CSV downloads."""

import csv
import io
from typing import Any

from httpx import Response
from sqlalchemy.orm import Session

from models import Product, StockMovement
from services.product_service import create_product


INVENTORY_HEADERS: list[str] = [
    "id",
    "name",
    "price",
    "quantity",
    "low_stock_level",
    "category",
    "supplier",
]

MOVEMENT_HEADERS: list[str] = [
    "id",
    "product_id",
    "movement_type",
    "quantity",
    "note",
    "created_at",
]


def assert_login_redirect(response: Response) -> None:
    """Confirm anonymous requests redirect to the login page."""
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def read_csv(response: Response) -> list[list[str]]:
    """Parse a CSV HTTP response into rows of strings."""
    csv_content: str = response.text
    rows: list[list[str]] = list(csv.reader(io.StringIO(csv_content)))
    return rows


def make_product(db: Session, name: str = "Reports Test Laptop") -> Product:
    """Create a product using the existing service layer."""
    product: Product = create_product(
        db,
        name,
        500,
        4,
        2,
        "Electronics",
        "Reports Test Supplier",
    )
    assert isinstance(product, Product)
    return product


# Pytest injects the client fixtures; Any also supports the authenticated wrapper.
def test_anonymous_user_cannot_view_reports(client: Any) -> None:
    test_client, _ = client
    response: Response = test_client.get("/reports", follow_redirects=False)
    assert_login_redirect(response)


def test_anonymous_user_cannot_download_inventory_csv(client: Any) -> None:
    test_client, _ = client
    response: Response = test_client.get(
        "/reports/download/inventory",
        follow_redirects=False,
    )
    assert_login_redirect(response)


def test_anonymous_user_cannot_download_stock_movements_csv(client: Any) -> None:
    test_client, _ = client
    response: Response = test_client.get(
        "/reports/download/stock-movements",
        follow_redirects=False,
    )
    assert_login_redirect(response)


def test_admin_can_view_reports(authenticated_client: Any) -> None:
    test_client, _ = authenticated_client
    response: Response = test_client.get("/reports")
    assert response.status_code == 200
    assert "Category Breakdown" in response.text
    assert "Supplier Breakdown" in response.text


def test_reports_dashboard_handles_empty_inventory(authenticated_client: Any) -> None:
    test_client, db = authenticated_client
    assert db.query(Product).count() == 0
    response: Response = test_client.get("/reports")
    assert response.status_code == 200
    assert "Download Inventory CSV" in response.text
    assert "Download Stock Movements CSV" in response.text


def test_reports_dashboard_displays_product_data(authenticated_client: Any) -> None:
    test_client, db = authenticated_client
    make_product(db)
    response: Response = test_client.get("/reports")
    assert response.status_code == 200
    assert "Electronics" in response.text
    assert "Reports Test Supplier" in response.text


def test_admin_can_download_inventory_csv(authenticated_client: Any) -> None:
    test_client, _ = authenticated_client
    response: Response = test_client.get("/reports/download/inventory")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert 'filename="inventory.csv"' in response.headers["content-disposition"]
    rows: list[list[str]] = read_csv(response)
    assert rows == [INVENTORY_HEADERS]


def test_inventory_csv_contains_product(authenticated_client: Any) -> None:
    test_client, db = authenticated_client
    product: Product = make_product(db, "CSV Test Laptop")
    response: Response = test_client.get("/reports/download/inventory")
    assert response.status_code == 200
    rows: list[list[str]] = read_csv(response)
    assert rows[0] == INVENTORY_HEADERS
    assert len(rows) == 2
    row: dict[str, str] = dict(zip(rows[0], rows[1]))
    assert row == {
        "id": str(product.id),
        "name": "CSV Test Laptop",
        "price": "500",
        "quantity": "4",
        "low_stock_level": "2",
        "category": "Electronics",
        "supplier": "Reports Test Supplier",
    }


def test_admin_can_download_stock_movements_csv(authenticated_client: Any) -> None:
    test_client, _ = authenticated_client
    response: Response = test_client.get("/reports/download/stock-movements")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert 'filename="stock-movements.csv"' in response.headers["content-disposition"]
    rows: list[list[str]] = read_csv(response)
    assert rows == [MOVEMENT_HEADERS]


def test_stock_movements_csv_contains_record(authenticated_client: Any) -> None:
    test_client, db = authenticated_client
    product: Product = make_product(db)
    movement: StockMovement = StockMovement(
        product_id=product.id,
        movement_type="IN",
        quantity=5,
        note="New shipment",
    )
    db.add(movement)
    db.commit()
    response: Response = test_client.get("/reports/download/stock-movements")
    assert response.status_code == 200
    rows: list[list[str]] = read_csv(response)
    assert rows[0] == MOVEMENT_HEADERS
    assert len(rows) == 2
    row: dict[str, str] = dict(zip(rows[0], rows[1]))
    assert row["id"] == str(movement.id)
    assert row["product_id"] == str(product.id)
    assert row["movement_type"] == "IN"
    assert row["quantity"] == "5"
    assert row["note"] == "New shipment"
    assert row["created_at"]


def test_main_dashboard_links_to_reports(authenticated_client: Any) -> None:
    test_client, _ = authenticated_client
    response: Response = test_client.get("/")
    assert response.status_code == 200
    assert 'href="/reports"' in response.text
    assert "View Reports" in response.text
