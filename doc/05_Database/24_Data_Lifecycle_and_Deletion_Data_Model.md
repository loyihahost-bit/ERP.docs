# Data Lifecycle and Deletion Data Model

**Document ID:** DB-24
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

---

## 1. Purpose

This document defines the database model and persistence rules for Business data lifecycle, subscription expiry, read-only state, deletion eligibility, controlled deletion, reactivation and permanent data removal.

The model must preserve:

* tenant isolation;
* historical integrity;
* financial integrity;
* auditability;
* deletion safety;
* reactivation capability;
* offline synchronization safety;
* idempotent deletion;
* dependency-aware cleanup.

Data deletion must never be implemented as uncontrolled cascading deletion from the Business record.

---

## 2. Scope

This document covers:

* Business lifecycle;
* subscription expiry;
* read-only state;
* deletion eligibility;
* retention period;
* reactivation;
* deletion scheduling;
* deletion jobs;
* deletion batches;
* dependency ordering;
* soft deletion where required;
* permanent deletion;
* historical data;
* audit data;
* financial data;
* inventory data;
* employee data;
* device data;
* offline data;
* synchronization data;
* reports;
* notifications;
* configuration;
* backups;
* deletion failures;
* concurrency;
* idempotency;
* database constraints;
* indexing;
* security;
* recovery.

---

# 3. Lifecycle Ownership

The Business entity is the root of tenant data lifecycle.

Conceptual lifecycle:

```text
Active
   ↓
Expired / Read-Only
   ↓
Deletion Eligible
   ↓
Deleting
   ↓
Deleted
```

Reactivation is possible from:

```text
Expired / Read-Only
Deletion Eligible
```

provided deletion has not permanently removed the Business.

Once permanent deletion is completed:

```text
Deleted
```

is terminal.

---

# 4. Business as Lifecycle Root

The Business UUID is the primary tenant lifecycle identifier.

All tenant-owned records must be traceable to a Business either:

* directly through `business_id`; or
* indirectly through a parent entity whose ownership is unambiguous.

The Business UUID must never be reused.

A deleted Business must not be recreated using the same UUID.

---

# 5. Business Lifecycle Fields

The `businesses` table should contain lifecycle-related state such as:

```text
id
status
subscription_expired_at
deletion_eligible_at
deletion_started_at
deletion_completed_at
created_at
updated_at
```

Additional implementation metadata may be stored separately in lifecycle tables.

The Business table must not become a large storage container for deletion-job state.

---

# 6. Business Status

The authoritative Business lifecycle status may use:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

The exact internal enum representation may vary, but the semantic states must remain distinguishable.

---

# 7. Active State

An `ACTIVE` Business may perform all operations allowed by:

* subscription entitlement;
* employee permissions;
* branch scope;
* device trust;
* operational rules.

Normal database writes are allowed when all other business rules are satisfied.

---

# 8. Read-Only State

After subscription expiry, the Business enters a read-only operational state according to subscription rules.

Read-only means:

* existing data remains accessible;
* historical data remains accessible;
* reports remain accessible where permitted;
* allowed Excel exports remain available;
* modifying operations are blocked.

Read-only state must not physically delete or archive ordinary operational records.

---

# 9. Subscription Expiry Timestamp

The authoritative expiry timestamp is stored as:

```text
subscription_expired_at
```

The server uses this timestamp together with current subscription state.

Client-provided time must never determine Business lifecycle.

---

# 10. Retention Period

The Business remains recoverable for **60 days** after subscription expiry unless otherwise explicitly defined by the subscription lifecycle policy.

Conceptually:

```text
subscription_expired_at
        +
60 days
        =
deletion_eligible_at
```

The calculation must be deterministic.

---

# 11. Deletion Eligibility

A Business becomes deletion eligible only when:

1. subscription has expired;
2. the required retention period has elapsed;
3. the Business has not been reactivated;
4. the lifecycle state permits deletion.

Deletion eligibility does not mean immediate deletion.

A separate deletion process must perform the actual operation.

---

# 12. Reactivation

A Business may be reactivated before permanent deletion.

Reactivation:

* restores operational access according to the new subscription;
* does not create a new Business;
* does not create a new Business UUID;
* does not rewrite historical records;
* does not reset historical creation timestamps.

If reactivation occurs before deletion starts, the deletion process must be cancelled safely.

---

# 13. Reactivation During Deletion

If deletion has already started, reactivation must not race with deletion.

The system must acquire a lifecycle lock or equivalent concurrency control.

Possible outcomes:

```text
Deletion not started
    → Reactivation allowed

Deletion started
    → Reactivation rejected or requires administrative recovery

Deletion completed
    → Reactivation impossible
```

The system must never report successful reactivation while permanent deletion continues in the background.

---

# 14. Lifecycle History

Business lifecycle transitions should be recorded separately from the current Business status.

Recommended table:

```text
business_lifecycle_events
```

Suggested fields:

```text
id
business_id
from_status
to_status
reason
actor_type
actor_id
created_at
metadata
```

Lifecycle history is append-only.

---

# 15. Deletion Request

Deletion eligibility may create a deletion request or lifecycle record.

Recommended table:

```text
business_deletion_requests
```

Suggested fields:

```text
id
business_id
eligible_at
requested_at
scheduled_at
started_at
completed_at
cancelled_at
status
reason
created_at
updated_at
```

The table provides durable deletion orchestration state.

---

# 16. Deletion Request States

A deletion request may use:

```text
PENDING
SCHEDULED
RUNNING
PAUSED
CANCELLED
FAILED
COMPLETED
```

The exact implementation may simplify states, but running and completed states must remain distinguishable.

---

# 17. Deletion Job

Permanent deletion should be executed by a background job.

The job must:

* identify one Business;
* acquire lifecycle ownership;
* validate deletion eligibility;
* process dependencies;
* record progress;
* retry safely;
* remain idempotent.

Deletion must not run inside a single unbounded database transaction.

---

# 18. Deletion Job Identity

Every deletion execution should have a stable job UUID.

Recommended table:

```text
business_deletion_jobs
```

Suggested fields:

```text
id
business_id
deletion_request_id
status
started_at
completed_at
last_progress_at
attempt_count
current_phase
error_code
error_message
created_at
updated_at
```

---

# 19. Deletion Phases

Deletion should be divided into deterministic phases.

Example:

```text
1. Validate
2. Freeze
3. Invalidate Devices
4. Stop Offline Acceptance
5. Stop Synchronization
6. Remove Operational Data
7. Remove Secondary Data
8. Remove Lifecycle Data
9. Finalize
```

The exact number of phases may change during implementation.

---

# 20. Freeze Before Deletion

Before destructive deletion begins, the Business must enter:

```text
DELETING
```

This prevents new operational writes.

The server must reject:

* new Orders;
* Payments;
* Inventory Transactions;
* Attendance;
* Payroll changes;
* Configuration changes;
* Device registrations;
* synchronization writes.

Read operations may be blocked or restricted depending on the deletion phase.

---

# 21. Offline Device Invalidation

All trusted devices associated with the Business must be invalidated before permanent deletion.

The system must prevent an offline device from later submitting transactions for the deleted Business.

Offline authorization must therefore become invalid when the Business enters deletion.

---

# 22. Synchronization Freeze

Synchronization for the Business must be stopped before destructive deletion.

Pending synchronization events must not be allowed to create new Business data after deletion starts.

The sync system must reject events referencing:

* deleted Business;
* deleting Business;
* invalid lifecycle state.

---

# 23. Stale Offline Events

An offline event created before deletion may arrive after the Business becomes `DELETING`.

The server must reject the event if the lifecycle policy does not permit processing.

The event must not:

* recreate records;
* reopen the Business;
* recreate devices;
* recreate employees;
* restore Orders;
* restore Inventory.

The rejection should be recorded when appropriate.

---

# 24. Deletion and Historical Integrity

During normal operation, historical records must not be physically deleted merely because they are old.

Historical records remain available until Business-level deletion becomes authorized.

Deletion is a lifecycle operation, not a routine data cleanup mechanism.

---

# 25. Financial Data

Financial records include:

* Payments;
* Refunds;
* Debt;
* Debt Repayments;
* Cash Transactions;
* Cash Sessions;
* Corrections;
* Overpayments.

These records must remain internally consistent during deletion.

Partial deletion of financial data is prohibited.

---

# 26. Inventory Data

Inventory data includes:

* Warehouses;
* Inventory Balances;
* Inventory Transactions;
* Purchases;
* Purchase Items;
* Inventory Counts;
* Inventory Corrections;
* Recipe-based consumption;
* Production records.

Inventory deletion must not leave unrelated records referencing deleted inventory entities.

---

# 27. Order Data

Order deletion includes:

* Orders;
* Order Items;
* Order status history;
* Order modification history;
* Kitchen tickets;
* Cancellation records;
* Order financial snapshots;
* Table Visit references.

The deletion process must preserve referential integrity until each dependency is removed.

---

# 28. Employee Data

Employee-related data includes:

* Employees;
* Employee Branch assignments;
* Roles;
* Permission overrides;
* Attendance;
* Work Sessions;
* Payroll;
* Salary configuration;
* Payroll corrections.

Historical employee references must be removed or anonymized according to the deletion policy.

No deleted Business may retain active employee access.

---

# 29. Device Data

Device-related data includes:

* Devices;
* Trusted device state;
* Employee-device assignments;
* Authentication sessions;
* Offline authorizations;
* Device synchronization metadata.

Device trust must be invalidated before deletion.

---

# 30. Configuration Data

Business configuration includes:

* Menu;
* Pricing;
* Branch overrides;
* Recipe configuration;
* Set configuration;
* Printer configuration;
* Notification thresholds;
* Permission configuration;
* Subscription-related configuration.

Configuration versions must be deleted only as part of the controlled Business deletion process.

---

# 31. Report Data

Reports may contain materialized or snapshot data.

Deletion must remove Business-owned report data after the Business deletion process reaches the report phase.

A report must not independently keep the Business operationally alive.

---

# 32. Notification Data

Business notifications may include:

* subscription alerts;
* inventory alerts;
* cash alerts;
* payment alerts;
* payroll alerts;
* device/security alerts;
* synchronization alerts.

Notification records must not remain accessible after Business deletion.

---

# 33. Audit Data

Audit data contains sensitive historical information.

During the normal Business lifecycle, audit data is append-only and retained.

When the Business is permanently deleted, Business-owned audit data is removed according to the deletion policy.

Deletion itself should create a platform-level lifecycle event outside the deleted Business dataset where necessary to prove that deletion occurred.

---

# 34. Audit of Deletion

The deletion operation must be auditable.

The platform-level deletion record should identify:

* Business UUID;
* deletion request UUID;
* deletion job UUID;
* eligibility timestamp;
* deletion start timestamp;
* completion timestamp;
* executor;
* result;
* failure information if applicable.

The final deletion record must not depend solely on the deleted Business database rows.

---

# 35. Referential Dependency Order

Deletion must follow dependency order.

Conceptually:

```text
Business
  ├── Branch
  │    ├── Table
  │    ├── Cash
  │    ├── Inventory
  │    └── Attendance
  │
  ├── Employee
  ├── Product
  ├── Recipe
  ├── Set
  ├── Menu
  ├── Order
  ├── Payment
  ├── Configuration
  ├── Device
  ├── Report
  ├── Notification
  ├── Sync
  └── Audit
```

Actual deletion order must follow foreign-key dependencies rather than this conceptual ordering alone.

---

# 36. Foreign Key Strategy

Foreign keys must protect operational integrity during normal lifecycle states.

For Business-owned records, preferred behavior is:

```text
ON DELETE RESTRICT
```

or explicit application-controlled deletion.

Blind:

```text
ON DELETE CASCADE
```

from `businesses` must not be used for the complete tenant dataset.

---

# 37. Controlled Cascading

Cascading may be used inside tightly bounded dependent tables where:

* dependency is strictly owned;
* historical preservation is not required independently;
* deletion is part of a controlled phase;
* cascade cannot cross Business boundaries.

Example:

```text
Order
  └── OrderItem
```

may use controlled cascading if validated by the database design.

Business-level deletion must remain orchestrated.

---

# 38. Soft Deletion

Soft deletion may be used when an entity requires historical visibility during its normal lifecycle.

Examples:

* Product;
* Employee;
* Branch;
* Configuration;
* Device.

Soft deletion must not be treated as permanent Business deletion.

The final Business deletion process may physically remove those records.

---

# 39. Archive vs Deletion

Archive means:

```text
Entity remains in the database.
```

Deletion means:

```text
Entity is permanently removed according to lifecycle policy.
```

These concepts must not be mixed.

---

# 40. Business Reactivation After Read-Only

Reactivation from `READ_ONLY` must preserve:

* Business UUID;
* Branch UUIDs;
* Employee UUIDs;
* Product UUIDs;
* Order UUIDs;
* Payment UUIDs;
* Inventory Transaction UUIDs;
* configuration history;
* audit history.

No historical identity may be regenerated.

---

# 41. Reactivation After Deletion Eligibility

If the Business is `DELETION_ELIGIBLE` but deletion has not started, reactivation may return the Business to an operational state.

The deletion request must be cancelled atomically with reactivation.

---

# 42. Deletion Eligibility Recalculation

A background job may periodically identify Businesses whose retention period has elapsed.

The query must validate current lifecycle state and subscription status.

A stale deletion candidate must not be deleted if the Business was reactivated.

---

# 43. Deletion Candidate Query

Conceptually:

```sql
status = 'READ_ONLY'
AND deletion_eligible_at <= current_server_time
AND active_subscription = false
```

The actual query must also account for lifecycle locks and deletion state.

---

# 44. Server Time

Lifecycle decisions use server/database time.

Client clocks must not determine:

* expiry;
* deletion eligibility;
* deletion start;
* deletion completion.

This protects the lifecycle process from client clock manipulation.

---

# 45. Timezone

Business timezone may be retained for business-facing timestamps.

Retention calculations should use absolute timestamps.

The system must not accidentally extend or shorten the 60-day retention period because of timezone conversion.

---

# 46. Deletion Notifications

Before deletion, the system should notify eligible recipients according to notification policy.

Notifications may include:

* subscription expired;
* Business is read-only;
* deletion approaching;
* deletion eligible;
* deletion started;
* deletion completed.

Notification failure must not silently extend the retention period.

---

# 47. Notification Failure

Failure to deliver a notification must not:

* block deletion indefinitely;
* reset the retention period;
* reactivate the Business;
* create duplicate lifecycle transitions.

Notification delivery is secondary processing.

---

# 48. Export Before Deletion

Allowed data export does not reset or extend the deletion countdown.

For example:

```text
Subscription expires
        ↓
60-day retention begins
        ↓
User exports Excel
        ↓
Deletion deadline remains unchanged
```

---

# 49. Deletion and Reports

Report generation must stop creating new Business reports after deletion begins.

Existing report generation jobs must check lifecycle state before writing results.

A stale report job must not recreate deleted Business records.

---

# 50. Deletion and Background Jobs

All Business-scoped background jobs must validate lifecycle state before writing.

Examples:

* report generation;
* notification jobs;
* payroll calculation;
* synchronization;
* configuration activation;
* inventory processing.

Jobs targeting a deleted Business must terminate safely.

---

# 51. Deletion and Queue Messages

Queued messages containing Business context must be validated at processing time.

A message created before deletion may become invalid before processing.

The worker must not assume that queue insertion guarantees future execution.

---

# 52. Deletion and Outbox

Outbox events related to a deleting Business must be handled according to event lifecycle policy.

The system must prevent an outbox consumer from recreating operational state after deletion.

Business deletion must not depend on successful delivery of every historical secondary event.

---

# 53. Deletion and Cache

Business-related cache entries must be invalidated during deletion.

Examples:

```text
business:{business_id}:*
branch:{branch_id}:*
employee:{employee_id}:*
menu:{business_id}:*
permissions:{employee_id}:*
```

Cache is not authoritative and must never preserve access after deletion.

---

# 54. Deletion and Search Indexes

If external search or indexing exists, Business data must be removed from those indexes.

Search indexes must not be treated as authoritative storage.

---

# 55. Deletion and Files

Business-owned files may include:

* Product images;
* generated reports;
* exported files;
* configuration attachments.

File deletion must be coordinated with Business lifecycle.

Database deletion must not assume that filesystem deletion succeeded.

---

# 56. File Deletion State

If file storage is used, a cleanup table may track:

```text
file_cleanup_tasks
```

Suggested fields:

```text
id
business_id
object_key
status
attempt_count
last_error
created_at
completed_at
```

Cleanup must be idempotent.

---

# 57. Deletion and External Integrations

Current system scope does not require external financial or customer systems.

If future integrations exist, Business deletion must define whether external data is:

* deleted;
* disconnected;
* anonymized;
* retained under another legal owner.

External deletion must not be assumed to happen automatically because local database rows were deleted.

---

# 58. Deletion and Authentication

After deletion:

* all Business employee sessions become invalid;
* refresh tokens become invalid;
* device trust becomes invalid;
* offline authorization becomes invalid;
* Business-scoped API access is rejected.

Authentication must not bypass lifecycle state.

---

# 59. Deletion and Authorization

Authorization checks must include Business lifecycle state.

For example:

```text
DELETING → no operational writes
DELETED  → no Business access
```

A valid employee permission is insufficient when the Business lifecycle prohibits the operation.

---

# 60. Deletion and Subscription

Subscription reactivation must be coordinated with lifecycle state.

The system must not permit subscription renewal for a permanently deleted Business.

A renewal payment arriving after deletion must not recreate the Business automatically.

---

# 61. Late Payment

If a subscription payment arrives after deletion has started, the system must not silently restore the Business.

The payment must enter a controlled exception/reconciliation flow.

---

# 62. Deletion and Branches

All Business Branches become unavailable for normal operation when the Business enters `DELETING`.

Branch lifecycle data must not independently reactivate the Business.

Branch UUIDs remain globally unique until deletion is complete.

---

# 63. Deletion and Employees

Employee accounts belonging to the Business must lose access before destructive deletion.

Employee UUIDs must not be reused for another Business.

---

# 64. Deletion and Permissions

Business-specific permission configuration must be removed as part of Business deletion.

Global platform permission definitions may remain because they belong to the platform rather than the Business.

This distinction must be enforced through ownership.

---

# 65. Deletion and Subscription Plans

Subscription plans are platform-owned.

Deleting a Business must not delete:

* SubscriptionPlan;
* PlanVersion;
* Feature;
* global entitlement definitions.

Only Business-specific subscription records are deleted.

---

# 66. Deletion and Shared Reference Data

Reference data that is shared across Businesses must never be deleted as part of tenant deletion.

Examples may include:

* global currencies;
* system permission definitions;
* system feature definitions;
* platform-level plan definitions;
* system status definitions.

---

# 67. Business-Owned Reference Data

Business-specific reference data must be deleted with the Business where applicable.

Examples:

* Business categories;
* Business products;
* Business recipes;
* Business menu configuration;
* Business printer definitions.

---

# 68. Cross-Tenant Safety

A deletion query must always be constrained by Business ownership.

Example principle:

```text
DELETE ... WHERE business_id = :business_id
```

is preferred over deleting by a non-tenant identifier alone.

Deletion code must never accept arbitrary table-wide identifiers without tenant validation.

---

# 69. Composite Ownership Validation

Where a child has both:

```text
business_id
branch_id
```

the database should enforce that the Branch belongs to the same Business where practical.

This prevents accidental cross-tenant deletion.

---

# 70. Deletion Transaction Size

Deletion must avoid one enormous transaction for the entire Business.

Large transactions can cause:

* excessive locks;
* WAL growth;
* long blocking;
* replication pressure;
* memory pressure.

Deletion should process bounded batches.

---

# 71. Batch Deletion

Large tables should be deleted in bounded batches.

Conceptual:

```text
DELETE batch
↓
commit
↓
record progress
↓
next batch
```

Batch size must be configurable.

---

# 72. Deletion Ordering

A deletion phase may use:

```text
child records
    ↓
dependent records
    ↓
parent records
```

The database must remain internally consistent after each committed phase.

Intermediate deletion states must therefore be valid database states.

---

# 73. Progress Tracking

Deletion progress should be persisted.

Suggested fields:

```text
phase
last_processed_id
processed_count
failed_count
updated_at
```

This allows safe retry after process failure.

---

# 74. Idempotent Deletion

Running the same deletion phase more than once must not corrupt data.

For example:

```text
already deleted row
```

must not cause the whole Business deletion job to fail.

Deletion must tolerate partially completed previous attempts.

---

# 75. Deletion Retry

If a deletion phase fails:

1. record failure;
2. preserve lifecycle state;
3. retry according to policy;
4. continue from a safe checkpoint;
5. avoid reprocessing completed work unnecessarily.

---

# 76. Permanent Failure

If deletion cannot safely continue automatically, the Business remains in:

```text
DELETING
```

or:

```text
FAILED
```

depending on implementation.

It must not be marked `DELETED` before verification succeeds.

---

# 77. Deletion Completion

The Business may transition to:

```text
DELETED
```

only after required deletion phases have completed successfully.

Completion should be verified.

---

# 78. Completion Verification

Verification may check:

* no active employee access;
* no active device trust;
* no Business-owned operational rows;
* no Business-owned configuration rows;
* no Business-owned synchronization rows;
* no Business-owned report rows;
* no Business-owned notification rows;
* required file cleanup completed;
* required secondary indexes cleaned.

---

# 79. Post-Deletion Access

API requests containing the deleted Business UUID must return an appropriate not-found or lifecycle response.

The API must not reveal deleted Business information.

The system must not automatically recreate a missing Business because a valid UUID was supplied.

---

# 80. UUID Non-Reuse

Deleted Business UUIDs must never be reused.

The same rule applies to important child identities where historical references or external logs may exist.

---

# 81. Deletion and Backups

Database backups may contain data that existed before deletion.

Therefore:

```text
application deletion
```

and:

```text
backup expiration
```

are separate lifecycle processes.

A deleted Business must not automatically be restored from an old backup into production.

---

# 82. Backup Retention

Backup retention must be governed by the operational backup policy.

The deletion system must not silently rewrite historical backups.

If regulatory or contractual requirements require backup-level deletion, that must be handled by a separate controlled backup lifecycle process.

---

# 83. Restore Safety

When restoring a backup:

* deleted Businesses must not automatically become active;
* lifecycle state must be revalidated;
* subscription state must be checked;
* deletion records must be reconciled.

A restore operation must not bypass Business lifecycle rules.

---

# 84. Disaster Recovery

Disaster recovery may restore database state from an earlier point in time.

After restoration, lifecycle jobs must recalculate:

* expired subscriptions;
* deletion eligibility;
* deleting Businesses;
* completed deletion state.

The system must reconcile restored state against lifecycle policy.

---

# 85. Deletion and Auditability

Deletion must remain observable even if the Business's own audit rows are removed.

Therefore the platform should maintain a minimal platform-level deletion record such as:

```text
business_deletion_registry
```

Suggested fields:

```text
business_id
deletion_job_id
eligible_at
started_at
completed_at
status
result
created_at
```

This record must contain only the minimum information required for lifecycle accountability.

---

# 86. Deletion Registry

The deletion registry is platform-level metadata.

It must not contain:

* passwords;
* payment credentials;
* sensitive order contents;
* full employee information;
* unnecessary Business data.

Its purpose is to prove lifecycle execution, not preserve deleted tenant data.

---

# 87. Data Minimization

Deletion metadata should follow data minimization.

After Business deletion, the platform should retain only information required for:

* operational integrity;
* security;
* audit of deletion;
* legal/administrative requirements where applicable.

---

# 88. Privacy

Sensitive Business data must not remain in:

* logs;
* error messages;
* cache;
* temporary files;
* queues;
* worker memory beyond normal processing;
* generated exports.

Deletion must include secondary storage where applicable.

---

# 89. Application Logs

