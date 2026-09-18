import hmac
import secrets

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from auth_credentials import verify_admin_credentials


router = APIRouter()
templates = Jinja2Templates(directory="templates")


def create_csrf_token(request: Request) -> str:
    token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = token
    return token


def verify_csrf_token(request: Request, submitted_token: str) -> None:
    expected_token = request.session.get("csrf_token")

    if (
        not isinstance(expected_token, str)
        or not isinstance(submitted_token, str)
        or not hmac.compare_digest(expected_token, submitted_token)
    ):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("authenticated") is True:
        return RedirectResponse(url="/", status_code=303)

    token = create_csrf_token(request)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None,
            "csrf_token": token,
        },
    )


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    verify_csrf_token(request, csrf_token)

    if not verify_admin_credentials(username, password):
        token = create_csrf_token(request)

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
    request.session["csrf_token"] = secrets.token_urlsafe(32)

    return RedirectResponse(url="/", status_code=303)


@router.post("/logout")
def logout(
    request: Request,
    csrf_token: str = Form(...),
):
    verify_csrf_token(request, csrf_token)

    request.session.clear()

    return RedirectResponse(url="/login", status_code=303)