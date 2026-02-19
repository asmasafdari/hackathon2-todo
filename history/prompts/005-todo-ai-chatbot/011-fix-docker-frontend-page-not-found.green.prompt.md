---
id: 011
title: Fix Docker Frontend Page Not Found
stage: green
date: 2026-02-18
surface: agent
model: claude-sonnet-4-6
feature: 005-todo-ai-chatbot
branch: 005-todo-ai-chatbot
user: Amena
command: "in existing todo docker frontend says page not found"
labels: ["bugfix","clerk","docker","nextjs","server-components"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/components/NavBar.tsx
  - frontend/app/layout.tsx
tests:
  - docker logs desktop-todo-todo-frontend-1 (no errors after fix)
---

## Prompt

in existing todo docker frontend says page not found

## Response snapshot

Diagnosed root cause from container logs: `Error: Clerk: auth() was called but Clerk can't detect usage of clerkMiddleware()`. The `layout.tsx` used `SignedIn`, `SignedOut`, `UserButton` as server components (Clerk v6), which internally call `auth()`. In a standalone Docker build with placeholder Clerk keys the middleware context is not available, causing server-component rendering to throw and Next.js to return an error page.

Fix: extracted the navbar into a new `"use client"` component (`frontend/components/NavBar.tsx`) so Clerk's client-side React context is used instead of server-side `auth()`. Updated `layout.tsx` to import `NavBar` and removed the now-unused server-side Clerk imports. Rebuilt the Docker image (`--no-cache`); build passed cleanly and container restarted with `✓ Ready in 997ms` and no errors.

## Outcome

- ✅ Impact: Frontend container starts without Clerk auth() errors; page loads correctly
- 🧪 Tests: Docker logs show clean startup; no more digest errors
- 📁 Files: Created NavBar.tsx client component; updated layout.tsx
- 🔁 Next prompts: Verify sign-in flow with real Clerk keys; test todo CRUD operations
- 🧠 Reflection: Clerk v6 server components require the middleware to set auth context via request headers. When Clerk keys are invalid/missing, the middleware can't populate that context, so any server component calling auth() throws. Moving auth-gating UI to client components is the robust fix for Docker/standalone builds.

## Evaluation notes (flywheel)

- Failure modes observed: Server-component auth() calls failing silently in standalone builds when Clerk keys are placeholders
- Graders run and results (PASS/FAIL): Manual log inspection — PASS
- Prompt variant (if applicable): none
- Next experiment: Test with real Clerk publishable key to confirm full auth flow works in Docker
