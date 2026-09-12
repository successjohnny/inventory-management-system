from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
        unique=True,
    )

    price = Column(
        Integer,
        nullable=False,
    )

    quantity = Column(
        Integer,
        nullable=False,
    )

    low_stock_level = Column(
        Integer,
        nullable=False,
    )

    category = Column(
        String,
        nullable=False,
    )

    stock_movements = relationship(
        "StockMovement",
        back_populates="product",
        cascade="all, delete-orphan",
    )


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )

    movement_type = Column(
        String,
        nullable=False,
    )

    quantity = Column(
        Integer,
        nullable=False,
    )

    note = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    product = relationship(
        "Product",
        back_populates="stock_movements",
    )