
from datetime import date, datetime, time, timedelta, timezone

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from browser_security import (
    get_csrf_token,
    require_admin,
    require_csrf,
)
from database import get_db
from models import AIAnalysis, Product, StockMovement
from services.error_messages import ERROR_MESSAGES
from services.product_service import (
    create_product,
    update_product,
    validate_product,
    delete_product,
)
from services.stock_trends import build_stock_trends


# Browser-only routes are excluded from the OpenAPI/Swagger schema.
router = APIRouter(
    include_in_schema=False,
)

templates = Jinja2Templates(directory="templates")


@router.get("/")
def home(
    request: Request,
    search: str = "",
    error: str = "",
    trend_start: date | None = Query(default=None),
    trend_end: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)

    if redirect is not None:
        return redirect

    # ==========================================
    # Inventory Products
    # ==========================================

    all_products = db.query(Product).all()

    # ==========================================
    # Category Inventory Valuations
    # ==========================================

    category_valuations = {}

    for product in all_products:
        if product.category not in category_valuations:
            category_valuations[product.category] = 0

        category_valuations[product.category] += (
            product.price * product.quantity
        )

    # ==========================================
    # Supplier Inventory Valuations
    # ==========================================

    supplier_valuations = {}

    for product in all_products:
        if not product.supplier:
            continue

        if product.supplier not in supplier_valuations:
            supplier_valuations[product.supplier] = 0

        supplier_valuations[product.supplier] += (
            product.price * product.quantity
        )

    # ==========================================
    # Low-Stock Insights
    # ==========================================

    low_stock_insights = [
        product
        for product in all_products
        if product.quantity <= product.low_stock_level
    ]

    # ==========================================
    # Complete Stock Movement History
    # ==========================================

    movements = (
        db.query(StockMovement)
        .options(
            joinedload(StockMovement.product)
        )
        .all()
    )

    # ==========================================
    # Pass 5: Historical Stock Trends
    # ==========================================

    today = datetime.now(timezone.utc).date()

    # Use today when no end date is provided.
    end_date = (
        trend_end
        if trend_end is not None
        else today
    )

    # Default to 30 calendar days, including
    # the selected end date.
    start_date = (
        trend_start
        if trend_start is not None
        else end_date - timedelta(days=29)
    )

    # Validate the selected reporting period.
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Trend start date cannot be later "
                "than trend end date."
            ),
        )

    # Both boundary dates count toward the limit.
    if (end_date - start_date).days >= 365:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "The reporting period cannot "
                "exceed 365 calendar days."
            ),
        )

    # Convert inclusive dates to UTC timestamps.
    start_datetime = datetime.combine(
        start_date,
        time.min,
        tzinfo=timezone.utc,
    )

    # Exclusive boundary at midnight after end_date.
    end_datetime = datetime.combine(
        end_date + timedelta(days=1),
        time.min,
        tzinfo=timezone.utc,
    )

    # Query only movements in the chart period.
    trend_movements = (
        db.query(StockMovement)
        .filter(
            StockMovement.created_at >= start_datetime,
            StockMovement.created_at < end_datetime,
        )
        .order_by(
            StockMovement.created_at.asc(),
            StockMovement.id.asc(),
        )
        .all()
    )

    stock_trends = build_stock_trends(
        trend_movements,
        start_date,
        end_date,
    )

    # ==========================================
    # Saved AI Analysis History
    # ==========================================

    ai_analysis_history = (
        db.query(AIAnalysis)
        .order_by(
            AIAnalysis.created_at.desc(),
            AIAnalysis.id.desc(),
        )
        .limit(5)
        .all()
    )

    # ==========================================
    # Product Search
    # ==========================================

    normalized_search = search.strip().lower()

    if normalized_search:
        products = (
            db.query(Product)
            .filter(
                Product.normalized_name.ilike(
                    f"%{normalized_search}%"
                )
            )
            .all()
        )
    else:
        products = all_products

    # ==========================================
    # Dashboard Template Response
    # ==========================================

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "products": products,
            "category_valuations": category_valuations,
            "supplier_valuations": supplier_valuations,
            "low_stock_insights": low_stock_insights,
            "total_products": len(all_products),
            "total_items": sum(
                product.quantity
                for product in all_products
            ),
            "total_categories": len(
                {
                    product.category
                    for product in all_products
                }
            ),
            "low_stock_products": sum(
                1
                for product in all_products
                if product.quantity
                <= product.low_stock_level
            ),
            "movements": movements,
            "stock_trends": stock_trends,
            "trend_start": start_date.isoformat(),
            "trend_end": end_date.isoformat(),
            "ai_analysis_history": ai_analysis_history,
            "error": ERROR_MESSAGES.get(
                error,
                error,
            ),
            "search": search,
            "csrf_token": get_csrf_token(
                request
            ),
        },
    )


