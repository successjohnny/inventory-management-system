from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Product


# ==========================================
# NORMALIZE PRODUCT NAME
# ==========================================


def normalize_product_name(name: str) -> str:
    """
    Remove leading/trailing spaces and
    convert a product name to lowercase.

    Parameters:
        name (str): Product name.

    Returns:
        str: Normalized product name.
    """

    normalized_name: str = name.strip().lower()

    return normalized_name


# ==========================================
# VALIDATE PRODUCT INFORMATION
# ==========================================


def validate_product(
    name: str,
    price: int,
    low_stock_level: int,
    category: str,
) -> str | None:
    """
    Validate product information.

    Parameters:
        name (str): Product name.
        price (int): Product price.
        low_stock_level (int): Low-stock threshold.
        category (str): Product category.

    Returns:
        str: Validation error code.
        None: All values are valid.
    """

    if not name.strip():
        return "name_required"

    if price <= 0:
        return "invalid_price"

    if low_stock_level < 0:
        return "invalid_low_stock"

    if not category.strip():
        return "category_required"

    return None


# ==========================================
# CREATE PRODUCT
# ==========================================


def create_product(
    db: Session,
    name: str,
    price: int,
    quantity: int,
    low_stock_level: int,
    category: str,
    supplier: str,
) -> Product | str:
    """
    Create a new inventory product.

    Parameters:
        db (Session): SQLAlchemy database session.
        name (str): Product name.
        price (int): Product price.
        quantity (int): Initial stock quantity.
        low_stock_level (int): Low-stock threshold.
        category (str): Product category.
        supplier (str): Product supplier.

    Returns:
        Product: Successfully created product.
        str: Error code if the product already exists.
    """

    name = name.strip()
    category = category.strip()
    supplier = supplier.strip()

    normalized_name: str = normalize_product_name(name)

    # Check for duplicate product names.
    existing_product: Product | None = (
        db.query(Product).filter(Product.normalized_name == normalized_name).first()
    )

    if existing_product is not None:
        return "duplicate_product"

    # Data type: Product
    product: Product = Product(
        name=name,
        normalized_name=normalized_name,
        price=price,
        quantity=quantity,
        low_stock_level=low_stock_level,
        category=category,
        supplier=supplier,
    )

    db.add(product)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()
        return "duplicate_product"

    db.refresh(product)

    return product


# ==========================================
# UPDATE PRODUCT
# ==========================================


def update_product(
    db: Session,
    product_id: int,
    name: str,
    price: int,
    low_stock_level: int,
    category: str,
    supplier: str,
) -> Product | str:
    """
    Update an existing product.

    Quantity is intentionally not changed here.
    Quantity is controlled by stock movements.

    Parameters:
        db (Session): SQLAlchemy database session.
        product_id (int): Product identifier.
        name (str): Updated product name.
        price (int): Updated product price.
        low_stock_level (int): Low-stock threshold.
        category (str): Updated product category.
        supplier (str): Updated supplier.

    Returns:
        Product: Successfully updated product.
        str: Error code if the update fails.
    """

    name = name.strip()
    category = category.strip()
    supplier = supplier.strip()

    normalized_name: str = normalize_product_name(name)

    # Find the existing product.
    product: Product | None = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        return "product_not_found"

    # Check for duplicate product names,
    # excluding the current product.
    existing_product: Product | None = (
        db.query(Product)
        .filter(
            Product.normalized_name == normalized_name,
            Product.id != product_id,
        )
        .first()
    )

    if existing_product is not None:
        return "duplicate_product"

    # Update product information.
    product.name = name
    product.normalized_name = normalized_name
    product.price = price
    product.low_stock_level = low_stock_level
    product.category = category
    product.supplier = supplier

    try:
        db.commit()

    except IntegrityError:
        db.rollback()
        return "duplicate_product"

    db.refresh(product)

    return product


# ==========================================
# DELETE PRODUCT
# ==========================================


def delete_product(
    db: Session,
    product_id: int,
) -> str | None:
    """
    Delete a product by its ID.

    Parameters:
        db (Session): SQLAlchemy database session.
        product_id (int): Product identifier.

    Returns:
        None: Product deleted successfully.
        str: Error code if the product does not exist.
    """

    product: Product | None = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        return "product_not_found"

    db.delete(product)
    db.commit()

    return None
