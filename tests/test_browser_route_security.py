import pytest

from models import Product, StockMovement
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


def assert_login_redirect(response):
    """
    Verify that a request redirects to the login page.
    """

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


# ==========================================
# ANONYMOUS ACCESS
# ==========================================

def test_anonymous_user_cannot_access_dashboard(client):
    test_client, db = client

    response = test_client.get(
        "/",
        follow_redirects=False,
    )

    assert_login_redirect(response)


def test_anonymous_user_cannot_access_edit_page(client):
    test_client, db = client

    product = make_product(db)

    response = test_client.get(
        f"/edit-product/{product.id}",
        follow_redirects=False,
    )

    assert_login_redirect(response)


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

    assert_login_redirect(response)

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

    assert_login_redirect(response)

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

    assert_login_redirect(response)

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

    assert_login_redirect(response)

    db.refresh(product)

    assert product.quantity == 10
    assert db.query(StockMovement).count() == 0


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
# PRODUCT CREATION CSRF TESTS
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

    assert db.query(Product).count() == 0


def test_missing_csrf_blocks_product_creation(
    authenticated_client,
):
    """
    Omit the CSRF field entirely.
    """

    wrapped_client, db = authenticated_client

    response = wrapped_client.test_client.post(
        "/add-product",
        data={
            "name": "Missing Token Product",
            "price": 100,
            "quantity": 10,
            "low_stock_level": 2,
            "category": "Testing",
            "supplier": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 403

    assert db.query(Product).count() == 0


# ==========================================
# PRODUCT EDITING CSRF TEST
# ==========================================

def test_invalid_csrf_blocks_product_edit(
    authenticated_client,
):
    wrapped_client, db = authenticated_client

    product = make_product(db)

    response = wrapped_client.test_client.post(
        f"/edit-product/{product.id}",
        data={
            "name": "Hacked Product",
            "price": 999,
            "low_stock_level": 1,
            "category": "Changed Category",
            "supplier": "",
            "csrf_token": "invalid-token",
        },
        follow_redirects=False,
    )

    assert response.status_code == 403

    db.refresh(product)

    assert product.name == "Security Test Product"
    assert product.price == 100
    assert product.low_stock_level == 2
    assert product.category == "Testing"


# ==========================================
# PRODUCT DELETION CSRF TEST
# ==========================================

def test_invalid_csrf_blocks_product_deletion(
    authenticated_client,
):
    wrapped_client, db = authenticated_client

    product = make_product(db)
    product_id = product.id

    response = wrapped_client.test_client.post(
        f"/delete-product/{product_id}",
        data={
            "csrf_token": "invalid-token",
        },
        follow_redirects=False,
    )

    assert response.status_code == 403

    assert db.get(Product, product_id) is not None


# ==========================================
# STOCK MOVEMENT CSRF TESTS
# ==========================================

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

    assert db.query(StockMovement).count() == 0


def test_missing_csrf_blocks_stock_movement(
    authenticated_client,
):
    """
    A stock movement without a CSRF token must fail.

    Both the product quantity and movement history
    must remain unchanged.
    """

    wrapped_client, db = authenticated_client

    product = make_product(db)

    response = wrapped_client.test_client.post(
        f"/stock-movement/{product.id}",
        data={
            "movement_type": "OUT",
            "quantity": 5,
            "note": "Missing CSRF test",
        },
        follow_redirects=False,
    )

    assert response.status_code == 403

    db.refresh(product)

    assert product.quantity == 10

    assert db.query(StockMovement).count() == 0


# ==========================================
# LOGOUT TESTS
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

    assert_login_redirect(dashboard)


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
