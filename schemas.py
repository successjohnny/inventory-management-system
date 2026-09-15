from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: int
    quantity: int
    low_stock_level: int
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