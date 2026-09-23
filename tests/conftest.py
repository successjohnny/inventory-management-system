import os
import re

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth_credentials import hash_password
from database import Base, get_db


# ==========================================
# TEST ENVIRONMENT CONFIGURATION
# ==========================================

# These credentials are for automated tests only.
# Never use production secrets in the test suite.
#
# They must exist before importing main.py because
# the application validates its security configuration
# during startup.

os.environ.setdefault(
    "SESSION_SECRET_KEY",
    "pytest-only-session-secret-do-not-use-in-production",
)

os.environ.setdefault(
    "API_TOKEN",
    "pytest-api-token-only-do-not-use-in-production-123456789",
)


from main import app


# ==========================================
# TEST CREDENTIALS
# ==========================================

# Test credentials only.
# Never use your real administrator password in tests.
TEST_ADMIN_USERNAME = "test_admin"
TEST_ADMIN_PASSWORD = "test-password-for-pytest"


# ==========================================
# DATABASE FIXTURE
# ==========================================

@pytest.fixture
def db_session():
    """
    Create a temporary in-memory database
    for service tests.
    """

    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()

        Base.metadata.drop_all(bind=engine)

        engine.dispose()


# ==========================================
# UNAUTHENTICATED TEST CLIENT
# ==========================================

@pytest.fixture
def client():
    """
    Create an unauthenticated FastAPI test client
    using a temporary in-memory database.

    Use an HTTPS base URL so that session cookies
    marked Secure are returned by the test client.

    This fixture is also used for API tests and
    security tests.
    """

    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(
            app,
            base_url="https://testserver",
        ) as test_client:
            yield test_client, db

    finally:
        app.dependency_overrides.clear()

        db.close()

        Base.metadata.drop_all(bind=engine)

        engine.dispose()


# ==========================================
# CSRF HELPER
# ==========================================

def extract_csrf_token(html: str) -> str:
    """
    Extract a CSRF token from an HTML form.
    """

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        html,
    )

    if match is None:
        raise AssertionError(
            "CSRF token was not found in the HTML response."
        )

    return match.group(1)


# ==========================================
# AUTHENTICATED CLIENT WRAPPER
# ==========================================

class AuthenticatedInventoryClient:
    """
    Wrap a logged-in TestClient.

    Automatically include a valid CSRF token when
    existing browser-route tests submit forms.

    API requests remain unchanged.

    Security tests should use the original client
    fixture to test missing or invalid tokens.
    """

    def __init__(
        self,
        test_client,
        csrf_token,
    ):
        self.test_client = test_client

        self.csrf_token = csrf_token

    def get(self, *args, **kwargs):
        return self.test_client.get(
            *args,
            **kwargs,
        )

    def post(self, url, *args, **kwargs):

        browser_form_routes = (
            url == "/add-product"
            or url.startswith("/edit-product/")
            or url.startswith("/delete-product/")
            or url.startswith("/stock-movement/")
        )

        if browser_form_routes:

            data = dict(
                kwargs.get("data") or {}
            )

            data.setdefault(
                "csrf_token",
                self.csrf_token,
            )

            kwargs["data"] = data

        return self.test_client.post(
            url,
            *args,
            **kwargs,
        )

    def __getattr__(self, name):
        """
        Allow access to other TestClient methods
        and attributes.
        """

        return getattr(
            self.test_client,
            name,
        )


# ==========================================
# AUTHENTICATED BROWSER CLIENT
# ==========================================

@pytest.fixture
def authenticated_client(
    client,
    monkeypatch,
):
    """
    Log in through the actual authentication endpoint.

    Return:
        - Authenticated test client
        - Temporary test database
    """

    test_client, db = client

    # Configure temporary administrator credentials.
    monkeypatch.setenv(
        "ADMIN_USERNAME",
        TEST_ADMIN_USERNAME,
    )

    monkeypatch.setenv(
        "ADMIN_PASSWORD_HASH",
        hash_password(
            TEST_ADMIN_PASSWORD
        ),
    )

    # Step 1: Open the login page.
    login_page = test_client.get(
        "/login"
    )

    assert login_page.status_code == 200

    # Step 2: Extract the login CSRF token.
    login_token = extract_csrf_token(
        login_page.text
    )

    # Step 3: Submit the actual login form.
    login_response = test_client.post(
        "/login",
        data={
            "username": TEST_ADMIN_USERNAME,
            "password": TEST_ADMIN_PASSWORD,
            "csrf_token": login_token,
        },
        follow_redirects=False,
    )

    assert login_response.status_code == 303

    assert (
        login_response.headers["location"]
        == "/"
    )

    # Step 4: Open the authenticated dashboard.
    dashboard = test_client.get(
        "/"
    )

    assert dashboard.status_code == 200

    # Step 5: Extract the authenticated session's
    # CSRF token from the dashboard.
    dashboard_token = extract_csrf_token(
        dashboard.text
    )

    # Step 6: Return the authenticated client
    # and temporary database.
    authenticated_test_client = AuthenticatedInventoryClient(
        test_client,
        dashboard_token,
    )

    return authenticated_test_client, db


# ==========================================
# AUTHENTICATED API CLIENT
# ==========================================

@pytest.fixture
def api_client(
    client,
    monkeypatch,
):
    """
    Return an API test client with a valid bearer token.

    Reuse the temporary database provided by the
    client fixture.
    """

    test_client, db = client

    test_token = (
        "test-api-token-for-inventory-tests-123456789"
    )

    monkeypatch.setenv(
        "API_TOKEN",
        test_token,
    )

    test_client.headers.update(
        {
            "Authorization": f"Bearer {test_token}",
        }
    )

    return test_client, db