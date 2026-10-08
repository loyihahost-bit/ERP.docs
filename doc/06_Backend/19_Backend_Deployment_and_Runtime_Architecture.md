# Backend Deployment and Runtime Architecture

**Document ID:** BA-19
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This document defines the deployment and runtime architecture for FastFood ERP.

The deployment architecture must provide:

* reliable production operation;
* secure network boundaries;
* predictable application startup;
* graceful shutdown;
* database safety;
* background job execution;
* offline synchronization support;
* monitoring and health checks;
* backup and recovery;
* controlled deployments;
* horizontal scalability when required.

The initial deployment must remain simple enough to operate without unnecessary infrastructure complexity.

---

## 2. Deployment Principles

The system follows these principles:

1. Production deployment must be reproducible.
2. PostgreSQL remains the authoritative data store.
3. Application instances must remain stateless where practical.
4. Local application filesystem must not be treated as durable shared storage.
5. Secrets must never be stored in source code.
6. Database migrations must be controlled and reversible where practical.
7. Deployment must not silently destroy existing data.
8. Background workers must be isolated from API request processing.
9. POS traffic must have priority over non-critical background workloads.
10. Health checks must distinguish liveness from readiness.
11. Shutdown must be graceful.
12. Failed deployments must be detectable quickly.
13. Backups must be tested through restoration.
14. Monitoring must cover both application and infrastructure.
15. Scaling must be introduced only when actual workload requires it.
16. Security boundaries must be preserved during deployment.
17. Offline clients must remain operational during temporary API outages within their authorization limits.

---

## 3. Initial Deployment Model

The initial production environment may use a single application server with separated runtime processes.

Recommended topology:

```text id="dpl982"
                    Internet
                       |
                     HTTPS
                       |
                    Nginx
                       |
              +--------+--------+
              |                 |
          Web/API          Static assets
              |
        Application Server
        +------+------+
        |             |
      Gunicorn      Workers
        |             |
        +------+------+
               |
        +------+------+
        |             |
    PostgreSQL       Redis
        |
   Backup Storage
```

Redis is optional.

The architecture must function correctly without Redis.

---

## 4. Production Runtime Components

The initial production deployment consists of:

* Nginx;
* Gunicorn/application workers;
* PostgreSQL;
* optional Redis;
* background worker process;
* scheduler process where required;
* persistent file storage;
* backup mechanism;
* monitoring/logging components.

Each component has a clearly defined responsibility.

---

## 5. Nginx Responsibilities

Nginx acts as the external HTTP reverse proxy.

Responsibilities include:

* TLS termination;
* HTTP to HTTPS redirect;
* request forwarding;
* connection limits;
* request size limits;
* basic rate limiting where appropriate;
* security headers;
* static file delivery where applicable;
* access logging;
* upstream health behavior.

Nginx must not contain business logic.

---

## 6. Gunicorn Responsibilities

Gunicorn hosts the Python application.

Responsibilities include:

* application process management;
* worker lifecycle;
* graceful worker restart;
* request concurrency;
* worker timeout management;
* worker recycling where required.

Gunicorn must not execute long-running background jobs inside request workers.

---

## 7. Gunicorn Worker Model

The initial runtime should use synchronous or appropriate worker behavior based on actual Flask workload.

Initial configuration must be benchmarked rather than blindly maximizing worker count.

Example principle:

```text id="gnm531"
CPU cores
   ↓
benchmark
   ↓
worker count
   ↓
database connection capacity
```

Worker count must be coordinated with:

* CPU;
* RAM;
* database pool;
* expected concurrency.

Too many workers may reduce performance by exhausting memory or database connections.

---

## 8. Worker Count Guardrail

The deployment must not configure unlimited workers.

Initial production configuration should be conservative.

For example:

```text
2–4 Gunicorn workers
```

may be suitable for a small server, but the exact number must be determined through load testing.

Worker count is a deployment configuration, not a business rule.

---

## 9. Background Workers

Background workers handle tasks that should not block HTTP requests.

Examples:

* notifications;
* email;
* print jobs;
* report generation;
* XLSX exports;
* synchronization processing where appropriate;
* cleanup;
* subscription lifecycle jobs;
* deletion jobs;
* maintenance;
* reconciliation.

Workers must invoke Application-layer use cases rather than directly manipulating business state.

---

## 10. Worker Isolation

Background workers should have separate process/resource limits from API workers.

A heavy report must not consume all CPU or memory required by POS requests.

Priority:

```text id="pri741"
POS/API
  ↓
Synchronization
  ↓
Operational background jobs
  ↓
Reports/exports
  ↓
Cleanup/maintenance
```

Exact queue priority may be adjusted after production measurements.

---

## 11. Scheduler

Scheduled tasks may include:

* subscription expiry checks;
* deletion eligibility checks;
* report generation;
* notification generation;
* cleanup;
* reconciliation;
* backup verification;
* maintenance.

The scheduler must create bounded jobs rather than perform large operations itself.

---

## 12. PostgreSQL Runtime

PostgreSQL is the primary authoritative database.

The application must connect through a controlled connection pool.

PostgreSQL must not be publicly exposed to the Internet.

Network access should be limited to:

* application servers;
* worker servers where required;
* approved administration/backup systems.

---

## 13. PostgreSQL Connection Pool

Connection pool configuration must consider the total number of application processes.

Example:

```text
Gunicorn workers × pool capacity
+
Worker process pools
<
PostgreSQL max connections
```

The deployment must avoid connection exhaustion.

Pool size must be load-tested.

---

## 14. Database Connection Guardrail

The total theoretical database connections must leave reserved capacity for:

* migrations;
* administrative access;
* monitoring;
* emergency operations.

The application must not consume 100% of PostgreSQL connection capacity.

---

## 15. Redis Runtime

Redis is optional infrastructure.

Potential uses:

* cache;
* short-lived coordination;
* rate limiting;
* job queue support;
* ephemeral state.

Redis must not become the authoritative source for:

* Orders;
* Payments;
* Cash Sessions;
* Inventory;
* historical audit;
* configuration history.

---

## 16. Redis Failure Behavior

If Redis becomes unavailable:

* cache-dependent reads should fall back where practical;
* core database operations must continue;
* financial state must remain correct;
* API correctness must not depend on cached values.

Performance may degrade, but correctness must remain intact.

---

## 17. File Storage

Durable files must use persistent storage.

Examples:

* report exports;
* uploaded product images;
* documents;
* generated files.

The application container/process filesystem must not be considered durable.

Storage access must go through the File Storage abstraction.

---

## 18. File Storage Security

Stored files must have:

* unique identifiers;
* controlled access;
* metadata;
* Business scope;
* optional Branch scope;
* owner/creator context where required;
* creation timestamp;
* retention information where applicable.

Raw filesystem paths must never be exposed to clients.

---

## 19. Network Topology

Production should use network separation:

```text
Internet
   |
HTTPS
   |
Nginx
   |
Application Network
   |
+--+----------+-----------+
|             |           |
App         Worker     Monitoring
|
+-----------+
|
Private Data Network
|
+-----------+-----------+
|                       |
PostgreSQL             Redis
```

PostgreSQL and Redis should not be directly accessible from the public Internet.

---

## 20. Firewall Rules

Production firewall rules should allow only required traffic.

Typical public access:

```text
TCP 443 → Nginx
```

HTTP port 80 may be used only for HTTPS redirection if required.

Database and Redis ports should remain private.

SSH administration should be restricted where possible.

---

## 21. TLS

Production API traffic must use HTTPS.

TLS configuration must:

* disable obsolete protocols;
* use trusted certificates;
* automatically renew certificates where possible;
* redirect HTTP to HTTPS;
* avoid insecure mixed content.

Certificate expiration must be monitored.

---

## 22. Domain and DNS

Production DNS should point to the external reverse proxy/load balancer.

DNS changes must be documented.

Where multiple application servers are introduced:

```text
DNS / Load Balancer
        ↓
App 1
App 2
App 3
```

Application instances must remain stateless enough to support this model.

---

## 23. Environment Separation

At minimum:

```text id="env203"
Development
Testing
Staging
Production
```

Each environment must have separate:

* database;
* credentials;
* secrets;
* storage;
* API configuration;
* external integration credentials.

Production data must not be copied into development without an approved anonymization process.

---

## 24. Production Configuration

Production configuration must be external to source code.

Examples:

```text
DATABASE_URL
REDIS_URL
SECRET_KEY
TOKEN_SIGNING_KEY
STORAGE_CONFIG
EMAIL_CONFIG
APP_ENV
```

Secrets must be supplied through a secure secret/configuration mechanism.

---

## 25. Secret Management

Secrets must not be committed to Git.

Examples:

* database passwords;
* JWT signing keys;
* encryption keys;
* API credentials;
* SMTP credentials;
* storage credentials.

`.env.example` may contain placeholders but never real secrets.

---

## 26. Application Startup

Application startup should perform controlled validation.

Startup checks may include:

* configuration validity;
* required environment variables;
* database connectivity;
* migration compatibility;
* cryptographic configuration;
* storage configuration;
* required external dependencies.

The application should fail fast when a mandatory configuration is invalid.

---

## 27. Startup Dependency Policy

Not every dependency must block application startup.

For example:

```text
PostgreSQL unavailable
→ readiness failure

Redis unavailable
→ application may start if Redis is optional

Email provider unavailable
→ application may start

Printer unavailable
→ application may start
```

The distinction between critical and optional dependencies must be explicit.

---

## 28. Database Migration Strategy

Alembic is used for database schema migrations.

Migrations must be:

* version-controlled;
* reviewed;
* tested;
* ordered;
* reproducible.

Production migrations must not be manually edited after execution.

---

## 29. Expand/Contract Migration

Breaking database changes should use expand/contract deployment.

Example:

```text
Version N
    ↓
Add new nullable column
    ↓
Deploy compatible application
    ↓
Backfill
    ↓
Switch application behavior
    ↓
Validate
    ↓
Remove old column later
```

This reduces deployment downtime and rollback risk.

---

## 30. Migration Safety

Production migrations must avoid:

* uncontrolled destructive operations;
* long blocking table rewrites where avoidable;
* unbounded data transformations;
* deleting historical data accidentally.

Large migrations should be broken into bounded operations.

---

## 31. Migration Locking

Migration execution must be serialized.

Two deployment processes must not run conflicting migrations simultaneously.

The deployment system must have a clear migration ownership mechanism.

---

## 32. Deployment Order

Recommended order:

```text
1. Validate release
2. Backup / verify backup state
3. Apply compatible database migration
4. Deploy application
5. Start/restart workers
6. Run readiness checks
7. Run smoke tests
8. Enable traffic
9. Monitor
```

For expand/contract changes, migration and application compatibility must be maintained across the transition.

---

## 33. Zero-Downtime Deployment

The architecture should support zero or near-zero downtime for normal releases.

For multiple application instances:

```text
Load Balancer
     |
     +-- App A
     |
     +-- App B
```

Instances can be upgraded progressively.

For the initial single-server deployment, a short controlled restart may be acceptable if measured and documented.

---

## 34. Graceful Shutdown

Application shutdown must:

1. stop accepting new requests;
2. allow active safe requests to finish;
3. stop accepting new background jobs;
4. finish or safely release active jobs;
5. close database connections;
6. close Redis connections;
7. exit cleanly.

The shutdown timeout must be bounded.

---

## 35. Worker Shutdown

Workers must support graceful shutdown.

A worker should not terminate halfway through a critical operation without recovery handling.

Retryable jobs must remain recoverable.

Financial state must be protected by database transactions and idempotency.

---

## 36. Request Timeout

HTTP requests must have bounded timeouts.

Long operations must not remain open indefinitely.

Examples of operations that should normally be asynchronous:

* large report;
* XLSX export;
* large file processing;
* bulk maintenance.

---

## 37. Process Recovery

Production process supervisors should automatically restart failed application/worker processes.

Possible mechanisms include:

* systemd;
* container orchestration;
* process supervisors.

The initial deployment may use systemd for simplicity.

---

## 38. Recommended Initial Linux Runtime

For a simple VPS deployment:

```text
systemd
  ├── nginx.service
  ├── fastfood-api.service
  ├── fastfood-worker.service
  └── fastfood-scheduler.service
```

PostgreSQL may run:

* locally;
* or on a managed/private database server.

Redis may be local or managed.

---

## 39. systemd Responsibilities

systemd should manage:

* startup;
* restart;
* dependency ordering;
* environment configuration;
* process limits;
* service user;
* shutdown behavior.

Application services should run under dedicated non-root users.

---

## 40. Root Privilege Restriction

The FastFood application must not normally run as root.

Recommended:

```text
fastfood
  ↓
dedicated service user
```

Nginx should also use its standard restricted user model.

---

## 41. Runtime Filesystem Permissions

Application directories must use least privilege.

Writable locations should be limited to:

* temporary files;
* required runtime files;
* local cache if used.

Source code and configuration should not be writable by the runtime process unless explicitly required.

---

## 42. Dependency Installation

Production dependencies must be pinned or constrained through the Python dependency management strategy.

Deployment should install the exact tested dependency set.

Unexpected package upgrades must not occur during normal production deployment.

---

## 43. Build Artifact

Production should deploy a reproducible application artifact.

The artifact should contain:

* application source/package;
* locked dependencies;
* migration code;
* static assets where applicable;
* version metadata.

The artifact should identify the application release version.

---

## 44. Release Version

Each deployment must have a release identifier.

Example:

```text
FastFood ERP
Release: 2026.10.06-abc123
```

The release identifier should be visible in:

* logs;
* health information where safe;
* monitoring;
* deployment records.

---

## 45. Health Endpoints

The API provides:

```text
GET /health/live
GET /health/ready
```

### Liveness

Confirms that the process is running.

### Readiness

Confirms that the instance can safely receive traffic.

Readiness may check:

* PostgreSQL connectivity;
* required migration compatibility;
* critical configuration.

Optional dependencies should not necessarily make the service unready.

---

## 46. Health Check Security

Health endpoints must not expose:

* database credentials;
* connection strings;
* internal hostnames;
* secrets;
* detailed exception traces.

External health output should remain minimal.

---

## 47. Startup and Readiness States

The service lifecycle should be conceptually:

```text
STARTING
   ↓
INITIALIZING
   ↓
READY
   ↓
DEGRADED
   ↓
NOT_READY
   ↓
STOPPING
```

The implementation may use simpler states, but readiness behavior must remain clear.

---

## 48. Graceful Degradation

The application should continue operating when non-critical components fail.

Examples:

```text
Redis unavailable
→ PostgreSQL fallback

Email unavailable
→ notification remains queued

Printer unavailable
→ Order remains committed, print job retries

Report worker unavailable
→ report job remains pending

External API unavailable
→ bounded retry / failure state
```

---

## 49. POS Availability Priority

During resource pressure, the system should prioritize:

1. authentication;
2. POS order operations;
3. payments;
4. cash operations;
5. inventory operations;
6. synchronization;
7. business management;
8. reports;
9. exports;
10. cleanup.

Background work must not consume all available resources.

---

## 50. Resource Limits

Production services should have explicit limits for:

* CPU;
* memory;
* file descriptors;
* database connections;
* worker concurrency;
* queue size;
* request body size;
* upload size;
* report size;
* synchronization batch size.

Limits must be based on measured workload.

---

## 51. Memory Protection

The application must avoid unbounded in-memory operations.

Examples:

* paginated queries;
* streaming large exports where appropriate;
* bounded synchronization batches;
* bounded report datasets;
* controlled file uploads.

A single request must not be able to exhaust process memory.

---

## 52. CPU Protection

Expensive operations should be moved to background workers.

Examples:

* XLSX generation;
* large reports;
* image processing;
* large synchronization reconciliation.

Workers should have concurrency limits.

---

## 53. Database Protection

The application must prevent:

* unbounded queries;
* unbounded result sets;
* excessive connection creation;
* long-running idle transactions;
* unnecessary repeated queries.

Database performance targets follow the database and backend performance documents.

---

## 54. Runtime Logging

Production logs should be structured.

Minimum context:

```text
timestamp
level
service
release
request_id
operation_id
Business
Branch
employee
device
endpoint
status
latency
error_code
```

Sensitive information must be excluded.

---

## 55. Log Levels

Recommended levels:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Production should normally avoid unrestricted DEBUG logging.

Temporary debug logging must be controlled and time-limited.

---

## 56. Log Retention

Logs should have a defined retention policy based on:

* operational requirements;
* security requirements;
* storage cost;
* privacy requirements.

Logs must not grow without bounds.

---

## 57. Monitoring

Monitoring should cover:

### Application

* request latency;
* error rate;
* throughput;
* worker queue;
* worker failures;
* synchronization failures.

### Database

* CPU;
* memory;
* disk;
* connections;
* query latency;
* locks;
* deadlocks;
* replication state if applicable.

### Infrastructure

* CPU;
* RAM;
* disk;
* network;
* filesystem;
* certificate expiration.

---

## 58. Critical Alerts

Alerts should exist for:

* API availability below SLO;
* PostgreSQL unavailable;
* database disk near capacity;
* database connection exhaustion;
* worker queue growth;
* repeated worker crashes;
* failed migrations;
* backup failure;
* certificate expiration;
* suspicious authentication failures;
* synchronization conflict spikes;
* storage failure.

---

## 59. Performance SLOs

Initial runtime targets:

| Metric                         |          Target |
| ------------------------------ | --------------: |
| API availability               | ≥ 99.9% monthly |
| Ordinary API p95               |        ≤ 300 ms |
| Core POS command p95           |        ≤ 500 ms |
| Ordinary API p99               |        ≤ 800 ms |
| Authorization overhead p95     |        ≤ 100 ms |
| Health check p95               |        ≤ 100 ms |
| Readiness check p95            |        ≤ 500 ms |
| Normal sync batch p95          |           ≤ 1 s |
| Background job acknowledgement |           ≤ 2 s |
| Graceful shutdown              |          ≤ 30 s |
| Deployment smoke test          |         ≤ 5 min |
| Critical alert detection       |          ≤ 60 s |

These are initial engineering targets and must be validated through load testing.

---

## 60. Availability SLO Scope

The 99.9% API availability target applies to normal production API availability excluding:

* planned maintenance communicated in advance;
* force majeure;
* external provider failures outside system control.

Internal infrastructure failures remain within the operational reliability target.

---

## 61. Recovery Point Objective

Initial target:

**RPO ≤ 15 minutes**

for production database data where the selected backup/replication architecture supports it.

