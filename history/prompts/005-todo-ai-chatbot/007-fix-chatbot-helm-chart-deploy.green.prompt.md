---
id: 007
title: Fix Chatbot Helm Chart & Deploy to Minikube
stage: green
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: 005-todo-ai-chatbot
branch: 005-todo-ai-chatbot
user: Amena
command: implement plan
labels: ["helm", "minikube", "clerk", "deployment", "kubernetes"]
links:
  spec: specs/005-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - charts/chatbot/values.yaml
  - charts/chatbot/values-minikube.yaml
  - charts/chatbot/templates/backend.yaml
  - charts/chatbot/templates/frontend.yaml
  - scripts/deploy-minikube.sh
  - charts/DEPLOYMENT.md
tests:
  - helm template chatbot charts/chatbot -f charts/chatbot/values-minikube.yaml
---

## Prompt

Implement the following plan:

# Plan: Fix Chatbot Helm Chart & Deploy to Minikube

## Context
The `charts/chatbot/` Helm chart and Docker infrastructure already exist but have gaps that prevent a working Minikube deployment. The backend template is missing Clerk authentication env vars, the frontend template is missing Clerk keys, and there's no deployment automation script. This plan fixes the chart, adds a deploy script, and ensures a working end-to-end Minikube deployment of the Phase III Todo AI Chatbot.

## Response snapshot

Implemented all 6 changes from the plan:

1. **values.yaml** — Added `clerkSecretKey`, `clerkPublishableKey`, `clerkDomain` to secrets section
2. **values-minikube.yaml** — Added same Clerk secret placeholders with `--set` usage comments
3. **backend.yaml** — Added `clerk-secret-key`, `clerk-domain`, `clerk-publishable-key` to `chatbot-secrets` Secret; added `CLERK_SECRET_KEY` and `CLERK_DOMAIN` env vars to backend Deployment
4. **frontend.yaml** — Added `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` env vars referencing `chatbot-secrets`
5. **scripts/deploy-minikube.sh** — Created full deployment automation script (prereq checks, Minikube start, ingress, Docker builds, Helm install/upgrade, pod readiness wait, access instructions)
6. **charts/DEPLOYMENT.md** — Added "Chatbot Deployment (Phase III)" section with quick start and manual deployment instructions

## Outcome

- ✅ Impact: Helm chart now includes all Clerk auth env vars needed for backend and frontend; deploy script automates the full Minikube workflow
- 🧪 Tests: helm template rendering should succeed with values-minikube.yaml
- 📁 Files: 6 files modified/created
- 🔁 Next prompts: Run helm template to validate, then deploy to Minikube with real secrets
- 🧠 Reflection: Straightforward gap-filling — the chart structure was already sound, just missing Clerk-specific config

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A — manual verification needed with helm template
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate with `helm template` command
