# Tasks: AI Agent-Driven Todo Management

**Input**: Design documents from `/specs/002-ai-agent-mcp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec. Test tasks included for critical paths only.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
- Agent code: `agent/`
- Tests: `agent/tests/`
- Backend (existing): `backend/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create agent project structure and install dependencies

- [x] T001 Create agent directory structure per plan.md: `agent/`, `agent/tests/`
- [x] T002 Create `agent/__init__.py` with package metadata
- [x] T003 [P] Create `agent/requirements.txt` with runtime dependencies (openai-agents, mcp[cli], httpx, pydantic, python-dotenv)
- [x] T004 [P] Create `agent/tests/__init__.py` and `agent/tests/conftest.py` with pytest fixtures
- [x] T005 Create `.env.example` with required environment variables (OPENAI_API_KEY, TODO_API_BASE_URL)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: All user stories depend on MCP server and agent configuration being in place

- [x] T006 Create `agent/config.py` with environment loading (dotenv, API base URL, OpenAI settings)
- [x] T007 Define system prompt in `agent/agent.py` per contracts/agent-config.json (role, tone, available tools, instructions, safety rules)
- [x] T008 Implement `create_todo` MCP tool in `agent/mcp_server.py` (FR-006)
- [x] T009 Implement `list_todos` MCP tool in `agent/mcp_server.py` (FR-007)
- [x] T010 Implement `get_todo` MCP tool in `agent/mcp_server.py` (FR-008)
- [x] T011 Implement `update_todo` MCP tool in `agent/mcp_server.py` (FR-009)
- [x] T012 Implement `toggle_todo` MCP tool in `agent/mcp_server.py` (FR-010)
- [x] T013 Implement `delete_todo` MCP tool in `agent/mcp_server.py` (FR-011)
- [x] T014 Add MCP tool error handling with user-friendly messages in `agent/mcp_server.py` (FR-018, NFR-003)
- [x] T015 Initialize OpenAI Agents SDK client in `agent/agent.py` with model settings
- [x] T016 Wire agent to MCP server using stdio transport in `agent/agent.py`
- [x] T017 Implement basic CLI entry point in `agent/cli.py` with input loop
- [x] T018 Add session management using SQLiteSession in `agent/agent.py` (FR-016)

**Checkpoint**: Foundation ready - agent can accept input and call MCP tools. User story implementation can begin.

---

## Phase 3: User Story 1 - Natural Language Todo Creation (Priority: P1)

**Goal**: Users can create todos using natural language like "Add a task to buy groceries"

**Independent Test**: Send "Add a task to review the quarterly report" and verify todo is created with correct title

### Implementation for User Story 1

- [x] T019 [US1] Enhance system prompt with todo creation instructions in `agent/agent.py`
- [x] T020 [US1] Add title extraction logic from natural language in agent reasoning
- [x] T021 [US1] Implement clarification behavior for ambiguous create requests in `agent/agent.py` (FR-017)
- [x] T022 [US1] Add confirmation message after successful creation

**Checkpoint**: User Story 1 complete - natural language todo creation works independently

---

## Phase 4: User Story 2 - Natural Language Todo Operations (Priority: P1)

**Goal**: Users can update, complete, and delete todos using natural language

**Independent Test**: Create a todo, then use "Mark [title] as done" to complete it

### Implementation for User Story 2

- [x] T023 [US2] Enhance system prompt with update/toggle/delete instructions in `agent/agent.py`
- [x] T024 [US2] Implement todo matching logic to find todos by title/description in agent reasoning
- [x] T025 [US2] Add confirmation prompt before delete operations in `agent/agent.py` (FR-019)
- [x] T026 [US2] Implement disambiguation when multiple todos match in `agent/agent.py` (FR-020)
- [x] T027 [US2] Add bulk operation support (e.g., "complete all shopping tasks")

**Checkpoint**: User Stories 1 and 2 complete - full CRUD via natural language works

---

## Phase 5: User Story 3 - Todo Summarization (Priority: P2)

**Goal**: Users can ask "What should I do today?" and get a prioritized summary

**Independent Test**: Create several todos, ask "Summarize my tasks" and verify accurate summary

### Implementation for User Story 3

- [x] T028 [US3] Enhance system prompt with summarization instructions in `agent/agent.py` (FR-013)
- [x] T029 [US3] Implement pending task summary logic in agent reasoning
- [x] T030 [US3] Implement completed task summary logic for "What have I accomplished?"
- [x] T031 [US3] Add empty state handling when no todos exist

**Checkpoint**: User Story 3 complete - todo summarization works

---

## Phase 6: User Story 4 - Task Prioritization (Priority: P2)

**Goal**: Agent suggests priorities based on urgency cues (urgent, ASAP, deadline)

**Independent Test**: Create todos with urgency keywords, ask "What's most urgent?" and verify ranking

### Implementation for User Story 4

- [x] T032 [US4] Enhance system prompt with urgency detection instructions in `agent/agent.py` (FR-014)
- [x] T033 [US4] Implement urgency keyword detection (urgent, ASAP, deadline, today, important, critical)
- [x] T034 [US4] Add priority ranking logic in agent reasoning
- [x] T035 [US4] Implement clarification for todos without clear urgency

**Checkpoint**: User Story 4 complete - prioritization suggestions work

---

## Phase 7: User Story 5 - Task Breakdown Suggestions (Priority: P3)

**Goal**: Agent suggests breaking down complex todos into subtasks

**Independent Test**: Create "Plan vacation to Japan", ask "Can you break this down?" and verify subtask suggestions

### Implementation for User Story 5