Application logs should not contain complete tenant datasets.

After Business deletion, ordinary logs should not allow reconstruction of deleted operational data.

Logs should contain identifiers and safe metadata rather than sensitive payloads.

---

# 90. Deletion and Metrics

Operational metrics may contain aggregate values associated with a Business.

If Business-identifying labels are used, retention must follow the observability policy.

High-cardinality Business identifiers should not be used unnecessarily.

---

# 91. Deletion and Error Monitoring

Error monitoring systems must avoid storing full Business-sensitive payloads.

Deletion of database rows does not necessarily delete third-party error-monitoring records.

The architecture must therefore minimize sensitive data sent to external monitoring.

---

# 92. Deletion and Export Files

Generated XLSX reports and exports must have lifecycle metadata.

When the Business is permanently deleted:

* Business-owned generated exports must be removed;
* temporary exports must expire;
* download links must become invalid.

---

# 93. Deletion and Object Storage

If object storage is used, object keys should contain Business context where practical.

Example:

```text
business/{business_uuid}/reports/{report_uuid}.xlsx
```

This simplifies controlled cleanup.

---

# 94. Deletion and Configuration Activation Jobs

Scheduled configuration jobs must check Business lifecycle before activation.

A scheduled price or menu configuration must never become effective after Business deletion.

---

# 95. Deletion and Payroll Jobs

Payroll calculation jobs must stop when the Business enters `DELETING`.

A payroll result must not be created for a deleting Business.

Already finalized payroll remains consistent until the deletion phase removes Business data.

---

# 96. Deletion and Inventory Jobs

Inventory background operations must validate Business lifecycle.

No inventory transaction may be created after deletion begins.

---

# 97. Deletion and Notification Jobs

Notification workers must stop creating new Business notifications after deletion begins.

Already queued notifications must be cancelled, expired or safely discarded.

---

# 98. Deletion and Sync Workers

Synchronization workers must reject:

```text
DELETING
DELETED
```

Business contexts.

A sync worker must never recreate a deleted child record.

---

# 99. Deletion and Configuration Cache

Cached effective configuration must be invalidated before or during deletion.

A stale configuration cache must never allow:

* Order creation;
* Payment;
* Inventory mutation;
* employee modification.

---

# 100. Deletion and Read Access

Read access during the deletion process should be controlled.

The Business may be:

```text
visible during READ_ONLY
restricted during DELETING
unavailable during DELETED
```

The exact UI behavior is an application-layer concern, but the database lifecycle state must be authoritative.

---

# 101. Lifecycle Concurrency

Lifecycle operations require concurrency control.

Potential races include:

* renewal vs deletion eligibility;
* reactivation vs deletion;
* deletion vs synchronization;
* deletion vs report generation;
* deletion vs configuration activation;
* deletion vs background jobs.

The database must prevent conflicting operations from silently succeeding.

---

# 102. Lifecycle Lock

A lifecycle lock may be implemented using:

* row-level locking;
* advisory locks;
* optimistic versioning;
* deletion-job ownership.

The selected mechanism must guarantee one authoritative lifecycle transition at a time.

---

# 103. Version Check

The Business row may contain:

```text
version
```

or equivalent optimistic concurrency metadata.

Lifecycle updates should verify the expected current state/version.

---

# 104. State Transition Validation

Invalid transitions must be rejected.

Examples:

```text
DELETED → ACTIVE
DELETED → READ_ONLY
DELETING → ACTIVE
```

must not occur through normal application operations.

---

# 105. Lifecycle Atomicity

The following transition should be atomic:

```text
READ_ONLY
    →
DELETION_ELIGIBLE
```

Likewise:

```text
DELETION_ELIGIBLE
    →
DELETING
```

must not leave the Business ambiguously in two states.

---

# 106. Reactivation Atomicity

Reactivation must atomically:

* update Business lifecycle state;
* update subscription state;
* cancel pending deletion when applicable;
* invalidate obsolete deletion work.

---

# 107. Deletion Job Ownership

Only one active deletion job may own a Business.

A uniqueness constraint should prevent:

```text
multiple RUNNING jobs
```

for the same Business.

---

# 108. Deletion Idempotency Key

Deletion requests and jobs should have stable UUIDs.

Repeated scheduler execution must not create duplicate deletion jobs for the same lifecycle state.

---

# 109. Scheduler Safety

The deletion scheduler must use a claim mechanism.

Conceptually:

```text
candidate
   ↓
claim
   ↓
lock
   ↓
run
```

Two workers must not process the same Business concurrently.

---

# 110. Database Constraints

Recommended constraints include:

```text
business.id UNIQUE

business_deletion_request.business_id UNIQUE
    WHERE active request exists

business_deletion_job.business_id UNIQUE
    WHERE status = RUNNING

deletion_eligible_at >= subscription_expired_at

deletion_completed_at >= deletion_started_at
```

Exact PostgreSQL implementation may use partial unique indexes and CHECK constraints.

---

# 111. Lifecycle Indexes

Recommended indexes:

```text
business(status)

business(deletion_eligible_at)

business(subscription_expired_at)

business_deletion_requests(status)

business_deletion_requests(scheduled_at)

business_deletion_jobs(status)

business_deletion_jobs(business_id)
```

Indexes must support scheduler and recovery queries without creating unnecessary write overhead.

---

# 112. Business-Scoped Indexes

Large Business-owned tables should have indexes beginning with `business_id` where appropriate.

Examples:

```text
(business_id, created_at)
(business_id, status)
(business_id, branch_id)
```

This supports:

* tenant isolation;
* reporting;
* lifecycle cleanup;
* administrative queries.

---

# 113. Deletion Query Strategy

Deletion queries must avoid unbounded scans where possible.

Preferred approach:

```text
WHERE business_id = :business_id
ORDER BY id
LIMIT :batch_size
```

or equivalent indexed keyset processing.

Offset-based deletion should be avoided for large tables.

---

# 114. Primary Key Processing

Stable primary keys should be used for deletion checkpoints.

Example:

```text
last_processed_id
```

This allows recovery after worker failure.

---

# 115. Large Tables

Potentially large tables include:

* Orders;
* Order Items;
* Inventory Transactions;
* Audit Events;
* Sync Events;
* Notifications;
* Attendance;
* Payments.

Deletion of these tables should use bounded batches.

---

# 116. Partitioning Compatibility

If large tables are partitioned in the future, Business deletion must remain compatible with partition strategy.

Partitioning must not weaken tenant isolation or deletion correctness.

---

# 117. Deletion and Foreign Keys

Foreign key dependencies must be documented.

Before deleting a parent table row, all dependent rows must either:

* be deleted;
* be reassigned under an explicitly allowed model;
* or prevent deletion.

Silent orphan creation is prohibited.

---

# 118. Orphan Detection

Periodic integrity checks may identify:

* Business-less Branches;
* Business-less Employees;
* orphaned Orders;
* orphaned Payments;
* orphaned Inventory Transactions;
* orphaned configuration versions;
* orphaned devices.

Any orphan created by a lifecycle bug must be treated as a data-integrity incident.

---

# 119. Deletion Validation Before Start

Before setting `DELETING`, the system should verify:

* subscription remains expired;
* retention period has elapsed;
* no valid reactivation exists;
* Business is not already deleted;
* no lifecycle conflict exists.

---

# 120. Deletion Validation During Execution

Each deletion phase must verify that it still owns the deletion job.

A stale worker must stop if:

* job ownership changed;
* lifecycle state changed unexpectedly;
* cancellation was authorized.

---

# 121. Cancellation of Deletion

Deletion may be cancelled before irreversible destructive phases where policy allows.

Cancellation must be audited.

After irreversible permanent deletion has begun, cancellation may no longer be possible.

---

# 122. Partial Deletion

A Business must never be marked `DELETED` after only partial deletion.

Partial deletion remains an operational failure state requiring recovery.

---

# 123. Recovery From Partial Deletion

Recovery options depend on the deletion phase.

Possible strategies:

* resume deletion;
* restore from backup;
* administrative reconciliation.

Automatic reactivation after arbitrary partial deletion is prohibited.

