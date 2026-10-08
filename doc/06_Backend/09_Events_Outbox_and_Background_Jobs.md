# Events, Outbox and Background Jobs

**Document ID:** BE-09
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/06_Backend/README.md`

---

## 1. Purpose

This document defines the backend architecture for:

* domain events;
* application events;
* transactional Outbox;
* event processing;
* background jobs;
* scheduled jobs;
* retries;
* dead-letter handling;
* asynchronous notifications;
* report generation;
* file exports;
* printing;
* synchronization-related background processing;
* recovery and operational monitoring.

The main goal is to keep core business transactions reliable while moving non-critical or expensive work outside the main request transaction.

---

## 2. Core Principle

The backend follows:

> Core business state is committed synchronously. Secondary work is processed asynchronously when it does not need to block the core transaction.

Examples of secondary work:

* notifications;
* printing;
* report generation;
* Excel export;
* email;
* background synchronization;
* cleanup;
* scheduled reports.

The system must never use background processing to hide the failure of a required core business operation.

---

# 3. Event Categories

FastFood ERP distinguishes:

```text
Domain Event
Application Event
Integration Event
Outbox Event
Background Job
Scheduled Job
```

These concepts have different responsibilities.

---

# 4. Domain Event

A Domain Event represents an important state change inside the domain.

Examples:

```text
OrderAccepted
PaymentCompleted
CashSessionClosed
InventoryAdjusted
RecipeApproved
ProductArchived
ConfigurationChanged
EmployeeDeactivated
```

Domain events describe something that happened.

They do not directly perform external actions.

---

# 5. Application Event

An Application Event represents a use-case-level event that may trigger application processing.

Examples:

```text
ReportGenerationRequested
NotificationRequested
PrintRequested
SynchronizationProcessingRequested
```

Application events may be generated after successful business operations.

---

# 6. Integration Event

An Integration Event is intended for communication outside the current application boundary.

The current FastFood ERP is a modular monolith, so integration events are not required for every internal module interaction.

They become more important if future external systems or services are introduced.

---

# 7. Outbox Event

An Outbox Event is a durable event record stored in the same PostgreSQL transaction as the business state change that caused it.

Example:

```text
Order Accepted
      ↓
Order State Updated
      +
Outbox Event Created
      ↓
COMMIT
```

Both changes succeed or fail together.

---

# 8. Why Outbox Is Required

Without an Outbox, the system could perform:

```text
Database Commit
      ↓
Application crashes
      ↓
Notification never sent
```

or:

```text
Send Notification
      ↓
Database Transaction Rolls Back
      ↓
Notification incorrectly claims success
```

The Outbox pattern avoids this inconsistency.

---

# 9. Transactional Outbox Principle

For operations that require asynchronous follow-up:

```text
Core State Change
+
Outbox Event
=
One Database Transaction
```

If the transaction commits:

```text
Core State → committed
Outbox Event → committed
```

If the transaction rolls back:

```text
Core State → rolled back
Outbox Event → rolled back
```

---

# 10. Outbox Is Not the Business State

The Outbox is not the authoritative representation of the business entity.

For example:

```text
orders
```

remains authoritative for Order state.

The Outbox only records work that must be processed because the Order changed.

---

# 11. PostgreSQL as Outbox Storage

Initially, Outbox events are stored in PostgreSQL.

The architecture does not require Kafka, RabbitMQ or another distributed broker for the initial modular monolith.

A separate broker may be introduced later if scale or integration requirements justify it.

---

# 12. Outbox Event Structure

An Outbox record should contain information similar to:

```text
event_id
event_type
aggregate_type
aggregate_id
business_id
branch_id
operation_id
payload
created_at
available_at
status
attempt_count
processed_at
last_error
```

Exact fields may evolve with implementation.

---

# 13. Event ID

Every Outbox Event must have a globally unique identifier.

The Event ID is normally a UUID.

It provides:

* event identity;
* processing traceability;
* duplicate detection;
* operational investigation.

---

# 14. Operation ID

Where an event originates from a business command, the Outbox should preserve the associated `operation_id`.

Example:

```text
POS Request
operation_id = O1

Order Accepted
       ↓
Outbox Event
operation_id = O1
```

This connects the asynchronous work with the original business operation.

---

# 15. Request ID

The originating `request_id` may also be stored when useful for tracing.

However, the Request ID identifies an individual API request, while the Operation ID identifies the logical business operation.

---

# 16. Business and Branch Context

Business and Branch context should be preserved for events that are tenant or branch scoped.

Examples:

```text
business_id
branch_id
employee_id
device_id
cash_session_id
```

Only context relevant to the event should be stored.

---

# 17. Event Payload

Event payload should contain the minimum information necessary for processing.

Avoid storing unnecessarily large payloads.

For example, a notification event may contain:

```json
{
  "notification_type": "LOW_STOCK",
  "product_id": "...",
  "branch_id": "..."
}
```

The worker may load current permitted data when appropriate.

---

# 18. Historical Event Payloads

If an asynchronous operation depends on historical values, the event must contain or reference an immutable snapshot.

The worker must not reinterpret historical business facts from mutable current configuration.

Example:

```text
Order Accepted
Price Snapshot = 30,000

Later Product Price = 35,000
```

A historical report or notification must not accidentally use 35,000 when the original operation requires 30,000.

---

# 19. Event Version

Events may include an event schema version.

Example:

```text
event_type = ORDER_ACCEPTED
event_version = 1
```

When payload structure changes incompatibly, a new event version should be introduced.

---

# 20. Event Status

An Outbox Event may use states such as:

```text
PENDING
PROCESSING
PROCESSED
RETRYING
FAILED
DEAD_LETTER
```

Exact states may be simplified in implementation.

The important requirement is that processing state remains observable and recoverable.

---

# 21. Event Availability

An event may contain an `available_at` timestamp.

This allows:

* delayed retry;
* scheduled processing;
* controlled backoff.

Workers should process events whose availability time has been reached.

---

# 22. Outbox Worker

The Outbox Worker is responsible for:

1. discovering pending events;
2. claiming work safely;
3. processing the event;
4. recording success or failure;
5. scheduling retries where appropriate;
6. moving permanently failing events to dead-letter state.

---

# 23. Event Claiming

Multiple workers may operate concurrently.

The system must prevent the same event from being processed simultaneously when the handler is not safely concurrent.

PostgreSQL row locking or an equivalent claiming mechanism may be used.

Example concept:

```text
Worker A → claims Event X
Worker B → cannot claim Event X
```

---

# 24. Worker Concurrency

Worker concurrency must be controlled.

The system should support multiple workers where useful without causing duplicate side effects.

Event handlers must therefore be idempotent whenever possible.

---

# 25. At-Least-Once Processing

The Outbox system should assume:

> Events may be delivered to handlers more than once.

Exactly-once execution cannot be assumed merely because an event exists in the Outbox.

Handlers must therefore be designed for idempotent or duplicate-safe processing.

---

# 26. Duplicate Event Processing

Example:

```text
Event X
  ↓
Worker processes
  ↓
External action succeeds
  ↓
Worker crashes before marking PROCESSED
  ↓
Event X processed again
```

The second attempt must not create an unintended duplicate business effect.

---

# 27. Handler Idempotency

Where duplicate processing is possible, handlers should use:

* event ID;
* operation ID;
* idempotency record;
* unique constraints;
* deterministic state transitions.

The exact mechanism depends on the event type.

---

# 28. Notification Idempotency

Notification handlers should prevent duplicate notifications where the business requirement requires uniqueness.

Example:

```text
notification_key =
BUSINESS + EVENT_TYPE + REFERENCE_ID
```

The exact key may vary.

---

# 29. Print Job Idempotency

Printing requires special consideration because printers may not support transactional behavior.

A print job should have a stable identifier.

Example:

```text
print_job_id = UUID
```

Retrying the job must not accidentally create uncontrolled duplicate printing.

Where printer-level deduplication is impossible, the system should expose print-job state clearly.

---

# 30. Report Job Idempotency

Report generation should be linked to a stable report request/version identity.

Repeated worker execution must not create multiple authoritative report versions for the same logical generation request unless explicitly intended.

---

# 31. Export Job Idempotency

XLSX export jobs should have a stable export request ID.

Repeated processing should either:

* return the already generated export;
* regenerate safely into the same logical result;
* or create a clearly distinct export when requested.

---

# 32. Background Job

A Background Job is executable asynchronous work.

Examples:

```text
GenerateMonthlyReport
GenerateExcelExport
SendNotification
ProcessPrintJob
ProcessSynchronizationBatch
CleanupExpiredData
RebuildDerivedData
```

Jobs may be created by Outbox events or directly by a scheduler where no transactional business event is required.

---

# 33. Event vs Job

The distinction is:

### Event

Describes something that happened.

```text
OrderAccepted
```

### Job

Describes work that must be performed.

```text
PrintKitchenReceipt
```

An event may create one or more jobs.

---

# 34. Job Queue

The initial implementation may use PostgreSQL-backed job coordination.

A dedicated message broker is not required unless workload or reliability requirements justify it.

The abstraction should allow a future queue implementation without changing business logic.

---

# 35. Job Structure

A job should contain:

```text
job_id
job_type
operation_id
business_id
branch_id
payload
status
attempt_count
available_at
created_at
started_at
completed_at
last_error
```

---

# 36. Job States

Recommended states:

```text
PENDING
RUNNING
SUCCEEDED
RETRYING
FAILED
DEAD_LETTER
CANCELLED
```

Not every job type must use every state.

---

# 37. Job Retry Policy

Retry behavior depends on failure classification.

### Retry

Temporary infrastructure failure.

### Do Not Retry

Invalid business data.

### Reconcile

Conflict requiring human/system decision.

### Dead Letter

Permanent failure after bounded retries.

---

# 38. Retry Backoff

Retries should not happen in a tight loop.

A controlled backoff should be used.

Conceptually:

```text
Attempt 1 → short delay
Attempt 2 → longer delay
Attempt 3 → longer delay
...
```

The exact backoff policy depends on job type.

---

# 39. Maximum Retry Count

Every retryable job must have a bounded retry policy.

A job must not retry forever.

Maximum attempts may vary by:

* notification;
* print;
* report;
* synchronization;
* infrastructure operation.

---

# 40. Dead-Letter Queue

Jobs that cannot succeed after the allowed retry policy should enter a dead-letter state.

Dead-letter records should preserve:

* job ID;
* event ID;
* operation ID;
* error code;
* last error;
* attempt count;
* timestamps;
* Business/Branch context.

---

# 41. Dead-Letter Recovery

Authorized operational tools may:

* retry;
* cancel;
* inspect;
* reconcile.

Recovery must not silently modify the original business transaction.

---

# 42. Scheduled Jobs

Scheduled jobs execute based on time or calendar rules.

Examples:

* monthly report generation;
* subscription expiration checks;
* lifecycle notifications;
* 60-day deletion processing;
* cleanup;
* retry processing;
* synchronization maintenance.

---

# 43. Scheduled Job Idempotency

Scheduled jobs must be safe when executed more than once.

Example:

```text
Monthly report for:
Business X
Period:
2026-09
```

The scheduler must not accidentally generate uncontrolled duplicate authoritative report versions.

---

# 44. Monthly Reports

Monthly automatic reports have a defined business rule:

> Generate the report on the last calendar day after the required operational data is available.

The scheduler must determine the correct calendar period.

A scheduled job must not assume that server restart means the report period was skipped permanently.

---

# 45. Missed Scheduled Jobs

If the application is unavailable during the scheduled time:

```text
Scheduled Time
     ↓
Application Offline
     ↓
Application Restarts
     ↓
Scheduler Detects Missed Job
     ↓
Safe Execution
```

The job must be idempotent.

---

# 46. Subscription Jobs

Background jobs may handle:

* expiry notifications;
* subscription state transition;
* read-only transition;
* 60-day deletion eligibility;
* deletion preparation.

Lifecycle changes must still follow the authoritative lifecycle rules.

---

# 47. Subscription Expiry

When a subscription expires:

```text
Business
   ↓
READ_ONLY
```

The state transition itself must be authoritative.

Notification delivery should be asynchronous.

Notification failure must not prevent the lifecycle transition.

---

# 48. Data Deletion Jobs

Business deletion after the configured retention period must be processed asynchronously.

The system must not attempt to delete a large Business dataset in one giant transaction.

Instead:

```text
DELETION_ELIGIBLE
       ↓
DELETING
       ↓
Batch Deletion
       ↓
Verification
       ↓
DELETED
```

---

# 49. Deletion Safety

Before deletion, the job must verify:

* Business lifecycle state;
* retention period;
* reactivation status;
* deletion cancellation conditions;
* authorization/system policy.

A reactivated Business must not be deleted because of a stale scheduled job.

---

# 50. Synchronization Jobs

Background workers may process offline synchronization.

Example:

```text
Device
  ↓
Upload Batch
  ↓
Sync Ingestion
  ↓
Validate
  ↓
