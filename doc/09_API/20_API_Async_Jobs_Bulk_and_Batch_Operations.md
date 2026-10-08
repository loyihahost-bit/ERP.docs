# API Async Jobs, Bulk and Batch Operations

**Document ID:** API-20
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the API architecture for asynchronous jobs, bulk operations and batch processing in FastFood ERP.

The API must support operations that are:

* too large for a normal synchronous request;
* computationally expensive;
* long-running;
* suitable for background processing;
* naturally processable as bounded batches;
* capable of producing downloadable files;
* operationally safe to retry;
* unsuitable for blocking normal POS requests.

The architecture must preserve:

* Business isolation;
* Branch isolation;
* authorization;
* idempotency;
* historical integrity;
* transactional correctness;
* bounded resource usage;
* predictable client behavior.

---

# 2. Scope

This document covers:

* asynchronous API operations;
* Job resources;
* Job lifecycle;
* Job creation;
* Job status;
* Job results;
* Job cancellation;
* Job retry;
* Job expiration;
* bulk operations;
* batch operations;
* batch size limits;
* per-item results;
* partial success;
* transaction boundaries;
* idempotency;
* concurrency;
* queue interaction;
* worker interaction;
* progress reporting;
* rate limiting;
* backpressure;
* resource quotas;
* Business and Branch isolation;
* authorization;
* subscription restrictions;
* offline interaction boundaries;
* report generation;
* XLSX export;
* large file processing;
* notifications;
* cleanup;
* failure recovery;
* observability;
* performance;
* API invariants.

---

# 3. Architectural Position

The API asynchronous model follows:

```text
Client
   ↓
API Request
   ↓
Authentication
   ↓
Authorization
   ↓
Request Validation
   ↓
Application Use Case
   ↓
Create Job / Batch
   ↓
Commit Job State
   ↓
Queue
   ↓
Worker
   ↓
Application / Domain
   ↓
PostgreSQL / Storage
   ↓
Job Result
   ↓
Client Poll / Notification
```

The API request should return quickly when the operation is suitable for asynchronous processing.

---

# 4. Synchronous vs Asynchronous Decision

The API should remain synchronous when an operation:

* completes quickly;
* has bounded processing cost;
* does not require long-running external work;
* does not generate large files;
* does not process large datasets.

The API should use asynchronous processing when an operation:

* may exceed the normal API timeout;
* generates a large report;
* generates XLSX;
* processes a large file;
* performs a large bulk operation;
* performs extensive data reconciliation;
* requires heavy background computation;
* would unnecessarily consume POS request resources.

---

# 5. Core Principle

The API must not use asynchronous processing merely to hide inefficient implementation.

The preferred order is:

```text
Optimize Query / Transaction
        ↓
Bound Work
        ↓
Use Synchronous API if Appropriate
        ↓
Use Async Job when Work Remains Long-Running
```

---

# 6. Job Resource

An asynchronous operation creates a Job resource.

Example:

```json
{
  "job_id": "018f7e7c-...",
  "job_type": "REPORT_EXPORT",
  "status": "PENDING"
}
```

The Job UUID is separate from:

* Operation UUID;
* Batch UUID;
* Business UUID;
* Branch UUID;
* Resource UUID.

---

# 7. Job Endpoint

Generic status endpoint:

```http
GET /api/v1/jobs/{job_id}
```

The response must contain enough information for the client to determine:

* current state;
* progress;
* result availability;
* failure state;
* retry availability;
* cancellation availability.

---

# 8. Job Creation

An asynchronous endpoint normally returns:

```http
202 Accepted
```

Example:

```http
POST /api/v1/reports/{report_id}/exports
```

Response:

```json
{
  "job_id": "018f...",
  "status": "PENDING"
}
```

The request must not wait for the entire background operation.

---

# 9. Job Lifecycle

Initial lifecycle:

```text
PENDING
   ↓
QUEUED
   ↓
PROCESSING
   ↓
COMPLETED
```

Failure path:

```text
PROCESSING
   ↓
FAILED
```

Cancellation:

```text
PENDING / QUEUED
   ↓
CANCELLED
```

Expiration:

```text
COMPLETED
   ↓
EXPIRED
```

---

# 10. Job States

Supported states:

```text
PENDING
QUEUED
PROCESSING
COMPLETED
FAILED
CANCEL_REQUESTED
CANCELLED
EXPIRED
```

The exact internal worker states may be more detailed, but the public API should remain stable.

---

# 11. Job State Authority

Job state is authoritative on the server.

The client must not mark a Job as:

* completed;
* failed;
* cancelled;
* retried

without server confirmation.

---

# 12. Job Status Response

Example:

```json
{
  "job_id": "018f...",
  "job_type": "XLSX_EXPORT",
  "status": "PROCESSING",
  "progress": {
    "completed": 4200,
    "total": 10000,
    "percentage": 42
  }
}
```

Progress information is optional when exact progress cannot be calculated.

---

# 13. Progress Model

A Job may expose:

```text
completed
total
percentage
stage
```

Example stages:

```text
QUEUED
PREPARING
QUERYING
GENERATING
UPLOADING
FINALIZING
```

Progress must not be reported as exact when the worker cannot reliably calculate it.

---

# 14. Unknown Progress

For operations where total work is unknown:

```json
{
  "progress": {
    "percentage": null
  }
}
```

The API should use a clear state such as:

```text
PROCESSING
```

rather than inventing inaccurate percentages.

---

# 15. Job Result

Completed Jobs may expose:

* result resource;
* Report Version;
* File UUID;
* export UUID;
* bulk result;
* batch result.

Example:

```json
{
  "job_id": "018f...",
  "status": "COMPLETED",
  "result": {
    "file_id": "018f..."
  }
}
```

The result remains subject to authorization.

---

# 16. Job Error

Failed Jobs should provide a stable error representation.

Example:

```json
{
  "job_id": "018f...",
  "status": "FAILED",
  "error": {
    "code": "EXPORT_FAILED"
  }
}
```

Sensitive infrastructure details must not be exposed.

---

# 17. Job Error Classification

Failures should be classified as:

```text
VALIDATION_FAILURE
AUTHORIZATION_FAILURE
BUSINESS_RULE_FAILURE
CONFLICT
TEMPORARY_FAILURE
PERMANENT_FAILURE
DEPENDENCY_FAILURE
INTERNAL_FAILURE
```

The client should use stable error codes rather than implementation messages.

---

# 18. Job Retryability

A failed Job may be:

```text
RETRYABLE
NON_RETRYABLE
USER_ACTION_REQUIRED
```

The server determines retryability.

Clients must not automatically retry every failed Job.

---

# 19. Job Retry

Optional endpoint:

```http
POST /api/v1/jobs/{job_id}/retry
```

Retry must:

* verify authorization;
* verify Job state;
* verify retryability;
* preserve original Job history;
* create a new execution attempt or Job instance as defined by the contract;
* remain idempotent.

Retry must not silently erase the original failure.

---

# 20. Job Attempts

A Job may have execution attempts.

Example:

```text
Job
 ├── Attempt 1 → FAILED
 ├── Attempt 2 → FAILED
 └── Attempt 3 → COMPLETED
```

Attempt information may include:

* attempt number;
* start time;
* end time;
* failure code;
* worker metadata where appropriate.

Sensitive infrastructure details must remain internal.

---

# 21. Job Cancellation

Optional endpoint:

```http
POST /api/v1/jobs/{job_id}/cancel
```

Cancellation is best-effort.

A Job already committed to an irreversible operation may not be cancellable.

---

# 22. Cancellation States

Example:

```text
PROCESSING
   ↓
CANCEL_REQUESTED
   ↓
CANCELLED
```

or:

```text
CANCEL_REQUESTED
   ↓
COMPLETED
```

if the worker completes before cancellation takes effect.

The server must return the final authoritative state.

---

# 23. Cancellation and Transactions

Cancellation must not leave partial authoritative transactions in an invalid state.

Where an individual business operation is transactional:

```text
Validate
   ↓
Transaction
   ↓
Commit
```

The transaction remains atomic.

Cancellation cannot interrupt a committed transaction and rewrite it.

---

# 24. Job Expiration

Completed results may expire.

For example:

```text
COMPLETED
   ↓
EXPIRED
```

Expiration may apply to:

* temporary exports;
* generated files;
* intermediate processing artifacts.

Expiration of a Job result must not delete authoritative:

* Orders;
* Payments;
* Inventory Transactions;
* Audit Records;
* Report Versions.

---

# 25. Job Cleanup

Cleanup must be asynchronous.

The system must not perform large cleanup work inside normal API requests.

Cleanup should remove only data that is eligible under lifecycle rules.

---

# 26. Job Authorization

Every Job read or mutation must validate:

* authenticated actor;
* Business scope;
* Branch scope where applicable;
* permission;
* resource ownership;
* subscription state where applicable.

Knowing a Job UUID is not sufficient authorization.

---

# 27. Job Business Scope

Every Business-scoped Job must retain:

```text
Business UUID
```

Branch-specific Jobs must additionally retain:

```text
Branch UUID
```

This prevents cross-Business or cross-Branch Job access.

---

# 28. Job Actor Context

A Job may retain:

```text
Employee UUID
Device UUID
Request UUID
Operation UUID
Business UUID
Branch UUID
```

Only the minimum necessary context should be stored.

---

# 29. Job Context Immutability

Important context such as:

* Business;
* Branch;
* initiating actor;
* original operation

must remain attributable after Job execution.

Changing employee permissions later must not erase historical Job attribution.

---

# 30. Job and Subscription

A Job must respect current subscription policy.

Examples:

```text
ACTIVE
→ normal allowed operations

READ_ONLY
→ reports and exports may remain available where permitted
→ modifying jobs blocked

DELETION_ELIGIBLE
→ normal mutation jobs blocked

DELETING
→ normal jobs blocked

DELETED
→ normal jobs rejected
```

A queued Job must be revalidated when it starts if the operation is subscription-sensitive.

---

# 31. Queued Job and Subscription Expiry

Example:

```text
Job created while ACTIVE
        ↓
Business becomes READ_ONLY
        ↓
Worker starts
```

The worker must not automatically execute a prohibited mutation.

The Application layer revalidates the relevant authorization and subscription state.

---

# 32. Job and Authorization Changes

Authorization should be revalidated at execution time for security-sensitive operations.

A Job created by an authorized employee does not automatically guarantee that the operation remains authorized forever.

---

# 33. Job and Historical Integrity

A Job must never modify historical records merely because it is asynchronous.

For example:

```text
Current Price
≠
Historical Order Price
```

The same principle applies to:

* Recipes;
* Set configurations;
* Payments;
* Refunds;
* Inventory Transactions;
* Cash Sessions;
* Report Versions.

---

# 34. Bulk Operations

Bulk operations apply one logical operation to multiple resources.

Example:

```http
POST /api/v1/employees/bulk-update
```

Bulk operations must be:

* bounded;
* authorized;
* validated;
* auditable;
* idempotent where retryable;
* explicit about partial success.

---

# 35. Bulk vs Batch

The terms are distinct.

### Bulk

One business intent applies to multiple resources.

Example:

```text
Deactivate 20 employees.
```

### Batch

A transport container carries multiple independent operations.

Example:

```text
Operation A
Operation B
Operation C
```

A batch does not necessarily imply one business transaction.

---

# 36. Bulk Request Limits

Initial recommendation:

```text
Maximum bulk items = 100
```

The exact limit may vary by endpoint.

Large operations should use asynchronous processing.

---

# 37. Bulk Validation

Before processing a bulk request, the API validates:

* request structure;
* item count;
* duplicate IDs;
* resource scope;
* allowed operation;
* permission;
* subscription;
* payload size.

Business validation occurs per item where necessary.

---

# 38. Bulk Processing Result

Example:

```json
{
  "job_id": "018f...",
  "status": "PENDING",
  "total_items": 50
}
```

For small synchronous bulk operations, the API may return per-item results directly.

---

# 39. Bulk Partial Success

Bulk processing may result in:

```text
40 ACCEPTED
5 REJECTED
3 CONFLICT
2 TEMPORARY_FAILURE
```

The API must not claim complete success when only part of the request succeeded.

---

# 40. Bulk Item Result

Example:

```json
{
  "resource_id": "018f...",
  "status": "REJECTED",
  "error": {
    "code": "EMPLOYEE_INACTIVE"
  }
}
```

Each item must be independently identifiable.

---

# 41. Bulk Transaction Boundary

Bulk request ≠ one database transaction.

The Application layer determines whether:

* each item is independent;
* a subset must be atomic;
* the entire request must be atomic.

For large operations, independent bounded transactions are preferred where business rules allow.

---

# 42. Bulk Financial Operations

Bulk financial operations are highly restricted.

The system should generally avoid generic bulk:

* payments;
* refunds;
* cash corrections.

Where a financial bulk operation is genuinely required, each financial effect must retain independent:

* operation UUID;
* authorization;
* audit;
* idempotency;
* transaction boundary.

---

# 43. Bulk Inventory Operations

Bulk inventory operations may be supported for controlled administrative workflows.

Each item must validate:

* Business;
* Branch;
* Product;
* quantity;
* inventory state;
* permission;
* transaction identity.

A bulk inventory operation must never bypass negative-stock rules.

---

# 44. Bulk Employee Operations

Examples:

```text
Bulk employee activation
Bulk employee deactivation
Bulk Branch assignment
Bulk role assignment
```

Permission changes must still respect Manager authority and employee scope.

---

# 45. Bulk Menu Operations

Examples:

```text
Bulk Branch availability update
Bulk Product activation
Bulk category assignment
```

Important menu changes must remain versioned and auditable.

---

# 46. Bulk Configuration Operations

Bulk configuration changes must support optimistic concurrency.

If one item has become stale:

```text
Item A → ACCEPTED
Item B → STALE_VERSION
Item C → ACCEPTED
```

The API must not silently overwrite the stale item.

---

# 47. Bulk Result Retention

Bulk results should remain available long enough for the client to reconcile the operation.

Retention must be bounded according to operational requirements.

Authoritative Business records remain governed by their own lifecycle.

---

# 48. Batch API

A bounded batch endpoint may accept multiple operations.

Example:

```http
POST /api/v1/batch
```

The batch is a transport mechanism.

Each operation remains individually identifiable.

---

# 49. Batch Operation Identity

Each batch operation must have:

```text
operation_id
operation_type
payload
```

Optional:

```text
depends_on
client_sequence
```

---

# 50. Batch Result

Example:

```json
{
  "batch_id": "018f...",
  "results": [
    {
      "operation_id": "018f...",
      "status": "ACCEPTED"
    },
    {
      "operation_id": "018f...",
      "status": "CONFLICT"
    }
  ]
}
```

---

# 51. Batch Transaction Semantics

The API must explicitly document whether a batch is:

* independently processed;
* partially successful;
* atomic;
* asynchronous.

The default batch model is:

**independent bounded operations with per-item results.**

---

# 52. Atomic Batch

An atomic batch may be supported only when the complete operation set has a clear business requirement for atomicity.

Atomic batches must have:

* strict size limits;
* predictable transaction duration;
* bounded lock scope;
* rollback semantics.

Large atomic batches are discouraged.

---

# 53. Batch Dependencies

A batch may define dependencies:

```text
Operation A
   ↓
Operation B
   ↓
Operation C
```

The server must validate dependency order.

Dependency cycles are rejected.

---

# 54. Batch Dependency Failure

If:

```text
A → REJECTED
B depends on A
```

then B should normally become:

```text
DEPENDENCY_NOT_RESOLVED
```

unless the operation can be safely evaluated independently.

---

# 55. Batch Idempotency

Each state-changing operation must have its own operation identity.

The batch identity does not replace operation idempotency.

A duplicate batch submission must not duplicate accepted operations.

---

# 56. Batch Retry

When a batch partially fails, the client should retry only retryable operations where practical.

Example:

```text
Accepted
→ do not retry

Conflict
→ user/system reconciliation

Temporary Failure
→ retry

Permanent Rejection
→ do not retry automatically
```

---

# 57. Async Batch Processing

Large batches may become asynchronous.

Example:

```http
POST /api/v1/bulk/inventory-adjustments
```

Response:

```http
202 Accepted
```

with:

```json
{
  "job_id": "018f..."
}
```

The Job owns execution state.

---

# 58. Job and Batch Relationship

A Job may execute:

```text
one bulk request
```

or:

```text
one large batch
```

The relationship should be explicit:

```text
Job
 ↓
Batch
 ↓
Operations
```

The API should expose enough identifiers for support and reconciliation.

---

# 59. Queue Interaction

Async Jobs are placed into appropriate queues.

Example:

```text
API
 ↓
Job
 ↓
Queue
 ├── Critical
 ├── Normal
 └── Heavy
```

Queue topology is defined by backend worker architecture.

The API contract should not expose internal queue implementation details.

---

# 60. Queue Priority

Critical operational jobs must not be starved by large exports.

Examples:

```text
Critical:
Synchronization-related work
Security/lifecycle work

Normal:
Standard reports

Heavy:
Large XLSX exports
Large data processing
```

Exact classification is implementation-defined.

---

# 61. POS Protection

Async jobs must not consume unlimited resources required by:

* Order creation;
* Order acceptance;
* Payment;
* Cash Session;
* inventory transaction.

The API may reject or delay heavy jobs when system resource pressure is high.

---

# 62. Backpressure

Backpressure may be applied through:

* queue limits;
* concurrency limits;
* per-Business quotas;
* endpoint rate limits;
* job priority;
* retry delays.

The API should return a stable temporary error when work cannot safely be accepted.

---

# 63. Job Quotas

The system may enforce:

* maximum active Jobs per Business;
* maximum concurrent Jobs;
* maximum bulk items;
* maximum export size;
* maximum file size;
* maximum report duration.

Quotas should be configurable.

---

# 64. Fairness

One Business must not monopolize shared asynchronous infrastructure.

Resource allocation should consider:

```text
Business
Branch
Job Type
Priority
Current Load
```

The exact scheduling mechanism belongs to backend worker architecture.

---

# 65. Rate Limiting

Async creation endpoints should have rate limits.

Rate limits may apply to:

* report creation;
* exports;
* bulk operations;
* file processing;
* large synchronization;
* administrative jobs.

Repeated requests must not create unlimited Jobs.

---

# 66. Job Creation Idempotency

Creating an async Job for a retryable business operation should support idempotency.

Example:

```text
Request A
Idempotency-Key: X
        ↓
Job 123 created

Request B
Idempotency-Key: X
        ↓
Job 123 returned
```

The system must not create duplicate expensive Jobs.

---

# 67. Idempotency Scope

Idempotency should include enough context to prevent cross-scope collisions:

```text
Business
Actor where required
Operation Type
Idempotency Key
Payload Hash
```

The exact scope depends on endpoint semantics.

---

# 68. Conflicting Job Request

If the same idempotency key is reused with different input:

```text
409 Conflict
```

with a stable error code such as:

```text
IDEMPOTENCY_KEY_REUSE_CONFLICT
```

---

# 69. Job Concurrency

Two Jobs modifying the same resource must still respect domain concurrency rules.

Async execution does not remove:

* optimistic version checks;
* row locks;
* unique constraints;
* state transition rules.

---

# 70. Job Ordering

If two Jobs depend on ordering:

```text
Job A
  ↓
Job B
```

the Application layer or job orchestration mechanism must enforce the dependency.

The client must not assume queue order guarantees Business ordering.

---

# 71. Job Timeout

Every Job type must have a bounded execution timeout.

A timeout must produce:

```text
FAILED
```

or another defined terminal/retryable state.

A timed-out worker must not continue indefinitely in the background.

---

# 72. Job Heartbeat

Long-running Jobs may expose internal worker heartbeat mechanisms.

Heartbeat details do not need to be exposed publicly.

The public API should expose only stable Job state.

---

# 73. Stuck Job Detection

The worker infrastructure should detect Jobs that remain in `PROCESSING` beyond the expected execution window.

Recovery may:

* retry;
* mark failed;
* move to recovery state;
* require operational intervention.

A stuck Job must not remain indefinitely invisible.

---

# 74. Job Recovery

If a worker crashes:

```text
PROCESSING
   ↓
Worker Failure
   ↓
Recovery
   ↓
Retry or FAILED
```

Retry must preserve idempotency.

---

# 75. Job Result Atomicity

A Job must not report `COMPLETED` before its authoritative result is safely persisted.

For example, an XLSX export should not be reported complete until:

* file generated;
* file stored;
* metadata committed;
* authorization reference established.

---

# 76. File Generation

Large file generation should use:

```text
POST /api/v1/reports/{report_id}/exports
```

or an equivalent asynchronous endpoint.

The API returns a Job.

The generated file is accessed through the File API.

---

# 77. File Expiration

Generated temporary files may expire.

After expiration:

```text
EXPORT_EXPIRED
```

The user may request a new export if authorized.

Expiration does not delete the underlying Report Version.

---

# 78. Report Job

A report Job should retain:

```text
Report ID
Report Version ID where applicable
Business
Branch
Requested Period
Report Definition Version
Export Format
Actor
```

This preserves reproducibility and auditability.

---

# 79. Notification Jobs

Notifications should normally be generated asynchronously.

Example:

```text
Business Event
   ↓
Outbox
   ↓
Notification Job
   ↓
Notification Record
```

A notification failure must not rollback the originating transaction.

---

# 80. Large Data Processing

Large processing tasks must use bounded database reads.

Workers should avoid:

```text
SELECT entire dataset
↓
load everything into memory
```

Instead use:

* pagination;
* streaming where appropriate;
* bounded batches;
* database aggregation.

---

# 81. Bulk Processing Memory

Bulk processing must have bounded memory usage.

The worker should process:

```text
100 items
```

or another bounded chunk rather than loading an unbounded request into memory.

---

# 82. Bulk Validation Strategy

For large bulk operations:

```text
Request Validation
      ↓
Structural Validation
      ↓
Authorization
      ↓
Per-item Business Validation
      ↓
Processing
```

The API may reject the entire request early for structural errors.

Per-item business failures may be returned individually.

---

# 83. Bulk Duplicate Detection

The API must detect duplicate resource identifiers where the operation semantics prohibit duplicates.

Example:

```json
{
  "items": [
    {"employee_id": "A"},
    {"employee_id": "A"}
  ]
}
```

may return:

```text
DUPLICATE_BULK_ITEM
```

---

# 84. Bulk Scope Validation

Every item must be validated against the current Business and Branch scope.

The API must not assume that because the first item belongs to Branch A, every item belongs to Branch A.

---

# 85. Bulk Permission Evaluation

Bulk authorization may use an optimized shared permission context.

However, resource-specific scope and business rules must still be validated per item.

Authorization caching must not bypass Business/Branch isolation.

---

# 86. Bulk Partial Commit

When independent items are processed separately:

```text
Item 1 → COMMITTED
Item 2 → CONFLICT
Item 3 → COMMITTED
```

The committed items remain committed.

The failed items remain independently retryable where appropriate.

---

# 87. Bulk Rollback

If an atomic bulk operation fails:

```text
Transaction
   ↓
Validation / Processing
   ↓
Failure
   ↓
Rollback
```

No partial Business state should remain from the atomic group.

---

# 88. Async vs Bulk

These concepts may be combined but are not identical.

Examples:

```text
Small Bulk
→ synchronous

Large Bulk
→ asynchronous Job

Small Batch
→ synchronous

Large Batch
→ asynchronous Job
```

The decision depends on measured workload and endpoint limits.

---

# 89. Async API Polling

Clients may poll:

```http
GET /api/v1/jobs/{job_id}
```

Polling must be bounded.

The server may provide:

```http
Retry-After: 2
```

where appropriate.

Clients should use increasing polling intervals for long-running Jobs.

---

# 90. Push Notifications for Jobs

Future implementations may notify clients when Jobs complete.

Possible mechanisms:

* in-app notification;
* WebSocket;
* server-sent events;
* push notification.

These are optional delivery mechanisms.

The Job resource remains authoritative.

---

# 91. Job Result Download

A completed Job may provide:

```json
{
  "result": {
    "file_id": "018f..."
  }
}
```

The client must obtain the file through authorized File APIs.

Raw filesystem URLs must never be exposed.

---

# 92. Job Visibility

A user should only see Jobs they are authorized to see.

Visibility may be:

* Employee-specific;
* Business-wide;
* Branch-scoped;
* Owner/Super Admin operational scope.

The Job UUID itself does not grant access.

---

# 93. Job Audit

Important Job operations should be auditable:

* creation;
* cancellation;
* retry;
* manual recovery;
* conflict resolution;
* sensitive export;
* administrative execution.

Routine polling does not necessarily require a business audit event.

---

# 94. Job and API Logging

Logs should include:

```text
Request ID
Job ID
Operation UUID
Business UUID
Branch UUID
Actor UUID where applicable
Job Type
Status
Duration
```

Sensitive payloads must not be logged indiscriminately.

---

# 95. Job Observability

Metrics should include:

```text
job_created_count
job_completed_count
job_failed_count
job_cancelled_count
job_expired_count
job_retry_count
job_duration
job_queue_wait
job_active_count
bulk_item_count
bulk_failure_count
```

Metrics must avoid uncontrolled UUID cardinality.

---

# 96. Job Alerts

Operational alerts may trigger for:

* abnormal failure rate;
* queue backlog;
* excessive processing time;
* stuck Jobs;
* repeated retries;
* storage failure;
* export failures;
* resource quota exhaustion.

---

# 97. API Performance Targets

Initial targets:

| Operation                      |                  Target |
| ------------------------------ | ----------------------: |
| Async Job creation p95         |                ≤ 300 ms |
| Job status p95                 |                ≤ 200 ms |
| Job cancellation request p95   |                ≤ 300 ms |
| Job retry request p95          |                ≤ 300 ms |
| Small synchronous bulk p95     |                ≤ 500 ms |
| Batch submission p95           |                ≤ 500 ms |
| Large async batch creation p95 |                ≤ 300 ms |
| Job state propagation          | ≤ 5 s under normal load |

Long-running Job execution time is workload-specific.

---

# 98. Availability

The API Job subsystem should maintain:

**≥ 99.9% monthly availability**

Critical Business transactions remain protected even if optional asynchronous processing is degraded.

---

# 99. Async Failure Isolation

Failure of:

* report export;
* notification processing;
* file generation;
* non-critical analytics

must not rollback or block:

* Order creation;
* Order acceptance;
* Payment;
* Cash Session;
* inventory transaction.

---

# 100. Async and POS Performance

The asynchronous subsystem must protect POS latency.

Under resource pressure, the system should prefer:

```text
POS
  ↓
Financial Operations
  ↓
Inventory
  ↓
Synchronization
  ↓
Normal Jobs
  ↓
Heavy Jobs
```

The exact priority can be refined during deployment.

---

# 101. Async and Database Protection

Workers must use:

* bounded concurrency;
* bounded batch size;
* short transactions;
* connection pool limits;
* retry backoff;
* lock-aware processing.

Background work must not exhaust PostgreSQL connections.

---

# 102. Async and External Services

External APIs should normally be called from workers rather than core API transactions when business rules permit.

External calls must use:

* timeout;
* bounded retry;
* backoff;
* failure classification.

---

# 103. Job Retry and External Effects

If a Job interacts with an external service:

```text
Unknown external outcome
```

must be reconciled before blindly repeating a non-idempotent external operation.

External idempotency keys should be used where supported.

---

# 104. Async Job Security

Jobs must not:

* execute with expired authorization blindly;
* expose one Business's data to another;
* bypass subscription restrictions;
* trust client-provided Branch scope;
* expose internal storage paths;
* execute arbitrary user-supplied code.

---

# 105. Job Input Immutability

Once a Job is created, its business input should be immutable.

A user who wants a different input should create a new Job.

This improves:

* reproducibility;
* auditability;
* debugging;
* concurrency safety.

---

# 106. Job Definition Version

Where Job behavior depends on a report/configuration definition, the Job should retain the relevant version.

Example:

```text
Report Definition Version = 7
```

This allows the system to explain what logic produced the result.

---

# 107. Bulk Request Immutability

A submitted bulk request should retain its original input representation or sufficient canonical representation for:

* audit;
* retry;
* result reconstruction.

The system must not silently change submitted input.

---

# 108. Async Result Reproducibility

For authoritative reports and exports, the Job should identify:

* source state;
* Report Version;
* definition version;
* requested period;
* Business;
* Branch.

A regenerated result may become a new version where required.

---

# 109. Job and Report Versioning

A report Job must not modify an immutable Report Version.

If a new authoritative report result is required:

```text
New Report Version
```

is created according to report versioning rules.

---

# 110. Job and File Lifecycle

Job result files follow File lifecycle rules.

Deleting an expired export file must not delete:

* Report Version;
* source transactions;
* audit history.

---

# 111. Job and Subscription Expiration

If subscription expires while a report/export Job is queued:

* read/export rights must be revalidated;
* prohibited mutation Jobs must not execute;
* already committed historical report versions remain accessible according to permissions.

---

# 112. Async Job and Deleted Business

If the Business enters deletion lifecycle before Job execution:

```text
DELETION_ELIGIBLE
DELETING
DELETED
```

the Job must be stopped or rejected according to lifecycle policy.

The worker must not recreate Business state.

---

# 113. Job Cleanup and Deletion

Business deletion must account for:

* pending Jobs;
* queued Jobs;
* Job metadata;
* temporary files;
* export files;
* worker state.

Deletion must not leave uncontrolled references that could resurrect Business data.

---

# 114. Async Job API Endpoints

Generic endpoints:

```text
GET  /api/v1/jobs/{job_id}
POST /api/v1/jobs/{job_id}/cancel
POST /api/v1/jobs/{job_id}/retry
```

Endpoint availability depends on Job type and authorization.

---

# 115. Bulk Endpoint Examples

Examples:

```text
POST /api/v1/employees/bulk-update
POST /api/v1/menu/bulk-update
POST /api/v1/inventory/bulk-adjustments
POST /api/v1/configuration/bulk-update
```

These endpoints must follow endpoint-specific authorization and domain rules.

---

# 116. Batch Endpoint Examples

Examples:

```text
POST /api/v1/batch
POST /api/v1/sync/batches
```

Synchronization batches remain governed by:

`19_API_Offline_Synchronization_and_Reconciliation.md`

and must not be confused with general API batches.

---

# 117. General Batch vs Sync Batch

General batch:

```text
Online client
→ API batch
→ normal authenticated context
```

Synchronization batch:

```text
Offline/trusted device
→ synchronization context
→ offline authorization
→ reconciliation
```

They must remain separate contracts.

---

# 118. API Error Codes

Relevant error codes include:

```text
JOB_NOT_FOUND
JOB_ACCESS_DENIED
JOB_NOT_RETRYABLE
JOB_NOT_CANCELLABLE
JOB_ALREADY_COMPLETED
JOB_ALREADY_CANCELLED
JOB_EXPIRED
JOB_EXECUTION_TIMEOUT
JOB_QUOTA_EXCEEDED
JOB_RATE_LIMITED
JOB_DEPENDENCY_FAILED
JOB_RESULT_NOT_READY

BULK_REQUEST_TOO_LARGE
BULK_ITEM_INVALID
BULK_ITEM_NOT_FOUND
BULK_ITEM_SCOPE_DENIED
DUPLICATE_BULK_ITEM
BULK_PARTIAL_FAILURE

BATCH_TOO_LARGE
BATCH_OPERATION_INVALID
BATCH_DEPENDENCY_FAILED
DEPENDENCY_CYCLE
BATCH_PARTIAL_FAILURE

IDEMPOTENCY_KEY_REUSE_CONFLICT
SUBSCRIPTION_READ_ONLY
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
ACCESS_DENIED
SERVICE_UNAVAILABLE
```

Canonical HTTP mapping follows:

`09_API_Error_Handling_and_Error_Codes.md`

---

# 119. Testing Requirements

The async and bulk architecture must be tested through:

* Job creation;
* Job status;
* Job completion;
* Job failure;
* Job retry;
* Job cancellation;
* Job expiration;
* worker failure;
* queue failure;
* database failure;
* duplicate Job request;
* idempotency conflict;
* bulk partial success;
* bulk atomicity;
* batch partial success;
* dependency handling;
* dependency cycle;
* authorization;
* Business isolation;
* Branch isolation;
* subscription changes;
* resource quotas;
* rate limiting;
* POS protection;
* concurrency;
* recovery.

---

# 120. Load Testing

Load testing must include:

### Normal Load

Regular reports and small bulk requests.

### Heavy Load

Large exports and large bulk processing.

### Mixed Load

```text
POS
+
Payments
+
Synchronization
+
Reports
+
Large Jobs
```

### Failure Load

