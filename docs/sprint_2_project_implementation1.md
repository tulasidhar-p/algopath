# Sprint 2 Implementation Plan: Curriculum Engine & End-to-End Learning Flow

This plan outlines the technical changes and structure required to deliver Sprint 2, establishing the core learning engine of **AlgoPath** with interactive visual styling.

---

## Proposed Architecture & Changes

### 1. Seeding Refactoring (Curriculum Engine)
We will transition from a single `seed_data.json` to a dynamic, folder-based seeding model under `backend/seed/`.

- **Directory Structure**:
  - `backend/seed/dsa/domain.json` (metadata for DSA domain)
  - `backend/seed/dsa/arrays.json` (arrays curriculum)
  - `backend/seed/dsa/strings.json` (strings curriculum)
  - `backend/seed/dsa/linked_list.json` (linked list curriculum)
  - `backend/seed/dsa/stack.json` (stack curriculum)
  - `backend/seed/dsa/queue.json` (queue curriculum)
  - `backend/seed/dsa/trees.json` (trees curriculum)
  - `backend/seed/dsa/graphs.json` (graphs curriculum)
  - `backend/seed/dsa/dp.json` (dynamic programming curriculum)

- **Seeding Service (`seeding_service.py`)**:
  - Automatically scan all subdirectories under `backend/seed/`.
  - Treat each subdirectory name as a domain slug.
  - Read `domain.json` for domain metadata (name, description, order_index).
  - Scan and load all other `.json` files inside the domain directory as Topic configurations.
  - Dynamically populate `Topic`, `Pattern`, `Concept`, and `Question` records in order.
  - Track prerequisites as lists of topic slugs in JSON and bind them after all topics are seeded.

---

## Proposed Changes

### Backend Components

#### [NEW] [curriculum.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/routes/curriculum.py)
This router will handle all learning content retrieval and progress updates.
- `GET /api/domains`: List all domains.
- `GET /api/domains/{slug}`: Fetch specific domain.
- `GET /api/domains/{slug}/roadmap`: Fetch domain structure with user topic progress and unlock states.
- `GET /api/topics/{slug}`: Fetch nested patterns, concepts, questions, and the user's solve statuses.
- `GET /api/topics/{slug}/progress`: Fetch progress data for a topic.
- `GET /api/patterns/{slug}`: Fetch pattern details and its concepts/questions.
- `GET /api/concepts/{slug}`: Fetch concept details with full theory markdown.
- `GET /api/questions`: List all questions.
- `GET /api/questions/{id}`: Fetch single question with user progress (solved, bookmark, notes).
- `PATCH /api/questions/{id}/solve`: Set solve status, calculate progress, and dynamically unlock next topics.
- `PATCH /api/questions/{id}/bookmark`: Bookmark or unbookmark a question.

#### [NEW] [curriculum.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/schemas/curriculum.py)
Define validation schemas for curriculum objects and progress stats:
- `DomainResponse`, `TopicResponse`, `PatternResponse`, `ConceptResponse`, `QuestionResponse` (with status, bookmark, notes).
- `SolveRequest`, `BookmarkRequest` schemas.
- Progress wrapper schemas.

#### [MODIFY] [seeding_service.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/services/seeding_service.py)
Refactor `seed_database` to dynamically scan directories and load topic files.

#### [MODIFY] [main.py](file:///d:/Projects/Antigravity/project%201/project%201.1/backend/app/main.py)
Include the curriculum router: `app.include_router(curriculum.router)`.

---

### Progress & Unlock Engine

- **Progress Calculations**:
  - When `PATCH /api/questions/{id}/solve` is triggered, insert or update `UserProgress` (mark `status = "solved"` or `"unsolved"`).
  - Recalculate the corresponding topic's solved count for this user in `UserTopicProgress`.
  - Update `UserTopicProgress.solved_count`.
- **Unlock Logic**:
  - Run check on all topics in the active domain:
    - For each topic, verify all prerequisites are unlocked and their completion rate (solved questions / total questions) is $\ge$ `unlock_percentage` (default 30%).
    - If prerequisites are satisfied, set `UserTopicProgress.is_unlocked = True`.

---

### Frontend Components (React + Tailwind CSS)

#### [NEW] [DomainSelection.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/pages/DomainSelection.tsx)
- Premium landing dashboard with dark glassmorphic cards.
- Show "Data Structures & Algorithms" as active.
- Show "Web Development", "Data Analysis", and "AI/ML" as "Coming Soon" with muted, blurred overlays and locks.

#### [NEW] [Roadmap.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/pages/Roadmap.tsx)
- Vertical or horizontal path nodes representing DSA topics connected by glowing SVG lines.
- Color code nodes:
  - **Completed**: Green glow, check icon.
  - **In Progress**: Indigo pulse, active.
  - **Locked**: Grayed out with lock icon. Shows hover info like "Requires 30% completion of [Prereq Topic]".

#### [NEW] [TopicPage.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/pages/TopicPage.tsx)
- Left panel listing sub-patterns.
- Main area displaying:
  - Selected concept's theory editor (rendered Markdown).
  - Interactive **Question Table** filtered by pattern or displaying all topic questions.
  - Real-time progress bar (e.g., "7/22 Questions Solved").

#### [NEW] [QuestionTable.tsx](file:///d:/Projects/Antigravity/project%201/project%201.1/frontend/src/components/QuestionTable.tsx)
- Columns: Title (link to external problem), Difficulty (color badge), Platform (badge), Solve Time (e.g., 30m), Solved Checkbox, Bookmark Star.
- Interactive actions to mark solved and bookmark immediately.

---

## Verification Plan

### Automated Verification
- Run database seeding command: `python -m backend.app.seed`
- Verify OpenAPI Swagger docs at `http://localhost:8000/docs`.
- Test solving questions and observe automatic topic progress and unlocks.

### Manual Verification
- Walk through end-to-end user flow:
  1. Register/Login.
  2. Select DSA Domain.
  3. Inspect DSA Roadmap (check locked/unlocked nodes).
  4. Open "Arrays" topic.
  5. Read "1D Prefix Sum Basics" theory.
  6. Solve "Range Sum Query - Immutable" (mark solved, check status update).
  7. Check if topic completion updates in real-time.
  8. Unlocking check: verify next topic unlocks after 30% threshold is met.
