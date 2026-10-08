# Backend Operations and Incident Management Architecture

**Document ID:** BA-20
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the operational architecture for running, monitoring, maintaining, recovering and troubleshooting the FastFood ERP backend in production.

The system must remain reliable during:

* normal production load;
* temporary infrastructure failures;
* database failures;
* Redis failures;
* background worker failures;
* synchronization problems;
* deployment failures;
* security incidents;
* storage failures;
* network interruptions;
* unexpected application errors;
* partial service degradation.

Operations must preserve:

* business data integrity;
* tenant isolation;
* historical integrity;
* auditability;
* offline continuity;
* synchronization correctness;
* security;
* recoverability.

The operational model must remain simple enough for the initial VPS-based deployment while allowing future horizontal scaling.

---

# 2. Operational Principles

The backend follows these principles:

1. PostgreSQL remains the authoritative business data store.
2. Redis is never the source of truth.
3. Background workers are replaceable and restartable.
4. Failed background jobs must be retryable.
5. Important business operations must remain recoverable.
6. Operational recovery must not rewrite historical business data.
7. Incident response must prioritize business continuity and data integrity.
8. Security incidents must fail closed where authoritative security decisions cannot be verified.
9. Monitoring must detect failures before users report them where practical.
10. Operational tooling must not bypass application business rules without explicit privileged procedures.
11. Production changes must be traceable.
12. Backups are useful only if restoration has been tested.
13. Deployment must support rollback or forward recovery.
14. Operational automation must be idempotent.
15. Manual emergency actions must be audited.

---

# 3. Operational Scope

This document covers:

* production runtime;
* service lifecycle;
* monitoring;
* health checks;
* metrics;
* logging;
* alerting;
* incident classification;
* incident response;
* escalation;
* service degradation;
* recovery;
* deployment incidents;
* database incidents;
* Redis incidents;
* worker incidents;
* synchronization incidents;
* security incidents;
* data integrity incidents;
* backup and restore operations;
* disaster recovery;
* maintenance;
* operational access;
* runbooks;
* post-incident review;
* SLO monitoring;
* operational invariants.

---

# 4. Production Runtime

The initial production environment may use:

```text
Internet
   ↓
Nginx
   ↓
Gunicorn
   ↓
FastFood Backend
   ↓
PostgreSQL

Optional:
Redis
Background Worker
Scheduler
File Storage
Backup Storage
Monitoring
```

The initial deployment may run on a Linux VPS.

The architecture must not require Kubernetes or another orchestration platform at the initial stage.

Future deployments may introduce:

* multiple application instances;
* load balancer;
* managed PostgreSQL;
* managed Redis;
* distributed workers;
* centralized logging;
* external monitoring;
* object storage.

---

# 5. Service Components

Operationally important components include:

### 5.1. API Service

Responsible for:

* authentication;
* authorization;
* POS operations;
* business management;
* configuration;
* reports queries;
* synchronization API.

### 5.2. Background Worker

Responsible for:

* notifications;
* emails;
* print jobs;
* report generation;
* XLSX exports;
* synchronization processing where applicable;
* lifecycle jobs;
* cleanup;
* reconciliation.

### 5.3. Scheduler

Responsible for scheduled tasks such as:

* report generation;
* subscription checks;
* notification scheduling;
* cleanup;
* deletion lifecycle processing;
* reconciliation;
* operational maintenance.

### 5.4. PostgreSQL

Authoritative store for:

* business data;
* orders;
* payments;
* inventory;
* cash;
* configuration;
* audit;
* synchronization state;
* report versions;
* lifecycle state.

### 5.5. Redis

Optional acceleration layer for:

* cache;
* rate limiting;
* temporary coordination.

Redis failure must not corrupt authoritative business state.

### 5.6. File Storage

Used for:

* generated reports;
* XLSX files;
* product images;
* documents;
* other persistent files.

Application local filesystem must not be treated as durable storage.

---

# 6. Service Lifecycle

Every production service must support:

```text
STARTING
   ↓
READY
   ↓
RUNNING
   ↓
DEGRADED
   ↓
DRAINING
   ↓
STOPPED
```

A service may transition directly to:

```text
STARTING → FAILED
```

if startup validation fails.

A failed service must not report itself as healthy.

---

# 7. Startup Validation

Application startup must validate critical configuration before accepting traffic.

Validation includes:

* environment;
* required configuration;
* secret availability;
* database connectivity;
* migration compatibility;
* application version;
* required signing configuration;
* required encryption configuration;
* storage configuration;
* queue configuration;
* security configuration.

Invalid critical configuration must cause startup failure.

The application must fail fast instead of running with unsafe defaults.

---

# 8. Health Endpoints

The backend provides at least:

```text
GET /health/live
GET /health/ready
```

## 8.1. Liveness

Liveness answers:

> Is the process alive?

It must not perform expensive dependency checks.

Target:

**p95 ≤ 100 ms**

## 8.2. Readiness

Readiness answers:

> Can this instance safely receive normal production traffic?

Readiness may validate:

* PostgreSQL;
* required application state;
* migration compatibility;
* critical configuration.

Target:

**p95 ≤ 500 ms**

Redis failure must not automatically make the entire API unavailable when Redis is non-authoritative.

---

# 9. Health Status

Health state should distinguish:

```text
HEALTHY
DEGRADED
UNHEALTHY
UNKNOWN
```

Examples:

### HEALTHY

All critical dependencies operate normally.

### DEGRADED

A non-critical dependency is unavailable.

Example:

```text
Redis unavailable
```

while PostgreSQL and API remain operational.

### UNHEALTHY

A critical dependency prevents safe operation.

Example:

```text
PostgreSQL unavailable
```

### UNKNOWN

Monitoring cannot reliably determine service state.

---

# 10. Graceful Shutdown

When a service is stopping:

1. stop accepting new work;
2. mark instance unavailable for new traffic;
3. allow safe in-flight requests to complete;
4. stop claiming new background jobs;
5. finish safe current jobs;
6. release database connections;
7. flush required logs;
8. exit.

Target:

**Graceful shutdown ≤ 30 seconds**

Long-running jobs must support retry/recovery instead of requiring indefinite shutdown time.

---

# 11. Process Supervision

Initial VPS deployment may use `systemd`.

Recommended services:

```text
nginx.service
fastfood-api.service
fastfood-worker.service
fastfood-scheduler.service
postgresql.service
redis.service
```

Service restart policies must use bounded restart behavior.

A continuously crashing service must not create an uncontrolled restart loop.

---

# 12. Logging Architecture

The backend uses structured logs.

Each important log should contain where applicable:

* timestamp;
* level;
* service;
* release/version;
* environment;
* request_id;
* operation_id;
* Business UUID;
* Branch UUID;
* employee UUID;
* device UUID;
* cash session UUID;
* endpoint;
* HTTP method;
* status;
* latency;
* error code;
* exception type;
* source.

Logs must not contain:

* passwords;
* authentication secrets;
* access tokens;
* refresh tokens;
* private keys;
* encryption keys;
* full payment secrets;
* sensitive personal data unless explicitly required.

---

# 13. Log Levels

Supported levels:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

### DEBUG

Development and troubleshooting information.

Normally disabled or restricted in production.

### INFO

Normal operational events.

Examples:

* service started;
* deployment completed;
* worker started;
* synchronization batch completed.

### WARNING

Unexpected but recoverable conditions.

Examples:

* retry;
* stale cache;
* temporary external failure;
* synchronization conflict.

### ERROR

Operation failed and requires attention.

### CRITICAL

Potential major outage, security incident or data integrity problem.

---

# 14. Logging Reliability

Logging must not block critical POS transactions indefinitely.

If the centralized logging destination is temporarily unavailable:

* application operation should continue where safe;
* local buffering may be used;
* critical security/audit events must have stronger durability requirements;
* logs must be flushed/recovered where possible.

Business audit data is separate from ordinary application logs.

---

# 15. Metrics

Operational metrics must cover:

### API

* request count;
* error count;
* latency;
* p50;
* p95;
* p99;
* status code distribution;
* endpoint throughput.

### Database

* connection usage;
* connection pool exhaustion;
* query latency;
* slow queries;
* lock waits;
* deadlocks;
* transaction duration;
* disk usage;
* replication state where applicable;
* WAL growth.

### Workers

* queue depth;
* job execution time;
* retry count;
* failure count;
* dead-letter count;
* worker availability.

### Synchronization

* batches received;
* operations processed;
* operations rejected;
* conflicts;
* retry count;
* duplicate operations;
* processing latency;
* pending backlog.

### Cache

* hit rate;
* miss rate;
* latency;
* errors;
* eviction;
* invalidation failures.

### Storage

* disk usage;
* file creation failures;
* export failures;
* backup storage capacity.

---

# 16. Business Metrics vs Operational Metrics

Business metrics and operational metrics must remain separate.

Operational metrics answer:

> Is the system healthy?

Business metrics answer:

> What is happening in the business?

Examples:

```text
Operational:
API p95 = 240 ms

Business:
Orders today = 1,842
```

Operational dashboards must not become the authoritative source for financial reporting.

---

# 17. Alerting

Alerts must be actionable.

An alert should contain:

* problem;
* affected service;
* severity;
* detected time;
* relevant metric;
* current state;
* probable impact;
* recommended runbook;
* escalation level.

Alerts should not be generated for every ordinary warning.

---

# 18. Alert Severity

Recommended levels:

```text
P0 — Critical
P1 — High
P2 — Medium
P3 — Low
```

## P0

Major outage or severe integrity/security problem.

Examples:

* PostgreSQL unavailable;
* confirmed cross-Business isolation failure;
* confirmed data corruption;
* production-wide API outage.

## P1

Major functionality significantly affected.

Examples:

* POS operations broadly failing;
* synchronization backlog growing rapidly;
* payment processing unavailable;
* workers permanently failing for critical jobs.

## P2

Limited degradation.

Examples:

* report generation delayed;
* email notifications delayed;
* Redis unavailable while API remains functional.

## P3

Minor issue or maintenance warning.

Examples:

* disk usage approaching threshold;
* non-critical job retries.

---

# 19. Incident Definition

An incident is an operational event that causes or threatens:

* service availability;
* business continuity;
* data integrity;
* security;
* synchronization correctness;
* financial correctness.

Not every application error is an incident.

A single rejected invalid request is normally not an incident.

A widespread unexpected failure is.

---

# 20. Incident Lifecycle

The incident lifecycle is:

```text
DETECTED
   ↓
TRIAGED
   ↓
CONTAINED
   ↓
RECOVERED
   ↓
VERIFIED
   ↓
CLOSED
   ↓
POST-INCIDENT REVIEW
```

---

# 21. Incident Detection

Incidents may be detected by:

* monitoring;
* alerts;
* health checks;
* logs;
* security systems;
* synchronization monitoring;
* employee reports;
* Owner reports;
* automated integrity checks.

Monitoring should detect critical failures without depending entirely on user reports.

---

# 22. Incident Triage

Initial triage determines:

1. What is failing?
2. Which services are affected?
3. Which Businesses/Branches are affected?
4. Is data integrity at risk?
5. Is security at risk?
6. Is POS operational?
7. Is synchronization affected?
8. Is rollback safe?
9. Is customer-facing degradation required?
10. What is the current severity?

---

# 23. Incident Containment

Containment aims to prevent further damage.

Examples:

* stop a faulty deployment;
* disable a problematic feature;
* pause a failing worker;
* stop a bad synchronization route;
* isolate an affected component;
* revoke compromised device access;
* block malicious traffic.

Containment must not silently modify historical business data.

---

# 24. Degraded Mode

The system should degrade gracefully where safe.

Examples:

### Redis unavailable

Continue using PostgreSQL where possible.

### Email unavailable

Keep in-app notifications and queue email for retry.

### Printer unavailable

Keep Order state authoritative and queue/retry printing.

### Report worker unavailable

Keep core POS and business operations running.

### External API unavailable

Use retry/reconciliation where supported.

---

# 25. Critical Dependency Failure

If PostgreSQL is unavailable:

* new authoritative transactions cannot safely commit;
* API must fail safely;
* cached data must not be treated as authoritative;
* client must not assume transaction success;
* offline-capable trusted devices may continue permitted local operations according to offline rules;
* synchronization must retry later.

The backend must never report a transaction as successfully committed when PostgreSQL has not confirmed it.

---

# 26. PostgreSQL Incident

When PostgreSQL is degraded:

1. identify connection failure;
2. check database health;
3. inspect connection pool;
4. inspect locks/deadlocks;
5. inspect disk capacity;
6. inspect CPU/memory/I/O;
7. inspect recent deployments/migrations;
8. protect data integrity;
9. fail or degrade safely;
10. restore service;
11. validate transaction consistency.

Manual database modification is prohibited unless performed through an approved emergency procedure.

---

# 27. Database Connection Exhaustion

If the connection pool is exhausted:

* identify long-running queries;
* identify blocked transactions;
* identify leaked connections;
* inspect worker concurrency;
* inspect background job load;
* reduce unnecessary concurrency;
* terminate only explicitly identified unsafe sessions where necessary.

The system must not blindly terminate all database connections.

---

# 28. Long-Running Transactions

Long-running transactions must be monitored.

Potential causes:

* unexpected application behavior;
* report query;
* lock contention;
* network interaction inside transaction;
* forgotten transaction closure.

Core POS transactions must remain short.

Long-running transactions must not become a normal operational pattern.

---

# 29. Deadlock Handling

Deadlocks are recoverable database errors.

The application may perform bounded retry when:

* operation is safe;
* transaction is retryable;
* operation is idempotent where necessary.

Each retry must use a fresh transaction.

Unbounded retries are prohibited.

---

# 30. Redis Incident

Redis is non-authoritative.

If Redis fails:

* application should fall back where practical;
* cache misses may increase;
* rate limiting may use a safe fallback or fail closed where security requires it;
* business data must remain correct;
* Redis restart must not require database reconstruction.

Redis recovery must not alter PostgreSQL business state.

---

# 31. Background Worker Incident

Workers may fail independently from API service.

If a worker fails:

* unprocessed jobs remain recoverable;
* retryable jobs are retried;
* permanent failures are marked;
* critical jobs are alerted;
* API operations remain available where possible.

A worker restart must not duplicate business effects.

---

# 32. Dead-Letter Handling

Jobs that repeatedly fail may enter a dead-letter state.

Dead-letter records must retain:

* job UUID;
* operation UUID;
* job type;
* attempts;
* last error;
* first failure;
* latest failure;
* relevant Business/Branch scope;
* timestamps.

Dead-letter jobs must be manually or automatically recoverable through an explicit process.

---

# 33. Queue Backlog

Queue backlog is monitored.

Alert thresholds should consider:

* queue depth;
* oldest job age;
* job priority;
* processing rate;
* failure rate.

POS-related asynchronous work receives higher operational priority than:

* reports;
* exports;
* cleanup;
* historical maintenance.

---

# 34. Synchronization Incident

Synchronization incidents require special handling because offline transactions may contain valid business operations.

The system must distinguish:

```text
Accepted
Rejected
Duplicate
Conflict
Retryable Failure
Permanent Failure
```

A synchronization failure must not cause the device to blindly resend the same operation indefinitely.

---

# 35. Synchronization Backlog

Monitoring must track:

* total pending operations;
* oldest pending operation;
* rejected operations;
* conflict count;
* retry count;
* Business/Branch concentration;
* device concentration.

Critical backlog growth must generate an alert.

---

# 36. Synchronization Recovery

Recovery must:

1. identify affected devices;
2. preserve received operation UUIDs;
3. determine accepted operations;
4. retry safe transient failures;
5. resolve conflicts explicitly;
6. prevent duplicate application;
7. reconcile authoritative state;
8. report final synchronization state.

Client-side assumptions must not override server-authoritative results.

---

# 37. Security Incident

Security incidents include:

* unauthorized access;
* credential compromise;
* suspicious device;
* privilege escalation attempt;
* cross-Business access attempt;
* invalid offline signature;
* token abuse;
* suspicious synchronization;
* malicious request patterns.

Security incidents receive priority based on potential impact.

---

# 38. Security Incident Containment

Possible actions include:

* revoke session;
* revoke trusted device;
* disable employee;
* disable compromised integration credential;
* increase rate limiting;
* block malicious source;
* disable affected feature;
* preserve forensic logs.

Emergency containment must be auditable.

---

# 39. Tenant Isolation Incident

A suspected cross-Business data access issue is automatically treated as critical.

Immediate actions:

1. stop affected endpoint or feature;
2. preserve logs;
3. identify affected requests;
4. determine exposure;
5. revoke affected sessions if necessary;
6. inspect repository/query scope;
7. verify Business isolation;
8. patch;
9. test;
10. reopen service only after validation.

Cross-Business isolation must have a target of:

**100% prevention of unauthorized access.**

---

# 40. Data Integrity Incident

Potential data integrity incidents include:

* duplicate payment;
* duplicate inventory deduction;
* incorrect cash balance;
* incorrect Order total;
* broken historical snapshot;
* incorrect synchronization application;
* corrupted configuration version;
* unexpected financial mutation.

Data integrity incidents are higher priority than ordinary availability issues.

---

# 41. Data Integrity Response

The first priority is:

**Stop further incorrect writes.**

Then:

1. identify affected operation;
2. identify affected Business/Branch;
3. preserve evidence;
4. determine first bad state;
5. identify affected transactions;
6. stop automated propagation where necessary;
7. restore safe processing;
8. create corrections through business mechanisms;
9. preserve historical records;
10. audit the recovery.

Historical records must not be silently overwritten.

---

# 42. Financial Incident

Financial incidents include:

* duplicate payment;
* incorrect refund;
* cash discrepancy caused by system error;
* incorrect Order financial amount;
* incorrect inventory cost affecting financial reports.

Financial corrections must use explicit correction mechanisms.

Direct database edits must not be used as a normal correction method.

---

# 43. Deployment Incident

A deployment incident may occur when a release causes:

* elevated errors;
* latency degradation;
* migration problems;
* authentication failures;
* synchronization failures;
* POS failures;
* data integrity problems.

Deployment must immediately be considered a possible incident source after a recent release.

---

# 44. Deployment Rollback

Rollback is allowed only when safe.

Application rollback may be performed when:

* database schema remains compatible;
* migration is backward-compatible;
* rollback does not lose committed data.

Destructive database rollback must not be performed merely to restore application version.

When rollback is unsafe:

**forward recovery** must be used.

---

# 45. Forward Recovery

Forward recovery means:

1. keep compatible schema;
2. identify defect;
3. prepare corrective release;
4. deploy correction;
5. validate;
6. reconcile affected data if required.

This is preferred over destructive rollback when business data has already been written under the new version.

---

# 46. Migration Incident

Database migrations must be treated as high-risk production changes.

If migration fails:

* do not blindly rerun destructive operations;
* inspect migration state;
* determine whether transaction committed;
* verify schema;
* verify application compatibility;
* restore from backup only when required;
* use forward migration where possible.

---

# 47. Backup Architecture

Backups must cover:

* PostgreSQL database;
* required configuration;
* persistent files;
* required operational metadata.

Recommended strategy:

```text
Continuous/WAL backup
        +
Daily full backup
        +
File backup
        +
Separate backup storage
```

Backups must be:

* encrypted;
* access-controlled;
* monitored;
* independently stored.

---

# 48. Backup Verification

A successful backup job does not prove recoverability.

The system must periodically perform restore tests.

Restore testing must verify:

* database opens;
* migrations are compatible;
* required files exist;
* application can connect;
* important business records exist;
* audit/history remains intact.

---

# 49. Recovery Point Objective

Target:

**RPO ≤ 15 minutes**, where infrastructure supports appropriate WAL/continuous backup.

For infrastructure without continuous backup capability, the actual RPO must be explicitly documented.

---

# 50. Recovery Time Objective

Target:

**RTO ≤ 2 hours**

for a major infrastructure failure under the initial production architecture.

RTO includes:

* infrastructure recovery;
* database recovery;
* application startup;
* worker startup;
* health validation;
* smoke testing.

---

# 51. Disaster Recovery

A disaster may include:

* complete VPS loss;
* disk failure;
* PostgreSQL corruption;
* accidental infrastructure deletion;
* severe security compromise.

Recovery process:

```text
Provision replacement infrastructure
        ↓
Restore secrets/configuration
        ↓
Restore PostgreSQL
        ↓
Restore files
        ↓
Validate schema
        ↓
Deploy compatible application
        ↓
Start workers
        ↓
Run health checks
        ↓
Run smoke tests
        ↓
Enable traffic
        ↓
Monitor
```

---

# 52. Disaster Recovery Validation

After recovery, verify at minimum:

* authentication;
* authorization;
* Business isolation;
* Branch isolation;
* POS;
* Order creation;
* payment;
* inventory;
* cash session;
* synchronization;
* notifications;
* reports;
* file access;
* audit;
* subscription state.

---

# 53. Maintenance Windows

Maintenance must be planned where practical.

Maintenance communication should include:

* start time;
* expected duration;
* affected functionality;
* risk;
* rollback/recovery plan.

Maintenance must not unnecessarily interrupt POS operations.

---

# 54. Zero-Downtime Preference

The architecture should prefer changes that do not require full application downtime.

Examples:

* rolling application restart;
* backward-compatible migration;
* expand/contract schema changes;
* background migration;
* cache version transition.

Full downtime may be accepted for exceptional maintenance where necessary.

---

# 55. Operational Access

Production access must follow least privilege.

Roles should distinguish:

```text
Application Operator
Database Operator
Security Operator
Infrastructure Operator
Developer
Super Admin
```

A Super Admin business role must not automatically provide operating-system or database access.

Application privilege and infrastructure privilege are separate.

---

# 56. Emergency Access

Emergency access must:

* require explicit authorization;
* be time-limited where possible;
* be logged;
* be reviewed afterward;
* use the minimum required privilege.

Emergency access must not become a permanent bypass mechanism.

---

# 57. Operational Commands

Operational scripts must be:

* version-controlled;
* documented;
* idempotent where possible;
* safe by default;
* environment-aware;
* explicit about destructive operations.

Examples:

```text
backup verification
restore verification
queue inspection
failed job retry
cache invalidation
health diagnostic
synchronization inspection
report regeneration
```

---

# 58. Destructive Operations

Potentially destructive commands must require explicit confirmation.

Examples:

* deleting data;
* forcing lifecycle deletion;
* dropping database objects;
* removing files;
* invalidating large numbers of devices;
* clearing operational queues.

Production destructive commands must not default to production execution.

---

# 59. Runbooks

Each recurring operational incident should have a runbook.

A runbook should contain:

1. symptom;
2. impact;
3. severity;
4. detection;
5. immediate containment;
6. diagnostic commands;
7. recovery steps;
8. validation;
9. rollback/forward recovery;
10. escalation;
11. post-incident checks.

Initial runbooks should include:

```text
API unavailable
PostgreSQL unavailable
Redis unavailable
Worker stopped
Queue backlog
Synchronization backlog
Failed deployment
Migration failure
Disk full
High CPU
High memory
Backup failure
Restore procedure
Security incident
Tenant isolation incident
Data integrity incident
```

---

# 60. Operational Diagnostics

Diagnostic tooling must avoid changing business state.

Read-only diagnostics should be preferred.

Examples:

* service status;
* process status;
* queue depth;
* database connection count;
* slow queries;
* lock state;
* error rates;
* synchronization status;
* backup status.

Diagnostic queries must respect Business isolation when application-level data is inspected.

---

# 61. Performance Incident

Performance incidents may involve:

* increased API latency;
* database saturation;
* lock contention;
* cache failure;
* queue backlog;
* CPU saturation;
* memory pressure;
* disk I/O saturation.

Investigation order:

```text
Application
    ↓
Database
    ↓
Cache
    ↓
Background Jobs
    ↓
Infrastructure
    ↓
External Dependencies
```

The actual root cause must be verified using metrics and logs.

---

# 62. API SLOs

Production API targets:

| Metric                     |          Target |
| -------------------------- | --------------: |
| API availability           | ≥ 99.9% monthly |
| Ordinary API p95           |        ≤ 300 ms |
| Core POS command p95       |        ≤ 500 ms |
| Ordinary API p99           |        ≤ 800 ms |
| Authorization overhead p95 |        ≤ 100 ms |
| Liveness p95               |        ≤ 100 ms |
| Readiness p95              |        ≤ 500 ms |

These are operational targets, not guarantees under unlimited load.

---

# 63. Background SLOs

Targets:

| Metric                             | Target |
| ---------------------------------- | -----: |
| Job acknowledgement                |  ≤ 2 s |
| Critical alert detection           | ≤ 60 s |
| Critical security event visibility | ≤ 60 s |
| Normal sync batch p95              |  ≤ 1 s |
| Graceful shutdown                  | ≤ 30 s |

Long-running reports and XLSX exports are asynchronous and are not required to meet ordinary API latency targets.

---

# 64. Security SLOs

Security-related targets:

| Metric                                        |          Target |
| --------------------------------------------- | --------------: |
| Critical security event ingestion             |         ≥ 99.9% |
| Security log availability                     | ≥ 99.9% monthly |
| Mandatory audit event creation                |        ≥ 99.99% |
| Duplicate operation rejection                 |        ≥ 99.99% |
| Online device revocation                      |          ≤ 30 s |
| Employee deactivation propagation             |          ≤ 30 s |
| Authorization invalidation                    |          ≤ 30 s |
| Cross-Business unauthorized access prevention |            100% |
| Cross-Branch unauthorized access prevention   |            100% |

---

# 65. Monitoring SLO

Monitoring itself is an operational dependency.

The monitoring system should target:

**≥ 99.9% monthly availability**

Critical incidents must not depend on a single monitoring component.

Where practical, production health monitoring should exist outside the monitored application infrastructure.

---

# 66. Capacity Management

Capacity must be monitored before resources become critical.

Track:

* CPU;
* RAM;
* disk;
* PostgreSQL storage;
* WAL;
* database connections;
* Redis memory;
* queue depth;
* worker concurrency;
* API throughput.

Capacity alerts should be based on sustained pressure rather than one short spike.

---

# 67. Initial Resource Planning

The initial deployment should use bounded resources.

Examples of bounded resources:

* Gunicorn workers;
* PostgreSQL connections;
* worker concurrency;
* Redis memory;
* request body size;
* file upload size;
* queue size;
* report generation concurrency.

The exact values are environment-specific and must be measured through load testing.

---

# 68. Autoscaling Future

The architecture must allow future scaling to:

```text
Load Balancer
      ↓
API Instance 1
API Instance 2
API Instance N
      ↓
PostgreSQL
Redis
Workers
```

The application should remain stateless where practical.

Session state must not depend on one application process.

---

# 69. Cache Recovery

After Redis restart or cache flush:

* PostgreSQL remains authoritative;
* cache entries are repopulated;
* stale cache must not override newer data;
* cache versioning prevents incompatible data use;
* application remains correct even if cache is empty.

Cache warm-up should not block core POS functionality.

---

# 70. File Storage Recovery

If file storage is temporarily unavailable:

* core business transactions continue where possible;
* file-dependent operations fail safely;
* generated reports remain retryable;
* database metadata must not claim a file exists when persistence was not confirmed.

---

# 71. Notification Recovery

If email or another external notification provider fails:

* in-app notification remains authoritative for supported notification types;
* failed external delivery is retryable;
* provider failure does not roll back the business transaction;
* repeated failures are monitored.

---

# 72. Printing Incident

Printer failure must not rollback an accepted Order.

The system must distinguish:

```text
Order Accepted
Print Pending
Print Processing
Print Success
Print Failed
```

A print failure may generate:

* retry;
* operational alert;
* manual reprint.

Manual reprint must be audited where required.

---

# 73. Subscription and Lifecycle Jobs

Lifecycle operations are operationally sensitive.

Scheduled jobs must monitor:

* subscription expiry processing;
* READ_ONLY transitions;
* DELETION_ELIGIBLE transitions;
* deletion scheduling;
* deletion execution;
* backup retention.

A lifecycle job failure must not silently delete or permanently alter business data.

Deletion requires explicit lifecycle state validation.

---

# 74. Data Deletion Incident

If deletion automation behaves incorrectly:

1. stop deletion workers;
2. preserve affected state;
3. identify affected Businesses;
4. verify lifecycle state;
5. determine whether deletion is reversible;
6. restore from backup where necessary;
7. investigate root cause;
8. correct automation;
9. resume only after validation.

Deletion jobs must be designed with bounded batches and restartability.

---

# 75. Operational Audit

The following operational actions must be auditable where applicable:

* emergency access;
* production configuration changes;
* deployment;
* rollback;
* manual job retry;
* device revocation;
* lifecycle intervention;
* data recovery;
* manual reconciliation;
* security containment;
* privileged database operation.

Operational audit records must contain:

* actor;
* timestamp;
* environment;
* action;
* target;
* reason;
* result;
* request/operation ID where applicable.

---

# 76. Change Management

Production changes should follow:

```text
Plan
  ↓
Review
  ↓
Test
  ↓
Deploy
  ↓
Validate
  ↓
Monitor
```

High-risk changes require:

* backup verification;
* rollback/forward recovery plan;
* migration review;
* monitoring plan;
* explicit approval.

---

# 77. Change Categories

Changes may be classified as:

```text
Standard
Normal
High Risk
Emergency
```

Examples:

### Standard

Low-risk configuration or routine restart.

### Normal

Application release.

### High Risk

Database migration affecting core financial tables.

### Emergency

Security containment or critical outage recovery.

---

# 78. Incident Communication

During major incidents, communication must be concise and factual.

Internal incident updates should include:

```text
Status:
Impact:
Affected Components:
Current Action:
Next Check:
Owner:
```

Do not speculate about root cause before evidence is available.

---

# 79. Incident Ownership

Every P0/P1 incident must have a clearly identified incident owner.

The owner is responsible for:

* coordination;
* prioritization;
* communication;
* containment;
* recovery;
* verification;
* closure.

The incident owner does not necessarily perform every technical action.

---

# 80. Escalation

Escalation occurs when:

* impact increases;
* recovery is blocked;
* security risk increases;
* data integrity is uncertain;
* SLO breach becomes likely;
* specialist access is required.

Escalation must happen early for critical data/security incidents.

---

# 81. Incident Closure

An incident may be closed only after:

* service recovered;
* affected functionality validated;
* no active dangerous error remains;
* queues are stable;
* synchronization is stable;
* data integrity is checked where applicable;
* security containment is complete where applicable.

A service appearing “up” is not sufficient if business correctness remains uncertain.

---

# 82. Post-Incident Review

P0 and significant P1 incidents require a post-incident review.

The review should contain:

* incident summary;
* timeline;
* impact;
* detection method;
* root cause;
* contributing factors;
* containment;
* recovery;
* affected data;
* missed detection;
* corrective actions;
* preventive actions;
* owner;
* deadline.

The purpose is system improvement, not blame.

---

# 83. Corrective Actions

Corrective actions may include:

* code fix;
* database constraint;
* additional monitoring;
* improved test;
* configuration change;
* runbook update;
* security control;
* capacity adjustment;
* architectural change.

Every corrective action should have an owner and measurable completion condition.

---

# 84. Testing Operational Recovery

Operational recovery must be tested.

Tests should include:

* application restart;
* worker restart;
* Redis restart;
* database backup restore;
* database fail/recovery;
* queue retry;
* dead-letter recovery;
* synchronization retry;
* cache flush;
* failed deployment recovery;
* migration recovery;
* security incident containment.

---

# 85. Game Day / Recovery Exercise

At planned intervals, the team should simulate selected failures.

Example:

```text
Scenario:
Redis unavailable

Expected result:
POS continues
Cache misses increase
No business data corruption
Alert generated
Redis restored
Cache repopulates
```

Other scenarios should include PostgreSQL failure, worker failure and synchronization backlog.

---

# 86. Operational Security

Operational infrastructure must follow:

* least privilege;
* SSH key authentication;
* restricted administrative access;
* firewall;
* private database access;
* encrypted transport;
* secret rotation;
* audit logging;
* dependency patching;
* OS security updates.

Production database must not be publicly exposed.

---

# 87. Secret Incident

If a production secret is suspected to be compromised:

1. identify secret;
2. determine scope;
3. revoke/rotate secret;
4. invalidate affected sessions/credentials where necessary;
5. inspect access logs;
6. determine exposure;
7. restore normal service;
8. document incident.

Secrets must never be committed to Git.

---

# 88. Dependency Incident

If a dependency contains a serious vulnerability:

1. identify affected versions;
2. determine whether the dependency is reachable;
3. assess exploitability;
4. patch or upgrade;
5. run security tests;
6. deploy;
7. monitor.

Emergency dependency updates must still pass essential compatibility tests.

---

# 89. Operational Data Access

Production business data should not be copied to developer machines as a routine troubleshooting method.

When data inspection is required:

* use controlled access;
* minimize exposed data;
* redact sensitive fields;
* record privileged access where appropriate.

Production data must remain protected during diagnostics.

---

# 90. Environment Separation

Production must remain isolated from:

* development;
* testing;
* local machines;
* staging.

Production credentials must never be reused in development.

Test automation must not point to production.

---

# 91. Operational Tooling Structure

Recommended structure:

```text
backend/
├── scripts/
│   ├── health/
│   ├── backup/
│   ├── restore/
│   ├── diagnostics/
│   ├── synchronization/
│   ├── maintenance/
│   └── migration/
├── configuration/
└── app/
```

Operational scripts must call supported application services or safe infrastructure commands rather than duplicating business logic.

---

# 92. Operational Documentation

Production documentation should include:

```text
docs/
├── 04_Architecture/
├── 10_Deployment/
└── 14_Operations/
```

Operational documentation should include:

* deployment procedure;
* rollback procedure;
* backup procedure;
* restore procedure;
* incident runbooks;
* monitoring guide;
* security response;
* synchronization recovery;
* disaster recovery.

---

# 93. Operational Readiness Checklist

Before production launch:

### Infrastructure

* [ ] TLS configured
* [ ] Firewall configured
* [ ] PostgreSQL private
* [ ] Redis private
* [ ] Secrets protected
* [ ] Service users configured
* [ ] Backup storage configured

### Application

* [ ] Production configuration validated
* [ ] Debug disabled
* [ ] Health endpoints available
* [ ] Graceful shutdown tested
* [ ] Error handling tested
* [ ] Logging enabled
* [ ] Metrics enabled

### Database

* [ ] Migrations validated
* [ ] Backup tested
* [ ] Restore tested
* [ ] Connection pool configured
* [ ] Slow query monitoring enabled

### Security

* [ ] Authentication tested
* [ ] Authorization tested
* [ ] Business isolation tested
* [ ] Branch isolation tested
* [ ] Rate limiting tested
* [ ] Secret rotation procedure documented

### Operations

* [ ] Alerts configured
* [ ] Runbooks available
* [ ] Incident owner defined
* [ ] Escalation procedure defined
* [ ] Disaster recovery procedure tested

---

# 94. System Operational Invariants

The following invariants apply to Backend Operations and Incident Management:

1. PostgreSQL remains authoritative for business state.
2. Redis is never authoritative.
3. Cache failure must not corrupt business data.
4. Service health must distinguish liveness from readiness.
5. Unhealthy services must not report readiness.
6. Critical configuration failures must prevent unsafe startup.
7. Graceful shutdown must stop new work before termination.
8. Background jobs must be recoverable.
9. Retryable jobs must not create duplicate business effects.
10. Job retries must be bounded.
11. Dead-letter jobs must remain inspectable.
12. Queue backlog must be observable.
13. Synchronization backlog must be observable.
14. Synchronization operation UUIDs remain stable across retries.
15. Duplicate synchronization operations must not duplicate business effects.
16. Server state remains authoritative after synchronization.
17. Critical security events must be durable.
18. Security secrets must not appear in ordinary logs.
19. Production credentials must not be stored in source code.
20. Production database must not be publicly exposed.
21. Operational access follows least privilege.
22. Emergency access is auditable.
23. Manual production interventions are traceable.
24. Historical business data must not be silently overwritten during recovery.
25. Financial corrections use explicit correction mechanisms.
26. Database recovery must preserve transaction integrity.
27. Backup success alone does not prove recoverability.
28. Restore testing is required.
29. RPO must be measurable.
30. RTO must be measurable.
31. Application rollback must not cause committed business data loss.
32. Forward recovery is preferred when rollback is unsafe.
33. Destructive migrations require explicit planning.
34. Failed migrations must not be blindly rerun.
35. Redis recovery must not require business-state reconstruction.
36. Printer failure must not rollback accepted Orders.
37. Notification failure must not rollback committed business transactions.
38. Report failure must not block core POS operations.
39. XLSX generation must remain asynchronous.
40. Background maintenance must not unnecessarily block POS.
41. Lifecycle deletion must be restartable.
42. Lifecycle jobs must validate current state before destructive action.
43. Security incidents receive priority based on impact.
44. Suspected tenant-isolation failure is critical.
45. Data-integrity incidents prioritize stopping incorrect writes.
46. Incident severity must reflect business impact.
47. Every P0/P1 incident has an owner.
48. Major incidents require post-incident review.
49. Corrective actions must have owners.
50. Operational runbooks must be executable and maintained.
51. Monitoring must itself be monitored.
52. Alerts must be actionable.
53. Critical alerts must not depend on one fragile component.
54. Operational diagnostics should prefer read-only operations.
55. Production data must be protected during troubleshooting.
56. Development and production environments remain isolated.
57. Test automation must not target production.
58. Operational scripts must be version-controlled.
59. Destructive operational scripts require explicit confirmation.
60. Service restarts must not silently lose accepted transactions.
61. Database connection pools must be bounded.
62. Worker concurrency must be bounded.
63. Queue processing must be prioritized.
64. POS-related asynchronous work has higher priority than maintenance workloads.
65. Performance degradation must be observable through metrics.
66. API latency must be measured at p50, p95 and p99.
67. Database lock contention must be observable.
68. Background job failures must be observable.
69. Backup failures must generate alerts.
70. Restore failures must generate alerts.
71. Disk capacity must be monitored.
72. Resource exhaustion must not be handled through uncontrolled automatic restarts.
73. Incident recovery must include functional validation.
74. Service availability alone is not sufficient for incident closure.
75. Data integrity must be verified where relevant.
76. Synchronization correctness must be verified after synchronization incidents.
77. Security containment must be verified before incident closure.
78. Deployment validation must occur after production release.
79. Health endpoints must not expose secrets.
80. Operational APIs must not bypass authorization.
81. Super Admin application privileges do not imply infrastructure privileges.
82. Business and Branch scope must remain enforced during diagnostics.
83. Audit records remain immutable.
84. Operational recovery must preserve historical configuration.
85. Operational recovery must preserve Order price snapshots.
86. Operational recovery must preserve payment history.
87. Operational recovery must preserve inventory history.
88. Operational recovery must preserve cash history.
89. Operational recovery must preserve synchronization history.
90. Operational recovery must preserve audit history.
91. Backup data may outlive live Business deletion according to retention policy.
92. Business deletion must not be accidentally triggered by ordinary recovery.
93. Security incident evidence must be preserved before destructive containment where practical.
94. Incident communication must distinguish facts from assumptions.
95. Root cause must be supported by evidence.
96. Operational changes must be traceable to a release or authorized action.
97. Production configuration changes must be auditable.
98. Cache invalidation failure must not make stale data authoritative.
99. Recovery procedures must be tested periodically.
100. The operational architecture must preserve business continuity without sacrificing data integrity.

---

# 95. Recommended Operational Architecture

```text
                    ┌──────────────────────┐
                    │      Monitoring      │
                    │ Metrics / Alerts /   │
                    │ Health / Logs        │
                    └──────────┬───────────┘
                               │
                               ▼
Internet ──► Nginx ──► Gunicorn/API
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     PostgreSQL        Redis         Workers
     Authoritative   Non-authority    Async Jobs
          │              │              │
          │              │              │
          ▼              ▼              ▼
      Backups        Cache Only      Queue/Outbox
          │
          ▼
   Separate Backup Storage
```

Operational control surrounds the entire runtime:

```text
Monitoring
    ↓
Detection
    ↓
Incident Triage
    ↓
Containment
    ↓
Recovery
    ↓
Validation
    ↓
Post-Incident Review
```

---

# 96. Initial Production Operations Model

For the initial deployment, the recommended operational model is:

```text
Linux VPS
│
├── Nginx
├── Gunicorn
├── FastFood API
├── Background Worker
├── Scheduler
├── PostgreSQL
├── Redis (optional)
└── Monitoring Agent
```

The system should avoid unnecessary operational complexity during the initial stage.

The architecture remains compatible with later migration to:

```text
Load Balancer
     ↓
Multiple API Instances
     ↓
Managed PostgreSQL
     ↓
Distributed Workers
     ↓
Managed Redis
     ↓
Centralized Monitoring
```

---

# 97. Operational Priority

When resources are constrained, operational priority is:

```text
1. Data Integrity
2. Security
3. POS Core Operations
4. Payment and Cash
5. Inventory
6. Synchronization
7. Authentication
8. Business Management
9. Reports
10. XLSX Exports
11. Notifications
12. Cleanup and Maintenance
```

A lower-priority workload must not consume resources required by a higher-priority workload.

---

# 98. Final Operational Principle

The backend must be operated according to the following principle:

> **Recover the system without losing trust in the data.**

Availability is important, but an apparently available system that produces incorrect financial, inventory, cash or historical data is not considered healthy.

The operational architecture therefore prioritizes:

* correctness;
* security;
* recoverability;
* observability;
* controlled degradation;
* explicit incident handling;
* historical integrity;
* business continuity.

---

## Related Documents

### Backend Architecture

* `docs/04_Architecture/01_Backend_Architecture.md`
* `docs/04_Architecture/02_Backend_Project_Structure.md`
* `docs/04_Architecture/03_Application_and_Use_Case_Layer.md`
* `docs/04_Architecture/04_Domain_Service_and_Business_Logic.md`
* `docs/04_Architecture/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/07_Transaction_Management.md`
* `docs/04_Architecture/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/11_Configuration_and_Environment_Management.md`
* `docs/04_Architecture/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/19_Backend_Deployment_and_Runtime_Architecture.md`

### Database

* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/28_Database_Backup_and_Recovery.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Operations

* `docs/14_Operations/README.md`
* `docs/14_Operations/01_Production_Operations.md`
* `docs/14_Operations/02_Monitoring_and_Alerting.md`
* `docs/14_Operations/03_Incident_Response.md`
* `docs/14_Operations/04_Backup_and_Restore.md`
* `docs/14_Operations/05_Disaster_Recovery.md`

---

## Status

**Backend Architecture Document:** Completed.

**Document Status:** Proposed.

**Current Document:** `20_Backend_Operations_and_Incident_Management_Architecture.md`

**Next Document:** `21_Backend_Disaster_Recovery_and_Business_Continuity_Architecture.md`