* worker crashes;
* Redis failure;
* PostgreSQL pressure;
* queue backlog;
* storage failure;
* external dependency timeout.

---

# 121. Recovery Testing

Recovery tests must verify:

* Jobs survive worker restart;
* duplicate requests do not create duplicate Jobs;
* failed Jobs remain traceable;
* retries preserve idempotency;
* partial bulk results remain available;
* committed Business transactions are not rolled back by secondary failures;
* temporary files are cleaned safely.

---

# 122. API Contract Testing

OpenAPI/contract tests must verify:

* `202 Accepted` for asynchronous creation where applicable;
* Job schema;
* status schema;
* result schema;
* error schema;
* pagination where applicable;
* cancellation behavior;
* retry behavior;
* bulk item result schema;
* batch result schema.

---

# 123. Security Testing

Security tests must verify:

* Job UUID enumeration protection;
* Business isolation;
* Branch isolation;
* permission enforcement;
* subscription enforcement;
* actor attribution;
* result access;
* file access;
* cancellation authorization;
* retry authorization;
* bulk scope validation.

---

# 124. Performance Testing

Performance tests must measure:

* Job creation latency;
* status lookup latency;
* queue wait;
* worker execution time;
* database load;
* connection pool utilization;
* memory usage;
* bulk throughput;
* batch throughput;
* POS latency under heavy async load.

---

# 125. Operational Controls

Authorized operators may need to:

* pause heavy queues;
* reduce worker concurrency;
* retry failed Jobs;
* cancel stuck Jobs;
* inspect queue backlog;
* inspect Job failures;
* inspect resource quotas.

Operational controls must be audited where they affect Business operations.

---

# 126. Job Data Retention

Job metadata retention must be bounded.

Retention depends on:

* operational troubleshooting;
* audit requirements;
* result lifecycle;
* security;
* storage cost.

Authoritative Business history follows its own lifecycle.

---

# 127. Job Result Retention

Temporary results such as exports may have shorter retention.

Example:

```text
Job metadata
→ longer retention

Temporary XLSX
→ shorter retention
```

Exact periods are operational configuration.

---

# 128. Async Architecture and Historical Integrity

The async subsystem is an execution mechanism.

It is never an alternative source of Business truth.

Authoritative state remains:

```text
PostgreSQL
+
Immutable History
+
Report Versions
+
Audit Records
```

---

# 129. Async Architecture Guardrails

The implementation must prohibit:

* unbounded Jobs;
* unbounded bulk requests;
* unbounded batches;
* unlimited retries;
* unlimited worker concurrency;
* one Business monopolizing queues;
* Job result used as financial authority;
* client-controlled Job completion;
* silent partial success;
* silent partial rollback;
* authorization bypass during worker execution;
* subscription bypass during worker execution;
* direct API-to-database mutation;
* external API calls inside long core transactions;
* uncontrolled memory growth.

---

# 130. System Invariants

The following invariants apply to Async Jobs, Bulk and Batch Operations:

1. Asynchronous processing does not change Business authority.
2. PostgreSQL remains authoritative.
3. Job state is server-authoritative.
4. Job UUID is distinct from resource UUID.
5. Job UUID is distinct from operation UUID.
6. Job UUID is distinct from batch UUID.
7. Async creation is bounded.
8. Job input is immutable after creation.
9. Job context remains attributable.
10. Job Business scope is immutable.
11. Job Branch scope is immutable where applicable.
12. Job authorization is enforced on read.
13. Job authorization is enforced on mutation.
14. Sensitive Job execution is revalidated where required.
15. Subscription state is revalidated for subscription-sensitive Jobs.
16. Deleted Business cannot be resurrected by a Job.
17. Queued mutation Jobs cannot bypass READ_ONLY state.
18. Job results are authorized before access.
19. Job completion requires authoritative result persistence.
20. Failed Jobs remain traceable.
21. Retry does not erase original Job history.
22. Retry uses idempotent execution.
23. Non-retryable Jobs are not blindly retried.
24. Job cancellation is best-effort unless explicitly guaranteed.
25. Cancellation cannot corrupt committed transactions.
26. Job expiration cannot delete authoritative Business history.
27. Job cleanup is bounded.
28. Job execution time is bounded.
29. Stuck Jobs are detectable.
30. Worker failure is recoverable.
31. Queue failure does not corrupt authoritative state.
32. Async failure does not rollback unrelated committed Business state.
33. Bulk requests are bounded.
34. Batch requests are bounded.
35. Bulk items are individually identifiable.
36. Batch operations are individually identifiable.
37. Bulk partial success is explicit.
38. Batch partial success is explicit.
39. Bulk failure does not imply success.
40. Batch failure does not imply success.
41. Batch transport does not automatically define transaction scope.
42. Bulk transport does not automatically define transaction scope.
43. Atomic bulk operations are explicitly defined.
44. Atomic batches are explicitly defined.
45. Large atomic transactions are discouraged.
46. Independent items may be committed independently.
47. Bulk duplicate items are detected where prohibited.
48. Bulk scope is validated per item.
49. Bulk authorization is validated per item where required.
50. Bulk permission optimization cannot bypass resource scope.
51. Financial bulk operations require stronger safeguards.
52. Bulk inventory cannot create negative stock.
53. Bulk configuration respects optimistic concurrency.
54. Bulk employee changes respect Manager authority.
55. Bulk menu changes remain auditable.
56. Every retryable state-changing operation has idempotency protection.
57. Reusing an idempotency key with different input returns conflict.
58. Duplicate Job creation does not create duplicate expensive work.
59. Duplicate batch submission does not duplicate Business effects.
60. Dependency order is validated.
61. Dependency cycles are rejected.
62. Missing dependencies are not silently ignored.
63. Dependent operations do not execute against invalid prerequisites.
64. Async queue order is not assumed to guarantee Business ordering.
65. Domain concurrency rules remain authoritative.
66. Optimistic version checks remain active.
67. Database constraints remain active.
68. Row locking remains available where required.
69. Async processing does not bypass Domain rules.
70. Async processing does not bypass authorization.
71. Async processing does not bypass subscription restrictions.
72. Async processing does not bypass Business isolation.
73. Async processing does not bypass Branch isolation.
74. POS operations have higher resource priority than heavy Jobs.
75. Background work cannot monopolize PostgreSQL connections.
76. Worker concurrency is bounded.
77. Queue concurrency is bounded.
78. Per-Business resource consumption may be limited.
79. Retry traffic is bounded.
80. Job creation is rate limited where required.
81. Bulk creation is rate limited where required.
82. Batch creation is rate limited where required.
83. Backpressure is supported.
84. Resource pressure can reduce optional background workload.
85. Resource pressure cannot disable mandatory security.
86. Resource pressure cannot disable transactional correctness.
87. Job status remains observable.
88. Queue wait remains observable.
89. Worker duration remains observable.
90. Bulk failure remains observable.
91. Batch failure remains observable.
92. Metrics avoid uncontrolled UUID cardinality.
93. Logs avoid secrets.
94. Job results do not expose internal filesystem paths.
95. File access remains authorization-controlled.
96. Export files remain subject to File lifecycle rules.
97. Report Versions remain immutable.
98. Job results cannot replace Report Version authority.
99. Job results cannot replace financial authority.
100. Job results cannot replace inventory authority.
101. Job results cannot replace audit authority.
102. Job results cannot replace historical transaction authority.
103. External dependency failure is isolated where possible.
104. External calls have bounded timeouts.
105. External retries are bounded.
106. Unknown external outcomes require reconciliation where necessary.
107. Notification failure does not rollback core state.
108. Printing failure does not rollback core state.
109. Report export failure does not rollback source transactions.
110. File generation does not block core transactions.
111. Large reports are asynchronous where required.
112. Large XLSX generation is asynchronous.
113. Large bulk operations are asynchronous where required.
114. Large batches are asynchronous where required.
115. Job progress is not fabricated.
116. Unknown progress may remain unspecified.
117. Client cannot mark a Job completed.
118. Client cannot mark a Job failed.
119. Client cannot mark a Job cancelled without server confirmation.
120. Job result access requires authorization.
121. Job cancellation requires authorization.
122. Job retry requires authorization.
123. Manual recovery requires appropriate operational permission.
124. Manual recovery is auditable where business impact exists.
125. Job input remains reproducible.
126. Job definition/version is retained where required.
127. Report Job source state is identifiable.
128. Export Job result is identifiable.
129. Temporary result expiration does not delete source data.
130. Job metadata retention is bounded.
131. Job result retention is bounded.
132. Business deletion accounts for pending Jobs.
133. Business deletion accounts for queued Jobs.
134. Business deletion accounts for Job result files.
135. Business deletion cannot leave a path to resurrect Business state.
136. API asynchronous creation remains within defined latency targets.
137. Job status remains within defined latency targets.
138. Small synchronous bulk remains within defined latency targets.
139. POS latency is protected under async load.
140. Database load is bounded under async load.
141. Worker memory is bounded.
142. Bulk memory usage is bounded.
143. Batch memory usage is bounded.
144. Queue backlog is bounded or actively controlled.
145. Async subsystem remains horizontally scalable.
146. Async subsystem remains compatible with backend worker architecture.
147. Async subsystem remains compatible with offline synchronization architecture.
148. Async subsystem remains compatible with report architecture.
149. Async subsystem remains compatible with file storage architecture.
150. Async subsystem remains compatible with notification architecture.
151. Async API contracts are versioned.
152. Breaking Job schema changes require explicit migration/versioning.
153. Public Job states remain stable.
154. Internal worker states do not leak as unstable API contracts.
155. API errors use stable error codes.
156. Partial results remain distinguishable from complete results.
157. A completed Job cannot silently become a different completed operation.
158. Retried execution remains traceable to the original Job.
159. Async execution preserves historical integrity.
160. Correctness has priority over background processing convenience.

---

# 131. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/16_Reports_and_Dashboards.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/12_Reporting_and_Export_Architecture.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/15_Backend_File_Storage_and_Document_Management.md`
* `docs/04_Architecture/06_Backend/20_Backend_Operations_and_Incident_Management_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/11_API_Pagination_Search_Filtering_and_Sorting.md`
* `docs/04_Architecture/09_API/12_API_CRUD_and_Command_Endpoint_Architecture.md`
* `docs/04_Architecture/09_API/17_API_Report_File_and_Notification_Endpoints.md`
* `docs/04_Architecture/09_API/18_API_Configuration_and_Subscription_Endpoints.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/21_API_Security_CORS_CSRF_and_Data_Protection.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

---

# 132. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `20_API_Async_Jobs_Bulk_and_Batch_Operations.md`

**Previous Document:** `19_API_Offline_Synchronization_and_Reconciliation.md`

**Next Document:** `21_API_Security_CORS_CSRF_and_Data_Protection.md`

---

## Final Principle

> Asynchronous processing must make large and long-running operations safe and manageable without changing Business authority. Jobs, bulk requests and batches must remain bounded, observable, retry-safe and authorization-aware while protecting POS performance and preserving transactional and historical integrity.