---

# 124. Data Restoration

If backup restoration is required after partial deletion, the restored Business must undergo lifecycle reconciliation before becoming accessible.

---

# 125. Deleted Business API Identity

A deleted Business UUID remains invalid permanently.

An API request using that UUID must not create a new tenant.

---

# 126. Deleted Child Identity

Deleted child UUIDs must not be reused.

This protects:

* audit references;
* external logs;
* sync records;
* debugging;
* historical identifiers.

---

# 127. Data Lifecycle Service Boundary

The application should expose a dedicated lifecycle service responsible for:

* expiry transition;
* deletion eligibility;
* reactivation coordination;
* deletion orchestration;
* lifecycle locking.

Other domains must not directly change Business lifecycle state.

---

# 128. Aggregate Ownership

The Business aggregate owns lifecycle state.

Other aggregates may respond to lifecycle events but must not independently declare the Business deleted.

---

# 129. Lifecycle Events

Conceptual events include:

```text
BusinessSubscriptionExpired
BusinessReadOnlyEntered
BusinessDeletionEligible
BusinessDeletionStarted
BusinessDeletionCompleted
BusinessDeletionFailed
BusinessReactivated
BusinessDeletionCancelled
```

These events are secondary integration mechanisms.

The database lifecycle state remains authoritative.

---

# 130. Event Reliability

Lifecycle events should use the established outbox mechanism.

Event delivery failure must not cause the database lifecycle transition to roll back unless the event is part of the core transaction requirement.

---

# 131. Historical Lifecycle Snapshot

Important lifecycle transitions should preserve:

* previous status;
* new status;
* actor/source;
* timestamp;
* reason;
* related subscription;
* deletion job if applicable.

---

# 132. Subscription Relation

Business lifecycle must reference subscription state but should not duplicate the entire subscription model.

The Subscription domain remains authoritative for entitlement.

The Data Lifecycle model consumes subscription lifecycle information.

---

# 133. Entitlement vs Lifecycle

These concepts remain separate:

```text
Entitlement
    = what the Business may use

Lifecycle
    = whether the Business still exists
```

A Business may be:

```text
ACTIVE + limited entitlement
```

or:

```text
READ_ONLY + no modifying entitlement
```

---

# 134. Deletion vs Archive

Subscription expiry must not archive every Business entity individually.

The Business lifecycle state is sufficient to block operations.

Entity-level archival remains a domain-specific concept.

---

# 135. Data Retention Configuration

The 60-day Business deletion retention is currently a system rule.

Implementation may store policy configuration at platform level, but individual Businesses must not arbitrarily change their own retention period.

---

# 136. Retention Policy Version

If retention policy changes in the future, the deletion request should preserve the policy version used to calculate eligibility.

Suggested field:

```text
retention_policy_version
```

This prevents historical deletion calculations from becoming ambiguous.

---

# 137. Eligibility Snapshot

When a Business becomes deletion eligible, the system may store:

```text
subscription_expired_at
deletion_eligible_at
retention_policy_version
```

This makes the eligibility decision reconstructable.

---

# 138. Deletion Reason

Deletion reason should use controlled values where possible.

Examples:

```text
SUBSCRIPTION_EXPIRED
ADMINISTRATIVE_DELETION
SECURITY_REQUIRED
DATA_RETENTION_EXPIRED
```

Administrative deletion must remain separately authorized.

---

# 139. Administrative Deletion

If a privileged platform operator can trigger deletion before normal subscription retention expires, it must be a separate authorization flow.

Normal subscription expiry must not grant administrative deletion authority.

---

# 140. Emergency Deletion

Emergency deletion for security/legal reasons may bypass ordinary waiting periods only through a dedicated privileged procedure.

It must be:

* strongly authorized;
* audited;
* reason-coded;
* irreversible after execution.

---

# 141. Business Owner Deletion Request

If Business owners can request deletion, the request must not immediately permanently delete data.

The request enters the controlled lifecycle process.

---

# 142. Deletion Confirmation

If user confirmation is required, it must be recorded.

Confirmation must not replace server-side lifecycle validation.

---

# 143. Deletion Access Control

Only authorized platform-level processes may transition:

```text
DELETION_ELIGIBLE → DELETING
```

Normal Business employees must not be able to execute the destructive operation.

---

# 144. Tenant Isolation During Deletion

Deletion of Business A must never affect:

```text
Business B
Business C
...
```

Shared platform data must remain intact.

---

# 145. Cross-Business Foreign Keys

If a table contains multiple Business-owned references, the database/application must ensure they belong to the same Business unless cross-Business references are explicitly allowed.

Cross-Business operational references are generally prohibited.

---

# 146. Deletion and Reporting Aggregates

Materialized report data must be deleted or invalidated with the Business.

Global aggregate metrics must not expose deleted Business-specific data unless the metric is intentionally anonymized and governed by policy.

---

# 147. Deletion and Cache Keys

All Business-specific cache keys must be discoverable or namespace-isolated.

A cache namespace should allow complete invalidation without scanning unrelated tenants.

---

# 148. Deletion and Rate Limits

Business-specific rate-limit or security state should be invalidated or expire naturally.

It must not preserve active authorization after deletion.

---

# 149. Deletion and Sessions

Application sessions must be invalidated.

The authentication layer should validate Business lifecycle on sensitive requests even if a session token has not yet expired.

---

# 150. Deletion and Refresh Tokens

Refresh tokens belonging to Business employees must become unusable after deletion.

Token revocation may use:

* Business lifecycle version;
* token version;
* session revocation;
* server-side lifecycle check.

---

# 151. Lifecycle Version

A Business lifecycle version may be useful for efficient invalidation.

Example:

```text
lifecycle_version
```

Changing this value can invalidate cached authorization/session state.

---

# 152. Database Transaction Boundary

A lifecycle state transition must be committed atomically with its required core metadata.

Secondary work must be handled asynchronously.

Example:

```text
Mark DELETING + create deletion job
```

is core.

Actual child-row deletion is background processing.

---

# 153. Deletion Job Transaction

Each deletion batch should be independently transactional.

A failed batch must roll back that batch without rolling back successfully completed previous batches.

---

# 154. Deletion Progress Consistency

Progress must be recorded only after the corresponding deletion batch has committed.

The system must not record:

```text
1000 rows deleted
```

before the transaction containing those deletions commits.

---

# 155. Deletion Metrics

Operational metrics may include:

* deletion jobs pending;
* deletion jobs running;
* deletion failures;
* rows processed;
* deletion duration;
* retry count;
* Businesses awaiting deletion.

Metrics must not expose sensitive tenant data.

---

# 156. Deletion Monitoring

The operations layer should alert when:

* deletion job remains stuck;
* deletion fails repeatedly;
* deletion exceeds expected duration;
* lifecycle state remains `DELETING` unusually long.

---

# 157. Stuck Deletion

A deletion job may be considered stuck if:

```text
current_time - last_progress_at
```

exceeds an operational threshold.

The threshold must be configurable.

---

# 158. Worker Crash

If a worker crashes during deletion:

* Business remains `DELETING`;
* completed batches remain committed;
* unfinished batch rolls back;
* a new worker may safely resume.

---

# 159. Database Restart

A database restart must not corrupt deletion state.

Committed deletion batches remain committed.

Uncommitted batches are rolled back by PostgreSQL.

---

# 160. Application Restart

Application restart must not lose deletion progress because progress is stored in the database.

---

# 161. Scheduler Restart

Scheduler restart must safely rediscover:

* eligible Businesses;
* scheduled deletion jobs;
* stale running jobs.

Duplicate execution must be prevented by locking/claiming.

---

# 162. Deletion Job Timeout

Long-running deletion jobs should have operational timeout or heartbeat rules.

A timeout must not automatically mark the Business deleted.

---

# 163. Heartbeat

A running deletion job may periodically update:

```text
last_progress_at
```

or equivalent heartbeat metadata.

This helps distinguish active jobs from abandoned workers.

---

# 164. Job Recovery

A recovery worker may reclaim a job only after verifying that the previous owner is no longer active.

Two active workers must never process the same Business concurrently.

---

# 165. Data Integrity Check

Before final completion, the system may execute integrity checks appropriate to the Business.

Examples:

* remaining Business-owned rows;
* active devices;
* pending sync;
* active sessions;
* orphan references.

---

# 166. Finalization Transaction

Finalization should atomically:

* verify deletion phases;
* set Business status to `DELETED`;
* set completion timestamp;
* finalize deletion job;
* create platform deletion registry record if required.

---

# 167. Finalization Safety

If verification fails, finalization must not occur.

The Business remains recoverable only according to the current deletion phase and recovery policy.

---

# 168. Data Lifecycle Security

Deletion operations are security-sensitive.

They require:

* least privilege;
* protected worker credentials;
* authorization;
* audit;
* restricted administrative access;
* safe error handling.

---

# 169. Database Role Separation

Application runtime roles should not automatically have unrestricted database-level destructive privileges if the deployment architecture permits separation.

Deletion workers may have only the permissions necessary to perform controlled lifecycle operations.

---

# 170. SQL Injection Protection

Deletion queries must use parameterized SQL/ORM operations.

Business UUIDs, batch sizes, table identifiers and other inputs must never be interpolated into raw SQL without validation.

---

# 171. Sensitive Error Handling

Deletion errors must not expose:

* database credentials;
* SQL statements containing secrets;
* sensitive tenant data;
* internal security details to end users.

Detailed errors remain in protected operational logs.

---

# 172. Deletion and Encryption

Encrypted Business data may require key lifecycle handling.

If tenant-specific encryption keys are introduced, deletion may require:

```text
data deletion
+
key destruction
```

according to the security architecture.

Key destruction must be separately audited.

---

# 173. Cryptographic Key Ownership

Platform-wide encryption keys must not be destroyed because one Business was deleted.

Tenant-specific key material, if used, must be scoped correctly.

---

# 174. Deletion and Secrets

Secrets such as:

* API credentials;
* integration tokens;
* printer credentials;
* device secrets

must be removed or revoked as part of Business deletion.

Secrets must not remain in configuration history unnecessarily.

---

# 175. Configuration History and Secrets

Configuration history should not preserve plaintext secrets indefinitely.

Secret values should be referenced through secure secret storage or redacted snapshots.

---

# 176. Deletion and Audit Snapshots

Audit snapshots may contain sensitive state.

They must follow the same Business lifecycle and deletion policy unless explicitly governed by a higher-level retention requirement.

---

# 177. Deletion and Correction History

Correction records are Business-owned historical data.

They must remain intact during normal operation and be deleted only during Business-level deletion.

---

# 178. Deletion and Immutable Records

Immutable does not mean permanently retained forever.

It means the record cannot be silently changed during its valid lifecycle.

Business-level permanent deletion remains a separate lifecycle operation.

---

# 179. Deletion and Historical Reports

Historical report versions are Business-owned.

They remain available during read-only retention.

They are deleted during permanent Business deletion.

---

# 180. Deletion and Export Audit

An export event occurring before deletion may remain in platform-level operational logs according to the audit policy.

The exported file itself must follow Business data lifecycle.

---

# 181. Deletion and Notification Read State

Notification recipient/read-state records are deleted together with their Business notification data.

---

# 182. Deletion and Device Assignment History

Historical EmployeeDevice assignment records are Business-owned.

They must not be used to grant access after Business deletion.

---

# 183. Deletion and Cash Sessions

Cash Sessions must be deleted only after dependent:

* Cash Transactions;
* Handover records;
* corrections;
* session reports

have been processed.

---

# 184. Deletion and Handover

Shift Handover records must be removed as part of Business deletion.

A handover record must not survive independently with references to a deleted Business.

---

# 185. Deletion and Open Orders

Before entering `DELETING`, no new Order may be created.

Existing open Orders remain immutable from the lifecycle perspective and are eventually deleted as part of the controlled Business deletion.

---

# 186. Deletion and Pending Payments

Pending payment operations must be stopped before destructive deletion.

A late payment response must not recreate a deleted Payment.

---

# 187. Deletion and Debt

Debt records are Business-owned financial data.

They must remain consistent during read-only retention and be deleted only as part of the Business deletion process.

---

# 188. Deletion and Inventory Reservations

If inventory reservation exists in a future implementation, reservations must be cleared before inventory parent records are removed.

---

# 189. Deletion and Recipe Dependencies

Recipe Versions referencing Products must be deleted in dependency order.

The system must not leave RecipeComponent rows referencing deleted Products.

---

# 190. Deletion and Set Dependencies

Set Components and Set Versions must be deleted before their parent Sets when foreign-key dependencies require it.

---

# 191. Deletion and Menu Dependencies

Branch Menu and pricing records must be removed before their parent Business Product configuration where required.

---

# 192. Deletion and Category Dependencies

Products referencing Business-owned Categories must be removed or detached before Categories are deleted.

---

# 193. Deletion and Warehouse Dependencies

Inventory Transactions and Balances must be removed before Warehouses if foreign-key dependencies require this order.

---

# 194. Deletion and Branch Dependencies

Branch-owned data must be removed before the Branch row is permanently deleted.

---

# 195. Deletion and Business Dependencies

The Business row itself must be one of the final records removed or transformed into a minimal deletion marker, depending on platform design.

The deletion registry must remain separate.

---

# 196. Deletion and Unique Constraints

Deleting Business data must release Business-scoped unique values.

However, globally unique identifiers must never be reused.

---

# 197. Business Codes

Business codes or slugs may become available for reuse only if the product policy explicitly permits it.

UUIDs remain non-reusable.

---

# 198. Deletion and Human-Readable Numbers

Customer-facing identifiers such as:

* order numbers;
* table numbers;
* employee codes

may be reused only according to their Business-scoped lifecycle.

They must not be confused with permanent UUID identity.

---

# 199. Data Lifecycle Testing

Deletion must be tested with:

* active Business;
* recently expired Business;
* 60-day boundary;
* reactivated Business;
* deletion eligible Business;
* deleting Business;
* partially deleted Business;
* deleted Business;
* concurrent renewal;
* concurrent reactivation;
* offline synchronization;
* worker crash;
* database restart.

---

# 200. Boundary Testing

Important boundaries include:

```text
expiry - 1 second
expiry
expiry + 1 second

eligibility - 1 second
eligibility
eligibility + 1 second
```

Tests must use server-controlled timestamps.

---

# 201. Deletion Dry Run

A controlled dry-run capability may be provided for administrators.

Dry-run must:

* identify rows;
* estimate volume;
* validate dependencies;
* detect blockers;

without physically deleting data.

---

# 202. Dry Run Safety

Dry-run must not modify Business data.

Any temporary operational state must be isolated and cleaned automatically.

---

# 203. Deletion Estimate

Before deletion, the system may calculate:

```text
Orders
Payments
Inventory Transactions
Employees
Devices
Reports
Audit Events
Files
```

This is informational and must not be used as the sole integrity check.

---

# 204. Deletion Dependency Manifest

A deletion job may create a manifest describing expected data domains.

Example:

```text
orders
payments
inventory
employees
devices
reports
notifications
audit
configuration
sync
files
```

The manifest assists monitoring and recovery.

---

# 205. Schema Evolution

New Business-owned tables introduced in future migrations must define their lifecycle behavior.

Every new Business-owned table must answer:

1. Does it contain `business_id`?
2. How is Business ownership established?
3. What happens during read-only?
4. What happens during deletion?
5. What are its foreign-key dependencies?
6. Does it contain sensitive data?
7. Does it need cleanup batching?

---

# 206. Migration Guardrail

A migration that introduces a new Business-owned table must not be accepted without defining its deletion behavior.

This prevents orphaned tenant data.

---

# 207. Database Documentation

Each Business-owned table should document:

* owner domain;
* Business scope;
* Branch scope;
* lifecycle behavior;
* deletion phase;
* retention;
* foreign-key strategy.

---

# 208. Data Ownership Metadata

The schema documentation should clearly identify:

```text
Owner Domain
Business Scoped
Branch Scoped
Lifecycle Behavior
Deletion Phase
```

