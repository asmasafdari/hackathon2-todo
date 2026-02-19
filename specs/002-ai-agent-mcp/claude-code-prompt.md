# Claude Code Implementation Prompt: Phase III AI Agent MCP

Use this prompt to instruct Claude Code to implement Phase III of the desktop-todo application.

---

## Prompt

```
Implement Phase III: AI Agent-Driven Todo Management for the desktop-todo application.

## Project Context

This is a 3-phase todo application:
- Phase I: CLI todo app (Python, in-memory)
- Phase II: Full-stack web app (FastAPI backend + React frontend, PostgreSQL)
- Phase III (this phase): AI Agent layer using OpenAI Agents SDK + MCP

The Phase II backend is already running at http://localhost:8000 with these endpoints:
- GET /api/todos - List all todos
- POST /api/todos - Create todo (body: {title, description?})
- GET /api/todos/{id} - Get single todo
- PUT /api/todos/{id} - Update todo (body: {title?, description?})
- PATCH /api/todos/{id}/toggle - Toggle completion status
- DELETE /api/todos/{id} - Delete todo

Todo schema: {id: UUID, title: string, description?: string, completed: boolean, created_at: datetime}

## What to Build

Create an `agent/` directory with a CLI-based AI agent that:
1. Accepts natural language input from users
2. Uses OpenAI Agents SDK for orchestration
3. Exposes MCP tools that call the Phase II REST API
4. Maintains conversation context for follow-up references

## Architecture

```
User (CLI) → OpenAI Agents SDK → MCP Server (stdio) → HTTP → Phase II REST API
```

## Files to Create

agent/
├── __init__.py           # Package marker, version
├── __main__.py           # Module entry point
├── config.py             # Pydantic Settings (env vars)
├── mcp_server.py         # FastMCP server with 6 tools
├── agent.py              # Agent setup, system prompt
├── cli.py                # CLI entry point
├── requirements.txt      # Dependencies
├── .env.example          # Environment template
├── pytest.ini            # Test config
└── tests/
    ├── __init__.py
    ├── conftest.py       # Fixtures
    └── test_mcp_server.py

## MCP Tools to Implement

| Tool | HTTP Method | Endpoint | Notes |
|------|-------------|----------|-------|
| create_todo | POST | /api/todos | title required, description optional |
| list_todos | GET | /api/todos | filter param: all/pending/completed (client-side) |
| get_todo | GET | /api/todos/{id} | UUID parameter |
| update_todo | PUT | /api/todos/{id} | At least one field required |
| toggle_todo | PATCH | /api/todos/{id}/toggle | Flip completion status |
| delete_todo | DELETE | /api/todos/{id} | Return {success: true, deleted_id} |

## Requirements

### Dependencies (requirements.txt)
```
openai-agents>=0.1.0
mcp[cli]>=1.0.0
httpx>=0.25.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

### Environment Variables
- OPENAI_API_KEY (required)
- TODO_API_BASE_URL (default: http://localhost:8000)
- REQUEST_TIMEOUT (default: 30)

### Error Handling
- 404 → "I couldn't find that todo"
- Connection error → "I'm having trouble reaching the todo service"
- Timeout → "Request took too long, please try again"
- Never expose stack traces or technical errors to users

### CLI Features
- Interactive mode: `python -m agent.cli` with "You: " prompt
- Single command: `python -m agent.cli "add buy groceries"`
- Exit on: quit, exit, q, Ctrl+C
- --reset flag to clear conversation context

### Agent Behavior (System Prompt Requirements)
1. **Delete Confirmation**: Always ask before deleting - "Delete '[title]'? Reply 'yes' to confirm."
2. **Ambiguity**: If unclear, list options and ask user to specify
3. **Context References**: Handle "that", "it", "the first one" from conversation
4. **Urgency Detection**: Recognize urgent/ASAP/deadline/today keywords
5. **Empty States**: Helpful messages when no todos exist
6. **Concise Responses**: 1-3 lines for simple actions, use checkboxes [ ] [✓]

## System Prompt Template

The agent system prompt should include:
- Personality (friendly, efficient, concise)
- Tool reference table
- Behavioral rules (especially delete confirmation)
- Response formatting guidelines
- Multi-turn conversation patterns
- Edge case handling
- "What NOT to do" guardrails

## Testing Requirements

Unit tests for each MCP tool covering:
- Successful operations
- 404 handling (TodoNotFoundError)
- Connection error handling
- Filter logic for list_todos

Use fixtures for:
- sample_todo (pending)
- sample_todo_completed
- mock_http_client
- mock_response_factory

## Verification

After implementation, test with:
1. Start backend: `cd backend && uvicorn main:app --reload`
2. Install deps: `cd agent && pip install -r requirements.txt`
3. Set env: `export OPENAI_API_KEY=your-key`
4. Run CLI: `python -m agent.cli`
5. Test: "Add buy groceries" → "Show tasks" → "Mark first as done" → "Delete that"
6. Run tests: `pytest agent/tests/ -v`

## Success Criteria
- [ ] CLI accepts natural language input
- [ ] "Add X" creates a todo
- [ ] "Show tasks" lists todos
- [ ] "Mark X as done" toggles completion
- [ ] "Delete X" asks for confirmation
- [ ] Errors are user-friendly
- [ ] Tests pass
```

---

## Usage

Copy the prompt above (between the ``` markers) and paste it into Claude Code or any AI coding assistant that can create files and write code.

## Post-Implementation Checklist

After Claude Code completes the implementation:

1. **Verify file structure**
   ```bash
   ls -la agent/
   ls -la agent/tests/
   ```

2. **Install dependencies**
   ```bash
   cd agent && pip install -r requirements.txt
   ```

3. **Run tests**
   ```bash
   pytest agent/tests/ -v
   ```

4. **Test interactively** (requires backend running)
   ```bash
   export OPENAI_API_KEY=your-key
   python -m agent.cli
   ```

5. **Verify behaviors**
   - Create: "Add a task to buy groceries"
   - List: "Show all my tasks"
   - Toggle: "Mark the first one as done"
   - Delete: "Delete that task" (should confirm)
   - Context: "Actually undo that" (should understand reference)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "OPENAI_API_KEY not set" | Export the environment variable |
| Connection refused | Ensure Phase II backend is running on port 8000 |
| Import errors | Run from project root, not agent/ directory |
| MCP server fails | Check Python path in MCPServerStdio command |
