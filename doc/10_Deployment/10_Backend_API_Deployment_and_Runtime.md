# Backend API Deployment and Runtime

**Document ID:** DEP-10
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/10_Deployment/README.md`
**Previous Document:** `docs/10_Deployment/09_Redis_Queue_and_Cache_Runtime_Architecture.md`
**Next Document:** `docs/10_Deployment/11_Frontend_Deployment_and_Static_Asset_Delivery.md`

---

## 1. Purpose

This document defines the deployment and runtime architecture of the FastFood ERP Backend API.

The Backend API runtime must:

* serve Web and POS requests;
* execute application use cases;
* preserve transactional correctness;
* support multiple worker processes;
* support future horizontal scaling;
* protect PostgreSQL from uncontrolled concurrency;
* interact safely with Redis and queue infrastructure;
* support health checks;
* support graceful startup and shutdown;
* support controlled rolling deployment;
* protect critical POS operations during overload;
* remain compatible with offline synchronization;
* meet defined API performance and availability objectives.

This document is concerned with how the API process runs in production.

It does not redefine API contracts, domain rules, database schema or background worker internals.

---

# 2. Scope

This document covers:

* API process model;
* Flask runtime;
* Gunicorn runtime;
* worker management;
* worker sizing;
* database connection relationship;
* Redis runtime dependency;
* queue interaction;
* request execution limits;
* request timeouts;
* health endpoints;
* readiness;
* liveness;
* graceful shutdown;
* deployment draining;
* rolling deployment;
* process restart;
* horizontal scaling;
* load balancing;
* resource limits;
* runtime security;
* logging;
* metrics;
* tracing;
* overload protection;
* offline synchronization runtime;
* runtime failure handling;
* release compatibility;
* rollback requirements;
* API runtime testing;
* runtime invariants.

---

# 3. Runtime Architectural Position

The Backend API runtime is positioned between the reverse proxy and the application layer.

```text
Client
  ↓
DNS / TLS
  ↓
Reverse Proxy
  ↓
Backend API Runtime
  ↓
Application Layer
  ↓
Domain Layer
  ↓
Repository / Data Access
  ↓
PostgreSQL
```

Supporting runtime services may include:

```text
Backend API
   ├── PostgreSQL
   ├── Redis
   ├── Queue
   ├── Object Storage
   ├── Background Workers
   └── AI Runtime
```

The API runtime does not own durable Business state.

---

# 4. Runtime Principles

The Backend API runtime follows these principles:

1. API processes are stateless.
2. PostgreSQL remains the authoritative transactional source.
3. Worker memory is temporary.
4. Local filesystem state is not the authoritative Business state.
5. API instances must be replaceable.
6. API instances must be horizontally scalable.
7. Request correctness must not depend on worker identity.
8. Sticky sessions must not be required for core Business operations.
9. Core POS operations receive the highest runtime priority.
10. Runtime resources must be bounded.
11. Database connection usage must be bounded.
12. Startup must fail safely when required configuration is invalid.
13. Liveness and readiness are separate concepts.
14. Shutdown must be graceful.
15. Long-running work should be delegated to background workers.
16. External dependencies must have bounded timeouts.
17. Retries must be bounded and idempotency-aware.
18. Security controls must remain active during degraded operation.
19. Deployment must support controlled mixed-version operation.
20. Performance optimization must not weaken correctness or historical integrity.

---

# 5. Initial Runtime Technology

The initial production runtime uses:

```text
Reverse Proxy
     ↓
Gunicorn
     ↓
Flask Application
```

The Backend API is initially a WSGI application.

Gunicorn provides the production process manager and application server runtime.

The architecture must remain compatible with future containerized deployment.

---

# 6. Flask Application Runtime

The Flask application should use an application factory.

Conceptual structure:

```text
Gunicorn
   ↓
Application Factory
   ↓
Runtime Configuration
   ↓
Application Initialization
   ↓
Routes / Middleware
   ↓
Ready
```

The application factory must not perform large Business queries or expensive data processing during startup.

---

# 7. WSGI Entry Point

The deployment must expose a stable WSGI application entry point.

Conceptually:

```text
app:create_app()
```

The exact implementation path may be refined during coding, but the deployment contract must identify:

* Python runtime;
* WSGI module;
* application factory;
* required configuration;
* startup command.

---

# 8. Gunicorn Responsibilities

Gunicorn is responsible for:

* worker process management;
* request serving;
* worker lifecycle;
* worker restart;
* graceful worker shutdown;
* process-level concurrency;
* runtime isolation.

Gunicorn does not own:

* Business transactions;
* authorization rules;
* inventory correctness;
* payment correctness;
* audit persistence;
* queue durability.

---

# 9. Worker Process Model

The initial runtime uses multiple Gunicorn worker processes.

Conceptually:

```text
Gunicorn Master
   ├── Worker 1
   ├── Worker 2
   ├── Worker 3
   └── Worker N
```

Each worker is an independent operating-system process.

Worker memory is not shared for correctness.

---

# 10. Initial Worker Count

For a small initial deployment, the starting range may be:

```text
2–4 workers
```

This is an initial deployment value, not a permanent rule.

Worker count must be validated against:

* available CPU;
* available memory;
* request concurrency;
* request latency;
* PostgreSQL capacity;
* Redis capacity;
* actual POS workload.

---

# 11. Worker Sizing

Worker count must be measured rather than copied from a generic formula.

The sizing decision should consider:

```text
CPU
Memory
Average request duration
Peak request concurrency
Database latency
Redis latency
Peak POS traffic
Synchronization traffic
Administrative traffic
```

The goal is stable throughput and predictable latency.

Maximum worker count is not automatically the optimal worker count.

---

# 12. Worker Count and Database Capacity

Increasing API workers increases potential database concurrency.

The deployment must consider:

```text
API Instances
    ×
Workers per Instance
    ×
Pool Capacity
    +
Background Worker Connections
    +
Scheduler Connections
    +
Administrative Connections
```

The total must remain within the PostgreSQL connection budget.

API scaling without database capacity review is prohibited.

---

# 13. Stateless Runtime

Each API instance must be stateless with respect to durable Business state.

Incorrect:

```text
Worker A
   ↓
Order state stored only in memory
```

Correct:

```text
Worker A ─┐
          ├── PostgreSQL / Durable State
