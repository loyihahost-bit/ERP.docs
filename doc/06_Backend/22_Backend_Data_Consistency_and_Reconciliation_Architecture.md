# Backend Data Consistency and Reconciliation Architecture

**Document ID:** BA-22
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the architecture for maintaining, detecting, validating and recovering data consistency across the FastFood ERP backend.

The system operates across:

* multiple Businesses;
* multiple Branches;
* trusted offline devices;
* online and offline transactions;
* PostgreSQL;
* background workers;
* outbox events;
* cache;
* reports;
* file storage;
* external integrations.

Because different components may temporarily observe different states, the system must explicitly define:

* which state is authoritative;
* when data is considered consistent;
* how inconsistencies are detected;
* how inconsistencies are reconciled;
* which differences are expected;
* which differences are business errors;
* which differences are security incidents;
* how corrections are recorded.

The primary principle is:

> **Consistency must be measurable, explainable and recoverable.**

---

# 2. Consistency Principles

The backend follows these principles:

1. PostgreSQL is authoritative for committed server-side business state.
2. Client-local offline state is authoritative only for the device's local pending operations until server reconciliation.
3. Cache is never authoritative.
4. Reports are derived from authoritative transactional state and report snapshots.
5. Audit history is immutable.
6. Historical financial snapshots are immutable.
7. Reconciliation must never silently overwrite historical state.
8. Differences must be classified before correction.
9. Corrections must create explicit new state.
10. Every important reconciliation must be attributable.
11. Duplicate operations must be detected through operation UUID/idempotency.
12. Financial reconciliation receives higher priority than secondary reporting reconciliation.
13. Security inconsistencies are treated separately from ordinary business inconsistencies.
14. Reconciliation must be idempotent.
15. Reconciliation must be restartable.
16. Large reconciliation jobs must use bounded batches.
17. A successful reconciliation must produce evidence.
18. Reconciliation must preserve Business and Branch isolation.

---

# 3. Scope

This document covers:

* consistency model;
* authoritative state;
* transactional consistency;
* entity consistency;
* financial consistency;
* inventory consistency;
* cash consistency;
* Order consistency;
* configuration consistency;
* report consistency;
* offline consistency;
* synchronization reconciliation;
* cache consistency;
* outbox consistency;
* file consistency;
* external integration reconciliation;
* invariant checks;
* discrepancy classification;
* reconciliation workflows;
* correction mechanisms;
* monitoring;
* consistency SLOs;
* operational recovery.

---

# 4. Consistency Model

FastFood ERP uses a layered consistency model.

```text id="zqk2c7"
Authoritative Transactional State
            ↓
Derived Operational State
            ↓
Cache / Read Optimization
            ↓
External / Secondary State
```

The higher layer determines the truth for the lower layer.

For example:

```text id="q1n8xw"
PostgreSQL Order State
        ↓
Report
        ↓
Cache
        ↓
Dashboard
```

A dashboard mismatch does not change the authoritative Order state.

---

# 5. Authoritative State

The following are authoritative in PostgreSQL:

* Business;
* Branch;
* Employee;
* permissions;
* subscription;
* trusted device state;
* Product;
* Recipe;
* inventory transactions;
* inventory balances;
* Order;
* Order Items;
* payments;
* refunds;
* cash sessions;
* handovers;
* configuration;
* synchronization records;
* audit records;
* report versions;
* lifecycle state;
* idempotency records.

---

# 6. Non-Authoritative State

The following are not authoritative:

* Redis cache;
* browser cache;
* device display state;
* generated dashboard aggregates;
* temporary worker memory;
* temporary files;
* printer state;
* email delivery state;
* external notification provider state.

These states may be reconciled against PostgreSQL.

---

# 7. Consistency Boundaries

Consistency boundaries include:

```text id="9g7k2n"
Transaction
    ↓
Database
    ↓
Outbox
    ↓
Background Job
    ↓
External/Derived State
```

The system guarantees strong consistency inside required database transactions.

It uses eventual consistency for appropriate secondary operations.

---

# 8. Strong Consistency

Strong consistency is required for operations such as:

* payment;
* refund;
* cash session;
* cash handover;
* inventory deduction;
* Order acceptance;
* important configuration changes;
* permission changes;
* subscription state changes;
* lifecycle deletion state;
* idempotency state.

These operations must not depend on eventually consistent cache or external services.

---

# 9. Eventual Consistency

Eventual consistency is acceptable for:

* notifications;
* email;
* printer status;
* dashboard aggregates;
* report generation;
* XLSX generation;
* cache;
* non-critical external integrations.

The system must expose or internally track processing state where useful.

---

# 10. Transactional Consistency

A core business transaction must either:

```text id="p2z7la"
Commit Completely
```

or:

```text
Rollback Completely
```

Examples:

### Order Acceptance

```text
Validate Order
      ↓
Validate Inventory
      ↓
Deduct Inventory
      ↓
Change Order State
      ↓
Create Audit
      ↓
Create Required Outbox Event
      ↓
Commit
```

A partial database transaction is not accepted.

---

# 11. Transaction Boundary

The Application Layer owns transaction boundaries.

Repositories must not independently commit business operations.

A transaction must contain only the state changes that must remain atomic.

