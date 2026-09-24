from models import Product


def test_get_products(api_client):
    test_client, db = api_client

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=110,
        low_stock_level=5,
        category="Electronics",
        supplier="Merabgold Associates Services",
    )

    db.add(product)
    db.commit()

    response = test_client.get("/api/products/")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_items"] == 1
    assert data["total_pages"] == 1

    assert len(data["items"]) == 1

    item = data["items"][0]

    assert item["name"] == "Laptop"
    assert item["price"] == 200000
    assert item["quantity"] == 110

    assert "normalized_name" not in item


def test_get_products_pagination(api_client):
    test_client, db = api_client

    for number in range(1, 6):
        product = Product(
            name=f"Product {number}",
            normalized_name=f"product {number}",
            price=1000 * number,
            quantity=10 * number,
            low_stock_level=2,
            category="Test",
            supplier="Test Supplier",
        )

        db.add(product)

    db.commit()

    response = test_client.get(
        "/api/products/?page=2&page_size=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["page_size"] == 2
    assert data["total_items"] == 5
    assert data["total_pages"] == 3

    assert len(data["items"]) == 2

    assert data["items"][0]["name"] == "Product 3"
    assert data["items"][1]["name"] == "Product 4"

def test_get_products_search_by_name(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Gaming Laptop",
            normalized_name="gaming laptop",
            price=350000,
            quantity=10,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier A",
        ),
        Product(
            name="Laptop Stand",
            normalized_name="laptop stand",
            price=15000,
            quantity=20,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier B",
        ),
        Product(
            name="Wireless Mouse",
            normalized_name="wireless mouse",
            price=10000,
            quantity=30,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?search=laptop"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_items"] == 2
    assert data["total_pages"] == 1

    assert len(data["items"]) == 2

    assert data["items"][0]["name"] == "Gaming Laptop"
    assert data["items"][1]["name"] == "Laptop Stand"

def test_get_products_search_is_case_insensitive(api_client):
    test_client, db = api_client

    product = Product(
        name="Gaming Laptop",
        normalized_name="gaming laptop",
        price=350000,
        quantity=10,
        low_stock_level=3,
        category="Computers",
        supplier="Supplier A",
    )

    db.add(product)
    db.commit()

    response = test_client.get(
        "/api/products/?search=GAMING"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_items"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Gaming Laptop"

def test_get_products_filter_by_category(api_client):
    test_client, db = api_client

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
            name="Keyboard",
            normalized_name="keyboard",
            price=15000,
            quantity=20,
            low_stock_level=5,
            category="Electronics",
            supplier="Supplier B",
        ),
        Product(
            name="Office Chair",
            normalized_name="office chair",
            price=50000,
            quantity=8,
            low_stock_level=2,
            category="Furniture",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?category=ELECTRONICS"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_items"] == 2
    assert data["total_pages"] == 1

    assert len(data["items"]) == 2

    assert data["items"][0]["name"] == "Laptop"
    assert data["items"][1]["name"] == "Keyboard"

def test_get_products_combined_search_and_category(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Gaming Laptop",
            normalized_name="gaming laptop",
            price=350000,
            quantity=10,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier A",
        ),
        Product(
            name="Laptop Stand",
            normalized_name="laptop stand",
            price=15000,
            quantity=20,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier B",
        ),
        Product(
            name="Gaming Mouse",
            normalized_name="gaming mouse",
            price=12000,
            quantity=25,
            low_stock_level=5,
            category="Computers",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?search=gaming&category=computers"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_items"] == 2
    assert data["total_pages"] == 1
    assert len(data["items"]) == 2

    assert data["items"][0]["name"] == "Gaming Laptop"
    assert data["items"][1]["name"] == "Gaming Mouse"

def test_get_products_filter_no_matches(api_client):
    test_client, db = api_client

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=10,
        low_stock_level=3,
        category="Electronics",
        supplier="Supplier A",
    )

    db.add(product)
    db.commit()

    response = test_client.get(
        "/api/products/?search=projector"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_items"] == 0
    assert data["total_pages"] == 0

def test_get_products_filter_with_pagination(api_client):
    test_client, db = api_client

    for number in range(1, 6):
        product = Product(
            name=f"Laptop {number}",
            normalized_name=f"laptop {number}",
            price=100000 * number,
            quantity=10,
            low_stock_level=3,
            category="Computers",
            supplier="Test Supplier",
        )

        db.add(product)

    other_product = Product(
        name="Office Chair",
        normalized_name="office chair",
        price=50000,
        quantity=10,
        low_stock_level=2,
        category="Furniture",
        supplier="Test Supplier",
    )

    db.add(other_product)
    db.commit()

    response = test_client.get(
        "/api/products/"
        "?search=laptop"
        "&page=2"
        "&page_size=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["page_size"] == 2
    assert data["total_items"] == 5
    assert data["total_pages"] == 3

    assert len(data["items"]) == 2

    assert data["items"][0]["name"] == "Laptop 3"
    assert data["items"][1]["name"] == "Laptop 4"

def test_get_products_sort_by_name_ascending(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=10000,
            quantity=30,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier A",
        ),
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=350000,
            quantity=10,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier B",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=15000,
            quantity=20,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?sort_by=name&sort_order=asc"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_items"] == 3

    names = [
        item["name"]
        for item in data["items"]
    ]

    assert names == [
        "Keyboard",
        "Laptop",
        "Mouse",
    ]

def test_get_products_sort_by_name_descending(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=10000,
            quantity=30,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier A",
        ),
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=350000,
            quantity=10,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier B",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=15000,
            quantity=20,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?sort_by=name&sort_order=desc"
    )

    assert response.status_code == 200

    data = response.json()

    names = [
        item["name"]
        for item in data["items"]
    ]

    assert names == [
        "Mouse",
        "Laptop",
        "Keyboard",
    ]

