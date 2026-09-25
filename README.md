# Inventory Management System

A full-stack inventory management application built with **Python, FastAPI, SQLAlchemy, PostgreSQL, Jinja2, HTML, and CSS**.

The system manages products, tracks stock movements, monitors low-stock levels, provides inventory dashboard statistics, supports inventory and stock-movement CSV exports, and exposes a secure REST API for programmatic access.

---

## Live Application

The application is deployed on Render:

https://inventory-management-system-ycyy.onrender.com

Interactive Swagger API documentation:

https://inventory-management-system-ycyy.onrender.com/docs

---

## Features

### Inventory Management

- Add new products
- Edit existing products
- Delete products
- Search products
- Product categories
- Supplier information
- Configurable low-stock level for each product
- Duplicate product-name protection
- Product validation
- Case-insensitive product-name handling
- REST API pagination
- REST API product filtering
- REST API low-stock filtering
- REST API product sorting

### Stock Management

- Record stock-in transactions
- Record stock-out transactions
- Prevent stock from going below zero
- Track stock movement history
- Store movement notes
- Record movement date and time
- View movement history for individual products
- Paginate individual product stock-movement history
- Filter stock movement history by start date and end date

### Reporting and Export

- View aggregate inventory summary statistics through the REST API
- Export the current product inventory as CSV
- Export stock-movement history as CSV
- Filter stock-movement CSV exports by start date and end date
- Download report data through the REST API
- Protect report exports with bearer-token authentication
- Export inventory with deterministic product-ID ordering
- Export stock movements from newest to oldest
- Return valid CSV headers even when report results are empty

### Dashboard

The browser dashboard provides inventory statistics including:

- Total products
- Total inventory items
- Total categories
- Low-stock products
- Product inventory table
- Product search
- Stock movement history

---

## REST API

The application includes a token-secured REST API for programmatic inventory management.

### Product Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/products/` | List products with pagination, search, category filtering, low-stock filtering, and sorting |
| POST | `/api/products/` | Create a product |
| GET | `/api/products/{product_id}` | Get a product |
| PUT | `/api/products/{product_id}` | Update a product |
| DELETE | `/api/products/{product_id}` | Delete a product |
| GET | `/api/products/{product_id}/stock-movements` | Get a product's paginated stock movement history |

### Product Pagination

The product-list endpoint supports server-side pagination:

```text
GET /api/products/?page=1&page_size=10
```

Pagination parameters:

| Parameter | Default | Validation | Description |
| --- | ---: | --- | --- |
| `page` | `1` | Minimum `1` | Page number to retrieve |
| `page_size` | `10` | Minimum `1`, maximum `100` | Number of products per page |

Example response:

```json
{
  "items": [
    {
      "id": 1,
      "name": "Laptop",
      "price": 200000,
      "quantity": 10,
      "low_stock_level": 3,
      "category": "Electronics",
      "supplier": "Example Supplier"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total_items": 1,
  "total_pages": 1
}
```

The response includes the requested page, page size, total number of matching products, and total number of pages.

When no explicit sorting field is supplied, products are returned in ascending product-ID order to provide deterministic pagination.

### Product Filtering

The product-list endpoint supports optional server-side filtering by product name and category.

Search for products by name:

```text
GET /api/products/?search=laptop
```

The `search` parameter performs a case-insensitive partial match on the product name.

For example:

```text
search=laptop
```

can match product names such as:

```text
Laptop
Gaming Laptop
Laptop Stand
```

Filter products by category:

```text
GET /api/products/?category=Electronics
```

Category matching is case-insensitive and uses an exact category match.

The filters can be combined:

```text
GET /api/products/?search=laptop&category=Electronics
```

Filtering can also be combined with pagination:

```text
GET /api/products/?search=laptop&category=Electronics&page=1&page_size=10
```

Filtering is applied **before pagination**. Therefore, `total_items` and `total_pages` describe the filtered result set rather than all products in the database.

Filtering parameters:

| Parameter | Required | Description |
| --- | --- | --- |
| `search` | No | Case-insensitive partial match on product name |
| `category` | No | Case-insensitive exact match on product category |

If no products match the filters, the API returns HTTP `200 OK` with an empty `items` list and zero result totals.

Example:

```json
{
  "items": [],
  "page": 1,
  "page_size": 10,
  "total_items": 0,
  "total_pages": 0
}
```

### Low-Stock Filtering

The product-list endpoint supports filtering products by their stock status using the `low_stock` query parameter.

A product is considered **low stock** when:

```text
quantity <= low_stock_level
```

Retrieve only low-stock products:

```text
GET /api/products/?low_stock=true
```

When `low_stock=true`, the API returns only products whose current quantity is less than or equal to their configured low-stock level.

For example:

```text
Product A: quantity = 2, low_stock_level = 3 → low stock
Product B: quantity = 5, low_stock_level = 5 → low stock
Product C: quantity = 10, low_stock_level = 5 → healthy stock
```

The equality boundary is intentional: a product whose quantity exactly equals its low-stock level is considered low stock.

Retrieve only products above their low-stock threshold:

```text
GET /api/products/?low_stock=false
```

When `low_stock=false`, the API returns products where:

```text
quantity > low_stock_level
```

If the `low_stock` parameter is omitted, no stock-status filter is applied.

| Value | Behavior |
| --- | --- |
| `low_stock=true` | Return products where `quantity <= low_stock_level` |
| `low_stock=false` | Return products where `quantity > low_stock_level` |
| Omitted | Do not filter by stock status |

Low-stock filtering can be combined with product search and category filtering:

```text
GET /api/products/?search=laptop&category=Computers&low_stock=true
```

It can also be combined with sorting:

```text
GET /api/products/?low_stock=true&sort_by=quantity&sort_order=asc
```

And with pagination:

```text
GET /api/products/?low_stock=true&page=1&page_size=10
```

All product-list query features can be combined in one request:

```text
GET /api/products/?search=laptop&category=Computers&low_stock=true&sort_by=price&sort_order=desc&page=1&page_size=10
```

The API applies the operations in this order:

1. Filter by product name when `search` is supplied.
2. Filter by category when `category` is supplied.
3. Filter by stock status when `low_stock` is supplied.
4. Sort the filtered products when `sort_by` is supplied.
5. Paginate the resulting products.

Therefore, `total_items` and `total_pages` represent the result set after all requested filters have been applied.

### Product Sorting

The product-list endpoint supports optional server-side sorting by product name, price, quantity, or category.

Sort products by name in ascending order:

```text
GET /api/products/?sort_by=name&sort_order=asc
```

Sort products by price in descending order:

```text
GET /api/products/?sort_by=price&sort_order=desc
```

Sorting parameters:

| Parameter | Default | Allowed Values | Description |
| --- | --- | --- | --- |
| `sort_by` | None | `name`, `price`, `quantity`, `category` | Product field used for sorting |
| `sort_order` | `asc` | `asc`, `desc` | Sort direction |

Name and category sorting are case-insensitive.

When products have the same value for the selected sorting field, product ID is used as a secondary ascending sort to keep the result order deterministic.

If `sort_by` is omitted, products retain the default ascending product-ID order.

Sorting can be combined with filtering:

```text
GET /api/products/?search=laptop&category=Electronics&sort_by=price&sort_order=desc
```

Sorting can also be combined with pagination:

```text
GET /api/products/?sort_by=quantity&sort_order=asc&page=1&page_size=10
```

Filtering, sorting, and pagination can be used together:

```text
GET /api/products/?search=laptop&category=Computers&sort_by=price&sort_order=desc&page=1&page_size=10
```

The API returns HTTP `422 Unprocessable Entity` when an unsupported `sort_by` or `sort_order` value is supplied.

### Product Stock Movement History Pagination

The stock-movement-history endpoint for an individual product supports server-side pagination:

```text
GET /api/products/{product_id}/stock-movements?page=1&page_size=10
```

Pagination parameters:

| Parameter | Default | Validation | Description |
| --- | ---: | --- | --- |
| `page` | `1` | Minimum `1` | Page number to retrieve |
| `page_size` | `10` | Minimum `1`, maximum `100` | Number of stock movements per page |

Stock movements are returned from newest to oldest. When two movements have the same timestamp, movement ID is used as a secondary descending sort to keep the order deterministic.

Example response:

```json
{
  "items": [
    {
      "id": 5,
      "product_id": 1,
      "movement_type": "IN",
      "quantity": 5,
      "note": "New shipment",
      "created_at": "2026-09-24T09:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total_items": 1,
  "total_pages": 1
}
```

The response includes:

- `items` — stock movements on the requested page
- `page` — requested page number
- `page_size` — requested page size
- `total_items` — total stock movements for the product
- `total_pages` — total number of available pages

A product with no stock-movement history returns HTTP `200 OK` with:

```json
{
  "items": [],
  "page": 1,
  "page_size": 10,
  "total_items": 0,
  "total_pages": 0
}
```

Requesting a valid page number beyond the available results also returns HTTP `200 OK` with an empty `items` list while preserving the correct `total_items` and `total_pages`.

For example:

```json
{
  "items": [],
  "page": 5,
  "page_size": 10,
  "total_items": 1,
  "total_pages": 1
}
```

Invalid pagination parameters are rejected automatically:

- `page` below `1` returns HTTP `422 Unprocessable Entity`.
- `page_size` below `1` or above `100` returns HTTP `422 Unprocessable Entity`.

A request for a product that does not exist returns HTTP `404 Not Found`.

### Stock Movement Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/stock-movements/` | List stock movements with optional date-range filtering |
| POST | `/api/stock-movements/{product_id}` | Create a stock movement |

### Stock Movement Date-Range Filtering

The stock-movement-list endpoint supports optional filtering by start date and end date.

Filter movements from a specific date onward:

```text
GET /api/stock-movements/?start_date=2026-09-01
```

Filter movements through a specific date:

```text
GET /api/stock-movements/?end_date=2026-09-30
```

Filter movements within a date range:

```text
GET /api/stock-movements/?start_date=2026-09-01&end_date=2026-09-30
```

Date-filtering parameters:

| Parameter | Required | Description |
| --- | --- | --- |
| `start_date` | No | Return stock movements on or after this date |
| `end_date` | No | Return stock movements on or before this date |

Dates use the `YYYY-MM-DD` format.

Both date boundaries are inclusive at the date level. For example, `end_date=2026-09-30` includes stock movements throughout September 30.

Either parameter can be used independently, or both can be supplied together.

If neither parameter is supplied, the endpoint returns the stock movement history without date filtering.

Stock movements remain ordered from newest to oldest.

If `start_date` is later than `end_date`, the API returns HTTP `422 Unprocessable Entity`.

Malformed date values are also rejected with HTTP `422 Unprocessable Entity`.

### Reporting Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/reports/summary` | Return aggregate inventory summary statistics |
| GET | `/api/reports/inventory.csv` | Export the current product inventory as CSV |
| GET | `/api/reports/stock-movements.csv` | Export stock-movement history as CSV with optional date-range filtering |

### Inventory Summary

The inventory summary endpoint returns aggregate statistics for the current inventory:

```text
GET /api/reports/summary
```

The endpoint is protected by bearer-token authentication.

The response contains:

- `total_products` — total number of products
- `total_items` — sum of the current quantities of all products
- `total_categories` — number of distinct product categories
- `low_stock_products` — number of products whose quantity is less than or equal to their configured low-stock level

Example response:

```json
{
  "total_products": 3,
  "total_items": 20,
  "total_categories": 2,
  "low_stock_products": 2
}
```

When the inventory contains no products, all four values are returned as `0`.

A valid API bearer token is required to access the report. Requests without valid authentication are rejected.

### Inventory CSV Export

The inventory report endpoint exports the current product inventory as a downloadable CSV file:

```text
GET /api/reports/inventory.csv
```

The endpoint is protected by bearer-token authentication.

The CSV contains the following columns:

| Column | Description |
| --- | --- |
| `id` | Product ID |
| `name` | Product name |
| `price` | Product price |
| `quantity` | Current quantity |
| `low_stock_level` | Configured low-stock threshold |
| `category` | Product category |
| `supplier` | Product supplier |

The internal `normalized_name` field is intentionally excluded from the export.

Products are exported in ascending product-ID order to provide deterministic output.

When a product has no supplier value, the supplier field is exported as an empty CSV value.

When the inventory contains no products, the endpoint still returns a valid CSV file containing the column headers and no product rows.

The response is returned with a CSV content type and a download header using the filename:

```text
inventory.csv
```

A valid API bearer token is required to access the report. Requests without valid authentication are rejected.

### Stock-Movement CSV Export

The stock-movement report endpoint exports stock-movement history as a downloadable CSV file:

```text
GET /api/reports/stock-movements.csv
```

The endpoint is protected by bearer-token authentication.

The CSV contains the following columns:

| Column | Description |
| --- | --- |
| `id` | Stock-movement ID |
| `product_id` | ID of the product associated with the movement |
| `movement_type` | Stock movement type, such as `IN` or `OUT` |
| `quantity` | Quantity involved in the stock movement |
| `note` | Optional stock-movement note |
| `created_at` | Date and time the stock movement was recorded |

When a stock movement has no note, the `note` field is exported as an empty CSV value.

Stock movements are exported from newest to oldest. When two movements have the same timestamp, movement ID is used as a secondary descending sort to keep the export order deterministic.

When no stock movements exist, the endpoint still returns a valid CSV file containing the column headers and no data rows.

The response is returned with a CSV content type and a download header using the filename:

```text
stock-movements.csv
```

The export supports optional `start_date` and `end_date` query parameters.

Export stock movements from a specific date onward:

```text
GET /api/reports/stock-movements.csv?start_date=2026-09-01
```

Export stock movements through a specific date:

```text
GET /api/reports/stock-movements.csv?end_date=2026-09-30
```

Export stock movements within a date range:

```text
GET /api/reports/stock-movements.csv?start_date=2026-09-01&end_date=2026-09-30
```

Date-filtering parameters:

| Parameter | Required | Description |
| --- | --- | --- |
| `start_date` | No | Export stock movements on or after this date |
| `end_date` | No | Export stock movements on or before this date |

Dates use the `YYYY-MM-DD` format.

Both date boundaries are inclusive at the date level. An `end_date` includes stock movements throughout the specified date.

Either date parameter can be used independently, or both can be supplied together.

If neither parameter is supplied, all stock movements are exported.

If `start_date` is later than `end_date`, the API returns HTTP `422 Unprocessable Entity`.

Malformed date values are also rejected with HTTP `422 Unprocessable Entity`.

A valid API bearer token is required to access the report. Requests without valid authentication are rejected.

### System Health

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Check application and database health |

The health endpoint verifies that the application is running and can successfully communicate with the database.

A healthy response returns:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

If the application cannot communicate with the database, the endpoint returns HTTP **503 Service Unavailable**.

The health endpoint is publicly accessible and does not require bearer-token authentication.

Interactive Swagger documentation is available at:

https://inventory-management-system-ycyy.onrender.com/docs

---

## API Authentication

REST API endpoints are protected using bearer-token authentication.

Clients must send the configured API token in the `Authorization` header:

```text
Authorization: Bearer YOUR_API_TOKEN
```

Example:

```bash
curl \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  "https://inventory-management-system-ycyy.onrender.com/api/products/?page=1&page_size=10"
```

The API token is stored in an environment variable and is not committed to the repository.

The `/health` endpoint is intentionally public so deployment and monitoring systems can check application availability without an API token.

---

## Browser Security

The browser interface includes several security protections:

- Administrator authentication
- Password hashing
- Session-based authentication
- Secure session configuration
- CSRF protection for browser forms
- Environment-based secret configuration
- Protected inventory-management routes
- Token-secured REST API endpoints
- Validation of user input
- Database constraints for product uniqueness

Sensitive credentials and application secrets are stored in environment variables rather than source code.

---

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy ORM
- Pydantic
- Uvicorn
- Alembic

### Frontend

- Jinja2 templates
- HTML5
- CSS3

### Database

- PostgreSQL
- Aiven PostgreSQL
- SQLite for isolated automated tests
- SQLAlchemy ORM
- Alembic database migrations

### Testing

- Pytest
- FastAPI TestClient
- HTTPX
- Isolated test database

### Deployment

- Render web service
- Aiven PostgreSQL
- GitHub

---

## Project Structure

```text
inventory-management-system/
│
├── alembic/
│   └── versions/
│
├── routers/
│   ├── api_products.py
│   ├── api_reports.py
│   ├── api_stock.py
│   ├── auth.py
│   ├── products.py
│   └── stock.py
│
├── services/
│   ├── error_messages.py
│   ├── inventory_service.py
│   └── product_service.py
│
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── edit_product.html
│   └── login.html
│
├── tests/
│   ├── conftest.py
│   ├── test_api_products.py
│   ├── test_api_reports.py
│   ├── test_api_security.py
│   ├── test_api_stock.py
│   ├── test_health.py
│   └── ...
│
├── alembic.ini
├── api_security.py
├── auth_config.py
├── auth_credentials.py
├── browser_security.py
├── database.py
├── main.py
├── models.py
├── requirements.txt
├── schemas.py
└── README.md
```

---

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/successjohnny/inventory-management-system.git
cd inventory-management-system
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

The application requires environment variables for database access and security.

Example names:

```text
DATABASE_URL
SESSION_SECRET_KEY
API_TOKEN
ADMIN_USERNAME
ADMIN_PASSWORD_HASH
SESSION_HTTPS_ONLY
```

Do not commit real credentials or secrets to Git.

For local development, configure appropriate development values in your environment.

### 5. Apply database migrations

```bash
alembic upgrade head
```

### 6. Start the application

