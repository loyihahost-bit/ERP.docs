# Notification Data Model

**Document ID:** DB-19
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for application notifications and alerts.

The model covers:

* notification identity;
* Business and Branch scope;
* notification type and severity;
* recipients;
* deduplication;
* unread/read state;
* active/resolved lifecycle;
* action references;
* configurable thresholds;
* subscription-related notifications;
* financial and inventory alerts;
* offline notification behavior;
* synchronization;
* retries;
* notification history;
* audit;
* data lifecycle;
* performance and indexing.

Notifications are secondary application data. A notification must never become the authoritative source of the business state that caused it.

---

## 2. Design Principles

The Notification model follows these principles:

1. Every notification has a permanent UUID.
2. Every notification belongs to a Business.
3. Branch-specific notifications belong to a Branch.
4. Notifications reference the underlying business event or condition.
5. Notification state does not replace domain state.
6. Notification creation must not roll back a successful core transaction.
7. Duplicate notifications for the same active condition must be prevented.
8. Read/unread state is recipient-specific.
9. Important notifications remain historically available.
10. Resolved notifications are not silently deleted.
11. Critical notifications must remain visible until appropriately resolved or dismissed according to policy.
12. Notification recipients are determined by permissions and scope.
13. A notification cannot grant permissions.
14. Action links must be authorization-checked when opened.
15. Offline notifications are secondary synchronized data.
16. Notification delivery failure must not invalidate the underlying business transaction.
17. Retry must be idempotent.
18. Notification thresholds are configurable where supported.
19. Historical notification data follows Business data lifecycle rules.
20. Notification processing must not block POS-critical operations.

---

## 3. Notification Ownership

Notifications belong to the Notification domain.

Conceptually:

```text
Business Event / Condition
        ↓
Notification
        ↓
Recipient State
        ↓
Read / Unread / Resolved
```

The underlying business domain remains authoritative.

Examples:

```text
Low Stock
   ↓
Inventory remains authoritative
   ↓
Notification informs authorized users
```

```text
Large Refund
   ↓
Refund remains authoritative
   ↓
Notification informs authorized users
```

---

## 4. Notification Identity

Every Notification should have a permanent UUID.

Suggested:

```text
notification.id
```

The UUID:

* is globally unique;
* is immutable;
* supports synchronization;
* supports idempotency;
* is never reused.

---

## 5. Notification Scope

Every notification must identify its Business.

Branch-specific notifications additionally identify Branch.

Examples:

```text
Business-wide:
Business → Notification
```

```text
Branch-specific:
Business → Branch → Notification
```

A notification must never expose data belonging to another Business or unauthorized Branch.

---

## 6. Notification Types

Notification types should be represented by stable identifiers.

Examples:

```text
SUBSCRIPTION_EXPIRING
SUBSCRIPTION_EXPIRED
LOW_STOCK
OUT_OF_STOCK
LARGE_REFUND
LARGE_INVENTORY_VARIANCE
BRANCH_LOSS
SALARY_DUE
CASH_DISCREPANCY
CASH_SESSION_CLOSED
SHIFT_HANDOVER_DISCREPANCY
ATTENDANCE_CONFLICT
PAYROLL_CORRECTION
SYNC_CONFLICT
DEVICE_REVOKED
SECURITY_EVENT
```

The list may expand without changing the notification storage model.

---

## 7. Notification Severity

Suggested severity levels:

```text
INFO
WARNING
CRITICAL
```

Severity affects presentation and prioritization.

Severity must not automatically change business state.

---

## 8. Notification Lifecycle

Suggested lifecycle:

```text
ACTIVE
READ
RESOLVED
EXPIRED
FAILED
```

Read state is recipient-specific and therefore should normally be represented through recipient state rather than changing the global Notification state.

A better conceptual model is:

```text
Notification
    ↓
Recipient Notification State
```

---

## 9. Notification Condition

A notification may represent either:

1. an event that happened once; or
2. an active condition that may remain true.

Examples:

```text
Event:
Large Refund Completed
```

```text
Condition:
Stock Below Threshold
```

These must be distinguished because condition notifications require deduplication and resolution.

---

## 10. Event-Based Notification

An event-based notification represents an important event.

Examples:

* large refund completed;
* cash shortage detected;
* payroll finalized;
* device revoked.

