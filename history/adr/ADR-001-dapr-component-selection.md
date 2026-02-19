# ADR-001: Dapr Component Selection for Minikube Deployment

> **Scope**: Selection of Dapr building block components (State Store, Pub/Sub, Secrets, Bindings) and service invocation configuration (mTLS, Resiliency) for the Todo Platform's Minikube deployment.

- **Status:** Accepted
- **Date:** 2026-02-12
- **Feature:** dapr-deployment
- **Context:** Deploying the Todo Platform to Minikube requires selecting appropriate Dapr components for local development that balance simplicity, feature completeness, and production-readiness for eventual cloud migration.

## Significance Checklist

- ✅ **Impact**: Long-term architectural decisions affecting data persistence, messaging, security, and service communication patterns
- ✅ **Alternatives**: Multiple viable component options exist for each building block (Redis vs PostgreSQL for state, Kafka vs Redis for pub/sub, etc.)
- ✅ **Scope**: Cross-cutting concerns affecting all microservices (backend, activity-logger, MCP)

## Decision

We will use the following Dapr component stack for Minikube deployment:

### Building Blocks

| Building Block | Component | Configuration |
|----------------|-----------|---------------|
| **State Store** | Redis | Standalone Redis with persistence, actor state enabled |
| **Pub/Sub** | Redis Streams | Redis-based pub/sub (with Kafka as alternative) |
| **Secrets** | Kubernetes | Native Kubernetes secrets store |
| **Bindings** | Cron | Input binding for scheduled tasks |
| **Service Invocation** | mTLS + Resiliency | Encrypted communication with retries, timeouts, circuit breakers |

### Supporting Infrastructure

- **Dapr Runtime**: v1.12.0 with high availability mode
- **Observability**: Zipkin for distributed tracing
- **Metrics**: Prometheus-compatible metrics enabled
- **Security**: mTLS enabled for all service-to-service communication

## Consequences

### Positive

1. **Simplified Local Development**: Single Redis instance handles both state and pub/sub, reducing infrastructure complexity
2. **Production-Ready Patterns**: mTLS, resiliency policies, and distributed tracing provide enterprise-grade features out of the box
3. **Cloud Migration Path**: Component abstractions allow swapping Redis for managed services (AWS ElastiCache, Azure Cosmos DB) with minimal code changes
4. **Security by Default**: mTLS encryption and Kubernetes secrets management follow security best practices
5. **Operational Visibility**: Zipkin tracing and Dapr metrics provide comprehensive observability
6. **Scalability Foundation**: Actor state store support enables future actor-based microservices

### Negative

1. **Redis Limitations**: Redis pub/sub doesn't provide message persistence or complex routing like Kafka
2. **Single Point of Failure**: Single Redis instance in Minikube (acceptable for local dev, needs HA in production)
3. **Resource Overhead**: Dapr sidecars add ~100MB memory per pod and slight latency overhead
4. **Learning Curve**: Team must learn Dapr concepts (components, resiliency policies, annotations)
5. **Vendor Abstraction Tradeoff**: While Dapr abstracts vendors, debugging requires understanding both Dapr and underlying components
6. **Limited Binding Types**: Only Cron binding implemented initially; HTTP bindings would require additional work

## Alternatives Considered

### Alternative A: PostgreSQL for State Store

**Why Considered**: ACID compliance, relational queries, better data integrity

**Why Rejected**:
- Higher resource overhead in Minikube
- More complex setup (requires persistent volumes)
- Redis is sufficient for simple key-value state needs
- PostgreSQL can be added later for relational data if needed

**Tradeoff**: Sacrificed relational capabilities for operational simplicity

### Alternative B: Kafka for Pub/Sub (Primary)

**Why Considered**: Industry standard, message persistence, consumer groups, better for production

**Why Rejected as Default**:
- Significantly higher resource requirements (Zookeeper + Brokers)
- More complex to operate locally
- Redis Streams sufficient for development workloads

**Compromise**: Kafka configuration preserved as alternative in values file for production migration

### Alternative C: Local File Secrets Store

**Why Considered**: Simpler for local development, no Kubernetes dependency

**Why Rejected**:
- Doesn't match production patterns
- Secrets would be committed to version control (security risk)
- Kubernetes secrets provide better security and are standard for K8s deployments

**Tradeoff**: Slightly more complex initial setup for better security posture

### Alternative D: No Resiliency Policies

**Why Considered**: Simpler configuration, faster development iteration

**Why Rejected**:
- Resiliency is core value proposition of Dapr service invocation
- Better to establish patterns early rather than retrofit
- Minimal configuration overhead with Helm templating

### Alternative E: HTTP Service Mesh (Istio/Linkerd)

**Why Considered**: More mature ecosystem, extensive feature set

**Why Rejected**:
- Significantly higher complexity and resource overhead
- Dapr provides sufficient features (mTLS, retries, observability) with less complexity
- Dapr's programming model (sidecar SDK) is more developer-friendly

**Tradeoff**: Less ecosystem maturity for operational simplicity

## Migration Path to Production

### Phase 1: Minikube (Current)
- Redis: Single instance
- Pub/Sub: Redis Streams
- Secrets: Kubernetes native
- mTLS: Enabled with Dapr-managed certs

### Phase 2: Cloud Kubernetes (EKS/GKE/AKS)
- Redis: AWS ElastiCache / Azure Cache / Memorystore
- Pub/Sub: Amazon MSK / Event Hubs / Cloud Pub/Sub
- Secrets: AWS Secrets Manager / Azure Key Vault / Secret Manager
- mTLS: Certificate rotation, custom CA integration

### Phase 3: Multi-Region
- Redis: Global Redis with replication
- Pub/Sub: Cross-region replication
- Secrets: Multi-region secret replication
- mTLS: Federated identity, regional CA hierarchies

## References

- Feature Spec: N/A (Infrastructural decision)
- Implementation Plan: `DAPR_DEPLOYMENT_SUMMARY.md`
- Related ADRs: None (first ADR)
- Implementation Files:
  - `charts/todo-platform/templates/dapr-components/statestore.yaml`
  - `charts/todo-platform/templates/dapr-components/bindings-cron.yaml`
  - `charts/todo-platform/templates/dapr-components/secrets.yaml`
  - `charts/todo-platform/templates/dapr-components/resiliency.yaml`
  - `charts/todo-platform/values-minikube.yaml`
  - `scripts/minikube-dapr-deploy.sh`
- Documentation: `docs/minikube-dapr-quickstart.md`
- Dapr Documentation: https://docs.dapr.io/

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-12 | Redis for State + Pub/Sub | Simplicity for local dev, sufficient for current needs |
| 2026-02-12 | Kubernetes Secrets | Security best practice, production-ready |
| 2026-02-12 | Enable mTLS by default | Security first, minimal overhead |
| 2026-02-12 | Resiliency policies (3 retries, 30s timeout) | Balance between reliability and responsiveness |
| 2026-02-12 | Zipkin for tracing | Industry standard, good Minikube support |

---

**Status**: ✅ Accepted  
**Next Review**: Upon production deployment readiness assessment