The exact achievable RPO must be validated against the deployed PostgreSQL backup strategy.

---

## 62. Recovery Time Objective

Initial target:

**RTO ≤ 2 hours**

for a major production database/server failure.

The target includes:

* infrastructure recovery;
* database restoration;
* application startup;
* migration compatibility;
* health validation;
* smoke testing.

---

## 63. Backup Strategy

Backups must include:

* PostgreSQL data;
* required configuration;
* persistent application files;
* deployment metadata where necessary.

Backups must be stored separately from the primary runtime server.

---

## 64. Backup Frequency

Recommended initial strategy:

```text
Continuous / frequent WAL-based recovery
+
Daily full database backup
+
Regular file backup
```

Exact implementation depends on the PostgreSQL hosting model.

---

## 65. Backup Retention

Retention must support:

* operational recovery;
* accidental deletion recovery;
* security incident investigation;
* subscription lifecycle requirements where legally/business-wise required.

Live Business deletion does not automatically imply immediate destruction of every backup copy.

Backup lifecycle must be separately controlled.

---

## 66. Backup Encryption

Backups must be encrypted at rest.

Access must be restricted to authorized infrastructure/service identities.

Backup credentials must not be stored in source code.

---

## 67. Backup Verification

A backup is not considered reliable merely because the backup job reports success.

The system must periodically perform restoration tests.

Example:

```text
Backup
  ↓
Restore to isolated environment
  ↓
Run integrity checks
  ↓
Run application smoke tests
  ↓
Record result
```

---

## 68. Disaster Recovery

Major failure scenarios include:

* server loss;
* PostgreSQL corruption;
* accidental deletion;
* ransomware/security compromise;
* storage failure;
* deployment failure;
* certificate failure;
* Redis loss.

The recovery process must be documented and tested.

---

## 69. Deployment Failure

If deployment fails:

1. stop further rollout;
2. preserve logs;
3. determine whether database changes are compatible;
4. restore application version where safe;
5. do not blindly downgrade schema;
6. validate health;
7. monitor;
8. document incident.

---

## 70. Database Rollback

Database rollback is not assumed to mean reversing a migration.

For destructive migrations, preferred strategy:

```text
restore / forward-fix
```

rather than blindly executing a reverse migration against production data.

---

## 71. Application Rollback

Application rollback should be possible when database compatibility permits.

Expand/contract migrations are specifically intended to preserve this compatibility.

---

## 72. Deployment Smoke Tests

After deployment, automated smoke tests should verify:

* API reachable;
* authentication works;
* authorization works;
* database access works;
* basic Product read;
* basic Order read/create path where safe;
* health endpoints;
* worker availability.

Production smoke tests must avoid creating uncontrolled financial data.

---

## 73. Deployment Security

Deployment credentials must be separated from application runtime credentials.

CI/CD should use minimal permissions.

Deployment systems must not automatically receive unrestricted database administrator access unless required.

---

## 74. CI/CD

A controlled deployment pipeline should include:

```text
Commit
  ↓
Lint
  ↓
Unit tests
  ↓
Integration tests
  ↓
Security checks
  ↓
API contract tests
  ↓
Build artifact
  ↓
Migration validation
  ↓
Deploy staging
  ↓
Smoke tests
  ↓
Production approval
  ↓
Production deployment
  ↓
Post-deploy validation
```

---

## 75. Production Approval

Production deployment should require an explicit controlled release step.

For critical changes:

* security review;
* migration review;
* rollback plan;
* monitoring plan

should be available before deployment.

---

## 76. Infrastructure as Code

Infrastructure configuration should eventually be version-controlled where practical.

Examples:

* server configuration;
* systemd service definitions;
* Nginx configuration;
* firewall rules;
* monitoring configuration;
* backup configuration.

Secrets remain outside source control.

---

## 77. Containerization

Containerization is optional in the initial deployment.

The architecture must not depend on Docker/Kubernetes.

A direct Linux deployment using:

```text
Nginx
+
Gunicorn
+
systemd
+
PostgreSQL
```

is valid for the initial production scale.

Containerization may be introduced later if operational benefits justify it.

---

## 78. Kubernetes

Kubernetes is not required for the initial deployment.

It may become appropriate when:

* application instances become numerous;
* automatic scaling becomes necessary;
* multi-node orchestration becomes operationally difficult;
* deployment complexity justifies orchestration.

Introducing Kubernetes without actual operational need is discouraged.

---

## 79. Horizontal Scaling

When workload grows:

```text
Load Balancer
      |
+-----+-----+-----+
|     |     |     |
App1 App2 App3
      |
 PostgreSQL
      |
 Redis
```

Application instances must remain stateless enough to support this.

Sessions, caches, jobs and files must use shared/appropriate infrastructure.

---