External calls must not be required for transaction success.

---

# 12. Operation UUID

Retryable business operations use an operation UUID.

Examples:

* payment;
* refund;
* inventory deduction;
* cash correction;
* configuration change;
* synchronization operation.

The operation UUID allows the backend to determine:

```text id="7o5d1v"
New Operation
or
Already Processed Operation
```

---

# 13. Idempotency

An operation is idempotent when repeated execution produces one authoritative business effect.

Example:

```text id="m8v4jz"
Payment Operation UUID = OP-123

Request 1 → Payment Created
Request 2 → Existing Result Returned
Request 3 → Existing Result Returned
```

Repeated requests must not create duplicate payments.

---

# 14. Duplicate Detection

Duplicate detection must use appropriate identifiers.

Possible identifiers:

* operation UUID;
* payment UUID;
* Order UUID;
* synchronization event UUID;
* device transaction UUID;
* external provider reference.

A client-generated identifier is never trusted as proof of authorization.

---

# 15. Business Scope Consistency

Every Business-scoped record must belong to exactly one valid Business.

The system must prevent:

```text id="d2t9e4"
Business A
   ↓
Record belonging to Business B
```

Cross-Business references are invalid.

---

# 16. Branch Scope Consistency

Branch-scoped records must belong to a Branch that belongs to the same Business.

The following relationship must remain valid:

```text id="0n8qfx"
Business
   ↓
Branch
   ↓
Branch Record
```

A Branch record from Business A cannot reference Business B.

---

# 17. Employee Scope Consistency

Employee operations must preserve:

* Business;
* Branch;
* role;
* permission;
* employee status.

Inactive employees cannot create new valid business modifications.

Historical records retain the original employee identity.

---

# 18. Order Consistency

An Order must maintain consistent relationships between:

* Business;
* Branch;
* employee;
* device;
* cash session where applicable;
* Order Items;
* payments;
* refunds;
* configuration snapshots.

An Order cannot reference entities from another Business.

---

# 19. Order Financial Consistency

The authoritative Order financial state includes:

* item prices;
* quantities;
* discounts;
* markup;
* extras;
* removals;
* total amount;
* payments;
* refunds.

Historical Order totals must not be recalculated from current Product prices.

---

# 20. Order Item Snapshot

Each Order Item must retain the information necessary to preserve its historical financial meaning.

At minimum where applicable:

* Product UUID;
* Product name snapshot;
* price;
* quantity;
* discount;
* applicable configuration/version;
* recipe/configuration reference where required.

Current menu configuration cannot reinterpret historical Order Items.

---

# 21. Payment Consistency

A Payment must:

* belong to one Business;
* belong to the correct Order;
* have a valid amount;
* have a valid status;
* use a unique operation/idempotency identity.

Payment totals must be reconciled against Order financial state.

---

# 22. Payment Reconciliation

A payment reconciliation check may compare:

```text id="3s8x0p"
Order Expected Amount
        ↓
Payment Amounts
        ↓
Refund Amounts
        ↓
Net Paid Amount
```

A discrepancy must be classified before correction.

Possible results:

```text
CONSISTENT
UNDERPAID
OVERPAID
REFUND_MISMATCH
DUPLICATE_PAYMENT
MISSING_PAYMENT
UNKNOWN
```

---

# 23. Refund Consistency

Refunds must reference the original financial transaction.

Refund calculation must use historical transaction information.

Current Product price must never determine historical refund amount.

Refunds must not exceed permitted refundable amount according to business rules.

---

# 24. Cash Consistency

Cash state must reconcile:

```text id="j9g2zw"
Opening Cash
+ Cash Sales
+ Cash In
- Cash Out
- Refunds
± Corrections
= Expected Cash
```

The actual physical cash is compared separately.

---

# 25. Cash Reconciliation

Cash reconciliation may produce:

```text
MATCH
SHORTAGE
SURPLUS
UNRESOLVED
```

A discrepancy must retain:

* Cash Session;
* Branch;
* cashier;
* expected amount;
* actual amount;
* difference;
* reason/comment;
* correction history.

---

# 26. Cash Session Integrity

The system must ensure:

* one valid opening state;
* valid session owner;
* valid Branch;
* valid register;
* valid close state;
* no duplicate close;
* no reopening of closed sessions.

A closed session cannot become open through reconciliation.

---

# 27. Cash Handover Consistency

Handover state must reconcile:

```text id="r4q6ku"
Outgoing Cashier
      ↓
Transfer Amount
      ↓
Incoming Cashier
      ↓
Counted Cash
      ↓
Confirmation
```

Discrepancies must remain attributable to the relevant handover.

---

# 28. Inventory Consistency

Inventory has two important representations:

1. Inventory transaction history.
2. Current inventory balance.

The transaction history is authoritative for reconstructing inventory movement.

Current balance must remain consistent with applicable transactions.

---

# 29. Inventory Reconciliation

A reconciliation may calculate:

```text id="v9c2ms"
Opening Balance
+ Purchases
+ Production
+ Transfers In
- Sales Consumption
- Manual Exits
- Transfers Out
± Adjustments
= Expected Closing Balance
```

Actual stock count is compared separately.

---

