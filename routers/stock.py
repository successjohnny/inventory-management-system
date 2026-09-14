from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from services.error_messages import ERROR_MESSAGES
from services.inventory_service import process_stock_movement


router = APIRouter()


@router.post("/stock-movement/{product_id}")
def stock_movement(
    product_id: int,
    movement_type: str = Form(...),
    quantity: int = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    error = process_stock_movement(
        db,
        product_id,
        movement_type,
        quantity,
        note,
    )

    if error:
        if error == "product_not_found":
            return RedirectResponse(
                url="/?error=product_not_found",
                status_code=303,
            )

        return RedirectResponse(
            url=(
                f"/edit-product/"
                f"{product_id}"
                f"?error={error}"
            ),
            status_code=303,
        )

    return RedirectResponse(
        url="/",
        status_code=303,
    )