## 80. Database Scaling

The initial database may remain a single PostgreSQL primary.

Future scaling options include:

* stronger hardware;
* query optimization;
* connection pooling;
* read replicas;
* partitioning;
* archival;
* reporting replicas.

Database sharding is not part of the initial architecture.

---

## 81. Redis Scaling

Redis may later be separated into dedicated infrastructure if:

* cache load increases;
* queue workload increases;
* multiple application instances require shared coordination.

Redis scaling must not change database authority.

---

## 82. File Storage Scaling

As file volume grows, local storage may be replaced with:

* S3-compatible object storage;
* managed object storage;
* dedicated file storage.

The application continues using the File Storage abstraction.

---

## 83. Multi-Server Worker Scaling

Workers may be scaled independently from API instances.

Example:

```text
API servers
    2
    |
Worker servers
    2–N
    |
PostgreSQL
```

Queue priority must preserve POS/API performance.

---

## 84. Deployment and Offline Devices

Deployment must account for trusted offline devices.

An API release must not invalidate valid offline authorization unexpectedly unless a security or lifecycle rule requires it.

Backward-compatible synchronization contracts are required during rolling deployments.

---

## 85. Sync Compatibility During Deployment

During rolling deployment:

```text
Old API
+
New API
+
Offline client
```

may temporarily coexist.

Therefore:

* synchronization payloads must remain compatible;
* unknown optional fields should be tolerated where safe;
* old operations must not be silently reinterpreted;
* operation UUID semantics must remain stable.

---

## 86. Configuration Deployment

Environment configuration changes should follow controlled deployment.

Business/Branch configuration changes are runtime business operations and must not require server redeployment.

The two mechanisms must remain separate.

---

## 87. Runtime Feature Flags

Feature flags may be used for controlled rollout.

Feature flags must not replace:

* authorization;
* subscription entitlement;
* Business configuration;
* security policy.

A disabled feature must fail predictably.

---

## 88. Maintenance Mode

A controlled maintenance mode may be implemented for exceptional operations.

Maintenance mode must:

* be explicit;
* be auditable;
* show a controlled user message;
* avoid corrupting in-flight transactions;
* not silently discard requests.

Critical security operations may remain available to authorized administrators where appropriate.

---

## 89. Operational Runbooks

Production must have runbooks for:

* application restart;
* worker restart;
* database restart;
* Redis failure;
* migration failure;
* backup restore;
* certificate renewal;
* disk pressure;
* high memory usage;
* high database connections;
* synchronization backlog;
* deployment rollback.

---

## 90. Incident Response

Operational incidents should follow:

```text
Detect
  ↓
Assess
  ↓
Contain
  ↓
Recover
  ↓
Validate
  ↓
Monitor
  ↓
Post-incident review
```

Critical incidents must preserve relevant logs and audit information.

---

## 91. Runtime Security

Production servers must use:

* least-privilege users;
* firewall;
* SSH hardening;
* automatic security updates where safe;
* dependency updates;
* TLS;
* restricted database access;
* secret protection;
* file permission controls.

Application security requirements remain defined in:

`16_Backend_Security_Hardening_and_Application_Security.md`

---

## 92. Runtime Resource Monitoring

The following thresholds should be monitored:

* CPU saturation;
* memory pressure;
* disk usage;
* inode usage;
* database connections;
* database locks;
* queue depth;
* worker failure rate;
* API latency;
* error rate.

Alert thresholds should be tuned from real production baselines.

---

## 93. Disk Protection

The application must monitor disk capacity.

Recommended operational alerts:

```text
70% → warning
80% → important
90% → critical
```

These values may be adjusted according to storage characteristics.

At critical levels, non-essential background jobs may be paused.

---

## 94. Database Disk Protection

Database disk pressure is critical.

If database storage approaches capacity:

1. alert operators;
2. reduce non-essential workload;
3. investigate large queries/tables/logs;
4. expand storage;
5. do not automatically delete business data.

---

## 95. Queue Protection

Background queues must have bounded capacity.

If queue depth grows significantly:

* alert;
* preserve POS/API priority;
* scale workers where possible;
* pause low-priority jobs if necessary.

A queue backlog must not cause unlimited memory growth.

---

## 96. Database Maintenance

Regular maintenance should include:

* VACUUM;
* ANALYZE;
* index health review;
* slow query review;
* connection review;
* table growth review.

PostgreSQL autovacuum should remain enabled unless there is a documented reason otherwise.

---

## 97. Runtime Time Synchronization

Production servers must use reliable time synchronization.

Correct time is important for:

* authentication;
* offline authorization;
* audit timestamps;
* Cash Sessions;
* synchronization;
* subscription lifecycle;
* logs.

Clock rollback detection remains part of security.

---

## 98. Timezone