Such notifications normally remain historical even after they are read.

---

## 11. Condition-Based Notification

Condition-based notifications represent an active condition.

Examples:

* stock below threshold;
* subscription approaching expiry;
* subscription expired;
* branch loss;
* unresolved synchronization conflict.

The same condition should not continuously generate duplicate active notifications.

---

## 12. Notification Deduplication

A condition-based notification should have a stable deduplication identity.

Conceptually:

```text
Business
+
Branch
+
Notification Type
+
Condition Key
+
Active Cycle
```

Only one active notification should normally exist for the same condition.

---

## 13. Notification Cycle

When a condition becomes true:

```text
Cycle 1
   ↓
Notification Active
```

When the condition is resolved:

```text
Notification Resolved
```

If the same condition becomes true again later:

```text
Cycle 2
   ↓
New Notification
```

The previous notification remains historical.

---

## 14. Condition Key

A condition key identifies the specific underlying condition.

Examples:

```text
product:{product_uuid}:low_stock
branch:{branch_uuid}:loss
business:subscription_expiry
cash_session:{session_uuid}:shortage
```

The exact key format may be implementation-specific but must remain deterministic.

---

## 15. Notification Title

The notification should store a stable human-readable title or title key.

Dynamic data should not be required to reconstruct historical meaning.

---

## 16. Notification Message

The message may contain:

* human-readable text;
* structured parameters;
* entity references.

Historical notifications should remain understandable even if current product names or configurations change.

---

## 17. Structured Payload

A notification may store structured payload data.

Example:

```json
{
  "product_id": "...",
  "current_quantity": "2.000",
  "threshold": "5.000"
}
```

The payload must not become an uncontrolled copy of the entire domain object.

Only relevant information should be stored.

---

## 18. Underlying Entity Reference

A notification may reference the underlying entity.

Suggested fields:

```text
entity_type
entity_id
```

Examples:

```text
entity_type = PRODUCT
entity_id = <product UUID>
```

```text
entity_type = CASH_SESSION
entity_id = <cash session UUID>
```

---

## 19. Transaction Reference

When a notification originates from a transaction, it may reference the Transaction UUID.

Examples:

* Order;
* Payment;
* Refund;
* Inventory transaction;
* Cash transaction;
* Synchronization transaction.

This allows historical reconstruction.

---

## 20. Source Domain

The notification should identify the source domain.

Examples:

```text
INVENTORY
CASH
PAYMENT
ORDER
EMPLOYEE
PAYROLL
SUBSCRIPTION
DEVICE
SYNCHRONIZATION
SECURITY
```

This supports filtering and diagnostics.

---

## 21. Recipient Model

Recipients should be represented separately from the Notification itself.

Conceptually:

```text
Notification
    ↓ 1:N
Notification Recipient
    ↓
Employee
```

One notification may therefore be visible to multiple employees.

---

## 22. Recipient Eligibility

Recipients are determined by:

* Employee status;
* Business membership;
* Branch scope;
* permissions;
* notification type;
* configured recipient policy.

Example:

```text
Large Refund
    ↓
Owner
+
Authorized Manager
```

---

## 23. Permission-Based Visibility

A notification must not grant access to the underlying entity.

If a recipient opens a notification action:

```text
Notification
   ↓
Permission Check
   ↓
Entity Access
```

The current authorization system remains authoritative.

---

## 24. Owner Notifications

Owners may receive important business-level notifications such as:

* subscription expiry;
* branch loss;
* major cash discrepancy;
* large refund;
* major inventory variance.

Owner visibility may be configured where appropriate.

---

## 25. Manager Notifications

Managers may receive notifications only within their authorized Business and Branch scope.

A Manager must not automatically receive all Business-wide information.

---

## 26. Permissioned Employee Notifications

Some notifications may be sent to employees with a specific permission.

Example:

```text
Inventory Adjustment Conflict
    ↓
inventory.view
or
inventory.manage
```

The exact permission is determined by business configuration.

---

## 27. Recipient Snapshot

For historical integrity, a notification may store limited recipient context.

Examples:

* Employee UUID;
* Branch UUID;
* recipient role/scope at creation time.

Current permission state must still be checked when the user opens an action.

---

## 28. Read State

Read state is per recipient.

Example:

```text
Notification A
 ├── Owner → READ
 ├── Manager 1 → UNREAD
 └── Manager 2 → READ
```

One recipient reading the notification must not mark it read for everyone.

---

## 29. Recipient Notification Fields

Suggested:

```text
id
notification_id
employee_id
status
read_at
resolved_at
created_at
updated_at
```

---

## 30. Read Timestamp

When a recipient marks a notification as read:

```text
read_at
```

is recorded.

The timestamp should not be overwritten repeatedly unless a separate read-history model is explicitly introduced.

---

## 31. Unread Count

Unread count should normally be calculated or cached from recipient state.

A cached count must never be the authoritative source.

---

## 32. Resolution

Condition-based notifications may be resolved automatically when the underlying condition becomes false.

Examples:

```text
Low Stock
   ↓
Purchase received
   ↓
Stock above threshold
   ↓
Notification resolved
```

---

## 33. Manual Resolution

Some notifications may require authorized manual resolution.

Examples:

* synchronization conflict;
* security event;
* cash discrepancy;
* attendance conflict.

Manual resolution requires appropriate permission.

---

## 34. Resolution Reference

When resolved, the system may store:

```text
resolved_by
resolved_at
resolution_reason
resolution_entity_id
```

The original notification remains unchanged.

---

## 35. Notification Actions

A notification may provide an action target.

Examples:

```text
View Product
View Cash Session
View Refund
View Payroll
Resolve Conflict
```

The action must be permission-checked at execution time.

---

## 36. Deep-Link Safety

Stored action references must never bypass authorization.

Invalid or stale actions must produce a safe error rather than exposing the underlying entity.

---

## 37. Notification Configuration

Business-level notification configuration may control:

* enabled notification types;
* thresholds;
* recipient policy;
* severity;
* escalation behavior.

Branch-specific configuration may override Business defaults where permitted.

---

## 38. Threshold Configuration

Examples:

```text
LOW_STOCK_THRESHOLD
LARGE_REFUND_THRESHOLD
LARGE_INVENTORY_VARIANCE_THRESHOLD
BRANCH_LOSS_THRESHOLD
```

Threshold values must be stored separately from generated notifications.

---

## 39. Threshold History

Changes to thresholds should be versioned or auditable.

Changing a threshold must not rewrite existing notifications.

---

## 40. Notification Priority

Notifications may have a priority derived from severity.

For example:

```text
CRITICAL > WARNING > INFO
```

Priority affects display ordering but does not replace severity.

---

## 41. Critical Notifications

Critical notifications should be prominently visible.

Examples:

* security incident;
* serious cash discrepancy;
* subscription deletion warning.

Critical notifications must not unnecessarily block POS operations.

---

## 42. POS Performance

Notification creation must not significantly slow:

* order acceptance;
* payment;
* cash session operations;
* inventory transactions;
* shift handover.

The preferred flow is:

```text
Core Transaction
      ↓
Commit
      ↓
Outbox/Event
      ↓
Notification Worker
      ↓
Notification
```

---

## 43. Transaction Boundary

A notification should normally be generated after the core transaction succeeds.

Example:

```text
Refund Transaction
      ↓
Commit
      ↓
Notification Event
      ↓
Large Refund Notification
```

If notification processing fails, the refund remains successful.

---

## 44. Outbox Integration

Important notification events should use the Outbox pattern where reliable delivery is required.

The Outbox Event should contain:

* Event UUID;
* Business UUID;
* Branch UUID where applicable;
* source entity;
* event type;
* payload reference;
* created timestamp;
* processing state.

---

## 45. Notification Idempotency

Repeated event processing must not create duplicate notifications.

A deterministic idempotency key should be used.

Example:

```text
event_uuid
+
notification_type
+
condition_cycle
```

---

## 46. Notification Processing States

Internal processing may use:

```text
PENDING
PROCESSING
DELIVERED
RETRYING
FAILED
```

These are processing states and should not be confused with recipient read state.

---

## 47. Retry

Transient notification failures should be retried.

Examples:

* temporary database failure;
* worker restart;
* temporary queue failure.

Retries must be bounded and idempotent.

---

## 48. Permanent Failure

After retry limits are exhausted:

```text
FAILED
```

may be recorded.

The failure must remain observable to administrators/operators.

A failed notification must not roll back the source business transaction.

---

## 49. Application Delivery Channel

The current primary channel is:

```text
IN_APP
```

The model should not require external messaging services.

Future channels may include:

* SMS;
* email;
* Telegram;
* push notification.

These should be added without changing the authoritative notification history model.

---

## 50. Multi-Device Visibility

The same recipient should see the same logical notification across trusted devices.

Example:

```text
Employee
 ├── Device A
 └── Device B
       ↓
Same Notification Recipient State
```

Read state should synchronize between devices.

---

## 51. Offline Notification

Offline devices may display locally known notifications.

Local notifications are not authoritative.

After synchronization:

* new server notifications are received;
* resolved notifications are updated;
* invalid local notifications are reconciled;
* duplicate notifications are prevented.

---

## 52. Offline Notification Creation

Offline notification creation should be limited to conditions that can be reliably evaluated locally.

The server remains authoritative for:

* subscription lifecycle;
* global security events;
* cross-device events;
* cross-branch conditions;
* final financial state.

---

## 53. Notification Synchronization

Notification synchronization should use permanent Notification UUIDs.

Recipient state synchronization should also use permanent identifiers.

Duplicate sync must be idempotent.

---

## 54. Sync Conflict

Possible conflicts include:

* notification already resolved;
* recipient already read;
* notification deleted by lifecycle process;
* employee deactivated;
* Branch access removed.

Server state remains authoritative.

---

## 55. Notification and Subscription

Subscription notifications may include:

* subscription ending soon;
* subscription expired;
* deletion warning;
* deletion eligible;
* reactivation completed.

Subscription lifecycle remains authoritative in the Subscription domain.

---

## 56. Notification and Inventory

Inventory notifications may include:

* low stock;
* out of stock;
* large inventory variance.

Inventory balances and transactions remain authoritative.

---

## 57. Notification and Cash

Cash notifications may include:

* cash shortage;
* cash overage;
* session close discrepancy;
* shift handover discrepancy.

Cash Sessions and Cash Transactions remain authoritative.

---

## 58. Notification and Payment

Payment notifications may include:

* large refund;
* large overpayment;
* unusual correction.

Payment records remain authoritative.

---

## 59. Notification and Payroll

Payroll notifications may include:

* salary due;
* payroll finalized;
* payroll correction;
* payroll discrepancy.

Payroll records remain authoritative.

---

## 60. Notification and Device Security

Device notifications may include:

* device revoked;
* suspicious device activity;
* offline authorization failure.

Device Trust remains authoritative.

---

## 61. Notification and Synchronization

Synchronization notifications may include:

* unresolved conflict;
* repeated sync failure;
* invalid offline event;
* device synchronization issue.

The synchronization domain remains authoritative.

---

## 62. Notification History

Historical notifications should preserve:

* notification UUID;
* Business;
* Branch;
* type;
* severity;
* source;
* entity;
* transaction;
* message/title;
* creation time;
* resolution state;
* recipient state.

---

## 63. Notification Retention

Notifications follow Business data lifecycle rules.

Subscription expiry must not immediately delete notification history.

Business deletion eventually removes notification data through the controlled deletion process.

---

## 64. Business Deletion

When Business deletion begins:

* active notifications stop generating;
* notification workers reject new events for the deleting Business;
* pending notification jobs are cancelled or marked obsolete;
* existing notification data is deleted according to dependency rules.

Stale devices must not recreate notifications for a deleted Business.

---

## 65. Notification Security

Notifications may contain sensitive information.

Examples:

* salary information;
* cash discrepancies;
* security events;
* financial corrections.

Therefore notification payloads must not expose more information than the recipient is authorized to see.

---

## 66. Sensitive Payload Handling

Sensitive values should preferably be referenced rather than copied into unrestricted notification payloads.

Example:

```text
View Payroll Record
```

is safer than exposing the full salary calculation in the notification message.

---

## 67. Audit

Important notification operations may create Audit Events:

* notification configuration change;
* threshold change;
* manual resolution;
* security notification;
* notification export;
* notification administrative action.

Routine notification reads do not normally require audit events.

---

## 68. Notification Export

If notification export is provided later, it must be:

* permission-controlled;
* Business scoped;
* Branch scoped where applicable;
* paginated;
* audited.

The current report/export model remains authoritative for formal business reports.

---

## 69. Indexing

Recommended indexes:

```text
notifications(business_id, created_at)
notifications(business_id, branch_id, created_at)
notifications(business_id, type, created_at)
notifications(business_id, severity, created_at)
notifications(business_id, condition_key, status)
notifications(entity_type, entity_id)
notifications(transaction_id)
```

---

## 70. Recipient Indexing

Recommended:

```text
notification_recipients(employee_id, status, created_at)
notification_recipients(employee_id, read_at)
notification_recipients(notification_id, employee_id)
notification_recipients(employee_id, notification_id)
```

Unread queries should use an efficient index on Employee and unread status.

---

## 71. Deduplication Constraint

For condition notifications, the database should enforce uniqueness where practical.

Conceptually:

```text
Business
+
Branch
+
Type
+
Condition Key
+
Active Cycle
```

must identify one active condition notification.

---

## 72. Recipient Uniqueness

The same Employee must not have duplicate recipient rows for the same Notification.

Conceptually:

```text
UNIQUE(notification_id, employee_id)
```

---

## 73. Suggested `notifications` Fields

```text
id
business_id
branch_id
type
severity
source_domain
condition_key
cycle_number
title
message
payload
entity_type
entity_id
transaction_id
status
created_at
resolved_at
resolved_by
resolution_reason
expires_at
version
```

---

## 74. Suggested `notification_recipients` Fields

```text
id
notification_id
business_id
branch_id
employee_id
recipient_scope
status
read_at
resolved_at
created_at
updated_at
```

---

## 75. Suggested `notification_configurations` Fields

```text
id
business_id
branch_id
notification_type
enabled
severity
threshold_value
recipient_policy
effective_from
effective_to
version
created_at
updated_at
```

---

## 76. Suggested `notification_configuration_versions` Fields

```text
id
configuration_id
version
configuration_snapshot
effective_from
created_by
created_at
```

---

## 77. Suggested `notification_outbox_events` Fields

```text
id
event_id
business_id
branch_id
source_domain
event_type
entity_type
entity_id
transaction_id
payload
status
attempt_count
next_attempt_at
processed_at
created_at
```

---

## 78. Notification Query Strategy

Common queries include:

* current unread notifications;
* critical notifications;
* notifications for a Branch;
* notifications for an Employee;
* notification history;
* unresolved notifications;
* notifications related to a transaction;
* notifications related to an entity.

Queries must always apply Business scope.

---

## 79. Pagination

Notification lists must use server-side pagination.

The preferred ordering is:

```text
created_at DESC
+
id DESC
```

This provides deterministic ordering when timestamps are equal.

---

## 80. Notification Caching

Unread counts may be cached.

However:

* cache is not authoritative;
* invalidation must occur after state changes;
* stale counts must not affect authorization;
* stale counts must not hide critical notifications permanently.

---

## 81. Notification Failure Isolation

The following failure must not roll back a successful core transaction:

```text
Notification Worker Failure
Notification Queue Failure
Notification Rendering Failure
Notification Retry Failure
```

The source transaction remains authoritative.

---

## 82. Notification Recovery

After worker recovery:

1. Pending events are loaded.
2. Idempotency is checked.
3. Notification is created or reconciled.
4. Recipient records are created.
5. Processing state is updated.
6. Failed events are retried according to policy.

---

## 83. Concurrency

Concurrent notification generation must not create duplicate active condition notifications.

The implementation may use:

* unique constraints;
* transactions;
* advisory locks;
* row locks;
* idempotency keys.

Database constraints are preferred where possible.

---

## 84. Historical Integrity

Changing:

* product name;
* employee role;
* threshold;
* salary;
* branch configuration;
* notification configuration

must not silently rewrite historical notifications.

Historical notification content must remain understandable.

---

## 85. Notification Data Types

Recommended:

* UUID for identifiers;
* timezone-aware timestamps;
* exact decimal values for thresholds where monetary/quantity values are involved;
* JSON/JSONB for controlled structured payloads;
* enumerated or stable string codes for types/statuses.

Unbounded uncontrolled JSON should not become the primary relational data model.

---

## 86. Notification Transaction Example

Example: large refund.

```text
Refund Transaction
       ↓
Validate Permission
       ↓
Create Refund
       ↓
Commit Refund
       ↓
Outbox Event
       ↓
Notification Worker
       ↓
Create Large Refund Notification
       ↓
Create Recipients
```

If the worker fails:

```text
Refund = Successful
Notification = Pending/Retrying
```

---

## 87. Notification Configuration Example

Example:

```text
Notification:
LARGE_REFUND

Threshold:
500,000

Severity:
WARNING

Recipients:
Owner
Authorized Manager
```

Changing the threshold affects future notification evaluation.

It does not modify historical notifications.

---

## 88. Security Boundary

Notification access must follow:

```text
Authentication
+
Authorization
+
Business Scope
+
Branch Scope
+
Notification Visibility
```

Opening a notification action must perform a fresh authorization check.

---

## 89. Performance Boundary

Notification generation is secondary processing.

Core operations should not wait for:

* recipient resolution;
* notification rendering;
* unread count recalculation;
* external delivery;
* notification history indexing.

The core event should be committed first.

---

## 90. Database Invariants

The following invariants are mandatory:

1. Every Notification has a permanent UUID.
2. Notification UUIDs are globally unique.
3. Notification UUIDs are never reused.
4. Every Notification belongs to one Business.
5. Branch-specific Notifications belong to one Branch.
6. Notification Business and Branch relationships are consistent.
7. Notification type is a stable identifier.
8. Notification severity is valid.
9. Notification source domain is valid.
10. Notification status is controlled.
11. Condition-based Notifications have deterministic condition keys.
12. Active condition Notifications are deduplicated.
13. Resolved condition Notifications remain historically available.
14. A new active cycle creates a new historical Notification.
15. Notification recipients are stored separately.
16. Recipient Employee belongs to the same Business.
17. Branch recipient scope is valid.
18. One Employee cannot have duplicate recipient rows for one Notification.
19. Read state is recipient-specific.
20. One recipient reading a Notification does not mark it read for others.
21. Read timestamps are preserved.
22. Resolution timestamps are preserved.
23. Manual resolution requires authorization.
24. Resolution reason is preserved where required.
25. Notification actions never bypass authorization.
26. Notification action targets are validated at execution time.
27. Notifications do not grant permissions.
28. Notification payloads do not become an uncontrolled copy of domain state.
29. Sensitive notification data is permission-controlled.
30. Notification entity references are Business scoped.
31. Transaction references are Business scoped.
32. Notification creation does not become part of the core business transaction unless explicitly required.
33. Notification failure does not roll back a successful core transaction.
34. Notification retries are idempotent.
35. Repeated Outbox processing does not create duplicate Notifications.
36. Notification workers use durable processing state.
37. Failed notifications remain observable.
38. Notification retries are bounded.
39. Notification configuration is separate from generated Notifications.
40. Configuration changes do not rewrite historical Notifications.
41. Threshold changes affect future evaluation.
42. Notification severity changes do not rewrite historical severity.
43. Notification history remains reconstructable.
44. Owner notifications remain Business scoped.
45. Manager notifications respect Branch scope.
46. Permissioned employee notifications respect effective permissions.
47. Notification visibility cannot cross Business boundaries.
48. Notification visibility cannot cross unauthorized Branch boundaries.
49. Critical Notifications remain visible according to configured lifecycle rules.
50. Critical Notifications do not automatically block POS operations.
51. Low Stock Notifications do not modify Inventory.
52. Cash Notifications do not modify Cash Sessions.
53. Payment Notifications do not modify Payments.
54. Payroll Notifications do not modify Payroll.
55. Subscription Notifications do not modify Subscription state.
56. Device Notifications do not modify Device Trust state unless an explicit authorized workflow performs the action.
57. Synchronization Notifications do not silently resolve Sync Conflicts.
58. Notification resolution does not automatically change underlying domain state unless an explicit authorized action is executed.
59. Offline Notifications are not authoritative.
60. Offline Notification synchronization is idempotent.
61. Server state is authoritative after synchronization.
62. Revoked devices cannot continue creating authoritative Notifications.
63. Deactivated employees cannot receive new operational notifications outside allowed historical access.
64. Business deletion prevents new Notifications for that Business.
65. Pending Notification events for a deleting Business are safely terminated.
66. Deleted Business Notifications cannot be recreated by stale offline events.
67. Notification data follows Business lifecycle rules.
68. Notification retention does not alter subscription expiry timing.
69. Notification indexes include Business scope for tenant isolation.
70. Notification queries apply Business scope.
71. Notification queries apply Branch scope where required.
72. Notification lists use deterministic ordering.
73. Notification pagination is server-controlled.
74. Cached unread counts are not authoritative.
75. Cache failure does not change Notification correctness.
76. Notification processing does not block POS-critical transactions.
77. Notification workers can be restarted safely.
78. Notification events can be retried safely.
79. Notification state transitions are concurrency-safe.
80. Concurrent condition evaluation cannot create duplicate active Notifications.
81. Notification recipient creation is concurrency-safe.
82. Notification history remains auditable where required.
83. Important configuration changes create Audit Events.
84. Manual Notification resolution is auditable.
85. Security-related Notifications are auditable.
86. Notification export, if enabled, is permission-controlled.
87. Notification export is Business scoped.
88. Notification export is auditable.
89. Monetary and quantity thresholds use exact decimal types.
90. Notification timestamps are timezone-aware.
91. Notification identifiers use UUIDs.
92. Historical notification messages remain understandable after configuration changes.
93. Historical notifications do not depend on mutable current product names.
94. Historical notifications do not depend on mutable current employee roles.
95. Historical notifications do not depend on mutable current thresholds.
96. Notification payloads contain only required business context.
97. Database constraints and application validation enforce Notification ownership boundaries.
98. Notification data is never authoritative for the underlying domain state.
99. Notification failures remain isolated from core business failures.
100. The complete Notification history must remain reconstructable from authoritative notification records and their source references.

