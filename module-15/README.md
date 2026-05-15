# ToriloShop Production Deployment Setup

ToriloShop is a Django-based e-commerce project with product listings, categories, user authentication, API endpoints, JWT/token authentication, image uploads, and static asset support. This version of the project has been prepared for production deployment by moving sensitive settings into environment variables, configuring production-ready static file handling, and adding deployment server support.

## Project Description

The production setup for ToriloShop includes changes that make the Django application safer and easier to deploy on platforms such as Render. The project now uses environment variables for sensitive settings, supports both SQLite and PostgreSQL databases, serves static files with WhiteNoise, and includes a `Procfile` for deployment commands.

The main production changes made are:

- Sensitive values were removed from hardcoded settings and moved into a `.env` file.
- `python-decouple` was added so Django can read environment variables cleanly.
- `dj-database-url` was added so the project can use SQLite locally and PostgreSQL in production.
- `gunicorn` was added as the production WSGI server.
- `waitress` was added for local Windows WSGI testing.
- `whitenoise` was added to serve static files in production.
- Static file collection was configured using `STATIC_ROOT` and WhiteNoise storage.
- A `Procfile` was added with the production start command.
- `requirements.txt` was generated with all installed packages.
- `.env`, `db.sqlite3`, `media/`, `staticfiles/`, and `venv/` are excluded from Git using `.gitignore`.

## Features Implemented

- Environment variable configuration using `.env`
- Secure `SECRET_KEY` loading with `python-decouple`
- Configurable `DEBUG` setting
- Configurable `ALLOWED_HOSTS`
- Database configuration using `DATABASE_URL`
- SQLite fallback for local development
- PostgreSQL support for production deployment
- Static file serving with WhiteNoise
- Production process command using Gunicorn
- Windows local WSGI testing support with Waitress
- Static files prepared using `collectstatic`
- Dependency tracking with `requirements.txt`

## Tech Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite for local development
- PostgreSQL for production
- Gunicorn
- Waitress
- WhiteNoise
- python-decouple
- dj-database-url

## Project Structure

```txt
module-15/
+-- accounts/
+-- products/
+-- toriloshop/
|   +-- settings.py
|   +-- urls.py
|   +-- wsgi.py
|   +-- asgi.py
+-- users/
+-- manage.py
+-- Procfile
+-- requirements.txt
+-- .gitignore
+-- README.md
```

## Local Setup Instructions


### 1. Create and Activate a Virtual Environment

On Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a Local `.env` File

Create a `.env` file in the `module-15` folder:

```env
SECRET_KEY=your-local-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

The `.env` file must not be committed to Git. It is already listed in `.gitignore`.

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit:

```txt
http://127.0.0.1:8000/
```

## Running Locally with Waitress on Windows

Gunicorn does not run natively on Windows. Use Waitress for local WSGI testing:

```powershell
waitress-serve --listen=127.0.0.1:8001 toriloshop.wsgi:application
```

Visit:

```txt
http://127.0.0.1:8001/
```

## Running with Gunicorn

Gunicorn is used in production on Linux-based deployment platforms:

```bash
gunicorn toriloshop.wsgi:application --log-file -
```

The same command is included in the `Procfile`:

```txt
web: gunicorn toriloshop.wsgi:application --log-file -
```

## Production Environment Variables

Set these environment variables on your deployment platform:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DB_NAME
```

Replace `yourdomain.com` and the PostgreSQL credentials with the actual values from your hosting platform.

## Deployment Steps

After uploading the project to your deployment platform, run:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then start the application with:

```bash
gunicorn toriloshop.wsgi:application --log-file -
```

If the platform uses a `Procfile`, it will automatically use:

```txt
web: gunicorn toriloshop.wsgi:application --log-file -
```

## Static and Media Files

Static files are handled by WhiteNoise in production. These include CSS, JavaScript, admin static files, and app static assets.

Media files are uploaded files such as product images. Django serves media files locally only when `DEBUG=True`. In production, uploaded media files should be handled by one of the following:

- Cloudinary
- AWS S3
- A VPS/Nginx media folder setup
- A deployment platform that supports persistent media storage

WhiteNoise does not serve uploaded media files.

## Git Ignore Notes

The following files and folders are excluded from Git:

```txt
venv/
__pycache__/
*.pyc
db.sqlite3
.env
media/
staticfiles/
*.log
```

To confirm `.env` is ignored, run:

```bash
git check-ignore -v .env
```

To confirm `.env` is not tracked, run:

```bash
git status --short -- .env
```

If the second command prints nothing, `.env` will not be uploaded to GitHub.

## Useful Checks

Run Django's normal system check:

```bash
python manage.py check
```

Run deployment checks:

```bash
python manage.py check --deploy
```

Check if migrations are applied:

```bash
python manage.py migrate --check
```

## Notes

- Keep `DEBUG=True` only for local development.
- Use `DEBUG=False` in production.
- Do not commit `.env`, `db.sqlite3`, `media/`, `staticfiles/`, or `venv/`.
- Use PostgreSQL in production through `DATABASE_URL`.
- Use Gunicorn in production and Waitress only for local Windows WSGI testing.
- Ensure `SECRET_KEY` is unique and kept secret in production.
- Configure `ALLOWED_HOSTS` correctly for production deployment.
- Use `collectstatic` to prepare static files for production.
- Consider using a cloud storage solution for media files in production.

### CONCLUSION
This production setup for ToriloShop ensures that the Django application is secure, configurable, and ready for deployment on platforms like Render. By following the local setup instructions, you can run the project locally with the new production-ready configuration. 