Worker B ─┘
```

Local memory may only contain bounded derived or temporary state.

---

# 14. Runtime State Categories

### Durable State

Examples:

* Orders;
* Payments;
* Inventory Transactions;
* Cash Sessions;
* configuration history;
* audit history;
* synchronization results.

Durable state belongs to persistent infrastructure.

### Temporary State

Examples:

* request context;
* local cache;
* temporary file;
* in-memory calculation.

Temporary state must not become the only copy of Business state.

---

# 15. Request Context Isolation

The runtime must isolate request-specific context between requests.

The following must never leak from one request to another:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Cash Session UUID;
* Operation UUID;
* Request ID;
* authorization context.

Request context must not be stored in unsafe global mutable state.

---

# 16. Worker Restart

A worker may restart after:

* application failure;
* controlled deployment;
* worker recycling;
* emergency recovery;
* resource protection.

Restarting a worker must not corrupt committed Business state.

---

# 17. Worker Recycling

Worker recycling may be used to limit:

* memory fragmentation;
* long-term memory growth;
* impact of process-level leaks.

A recycling configuration should be bounded.

Workers should not all recycle simultaneously unless intentionally controlled.

---

# 18. Worker Timeout

Gunicorn worker timeout must be explicitly configured.

It must be:

* long enough for normal valid requests;
* short enough to prevent permanently occupied workers;
* compatible with reverse proxy timeouts.

Repeated requests approaching the worker timeout indicate a performance problem or missing asynchronous boundary.

---

# 19. Reverse Proxy and Application Timeout Relationship

Reverse proxy and Gunicorn timeout settings must be designed together.

The system must avoid:

```text
Proxy Timeout
     ↓
Client Retry
     ↓
Original Request Still Processing
     ↓
Duplicate Request Risk
```

State-changing operations therefore rely on:

* idempotency;
* transaction correctness;
* database constraints.

---

# 20. Core Request Performance Targets

Initial API runtime targets are:

| Metric                               |   Target |
| ------------------------------------ | -------: |
| Ordinary authenticated API p95       | ≤ 300 ms |
| Ordinary authenticated API p99       | ≤ 800 ms |
| Core POS command p95                 | ≤ 500 ms |
| Authorization overhead p95           | ≤ 100 ms |
| Cached authorization lookup p95      |  ≤ 20 ms |
| Business/Branch scope validation p95 |  ≤ 50 ms |
| Idempotency lookup p95               |  ≤ 50 ms |
| Normal synchronization batch p95     |    ≤ 1 s |

These are production SLO targets and must be measured under representative load.

---

# 21. Long-Running Operations

Requests that are expected to exceed normal runtime targets should use asynchronous processing where practical.

Example:

```text
POST /reports
      ↓
Validate
      ↓
Create Job
      ↓
202 Accepted
      ↓
Background Worker
```

The API worker should return once the authoritative job state has been created.

---

# 22. CPU-Heavy Work

The Backend API should not normally perform large CPU-intensive tasks such as:

* large XLSX generation;
* large report transformation;
* heavy image processing;
* large document conversion;
* AI inference;
* large analytical computation.

These belong to dedicated worker or AI runtimes.

---

# 23. I/O-Bound Work

Normal database and cache access is acceptable inside API requests when:

* the access is required;
* timeout is bounded;
* transaction scope is controlled;
* expected latency is reasonable.

External I/O must not be unbounded.

---

# 24. Database Connection Pool

The API must use a bounded PostgreSQL connection pool.

The pool must define controlled values for:

* pool size;
* overflow capacity;
* connection acquisition timeout;
* connection timeout;
* connection lifetime where appropriate.

---

# 25. Connection Budget

The deployment must calculate total database connection demand across:

```text
API Workers
Background Workers
Reporting Workers
Synchronization Workers
Schedulers
Administrative Processes
```

The total must remain within PostgreSQL capacity.

---

# 26. Connection Acquisition

When the database pool is exhausted, request handling must wait only for a bounded period.

Example:

```text
Request
   ↓
Pool Wait
   ↓
Pool Timeout
   ↓
Controlled Failure
```

The API must not create unlimited connections to compensate for overload.

---

# 27. Connection Release

Database connections must be released deterministically.

Monitoring should detect:

* pool exhaustion;
* abnormal connection hold duration;
* leaked connections;
* increasing active connections.

Connection leaks are production-critical defects.

---

# 28. Transaction Boundary

Business transaction boundaries remain owned by the Application/Unit of Work layer.

The API runtime must not introduce hidden transactions that bypass application behavior.

Transactions must not remain open during:

* printing;
* notification delivery;
* external API calls;
* large serialization;
* report generation.

---

# 29. Recommended Request Transaction Sequence

For core state-changing requests:

```text
Request
 ↓
Request Validation
 ↓
Authentication
 ↓
Authorization
 ↓
Application Use Case
 ↓
Database Transaction
 ↓
Domain Operation
 ↓
Audit / Outbox
 ↓
Commit
 ↓
Response
```

Secondary work occurs after the durable transaction where applicable.

---

# 30. Redis Runtime Dependency

Redis may support:

* caching;
* short-lived coordination;
* permission-derived state;
* queue-related functionality.

Redis is not authoritative for:

* Orders;
* Payments;
* Inventory;
* Cash Sessions;
* audit history;
* historical financial state.

---

# 31. Redis Failure

If Redis becomes unavailable:

* safe cache reads may fall back;
* latency may temporarily increase;
* authorization must remain secure;
* database state remains authoritative;
* retry storms must be avoided.

Redis failure must not become an authorization bypass.

---

# 32. Queue Interaction

The API may publish background work through the queue architecture.

For transactional events, the preferred flow is:

```text
PostgreSQL Transaction
    ├── Business Change
    └── Outbox Event
          ↓
        Commit
          ↓
        Queue
          ↓
       Worker
```

Queue availability must not replace transaction durability.

---

# 33. Outbox Runtime Boundary

When Business state and an outbox event belong to the same operation:

```text
Business State
+
Outbox Event
```

must be committed atomically.

Immediate queue execution is not required for the transaction to become valid unless explicitly required by Business rules.

---

# 34. External Dependency Runtime

Each external dependency must have:

* explicit timeout;
* bounded retry;
* failure handling;
* observable failure state.

External dependency latency must not unnecessarily hold a critical database transaction open.

---

# 35. Retry Safety

The runtime assumes that requests may be retried after:

* timeout;
* network interruption;
* reverse proxy failure;
* client restart;
* offline client reconnection.

Retryable state-changing commands therefore require idempotency.

---

# 36. Request Size Limits

The API must enforce maximum request sizes.

Different limits may exist for:

* standard JSON;
* synchronization batches;
* file uploads.

Oversized requests must be rejected before excessive memory consumption.

---

# 37. JSON Request Limits

Normal JSON payloads should remain bounded.

Large data sets should use:

* pagination;
* bounded batch APIs;
* asynchronous jobs;
* dedicated file processing.

The exact maximum size is deployment configuration.

---

# 38. File Upload Runtime Boundary

The API must not become a large-file processing engine.

File uploads should use:

* bounded size;
* controlled streaming;
* temporary storage;
* durable file storage.

Large files must not be unnecessarily loaded entirely into process memory.

---

# 39. Temporary File Runtime

Temporary directories may be used for short-lived processing.

Temporary files must have:

* restricted permissions;
* size limits;
* cleanup;
* finite lifetime.

The API host filesystem must not be treated as durable Business storage.

---

# 40. Runtime Configuration

Runtime configuration should come from controlled deployment sources:

```text
Environment Variables
Secret Injection
Configuration Files
Deployment Parameters
```

Environment-specific values must not be hard-coded into application source.

---

# 41. Startup Configuration Validation

Required runtime configuration must be validated before readiness.

Examples:

```text
Missing Database Configuration
→ Startup Failure

Invalid Security Configuration
→ Startup Failure

Invalid Runtime Limits
→ Startup Failure
```

The runtime must fail safely instead of starting in an unsafe state.

---

# 42. Secret Injection

Secrets must be injected into the runtime.

The application artifact must not contain:

* database passwords;
* Redis credentials;
* signing private keys;
* third-party provider credentials;
* deployment credentials.

Secret handling follows:

`05_Secrets_and_Credential_Management.md`

---

# 43. Startup Lifecycle

The startup sequence should be:

```text
Process Start
    ↓
Load Configuration
    ↓
Validate Configuration
    ↓
Create Application
    ↓
Initialize Runtime Dependencies
    ↓
Register API
    ↓
Expose Health Endpoints
    ↓
Readiness
```

The startup process must remain bounded.

---

# 44. Startup Restrictions

The API must not perform large workloads during startup.

Startup must not:

* generate reports;
* process full synchronization backlogs;
* rebuild all Business caches;
* query entire historical datasets;
* run large AI models;
* execute unnecessary external API calls.

---

# 45. Liveness

Liveness answers:

> Is the API process alive?

Example:

```text
GET /health/live
```

Liveness should remain lightweight and primarily process-oriented.

---

# 46. Readiness

Readiness answers:

> Can this API instance safely receive normal traffic?

Example:

```text
GET /health/ready
```

Readiness may verify:

* application initialization;
* required configuration;
* required PostgreSQL connectivity;
* mandatory runtime dependencies.

---

# 47. Liveness and Readiness Separation

The runtime must preserve the distinction:

```text
Alive
≠
Ready
```

An API may remain alive but unready during:

* startup;
* graceful shutdown;
* dependency failure;
* controlled deployment.

---

# 48. Readiness During Startup

A new instance must remain unready until required initialization has completed.

Traffic must not reach a partially initialized instance.

---

# 49. Readiness During Shutdown

Shutdown sequence:

```text
Ready
  ↓
Not Ready
  ↓
Stop New Traffic
  ↓
Drain Requests
  ↓
Release Resources
  ↓
Exit
```

The API must stop receiving new traffic before termination.

---

# 50. Graceful Shutdown

Graceful shutdown is required for:

* deployment;
* restart;
* maintenance;
* scaling;
* controlled configuration changes.

The runtime should allow active requests to complete within a bounded grace period.

---

# 51. Shutdown and Transactions

During shutdown:

* committed transactions remain committed;
* uncommitted transactions may roll back safely;
* incomplete transactions must not be reported as successful.

---

# 52. Shutdown and Background Work

API workers must not become background workers during shutdown.

Durable outbox records remain available for background workers after API termination.

---

# 53. Deployment Drain

The deployment layer should use:

```text
Ready
 ↓
Unready
 ↓
Stop New Requests
 ↓
Drain Active Requests
 ↓
Terminate
```

This minimizes failed requests during replacement.

---

# 54. Process Supervisor

The initial VPS runtime may use:

```text
systemd
   ↓
Gunicorn
   ↓
Flask
```

Future deployment models may use:

* container runtime;
* orchestration platform;
* managed application runtime.

The application must remain compatible with all supported process supervisors.

---

# 55. systemd Runtime Requirements

When systemd is used, the service should define:

* dedicated service user;
* application working directory;
* startup command;
* environment configuration;
* restart policy;
* resource limits;
* shutdown behavior;
* logging behavior.

---

# 56. Restart Policy

Unexpected API termination should trigger controlled restart where appropriate.

Restart policies must include backoff and crash-loop protection.

Example:

```text
Crash
 ↓
Restart
 ↓
Crash
 ↓
Backoff
 ↓
Alert
```

---

# 57. Worker Crash Protection

One worker crash must not unnecessarily terminate all other healthy workers.

Gunicorn should manage worker replacement without making a single worker failure a full-service failure where possible.

---

# 58. Resource Limits

Runtime resources must be bounded.

At minimum:

* CPU;
* memory;
* process count;
* file descriptors;
* temporary disk usage;
* request sizes;
* database connections.

---

# 59. Memory Protection

Memory growth must be monitored.

Possible causes:

* oversized request;
* oversized response;
* file processing;
* synchronization burst;
* report processing;
* cache growth;
* application memory leak.

Worker recycling may be used as a defensive mechanism.

---

# 60. CPU Protection

CPU-intensive workloads must be isolated from normal API traffic where practical.

The runtime should prioritize:

```text
POS
  ↓
Financial / Inventory
  ↓
Management
  ↓
Synchronization
  ↓
Heavy Reports / Optional Work
```

---

# 61. File Descriptor Limits

The runtime must maintain sufficient but bounded file descriptor capacity for:

* HTTP connections;
* PostgreSQL;
* Redis;
* temporary files;
* logs.

Exhaustion must be monitored.

---

# 62. Keep-Alive

Keep-alive should be configured between reverse proxy and API where useful.

Keep-alive improves connection reuse but must remain bounded.

Configuration should consider:

* idle timeout;
* maximum idle connections;
* expected concurrent connections.

---

# 63. Proxy Trust

The API may receive headers such as:

```text
X-Forwarded-For
X-Forwarded-Proto
X-Request-ID
```

Only explicitly trusted reverse proxies may define authoritative forwarding headers.

Client-provided forwarding headers must not be trusted directly.

---

# 64. Public Port Exposure

Gunicorn should not normally be exposed directly to the public Internet.

Expected network path:

```text
Internet
   ↓
Reverse Proxy
   ↓
Private API Network
   ↓
Gunicorn
```

Firewall rules must restrict direct access to the application port.

---

# 65. Authentication Runtime

Authentication must remain efficient enough for ordinary POS traffic.

The runtime may use:

* access tokens;
* sessions;
* trusted device context;
* short-lived authorization state.

Revocation-sensitive security state must propagate according to the security architecture.

---

# 66. Authorization Runtime

Authorization remains server-side.

The runtime may use:

* cached permission state;
* bounded database lookups;
* short-lived request context.

If required authorization information cannot be established safely, the request must fail closed.

---

# 67. Business Scope Runtime

The runtime must establish authoritative Business context:

```text
Authenticated Actor
        ↓
Authorized Business
        ↓
Authorized Branch
        ↓
Application Use Case
```

Client-provided Business IDs are context hints only.

---

# 68. Branch Scope Runtime

When Branch context exists:

* employee Branch scope must be verified;
* effective permissions must be resolved;
* Branch configuration must be loaded or safely cached;
* Branch-specific data must remain isolated.

---

# 69. Cache Scope

Runtime caches must include all relevant scope dimensions.

Examples:

```text
business:{business_id}:configuration

branch:{business_id}:{branch_id}:menu

permissions:{business_id}:{branch_id}:{employee_id}:{version}
```

Cache keys must prevent cross-Business and cross-Branch collisions.

---

# 70. Offline Synchronization Runtime

Offline devices may reconnect after hours or days.

The API runtime must accept synchronization without allowing synchronization load to make live POS operations unusable.

Synchronization must use:

* operation UUID;
* idempotency;
* bounded batch size;
* conflict handling;
* server validation.

---

# 71. Synchronization Burst

A large reconnection event may produce simultaneous batches.

The runtime must use:

* batch limits;
* concurrency limits;
* backpressure;
* bounded retries;
* queue prioritization.

---

# 72. Synchronization Priority

During load pressure:

```text
1. POS Core Operations
2. Cash / Inventory
3. Normal Management
4. Synchronization
5. Reports / XLSX / Optional Work
```

The exact infrastructure implementation may change without changing this priority rule.

---

# 73. API and Printing

Printing should normally occur after the core transaction commits.

Preferred flow:

```text
Order Transaction
     ↓
Commit
     ↓
Print Job
     ↓
Worker / Printer Service
```

Printer failure must not normally roll back committed Order state.

---

# 74. API and Notifications

Notification delivery should be asynchronous.

Preferred flow:

```text
Business Event
     ↓
Transaction Commit
     ↓
Outbox
     ↓
Notification Worker
```

Notification provider failure must not roll back core Business state.

---

# 75. API and Reporting

Large reports should be asynchronous.

Preferred flow:

```text
API
 ↓
Create Report Job
 ↓
202 Accepted
 ↓
Report Worker
```

The API must remain available for normal POS traffic.

---

# 76. API and XLSX Export

Large XLSX generation must not occupy normal Gunicorn workers unnecessarily.

The API creates an export job and returns a job reference.

---

# 77. API and AI Workloads

AI inference should use the dedicated AI runtime when it is:

* CPU intensive;
* memory intensive;
* GPU dependent;
* long-running;
* operationally isolated from core ERP.

AI failure must not unnecessarily block core ERP operations.

---

# 78. Dependency Timeout Policy

Runtime dependencies must use bounded timeouts:

```text
PostgreSQL
Redis
Queue
Object Storage
External Providers
```

No external dependency may block an API worker indefinitely.

---

# 79. Retry Policy

Retries must be:

* bounded;
* dependency-specific;
* idempotency-aware;
* backoff-based where appropriate.

Retries inside one API request should remain minimal.

Long retry workflows should move to background processing.

---

# 80. Retry Storm Protection

The runtime must prevent retry amplification.

Example:

```text
Dependency Failure
       ↓
Many API Requests
       ↓
Retries
       ↓
Higher Dependency Load
       ↓
Wider Failure
```

Protection may include:

* bounded retry count;
* exponential backoff;
* circuit protection;
* failure-fast behavior;
* asynchronous retry.

---

# 81. Overload Protection

When the API approaches capacity, the runtime should:

1. Protect PostgreSQL.
2. Protect core POS capacity.
3. Throttle synchronization.
4. Throttle heavy workloads.
5. Reject excessive low-priority work.
6. Alert operators.

The system must not accept unlimited workload until the server collapses.

---

# 82. Rate Limiting

Rate limiting may exist at:

```text
Reverse Proxy
API Middleware
Shared Rate Limiter
```

Rate limits must be configured so normal POS operations are not unnecessarily interrupted.

---

# 83. Error Behavior During Overload

Resource exhaustion must produce controlled API errors.

Typical response:

```text
503 SERVICE_UNAVAILABLE
```

or another documented temporary-failure response.

Internal stack traces must not be returned.

---

# 84. Structured Logging

Runtime logs should be structured.

Typical fields:

```text
timestamp
level
request_id
operation_id
route
method
status
latency_ms
release_id
business_id where applicable
branch_id where applicable
employee_id where appropriate
```

Sensitive credentials must never appear in logs.

---

# 85. Logging Volume Control

Routine successful POS requests must not create uncontrolled log volume.

Detailed logging should focus on:

* failures;
* unusual latency;
* security events;
* synchronization conflicts;
* operational anomalies.

---

# 86. Runtime Metrics

The API runtime should expose metrics including:

```text
request_count
request_latency
request_error_count
request_timeout_count
active_requests
worker_count
worker_restart_count
cpu_usage
memory_usage
database_pool_usage
redis_latency
queue_publish_latency
```

Metrics must remain low-cardinality.

Business/Product UUIDs must not become uncontrolled metric labels.

---

# 87. Request Correlation

The runtime should propagate:

```text
Request ID
Operation UUID
```

through relevant application and background contexts.

This supports incident investigation.

---

# 88. Runtime Tracing

Distributed tracing may be enabled where operationally justified.

Tracing may include:

```text
Reverse Proxy
 ↓
API
 ↓
Application
 ↓
PostgreSQL
 ↓
Redis
 ↓
External Provider
```

Sensitive data must not be placed into traces.

---

# 89. API Availability SLO

Initial API availability target:

**≥ 99.9% monthly**

The target applies to the production API service under defined operating conditions.

---

# 90. SLO Measurement

Performance monitoring should distinguish:

* proxy latency;
* API processing latency;
* database latency;
* Redis latency;
* external dependency latency;
* queue publication latency.

This allows the actual source of SLO breaches to be identified.

---

# 91. Error Budget

Repeated SLO failures should trigger:

* capacity review;
* query investigation;
* runtime investigation;
* dependency reliability investigation;
* release review.

SLOs are operational controls, not documentation-only targets.

---

# 92. Deployment Health Verification

Every production deployment should verify:

```text
Process Started
Health Passed
Readiness Passed
Expected Release Active
Database Connectivity
Authentication
Authorization
Redis Behavior
Queue Behavior where required
Critical Smoke Tests
```

---

# 93. Smoke Testing

Production smoke tests should use safe operations.

Examples:

```text
GET /health/live
GET /health/ready
Authenticated read
Business context validation
Branch context validation
Menu read
Configuration read
```

Real payment or financial mutations must not be used for routine production smoke tests unless a dedicated isolated mechanism exists.

---

# 94. Rolling Deployment

When multiple API instances exist, deployment should replace instances gradually.

Example:

```text
Version A
Version A
Version B
Version B
```

New instances must pass readiness before receiving normal traffic.

---

# 95. Mixed-Version Compatibility

During rolling deployment, old and new versions may temporarily coexist.

Therefore:

* database migrations must be compatible;
* cache changes must be compatible;
* queue messages must be compatible;
* API behavior must remain compatible;
* offline synchronization protocol must remain compatible.

---

# 96. Database Migration Relationship

Database changes must follow expand/contract principles.

```text
Expand
 ↓
Deploy Compatible Application
 ↓
Switch Traffic
 ↓
Contract Later
```

Destructive schema changes must not break old API workers during rollout.

---

# 97. Cache Compatibility During Deployment

If a release changes cache representation:

* change cache key version where required;
* invalidate incompatible entries;
* preserve Business and Branch isolation;
* prevent old and new processes from misinterpreting the same data.

---

# 98. Queue Compatibility During Deployment

Queue messages must remain processable during controlled mixed-version deployment.

Breaking message changes require:

* explicit versioning;
* compatibility period;
* controlled migration.

---

# 99. Release Identity

Each API deployment must have a controlled release identity.

Recommended metadata:

```text
Release ID
Build ID
Source Commit
```

Operational metadata must not reveal sensitive infrastructure information.

---

# 100. Artifact Reproducibility

A deployment artifact should be reproducible from:

```text
Source Commit
+
Dependency Lock
+
Build Configuration
```

The running process must not modify its own application artifact.

---

# 101. Production Dependency Control

Production dependencies must be:

* pinned;
* locked;
* reviewed;
* reproducible.

The API must not download arbitrary dependencies during startup.

---

# 102. Runtime Security

The API process must use:

* dedicated service user;
* least filesystem privileges;
* controlled network access;
* secure secret injection;
* bounded request sizes;
* protected runtime configuration.

---

# 103. Service User

The Gunicorn process must not normally run as root.

The service user should have access only to:

* application files;
* required configuration;
* required temporary directories;
* required runtime files.

---

# 104. Filesystem Permissions

The API process should not normally have write access to application source files.

Writable locations should be explicitly defined.

---

# 105. Production Debug Mode

Production debug functionality is prohibited.

The runtime must not expose:

* interactive debugger;
* development reload;
* debug console;
* development diagnostics.

---

# 106. Production Error Responses

Production API responses may expose:

* stable error code;
* safe message;
* request ID.

They must not expose:

* stack traces;
* SQL details;
* database credentials;
* filesystem paths;
* secrets.

---

# 107. PostgreSQL Failure

When PostgreSQL is unavailable:

* write operations must fail safely;
* successful state must never be fabricated;
* readiness should normally fail;
* retries must remain bounded.

The API must not pretend that a transaction succeeded.

---

# 108. Redis Failure

When Redis is unavailable:

* safe cache fallback may be used;
* latency may increase;
* PostgreSQL remains authoritative;
* authorization remains enforced;
* retry storms must be prevented.

---

# 109. Queue Failure

When queue publication is unavailable:

* committed Business state remains durable;
* outbox events remain available where used;
* secondary processing may be delayed;
* recovery must be observable.

---

# 110. Object Storage Failure

If durable file storage is unavailable:

* file-dependent operations must fail explicitly;
* unrelated core operations may continue where Business rules allow;
* nonexistent file references must not be treated as successfully stored documents.

---

# 111. External Provider Failure

External service failures should normally affect secondary workflows rather than rollback committed ERP state.

Examples:

* email provider;
* SMS provider;
* optional integrations;
* external notification systems.

---

# 112. Resource Exhaustion Recovery

When resources become constrained:

```text
Protect PostgreSQL
       ↓
Protect POS
       ↓
Throttle Synchronization
       ↓
Throttle Heavy Work
       ↓
Pause Optional Work
       ↓
Alert Operators
```

---

# 113. Graceful Degradation

The runtime may enter controlled degraded modes.

Example:

```text
Normal
 ↓
Redis Degraded
 ↓
Heavy Jobs Throttled
 ↓
Synchronization Throttled
```

Degraded mode must never silently disable:

* authorization;
* Business isolation;
* Branch isolation;
* financial validation;
* inventory validation.

---

# 114. Maintenance Mode

Exceptional maintenance mode may be supported.

The mode must explicitly define:

* read access;
* write access;
* POS behavior;
* synchronization behavior;
* administrative behavior.

Maintenance controls must be access-controlled and auditable where appropriate.

---

# 115. Runtime Configuration Reload

Selected runtime values may be reloadable.

Examples:

* logging level;
* controlled rate limits;
* selected resource limits.

Other changes normally require restart:

* worker count;
* process model;
* major dependencies;
* incompatible runtime configuration.

---

# 116. Worker Count Change Procedure

Changing worker count requires:

1. Review PostgreSQL connection budget.
2. Update deployment configuration.
3. Apply controlled restart/rollout.
4. Verify latency.
5. Verify CPU and memory.
6. Verify database connection usage.
7. Verify POS SLO.

---

# 117. Warm-Up

Optional startup warm-up may load:

* application metadata;
* reference data;
* controlled configuration.

Warm-up must remain bounded.

Failure to warm optional data must not prevent correct operation.

---

# 118. Cache Warm-Up

Cache warm-up may preload:

* Branch menu;
* effective pricing;
* safe configuration;
* reference data.

Cache warm-up failure must not make PostgreSQL-derived correctness unavailable.

---

# 119. API and Offline Client Compatibility

Deployment must consider clients that may remain offline during a release.

Valid offline operations must not become invalid merely because the server has been upgraded.

---

# 120. Synchronization Protocol Compatibility

When synchronization behavior changes:

* protocol versions must be explicit where necessary;
* backward compatibility must be preserved during migration;
* incompatible operations must fail explicitly;
* historical transaction snapshots must not be reinterpreted.

---

# 121. Synchronization Reconnection Storm

After a network outage, many devices may synchronize simultaneously.

Protection mechanisms include:

* bounded batches;
* controlled concurrency;
* backpressure;
* retry delay;
* queue prioritization.

Live POS traffic retains higher priority.

---

# 122. Capacity Planning

API capacity should consider:

```text
Business Count
Branch Count
Active POS Devices
Concurrent Cashiers
Peak Orders / Minute
Synchronization Devices
Management Requests
Report Jobs
Background Jobs
```

Capacity assumptions must be revalidated from production measurements.

---

# 123. Peak Traffic Scenarios

The runtime must account for:

* meal periods;
* shift start;
* shift closing;
* daily reporting;
* network recovery;
* large synchronization bursts;
* administrative configuration changes.

---

# 124. Horizontal Scaling

The API should support:

```text
Reverse Proxy
   ├── API Instance 1
   ├── API Instance 2
   ├── API Instance 3
   └── API Instance N
```

Scaling requires shared authoritative infrastructure.

No transaction may depend on a particular API instance.

---

# 125. Load Balancing

The load balancer/reverse proxy should distribute requests among healthy API instances.

Unready instances must not receive normal traffic.

---

# 126. Sticky Session Restriction

Sticky sessions should not be required for:

* Orders;
* Payments;
* Inventory;
* Cash Sessions;
* configuration;
* synchronization.

If a future feature requires affinity, the dependency must be explicitly documented.

---

# 127. Auto Scaling

Auto scaling may be introduced later using signals such as:

* CPU;
* request rate;
* active requests;
* p95 latency.

Scaling must have bounded minimum and maximum values.

---

# 128. API Scaling Guardrail

API scaling must trigger review of:

```text
PostgreSQL Capacity
Redis Capacity
Network Capacity
Queue Capacity
Object Storage Capacity
```

More API workers do not automatically produce more total system capacity.

---

# 129. Single-Instance Deployment

The initial system may run with one API host.

In this mode:

* API restart may cause temporary interruption;
* graceful restart is important;
* database remains authoritative;
* architecture remains compatible with future multiple instances.

Single-instance deployment is not considered highly available.

---

# 130. Multi-Instance Deployment

Multiple API instances provide:

* failure tolerance at API tier;
* rolling deployment;
* horizontal capacity;
* safer maintenance.

All instances must use compatible application and infrastructure contracts.

---

# 131. Host Replacement

An API host must be replaceable without manual recreation of Business state.

Replacement requires:

```text
Application Artifact
+
Runtime Configuration
+
Secrets
+
Infrastructure References
```

---

# 132. Local Business State Restriction

The following must never be the only copy of Business state:

```text
Gunicorn Memory
Local Cache
Temporary Files
API Host Filesystem
Worker Process State
```

---

# 133. Disaster Recovery Relationship

API runtime recovery is infrastructure reconstruction.

Conceptual sequence:

```text
Infrastructure
 ↓
Application Artifact
 ↓
Runtime Configuration
 ↓
Secrets
 ↓
Database / Required Dependencies
 ↓
Health
 ↓
Readiness
 ↓
Traffic Restoration
```

Business data recovery is governed by the dedicated Disaster Recovery architecture.

---

# 134. Security Incident Runtime Recovery

If the API runtime is compromised:

1. Isolate affected runtime.
2. Protect authoritative Business data.
3. Rotate affected credentials if required.
4. Deploy a known-good artifact.
5. Verify authentication and authorization.
6. Verify Business and Branch isolation.
7. Review logs and audit events.
8. Restore traffic gradually.

---

# 135. Secret Rotation Runtime

Secret rotation may require:

* controlled process restart;
* rolling replacement;
* temporary dual-key support where designed.

Secret rotation must not expose credentials in logs.

---

# 136. Container Compatibility

Even when the initial deployment uses systemd, the API runtime should remain container-compatible.

The process must:

* read external configuration;
* handle termination signals;
* remain stateless;
* avoid mandatory mutable host-local state;
* expose health endpoints.

---

# 137. Runtime Manifest

Deployment configuration may define:

```text
service
release
artifact
environment
worker_count
resource_limits
health_checks
timeouts
restart_policy
dependencies
```

The exact representation depends on the deployment platform.

---

# 138. Deployment Contract

The deployment artifact must identify:

```text
Python Runtime Version
Dependency Set
WSGI Entry Point
Required Configuration
Required Secrets
Required Network Dependencies
Health Endpoints
Database Compatibility
```

Deployment automation should validate these requirements.

---

# 139. Configuration Drift

Expected deployment configuration must be comparable with the active runtime configuration.

Undocumented production changes must be detectable.

---

# 140. Operational Documentation

The deployment runbook must explain:

* how to start the API;
* how to stop it;
* how to restart it;
* how to check liveness;
* how to check readiness;
* how to inspect logs;
* how to verify the release;
* how to diagnose common runtime failures.

Platform-specific commands belong in the operational runbook.

---

# 141. Runtime Testing

The runtime must be tested for:

* startup;
* invalid configuration;
* liveness;
* readiness;
* graceful shutdown;
* worker crash;
* worker restart;
* database failure;
* Redis failure;
* queue failure;
* high API load;
* synchronization burst;
* memory pressure;
* rolling deployment;
* rollback.

---

# 142. Load Testing

Load testing must include:

### POS

Concurrent order creation and modification.

### Financial

Payment and Cash Session operations.

### Inventory

Concurrent stock-affecting operations.

### Synchronization

Multiple trusted devices reconnecting.

### Management

Menu and configuration requests.

### Heavy Work

Reports and exports.

### Mixed Load

POS + synchronization + management + background processing.

Mixed-load testing is the most important production-like scenario.

---

# 143. Performance Regression

A release must be compared with the previous baseline for:

```text
p50
p95
p99
Error Rate
Timeout Rate
CPU
Memory
Database Load
Redis Load
Worker Restarts
```

A release that materially degrades core POS SLO must be investigated before acceptance.

---

# 144. Production Readiness Gate

Before production deployment:

```text
[ ] Artifact verified
[ ] Dependency versions verified
[ ] Configuration verified
[ ] Secrets available
[ ] Database compatibility verified
[ ] Worker count reviewed
[ ] Database connection budget reviewed
[ ] Request limits configured
[ ] Timeouts configured
[ ] Health checks verified
[ ] Logging enabled
[ ] Metrics enabled
[ ] Monitoring ready
[ ] Reverse proxy routing verified
[ ] Smoke tests passed
[ ] Rollback path available
```

---

# 145. Runtime Failure Matrix

| Failure                   | Expected Runtime Behavior                         |
| ------------------------- | ------------------------------------------------- |
| Gunicorn worker crash     | Worker is restarted                               |
| API process crash         | Supervisor restarts process                       |
| PostgreSQL unavailable    | Safe failure and readiness degradation            |
| Redis unavailable         | Safe degraded operation                           |
| Queue unavailable         | Outbox preserves committed state where applicable |
| Storage unavailable       | File-dependent operations fail explicitly         |
| External provider failure | Secondary work delayed or failed safely           |
| Synchronization burst     | Backpressure and throttling                       |
| Heavy reports             | Background processing                             |
| Memory pressure           | Worker recycling and/or scaling                   |
| CPU saturation            | Heavy-work throttling                             |
| Invalid configuration     | Startup failure                                   |
| New version unhealthy     | Traffic not routed                                |
| Release regression        | Controlled rollback                               |

---

# 146. Runtime Invariants

The following invariants apply to Backend API Deployment and Runtime:

1. PostgreSQL remains authoritative for transactional Business state.
2. API worker memory is never authoritative Business state.
3. Local API files are never the only durable Business storage.
4. API instances can be restarted without corrupting committed Business state.
5. API instances can be replaced without manually recreating Business state.
6. Request correctness does not depend on worker identity.
7. Request correctness does not depend on sticky sessions.
8. Multiple workers may process requests concurrently.
9. Multiple API instances may process requests concurrently.
10. Business authorization remains server-side.
11. Branch authorization remains server-side.
12. Authentication remains server-side.
13. Authorization fails closed.
14. Client Business UUID is not authoritative.
15. Client Branch UUID is not authoritative.
16. Client Employee UUID is not sufficient authentication.
17. Client Device UUID is not sufficient authentication.
18. Database connection pools are bounded.
19. Total database connection usage is deployment-budgeted.
20. Database connection acquisition is bounded.
21. Database connections are released deterministically.
22. Core transactions remain short.
23. External dependency calls do not unnecessarily hold critical transactions.
24. Large report processing does not unnecessarily occupy core API workers.
25. Large XLSX generation is asynchronous where required.
26. Heavy AI processing does not unnecessarily occupy normal API workers.
27. Request payload size is bounded.
28. File upload size is bounded.
29. Temporary files are bounded and cleaned.
30. Public clients do not normally connect directly to Gunicorn.
31. Trusted proxy headers are explicitly controlled.
32. Production debug mode is disabled.
33. Production error responses do not expose stack traces.
34. Secrets are not stored in application source.
35. Secrets are not written to logs.
36. Required configuration must be valid before readiness.
37. Liveness remains lightweight.
38. Readiness represents safe traffic acceptance.
39. Shutdown removes readiness before process exit.
40. Active requests receive a bounded drain period.
41. Uncommitted transactions are never reported as committed.
42. Committed transactions remain durable after worker restart.
43. Retryable financial commands remain idempotent.
44. Redis is not transactional authority.
45. Redis failure cannot bypass authorization.
46. Redis failure cannot bypass Business isolation.
47. Redis failure cannot bypass Branch isolation.
48. Queue infrastructure is not transactional authority.
49. Outbox records remain durable independently of immediate worker execution.
50. Synchronization batches are bounded.
51. Synchronization concurrency is bounded.
52. Synchronization traffic cannot intentionally starve POS traffic.
53. Offline operations remain idempotent.
54. Offline timestamps do not override server authority.
55. Current configuration cannot rewrite historical transaction snapshots.
56. Historical prices remain authoritative.
57. Historical Recipe Versions remain authoritative.
58. Historical Set configurations remain authoritative.
59. Historical payment information remains authoritative.
60. Runtime deployment cannot silently reinterpret historical data.
61. Request-specific context is isolated between requests.
62. Business context cannot leak between requests.
63. Branch context cannot leak between requests.
64. Worker count remains bounded.
65. Worker crash loops are observable.
66. CPU exhaustion is observable.
67. Memory pressure is observable.
68. Database pool exhaustion is observable.
69. Redis failures are observable.
70. Queue pressure is observable.
71. Synchronization pressure is observable.
72. API latency is observable.
73. API error rate is observable.
74. API availability is monitored against SLO.
75. Ordinary authenticated API p95 target is ≤ 300 ms.
76. Ordinary authenticated API p99 target is ≤ 800 ms.
77. Core POS p95 target is ≤ 500 ms.
78. Authorization overhead target is ≤ 100 ms p95.
79. Cached authorization lookup target is ≤ 20 ms p95.
80. Business/Branch validation target is ≤ 50 ms p95.
81. Idempotency lookup target is ≤ 50 ms p95.
82. Normal synchronization batch target is ≤ 1 s p95.
83. Monthly API availability target is ≥ 99.9%.
84. Performance targets are measured rather than assumed.
85. Performance optimization cannot disable authorization.
86. Performance optimization cannot remove Business isolation.
87. Performance optimization cannot remove Branch isolation.
88. Performance optimization cannot remove audit requirements.
89. API scaling requires database capacity review.
90. Horizontal scaling does not imply unlimited PostgreSQL capacity.
91. Healthy instances receive traffic.
92. Unready instances do not receive normal traffic.
93. Rolling deployment preserves sufficient serving capacity.
94. Old and new versions remain compatible during rollout where required.
95. Database migrations support controlled deployment sequencing.
96. Cache representation changes are safely versioned or invalidated.
97. Queue messages remain compatible during controlled deployment.
98. Release artifacts are reproducible.
99. Runtime dependencies are controlled.
100. Runtime secrets remain outside source artifacts.
101. Configuration drift is detectable.
102. Emergency restart preserves authoritative data.
103. Host replacement does not require manual Business data reconstruction.
104. API runtime can be rebuilt from controlled artifacts and configuration.
105. Health endpoints do not expose sensitive information.
106. Production debug facilities are disabled.
107. Runtime remains compatible with the modular monolith architecture.
108. Runtime remains compatible with future horizontal scaling.
109. Runtime remains compatible with future containerization.
110. Runtime remains compatible with future infrastructure growth.
111. Heavy workloads are throttled before threatening POS stability.
112. Retry behavior is bounded.
113. Retry storms are controlled.
114. External dependency failure cannot cause uncontrolled blocking.
115. Shutdown does not perform arbitrary long-running background work.
116. API deployment remains compatible with supported offline clients.
117. Synchronization protocol changes are explicitly versioned where required.
118. Metrics remain low-cardinality.
119. Logs do not expose credentials or tokens.
120. Operational failures remain distinguishable by dependency category.
121. Runtime configuration changes are controlled.
122. Process-level security uses least privilege.
123. API processes do not run as root under normal operation.
124. Application source is protected from unnecessary runtime writes.
125. Temporary directories are permission-restricted.
126. Cache keys preserve Business isolation.
127. Cache keys preserve Branch isolation.
128. Runtime does not become durable file storage.
129. Runtime does not become the permanent queue worker.
130. Runtime does not become the reporting engine.
131. Runtime does not become the AI inference cluster.
132. Runtime protects PostgreSQL during overload.
133. Runtime protects POS during overload.
134. Additional infrastructure is introduced only when measured need justifies it.
135. Simplicity is preferred where multiple runtime strategies provide equivalent correctness.
136. Correctness has priority over optimization.
137. Security has priority over convenience.
138. Historical integrity has priority over runtime shortcuts.

---

# 147. Recommended Runtime Structure

```text
backend/
├── app/
│   ├── api/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── security/
│   ├── background/
│   ├── synchronization/
│   └── reporting/
│
├── migrations/
├── tests/
│   ├── api/
│   ├── integration/
│   ├── performance/
│   └── runtime/
│
├── deployment/
│   ├── systemd/
│   ├── nginx/
│   ├── config/
│   └── health/
│
├── gunicorn.conf.py
├── wsgi.py
└── pyproject.toml
```

Exact implementation filenames may be refined without changing the runtime responsibilities defined by this document.

---

# 148. Recommended Runtime Configuration

Conceptually:

```text
API_RUNTIME
├── host
├── port
├── workers
├── timeout
├── keepalive
├── graceful_timeout
├── max_requests
├── max_requests_jitter
└── request_size_limit

DATABASE
├── pool_size
├── max_overflow
├── pool_timeout
├── statement_timeout
└── connection_timeout

REDIS
├── connection_timeout
├── operation_timeout
└── namespace

SECURITY
├── secret references
├── token configuration
└── trusted proxy configuration

OBSERVABILITY
├── log level
├── metrics
├── tracing
└── health endpoints
```

Actual values are environment-specific and must be managed by deployment configuration.

---

# 149. Related Documents

### Architecture

* `docs/04_Architecture/01_Backend_Architecture.md`
* `docs/04_Architecture/02_Backend_Project_Structure.md`
* `docs/04_Architecture/03_Application_and_Use_Case_Layer.md`
* `docs/04_Architecture/04_Domain_Service_and_Business_Logic.md`
* `docs/04_Architecture/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/07_Transaction_Management.md`
* `docs/04_Architecture/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/15_Backend_File_Storage_and_Document_Management.md`
* `docs/04_Architecture/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/17_Backend_Testing_and_Quality_Assurance_Architecture.md`
* `docs/04_Architecture/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/20_Backend_Operations_and_Incident_Management_Architecture.md`
* `docs/04_Architecture/21_Backend_Disaster_Recovery_and_Business_Continuity_Architecture.md`
* `docs/04_Architecture/22_Backend_Data_Consistency_and_Concurrency_Architecture.md`
* `docs/04_Architecture/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/24_Backend_Search_and_Filtering_Architecture.md`
* `docs/04_Architecture/25_Backend_Queue_and_Worker_Architecture.md`

### Deployment

* `docs/10_Deployment/01_Deployment_Architecture_Overview.md`
* `docs/10_Deployment/02_Deployment_Principles_and_Environment_Strategy.md`
* `docs/10_Deployment/03_Deployment_Topology_and_Runtime_Architecture.md`
* `docs/10_Deployment/04_Environment_Architecture_and_Configuration.md`
* `docs/10_Deployment/05_Secrets_and_Credential_Management.md`
* `docs/10_Deployment/06_Infrastructure_Architecture_and_Server_Provisioning.md`
* `docs/10_Deployment/07_Networking_DNS_TLS_and_Reverse_Proxy.md`
* `docs/10_Deployment/08_Database_Deployment_and_Runtime_Architecture.md`
* `docs/10_Deployment/09_Redis_Queue_and_Cache_Runtime_Architecture.md`
* `docs/10_Deployment/11_Frontend_Deployment_and_Static_Asset_Delivery.md`
* `docs/10_Deployment/12_Background_Workers_and_Scheduler_Deployment.md`
* `docs/10_Deployment/13_AI_Runtime_and_Model_Service_Deployment.md`
* `docs/10_Deployment/14_CI_CD_Pipeline_Architecture.md`
* `docs/10_Deployment/15_Database_Migration_and_Release_Deployment.md`
* `docs/10_Deployment/16_Release_Strategy_and_Zero_Downtime_Deployment.md`
* `docs/10_Deployment/17_Rollback_and_Release_Recovery.md`
* `docs/10_Deployment/18_Scaling_Load_Balancing_and_Capacity_Architecture.md`
* `docs/10_Deployment/19_High_Availability_and_Failure_Isolation.md`
* `docs/10_Deployment/20_Disaster_Recovery_and_Business_Continuity_Deployment.md`
* `docs/10_Deployment/21_Deployment_Monitoring_Health_Checks_and_Alerting.md`
* `docs/10_Deployment/22_Deployment_Security_Hardening.md`
* `docs/10_Deployment/23_Deployment_Testing_and_Production_Readiness.md`
* `docs/10_Deployment/24_Deployment_Governance_and_Change_Management.md`
* `docs/10_Deployment/25_Deployment_Architecture_Invariants_and_Guardrails.md`

### API

* `docs/09_API/01_API_Architecture_Overview.md`
* `docs/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/09_API/24_API_Performance_Observability_and_SLO.md`

---

# 150. Status

**Document Type:** Deployment Architecture

**Document ID:** `DEP-10`

**Document Status:** Proposed

**Version:** `1.0`

**Current Document:** `10_Backend_API_Deployment_and_Runtime.md`

**Previous Document:** `09_Redis_Queue_and_Cache_Runtime_Architecture.md`

**Next Document:** `11_Frontend_Deployment_and_Static_Asset_Delivery.md`

---

# 151. Final Architecture Principle

The Backend API runtime should remain simple and replaceable:

```text
Reverse Proxy
      ↓
Gunicorn
      ↓
Flask API
      ↓
Application
      ↓
Domain
      ↓
PostgreSQL
```

with supporting infrastructure:

```text
Redis
Queue / Outbox
Object Storage
Background Workers
AI Runtime
```

The API runtime must be treated as a stateless execution layer rather than a Business data store.

The primary runtime priorities are:

**Correctness → Security → POS Availability → Controlled Performance → Scalability → Operational Simplicity**

