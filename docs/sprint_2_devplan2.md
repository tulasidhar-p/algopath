# Implementation Plan - Sprint 2.1 Stabilization & Runtime Bug Fixes

This plan addresses runtime, startup, configuration, dependency, and integration issues in both the backend and frontend to ensure a smooth local execution experience.

## User Review Required

> [!NOTE]
> - We will update the `typescript` version in `frontend/package.json` to `^5.5.2`. This resolves the target compiler settings mismatch (such as `target: es2023` and `erasableSyntaxOnly: true`) that fail compilation on the older version `5.2.2`.
> - We will upgrade `lucide-react` to a modern version `^0.468.0` to ensure complete compatibility with React 19.
> - We will create a centralized API client `frontend/src/services/api.ts` that automatically reads the base URL from `import.meta.env.VITE_API_BASE_URL` and attaches the authorization headers dynamically. All components and pages using Axios will be refactored to use this client.
> - We will create a `.env` file in the frontend configured with `VITE_API_BASE_URL=http://127.0.0.1:8001` (to match the user's running backend port of 8001).

## Open Questions

None. All details are specified.

---

## Proposed Changes

### Backend

#### [MODIFY] [seed.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/seed.py)
- Modify the `sys.path` append instruction on line 5 so it appends the correct `backend/` root directory instead of the grandparent project root. This ensures running `python app/seed.py` from within the `backend/` folder resolves the `app` package.

```diff
-sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
+sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

#### [MODIFY] [main.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/main.py)
- Allow CORS from both `http://localhost:5173` and `http://127.0.0.1:5173` to prevent CORS issues if the frontend uses localhost vs the loopback IP.

---

### Frontend

#### [NEW] [api.ts](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/services/api.ts)
- Create a centralized API client. It reads the base URL from `import.meta.env.VITE_API_BASE_URL` (with no hardcoded fallback port in files) and uses a request interceptor to automatically attach authorization tokens from localStorage.

#### [MODIFY] [package.json](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/package.json)
- Update typescript version to `^5.5.2`.
- Update `lucide-react` version to `^0.468.0`.

#### [NEW] [.env](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/.env)
- Configure the API base URL matching the backend running port of `8001`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8001
```

#### [NEW] [.env.example](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/.env.example)
- Add a template `.env.example` file.

#### [MODIFY] [AuthContext.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/context/AuthContext.tsx)
- Refactor to use the centralized API client.
- Eliminate `API_BASE_URL` definition and imports.

#### [MODIFY] [Roadmap.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/pages/Roadmap.tsx)
- Refactor all axios calls to use the centralized API client.
- Eliminate `API_BASE_URL` import.

#### [MODIFY] [TopicPage.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/pages/TopicPage.tsx)
- Refactor all axios calls to use the centralized API client.
- Eliminate `API_BASE_URL` import.

---

### Documentation

#### [NEW] [README.md](file:///d:/Projects/Antigravity/project%201/project%201.1/README.md)
- Create a comprehensive root-level `README.md` file listing startup instructions, how to build/run, and detailing how the backend port can be changed easily.

---

## Verification Plan

### Automated Tests
- Run `npm run build` in `frontend/` to verify clean compilation.
- Run `venv\Scripts\python app/seed.py` in `backend/` to verify database seeding.

### Manual Verification
- Start backend: `venv\Scripts\python -m uvicorn app.main:app --reload --port 8001`
- Start frontend: `npm run dev`
- Run the browser integration tests (using browser subagent) to check:
  1. Login and registration flows.
  2. Domain selection (`dsa`).
  3. Opening topic roadmap and specific topics.
  4. Solving questions and verifying successful API responses.
