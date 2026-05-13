# ToriloShop API

ToriloShop is a Django ecommerce backend with product and category management. The API is built with Django REST Framework and includes authentication, authorization, pagination, filtering, searching, ordering, and CORS support.

## Project Description

This project was secured and improved with the following API features:

- Token authentication for protected product actions.
- JWT authentication endpoints for access and refresh tokens.
- Product ownership using a `created_by` field.
- Only the product creator can update or delete their own product.
- Public product/category read endpoints.
- Pagination for product listing.
- Filtering, searching, and ordering for products.
- CORS headers enabled to allow API requests from any origin during development.

## Features Implemented

| Feature | Description |
| --- | --- |
| Token Auth | Users can get a single auth token from `/api/auth-token/`. |
| JWT Auth | Users can get JWT access and refresh tokens from `/api/token/`. |
| JWT Refresh | Users can refresh access tokens from `/api/token/refresh/`. |
| Protected Writes | `POST`, `PUT`, and `DELETE` product requests require authentication. |
| Creator Permissions | Only the user who created a product can update or delete it. |
| `created_by` Field | Each product stores the user who created it. |
| Pagination | Product list returns 6 products per page with `next` and `previous` links. |
| Filtering | Products can be filtered by `category` and `is_available`. |
| Search | Products can be searched by `name`. |
| Ordering | Products can be ordered by `price` or `-price`. |
| CORS | CORS is enabled for all origins during development. |

## Tech Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- Django Filter
- Django CORS Headers

## Setup Instructions

From the project folder:

```powershell
cd C:\Users\ogbon\OneDrive\Desktop\alfred-ogbonna-backend-dune-cohort\module-14
```

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Install dependencies:

```powershell
pip install django djangorestframework djangorestframework-simplejwt django-filter django-cors-headers pillow
```

Run migrations:

```powershell
python manage.py migrate
```

Create a user for testing authentication:

```powershell
python manage.py createsuperuser
```

Start the development server:

```powershell
python manage.py runserver
```

Base URL:

```text
http://127.0.0.1:8000
```

## Authentication

The API supports two authentication methods:

- Token Auth: `Authorization: Token your_token`
- JWT Auth: `Authorization: Bearer your_access_token`

## Obtain A Single Auth Token

Use this endpoint when you want one token response.

```text
POST http://127.0.0.1:8000/api/auth-token/
```

Postman setup:

- Authorization: `No Auth`
- Body: `raw`
- Type: `JSON`

Request body:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Expected response:

```json
{
  "token": "your_auth_token"
}
```

Use the token on protected product requests:

```text
Authorization: Token your_auth_token
```

## Obtain JWT Access And Refresh Tokens

Use this endpoint when you want JWT authentication.

```text
POST http://127.0.0.1:8000/api/token/
```

Postman setup:

- Authorization: `No Auth`
- Body: `raw`
- Type: `JSON`

Request body:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Expected response:

```json
{
  "refresh": "your_refresh_token",
  "access": "your_access_token"
}
```

Use the JWT access token on protected product requests:

```text
Authorization: Bearer your_access_token
```

## Refresh JWT Access Token

```text
POST http://127.0.0.1:8000/api/token/refresh/
```

Request body:

```json
{
  "refresh": "your_refresh_token"
}
```

Expected response:

```json
{
  "access": "new_access_token"
}
```

## API Endpoints

| Method | Endpoint | Auth Required | Description |
| --- | --- | --- | --- |
| POST | `/api/auth-token/` | No | Get a single auth token |
| POST | `/api/token/` | No | Get JWT access and refresh tokens |
| POST | `/api/token/refresh/` | No | Refresh JWT access token |
| GET | `/api/products/` | No | List products |
| POST | `/api/products/` | Yes | Create product |
| GET | `/api/products/<id>/` | No | Retrieve one product |
| PUT | `/api/products/<id>/` | Yes, creator only | Update product |
| DELETE | `/api/products/<id>/` | Yes, creator only | Delete product |
| GET | `/api/categories/` | No | List categories |

## Test Each Endpoint In Postman

### 1. Get Categories

Use this first to find a valid `category_id`.

```text
GET http://127.0.0.1:8000/api/categories/
```

Authorization:

```text
No Auth
```

Expected response:

```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic products",
    "product_count": 0,
    "products": []
  }
]
```

### 2. List Products

```text
GET http://127.0.0.1:8000/api/products/
```

Authorization:

```text
No Auth
```

Expected response:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "iPhone Charger",
      "price": "15000.00",
      "stock": 20,
      "is_available": true,
      "image": null,
      "created_at": "2026-05-13T10:00:00Z",
      "created_by": "prime190",
      "category": {
        "id": 1,
        "name": "Electronics",
        "description": "Electronic products",
        "product_count": 1
      }
    }
  ]
}
```

### 3. Create Product Without Auth

This should fail.

```text
POST http://127.0.0.1:8000/api/products/
```

Authorization:

```text
No Auth
```

Request body:

```json
{
  "name": "iPhone Charger",
  "price": "15000.00",
  "stock": 20,
  "is_available": true,
  "category_id": 1
}
```

Expected response:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

Expected status:

```text
401 Unauthorized
```

### 4. Create Product With Token Auth

```text
POST http://127.0.0.1:8000/api/products/
```

Headers:

```text
Authorization: Token your_auth_token
Content-Type: application/json
```

Request body:

```json
{
  "name": "iPhone Charger",
  "price": "15000.00",
  "stock": 20,
  "is_available": true,
  "category_id": 1
}
```

Expected response:

```json
{
  "id": 1,
  "name": "iPhone Charger",
  "price": "15000.00",
  "stock": 20,
  "is_available": true,
  "image": null,
  "created_at": "2026-05-13T10:00:00Z",
  "created_by": "prime190",
  "category": {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic products",
    "product_count": 1
  }
}
```

Expected status:

```text
201 Created
```

### 5. Retrieve One Product

```text
GET http://127.0.0.1:8000/api/products/1/
```

Authorization:

```text
No Auth
```

Expected status:

```text
200 OK
```

### 6. Update Product

Only the creator can update the product.

```text
PUT http://127.0.0.1:8000/api/products/1/
```

Headers:

```text
Authorization: Token your_auth_token
Content-Type: application/json
```

Request body:

```json
{
  "name": "Updated iPhone Charger",
  "price": "18000.00",
  "stock": 15,
  "is_available": true,
  "category_id": 1
}
```

Expected status:

```text
200 OK
```

### 7. Delete Product

Only the creator can delete the product.

```text
DELETE http://127.0.0.1:8000/api/products/1/
```

Headers:

```text
Authorization: Token your_auth_token
```

Expected response:

```text
204 No Content
```

## Pagination

Products are paginated 6 per page.

```text
GET http://127.0.0.1:8000/api/products/
```

If there are more than 6 products, the response includes a `next` page link:

```json
{
  "count": 7,
  "next": "http://127.0.0.1:8000/api/products/?page=2",
  "previous": null,
  "results": []
}
```

Page 2:

```text
GET http://127.0.0.1:8000/api/products/?page=2
```

## Filtering, Search, And Ordering

Filter by category:

```text
GET http://127.0.0.1:8000/api/products/?category=1
```

Filter by availability:

```text
GET http://127.0.0.1:8000/api/products/?is_available=true
```

Search by product name:

```text
GET http://127.0.0.1:8000/api/products/?search=charger
```

Order by price from low to high:

```text
GET http://127.0.0.1:8000/api/products/?ordering=price
```

Order by price from high to low:

```text
GET http://127.0.0.1:8000/api/products/?ordering=-price
```

Combined example:

```text
GET http://127.0.0.1:8000/api/products/?category=1&is_available=true&search=charger&ordering=price
```

## CORS

CORS is enabled for all origins during development:

```python
CORS_ALLOW_ALL_ORIGINS = True
```

This allows frontend clients and Postman to call the API without CORS restrictions during local development.

## Notes

- Use `/api/auth-token/` when you want one simple token response.
- Use `/api/token/` when you want JWT `refresh` and `access` tokens.
- Product `GET` requests are public.
- Product `POST`, `PUT`, and `DELETE` requests require authentication.
- Product `PUT` and `DELETE` requests require the authenticated user to be the product creator.
- Product list responses are paginated.
- Category list responses are not paginated.

## CONCLUSION
This project demonstrates how to build a secure and feature-rich ecommerce API with Django REST Framework. It includes token and JWT authentication, product ownership permissions, pagination, filtering, searching, ordering, and CORS support. The API allows users to manage products while ensuring that only authenticated users can create, update, or delete their own products.