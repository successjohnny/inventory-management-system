from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    price: int = Field(gt=0)
    quantity: int = Field(ge=0)
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

    model_config = {
        "from_attributes": True
    }


class StockMovementCreate(BaseModel):
    movement_type: str
    quantity: int = Field(gt=0)
    note: str | None = None