from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str
    price: int = Field(gt=0)
    quantity: int = Field(ge=0)
    low_stock_level: int = Field(ge=0)
    category: str
    supplier: str | None = None


class ProductUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    name: str
    price: int = Field(gt=0)
    low_stock_level: int = Field(ge=0)
    category: str
    supplier: str | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    quantity: int
    low_stock_level: int
    category: str
    supplier: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int


class StockMovementCreate(BaseModel):
    movement_type: str
    quantity: int = Field(gt=0)
    note: str | None = None


class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: str
    quantity: int
    note: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )