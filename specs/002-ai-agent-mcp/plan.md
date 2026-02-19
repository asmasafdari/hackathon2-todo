# Implementation Plan: AI Agent-Driven Todo Management

**Branch**: `002-ai-agent-mcp` | **Date**: 2026-01-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-ai-agent-mcp/spec.md`

## Summary

Augment the Phase II full-stack todo application with an AI agent that manages todos through natural language. The agent uses the OpenAI Agents SDK for orchestration and Model Context Protocol (MCP) for tool definitions. All todo operations flow through the Phase II REST API - the agent has no direct database access.

**Key Architectural Decision**: The agent layer sits on top of the existing Phase II system, communicating exclusively through the REST API. This maintains the separation of concerns and allows the agent to be developed independently.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: openai-agents, mcp[cli], httpx, pydantic
**Storage**: SQLite (sessions via OpenAI Agents SDK); Phase II database via API
**Testing**: pytest, pytest-asyncio, pytest-httpx
**Target Platform**: Local development (CLI application)
**Project Type**: Single project with CLI interface
**Performance Goals**: <3s agent response latency for simple operations (NFR-001)
**Constraints**: All mutations via MCP tools only (TC-004), no direct DB access (FR-005)
**Scale/Scope**: Single-user CLI, session-based conversation context

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| In-Memory Only | DEVIATION | Agent uses Phase II API (no direct DB); sessions in SQLite |
| Single Module | DEVIATION | Agent requires separate modules (agent, MCP server) |
| No External Deps | DEVIATION | OpenAI SDK, MCP SDK required for AI functionality |
| CLI-First | PASS | Agent interface is CLI-based |
| Input Validation | PASS | MCP layer validates all tool inputs |
| Simplicity | PASS | Minimal viable implementation per spec |

**Deviation Justification**: The constitution applies to the Phase I core application. Phase III is an **augmentation layer** that interacts with the existing system through its public API. The agent does not modify the core todo application - it consumes it as a service.

## Project Structure

### Documentation (this feature)

```text
specs/002-ai-agent-mcp/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technology research
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Getting started guide
├── contracts/           # Phase 1: API contracts
│   ├── mcp-tools.json   # MCP tool definitions
│   └── agent-config.json # Agent configuration schema
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
agent/
├── __init__.py
├── cli.py              # CLI entry point (main interface)
├── agent.py            # Agent configuration and setup
├── mcp_server.py       # MCP server with tool definitions
├── config.py           # Environment and configuration loading
├── requirements.txt    # Python dependencies
└── tests/
    ├── __init__.py
    ├── conftest.py     # pytest fixtures
    ├── test_agent.py   # Agent behavior tests
    ├── test_mcp_server.py  # MCP tool tests
    └── test_integration.py # End-to-end tests

backend/                # Phase II (existing)
├── main.py
├── models.py
├── database.py
├── routers/
│   └── todos.py
└── services/
    └── todo_service.py
```

**Structure Decision**: Single `agent/` directory for all Phase III code. Separate from `backend/` (Phase II) to maintain clear boundaries. Agent communicates with backend via HTTP only.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User (CLI)                              │
└─────────────────────────────────────────────────────────────┘
                           │ natural language
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI Agent (OpenAI Agents SDK)               │
│  - Interprets user intent                                   │
│  - Maintains conversation context (SQLite session)          │
│  - Decides which tools to call                              │
└─────────────────────────────────────────────────────────────┘
                           │ tool calls (JSON)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   MCP Server (FastMCP, stdio)                │
│  - Validates tool inputs                                    │
│  - Maps tools to REST API calls                             │
│  - Returns structured responses                             │
└─────────────────────────────────────────────────────────────┘
                           │ HTTP requests
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Phase II REST API (FastAPI)                │
│  - /api/todos (CRUD operations)                             │
│  - /api/todos/{id}/toggle                                   │
└─────────────────────────────────────────────────────────────┘
                           │ SQL
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database (Neon PostgreSQL)                 │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. stdio Transport for MCP

**Decision**: Use stdio transport (subprocess) instead of HTTP

**Rationale**:
- Simplest integration with OpenAI Agents SDK
- No additional HTTP server needed for MCP layer
- Sufficient for single-user CLI application
- Server lifecycle managed by agent process

### 2. SQLite Session Storage

**Decision**: Use SQLite via `SQLiteSession` for conversation context

**Rationale**:
- Built into OpenAI Agents SDK
- Persists between CLI invocations
- No additional infrastructure needed
- Easy to clear/reset for testing

### 3. Confirmation for Destructive Actions

**Decision**: Agent asks for confirmation before delete operations

**Rationale**:
- Spec requirement FR-019
- Prevents accidental data loss
- Better user experience

### 4. Error Message Strategy

**Decision**: User-friendly errors, no technical details exposed

**Rationale**:
- Spec requirement NFR-003
- Agent translates API errors to natural language
- Example: 404 → "I couldn't find a todo with that ID"

## Dependencies

### Runtime

```
openai-agents>=0.1.0    # Agent orchestration
mcp[cli]>=1.0.0         # MCP protocol and FastMCP
httpx>=0.25.0           # Async HTTP client
pydantic>=2.0.0         # Data validation
python-dotenv>=1.0.0    # Environment loading
```

### Development

```
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-httpx>=0.30.0
```

## MCP Tools Summary

| Tool | Purpose | Spec Ref |
|------|---------|----------|
| `create_todo` | Create new todo with title/description | FR-006 |
| `list_todos` | List todos with optional filter | FR-007 |
| `get_todo` | Get single todo by ID | FR-008 |
| `update_todo` | Update todo title/description | FR-009 |
| `toggle_todo` | Toggle completion status | FR-010 |
| `delete_todo` | Delete todo (with confirmation) | FR-011 |

See [contracts/mcp-tools.json](contracts/mcp-tools.json) for full schema.

## Testing Strategy

| Test Type | Coverage | Location |
|-----------|----------|----------|
| Unit | MCP tool validation, error handling | `agent/tests/test_mcp_server.py` |
| Integration | Agent + MCP + mock API | `agent/tests/test_agent.py` |
| E2E | Full flow with real backend | `agent/tests/test_integration.py` |

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI API latency | User experience | Set reasonable timeouts, provide feedback |
| Context window limits | Long conversations fail | Session truncation, summarization |
| API unavailability | Agent cannot function | Graceful error messages, retry logic |

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| External dependencies (OpenAI SDK, MCP) | Core requirement for AI agent functionality | Native implementation would require reimplementing agent orchestration |
| Multiple modules | Separation of concerns (agent, MCP, CLI) | Single module would violate SRP and make testing difficult |
| SQLite session storage | Conversation context persistence (FR-016) | In-memory only would lose context between CLI invocations |

## Related Documents

- [Feature Specification](spec.md)
- [Research Findings](research.md)
- [Data Model](data-model.md)
- [Quickstart Guide](quickstart.md)
- [MCP Tool Contracts](contracts/mcp-tools.json)
- [Agent Configuration](contracts/agent-config.json)
- [Phase II OpenAPI](../001-fullstack-todo/contracts/openapi.yaml)
