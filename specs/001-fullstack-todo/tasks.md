# Tasks: Phase II - Fullstack Todo Application

**Input**: Design documents from `/specs/001-fullstack-todo/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Not explicitly requested in specification. Tests are NOT included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` - FastAPI + SQLModel
- **Frontend**: `frontend/` - Next.js App Router
- Per plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both backend and frontend

- [x] T001 Create project directory structure per plan.md (backend/, frontend/)
- [x] T002 [P] Initialize Python backend with FastAPI in backend/main.py and backend/requirements.txt
- [x] T003 [P] Initialize Next.js frontend with App Router in frontend/ (npx create-next-app)
- [x] T004 [P] Configure Tailwind CSS in frontend/tailwind.config.js and frontend/app/globals.css
- [x] T005 [P] Create backend/.env.example with DATABASE_URL placeholder
- [x] T006 [P] Create frontend/.env.local.example with NEXT_PUBLIC_API_URL placeholder

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Implement database connection with async SQLModel in backend/database.py
- [x] T008 Create SQLModel Todo models (Todo, TodoBase, TodoCreate, TodoUpdate, TodoRead) in backend/models.py
- [x] T009 Implement database table initialization function in backend/database.py
- [x] T010 [P] Configure CORS middleware for localhost:3000 in backend/main.py
- [x] T011 [P] Create TypeScript Todo interfaces in frontend/types/todo.ts
- [x] T012 [P] Create API client base with fetch wrapper in frontend/lib/api.ts
- [x] T013 Create TodoService class with CRUD methods in backend/services/todo_service.py
- [x] T014 Create API router structure in backend/routers/todos.py (empty endpoints)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View All Todos (Priority: P1)

**Goal**: Users can open the web application and see a list of all their existing todos

**Independent Test**: Load the web page and verify todos from the database are displayed correctly with title, status, and creation date

### Implementation for User Story 1

- [x] T015 [US1] Implement GET /api/todos endpoint (list all) in backend/routers/todos.py
- [x] T016 [US1] Add get_all_todos method to TodoService in backend/services/todo_service.py
- [x] T017 [US1] Wire GET /api/todos router to main app in backend/main.py
- [x] T018 [US1] Implement fetchTodos API function in frontend/lib/api.ts
- [x] T019 [US1] Create TodoList component in frontend/components/TodoList.tsx
- [x] T020 [US1] Create TodoItem component (display only) in frontend/components/TodoItem.tsx
- [x] T021 [US1] Implement home page with todo list in frontend/app/page.tsx
- [x] T022 [US1] Add loading state to TodoList in frontend/components/TodoList.tsx
- [x] T023 [US1] Add empty state message when no todos exist in frontend/components/TodoList.tsx
- [x] T024 [US1] Add error handling for failed API calls in frontend/app/page.tsx

**Checkpoint**: User Story 1 complete - users can view all todos with empty state and error handling

---

## Phase 4: User Story 2 - Create a New Todo (Priority: P1)

**Goal**: Users can add a new task via form and see it immediately appear in the list

**Independent Test**: Fill out the create form, submit it, verify the new todo appears and persists after refresh

### Implementation for User Story 2

- [x] T025 [US2] Implement POST /api/todos endpoint (create) in backend/routers/todos.py
- [x] T026 [US2] Add create_todo method to TodoService in backend/services/todo_service.py
- [x] T027 [US2] Add title validation (non-empty, trim whitespace) in backend/models.py
- [x] T028 [US2] Implement createTodo API function in frontend/lib/api.ts
- [x] T029 [US2] Create TodoForm component in frontend/components/TodoForm.tsx
- [x] T030 [US2] Add form validation (prevent empty title submission) in frontend/components/TodoForm.tsx
- [x] T031 [US2] Integrate TodoForm into home page in frontend/app/page.tsx
- [x] T032 [US2] Add optimistic UI update after create in frontend/app/page.tsx
- [x] T033 [US2] Add loading state during form submission in frontend/components/TodoForm.tsx

**Checkpoint**: User Story 2 complete - users can create todos with validation and immediate feedback

---

## Phase 5: User Story 3 - Toggle Todo Completion (Priority: P2)

**Goal**: Users can mark a todo as complete/incomplete with a single click and see immediate visual feedback

**Independent Test**: Click the toggle control on a todo, verify status changes visually and persists after refresh

### Implementation for User Story 3

- [x] T034 [US3] Implement PATCH /api/todos/{id}/toggle endpoint in backend/routers/todos.py
- [x] T035 [US3] Add toggle_todo method to TodoService in backend/services/todo_service.py
- [x] T036 [US3] Add 404 handling for non-existent todo in toggle endpoint
- [x] T037 [US3] Implement toggleTodo API function in frontend/lib/api.ts
- [x] T038 [US3] Add checkbox/toggle control to TodoItem in frontend/components/TodoItem.tsx
- [x] T039 [US3] Add visual distinction for completed todos (strikethrough) in frontend/components/TodoItem.tsx
- [x] T040 [US3] Wire toggle handler to update list state in frontend/app/page.tsx

**Checkpoint**: User Story 3 complete - users can toggle completion status with visual feedback

---

## Phase 6: User Story 4 - Update an Existing Todo (Priority: P2)

**Goal**: Users can edit the title or description of an existing todo

**Independent Test**: Click edit on a todo, modify the text, save, verify changes appear and persist

### Implementation for User Story 4

