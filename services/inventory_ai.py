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
    Build a prompt from structured inventory insights.
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
        "Pay particular attention to low-stock products and "
        "explain any recommended action.\n\n"
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