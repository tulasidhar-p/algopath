# Implementation Plan - Sprint 2.1 Stabilization & Runtime Bug Fixes

This plan addresses runtime, startup, configuration, dependency, and integration issues in both the backend and frontend to ensure a smooth local execution experience.

## User Review Required

> [!NOTE]
> - We will update the `typescript` version in `frontend/package.json` to `^5.5.2`. This is required because the current compiler settings in `tsconfig.app.json` (such as `target: es2023` and `erasableSyntaxOnly: true`) require TypeScript 5.5+ and fail compilation on the older version `5.2.2`.
> - We will upgrade `lucide-react` to a modern version `^0.468.0` to ensure complete compatibility with React 19.

## Open Questions

None at this stage. The requirements are clear, and the issues have been diagnosed.

---

## Proposed Changes

### Backend

#### [MODIFY] [seed.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/seed.py)
- Modify the `sys.path` append instruction on line 5. Currently, it appends the project root (`project 1.1`), which causes `ModuleNotFoundError: No module named 'app'` when running `python app/seed.py` directly from the `backend/` folder.
- Change it to append the `backend/` directory so that `app` can be imported directly.

```diff
-sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
+sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

#### [MODIFY] [main.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/main.py)
- Update CORS middleware allowed origins to support both `http://localhost:5173` and `http://127.0.0.1:5173` to prevent any cross-origin errors if the frontend is loaded via IP address rather than localhost.

---

### Frontend

#### [MODIFY] [package.json](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/package.json)
- Update typescript version to `^5.5.2` (resolves compilation errors on `erasableSyntaxOnly` and target `es2023`).
- Update `lucide-react` version from the invalid/extremely old `^1.21.0` to `^0.468.0` (resolves compatibility warnings with React 19).

#### [NEW] [.env](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/.env)
- Add a new `.env` file to configure the backend API URL.
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

### Documentation

#### [NEW] [README.md](file:///d:/Projects/Antigravity/project%201/project%201.1/README.md)
- Create a main project README in the root `project 1.1/` with exact step-by-step startup instructions.

---

## Verification Plan

### Automated Tests
- Run `npm run build` in the `frontend/` folder to verify that typescript builds successfully without errors.
- Run `venv\Scripts\python app/seed.py` in the `backend/` folder to verify database tables initialization and seeding runs correctly.

### Manual Verification
- Start backend: `venv\Scripts\python -m uvicorn app.main:app --reload`
- Start frontend: `npm run dev`
- Launch the browser and verify the complete flow:
  1. Register a new user
  2. Login
  3. Select DSA domain
  4. View Roadmap
  5. Select a Topic
  6. Solve a Question and confirm the progress updates
