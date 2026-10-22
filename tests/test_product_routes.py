from models import Product, StockMovement


def test_home_page(authenticated_client):

    test_client, db = authenticated_client

    response = test_client.get("/")

    assert response.status_code == 200


def test_add_product(authenticated_client):

    test_client, db = authenticated_client

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

    product = db.query(Product).filter(Product.name == "Laptop").first()

    assert product is not None

    assert product.price == 100000

    assert product.quantity == 10

    assert product.low_stock_level == 5

    assert product.category == "Electronics"

    assert product.supplier == "ABC Electronics"


def test_add_duplicate_product(authenticated_client):

    test_client, db = authenticated_client

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

    assert second_response.headers["location"] == "/?error=duplicate_product"

    # Only one Laptop should exist

    products = db.query(Product).filter(Product.normalized_name == "laptop").all()

    assert len(products) == 1


def test_add_product_invalid_price(authenticated_client):

    test_client, db = authenticated_client

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

    assert response.headers["location"] == "/?error=invalid_price"

    product = db.query(Product).filter(Product.normalized_name == "mouse").first()

    assert product is None


def test_add_product_invalid_quantity(authenticated_client):

    test_client, db = authenticated_client

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

    assert response.headers["location"] == "/?error=invalid_quantity"

    product = db.query(Product).filter(Product.normalized_name == "keyboard").first()

    assert product is None


def test_edit_product(authenticated_client):

    test_client, db = authenticated_client

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


def test_edit_product_not_found(authenticated_client):

    test_client, db = authenticated_client

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

    assert response.headers["location"] == "/edit-product/9999?error=product_not_found"


