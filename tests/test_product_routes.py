from models import Product, StockMovement

def test_home_page(client):

    test_client, db = client

    response = test_client.get("/")

    assert response.status_code == 200

def test_add_product(client):

    test_client, db = client

    response = test_client.post(

        "/add-product",

        data={

            "name": "Laptop",

            "price": "100000",

            "quantity": "10",

            "low_stock_level": "5",

            "category": "Electronics",

            "supplier": "ABC Electronics",

        },

        follow_redirects=False,

    )

    assert response.status_code == 303

    assert response.headers["location"] == "/"

    product = db.query(Product).filter(

        Product.name == "Laptop"

    ).first()

    assert product is not None

    assert product.price == 100000

    assert product.quantity == 10

    assert product.low_stock_level == 5

    assert product.category == "Electronics"

    assert product.supplier == "ABC Electronics"

def test_add_duplicate_product(client):

    test_client, db = client

    # Create the first product

    first_response = test_client.post(

        "/add-product",

        data={

            "name": "Laptop",

            "price": "100000",

            "quantity": "10",

            "low_stock_level": "5",

            "category": "Electronics",

            "supplier": "ABC Electronics",

        },

        follow_redirects=False,

    )

    assert first_response.status_code == 303

    # Try to create the same product again

    second_response = test_client.post(

        "/add-product",

        data={

            "name": "Laptop",

            "price": "120000",

            "quantity": "5",

            "low_stock_level": "2",

            "category": "Computers",

            "supplier": "XYZ Electronics",

        },

        follow_redirects=False,

    )

    assert second_response.status_code == 303

    assert (

        second_response.headers["location"]

        == "/?error=duplicate_product"

    )

    # Only one Laptop should exist

    products = db.query(Product).filter(

        Product.normalized_name == "laptop"

    ).all()

    assert len(products) == 1

def test_add_product_invalid_price(client):

    test_client, db = client

    response = test_client.post(

        "/add-product",

        data={

            "name": "Mouse",

            "price": "0",

            "quantity": "10",

            "low_stock_level": "5",

            "category": "Electronics",

            "supplier": "ABC Electronics",

        },

        follow_redirects=False,

    )

    assert response.status_code == 303

    assert (

        response.headers["location"]

        == "/?error=invalid_price"

    )

    product = db.query(Product).filter(

        Product.normalized_name == "mouse"

    ).first()

    assert product is None

def test_add_product_invalid_quantity(client):

    test_client, db = client

    response = test_client.post(

        "/add-product",

        data={

            "name": "Keyboard",

            "price": "5000",

            "quantity": "-1",

            "low_stock_level": "5",

            "category": "Electronics",

            "supplier": "ABC Electronics",

        },

        follow_redirects=False,

    )

    assert response.status_code == 303

    assert (

        response.headers["location"]

        == "/?error=invalid_quantity"

    )

    product = db.query(Product).filter(

        Product.normalized_name == "keyboard"

    ).first()

    assert product is None

def test_edit_product(client):

    test_client, db = client

    # Create a product first

    product = Product(

        name="Laptop",

        normalized_name="laptop",

        price=100000,

        quantity=10,

        low_stock_level=5,

        category="Electronics",

        supplier="ABC Electronics",

    )

    db.add(product)

    db.commit()

    db.refresh(product)

    response = test_client.post(

        f"/edit-product/{product.id}",

        data={

            "name": "Gaming Laptop",

            "price": "150000",

            "low_stock_level": "3",

            "category": "Computers",

            "supplier": "XYZ Electronics",

        },

        follow_redirects=False,

    )

    assert response.status_code == 303

    assert response.headers["location"] == "/"

    db.refresh(product)

    assert product.name == "Gaming Laptop"

    assert product.normalized_name == "gaming laptop"

    assert product.price == 150000

    assert product.quantity == 10

    assert product.low_stock_level == 3

    assert product.category == "Computers"

    assert product.supplier == "XYZ Electronics"

def test_edit_product_not_found(client):

    test_client, db = client

    response = test_client.post(

        "/edit-product/9999",

        data={

            "name": "Laptop",

            "price": "100000",

            "low_stock_level": "5",

            "category": "Electronics",

            "supplier": "ABC Electronics",

        },

        follow_redirects=False,

    )

    assert response.status_code == 303

    assert (

        response.headers["location"]

        == "/edit-product/9999?error=product_not_found"

    )