# ==========================================
# Saved AI Analysis Detail
# ==========================================

@router.get("/ai-analysis/{analysis_id}")
def ai_analysis_detail(
    request: Request,
    analysis_id: int,
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)

    if redirect is not None:
        return redirect

    analysis = (
        db.query(AIAnalysis)
        .filter(
            AIAnalysis.id == analysis_id
        )
        .first()
    )

    if analysis is None:
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="ai_analysis_detail.html",
        context={
            "analysis": analysis,
        },
    )


# ==========================================
# Add Product
# ==========================================

@router.post("/add-product")
def add_product(
    request: Request,
    name: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    low_stock_level: int = Form(...),
    category: str = Form(...),
    supplier: str = Form(""),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)

    if redirect is not None:
        return redirect

    require_csrf(
        request,
        csrf_token,
    )

    error = validate_product(
        name,
        price,
        low_stock_level,
        category,
    )

    if error:
        return RedirectResponse(
            url=f"/?error={error}",
            status_code=303,
        )

    if quantity < 0:
        return RedirectResponse(
            url="/?error=invalid_quantity",
            status_code=303,
        )

    result = create_product(
        db,
        name,
        price,
        quantity,
        low_stock_level,
        category,
        supplier,
    )

    if isinstance(result, str):
        return RedirectResponse(
            url=f"/?error={result}",
            status_code=303,
        )

    return RedirectResponse(
        url="/",
        status_code=303,
    )


# ==========================================
# Edit Product Page
# ==========================================

@router.get("/edit-product/{product_id}")
def edit_product(
    request: Request,
    product_id: int,
    error: str = "",
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)

    if redirect is not None:
        return redirect

    product = (
        db.query(Product)
        .filter(
            Product.id == product_id
        )
        .first()
    )

    if not product:
        return RedirectResponse(
            url="/?error=product_not_found",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_product.html",
        context={
            "product": product,
            "error": ERROR_MESSAGES.get(
                error,
                error,
            ),
            "csrf_token": get_csrf_token(
                request
            ),
        },
    )


# ==========================================
# Update Product
# ==========================================

@router.post("/edit-product/{product_id}")
def update_product_route(
    request: Request,
    product_id: int,
    name: str = Form(...),
    price: int = Form(...),
    low_stock_level: int = Form(...),
    category: str = Form(...),
    supplier: str = Form(""),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)

    if redirect is not None:
        return redirect

    require_csrf(
        request,
        csrf_token,
    )

    error = validate_product(
        name,
        price,
        low_stock_level,
        category,
    )

    if error:
        return RedirectResponse(
            url=(
                f"/edit-product/{product_id}"
                f"?error={error}"
            ),
            status_code=303,
        )

    result = update_product(
        db,
        product_id,
        name,
        price,
        low_stock_level,
        category,
        supplier,
    )

    if isinstance(result, str):
        return RedirectResponse(
            url=(
                f"/edit-product/{product_id}"
                f"?error={result}"
            ),
            status_code=303,
        )

    return RedirectResponse(
        url="/",
        status_code=303,
    )


# ==========================================
# Delete Product
# ==========================================

@router.post("/delete-product/{product_id}")
def delete_product_route(
    request: Request,
    product_id: int,
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    redirect = require_admin(request)

    if redirect is not None:
        return redirect

    require_csrf(
        request,
        csrf_token,
    )

    error = delete_product(
        db,
        product_id,
    )

    if error == "product_not_found":
        return RedirectResponse(
            url="/?error=product_not_found",
            status_code=303,
        )

    return RedirectResponse(
        url="/",
        status_code=303,
    )