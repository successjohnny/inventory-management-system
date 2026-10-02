from collections.abc import Iterable

from models import Product


def get_low_stock_products(
    products: Iterable[Product],
) -> list[Product]:
    """
    Return products whose quantity is at or below
    their configured low-stock level.
    """

    return [
        product
        for product in products
        if product.quantity <= product.low_stock_level
    ]


def build_inventory_insights(
    products: Iterable[Product],
) -> dict:
    """
    Build a structured summary of inventory data.
    """

    products = list(products)
    low_stock_products = get_low_stock_products(products)

    total_inventory_value = sum(
        product.price * product.quantity
        for product in products
    )

    total_items = sum(
        product.quantity
        for product in products
    )

    return {
        "total_products": len(products),
        "total_items": total_items,
        "total_inventory_value": total_inventory_value,
        "low_stock_count": len(low_stock_products),
        "low_stock_products": [
            {
                "name": product.name,
                "quantity": product.quantity,
                "low_stock_level": product.low_stock_level,
            }
            for product in low_stock_products
        ],
        "recommendations": generate_inventory_recommendations(
            products
        ),
    }


def generate_inventory_recommendations(
    products: Iterable[Product],
) -> list[dict]:
    """
    Generate explainable recommendations from inventory data.
    """

    low_stock_products = get_low_stock_products(products)

    return [
        {
            "type": "low_stock",
            "product": product.name,
            "message": (
                f"{product.name} is at or below its low-stock level. "
                "Review this product for restocking."
            ),
        }
        for product in low_stock_products
    ]
