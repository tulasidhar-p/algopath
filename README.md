# AlgoPath - Multi-Domain Study Planner Platform

This is a stabilization release (Sprint 2.1) ensuring correct local environment setup, runtime imports, frontend dependency resolution, and centralized API communication.

---

## Startup Instructions

### 1. Backend Startup

The backend is built with FastAPI. To start the backend:

1. Open a terminal and navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```
3. (First-time / Reset) Initialize the database tables and seed curriculum data:
   ```bash
   python -m app.seed
   ```
4. Start the development server on port **8001** (or your preferred port):
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

### 2. Frontend Startup

The frontend is built with React, TypeScript, and Vite. To start the frontend:

1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install the dependencies cleanly:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173`.

---

## Configuring the Backend Port

By default, the backend port is set to **8001** in the frontend's `.env` configuration to prevent conflicts and align with typical local setups.

If you need to run the backend on a different port (e.g., port **8000** or **8080**):

1. **Start the backend** with your chosen port:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
2. **Update the frontend configuration** by editing the `.env` file in the `frontend/` directory:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```
3. The frontend centralized API client (`frontend/src/services/api.ts`) will automatically pick up this change and route all requests (Authentication, Curriculum, Question solving, and Bookmarks) to the new address.
