# Background Workers and Scheduler Deployment

**Document ID:** DEP-12
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/10_Deployment/README.md`
**Previous Document:** `docs/10_Deployment/11_Frontend_Deployment_and_Static_Asset_Delivery.md`
**Next Document:** `docs/10_Deployment/13_AI_Runtime_and_Model_Service_Deployment.md`

---

## 1. Purpose

This document defines the deployment and runtime architecture for FastFood ERP background workers and scheduler processes.

Background processing exists to execute work that should not unnecessarily occupy normal API workers.

The architecture must support:

* asynchronous business-side work;
* notifications;
* printing;
* report generation;
* XLSX export;
* synchronization processing where applicable;
* cleanup;
* lifecycle processing;
* selected external integrations;
* scheduled jobs;
* retryable background operations.

The worker architecture must remain:

* bounded;
* observable;
* idempotent;
* recoverable;
* horizontally scalable;
* isolated from core POS traffic.

---

# 2. Scope

This document covers:

* worker process model;
* worker deployment;
* worker pools;
* queue selection;
* queue priority;
* scheduler deployment;
* scheduled jobs;
* cron interaction;
* concurrency;
* retry;
* backoff;
* dead-letter handling;
* job lifecycle;
* idempotent processing;
* graceful shutdown;
* worker health;
* worker resource limits;
* worker scaling;
* queue isolation;
* synchronization worker deployment;
* notification worker deployment;
* printing worker deployment;
* reporting worker deployment;
* cleanup worker deployment;
* lifecycle worker deployment;
* external integration workers;
* deployment rollout;
* mixed-version compatibility;
* failure recovery;
* monitoring;
* worker SLOs;
* production readiness;
* runtime invariants.

This document does not redefine queue semantics already established by the Redis/Queue architecture.

---

# 3. Runtime Position

Background workers operate outside the synchronous API request path.

```text
API
 ↓
Application
 ↓
PostgreSQL Transaction
 ↓
Outbox / Durable Job State
 ↓
Queue
 ↓
Background Worker
 ↓
External Service / Report / Printer / Secondary Processing
```

Scheduled work follows:

```text
Scheduler
   ↓
Create / Enqueue Job
   ↓
Queue
   ↓
Worker
```

The scheduler does not directly perform large Business operations.

---

# 4. Deployment Principles

The worker deployment follows these principles:

1. Core Business transactions remain authoritative in PostgreSQL.
2. Background workers execute secondary or deferred work.
3. Worker processes are replaceable.
4. Worker processes are stateless with respect to durable Business state.
5. Workers use durable job identifiers.
6. Retryable jobs are idempotent.
7. Concurrency is bounded.
8. Queue consumption is bounded.
9. Critical work is isolated from heavy work.
10. Synchronization must not starve POS-related processing.
11. Large reports must not starve notifications or critical work.
12. Scheduler failure must not silently duplicate scheduled jobs.
13. Retry behavior must be bounded.
14. Failed jobs must remain observable.
15. Permanent failures must be separated from retryable failures.
16. Worker shutdown must be graceful.
17. Deployment must support rolling replacement where infrastructure allows.
18. Mixed-version processing must remain compatible during deployment.
19. Worker resource usage must be measurable.
20. Heavy background work must remain controllable during resource pressure.

---

# 5. Why Background Workers Exist

Background workers prevent long-running work from occupying API request processes.

Suitable background tasks include:

```text
Notifications
Printing
Large Reports
XLSX Export
Lifecycle Processing
Cleanup
Selected Synchronization Work
External Integrations
Heavy Computation
```

The API should normally perform:

```text
Validate
Authorize
Commit Core State
Create Durable Work Reference
Return
```

and allow workers to perform deferred work afterward.

---

# 6. API and Worker Boundary

The API runtime and worker runtime are separate execution environments.

```text id="9ryfw3"
API
→ latency-sensitive request processing

Worker
→ asynchronous processing
```

A worker must never require a specific API process to remain alive.

---

# 7. Worker Process Model

The initial worker model uses independent worker processes.

Conceptually:

```text id="j8efy4"
Worker Runtime
├── Worker Process 1
├── Worker Process 2
├── Worker Process 3
└── Worker Process N
```

Each process has bounded concurrency.

Worker process memory is temporary.

---

# 8. Worker Runtime Technology

The worker framework is implementation-specific.

It may use:

* a Python task processing framework;
* a queue consumer library;
* another compatible background-job runtime.

The selected technology must support:

* durable job handling;
* acknowledgements;
* retries;
* visibility/recovery of unfinished work;
* bounded concurrency;
* graceful shutdown.

The architecture must not depend on a specific vendor unless explicitly approved.

---

# 9. Worker Deployment Types

The deployment may contain different worker groups:

```text id="avgl6o"
Critical Workers
Normal Workers
Heavy Workers
Synchronization Workers
Reporting Workers
AI Workers
```

Separate groups may use different:

* queues;
* concurrency;
* resource limits;
* autoscaling rules;
* deployment cadence.

---

# 10. Critical Worker Pool

Critical workers process jobs with high operational importance.

Examples:

* required synchronization processing;
* critical security/lifecycle jobs;
* high-priority notification processing;
* other jobs explicitly classified as critical.

Critical worker capacity must be protected from heavy workloads.

---

# 11. Normal Worker Pool

Normal workers handle routine deferred processing.

Examples:

* ordinary notifications;
* printing;
* normal external integrations;
* routine asynchronous operations.

---

# 12. Heavy Worker Pool

Heavy workers execute resource-intensive work.

Examples:

* large reports;
* XLSX generation;
* large cleanup operations;
* computationally expensive transformation.

Heavy workers must not consume the full resource budget required by critical and POS-related workloads.

---

# 13. Synchronization Worker Pool

Synchronization processing may use a dedicated worker pool when traffic volume justifies separation.

Its purpose is to prevent reconnect bursts from consuming all general worker capacity.

---

# 14. Reporting Worker Pool

Large reports and exports may use separate worker processes.

This allows:

```text id="rzz0s9"
POS / Critical Work
        ≠
Large Report Processing
```

A report burst must not starve critical queues.

---

# 15. AI Worker Boundary

AI-heavy background workloads should use the dedicated AI runtime where appropriate.

General ERP workers should not become an uncontrolled AI inference pool.

---

# 16. Queue Topology

A simple deployment may use logical queues such as:

```text id="v8rh32"
critical
normal
heavy
sync
report
```

Exact queue count may change with measured workload.

The queue topology must remain understandable.

---

# 17. Queue Priority

Initial priority principle:

```text id="bqz8zy"
1. Critical
2. POS-supporting background work
3. Financial / inventory supporting work
4. Normal
5. Synchronization
6. Heavy reports / exports
7. Optional integrations
```

The exact queue classification must be documented for each job type.

---

# 18. Queue Isolation

A single queue must not be allowed to monopolize all workers.

For example:

```text id="s9ap4c"
1000 Report Jobs
      ↓
must not block
      ↓
Critical Notification Jobs
```

Isolation may be implemented through:

* separate queues;
* separate worker pools;
* concurrency reservations;
* weighted scheduling.

---

# 19. Reserved Critical Capacity

Production deployments should reserve worker capacity for critical work.

Example:

```text id="kn52gf"
Critical Worker Pool
→ protected capacity

Heavy Worker Pool
→ independent capacity
```

The exact ratio is environment-specific.

---

# 20. Worker Concurrency

Concurrency must be explicitly bounded.

The maximum concurrency depends on:

* CPU;
* memory;
* database connections;
* external provider limits;
* job type;
* expected job duration.

Unlimited concurrency is prohibited.

---

# 21. Job Concurrency Classes

Different jobs may require different concurrency limits.

Example:

```text id="u1s8hl"
CPU-heavy
→ low concurrency

Database-heavy
→ moderate controlled concurrency

I/O-heavy
→ higher concurrency only when safe
```

One global worker concurrency value should not be assumed to suit every job type.

---

# 22. Database-Aware Concurrency

Worker concurrency must consider PostgreSQL connection capacity.

Example:

```text id="dq5f1n"
Worker Processes
×
Worker Concurrency
×
Database Connection Usage
```

must remain within the database capacity budget.

Scaling workers without increasing database capacity review is prohibited.

---

# 23. Worker Memory Limits

Worker memory must remain bounded.

Potential memory-heavy tasks include:

* report generation;
* XLSX generation;
* file processing;
* data aggregation;
* image processing.

Heavy jobs should use dedicated limits and may require worker recycling.

---

# 24. Worker CPU Limits

CPU-heavy jobs should use:

* separate queues;
* separate worker pools;
* bounded concurrency;
* controlled CPU resources.

They must not exhaust API host CPU required for POS traffic.

---

# 25. Worker Process Recycling

Worker processes may be recycled based on:

* job count;
* memory growth;
* deployment;
* operational maintenance.

Recycling should be staggered where practical.

---

# 26. Job Lifecycle

A job should follow a controlled lifecycle:

```text id="vktbg9"
PENDING
   ↓
QUEUED
   ↓
PROCESSING
   ↓
SUCCEEDED
```

Failure path:

```text id="g2ijyl"
PROCESSING
   ↓
FAILED
   ↓
RETRYING
   ↓
PROCESSING
```

Permanent failure:

```text id="h0yx8q"
FAILED
   ↓
DEAD_LETTER / MANUAL REVIEW
```

Exact state names may be refined during implementation.

---

# 27. Job Identity

Every durable background operation should have a unique job identity.

The job identity is separate from:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Order UUID;
* Operation UUID.

---

# 28. Operation Identity

Where a job originates from a user or device operation, the worker should preserve the original operation identity.

This supports:

* idempotency;
* audit;
* tracing;
* debugging;
* recovery.

---

# 29. Job Payload

Jobs should carry the minimum required payload.

A job should prefer durable identifiers rather than large embedded object graphs.

Example:

```text id="e8rb1m"
job:
    job_id
    operation_id
    Business
    Branch
    entity_id
    job_type
```

The worker may reload current authoritative data when appropriate.

Historical snapshot requirements must be respected.

---

# 30. Historical Job Payloads

Jobs related to historical Business transactions must not silently reinterpret those transactions using current configuration.

For example:

```text id="pv4h8o"
Historical Order
≠
Current Product Price
```

The worker must use the authoritative transaction snapshot or version required by the Business rule.

---

# 31. Idempotent Processing

Worker handlers must be idempotent where duplicate delivery is possible.

Example:

```text id="6xzzh3"
Job J
 ↓
Processed successfully

Job J
 ↓
Delivered again

Result:
No duplicate Business effect
```

At-least-once queue processing must therefore be expected.

---

# 32. Duplicate Job Delivery

Workers must assume that the same job may be delivered more than once because of:

* worker crash;
* acknowledgement loss;
* network interruption;
* queue redelivery;
* deployment.

Duplicate handling must be explicit.

---

# 33. Database Idempotency

Where job processing changes authoritative Business state, duplicate protection should rely on:

* unique constraints;
* operation UUID;
* idempotency records;
* transactional state checks.

A worker-local boolean flag is insufficient.

---

# 34. Acknowledgement Strategy

A job should be acknowledged only after the worker has completed the required processing according to the job's durability semantics.

For example:

```text id="q2tkr6"
Receive Job
 ↓
Process
 ↓
Commit Required State
 ↓
Acknowledge
```

The exact acknowledgement behavior depends on the selected queue technology.

---

# 35. Crash During Processing

If a worker crashes during processing:

```text id="jc1q89"
Job
 ↓
PROCESSING
 ↓
Worker Crash
 ↓
Job Becomes Retryable / Recoverable
```

The job must not be permanently lost when durable queue semantics require redelivery.

---

# 36. Retry Classification

Failures should be classified as:

### Retryable

Examples:

* temporary database failure;
* temporary Redis failure;
* temporary storage failure;
* temporary external API failure;
* network timeout.

### Non-Retryable

Examples:

* invalid payload;
* unsupported operation type;
* permanently invalid Business state;
* authorization failure;
* incompatible schema.

---

# 37. Retry Count

Retry count must be bounded.

Example conceptual configuration:

```text id="4sa41k"
Attempt 1
Attempt 2
Attempt 3
...
Maximum Attempts
```

The exact maximum is job-type-specific.

Unlimited retries are prohibited.

---

# 38. Retry Backoff

Retryable jobs should use backoff.

Conceptually:

```text id="qd1f92"
Failure
 ↓
Short Delay
 ↓
Retry
 ↓
Longer Delay
 ↓
Retry
```

Exponential or another bounded backoff strategy may be used.

---

# 39. Retry Jitter

Jitter may be applied so many jobs do not retry simultaneously after a shared dependency failure.

This reduces retry storms.

---

# 40. Retry and Idempotency

A job must be safe to retry before retry is enabled.

The system must not configure aggressive retries for a non-idempotent job.

---

# 41. Dead-Letter Queue

Jobs that exceed retry limits or encounter permanent processing errors should enter a dead-letter state.

The dead-letter record should retain:

* job identity;
* operation identity;
* error classification;
* attempt count;
* timestamps;
* relevant context;
* last failure reason.

---

# 42. Dead-Letter Handling

Dead-letter jobs must remain observable.

Operators may:

* inspect;
* repair;
* retry;
* cancel;
* permanently resolve.

Any Business-impacting manual action must follow authorization and audit requirements.

---

# 43. Poison Job Protection

A malformed or permanently failing job must not continuously consume worker resources.

Once classified as non-retryable or retry-exhausted, it must be isolated.

---

# 44. Queue Backpressure

When queues grow excessively:

* worker concurrency may be increased within capacity;
* low-priority work may be throttled;
* synchronization may be reduced;
* heavy jobs may be paused;
* producers may receive backpressure where appropriate.

The system must not allow unlimited queue growth without control.

---

# 45. Queue Growth Monitoring

Monitoring should track:

```text id="k1ubtp"
Queue Depth
Oldest Job Age
Processing Rate
Failure Rate
Retry Rate
Dead-Letter Count
```

Queue depth alone is insufficient.

---

# 46. Oldest Job Age

The age of the oldest pending job is an important operational signal.

A low queue count can still indicate failure if the oldest job remains stuck for too long.

---

# 47. Worker Fairness

The scheduler/worker system should avoid starvation.

Critical work should remain protected.

Normal work should not permanently starve.

Heavy work may be throttled but should remain eventually processable under normal conditions.

---

# 48. Scheduled Job Architecture

Scheduled jobs should follow:

```text id="i16qwj"
Scheduler
   ↓
Create Job
   ↓
Queue
   ↓
Worker
   ↓
Process
```

The scheduler should normally enqueue work rather than execute large jobs itself.

---

# 49. Scheduler Responsibilities

The scheduler is responsible for:

* deciding when a job is due;
* creating/enqueuing scheduled work;
* avoiding unintended duplicate scheduling;
* recording scheduling outcome;
* supporting retry/recovery of scheduler actions.

The scheduler should not become a general-purpose worker.

---

# 50. Scheduler Process

The scheduler may run as a separate process:

```text id="z6cjw9"
Scheduler
   ↓
Queue
   ↓
Workers
```

This makes scheduler failure independent from API and worker execution.

---

# 51. Scheduler Singleton Coordination

If multiple scheduler instances are deployed, they must coordinate so the same scheduled job is not created multiple times.

Possible mechanisms include:

* database advisory locking;
* durable scheduler state;
* distributed coordination.

The mechanism must preserve idempotency.

---

# 52. Scheduler Idempotency

A scheduled job should have a deterministic schedule identity.

Example:

```text id="vvgl4t"
job:
    schedule_name
    scheduled_for
    Business
    Branch where applicable
```

The same scheduled occurrence must not create unintended duplicate jobs.

---

# 53. Scheduled Occurrence Identity

Each scheduled occurrence should be uniquely identifiable where duplicate creation could cause Business impact.

Conceptually:

```text id="w7x3n2"
daily_report
+
Business
+
Branch
+
2026-10-08
```

should resolve to one logical scheduled occurrence.

---

# 54. Scheduler Timezone

Scheduled Business operations must use explicit timezone rules.

The scheduler must distinguish:

* UTC timestamps;
* Business timezone;
* Branch timezone;
* calendar date.

Ambiguous local time must not silently change the scheduled Business date.

---

# 55. Business-Date Scheduling

Jobs such as monthly reports and payroll-related processing may depend on Business calendar rules.

The scheduler must use the configured Business/Branch timezone rather than assuming the server timezone.

---

# 56. Scheduler and DST

Where deployments operate across timezones with daylight-saving changes, scheduled jobs must use timezone-aware scheduling.

No Business operation should rely on an ambiguous naive local timestamp.

---

# 57. Scheduler Missed Job Policy

If the scheduler is unavailable when a job becomes due, the system must have an explicit missed-job policy.

Possible policies:

```text
Run Once After Recovery
Skip
Recalculate
```

The choice is job-specific.

---

# 58. Scheduler Recovery

After scheduler restart:

```text id="udxbpp"
Scheduler Restart
 ↓
Load Durable Schedule State
 ↓
Detect Missed / Pending Occurrences
 ↓
Create Required Jobs
 ↓
Resume Scheduling
```

The scheduler must not blindly recreate every historical occurrence.

---

# 59. Scheduler Failure

If the scheduler stops:

* existing queued jobs continue to run;
* already created jobs remain processable;
* future schedule creation stops until recovery;
* monitoring must alert.

Scheduler failure must not cancel already committed Business state.

---

# 60. Scheduler and Cron

Traditional OS cron may be used for simple infrastructure tasks such as:

* service maintenance;
* host-level cleanup;
* backup trigger where architecture permits.

Business-critical application schedules should preferably be managed through the application scheduler and durable job state.

---

# 61. Cron Restriction

Business-critical processing must not depend only on an undocumented host crontab.

A cron-based process must be:

* version-controlled;
* documented;
* monitored;
* recoverable.

---

# 62. Scheduler Frequency

Scheduler polling frequency should be appropriate to job criticality.

High-frequency polling must not create unnecessary database load.

A scheduled job should not require millisecond-level precision unless explicitly required.

---

# 63. Scheduler Database Load

The scheduler must not perform broad database scans every few seconds.

Schedule lookup should use:

* indexed due-time fields;
* efficient locking;
* bounded queries.

---

# 64. Scheduled Job Batching

When many schedules become due simultaneously, the scheduler should process them in bounded batches.

Example:

```text id="v4j06q"
10,000 due jobs
    ↓
bounded batches
    ↓
queue
```

The scheduler must not attempt unlimited enqueueing in one operation.

---

# 65. Scheduler Queue Protection

A large scheduled release must not flood critical queues.

Scheduled jobs should use:

* appropriate priority;
* queue limits;
* bounded enqueue batches.

---

# 66. Recurring Job Types

Expected recurring workload may include:

```text id="zpn8qb"
Monthly reports
Subscription checks
Subscription lifecycle processing
Salary reminders
Low-stock analysis
Cleanup
Notification reminders
Data lifecycle tasks
Operational maintenance
```

Each recurring job must have a documented ownership and failure policy.

---

# 67. Monthly Report Scheduling

The monthly report job must respect Business calendar rules.

The worker must generate the report only when the defined reporting conditions are satisfied.

The scheduler must not interpret an already-created immutable report version as mutable state.

---

# 68. Subscription Lifecycle Scheduling

Subscription jobs may:

* detect expiry;
* transition Business lifecycle state;
* create notifications;
* mark deletion eligibility;
* initiate deletion workflows.

Critical lifecycle state changes must remain authoritative in PostgreSQL.

---

# 69. Data Deletion Jobs

Data deletion is a high-impact background process.

Deletion workers must use:

* bounded batches;
* explicit lifecycle state;
* authorization-controlled execution;
* audit/logging;
* recovery-safe sequencing.

Deletion must not be performed by the scheduler directly.

---

# 70. Notification Worker

Notification workers process asynchronous notifications.

Examples:

* subscription ending;
* salary due;
* inventory alert;
* large refund;
* cash discrepancy;
* correction request;
* synchronization conflict;
* security alert.

Notification delivery is secondary to the underlying Business transaction.

---

# 71. Notification Retry

Notification jobs may retry temporary provider failures.

A permanently invalid recipient/provider configuration should not retry indefinitely.

---

# 72. Printing Worker

Printing may use a dedicated worker or worker pool.

Preferred flow:

```text id="kmgpyj"
Order Commit
 ↓
Print Job
 ↓
Print Worker
 ↓
Printer
```

Printer failure must not normally roll back the committed Order.

---

# 73. Printer Retry

Printing retry must be designed carefully.

Repeated printer failure must not create duplicate physical prints without tracking.

Print jobs should have:

* print job identity;
* attempt count;
* target printer;
* target document;
* print status.

---

# 74. Report Worker

Report workers generate large reports asynchronously.

The report worker must use:

* bounded memory;
* efficient database queries;
* bounded concurrency;
* controlled file generation.

Reports must not block API workers.

---

# 75. XLSX Worker

XLSX export should use a dedicated report/export worker class or queue where workload justifies isolation.

Large XLSX generation must not consume all worker memory.

Streaming or chunked generation should be preferred when appropriate.

---

# 76. Synchronization Worker

Synchronization workers process reconnecting trusted devices.

The worker must preserve:

* operation UUID;
* Business;
* Branch;
* Device;
* Employee;
* client sequence;
* authoritative validation result.

---

# 77. Synchronization Retry

Temporary infrastructure errors may be retried.

Business conflicts and validation failures must not be retried automatically as though they were infrastructure failures.

---

# 78. Synchronization Priority

Synchronization must not outrank live core POS operations.

During high load:

```text id="t9i4oe"
POS
 ↓
Financial / Inventory
 ↓
Critical Background
 ↓
Normal Background
 ↓
Synchronization
 ↓
Heavy Processing
```

---

# 79. External Integration Worker

External integrations should normally execute through background workers when latency is not part of the core transaction.

Examples:

* email;
* SMS;
* third-party webhooks;
* future integrations.

---

# 80. External Integration Retry

External integration jobs require:

* bounded retry;
* provider-specific timeout;
* idempotency;
* failure classification;
* dead-letter handling.

---

# 81. Webhook Worker

Inbound or outbound webhook processing should be isolated where volume justifies it.

Webhook delivery must use:

* stable event identity;
* retry;
* idempotency;
* signature validation where applicable.

---

# 82. Worker Startup

Worker startup sequence:

```text id="rx1wdn"
Process Start
 ↓
Load Configuration
 ↓
Validate Configuration
 ↓
Initialize Application
 ↓
Connect to Required Infrastructure
 ↓
Register Worker
 ↓
Health / Readiness
 ↓
Consume Jobs
```

Large Business data must not be preloaded unnecessarily.

---

# 83. Worker Readiness

A worker should become ready only after:

* configuration is valid;
* required queue access exists;
* required database access is available;
* required dependencies are initialized.

An unready worker must not receive normal work.

---

# 84. Worker Liveness

Worker liveness should indicate that the process is alive and able to execute its event loop/consumer loop.

Liveness should remain lightweight.

---

# 85. Worker Health

Worker health should provide enough information to determine:

* process is alive;
* queue consumption is active;
* required dependencies are reachable;
* worker is not permanently stuck.

Sensitive infrastructure data must not be exposed.

---

# 86. Worker Heartbeat

Where supported, workers should provide a heartbeat or lease mechanism.

The purpose is to detect:

* worker crash;
* worker stall;
* network partition;
* processing inactivity.

The mechanism must not itself become an authoritative Business state store.

---

# 87. Job Visibility Timeout

If the selected queue technology uses a visibility timeout or lease:

* it must exceed expected job execution time;
* long-running jobs must renew the lease when necessary;
* a job must not be prematurely redelivered while healthy processing is still occurring.

The exact mechanism depends on the queue technology.

---

# 88. Long-Running Job Protection

Long-running jobs should support:

* heartbeat;
* lease renewal;
* progress tracking where useful;
* cancellation policy.

A worker must not appear idle while performing valid long-running work.

---

# 89. Graceful Worker Shutdown

Shutdown sequence:

```text id="h4f6yp"
Ready
 ↓
Stop Accepting New Jobs
 ↓
Finish Safe Active Jobs
 ↓
Acknowledge Completed Jobs
 ↓
Release Resources
 ↓
Exit
```

Jobs that cannot safely complete should remain retryable.

---

# 90. Worker Shutdown Timeout

Shutdown must have a bounded grace period.

The grace period must be compatible with:

* typical job duration;
* lease timeout;
* deployment strategy.

A worker must not block deployment indefinitely.

---

# 91. Forced Worker Termination

If forced termination occurs:

* incomplete jobs must remain recoverable;
* already committed state must remain committed;
* non-committed state must not be reported as successful.

---

# 92. Rolling Worker Deployment

With multiple workers:

```text id="h2km7g"
Old Worker
Old Worker
New Worker
New Worker
```

may coexist during rollout.

The deployment must ensure:

* queue compatibility;
* job schema compatibility;
* database schema compatibility;
* idempotency compatibility.

---

# 93. Mixed-Version Jobs

Jobs created by an older application version may be processed by a newer worker.

The worker must either:

* remain backward-compatible;
* support explicit job versioning;
* reject incompatible jobs safely into a controlled failure state.

Silent reinterpretation is prohibited.

---

# 94. Job Schema Version

For complex jobs, the payload may include:

```text id="c9r4e3"
job_type
job_version
```

This allows workers to distinguish old and new job contracts.

---

# 95. Breaking Job Changes

Breaking job payload changes require:

* explicit versioning;
* migration;
* compatibility layer;
* controlled queue drain.

A worker must not assume every existing queued message uses the newest schema.

---

# 96. Worker Deployment Artifact

Each worker release should be identifiable by:

```text id="f6lhuw"
Source Commit
Release ID
Build ID
Dependency Lock
```

Worker artifacts should be reproducible.

---

# 97. Worker and API Version Compatibility

Workers and API instances may temporarily run different releases.

The architecture must define compatibility for:

* job payloads;
* database schema;
* outbox events;
* cache;
* configuration.

---

# 98. Worker Resource Isolation

Where possible, workers should run in separate resource groups from API processes.

This is especially important for:

* reports;
* XLSX;
* AI;
* large cleanup;
* heavy synchronization.

---

# 99. Host Co-Location

On small deployments, API and workers may share the same host.

If co-located:

* CPU limits must protect API;
* memory limits must protect API;
* heavy jobs must be restricted;
* worker concurrency must be bounded.

---

# 100. Worker Isolation on Larger Deployments

As workload grows, workers may move to separate hosts or compute pools.

Conceptually:

```text id="tp4l1p"
API Host
   ↓
API

Worker Host
   ↓
Workers

Heavy Worker Host
   ↓
Reports / Heavy Work
```

The application architecture remains unchanged.

---

# 101. Autoscaling Workers

Workers may scale based on:

* queue depth;
* oldest job age;
* processing rate;
* CPU;
* memory.

Autoscaling must use bounded minimum and maximum worker counts.

---

# 102. Autoscaling and Database Capacity

Worker autoscaling must account for:

```text id="2l9c5o"
More Workers
→ More Database Connections
→ More Database Load
```

The autoscaler must not create unlimited database pressure.

---

# 103. Queue Age Based Scaling

For latency-sensitive queues, oldest-job age may be more useful than queue depth alone.

Example:

```text id="z1u5vk"
Critical queue depth = 5
Oldest job = 40 seconds
```

may require scaling even though queue depth is small.

---

# 104. Worker Minimum Capacity

Critical worker pools should maintain enough capacity to meet their latency objective under expected normal load.

The minimum must be based on measured workload.

---

# 105. Worker Maximum Capacity

Maximum workers must be limited by:

* CPU;
* memory;
* PostgreSQL;
* Redis;
* external provider limits;
* deployment budget.

---

# 106. Queue Fairness Under Load

Heavy queue growth must not cause:

```text id="i4xwgl"
Heavy Queue
→ Consume All Workers
```

Critical and normal worker capacity must remain protected.

---

# 107. Backpressure

The system should use backpressure when:

* queue depth is excessive;
* database load is high;
* external provider rate limits are reached;
* synchronization bursts occur;
* memory pressure increases.

Backpressure may reduce enqueue rate, worker concurrency or processing priority.

---

# 108. External Provider Rate Limits

Workers communicating with external providers must respect:

* provider rate limits;
* bounded concurrency;
* retry-after information where available.

A provider outage must not create unlimited retries.

---

# 109. Worker Network Limits

Worker processes must have appropriate network access.

They should not receive unnecessary access to:

* public services;
* administrative ports;
* unrelated internal services.

Least network privilege should be used.

---

# 110. Worker Security Context

Worker processes must execute with the minimum permissions required for their jobs.

A notification worker should not automatically have access to:

* database administration;
* deployment infrastructure;
* unrelated file storage.

---

# 111. Worker Secrets

Worker-specific credentials should be injected through controlled secret management.

Secrets must not be:

* embedded into job payloads;
* written to logs;
* stored in source control.

---

# 112. Job Payload Security

Job payloads may contain Business or operational data.

Therefore:

* sensitive information should be minimized;
* access should be restricted;
* logs must not print full payloads unnecessarily;
* durable job storage must follow the security architecture.

---

# 113. Business Scope in Jobs

Every Business-scoped job must retain Business context where necessary.

Example:

```text id="36uwm4"
job
├── business_id
├── branch_id where applicable
├── operation_id
└── entity_id
```

Workers must validate scope before executing Business-sensitive work.

---

# 114. Branch Scope in Jobs

Branch-scoped jobs must retain Branch identity where required.

A worker must not accidentally execute Branch A work against Branch B.

---

# 115. Employee Context

Where a job originated from an employee action, employee identity may be retained for audit and traceability.

The worker must not assume that the employee remains active merely because the job payload contains the employee UUID.

Current authorization and Business rules remain authoritative where required.

---

# 116. Subscription-Aware Workers

Background processing must respect subscription lifecycle rules.

For example:

* notification jobs may continue where required;
* modification-producing jobs must respect READ_ONLY state;
* deletion jobs execute only in valid lifecycle states.

Workers must not bypass subscription restrictions.

---

# 117. Lifecycle Job Safety

Data lifecycle jobs are high-impact operations.

They must use:

* explicit lifecycle states;
* bounded batches;
* checkpointing where useful;
* auditability;
* deterministic retry behavior.

---

# 118. Worker Checkpointing

Large jobs may use checkpoints.

A checkpoint should identify progress without making partial progress appear fully committed.

Checkpoint state must be durable where recovery depends on it.

---

# 119. Partial Job Success

Some batch jobs may process multiple independent items.

The worker should support:

```text id="0z1u5b"
Item 1 → Success
Item 2 → Success
Item 3 → Retry
Item 4 → Invalid
```

rather than forcing an unnecessary all-or-nothing process when Business rules allow independent outcomes.

---

# 120. Job Cancellation

Jobs may support cancellation where safe.

Cancellation must not:

* corrupt partial Business state;
* silently reverse committed operations;
* discard audit information.

A cancellation policy must be defined per job type.

---

# 121. Job Progress

Long-running jobs may expose progress such as:

```text id="xg1p3b"
PENDING
PROCESSING
42%
COMPLETED
```

Progress is operational metadata.

The authoritative Business outcome remains the underlying committed state.

---

# 122. Scheduler and Job Dependencies

Some scheduled jobs may depend on other Business conditions.

Example:

```text id="q9fl5o"
Monthly Report
   ↓
Required Period Data Ready
   ↓
Create Report Job
```

The scheduler should not assume that time alone guarantees Business readiness.

---

# 123. Dependency-Aware Scheduling

Where a job has prerequisites:

* check the prerequisite;
* defer when appropriate;
* avoid rapid retry loops;
* record why execution is delayed.

---

# 124. Job Ordering

Where jobs have dependencies, they should use explicit ordering.

Example:

```text id="l8j4z0"
Transaction Synchronization
        ↓
Derived Report Generation
```

The second job should not run against incomplete prerequisite state.

---

# 125. Queue Dependency Safety

Queue order alone must not be treated as a transactional dependency.

Authoritative prerequisites must be validated using durable state.

---

# 126. Worker Observability

Worker monitoring must include:

```text id="m2v2je"
Worker Count
Worker Health
Queue Depth
Oldest Job Age
Processing Rate
Job Success Rate
Job Failure Rate
Retry Rate
Dead-Letter Count
Job Duration
CPU
Memory
Database Connections
```

---

# 127. Worker Metrics

Metrics should include stable labels such as:

```text id="x9tc6h"
job_type
queue
worker_pool
result
```

Business/Product UUIDs should not become uncontrolled metric labels.

---

# 128. Worker Logs

Worker logs should include:

```text id="zn2ix0"
timestamp
level
job_id
operation_id
job_type
queue
worker_pool
status
duration
release_id
```

Business context may be included where operationally required.

---

# 129. Payload Logging Restriction

Full job payloads must not normally be logged.

This reduces:

* sensitive data exposure;
* log volume;
* operational cost.

---

# 130. Worker Error Logging

Worker errors should record:

* job identity;
* failure classification;
* attempt number;
* safe error summary;
* retry decision.

Secrets and sensitive payloads must remain excluded.

---

# 131. Worker SLOs

Initial worker runtime objectives include:

| Metric                              |                       Target |
| ----------------------------------- | ---------------------------: |
| Critical queue normal dispatch      |                        ≤ 5 s |
| Critical notification processing    |                       ≤ 10 s |
| Normal notification processing      |                       ≤ 60 s |
| Normal synchronization batch        |                    ≤ 1 s p95 |
| Job enqueue latency                 |                 ≤ 100 ms p95 |
| Job status retrieval                |                 ≤ 200 ms p95 |
| Worker/service monthly availability |                      ≥ 99.9% |
| Retry storm prevention              |                      bounded |
| Dead-letter visibility              | 100% of failed terminal jobs |

These targets are initial operational objectives and must be validated from production measurements.

---

# 132. Worker Latency Measurement

Worker latency should distinguish:

```text id="2u9gso"
Enqueue Delay
Queue Wait
Processing Duration
External Provider Delay
Database Time
Total Completion Time
```

This allows the actual bottleneck to be identified.

---

# 133. Scheduler SLO

The scheduler should meet an initial target of:

**Scheduled job creation p95 ≤ 60 seconds from intended schedule time under normal load.**

Higher precision should be used only where the Business requirement explicitly requires it.

---

# 134. Scheduler Monitoring

Monitor:

* scheduler heartbeat;
* last successful scheduling cycle;
* missed schedules;
* duplicate scheduling attempts;
* scheduling latency;
* scheduler process restarts.

---

# 135. Worker Alerting

Alerts should include:

### Critical

* critical queue oldest age above threshold;
* worker pool unavailable;
* repeated worker crashes;
* dead-letter growth.

### Warning

* sustained queue growth;
* retry spike;
* increased job duration;
* high memory;
* high CPU.

---

# 136. Scheduler Alerting

Alert when:

* scheduler heartbeat stops;
* scheduling cycles fail repeatedly;
* missed schedule count rises;
* duplicate schedule prevention triggers unexpectedly;
* schedule lag exceeds objective.

---

# 137. Deployment Monitoring

During worker deployment monitor:

```text id="vx3t8j"
Old Workers
New Workers
Queue Depth
Oldest Job Age
Job Failures
Retries
Dead Letters
Database Load
CPU
Memory
```

The deployment must not be judged only by whether processes start.

---

# 138. Worker Deployment Failure

If a new worker release fails:

```text id="zq2n6m"
New Worker
 ↓
Health Failure
 ↓
Do Not Increase Traffic
 ↓
Keep Healthy Workers
 ↓
Rollback / Investigate
```

Existing workers should continue processing compatible jobs where possible.

---

# 139. Worker Rollback

Rollback should:

* stop new worker versions;
* restore known-good worker artifact;
* preserve queued jobs;
* verify job schema compatibility;
* monitor queue recovery.

Rollback must not delete valid queued Business work.

---

# 140. Queue Drain Before Deployment

A queue does not necessarily need to be empty before deployment.

Instead, the system should verify:

* old job payloads are compatible;
* new workers can process them;
* old workers can finish safely;
* deployment does not discard queued jobs.

---

# 141. Job Schema Migration

When queued job schema must change:

```text id="7xk2pp"
Old Job
   ↓
Compatibility Worker
   ↓
New Job
```

or another explicit migration approach should be used.

Silent reinterpretation is prohibited.

---

# 142. Worker Deployment Order

A safe worker release may follow:

```text id="t7y8tu"
Deploy Compatibility Changes
       ↓
Deploy New Worker
       ↓
Verify
       ↓
Increase Worker Share
       ↓
Drain / Retire Old Worker
       ↓
Remove Legacy Support Later
```

---

# 143. Database Migration Relationship

Worker releases must obey the same expand/contract migration strategy as the API.

Workers may process jobs against a database schema shared with old and new application versions.

---

# 144. Cache Relationship

Worker cache usage must follow the same cache versioning and invalidation rules as the Backend API.

Worker-local caches must never become authoritative.

---

# 145. Redis Relationship

Workers may use Redis for:

* queue transport;
* short-lived coordination;
* caching.

Redis remains non-authoritative for Business transactions.

---

# 146. Worker Host Deployment

Workers may initially share an application host.

As workload grows, they may be moved to separate hosts.

Worker host replacement must not require Business data reconstruction.

---

# 147. Process Supervisor

Workers and scheduler should run under controlled process supervisors.

Initial VPS deployment may use:

```text id="q8gp95"
systemd
   ├── worker-critical
   ├── worker-normal
   ├── worker-heavy
   └── scheduler
