import hmac
import secrets

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse


def require_admin(request: Request):
    """
    Require an authenticated administrator.

    Return a redirect response for anonymous browser users.
    """
    if request.session.get("authenticated") is not True:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return None


def get_csrf_token(request: Request) -> str:
    """
    Return the session's existing CSRF token.

    Create one if the session does not already have one.
    """
    token = request.session.get("csrf_token")

    if not isinstance(token, str) or not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token

    return token


def require_csrf(request: Request, submitted_token: str) -> None:
    """
    Reject requests without the correct session CSRF token.
    """
    expected_token = request.session.get("csrf_token")

    if (
        not isinstance(expected_token, str)
        or not isinstance(submitted_token, str)
        or not hmac.compare_digest(
            expected_token,
            submitted_token,
        )
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid CSRF token.",
        )