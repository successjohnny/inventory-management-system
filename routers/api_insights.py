import os

from openai import OpenAI
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api_security import require_api_token
from database import get_db
from models import Product
from services.inventory_ai import (
    generate_ai_inventory_analysis,
    get_ai_model,
)
from services.inventory_insights import build_inventory_insights


router = APIRouter(
    prefix="/api/insights",
    tags=["Inventory Insights API"],
    dependencies=[Depends(require_api_token)],
)


def get_ai_client():
    """
    Return a configured OpenAI client.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI inventory analysis is temporarily "
                "unavailable."
            ),
        )

    return OpenAI(
        api_key=api_key,
    )


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
):
    """
    Return structured insights for the current inventory.
    """

    products = (
        db.query(Product)
        .order_by(Product.id.asc())
        .all()
    )

    return build_inventory_insights(products)


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
    client=Depends(get_ai_client),
):
    """
    Return inventory facts and AI-assisted analysis.
    """

    products = (
        db.query(Product)
        .order_by(Product.id.asc())
        .all()
    )

    insights = build_inventory_insights(products)

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