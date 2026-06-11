# Handmade Marketplace Backend

![Django Tests](https://github.com/Hozz1/marketplace/actions/workflows/tests.yml/badge.svg)

Backend API for a handmade products marketplace built with Django REST Framework.

The project demonstrates practical backend development skills: REST API design, JWT authentication, role-based permissions, PostgreSQL integration, service-layer business logic, cursor pagination, filtering, Swagger/OpenAPI documentation, Docker-based local development, and automated testing with GitHub Actions.

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* Simple JWT
* django-environ
* drf-spectacular
* Docker
* Docker Compose
* GitHub Actions
* DRF APITestCase / Django test framework

## Key Features

* User registration with role-based profiles.
* JWT authentication with access and refresh tokens.
* User roles:

  * buyer;
  * seller;
  * admin.
* Product catalog with categories.
* Product creation and management by sellers.
* Owner/admin permissions for product updates and deletion.
* Product search by title and description.
* Product filtering by category and price range.
* Product ordering by price and creation date.
* Cursor pagination for product listings.
* Order creation by buyers.
* Backend-side order total calculation.
* Automatic product stock reduction after order creation.
* Automatic product availability update when stock reaches zero.
* User-specific order visibility.
* Admin access to all orders.
* Swagger/OpenAPI documentation.
* Docker and Docker Compose setup.
* GitHub Actions CI pipeline.
* Automated API tests, including negative scenarios.

## Project Structure

```text
marketplace/
├── admin.py
├── apps.py
├── models.py
├── pagination.py
├── permissions.py
├── roles.py
├── serializers.py
├── services.py
├── urls.py
├── views.py
└── tests/
    ├── test_auth_api.py
    ├── test_products_api.py
    └── test_orders_api.py
```

## Architecture Overview

The project follows a layered structure:

* `models.py` — database models and relationships.
* `serializers.py` — input validation and JSON serialization.
* `permissions.py` — API access rules.
* `roles.py` — reusable role-checking helpers.
* `pagination.py` — cursor pagination configuration for products.
* `views.py` — HTTP request handling and API endpoints.
* `services.py` — business logic for order creation.
* `tests/` — automated API tests.

The order creation logic is intentionally moved into the service layer. This keeps the view layer focused on HTTP handling, while business rules such as stock validation, price calculation, database locking and order creation remain isolated and easier to test.

## Models

### UserProfile

Extends Django's default `User` model through a one-to-one relationship.

Fields:

* `user`
* `role`

Available roles:

* `buyer`
* `seller`
* `admin`

### Category

Represents a product category.

Fields:

* `name`
* `description`

### Product

Represents a marketplace product.

Fields:

* `title`
* `description`
* `price`
* `quantity`
* `image`
* `category`
* `seller`
* `created_at`
* `updated_at`
* `is_available`

### Order

Represents a customer order.

Fields:

* `buyer`
* `product`
* `quantity`
* `total_price`
* `status`
* `created_at`

## Permissions

| Action                          | Anonymous | Buyer | Seller | Admin |
| ------------------------------- | --------: | ----: | -----: | ----: |
| View categories                 |       Yes |   Yes |    Yes |   Yes |
| View products                   |       Yes |   Yes |    Yes |   Yes |
| Create product                  |        No |    No |    Yes |    No |
| Update own product              |        No |    No |    Yes |   Yes |
| Update another seller's product |        No |    No |     No |   Yes |
| Delete own product              |        No |    No |    Yes |   Yes |
| Create order                    |        No |   Yes |     No |    No |
| View own orders                 |        No |   Yes |    Yes |   Yes |
| View all orders                 |        No |    No |     No |   Yes |

## API Documentation

Swagger UI is available at:

```text
/api/docs/
```

OpenAPI schema:

```text
/api/schema/
```

ReDoc documentation:

```text
/api/redoc/
```

## API Endpoints

Base API prefix:

```text
/api/v1/
```

### Auth

```text
POST /api/v1/auth/register/
POST /api/v1/auth/token/
POST /api/v1/auth/token/refresh/
```

### Categories

```text
GET /api/v1/categories/
GET /api/v1/categories/{id}/
```

### Products

```text
GET    /api/v1/products/
POST   /api/v1/products/
GET    /api/v1/products/{id}/
PUT    /api/v1/products/{id}/
PATCH  /api/v1/products/{id}/
DELETE /api/v1/products/{id}/
```

Product list supports search, filtering, ordering and cursor pagination.

Available query parameters:

```text
search      — search by product title or description
category    — filter by category id
min_price   — minimum product price
max_price   — maximum product price
ordering    — price, -price, created_at, -created_at
page_size   — custom page size
cursor      — cursor for next or previous page
```

Examples:

```text
/api/v1/products/?search=mug
/api/v1/products/?category=1
/api/v1/products/?min_price=500&max_price=2000
/api/v1/products/?ordering=-price
/api/v1/products/?page_size=5
```

Paginated response example:

```json
{
  "next": "http://127.0.0.1:8000/api/v1/products/?cursor=...",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Ceramic mug",
      "description": "Handmade white clay mug.",
      "price": "1200.00",
      "quantity": 5,
      "category": 1,
      "category_name": "Ceramics",
      "seller": 2,
      "seller_username": "seller1",
      "is_available": true
    }
  ]
}
```

### Orders

```text
GET  /api/v1/orders/
POST /api/v1/orders/
GET  /api/v1/orders/{id}/
```

Regular users can see only their own orders. Admin users can see all orders.

## Environment Variables

The project uses environment variables for local configuration.

Create `.env` in the project root based on `.env.example`.

Example:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=postgres://your_db_user:your_db_password@localhost:5432/your_db_name
```

The `.env` file must not be committed to Git.

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create `.env`

Create a `.env` file in the project root and configure it using `.env.example`.

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

Application:

```text
http://127.0.0.1:8000/
```

API:

```text
http://127.0.0.1:8000/api/v1/
```

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

## Docker Setup

The project can also be launched with Docker Compose.

Docker Compose starts two services:

* `backend` — Django / DRF application;
* `db` — PostgreSQL database.

### 1. Create `.env.docker`

Create `.env.docker` in the project root based on `.env.docker.example`.

Example:

```env
SECRET_KEY=your-docker-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0

DATABASE_URL=postgres://marketplace_user:marketplace_password@db:5432/handmade_marketplace_db
```

In Docker, the database host is `db`, because PostgreSQL runs in a separate container with that service name.

The `.env.docker` file must not be committed to Git.

### 2. Build and run containers

```bash
docker compose up --build
```

### 3. Apply migrations inside the backend container

In a separate terminal:

```bash
docker compose exec backend python manage.py migrate
```

### 4. Create a superuser inside the Docker database

```bash
docker compose exec backend python manage.py createsuperuser
```

### 5. Run tests inside Docker

```bash
docker compose exec backend python manage.py test
```

### 6. Stop containers

```bash
docker compose down
```

### 7. Stop containers and remove Docker database volume

```bash
docker compose down -v
```

The `-v` flag removes the PostgreSQL volume. All data stored in the Docker database will be deleted.

## Useful Docker Commands

Check running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs
```

View backend logs:

```bash
docker compose logs backend
```

Enter the backend container:

```bash
docker compose exec backend sh
```

Rebuild the backend image:

```bash
docker compose build backend
```

## Running Tests

Run tests locally:

```bash
python manage.py test
```

Run tests inside Docker:

```bash
docker compose exec backend python manage.py test
```

The project currently includes 23 automated API tests.

Covered scenarios include:

* user registration;
* preventing public registration with the admin role;
* product creation by sellers;
* preventing product creation by buyers;
* preventing product creation with invalid price;
* preventing available products with zero stock;
* product update by owner;
* preventing product update by another seller;
* product search;
* product filtering by category;
* product filtering by price range;
* product ordering;
* order creation by buyers;
* backend-side `total_price` calculation;
* product stock reduction after order creation;
* automatic product unavailability when stock reaches zero;
* preventing orders above available stock;
* preventing orders with `quantity = 0`;
* preventing orders for unavailable products;
* preventing sellers from creating orders;
* showing users only their own orders;
* showing all orders to admins.

Tests are also executed automatically through GitHub Actions on push and pull request to the `main` branch.

## Example Requests

### Register seller

```json
{
  "username": "seller1",
  "email": "seller1@example.com",
  "password": "strongpass123",
  "role": "seller"
}
```

### Get JWT token

```json
{
  "username": "seller1",
  "password": "strongpass123"
}
```

### Create product

Requires seller authentication.

```json
{
  "title": "Ceramic mug",
  "description": "Handmade white clay mug.",
  "price": "1200.00",
  "quantity": 5,
  "category": 1
}
```

### Create order

Requires buyer authentication.

```json
{
  "product": 1,
  "quantity": 2
}
```

## Business Logic: Order Creation

Order creation is implemented in the service layer.

When a buyer creates an order, the backend:

1. Validates product availability.
2. Validates requested quantity.
3. Locks the product row using `select_for_update()`.
4. Calculates `total_price` on the backend.
5. Creates the order.
6. Decreases product `quantity`.
7. Sets `is_available = False` when stock reaches zero.

This prevents clients from manually controlling order price or corrupting stock data.

## CI

The project uses GitHub Actions to run checks and tests automatically.

Workflow file:

```text
.github/workflows/tests.yml
```

The CI pipeline:

1. Starts PostgreSQL service.
2. Installs Python dependencies.
3. Runs Django system checks.
4. Runs the test suite.

## Project Status

The project is under active development as a backend portfolio project.

Implemented:

* Django REST Framework API;
* PostgreSQL database integration;
* JWT authentication;
* role-based access control;
* product and order management;
* service-layer order creation logic;
* product filtering, search, ordering and cursor pagination;
* Swagger/OpenAPI documentation;
* Docker Compose setup;
* GitHub Actions test workflow;
* automated API test suite.

Planned improvements:

* advanced product filtering;
* product image handling improvements;
* user profile endpoint;
* order status management;
* API documentation refinements;
* production-ready deployment configuration.