This metadata assists future development and AI coding agents.

---

# 209. AI Coding Agent Guardrail

AI-generated code must not introduce:

* uncontrolled Business deletion;
* cascade deletion from Business without review;
* tenant-unscoped delete queries;
* lifecycle bypass;
* reactivation of deleted Business;
* writes during `DELETING`.

Lifecycle-sensitive code requires review against this document.

---

# 210. Transaction and Lifecycle Guardrail

Any transaction that creates or modifies Business-owned state must verify that the Business is operationally writable.

Conceptually:

```text
Business lifecycle
    ↓
Subscription entitlement
    ↓
Authorization
    ↓
Operation
```

The exact validation order may vary, but lifecycle cannot be skipped.

---

# 211. Read-Only Guardrail

Read-only state must not be implemented merely through frontend disabling.

The backend/database transaction boundary must enforce it.

---

# 212. Deleted State Guardrail

Deleted Business access must be rejected server-side.

No frontend, cached token or offline device may override it.

---

# 213. Offline Guardrail

Offline clients must receive lifecycle-aware authorization.

They must not assume that previous authorization remains valid indefinitely.

---

# 214. Synchronization Guardrail

Every synchronized event must validate current Business lifecycle before mutation.

---

# 215. Background Worker Guardrail

Every Business-scoped worker must validate lifecycle before writing.

---

# 216. Report Worker Guardrail

Report workers must validate lifecycle before storing a generated report version.

---

# 217. Notification Worker Guardrail

Notification workers must validate lifecycle before creating a new Business notification.

---

# 218. Configuration Worker Guardrail

Scheduled configuration activation must validate lifecycle before activation.

---

# 219. Payroll Worker Guardrail

Payroll workers must validate lifecycle before creating calculation or correction records.

---

# 220. Inventory Worker Guardrail

Inventory background workers must validate lifecycle before creating inventory mutations.

---

# 221. Data Lifecycle and Historical Integrity

The fundamental rule is:

> Normal corrections never destroy history; Business deletion is the explicit lifecycle mechanism for permanent removal.

This distinction must remain clear throughout the database architecture.

---

# 222. Recommended Tables

The lifecycle model should include or support:

```text
businesses
business_lifecycle_events
business_deletion_requests
business_deletion_jobs
business_deletion_registry
file_cleanup_tasks
```

Optional:

```text
business_deletion_phase_progress
business_retention_policy_versions
```

---

# 223. Suggested `businesses` Fields

```text
id UUID PRIMARY KEY
status
subscription_expired_at TIMESTAMPTZ NULL
deletion_eligible_at TIMESTAMPTZ NULL
deletion_started_at TIMESTAMPTZ NULL
deletion_completed_at TIMESTAMPTZ NULL
lifecycle_version
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

---

# 224. Suggested `business_lifecycle_events` Fields

```text
id UUID PRIMARY KEY
business_id UUID
from_status
to_status
reason_code
reason_text
actor_type
actor_id
source
created_at TIMESTAMPTZ
metadata JSONB
```

---

# 225. Suggested `business_deletion_requests` Fields

```text
id UUID PRIMARY KEY
business_id UUID
status
eligible_at TIMESTAMPTZ
requested_at TIMESTAMPTZ
scheduled_at TIMESTAMPTZ
started_at TIMESTAMPTZ
cancelled_at TIMESTAMPTZ
completed_at TIMESTAMPTZ
retention_policy_version
reason_code
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

---

# 226. Suggested `business_deletion_jobs` Fields

