
import hmac
import secrets

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    Response,
)
from fastapi.templating import Jinja2Templates

from auth_credentials import verify_admin_credentials


# ==========================================
# AUTHENTICATION ROUTER
# ==========================================

# Browser-only routes are excluded from
# the OpenAPI/Swagger schema.

router: APIRouter = APIRouter(
    include_in_schema=False,
)

templates: Jinja2Templates = Jinja2Templates(
    directory="templates"
)


# ==========================================
# CREATE CSRF TOKEN
# ==========================================

def create_csrf_token(
    request: Request,
) -> str:
    """
    Generate a CSRF token and store it
    in the user's session.
    """

    token: str = secrets.token_urlsafe(32)

    request.session["csrf_token"] = token

    return token


# ==========================================
# VERIFY CSRF TOKEN
# ==========================================

def verify_csrf_token(
    request: Request,
    submitted_token: str,
) -> None:
    """
    Validate a submitted CSRF token
    against the token stored in the session.
    """

    expected_token: object = request.session.get(
        "csrf_token"
    )

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


# ==========================================
# LOGIN PAGE
# ==========================================

@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(
    request: Request,
) -> Response:
    """
    Display the login page or redirect
    an already authenticated user.
    """

    if request.session.get("authenticated") is True:
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    token: str = create_csrf_token(request)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None,
            "csrf_token": token,
        },
    )


# ==========================================
# LOGIN
# ==========================================

@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
) -> Response:
    """
    Verify login credentials and establish
    an authenticated session.
    """

    verify_csrf_token(
        request,
        csrf_token,
    )

    if not verify_admin_credentials(
        username,
        password,
    ):
        token: str = create_csrf_token(request)

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid username or password.",
                "csrf_token": token,
            },
            status_code=401,
        )

    request.session.clear()

    request.session["authenticated"] = True

    request.session["csrf_token"] = (
        secrets.token_urlsafe(32)
    )

    return RedirectResponse(
        url="/",
        status_code=303,
    )


# ==========================================
# LOGOUT
# ==========================================

@router.post("/logout")
def logout(
    request: Request,
    csrf_token: str = Form(...),
) -> RedirectResponse:
    """
    Validate the CSRF token, clear the
    session, and redirect to the login page.
    """

    verify_csrf_token(
        request,
        csrf_token,
    )

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303,
    )