def test_delete_product(authenticated_client):
    test_client, db = authenticated_client
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
    product_id = product.id

    response = test_client.post(
        f"/delete-product/{product_id}",
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert db.query(Product).filter(Product.id == product_id).first() is None


def test_dashboard_displays_products(authenticated_client):

    test_client, db = authenticated_client

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


def test_dashboard_search(authenticated_client):

    test_client, db = authenticated_client

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

    response = test_client.get("/?search=laptop")

    assert response.status_code == 200

    assert "Laptop" in response.text

    assert "Keyboard" not in response.text


def test_dashboard_search_not_found(authenticated_client):

    test_client, db = authenticated_client

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

    response = test_client.get("/?search=phone")

    assert response.status_code == 200

    assert "Laptop" not in response.text

    assert "search not found" in response.text.lower()


def test_dashboard_statistics(authenticated_client):
    test_client, db = authenticated_client
    laptop = Product(
        name="Laptop",
        normalized_name="laptop",
        price=100000,
        quantity=10,
        low_stock_level=5,
        category="Electronics",
        supplier="ABC Electronics",
    )
    mouse = Product(
        name="Mouse",
        normalized_name="mouse",
        price=2000,
        quantity=3,
        low_stock_level=5,
        category="Electronics",
        supplier="XYZ Electronics",
    )
    chair = Product(
        name="Office Chair",
        normalized_name="office chair",
        price=50000,
        quantity=8,
        low_stock_level=2,
        category="Furniture",
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


def test_dashboard_displays_stock_movement(authenticated_client):

    test_client, db = authenticated_client

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


def test_delete_product_deletes_stock_movements(authenticated_client):

    test_client, db = authenticated_client

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

    movement_count = (
        db.query(StockMovement).filter(StockMovement.product_id == product.id).count()
    )

    assert movement_count == 1

    product_id = product.id

    response = test_client.post(
        f"/delete-product/{product_id}",
        follow_redirects=False,
    )

    assert response.status_code == 303

    assert response.headers["location"] == "/"

    deleted_product = db.query(Product).filter(Product.id == product_id).first()

    assert deleted_product is None

    remaining_movements = (
        db.query(StockMovement).filter(StockMovement.product_id == product_id).count()
    )

    assert remaining_movements == 0


def test_delete_product_get_not_allowed(authenticated_client):
    test_client, db = authenticated_client
    product = Product(
        name="Monitor",
        normalized_name="monitor",
        price=50000,
        quantity=5,
        low_stock_level=2,
        category="Electronics",
        supplier="ABC Electronics",
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    product_id = product.id

    response = test_client.get(
        f"/delete-product/{product_id}",
        follow_redirects=False,
    )
    assert response.status_code == 405
    assert db.query(Product).filter(Product.id == product_id).first() is not None


def test_home_page_displays_category_valuations(
    authenticated_client,
):
    test_client, db = authenticated_client

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
            quantity=5,
            low_stock_level=2,
            category="Electronics",
            supplier="Supplier A",
        ),
        Product(
            name="Office Chair",
            normalized_name="office chair",
            price=50000,
            quantity=8,
            low_stock_level=2,
            category="Furniture",
            supplier="Supplier B",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get("/")

    assert response.status_code == 200

    assert "Category Inventory Valuation" in response.text
    assert "Electronics" in response.text
    assert "2025000" in response.text
    assert "Furniture" in response.text
    assert "400000" in response.text


def test_home_page_displays_empty_category_valuations(
    authenticated_client,
):
    test_client, _ = authenticated_client

    response = test_client.get("/")

    assert response.status_code == 200
    assert "Category Inventory Valuation" in response.text
    assert "No category valuation data available." in response.text


def test_home_page_displays_supplier_valuations(
    authenticated_client,
):
    test_client, db = authenticated_client

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
            quantity=5,
            low_stock_level=2,
            category="Electronics",
            supplier="Supplier A",
        ),
        Product(
            name="Office Chair",
            normalized_name="office chair",
            price=50000,
            quantity=8,
            low_stock_level=2,
            category="Furniture",
            supplier="Supplier B",
        ),
        Product(
            name="Keyboard",
            normalized_name="keyboard",
            price=10000,
            quantity=4,
            low_stock_level=2,
            category="Electronics",
            supplier=None,
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get("/")

    assert response.status_code == 200

    assert "Supplier Inventory Valuation" in response.text
    assert "Supplier A" in response.text
    assert "2025000" in response.text
    assert "Supplier B" in response.text
    assert "400000" in response.text


def test_home_page_excludes_products_without_supplier_from_supplier_valuations(
    authenticated_client,
):
    test_client, db = authenticated_client

    product = Product(
        name="Keyboard",
        normalized_name="keyboard",
        price=10000,
        quantity=4,
        low_stock_level=2,
        category="Electronics",
        supplier=None,
    )

    db.add(product)
    db.commit()

    response = test_client.get("/")

    assert response.status_code == 200
    assert "Supplier Inventory Valuation" in response.text
    assert "No supplier valuation data available." in response.text


def test_home_page_displays_low_stock_insights(
    authenticated_client,
):
    test_client, db = authenticated_client

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

    db.add_all(products)
    db.commit()

    response = test_client.get("/")

    assert response.status_code == 200

    assert "Low-Stock Insights" in response.text
    assert "Laptop" in response.text
    assert "Mouse" in response.text


def test_home_page_displays_empty_low_stock_insights(
    authenticated_client,
):
    test_client, db = authenticated_client

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

    response = test_client.get("/")

    assert response.status_code == 200
    assert "Low-Stock Insights" in response.text
    assert "No low-stock products." in response.text


def test_home_page_displays_category_valuation_chart(
    authenticated_client,
):
    test_client, db = authenticated_client

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
            name="Office Chair",
            normalized_name="office chair",
            price=50000,
            quantity=8,
            low_stock_level=2,
            category="Furniture",
            supplier="Supplier B",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get("/")

    assert response.status_code == 200
    assert "Inventory Value by Category" in response.text
    assert 'id="categoryValuationChart"' in response.text


def test_home_page_displays_supplier_valuation_chart(
    authenticated_client,
):
    test_client, db = authenticated_client

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
            name="Office Chair",
            normalized_name="office chair",
            price=50000,
            quantity=8,
            low_stock_level=2,
            category="Furniture",
            supplier="Supplier B",
        ),
    ]

    db.add_all(products)
    db.commit()

    response = test_client.get("/")

    assert response.status_code == 200
    assert "Inventory Value by Supplier" in response.text
    assert 'id="supplierValuationChart"' in response.text


def test_home_page_displays_low_stock_chart(
    authenticated_client,
):
    test_client, db = authenticated_client

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

    db.add_all(products)
    db.commit()

    response = test_client.get("/")

    assert response.status_code == 200
    assert "Low-Stock Overview" in response.text
    assert 'id="lowStockChart"' in response.text


def test_dashboard_displays_ai_analysis_history(
    authenticated_client,
):
    from datetime import datetime, timezone

    from models import AIAnalysis

    test_client, db = authenticated_client

    analysis = AIAnalysis(
        inventory_snapshot=('{"total_products": 1, "total_items": 2}'),
        analysis=("Inventory Health\nLaptop inventory requires attention."),
        created_at=datetime(
            2026,
            10,
            16,
            12,
            30,
            tzinfo=timezone.utc,
        ),
    )

    db.add(analysis)
    db.commit()

    response = test_client.get("/")

    assert response.status_code == 200
    assert "AI Analysis History" in response.text
    assert "Laptop inventory requires attention." in response.text


def test_dashboard_displays_empty_ai_analysis_history(
    authenticated_client,
):
    test_client, _ = authenticated_client

    response = test_client.get("/")

    assert response.status_code == 200
    assert "AI Analysis History" in response.text
    assert "No previous AI analyses available." in response.text


def test_dashboard_limits_ai_analysis_history_to_five(
    authenticated_client,
):
    from datetime import datetime, timedelta, timezone

    from models import AIAnalysis

    test_client, db = authenticated_client

    base_time = datetime(
        2026,
        10,
        16,
        12,
        0,
        tzinfo=timezone.utc,
    )

    analyses = []

    for number in range(1, 7):
        analyses.append(
            AIAnalysis(
                inventory_snapshot="{}",
                analysis=f"Analysis number {number}",
                created_at=(base_time + timedelta(minutes=number)),
            )
        )

    db.add_all(analyses)
    db.commit()

    response = test_client.get("/")

    assert response.status_code == 200

    assert "Analysis number 6" in response.text
    assert "Analysis number 5" in response.text
    assert "Analysis number 4" in response.text
    assert "Analysis number 3" in response.text
    assert "Analysis number 2" in response.text

    assert "Analysis number 1" not in response.text


def test_ai_analysis_detail_page_displays_saved_analysis(
    authenticated_client,
):
    from datetime import datetime, timezone

    from models import AIAnalysis

    test_client, db = authenticated_client

    analysis = AIAnalysis(
        inventory_snapshot=(
            '{"total_products": 1, "total_items": 2, "total_inventory_value": 1700000}'
        ),
        analysis=("## Inventory Health\n- Laptop inventory requires attention."),
        created_at=datetime(
            2026,
            10,
            16,
            12,
            30,
            tzinfo=timezone.utc,
        ),
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    response = test_client.get(f"/ai-analysis/{analysis.id}")

    assert response.status_code == 200
    assert "AI Analysis Details" in response.text
    assert "Laptop inventory requires attention." in response.text
    assert "Inventory Snapshot" in response.text
    assert "total_products" in response.text
    assert "1700000" in response.text


def test_ai_analysis_detail_requires_login(
    client,
):
    from models import AIAnalysis

    test_client, db = client

    analysis = AIAnalysis(
        inventory_snapshot="{}",
        analysis="Test analysis",
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    response = test_client.get(
        f"/ai-analysis/{analysis.id}",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_ai_analysis_detail_missing_record_redirects(
    authenticated_client,
):
    test_client, _ = authenticated_client

    response = test_client.get(
        "/ai-analysis/999999",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_dashboard_ai_history_has_details_link(
    authenticated_client,
):
    from models import AIAnalysis

    test_client, db = authenticated_client

    analysis = AIAnalysis(
        inventory_snapshot="{}",
        analysis="Saved inventory analysis",
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    response = test_client.get("/")

    assert response.status_code == 200
    assert f'href="/ai-analysis/{analysis.id}"' in response.text
    assert "View Details" in response.text
