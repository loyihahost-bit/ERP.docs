# Backend Audit and History Architecture

**Document ID:** BE-23
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This document defines the backend architecture for audit records, historical records, change history, correction history and traceability.

The system must make important business and security actions traceable without allowing historical records to be silently modified or deleted.

Audit and history must support:

* accountability;
* financial traceability;
* security investigation;
* business correction;
* offline synchronization;
* configuration history;
* inventory history;
* report history;
* subscription lifecycle;
* compliance and operational investigation.

Audit and history must not become a performance bottleneck for normal POS operations.

---

## 2. Scope

This document covers:

* business audit;
* security audit;
* change history;
* transaction history;
* correction history;
* configuration history;
* inventory history;
* financial history;
* offline synchronization history;
* actor attribution;
* device attribution;
* operation attribution;
* immutable records;
* audit event structure;
* history reconstruction;
* retention;
* querying;
* indexing;
* archival;
* access control;
* audit integrity;
* background processing;
* performance;
* monitoring;
* recovery;
* reconciliation;
* system invariants.

---

## 3. Audit and History Principles

The backend follows these principles:

1. Important business actions must be attributable.
2. Security-sensitive actions must be auditable.
3. Historical records must be immutable.
4. Corrections must create new records rather than silently changing history.
5. Audit records must identify the responsible actor where applicable.
6. Device context must be retained for important operational actions.
7. Business and Branch scope must be explicit.
8. Client-provided audit information is not authoritative.
9. Server-generated audit context is authoritative.
10. Audit creation must be atomic with the business operation when the audit is mandatory.
11. Secondary audit processing must not block critical POS operations unnecessarily.
12. Audit records must never grant permissions.
13. History must remain reconstructable.
14. Deleting current data must not silently erase required historical evidence.
15. Audit queries must respect Business and Branch authorization.
16. Offline operations must retain their original operation identity and source.
17. Synchronization must not create duplicate audit records.
18. Audit failures must be observable.
19. Audit storage must be protected from ordinary application modification.
20. Historical integrity has priority over UI convenience.

---

## 4. Audit vs History

Audit and history are related but different concepts.

### 4.1. Audit

Audit answers:

> Who performed what action, where, when, from which device and with what result?

Examples:

* employee changed Product price;
* Manager changed permissions;
* Owner approved a Recipe;
* Cashier closed a Cash Session;
* employee requested a refund;
* employee exported a report;
* device was revoked.

### 4.2. History

History answers:

> How did a business object or transaction change over time?

Examples:

* Product price history;
* Order status history;
* Recipe Version history;
* Configuration Version history;
* Cash Session history;
* inventory transaction history;
* subscription lifecycle history;
* correction history.

A business operation may therefore produce both:

```text
Business Operation
      ↓
Current State Change
      ↓
History Record
      ↓
Audit Event
```

Not every technical change requires a separate user-facing history record, and not every history record is itself a security audit event.

---

## 5. Audit Categories

The system uses the following logical audit categories:

```text
BUSINESS_AUDIT
SECURITY_AUDIT
CONFIGURATION_AUDIT
FINANCIAL_AUDIT
INVENTORY_AUDIT
ORDER_AUDIT
ACCESS_AUDIT
DEVICE_AUDIT
SUBSCRIPTION_AUDIT
SYNCHRONIZATION_AUDIT
SYSTEM_AUDIT
EXPORT_AUDIT
LIFECYCLE_AUDIT
```

The category must be queryable without requiring application-specific interpretation of free-form text.

---

## 6. Business Audit

Business audit records important business operations.

Examples:

* Product activation/deactivation;
* price change;
* Branch menu change;
* Recipe approval;
* Set configuration change;
* inventory adjustment;
* cash correction;
* refund;
* payroll modification;
* employee permission change;
* Business configuration change.

Routine read operations do not require business audit unless explicitly classified as sensitive.

---

## 7. Security Audit

Security audit records security-sensitive actions and security events.

Examples:

* successful authentication;
* failed authentication where required;
* session revocation;
* device registration;
* device verification;
* trusted device revocation;
* permission escalation attempt;
* unauthorized access attempt;
* invalid offline signature;
* expired offline authorization;
* suspicious replay;
* synchronization authentication failure;
* security policy violation.

Security audit must be separated logically from ordinary business history.

---

## 8. Change History

Change history records meaningful state transitions.

Example:

```text
Product Price

30,000
   ↓
32,000
   ↓
35,000
```

Each state transition must remain reconstructable.

The current value alone is insufficient to reconstruct historical state.

---

## 9. Correction History

Corrections must never silently rewrite historical records.

Example:

```text
Original Cash Closing
        ↓
Correction Request
        ↓
Authorized Correction
        ↓
New Corrected State
```

The original state remains available.

The correction references the original record.

---

## 10. Historical Immutability

Historical audit and history records are immutable after creation.

The system must not allow ordinary update operations such as:

```text
UPDATE audit_log SET ...
```

for business correction purposes.

If a historical interpretation is wrong, the system creates a new correction or clarification record.

The original event remains unchanged.

---

## 11. Audit Event Identity

Every audit event receives a unique Event UUID.

Example:

```text
event_id = UUID
```

Event UUID must be globally unique within the system.

The same Event UUID must not represent two different audit events.

---

## 12. Operation Identity

Audit records must retain the operation UUID when the business operation is command-based.

Example:

```text
operation_id
    ↓
Order Acceptance
    ↓
Audit Event
```

This allows the system to correlate:

* API request;
* business operation;
* database transaction;
* audit event;
* outbox event;
* synchronization result.

---

## 13. Request Identity

Where applicable, audit records should retain:

* request_id;
* operation_id;
* correlation_id.

`request_id` identifies the request execution.

`operation_id` identifies the business operation.

The two values must not be treated as interchangeable.

---

## 14. Actor Attribution

Where a human performs an action, the audit record should contain:

* Employee UUID;
* employee role context where required;
* Business UUID;
* Branch UUID where applicable;
* permission context where required.

The server derives actor identity from authenticated context.

The client must not be trusted to declare the actor.

---

## 15. System Actor

Some operations are performed by the system.

Examples:

* subscription lifecycle transition;
* scheduled report generation;
* automatic reconciliation;
* background cleanup;
* data deletion;
* synchronization processing;
* retry processing.

These events use an explicit system actor identity.

The system must not falsely attribute system operations to a human employee.

---

## 16. Device Attribution

Important operational audit events should contain Device UUID where applicable.

This is particularly important for:

* POS operations;
* offline transactions;
* cash operations;
* authentication;
* device registration;
* configuration changes;
* synchronization.

Device UUID identifies the device context and is not itself an authentication credential.

---

## 17. Cash Context

Cash-related audit records should contain:

* Cash Register UUID;
* Cash Session UUID;
* Employee UUID;
* Branch UUID;
* Device UUID where applicable.

This allows the system to answer:

> Which cashier, on which register, during which session, from which device, performed this action?

---

## 18. Order Context

Order-related audit records may contain:

* Order UUID;
* Order number;
* Branch UUID;
* Cash Session UUID;
* Employee UUID;
* Device UUID;
* operation UUID.

The stable Order UUID is authoritative for correlation.

Customer-facing Order numbers are not sufficient as unique technical identifiers.

---

## 19. Audit Event Structure

A logical audit event contains:

```text
AuditEvent
├── event_id
├── event_type
├── category
├── action
├── result
├── actor_type
├── employee_id
├── business_id
├── branch_id
├── device_id
├── cash_register_id
├── cash_session_id
├── order_id
├── operation_id
├── request_id
├── source
├── occurred_at
├── recorded_at
├── entity_type
├── entity_id
├── before_state_reference
├── after_state_reference
├── reason
├── metadata
└── integrity_metadata
```

Not every field is required for every event.

---

## 20. Event Type

`event_type` must identify a stable machine-readable event.

Examples:

```text
ORDER_CREATED
ORDER_ACCEPTED
ORDER_CANCELLED
PAYMENT_COMPLETED
REFUND_CREATED
CASH_SESSION_OPENED
CASH_SESSION_CLOSED
CASH_CORRECTION_CREATED
PRICE_CHANGED
MENU_AVAILABILITY_CHANGED
RECIPE_APPROVED
INVENTORY_ADJUSTED
EMPLOYEE_PERMISSION_CHANGED
DEVICE_REVOKED
REPORT_EXPORTED
SUBSCRIPTION_EXPIRED
BUSINESS_DELETION_STARTED
```

Event names must remain stable after production use.

---

## 21. Action

`action` describes the operation performed.

Examples:

```text
CREATE
UPDATE
APPROVE
REJECT
CLOSE
OPEN
TRANSFER
REFUND
CORRECT
REVOKE
EXPORT
SYNC
DELETE
ARCHIVE
```

The exact event type remains the primary machine-readable identifier.

---

## 22. Result

Audit events must record the result where useful.

Possible values:

```text
SUCCESS
REJECTED
FAILED
CONFLICT
DUPLICATE
CANCELLED
```

A failed request that never reached the business transaction may belong to security/application logging rather than mandatory business audit.

---

## 23. Source

Audit events identify their source.

Possible values:

```text
WEB
POS
OFFLINE
SYNC
BACKGROUND_JOB
SYSTEM
API
ADMIN
```

Source must not override authenticated actor context.

For example:

```text
source = OFFLINE
employee_id = authenticated employee
device_id = trusted device
```

---

## 24. Timestamp Model

The system must distinguish:

* `occurred_at`;
* `recorded_at`.

`occurred_at` represents when the business action occurred according to the authoritative processing context.

For offline events, the client event time may be retained separately as source metadata.

`recorded_at` represents when the server recorded the audit event.

Server time remains authoritative for server-side ordering.

---

## 25. Offline Audit

Offline transactions must retain:

* operation UUID;
* device UUID;
* employee UUID;
* local event timestamp;
* server receipt timestamp;
* synchronization batch UUID;
* synchronization result.

Example:

```text
Offline Order
    ↓
Local Audit
    ↓
Sync
    ↓
Server Validation
    ↓
Server Audit
```

The synchronization process must not create a second independent business operation for the same operation UUID.

---

## 26. Offline Time Integrity

Offline event time must not be blindly trusted.

The server must validate:

* offline authorization validity;
* device validity;
* allowed offline period;
* clock rollback/tampering signals;
* event ordering where required.

Suspicious timestamps may be retained as metadata while server processing time remains authoritative.

---

## 27. Audit and Idempotency

Audit creation must respect operation idempotency.

If the same operation is retried:

```text
Operation UUID A
        ↓
First request → Audit Event A
        ↓
Retry         → No duplicate business audit
```

A retry may generate a technical retry log, but it must not create duplicate business effects.

---

## 28. Atomic Audit

For mandatory audit events, audit creation must occur in the same database transaction as the business state change.

Example:

```text
BEGIN
    update price
    create price history
    create audit event
COMMIT
```

If the transaction fails:

```text
Price change = not committed
Audit event  = not committed
```

This prevents an audit record from claiming a successful operation that never committed.

---

## 29. Secondary Audit Processing

Some secondary processing may happen asynchronously.

Examples:

* audit analytics;
* external security monitoring;
* long-term archival;
* search indexing;
* aggregation.

These operations must not alter the authoritative audit record.

The primary audit record is committed first.

---

## 30. Outbox Integration

When an audit event must trigger asynchronous processing, the event may be published through the Outbox pattern.

Example:

```text
Business Transaction
       │
       ├── Current State
       ├── History
       ├── Audit Event
       └── Outbox Event
              ↓
          Background Job
              ↓
      Secondary Processing
```

The outbox event and mandatory audit state must be committed atomically where required.

---

## 31. Audit Failure Handling

If mandatory audit creation fails, the corresponding critical business transaction must fail rather than silently commit without required audit evidence.

For non-critical secondary audit processing:

* retry;
* monitor;
* alert;
* preserve the primary event.

The system must distinguish mandatory audit failure from secondary audit delivery failure.

---

## 32. Financial Audit

Financial operations require strong auditability.

Examples:

* payment;
* refund;
* discount;
* cash session close;
* cash discrepancy;
* cash correction;
* debt operation;
* payroll modification.

Financial audit must preserve:

* original amount;
* resulting amount where applicable;
* currency;
* reason;
* actor;
* Branch;
* transaction reference;
* correction reference where applicable.

---

## 33. Inventory Audit

Inventory audit must support reconstruction of stock changes.

Examples:

* purchase;
* stock receipt;
* manual adjustment;
* stock count;
* recipe deduction;
* waste;
* correction;
* transfer.

Inventory history must use immutable Inventory Transactions rather than repeatedly rewriting a historical quantity.

---

## 34. Order History

Order history must preserve meaningful lifecycle transitions.

Example:

```text
DRAFT
  ↓
ACCEPTED
  ↓
PREPARING
  ↓
READY
  ↓
COMPLETED
```

Each important transition may produce:

* Order status history;
* audit event where required.

Historical status must remain reconstructable.

---

## 35. Payment History

Payment history must preserve:

* payment identity;
* amount;
* method;
* status;
* Order reference;
* actor;
* timestamp;
* correction/refund relationship.

A completed payment must not be silently rewritten into another payment.

Corrections use dedicated financial mechanisms.

---

## 36. Cash History

Cash history must preserve:

* opening;
* closing;
* expected amount;
* actual amount;
* discrepancy;
* handover;
* correction;
* responsible employee;
* Cash Session;
* timestamps.

Closed Cash Sessions remain historical records.

---

## 37. Configuration History

Configuration changes must create reconstructable history.

Examples:

* menu;
* price;
* permissions;
* branch configuration;
* subscription settings;
* payroll settings;
* printer routing;
* notification thresholds.

Configuration history must preserve version identity.

A configuration rollback creates a new version rather than deleting newer history.

---

## 38. Permission History

Permission changes are security-sensitive.

History must identify:

* employee;
* role;
* previous permission state;
* new permission state;
* Branch scope;
* actor;
* timestamp;
* reason where required.

A Manager must not be able to create an audit record implying authority beyond their own permissions.

---

## 39. Device History

Device history must preserve:

* registration;
* verification;
* trust state;
* revocation;
* replacement;
* security events.

Example:

```text
REGISTERED
   ↓
VERIFIED
   ↓
TRUSTED
   ↓
REVOKED
```

Device history is separate from employee permission history.

---

## 40. Subscription History

Subscription lifecycle changes must be auditable.

Examples:

```text
ACTIVE
  ↓
EXPIRING
  ↓
EXPIRED
  ↓
READ_ONLY
  ↓
DELETION_ELIGIBLE
  ↓
DELETING
  ↓
DELETED
```

Each lifecycle transition must be attributable to either an authorized employee or system actor.

---

## 41. Data Deletion History

Permanent Business deletion is a high-risk operation.

The system must retain sufficient lifecycle metadata to establish:

* deletion eligibility;
* notification;
* authorization;
* deletion start;
* deletion completion;
* deletion reason;
* system job identity.

Deleted business data itself may no longer be queryable after the retention policy completes, but required deletion evidence must follow the approved lifecycle policy.

---

## 42. Report History

Reports are versioned and immutable.

Audit must record important report operations such as:

* report generated;
* report version created;
* report exported;
* report downloaded where required;
* report regeneration;
* report correction/version creation.

Historical report versions must not be silently replaced.

---

## 43. Export Audit

Exports can contain sensitive Business data.

Export operations should be auditable.

Example:

```text
Employee
   ↓
Requests XLSX
   ↓
Authorization
   ↓
Export Job
   ↓
File Created
   ↓
Audit Event
```

The audit record should identify:

* report;
* report version;
* exporter;
* Business;
* Branch scope;
* export format;
* file/reference ID where appropriate;
* timestamp;
* result.

---

## 44. File and Document History

Important generated documents must retain:

* document identity;
* version;
* creator/system source;
* related Business/Branch;
* related report/configuration;
* creation time;
* storage reference.

File deletion must not automatically imply deletion of the business history that referenced it.

---

## 45. Audit Access Control

Audit data is sensitive.

Access must require explicit permission.

Example permissions:

```text
audit.view
audit.view_security
audit.view_financial
audit.export
history.view
history.export
```

Exact permissions may be adjusted by the general permission model.

---

## 46. Business Isolation

Audit queries must always respect Business scope.

A user from Business A must never retrieve audit events belonging to Business B.

This rule applies to:

* API;
* application services;
* repositories;
* reporting;
* exports;
* background jobs.

---

## 47. Branch Isolation

Branch-scoped audit data must respect Branch permissions.

An employee with Branch A access must not automatically see Branch B audit history.

All-Branch permissions may permit cross-Branch visibility.

The system must still retain the exact Branch identity in each event.

---

## 48. Super Admin Audit

Super Admin actions are platform-level operations.

They must be distinguishable from Business employee actions.

Examples:

* Business creation;
* tariff configuration;
* subscription administration;
* Business lifecycle action;
* platform-level access operation.

Super Admin must not appear as an ordinary Business employee in audit history.

---

## 49. Audit Data Minimization

Audit records must contain enough information for traceability but should not duplicate large business objects unnecessarily.

Do not store full copies of:

* complete Order objects;
* complete Product objects;
* large images;
* file contents;
* unnecessary personal data

inside every audit event.

Use references and targeted snapshots where required.

---

## 50. Before and After State

For important configuration and financial changes, the system may retain structured before/after values.

Example:

```text
before:
{
    "price": 30000
}

after:
{
    "price": 32000
}
```

Only relevant fields should be captured.

Sensitive fields must be redacted or excluded.

---

## 51. Sensitive Data Protection

Audit records must not contain:

* plaintext passwords;
* authentication secrets;
* access tokens;
* private signing keys;
* encryption keys;
* unnecessary payment credentials;
* sensitive data not required for traceability.

Security-sensitive values must be represented safely.

---

## 52. Audit Integrity

Audit records must be protected against unauthorized modification.

Protection includes:

* database permissions;
* application-level immutability;
* restricted repository methods;
* append-only service behavior;
* integrity metadata where justified;
* monitoring;
* backup protection.

Audit integrity mechanisms must not impose unnecessary latency on POS operations.

---

## 53. Append-Only Model

Audit history should follow an append-only model.

Normal operations:

```text
INSERT
```

are allowed.

Normal historical mutation:

```text
UPDATE
DELETE
```

is prohibited.

Administrative maintenance must use controlled infrastructure-level procedures and must itself be auditable.

---

## 54. Audit Partitioning

As audit volume grows, the audit table may require partitioning.

Possible partition strategies:

* time-based partitioning;
* Business-aware partitioning where operationally justified;
* archival partitions.

Partitioning must not weaken Business isolation.

The initial implementation may use a normal indexed table until measured volume justifies partitioning.

---

## 55. Audit Index Strategy

Important indexes may include:

```text
(business_id, occurred_at)
(business_id, branch_id, occurred_at)
(business_id, entity_type, entity_id, occurred_at)
(business_id, employee_id, occurred_at)
(business_id, operation_id)
(business_id, event_type, occurred_at)
(device_id, occurred_at)
```

Exact indexes must be validated against real query patterns.

Over-indexing must be avoided because every audit insert pays index maintenance cost.

---

## 56. History Query Strategy

Common history queries must be optimized.

Examples:

```text
Product price history
Order status history
Employee permission history
Cash Session history
Inventory transaction history
Configuration version history
```

History queries should use:

* indexed identifiers;
* bounded date ranges;
* pagination;
* projections;
* deterministic ordering.

Unbounded audit queries are prohibited in normal API requests.

---

## 57. Pagination

Audit and history APIs must use bounded pagination.

Preferred approach:

```text
cursor-based pagination
```

for large history collections.

Offset pagination may be used for small administrative lists where performance is acceptable.

The API must not return an unbounded audit collection.

---

## 58. Ordering

History results must have deterministic ordering.

Recommended ordering:

```text
occurred_at
+
event_id
```

or another stable unique tie-breaker.

Timestamp alone is insufficient when multiple events may occur at the same time.

---

## 59. History Reconstruction

The system must be able to reconstruct relevant historical state from:

* immutable history records;
* version records;
* transaction records;
* audit records;
* correction chains.

Current state must not be the only source needed to understand historical operations.

---

## 60. Correction Chain

Corrections should use explicit references.

Example:

```text
Original Event A
      ↓
Correction B
      ↓
Correction C
```

Each correction retains:

* original reference;
* previous correction where applicable;
* correcting actor;
* reason;
* timestamp;
* resulting state.

The chain must remain traversable.

---

## 61. No Silent Historical Mutation

The following behavior is prohibited:

```text
Original price 30,000
       ↓
UPDATE old record
       ↓
Historical record now says 35,000
```

Correct behavior:

```text
Original price 30,000
       ↓
New correction/version
       ↓
Current price 35,000
```

---

## 62. Audit and Reconciliation

The reconciliation subsystem may validate audit consistency.

Examples:

* committed payment without required audit;
* audit claiming success without committed transaction;
* duplicate audit event for one operation;
* history version missing;
* correction referencing missing original record.

These are reconciliation anomalies.

They must be classified and handled according to:

`22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`.

---

## 63. Audit Reconciliation

A reconciliation job may verify:

```text
Business State
      ↕
History
      ↕
Audit
      ↕
Outbox
```

The job must not rewrite historical records automatically unless a deterministic repair mechanism exists.

Ambiguous discrepancies require investigation.

---

## 64. Audit and Synchronization

Synchronization must preserve audit relationships.

For an offline operation:

```text
local_operation_id
        ↓
sync_batch_id
        ↓
server_operation_id
        ↓
audit_event_id
```

The system must retain enough identifiers to trace the operation from device to server.

---

## 65. Duplicate Synchronization

If an offline operation is synchronized more than once:

* the operation UUID is checked;
* duplicate business effect is prevented;
* duplicate audit effect is prevented;
* synchronization result is recorded.

The system may return:

```text
DUPLICATE
```

without creating a second business history chain.

---

## 66. Failed Synchronization

If synchronization fails before business commit:

* no successful business audit must be created;
* technical failure information may be logged;
* retry must preserve the original operation UUID.

If the business operation committed but response delivery failed, retry must resolve through idempotency rather than creating another history record.

---

## 67. Background Job Audit

Important background jobs should have explicit system identity.

Examples:

* reconciliation;
* deletion;
* report generation;
* notification processing;
* subscription lifecycle;
* configuration synchronization.

The audit should identify:

* job type;
* job execution UUID;
* system actor;
* result;
* affected Business/Branch where applicable.

---

## 68. Audit and Notifications

Audit creation must not depend on notification delivery.

Example:

```text
Price Change
   ↓
Audit committed
   ↓
Notification queued
```

If notification fails:

```text
Audit = preserved
Notification = retryable failure
```

Notification failure must not remove the audit record.

---

## 69. Audit and Printing

Printing is not part of the audit transaction unless explicitly required.

Example:

```text
Order Accepted
   ↓
Order + Inventory + Audit committed
   ↓
Print Job created
```

Printer failure does not erase Order history or audit history.

---

## 70. Audit and Reporting

Reports may query audit/history data through dedicated read models or optimized queries.

Heavy audit analysis must not block POS transactions.

Long-running historical reports should run as background jobs.

---

## 71. Audit Export

Audit exports must themselves be audited.

Example:

```text
Employee requests audit export
        ↓
Authorization
        ↓
Export created
        ↓
Export Audit Event
```

An employee must not be able to erase evidence by exporting or downloading it.

---

## 72. Retention

Audit and history retention follows Business lifecycle and applicable operational policy.

The system must distinguish:

* live history;
* archived history;
* deleted Business data;
* legally/operationally required retention;
* backup retention.

Retention policy must be explicit.

---

## 73. Subscription Expiry

Subscription expiry does not immediately erase audit/history data.

During read-only state:

* history remains viewable according to permissions;
* audit remains available;
* exports allowed by policy remain available;
* modifying operations are blocked.

---

## 74. Business Deletion

When Business deletion becomes eligible:

1. deletion notification is completed according to lifecycle rules;
2. deletion process begins;
3. live Business data is deleted in controlled batches;
4. required deletion lifecycle evidence is retained according to policy;
5. backup copies follow backup retention policy.

Deletion must not be implemented through uncontrolled cascade operations.

---

## 75. Backup and Restore

Audit/history data must be included in database backups.

Restore testing must verify:

* audit records are present;
* history chains remain valid;
* Event UUID uniqueness is preserved;
* Business/Branch scope remains correct;
* correction references remain valid;
* timestamps remain intact.

---

## 76. Audit Security

Access to audit/history must be protected by:

* authentication;
* authorization;
* Business scope;
* Branch scope;
* subscription state;
* least privilege.

Audit records must not become an alternative path to privileged information.

---

## 77. Audit Performance

Audit must not significantly slow critical POS operations.

Mandatory audit records should use efficient inserts and avoid:

* large payloads;
* synchronous external API calls;
* expensive serialization;
* network calls;
* unbounded calculations.

Historical analysis belongs outside the critical transaction path.

---

## 78. Audit SLOs

Initial service-level objectives:

| Metric                                            |                       Target |
| ------------------------------------------------- | ---------------------------: |
| Mandatory audit creation success                  |                      ≥99.99% |
| Critical audit persistence latency overhead       |                   p95 ≤50 ms |
| Normal authenticated audit query                  |                  p95 ≤300 ms |
| Audit authorization decision                      |                  p95 ≤100 ms |
| Critical audit visibility in monitoring           |                        ≤60 s |
| Duplicate audit prevention                        |                      ≥99.99% |
| Cross-Business audit access prevention            |                         100% |
| Cross-Branch unauthorized audit access prevention |                         100% |
| Audit integrity violation detection               |                       ≤5 min |
| Audit reconciliation detection                    | ≤60 s for critical anomalies |
| Export audit creation                             |                      ≥99.99% |
| Audit API availability                            |               ≥99.9% monthly |

These targets are initial engineering SLOs and must be validated through load testing and production measurements.

---

## 79. Monitoring

The backend must monitor:

### Audit

* audit event creation rate;
* audit insertion latency;
* failed audit writes;
* duplicate events;
* missing mandatory audit;
* audit query latency;
* audit authorization failures.

### History

* history creation rate;
* correction chains;
* invalid references;
* missing versions;
* history query latency.

### Integrity

* unexpected update attempts;
* unexpected delete attempts;
* cross-Business access attempts;
* cross-Branch access attempts;
* audit reconciliation anomalies.

---

## 80. Alerts

Critical alerts include:

* mandatory audit write failures;
* audit storage unavailable;
* suspected audit modification;
* cross-Business access violation;
* cross-Branch access violation;
* duplicate financial audit anomaly;
* missing payment audit;
* missing refund audit;
* broken correction chain;
* unexpected historical deletion;
* audit reconciliation failure.

---

## 81. Logging

Application logs and audit records serve different purposes.

### Application logs

Used for:

* debugging;
* performance;
* infrastructure diagnosis;
* runtime errors.

### Audit records

Used for:

* accountability;
* business traceability;
* security investigation;
* historical reconstruction.

Application logs must not be treated as a replacement for audit.

Audit records must not be treated as general-purpose debug logs.

---

## 82. Error Handling

Audit-related errors are classified as:

```text
AUDIT_VALIDATION_ERROR
AUDIT_AUTHORIZATION_ERROR
AUDIT_PERSISTENCE_ERROR
AUDIT_CONFLICT
AUDIT_INTEGRITY_ERROR
AUDIT_RECONCILIATION_ERROR
AUDIT_STORAGE_ERROR
```

Mandatory audit persistence errors may cause the parent business transaction to fail.

Secondary audit delivery errors may be retried asynchronously.

---

## 83. Recovery

Recovery mechanisms include:

* database transaction rollback;
* retry;
* outbox replay;
* reconciliation;
* backup restore;
* correction chain;
* audit integrity verification.

Recovery must not rewrite successful historical events merely to make the database appear consistent.

---

## 84. Repository Rules

Audit repositories must provide append-oriented operations.

Example conceptual interface:

```text
append_event(...)
get_event(...)
list_events(...)
find_by_operation(...)
find_by_entity(...)
```

The repository must not expose ordinary:

```text
update_event(...)
delete_event(...)
```

methods for normal application use.

---

## 85. Application Layer Rules

The Application layer decides:

* when audit is mandatory;
* which event type applies;
* which actor context is used;
* which Business/Branch scope applies;
* which history record is created;
* which correction relationship is required.

The Domain layer owns business rules.

The Infrastructure layer persists audit/history data.

---

## 86. API Rules

API routes must not create audit rows directly.

Correct flow:

```text
API
 ↓
Application Use Case
 ↓
Domain Operation
 ↓
Repository / Unit of Work
 ↓
Audit + History
 ↓
Commit
```

This prevents different API endpoints from implementing inconsistent audit behavior.

---

## 87. Domain Events

Domain events may represent business state transitions.

They are not automatically equivalent to persisted audit records.

For critical traceability:

```text
Domain Event
      ↓
Application Policy
      ↓
Audit Record
```

The system must explicitly decide which domain events require durable audit.

---

## 88. Security Event Separation

Security monitoring may generate events that do not belong in Business history.

For example:

```text
Invalid password attempt
```

may be primarily a security event.

Whereas:

```text
Employee permission changed
```

is both a security-sensitive business operation and a Business history event.

The system must avoid duplicating the same information unnecessarily.

---

## 89. Audit Metadata

Metadata must use structured fields rather than arbitrary text whenever the value is operationally important.

Bad:

```text
metadata = "something changed"
```

Better:

```text
metadata = {
    "permission": "inventory.adjust",
    "scope": "branch"
}
```

Metadata schemas must remain bounded and versionable.

---

## 90. Audit Schema Version

If the structure of audit metadata changes, the event schema version should be retained.

Example:

```text
schema_version = 1
```

Older events remain readable.

Schema evolution must not require rewriting historical records.

---

## 91. Audit Correlation

The system should allow investigation through:

```text
Business
 ↓
Branch
 ↓
Employee
 ↓
Device
 ↓
Cash Session
 ↓
Order
 ↓
Payment
 ↓
Correction
 ↓
Audit Event
```

Correlation identifiers must be stable and indexed where necessary.

---

## 92. Investigation Workflow

A typical investigation should be possible as:

```text
1. Find entity
2. Find entity history
3. Find related operation
4. Find audit event
5. Identify actor
6. Identify device
7. Identify Branch
8. Inspect correction chain
9. Inspect related financial/inventory events
10. Inspect synchronization information
```

Investigation must not require direct database access for normal authorized administrative users.

---

## 93. Audit UI Support

Backend APIs should support administrative UI features such as:

* event list;
* event detail;
* entity history;
* actor history;
* correction chain;
* configuration version history;
* security event history;
* filters;
* date ranges;
* Branch filters;
* event type filters.

UI convenience must not weaken authorization.

---

## 94. Search and Filtering

Audit search should support bounded filters:

* date range;
* Business;
* Branch;
* employee;
* device;
* event type;
* entity;
* operation UUID;
* source;
* result.

Free-text search may be provided as a secondary feature but must not replace structured filters.

---

## 95. Audit Detail

Audit detail should expose only information the requesting employee is authorized to view.

Sensitive metadata must be masked where required.

Example:

```text
Password → [REDACTED]
Token → [REDACTED]
```

Sensitive values must never be recoverable from audit output.

---

## 96. Concurrency

Concurrent business operations may produce multiple audit events.

The system must preserve:

* transaction ordering where authoritative;
* timestamps;
* unique event IDs;
* operation IDs.

Audit consumers must not assume that timestamp alone determines causal order.

---

## 97. Transaction Ordering

Where ordering is business-critical, the system should use the authoritative transaction or version sequence.

Examples:

* configuration version;
* Order status sequence;
* inventory transaction sequence;
* correction sequence.

Audit timestamps alone are insufficient for reconstructing all business causality.

---

## 98. Cross-Business Protection

Every audit query and history query must apply Business scope.

Repository-level protections should provide defense in depth.

A valid Event UUID alone must not allow access across Business boundaries.

---

## 99. Cross-Branch Protection

Branch-scoped audit/history queries must validate Branch permissions.

A user may have:

```text
Branch A → allowed
Branch B → denied
```

The backend must enforce this independently of UI filtering.

---

## 100. System Invariants

The following invariants apply to Audit and History:

1. Every mandatory audit event has a unique Event UUID.
2. Event UUID cannot represent two different events.
3. Important business operations are auditable.
4. Security-sensitive operations are auditable.
5. Historical records are immutable.
6. Corrections create new records.
7. Corrections do not overwrite original records.
8. Correction chains remain traversable.
9. Audit records retain Business scope where applicable.
10. Branch-scoped records retain Branch identity.
11. Client-provided actor identity is not authoritative.
12. Server authentication context determines actor identity.
13. System operations use explicit system identity.
14. Important POS operations retain Device identity.
15. Cash operations retain Cash Session identity where applicable.
16. Order operations retain Order identity where applicable.
17. Operation UUID is retained where applicable.
18. Request UUID and operation UUID are not interchangeable.
19. Mandatory audit is atomic with its business transaction.
20. Failed transactions do not create false successful audit records.
21. Duplicate operations do not create duplicate business audit effects.
22. Offline operations retain original operation identity.
23. Synchronization does not create duplicate business history.
24. Server processing time remains authoritative for server ordering.
25. Client offline time is not blindly trusted.
26. Mandatory audit does not depend on notification delivery.
27. Mandatory audit does not depend on printer availability.
28. Audit does not grant permissions.
29. Audit access requires authorization.
30. Audit access respects Business scope.
31. Audit access respects Branch scope.
32. Super Admin events are distinguishable from Business employee events.
33. Audit records do not store plaintext passwords.
34. Audit records do not store authentication secrets.
35. Audit records do not store private cryptographic keys.
36. Audit records minimize unnecessary sensitive data.
37. Large business objects are not duplicated unnecessarily in every audit event.
38. Before/after data is limited to relevant fields.
39. Audit metadata is structured where operationally important.
40. Audit schema versions are preserved.
41. Historical schema versions are not rewritten.
42. Audit repository does not expose normal update operations.
43. Audit repository does not expose normal delete operations.
44. API routes do not directly create audit records.
45. Application layer controls audit policy.
46. Domain rules remain independent from persistence.
47. Infrastructure persists audit records.
48. Outbox may be used for secondary audit processing.
49. Secondary audit failure does not invalidate committed business state.
50. Mandatory audit failure may fail the parent transaction.
51. Audit queries are bounded.
52. Audit APIs use pagination.
53. History ordering is deterministic.
54. Timestamp alone is not assumed to provide causal ordering.
55. Business version sequences are used where ordering is critical.
56. Audit indexes support common investigation queries.
57. Audit indexes are not created without measured query value.
58. Audit performance does not unnecessarily block POS operations.
59. Audit queries do not execute unbounded scans in normal requests.
60. Heavy historical analysis runs asynchronously where required.
61. Audit exports are themselves auditable.
62. Exported audit data remains protected.
63. Report versions referenced by audit remain immutable.
64. Configuration versions referenced by audit remain immutable.
65. Inventory history uses immutable transaction records.
66. Financial corrections use dedicated financial mechanisms.
67. Historical payment state is not silently rewritten.
68. Historical refund state is not silently rewritten.
69. Historical cash state is not silently rewritten.
70. Historical Order prices remain immutable.
71. Historical Recipe Versions remain immutable.
72. Historical Set Versions remain immutable.
73. Permission history remains attributable.
74. Device history remains attributable.
75. Subscription lifecycle history remains attributable.
76. Business deletion does not use uncontrolled cascade deletion.
77. Required deletion lifecycle evidence follows retention policy.
78. Backup restore preserves audit identity.
79. Backup restore preserves correction relationships.
80. Reconciliation can detect missing mandatory audit.
81. Reconciliation can detect duplicate audit effects.
82. Reconciliation can detect broken correction references.
83. Reconciliation does not silently rewrite ambiguous history.
84. Audit integrity violations are observable.
85. Unauthorized historical modification attempts are observable.
86. Cross-Business access violations are blocked.
87. Cross-Branch unauthorized access is blocked.
88. Audit data cannot be used as a privilege escalation path.
89. Audit consumers do not assume timestamp-only causal order.
90. Background jobs have explicit system identity.
91. Job execution UUID is retained where applicable.
92. Synchronization retains enough identifiers for end-to-end tracing.
93. Duplicate synchronization does not create duplicate history.
94. Failed synchronization does not create false successful audit.
95. Committed synchronization followed by lost response resolves through idempotency.
96. Audit events remain queryable according to lifecycle policy.
97. Read-only subscription state does not erase history.
98. Current state alone is not the only source for historical reconstruction.
99. Historical integrity has priority over UI convenience.
100. Audit architecture must remain scalable without weakening traceability or POS performance.

---

## 101. Recommended Backend Structure

```text
app/
├── application/
│   ├── audit/
│   │   ├── commands/
│   │   ├── queries/
│   │   ├── services/
│   │   └── policies/
│   ├── history/
│   │   ├── queries/
│   │   ├── services/
│   │   └── reconstruction/
│   └── ...
│
├── domain/
│   ├── audit/
│   ├── history/
│   └── ...
│
├── infrastructure/
│   ├── database/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── migrations/
│   ├── audit/
│   │   ├── repository.py
│   │   ├── serialization.py
│   │   └── integrity.py
│   └── ...
│
├── background/
│   ├── audit/
│   ├── reconciliation/
│   └── ...
│
├── reporting/
│   ├── audit/
│   └── history/
│
└── shared/
    ├── identifiers/
    ├── time/
    └── errors/
```

The exact directory structure may evolve with implementation, but the architectural boundaries must remain.

---

## 102. Database Considerations

Audit/history tables should use:

* UUID identifiers;
* explicit Business scope;
* Branch scope where applicable;
* indexed entity references;
* indexed operation UUID;
* immutable timestamps;
* schema version;
* structured event type;
* bounded metadata.

Foreign-key behavior must be designed carefully for Business lifecycle deletion.

Historical integrity must not depend on uncontrolled database cascades.

---

## 103. Migration Strategy

Audit schema changes follow normal database migration policy.

Changes should use:

```text
expand
  ↓
deploy compatible code
  ↓
backfill if required
  ↓
switch readers
  ↓
contract later
```

Existing historical records must remain readable.

Destructive migration of audit/history data is prohibited unless explicitly required by an approved retention policy.

---

## 104. Testing Requirements

Testing must cover:

### Unit Tests

* event creation;
* event type mapping;
* actor attribution;
* correction chain;
* metadata validation;
* sensitive-field redaction.

### Integration Tests

* atomic business + audit transaction;
* duplicate operation;
* synchronization;
* Business isolation;
* Branch isolation;
* repository immutability.

### Security Tests

* unauthorized audit access;
* cross-Business access;
* cross-Branch access;
* audit modification attempts;
* sensitive data leakage.

### Recovery Tests

* transaction rollback;
* outbox retry;
* database restore;
* reconciliation;
* broken correction detection.

### Performance Tests

* audit insert throughput;
* POS transaction latency with mandatory audit;
* audit query latency;
* large history pagination;
* concurrent audit writes.

---

## 105. Operational Guardrails

The backend must enforce:

* no direct audit table mutation from ordinary application code;
* no audit deletion through normal API;
* no cross-Business history query;
* no unbounded history API;
* no sensitive secret storage;
* no client-controlled actor attribution;
* no silent correction;
* no silent historical overwrite;
* no audit-dependent external network call inside critical transaction;
* no unbounded metadata payload.

---

## 106. Relationship With Other Backend Documents

This document depends on and extends:

* `01_Backend_Architecture.md`
* `06_Authentication_and_Authorization.md`
* `07_Transaction_Management.md`
* `09_Events_Outbox_and_Background_Jobs.md`
* `10_Notifications_and_External_Integrations.md`
* `14_Backend_Caching_and_Performance_Architecture.md`
* `16_Backend_Security_Hardening_and_Application_Security.md`
* `19_Backend_Deployment_and_Runtime_Architecture.md`
* `22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`

It also relates to:

* Database Audit and History;
* Order and Payment models;
* Cash Session;
* Inventory Transactions;
* Configuration Versions;
* Report Versions;
* Offline Synchronization;
* Data Lifecycle and Deletion.

---

## 107. Related System Analysis Documents

Relevant System Analysis documents include:

* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

Exact filenames must be aligned with the repository's final System Analysis structure.

---

## 108. Status

**Backend Architecture:** In progress.

**Document Status:** Proposed.

**Current Document:** `23_Backend_Audit_and_History_Architecture.md`

**Previous Document:** `22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`

**Next Document:** `24_Backend_Search_and_Filtering_Architecture.md`

