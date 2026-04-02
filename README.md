# Finance Data Processing and Access Control Backend

A RESTful backend API for a finance dashboard system built with **Django** and **Django REST Framework**. It supports role-based access control, financial record management, and dashboard-level analytics.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Framework | Django 4.2 + Django REST Framework |
| Database | PostgreSQL |
| Authentication | JWT via `djangorestframework-simplejwt` |
| Filtering | `django-filter` |
| Config | `python-decouple` (.env) |
| CORS | `django-cors-headers` |

---

## Project Structure

```
finance-backend/
├── core/                        # Shared permission classes
│   └── permissions.py
├── users/                       # User management + auth
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── transactions/                # Financial records
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── dashboard/                   # Summary & analytics
│   ├── views.py
│   └── urls.py
├── zorvyn/                      # Django project config
│   ├── settings.py
│   └── urls.py
├── .env
├── manage.py
└── requirements.txt
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd finance-backend
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=finance_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Create the PostgreSQL database

```sql
CREATE DATABASE finance_db;
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create a superuser (admin)

```bash
python manage.py createsuperuser
```

### 8. Start the server

```bash
python manage.py runserver
```

API is now available at `http://127.0.0.1:8000/api/`

---

## Roles

| Role | Description |
|---|---|
| `admin` | Full access — manage users and transactions |
| `analyst` | Read transactions and view dashboard |
| `viewer` | View dashboard and transactions (read-only) |

---

## API Endpoints

### Auth

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/auth/login/` | Public | Login and get JWT tokens |
| POST | `/api/auth/refresh/` | Public | Refresh access token |

**Login request body:**
```json
{
  "username": "jjbrij",
  "password": "yourpassword"
}
```

**Login response:**
```json
{
  "access": "<jwt-access-token>",
  "refresh": "<jwt-refresh-token>",
  "user": {
    "id": 1,
    "username": "jjbrij",
    "email": "jjbrij2204@gmail.com",
    "role": "admin"
  }
}
```

---

### Users *(Admin only)*

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/users/` | List all users |
| POST | `/api/users/` | Create a new user |
| GET | `/api/users/<id>/` | Get user details |
| PATCH | `/api/users/<id>/` | Update role or status |
| DELETE | `/api/users/<id>/` | Delete a user |
| GET | `/api/users/me/` | Current user profile |
| POST | `/api/users/change-password/` | Change own password |

**Create user request body:**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "securepass123",
  "role": "analyst"
}
```

---

### Transactions

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/transactions/` | All roles | List transactions (with filters) |
| POST | `/api/transactions/` | Admin | Create a transaction |
| GET | `/api/transactions/<id>/` | All roles | Get transaction detail |
| PUT | `/api/transactions/<id>/` | Admin | Full update |
| PATCH | `/api/transactions/<id>/` | Admin | Partial update |
| DELETE | `/api/transactions/<id>/` | Admin | Soft delete |

**Filtering (query params):**

```
GET /api/transactions/?type=income
GET /api/transactions/?category=salary
GET /api/transactions/?from=2026-01-01&to=2026-03-31
GET /api/transactions/?type=expense&category=food
```

**Create transaction request body:**
```json
{
  "amount": 5000.00,
  "type": "income",
  "category": "salary",
  "date": "2026-04-01",
  "notes": "Monthly salary"
}
```

**Transaction types:** `income`, `expense`

**Categories:** `salary`, `freelance`, `investment`, `food`, `transport`, `utilities`, `healthcare`, `education`, `entertainment`, `other`

---

### Dashboard *(All roles)*

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard/summary/` | Total income, expenses, net balance |
| GET | `/api/dashboard/by-category/` | Totals grouped by category |
| GET | `/api/dashboard/trends/` | Monthly income vs expense breakdown |
| GET | `/api/dashboard/recent/` | Last 10 transactions |

**Summary response example:**
```json
{
  "total_income": 15000.00,
  "total_expense": 6200.00,
  "net_balance": 8800.00
}
```

**Trends response example:**
```json
[
  { "month": "2026-01", "income": 5000.00, "expense": 2100.00 },
  { "month": "2026-02", "income": 5000.00, "expense": 1800.00 },
  { "month": "2026-03", "income": 5000.00, "expense": 2300.00 }
]
```

---

## Access Control Summary

| Endpoint | Viewer | Analyst | Admin |
|---|---|---|---|
| Login | ✅ | ✅ | ✅ |
| View transactions | ✅ | ✅ | ✅ |
| Create/Edit/Delete transactions | ❌ | ❌ | ✅ |
| View dashboard | ✅ | ✅ | ✅ |
| View users | ❌ | ❌ | ✅ |
| Create/Edit/Delete users | ❌ | ❌ | ✅ |

---

## Authentication

All protected endpoints require a Bearer token in the request header:

```
Authorization: Bearer <access-token>
```

Tokens expire after **12 hours**. Use `/api/auth/refresh/` with the refresh token to get a new access token.

---

## Assumptions & Design Decisions

- **Custom User model** extends Django's `AbstractUser` with a `role` field and `is_active` status, defined before any migrations to avoid inconsistency.
- **Soft delete** is used for transactions (`is_deleted=True`) so financial records are never permanently removed — important for audit trails.
- **Role enforcement** is handled via reusable permission classes in `core/permissions.py` (`IsAdmin`, `IsAnalystOrAdmin`, `IsAnyRole`) applied per view.
- **Amount validation** ensures no zero or negative values are accepted on transaction creation.
- **Category choices** are defined as constants on the model to ensure data consistency.
- A superuser created via `createsuperuser` must manually have their `role` set to `admin` via the Django admin panel or by updating the database directly.

---

## Requirements

```
django>=4.2,<5.0
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
django-filter>=23.0
python-decouple>=3.8
psycopg2-binary>=2.9
django-cors-headers>=4.3
```