Idempotency
  ↓
Apply Transactions
  ↓
Return Results
```

Large synchronization work may continue asynchronously when appropriate.

---

# 51. Synchronization Priority

Transaction synchronization has priority over configuration synchronization.

Example:

```text
Offline Order
      ↓
Transaction Sync
      ↓
Configuration Sync
```

This protects historical transaction snapshots.

---

# 52. Background Jobs Must Respect Authorization Context

A background worker must not blindly execute client-supplied permissions.

The job must preserve and validate its intended context.

For system-generated jobs, an explicit system identity should be used.

---

# 53. System Identity

Background jobs may execute as a system actor.

The system actor should be explicit.

Example:

```text
actor_type = SYSTEM
actor_id = REPORT_SCHEDULER
```

This distinguishes automated actions from employee actions.

---

# 54. Employee Attribution

If a job originates from an employee operation, the original employee identity should remain traceable.

Example:

```text
Employee A
  ↓
Configuration Change
  ↓
Outbox Event
  ↓
Notification Worker
```

The notification worker does not become the original actor.

---

# 55. Audit and Background Processing

Important automated state changes should be auditable.

Examples:

* automatic lifecycle transition;
* scheduled report creation;
* automatic deletion;
* background correction/reconciliation.

Audit should identify the system actor and originating operation where available.

---

# 56. Background Job Transactions

Each job execution should use its own short transaction where database state changes are required.

Do not keep one transaction open for the entire lifetime of a long-running job.

Example:

```text
Fetch Job
  ↓
Short Transaction
  ↓
Claim
  ↓
Commit
  ↓
Perform Work
  ↓
Short Transaction
  ↓
Save Result
  ↓
Commit
```

---

# 57. External Calls

Workers may call external systems, but external calls should not hold database transactions open unnecessarily.

Bad:

```text
BEGIN
  ↓
Call Email Provider
  ↓
Wait 10 seconds
  ↓
COMMIT
```

Preferred:

```text
BEGIN
  ↓
Claim Work
  ↓
COMMIT

Call External Provider

BEGIN
  ↓
Save Result
  ↓
COMMIT
```

---

# 58. Worker Crash Recovery

If a worker crashes while processing a job:

```text
Job = RUNNING
Worker crashes
      ↓
Recovery detects stale execution
      ↓
Job becomes retryable
```

The system must use a lease, heartbeat, timeout, or equivalent mechanism where required.

---

# 59. Stale Running Jobs

A job stuck in `RUNNING` must not remain there indefinitely.

Recovery should identify stale jobs based on execution metadata.

The recovery mechanism must be conservative to avoid running a non-idempotent job concurrently.

---

# 60. Event Ordering

Not all events require global ordering.

Ordering should be enforced only where business dependencies require it.

Example:

```text
Recipe Version Created
      ↓
Recipe Approved
      ↓
Menu Configuration Updated
```

If one event depends on another, the dependency must be represented explicitly.

---

# 61. Event Dependency

Jobs may contain dependency references.

Example:

```text
Job A
  ↓
Recipe Approval

Job B
  ↓
Menu Activation
```

Job B must not execute before the required state from Job A is available.

---

# 62. Event Ordering and Offline Sync

Offline operations may arrive later than online configuration changes.

The server must validate business ordering rather than trusting client timestamps alone.

Client timestamps are evidence/context, not authoritative ordering for important state.

---

# 63. Event Payload Security

Event payloads must not contain unnecessary sensitive data.

Do not place:

* passwords;
* access tokens;
* private keys;
* unnecessary personal information.

If sensitive data is required, use a secure reference to authoritative storage.

---

# 64. Event Payload Size

Payloads should remain small.

Large reports, images and files should not be embedded directly into Outbox rows.

Store them in appropriate storage and place a reference in the event.

---

# 65. Event Serialization

Event payloads should use a stable serialization format.

JSON is acceptable for the initial implementation.

Payloads should be versioned where compatibility is important.

---

# 66. Event Schema Evolution

When an event changes:

### Compatible Change

Adding optional data may remain in the same version if all consumers remain compatible.

### Incompatible Change

Create a new event version.

Old workers should not receive payloads they cannot understand.

---

# 67. Event Retention

Outbox records should not grow indefinitely.

After successful processing, records may be retained according to operational and audit requirements.

The system must distinguish:

* operational processing history;
* business audit history.

Outbox cleanup must not delete required audit/history records.

---

# 68. Outbox Cleanup

Cleanup should run asynchronously.

It should remove or archive only records that:

* are successfully processed;
* are older than the configured retention period;
* are not required for active recovery;
* are not required by operational policy.

---

# 69. Failed Event Retention

Failed and dead-letter events should generally be retained longer than successfully processed operational events.

This allows investigation and recovery.

---

# 70. Event Monitoring

The system should monitor:

* pending event count;
* processing latency;
* retry count;
* failed events;
* dead-letter events;
* oldest pending event;
* worker health.

---

# 71. Job Monitoring

The system should monitor:

* pending jobs;
* running jobs;
* failed jobs;
* retrying jobs;
* dead-letter jobs;
* execution duration;
* queue latency;
* worker availability.

---

# 72. Operational Alerts

Alerts may be generated for:

* large pending queue;
* rapidly increasing failures;
* dead-letter growth;
* stale running jobs;
* synchronization backlog;
* report generation backlog;
* repeated infrastructure failures.

Alerts must be meaningful and avoid excessive noise.

---

# 73. Performance

Background processing must protect the POS path.

Heavy work should not run synchronously during:

* Order creation;
* Order acceptance;
* payment;
* Cash Session opening;
* Cash Session closing;
* normal inventory operations.

---

# 74. POS Responsiveness

The following should normally be asynchronous:

* kitchen printing;
* notifications;
* email;
* report generation;
* Excel generation;
* non-critical audit exports;
* heavy synchronization processing.

Core transaction validation and persistence remain synchronous.

---

# 75. Background Worker Isolation

A worker failure must not bring down the main API process.

Workers should be independently restartable.

The architecture should allow:

```text
API Process
+
Worker Process
+
Scheduler Process
```

to be scaled or restarted independently when required.

---

# 76. Initial Deployment

The initial deployment may run:

```text
Gunicorn/API
Background Worker
Scheduler
PostgreSQL
```

on the same VPS if resource usage allows.

The architecture should not require separate infrastructure from day one.

---

# 77. Future Scaling

If workload increases, workers may be scaled independently.

Example:

```text
API × N
Worker × N
Scheduler × 1
PostgreSQL
Optional Queue
```

The business/domain/application layers should remain unchanged.

---

# 78. Scheduler Single-Execution

Scheduled jobs must avoid duplicate execution when multiple application instances exist.

The scheduler should use:

* database lock;
* distributed lock;
* unique scheduled-job record;
* or equivalent coordination.

Only one authoritative scheduler execution should create the logical scheduled job.

---

# 79. Job Deduplication

Jobs that represent the same logical work should use a deterministic uniqueness strategy when duplication is undesirable.

Example:

```text
Business
+
Report Type
+
Period
+
Job Type
```

may form a logical uniqueness key.

---

# 80. Event and Job Failure Policy

The system must distinguish:

```text
Business Failure
Technical Failure
Transient Failure
Permanent Failure
Conflict
```

Each category must have an explicit processing policy.

---

# 81. Event Handler Failure

If an event handler fails:

```text
Attempt
  ↓
Classify Error
  ├── Success → PROCESSED
  ├── Retryable → RETRYING
  ├── Permanent → FAILED
  └── Exhausted → DEAD_LETTER
```

The event must not disappear silently.

---

# 82. Event Processing Transaction

Where an event handler changes database state, the state update and handler processing result should be coordinated carefully.

A handler must not mark an event successfully processed before its required state change is durable.

---

# 83. Event Handler and Idempotent State

Preferred pattern:

```text
BEGIN
  ↓
Check event/idempotency
  ↓
Apply required state
  ↓
Record processing result
  ↓
COMMIT
```

This prevents duplicate execution after a worker crash.

---

# 84. Outbox and Outbox

An event handler may create another Outbox event.

Example:

```text
OrderAccepted
    ↓
NotificationRequested
    ↓
NotificationSent
```

If the second event is business-relevant, its creation must follow the same transactional Outbox rules.

---

# 85. Cascading Events

Cascading event chains must be controlled.

Avoid uncontrolled chains such as:

```text
Event A
 → Event B
   → Event C
     → Event D
       → ...
```

Each event should have a clear business purpose.

---

# 86. Event Loop Protection

The system must prevent accidental event loops.

Examples:

```text
ConfigurationChanged
 → SyncConfiguration
 → ConfigurationChanged
 → SyncConfiguration
 → ...
```

Idempotency and event-origin metadata should prevent such loops.

---

# 87. Background Work and Subscription Restrictions

Background jobs must respect Business lifecycle state.

A stale job must not:

* modify a READ_ONLY Business;
* resurrect a DELETED Business;
* bypass subscription restrictions;
* create new business operations after deletion.

System maintenance jobs are an exception only where explicitly defined by lifecycle policy.

---

# 88. Background Work and Branch Scope

Branch-scoped jobs must retain Branch identity.

A worker must never accidentally execute a Branch A job against Branch B.

Every branch-scoped job should validate:

```text
Business
+
Branch
+
Resource
```

before modifying state.

---

# 89. Background Work and Historical Integrity

Background processing must not rewrite historical transactions.

Examples:

* current Product price must not modify historical Order prices;
* current Recipe must not modify historical inventory deductions;
* current employee permissions must not change historical audit attribution.

---

# 90. Background Work and Reports

Report generation must use the appropriate report period and data snapshot/versioning rules.

A new report version is created only when business rules require a new authoritative version.

Background generation must not silently replace an immutable report version.

---

# 91. Background Work and Notifications

Notifications are secondary effects.

Example:

```text
Cash discrepancy detected
       ↓
Cash state committed
       ↓
Notification event created
       ↓
Worker sends notification
```

If notification delivery fails, the cash state remains committed.

---

# 92. Background Work and Printing

Printing is a secondary operation.

Example:

```text
Order Accepted
       ↓
Transaction Commit
       ↓
Print Job
       ↓
Kitchen Printer
```

Printer failure does not invalidate the Order.

---

# 93. Background Work and File Storage

File uploads and generated files may be processed asynchronously where practical.

The system must distinguish:

```text
Business State
File Metadata
Physical File
```

A missing physical file must not silently create a false successful state.

---

# 94. Background Work and Audit

Background jobs may create audit records when they perform important state-changing actions.

Audit records should identify:

* system actor;
* job ID;
* event ID;
* operation ID;
* Business;
* Branch;
* action;
* result;
* timestamp.

---

# 95. Recovery Principle

Recovery must be:

* explicit;
* idempotent;
* auditable;
* bounded;
* safe against duplicate execution.

Never repair production data by manually deleting event history.

---

# 96. Manual Retry

Authorized operators may retry failed jobs.

Manual retry must:

* preserve original job identity;
* create a retry attempt;
* retain failure history;
* avoid bypassing idempotency;
* respect current lifecycle and authorization rules.

---

# 97. Manual Reconciliation

Some failures cannot be solved by retry.

Examples:

* synchronization conflict;
* inconsistent external dependency result;
* ambiguous printer result;
* historical data discrepancy.

These require explicit reconciliation.

Reconciliation must create an auditable result rather than silently modifying history.

---

# 98. Testing Strategy

### Unit Tests

Test:

* event creation;
* event serialization;
* event classification;
* retry policy;
* idempotency;
* scheduler rules.

### Integration Tests

Test:

* transactional Outbox;
* worker claiming;
* concurrent workers;
* rollback behavior;
* retry;
* dead-letter transition;
* event handler transactions.

### Failure Tests

Test:

* worker crash;
* database outage;
* duplicate event;
* timeout after commit;
* external provider failure;
* stale running job.

---

# 99. Important Failure Scenario

Example:

```text
Order Accepted
    ↓
Inventory Deducted
    ↓
Outbox Event Created
    ↓
COMMIT
    ↓
API Response
    ↓
Worker Crash
```

After recovery:

```text
Outbox Event = PENDING
    ↓
Worker retries
    ↓
Notification / Print processed
```

The Order remains accepted throughout.

---

# 100. Important Rollback Scenario

Example:

```text
Order Acceptance
    ↓
Inventory Validation
    ↓
Failure
    ↓
ROLLBACK
```

Because the Outbox event was created in the same transaction:

```text
Order Change → Rolled Back
Inventory Change → Rolled Back
Outbox Event → Rolled Back
```

No asynchronous worker receives a false success event.

---

# 101. Important Duplicate Scenario

```text
Outbox Event
    ↓
Worker processes
    ↓
External operation succeeds
    ↓
Worker crashes
```

The event may be retried.

Therefore the handler must be duplicate-safe.

---

# 102. Architecture Summary

The backend follows:

```text
Core Business Operation
        ↓
Database Transaction
   ┌────┴────┐
   │         │
