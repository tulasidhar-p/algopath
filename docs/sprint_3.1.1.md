# Implementation Plan - Sprint 3.1 – Phase 1: Authentication Foundation

This plan establishes the revised foundational authentication architecture for **AlgoPath**. The system will continue to use the existing **FastAPI + SQLAlchemy + SQLite** architecture, structured to support a future transition to **PostgreSQL** by updating configuration. In this phase, we centralize configurations, update the User model, define schemas, and ensure the backend starts successfully with all authentication endpoints temporarily disabled.

## User Review Required

> [!IMPORTANT]
> **SQLAlchemy SQLite & PostgreSQL Portability**: The database configuration is centralized in `app/config/settings.py` and consumed by the connection layer in `app/database.py`. SQLite will be used for Sprint 3, but the engine is configured to check dialect compatibility (e.g., configuring `check_same_thread=False` only when using SQLite) to allow a simple swap to PostgreSQL via the `DATABASE_URL` environment variable.
>
> **Backward Compatibility Safeguards**: 
> 1. Renaming `password_hash` to `hashed_password` in the `User` model requires us to update database references in `user_repo.py` and `seeding_service.py` so that existing seeding scripts and data operations function smoothly.
> 2. Existing user-tracking fields (`is_admin`, `streak_count`, `last_active`) are preserved in both the model and the `UserResponse` schema to prevent breaking the frontend dashboard and curriculum engines.
> 3. Database migrations / DDL updates: Since SQLite is used in development and has limited support for altering columns directly, we will rename the column and add `updated_at`. If the local SQLite database file `algopath.db` causes column mismatches, running seed operations (`python -m backend.seed` or `python backend/app/seed.py`) will re-create and populate the schema from scratch.

## Open Questions

> [!NOTE]
> None. All architectural constraints have been fully specified by the user.

---

## Proposed Changes

### Configuration Layer

#### [NEW] [settings.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/config/settings.py)
Create a centralized settings model to load configuration from environment variables with safe defaults:
* `DATABASE_URL` (default: `sqlite:///./algopath.db`)
* `SECRET_KEY` (JWT signature key; default: `"algo-path-super-secret-key-32-chars-long!"`)
* `ALGORITHM` (default: `"HS256"`)
* `ACCESS_TOKEN_EXPIRE_MINUTES` (default: `10080` (7 days))
* `CORS_ALLOWED_ORIGINS` (default: `"http://localhost:5173,http://127.0.0.1:5173"`)

#### [NEW] [.env](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/.env)
Create a `.env` template in the backend root with appropriate development defaults.

---

### Database Connection Layer

#### [MODIFY] [database.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/database.py)
Refactor to read `DATABASE_URL` directly from the centralized `settings` module. Retain connection argument logic (`check_same_thread=False` only when using `sqlite`) to maintain compatibility with SQLite and ensure easy transition to PostgreSQL.

---

### Data Models & Repositories

#### [MODIFY] [user.py (Model)](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/models/user.py)
* Rename `password_hash` column to `hashed_password` (String(255), nullable=False).
* Add `updated_at` column (DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False).
* Preserve existing columns: `is_admin`, `streak_count`, `last_active`, `created_at`.

#### [MODIFY] [user_repo.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/repositories/user_repo.py)
Update all references of `password_hash` to `hashed_password` inside queries and entity creation hooks.

---

### Schemas

#### [NEW] [auth.py (Schema)](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/schemas/auth.py)
Define production-quality validation schemas using Pydantic:
* `RegisterRequest`: validating `name` (str), `email` (EmailStr), and `password` (str).
* `LoginRequest`: validating `email` (EmailStr) and `password` (str).
* `UserResponse`: output structure containing `id`, `name`, `email`, `created_at`, `updated_at`, and backward-compatible fields `is_admin`, `streak_count`, `last_active`.
* `TokenResponse`: output structure containing `access_token` and `token_type` (default "bearer").

#### [MODIFY] [\_\_init\_\_.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/schemas/__init__.py)
Export the newly created schemas (`RegisterRequest`, `LoginRequest`, `UserResponse`, `TokenResponse`) to be globally importable under `app.schemas`.

---

### Services & Routes Alignments

#### [MODIFY] [seeding_service.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/services/seeding_service.py)
Update admin seed initialization to map the generated password hash to `hashed_password` instead of `password_hash`.

#### [MODIFY] [auth_service.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/services/auth_service.py)
Update password verification and token utilities to query `hashed_password` from the `User` model.

#### [MODIFY] [auth.py (Routes)](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/routes/auth.py)
To satisfy the requirement *"No authentication endpoints exist yet"*, temporarily comment out or delete the path operations (`/register`, `/login`, `/me`) from `routes/auth.py`, returning a clean `router = APIRouter(prefix="/api/auth", tags=["Authentication"])` without routes.

---

## Verification Plan

### Automated Tests
* Run the schema and import verification scripts to guarantee zero syntax or import errors:
  ```powershell
  .\venv\Scripts\python.exe -c "from app.config.settings import settings; from app.models.user import User; from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenResponse; print('Python imports and syntax checks passed!')"
  ```
* Test startup behavior of the FastAPI backend application:
  ```powershell
  .\venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
  ```

### Manual Verification
* Access the Swagger docs at `http://127.0.0.1:8001/docs` to check that:
  1. The API starts and compiles without warnings or errors.
  2. No `/api/auth/register`, `/api/auth/login`, or `/api/auth/me` endpoints are exposed in the endpoints list.
  3. The schema objects (`RegisterRequest`, `LoginRequest`, `UserResponse`, `TokenResponse`) are loaded and recognized by FastAPI.
