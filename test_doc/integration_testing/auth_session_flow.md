# Integration Test Scenario: Authentication and Session Flow

## Overview
This integration scenario validates the end-to-end user path from initial sign-up to logging in and secure, role-restricted page access.

## Flow Steps & Components Involved

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant FE as Vue.js Frontend (Register/Login)
    participant Store as Pinia auth Store
    participant BE as Flask Backend (/api/auth)
    participant DB as SQLite Database (Users)

    User->>FE: Fills registration form
    FE->>BE: POST /api/auth/register
    BE->>DB: Insert new user with hashed password
    DB-->>BE: Success
    BE-->>FE: 201 Created

    User->>FE: Enters credentials
    FE->>BE: POST /api/auth/login
    BE->>DB: Check email & verify hash
    BE-->>FE: 200 OK (Returns JWT token)
    FE->>Store: Save token & user metadata
    
    User->>FE: Navigates to role-guarded route
    FE->>Store: Check role matches route guard
    Note over FE: Router.beforeEach validates permissions
```

### 1. User Registration
* **Frontend View:** [Register.vue](file:///c:/Users/nithi/OneDrive/Desktop/Projects/SE_P/MAY2026-Team-034/frontend/src/views/Register.vue)
* **Backend Endpoint:** `POST /api/auth/register` (in [auth.py](file:///c:/Users/nithi/OneDrive/Desktop/Projects/SE_P/MAY2026-Team-034/backend/app/routes/auth.py))
* **Verification:** Check that a new user record with appropriate default role is created in the database.

### 2. User Authentication
* **Frontend View:** [Login.vue](file:///c:/Users/nithi/OneDrive/Desktop/Projects/SE_P/MAY2026-Team-034/frontend/src/views/Login.vue)
* **Backend Endpoint:** `POST /api/auth/login` (in [auth.py](file:///c:/Users/nithi/OneDrive/Desktop/Projects/SE_P/MAY2026-Team-034/backend/app/routes/auth.py))
* **Verification:** Retrieve the JWT access token and user claims. Ensure the Axios client defaults are updated with the authorization header.

### 3. Session Persistence & Token Handling
* **Frontend Store:** `frontend/src/stores/auth.js`
* **Verification:** Ensure that page refreshes do not clear the user session unless the token expires or [LogoutModal.vue](file:///c:/Users/nithi/OneDrive/Desktop/Projects/SE_P/MAY2026-Team-034/frontend/src/components/LogoutModal.vue) is triggered.

### 4. Role-based Route Guard Integration
* **Frontend Router:** `frontend/src/router/index.js`
* **Verification:** 
  * Attempt to access a student view using a faculty token (should permit access if correct, or block if role mismatch).
  * Attempt to access an admin view using a student token (should redirect to `/unauthorized` or `/login`).