Business   Outbox
State      Event
   │         │
   └────┬────┘
        ↓
      COMMIT
        ↓
   Background Worker
        ↓
   Handler / Job
        ↓
 ┌──────┼────────┐
Success Retry  Failure
           ↓
      Dead Letter
```

This architecture provides reliable asynchronous processing without making the POS transaction dependent on secondary systems.

---

# 103. System Invariants

1. Core business state is authoritative in PostgreSQL.
2. Outbox events are stored transactionally with required core state changes.
3. Rolled-back business transactions do not produce committed Outbox events.
4. Outbox events have unique identifiers.
5. Retryable business operations preserve their operation UUID.
6. Event processing is assumed to be at-least-once.
7. Event handlers must be idempotent or duplicate-safe where required.
8. Duplicate event processing must not create unintended duplicate business effects.
9. Background jobs have bounded retry policies.
10. Failed jobs do not retry forever.
11. Permanent failures are not automatically retried indefinitely.
12. Dead-letter events remain recoverable.
13. Dead-letter recovery is auditable.
14. Background workers do not bypass authorization or lifecycle rules.
15. System-generated operations use explicit system identity.
16. Employee-originated operations remain attributable to the original employee.
17. Background jobs do not rewrite immutable historical transactions.
18. Printer failure does not roll back committed Orders.
19. Notification failure does not roll back committed business state.
20. Report generation failure does not corrupt report history.
21. File export failure does not corrupt operational state.
22. External calls do not unnecessarily hold database transactions open.
23. Long-running jobs do not hold one database transaction for their entire execution.
24. Stale running jobs are recoverable.
25. Scheduled jobs are idempotent.
26. Multiple scheduler instances cannot create duplicate authoritative scheduled work.
27. Event ordering is enforced only where business dependencies require it.
28. Client timestamps are not authoritative for important server-side ordering.
29. Event payloads do not contain unnecessary secrets.
30. Large files are not stored directly in Outbox payloads.
31. Event schemas are versioned when compatibility requires it.
32. Outbox cleanup does not delete required audit history.
33. Business and Branch scope are validated before background state changes.
34. Background jobs cannot resurrect deleted Businesses.
35. READ_ONLY Businesses cannot receive unauthorized modifying operations through workers.
36. Synchronization processing preserves transaction-before-configuration priority.
37. Event handlers must not create uncontrolled event loops.
38. Event processing failures remain observable.
39. Worker health and queue latency are monitorable.
40. Core POS operations remain independent from slow secondary processing.
41. Background processing must not become a hidden source of business-state inconsistency.
42. Recovery is explicit, bounded, idempotent and auditable.

---

# 104. Related Documents

### Backend

* `README.md`
* `01_Backend_Architecture.md`
* `02_Backend_Project_Structure.md`
* `03_Application_and_Use_Case_Layer.md`
* `04_Domain_Service_and_Business_Logic.md`
* `05_Repository_and_Data_Access.md`
* `06_Authentication_and_Authorization.md`
* `07_Transaction_Management.md`
* `08_Error_Handling_and_Exception_Architecture.md`
* `10_Notifications_and_External_Integrations.md`
* `23_Backend_Concurrency_and_Idempotency.md`
* `24_Backend_Invariants_and_Guardrails.md`

### Database

* `../05_Database/19_Notification_Data_Model.md`
* `../05_Database/20_Audit_and_History_Data_Model.md`
* `../05_Database/21_Report_and_Report_Version_Data_Model.md`
* `../05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `../05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `../05_Database/27_Database_Migrations_and_Change_Management.md`
* `../05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `../02_System_Analysis/16_Reports_and_Report_Versioning.md`
* `../02_System_Analysis/18_Notifications_and_Alerts.md`
* `../02_System_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `../02_System_Analysis/22_Audit_and_History.md`
* `../02_System_Analysis/23_Offline_Operation.md`
* `../02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `../02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `../02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`

---

# 105. Status

**Document ID:** BE-09

**Document Status:** Accepted

**Event Model:** Transactional Outbox

**Processing Model:** At-Least-Once

**Retry Model:** Bounded and Error-Classified

**Failure Recovery:** Retry + Dead Letter + Explicit Reconciliation

**Initial Storage:** PostgreSQL

**Initial Architecture:** Modular Monolith

**Core Principle:** Secondary work must not compromise core transaction integrity

**Next Document:** `10_Notifications_and_External_Integrations.md`

