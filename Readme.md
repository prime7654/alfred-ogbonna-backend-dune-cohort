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