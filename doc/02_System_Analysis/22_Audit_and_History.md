# Audit and History

**Document ID:** SA-22
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for audit records, change history and traceability of important business and system operations.

The audit system must make important state changes explainable and traceable without unnecessarily slowing down daily operations.

Audit records are historical records and must not be silently modified or deleted.

---

## 2. Scope

This document covers:

* audit event identity;
* audit context;
* business and branch scope;
* actor identification;
* device and Cash Session context;
* entity and transaction references;
* old and new state;
* correction chains;
* online and offline audit;
* synchronization;
* audit visibility;
* filtering;
* pagination;
* export;
* sensitive access;
* retention;
* immutability;
* audit reliability;
* audit failure recovery;
* performance;
* system invariants.

---

## 3. Audit Principles

The audit system follows these principles:

1. Important state changes must be traceable.
2. Audit records are immutable.
3. Original business data must not be silently overwritten.
4. Corrections must create separate historical records.
5. Audit records must preserve sufficient context to reconstruct important operations.
6. Audit generation must not unnecessarily block POS.
7. Audit failures must not result in silent loss of required audit information.
8. Authorization is required to view sensitive audit information.
9. Offline operations must remain traceable after synchronization.
10. Business and Branch isolation must always be preserved.

---

## 4. Audit Event Identity

Every audit event has a stable UUID.

The Audit Event UUID is used for:

* unique identification;
* synchronization;
* deduplication;
* correction references;
* history navigation;
* investigation.

An audit event UUID must not be reused for another event.

---

## 5. Audit Event Context

An audit event may contain:

* Event UUID;
* Business UUID;
* Branch UUID;
* Actor Employee UUID;
* Device UUID;
* Cash Session UUID;
* Entity type;
* Entity UUID;
* Transaction UUID;
* timestamp;
* old state;
* new state;
* reason;
* result;
* source.

The exact context depends on the operation.

---

## 6. Business Context

Every business-level audit event must identify its Business.

The Business context prevents audit information from one tenant being exposed to another tenant.

Business isolation applies to:

* API access;
* database queries;
* reports;
* exports;
* background jobs;
* synchronization;
* offline data.

---

## 7. Branch Context

Where an operation is Branch-specific, the audit event must identify the Branch.

Examples include:

* Order;
* Cash Session;
* inventory movement;
* attendance;
* Branch expense;
* Branch configuration.

Business-wide events may have no Branch UUID.

---

## 8. Actor

The actor identifies who or what caused the operation.

Possible actors include:

* Employee;
* SYSTEM.

When an Employee performs an operation, the Employee UUID must be retained.

System-generated events use:

```text id="sys713"
Actor = SYSTEM
```

The system must not attribute an automated operation to an Employee who did not perform it.

---

## 9. Device Context

Where applicable, the audit event records the Device UUID.

This is important for:

* POS operations;
* offline operations;
* payment operations;
* Cash Session operations;
* synchronization;
* security events.

Device identity is separate from Employee identity.

---

## 10. Cash Session Context

Cash-related operations should identify the relevant Cash Session.

Examples include:

* payment;
* cash refund;
* cash correction;
* session opening;
* session closing;
* handover;
* discrepancy correction.

The Cash Session UUID allows the operation to be connected to the correct historical financial context.

---

## 11. Transaction Context

Where an operation belongs to a business transaction, the Transaction UUID should be recorded.

This supports tracing operations such as:

```text id="trace821"
Order
  ↓
Inventory Deduction
  ↓
Payment
  ↓
Audit
```

The transaction reference must remain stable throughout the operation.

---

## 12. Entity Context

The audit event identifies the affected entity.

Examples:

* Order;
* Payment;
* Refund;
* Product;
* Recipe;
* Inventory Movement;
* Cash Session;
* Employee;
* Payroll;
* Report;
* Notification;
* Subscription;
* Device.

Entity type and UUID must be sufficient to locate the relevant historical object within the authorized scope.

---

## 13. Important Operations Requiring Audit

Important business/state-changing operations include, where applicable:

* Order creation;
* Order acceptance;
* Order modification;
* Order cancellation;
* payment creation;
* payment correction;
* refund;
* discount application;
* overpayment confirmation;
* Cash Session opening;
* Cash Session closing;
* Cash correction;
* handover;
* inventory adjustment;
* inventory discrepancy confirmation;
* recipe creation;
* recipe modification;
* recipe approval;
* menu configuration;
* price change;
* Branch price override;
* employee creation;
* employee activation/deactivation;
* permission changes;
* salary configuration changes;
* payroll finalization;
* payroll correction;
* report generation;
* report version creation;
* notification configuration;
* threshold changes;
* device registration;
* device revocation;
* subscription changes;
* deletion lifecycle transitions;
* synchronization conflict resolution.

The complete event catalogue may be extended without changing the audit model.

---

## 14. Ordinary Reads

Ordinary reads do not normally require an audit event.

Examples include:

* opening a normal dashboard;
* viewing a standard menu;
* viewing ordinary order history.

However, sensitive or administrative access may be audited when required.

---

## 15. Sensitive Access

Sensitive operations or data access may require audit records.

Examples include:

* sensitive payroll information;
* administrative configuration;
* security information;
* high-privilege audit access;
* data lifecycle administration.

The requirement is determined by permission and system policy.

---

## 16. Old and New State

For state-changing events, the audit record should preserve both:

* Old State;
* New State.

This allows the system to explain what changed.

Example:

```text id="chg416"
Old:
status = "Accepted"

New:
status = "Preparing"
```

---

## 17. Changed Fields

For large entities, storing complete duplicate snapshots for every event may be unnecessary.

The system may record:

* changed fields;
* old values;
* new values;
* relevant snapshots where required.

The audit representation must remain sufficient to reconstruct important changes.

---

## 18. Sensitive Data

Audit records must avoid unnecessary duplication of sensitive data.

Only information required for traceability should be retained.

Sensitive values must follow the same access restrictions applicable to the underlying information.

---

## 19. Reason

Operations requiring an explanation must include a reason or comment.

Examples:

* payment correction;
* refund;
* order cancellation;
* inventory adjustment;
* cash correction;
* conflict resolution;
* administrative intervention.

The reason is part of the historical context.

---

## 20. Result

Audit events should record the operation result where useful.

Possible results include:

```text id="res218"
Success
Rejected
Failed
Conflict
Cancelled
```

The result must accurately represent the operation outcome.

---

## 21. Source

Audit events identify their source.

Possible values include:

```text id="src582"
Online
Offline
Sync
System
```

This allows operators to distinguish locally performed operations from synchronization or automated processing.

---

## 22. Client and Server Time

Offline and synchronized operations may have more than one relevant timestamp.

The system may preserve:

* client event timestamp;
* server received timestamp;
* server processed timestamp.

This allows the system to distinguish when an operation was created from when the server received it.

---

## 23. Clock Anomaly

The system must detect relevant clock anomalies.

Examples include:

* clock rollback;
* suspicious timestamp jumps;
* offline events appearing outside permitted authorization time.

A detected anomaly must be recorded where appropriate.

An anomaly does not automatically mean the underlying operation is invalid unless a separate security or business rule rejects it.

---

## 24. Immutability

Audit records are immutable.

Users must not be able to:

* edit an audit event;
* change its actor;
* change its timestamp;
* remove its reason;
* replace its old/new state;
* delete the event.

Any correction to a business operation creates a new event.

---

## 25. Correction Chain

Corrections must reference the original event or relevant parent event.

Example:

```text id="cor472"
Original Payment
      ↓
Correction Event
      ↓
Second Correction
```

The correction chain preserves the history of the change.

---

## 26. Payment Corrections

Payment edits are represented as controlled corrections.

The audit history must preserve:

* original payment state;
* revised state;
* actor;
* reason;
* timestamp;
* related transaction;
* correction reference.

The original payment event remains immutable.

---

## 27. Overpayment Audit

When an overpayment is confirmed, the audit history should identify:

* Order UUID;
* original order amount;
* entered/received amount;
* overpayment amount;
* payment method;
* cashier;
* waiter where applicable;
* Business;
* Branch;
* Cash Session where applicable;
* confirmation;
* timestamp;
* reason/comment where required.

The overpayment belongs to the Business/Branch and is not treated as cashier personal income.

---

## 28. Inventory Corrections

Inventory corrections must preserve:

* original inventory state;
* adjusted state;
* quantity difference;
* actor;
* reason;
* affected product;
* Branch;
* timestamp;
* related transaction where applicable.

The correction must not silently rewrite the original inventory history.

---

## 29. Cash Corrections

Cash corrections must preserve:

* original discrepancy;
* correction amount;
* new resulting state;
* actor;
* authorization;
* reason;
* Cash Session;
* timestamp.

The original shortage or overage remains immutable.

---

## 30. Permission Changes

Permission changes must be auditable.

The history should identify:

* Employee;
* previous effective permissions;
* new effective permissions;
* Branch scope;
* actor;
* timestamp;
* reason where required.

Permission history must remain available for later investigation.

---

## 31. Employee Status Changes

Employee activation/deactivation events must be auditable.

The event should identify:

* previous status;
* new status;
* actor;
* timestamp;
* Business;
* Branch context where applicable;
* reason where required.

---

## 32. Configuration Changes

Important configuration changes should be auditable.

Examples include:

* price;
* Branch price override;
* menu availability;
* recipe;
* Set composition;
* notification threshold;
* notification configuration;
* salary configuration;
* subscription configuration.

Historical configuration must not be silently overwritten.

---

## 33. Recipe and Menu History

Recipe and menu changes preserve historical versions.

Audit records should connect:

```text id="rcp318"
Old Configuration
      ↓
Change Event
      ↓
New Configuration
```

Historical Orders must continue using their own historical snapshots.

---

## 34. Report Audit

Report generation and important report actions may be audited.

The audit context should identify:

* report definition;
* period;
* Business/Branch scope;
* report version;
* creator/system source;
* creation reason;
* related correction/change where applicable.

Report versions remain immutable.

---

## 35. Notification Audit

Important notification actions and configuration changes may be audited.

Examples:

* threshold changes;
* notification configuration;
* notification resolution;
* important notification action;
* administrative intervention.

Routine notification reading does not necessarily require audit.

---

## 36. Device and Security Audit

Security-relevant device events should be auditable.

Examples include:

* device registration;
* verification;
* device revocation;
* suspicious clock behavior;
* authorization failure;
* synchronization security event.

The Device UUID must be retained where applicable.

---

## 37. Offline Audit

Offline operations generate local audit information.

The local audit event retains:

* Event UUID;
* Employee;
* Device;
* Business;
* Branch;
* transaction;
* entity;
* local timestamp;
* source;
* state change.

The event remains associated with the original offline operation.

---

## 38. Offline Audit Synchronization

When an offline operation synchronizes:

* the original Audit Event UUID is retained;
* the server associates the event with the authoritative server context;
* server processing time is recorded;
* duplicate audit events are prevented.

The server must not replace the original event with a new unrelated audit identity.

---

## 39. Sync-Generated Audit Events

Synchronization may create a separate audit event when the synchronization itself changes state.

Example:

```text id="sync512"
Offline Event
     ↓
Sync Validation
     ↓
Conflict
     ↓
Conflict Resolution Event
```

The original event remains unchanged.

---

## 40. Conflict Resolution Audit

Conflict resolution must be separately auditable.

The resolution event should include:

* conflict UUID;
* original event UUID;
* affected entity;
* previous state;
* selected resolution;
* resulting state;
* actor;
* reason;
* timestamp.

Conflict resolution must never silently overwrite the original conflict history.

---

## 41. Audit Access Control

Audit visibility is permission-based.

A user may only view audit information that falls within their:

* Business scope;
* Branch scope;
* permission;
* employee status;
* subscription/read-only entitlement.

---

## 42. Audit and Subscription

Subscription expiry does not immediately remove audit history.

During read-only retention:

* authorized audit history remains viewable;
* modification of audit records remains impossible;
* permitted Excel export remains available.

Offline devices cannot use audit functionality to bypass subscription restrictions.

---

## 43. Audit Branch Filtering

Authorized users may filter audit history by Branch where applicable.

Branch filtering must be enforced server-side.

The UI must not be trusted to enforce Branch isolation.

---

## 44. Audit Filters

Authorized audit users may filter by:

* date/time;
* Employee;
* Branch;
* event type;
* entity type;
* entity UUID;
* transaction UUID;
* Device;
* Cash Session;
* source;
* result/status.

Filters must not expose records outside the user's authorized scope.

---

## 45. Pagination

Audit history must use server-side pagination for large datasets.

The system must avoid loading an entire audit history into the client.

Pagination must preserve:

* authorization;
* filters;
* ordering;
* stable results where required.

---

## 46. Audit Ordering

Audit history should provide a deterministic ordering.

Where events have identical timestamps, the system must use a stable secondary ordering such as Event UUID or server processing sequence.

This prevents ambiguous ordering during investigation.

---

## 47. Audit Export

Authorized users may export audit history to `.xlsx`.

Export must respect:

* Business scope;
* Branch scope;
* permissions;
* selected filters;
* applicable subscription state.

Export does not modify audit records.

---

## 48. Audit Export Audit

Exporting audit data is itself an auditable operation when required by security policy.

The export event may include:

* actor;
* time;
* Business;
* Branch scope;
* filter criteria;
* export result.

---

## 49. Audit and Reports

Audit data may be used as a source for operational reports.

Reports must not modify audit records.

A report generated from audit data does not become a replacement for the original audit history.

---

## 50. Audit and Data Lifecycle

Audit history follows the applicable Business data lifecycle.

During the retention period:

* records remain available according to permissions;
* records remain immutable.

When the Business reaches permanent deletion:

* Business-scoped audit data is deleted as part of the controlled deletion process;
* deletion itself remains traceable at the platform level where required.

---

## 51. Audit Deletion Protection

Normal Business users must not be able to delete audit records.

Administrative deletion is only part of the controlled data lifecycle.

Audit deletion must never be performed as a routine correction mechanism.

---

## 52. Audit Reliability

Important audit events must be reliably persisted.

The system must avoid a situation where:

```text id="aud903"
Business Transaction = Committed
Audit History = Silently Lost
```

Transactional or outbox-style reliability may be used to guarantee eventual audit persistence without unnecessarily blocking POS.

---

## 53. Audit Failure

If audit persistence temporarily fails:

* the failure must be observable;
* recovery must be attempted;
* the event must not be silently discarded.

For operations where audit is mandatory, the system must use a reliability mechanism that preserves the audit event.

---

## 54. Audit Retry

Retryable audit failures may use:

* queue;
* retry count;
* exponential backoff;
* failure state;
* monitoring;
* reconciliation.

Retries must be idempotent.

---

## 55. Audit Idempotency

Repeated processing of the same Audit Event UUID must not create duplicate audit records.

This applies to:

* online requests;
* offline synchronization;
* worker retries;
* timeout recovery.

---

## 56. Audit and Core Transactions

For critical state-changing operations, audit persistence should be transactionally reliable with the business operation or guaranteed through a reliable transactional event mechanism.

The system must not knowingly commit an important operation while silently losing its required audit trail.

---

## 57. Audit and Performance

Audit processing must not unnecessarily slow down POS.

Performance strategies may include:

* lightweight event creation;
* transactional event/outbox storage;
* asynchronous indexing;
* asynchronous export;
* server-side pagination.

Audit reliability has priority over convenience, but implementation must avoid unnecessary synchronous overhead.

---

## 58. Audit and Background Processing

Background jobs may process:

* audit indexing;
* export;
* retention;
* reconciliation;
* integrity checks.

Background processing must preserve:

* Business context;
* Branch context;
* Event UUID;
* transaction identity;
* ordering where required.

---

## 59. Audit and Concurrency

Concurrent operations must create distinct audit events.

The system must preserve the actual accepted order of state changes.

If optimistic concurrency rejects an operation, the rejected attempt may be recorded when required for security or investigation.

---

## 60. Audit and Error Handling

Audit-related errors follow system-wide error categories:

* Validation;
* Authorization;
* Conflict;
* Business Rule Violation;
* Temporary Infrastructure Error;
* Permanent Failure.

Technical details belong in logs.

Users receive safe operational messages.

---

## 61. Historical Reconstruction

The audit model must support reconstruction of important business changes.

For an important operation, authorized investigators should be able to determine:

* who performed it;
* what changed;
* when it happened;
* where it happened;
* from which device;
* during which Cash Session where applicable;
* why it was changed where required;
* whether it was online, offline or synchronized;
* what the previous state was;
* what the resulting state was.

---

## 62. System Invariants

The following invariants apply to Audit and History:

1. Every audit event has a unique UUID.
2. Audit Event UUIDs are never reused.
3. Every Business-scoped audit event identifies its Business.
4. Branch-scoped events identify their Branch.
5. Cross-Business audit access is prohibited.
6. Cross-Branch audit access is permission-controlled.
7. Employee actors are identified by Employee UUID.
8. System-generated events use SYSTEM as actor.
9. Device context is retained where applicable.
10. Cash Session context is retained for relevant cash operations.
11. Transaction UUID is retained where applicable.
12. Entity type and UUID identify the affected entity.
13. Important state changes generate audit history.
14. Ordinary reads are not normally audited.
15. Sensitive access may be audited.
16. State-changing events preserve old state where required.
17. State-changing events preserve new state where required.
18. Large entity changes may use changed-field records and relevant snapshots.
19. Required correction reasons are preserved.
20. Audit result reflects the actual operation outcome.
21. Audit source identifies Online, Offline, Sync or System where applicable.
22. Client and server timestamps may both be retained.
23. Clock anomalies are traceable where detected.
24. Audit records are immutable.
25. Audit records cannot be edited by normal users.
26. Audit records cannot be deleted as a correction mechanism.
27. Corrections create new audit events.
28. Correction events reference their parent/original event.
29. Payment corrections preserve the original payment history.
30. Overpayment history preserves the relevant financial context.
31. Inventory corrections preserve original and adjusted states.
32. Cash corrections preserve the original discrepancy.
33. Permission changes are auditable.
34. Employee status changes are auditable.
35. Important configuration changes are auditable.
36. Historical recipe/menu changes remain traceable.
37. Report version creation is traceable where required.
38. Important notification configuration changes are auditable.
39. Device security events are auditable where required.
40. Offline audit events retain their original Event UUID.
41. Offline synchronization does not replace original audit identity.
42. Synchronization-generated events are separately identifiable where required.
43. Conflict resolution creates a separate audit event.
44. Audit visibility is permission-controlled.
45. Audit visibility is Branch-scoped where applicable.
46. Audit access respects subscription/read-only state.
47. Server-side filtering enforces access scope.
48. Server-side pagination is used for large audit histories.
49. Audit ordering is deterministic.
50. Audit exports use `.xlsx`.
51. Audit exports respect authorization.
52. Important audit exports may themselves be audited.
53. Audit records follow Business data lifecycle rules.
54. Normal Business users cannot delete audit records.
55. Audit deletion is part of controlled data lifecycle only.
56. Important audit events must not be silently lost.
57. Audit failures remain observable.
58. Retryable audit failures may be retried.
59. Audit retries are idempotent.
60. Duplicate Audit Event UUID processing creates no duplicate event.
61. Important business operations must have reliable audit persistence.
62. Audit processing must not unnecessarily block POS.
63. Background audit processing preserves Business and Branch context.
64. Concurrent operations create distinct audit events.
65. Rejected operations may be audited when security or investigation requires it.
66. Audit history must support reconstruction of important changes.
67. Historical records preserve original actors.
68. Historical records preserve original timestamps.
69. Historical records preserve original device context where applicable.
70. Historical records preserve Cash Session context where applicable.
71. Historical records preserve correction chains.
72. Audit records must not silently overwrite previous history.
73. Audit data must remain tenant-isolated.
74. Audit recovery must be idempotent.
75. Audit reliability must not be sacrificed for UI convenience.
76. Business transaction integrity and audit integrity must be jointly preserved.
77. Audit history must remain explainable throughout the Business lifecycle.
78. Permanent Business deletion must follow the controlled data lifecycle.
79. Platform-level deletion records must remain traceable where required.
80. Audit access itself must never become an authorization bypass.

---

## 63. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/15_Employees_Attendance_and_Payroll.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/12_Debt_and_Payment_Allocation.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/15_Shift_Handover.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/19_Attendance_and_Payroll.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/21_Notifications_and_Alerts.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 64. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `22_Audit_and_History.md`

**Next Document:** `23_Offline_Operation.md`

