
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, relationship

from database import Base


# ==========================================
# PRODUCT MODEL
# ==========================================

class Product(Base):
    """
    Represent a product stored in inventory.

    Python data types:
        id: int
        name: str
        normalized_name: str
        price: int
        quantity: int
        low_stock_level: int
        category: str
        supplier: str | None
        stock_movements: list[StockMovement]
    """

    __tablename__ = "products"

    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = Column(
        String,
        nullable=False,
    )

    normalized_name: Mapped[str] = Column(
        String,
        nullable=False,
        unique=True,
    )

    price: Mapped[int] = Column(
        Integer,
        nullable=False,
    )

    quantity: Mapped[int] = Column(
        Integer,
        nullable=False,
    )

    low_stock_level: Mapped[int] = Column(
        Integer,
        nullable=False,
    )

    category: Mapped[str] = Column(
        String,
        nullable=False,
    )

    supplier: Mapped[str | None] = Column(
        String,
        nullable=True,
    )

    stock_movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="product",
        cascade="all, delete-orphan",
    )


# ==========================================
# STOCK MOVEMENT MODEL
# ==========================================

class StockMovement(Base):
    """
    Represent a stock-in or stock-out transaction.

    Python data types:
        id: int
        product_id: int
        movement_type: str
        quantity: int
        note: str | None
        created_at: datetime
        product: Product
    """

    __tablename__ = "stock_movements"

    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    product_id: Mapped[int] = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )

    movement_type: Mapped[str] = Column(
        String,
        nullable=False,
    )

    quantity: Mapped[int] = Column(
        Integer,
        nullable=False,
    )

    note: Mapped[str | None] = Column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="stock_movements",
    )


# ==========================================
# AI ANALYSIS MODEL
# ==========================================

class AIAnalysis(Base):
    """
    Store historical AI inventory analyses.

    Python data types:
        id: int
        inventory_snapshot: str
        analysis: str
        created_at: datetime
    """

    __tablename__ = "ai_analyses"

    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    inventory_snapshot: Mapped[str] = Column(
        Text,
        nullable=False,
    )

    analysis: Mapped[str] = Column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )