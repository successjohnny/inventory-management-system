# Inventory Management System

A full-stack inventory management application built with **Python, FastAPI, SQLAlchemy, PostgreSQL, Jinja2, HTML, and CSS**.

The system manages products, tracks stock movements, monitors low-stock levels, provides inventory dashboard statistics, and exposes a secure REST API for programmatic access.

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

### Stock Management

- Record stock-in transactions
- Record stock-out transactions
- Prevent stock from going below zero
- Track stock movement history
- Store movement notes
- Record movement date and time
- View movement history for individual products

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
| GET | `/api/products/` | List products with pagination, search, category filtering, and sorting |
| POST | `/api/products/` | Create a product |
| GET | `/api/products/{product_id}` | Get a product |
| PUT | `/api/products/{product_id}` | Update a product |
| DELETE | `/api/products/{product_id}` | Delete a product |
| GET | `/api/products/{product_id}/stock-movements` | Get a product's stock movement history |

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

All three features can be used together:

```text
GET /api/products/?search=laptop&category=Computers&sort_by=price&sort_order=desc&page=1&page_size=10
```

When filtering, sorting, and pagination are combined, the API processes the request in this order:

1. Filter the matching products.
2. Sort the filtered products.
3. Paginate the sorted result.

The API returns HTTP `422 Unprocessable Entity` when an unsupported `sort_by` or `sort_order` value is supplied.

### Stock Movement Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/stock-movements/` | List stock movements |
| POST | `/api/stock-movements/{product_id}` | Create a stock movement |

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
│   ├── api_stock.py
│   ├── auth.py
│   ├── products.py
│   └── stock.py
│
├── services/
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
│   ├── test_api_security.py
│   ├── test_health.py
│   └── ...
│
├── alembic.ini
├── api_security.py
├── auth_config.py
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

The project currently contains **149 automated tests** covering areas including:

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
- API authentication
- Browser authentication
- Security behavior
- Database behavior
- Application health checks
- Database health failure handling

The latest complete test run passed:

```text
149 passed
```

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
- Product pagination parameters and response schema
- Product search parameter
- Product category filter
- Combined filtering and pagination
- Product sorting parameters
- Ascending and descending product sorting
- Combined filtering, sorting, and pagination
- Request schemas
- Response schemas
- Validation rules
- Bearer-token authentication
- System health endpoint

API endpoints are organized into Swagger sections including:

- Products API
- Stock Movements API
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

- Filtering products by low-stock status
- Pagination for stock movement history
- Date-range filtering for stock movements
- Inventory reporting and export
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