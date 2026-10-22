from collections.abc import Iterable
from typing import TypedDict

from models import Product


# ==========================================
# INVENTORY DATA TYPES
# ==========================================


class LowStockProductInfo(TypedDict):
    """
    Structure of a low-stock product summary.

    Data types:
        name: str
        quantity: int
        low_stock_level: int
    """

    name: str
    quantity: int
    low_stock_level: int


class InventoryRecommendation(TypedDict):
    """
    Structure of an inventory recommendation.

    Data types:
        type: str
        product: str
        message: str
    """

    type: str
    product: str
    message: str


class InventoryInsights(TypedDict):
    """
    Structure of the complete inventory summary.

    Data types:
        total_products: int
        total_items: int
        total_inventory_value: int
        low_stock_count: int
        low_stock_products: list[LowStockProductInfo]
        recommendations: list[InventoryRecommendation]
    """

    total_products: int
    total_items: int
    total_inventory_value: int
    low_stock_count: int
    low_stock_products: list[LowStockProductInfo]
    recommendations: list[InventoryRecommendation]


# ==========================================
# LOW-STOCK PRODUCTS
# ==========================================


def get_low_stock_products(
    products: Iterable[Product],
) -> list[Product]:
    """
    Return products whose quantity is at or below
    their configured low-stock level.

    Parameters:
        products (Iterable[Product]):
            Collection of Product objects.

    Returns:
        list[Product]:
            Products with low stock.
    """

    low_stock_products: list[Product] = [
        product for product in products if product.quantity <= product.low_stock_level
    ]

    return low_stock_products


# ==========================================
# BUILD INVENTORY INSIGHTS
# ==========================================


def build_inventory_insights(
    products: Iterable[Product],
) -> InventoryInsights:
    """
    Build a structured summary of inventory data.

    Parameters:
        products (Iterable[Product]):
            Collection of Product objects.

    Returns:
        InventoryInsights:
            Dictionary containing inventory statistics,
            low-stock products, and recommendations.
    """

    # Convert the iterable to a reusable list.
    product_list: list[Product] = list(products)

    # Identify products requiring attention.
    low_stock_products: list[Product] = get_low_stock_products(product_list)

    # Calculate total inventory value.
    total_inventory_value: int = sum(
        product.price * product.quantity for product in product_list
    )

    # Calculate the total number of stock units.
    total_items: int = sum(product.quantity for product in product_list)

    # Build low-stock product summaries.
    low_stock_details: list[LowStockProductInfo] = [
        {
            "name": product.name,
            "quantity": product.quantity,
            "low_stock_level": product.low_stock_level,
        }
        for product in low_stock_products
    ]

    # Generate inventory recommendations.
    recommendations: list[InventoryRecommendation] = generate_inventory_recommendations(
        product_list
    )

    # Build the final structured response.
    insights: InventoryInsights = {
        "total_products": len(product_list),
        "total_items": total_items,
        "total_inventory_value": total_inventory_value,
        "low_stock_count": len(low_stock_products),
        "low_stock_products": low_stock_details,
        "recommendations": recommendations,
    }

    return insights


# ==========================================
# INVENTORY RECOMMENDATIONS
# ==========================================


def generate_inventory_recommendations(
    products: Iterable[Product],
) -> list[InventoryRecommendation]:
    """
    Generate explainable recommendations from inventory data.

    Parameters:
        products (Iterable[Product]):
            Collection of Product objects.

    Returns:
        list[InventoryRecommendation]:
            Inventory recommendations with explanations.
    """

    low_stock_products: list[Product] = get_low_stock_products(products)

    recommendations: list[InventoryRecommendation] = [
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

    return recommendations
