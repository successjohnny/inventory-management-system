import pytest

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

from browser_security import (
    get_csrf_token,
    require_admin,
    require_csrf,
)


def make_request(session_data):
    """
    Build a test request with a controllable session.
    """
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "session": session_data,
    }

    return Request(scope)


def test_anonymous_user_is_redirected():
    request = make_request({})

    response = require_admin(request)

    assert isinstance(response, RedirectResponse)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_authenticated_admin_is_allowed():
    request = make_request({
        "authenticated": True,
    })

    response = require_admin(request)

    assert response is None


def test_false_authentication_is_rejected():
    request = make_request({
        "authenticated": False,
    })

    response = require_admin(request)

    assert isinstance(response, RedirectResponse)


def test_csrf_token_is_created():
    session = {}
    request = make_request(session)

    token = get_csrf_token(request)

    assert isinstance(token, str)
    assert len(token) > 20
    assert session["csrf_token"] == token


def test_existing_csrf_token_is_reused():
    request = make_request({
        "csrf_token": "existing-test-token",
    })

    token = get_csrf_token(request)

    assert token == "existing-test-token"


def test_valid_csrf_token_is_accepted():
    request = make_request({
        "csrf_token": "valid-test-token",
    })

    assert require_csrf(
        request,
        "valid-test-token",
    ) is None


def test_invalid_csrf_token_is_rejected():
    request = make_request({
        "csrf_token": "correct-token",
    })

    with pytest.raises(HTTPException) as error:
        require_csrf(
            request,
            "incorrect-token",
        )

    assert error.value.status_code == 403


def test_missing_csrf_token_is_rejected():
    request = make_request({})

    with pytest.raises(HTTPException) as error:
        require_csrf(
            request,
            "submitted-token",
        )

    assert error.value.status_code == 403