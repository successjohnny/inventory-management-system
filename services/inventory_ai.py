import json
import os


def get_ai_model() -> str:
    """
    Return the configured OpenAI model name.
    """

    return os.environ["OPENAI_MODEL"]


def build_inventory_ai_prompt(
    insights: dict,
) -> str:
    """
    Build a grounded, structured prompt from inventory insights.
    """

    inventory_data = json.dumps(
        insights,
        indent=2,
    )

    return (
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


def generate_ai_inventory_analysis(
    insights: dict,
    *,
    client,
    model: str,
) -> str:
    """
    Generate AI-assisted analysis from structured
    inventory insights.
    """

    if insights.get("total_products", 0) == 0:
        return (
            "No inventory data is available for AI analysis."
        )

    prompt = build_inventory_ai_prompt(insights)

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    if not response.output_text:
        return (
            "AI analysis did not return any content."
        )

    return response.output_text