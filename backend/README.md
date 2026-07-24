# Backend API Service (Flask + SQLAlchemy + SQLite)

This is the backend REST API service for **MAY2026-Team-034**, built with Flask, Flask-SQLAlchemy, SQLite3, Celery, and Redis.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python **3.9+** installed
- Git

---

## 🛠️ Step 1: Virtual Environment Setup & Dependencies

Navigate to the `backend` directory:
```bash
cd backend
```

### Option A: Linux / macOS / WSL (Bash/Zsh)
```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Option B: Windows (PowerShell)
```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt
```
*(If PowerShell throws an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first)*

---

## 🗄️ Step 2: Shared Database & Re-Seeding

The SQLite database (`instance/app.db`) comes **pre-seeded and included in this repository** so all team members use the exact same shared database out of the box!

If you want to reset or re-seed the shared database at any time(only for **reseting db**):

```bash
# With venv activated:
python -m app.utils.seed
```

---

## 🏃 Step 3: Run the Application

Start the Flask development server:

```bash
# With venv activated:
python main.py
```

The application will start at: **`http://127.0.0.1:5000`**

---

## 📖 Developer Documentation
For full details on database models, relationships, JWT authentication decorators, and API endpoint specs, read **[MODULE1_DOCUMENTATION.md](MODULE1_DOCUMENTATION.md)**.
