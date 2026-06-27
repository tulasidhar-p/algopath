# Implementation Plan - AlgoPath Multi-Domain Learning Platform

This plan details how to build and execute **AlgoPath** inside the workspace `d:\Projects\Antigravity\project 1\project 1.1` as a production-ready, multi-domain learning platform using FastAPI and React + TypeScript + Tailwind CSS.

---

## Goal Description

Build a scalable, multi-domain study platform (supporting DSA, Web Development, Data Analysis, and AI/ML). The application will start with a fully-featured DSA curriculum and progress-tracking workbench. The backend is designed with a top-level `Domain` model, allowing additional domains to be added in the future with zero database schema modifications.

---

## User Review Required

> [!IMPORTANT]
> **Database Dialect**: The backend will support both local development (SQLite via file path) and production (PostgreSQL via environment variables).
> 
> **Admin Privileges**: We will add an `is_admin` boolean flag to the `User` model. The admin panel features (creating/updating domains, topics, patterns, and questions) will require this flag to be `True`. We will seed one admin account by default during database creation.
> 
> **UI Aesthetic**: To prevent Vite/Tailwind build issues or interactive CLI hanging during `npx shadcn-ui init`, we will construct pre-styled, high-fidelity components (e.g., Dialog, Progress, Alerts, Tooltips) directly using Tailwind CSS and React hooks. They will emulate the dark-theme shadcn/ui aesthetic perfectly (slate borders, neon accents, clean typography, smooth transitions).

---

## Open Questions

- *Do you have a specific username/password format you would like to use for the seeded admin user, or is a default admin email like `admin@algopath.com` with password `AdminPassword123!` acceptable?*
- *Should we enforce sequential unlocking (e.g., Topic 2 only unlocks when Topic 1 is 30% solved) across all domains, or should this be configurable per domain? (We will default to enforcing it per domain).*

---

## Proposed Changes

We will copy the prototype base from `c:\Users\pottu\.gemini\antigravity-ide\scratch\algopath` to our workspace root `d:\Projects\Antigravity\project 1\project 1.1` and perform modular upgrades.

### Backend Setup (`backend/`)

#### [NEW] [models.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/models.py)
Create SQLAlchemy models including:
- `User` (adding `is_admin` column)
- `Domain` (new table mapping to domains like DSA, Web Dev, etc.)
- `Topic` (updated with `domain_id` ForeignKey)
- `Pattern` (linked to `Topic`)
- `Question` (linked to `Topic` and `Pattern`)
- `UserProgress` (saves question status and notes)
- `UserTopicProgress` (caches completed counts)

#### [NEW] [database.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/database.py)
Establish session maker. Reads `DATABASE_URL` from env; defaults to SQLite `sqlite:///./algopath.db` for development or connects to PostgreSQL.

#### [NEW] [auth.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/auth.py)
JWT credentials helper, password hashing, and token verification.

#### [NEW] [main.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/main.py)
Entrypoint registering FastAPI application, CORS middleware, and API router.

#### [NEW] [routes/admin.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/routes/admin.py)
CRUD routes for domains, topics, patterns, and questions, restricted to `current_user.is_admin == True`.

#### [NEW] [routes/domains.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/routes/domains.py)
Endpoints for getting domains, individual roadmaps, and topic unlock lists.

#### [NEW] [seed.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/seed.py)
Database seeding script to initialize the "dsa" domain, its 15 topics (Arrays to Tries), patterns, questions, and the default admin user.

---

### Frontend Setup (`frontend/`)

We will create a clean React + TypeScript + Tailwind workspace inside `frontend/`.

#### [NEW] [tsconfig.json](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/tsconfig.json)
Configure TypeScript rules for compiler options, imports, and React JSX files.

#### [NEW] [package.json](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/package.json)
Include dependencies: React 18, React Router DOM, Axios, Lucide React, Tailwind CSS, Autoprefixer, PostCSS.

#### [NEW] [src/context/AuthContext.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/context/AuthContext.tsx)
Context for managing login states, JWT tokens, user profiles, and checking `is_admin`.

#### [NEW] [src/pages/DomainSelection.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/pages/DomainSelection.tsx)
Cards for selecting domains. DSA is active; Web Development, Data Analysis, and AI/ML show custom "Locked / Coming Soon" graphics.

#### [NEW] [src/pages/Dashboard.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/pages/Dashboard.tsx)
Contains the interactive roadmap graph, completion percentages, streak metrics, and difficulty breakdowns.

#### [NEW] [src/pages/TopicPage.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/pages/TopicPage.tsx)
The practice workbench. Contains:
- Left Column: Patterns navigation
- Middle Column: Search, filters (Easy/Med/Hard, Solved/Starred), and questions list
- Right Column: Autosaved markdown notes block

#### [NEW] [src/pages/AdminPanel.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/pages/AdminPanel.tsx)
Admin dashboard showing tables of Domains, Topics, Patterns, and Questions with modal forms to Add, Edit, or Delete them.

---

## Verification Plan

### Automated Tests
- Script a basic database connection test.
- Verify backend FastAPI app builds and registers all endpoints successfully.

### Manual Verification
1. Run backend server: `uvicorn backend.main:app --reload` and check docs at `http://localhost:8000/docs`.
2. Seed the database (`python -m backend.seed`) and verify data imports correctly.
3. Build and launch the React+TS dev server (`npm run dev`) and test:
   - Login / Register workflows.
   - Domain selection -> Roadmap view.
   - Solving questions, updating status (solved, revisit), and typing debounced notes.
   - Accessing `/admin` page using an admin account vs a normal user account to test route safety.
