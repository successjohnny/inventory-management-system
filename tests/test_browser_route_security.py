import pytest

from models import Product
from services.product_service import create_product


def make_product(db):
    """
    Create a product directly in the test database.
    """

    product = create_product(
        db,
        "Security Test Product",
        100,
        10,
        2,
        "Testing",
        "",
    )

    assert isinstance(product, Product)

    return product


# ==========================================
# ANONYMOUS ACCESS
# ==========================================

def test_anonymous_user_cannot_access_dashboard(client):
    test_client, db = client

    response = test_client.get(
        "/",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_anonymous_user_cannot_access_edit_page(client):
    test_client, db = client

    product = make_product(db)

    response = test_client.get(
        f"/edit-product/{product.id}",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_anonymous_user_cannot_create_product(client):
    test_client, db = client

    response = test_client.post(
        "/add-product",
        data={
            "name": "Unauthorized Product",
            "price": 100,
            "quantity": 10,
            "low_stock_level": 2,
            "category": "Testing",
            "supplier": "",
            "csrf_token": "unauthorized-token",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    assert db.query(Product).count() == 0


def test_anonymous_user_cannot_edit_product(client):
    test_client, db = client

    product = make_product(db)

    response = test_client.post(
        f"/edit-product/{product.id}",
        data={
            "name": "Unauthorized Change",
            "price": 999,
            "low_stock_level": 2,
            "category": "Testing",
            "supplier": "",
            "csrf_token": "unauthorized-token",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    db.refresh(product)

    assert product.name == "Security Test Product"
    assert product.price == 100


def test_anonymous_user_cannot_delete_product(client):
    test_client, db = client

    product = make_product(db)
    product_id = product.id

    response = test_client.post(
        f"/delete-product/{product_id}",
        data={
            "csrf_token": "unauthorized-token",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    assert db.get(Product, product_id) is not None


def test_anonymous_user_cannot_change_stock(client):
    test_client, db = client

    product = make_product(db)

    response = test_client.post(
        f"/stock-movement/{product.id}",
        data={
            "movement_type": "OUT",
            "quantity": 5,
            "note": "Unauthorized stock movement",
            "csrf_token": "unauthorized-token",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    db.refresh(product)

    assert product.quantity == 10


# ==========================================
# AUTHENTICATED ACCESS
# ==========================================

def test_authenticated_user_can_access_dashboard(
    authenticated_client,
):
    test_client, db = authenticated_client

    response = test_client.get("/")

    assert response.status_code == 200


# ==========================================
# CSRF PROTECTION
# ==========================================

@pytest.mark.parametrize(
    "submitted_token",
    [
        "invalid-token",
        "",
    ],
)
def test_invalid_csrf_blocks_product_creation(
    authenticated_client,
    submitted_token,
):
    wrapped_client, db = authenticated_client

    response = wrapped_client.test_client.post(
        "/add-product",
        data={
            "name": "Blocked Product",
            "price": 100,
            "quantity": 10,
            "low_stock_level": 2,
            "category": "Testing",
            "supplier": "",
            "csrf_token": submitted_token,
        },
        follow_redirects=False,
    )

    assert response.status_code == 403

    assert (
        db.query(Product)
        .filter(Product.name == "Blocked Product")
        .first()
        is None
    )


def test_invalid_csrf_blocks_stock_movement(
    authenticated_client,
):
    wrapped_client, db = authenticated_client

    product = make_product(db)

    response = wrapped_client.test_client.post(
        f"/stock-movement/{product.id}",
        data={
            "movement_type": "OUT",
            "quantity": 5,
            "note": "Invalid CSRF test",
            "csrf_token": "invalid-token",
        },
        follow_redirects=False,
    )

    assert response.status_code == 403

    db.refresh(product)

    assert product.quantity == 10


# ==========================================
# LOGOUT
# ==========================================

def test_logout_prevents_dashboard_access(
    authenticated_client,
):
    wrapped_client, db = authenticated_client

    response = wrapped_client.test_client.post(
        "/logout",
        data={
            "csrf_token": wrapped_client.csrf_token,
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    dashboard = wrapped_client.test_client.get(
        "/",
        follow_redirects=False,
    )

    assert dashboard.status_code == 303
    assert dashboard.headers["location"] == "/login"


def test_invalid_csrf_blocks_logout(
    authenticated_client,
):
    wrapped_client, db = authenticated_client

    response = wrapped_client.test_client.post(
        "/logout",
        data={
            "csrf_token": "invalid-token",
        },
        follow_redirects=False,
    )

    assert response.status_code == 403

    dashboard = wrapped_client.test_client.get("/")

    assert dashboard.status_code == 200