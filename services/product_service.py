from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Product


def normalize_product_name(name):
    """
    Remove leading/trailing spaces
    and convert the name to lowercase.
    """
    return name.strip().lower()


def validate_product(
    name,
    price,
    low_stock_level,
    category,
):
    """
    Validate product information.

    Returns an error code if validation fails.
    Returns None when all values are valid.
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


def create_product(
    db: Session,
    name,
    price,
    quantity,
    low_stock_level,
    category,
    supplier,
):
    """
    Create a new product.

    Returns:
        Product object when successful.
        Error code when the product already exists.
    """

    name = name.strip()
    category = category.strip()
    supplier = supplier.strip()

    normalized_name = normalize_product_name(name)

    # Check for duplicate product name
    existing_product = db.query(Product).filter(
        Product.normalized_name == normalized_name
    ).first()

    if existing_product:
        return "duplicate_product"

    product = Product(
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


def update_product(
    db: Session,
    product_id,
    name,
    price,
    low_stock_level,
    category,
    supplier,
):
    """
    Update an existing product.

    Quantity is intentionally not changed here.
    Quantity is controlled by stock movements.

    Returns:
        Product object when successful.
        Error code when the update fails.
    """

    name = name.strip()
    category = category.strip()
    supplier = supplier.strip()

    normalized_name = normalize_product_name(name)

    # Find the product
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        return "product_not_found"

    # Check for duplicate product name.
    # Exclude the current product.
    existing_product = db.query(Product).filter(
        Product.normalized_name == normalized_name,
        Product.id != product_id,
    ).first()

    if existing_product:
        return "duplicate_product"

    # Update product information
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