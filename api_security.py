import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)


bearer_scheme = HTTPBearer(auto_error=False)


def get_api_token() -> str:
    """
    Return the configured API token.

    Refuse to continue if it is missing or too short.
    """

    token = os.getenv("API_TOKEN")

    if not token:
        raise RuntimeError(
            "API_TOKEN is not configured."
        )

    if len(token) < 32:
        raise RuntimeError(
            "API_TOKEN must contain at least 32 characters."
        )

    return token


def require_api_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> None:
    """
    Require a valid bearer token for protected API endpoints.
    """

    expected_token = get_api_token()

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API authentication required.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not secrets.compare_digest(
        credentials.credentials,
        expected_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )