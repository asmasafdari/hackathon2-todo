"""
Event type constants for the Todo platform.

Event types follow the CloudEvents reverse-DNS naming convention:
com.desktoptodo.<domain>.<action>
"""

# Event source identifiers
SOURCE_BACKEND = "/backend/todo-service"
SOURCE_AGENT = "/agent/mcp-server"

# Todo domain event types
EVENT_TODO_CREATED = "com.desktoptodo.todo.created"
EVENT_TODO_UPDATED = "com.desktoptodo.todo.updated"
EVENT_TODO_COMPLETED = "com.desktoptodo.todo.completed"
EVENT_TODO_DELETED = "com.desktoptodo.todo.deleted"

# Agent domain event types
EVENT_AGENT_ACTION_EXECUTED = "com.desktoptodo.agent.action.executed"
EVENT_AGENT_ACTION_FAILED = "com.desktoptodo.agent.action.failed"

# Consolidated Kafka topics (Phase V event-driven architecture)
TOPIC_TODO_CREATED = "todo.created"
TOPIC_TODO_UPDATED = "todo.updated"
TOPIC_TODO_COMPLETED = "todo.completed"
TOPIC_TODO_DELETED = "todo.deleted"
TOPIC_AGENT_ACTION = "agent.action"

# Phase V aggregate topics for Kafka consumers
TOPIC_TASK_EVENTS = "task-events"       # All task CRUD operations (for audit, recurring task service)
TOPIC_REMINDERS = "reminders"           # Scheduled reminder triggers (for notification service)
TOPIC_TASK_UPDATES = "task-updates"     # Real-time client sync (for WebSocket service)

# Phase V event types
EVENT_REMINDER_DUE = "com.desktoptodo.reminder.due"
EVENT_RECURRING_CREATED = "com.desktoptodo.todo.recurring.created"

# Dapr pub/sub component name
PUBSUB_NAME = "kafka-pubsub"

# CloudEvents spec version
CLOUDEVENTS_SPEC_VERSION = "1.0"
