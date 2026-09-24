# Inventory Management System

A full-stack inventory management application built with **FastAPI, PostgreSQL, SQLAlchemy, Jinja2, and Alembic**.

The system provides a browser-based inventory dashboard together with a secured REST API for managing products and stock movements.

## Live Application

Production application:

https://inventory-management-system-ycyy.onrender.com

Interactive API documentation:

https://inventory-management-system-ycyy.onrender.com/docs

## Features

### Inventory Management

- Create inventory products
- Edit existing products
- Delete products
- Search products by name
- Organize products by category
- Record supplier information
- Configure individual low-stock thresholds
- Display low-stock status

### Stock Management

- Record stock-in transactions
- Record stock-out transactions
- Prevent stock-out when inventory is insufficient
- Maintain stock movement history
- Track movement date and time
- Add notes to stock movements

### Dashboard

The browser dashboard displays:

- Total products
- Total inventory items
- Total categories
- Low-stock products
- Product inventory
- Stock movement history

## REST API

The application includes a REST API for programmatic inventory management.

### Product Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/products/` | List products with pagination |
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

The response includes the requested page, page size, total number of products, and total number of pages.

Products are returned in ascending product-ID order to provide deterministic pagination.

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

## API Authentication

REST API endpoints are protected using **Bearer Token authentication**.

Example request:

```bash
curl \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  "https://inventory-management-system-ycyy.onrender.com/api/products/?page=1&page_size=10"
```

Never commit real API tokens or other credentials to the repository.

## Browser Security

The browser interface includes:

- Administrator authentication
- Password hashing
- Session-based authentication
- Secure session configuration
- CSRF protection for state-changing browser requests

The REST API uses separate bearer-token authentication.

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### Frontend

- HTML
- CSS
- Jinja2 Templates

### Database

- PostgreSQL
- Aiven PostgreSQL
- Alembic database migrations

### Testing

- Pytest
- FastAPI TestClient
- In-memory SQLite test database

### Deployment

- Render
- Aiven PostgreSQL

## Project Structure

```text
inventory-management-system/
├── alembic/
├── routers/
│   ├── api_products.py
│   ├── api_stock.py
│   ├── auth.py
│   ├── products.py
│   └── stock.py
├── services/
├── static/
├── templates/
├── tests/
│   ├── conftest.py
│   ├── test_api_config.py
│   ├── test_api_products.py
│   ├── test_api_security.py
│   ├── test_api_stock.py
│   ├── test_auth_credentials.py
│   ├── test_auth_routes.py
│   ├── test_browser_route_security.py
│   ├── test_browser_security.py
│   ├── test_health.py
│   ├── test_inventory_service.py
│   ├── test_product_routes.py
│   ├── test_product_service.py
│   └── test_stock_routes.py
├── alembic.ini
├── api_security.py
├── auth_config.py
├── auth_credentials.py
├── browser_security.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── requirements.txt
└── README.md
```

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/successjohnny/inventory-management-system.git
cd inventory-management-system
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

The application requires environment variables for database access and security.

Example:

```bash
export DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE"
export SESSION_SECRET_KEY="your-secret-session-key"
export API_TOKEN="your-api-token"
export ADMIN_USERNAME="your-admin-username"
export ADMIN_PASSWORD_HASH="your-password-hash"
```

Do not store real production credentials in the repository.

### 5. Apply database migrations

```bash
alembic upgrade head
```

### 6. Start the application

```bash
uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

## Running Tests

Run the complete automated test suite with:

```bash
pytest -v
```

The project currently contains **135 automated tests** covering application functionality, API behavior, pagination, authentication, security, inventory operations, and application/database health checks.

## Database Backups

Production PostgreSQL data is protected with a backup workflow that:

- Creates PostgreSQL database dumps
- Verifies backup integrity
- Encrypts backups using GPG AES-256
- Supports off-site backup storage

Credentials and encryption secrets are intentionally excluded from this repository.

## Database Migrations

Database schema changes are managed with Alembic.

Create a migration:

```bash
alembic revision --autogenerate -m "migration description"
```

Apply migrations:

```bash
alembic upgrade head
```

## API Documentation

FastAPI automatically generates OpenAPI documentation for the REST API.

Swagger UI:

```text
/docs
```

OpenAPI schema:

```text
/openapi.json
```

The API documentation includes:

- System health monitoring
- Product management endpoints
- Product pagination parameters and response schema
- Stock movement endpoints
- Request and response schemas
- Bearer-token authentication for protected API endpoints

Browser-only dashboard routes are excluded from the OpenAPI schema so the documentation remains focused on the REST API.

## Security

Security measures implemented in the project include:

- Hashed administrator passwords
- Session authentication
- CSRF protection
- Bearer-token API authentication
- Environment-based secret management
- HTTPS-only production session cookies
- Input validation
- Protected state-changing operations
- Encrypted database backups

Production secrets are stored outside the source code and are not committed to Git.

## Health Monitoring

The application provides a database-aware health endpoint:

```text
GET /health
```

A successful response returns HTTP **200 OK**:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

The health check executes a lightweight database query to verify that both the FastAPI application and its database connection are operational.

If the database cannot be reached, the endpoint returns HTTP **503 Service Unavailable** instead of reporting a false healthy state.

Production health endpoint:

https://inventory-management-system-ycyy.onrender.com/health

## Future Improvements

Possible future enhancements include:

- Role-based access control
- Multiple user accounts
- Advanced inventory reporting
- CSV/PDF report exports
- Dashboard charts
- Audit logging
- Automated scheduled backups
- AI-assisted inventory insights and forecasting

## Author

**John Ikwuobe**

AI-Native Full-Stack Developer & Software Engineer

GitHub: https://github.com/successjohnny

LinkedIn: https://linkedin.com/in/engr-john-ikwuobemnse-78a806b3

Portfolio: https://successjohnny.github.io/my-portfolio/