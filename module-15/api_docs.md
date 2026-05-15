# ToriloShop API Documentation

Base URL:

```text
http://127.0.0.1:8000
```

The API returns JSON responses. Product write actions accept either simple token auth or JWT auth:

```text
Authorization: Token your_auth_token
Authorization: Bearer your_jwt_access_token
```

Public read requests do not require authentication.

## Endpoints Summary

| Method | URL | Auth Required | Description |
| --- | --- | --- | --- |
| POST | `/api/auth-token/` | No | Get one simple auth token |
| POST | `/api/token/` | No | Get JWT access and refresh tokens |
| POST | `/api/token/refresh/` | No | Refresh a JWT access token |
| GET | `/api/products/` | No | List products with pagination |
| POST | `/api/products/` | Yes | Create a product |
| GET | `/api/products/<id>/` | No | Retrieve one product |
| PUT | `/api/products/<id>/` | Yes, creator only | Fully update one product |
| DELETE | `/api/products/<id>/` | Yes, creator only | Delete one product |
| GET | `/api/categories/` | No | List categories with products |

## Auth Token

### Get Simple Auth Token

```text
POST /api/auth-token/
```

Auth required: No

Request body:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Success response:

```json
{
  "token": "your_auth_token"
}
```

Error response:

```json
{
  "non_field_errors": [
    "Unable to log in with provided credentials."
  ]
}
```

Use this token on protected product requests:

```text
Authorization: Token your_auth_token
```

## JWT Auth

### Get JWT Token Pair

```text
POST /api/token/
```

Auth required: No

Request body:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Success response:

```json
{
  "refresh": "your_refresh_token",
  "access": "your_access_token"
}
```

Error response:

```json
{
  "detail": "No active account found with the given credentials"
}
```

Use the access token on protected product requests:

```text
Authorization: Bearer your_access_token
```

### Refresh JWT Access Token

```text
POST /api/token/refresh/
```

Auth required: No

Request body:

```json
{
  "refresh": "your_refresh_token"
}
```

Success response:

```json
{
  "access": "new_access_token"
}
```

Error response:

```json
{
  "detail": "Token is invalid",
  "code": "token_not_valid"
}
```

## Products

### List Products

```text
GET /api/products/
```

Auth required: No

Query parameters:

| Parameter | Example | Description |
| --- | --- | --- |
| `page` | `/api/products/?page=2` | Product page number |
| `category` | `/api/products/?category=1` | Filter by category ID |
| `is_available` | `/api/products/?is_available=true` | Filter by availability |
| `search` | `/api/products/?search=charger` | Search by product name |
| `ordering` | `/api/products/?ordering=price` | Order by price ascending |
| `ordering` | `/api/products/?ordering=-price` | Order by price descending |

Request body: None

Success response:

```json
{
  "count": 12,
  "next": "http://127.0.0.1:8000/api/products/?page=2",
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
        "product_count": 4
      }
    }
  ]
}
```

Notes:
- Products are paginated 6 per page.
- `next` and `previous` contain page links when another page exists.

### Create Product

```text
POST /api/products/
```

Auth required: Yes

Accepted auth:

```text
Authorization: Token your_auth_token
Authorization: Bearer your_jwt_access_token
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

Success response:

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

Notes:
- `created_by` is set automatically from the authenticated user.
- Do not send `created_by` in the request body.

Error responses:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

```json
{
  "name": [
    "This field is required."
  ]
}
```

### Retrieve Product

```text
GET /api/products/<id>/
```

Auth required: No

Request body: None

Success response:

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

Not found response:

```json
{
  "detail": "No Product matches the given query."
}
```

### Update Product

```text
PUT /api/products/<id>/
```

Auth required: Yes, and the authenticated user must be the product creator.

Accepted auth:

```text
Authorization: Token your_auth_token
Authorization: Bearer your_jwt_access_token
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

Success response:

```json
{
  "id": 1,
  "name": "Updated iPhone Charger",
  "price": "18000.00",
  "stock": 15,
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

Error responses:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

```json
{
  "detail": "You do not have permission to perform this action."
}
```

Notes:
- `PUT` is a full update, so include all required fields.
- Only the user stored in `created_by` can update the product.

### Delete Product

```text
DELETE /api/products/<id>/
```

Auth required: Yes, and the authenticated user must be the product creator.

Accepted auth:

```text
Authorization: Token your_auth_token
Authorization: Bearer your_jwt_access_token
```

Request body: None

Success response:

```text
204 No Content
```

Error responses:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

```json
{
  "detail": "You do not have permission to perform this action."
}
```

Notes:
- Only the user stored in `created_by` can delete the product.

## Categories

### List Categories

```text
GET /api/categories/
```

Auth required: No

Request body: None

Success response:

```json
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic products",
    "product_count": 1,
    "products": [
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
]
```

Notes:
- Category listing is public.
- Category listing is not paginated.
- Each category includes `product_count` and nested products.

## Common Status Codes

| Status | Meaning |
| --- | --- |
| `200 OK` | Request succeeded |
| `201 Created` | Product created successfully |
| `204 No Content` | Product deleted successfully |
| `400 Bad Request` | Missing or invalid request data |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Authenticated user is not allowed to edit/delete this product |
| `404 Not Found` | Product does not exist |