# 30. Negative Stock Invariant

Inventory must never become negative.

If a reconciliation detects negative stock:

1. mark discrepancy;
2. stop automatic propagation where necessary;
3. identify originating transaction;
4. inspect transaction ordering;
5. correct through explicit adjustment/recovery.

The system must not silently clamp negative values to zero.

---

# 31. Recipe Consistency

Inventory deductions must reference the correct Recipe Version.

Historical deductions retain the Recipe Version used at transaction time.

Current Recipe configuration cannot reinterpret historical inventory movements.

---

# 32. Recipe Reconciliation

Reconciliation may verify:

* Product → Recipe relationship;
* Recipe Version validity;
* Recipe component existence;
* quantity conversion;
* inventory deduction;
* effective configuration.

A missing historical Recipe Version is a data integrity incident.

---

# 33. Set Consistency

Set sales must remain consistent with:

* Set Version;
* component configuration;
* Branch menu availability;
* inventory deductions;
* Set price snapshot.

Historical Set Orders must not be recalculated from current component prices.

---

# 34. Configuration Consistency

Configuration state includes:

* Business configuration;
* Branch configuration;
* menu;
* pricing;
* permissions;
* subscription;
* feature configuration.

Each important configuration change must have a version or equivalent historical identity.

---

# 35. Configuration Reconciliation

A configuration reconciliation may compare:

```text
Current Effective Configuration
        ↓
Configuration Version
        ↓
Branch Override
        ↓
Cached Configuration
        ↓
Offline Device Configuration
```

The server configuration remains authoritative.

---

# 36. Offline Device Consistency

An offline device may temporarily contain:

```text
Local State
Pending Operations
Cached Configuration
```

This state is not equivalent to final server state.

The server must determine final authoritative results after synchronization.

---

# 37. Offline Operation Reconciliation

For every received offline operation:

1. authenticate device;
2. validate Business;
3. validate Branch;
4. validate employee;
5. validate offline authorization;
6. validate operation UUID;
7. detect duplicate;
8. validate business rules;
9. apply transaction;
10. record result.

---

# 38. Synchronization Result States

Each synchronized operation should resolve to:

```text id="m5p8qk"
ACCEPTED
DUPLICATE
REJECTED
CONFLICT
RETRYABLE_FAILURE
PERMANENT_FAILURE
```

The final state must be queryable.

---

# 39. Synchronization Conflict

A conflict exists when an offline operation cannot be safely applied to current server state.

Examples:

* stale configuration;
* changed Product availability;
* invalid Branch state;
* concurrent financial operation;
* incompatible inventory state.

A conflict must not be silently converted into success.

---

# 40. Synchronization Conflict Resolution

Resolution must:

* identify operation;
* identify conflicting state;
* identify affected entity;
* identify resolving actor/system;
* preserve original operation;
* record resolution;
* create new correction/configuration where required.

The original offline operation must remain historically identifiable.

---

# 41. Transaction Ordering

Synchronization must preserve required business ordering.

Example:

```text id="p5h0yz"
Order Created
     ↓
Order Accepted
     ↓
Payment
```

A later dependent operation must not be applied before its required predecessor.

If ordering cannot be established, the operation enters an appropriate pending/conflict state.

---

# 42. Outbox Consistency

When a business transaction requires an outbox event, the event must be created atomically with the business transaction.

Example:

```text id="0bq6cn"
Order State Change
      +
Outbox Event
      ↓
Same Database Transaction
```

The event cannot exist as “successfully published” if the authoritative business transaction failed.

---

# 43. Outbox Reconciliation

The system should periodically check:

* pending outbox events;
* processing state;
* failed events;
* retry count;
* stale processing state.

A committed business transaction with a missing required outbox event is a consistency incident.

---

# 44. Background Job Consistency

A background job must not assume that a previous execution failed simply because the worker restarted.

The job must inspect:

* operation UUID;
* business state;
* job state;
* idempotency state.

Duplicate execution must be safe.

---

# 45. Cache Consistency

Cache consistency uses:

```text id="8n2qwy"
PostgreSQL
   ↓
Commit
   ↓
Cache Invalidation
   ↓
New Cache Value
```

The database remains authoritative.

---

# 46. Stale Cache

A stale cache entry must never override a newer authoritative database state.

If cache version information is inconsistent:

* invalidate cache;
* reload from PostgreSQL;
* record metric if recurring.

---

# 47. Cache Reconciliation

Cache reconciliation may verify:

* key version;
* configuration version;
* Branch scope;
* Business scope;
* expiration;
* value identity.

A cache mismatch is normally an optimization problem, not a business-data corruption event.

---

# 48. Report Consistency

Reports are derived from authoritative business state.

A report must identify:

* period;
* source data state;
* report version;
* creation time;
* creator/system source;
* reason.

Historical report versions are immutable.

---

# 49. Report Reconciliation

A report reconciliation may compare:

```text id="r6p1qm"
Authoritative Transactions
        ↓
Report Calculation
        ↓
Stored Report Version
```

If the underlying data changes due to a valid correction, a new report version may be created.

The old version remains unchanged.

---

# 50. Dashboard Consistency

Dashboard values may be eventually consistent.

