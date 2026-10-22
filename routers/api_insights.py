import os
from typing import TypedDict

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from sqlalchemy.orm import Session

from api_security import require_api_token
from database import get_db
from models import Product
from services.inventory_ai import (
    generate_ai_inventory_analysis,
    get_ai_model,
)
from services.inventory_insights import (
    InventoryInsights,
    build_inventory_insights,
)


# ==========================================
# API RESPONSE DATA TYPES
# ==========================================


class AIInventoryInsightsResponse(TypedDict):
    """
    Define the AI inventory insights API response.

    Data types:
        insights: InventoryInsights
        ai_analysis: str
    """

    insights: InventoryInsights
    ai_analysis: str


# ==========================================
# API ROUTER CONFIGURATION
# ==========================================

router: APIRouter = APIRouter(
    prefix="/api/insights",
    tags=["Inventory Insights API"],
    dependencies=[Depends(require_api_token)],
)


# ==========================================
# CREATE AI CLIENT
# ==========================================


def get_ai_client() -> OpenAI:
    """
    Return a configured OpenAI client.

    Returns:
        OpenAI:
            Configured OpenAI client.

    Raises:
        HTTPException:
            If the API key is missing.
    """

    # Data type: str | None
    api_key: str | None = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=("AI inventory analysis is temporarily unavailable."),
        )

    # Data type: OpenAI
    client: OpenAI = OpenAI(
        api_key=api_key,
    )

    return client


# ==========================================
# GET INVENTORY INSIGHTS
# ==========================================


@router.get(
    "",
    summary="Get inventory insights",
    description=(
        "Return structured inventory statistics, low-stock "
        "information, and inventory recommendations."
    ),
)
def get_inventory_insights(
    db: Session = Depends(get_db),
) -> InventoryInsights:
    """
    Return structured insights for the current inventory.

    Parameters:
        db (Session):
            SQLAlchemy database session.

    Returns:
        InventoryInsights:
            Structured inventory statistics and
            recommendations.
    """

    # Data type: list[Product]
    products: list[Product] = db.query(Product).order_by(Product.id.asc()).all()

    # Data type: InventoryInsights
    insights: InventoryInsights = build_inventory_insights(products)

    return insights


# ==========================================
# GET AI INVENTORY INSIGHTS
# ==========================================


@router.get(
    "/ai",
    summary="Get AI-assisted inventory insights",
    description=(
        "Return deterministic inventory insights together "
        "with AI-assisted inventory analysis."
    ),
)
def get_ai_inventory_insights(
    db: Session = Depends(get_db),
    client: OpenAI = Depends(get_ai_client),
) -> AIInventoryInsightsResponse:
    """
    Return inventory facts and AI-assisted analysis.

    Parameters:
        db (Session):
            SQLAlchemy database session.

        client (OpenAI):
            Configured OpenAI client.

    Returns:
        AIInventoryInsightsResponse:
            Dictionary containing inventory insights
            and generated AI analysis.

    Raises:
        HTTPException:
            If AI analysis cannot be completed.
    """

    # Data type: list[Product]
    products: list[Product] = db.query(Product).order_by(Product.id.asc()).all()

    # Data type: InventoryInsights
    insights: InventoryInsights = build_inventory_insights(products)

    try:
        # Data type: str
        ai_analysis: str = generate_ai_inventory_analysis(
            insights,
            client=client,
            model=get_ai_model(),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=("AI inventory analysis is temporarily unavailable."),
        ) from exc

    # Data type: AIInventoryInsightsResponse
    response: AIInventoryInsightsResponse = {
        "insights": insights,
        "ai_analysis": ai_analysis,
    }

    return response
