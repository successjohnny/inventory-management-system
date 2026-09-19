import pytest

from fastapi.testclient import TestClient

from api_security import get_api_token
from main import app


TEST_API_TOKEN = "test-only-api-token-for-inventory-security-2026"


def test_api_token_missing(monkeypatch):
    """A missing API token must raise a configuration error."""

    monkeypatch.delenv("API_TOKEN", raising=False)

    with pytest.raises(
        RuntimeError,
        match="API_TOKEN is not configured",
    ):
        get_api_token()


def test_api_token_too_short(monkeypatch):
    """An API token shorter than 32 characters must be rejected."""

    monkeypatch.setenv("API_TOKEN", "short-token")

    with pytest.raises(
        RuntimeError,
        match="API_TOKEN must contain at least 32 characters",
    ):
        get_api_token()


def test_valid_api_token(monkeypatch):
    """A sufficiently long API token must be accepted."""

    monkeypatch.setenv("API_TOKEN", TEST_API_TOKEN)

    assert get_api_token() == TEST_API_TOKEN


def test_startup_fails_without_api_token(monkeypatch):
    """
    FastAPI must refuse to start when API_TOKEN is missing.
    """

    monkeypatch.delenv("API_TOKEN", raising=False)

    with pytest.raises(
        RuntimeError,
        match="API_TOKEN is not configured",
    ):
        with TestClient(app):
            pass


def test_startup_fails_with_short_api_token(monkeypatch):
    """
    FastAPI must refuse to start when API_TOKEN is too short.
    """

    monkeypatch.setenv("API_TOKEN", "short-token")

    with pytest.raises(
        RuntimeError,
        match="API_TOKEN must contain at least 32 characters",
    ):
        with TestClient(app):
            pass