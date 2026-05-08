## TORILOSHOP AUTHIENTICATION UPDATE

# ToriloShop

ToriloShop is a Django ecommerce project with product and category pages. It now includes user authentication so customers can register, log in, log out, and access protected pages.

## Project Description

ToriloShop now has a complete authentication flow:

- Users can create an account with their name, email, and password.
- Users can log in with either their username or email address.
- Logged-in users can log out securely.
- A dashboard page is protected, so only logged-in users can view it.
- Product create, edit, and delete pages require a logged-in user, and only staff users can manage products.

## Features Implemented

- Registration page for new users.
- Login page with username or email support.
- Logout button using Django's secure logout flow.
- Protected dashboard route for authenticated users.
- Protected product management routes.
- Navbar updates:
  - Guests see Login and Register links.
  - Logged-in users see Dashboard, their username, and Logout.