---

## 91. Related Documents

### Database

* `02_Database_Architecture.md`
* `03_Tenant_and_Business_Data_Model.md`
* `04_Identity_and_Access_Data_Model.md`
* `05_Branch_and_Organizational_Data_Model.md`
* `06_Subscription_and_Entitlement_Data_Model.md`
* `07_Device_and_Trust_Data_Model.md`
* `11_Inventory_and_Warehouse_Data_Model.md`
* `13_Order_and_Order_Item_Data_Model.md`
* `15_Payment_and_Debt_Data_Model.md`
* `16_Cash_Register_and_Cash_Session_Data_Model.md`
* `17_Shift_Handover_Data_Model.md`
* `18_Employee_Attendance_and_Payroll_Data_Model.md`
* `20_Audit_and_History_Data_Model.md`
* `21_Report_and_Report_Version_Data_Model.md`
* `22_Offline_and_Synchronization_Data_Model.md`
* `23_Configuration_Data_Model.md`
* `24_Data_Lifecycle_and_Deletion_Data_Model.md`

### Domain

* `14_Notification_Domain.md`
* `15_Audit_Domain.md`
* `16_Synchronization_Domain.md`
* `17_Data_Lifecycle_Domain.md`
* `18_Configuration_Domain.md`
* `19_Device_and_Trust_Domain.md`
* `20_Cross_Domain_Relationships_Domain.md`

### System Analysis

* `21_Notifications_and_Alerts.md`
* `22_Audit_and_History.md`
* `23_Offline_Operation.md`
* `24_Synchronization_and_Conflict_Resolution.md`
* `25_Subscription_and_Entitlement.md`
* `26_Data_Lifecycle_and_Deletion.md`
* `27_System_Wide_Consistency_and_Concurrency.md`
* `28_Background_Jobs_and_Recovery.md`
* `29_Error_Handling_and_Failure_Recovery.md`

### Architecture

* `07_Database_Architecture.md`
* `12_Event_and_Message_Architecture.md`
* `13_Background_Processing_Architecture.md`
* `14_Caching_Architecture.md`
* `17_Failure_Recovery_Architecture.md`
* `20_Architecture_Invariants_and_Guardrails.md`

---

## 92. Final Rule

The Notification database model must remain a reliable historical representation of notifications without becoming the authoritative source of business state.

The central rule is:

```text
Business State
      ↓
Domain Event / Condition
      ↓
Notification
      ↓
Recipient State
      ↓
Read / Resolve
```

The notification system must inform users without becoming a hidden dependency of POS-critical operations.

Notifications must remain:

* Business isolated;
* Branch scoped;
* permission-aware;
* idempotent;
* auditable where required;
* historically reconstructable;
* synchronization-safe;
* performance-safe;
* independent from core transaction success.

