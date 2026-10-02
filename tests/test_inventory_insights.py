from models import Product
from services.inventory_insights import (
    build_inventory_insights,
    generate_inventory_recommendations,
    get_low_stock_products,
)


def test_get_low_stock_products_returns_products_at_or_below_threshold():
    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=200000,
            quantity=2,
            low_stock_level=3,
            category="Electronics",
            supplier="Supplier A",
        ),
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=5000,
            quantity=5,
            low_stock_level=5,
            category="Electronics",
            supplier="Supplier B",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=10000,
            quantity=10,
            low_stock_level=4,
            category="Electronics",
            supplier="Supplier C",
        ),
    ]

    low_stock_products = get_low_stock_products(products)

    assert [product.name for product in low_stock_products] == [
        "Laptop",
        "Mouse",
    ]


def test_get_low_stock_products_returns_empty_list_when_stock_is_healthy():
    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=200000,
            quantity=10,
            low_stock_level=3,
            category="Electronics",
            supplier="Supplier A",
        ),
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=5000,
            quantity=8,
            low_stock_level=5,
            category="Electronics",
            supplier="Supplier B",
        ),
    ]

    low_stock_products = get_low_stock_products(products)

    assert low_stock_products == []


def test_build_inventory_insights_returns_structured_summary():
    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=200000,
            quantity=2,
            low_stock_level=3,
            category="Electronics",
            supplier="Supplier A",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=10000,
            quantity=10,
            low_stock_level=4,
            category="Electronics",
            supplier="Supplier B",
        ),
    ]

    insights = build_inventory_insights(products)

    assert insights == {
        "total_products": 2,
        "total_items": 12,
        "total_inventory_value": 500000,
        "low_stock_count": 1,
        "low_stock_products": [
            {
                "name": "Laptop",
                "quantity": 2,
                "low_stock_level": 3,
            },
        ],
        "recommendations": [
            {
                "type": "low_stock",
                "product": "Laptop",
                "message": (
                    "Laptop is at or below its low-stock level. "
                    "Review this product for restocking."
                ),
            },
        ],
    }


def test_build_inventory_insights_handles_empty_inventory():
    insights = build_inventory_insights([])

    assert insights == {
        "total_products": 0,
        "total_items": 0,
        "total_inventory_value": 0,
        "low_stock_count": 0,
        "low_stock_products": [],
        "recommendations": [],
    }


def test_build_inventory_insights_calculates_total_inventory_value():
    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=200000,
            quantity=2,
            low_stock_level=3,
            category="Electronics",
            supplier="Supplier A",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=10000,
            quantity=10,
            low_stock_level=4,
            category="Electronics",
            supplier="Supplier B",
        ),
    ]

    insights = build_inventory_insights(products)

    assert insights["total_inventory_value"] == 500000


def test_build_inventory_insights_calculates_total_items():
    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=200000,
            quantity=2,
            low_stock_level=3,
            category="Electronics",
            supplier="Supplier A",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=10000,
            quantity=10,
            low_stock_level=4,
            category="Electronics",
            supplier="Supplier B",
        ),
    ]

    insights = build_inventory_insights(products)

    assert insights["total_items"] == 12


def test_generate_inventory_recommendations_flags_low_stock_product():
    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=200000,
            quantity=2,
            low_stock_level=3,
            category="Electronics",
            supplier="Supplier A",
        ),
    ]

    recommendations = generate_inventory_recommendations(products)

    assert recommendations == [
        {
            "type": "low_stock",
            "product": "Laptop",
            "message": (
                "Laptop is at or below its low-stock level. "
                "Review this product for restocking."
            ),
        },
    ]


def test_generate_inventory_recommendations_ignores_healthy_stock():
    products = [
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=10000,
            quantity=10,
            low_stock_level=4,
            category="Electronics",
            supplier="Supplier B",
        ),
    ]

    recommendations = generate_inventory_recommendations(products)

    assert recommendations == []


def test_build_inventory_insights_includes_recommendations():
    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=200000,
            quantity=2,
            low_stock_level=3,
            category="Electronics",
            supplier="Supplier A",
        ),
    ]

    insights = build_inventory_insights(products)

    assert insights["recommendations"] == [
        {
            "type": "low_stock",
            "product": "Laptop",
            "message": (
                "Laptop is at or below its low-stock level. "
                "Review this product for restocking."
            ),
        },
    ]
