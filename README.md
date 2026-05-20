# Blood Bank Management System

A Django-based web application for managing blood donors, requesters, and donation coordination.

## Features

- **Role-based access control** — Admin, Donor, and Requester roles
- **Donor management** — Register, edit, and delete donor profiles
- **Blood request management** — Requesters can create and manage multiple blood requests
- **Donor matching** — Admins can find compatible donors for a requester by blood group
- **Donation requests** — Admins send requests to donors; donors can accept or reject
- **Notifications** — In-app notifications and email alerts for requesters when a donor accepts
- **Search** — Search donors by blood group

## Tech Stack

- Python 3.13
- Django 5.2
- MySQL (via PyMySQL / mysqlclient)
- django-widget-tweaks

## Prerequisites

- Python 3.13+
- MySQL server running locally
- `pipenv` installed (`pip install pipenv`)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd BloodBank_Management_System
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Create the MySQL database**
   ```sql
   CREATE DATABASE bloodbank_db;
   ```

4. **Configure the database** in `bloodbank/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'bloodbank_db',
           'USER': 'root',
           'PASSWORD': '<your_password>',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create an admin superuser**
   ```bash
   python manage.py createsuperuser
   ```
   Then go to `/admin` and create a `Profile` record for that user with role `admin`.

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/`

## User Roles

| Role | Registration | Access |
|---|---|---|
| Admin | Via Django admin panel | Full access — manage donors, requesters, matching, and notifications |
| Donor | `/register/donor/` | View and manage own profile; accept/reject donation requests |
| Requester | `/register/requester/` | Create and manage blood requests; receive donor notifications |

## Key URLs

| URL | Description |
|---|---|
| `/` | Home page |
| `/register/<role>/` | Register as `donor` or `requester` |
| `/login/<role>/` | Login as `donor`, `requester`, or `admin` |
| `/dashboard/` | Role-specific dashboard |
| `/create-request/` | Requester creates a blood request |
| `/search/` | Admin searches donors by blood group |
| `/requester/<id>/find-donors/` | Admin finds matching donors for a requester |

## Deploying to Vercel

> Vercel is a serverless platform — you need a **remote MySQL database** (e.g. [PlanetScale](https://planetscale.com), [Aiven](https://aiven.io), or [Railway](https://railway.app)) since Vercel cannot connect to `localhost`.

1. **Push your code to GitHub**

2. **Import the project on [vercel.com](https://vercel.com)**

3. **Set environment variables** in the Vercel dashboard (Settings → Environment Variables) using `.env.example` as a reference:

   | Variable | Description |
   |---|---|
   | `SECRET_KEY` | Django secret key |
   | `DEBUG` | Set to `False` |
   | `ALLOWED_HOSTS` | e.g. `.vercel.app` |
   | `DB_NAME` | Remote MySQL database name |
   | `DB_USER` | Database user |
   | `DB_PASSWORD` | Database password |
   | `DB_HOST` | Remote MySQL host |
   | `DB_PORT` | `3306` |
   | `EMAIL_HOST_USER` | SMTP email address |
   | `EMAIL_HOST_PASSWORD` | SMTP password / app password |

4. **Run migrations** once after first deploy (from your local machine pointing at the remote DB):
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Vercel will automatically run `build_files.sh` to install dependencies and collect static files on each deploy.

## Email Notifications

Email is used to notify donors of requests and requesters of donor details. Configure your email backend in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '<smtp_host>'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '<your_email>'
EMAIL_HOST_PASSWORD = '<your_password>'
DEFAULT_FROM_EMAIL = '<your_email>'
```

## Project Structure

```
BloodBank_Management_System/
├── bloodbank/          # Project settings, URLs, WSGI/ASGI
├── main/               # Core app — models, views, forms, templates
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── models.py       # Profile, Donor, Requester, Notification, DonationRequest
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── manage.py
└── Pipfile
```