- [x] T036 [US5] Enhance system prompt with task breakdown instructions in `agent/agent.py` (FR-015)
- [x] T037 [US5] Implement complexity detection in agent reasoning
- [x] T038 [US5] Add subtask suggestion generation
- [x] T039 [US5] Implement user approval flow for creating subtasks
- [x] T040 [US5] Add atomic task detection (e.g., "Buy milk" doesn't need breakdown)

**Checkpoint**: User Story 5 complete - task breakdown suggestions work

---

## Phase 8: User Story 6 - Conversational Context (Priority: P3)

**Goal**: Agent maintains context for natural follow-up interactions

**Independent Test**: Create a todo, then say "Actually, mark that as done" - agent should understand "that"

### Implementation for User Story 6

- [x] T041 [US6] Enhance session management for context persistence in `agent/agent.py`
- [x] T042 [US6] Implement pronoun resolution for recent todos ("that", "it", "the first one")
- [x] T043 [US6] Add context reference from previous agent responses
- [x] T044 [US6] Implement graceful context loss handling for new sessions

**Checkpoint**: User Story 6 complete - conversational context works

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting all user stories

- [x] T045 [P] Add `--reset` flag to CLI for session clearing in `agent/cli.py`
- [x] T046 [P] Add single-command mode to CLI (`python -m agent.cli "message"`)
- [x] T047 [P] Create unit tests for MCP tools in `agent/tests/test_mcp_server.py`
- [x] T048 [P] Create integration tests for agent behavior in `agent/tests/test_agent.py`
- [x] T049 Add graceful shutdown handling in `agent/cli.py`
- [x] T050 Validate against quickstart.md scenarios
- [x] T051 Add timeout handling for OpenAI API calls (NFR-001)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup → No dependencies
Phase 2: Foundational → Depends on Phase 1
Phase 3-8: User Stories → All depend on Phase 2 completion
Phase 9: Polish → Depends on desired user stories
```

### User Story Dependencies

All user stories can proceed independently after Phase 2:

| User Story | Priority | Can Start After | Dependencies on Other Stories |
|------------|----------|-----------------|-------------------------------|
| US1: Create | P1 | Phase 2 | None |
| US2: Operations | P1 | Phase 2 | None (independent CRUD) |
| US3: Summarization | P2 | Phase 2 | None |
| US4: Prioritization | P2 | Phase 2 | None |
| US5: Breakdown | P3 | Phase 2 | Relies on US1 for subtask creation |
| US6: Context | P3 | Phase 2 | Integrates with all stories |

### Within Each User Story

1. Enhance system prompt first
2. Implement core logic
3. Add edge case handling
4. Verify independently

### Parallel Opportunities

**Phase 1 (all parallel)**:
```
T003 (requirements.txt) || T004 (test init) || T005 (.env.example)
```

**Phase 2 (MCP tools parallel)**:
```
T008 (create_todo) || T009 (list_todos) || T010 (get_todo) || T011 (update_todo) || T012 (toggle_todo) || T013 (delete_todo)
```

**Phase 9 (polish parallel)**:
```
T045 (reset flag) || T046 (single-command) || T047 (MCP tests) || T048 (agent tests)
```

---

## Parallel Example: Phase 2 MCP Tools

```bash
# Launch all MCP tool implementations together:
Task: "Implement create_todo MCP tool in agent/mcp_server.py"
Task: "Implement list_todos MCP tool in agent/mcp_server.py"
Task: "Implement get_todo MCP tool in agent/mcp_server.py"
Task: "Implement update_todo MCP tool in agent/mcp_server.py"
Task: "Implement toggle_todo MCP tool in agent/mcp_server.py"
Task: "Implement delete_todo MCP tool in agent/mcp_server.py"
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T018)
3. Complete Phase 3: User Story 1 - Create (T019-T022)
4. Complete Phase 4: User Story 2 - Operations (T023-T027)
5. **STOP and VALIDATE**: Test with quickstart.md scenarios

At this point you have a functional agent that can:
- Create todos via natural language
- List, update, toggle, and delete todos via natural language
- Ask for confirmation before deletions
- Handle errors gracefully

### Incremental Delivery

| Milestone | Stories Complete | Value Delivered |
|-----------|-----------------|-----------------|
| MVP | US1 + US2 | Full CRUD via natural language |
| +Summarization | +US3 | "What should I do today?" |
| +Prioritization | +US4 | Urgency-based suggestions |
| +Breakdown | +US5 | Complex task decomposition |
| +Context | +US6 | Natural follow-ups |

---

## Task Summary

| Phase | Task Count | Description |
|-------|------------|-------------|
| Phase 1: Setup | 5 | Project initialization |
| Phase 2: Foundational | 13 | MCP server, agent, CLI |
| Phase 3: US1 Create | 4 | Natural language creation |
| Phase 4: US2 Operations | 5 | Update, toggle, delete |
| Phase 5: US3 Summarization | 4 | Todo summaries |
| Phase 6: US4 Prioritization | 4 | Urgency detection |
| Phase 7: US5 Breakdown | 5 | Task decomposition |
| Phase 8: US6 Context | 4 | Conversation persistence |
| Phase 9: Polish | 7 | Tests, cleanup, validation |
| **Total** | **51** | |

### By User Story

| Story | Tasks | Spec Refs |
|-------|-------|-----------|
| US1: Create | 4 | FR-006, FR-012, FR-017 |
| US2: Operations | 5 | FR-009-011, FR-019-020 |
| US3: Summarization | 4 | FR-013 |
| US4: Prioritization | 4 | FR-014 |
| US5: Breakdown | 5 | FR-015 |
| US6: Context | 4 | FR-016 |

---

## Notes

- [P] tasks can run in parallel (different files, no dependencies)
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable after Phase 2
- MVP scope: Phase 1-4 (Setup + Foundational + US1 + US2)
- All file paths are relative to repository root
- Phase II backend must be running for integration testing