```text
id UUID PRIMARY KEY
business_id UUID
deletion_request_id UUID
status
current_phase
attempt_count
last_processed_id
processed_count
last_progress_at TIMESTAMPTZ
started_at TIMESTAMPTZ
completed_at TIMESTAMPTZ
error_code
error_message
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

---

# 227. Suggested `business_deletion_registry` Fields

```text
business_id UUID PRIMARY KEY
deletion_job_id UUID
eligible_at TIMESTAMPTZ
started_at TIMESTAMPTZ
completed_at TIMESTAMPTZ
status
result
created_at TIMESTAMPTZ
```

The registry must contain minimal metadata only.

---

# 228. Suggested `file_cleanup_tasks` Fields

```text
id UUID PRIMARY KEY
business_id UUID
object_key
status
attempt_count
last_error
created_at TIMESTAMPTZ
completed_at TIMESTAMPTZ
```

---

# 229. Database-Level Invariants

The following invariants apply to Data Lifecycle and Deletion:

1. Every Business has exactly one authoritative lifecycle state.
2. Business UUID is immutable.
3. Business UUID is never reused.
4. Lifecycle state is server authoritative.
5. Client time cannot determine lifecycle state.
6. Subscription expiry is stored using an absolute timestamp.
7. Retention starts from the authoritative subscription expiry timestamp.
8. Current retention period is 60 days.
9. Deletion eligibility is deterministic.
10. Deletion eligibility does not itself delete data.
11. Read-only state preserves Business data.
12. Read-only state blocks modifying operations.
13. Reactivation preserves Business UUID.
14. Reactivation preserves historical records.
15. Reactivation does not reset historical creation timestamps.
16. Reactivation before deletion cancels deletion safely.
17. Reactivation and deletion cannot race successfully.
18. Deleted Businesses cannot be reactivated.
19. Deleted Business UUIDs are never reused.
20. Deleting state blocks new operational writes.
21. Deleting state blocks new synchronization writes.
22. Deleting state invalidates offline authorization.
23. Deleting state invalidates trusted device access.
24. Deleting state prevents new employee access.
25. Deleted Business access is rejected server-side.
26. Background jobs must respect lifecycle state.
27. Workers must validate lifecycle before writing.
28. Sync workers must validate lifecycle before mutation.
29. Configuration workers must validate lifecycle before activation.
30. Report workers must validate lifecycle before persistence.
31. Notification workers must validate lifecycle before persistence.
32. Payroll workers must validate lifecycle before persistence.
33. Inventory workers must validate lifecycle before mutation.
34. Business-level deletion is controlled, not an uncontrolled cascade.
35. Foreign keys protect integrity during normal operation.
36. Cross-Business deletion is prohibited.
37. Tenant scope must be validated for deletion queries.
38. Business-owned data must be traceable to a Business.
39. Shared platform data must not be deleted with a Business.
40. Subscription plans are not Business-owned.
41. Global feature definitions are not Business-owned.
42. Platform permission definitions are not Business-owned.
43. Business configuration is Business-owned.
44. Branch data is deleted only with the owning Business lifecycle.
45. Employee data is deleted only with the owning Business lifecycle.
46. Device trust is invalidated before Business deletion.
47. Offline authorization is invalidated before Business deletion.
48. Pending sync events cannot recreate deleted data.
49. Stale offline events cannot resurrect a Business.
50. Late subscription payments cannot automatically resurrect a deleted Business.
51. Late external payment responses cannot recreate deleted Payment records.
52. Deletion jobs have stable UUIDs.
53. Deletion requests have stable UUIDs.
54. Deletion execution is idempotent.
55. Duplicate deletion jobs for the same Business are prevented.
56. Only one active deletion worker owns a Business.
57. Deletion progress is persisted.
58. Deletion batches are bounded.
59. Large deletion operations are not performed as one unbounded transaction.
60. Completed deletion batches remain committed.
61. Failed deletion batches can be retried safely.
62. Deletion progress is recorded only after successful commit.
63. Worker crashes do not corrupt committed deletion progress.
64. Database restarts do not corrupt committed deletion progress.
65. Partial deletion does not imply successful deletion.
66. Business is marked Deleted only after required phases succeed.
67. Finalization is verified.
68. Deletion failures remain visible.
69. Stuck deletion jobs are detectable.
70. Deletion jobs support recovery.
71. Deletion phases are deterministic.
72. Deletion dependencies are explicitly ordered.
73. Parent rows are not deleted before required child rows.
74. Orphan creation is prohibited.
75. Referential integrity remains valid after every committed phase.
76. Soft deletion and permanent deletion are distinct concepts.
77. Archive and permanent deletion are distinct concepts.
78. Historical records are immutable during normal operation.
79. Business deletion is the explicit permanent removal mechanism.
80. Audit history is append-only during the normal Business lifecycle.
81. Business-owned audit data follows Business lifecycle.
82. Deletion itself is auditable.
83. Platform-level deletion metadata may survive Business deletion.
84. Platform deletion metadata contains minimal information.
85. Deletion metadata must not contain unnecessary sensitive data.
86. Business-owned reports are deleted with the Business.
87. Business-owned notifications are deleted with the Business.
88. Business-owned configuration is deleted with the Business.
89. Business-owned sync state is deleted with the Business.
90. Business-owned device records are deleted with the Business.
91. Business-owned employee records are deleted with the Business.
92. Business-owned inventory records are deleted with the Business.
93. Business-owned financial records are deleted with the Business.
94. Business-owned order records are deleted with the Business.
95. Business-owned file objects are cleaned up.
96. Cache cannot preserve deleted Business access.
97. Search indexes cannot remain an authoritative source after deletion.
98. Backup retention is separate from application deletion.
99. Backup restoration cannot bypass lifecycle rules.
100. Restored Business lifecycle state must be reconciled.
101. Lifecycle transitions are concurrency-controlled.
102. Invalid lifecycle transitions are rejected.
103. Lifecycle state changes are atomic.
104. Reactivation is atomic with deletion cancellation where applicable.
105. Deletion start is atomic with deletion-job creation.
106. Deletion completion is atomic with final lifecycle update.
107. Lifecycle versioning prevents stale updates.
108. Deletion scheduler uses safe claiming.
109. Multiple workers cannot delete the same Business concurrently.
110. Deletion cancellation is controlled and audited.
111. Irreversible deletion cannot be silently cancelled.
112. Deletion eligibility is based on server time.
113. Retention calculations are timezone-safe.
114. Retention policy version may be preserved.
115. Eligibility calculation is reconstructable.
116. Notification failure does not reset retention.
117. Export does not reset retention.
118. Read-only access does not extend retention.
119. Offline activity does not extend retention.
120. Offline activity cannot bypass deletion.
121. Lifecycle state is checked at write boundaries.
122. Frontend restrictions are not sufficient lifecycle enforcement.
123. Database/application deletion code must be tenant-scoped.
124. Raw destructive SQL requires controlled authorization.
125. SQL injection cannot influence deletion scope.
126. Deletion credentials follow least privilege.
127. Deletion errors do not expose sensitive data.
128. Logs do not contain unnecessary Business-sensitive payloads.
129. Error monitoring does not retain unnecessary Business data.
130. Temporary files follow Business lifecycle.
131. Generated exports follow Business lifecycle.
132. Object storage cleanup is idempotent.
133. File cleanup failure does not mark Business fully deleted.
134. File cleanup progress is observable.
135. Lifecycle metrics do not expose unnecessary tenant data.
136. High-cardinality tenant identifiers are avoided in metrics.
137. Deleted Business sessions are invalidated.
138. Deleted Business refresh tokens are invalidated.
139. Deleted Business devices cannot authenticate.
140. Deleted Business employees cannot authenticate.
141. Deleted Business permissions cannot authorize operations.
142. Deleted Business configuration cannot become effective.
143. Deleted Business reports cannot be generated.
144. Deleted Business notifications cannot be created.
145. Deleted Business inventory transactions cannot be created.
146. Deleted Business Payments cannot be created.
147. Deleted Business Orders cannot be created.
148. Deleted Business attendance cannot be created.
149. Deleted Business payroll cannot be created.
150. Deleted Business cannot be recreated by UUID.
151. Cross-tenant lifecycle operations are prohibited.
152. Child Business references must belong to the same Business where required.
153. Shared reference data remains intact.
154. Platform subscription definitions remain intact.
155. Platform feature definitions remain intact.
156. Platform permission definitions remain intact.
157. Business-specific configuration remains tenant-scoped.
158. Branch lifecycle cannot independently reactivate a deleted Business.
159. Employee lifecycle cannot independently reactivate a deleted Business.
160. Device lifecycle cannot independently reactivate a deleted Business.
161. Subscription renewal cannot independently reactivate a deleted Business.
162. Queue messages cannot override lifecycle state.
163. Outbox consumers cannot recreate deleted Business state.
164. Cache invalidation is part of deletion handling.
165. Search index cleanup is part of deletion handling where applicable.
166. External integration cleanup is explicitly defined where applicable.
167. Tenant-specific secrets are revoked or removed.
168. Tenant-specific encryption keys follow security lifecycle.
169. Configuration history does not preserve plaintext secrets unnecessarily.
170. Audit snapshots do not bypass Business lifecycle.
171. Correction history follows Business lifecycle.
172. Historical financial data remains consistent until deletion.
173. Historical inventory data remains consistent until deletion.
174. Historical order data remains consistent until deletion.
175. Historical employee data remains consistent until deletion.
176. Historical configuration data remains consistent until deletion.
177. Historical report versions remain consistent until deletion.
178. Historical device assignments remain consistent until deletion.
179. Historical synchronization records remain consistent until deletion.
180. Data deletion cannot create invalid financial references.
181. Data deletion cannot create invalid inventory references.
182. Data deletion cannot create invalid order references.
183. Data deletion cannot create invalid configuration references.
184. Data deletion cannot create invalid employee references.
185. Data deletion cannot create invalid device references.
186. Data deletion cannot create invalid audit references within retained scope.
187. Orphan detection is available for lifecycle integrity.
188. New Business-owned tables must define lifecycle behavior.
189. New Business-owned tables must define deletion dependencies.
190. New Business-owned tables must define Business ownership.
191. New migrations must preserve lifecycle constraints.
192. Lifecycle-sensitive code must follow this document.
193. AI-generated lifecycle code requires review.
194. Deletion dry runs do not modify Business data.
195. Deletion estimates do not replace integrity checks.
196. Deletion manifests are informational and traceable.
197. Deletion monitoring detects stuck jobs.
198. Deletion recovery is tested.
199. Boundary conditions around expiry and eligibility are tested.
200. The database must never report a Business as Deleted before permanent deletion requirements are satisfied.

---

# 230. Recommended Index Summary

At minimum, consider:

```text
businesses(status)
businesses(subscription_expired_at)
businesses(deletion_eligible_at)
businesses(status, deletion_eligible_at)

business_lifecycle_events(business_id, created_at)

business_deletion_requests(business_id)
business_deletion_requests(status, scheduled_at)

business_deletion_jobs(business_id)
business_deletion_jobs(status, last_progress_at)

business_deletion_registry(business_id)
```

Large Business-owned operational tables should also use Business-scoped indexes according to their domain query patterns.

---

# 231. Database Design Principles

The lifecycle database model follows these principles:

1. Business is the lifecycle root.
2. Lifecycle state is authoritative.
3. Subscription entitlement and lifecycle are separate concerns.
4. Read-only does not mean deleted.
5. Archive does not mean deleted.
6. Historical integrity is preserved during normal operation.
7. Deletion is explicit and controlled.
8. Deletion is tenant-scoped.
9. Deletion is dependency-aware.
10. Deletion is idempotent.
11. Deletion is resumable.
12. Deletion is observable.
13. Deletion is auditable.
14. Offline data cannot bypass lifecycle.
15. Background workers cannot bypass lifecycle.
16. Backups are separate from application deletion.
17. Deleted Business identities are never reused.
18. Shared platform data is never deleted with a tenant.
19. Database constraints protect lifecycle correctness.
20. New schema objects must define lifecycle behavior.

---

# 232. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Domain Analysis

* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### Architecture

* `docs/04_Architecture/08_Offline_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/10_Security_Architecture.md`
* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`
* `docs/04_Architecture/19_Architecture_Decisions_and_Tradeoffs.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`

### Database

* `docs/05_Database/01_Database_Overview.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`

---

# 233. Status

**Database Analysis:** Completed.

**Document Status:** Accepted.

**Current Document:** `24_Data_Lifecycle_and_Deletion_Data_Model.md`

**Next Document:** `25_Database_Integrity_and_Constraints.md`

