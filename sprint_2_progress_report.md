# Sprint 2 Progress Report

All core objectives for **Sprint 2 (Curriculum Engine & End-to-End Learning Flow)** have been implemented, verified, and are fully operational. There are no compilation or runtime errors.

---

## Sprint 2 Status Summary

| Phase / Feature Area | Task | Status | Details |
| :--- | :--- | :--- | :--- |
| **Curriculum Engine** | Folder-based JSON Seeding | **Completed** | Auto-scans subdirectories and parses domain metadata & topic files under `backend/seed/dsa/`. |
| **Backend API Router** | Curriculum & Question Endpoints | **Completed** | Full validation using Pydantic, proper status codes, and integrated progress payload queries. |
| **Unlock Logic** | Dynamic Topic Unlocking | **Completed** | Unlocks subsequent topics immediately when cumulative prerequisites reach the defined $\ge 30\%$ unlock percentage. |
| **Progress Engine** | Real-time Progress Tracking | **Completed** | DB transaction automatically recalculates question, concept, pattern, and topic progress on a solve event. |
| **Frontend UI/UX** | Domain Selection, Roadmap, Workspace | **Completed** | High-fidelity glassmorphic cards, SVG path nodes, and interactive 2-pane workbenches. |
| **System Verification** | End-to-End Student Flow | **Completed** | Validated registration $\rightarrow$ roadmap locks $\rightarrow$ question completion $\rightarrow$ roadmap auto-unlock. |

---

## Key Achievements & Implementation Details

### 1. Dynamic Seeding System
We successfully decoupled the curriculum structure from code:
- **Location**: `backend/seed/`
- **Sub-folders**: Directory name represents the domain slug (e.g. `dsa/`).
- **Domain Metadata**: `domain.json` defines domain properties.
- **Topic Configuration**: Separated into 9 JSON files (`arrays.json`, `strings.json`, etc.). Adding a new topic JSON auto-registers it upon running the seeding command:
  ```bash
  backend/venv/Scripts/python -m backend.app.seed
  ```

### 2. Progress & Auto-Unlock Flow
When a user updates a question's solve status (`PATCH /api/questions/{id}/solve`):
1. **UserProgress**: Updates solve state and notes.
2. **UserTopicProgress**: Recalculates solved counts.
3. **Unlock Check**: Iterates through subsequent topics to evaluate prerequisites completion percentages, toggling `is_unlocked` in real-time.

> [!NOTE]
> All changes are executed under a single database transaction, ensuring the client UI reflects progress immediately on the screen without reloading.

### 3. Frontend Pages Overview
- **Domain Selection (`/domains`)**: Custom grid of card components highlighting active learning tracks and locking upcoming tracks.
- **Roadmap (`/domains/dsa/roadmap`)**: Alternating left-right timeline nodes representing topics. Connected with a glowing SVG vector line. Unlocked nodes are active, while locked ones display required prerequisite paths.
- **Topic Workspace (`/topics/:topicSlug`)**: Split-pane workbench:
  - *Left sidebar*: Tree navigation of patterns and concepts with completed check indicators.
  - *Right workspace*: Custom-rendered theory explanation (supporting markdown blockquotes and code syntax highlighting) and the interactive **Question Table** component.

---

## Health & Compilation Check

- **FastAPI Backend Server**: **Running** on `http://127.0.0.1:8000`. No startup warnings or database schema errors.
- **Vite Frontend Dev Server**: **Running** on `http://localhost:5173/`. Compilation completes cleanly with zero console runtime exceptions.
- **TypeScript & Import Fixes**: Restructured runtime imports of interfaces/types in `TopicPage.tsx` to `import type { Question }` to guarantee successful compilation in direct-serve Vite builds.
