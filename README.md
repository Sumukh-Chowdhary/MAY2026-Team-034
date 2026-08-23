# AllClub

AllClub is a centralized multi-club management platform for student organizations, developed as part of the Software Engineering Project (May 2026).

This repository contains a Flask backend REST API and a Vue 3/Vite frontend with role-based interfaces for Admin, Faculty Coordinator, and Student users.

## Architecture

```text
AllClub/
├── backend/     # Flask REST API, database, authentication, Redis, Celery
└── frontend/    # Vue 3 + Vite application
```

Typical backend flow:

```text
Frontend → Flask Route / Blueprint → Service Layer → SQLAlchemy Models / Database
```

Routes handle HTTP concerns, authentication/authorization, request parsing and responses. Services contain business/database logic where a service layer exists.

## Tech Stack

### Backend
- Python 3.9+
- Flask
- Flask-SQLAlchemy / SQLAlchemy ORM
- SQLite3
- JWT authentication via the project's JWT helpers / PyJWT
- Werkzeug password hashing
- Flask-SocketIO
- Redis
- Celery
- pytest

### Frontend
- Vue 3
- Vite
- JavaScript
- Vue Router
- Bootstrap 5
- Bootstrap Icons
- Chart.js / Vue Chart.js

## Prerequisites

Install:
- Git
- Python 3.9+
- Node.js and npm
- Redis Server

Verify:

```bash
python3 --version
node -v
npm -v
redis-cli ping
```

A working Redis installation should return:

```text
PONG
```

# Backend Setup

WSL/Mac:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
cd backend
python -m venv venv
.env\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell reports an execution-policy error:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Database

The SQLite database is stored at:

```text
backend/instance/app.db
```

The repository includes a pre-seeded database.

To re-seed/reset it:

```bash
cd backend
source venv/bin/activate
python -m app.utils.seed
```

> Re-seeding resets the database state, so use it only when a clean seeded database is wanted.

## Running the Backend

With the virtual environment active:

```bash
cd backend
source venv/bin/activate
python3 main.py
```

Backend:

```text
http://127.0.0.1:5000
```

# Frontend Setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Production build:

```bash
npm run build
```

Preview a production build:

```bash
npm run preview
```

# Authentication and Authorization

The application uses JWT-based authentication.

Protected requests use:

```text
Authorization: Bearer <token>
```

Authentication answers **who the user is**; authorization answers **what that user is allowed to do**.

The main roles are:

- `ADMIN`
- `FACULTY`
- `STUDENT`

Project helpers include:

```python
from app.utils.auth_jwt import jwt_required, roles_required, generate_jwt_token
```

`@jwt_required` protects an endpoint and populates the current-user context. `@roles_required(...)` restricts access to specified roles.

For detailed authentication/model/API documentation, see `MODULE1_DOCUMENTATION.md`.

# Redis Caching

Redis is used as a **cache**, not as the source of truth.

Current shared cached GET datasets:

```text
clubs:all
venues:all
events:all
```

## Cache-aside flow

```text
GET request
    ↓
Check Redis
 ┌──┴──┐
HIT   MISS
 ↓      ↓
return  DB query
         ↓
      cache result
         ↓
       return
```

Cached entries use both Cache Invalidation & TTL.

## Cache invalidation

After a successful database mutation, affected cache entries are deleted. The next GET repopulates the cache from the database.

Examples:

```text
Club mutation  → clubs:all
Venue mutation → venues:all
Event mutation → events:all
```

Some mutations invalidate multiple caches when a serialized response contains related entity information. For example, editing a club or venue can also invalidate `events:all` because event responses contain relevant club/venue fields.

## Redis failure behavior

Redis is optional infrastructure for these cached reads. If Redis is unavailable, cache operations fail safely and the application falls back to the database. The result is slower reads, not loss of database functionality.

Useful commands:

```bash
redis-cli ping
redis-cli KEYS '*'
redis-cli GET clubs:all
redis-cli TTL clubs:all
```

# Celery

The backend also contains Celery infrastructure and Redis keys may contain Celery bindings. These are separate from the application cache keys such as `clubs:all`, `venues:all`, and `events:all`.

# Testing

The backend uses **pytest**.

From `backend/` with the virtual environment active:

```bash
pytest -v
```

This is the main command for running the complete test suite.

Run a particular test file:

```bash
pytest -v path/to/test_file.py
```

Run one test:

```bash
pytest -v path/to/test_file.py::test_name
```

Run tests matching a keyword:

```bash
pytest -v -k "club"
```

# Frontend Routes

## Public

```text
/              Landing Page
/login         Login Page
/register      Registration Page
/clubs         Club Discovery Page
```

## Admin

```text
/admin
/admin/users
/admin/clubs
/admin/events
/admin/requests
```

## Faculty

```text
/faculty
/faculty/roles
/faculty/clubs
/faculty/events
/faculty/requests
```

## Student

```text
/student
/student/roles
/student/clubs
/student/events
/student/requests
```

The exact functionality available on each page is controlled by the current frontend implementation and backend authorization.

# Test Accounts

The project documentation lists these pre-seeded accounts:

| Role | Username / Email | Password |
|---|---|---|
| Admin | `admin@allclub.com` | `admin123` |
| Faculty | `meena@allclub.com` | `faculty123` |
| Student | `Y24CS001` | `student123` |

After resetting/re-seeding the database, use the seeded credentials again.

# Useful Commands

## Backend

```bash
cd backend
source venv/bin/activate
python3 main.py
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Reset/seed:

```bash
python -m app.utils.seed
```

Run all tests:

```bash
pytest -v
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Build:

```bash
npm run build
```

Preview:

```bash
npm run preview
```

## Redis

```bash
redis-cli ping
redis-cli KEYS '*'
redis-cli GET clubs:all
redis-cli TTL clubs:all
```

# Project Structure

```text
AllClub/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── instance/
│   │   └── app.db
│   ├── requirements.txt
│   └── main.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── data/
│   │   ├── layouts/
│   │   ├── router/
│   │   └── views/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── MODULE1_DOCUMENTATION.md
└── README.md
```

# Developer Notes

## Route vs Service

Where a service exists, routes should delegate business operations to the service rather than duplicating the same database/business logic.

```text
Route
 ├── authentication
 ├── authorization
 ├── request parsing
 └── HTTP response
        ↓
Service
 ├── business logic
 ├── database operations
 └── related side effects
        ↓
Models / Database
```

## Database Transactions and Cache Invalidation

Mutations should commit successfully before invalidating their cache:

```python
db.session.commit()
delete_cached("relevant:key")
```

The database remains authoritative; Redis is only a performance layer.

## Code Style

The Module 1 documentation specifies PEP 8 / Flake8-compatible formatting.

Before submitting changes, run:

```bash
cd backend
pytest -v
```

and verify the frontend builds:

```bash
cd frontend
npm run build
```

# Additional Documentation

For detailed Module 1 authentication, profile, database model, decorator, endpoint, and seeded-account documentation, see:

```text
MODULE1_DOCUMENTATION.md
```

The frontend documentation contains additional Vue/Vite setup, IDE/browser recommendations, routes, and frontend structure.
