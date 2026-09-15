from services.product_service import (
    create_product,
    update_product,
    validate_product,
)


def test_invalid_price():
    result = validate_product(
        "Laptop",
        -100,
        5,
        "Electronics",
    )

    assert result == "invalid_price"


def test_name_required():
    result = validate_product(
        "",
        100000,
        5,
        "Electronics",
    )

    assert result == "name_required"


def test_invalid_low_stock():
    result = validate_product(
        "Laptop",
        100000,
        -1,
        "Electronics",
    )

    assert result == "invalid_low_stock"


def test_category_required():
    result = validate_product(
        "Laptop",
        100000,
        5,
        "",
    )

    assert result == "category_required"


def test_create_product(db_session):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    assert product.name == "Laptop"
    assert product.normalized_name == "laptop"
    assert product.price == 100000
    assert product.quantity == 10
    assert product.low_stock_level == 5
    assert product.category == "Electronics"
    assert product.supplier == "ABC Electronics"


def test_duplicate_product(db_session):
    first_product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    assert first_product.name == "Laptop"

    result = create_product(
        db_session,
        "laptop",
        120000,
        5,
        2,
        "Computers",
        "XYZ Electronics",
    )

    assert result == "duplicate_product"


def test_product_name_normalization(db_session):
    first_product = create_product(
        db_session,
        "  Laptop  ",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    assert first_product.name == "Laptop"
    assert first_product.normalized_name == "laptop"

    result = create_product(
        db_session,
        "LAPTOP",
        120000,
        5,
        2,
        "Computers",
        "XYZ Electronics",
    )

    assert result == "duplicate_product"


def test_update_product(db_session):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = update_product(
        db_session,
        product.id,
        "Gaming Laptop",
        150000,
        3,
        "Computers",
        "XYZ Electronics",
    )

    assert result.name == "Gaming Laptop"
    assert result.normalized_name == "gaming laptop"
    assert result.price == 150000
    assert result.quantity == 10
    assert result.low_stock_level == 3
    assert result.category == "Computers"
    assert result.supplier == "XYZ Electronics"


def test_update_product_duplicate_name(db_session):
    first_product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    second_product = create_product(
        db_session,
        "Keyboard",
        20000,
        20,
        5,
        "Electronics",
        "XYZ Electronics",
    )

    result = update_product(
        db_session,
        second_product.id,
        "Laptop",
        25000,
        3,
        "Computers",
        "ABC Electronics",
    )

    assert result == "duplicate_product"


def test_update_product_same_name(db_session):
    product = create_product(
        db_session,
        "Laptop",
        100000,
        10,
        5,
        "Electronics",
        "ABC Electronics",
    )

    result = update_product(
        db_session,
        product.id,
        "  LAPTOP  ",
        120000,
        3,
        "Computers",
        "XYZ Electronics",
    )

    assert result.name == "LAPTOP"
    assert result.normalized_name == "laptop"
    assert result.price == 120000
    assert result.quantity == 10
    assert result.low_stock_level == 3
    assert result.category == "Computers"
    assert result.supplier == "XYZ Electronics"


def test_update_product_not_found(db_session):
    result = update_product(
        db_session,
        999,
        "Laptop",
        100000,
        5,
        "Electronics",
        "ABC Electronics",
    )

    assert result == "product_not_found"