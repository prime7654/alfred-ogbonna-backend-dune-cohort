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

## Setup Instructions

Run these commands from the `module-12` folder.

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

Install the project packages:

```bash
pip install django pillow
```

Run database migrations:

```bash
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

Open the project in your browser:

```text
http://127.0.0.1:8000/
```


## SCREENSHOTS
![Protected Redirect](Screenshots\01_login_page.png)

![Protected Redirect](Screenshots\02_register_page.png)

![Protected Redirect](Screenshots\03_protected_route_redirect.png)

![Protected Redirect](Screenshots\04_logged_in_navbar.png)

![Protected Redirect](Screenshots\05_logged_out_navbar.png)


Conclusion:
With the authentication system in place, ToriloShop now offers a more personalized and secure shopping experience. Users can manage their accounts, access protected content, and staff can efficiently manage products. This sets a solid foundation for further enhancements like order management and user profiles.