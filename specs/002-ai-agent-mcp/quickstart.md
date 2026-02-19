# Quickstart: AI Agent-Driven Todo Management

**Feature**: 002-ai-agent-mcp
**Prerequisites**: Phase II backend running (`http://localhost:8000`)

## Prerequisites

1. **Python 3.11+** installed
2. **Phase II backend** running and accessible
3. **OpenAI API key** (set as environment variable)

## Installation

```bash
# From repository root
cd agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Unix/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create `.env` file in `agent/` directory:

```env
OPENAI_API_KEY=sk-your-api-key-here
TODO_API_BASE_URL=http://localhost:8000
```

## Running the Agent

### Option 1: CLI Mode (Recommended for Phase III)

```bash
# Start the agent CLI
python -m agent.cli

# You'll see a prompt:
# Todo Manager Agent (type 'quit' to exit)
# ----------------------------------------
# You:
```

### Option 2: Single Command Mode

```bash
# Run a single command
python -m agent.cli "Show me all my todos"

# Output:
# Here are your current todos:
# - [ ] Buy groceries
# - [x] Review PR #123
```

## Example Interactions

### Creating Todos

```
You: Add a task to buy groceries
Assistant: Created todo: "Buy groceries"

You: I need to call mom this weekend
Assistant: Created todo: "Call mom this weekend"

You: Create a task called "Review quarterly report" with description "Q4 2025 financials"
Assistant: Created todo: "Review quarterly report" with description "Q4 2025 financials"
```

### Listing and Summarizing

```
You: Show me all my tasks
Assistant: Here are your current todos:
- [ ] Buy groceries
- [ ] Call mom this weekend
- [x] Review quarterly report (completed)

You: What should I do today?
Assistant: You have 2 pending tasks:
1. Buy groceries
2. Call mom this weekend

I'd suggest starting with "Call mom this weekend" since it has a time-specific context.
```

### Completing and Updating

```
You: Mark "Buy groceries" as done
Assistant: Done! "Buy groceries" is now marked as complete.

You: Actually, change it to "Buy groceries and snacks"
Assistant: Updated "Buy groceries" to "Buy groceries and snacks"

You: Complete all my tasks
Assistant: I found 2 pending tasks. Would you like me to mark all of them as complete?
- Buy groceries and snacks
- Call mom this weekend
```

### Deleting

```
You: Delete the grocery task
Assistant: Are you sure you want to delete "Buy groceries and snacks"? This cannot be undone.

You: Yes, delete it
Assistant: Deleted "Buy groceries and snacks"
```

### Task Prioritization

```
You: I have an urgent deadline for the report
Assistant: I notice "urgent" and "deadline" - would you like me to create a high-priority task for this, or mark an existing todo as urgent?

You: What's most urgent right now?
Assistant: Looking at your todos, I found these with urgency indicators:
1. [URGENT] Deadline for quarterly report - due today
2. Call mom this weekend - time-specific but not urgent
```

### Task Breakdown

```
You: I need to plan a vacation to Japan
Assistant: Created todo: "Plan vacation to Japan"

Would you like me to break this down into smaller tasks? A typical vacation plan might include:
- Research flights
- Book accommodation
- Create itinerary
- Apply for visa (if needed)

You: Yes, break it down
Assistant: I've created 4 subtasks:
- Research flights to Japan
- Book accommodation in Japan
- Create Japan itinerary
- Check visa requirements for Japan
```

## Session Management

The agent maintains conversation context within a session:

```
You: Create a task to review the PR
Assistant: Created todo: "Review the PR"

You: Actually, mark that as done
Assistant: Done! "Review the PR" is now marked as complete.
```

To start a fresh session:

```bash
# Clear session and start fresh
python -m agent.cli --reset
```

## Troubleshooting

### API Connection Issues

```
You: Show my todos
Assistant: I'm having trouble reaching the todo service. Please make sure the backend is running at http://localhost:8000

# Check backend status:
curl http://localhost:8000/api/todos
```

### OpenAI API Issues

```bash
# Verify API key is set
echo $OPENAI_API_KEY  # Unix
echo %OPENAI_API_KEY%  # Windows

# Test with a simple request
python -c "from agents import Agent, Runner; print('SDK loaded')"
```

### Session Issues

```bash
# Clear corrupted session
rm -rf ~/.todo-agent/sessions.db

# Or use the reset flag
python -m agent.cli --reset
```

## Running Tests

```bash
# From repository root
pytest agent/tests/ -v

# Run specific test categories
pytest agent/tests/test_mcp_server.py -v  # MCP server tests
pytest agent/tests/test_agent.py -v       # Agent tests
pytest agent/tests/test_integration.py -v # Integration tests
```

## Project Structure

```
agent/
├── __init__.py
├── cli.py              # CLI entry point
├── agent.py            # Agent configuration
├── mcp_server.py       # MCP server with tool definitions
├── config.py           # Configuration loading
├── requirements.txt    # Python dependencies
└── tests/
    ├── test_agent.py
    ├── test_mcp_server.py
    └── test_integration.py
```

## Next Steps

After confirming the agent works:

1. Run the full test suite: `pytest agent/tests/ -v`
2. Test edge cases (ambiguous requests, API errors)
3. Verify conversation context persistence
4. Test concurrent sessions (if applicable)