Dashboard data must not be used as the final source for:

* financial correction;
* payment confirmation;
* cash correction;
* inventory adjustment.

When exact values are required, the authoritative query must be used.

---

# 51. File Consistency

File consistency covers:

* report files;
* XLSX exports;
* images;
* documents.

The database file metadata must correspond to actual persistent storage.

Possible state:

```text
REGISTERED
UPLOADING
AVAILABLE
MISSING
CORRUPTED
DELETED
```

---

# 52. File Reconciliation

A file reconciliation job may compare:

```text
Database Metadata
       ↔
Persistent Storage
```

If metadata exists but file is missing:

* mark discrepancy;
* alert if critical;
* attempt restoration where available;
* do not silently create fake file references.

---

# 53. External Integration Consistency

External systems may include:

* email providers;
* payment providers where applicable;
* printer systems;
* storage providers;
* future integrations.

External state must not automatically override authoritative internal business state.

---

# 54. External Reconciliation

Where an external provider supports lookup/reconciliation:

1. retrieve external status;
2. match stable external reference;
3. compare internal state;
4. classify discrepancy;
5. reconcile explicitly.

Provider response must be authenticated and validated.

---

# 55. Printer Consistency

Printer state is not Order state.

The system may have:

```text id="6m3g2h"
Order = ACCEPTED
Print = FAILED
```

This is an operational discrepancy, not an Order transaction failure.

Reconciliation may retry printing or create a manual reprint.

---

# 56. Notification Consistency

Notification delivery does not determine business transaction success.

Example:

```text id="n1w6vz"
Refund committed
Notification failed
```

The refund remains authoritative.

Notification is retried separately.

---

# 57. Subscription Consistency

Subscription state must be consistent across:

* Business;
* tariff;
* expiry;
* entitlement;
* cached entitlement;
* device/offline authorization.

Server-side subscription state is authoritative.

---

# 58. Subscription Reconciliation

Check:

```text id="g4c9wy"
Subscription State
      ↓
Expiry
      ↓
Entitlements
      ↓
Cached Authorization
      ↓
Offline Authorization
```

A stale cache must not allow a prohibited modification.

---

# 59. Lifecycle Consistency

Lifecycle states include:

```text id="5f9tqv"
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

Lifecycle transitions must be monotonic according to defined business rules.

Recovery must not accidentally move a Business backward without an explicit authorized operation.

---

# 60. Lifecycle Reconciliation

Reconciliation verifies:

* current state;
* subscription state;
* deletion schedule;
* deletion jobs;
* backup retention;
* pending operations.

A stale worker must not delete a Business whose lifecycle state has changed.

---

# 61. Consistency Check Types

Consistency checks are divided into:

### Structural

Relationship and foreign-key correctness.

### Transactional

Atomicity and state transitions.

### Financial

Orders, payments, refunds and cash.

### Inventory

Stock and transaction consistency.

### Security

Business/Branch isolation and authorization.

### Synchronization

Offline/server state.

### Operational

Jobs, outbox, files, cache.

---

# 62. Check Frequency

Checks may be:

```text id="f8g2zr"
Real-Time
Near Real-Time
Scheduled
On-Demand
Recovery-Time
```

### Real-Time

Critical transaction invariants.

### Near Real-Time

Queue/outbox/synchronization health.

### Scheduled

Full reconciliation.

### On-Demand

Incident investigation.

### Recovery-Time

Post-disaster validation.

---

# 63. Real-Time Validation

Real-time validation is required for:

* Business scope;
* Branch scope;
* authorization;
* inventory availability;
* cash state;
* payment state;
* Order state;
* operation idempotency.

---

# 64. Scheduled Reconciliation

Scheduled reconciliation may check:

* orphan records;
* duplicate operations;
* payment totals;
* cash balances;
* inventory balances;
* outbox;
* synchronization backlog;
* file metadata;
* report integrity;
* configuration versions.

Scheduled jobs must be bounded and resumable.

---

# 65. Reconciliation Batch Processing

Large reconciliation jobs must process data in batches.

Example:

```text id="n8x4ce"
Batch 1
Batch 2
Batch 3
...
Batch N
```

Each batch must:

* have bounded memory;
* have bounded transaction duration;
* record progress;
* support retry;
* avoid duplicate correction.

---

# 66. Reconciliation Cursor

Long-running reconciliation should use a stable cursor such as:

* primary key;
* UUID ordering where appropriate;
* timestamp + unique ID.

Offset-based pagination should not be used for very large mutable datasets when it can cause skipped or duplicated rows.

---

# 67. Reconciliation Job Identity

Every reconciliation job should have:

* job UUID;
* job type;
* scope;
* start time;
* end time;
* status;
* progress;
* discrepancy count;
* correction count;
* error count.

---

# 68. Reconciliation States

A reconciliation job may have:

```text id="j4p9tw"
PENDING
RUNNING
PARTIAL
COMPLETED
FAILED
CANCELLED
```

`PARTIAL` indicates that the job processed some scope but did not complete the entire requested scope.

---

# 69. Discrepancy Classification

Every detected discrepancy should be classified.

Recommended types:

```text id="v7k2qa"
EXPECTED_EVENTUAL_CONSISTENCY
DUPLICATE
MISSING_RECORD
ORPHAN_RECORD
VALUE_MISMATCH
STATE_MISMATCH
SCOPE_VIOLATION
ORDERING_VIOLATION
FINANCIAL_MISMATCH
INVENTORY_MISMATCH
CONFIGURATION_MISMATCH
SECURITY_VIOLATION
UNKNOWN
```

---

# 70. Expected Eventual Consistency

Not every mismatch is an error.

Example:

```text
Order committed
      ↓