def test_delete_product(client):
    test_client, db = client
    product = Product(
        name="Laptop", normalized_name="laptop", price=100000,
        quantity=10, low_stock_level=5, category="Electronics",
        supplier="ABC Electronics",
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    product_id = product.id

    response = test_client.post(
        f"/delete-product/{product_id}", follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert db.query(Product).filter(Product.id == product_id).first() is None

def test_dashboard_displays_products(client):

    test_client, db = client

    product = Product(

        name="Laptop",

        normalized_name="laptop",

        price=100000,

        quantity=10,

        low_stock_level=5,

        category="Electronics",

        supplier="ABC Electronics",

    )

    db.add(product)

    db.commit()

    response = test_client.get("/")

    assert response.status_code == 200

    assert "Laptop" in response.text

    assert "Electronics" in response.text

    assert "ABC Electronics" in response.text

def test_dashboard_search(client):

    test_client, db = client

    laptop = Product(

        name="Laptop",

        normalized_name="laptop",

        price=100000,

        quantity=10,

        low_stock_level=5,

        category="Electronics",

        supplier="ABC Electronics",

    )

    keyboard = Product(

        name="Keyboard",

        normalized_name="keyboard",

        price=5000,

        quantity=20,

        low_stock_level=5,

        category="Electronics",

        supplier="XYZ Electronics",

    )

    db.add_all([laptop, keyboard])

    db.commit()

    response = test_client.get(

        "/?search=laptop"

    )

    assert response.status_code == 200

    assert "Laptop" in response.text

    assert "Keyboard" not in response.text

def test_dashboard_search_not_found(client):

    test_client, db = client

    product = Product(

        name="Laptop",

        normalized_name="laptop",

        price=100000,

        quantity=10,

        low_stock_level=5,

        category="Electronics",

        supplier="ABC Electronics",

    )

    db.add(product)

    db.commit()

    response = test_client.get(

        "/?search=phone"

    )

    assert response.status_code == 200

    assert "Laptop" not in response.text

    assert "search not found" in response.text.lower()

def test_dashboard_statistics(client):
    test_client, db = client
    laptop = Product(
        name="Laptop", normalized_name="laptop", price=100000,
        quantity=10, low_stock_level=5, category="Electronics",
        supplier="ABC Electronics",
    )
    mouse = Product(
        name="Mouse", normalized_name="mouse", price=2000,
        quantity=3, low_stock_level=5, category="Electronics",
        supplier="XYZ Electronics",
    )
    chair = Product(
        name="Office Chair", normalized_name="office chair", price=50000,
        quantity=8, low_stock_level=2, category="Furniture",
        supplier="Office Supplies Ltd",
    )
    db.add_all([laptop, mouse, chair])
    db.commit()
    response = test_client.get("/")
    assert response.status_code == 200
    assert "3" in response.text
    assert "21" in response.text
    assert "2" in response.text
    assert "1" in response.text

def test_dashboard_displays_stock_movement(client):

    test_client, db = client

    product = Product(

        name="Laptop",

        normalized_name="laptop",

        price=100000,

        quantity=10,

        low_stock_level=5,

        category="Electronics",

        supplier="ABC Electronics",

    )

    db.add(product)

    db.commit()

    db.refresh(product)

    response = test_client.post(

        f"/stock-movement/{product.id}",

        data={

            "movement_type": "IN",

            "quantity": "5",

            "note": "New shipment received",

        },

        follow_redirects=False,

    )

    assert response.status_code == 303

    dashboard_response = test_client.get("/")

    assert dashboard_response.status_code == 200

    assert "Laptop" in dashboard_response.text

    assert "Stock In" in dashboard_response.text

    assert "5" in dashboard_response.text

    assert "New shipment received" in dashboard_response.text

def test_delete_product_deletes_stock_movements(client):

    test_client, db = client

    product = Product(

        name="Laptop",

        normalized_name="laptop",

        price=100000,

        quantity=10,

        low_stock_level=5,

        category="Electronics",

        supplier="ABC Electronics",

    )

    db.add(product)

    db.commit()

    db.refresh(product)

    response = test_client.post(

        f"/stock-movement/{product.id}",

        data={

            "movement_type": "IN",

            "quantity": "5",

            "note": "New shipment",

        },

        follow_redirects=False,

    )

    assert response.status_code == 303

    movement_count = db.query(StockMovement).filter(

        StockMovement.product_id == product.id

    ).count()

    assert movement_count == 1

    product_id = product.id

    response = test_client.post(

        f"/delete-product/{product_id}",

        follow_redirects=False,

    )

    assert response.status_code == 303

    assert response.headers["location"] == "/"

    deleted_product = db.query(Product).filter(

        Product.id == product_id

    ).first()

    assert deleted_product is None

    remaining_movements = db.query(

        StockMovement

    ).filter(

        StockMovement.product_id == product_id

    ).count()

    assert remaining_movements == 0

def test_delete_product_get_not_allowed(client):
    test_client, db = client
    product = Product(
        name="Monitor", normalized_name="monitor", price=50000,
        quantity=5, low_stock_level=2, category="Electronics",
        supplier="ABC Electronics",
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    product_id = product.id

    response = test_client.get(
        f"/delete-product/{product_id}", follow_redirects=False,
    )
    assert response.status_code == 405
    assert db.query(Product).filter(Product.id == product_id).first() is not None