Backend system timestamps should use UTC.

Business and Branch reporting should apply configured timezone.

Server local timezone must not become an implicit business rule.

---

## 99. Runtime Dependency Health

Dependencies should be classified:

### Critical

* PostgreSQL;
* application configuration;
* cryptographic/signing configuration.

### Important

* Redis;
* job queue;
* file storage.

### Optional

* email provider;
* external integrations;
* printing infrastructure.

This classification determines readiness and degradation behavior.

---

## 100. Release Observability

Every release should be observable through:

* release ID;
* deployment timestamp;
* application version;
* migration version;
* worker version;
* configuration version where relevant.

This allows operators to correlate incidents with deployments.

---

## 101. Canary / Progressive Deployment

When multiple servers exist, progressive deployment may be used:

```text
New release
   ↓
1 instance
   ↓
Smoke test
   ↓
Monitor
   ↓
Remaining instances
```

This reduces blast radius.

---

## 102. Rollout Abort Conditions

A deployment should stop if there is a significant increase in:

* 5xx responses;
* authentication failures;
* database errors;
* transaction failures;
* synchronization failures;
* latency;
* worker crashes;
* memory consumption.

Thresholds should be defined by monitoring configuration.

---

## 103. Runtime Compatibility

The deployment environment must document supported versions of:

* Python;
* PostgreSQL;
* Nginx;
* Redis where used;
* operating system;
* required system libraries.

Dependency upgrades require testing before production rollout.

---

## 104. Production Data Protection

Production data must be protected against:

* accidental deletion;
* unauthorized access;
* corruption;
* deployment mistakes;
* infrastructure failure.

The runtime must never use production database credentials for development/testing environments.

---

## 105. Data Deletion Jobs

Business deletion after the subscription lifecycle must be performed as a controlled background process.

Deletion must be:

* authorized;
* state-aware;
* auditable;
* bounded;
* resumable;
* idempotent where possible.

A large Business must not be deleted in one unbounded transaction.

---

## 106. Deletion and Backup

Live data deletion does not necessarily mean immediate deletion from every backup.

Backup retention must follow the defined backup lifecycle.

The system must distinguish:

```text
Live Data
Backup Data
Audit/Operational Logs
```

and apply their respective retention rules.

---

## 107. Runtime Testing

Deployment must be tested through:

* startup tests;
* readiness tests;
* graceful shutdown tests;
* migration tests;
* backup restore tests;
* deployment rollback tests;
* load tests;
* security tests;
* worker recovery tests;
* queue recovery tests;
* Redis failure tests;
* PostgreSQL failure/recovery tests.

---

## 108. Production Readiness Checklist

Before production:

* [ ] HTTPS enabled.
* [ ] Firewall configured.
* [ ] PostgreSQL private.
* [ ] Redis private if used.
* [ ] Secrets externalized.
* [ ] Production debug disabled.
* [ ] Database backups enabled.
* [ ] Backup restoration tested.
* [ ] Migration strategy validated.
* [ ] Health endpoints available.
* [ ] Monitoring enabled.
* [ ] Critical alerts configured.
* [ ] Log retention configured.
* [ ] Resource limits configured.
* [ ] Worker recovery configured.
* [ ] Graceful shutdown verified.
* [ ] Smoke tests automated.
* [ ] Rollback procedure documented.
* [ ] Runbooks available.
* [ ] Release version visible.
* [ ] Security review completed.

---

## 109. Deployment Anti-Patterns

The following are prohibited:

* PostgreSQL exposed directly to the Internet;
* application running as root without justification;
* production secrets committed to Git;
* unlimited Gunicorn workers;
* unlimited database connections;
* unbounded background concurrency;
* unbounded report generation;
* application filesystem treated as permanent storage;
* destructive migration without recovery strategy;
* automatic production dependency upgrades;
* Redis treated as financial authority;
* health endpoint exposing secrets;
* no backup restoration testing;
* no deployment rollback strategy;
* no graceful shutdown;
* running heavy reports inside API workers;
* production and development sharing the same database;
* silent migration downgrade;
* background workers bypassing Application/Domain rules.

---

## 110. Deployment Invariants

The following invariants apply to deployment and runtime:

1. PostgreSQL remains the authoritative persistent data store.
2. Application processes are stateless where practical.
3. Redis is never the financial source of truth.
4. PostgreSQL is not publicly exposed.
5. Production secrets are not stored in source code.
6. Application services do not normally run as root.
7. Database connections are bounded.
8. Gunicorn workers are bounded.
9. Background worker concurrency is bounded.
10. Request processing is bounded by timeouts.
11. Large operations use asynchronous processing where appropriate.
12. Background work cannot consume all resources required by POS.
13. Liveness and readiness are separate concepts.
14. Readiness reflects critical dependency availability.
15. Optional dependency failure does not automatically make the API unavailable.
16. Application startup validates mandatory configuration.
17. Invalid mandatory configuration causes startup failure.
18. Production debug mode is disabled.
19. Production API traffic uses HTTPS.
20. Database migrations are version-controlled.
21. Migration execution is serialized.
22. Destructive migration is controlled.
23. Expand/contract is preferred for breaking schema changes.
24. Database rollback is not assumed to be a simple reverse migration.
25. Application rollback depends on database compatibility.
26. Deployment release identifiers are recorded.
27. Production deployments are observable.
28. Failed deployment rollout can be stopped.
29. Health checks do not expose sensitive information.
30. Application shutdown is graceful.
31. Worker shutdown is graceful.
32. In-flight critical transactions remain protected during shutdown.
33. Failed workers can recover automatically.
34. Retryable jobs are idempotent or otherwise safely recoverable.
35. Queue size is bounded.
36. Disk usage is monitored.
37. Database storage pressure is monitored.
38. Backup jobs are monitored.
39. Backup restoration is periodically tested.
40. Backup storage is separate from primary runtime storage.
41. Backups are protected against unauthorized access.
42. RPO target is explicitly defined.
43. RTO target is explicitly defined.
44. Business data deletion is bounded and resumable.
45. Business deletion does not rely on one unbounded transaction.
46. Live deletion and backup retention are separate lifecycle concerns.
47. Production and development databases are separate.
48. Production credentials are not reused in development.
49. File storage is abstracted from application logic.
50. Local application filesystem is not assumed durable.
51. File access remains authorization-controlled.
52. Runtime time synchronization is enabled.
53. UTC is used for backend system timestamps.
54. Business/Branch timezone is explicit.
55. Offline authorization remains valid according to its security rules during normal deployment.
56. API synchronization contracts remain backward-compatible during rolling deployment.
57. Old and new application versions may coexist only when their contracts are compatible.
58. POS operations receive higher runtime priority than reports and cleanup.
59. API performance remains within defined SLOs.
60. API availability target is ≥99.9% monthly.
61. Initial RPO target is ≤15 minutes where infrastructure supports it.
62. Initial RTO target is ≤2 hours.
63. Critical alerts are detected within the defined alerting target.
64. Deployment smoke tests run after release.
65. Security failures fail closed.
66. Infrastructure changes are reviewed and controlled.
67. Runtime configuration is separated from Business configuration.
68. Feature flags do not replace authorization.
69. Monitoring must not create uncontrolled high-cardinality metrics.
70. Deployment must preserve Business isolation.
71. Deployment must preserve Branch isolation.
72. Deployment must preserve historical data integrity.
73. Deployment must preserve idempotency semantics.
74. Deployment must preserve synchronization semantics.
75. Deployment must not silently alter financial state.
76. Operational recovery procedures are documented.
77. Critical runtime failures have defined recovery paths.
78. Infrastructure complexity is introduced only when operationally justified.

---

## 111. Recommended Initial Production Topology

For the first production stage:

```text
                    Internet
                       |
                    HTTPS :443
                       |
                     Nginx
                       |
                 Gunicorn / Flask
                 2–4 workers*
                       |
            +----------+----------+
            |                     |
       PostgreSQL              Redis*
            |                     |
            +----------+----------+
                       |
                 Background Worker
                       |
                 Scheduler
                       |
                 File Storage
                       |
                 Backup Storage

* Redis is optional.
* Worker count must be validated through load testing.
```

The architecture must remain compatible with a future multi-server topology.

---

## 112. Future Scaled Topology

When workload requires horizontal scaling:

```text
                       Internet
                          |
                   Load Balancer
                          |
             +------------+------------+
             |            |            |
           App 1        App 2        App N
             |            |            |
             +------------+------------+
                          |
                  Shared Infrastructure
                    +-----+------+
                    |            |
                PostgreSQL      Redis
                    |
              Backup / Replica
                    |
             Object/File Storage

Background Workers
        |
     Queue
        |
PostgreSQL / Storage
```

Scaling should be driven by measurable workload rather than architecture preference.

---

## 113. Operational Priorities

During incidents, the system should prioritize:

1. Data integrity.
2. Security.
3. POS availability.
4. Payment correctness.
5. Cash correctness.
6. Inventory correctness.
7. Synchronization correctness.
8. Business management.
9. Reporting.
10. Non-critical background processing.

Correctness takes precedence over convenience.

---

## 114. Status

**Backend Architecture Document:** Completed.

**Document Status:** Proposed.

**Current Document:** `19_Backend_Deployment_and_Runtime_Architecture.md`

**Next Document:** `20_Backend_Operations_and_Incident_Management_Architecture.md`

