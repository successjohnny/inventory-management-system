import json
import os

from typing import Protocol

from services.inventory_insights import InventoryInsights


# ==========================================
# AI RESPONSE DATA TYPE
# ==========================================

class AIResponse(Protocol):
    """
    Describe the response fields used by this service.

    Data types:
        output_text: str | None
    """

    @property
    def output_text(self) -> str | None:
        ...


# ==========================================
# AI RESPONSE CREATION INTERFACE
# ==========================================

class AIResponsesAPI(Protocol):
    """
    Describe the response creation method.

    Parameters:
        model: str
        input: str

    Returns:
        AIResponse
    """

    def create(
        self,
        *,
        model: str,
        input: str,
    ) -> AIResponse:
        ...


# ==========================================
# AI CLIENT INTERFACE
# ==========================================

class AIClient(Protocol):
    """
    Describe the client interface required
    for generating inventory analysis.

    Data types:
        responses: AIResponsesAPI
    """

    @property
    def responses(self) -> AIResponsesAPI:
        ...


# ==========================================
# GET CONFIGURED AI MODEL
# ==========================================

def get_ai_model() -> str:
    """
    Return the configured OpenAI model name.

    Returns:
        str:
            Model name stored in OPENAI_MODEL.

    Raises:
        KeyError:
            If OPENAI_MODEL is not configured.
    """

    model: str = os.environ["OPENAI_MODEL"]

    return model


# ==========================================
# BUILD INVENTORY AI PROMPT
# ==========================================

def build_inventory_ai_prompt(
    insights: InventoryInsights,
) -> str:
    """
    Build a grounded, structured prompt
    from inventory insights.

    Parameters:
        insights (InventoryInsights):
            Dictionary containing inventory statistics,
            low-stock products, and recommendations.

    Returns:
        str:
            Formatted prompt for AI analysis.
    """

    # Data type: str
    inventory_data: str = json.dumps(
        insights,
        indent=2,
    )

    # Data type: str
    prompt: str = (
        "Analyze the following inventory data and provide "
        "clear, practical inventory recommendations.\n\n"

        "Use only the facts provided in the inventory data. "
        "Do not invent products, quantities, stock levels, "
        "prices, or inventory values.\n\n"

        "Do not invent reorder quantities, supplier information, "
        "currency, demand patterns, sales trends, lead times, "
        "or other facts that are not provided.\n\n"

        "Pay particular attention to low-stock products. "
        "Recommendations must be based only on the supplied "
        "inventory facts.\n\n"

        "Structure the response using exactly these sections:\n\n"

        "Inventory Health\n"
        "Give a short assessment of the overall inventory "
        "condition based only on the supplied data.\n\n"

        "Low-Stock Alerts\n"
        "List low-stock products and their supplied quantities "
        "and low-stock levels. If there are no low-stock "
        "products, state that clearly.\n\n"

        "Recommended Actions\n"
        "Give practical actions supported by the supplied data. "
        "Do not invent specific reorder quantities or unsupported "
        "business information.\n\n"

        "Inventory Summary\n"
        "Summarize the supplied totals, including total products, "
        "total items, total inventory value, and low-stock count. "
        "Do not assign a currency unless one is explicitly "
        "provided in the inventory data.\n\n"

        "Inventory data:\n"
        f"{inventory_data}"
    )

    return prompt


# ==========================================
# GENERATE AI INVENTORY ANALYSIS
# ==========================================

def generate_ai_inventory_analysis(
    insights: InventoryInsights,
    *,
    client: AIClient,
    model: str,
) -> str:
    """
    Generate AI-assisted inventory analysis.

    Parameters:
        insights (InventoryInsights):
            Structured inventory statistics.

        client (AIClient):
            AI client implementing the required
            responses.create() interface.

        model (str):
            Name of the AI model to use.

    Returns:
        str:
            Generated inventory analysis or
            a descriptive fallback message.
    """

    # Avoid AI requests when inventory is empty.
    if insights.get("total_products", 0) == 0:
        return (
            "No inventory data is available for AI analysis."
        )

    # Data type: str
    prompt: str = build_inventory_ai_prompt(insights)

    # Data type: AIResponse
    response: AIResponse = client.responses.create(
        model=model,
        input=prompt,
    )

    if not response.output_text:
        return (
            "AI analysis did not return any content."
        )

    return response.output_text
