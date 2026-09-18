import re

import pytest

from auth_credentials import hash_password


TEST_USERNAME = "test_admin"
TEST_PASSWORD = "Example-Test-Password-123!"


@pytest.fixture
def admin_credentials(monkeypatch):
    """Configure test-only administrator credentials."""
    monkeypatch.setenv("ADMIN_USERNAME", TEST_USERNAME)
    monkeypatch.setenv(
        "ADMIN_PASSWORD_HASH",
        hash_password(TEST_PASSWORD),
    )


def get_csrf_token(response):
    """Extract the CSRF token from the login form."""
    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        response.text,
    )

    assert match is not None, "CSRF token missing from login page."

    return match.group(1)


def test_login_page_loads(client):
    test_client, _ = client

    response = test_client.get("/login")

    assert response.status_code == 200
    assert "Administrator Login" in response.text
    assert 'name="csrf_token"' in response.text


def test_successful_login(client, admin_credentials):
    test_client, _ = client

    login_page = test_client.get("/login")
    csrf_token = get_csrf_token(login_page)

    response = test_client.post(
        "/login",
        data={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    # An authenticated administrator is redirected away
    # from the login page.
    response = test_client.get(
        "/login",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_wrong_password_is_rejected(client, admin_credentials):
    test_client, _ = client

    login_page = test_client.get("/login")
    csrf_token = get_csrf_token(login_page)

    response = test_client.post(
        "/login",
        data={
            "username": TEST_USERNAME,
            "password": "incorrect-password",
            "csrf_token": csrf_token,
        },
    )

    assert response.status_code == 401
    assert "Invalid username or password." in response.text


def test_wrong_username_is_rejected(client, admin_credentials):
    test_client, _ = client

    login_page = test_client.get("/login")
    csrf_token = get_csrf_token(login_page)

    response = test_client.post(
        "/login",
        data={
            "username": "unknown_user",
            "password": TEST_PASSWORD,
            "csrf_token": csrf_token,
        },
    )

    assert response.status_code == 401
    assert "Invalid username or password." in response.text


def test_login_rejects_invalid_csrf_token(client, admin_credentials):
    test_client, _ = client

    test_client.get("/login")

    response = test_client.post(
        "/login",
        data={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "csrf_token": "invalid-token",
        },
    )

    assert response.status_code == 403


def test_login_rejects_missing_csrf_token(client, admin_credentials):
    test_client, _ = client

    response = test_client.post(
        "/login",
        data={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 422


def test_logout_clears_session(client, admin_credentials):
    test_client, _ = client

    login_page = test_client.get("/login")
    csrf_token = get_csrf_token(login_page)

    login_response = test_client.post(
        "/login",
        data={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )

    assert login_response.status_code == 303

    # Obtain the token created for the authenticated session.
    session = test_client.cookies.get("inventory_session")
    assert session is not None

    # The login route stores a new CSRF token after authentication.
    # Read the signed session through a test-only request.
    from itsdangerous import TimestampSigner
    from base64 import b64decode
    import json
    from auth_config import get_session_secret

    signer = TimestampSigner(str(get_session_secret()))
    session_data = json.loads(
        b64decode(signer.unsign(session.encode("utf-8")))
    )

    logout_token = session_data["csrf_token"]

    response = test_client.post(
        "/logout",
        data={"csrf_token": logout_token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    response = test_client.get("/login")

    assert response.status_code == 200
    assert "Administrator Login" in response.text


def test_logout_rejects_invalid_csrf_token(client, admin_credentials):
    test_client, _ = client

    response = test_client.post(
        "/logout",
        data={"csrf_token": "invalid-token"},
        follow_redirects=False,
    )

    assert response.status_code == 403