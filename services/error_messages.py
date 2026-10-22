
from typing import Final


# ==========================================
# APPLICATION ERROR MESSAGES
# ==========================================

# Data type:
# Final[dict[str, str]]
#
# Dictionary keys are error codes (str).
# Dictionary values are error messages (str).
#
# Final prevents a static type checker from
# accepting reassignment of ERROR_MESSAGES.

ERROR_MESSAGES: Final[dict[str, str]] = {
    "name_required":
        "Please enter a product name.",

    "invalid_price":
        "Price must be greater than zero.",

    "invalid_quantity":
        "Quantity cannot be negative.",

    "invalid_low_stock":
        "Low stock level cannot be negative.",

    "category_required":
        "Please enter a product category.",

    "duplicate_product":
        "A product with this name already exists.",

    "product_not_found":
        "The requested product was not found.",

    "insufficient_stock":
        "Not enough stock available.",

    "invalid_movement_quantity":
        "Stock movement quantity must be greater than zero.",

    "invalid_movement_type":
        "Invalid stock movement type.",

    "stock_movement_failed":
        "The stock movement could not be completed. Please try again.",
}