def test_get_products_sort_by_price_ascending(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=350000,
            quantity=10,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier A",
        ),
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=10000,
            quantity=30,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier B",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=15000,
            quantity=20,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?sort_by=price&sort_order=asc"
    )

    assert response.status_code == 200

    data = response.json()

    prices = [
        item["price"]
        for item in data["items"]
    ]

    assert prices == [
        10000,
        15000,
        350000,
    ]

def test_get_products_sort_by_quantity_descending(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=350000,
            quantity=10,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier A",
        ),
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=10000,
            quantity=30,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier B",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=15000,
            quantity=20,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?sort_by=quantity&sort_order=desc"
    )

    assert response.status_code == 200

    data = response.json()

    quantities = [
        item["quantity"]
        for item in data["items"]
    ]

    assert quantities == [
        30,
        20,
        10,
    ]

def test_get_products_sort_by_category_ascending(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Office Chair",
            normalized_name="office chair",
            price=50000,
            quantity=8,
            low_stock_level=2,
            category="Furniture",
            supplier="Supplier A",
        ),
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=350000,
            quantity=10,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier B",
        ),
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=10000,
            quantity=30,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?sort_by=category&sort_order=asc"
    )

    assert response.status_code == 200

    data = response.json()

    categories = [
        item["category"]
        for item in data["items"]
    ]

    assert categories == [
        "Accessories",
        "Computers",
        "Furniture",
    ]

def test_get_products_rejects_invalid_sort_by(api_client):
    test_client, db = api_client

    response = test_client.get(
        "/api/products/?sort_by=supplier"
    )

    assert response.status_code == 422

def test_get_products_rejects_invalid_sort_order(api_client):
    test_client, db = api_client

    response = test_client.get(
        "/api/products/?sort_by=name&sort_order=random"
    )

    assert response.status_code == 422

