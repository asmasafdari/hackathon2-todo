---
id: 008
title: Deploy Todo Chatbot to Local Minikube
stage: green
date: 2026-02-17
surface: agent
model: claude-opus-4-6
feature: 005-todo-ai-chatbot
branch: 005-todo-ai-chatbot
user: Amena
command: implement plan
labels: ["kubernetes", "minikube", "helm", "deployment", "docker"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - scripts/deploy-chatbot-minikube.sh
  - charts/chatbot/values-minikube.yaml
tests:
  - kubectl get pods -n todo-chatbot — all pods Running/Ready
  - curl http://localhost:8001/health — returns 200 healthy
  - curl http://localhost:3002/ — returns 200
---

## Prompt

Implement the following plan: Verify Existing Todo + Deploy to Local Kubernetes (Minikube). Fix deploy script build context, start Minikube, build images inside Minikube's Docker, deploy with Helm, and verify the deployment.

## Response snapshot

Successfully deployed the Todo AI Chatbot to local Minikube (profile: todo-chatbot). Key fixes applied:
1. Fixed `deploy-chatbot-minikube.sh` build context — backend now builds from project root with `-f backend/Dockerfile .` instead of `cd backend && docker build .`
2. Added Clerk secret passthrough to the deploy script (was only passing OpenAI key)
3. Fixed SQLite database URL in `values-minikube.yaml` — changed from 3-slash relative to 4-slash absolute path (`////tmp/chatbot.db`)
4. Increased backend resource limits from 512Mi to 1024Mi and CPU from 500m to 1000m to prevent OOM kills
5. Increased liveness probe initial delay from 30s to 60s for backend startup time
6. Rebuilt chatbot-frontend image with actual Clerk publishable key (NEXT_PUBLIC_* vars baked at build time)
7. All pods running healthy, health endpoints verified via port-forward.

## Outcome

- ✅ Impact: Both backend and frontend pods running and healthy in Minikube K8s cluster
- 🧪 Tests: Health endpoint returns 200, frontend loads, no crash loops
- 📁 Files: 2 files modified (deploy script + helm values)
- 🔁 Next prompts: Test chat interaction end-to-end through K8s, set up minikube tunnel for ingress access
- 🧠 Reflection: Multiple issues discovered during deployment — SQLite path, OOM kills, Next.js build-time env vars. Iterative debugging was key.

## Evaluation notes (flywheel)

- Failure modes observed: SQLite relative path error, OOM kill (137) on 512Mi pods, Clerk publishable key baked as placeholder at build time
- Graders run and results (PASS/FAIL): kubectl pod status PASS, health endpoint PASS, frontend load PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run minikube tunnel and test ingress-based access
