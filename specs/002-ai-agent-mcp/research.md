# Research: AI Agent-Driven Todo Management

**Feature**: 002-ai-agent-mcp
**Date**: 2026-01-22
**Status**: Complete

## Technology Decisions

### 1. OpenAI Agents SDK for Agent Orchestration

**Decision**: Use `openai-agents` Python package (latest stable version)

**Rationale**:
- Native support for tool-based execution with automatic execution loop
- Built-in session management (SQLite, Redis) for conversation context
- Direct MCP server integration via `MCPServerStdio` and `MCPServerStreamableHttp`
- Handles tool calls, responses, and error propagation automatically
- Supports both sync and async execution patterns

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| LangChain Agents | More complex setup, less native tool support |
| Raw OpenAI API | No built-in session management, manual tool loop |
| Autogen | Overkill for single-agent use case |

**Key API Patterns**:
```python
from agents import Agent, Runner, SQLiteSession, function_tool

agent = Agent(
    name="Todo Manager",
    instructions="...",
    tools=[...],
)

result = await Runner.run(agent, user_input, session=session)
```

### 2. Model Context Protocol (MCP) for Tool Definitions

**Decision**: Use `mcp` Python SDK with FastMCP framework

**Rationale**:
- Standardized tool schema using JSON Schema
- Decorator-based tool definitions with automatic schema generation
- Native integration with OpenAI Agents SDK
- Supports type annotations and Pydantic constraints for validation
- Clean separation between agent logic and API integration

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Direct function tools | Less structured, no standard validation |
| Custom tool protocol | Non-standard, more maintenance |
| LangChain Tools | Tied to LangChain ecosystem |

**Key API Patterns**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Todo MCP Server")

@mcp.tool()
def create_todo(title: str, description: str = None) -> dict:
    """Create a new todo item."""
    # Call REST API
    pass
```

### 3. Transport Mechanism

**Decision**: stdio transport for MCP server

**Rationale**:
- Simplest integration with OpenAI Agents SDK
- Server runs as subprocess, managed by agent process
- No additional HTTP server required for MCP layer
- Sufficient for CLI-based Phase III (single user)
- Easy local development and testing

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Streamable HTTP | Overhead for single-user CLI |
| SSE | Deprecated, being replaced |

### 4. Session Management

**Decision**: SQLite-based session storage via `SQLiteSession`

**Rationale**:
- Built into OpenAI Agents SDK
- Persistent conversation context within a session
- No additional database infrastructure
- Suitable for single-user CLI application
- Easy to clear/reset for testing

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Redis | Requires additional infrastructure |
| In-memory only | No persistence between CLI invocations |
| PostgreSQL | Overkill for Phase III scope |

### 5. HTTP Client for REST API Calls

**Decision**: `httpx` with async support

**Rationale**:
- Modern Python HTTP client with async support
- Type-safe response handling
- Connection pooling
- Already a dependency of OpenAI SDK
- Clean error handling

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| requests | No native async support |
| aiohttp | Less clean API, more verbose |

## Architecture Decisions

### Agent-MCP-API Flow

```
User Input (CLI)
    ↓
AI Agent (OpenAI Agents SDK)
    ↓ tool calls
MCP Server (FastMCP, stdio transport)
    ↓ HTTP requests
Phase II REST API (FastAPI)
    ↓ database operations
Neon PostgreSQL
```

**Key Properties**:
1. Agent has no direct database access (FR-005)
2. All mutations go through MCP tools (FR-004)
3. MCP server validates inputs before forwarding to API
4. API errors propagate back as tool errors

### Tool Design

Per spec requirements FR-006 through FR-011:

| Tool | Parameters | Returns | Spec Ref |
|------|------------|---------|----------|
| `create_todo` | title (required), description | Created todo object | FR-006 |
| `list_todos` | filter (all/pending/completed) | Array of todos | FR-007 |
| `get_todo` | id | Single todo object | FR-008 |
| `update_todo` | id, title?, description? | Updated todo object | FR-009 |
| `toggle_todo` | id | Updated todo object | FR-010 |
| `delete_todo` | id | Success confirmation | FR-011 |

### Error Handling Strategy

1. **MCP Layer**: Validate inputs, raise `ToolError` for invalid params
2. **HTTP Layer**: Catch `HTTPStatusError`, convert to tool errors
3. **Agent Layer**: Receives tool errors, responds with user-friendly message

```python
@mcp.tool()
def get_todo(id: int) -> dict:
    try:
        response = client.get(f"{API_BASE}/todos/{id}")
        if response.status_code == 404:
            raise ToolError(f"Todo with ID {id} not found")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise ToolError(f"API error: {e.response.status_code}")
```

## Dependencies

### Runtime Dependencies

```
openai-agents>=0.1.0
mcp[cli]>=1.0.0
httpx>=0.25.0
pydantic>=2.0.0
```

### Development Dependencies

```
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-httpx>=0.30.0
```

## Constitution Alignment

The original constitution (Phase I) specifies:
- In-memory only
- Single module
- No external dependencies
- CLI-first interface

**Phase III Deviations (Justified)**:

| Constitution Rule | Phase III Approach | Justification |
|-------------------|-------------------|---------------|
| In-memory only | Uses Phase II database via API | Agent doesn't access DB directly; uses REST API |
| Single module | Multiple modules (agent, MCP server) | Separation of concerns for agent architecture |
| No external deps | OpenAI SDK, MCP SDK, httpx | Required for AI agent functionality |
| CLI-first | CLI chat interface | Maintains CLI-first principle |

The constitution applies to the core todo application. Phase III is an **augmentation layer** that interacts with the existing system through its public API.

## Open Questions Resolved

All technical unknowns have been resolved:

- [x] OpenAI Agents SDK patterns - documented above
- [x] MCP tool definition format - documented above
- [x] Transport mechanism - stdio chosen
- [x] Session management - SQLite chosen
- [x] Error handling patterns - three-tier strategy documented

## References

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [FastMCP Documentation](https://gofastmcp.com/servers/tools)
- [Phase II OpenAPI Contract](../001-fullstack-todo/contracts/openapi.yaml)
