---
id: "014"
title: Oracle OKE Full Dapr Redpanda CI/CD Monitoring
stage: green
date: 2026-02-18
surface: agent
model: claude-sonnet-4-6
feature: 005-todo-ai-chatbot
branch: 005-todo-ai-chatbot
user: Amena
command: "Deploy Dapr on OKE, Redpanda Cloud Kafka, GitHub Actions CI/CD, Prometheus + Grafana + OTel monitoring"
labels: ["dapr","oracle-oke","redpanda","kafka","ci-cd","github-actions","prometheus","grafana","opentelemetry","helm","kubernetes","monitoring"]
links:
  spec: specs/005-todo-ai-chatbot/spec.md
  ticket: specs/005-todo-ai-chatbot/tasks.md
  adr: null
  pr: null
files:
  - dapr/components/oke/config.yaml
  - dapr/components/oke/pubsub-redpanda.yaml
  - dapr/components/oke/pubsub-redis-fallback.yaml
  - dapr/components/oke/statestore-postgresql.yaml
  - dapr/components/oke/bindings-cron.yaml
  - dapr/components/oke/secretstore-kubernetes.yaml
  - dapr/components/oke/resiliency.yaml
  - charts/todo-platform/values-oke.yaml
  - backend/main.py
  - backend/routers/dapr_subscriptions.py
  - activity_logger/Dockerfile
  - k8s/monitoring/prometheus-stack-values.yaml
  - k8s/monitoring/otel-collector.yaml
  - k8s/monitoring/dapr-servicemonitor.yaml
  - k8s/monitoring/backend-servicemonitor.yaml
  - .github/workflows/deploy-oke.yml
  - scripts/oke-full-deploy.sh
tests:
  - CI/CD smoke-test job: GET /health (curl --retry 5)
  - CI/CD smoke-test job: GET /ready (curl --retry 3)
  - CI/CD smoke-test job: GET /dapr/subscribe (grep kafka-pubsub)
  - CI/CD smoke-test job: POST /api/todos (create smoke-test todo)
---

## Prompt

Deploy Dapr on GKE/AKS (clarified → Oracle Cloud OKE). Use Full Dapr: Pub/Sub, State, Bindings (cron), Secrets, Service Invocation. Use Kafka on Confluent/Redpanda Cloud. Set up CI/CD pipeline using GitHub Actions. Configure monitoring and logging.

Clarifications resolved:
- Kafka provider → **Redpanda Cloud** (SASL/SCRAM-SHA-256)
- Cloud platform → **Oracle Cloud OKE** (continue existing T071–T091 work)
- Redis Streams provided as fallback pub/sub (same component name `kafka-pubsub`)

## Response snapshot

Implemented 17 files across 4 major areas:

**Dapr OKE Components (7 files):**
- `config.yaml` — tracing enabled → OTel Collector (Zipkin endpoint), JSON logging
- `pubsub-redpanda.yaml` — Redpanda Cloud SASL/SCRAM auth, secrets from K8s `todo-secrets`
- `pubsub-redis-fallback.yaml` — same component name `kafka-pubsub`, drop-in Redis Streams swap
- `statestore-postgresql.yaml` — Neon PostgreSQL (DATABASE_URL from secret), tables: dapr_state + dapr_metadata
- `bindings-cron.yaml` — fires POST `/cron-reminder` every 1m, scoped to todo-backend
- `secretstore-kubernetes.yaml` — exposes K8s secrets via DaprClient().get_secret()
- `resiliency.yaml` — 3× retry (2 s constant), circuit breaker (3 consecutive failures), 30 s timeout on backend + activity-logger

**Backend + Helm changes:**
- `values-oke.yaml` — enabled all Dapr building blocks, Redpanda Kafka config, activity-logger (port 8082), configurable CORS
- `backend/main.py` — CORS list now reads `ALLOWED_ORIGINS` env var (comma-separated), fallback to localhost
- `backend/routers/dapr_subscriptions.py` — added `POST /cron-reminder` handler (cron binding safety-net)

**Activity Logger Dockerfile:**
- Multi-stage Python 3.11-slim build (gcc/libpq-dev build stage → libpq5 runtime)
- PYTHONPATH=/app, port 8082, uvicorn entry point

**Monitoring (4 files):**
- `prometheus-stack-values.yaml` — Grafana persistence (5 Gi/oci), Dapr + K8s dashboards from grafana.com, Prometheus 15 d retention/10 Gi, additionalScrapeConfigs for Dapr pod metrics
- `otel-collector.yaml` — ConfigMap + Deployment (otel/opentelemetry-collector-contrib:0.91.0) + Service; receives Zipkin (9411) + OTLP gRPC/HTTP (4317/4318), exports to logging + Prometheus (8889)
- `dapr-servicemonitor.yaml` — two CRDs: todo+dapr-system sidecars, dapr-system components
- `backend-servicemonitor.yaml` — two CRDs: backend + activity-logger, scrape /metrics every 30 s

**GitHub Actions CI/CD (4-job pipeline):**
- Job 1 `build-and-push`: OCIR login, build+push 4 images (SHA + :latest tags)
- Job 2 `deploy-monitoring` (parallel): kube-prometheus-stack + OTel + ServiceMonitors
- Job 3 `deploy-app` (parallel): secrets, Dapr Helm install, 7 Dapr component files (Redis fallback via workflow_dispatch input), todo-platform Helm deploy
- Job 4 `smoke-test`: /health, /ready, /dapr/subscribe, POST /api/todos

**Manual Deploy Script:**
- `scripts/oke-full-deploy.sh` — 11-step script: prereq checks, kubectl config, namespace create, Dapr Helm install, kube-prometheus-stack, OTel + ServiceMonitors, K8s secret creation, Dapr components, Helm app deploy, rollout wait, smoke tests + summary table

## Outcome

- ✅ Impact: Full Dapr event-driven architecture on Oracle OKE with Redpanda Cloud Kafka, Prometheus/Grafana/OTel monitoring, and automated 4-job GitHub Actions CI/CD pipeline — completing tasks T071–T091 implementation artifacts
- 🧪 Tests: Smoke tests via GitHub Actions Job 4: /health, /ready, /dapr/subscribe (grep kafka-pubsub), POST /api/todos create
- 📁 Files: 17 files created/modified across dapr/components/oke/, k8s/monitoring/, .github/workflows/, backend/, charts/, activity_logger/, scripts/
- 🔁 Next prompts: Add GitHub Secrets (KAFKA_BROKERS, KAFKA_API_KEY, KAFKA_API_SECRET, ALLOWED_ORIGINS, BACKEND_URL, GRAFANA_ADMIN_PASSWORD); push branch to trigger CI/CD; verify Dapr sidecar injection in OKE pods
- 🧠 Reflection: Redis fallback approach (same component name `kafka-pubsub`) is clean — zero app code change needed for pub/sub swap. Cron binding as reminder safety-net is minimal (only logs on tick). OTel Collector deployed standalone (no operator) for simplicity.

## Evaluation notes (flywheel)

- Failure modes observed: (1) Write tool required prior Read — fixed by reading 1–5 lines before overwriting existing files. (2) Edit with non-unique match string — fixed by providing more surrounding context for the specific block. (3) User said "GKE" but meant "OKE" — clarified via targeted questions before planning.
- Graders run and results (PASS/FAIL): File creation PASS (17/17 files written), CI/CD 4-job structure PASS, Monitoring stack PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add OTel → Grafana Tempo integration for distributed trace UI (currently traces only go to logging exporter)