```bash
uvicorn main:app --reload
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

Swagger documentation is available locally at:

```text
http://127.0.0.1:8000/docs
```

The health endpoint is available at:

```text
http://127.0.0.1:8000/health
```

---

## Running Tests

Run the complete automated test suite with:

```bash
pytest -v
```

The project currently contains **175 automated tests** covering areas including:

- Product creation
- Product retrieval
- Product updates
- Product deletion
- Duplicate-product validation
- Product pagination
- Product-name search
- Case-insensitive product search
- Category filtering
- Combined search and category filtering
- Filtering with pagination
- Empty filtered results
- Low-stock filtering
- Healthy-stock filtering
- Low-stock threshold boundary behavior
- Low-stock filtering combined with search and category filtering
- Low-stock filtering combined with sorting and pagination
- Product sorting by name
- Product sorting by price
- Product sorting by quantity
- Product sorting by category
- Ascending and descending sort order
- Invalid sorting-parameter validation
- Combined filtering, sorting, and pagination
- Stock-in operations
- Stock-out operations
- Insufficient-stock validation
- Stock movement history
- Stock movement start-date filtering
- Stock movement end-date filtering
- Combined stock movement date-range filtering
- Invalid stock movement date-range validation
- Invalid stock movement date-format validation
- Product stock-movement-history pagination
- Invalid stock-movement pagination validation
- Empty stock-movement history pagination
- Out-of-range stock-movement history pages
- Inventory CSV export
- Empty-inventory CSV export
- Inventory export authentication
- Stock-movement CSV export
- Empty stock-movement CSV export
- Stock-movement CSV start-date filtering
- Stock-movement CSV end-date filtering
- Invalid stock-movement CSV date-range validation
- Invalid stock-movement CSV date-format validation
- Stock-movement export authentication
- Inventory summary reporting
- Empty-inventory summary reporting
- Inventory summary authentication
- API authentication
- Browser authentication
- Security behavior
- Database behavior
- Application health checks
- Database health failure handling

The latest complete test run passed:

```text
175 passed, 1 warning
```

The current warning is associated with the Starlette/TestClient HTTPX compatibility layer and does not represent a failing test.

---

## Database Backups

Production PostgreSQL data is backed up using PostgreSQL backup tools.

The backup workflow:

1. Creates a PostgreSQL custom-format dump.
2. Verifies that the dump can be read.
3. Encrypts the backup.
4. Verifies the encrypted backup.
5. Keeps the backup credentials outside the repository.

Database credentials, encryption passphrases, and production secrets must never be committed to Git.

---

## Database Migrations

Database schema changes are managed using Alembic.

Apply all migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

Production migrations should be applied before the application begins serving requests that depend on new schema changes.

---

## API Documentation

FastAPI automatically generates interactive OpenAPI documentation.

Production Swagger UI:

https://inventory-management-system-ycyy.onrender.com/docs

The documentation includes:

- Product API endpoints
- Stock movement API endpoints
- Reporting API endpoints
- Inventory summary reporting
- Product pagination parameters and response schema
- Product search parameter
- Product category filter
- Product low-stock filter
- Product healthy-stock filter
- Product sorting parameters
- Ascending and descending product sorting
- Combined filtering, sorting, and pagination
- Product stock-movement-history pagination
- Stock-movement pagination parameters and response schema
- Stock movement start-date and end-date filtering
- Stock movement date-range validation
- Inventory CSV export
- Stock-movement CSV export
- Stock-movement CSV start-date and end-date filtering
- Stock-movement CSV date-range validation
- Request schemas
- Response schemas
- Validation rules
- Bearer-token authentication
- System health endpoint

API endpoints are organized into Swagger sections including:

- Products API
- Stock Movements API
- Reports API
- System

Browser-only routes are excluded from the public OpenAPI schema.

---

## Security

The project uses multiple security layers:

- Administrator login
- Hashed administrator password
- Session authentication
- Secure session secret
- CSRF protection
- Bearer-token REST API authentication
- Environment-based secrets
- HTTPS-only production sessions
- Input validation
- Product uniqueness enforcement
- Protected browser routes
- Protected report exports

Production secrets are configured through deployment environment variables and are not stored in the source repository.

---

## Health Monitoring

The application exposes:

```text
GET /health
```

This endpoint verifies both:

1. The FastAPI application is running.
2. The application can communicate with PostgreSQL.

Healthy response:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

If the database check fails, the application returns:

```text
503 Service Unavailable
```

This endpoint can be used by deployment platforms and external monitoring services to check application availability.

---

## Future Improvements

Possible future improvements include:

- Additional reporting formats and analytics
- Role-based user accounts
- Audit logging
- Automated backup scheduling
- Continuous integration with GitHub Actions
- AI-assisted inventory insights and forecasting

---

## Author

**John Ikwuobe**

AI-Native Full-Stack Developer · Software Engineer

GitHub: https://github.com/successjohnny

LinkedIn: https://linkedin.com/in/engr-john-ikwuobemnse-78a806b3