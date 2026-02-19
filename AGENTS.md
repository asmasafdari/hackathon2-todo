# AGENTS.md — Cross-Agent Authority

> **This file is the authoritative cross-agent reference for all AI agents working in this repository.**
> Claude Code loads this via the `@AGENTS.md` shim in `CLAUDE.md`.

---

## 1. Purpose

This repository follows **Spec-Driven Development (SDD)**: every feature starts with a spec, progresses through a plan and tasks, and is implemented test-first. No code is written without a task ID. No task is created without a plan. No plan without a spec.

The SDD workflow is enforced by 13 commands in `.claude/commands/` and exposed as MCP prompts via the SpecKit MCP server.

---

## 2. How Agents Must Work

Agents operating in this repository MUST follow these rules strictly:

1. **No spec, no plan** — Never create a plan (`/sp.plan`) without a spec (`/sp.specify`) in `specs/<feature>/spec.md`.
2. **No plan, no tasks** — Never generate tasks (`/sp.tasks`) without a completed plan in `specs/<feature>/plan.md`.
3. **No tasks, no code** — Never write implementation code without an active task ID from `specs/<feature>/tasks.md`.
4. **Smallest viable diff** — All changes must be the minimum required. No refactoring of unrelated code.
5. **PHR is mandatory** — After every substantive user interaction, create a Prompt History Record via `/sp.phr`.
6. **Surface ADR suggestions** — When a significant architectural decision is made, suggest (never auto-create) an ADR: `📋 Architectural decision detected: <brief> — Document? Run /sp.adr <title>`.

---

## 3. Spec-Kit Workflow

| Stage | Command | What It Does |
|-------|---------|--------------|
| Constitution | `/sp.constitution` | Create or update project principles in `.specify/memory/constitution.md` |
| Specify | `/sp.specify` | Create or update the feature spec in `specs/<feature>/spec.md` |
| Clarify | `/sp.clarify` | Identify underspecified areas; ask up to 5 targeted questions and encode answers back into spec |
| Analyze | `/sp.analyze` | Non-destructive cross-artifact consistency check across spec, plan, and tasks |
| Plan | `/sp.plan` | Generate architecture plan in `specs/<feature>/plan.md` |
| Tasks | `/sp.tasks` | Generate dependency-ordered task list in `specs/<feature>/tasks.md` |
| Implement | `/sp.implement` | Execute the implementation plan by processing tasks from tasks.md |
| ADR | `/sp.adr` | Review planning artifacts and create an Architecture Decision Record |
| PHR | `/sp.phr` | Record an AI exchange as a Prompt History Record for traceability |
| Checklist | `/sp.checklist` | Generate a custom checklist for the current feature |
| Issues | `/sp.taskstoissues` | Convert tasks.md entries into GitHub Issues |
| Git | `/sp.git.commit_pr` | Autonomously execute git workflow: commit work and create PR |
| Reverse-Engineer | `/sp.reverse-engineer` | Reverse engineer a codebase into SDD-RI artifacts (spec, plan, tasks, intelligence) |

---

## 4. Available MCP Prompts

The SpecKit MCP server (`scripts/speckit_mcp/server.py`) auto-discovers `.claude/commands/` and registers one prompt per file. Connect via `.mcp.json` at the project root.

| Prompt Name | Source File | When to Use |
|-------------|-------------|-------------|
| `sp-constitution` | `sp.constitution.md` | Starting a new project or amending principles |
| `sp-specify` | `sp.specify.md` | Creating or updating a feature spec |
| `sp-clarify` | `sp.clarify.md` | Resolving ambiguities in the current spec |
| `sp-analyze` | `sp.analyze.md` | Verifying consistency across spec/plan/tasks |
| `sp-plan` | `sp.plan.md` | Generating an architecture plan |
| `sp-tasks` | `sp.tasks.md` | Generating a task list from plan artifacts |
| `sp-implement` | `sp.implement.md` | Executing tasks from tasks.md |
| `sp-adr` | `sp.adr.md` | Documenting an architectural decision |
| `sp-phr` | `sp.phr.md` | Recording a prompt history record |
| `sp-checklist` | `sp.checklist.md` | Generating a feature checklist |
| `sp-taskstoissues` | `sp.taskstoissues.md` | Converting tasks to GitHub Issues |
| `sp-git-commit_pr` | `sp.git.commit_pr.md` | Committing work and opening a PR |
| `sp-reverse-engineer` | `sp.reverse-engineer.md` | Reverse engineering an existing codebase |

**Resources also available:**
- `speckit://constitution` — Returns the full project constitution
- `speckit://specs` — Returns directory listing of `specs/`

---

## 5. Agent Behavior

### Code Citations

When referencing existing code, use the format:
```
file_path:start_line-end_line
```
Example: `backend/services/todo_service.py:45-67`

### Checking Your Current Task

Before writing code:
1. Read `specs/<feature>/tasks.md` — find the first unchecked `[ ]` task.
2. Note the task ID (e.g., T039).
3. Implement only what that task requires. Nothing more.
4. Mark the task `[x]` when complete.

### Feature Context

The active branch encodes the feature: `005-todo-ai-chatbot` maps to `specs/005-todo-ai-chatbot/`.

---

## 6. Agent Failure Modes

| Failure Mode | Description | Prevention |
|--------------|-------------|------------|
| Spec-skip | Writing code before a spec exists | Always check `specs/<feature>/spec.md` first |
| Scope creep | Implementing beyond the task description | Implement only what the task ID requires |
| PHR-miss | Forgetting to record a Prompt History Record | Run `/sp.phr` after every substantive exchange |
| ADR-auto-create | Creating ADRs without user consent | Suggest only; wait for explicit approval |
| Over-abstraction | Adding helpers/utilities for one-time use | YAGNI; smallest viable diff |
| Hardcoded secrets | Embedding tokens or credentials in code | Always use `.env` files and docs |

---

## 7. Developer-Agent Alignment

- **Constitution**: `.specify/memory/constitution.md` — Project principles, tech constraints, governance.
- **Active Branch**: `005-todo-ai-chatbot` — All work maps to `specs/005-todo-ai-chatbot/`.
- **Active Feature**: Phase V — Todo AI Chatbot with Kafka, Dapr, OKE deployment.
- **MCP Server**: `scripts/speckit_mcp/server.py` — Connect via `.mcp.json` for IDE-agnostic access to all SpecKit prompts.
- **Command Authority**: `.claude/commands/` — 13 files define the canonical SDD workflow. Agents MUST use these rather than ad-hoc implementations.