def test_get_products_filter_sort_and_paginate(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Gaming Laptop",
            normalized_name="gaming laptop",
            price=350000,
            quantity=10,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier A",
        ),
        Product(
            name="Business Laptop",
            normalized_name="business laptop",
            price=250000,
            quantity=15,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier B",
        ),
        Product(
            name="Student Laptop",
            normalized_name="student laptop",
            price=180000,
            quantity=20,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier C",
        ),
        Product(
            name="Laptop Stand",
            normalized_name="laptop stand",
            price=15000,
            quantity=30,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier D",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/"
        "?search=laptop"
        "&category=computers"
        "&sort_by=price"
        "&sort_order=desc"
        "&page=2"
        "&page_size=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["page_size"] == 2
    assert data["total_items"] == 3
    assert data["total_pages"] == 2

    assert len(data["items"]) == 1

    assert data["items"][0]["name"] == "Student Laptop"
    assert data["items"][0]["price"] == 180000

def test_get_products_filter_by_low_stock(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=350000,
            quantity=2,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier A",
        ),
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=10000,
            quantity=10,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier B",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=15000,
            quantity=5,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?low_stock=true"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_items"] == 2

    names = [
        item["name"]
        for item in data["items"]
    ]

    assert names == [
        "Laptop",
        "Keyboard",
    ]

def test_get_products_low_stock_excludes_healthy_stock(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=350000,
            quantity=3,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier A",
        ),
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=10000,
            quantity=6,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier B",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?low_stock=true"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_items"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Laptop"

