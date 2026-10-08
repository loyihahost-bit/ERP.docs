# Queue and Worker Architecture

**Document ID:** BA-25
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This document defines the backend Queue and Worker architecture for FastFood ERP.

The system uses background processing for operations that:

* do not need to complete inside the user's request;
* may require retries;
* may take significant processing time;
* communicate with external systems;
* generate files or reports;
* process synchronization batches;
* send notifications;
* perform lifecycle and maintenance operations.

The queue/worker subsystem must improve responsiveness and reliability without becoming the source of truth for business state.

The PostgreSQL database remains authoritative for business data.

---

## 2. Scope

This document covers:

* queue architecture;
* worker architecture;
* job lifecycle;
* job types;
* queue priorities;
* job creation;
* job execution;
* retries;
* backoff;
* idempotency;
* dead-letter handling;
* scheduling;
* concurrency;
* worker isolation;
* transaction boundaries;
* Outbox integration;
* notification jobs;
* report/export jobs;
* print jobs;
* synchronization jobs;
* lifecycle jobs;
* reconciliation jobs;
* cleanup jobs;
* failure recovery;
* observability;
* security;
* resource limits;
* deployment;
* graceful shutdown;
* scalability;
* operational SLOs;
* invariants and guardrails.

---

# 3. Architectural Position

The queue and worker subsystem is an asynchronous execution layer.

```text
HTTP/API
   ↓
Application Use Case
   ↓
PostgreSQL Transaction
   ↓
Outbox / Job Request
   ↓
Queue
   ↓
Worker
   ↓
Job Handler
   ↓
Application Service
   ↓
Database / External Adapter
```

The queue does not replace the Application layer.

The worker does not contain an independent business logic implementation.

Workers invoke Application use cases or dedicated application services.

---

# 4. Core Principles

The Queue and Worker architecture follows these principles:

1. PostgreSQL remains the business source of truth.
2. Queue state is not business state.
3. Workers execute asynchronous work.
4. Business transactions remain in Application services.
5. Jobs must be idempotent where retries are possible.
6. Retryable failures must be distinguishable from permanent failures.
7. Failed jobs must not silently disappear.
8. Dead-lettered jobs must remain inspectable.
9. Critical POS operations must not wait for background processing.
10. Queue overload must not block ordinary POS operations.
11. Background jobs must have bounded resource usage.
12. External integrations must have explicit timeouts.
13. Worker concurrency must be configurable.
14. Queue priorities must protect operationally important work.
15. Job execution must be observable.
16. Sensitive information must not be stored unnecessarily in job payloads.
17. Job payloads should reference durable business entities rather than duplicate large datasets.
18. A worker must not trust client-provided job context.
19. Business and Branch scope must be validated during execution.
20. Background processing must respect subscription and lifecycle state.

---

# 5. Queue vs Business State

A queue represents execution state.

It must not become the authoritative representation of:

* Order state;
* Payment state;
* Cash Session state;
* Inventory state;
* Product state;
* Employee state;
* Subscription state;
* Business lifecycle;
* Configuration state.

For example:

```text
Order
  ↓
Order = ACCEPTED
  ↓
Outbox Event
  ↓
Print Job
  ↓
Printer
```

If the print job fails, the Order remains `ACCEPTED`.

The system must not change the Order back to another state merely because printing failed.

---

# 6. Queue Categories

The system may use logical queues rather than physically separate infrastructure.

Recommended initial queue categories:

```text
critical
operational
synchronization
notification
reporting
export
maintenance
lifecycle
```

The exact physical queue implementation may change without changing the Application architecture.

---

# 7. Queue Priority

Queue priority must reflect business importance.

Recommended priority order:

```text
1. Critical operational work
2. Normal operational work
3. Synchronization
4. Notifications
5. Reporting / exports
6. Maintenance
7. Cleanup
```

POS-critical synchronous operations must normally remain outside the queue.

Examples:

* Order acceptance;
* payment authorization;
* cash session opening;
* cash session closing;
* inventory deduction.

These operations must complete through the normal request/transaction path.

---

# 8. Critical Operational Jobs

Critical asynchronous jobs may include:

* required synchronization processing;
* security event processing;
* mandatory reconciliation;
* operational recovery tasks.

Critical jobs must receive sufficient worker capacity to avoid starvation.

Critical work must not be blocked indefinitely by:

* XLSX generation;
* large reports;
* cleanup;
* low-priority notifications.

---

# 9. Operational Jobs

Operational jobs support normal business workflows.

Examples:

* kitchen printing;
* printer retry;
* notification creation;
* synchronization follow-up;
* configuration propagation;
* operational reconciliation.

Operational jobs should normally receive higher priority than reports and maintenance.

---

# 10. Reporting and Export Jobs

Reports and exports are asynchronous when processing may be expensive.

Examples:

* XLSX generation;
* large report generation;
* report snapshots;
* historical report reconstruction;
* export preparation.

A user request should normally return a job identifier rather than keeping an HTTP request open for an unnecessarily long period.

Example:

```text
POST /reports/export
        ↓
202 Accepted
        ↓
Export Job ID
        ↓
Worker
        ↓
XLSX
        ↓
File Metadata
```

---

# 11. Notification Jobs

Notifications are asynchronous.

Recommended flow:

```text
Business Transaction
        ↓
Outbox Event
        ↓
Notification Job
        ↓
Notification Service
        ↓
Notification Record
        ↓
Optional External Delivery
```

Notification failure must not roll back the original business transaction.

---

# 12. Printing Jobs

Printing is treated as an external operational side effect.

Recommended flow:

```text
Order Accepted
        ↓
Transaction Commit
        ↓
Print Event / Job
        ↓
Print Queue
        ↓
Local Print Agent
        ↓
Printer
```

Printing must never be performed inside the core business transaction.

Printer failure must not roll back:

* Order acceptance;
* payment;
* inventory deduction;
* cash state.

---

# 13. Synchronization Jobs

Offline synchronization may generate background work when:

* a large batch arrives;
* additional validation is required;
* conflict resolution is required;
* reconciliation is required;
* follow-up processing is needed.

The synchronization subsystem remains responsible for:

* authentication;
* idempotency;
* validation;
* conflict detection;
* transaction application.

Workers provide execution capacity but do not bypass synchronization rules.

---

# 14. Lifecycle Jobs

Lifecycle processing may include:

* subscription expiry processing;
* read-only transition;
* deletion eligibility;
* data deletion;
* retention processing;
* backup-related cleanup;
* archived data processing.

Lifecycle jobs must revalidate current lifecycle state before making destructive changes.

---

# 15. Reconciliation Jobs

Reconciliation jobs detect inconsistencies between related system states.

Examples:

* payment vs order;
* cash session vs cash transactions;
* inventory transaction vs stock balance;
* report version vs source data;
* synchronization state vs authoritative server state;
* outbox vs downstream processing.

Reconciliation must not silently rewrite historical data.

Detected inconsistencies must create:

* reconciliation record;
* audit event;
* appropriate notification when required.

---

# 16. Maintenance Jobs

Maintenance jobs may include:

* expired temporary records;
* stale queue records;
* old temporary files;
* cache maintenance;
* non-authoritative cleanup;
* metrics aggregation;
* index maintenance coordination.

Maintenance work must not consume resources required by POS operations.

---

# 17. Job Model

A job should contain at least:

```text
Job UUID
Job Type
Queue
Priority
Status
Business UUID
Branch UUID (nullable)
Entity Type
Entity UUID
Operation UUID (nullable)
Correlation UUID
Created At
Scheduled At
Started At
Completed At
Attempt Count
Maximum Attempts
Next Retry At
Last Error Code
Last Error Message
Worker ID
Payload Reference
Result Reference
```

Sensitive information must not be stored in job payloads unless explicitly required.

---

# 18. Job Status

Recommended states:

```text
PENDING
SCHEDULED
PROCESSING
RETRYING
COMPLETED
FAILED
DEAD_LETTERED
CANCELLED
```

Possible lifecycle:

```text
PENDING
   ↓
PROCESSING
   ↓
COMPLETED
```

Retryable failure:

```text
PROCESSING
   ↓
RETRYING
   ↓
PROCESSING
```

Permanent failure:

```text
PROCESSING
   ↓
FAILED
   ↓
DEAD_LETTERED
```

---

# 19. Job Claiming

A worker must claim a job before processing it.

Claiming must prevent uncontrolled concurrent execution.

The system may use:

* queue-native reservation;
* database row locking;
* visibility timeout;
* lease-based execution.

The chosen implementation must provide a clear ownership mechanism.

---

# 20. Worker Lease

For jobs that may run for a long time, the worker may hold a lease.

The lease should contain:

* job UUID;
* worker UUID;
* lease start;
* lease expiration;
* heartbeat where required.

A worker that loses its lease must not continue performing unsafe duplicate work.

---

# 21. At-Least-Once Processing

The system should assume that background jobs may be delivered more than once.

Therefore:

**Workers must be designed for at-least-once execution.**

Exactly-once execution should not be assumed merely because the queue claims to support it.

Business operations must use:

* operation UUID;
* unique constraints;
* idempotency records;
* state validation.

---

# 22. Idempotent Job Execution

A retry must not create duplicate business effects.

Example:

```text
Job:
Generate Export

Operation UUID:
op-123
```

If the worker receives the same job again:

```text
op-123 already completed
        ↓
No duplicate export
```

The worker should return the existing authoritative result where possible.

---

# 23. Job Idempotency Scope

Idempotency may be based on:

* Operation UUID;
* Event UUID;
* Job UUID;
* Entity UUID + operation type;
* External provider idempotency key.

The chosen identity must match the business operation.

Job UUID alone is insufficient when duplicate jobs can represent the same business operation.

---

# 24. Retryable Failures

Retry may be appropriate for:

* temporary network failure;
* temporary database connectivity issue;
* provider timeout;
* rate limit;
* temporary printer unavailability;
* temporary storage failure;
* worker interruption;
* transient serialization/deadlock failure.

Retries must be bounded.

---

# 25. Permanent Failures

Permanent failure examples:

* invalid business state;
* missing required entity;
* unauthorized operation;
* invalid job payload;
* deleted Business where operation is no longer valid;
* unsupported job version;
* malformed data;
* violated immutable business rule.

Permanent failures must not be retried indefinitely.

---

# 26. Retry Backoff

Recommended strategy:

```text
Attempt 1 → short delay
Attempt 2 → longer delay
Attempt 3 → longer delay
...
```

Exponential backoff with bounded maximum delay is preferred.

A small randomized jitter may be added to prevent synchronized retry storms.

Example conceptual policy:

```text
delay = min(base × 2^attempt, max_delay) + jitter
```

The exact values are configuration, not business logic.

---

# 27. Maximum Retry Attempts

Every retryable job must have a maximum retry count.

Recommended defaults:

```text
Critical operational jobs:
3–5 attempts

External integrations:
3–5 attempts

Notifications:
3–5 attempts

Printing:
5–10 attempts

Reports/exports:
2–3 attempts

Maintenance:
2–3 attempts
```

These are default configuration values and may be adjusted according to operational evidence.

---

# 28. Dead-Letter Queue

A job that exhausts retry attempts must be moved to a Dead-Letter state.

Dead-letter processing must preserve:

* original Job UUID;
* original Operation UUID;
* original payload/reference;
* attempt history;
* error history;
* Business;
* Branch;
* timestamps;
* worker information.

Dead-lettered jobs must remain inspectable.

---

# 29. Dead-Letter Recovery

Authorized operators may:

* inspect;
* retry;
* cancel;
* resolve;
* mark permanently invalid.

A retry from Dead-Letter must create a controlled new execution attempt.

Historical failure information must not be deleted.

---

# 30. Poison Jobs

A poison job repeatedly fails because of invalid or unsupported input.

Examples:

* malformed payload;
* unsupported version;
* invalid entity reference;
* permanently invalid business state.

Poison jobs must be isolated quickly.

The system must not allow one poison job to consume unlimited worker capacity.

---

# 31. Retry Storm Protection

The system must protect against retry storms.

Controls may include:

* exponential backoff;
* jitter;
* maximum attempts;
* queue rate limits;
* circuit breakers for external providers;
* per-job concurrency limits;
* provider-specific queues;
* worker capacity limits.

---

# 32. Queue Starvation

Low-priority jobs must not completely starve.

The scheduler should provide controlled fairness.

For example:

```text
Critical → always prioritized
Operational → high priority
Sync → protected capacity
Reports → limited capacity
Maintenance → remaining capacity
```

The implementation must prevent unlimited low-priority backlog from affecting operational work.

---

# 33. Worker Pools

Workers should be grouped by workload.

Recommended logical pools:

```text
Operational Workers
Sync Workers
Notification Workers
Reporting Workers
Maintenance Workers
```

A single worker pool may be used initially if queue isolation and concurrency controls are sufficient.

Separate pools should be introduced when workload contention becomes measurable.

---

# 34. Worker Concurrency

Worker concurrency must be bounded.

Concurrency depends on:

* CPU;
* memory;
* database connections;
* external provider limits;
* job type;
* expected execution time.

The system must not allow unlimited worker concurrency.

---

# 35. Database Connection Protection

Workers share the application's database resources.

Worker concurrency must respect the PostgreSQL connection pool.

Example:

```text
Gunicorn/API connections
        +
Worker DB connections
        +
Reporting connections
        <
Safe PostgreSQL capacity
```

The worker system must not exhaust the database connection pool and cause POS requests to fail.

---

# 36. POS Protection

POS operations have higher priority than background workloads.

Background jobs must be throttled or delayed when necessary to protect:

* Order creation;
* Order acceptance;
* Payment;
* Cash operations;
* Inventory operations.

This is a system-level performance requirement.

---

# 37. Worker Resource Limits

Each job class should have reasonable limits for:

* execution time;
* memory;
* CPU;
* database rows processed;
* file size;
* network request duration;
* retry count.

Unbounded jobs are prohibited.

Large workloads must be chunked.

---

# 38. Long-Running Jobs

Long-running jobs include:

* large XLSX exports;
* large historical reports;
* Business deletion;
* large synchronization reconciliation;
* maintenance operations.

These jobs must:

* run asynchronously;
* expose progress where useful;
* support cancellation where safe;
* process data in bounded batches;
* avoid long database transactions.

---

# 39. Job Chunking

Large operations should use bounded chunks.

Example:

```text
100,000 records

↓
1,000 records
↓
1,000 records
↓
...
```

A failure should not require restarting the entire operation unnecessarily.

Chunk size must be configurable and measured.

---

# 40. Transaction Boundaries

A worker job must not automatically mean one giant database transaction.

Instead:

```text
Job
  ↓
Validate
  ↓
Short transaction
  ↓
Commit
  ↓
Next chunk
```

This prevents:

* long locks;
* transaction bloat;
* excessive rollback cost;
* database starvation.

---

# 41. Job and Database Transaction

Job status updates and business state changes must be coordinated carefully.

A worker must not mark a job `COMPLETED` before the authoritative business change is committed.

Recommended:

```text
Start job
   ↓
Execute business transaction
   ↓
Commit
   ↓
Mark execution result
   ↓
Complete job
```

If the worker crashes after business commit but before job completion, the job must be safely retried through idempotency.

---

# 42. Outbox Integration

Important asynchronous events should use the Outbox pattern.

Recommended:

```text
Business Transaction
        ↓
Business State Change
        +
Outbox Event
        ↓
Commit
        ↓
Outbox Dispatcher
        ↓
Queue
        ↓
Worker
```

The Outbox ensures that a committed business transaction does not silently lose its required asynchronous event.

---

# 43. Queue Publication Failure

If queue publication fails after a business transaction:

* the business transaction must not be rolled back merely because the queue is unavailable;
* the Outbox record remains pending;
* the dispatcher retries publication.

The queue is therefore recoverable from durable Outbox state.

---

# 44. Duplicate Outbox Delivery

Outbox events may be delivered more than once.

Workers must therefore use:

* Event UUID;
* operation UUID;
* idempotent handlers.

Duplicate delivery must not duplicate business effects.

---

# 45. Scheduling

The system may support:

* immediate jobs;
* delayed jobs;
* periodic jobs.

Examples:

```text
Immediate:
Print order

Delayed:
Subscription reminder

Periodic:
Daily reconciliation
```

Scheduling must not bypass authorization or lifecycle rules.

---

# 46. Scheduler

The scheduler creates or releases jobs.

It must be safe against duplicate execution.

If multiple scheduler instances are deployed, leader election or another coordination mechanism must prevent uncontrolled duplicate scheduling.

Scheduled jobs must have stable identifiers.

---

# 47. Periodic Job Idempotency

A periodic job must have a deterministic execution identity.

Example:

```text
daily-report:
Business UUID
+
2026-10-05
```

Running the scheduler twice must not generate duplicate authoritative reports.

---

# 48. Job Cancellation

Jobs may be cancelled when safe.

Cancellation is appropriate for:

* queued exports;
* queued reports;
* low-priority maintenance;
* obsolete notification delivery.

Cancellation must not be used to undo already committed business transactions.

---

# 49. Cooperative Cancellation

Long-running workers should periodically check whether cancellation was requested.

For example:

```text
Process chunk
   ↓
Check cancellation
   ↓
Process next chunk
```

Workers must not leave partially committed business state without a valid recovery path.

---

# 50. Job Timeout

Every job class must have a bounded execution timeout.

Timeout does not automatically mean that the underlying operation was rolled back.

Therefore, after timeout the worker must assume the operation may have committed and use idempotency/reconciliation before retrying unsafe operations.

---

# 51. External Integration Jobs

External operations must use:

* connection timeout;
* read timeout;
* retry policy;
* idempotency where supported;
* circuit breaker where appropriate;
* provider response validation.

Examples:

* email;
* printer;
* storage;
* external API.

---

# 52. External Provider Rate Limits

Provider-specific limits must be respected.

The worker system should support:

* per-provider concurrency;
* rate limiting;
* retry-after handling;
* backoff;
* circuit breaking.

One failing provider must not consume all worker capacity.

---

# 53. Circuit Breaker

For unstable external providers, a circuit breaker may temporarily stop new attempts.

Conceptually:

```text
CLOSED
  ↓ repeated failures
OPEN
  ↓ cooldown
HALF-OPEN
  ↓ successful test
CLOSED
```

Circuit breakers protect the application from cascading failure.

---

# 54. Notification Delivery

Notification delivery should distinguish:

```text
Created
Queued
Processing
Delivered
Failed
Retrying
```

The notification record remains separate from the queue job.

A queue failure must not delete the notification record.

---

# 55. Print Delivery

Print jobs must contain enough information to route the print operation but should not duplicate the complete Order unnecessarily.

The preferred model is:

```text
Print Job
   ↓
Order UUID
   ↓
Authoritative Order Snapshot
   ↓
Printer Routing
```

Where historical printing requires immutable data, the appropriate snapshot/reference must be preserved.

---

# 56. Report Jobs

Report workers must use the correct report version or data snapshot.

A report job must not silently change an already finalized report version.

If new data requires a new report version, the Report subsystem creates a new version.

---

# 57. Export Jobs

Export jobs should produce:

```text
Export Job
   ↓
Report/Data Snapshot
   ↓
XLSX Generator
   ↓
File Storage
   ↓
Export Result
```

Generated files must have controlled access.

Export creation must be audited.

---

# 58. Synchronization Worker

Synchronization workers must process:

```text
Batch
   ↓
Authenticate
   ↓
Validate
   ↓
Idempotency Check
   ↓
Business/Branch Scope
   ↓
Business Rules
   ↓
Apply
   ↓
Result
```

A worker must never treat the client as authoritative.

---

# 59. Offline Transaction Priority

When processing offline synchronization:

1. validate authorization;
2. validate Business lifecycle;
3. validate device;
4. validate operation UUID;
5. validate entity state;
6. apply transaction;
7. commit;
8. process secondary events.

Configuration synchronization must not incorrectly override an already committed transaction.

---

# 60. Subscription and Lifecycle Validation

Every modifying background job must validate current Business lifecycle where relevant.

For example:

```text
Job created while ACTIVE
        ↓
Business becomes READ_ONLY
        ↓
Worker starts
        ↓
Worker revalidates lifecycle
        ↓
Modification rejected if prohibited
```

A queued job must not preserve old authorization forever.

---

# 61. Authorization in Workers

Workers must execute with explicit system identity.

A worker must know:

* originating Business;
* Branch where applicable;
* originating employee where applicable;
* operation UUID;
* source;
* job type.

The worker must not assume that the employee is still authorized merely because the job was created earlier.

---

# 62. Employee Deactivation

If a queued job requires the employee's current authorization, the worker must revalidate employee status.

However, system-owned post-commit operations may continue when they represent already-authorized committed work.

The distinction must be explicit.

---

# 63. Business Isolation

Every tenant-sensitive job must carry Business context.

A worker must reject:

* missing Business context;
* invalid Business context;
* cross-Business entity reference;
* cross-Business file reference.

Cross-Business execution is prohibited.

---

# 64. Branch Isolation

Branch-scoped jobs must preserve Branch context.

A Branch A job must not accidentally operate on Branch B data.

Branch context must be validated against the referenced entity.

---

# 65. Security of Job Payloads

Job payloads must not contain unnecessary:

* passwords;
* authentication tokens;
* private keys;
* payment credentials;
* sensitive personal data.

Prefer durable references:

```text
business_id
branch_id
entity_id
operation_id
```

rather than large serialized objects.

---

# 66. Payload Versioning

Job payloads may outlive the software version that created them.

Therefore, job payloads should include a version where compatibility may matter.

Example:

```text
job_type = EXPORT_REPORT
payload_version = 2
```

Workers must either support the version or fail it safely.

---

# 67. Deployment Compatibility

During rolling deployment:

```text
Old Worker
      +
New Worker
      ↓
Same Queue
```

must be safe where possible.

Breaking job payload changes require:

* versioning;
* compatibility period;
* migration;
* or controlled queue draining.

---

# 68. Worker Graceful Shutdown

On shutdown:

1. stop accepting new jobs;
2. finish safe in-progress work;
3. release/renew leases appropriately;
4. acknowledge completed jobs;
5. return unfinished jobs safely to the queue;
6. close DB connections;
7. exit within bounded time.

A worker must not acknowledge a job before its authoritative operation is safely committed.

---

# 69. Worker Crash Recovery

If a worker crashes:

* unacknowledged jobs must become available again;
* leases must expire;
* idempotency must prevent duplicate business effects;
* partial operations must be reconciled where required.

The system must not depend on a worker surviving indefinitely.

---

# 70. Queue Availability Failure

If the queue is temporarily unavailable:

* core synchronous POS operations continue where possible;
* committed business transactions remain authoritative;
* Outbox records remain durable;
* dispatch resumes after queue recovery.

Background processing may be delayed, but business history must not be lost.

---

# 71. Database Availability Failure

If PostgreSQL is unavailable:

Workers must not repeatedly hammer the database.

They should:

* fail safely;
* apply bounded retries;
* use backoff;
* release capacity;
* report health state.

POS/API protection remains a priority.

---

# 72. Queue Backlog

The system must monitor:

* queue depth;
* oldest job age;
* processing rate;
* failure rate;
* retry rate;
* dead-letter count.

Backlog growth must trigger operational alerts before it affects business operations.

---

# 73. Backpressure

When queue backlog becomes excessive, the system may apply backpressure.

Examples:

* reduce report worker concurrency;
* delay maintenance;
* reduce export concurrency;
* limit low-priority job creation;
* preserve operational worker capacity.

Backpressure must protect the system rather than silently dropping work.

---

# 74. Queue Capacity Planning

Capacity must consider:

```text
Incoming jobs per second
×
Average execution time
×
Peak multiplier
```

The system must be sized using measured workload rather than arbitrary worker counts.

---

# 75. Queue Metrics

Required metrics include:

### Queue

* queue depth;
* oldest job age;
* enqueue rate;
* dequeue rate;
* completion rate;
* retry rate;
* dead-letter rate.

### Worker

* active workers;
* active jobs;
* worker utilization;
* job duration;
* worker errors;
* worker restarts;
* lease expirations.

### Database

* worker DB connections;
* query latency;
* lock waits;
* deadlocks;
* transaction duration.

### External

* provider latency;
* timeout rate;
* rate-limit responses;
* circuit-breaker state.

---

# 76. Job Tracing

Every important job should be traceable through:

```text
Request ID
Operation UUID
Correlation UUID
Event UUID
Job UUID
Worker ID
```

This allows:

```text
User Request
   ↓
Business Transaction
   ↓
Outbox Event
   ↓
Queue Job
   ↓
Worker
   ↓
External Effect
```

to be reconstructed.

---

# 77. Logging

Worker logs should include:

* timestamp;
* level;
* service;
* release;
* worker ID;
* Job UUID;
* Operation UUID;
* Business UUID;
* Branch UUID where applicable;
* job type;
* attempt;
* duration;
* result;
* error code.

Sensitive payloads must not be logged.

---

# 78. Error Classification

Worker errors should be classified consistently:

```text
VALIDATION_ERROR
AUTHORIZATION_ERROR
BUSINESS_RULE_ERROR
CONFLICT_ERROR
NOT_FOUND_ERROR
TRANSIENT_INFRASTRUCTURE_ERROR
EXTERNAL_PROVIDER_ERROR
TIMEOUT_ERROR
RATE_LIMIT_ERROR
PERMANENT_FAILURE
UNKNOWN_ERROR
```

Classification determines retry behavior.

---

# 79. Unknown Errors

Unknown errors must not automatically receive unlimited retries.

Recommended behavior:

```text
Unknown Error
   ↓
Bounded Retry
   ↓
Dead Letter
   ↓
Alert
```

The failure must remain observable.

---

# 80. Worker Alerts

Alerts should be generated for:

* critical queue backlog;
* excessive oldest-job age;
* high retry rate;
* dead-letter increase;
* worker crash loop;
* database connection exhaustion;
* provider outage;
* synchronization backlog;
* failed lifecycle deletion;
* repeated reconciliation failures.

---

# 81. Queue Health

A queue is considered healthy when:

* jobs are being accepted;
* jobs are being processed;
* backlog remains within expected bounds;
* retry rate remains normal;
* dead-letter rate remains low;
* worker capacity is available.

Queue health must be observable independently from API health.

---

# 82. Worker Health

Worker health should expose:

* process health;
* queue connectivity;
* database connectivity;
* current capacity;
* active job count;
* last successful job;
* graceful shutdown state.

Health endpoints must not expose sensitive information.

---

# 83. Readiness

A worker should not receive jobs when:

* required configuration is invalid;
* database connection is unavailable;
* queue connection is unavailable;
* required cryptographic configuration is invalid;
* required dependencies are unavailable.

Readiness and liveness must be separate.

---

# 84. Worker Deployment

Initial production deployment may use:

```text
Nginx
   ↓
Gunicorn
   ↓
FastFood API

Background:
FastFood Worker
FastFood Scheduler

Infrastructure:
PostgreSQL
Redis/Queue
File Storage
```

This is compatible with the initial Linux VPS architecture.

---

# 85. Worker Scaling

Initially:

```text
1 Worker Service
+
Multiple Logical Queues
```

As workload increases:

```text
Operational Workers
Sync Workers
Report Workers
Notification Workers
Maintenance Workers
```

can be scaled independently.

---

# 86. Horizontal Scaling

Workers should be stateless where possible.

Multiple worker instances may process the same queue when:

* jobs are safely claimable;
* idempotency is enforced;
* concurrency is bounded;
* database capacity supports the workload.

The system must not rely on a single worker instance.

---

# 87. Queue Infrastructure

The initial implementation may use a Redis-backed queue or another reliable queue implementation.

The queue abstraction should be isolated behind infrastructure interfaces.

Business logic must not depend directly on Redis APIs.

The system should be able to replace the queue technology without rewriting domain logic.

---

# 88. Redis Failure

If Redis is used as queue infrastructure and becomes unavailable:

* already committed PostgreSQL state remains safe;
* Outbox records remain durable;
* queue processing may pause;
* dispatcher retries after recovery.

Redis must not be treated as the authoritative source for business transactions.

---

# 89. Queue Persistence

Queue infrastructure should use durable configuration appropriate to the deployment.

However, even durable queue storage is not considered the only recovery mechanism for critical events.

Critical asynchronous work must be recoverable from PostgreSQL Outbox or another authoritative durable record.

---

# 90. File Processing

Workers generating files must:

* create temporary files safely;
* avoid predictable sensitive filenames;
* limit file size;
* validate generated content;
* store files through the storage abstraction;
* record file metadata;
* apply access control;
* audit exports where required.

---

# 91. Cleanup Jobs

Cleanup must be conservative.

A cleanup worker must not delete records merely because they appear old.

Deletion must follow:

* retention policy;
* lifecycle state;
* legal/business requirements;
* explicit deletion rules;
* backup policy.

Historical audit and business records must not be accidentally removed.

---

# 92. Business Deletion Jobs

Business deletion is a high-risk background operation.

It must:

1. verify deletion eligibility;
2. verify subscription lifecycle;
3. create deletion audit;
4. process data in bounded batches;
5. preserve required audit/operational evidence according to policy;
6. update lifecycle state;
7. prevent concurrent modification;
8. complete reconciliation;
9. mark final state.

Deletion must never be implemented as one unbounded database transaction.

---

# 93. Backup Interaction

Queue state must be considered in disaster recovery.

After database restoration:

* pending Outbox records may need redispatch;
* duplicate job execution must remain safe;
* already committed business transactions must not be duplicated.

Recovery must rely on idempotency rather than assuming perfect queue/database synchronization.

---

# 94. Disaster Recovery

After recovery:

```text
PostgreSQL Restored
        ↓
Validate Application State
        ↓
Validate Outbox
        ↓
Rebuild/Recover Queue
        ↓
Start Workers
        ↓
Process Pending Jobs
        ↓
Reconcile
```

High-priority operational jobs must be processed before low-priority maintenance.

---

# 95. Reconciliation After Recovery

After major infrastructure recovery, the system should reconcile:

* Outbox;
* queue;
* notifications;
* print jobs;
* synchronization batches;
* report jobs;
* lifecycle jobs.

Any inconsistency must be recorded and investigated.

---

# 96. Testing Strategy

Queue/worker architecture must be tested at multiple levels.

### Unit Tests

Test:

* retry classification;
* backoff;
* job state transitions;
* idempotency decisions;
* payload validation;
* cancellation rules.

### Integration Tests

Test:

* queue ↔ worker;
* worker ↔ PostgreSQL;
* Outbox ↔ queue;
* worker ↔ external adapter.

### Failure Tests

Test:

* worker crash;
* queue outage;
* database outage;
* provider timeout;
* duplicate job;
* stale job;
* lease expiration;
* dead-letter recovery.

---

# 97. Concurrency Testing

Tests must verify that two workers processing the same logical operation cannot create duplicate business effects.

Examples:

```text
Two workers
    ↓
Same Operation UUID
    ↓
One authoritative effect
```

This must be verified for:

* notifications;
* exports;
* printing;
* synchronization;
* reconciliation;
* lifecycle operations.

---

# 98. Load Testing

Load tests should measure:

* queue throughput;
* worker throughput;
* maximum safe concurrency;
* database impact;
* backlog growth;
* retry behavior;
* recovery after burst load.

Load testing must include mixed workloads:

```text
POS/API traffic
+
Synchronization
+
Notifications
+
Reports
+
Exports
```

The objective is to verify that background work does not materially degrade POS performance.

---

# 99. Performance SLOs

Initial operational targets:

| Metric                                    |                       Target |
| ----------------------------------------- | ---------------------------: |
| Queue enqueue acknowledgement             |                 p95 ≤ 200 ms |
| Normal background job start after enqueue |                    p95 ≤ 5 s |
| Critical operational job start            |                    p95 ≤ 2 s |
| Notification job start                    |                   p95 ≤ 10 s |
| Normal report job start                   |                   p95 ≤ 30 s |
| Export job acknowledgement                |                    p95 ≤ 2 s |
| Worker job state update                   |                 p95 ≤ 200 ms |
| Normal job completion success             |                      ≥ 99.9% |
| Duplicate business effect prevention      |                     ≥ 99.99% |
| Critical job loss prevention              |                     ≥ 99.99% |
| Dead-letter classification                |                      ≥ 99.9% |
| Queue subsystem availability              |              ≥ 99.9% monthly |
| Critical queue backlog alert              |                       ≤ 60 s |
| Worker crash detection                    |                       ≤ 60 s |
| Outbox-to-queue recovery                  | ≤ 5 min after queue recovery |

These are initial targets and must be validated through load testing.

---

# 100. POS Performance Protection SLO

Background processing must not cause unacceptable degradation to core POS operations.

Target:

* Core POS command p95 ≤ 500 ms under normal production load.
* Background worker resource consumption must remain bounded.
* Database worker connections must not exhaust capacity reserved for API/POS traffic.
* Queue backlog must not directly block synchronous Order acceptance.

If background workload threatens these targets, worker concurrency must be reduced or low-priority queues throttled.

---

# 101. Operational Runbook Requirements

Operations documentation must define procedures for:

* queue outage;
* worker outage;
* queue backlog;
* retry storm;
* dead-letter investigation;
* stuck job;
* provider outage;
* database exhaustion;
* worker deployment;
* queue migration;
* manual job retry;
* job cancellation;
* reconciliation.

Manual operational actions must be authenticated and audited.

---

# 102. Manual Job Operations

Authorized operators may:

* inspect job;
* inspect attempts;
* retry job;
* cancel job;
* move job to dead-letter;
* trigger reconciliation.

Manual actions must never directly modify business state outside approved application operations.

---

# 103. Queue Migration

Changing queue infrastructure must preserve:

* pending critical work;
* Outbox recoverability;
* job compatibility;
* idempotency;
* operational traceability.

Recommended migration:

```text
Old Queue
   ↓
Drain / Freeze
   ↓
Validate Pending Work
   ↓
New Queue
   ↓
Resume Dispatch
   ↓
Reconcile
```

---

# 104. Version Compatibility

Job handlers must be compatible with jobs created by supported application versions.

If compatibility cannot be maintained:

* drain the queue before deployment;
* version the job;
* migrate queued payloads;
* or temporarily disable affected job creation.

---

# 105. Security Requirements

Workers must:

* run as non-root users;
* use least-privilege credentials;
* access only required queues;
* access only required database resources;
* avoid shell execution unless explicitly required;
* validate external input;
* protect secrets;
* avoid logging sensitive payloads.

Worker credentials must be separate from unnecessary administrative credentials.

---

# 106. Command Execution

A worker must not execute arbitrary commands derived from job payloads.

If command execution is required for a controlled infrastructure task:

* command must be predefined;
* arguments must be validated;
* execution environment must be restricted;
* permissions must be minimal;
* execution must be audited.

---

# 107. SSRF and External Requests

Jobs receiving URLs or external references must not freely request arbitrary internal resources.

External requests must use:

* allowlists where appropriate;
* URL validation;
* network restrictions;
* timeouts;
* response size limits.

---

# 108. Worker Data Isolation

Worker execution context must preserve:

```text
Business
Branch
Employee
Device
Operation
Job
```

where applicable.

A worker must not accidentally reuse context from a previous job.

Context must be reset between jobs.

---

# 109. Memory Isolation

Long-running workers must avoid unbounded memory growth.

Workers should:

* process large datasets in chunks;
* release temporary resources;
* avoid keeping large result sets in memory;
* periodically recycle processes where appropriate;
* monitor memory usage.

---

# 110. Worker Recycling

Worker process recycling may be used to mitigate:

* memory leaks;
* fragmentation;
* long-lived dependency issues.

Recycling must be graceful and must not lose active jobs.

---

# 111. Dependency Boundaries

Recommended structure:

```text
app/
├── background/
│   ├── jobs/
│   ├── workers/
│   ├── handlers/
│   ├── scheduler/
│   ├── retry/
│   ├── policies/
│   └── monitoring/
│
├── infrastructure/
│   └── messaging/
│       ├── queue.py
│       ├── publisher.py
│       ├── consumer.py
│       ├── serializer.py
│       └── adapters/
│
├── application/
├── domain/
├── synchronization/
├── reporting/
└── shared/
```

---

# 112. Dependency Rules

The following dependency direction applies:

```text
Worker
   ↓
Application Service
   ↓
Domain / Repository Interface
   ↓
Infrastructure
```

Infrastructure queue implementation must not leak into Domain.

Domain must not know:

* Redis;
* queue implementation;
* worker framework;
* scheduler;
* HTTP;
* email provider.

---

# 113. Job Handler Design

A handler should be small and deterministic.

Conceptually:

```text
handle(job)
    ↓
validate job
    ↓
load authoritative state
    ↓
validate current state
    ↓
execute application operation
    ↓
commit
    ↓
return result
```

Handlers must not contain large duplicated business rules.

---

# 114. Job Registry

Job types should be centrally registered.

Example:

```text
ORDER_PRINT
SEND_NOTIFICATION
GENERATE_REPORT
GENERATE_XLSX
PROCESS_SYNC_BATCH
RECONCILE_INVENTORY
RECONCILE_CASH
PROCESS_SUBSCRIPTION
PROCESS_DELETION
```

Unknown job types must fail safely rather than being silently ignored.

---

# 115. Job Payload Contract

Each job type should define:

* payload schema;
* payload version;
* required identifiers;
* optional identifiers;
* maximum size;
* authorization expectations;
* retry policy;
* timeout;
* concurrency policy;
* handler.

This makes jobs understandable to both developers and automated agents.

---

# 116. Queue Naming

Queue names should be stable and descriptive.

Example:

```text
fastfood.operational
fastfood.sync
fastfood.notifications
fastfood.reports
fastfood.exports
fastfood.lifecycle
fastfood.maintenance
```

Environment isolation must be preserved.

Development jobs must never accidentally enter production queues.

---

# 117. Environment Isolation

Queue infrastructure must distinguish:

```text
development
testing
staging
production
```

Queue names, credentials and storage must be environment-specific.

---

# 118. Job Observability

Every important job must allow operators to answer:

1. Who created it?
2. Why was it created?
3. Which Business does it belong to?
4. Which Branch?
5. Which operation triggered it?
6. Which worker processed it?
7. How many attempts occurred?
8. Why did it fail?
9. Was it retried?
10. What was the final result?

---

# 119. Business Continuity

If workers are temporarily unavailable:

* core business transactions should continue where architecture permits;
* asynchronous effects may be delayed;
* Outbox records remain durable;
* queue processing resumes after recovery.

The system should degrade gracefully rather than fail the entire POS.

---

# 120. System Invariants

The following invariants apply to Queue and Worker architecture:

1. PostgreSQL remains authoritative for business state.
2. Queue state is not business state.
3. Workers do not replace Application services.
4. Domain logic does not depend on queue infrastructure.
5. Queue jobs are bounded.
6. Every retryable job has a maximum retry count.
7. Retry delays are bounded.
8. Retryable and permanent failures are distinguished.
9. Failed jobs are observable.
10. Exhausted jobs enter Dead-Letter handling.
11. Dead-lettered jobs are not silently deleted.
12. Duplicate job delivery is expected.
13. Idempotency protects duplicate business effects.
14. Job UUID is not automatically equivalent to business Operation UUID.
15. Important business operations use stable idempotency identity.
16. Workers validate authoritative database state before modification.
17. Workers do not trust stale job payload state.
18. Business scope is validated.
19. Branch scope is validated where applicable.
20. Cross-Business execution is prohibited.
21. Cross-Branch unauthorized execution is prohibited.
22. Worker context is isolated between jobs.
23. Sensitive job payload data is minimized.
24. Secrets are never stored unnecessarily in job payloads.
25. Secrets are never written to ordinary logs.
26. Worker credentials follow least privilege.
27. Workers do not run as root.
28. Core POS transactions do not depend on background job completion unless explicitly designed otherwise.
29. Order acceptance does not depend on printing completion.
30. Payment does not depend on notification completion.
31. Cash operations do not depend on reporting completion.
32. Inventory transactions do not depend on report generation.
33. External provider failures do not silently rewrite business state.
34. External calls have bounded timeouts.
35. External calls have bounded retries.
36. Provider-specific rate limits are respected.
37. One external provider cannot consume all worker capacity.
38. Low-priority jobs cannot indefinitely starve critical work.
39. Background work cannot intentionally exhaust the database connection pool.
40. Worker concurrency is bounded.
41. Queue capacity is monitored.
42. Queue backlog is monitored.
43. Oldest job age is monitored.
44. Retry rate is monitored.
45. Dead-letter rate is monitored.
46. Worker crashes are detectable.
47. Worker health is observable.
48. Worker readiness is separate from liveness.
49. Queue outage does not destroy committed business transactions.
50. Outbox provides recovery for required asynchronous events.
51. Outbox events are idempotently processed.
52. Queue publication failure does not silently lose required events.
53. A worker must not mark a job complete before the authoritative transaction commits.
54. A worker crash after commit must not create duplicate business effects.
55. Long-running jobs use bounded transactions.
56. Large operations are chunked.
57. Large exports do not run inside normal API requests when processing is expensive.
58. Large reports do not block POS operations.
59. Business deletion is processed in bounded batches.
60. Business deletion is lifecycle-aware.
61. Subscription restrictions apply to modifying background jobs.
62. A queued job does not preserve authorization forever.
63. Employee status is revalidated when required.
64. System-owned post-commit work is distinguished from new employee-authorized work.
65. Periodic jobs have deterministic execution identity.
66. Duplicate scheduler execution does not create duplicate authoritative effects.
67. Scheduled jobs respect lifecycle state.
68. Job payloads may be versioned.
69. Job handlers must support declared payload versions.
70. Breaking job changes require compatibility or controlled migration.
71. Queue migration preserves recoverable work.
72. Queue infrastructure is replaceable through an infrastructure abstraction.
73. Redis is not the business source of truth.
74. Queue persistence is not the only recovery mechanism for critical events.
75. Manual job operations are authenticated.
76. Manual job operations are audited.
77. Operators cannot bypass application business rules through queue administration.
78. Dead-letter retry preserves historical failure information.
79. Job cancellation cannot undo committed business transactions.
80. Job timeout does not automatically imply transaction rollback.
81. Timeout recovery uses idempotency and reconciliation where required.
82. Unknown errors do not receive unlimited retries.
83. Poison jobs are isolated.
84. Retry storms are controlled.
85. Backpressure protects POS resources.
86. Worker memory usage is bounded.
87. Worker CPU usage is bounded.
88. Worker database usage is bounded.
89. Worker network usage is bounded.
90. Large result sets are processed without unbounded memory usage.
91. Worker shutdown is graceful.
92. In-progress jobs are recoverable after worker termination.
93. Job tracing preserves request and operation relationships.
94. Job logs contain sufficient operational context.
95. Sensitive data is excluded from logs.
96. Job results are not treated as authoritative when the database contains authoritative state.
97. Reports use the appropriate report/data version.
98. Exports preserve historical data integrity.
99. Notification records are separate from queue execution state.
100. Print job state is separate from Order state.
101. Print failure does not rollback Order acceptance.
102. Synchronization workers enforce synchronization rules.
103. Offline client data is never trusted solely because it arrived through a worker.
104. Configuration synchronization cannot rewrite committed transaction snapshots.
105. Lifecycle deletion cannot resurrect deleted data.
106. Stale jobs cannot reactivate a deleted or read-only Business.
107. Reconciliation does not silently overwrite historical data.
108. Reconciliation failures are observable.
109. Backup recovery can rebuild asynchronous processing state.
110. Queue recovery is followed by reconciliation where necessary.
111. Background jobs do not bypass security controls.
112. Background workers do not bypass subscription entitlements.
113. Background workers do not bypass Branch scope.
114. Background workers do not bypass immutable history rules.
115. Background workers do not bypass idempotency.
116. Background workers do not bypass concurrency rules.
117. Job handlers use Application-level business operations.
118. Queue implementation details remain outside Domain.
119. Queue and worker failures degrade asynchronous functionality before core POS functionality.
120. Queue architecture must preserve FastFood ERP historical integrity.

---

# 121. Recommended Initial Implementation

The initial implementation should remain simple.

Recommended architecture:

```text
                    ┌──────────────────┐
                    │   FastFood API   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │
                    │  Business State  │
                    └────────┬─────────┘
                             │
                       Outbox Events
                             │
                             ▼
                    ┌──────────────────┐
                    │ Queue / Broker   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Operational       Reporting       Maintenance
          Worker           Worker            Worker
              │              │                │
              └──────────────┼────────────────┘
                             ▼
                    Application Services
```

The first production deployment does not require a distributed microservice architecture.

---

# 122. Initial Worker Processes

Recommended initial processes:

```text
fastfood-worker
fastfood-scheduler
```

The worker may initially process multiple logical queues with bounded concurrency.

Separate worker processes should be introduced only when workload isolation becomes necessary.

---

# 123. Initial Queue Strategy

Initial queue strategy:

```text
Operational
Synchronization
Notifications
Reports/Exports
Maintenance
```

Priority and concurrency limits should protect operational work.

---

# 124. Initial Technology Boundary

The technology choice for queue infrastructure may be:

* Redis-backed queue;
* another reliable queue implementation.

The exact technology is an Infrastructure decision.

The Application and Domain layers must remain independent from it.

---

# 125. Completion Criteria

The Queue and Worker architecture is considered production-ready when:

* jobs have explicit lifecycle states;
* retry policies are defined;
* idempotency is implemented;
* dead-letter handling exists;
* worker concurrency is bounded;
* queue backlog is observable;
* critical jobs are prioritized;
* POS resource protection exists;
* Outbox integration is implemented;
* graceful shutdown works;
* worker crash recovery works;
* Business/Branch isolation is enforced;
* subscription/lifecycle validation is enforced;
* sensitive payload protection exists;
* job tracing exists;
* SLO monitoring exists;
* load testing validates worker capacity;
* failure/recovery tests pass;
* operational runbooks exist.

---

# 126. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/02_Backend_Project_Structure.md`
* `docs/04_Architecture/06_Backend/03_Application_and_Use_Case_Layer.md`
* `docs/04_Architecture/06_Backend/04_Domain_Service_and_Business_Logic.md`
* `docs/04_Architecture/06_Backend/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/08_Error_Handling_and_Exception_Architecture.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/06_Backend/11_Configuration_and_Environment_Management.md`
* `docs/04_Architecture/06_Backend/12_Reporting_and_Export_Architecture.md`
* `docs/04_Architecture/06_Backend/13_Backend_Health_Observability_and_Monitoring.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/15_Backend_File_Storage_and_Document_Management.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/17_Backend_Testing_and_Quality_Assurance_Architecture.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/19_Backend_Deployment_and_Runtime_Architecture.md`
* `docs/04_Architecture/06_Backend/20_Backend_Operations_and_Incident_Management_Architecture.md`
* `docs/04_Architecture/06_Backend/21_Backend_Disaster_Recovery_and_Business_Continuity_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`

### Database

* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/28_Database_Backup_and_Recovery.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Security

* `docs/11_Security/README.md`

### Operations

* `docs/14_Operations/README.md`

---

# 127. Status

**Backend Architecture Document:** Completed

**Document:** `25_Backend_Queue_and_Worker_Architecture.md`

**Document Status:** Proposed

**Backend Document Sequence:** 01–25 complete

**Backend Architecture Scope:** Complete

**Next Documentation Area:** Continue with the next planned architecture/documentation section outside the Backend document sequence.

