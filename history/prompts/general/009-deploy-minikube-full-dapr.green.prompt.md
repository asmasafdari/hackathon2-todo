---
id: "009"
title: Deploy Todo Platform to Minikube with Full Dapr
stage: green
date: 2026-02-12
surface: agent
model: opencode/kimi-k2.5-free
feature: dapr-deployment
branch: main
user: user
command: Deploy to Minikube with Full Dapr including Pub/Sub, State, Bindings (cron), Secrets, and Service Invocation
labels: [dapr, minikube, kubernetes, deployment, state-store, pubsub, bindings, secrets]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - charts/todo-platform/templates/dapr-components/statestore.yaml
  - charts/todo-platform/templates/dapr-components/bindings-cron.yaml
  - charts/todo-platform/templates/dapr-components/secrets.yaml
  - charts/todo-platform/templates/dapr-components/resiliency.yaml
  - charts/todo-platform/values-minikube.yaml
  - charts/todo-platform/values.yaml (modified)
  - scripts/minikube-dapr-deploy.sh
  - docs/minikube-dapr-quickstart.md
  - DAPR_DEPLOYMENT_SUMMARY.md
tests:
  - N/A - Infrastructure/Configuration only
---

## Prompt

have you: Deploy to Minikube Deploy Dapr on Minikube use Full Dapr: Pub/Sub, State, Bindings (cron), Secrets, Service Invocation?

## Response snapshot

Created complete Minikube deployment with all Dapr building blocks:

1. **Dapr Components Created:**
   - State Store (Redis): `charts/todo-platform/templates/dapr-components/statestore.yaml`
   - Bindings (Cron): `charts/todo-platform/templates/dapr-components/bindings-cron.yaml`
   - Secrets Store: `charts/todo-platform/templates/dapr-components/secrets.yaml`
   - Resiliency + Configuration: `charts/todo-platform/templates/dapr-components/resiliency.yaml`

2. **Deployment Script:**
   - `scripts/minikube-dapr-deploy.sh` - Fully automated deployment
   - Installs Minikube, Dapr runtime, Redis, Kafka, Zipkin
   - Builds images and deploys application

3. **Configuration:**
   - `charts/todo-platform/values-minikube.yaml` - Complete Minikube-specific values
   - `charts/todo-platform/values.yaml` - Extended with Dapr configuration structure

4. **Documentation:**
   - `docs/minikube-dapr-quickstart.md` - Comprehensive quickstart guide
   - `DAPR_DEPLOYMENT_SUMMARY.md` - Implementation summary

## Outcome

- ✅ Impact: Full Dapr deployment infrastructure created with all 5 building blocks
- 🧪 Tests: N/A - Infrastructure configuration only
- 📁 Files: 9 files created/modified with complete Dapr integration
- 🔁 Next prompts: Run deployment script, test services, enable AI features
- 🧠 Reflection: Comprehensive template-based approach allows flexible configuration across different environments

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): Original
- Next experiment (smallest change to try): Run the deployment script and verify all services work