Report worker pending
```

The report may temporarily differ.

If the difference is within the expected processing window, it is classified as:

`EXPECTED_EVENTUAL_CONSISTENCY`.

---

# 71. Duplicate Discrepancy

A duplicate is detected when the same logical operation has produced multiple authoritative effects.

Examples:

* duplicate payment;
* duplicate inventory deduction;
* duplicate refund.

Duplicates involving financial state are high priority.

---

# 72. Missing Record

A missing record occurs when a required authoritative or derived record is absent.

Examples:

* missing required outbox event;
* missing payment record;
* missing report version;
* missing audit event where mandatory.

The expected relationship must be verified before classifying it as corruption.

---

# 73. Orphan Record

An orphan record references an entity that no longer exists or is outside the valid relationship.

Examples:

```text id="x4f8ka"
Order Item
   ↓
Missing Order
```

or:

```text
Branch Record
   ↓
Different Business
```

Orphan records in core business data are integrity incidents.

---

# 74. Scope Violation

A scope violation occurs when:

* Business A record references Business B;
* Branch A record references Branch B;
* unauthorized data becomes accessible across scope.

Scope violations are security incidents.

They require immediate containment.

---

# 75. Financial Mismatch

Financial mismatches include:

* Order total vs Item total;
* Order total vs payment;
* payment vs refund;
* cash expected vs transaction-derived cash;
* report total vs authoritative transactions.

Financial mismatches require controlled investigation.

---

# 76. Inventory Mismatch

Inventory mismatches include:

* transaction-derived balance differs from stored balance;
* negative stock;
* incorrect recipe deduction;
* missing inventory transaction;
* duplicate inventory movement.

Inventory discrepancies must not be resolved by silently editing current quantity.

---

# 77. Configuration Mismatch

Configuration mismatch may occur between:

* current DB configuration;
* configuration version;
* Branch override;
* cache;
* offline device.

Server-side configuration remains authoritative.

---

# 78. Security Mismatch

Security mismatches include:

* unauthorized Business access;
* unauthorized Branch access;
* revoked device still accepted;
* inactive employee still performing operations;
* invalid offline authorization accepted.

These are security incidents, not ordinary reconciliation issues.

---

# 79. Correction Principle

The system must distinguish:

```text
Detection
    ↓
Investigation
    ↓
Classification
    ↓
Correction
    ↓
Verification
```

Detection alone must never automatically rewrite important historical data.

---

# 80. Automatic Correction

Automatic correction is allowed only when:

* the rule is deterministic;
* the correction is safe;
* the operation is idempotent;
* historical state is preserved;
* the correction is auditable.

Examples:

* rebuilding a cache;
* retrying a notification;
* requeueing a failed job.

---

# 81. Manual Correction

Manual correction is required when:

* financial meaning is ambiguous;
* multiple valid states exist;
* historical interpretation is uncertain;
* security impact exists;
* inventory discrepancy cannot be deterministically reconstructed.

Manual correction requires:

* authorization;
* reason;
* actor;
* audit;
* before/after state.

---

# 82. Correction Records

Every important correction should record:

* correction UUID;
* target entity;
* original state;
* corrected state;
* reason;
* actor;
* timestamp;
* operation UUID;
* source;
* reconciliation job UUID where applicable.

---

# 83. Correction Does Not Delete History

A correction must not:

* delete original transaction;
* overwrite original historical price;
* erase audit;
* remove original synchronization event;
* silently modify report version.

Instead:

```text id="3v9hqa"
Original State
      ↓
Correction
      ↓
New Authoritative State
```

---

# 84. Financial Correction

Financial correction must use dedicated business mechanisms.

Examples:

* refund;
* payment correction;
* cash correction;
* Order correction.

Direct SQL modification of financial amounts is prohibited as a normal operational procedure.

---

# 85. Inventory Correction

Inventory correction should use:

* inventory adjustment;
* stock count;
* explicit correction transaction.

The original inventory transaction remains immutable.

---

# 86. Configuration Correction

Configuration correction creates a new version.

Example:

```text id="z7m2pl"
Version 10
   ↓
Incorrect configuration detected
   ↓
Correction
   ↓
Version 11
```

Version 10 remains available for historical reconstruction.

---

# 87. Report Correction

If a report result changes because authoritative data was corrected:

* create a new report version;
* preserve previous report version;
* record reason;
* identify correction source.

---

# 88. Reconciliation and Audit

Important reconciliation activities must generate audit records.

Audit context should include:

* reconciliation job UUID;
* Business;
* Branch;
* actor/system;
* discrepancy type;
* target entity;
* action;
* result.

System-generated reconciliation must use an explicit system identity.

---

# 89. Reconciliation Security

Reconciliation jobs must respect:

* Business scope;
* Branch scope;
* employee permissions where manually triggered;
* subscription/lifecycle rules;
* data access restrictions.

A reconciliation process must not become a hidden privilege escalation mechanism.

---

# 90. Consistency Monitoring

Monitor:

* discrepancy count;
* discrepancy rate;
* unresolved discrepancy age;
* reconciliation duration;
* correction count;
* failed reconciliation jobs;
* synchronization conflicts;
* payment mismatches;
* inventory mismatches;
* cash mismatches.

---

# 91. Consistency SLOs

Initial operational targets:

| Metric                                        |                                  Target |
| --------------------------------------------- | --------------------------------------: |
| Critical invariant detection                  |                                  ≤ 60 s |
| Required audit creation                       |                                ≥ 99.99% |
| Duplicate financial operation prevention      |                                ≥ 99.99% |
| Cross-Business unauthorized access prevention |                                    100% |
| Cross-Branch unauthorized access prevention   |                                    100% |
| Critical reconciliation alert                 |                                  ≤ 60 s |
| Normal reconciliation job acknowledgement     |                                   ≤ 2 s |
| Normal sync batch p95                         |                                   ≤ 1 s |
| Critical financial discrepancy classification |                                ≤ 15 min |
| Recovery reconciliation initiation            |                 ≤ 15 min after recovery |
| Cache consistency recovery                    | ≤ 30 s after authoritative invalidation |
| Employee deactivation propagation             |                           ≤ 30 s online |
| Device revocation propagation                 |                           ≤ 30 s online |

The exact reconciliation completion time depends on data volume and incident scope.

---

# 92. Consistency Incident Severity

Recommended severity:

### Critical

* cross-Business access;
* duplicate payment;
* major financial corruption;
* large inventory corruption;
* widespread synchronization corruption.

### High

* Branch-wide inventory mismatch;
* cash reconciliation failure;
* large report mismatch;
* important configuration corruption.

### Medium

* limited report mismatch;
* stale cache;
* delayed notification;
* isolated operational mismatch.

### Low

* expected eventual consistency;
* non-critical derived-data delay.

---

# 93. Reconciliation Workflow

The standard workflow is:

```text id="6s0g8j"
Detect
  ↓
Create Discrepancy
  ↓
Classify
  ↓
Assess Impact
  ↓
Contain if Required
  ↓
Investigate
  ↓
Determine Authoritative State
  ↓
Correct
  ↓
Verify
  ↓
Audit
  ↓
Close
```

---

# 94. Authoritative State Determination

When two states disagree, the system determines authority according to:

1. committed PostgreSQL transaction;
2. immutable historical transaction snapshot;
3. explicit correction transaction;
4. server synchronization result;
5. derived/report state;
6. cache/client state.

Lower-level state cannot override higher-level authoritative state.

---

# 95. Consistency After Deployment

After deployment, monitor:

* database schema compatibility;
* transaction errors;
* payment errors;
* inventory errors;
* synchronization errors;
* report discrepancies;
* configuration errors.

A deployment that changes data behavior requires additional reconciliation checks.

---

# 96. Consistency After Database Recovery

After database recovery:

1. verify schema;
2. verify constraints;
3. verify critical counts;
4. verify recent transactions;
5. verify payments;
6. verify inventory;
7. verify cash;
8. verify audit;
9. verify synchronization;
10. run targeted reconciliation.

---

# 97. Consistency After Synchronization Recovery

After major synchronization recovery:

* compare pending operations;
* compare accepted operations;
* inspect duplicates;
* inspect conflicts;
* reconcile financial operations;
* reconcile inventory effects;
* verify device configuration;
* verify server authority.

---

# 98. Consistency After Security Incident

After a security incident:

* verify Business isolation;
* verify Branch isolation;
* verify employee status;
* verify device trust;
* verify session revocation;
* inspect suspicious operations;
* reconcile affected financial/inventory operations;
* preserve evidence.

---

# 99. Reconciliation Performance

Reconciliation must not unnecessarily block POS.

Large reconciliation should:

* run asynchronously;
* use bounded batches;
* avoid long locks;
* avoid full-table locking;
* use indexed queries;
* use read-only checks where possible;
* isolate heavy reporting workloads.

Critical real-time business transactions always have higher priority.

---

# 100. Reconciliation Locking

Reconciliation should avoid locking authoritative business records unless correction requires it.

For correction:

* use the same locking rules as normal business operations;
* acquire locks in deterministic order;
* keep transactions short;
* revalidate state before commit.

---

# 101. Reconciliation Concurrency

Two reconciliation jobs must not create conflicting corrections.

Use:

* job identity;
* scope locking where required;
* idempotency;
* unique correction identifiers;
* optimistic version checks.

The system must not silently apply two incompatible corrections.

---

# 102. Reconciliation Retry

Retry is allowed when:

* failure is transient;
* operation is safe;
* correction is idempotent.

Retry must not occur indefinitely.

Permanent failures must be marked for investigation.

---

# 103. Reconciliation Cancellation

A running reconciliation job may be cancelled where supported.

Cancellation must:

* stop future batches;
* allow current safe transaction to finish;
* record partial progress;
* leave already committed corrections intact;
* allow later restart.

---

# 104. Partial Reconciliation

A partially completed reconciliation is not automatically rolled back.

Previously committed safe corrections remain.

The job state must record:

* completed scope;
* remaining scope;
* correction count;
* error count.

The job may later resume from a stable checkpoint.

---

# 105. Data Consistency Dashboard

Operational monitoring should provide visibility into:

```text
Critical Discrepancies
Unresolved Discrepancies
Payment Mismatches
Cash Mismatches
Inventory Mismatches
Sync Conflicts
Outbox Failures
Failed Jobs
File Mismatches
Configuration Conflicts
```

The dashboard is operational information, not the authoritative business source.

---

# 106. Reconciliation Access

Manual reconciliation should be restricted to authorized operational roles.

Normal Owner/Manager permissions must not automatically grant infrastructure-level reconciliation capabilities.

Business-level correction remains governed by business permissions.

---

# 107. Data Consistency Testing

Automated tests should cover:

### Transaction

* atomicity;
* rollback;
* duplicate requests.

### Financial

* payment;
* refund;
* cash;
* Order totals.

### Inventory

* stock deduction;
* Recipe Version;
* negative stock prevention.

### Synchronization

* duplicate operation;
* conflict;
* retry;
* ordering.

### Security

* Business isolation;
* Branch isolation;
* device revocation.

### Recovery

* database restore;
* outbox recovery;
* reconciliation after disaster.

---

# 108. Property and Invariant Testing

Important invariants should be tested independently of specific UI flows.

Examples:

```text id="1c6m2x"
Payment total cannot exceed permitted financial state
Inventory cannot become negative
Closed Cash Session cannot reopen
Business A cannot access Business B
Historical price cannot change
Duplicate operation cannot duplicate effect
```

---

# 109. Reconciliation Test Data

Tests should include:

* clean consistent state;
* duplicate operation;
* missing event;
* stale cache;
* stale offline device;
* payment mismatch;
* inventory mismatch;
* cash discrepancy;
* configuration conflict;
* failed outbox;
* missing file.

---

# 110. Operational Reconciliation Reports

Reconciliation reports should contain:

* job UUID;
* scope;
* execution time;
* records checked;
* discrepancies found;
* discrepancies resolved;
* unresolved count;
* failures;
* execution status.

Reports themselves must not replace underlying discrepancy records.

---

# 111. Historical Integrity

Historical integrity requires that:

* original Orders remain reconstructable;
* original prices remain reconstructable;
* original Recipe Versions remain reconstructable;
* original payments remain reconstructable;
* original cash sessions remain reconstructable;
* original synchronization operations remain reconstructable;
* original configuration remains reconstructable.

Reconciliation must never destroy this capability.

---

# 112. Data Consistency Architecture

```text id="5r9jka"
                    ┌──────────────────────┐
                    │     Monitoring       │
                    │ Metrics / Alerts     │
                    └──────────┬───────────┘
                               │
                               ▼
                     ┌─────────────────┐
                     │ Reconciliation  │
                     │ Engine          │
                     └────────┬────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
      PostgreSQL          Synchronization       Outbox
     Authoritative             │                   │
          │                    ▼                   ▼
          │                Offline Devices    Workers
          │
    ┌─────┼────────┬──────────┬──────────┐
    ▼     ▼        ▼          ▼          ▼
 Orders Payments Inventory   Cash    Configuration
    │     │        │          │          │
    └─────┴────────┴──────────┴──────────┘
                     │
                     ▼
              Derived State
              Reports / Cache
```

---

# 113. Reconciliation Architecture

```text id="2k7d1p"
Detection
   ↓
Discrepancy Record
   ↓
Classification
   ↓
Authoritative State Resolution
   ↓
Correction Decision
   ├── No Correction
   ├── Automatic Correction
   └── Manual Correction
             ↓
        New Authoritative State
             ↓
          Audit
             ↓
        Verification
