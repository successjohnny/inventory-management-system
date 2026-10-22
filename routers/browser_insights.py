
import json
import os
from typing import TypedDict

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)
from openai import OpenAI
from sqlalchemy.orm import Session

from browser_security import (
    require_admin,
    require_csrf,
)
from database import get_db
from models import AIAnalysis, Product
from services.inventory_ai import (
    generate_ai_inventory_analysis,
    get_ai_model,
)
from services.inventory_insights import (
    build_inventory_insights,
)


# ==========================================
# RESPONSE DATA TYPES
# ==========================================

class BrowserAIInsightsResponse(TypedDict):
    insights: dict[str, object]
    ai_analysis: str


# ==========================================
# API ROUTER
# ==========================================

router: APIRouter = APIRouter(
    include_in_schema=False,
)


# ==========================================
# GENERATE BROWSER AI INSIGHTS
# ==========================================

@router.post("/ai-insights")
def generate_browser_ai_insights(
    request: Request,
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
) -> BrowserAIInsightsResponse:
    """
    Generate AI-assisted inventory insights for an
    authenticated dashboard user.

    Successful analyses are stored with the inventory
    snapshot that produced them.
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

    products: list[Product] = (
        db.query(Product)
        .order_by(Product.id.asc())
        .all()
    )

    insights: dict[str, object] = (
        build_inventory_insights(products)
    )

    if insights.get("total_products", 0) == 0:
        response: BrowserAIInsightsResponse = {
            "insights": insights,
            "ai_analysis": (
                "No inventory data is available for AI analysis."
            ),
        }

        return response

    api_key: str | None = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI inventory analysis is temporarily "
                "unavailable."
            ),
        )

    client: OpenAI = OpenAI(
        api_key=api_key,
    )

    try:
        ai_analysis: str = generate_ai_inventory_analysis(
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

    analysis_record: AIAnalysis = AIAnalysis(
        inventory_snapshot=json.dumps(
            insights,
        ),
        analysis=ai_analysis,
    )

    try:
        db.add(analysis_record)
        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "AI analysis was generated but could not "
                "be saved."
            ),
        ) from exc

    response: BrowserAIInsightsResponse = {
        "insights": insights,
        "ai_analysis": ai_analysis,
    }

    return response