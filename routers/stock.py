from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from browser_security import (
    require_admin,
    require_csrf,
)
from database import get_db
from services.inventory_service import (
    process_stock_movement,
)


# Browser-only routes are excluded from the OpenAPI/Swagger schema.
router = APIRouter(
    include_in_schema=False,
)


@router.post("/stock-movement/{product_id}")
def stock_movement(
    request: Request,
    product_id: int,
    movement_type: str = Form(...),
    quantity: int = Form(...),
    note: str = Form(""),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    """
    Process a browser stock movement.

    Authentication and CSRF validation must succeed
    before inventory data can be modified.
    """

    # Step 1: Require an authenticated administrator.
    redirect = require_admin(request)

    if redirect is not None:
        return redirect

    # Step 2: Validate the CSRF token.
    require_csrf(
        request,
        csrf_token,
    )

    # Step 3: Process the stock movement.
    error = process_stock_movement(
        db,
        product_id,
        movement_type,
        quantity,
        note,
    )

    # Step 4: Handle errors.
    if error:
        if error == "product_not_found":
            return RedirectResponse(
                url="/?error=product_not_found",
                status_code=303,
            )

        return RedirectResponse(
            url=(
                f"/edit-product/{product_id}"
                f"?error={error}"
            ),
            status_code=303,
        )

    # Step 5: Return to the dashboard.
    return RedirectResponse(
        url="/",
        status_code=303,
    )