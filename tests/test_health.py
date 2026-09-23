from sqlalchemy.exc import OperationalError

from database import get_db
from main import app


def test_health_check_returns_healthy(client):
    test_client, _ = client

    response = test_client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "database": "connected",
    }


def test_health_check_returns_503_when_database_fails(
    client,
):
    test_client, _ = client

    class FailingDatabase:
        def execute(self, statement):
            raise OperationalError(
                "SELECT 1",
                {},
                Exception("Database unavailable"),
            )

    def override_get_db():
        yield FailingDatabase()

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = test_client.get("/health")

        assert response.status_code == 503

        assert response.json() == {
            "detail": "Database unavailable",
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )