# Todo App Overview

## Purpose
A todo application that evolves from console app to AI chatbot, built with spec-driven development.

## Current Phase
Phase V: Event-Driven Architecture (Kafka/Dapr)

## Tech Stack
- Frontend: Next.js 14, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLModel, Neon PostgreSQL
- AI Agent: OpenAI Agents SDK + MCP Server (FastMCP)
- Events: Dapr pub/sub with Kafka
- Deployment: Docker, Kubernetes (Minikube), Helm charts

## Features
- [x] Task CRUD operations (Phase I & II)
- [ ] User authentication (Better Auth)
- [x] AI chatbot with MCP tools (Phase III)
- [x] Cloud-native K8s deployment (Phase IV)
- [x] Event-driven architecture with Dapr/Kafka (Phase V)
- [x] Task filtering and sorting

## Spec Organization
- `specs/001-fullstack-todo/` - Phase II fullstack web app
- `specs/002-ai-agent-mcp/` - Phase III AI agent + MCP
- `specs/003-cloud-native-k8s/` - Phase IV Kubernetes
- `specs/004-event-driven-kafka/` - Phase V events
- `specs/005-todo-ai-chatbot/` - Phase III chatbot frontend
