# Implementation Plan - Sprint 3.1 – Phase 1: Authentication Foundation

This plan outlines the foundational changes required to establish the authentication architecture for the **AlgoPath** backend platform. It introduces centralized configuration, prepares the user database schemas, verifies connection layers, and defines Pydantic validation structures, while ensuring all existing systems compile and no auth endpoints are exposed yet.

## User Review Required

> [!IMPORTANT]
> **Database Dialect Integration**: The project currently runs on **SQLAlchemy + SQLite/MySQL**. There are no MongoDB client drivers (e.g., `pymongo` or `motor`) installed in the virtual environment. To address the task *"Verify and organize the MongoDB connection layer"*, we will:
> 1. Organize and refactor the existing **SQLAlchemy/SQLite** connection layer to load configuration dynamically from our new centralized settings.
> 2. Create a clean, lazy-loaded MongoDB connection helper (`app/database_mongo.py`) that safely handles MongoDB connections only if `pymongo` is installed and a MongoDB URI is supplied, ensuring the application starts successfully without `pymongo` installed.
>
> **Backward-Compatible User Model**: The user model is utilized by the curriculum progress engine and seed scripts (referencing `password_hash`, `is_admin`, `streak_count`, etc.). We will:
> 1. Rename `password_hash` to `hashed_password` as requested.
> 2. Add `updated_at`.
> 3. Keep the other fields (`is_admin`, `streak_count`, `last_active`) intact so that existing seeding scripts and progress tracking functionalities do not break.
> 4. Propagate the change from `password_hash` to `hashed_password` in repositories and seed scripts to prevent compilation and startup crashes.

## Open Questions

> [!IMPORTANT]
> - **MongoDB Transition**: Does the team plan to migrate the primary data store (including curriculum, roadmaps, and progress) to MongoDB in future sprints, or should we continue to use SQLAlchemy (SQLite/MySQL/PostgreSQL) as the primary store while keeping MongoDB optional? We assume SQLite/SQLAlchemy remains primary for now.

---

## Proposed Changes

### Configuration Layer

#### [NEW] [settings.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/config/settings.py)
Create a centralized settings class using standard library utilities and `dotenv` to load:
* `DATABASE_URL` (SQLite file path or MySQL/PostgreSQL connection string)
* `MONGODB_URL` & `MONGODB_DB_NAME` (For MongoDB setup)
* `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` (For JWT)
* `CORS_ALLOWED_ORIGINS`

#### [NEW] [.env](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/.env)
Create a local environment configuration file with default settings matching SQLite.

---

### Database Connection Layer

#### [MODIFY] [database.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/database.py)
Refactor the SQLAlchemy connection setup to pull configuration parameters directly from `app.config.settings.settings` instead of calling `os.getenv` locally.

#### [NEW] [database_mongo.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/database_mongo.py)
Create a modular, safe MongoDB connection helper. It will lazy-load `pymongo` imports and raise structured errors if a MongoDB connection is attempted without the package installed, ensuring zero startup errors.

---

### Data Models & Schemas

#### [MODIFY] [user.py (Model)](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/models/user.py)
* Rename `password_hash` column to `hashed_password`.
* Add `updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)`.
* Retain compatibility columns: `is_admin`, `streak_count`, `last_active`.

#### [NEW] [auth.py (Schema)](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/schemas/auth.py)
Define validation schemas:
* `RegisterRequest`: validating `name`, `email`, and `password`.
* `LoginRequest`: validating `email` and `password`.
* `UserResponse`: output structure containing `id`, `name`, `email`, `created_at`, `updated_at`, and optional attributes.
* `TokenResponse`: output structure containing `access_token` and `token_type`.

#### [MODIFY] [\_\_init\_\_.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/schemas/__init__.py)
Cleanly export the new authentication schemas to make them globally accessible.

---

### Code Alignment & Cleaning Routes

#### [MODIFY] [user_repo.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/repositories/user_repo.py)
Update references of `password_hash` to `hashed_password` in creation queries.

#### [MODIFY] [seeding_service.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/services/seeding_service.py)
Update admin creation query from `password_hash` to `hashed_password` to prevent seeding runtime failures.

#### [MODIFY] [auth.py (Routes)](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/routes/auth.py)
Ensure that **no authentication endpoints exist** yet by commenting out or deleting the `/register`, `/login`, and `/me` routes from the active router, while maintaining dependencies needed for current API runs.

---

## Verification Plan

### Automated Tests
* Execute the FastAPI development startup command to verify compile safety:
  ```powershell
  .\venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
  ```
* Run a Python import check to verify schemas and models import correctly:
  ```powershell
  .\venv\Scripts\python.exe -c "from app.models.user import User; from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenResponse; print('Imports verified successfully!')"
  ```

### Manual Verification
* Navigate to `http://127.0.0.1:8001/docs` in the browser or check using a GET request to verify that `/api/auth/register` and `/api/auth/login` endpoints are **not** present in the swagger spec.
