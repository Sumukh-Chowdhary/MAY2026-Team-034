# Module 1: Authentication & Profile Management - Developer Documentation

This document serves as a complete reference for team members building on top of **Module 1**.

---

## 📌 1. Overview & Setup

- **Backend Framework**: Flask + Flask-SQLAlchemy (SQLite)
- **Authentication**: JWT (JSON Web Tokens via `PyJWT`)
- **Password Security**: `werkzeug.security` (PBKDF2 SHA256 Hashing)
- **Formatting Standards**: PEP 8 / Flake8 Compliant

---

## 🗄️ 2. Database Models & Schema

All models are defined in `app/models/user.py` and exported through `app/models/__init__.py`.

### **Entity Overview**
```
            ┌───────────────┐
            │     Role      │
            └───────┬───────┘
                    │ 1
                    │
                    │ *
            ┌───────┴───────┐           ┌──────────────────┐
            │     User      ├───────────┤  StudentProfile  │
            └───────┬───────┘ 1       1 └──────────────────┘
                    │
                    │ 1
                    │
                    │ 1
            ┌───────┴───────┐
            │ FacultyProfile│
            └───────────────┘
```

### **Model Definitions**

#### 1. `User`
Minimal authentication and account state entity.
- `id` (Integer, Primary Key)
- `email` (String, Unique, Not Null)
- `password_hash` (String, Encrypted)
- `role_id` (ForeignKey -> `roles.id`)
- `account_status` (String, `'ACTIVE'` / `'DEACTIVATED'`)
- `created_at` / `updated_at` (DateTime)

#### 2. `StudentProfile`
Extended details for Student users.
- `id` (Integer, Primary Key)
- `user_id` (ForeignKey -> `users.id`, Unique)
- `roll_no` (String, Unique) — e.g. `CB.SC.U4CSE22001`
- `full_name` (String)
- `phone_number` (String)
- `year_of_study` (String) — e.g. `"3rd Year"`
- `department_id` (ForeignKey -> `departments.id`)
- `bio` (Text)

#### 3. `FacultyProfile`
Extended details for Faculty users.
- `id` (Integer, Primary Key)
- `user_id` (ForeignKey -> `users.id`, Unique)
- `employee_id` (String, Unique) — e.g. `FAC001`
- `full_name` (String)
- `phone_number` (String)
- `designation` (String) — e.g. `"Associate Professor"`
- `department_id` (ForeignKey -> `departments.id`)
- `bio` (Text)

#### 4. `Role`
- `id` (Integer, Primary Key)
- `name` (String, e.g. `'ADMIN'`, `'FACULTY'`, `'STUDENT'`)
- `description` (String)

#### 5. `Department`
- `id` (Integer, Primary Key)
- `name` (String, e.g. `"Computer Science"`)
- `code` (String, e.g. `"CSE"`)

#### 6. `TokenBlocklist`
Stores revoked JWT tokens for logout and session invalidation.
- `id` (Integer, Primary Key)
- `jti` (String, Unique JWT Identifier)
- `created_at` (DateTime)

---

## 🔐 3. Authentication & Helper Decorators

Import auth utilities from `app.utils.auth_jwt`:

```python
from app.utils.auth_jwt import jwt_required, roles_required, generate_jwt_token
```

### **1. `@jwt_required`**
Protects an endpoint. Requires `Authorization: Bearer <token>` header. Populates `g.current_user` and `g.jti`.

### **2. `@roles_required('ADMIN', 'FACULTY')`**
Restricts endpoint access to specified role names. Automatically enforces `@jwt_required`.

---

## 🚀 4. API Endpoints Reference

Base URL: `http://127.0.0.1:5000`

### **A. Authentication (`/api/auth`)**

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login` | None | Authenticate user via email or register number |
| `POST` | `/api/auth/register` | None | Register a new student or faculty user |
| `GET` | `/api/auth/me` | JWT | Get current logged-in user profile |
| `POST` | `/api/auth/change-password` | JWT | Change password for current user |
| `POST` | `/api/auth/logout` | JWT | Invalidate JWT token |

#### **Sample Payloads & Responses**

**Login Request (`POST /api/auth/login`)**:
```json
{
  "username": "rahul@allclub.com",
  "password": "student123"
}
```

**Login Response (`200 OK`)**:
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1Ni...",
  "user": {
    "id": 3,
    "email": "rahul@allclub.com",
    "fullName": "Rahul Sharma",
    "registerNumber": "CB.SC.U4CSE22001",
    "role": "STUDENT",
    "department": "Computer Science",
    "year": "3rd Year",
    "status": "ACTIVE"
  }
}
```

**Register Request (`POST /api/auth/register`)**:
```json
{
  "fullName": "Priya Patel",
  "email": "priya@allclub.com",
  "password": "student123",
  "role": "STUDENT",
  "registerNumber": "CB.SC.U4CSE22002",
  "departmentId": 2,
  "year": "3rd Year"
}
```

---

### **B. User Management (`/api/users`)**

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/users` | JWT | List users (Optional Query params: `?role=STUDENT&search=Rahul`) |
| `GET` | `/api/users/<id>` | JWT | Get details of a specific user |
| `PUT` | `/api/users/<id>` | JWT | Update user profile (Self or Admin) |
| `DELETE` | `/api/users/<id>` | Admin | Delete a user account |

**Update Profile Request (`PUT /api/users/3`)**:
```json
{
  "fullName": "Rahul Sharma",
  "phone": "+91 98765 43210",
  "bio": "Full stack software developer",
  "year": "4th Year"
}
```

---

## 🛠️ 5. How Team Members Can Extend This

When creating **Module 2 (Clubs)** or **Module 3 (Events)**:

1. **Import `db` and `User`**:
   ```python
   from app.models import db, User
   ```
2. **Foreign Key to User**:
   ```python
   created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
   user = db.relationship('User', lazy=True)
   ```
3. **Protecting Routes**:
   ```python
   from app.utils.auth_jwt import jwt_required, roles_required
   from flask import g

   @clubs_bp.route('', methods=['POST'])
   @jwt_required
   @roles_required('FACULTY', 'ADMIN')
   def create_club():
       creator = g.current_user
       ...
   ```

---

## 🧪 6. Pre-seeded Test Accounts

To re-seed the database at any time:
```bash
python3 -m app.utils.seed
```

| Role | Username / Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@allclub.com` | `admin123` |
| **Faculty** | `meena@allclub.com` | `faculty123` |
| **Student** | `rahul@allclub.com` | `student123` |
