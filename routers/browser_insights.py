import os

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from openai import OpenAI
from sqlalchemy.orm import Session

from browser_security import require_admin, require_csrf
from database import get_db
from models import Product
from services.inventory_ai import (
    generate_ai_inventory_analysis,
    get_ai_model,
)
from services.inventory_insights import build_inventory_insights


router = APIRouter(
    include_in_schema=False,
)


@router.post("/ai-insights")
def generate_browser_ai_insights(
    request: Request,
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    """
    Generate AI-assisted inventory insights for an
    authenticated dashboard user.
    """

    redirect = require_admin(request)

    if redirect is not None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    require_csrf(
        request,
        csrf_token,
    )

    products = (
        db.query(Product)
        .order_by(Product.id.asc())
        .all()
    )

    insights = build_inventory_insights(products)

    if insights.get("total_products", 0) == 0:
        return {
            "insights": insights,
            "ai_analysis": (
                "No inventory data is available for AI analysis."
            ),
        }

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI inventory analysis is temporarily "
                "unavailable."
            ),
        )

    client = OpenAI(
        api_key=api_key,
    )

    try:
        ai_analysis = generate_ai_inventory_analysis(
            insights,
            client=client,
            model=get_ai_model(),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI inventory analysis is temporarily "
                "unavailable."
            ),
        ) from exc

    return {
        "insights": insights,
        "ai_analysis": ai_analysis,
    }