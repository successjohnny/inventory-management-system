
"""
Browser routes for the Inventory Reports Dashboard.
"""

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from browser_security import require_admin
from database import get_db
from models import Product
from routers.api_reports import (
    export_inventory_csv,
    export_stock_movements_csv,
    get_category_valuation_report,
    get_supplier_summary_report,
)


# ==========================================
# BROWSER REPORTS ROUTER
# ==========================================

router: APIRouter = APIRouter(
    include_in_schema=False,
)

templates: Jinja2Templates = Jinja2Templates(
    directory="templates"
)


# ==========================================
# REPORTS DASHBOARD
# ==========================================

@router.get("/reports")
def reports_dashboard(
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    """
    Display inventory reports for authenticated administrators.
    """

    redirect = require_admin(request)

    if redirect is not None:
        return redirect

    products: list[Product] = (
        db.query(Product).all()
    )

    total_products: int = len(products)

    total_items: int = sum(
        product.quantity
        for product in products
    )

    total_inventory_value: int = sum(
        product.price * product.quantity
        for product in products
    )

    low_stock_products: int = sum(
        1
        for product in products
        if product.quantity <= product.low_stock_level
    )

    category_reports = get_category_valuation_report(
        db=db
    )

    supplier_reports = get_supplier_summary_report(
        db=db
    )

    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "total_products": total_products,
            "total_items": total_items,
            "total_inventory_value": total_inventory_value,
            "low_stock_products": low_stock_products,
            "category_reports": category_reports,
            "supplier_reports": supplier_reports,
        },
    )


# ==========================================
# DOWNLOAD INVENTORY CSV
# ==========================================

@router.get("/reports/download/inventory")
def download_inventory_report(
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    """
    Download inventory CSV for authenticated administrators.
    """

    redirect = require_admin(request)

    if redirect is not None:
        return redirect

    return export_inventory_csv(
        db=db
    )


# ==========================================
# DOWNLOAD STOCK MOVEMENTS CSV
# ==========================================

@router.get("/reports/download/stock-movements")
def download_stock_movements_report(
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    """
    Download stock movement CSV for authenticated administrators.
    """

    redirect = require_admin(request)

    if redirect is not None:
        return redirect

    return export_stock_movements_csv(
        start_date=None,
        end_date=None,
        db=db,
    )