```

---

# 114. Operational Priority

When reconciliation competes for resources, priority is:

```text id="f5s2rb"
1. Security Violations
2. Financial Integrity
3. Cash Integrity
4. Inventory Integrity
5. Synchronization Integrity
6. Configuration Integrity
7. Core Transaction Integrity
8. Reports
9. Cache
10. Notifications
11. File Cleanup
```

Reconciliation workloads must not degrade core POS operations unnecessarily.

---

# 115. System Consistency Invariants

The following invariants apply to Backend Data Consistency and Reconciliation:

1. PostgreSQL is authoritative for committed business state.
2. Client cache is not authoritative.
3. Redis is not authoritative.
4. Dashboard values are not authoritative.
5. Report values are derived from authoritative state.
6. Historical report versions are immutable.
7. Business records cannot cross Business boundaries.
8. Branch records cannot cross Business boundaries.
9. Employee scope remains attributable.
10. Inactive employees cannot create new valid operations.
11. Every retryable critical operation has an idempotency strategy.
12. Duplicate operations cannot create duplicate authoritative effects.
13. Core transactions are atomic.
14. External services cannot determine database transaction success.
15. Payment state remains authoritative in PostgreSQL.
16. Refund state remains authoritative in PostgreSQL.
17. Cash Session state remains authoritative in PostgreSQL.
18. Inventory transaction history remains authoritative for inventory reconstruction.
19. Historical Order prices remain immutable.
20. Historical Recipe Versions remain immutable.
21. Historical configuration versions remain reconstructable.
22. Historical audit records remain immutable.
23. Historical synchronization operations remain identifiable.
24. Closed Cash Sessions cannot be reopened through reconciliation.
25. Inventory cannot become negative.
26. Financial corrections create explicit correction records.
27. Inventory corrections create explicit inventory transactions.
28. Configuration corrections create new configuration versions.
29. Report corrections create new report versions.
30. Reconciliation cannot silently delete historical state.
31. Reconciliation must classify discrepancies.
32. Expected eventual consistency must not be treated as corruption.
33. Security discrepancies are treated as security incidents.
34. Financial discrepancies receive high priority.
35. Cross-Business access violations are critical.
36. Cross-Branch unauthorized access violations are critical.
37. Reconciliation jobs are idempotent.
38. Reconciliation jobs are restartable.
39. Reconciliation jobs are bounded.
40. Reconciliation jobs record progress.
41. Partial reconciliation remains observable.
42. Cancelled reconciliation does not undo unrelated committed corrections.
43. Automatic correction is allowed only when deterministic and safe.
44. Manual correction requires authorization.
45. Manual correction requires a reason.
46. Manual correction is audited.
47. Correction preserves original state.
48. Reconciliation cannot bypass authorization.
49. Reconciliation cannot bypass subscription restrictions.
50. Reconciliation cannot bypass lifecycle restrictions.
51. Reconciliation respects Business scope.
52. Reconciliation respects Branch scope.
53. Offline operations retain original operation UUIDs.
54. Offline operations retain original financial snapshots.
55. Synchronization preserves operation ordering where required.
56. Synchronization conflicts are explicit.
57. Synchronization duplicates are explicitly detected.
58. Server state remains authoritative after synchronization.
59. Outbox creation is atomic with required business transactions.
60. Outbox failures do not undo committed business transactions.
61. Background retries do not duplicate business effects.
62. Cache invalidation cannot change authoritative state.
63. Stale cache cannot override PostgreSQL.
64. Payment reconciliation compares authoritative financial records.
65. Cash reconciliation compares expected and actual state.
66. Inventory reconciliation uses transaction history.
67. Recipe reconciliation preserves historical Recipe Versions.
68. Set reconciliation preserves historical Set Versions.
69. Configuration reconciliation preserves historical versions.
70. Report reconciliation preserves old report versions.
71. File reconciliation does not fabricate missing files.
72. Notification reconciliation does not alter transaction state.
73. Printer reconciliation does not alter Order state.
74. External provider state does not automatically override internal state.
75. Subscription reconciliation cannot grant unauthorized entitlements.
76. Lifecycle reconciliation cannot accidentally trigger deletion.
77. Recovery reconciliation is required after major disaster recovery.
78. Security reconciliation is required after security incidents.
79. Financial reconciliation is required after financial incidents.
80. Inventory reconciliation is required after inventory incidents.
81. Synchronization reconciliation is required after major sync incidents.
82. Reconciliation metrics are observable.
83. Critical discrepancies generate alerts.
84. Unresolved discrepancies have an age.
85. Reconciliation failures generate operational alerts.
86. Reconciliation performance must not unnecessarily block POS.
87. Heavy reconciliation uses bounded batches.
88. Reconciliation uses indexed access patterns.
89. Reconciliation avoids unnecessary long locks.
90. Corrections use normal transactional rules.
91. Correction operations use deterministic lock ordering where locks are required.
92. Concurrent corrections cannot silently overwrite each other.
93. Reconciliation retry is bounded.
94. Permanent failures remain visible.
95. Reconciliation job state is durable.
96. Reconciliation results are auditable.
97. Consistency checks are testable.
98. Recovery procedures include consistency validation.
99. Data consistency is prioritized over superficial availability.
100. The final authoritative state must always be explainable and reconstructable.

---

## Related Documents

### Backend Architecture

* `docs/04_Architecture/01_Backend_Architecture.md`
* `docs/04_Architecture/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/07_Transaction_Management.md`
* `docs/04_Architecture/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/11_Configuration_and_Environment_Management.md`
* `docs/04_Architecture/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/19_Backend_Deployment_and_Runtime_Architecture.md`
* `docs/04_Architecture/20_Backend_Operations_and_Incident_Management_Architecture.md`
* `docs/04_Architecture/21_Backend_Disaster_Recovery_and_Business_Continuity_Architecture.md`

### Database

* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/28_Database_Backup_and_Recovery.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/22_Notifications_and_Alerts.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Operations

* `docs/14_Operations/01_Production_Operations.md`
* `docs/14_Operations/02_Monitoring_and_Alerting.md`
* `docs/14_Operations/03_Incident_Response.md`
* `docs/14_Operations/04_Backup_and_Restore.md`
* `docs/14_Operations/05_Disaster_Recovery.md`

---

## Status

**Backend Architecture Document:** Completed.

**Document Status:** Proposed.

**Current Document:** `22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`

**Next Document:** `23_Backend_Audit_and_History_Architecture.md`