def test_get_products_low_stock_with_filter_sort_and_pagination(
    api_client,
):
    test_client, db = api_client

    products = [
        Product(
            name="Gaming Laptop",
            normalized_name="gaming laptop",
            price=350000,
            quantity=2,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier A",
        ),
        Product(
            name="Business Laptop",
            normalized_name="business laptop",
            price=250000,
            quantity=3,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier B",
        ),
        Product(
            name="Student Laptop",
            normalized_name="student laptop",
            price=180000,
            quantity=10,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier C",
        ),
        Product(
            name="Laptop Stand",
            normalized_name="laptop stand",
            price=15000,
            quantity=1,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier D",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/"
        "?search=laptop"
        "&category=computers"
        "&low_stock=true"
        "&sort_by=price"
        "&sort_order=desc"
        "&page=2"
        "&page_size=1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["page_size"] == 1
    assert data["total_items"] == 2
    assert data["total_pages"] == 2

    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Business Laptop"
    assert data["items"][0]["price"] == 250000

def test_get_products_filter_by_healthy_stock(api_client):
    test_client, db = api_client

    products = [
        Product(
            name="Laptop",
            normalized_name="laptop",
            price=350000,
            quantity=2,
            low_stock_level=3,
            category="Computers",
            supplier="Supplier A",
        ),
        Product(
            name="Mouse",
            normalized_name="mouse",
            price=10000,
            quantity=10,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier B",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=15000,
            quantity=5,
            low_stock_level=5,
            category="Accessories",
            supplier="Supplier C",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get(
        "/api/products/?low_stock=false"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_items"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Mouse"


def test_get_products_page_must_be_positive(api_client):
    test_client, db = api_client

    response = test_client.get(
        "/api/products/?page=0"
    )

    assert response.status_code == 422


def test_get_products_page_size_limit(api_client):
    test_client, db = api_client

    response = test_client.get(
        "/api/products/?page_size=101"
    )

    assert response.status_code == 422


def test_get_product_by_id(api_client):
    test_client, db = api_client

    product = Product(
        name="Laptop",
        normalized_name="laptop",
        price=200000,
        quantity=110,
        low_stock_level=5,
        category="Electronics",
        supplier="Merabgold Associates Services",
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    response = test_client.get(
        f"/api/products/{product.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product.id
    assert data["name"] == "Laptop"
    assert data["quantity"] == 110

    assert "normalized_name" not in data


def test_get_product_not_found(api_client):
    test_client, db = api_client

    response = test_client.get(
        "/api/products/999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found"


def test_create_product_api(api_client):
    test_client, db = api_client

    response = test_client.post(
        "/api/products/",
        json={
            "name": "Keyboard",
            "price": 2500,
            "quantity": 30,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "ABC Supplies",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Keyboard"
    assert data["price"] == 2500
    assert data["quantity"] == 30
    assert data["category"] == "Electronics"
    assert data["supplier"] == "ABC Supplies"

    assert "normalized_name" not in data


def test_create_duplicate_product_api(api_client):
    test_client, db = api_client

    first_response = test_client.post(
        "/api/products/",
        json={
            "name": "Keyboard",
            "price": 2500,
            "quantity": 30,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "ABC Supplies",
        },
    )

    assert first_response.status_code == 201

    second_response = test_client.post(
        "/api/products/",
        json={
            "name": "keyboard",
            "price": 3000,
            "quantity": 20,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "Another Supplier",
        },
    )

    assert second_response.status_code == 400

    data = second_response.json()

    assert data["detail"] == "duplicate_product"


def test_create_product_negative_price(api_client):
    test_client, db = api_client

    response = test_client.post(
        "/api/products/",
        json={
            "name": "Invalid Product",
            "price": -5000,
            "quantity": 10,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 422


def test_create_product_negative_quantity(api_client):
    test_client, db = api_client

    response = test_client.post(
        "/api/products/",
        json={
            "name": "Invalid Product",
            "price": 5000,
            "quantity": -10,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 422


def test_create_product_negative_low_stock_level(api_client):
    test_client, db = api_client

    response = test_client.post(
        "/api/products/",
        json={
            "name": "Invalid Product",
            "price": 5000,
            "quantity": 10,
            "low_stock_level": -5,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 422


def test_get_product_stock_movements(api_client):
    test_client, db = api_client

    # Create the first product.
    first_product = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
            "supplier": "Supplier A",
        },
    )

    assert first_product.status_code == 201

    first_product_id = first_product.json()["id"]

    # Create a second product.
    second_product = test_client.post(
        "/api/products/",
        json={
            "name": "Mouse",
            "price": 5000,
            "quantity": 20,
            "low_stock_level": 5,
            "category": "Electronics",
            "supplier": "Supplier B",
        },
    )

    assert second_product.status_code == 201

    second_product_id = second_product.json()["id"]

    # Record a movement for the first product.
    first_movement = test_client.post(
        f"/api/stock-movements/{first_product_id}",
        json={
            "movement_type": "IN",
            "quantity": 5,
            "note": "Laptop shipment",
        },
    )

    assert first_movement.status_code == 201

    # Record a movement for the second product.
    second_movement = test_client.post(
        f"/api/stock-movements/{second_product_id}",
        json={
            "movement_type": "OUT",
            "quantity": 3,
            "note": "Mouse sale",
        },
    )

    assert second_movement.status_code == 201

    # Retrieve only the first product's history.
    response = test_client.get(
        f"/api/products/{first_product_id}/stock-movements"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_items"] == 1
    assert data["total_pages"] == 1

    movements = data["items"]

    assert len(movements) == 1

    assert movements[0]["product_id"] == first_product_id
    assert movements[0]["movement_type"] == "IN"
    assert movements[0]["quantity"] == 5
    assert movements[0]["note"] == "Laptop shipment"


def test_get_product_stock_movements_empty(api_client):
    test_client, db = api_client

    response = test_client.post(
        "/api/products/",
        json={
            "name": "Keyboard",
            "price": 10000,
            "quantity": 15,
            "low_stock_level": 4,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 201

    product_id = response.json()["id"]

    history_response = test_client.get(
        f"/api/products/{product_id}/stock-movements"
    )

    assert history_response.status_code == 200

    data = history_response.json()

    assert data["items"] == []
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_items"] == 0
    assert data["total_pages"] == 0


def test_get_product_stock_movements_not_found(api_client):
    test_client, db = api_client

    response = test_client.get(
        "/api/products/9999/stock-movements"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Product not found"

def test_get_product_stock_movements_pagination(api_client):
    test_client, db = api_client

    product_response = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 20,
            "low_stock_level": 3,
            "category": "Electronics",
            "supplier": "Supplier A",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    for number in range(5):
        movement_response = test_client.post(
            f"/api/stock-movements/{product_id}",
            json={
                "movement_type": "IN",
                "quantity": 1,
                "note": f"Shipment {number + 1}",
            },
        )

        assert movement_response.status_code == 201

    response = test_client.get(
        f"/api/products/{product_id}/stock-movements"
        "?page=2&page_size=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["page_size"] == 2
    assert data["total_items"] == 5
    assert data["total_pages"] == 3
    assert len(data["items"]) == 2

def test_get_product_stock_movements_rejects_invalid_page(
    api_client,
):
    test_client, db = api_client

    product_response = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
            "supplier": "Supplier A",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    response = test_client.get(
        f"/api/products/{product_id}/stock-movements"
        "?page=0"
    )

    assert response.status_code == 422

def test_get_product_stock_movements_rejects_invalid_page_size(
    api_client,
):
    test_client, db = api_client

    product_response = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
            "supplier": "Supplier A",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    response = test_client.get(
        f"/api/products/{product_id}/stock-movements"
        "?page_size=101"
    )

    assert response.status_code == 422

def test_get_product_stock_movements_page_beyond_results(
    api_client,
):
    test_client, db = api_client

    product_response = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
            "supplier": "Supplier A",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    movement_response = test_client.post(
        f"/api/stock-movements/{product_id}",
        json={
            "movement_type": "IN",
            "quantity": 1,
            "note": "Test shipment",
        },
    )

    assert movement_response.status_code == 201

    response = test_client.get(
        f"/api/products/{product_id}/stock-movements"
        "?page=5&page_size=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["page"] == 5
    assert data["page_size"] == 10
    assert data["total_items"] == 1
    assert data["total_pages"] == 1


def test_update_product_api(api_client):
    test_client, db = api_client

    create_response = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
            "supplier": "Supplier A",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    response = test_client.put(
        f"/api/products/{product_id}",
        json={
            "name": "Gaming Laptop",
            "price": 350000,
            "low_stock_level": 5,
            "category": "Computers",
            "supplier": "Supplier B",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Gaming Laptop"
    assert data["price"] == 350000
    assert data["low_stock_level"] == 5
    assert data["category"] == "Computers"
    assert data["supplier"] == "Supplier B"

    # Product quantity must remain unchanged.
    assert data["quantity"] == 10


def test_update_product_not_found(api_client):
    test_client, db = api_client

    response = test_client.put(
        "/api/products/9999",
        json={
            "name": "Missing Product",
            "price": 5000,
            "low_stock_level": 2,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product_invalid_price(api_client):
    test_client, db = api_client

    response = test_client.put(
        "/api/products/9999",
        json={
            "name": "Invalid Product",
            "price": -5000,
            "low_stock_level": 2,
            "category": "Electronics",
            "supplier": "Test Supplier",
        },
    )

    assert response.status_code == 422


def test_update_product_duplicate_name(api_client):
    test_client, db = api_client

    first = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
        },
    )

    second = test_client.post(
        "/api/products/",
        json={
            "name": "Mouse",
            "price": 5000,
            "quantity": 20,
            "low_stock_level": 5,
            "category": "Electronics",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    second_id = second.json()["id"]

    response = test_client.put(
        f"/api/products/{second_id}",
        json={
            "name": "Laptop",
            "price": 6000,
            "low_stock_level": 5,
            "category": "Electronics",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "duplicate_product"


def test_delete_product_api(api_client):
    test_client, db = api_client

    create_response = test_client.post(
        "/api/products/",
        json={
            "name": "Laptop",
            "price": 200000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    delete_response = test_client.delete(
        f"/api/products/{product_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = test_client.get(
        f"/api/products/{product_id}"
    )

    assert get_response.status_code == 404


def test_delete_product_not_found(api_client):
    test_client, db = api_client

    response = test_client.delete(
        "/api/products/9999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_delete_product_removes_stock_movements(api_client):
    test_client, db = api_client

    create_response = test_client.post(
        "/api/products/",
        json={
            "name": "Keyboard",
            "price": 10000,
            "quantity": 10,
            "low_stock_level": 3,
            "category": "Electronics",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    movement_response = test_client.post(
        f"/api/stock-movements/{product_id}",
        json={
            "movement_type": "IN",
            "quantity": 5,
            "note": "New shipment",
        },
    )

    assert movement_response.status_code == 201

    delete_response = test_client.delete(
        f"/api/products/{product_id}"
    )

    assert delete_response.status_code == 204

    history_response = test_client.get(
        "/api/stock-movements/"
    )

    assert history_response.status_code == 200
    assert history_response.json() == []