- [x] T041 [US4] Implement PUT /api/todos/{id} endpoint (update) in backend/routers/todos.py
- [x] T042 [US4] Add update_todo method to TodoService in backend/services/todo_service.py
- [x] T043 [US4] Add 404 handling for non-existent todo in update endpoint
- [x] T044 [US4] Implement updateTodo API function in frontend/lib/api.ts
- [x] T045 [US4] Add edit mode to TodoItem (inline editing) in frontend/components/TodoItem.tsx
- [x] T046 [US4] Add save/cancel buttons for edit mode in frontend/components/TodoItem.tsx
- [x] T047 [US4] Wire update handler to refresh list state in frontend/app/page.tsx

**Checkpoint**: User Story 4 complete - users can edit todos inline with save/cancel

---

## Phase 7: User Story 5 - Delete a Todo (Priority: P3)

**Goal**: Users can permanently remove a todo from their list

**Independent Test**: Click delete on a todo, verify it no longer appears in the list or database

### Implementation for User Story 5

- [x] T048 [US5] Implement DELETE /api/todos/{id} endpoint in backend/routers/todos.py
- [x] T049 [US5] Add delete_todo method to TodoService in backend/services/todo_service.py
- [x] T050 [US5] Add 404 handling for non-existent todo in delete endpoint
- [x] T051 [US5] Implement deleteTodo API function in frontend/lib/api.ts
- [x] T052 [US5] Add delete button to TodoItem in frontend/components/TodoItem.tsx
- [x] T053 [US5] Add confirmation before delete (optional) in frontend/components/TodoItem.tsx
- [x] T054 [US5] Wire delete handler to remove from list state in frontend/app/page.tsx

**Checkpoint**: User Story 5 complete - users can delete todos with confirmation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T055 [P] Add consistent error message component in frontend/components/ErrorMessage.tsx
- [x] T056 [P] Add loading spinner component in frontend/components/LoadingSpinner.tsx
- [x] T057 Implement global error boundary in frontend/app/layout.tsx
- [x] T058 [P] Add page metadata (title, description) in frontend/app/layout.tsx
- [x] T059 Review and apply consistent styling across all components
- [x] T060 Validate implementation against quickstart.md setup guide
- [x] T061 Manual end-to-end testing of all user flows

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS all user stories
    ↓
Phase 3-7 (User Stories) ← Can run in priority order or parallel
    ↓
Phase 8 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 - View All | Foundational | Phase 2 complete |
| US2 - Create | Foundational | Phase 2 complete |
| US3 - Toggle | Foundational | Phase 2 complete |
| US4 - Update | Foundational | Phase 2 complete |
| US5 - Delete | Foundational | Phase 2 complete |

**Note**: User stories are designed to be independently implementable. However, recommended order is P1 → P2 → P3 for logical feature progression.

### Within Each User Story

1. Backend endpoint implementation
2. Backend service method
3. Frontend API client function
4. Frontend component implementation
5. Integration and state management

### Parallel Opportunities

**Phase 1 Setup (can run in parallel)**:
- T002 (backend init) || T003 (frontend init)
- T004, T005, T006 can all run in parallel

**Phase 2 Foundational (can run in parallel)**:
- T010 (CORS) || T011 (TS types) || T012 (API client)

**Across User Stories** (after Phase 2):
- Different developers can work on different user stories simultaneously
- US1 and US2 are both P1 and can be done in parallel

---

## Parallel Example: Phase 1 Setup

```bash
# Launch these in parallel:
Task: "Initialize Python backend with FastAPI in backend/main.py"
Task: "Initialize Next.js frontend with App Router in frontend/"
Task: "Configure Tailwind CSS in frontend/tailwind.config.js"
Task: "Create backend/.env.example with DATABASE_URL placeholder"
Task: "Create frontend/.env.local.example with NEXT_PUBLIC_API_URL"
```

---

## Parallel Example: User Story 1 + User Story 2

After Phase 2 completes, two developers can work in parallel:

**Developer A (US1 - View)**:
```bash
Task: "Implement GET /api/todos endpoint in backend/routers/todos.py"
Task: "Create TodoList component in frontend/components/TodoList.tsx"
```

**Developer B (US2 - Create)**:
```bash
Task: "Implement POST /api/todos endpoint in backend/routers/todos.py"
Task: "Create TodoForm component in frontend/components/TodoForm.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (View All Todos)
4. Complete Phase 4: User Story 2 (Create Todo)
5. **STOP and VALIDATE**: Test viewing and creating todos
6. Deploy/demo if ready - this is a functional MVP!

### Incremental Delivery

| Increment | User Stories | Functionality |
|-----------|--------------|---------------|
| MVP | US1 + US2 | View list, create todos |
| +Toggle | US3 | Mark complete/incomplete |
| +Edit | US4 | Update existing todos |
| +Delete | US5 | Remove todos |
| Polish | N/A | Error handling, styling |

### Suggested MVP Scope

**Minimum Viable Product**: User Stories 1 and 2 (View + Create)
- Users can see their todo list
- Users can add new todos
- Data persists in database

This provides immediate value and validates the full stack integration.

---

## Task Summary

| Phase | Tasks | Parallel | Story Coverage |
|-------|-------|----------|----------------|
| Setup | 6 | 5 | N/A |
| Foundational | 8 | 3 | N/A |
| US1 - View | 10 | 0 | P1 |
| US2 - Create | 9 | 0 | P1 |
| US3 - Toggle | 7 | 0 | P2 |
| US4 - Update | 7 | 0 | P2 |
| US5 - Delete | 7 | 0 | P3 |
| Polish | 7 | 3 | N/A |
| **Total** | **61** | **11** | **5 stories** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend runs on port 8000, frontend on port 3000