```

The exact process grouping depends on workload.

---

# 148. Service Restart Policies

Each worker service should have:

* bounded restart behavior;
* backoff;
* crash-loop protection;
* logging;
* readiness/health monitoring.

---

# 149. Service User

Workers and scheduler should run under dedicated least-privilege service users.

A worker must not run as root under normal operation.

---

# 150. Worker Filesystem

Workers should use the filesystem only for controlled temporary processing.

Durable Business state must remain in:

* PostgreSQL;
* durable object/file storage;
* durable queue/job state where applicable.

---

# 151. Worker Temporary Storage

Temporary worker data must have:

* bounded size;
* cleanup;
* permission restrictions;
* finite lifetime.

A crashed worker must not leave unlimited temporary data accumulation.

---

# 152. Scheduler Configuration

Scheduler configuration must define:

```text id="9i03s5"
timezone
schedule definitions
poll interval
batch size
concurrency
missed-job policy
retry policy
```

Environment-specific settings must be controlled.

---

# 153. Scheduler Configuration Validation

Invalid scheduler configuration must fail safely.

Examples:

```text id="fz7bbf"
Invalid timezone
→ Startup Failure

Invalid schedule
→ Configuration Failure

Invalid queue
→ Startup Failure
```

---

# 154. Job Configuration

Each job type should define:

```text id="nd2hi4"
job_type
queue
priority
max_attempts
backoff
timeout
concurrency_class
resource_class
```

The exact representation may be configuration or code depending on implementation.

---

# 155. Job Timeout

Every job type should have a bounded execution timeout where practical.

A timeout should not automatically classify all failures as permanent.

The job failure policy must distinguish:

* timeout;
* retryable failure;
* permanent failure.

---

# 156. Job Heartbeat

Long-running jobs should use heartbeat/progress where supported.

This helps distinguish:

```text id="a4nxxn"
Healthy Long Job
vs
Stuck Worker
```

---

# 157. Worker Cancellation

Workers should stop accepting new work before shutdown.

Active jobs should either:

* finish;
* checkpoint;
* or become safely retryable.

---

# 158. Worker Pause

Operations may need to pause specific worker pools.

Examples:

```text id="v8xs3o"
Pause Heavy Reports
Pause Synchronization
Keep Critical Workers Running
```

This supports resource-pressure recovery.

---

# 159. Worker Capacity Protection

Critical worker pools must have protected capacity.

Heavy jobs must be prevented from consuming resources required by:

* POS-supporting tasks;
* financial operations;
* critical notifications;
* security/lifecycle jobs.

---

# 160. Synchronization Capacity Protection

Synchronization worker concurrency should be reduced during:

* database load spikes;
* POS latency degradation;
* queue backlog;
* reconnect storms.

---

# 161. Report Capacity Protection

Report/export concurrency should be reduced before database or memory pressure threatens API and critical workers.

---

# 162. Cleanup Capacity Protection

Cleanup jobs must use low or controlled priority.

They must not compete aggressively with active POS workload.

---

# 163. Job Retention

Completed and failed job metadata should have controlled retention.

Retention must support:

* operational investigation;
* audit requirements;
* retry/recovery;
* cost control.

Job retention must not become unlimited.

---

# 164. Job Cleanup

Job cleanup should itself be a bounded background operation.

Cleanup must not remove:

* active jobs;
* retryable jobs;
* dead-letter jobs still under review;
* records required for audit/history.

---

# 165. Scheduler State Retention

Scheduler state must be retained for enough time to investigate:

* missed jobs;
* duplicate prevention;
* schedule execution.

Retention must be bounded.

---

# 166. Worker Deployment Testing

Before production deployment, test:

* worker startup;
* scheduler startup;
* queue connection;
* job consumption;
* retry;
* backoff;
* dead-letter;
* worker crash recovery;
* graceful shutdown;
* concurrency limits;
* resource limits.

---

# 167. Failure Injection

Testing should simulate:

```text id="v2r1gi"
Database Failure
Redis Failure
Queue Failure
External Provider Timeout
Worker Crash
Scheduler Crash
Network Failure
Memory Pressure
CPU Pressure
```

The system must recover without duplicating Business effects.

---

# 168. Duplicate Delivery Testing

At-least-once processing must be tested explicitly.

Example:

```text id="k8j6c7"
Same Job
→ delivered twice
→ one Business effect
```

This is a release-blocking correctness test for idempotent jobs.

---

# 169. Retry Testing

Tests must verify:

* retryable failure retries;
* non-retryable failure does not retry indefinitely;
* backoff occurs;
* maximum attempts are respected;
* dead-letter transition occurs.

---

# 170. Scheduler Testing

Test:

* scheduled occurrence creation;
* duplicate prevention;
* missed schedule recovery;
* timezone behavior;
* DST-sensitive behavior where relevant;
* scheduler restart;
* concurrent scheduler instances.

---

# 171. Load Testing

Worker load tests should include:

```text id="q0i9ah"
Critical Queue
Normal Queue
Synchronization Burst
Large Reports
XLSX Exports
Notifications
Mixed Load
```

The mixed scenario is the most important.

---

# 172. Mixed-Load Requirement

A production-like test should demonstrate that:

```text id="fptu8z"
Large Report Burst
+
Synchronization Burst
+
Normal Notifications
```

does not make critical queue latency unacceptable.

---

# 173. Database Load Testing

Worker tests must measure:

* database CPU;
* query latency;
* connection count;
* lock wait;
* transaction duration.

A worker configuration that performs well at queue level but overloads PostgreSQL is not acceptable.

---

# 174. Worker Resource Regression

Each major worker release should compare:

```text id="9m6kmm"
Job Duration
CPU
Memory
Database Load
Queue Wait
Retry Rate
Failure Rate
```

against the previous baseline.

---

# 175. Production Readiness Gate

Before production worker deployment:

```text id="6xv7k6"
[ ] Worker artifact verified
[ ] Scheduler configuration verified
[ ] Queue connectivity verified
[ ] Database capacity verified
[ ] Worker concurrency verified
[ ] Retry policy verified
[ ] Dead-letter handling verified
[ ] Health checks verified
[ ] Monitoring enabled
[ ] Alerts enabled
[ ] Rollback path available
[ ] Mixed-version compatibility verified
[ ] Load tests passed
[ ] Failure tests passed
```

---

# 176. Initial Production Worker Layout

A small deployment may use:

```text id="u2m7q9"
Application Host
├── API
├── Critical Worker
├── Normal Worker
├── Heavy Worker
└── Scheduler
```

As workload grows:

```text id="04x3w6"
API Host
├── API

Worker Host
├── Critical Worker
├── Normal Worker
└── Synchronization Worker

Heavy Worker Host
├── Report Worker
├── XLSX Worker
└── Heavy Processing
```

The initial topology should remain simple until workload justifies separation.

---

# 177. Recommended Queue Allocation

Initial logical allocation:

```text id="d4h80l"
critical
normal
sync
heavy
report
```

Possible job mapping:

```text
critical
→ critical notifications
→ required lifecycle/security jobs

normal
→ printing
→ normal notifications
→ routine integrations

sync
→ offline synchronization

heavy
→ cleanup
→ heavy computation

report
→ reports
→ XLSX generation
```

Job classification may be refined after real workload measurement.

---

# 178. Recommended Concurrency Policy

Initial policy:

```text id="94x5sa"
Critical
→ reserved capacity

Normal
→ moderate concurrency

Sync
→ bounded burst capacity

Heavy
→ low controlled concurrency

Report
→ low controlled concurrency
```

Exact numerical concurrency values are environment-specific.

---

# 179. Runtime Optimization Order

Worker performance optimization should follow:

```text id="h41j4x"
1. Correct job boundaries
2. Database query efficiency
3. Job batching
4. Concurrency tuning
5. Queue isolation
6. Retry tuning
7. Worker scaling
8. Dedicated worker hosts
```

Complex infrastructure should not be introduced before simpler bottlenecks are measured.

---

# 180. Operational Recovery Priority

During worker resource pressure:

```text id="d4xqco"
1. Protect PostgreSQL
2. Protect POS
3. Protect critical jobs
4. Protect financial/inventory supporting work
5. Throttle synchronization
6. Throttle heavy/report work
7. Pause optional processing
```

---

# 181. Final Worker Architecture

The deployment model is:

```text id="1psynz"
                    ┌── Critical Workers
                    │
API ──→ Outbox ──→ Queue ──┼── Normal Workers
                    │
                    ├── Sync Workers
                    │
                    ├── Report Workers
                    │
                    └── Heavy Workers

Scheduler ───────────────→ Queue
```

The queue transports work.

Workers execute work.

PostgreSQL remains authoritative for transactional Business state.

---

# 182. Final Scheduler Architecture

```text id="m8q2e7"
Scheduler
   ↓
Determine Due Work
   ↓
Create Durable Job
   ↓
Queue
   ↓
Worker
   ↓
Business / External Processing
```

The scheduler does not replace:

* PostgreSQL transactions;
* worker processing;
* retry logic;
* Business authorization.

---

# 183. System Invariants

The following invariants apply to Background Workers and Scheduler Deployment:

1. Background workers are not authoritative Business storage.
2. PostgreSQL remains authoritative for transactional Business state.
3. Worker memory is temporary.
4. Worker local files are temporary.
5. Workers are replaceable.
6. Worker correctness does not depend on a specific process.
7. Worker correctness does not depend on a specific host.
8. Background jobs have stable identities.
9. Business-scoped jobs preserve Business context.
10. Branch-scoped jobs preserve Branch context where required.
11. Employee-originated jobs preserve actor context where needed.
12. Operation UUID remains distinct from Job UUID.
13. Retryable jobs are idempotent.
14. Duplicate job delivery does not duplicate authoritative Business effects.
15. Worker processing assumes at-least-once delivery where applicable.
16. Database constraints support duplicate protection where required.
17. Job acknowledgement does not precede required durable processing.
18. Failed processing remains recoverable according to queue semantics.
19. Retryable failures are classified separately from permanent failures.
20. Retry count is bounded.
21. Retry delay is bounded.
22. Retry storms are controlled.
23. Dead-letter jobs remain observable.
24. Poison jobs do not consume unlimited worker capacity.
25. Queue growth is observable.
26. Oldest pending job age is observable.
27. Worker concurrency is bounded.
28. Worker process count is bounded.
29. Worker memory is bounded.
30. Worker CPU usage is bounded.
31. Worker scaling requires PostgreSQL capacity review.
32. Worker scaling requires external dependency capacity review where applicable.
33. Critical worker capacity is protected from heavy work.
34. Synchronization cannot intentionally starve critical work.
35. Reports cannot intentionally starve critical work.
36. XLSX generation cannot intentionally starve critical work.
37. Heavy cleanup cannot intentionally starve POS-supporting work.
38. Heavy AI processing does not consume general worker capacity without explicit design.
39. Queue priority remains explicit.
40. Queue isolation remains explicit.
41. Background workers do not unnecessarily execute inside API requests.
42. Large reports run asynchronously.
43. Large XLSX generation runs asynchronously.
44. Printing is asynchronous where business rules allow.
45. Notifications are asynchronous where business rules allow.
46. External integrations are asynchronous where business rules allow.
47. Core transaction validity does not depend on immediate worker completion unless explicitly required.
48. Outbox and durable job creation follow transaction architecture.
49. Scheduler is not transactional Business authority.
50. Scheduler normally enqueues work instead of performing heavy work directly.
51. Scheduler has controlled identity.
52. Duplicate scheduled occurrences are prevented.
53. Multiple scheduler instances cannot unintentionally create duplicate scheduled jobs.
54. Scheduled jobs use explicit occurrence identity where duplicate execution has Business impact.
55. Scheduler uses explicit timezone rules.
56. Business-date schedules use Business or Branch timezone as required.
57. Scheduler does not depend blindly on server local timezone.
58. Missed-job policy is explicit.
59. Scheduler recovery does not blindly replay unlimited historical occurrences.
60. Scheduler failure does not cancel existing queued jobs.
61. Scheduler failure is observable.
62. Scheduler heartbeat is observable.
63. Scheduler lag is observable.
64. Scheduled job enqueueing is bounded.
65. Large scheduled bursts do not flood critical queues.
66. Cron is not the only undocumented source of Business-critical schedules.
67. Business-critical schedules are version-controlled and monitored.
68. Worker startup validates required configuration.
69. Invalid required worker configuration prevents safe readiness.
70. Worker readiness is separate from liveness.
71. Unready workers do not receive normal work.
72. Worker shutdown is graceful where possible.
73. Worker shutdown stops new work before termination.
74. Active jobs either complete safely or remain retryable.
75. Forced worker termination does not fabricate job success.
76. Worker deployment preserves queued jobs.
77. Worker rollback does not delete queued jobs.
78. Old and new workers may coexist during controlled rollout.
79. Job schema compatibility is maintained during rollout.
80. Database schema compatibility is maintained during rollout.
81. Queue compatibility is maintained during rollout.
82. Breaking job contract changes require explicit versioning or migration.
83. Workers do not silently reinterpret incompatible queued jobs.
84. Worker artifacts are reproducible.
85. Worker release identity is traceable.
86. Worker dependencies are controlled.
87. Production worker secrets are injected securely.
88. Worker secrets are not embedded in job payloads.
89. Worker secrets are not written to logs.
90. Full job payloads are not logged by default.
91. Worker access follows least privilege.
92. Workers do not run as root under normal operation.
93. Worker network access is restricted to required services.
94. Critical worker capacity remains available during heavy workload.
95. Synchronization worker concurrency can be throttled.
96. Report worker concurrency can be throttled.
97. Heavy worker concurrency can be throttled.
98. Optional work can be paused during resource pressure.
99. Database load from workers is observable.
100. Worker database connections are bounded.
101. Worker lock duration is controlled where applicable.
102. Worker transactions remain short where possible.
103. External provider calls do not unnecessarily hold database transactions.
104. External provider timeouts are bounded.
105. External provider retries are bounded.
106. External provider rate limits are respected.
107. Job execution time is observable.
108. Queue wait time is observable.
109. Enqueue latency is observable.
110. Retry rate is observable.
111. Dead-letter rate is observable.
112. Worker crash rate is observable.
113. Scheduler crash rate is observable.
114. Critical queue dispatch target is ≤ 5 seconds under normal load.
115. Critical notification processing target is ≤ 10 seconds under normal load.
116. Normal notification processing target is ≤ 60 seconds under normal load.
117. Normal synchronization batch target is ≤ 1 second p95.
118. Job enqueue target is ≤ 100 ms p95.
119. Job status retrieval target is ≤ 200 ms p95.
120. Worker service availability target is ≥ 99.9% monthly.
121. Scheduler creation latency target is ≤ 60 seconds p95 under normal load.
122. Worker SLOs are measured rather than assumed.
123. Queue age breaches are observable.
124. Critical queue SLO breaches trigger alerting.
125. Scheduler SLO breaches trigger alerting.
126. Worker resource exhaustion triggers alerting.
127. Worker deployment health is verified before increasing workload.
128. Failed worker deployment does not replace the last known-good release.
129. Worker rollback remains possible where release compatibility allows.
130. Queue state remains durable across worker restart where required.
131. Job identity remains stable across retry.
132. Operation UUID remains stable across retry.
133. Retry does not create a new logical Business operation.
134. Partial batch processing does not falsely report the entire batch as successful.
135. Large jobs use bounded batching where appropriate.
136. Large jobs may use checkpointing where recovery requires it.
137. Checkpoint state is durable where necessary.
138. Job cleanup does not remove active or retryable jobs.
139. Dead-letter cleanup does not remove jobs still under investigation.
140. Job retention is bounded.
141. Scheduler retention is bounded.
142. Background processing respects subscription lifecycle rules.
143. Background processing cannot bypass READ_ONLY restrictions.
144. Data deletion jobs require valid lifecycle state.
145. Data deletion is bounded and recoverable.
146. Historical transactions are not reinterpreted using current configuration.
147. Historical financial snapshots remain authoritative.
148. Historical Recipe Versions remain authoritative.
149. Historical Set configurations remain authoritative.
150. Background workers preserve audit requirements.
151. Notification failure does not roll back committed core state.
152. Printer failure does not roll back committed core state.
153. Report failure does not roll back committed core state.
154. External integration failure does not automatically roll back committed core state.
155. Queue failure does not silently fabricate Business completion.
156. Redis failure does not bypass transactional correctness.
157. Redis is not a substitute for durable Business state.
158. Worker caches are non-authoritative.
159. Scheduler state is not a substitute for Business transaction state.
160. Worker deployment does not require manual recreation of Business data.
161. Worker host replacement does not require manual recreation of Business data.
162. Background processing does not become a hidden source of Business truth.
163. Critical work remains operationally distinguishable from heavy work.
164. Background queues remain observable by category.
165. Worker pools remain independently controllable where isolation is required.
166. Background resource pressure cannot silently disable security.
167. Background resource pressure cannot silently bypass Business isolation.
168. Background resource pressure cannot silently bypass Branch isolation.
169. Performance optimization does not remove idempotency.
170. Performance optimization does not remove retry safety.
171. Performance optimization does not remove audit requirements.
172. Performance optimization does not remove authorization.
173. Background worker architecture remains compatible with API deployment.
174. Background worker architecture remains compatible with Redis/queue architecture.
175. Background worker architecture remains compatible with offline synchronization.
176. Background worker architecture remains compatible with database migration strategy.
177. Background worker architecture remains compatible with future horizontal scaling.
178. Additional worker infrastructure is introduced only when measured need justifies it.
179. Simplicity is preferred when multiple worker deployment strategies provide equivalent correctness.
180. Correctness, security and historical integrity have priority over worker throughput.

---

# 184. Recommended Worker Structure

```text
backend/
├── app/
│   ├── background/
│   │   ├── jobs/
│   │   │   ├── notifications/
│   │   │   ├── printing/
│   │   │   ├── reports/
│   │   │   ├── synchronization/
│   │   │   ├── lifecycle/
│   │   │   ├── cleanup/
│   │   │   └── integrations/
│   │   │
│   │   ├── workers/
│   │   ├── scheduler/
│   │   ├── queues/
│   │   └── registry/
│   │
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   └── synchronization/
│
├── deployment/
│   ├── systemd/
│   │   ├── worker-critical.service
│   │   ├── worker-normal.service
│   │   ├── worker-sync.service
│   │   ├── worker-heavy.service
│   │   ├── worker-report.service
│   │   └── scheduler.service
│   │
│   └── config/
│
├── tests/
│   ├── background/
│   ├── scheduler/
│   ├── integration/
│   ├── resilience/
│   └── performance/
│
└── pyproject.toml
```

Exact implementation names may change without changing the architectural responsibilities defined by this document.

---

# 185. Recommended Initial Runtime

Small deployment:

```text
Application Host
├── Backend API
├── Critical Worker
├── Normal Worker
├── Heavy Worker
└── Scheduler
```

As workload increases:

```text
API Host
└── Backend API

Worker Host
├── Critical Worker
├── Normal Worker
└── Synchronization Worker

Heavy Worker Host
├── Report Worker
├── XLSX Worker
└── Heavy Processing
```

The deployment should remain on the simpler topology until measured workload justifies separation.

---

# 186. Operational Checklist

Before enabling background processing in production:

```text
[ ] Worker artifact verified
[ ] Scheduler artifact/configuration verified
[ ] Required queues exist
[ ] Queue permissions verified
[ ] Database capacity verified
[ ] Worker concurrency configured
[ ] Retry limits configured
[ ] Backoff configured
[ ] Dead-letter handling configured
[ ] Health checks configured
[ ] Logging configured
[ ] Metrics configured
[ ] Alerts configured
[ ] Critical queue protected
[ ] Synchronization limits configured
[ ] Heavy worker limits configured
[ ] Report worker limits configured
[ ] Scheduler timezone verified
[ ] Missed-job policy verified
[ ] Rollback path verified
[ ] Failure recovery tested
```

---

# 187. Status

**Document Type:** Deployment Architecture

**Document ID:** `DEP-12`

**Document Status:** Proposed

**Version:** `1.0`

**Current Document:** `12_Background_Workers_and_Scheduler_Deployment.md`

**Previous Document:** `11_Frontend_Deployment_and_Static_Asset_Delivery.md`

**Next Document:** `13_AI_Runtime_and_Model_Service_Deployment.md`

---

# 188. Related Documents

### Architecture

* `docs/04_Architecture/01_Backend_Architecture.md`
* `docs/04_Architecture/03_Application_and_Use_Case_Layer.md`
* `docs/04_Architecture/07_Transaction_Management.md`
* `docs/04_Architecture/09_Events_Outbox_and_Domain_Integration.md`
* `docs/04_Architecture/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/12_Reporting_and_Export_Architecture.md`
* `docs/04_Architecture/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/17_Backend_Testing_and_Quality_Assurance_Architecture.md`
* `docs/04_Architecture/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/27_Database_Migrations_and_Change_Management.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### API

* `docs/09_API/17_API_Report_File_and_Notification_Endpoints.md`
* `docs/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/09_API/24_API_Performance_Observability_and_SLO.md`

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
* `docs/10_Deployment/10_Backend_API_Deployment_and_Runtime.md`
* `docs/10_Deployment/11_Frontend_Deployment_and_Static_Asset_Delivery.md`
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

---

# 189. Final Architecture Principle

Background workers exist to move non-immediate work away from latency-sensitive API processes.

The architecture is:

```text
API
 ↓
Durable Transaction / Outbox
 ↓
Queue
 ↓
Appropriate Worker Pool
 ↓
Processing
```

Scheduling is separate:

```text
Scheduler
 ↓
Due Job
 ↓
Queue
 ↓
Worker
```

The key rule is:

> Background processing may be delayed, retried, restarted, scaled or replaced, but it must never become an uncontrolled source of duplicate Business effects or authoritative Business state.

The runtime priorities remain:

**Correctness → Security → POS Protection → Critical Work → Controlled Throughput → Scalability → Operational Simplicity**

