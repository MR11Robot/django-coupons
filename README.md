# 🤖 Bot Management Dashboard

A Django-based web dashboard for managing and monitoring multiple automation bots. The system provides a centralized control panel for running bots, managing their data, and exposing a REST API for external integrations.

---

## 📦 Project Structure

```
coupon-checker/
├── manage.py
├── pyproject.toml
├── .env
│
├── config/                         # Django project settings & root URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/                          # Authentication & user management
│   ├── views.py
│   ├── urls.py
│   └── models.py
│
├── coupon_checker/                 # Coupon checker app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── permissions.py
│   ├── pagination.py
│   ├── decorators.py
│   ├── middleware/
│   │   └── request_logger.py
│   └── apis/                       # DRF REST API
│       ├── views.py
│       ├── serializers.py
│       └── urls.py
│
├── keyword_scrapper/               # Keyword scraper bot control panel
│   ├── views.py
│   └── urls.py
│
├── link_checker/                   # Backlink checker bot control panel
│   ├── views.py
│   └── urls.py
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── authenticate/
│   │   └── login.html
│   ├── includes/
│   │   ├── navbar.html
│   │   └── form.html
│   ├── coupon_checker/
│   │   ├── websites.html
│   │   ├── website_stores.html
│   │   ├── store_coupons.html
│   │   ├── coupon_checker.html
│   │   ├── company_list.html
│   │   ├── country_list.html
│   │   ├── report_list.html
│   │   ├── create/
│   │   │   ├── website_create.html
│   │   │   ├── store_create.html
│   │   │   ├── coupon_create.html
│   │   │   ├── company_create.html
│   │   │   └── country_create.html
│   │   ├── update/
│   │   │   ├── website_update.html
│   │   │   ├── store_update.html
│   │   │   ├── coupon_update.html
│   │   │   ├── company_update.html
│   │   │   └── country_update.html
│   │   └── partials/
│   │       └── store_list.html
│   ├── backlink_checker/
│   │   ├── control.html
│   │   ├── create/
│   │   │   └── add_website.html
│   │   └── update/
│   │       └── edit.html
│   └── keyword_scrapper/
│       └── control.html
│
└── static/
    ├── css/
    ├── js/
    └── fonts/
```

---

## 🧩 Apps Overview

### 1. Coupon Checker (`/coupon-checker/`)

The core app. Manages a hierarchy of **Websites → Stores → Coupons**, and records coupon validity reports per country.

**Models:**
- `Website` — a coupon website (e.g., coupon.com)
- `Store` — a store listed on a website
- `Coupon` — a coupon code belonging to a store, associated with companies and countries
- `CouponReport` — daily validity check result (valid/invalid, discount amount, country)
- `Company` — the brand/company behind a coupon
- `Country` — country a coupon is valid in

**Key Features:**
- Full CRUD for websites, stores, coupons, companies, and countries
- Coupon reports filtered by website, store, date, country, and status
- REST API for external bot integration (see API section below)
- Admin panel with search, filters, and autocomplete

---

### 2. Keyword Scraper (`/keyword-scrapper/`)

Control panel for a keyword scraping bot running as a separate service on port `5000`.

**Features:**
- Start / Stop the bot
- View real-time status (current keyword, country, progress)
- Download results as `.xlsx`

The bot is expected to expose the following endpoints locally:
```
GET  http://127.0.0.1:5000/status/
POST http://127.0.0.1:5000/start/
POST http://127.0.0.1:5000/stop/
GET  http://127.0.0.1:5000/download/
```

---

### 3. Backlink Checker (`/backlink_checker/`)

Control panel for a backlink checking bot running as a separate service on port `5001`.

**Features:**
- Start / Stop the bot
- View real-time status (current website, article count, link progress)
- Manage tracked websites (add, edit, delete)
- Download per-website reports as `.xlsx`

The bot is expected to expose the following endpoints locally:
```
GET    http://127.0.0.1:5001/status/
POST   http://127.0.0.1:5001/start/
POST   http://127.0.0.1:5001/stop/
GET    http://127.0.0.1:5001/websites/
POST   http://127.0.0.1:5001/add_website/
PUT    http://127.0.0.1:5001/update_website/<name>/
DELETE http://127.0.0.1:5001/delete_website/<name>/
GET    http://127.0.0.1:5001/download/<filename>/
```

---

## 🌐 REST API (`/api/coupon-checker/`)

The coupon checker exposes a REST API consumed by external bots. All endpoints require authentication via API key or session login.

### Authentication

Send the API key in the `Authorization` header:
```
Authorization: Api-Key <your-key>
```

The key must be named `Coupon-Checker` in the Django admin (`API Keys` section).

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/coupon-checker/websites/` | List all websites |
| `GET` | `/api/coupon-checker/stores/` | List all stores |
| `GET` | `/api/coupon-checker/coupons/` | List all coupons |
| `GET` | `/api/coupon-checker/stores/<store_slug>/coupons/` | List coupons for a store |
| `GET` | `/api/coupon-checker/reports/` | List coupon reports |
| `POST` | `/api/coupon-checker/reports/` | Submit a new coupon report |

### POST `/api/coupon-checker/reports/` — Submit Report

**Request Body:**
```json
{
  "coupon": "<coupon-uuid>",
  "status": "valid",
  "discount": 20,
  "product_link": "https://example.com/product",
  "checked_country": "<country-uuid>"
}
```

**Notes:**
- One report per coupon per country per day is allowed (enforced at model level)
- `status` must be `"valid"` or `"invalid"`

---

## ⚙️ Setup

### Requirements

- Python 3.10+
- Django 4.x
- Django REST Framework
- `djangorestframework-api-key`

### Installation

```bash
git clone <repo-url>
cd <project-dir>

poetry install

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Environment Variables

Set the following in your `.env` or `settings.py`:

```python
SECRET_KEY = "your-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Internal API key for simple decorator-based protection
SITE_API_KEY = "your-site-api-key"

# Bot API URLs
KEYWORD_SCRAPPER_API_URL = "http://127.0.0.1:5000"
BACKLINK_CHECKER_API_URL = "http://127.0.0.1:5001"
```

---

## 🔐 Authentication & Permissions

All views require login (`LoginRequiredMixin`).

The REST API supports two auth methods:
- **Session auth** — for browser-based access
- **API Key auth** — via `HasCouponCheckerAPIKey` permission class (key name must be `Coupon-Checker`)

A simple decorator-based guard (`@key_required`) is also available for internal use, checking `X-API-KEY` header against `settings.SITE_API_KEY`.

---

## 🛠️ Middleware

A custom request logger middleware is included:

```python
# settings.py
MIDDLEWARE = [
    ...
    "coupon_checker.middleware.request_logger.SimpleRequestLoggerMiddleware",
]
```

Logs every request with IP, method, path, and response status code to the console.

---

## 🗄️ Admin Panel

Access at `/admin/`. Registered models:

- `Website`, `Store`, `Coupon`, `Country`, `Company`, `CouponReport`
- Coupon admin includes autocomplete for stores and country display
- Report admin filters by website, store, country, and date

---

## 📄 URL Structure

```
/                          → Home (login required)
/users/                    → User auth
/coupon-checker/           → Coupon checker dashboard
/keyword-scrapper/         → Keyword scraper control panel
/backlink_checker/         → Backlink checker control panel
/api/coupon-checker/       → REST API
/admin/                    → Django admin
```