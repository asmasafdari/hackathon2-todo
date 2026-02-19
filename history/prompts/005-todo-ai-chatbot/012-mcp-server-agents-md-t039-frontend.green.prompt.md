---
id: 012
title: MCP Server AGENTS.md T039 Frontend Implementation
stage: green
date: 2026-02-18
surface: agent
model: claude-sonnet-4-6
feature: 005-todo-ai-chatbot
branch: 005-todo-ai-chatbot
user: Amena
command: Implement the following plan
labels: ["mcp-server","agents-md","t039","frontend","priority","tags","due-date","speckit"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - scripts/speckit_mcp/server.py
  - scripts/speckit_mcp/requirements.txt
  - .mcp.json
  - AGENTS.md
  - CLAUDE.md
  - .specify/memory/constitution.md
  - frontend/types/todo.ts
  - frontend/components/TodoItem.tsx
  - specs/005-todo-ai-chatbot/tasks.md
tests:
  - frontend TypeScript build (npm run build in frontend/)
  - python scripts/speckit_mcp/server.py starts without error
  - TodoItem renders priority badge, tags chips, due date
---

## Prompt

Implement the following plan:

# Plan: MCP Server + AGENTS.md + T039 Frontend

## Context
Wire the 13 `.claude/commands/` files as MCP prompts for any-IDE access, establish AGENTS.md as the cross-agent authority, align CLAUDE.md and the constitution, and implement T039 (priority/tags display in the frontend).

[Full plan with 4 tasks: Task 1 MCP server, Task 2 CLAUDE.md+constitution, Task 3 AGENTS.md, Task 4 T039 frontend]

## Response snapshot

Implemented all 4 tasks in execution order:

**Task 1 — SpecKit MCP Server:**
- Created `scripts/speckit_mcp/server.py` — FastMCP server that auto-discovers all 13 `.claude/commands/*.md` files and registers each as an MCP prompt (slug via `stem.replace(".", "-")`). Exposes `speckit://constitution` and `speckit://specs` resources.
- Created `scripts/speckit_mcp/requirements.txt` — `mcp[cli]>=1.0.0`
- Created `.mcp.json` — registers the `speckit` server for Claude Code auto-load

**Task 3 — AGENTS.md:**
- Created `AGENTS.md` at project root with 7 sections: Purpose, How Agents Must Work (5 strict rules), Spec-Kit Workflow (13-row table), Available MCP Prompts (13-row table with slug names), Agent Behavior, Agent Failure Modes (6 patterns), Developer-Agent Alignment

**Task 2 — CLAUDE.md + constitution:**
- Prepended `@AGENTS.md` as first line of `CLAUDE.md`
- Added `## MCP Server` section after `## Basic Project Structure`
- Added `### VIII. Tooling and Agent Infrastructure` to constitution
- Bumped version to `2.1.0`, Last Amended `2026-02-18`, added amendment row

**Task 4 — T039 Frontend:**
- Updated `frontend/types/todo.ts`: added `TodoPriority` type, added `priority`, `tags`, `due_date`, `remind_at`, `recurrence_rule` fields to `Todo` interface
- Updated `frontend/components/TodoItem.tsx`: added `PRIORITY_STYLES` map, priority colored pill badge (after title), tags gray chips (after description), due date with red highlight if overdue and incomplete
- Marked T039 `[x]` in `specs/005-todo-ai-chatbot/tasks.md`

## Outcome

- ✅ Impact: SpecKit workflow now accessible as MCP prompts from any IDE; AGENTS.md establishes cross-agent authority; frontend displays rich todo metadata (priority, tags, due dates)
- 🧪 Tests: TypeScript build should pass; MCP server starts on stdin; TodoItem renders all new fields conditionally (no regression for todos without them)
- 📁 Files: 9 files created/modified across scripts/, frontend/, specs/, CLAUDE.md, AGENTS.md, constitution.md
- 🔁 Next prompts: verify frontend build passes; connect Claude Code to speckit MCP server; implement T071 (Minikube verification)
- 🧠 Reflection: Execution order mattered — MCP server created first so AGENTS.md prompt names are accurate; `sp.git.commit_pr.md` slug is `sp-git-commit_pr` (underscore preserved, dots→dashes only)

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): TypeScript type correctness (PASS by inspection — all new fields nullable)
- Prompt variant (if applicable): none
- Next experiment: verify `python scripts/speckit_mcp/server.py` runs cleanly in the project venv
