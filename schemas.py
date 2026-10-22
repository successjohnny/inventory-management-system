from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# PRODUCT CREATION SCHEMA
# ==========================================


class ProductCreate(BaseModel):
    """
    Validate data when creating a product.

    Data types:
        name: str
        price: int
        quantity: int
        low_stock_level: int
        category: str
        supplier: str | None
    """

    name: str
    price: int = Field(gt=0)
    quantity: int = Field(ge=0)
    low_stock_level: int = Field(ge=0)
    category: str
    supplier: str | None = None


# ==========================================
# PRODUCT UPDATE SCHEMA
# ==========================================


class ProductUpdate(BaseModel):
    """
    Validate data when updating a product.

    Data types:
        name: str
        price: int
        low_stock_level: int
        category: str
        supplier: str | None

    Extra fields are forbidden.

    Product quantity is intentionally excluded.
    Quantity changes must use stock movements.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    price: int = Field(gt=0)
    low_stock_level: int = Field(ge=0)
    category: str
    supplier: str | None = None


# ==========================================
# PRODUCT RESPONSE SCHEMA
# ==========================================


class ProductResponse(BaseModel):
    """
    Define the data returned for a product.

    Data types:
        id: int
        name: str
        price: int
        quantity: int
        low_stock_level: int
        category: str
        supplier: str | None
    """

    id: int
    name: str
    price: int
    quantity: int
    low_stock_level: int
    category: str
    supplier: str | None = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# PRODUCT LIST RESPONSE SCHEMA
# ==========================================


class ProductListResponse(BaseModel):
    """
    Define a paginated product response.

    Data types:
        items: list[ProductResponse]
        page: int
        page_size: int
        total_items: int
        total_pages: int
    """

    items: list[ProductResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int


# ==========================================
# STOCK MOVEMENT CREATION SCHEMA
# ==========================================


class StockMovementCreate(BaseModel):
    """
    Validate a stock-in or stock-out request.

    Data types:
        movement_type: str
        quantity: int
        note: str | None
    """

    movement_type: str
    quantity: int = Field(gt=0)
    note: str | None = None


# ==========================================
# STOCK MOVEMENT RESPONSE SCHEMA
# ==========================================


class StockMovementResponse(BaseModel):
    """
    Define the data returned for a stock movement.

    Data types:
        id: int
        product_id: int
        movement_type: str
        quantity: int
        note: str | None
        created_at: datetime
    """

    id: int
    product_id: int
    movement_type: str
    quantity: int
    note: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# STOCK MOVEMENT LIST RESPONSE SCHEMA
# ==========================================


class StockMovementListResponse(BaseModel):
    """
    Define a paginated stock movement response.

    Data types:
        items: list[StockMovementResponse]
        page: int
        page_size: int
        total_items: int
        total_pages: int
    """

    items: list[StockMovementResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int
