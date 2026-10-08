# System-Wide Consistency and Concurrency

**Document ID:** SA-27
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines system-wide rules for data consistency, transaction boundaries, concurrency control, idempotency, race-condition handling, and cross-module state integrity.

FastFood ERP contains multiple operational domains that interact with the same Business data.

Examples include:

* Orders;
* Inventory;
* Payments;
* Cash Sessions;
* Tables;
* Employees;
* Permissions;
* Menu and pricing;
* Reports;
* Notifications;
* Offline synchronization;
* Subscription and entitlement.

A change in one domain must not silently create an invalid state in another domain.

The system must therefore prioritize:

* data correctness;
* atomic core operations;
* deterministic concurrency behavior;
* idempotency;
* explicit conflict handling;
* tenant isolation;
* historical integrity;
* offline safety;
* predictable recovery.

---

## 2. Scope

This document covers:

* consistency principles;
* transaction boundaries;
* atomicity;
* isolation;
* concurrency;
* locking;
* optimistic concurrency;
* pessimistic locking;
* idempotency;
* duplicate requests;
* race conditions;
* cross-module transactions;
* order/inventory consistency;
* order/payment consistency;
* cash/payment consistency;
* table/order consistency;
* configuration consistency;
* employee/permission consistency;
* subscription/entitlement consistency;
* report consistency;
* notification consistency;
* offline consistency;
* synchronization;
* conflict handling;
* background jobs;
* failure recovery;
* tenant isolation;
* historical integrity;
* performance;
* system-wide invariants.

---

## 3. Core Consistency Principle

The system must never prioritize convenience over business correctness when the two conflict.

For critical operations:

```text
Validate
   ↓
Authorize
   ↓
Execute Atomic Core Operation
   ↓
Persist State
   ↓
Trigger Secondary Operations
```

Secondary failures must not silently invalidate a successfully committed core transaction.

---

## 4. Source of Truth

For current server-side state:

**The server is authoritative.**

This applies to:

* stock;
* payment state;
* Cash Session state;
* order state;
* employee status;
* permissions;
* subscription;
* entitlement;
* configuration;
* report finalization;
* Business lifecycle.

Offline clients may continue authorized operations, but their events must be validated when synchronized.

---

## 5. Transaction Boundary Principle

A transaction must contain all state changes that must succeed or fail together.

Examples:

```text
Order Acceptance
+
Inventory Deduction
```

must be one core atomic transaction.

However:

```text
Order Acceptance
+
Kitchen Printer Output
```

does not need to be one database transaction.

Kitchen printing is a secondary operation.

---

## 6. Atomicity

An atomic operation must produce either:

* the complete intended state; or
* no core state change.

Partial core state is not acceptable.

Example:

If an Order is accepted but inventory deduction fails, the Order must not remain Accepted.

---

## 7. Core vs Secondary Operations

### Core operations

Examples:

* Order acceptance;
* inventory deduction;
* payment creation;
* Cash Session close;
* Cash Session opening;
* inventory adjustment;
* debt repayment allocation;
* payroll finalization;
* configuration state change.

### Secondary operations

Examples:

* kitchen printing;
* notification delivery;
* non-critical analytics;
* background report generation;
* UI refresh.

Secondary failure must not normally roll back a successfully committed core operation.

---

## 8. Database Transaction Principle

Database transactions should protect core consistency.

A transaction should be:

* as small as practical;
* limited to required data;
* deterministic;
* safe under concurrency;
* recoverable on failure.

Long-running transactions should be avoided for ordinary POS operations.

---

## 9. Isolation

The system must prevent concurrent operations from producing invalid business state.

The exact database isolation level may vary by operation.

Critical operations may require:

* row-level locking;
* atomic conditional update;
* optimistic version checking;
* unique constraints;
* serializable behavior for selected operations.

The strongest isolation level should not be applied globally without necessity because of performance impact.

---

## 10. Row-Level Locking

Row-level locking should be used where multiple operations may modify the same business-critical record concurrently.

Examples:

* inventory quantity;
* Cash Session state;
* payment remaining amount;
* debt balance;
* active session state;
* configuration version.

Locks should be as narrow as practical.

---

## 11. Inventory Concurrency

Inventory is concurrency-sensitive.

Example:

```text
Stock = 1

Order A → sells 1
Order B → sells 1
```

Only one Order may successfully consume the final unit.

The system must not allow:

```text
Stock = -1
```

as a result of concurrent sales.

---

## 12. Inventory Atomicity

Order acceptance and inventory deduction must be atomic.

Conceptually:

```text
Validate Order
      ↓
Lock/validate required stock
      ↓
Deduct stock
      ↓
Persist Order as Accepted
```

If any core step fails, the operation rolls back.

---

## 13. Inventory Modification Rollback

If an accepted Order modification requires inventory return and the return operation fails:

* the entire modification fails;
* the Order remains unchanged;
* inventory remains unchanged.

Partial modification is not allowed.

---

## 14. Payment Concurrency

Payment creation must validate the current payable state.

The system must verify:

* Order identity;
* Business;
* Branch;
* payment status;
* remaining amount;
* employee permission;
* subscription/entitlement where applicable.

A payment request based on stale remaining amount must not create an invalid financial state.

---

## 15. Overpayment Concurrency

Overpayment is an explicit financial state.

The system must distinguish:

```text
Order Amount
+
Accepted Payment
+
Overpayment
```

Overpayment belongs to the Business/Branch.

It must not become:

* cashier personal income;
* waiter personal income;
* hidden debt;
* duplicated payment.

---

## 16. Payment Idempotency

Payment creation must use a stable UUID/idempotency identity.

If the same payment request is submitted more than once:

* only one payment is created;
* retry receives the existing result where applicable;
* duplicate financial effect is prevented.

---

## 17. Order Idempotency

Order creation and acceptance use stable UUID-based identity.

A retry of the same operation must not create:

* duplicate Order;
* duplicate inventory deduction;
* duplicate kitchen event where protected by event idempotency.

---

## 18. Cash Session Concurrency

Only one active Cash Session may exist for the same Branch/register context according to the current business model.

If two requests attempt to open a new session concurrently:

```text
Request A → succeeds
Request B → rejected
```

The first successful valid request wins.

---

## 19. Cash Session Close Concurrency

Closing a Cash Session must validate that:

* the session is still Open;
* the actor is authorized;
* no conflicting transition has already closed it.

A second close request must not create another closure or overwrite the first result.

---

## 20. Cash Session Correction Concurrency

Correction count must be updated atomically.

Two simultaneous correction requests must not both observe:

```text
Correction Count = 2
```

and both create a third correction.

The correction limit must be enforced at the transaction boundary.

---

## 21. Handover Concurrency

Cash handover must maintain one authoritative session transition.

The sequence is:

```text
Previous Cashier
      ↓
Close Previous Session
      ↓
New Cashier Authentication
      ↓
Cash Acceptance
      ↓
Open New Session
```

Concurrent handover attempts must not create multiple active sessions.

---

## 22. Table Concurrency

Table occupancy must be derived from current operational Order state.

If an Order is Accepted or otherwise operationally open, the table may be Busy.

Concurrent operations must not create contradictory table states.

---

## 23. Table Visit/Session Grouping

A Table Visit/Session represents one operational table grouping.

When the table is freed:

* the previous grouping ends;
* a new grouping is created for the next visit.

Historical Orders remain linked to their original grouping.

---

## 24. Draft Order Concurrency

Draft Orders do not reserve table occupancy.

Two devices may create independent Draft Orders for the same table.

When a Draft is accepted:

* server state is rechecked;
* table/order context is validated;
* conflicts are handled explicitly.

---

## 25. Draft Sync Conflict

If an offline Draft synchronizes after another Order has already occupied the relevant table context:

* server state wins;
* the Draft is not silently converted into an Accepted Order;
* the Draft may be discarded according to the defined conflict rule;
* the conflict/result is recorded.

---

## 26. Order Modification Concurrency

Order modification must verify that the Order remains modifiable.

If one request changes the Order while another uses an earlier version:

* stale modification must be rejected or explicitly reconciled;
* silent overwrite is prohibited.

---

## 27. Paid Order Concurrency

Once an Order becomes fully paid:

* ordinary modification is blocked;
* correction/refund/cancellation workflow is required.

A concurrent edit that started before payment completion must not silently modify the paid Order afterward.

---

## 28. Order Cancellation Concurrency

Cancellation must validate current Order state.

If another operation already completed or served the Order:

* cancellation must follow applicable lifecycle rules;
* invalid cancellation is rejected;
* inventory/financial state must remain consistent.

---

## 29. Payment vs Order Lifecycle

Payment and operational Order lifecycle are independent.

Payment completion must not automatically change:

* Preparing;
* Ready;
* Served.

Similarly, Order status changes must not silently create or modify payment records.

---

## 30. Refund Concurrency

Refund creation must validate:

* original payment;
* refundable amount;
* refund amount;
* authorization;
* reason;
* applicable payment method.

Concurrent refunds must not exceed the refundable amount.

---

## 31. Refund Idempotency

A refund operation must have a stable identity.

Retrying the same refund request must not create duplicate financial effects.

---

## 32. Debt Concurrency

Debt repayment must protect:

* Customer balance;
* Debt Order balance;
* repayment allocation.

Two concurrent repayments must not allocate more than the outstanding debt.

---

## 33. Debt Allocation Atomicity

Debt repayment and its allocation must succeed or fail together.

A repayment must not be recorded without its required allocation state.

---

## 34. Inventory Adjustment Concurrency

Manual inventory adjustments must validate the current inventory state.

Concurrent adjustments must not silently overwrite each other.

Where required, the system should use:

* row locking;
* version checks;
* atomic quantity updates.

---

## 35. Purchase vs Sale Concurrency

Purchase and sale may occur concurrently.

The system must maintain a valid inventory quantity through transaction isolation/locking.

Example:

```text
Purchase +10
Sale -5
```

must result in a deterministic final stock state.

---

## 36. Recipe Configuration Concurrency

Recipe modifications must be versioned.

If two users modify the same Recipe configuration concurrently:

* one authoritative version is committed;
* stale modification must be rejected or handled through explicit conflict resolution;
* silent overwrite is prohibited.

---

## 37. Menu Configuration Concurrency

Menu and pricing configuration changes must use configuration versions/effective states.

A stale client must not overwrite a newer configuration without an explicit valid transition.

---

## 38. Price Concurrency

Price changes do not rewrite existing Order prices.

Open Orders retain their price snapshot.

New Orders use the applicable active configuration.

---

## 39. Configuration Effective Time

Recipe, Menu, Set and price changes follow the rule:

**effective from the next Cash Session.**

An active session continues using its valid configuration.

This prevents mid-session configuration changes from silently changing active operational behavior.

---

## 40. Configuration Version Consistency

Every device must know which configuration version it is using where configuration versioning applies.

Offline devices may continue with their latest valid configuration until synchronization.

---

## 41. Employee Status Concurrency

Employee activation/deactivation must be evaluated against the operation timestamp and current server state.

An employee deactivated before an operation must not continue to perform unauthorized new operations.

---

## 42. Permission Concurrency

Permission changes may occur while an employee is logged in.

Important operations must validate current server-side permission.

A stale UI must not preserve old authorization.

---

## 43. Branch Scope Concurrency

Branch switching must recalculate effective permissions.

A request created under Branch A context must not execute against Branch B merely because the user's current UI context changed.

---

## 44. Subscription Concurrency

Subscription and entitlement changes must be synchronized with protected operations.

If subscription expires while a modifying request is being processed:

* transaction ordering determines the authoritative result;
* the system must not leave an operation half-applied.

---

## 45. Subscription Renewal vs Expiry

Renewal and expiry processing may race.

The system must ensure:

* valid renewal prevents incorrect deletion/expiry;
* duplicate renewal does not create duplicate periods;
* lifecycle state remains deterministic.

---

## 46. Reactivation vs Deletion

Reactivation and deletion must use an atomic lifecycle decision.

A stale deletion worker must not delete a Business that was successfully reactivated.

---

## 47. Report Consistency

Reports must use a consistent transactional snapshot.

A report must not combine:

```text
Old Order Data
+
New Payment Data
+
Different Inventory State
```

in a way that produces an internally inconsistent result.

---

## 48. Report Versioning

If relevant underlying data changes after a report version is created:

* a new report version may be generated;
* previous version remains immutable.

If a correction does not affect relevant report metrics:

* no new version is required.

---

## 49. Report Generation Concurrency

Duplicate requests for the same logical report must be prevented through an idempotency/key mechanism.

Logical report identity:

```text
Report Definition
+
Period
+
Scope
```

---

## 50. Notification Consistency

Notifications are secondary effects.

A notification failure must not roll back a successfully committed core transaction.

Example:

```text
Cash Session closed successfully
+
Owner notification delivery failed
```

The Cash Session remains closed.

The notification enters retry/failure handling.

---

## 51. Audit Consistency

Important state-changing operations must create reliable audit information.

Audit persistence must not depend on a best-effort UI request.

Where required, audit persistence should be part of the core transaction or use a reliable transactional/outbox-style mechanism.

---

## 52. Audit Idempotency

Retrying the same operation must not create uncontrolled duplicate audit events.

Audit event identity should allow reliable correlation with:

* Transaction UUID;
* entity UUID;
* operation;
* actor;
* device;
* session.

---

## 53. Background Job Concurrency

Background jobs must be safe when:

* retried;
* duplicated;
* restarted;
* interrupted;
* processed by multiple workers.

Jobs should use:

* unique job identity;
* idempotency;
* locking/leases;
* explicit state transitions.

---

## 54. Job Ownership

Only one worker should own a mutually exclusive job operation at a time.

If a worker crashes:

* its lease may expire;
* another worker may safely continue;
* duplicate effects must still be prevented.

---

## 55. Synchronization Concurrency

Offline synchronization may produce multiple events from:

* one device;
* multiple devices;
* multiple employees.

The server must process events according to:

* Business;
* Branch;
* entity;
* dependency;
* transaction;
* event ordering.

---

## 56. Event Ordering

Dependent events must be processed in the correct order.

Example:

```text
Create Order
      ↓
Accept Order
      ↓
Payment
```

Payment must not be accepted before the server can establish a valid corresponding Order state.

---

## 57. Transaction UUID

Transactions use stable UUID identity where required.

Transaction UUID is different from:

* customer-facing Order number;
* device identity;
* Cash Session UUID.

It is used for correlation and idempotency.

---

## 58. Event UUID

Synchronization events use stable Event UUIDs.

If the same event reaches the server more than once:

* it is recognized;
* duplicate processing is prevented;
* original result can be returned where applicable.

---

## 59. Duplicate Request Handling

Duplicate requests may occur because of:

* user double-click;
* network retry;
* client timeout;
* server response loss;
* offline synchronization retry;
* background worker retry.

The system must treat these as normal operational conditions rather than exceptional corruption.

---

## 60. Lost Server Response

If the server successfully commits an operation but the client does not receive the response:

1. client retries using the same idempotency identity;
2. server detects the existing operation;
3. duplicate state change is not created;
4. existing result is returned where possible.

---

## 61. Network Timeout

A timeout does not prove that the operation failed.

The client must not automatically create a new operation with a new UUID merely because the previous response was not received.

---

## 62. Client Retry

Retry logic must preserve:

* UUID;
* Transaction UUID;
* Business context;
* Branch context;
* original operation identity.

Creating a new identity for every retry can cause duplicate business effects.

---

## 63. Optimistic Concurrency

Optimistic concurrency may be used for data that is frequently read but less frequently modified.

Examples:

* menu configuration;
* recipe configuration;
* employee settings.

A version mismatch indicates that the client is working with stale state.

---

## 64. Pessimistic Concurrency

Pessimistic locking may be used for highly contention-sensitive resources.

Examples:

* stock quantity;
* active Cash Session;
* financial balances;
* correction counters.

The lock duration must remain as short as practical.

---

## 65. Unique Constraints

Database-level unique constraints should protect critical uniqueness requirements where applicable.

Examples:

* one active Cash Session for a register;
* stable operation identity;
* duplicate prevention;
* Business-scoped unique configuration identity.

Application checks alone are insufficient for critical uniqueness.

---

## 66. Atomic Conditional Updates

Some operations can use conditional updates instead of explicit locks.

Example concept:

```text
UPDATE stock
SET quantity = quantity - requested_quantity
WHERE product_id = ?
  AND quantity >= requested_quantity
```

The affected-row result determines whether the operation succeeded.

The exact implementation remains an architectural/technical decision.

---

## 67. Cross-Module Consistency

Modules must not independently create contradictory state.

Examples:

### Order + Inventory

Accepted Order must correspond to the correct inventory deduction.

### Payment + Order

Payment must correspond to a valid payable Order state.

### Cash Session + Payment

Cash payments must belong to the appropriate Cash Session.

### Payroll + Attendance

Payroll calculation must use a consistent attendance snapshot.

### Report + Source Data

Report version must represent a consistent data snapshot.

---

## 68. Financial Consistency

Financial records must preserve:

* original amount;
* correction;
* refund;
* overpayment;
* actor;
* timestamp;
* reason.

Corrections must not silently rewrite original financial records.

---

## 69. Inventory Consistency

Inventory must preserve:

* opening state where applicable;
* movements;
* purchases;
* sales;
* adjustments;
* discrepancies;
* corrections.

Negative stock is prohibited.

---

## 70. Historical Consistency

Historical records must remain interpretable.

Examples:

* historical Order retains price snapshot;
* historical report retains version;
* historical payroll retains calculation snapshot;
* historical configuration retains version;
* historical payment retains original record.

---

## 71. Tenant Consistency

Every operation must carry or derive valid:

```text
Business Context
+
Branch Context where applicable
+
Actor Context
+
Device Context where applicable
```

The system must reject mismatched context.

---

## 72. Cross-Tenant Request Protection

A valid employee session from Business A must not access Business B by changing:

* URL parameters;
* UUID;
* request body;
* API path;
* query parameters;
* synchronization payload.

Tenant context must be validated server-side.

---

## 73. Cross-Branch Request Protection

A user authorized for Branch A must not modify Branch B data without appropriate Branch scope.

A Branch UUID supplied by the client is not sufficient authorization.

---

## 74. Offline Consistency

Offline operation may temporarily diverge from current server state.

This is expected.

The system must ensure that:

* offline authorization was valid;
* event identity is stable;
* events are durable;
* server validates events after synchronization;
* conflicts are explicit;
* invalid events do not silently corrupt server state.

---

## 75. Offline Conflict

When server state conflicts with an offline operation:

* conflict is recorded;
* server state remains authoritative for current state;
* authorized resolution may be required;
* resolution records actor/reason/time;
* original offline event remains historically traceable.

---

## 76. Offline Inventory Conflict

If offline inventory consumption conflicts with server inventory:

* server revalidates stock;
* conflict is recorded if required;
* no negative stock is created;
* authorized resolution determines final correction.

---

## 77. Offline Payment Conflict

If an offline payment reaches the server after the Order is already fully paid:

* payment is not silently duplicated;
* conflict is created;
* authorized resolution determines financial treatment.

---

## 78. Offline Cash Conflict

Offline Cash Session events retain their original Cash Session UUID.

Synchronization must not silently replace the original session identity.

If session state conflicts:

* conflict is recorded;
* server resolves according to Cash Session authority.

---

## 79. Configuration Sync Consistency

Transactions must synchronize before configuration changes.

This prevents a device from applying a new configuration to an older unsynchronized transaction context incorrectly.

---

## 80. Background Processing and Consistency

Background processing must not bypass core authorization or lifecycle rules.

A worker must validate relevant:

* Business;
* Branch;
* subscription;
* entitlement;
* record state.

---

## 81. Error Recovery

If a core transaction fails:

* transaction rollback occurs;
* client receives failure;
* retry may be attempted using the same operation identity.

If a secondary operation fails:

* core transaction remains committed;
* secondary operation enters retry/error state.

---

## 82. Transaction Boundary Documentation

Every major domain operation should explicitly define:

* input;
* validation;
* authorization;
* core transaction;
* secondary operations;
* rollback behavior;
* idempotency key;
* concurrency control;
* failure behavior.

This becomes important during implementation and testing.

---

## 83. Performance Principle

Consistency mechanisms must not unnecessarily degrade POS performance.

The system should prefer:

* short transactions;
* narrow locks;
* indexed queries;
* atomic conditional updates;
* asynchronous secondary work;
* background processing;
* efficient idempotency checks.

---

## 84. Avoid Global Locking

The system should not use broad global locks for ordinary operations.

For example, one Branch's inventory operation must not unnecessarily block unrelated Branches.

Locks should be scoped as narrowly as possible.

---

## 85. Deadlock Prevention

Operations using multiple locks must acquire them in deterministic order where possible.

The system should:

* keep transactions short;
* avoid unnecessary lock nesting;
* detect deadlocks;
* retry safe transactions where appropriate.

---

## 86. Deadlock Recovery

A deadlock victim transaction may be retried if the operation is idempotent and safe.

Retry must not create duplicate business effects.

---

## 87. Race Condition Handling

Race conditions must be resolved through authoritative state transitions.

The system must not depend on:

* frontend timing;
* user interface delays;
* JavaScript state;
* client-side locks.

---

## 88. Time Ordering

Server timestamps are authoritative for current server-side ordering.

Client timestamps may be retained as metadata but must not override server lifecycle state.

Offline events may preserve original client/event time while synchronization time is recorded separately.

---

## 89. Clock Rollback

Clock rollback or suspicious timestamp behavior must be detectable.

Suspicious events must not be allowed to bypass:

* subscription expiry;
* employee deactivation;
* device authorization;
* lifecycle rules.

---

## 90. Consistency Across Devices

Multiple trusted devices may operate against the same Business.

The system must ensure:

* UUID-based identity;
* server-side validation;
* synchronization;
* idempotency;
* conflict handling.

One device must not be trusted merely because another device previously performed the operation.

---

## 91. Multiple Devices in One Cash Session

Multiple trusted devices may operate within the same Cash Session according to the current business model.

Every action must retain:

* Employee UUID;
* Device UUID;
* Cash Register UUID;
* Cash Session UUID;
* Transaction UUID where applicable.

---

## 92. Permission Change During Concurrency

If permissions change while an operation is in progress:

* the transaction's authorization decision must be deterministic;
* an operation that has not yet passed authorization must use current permission;
* stale UI state cannot grant permission.

---

## 93. Employee Deactivation During Concurrency

If an employee is deactivated while a request is being processed:

* the system must use a deterministic transaction boundary;
* unauthorized new operations must be rejected;
* historical operations already committed remain valid.

---

## 94. Subscription Expiry During Concurrency

If expiry occurs during a modifying operation:

* transaction ordering determines whether the operation was authorized;
* the operation must not be partially committed;
* later operations must use the new entitlement state.

---

## 95. Report Snapshot During Correction

If a correction occurs while a report is being generated:

* report uses one consistent snapshot;
* correction belongs either before or after that snapshot;
* the report is not internally mixed.

If the correction changes relevant metrics, a later report version may be generated.

---

## 96. Notification Ordering

Notifications should be generated after the core event is durably committed where possible.

This prevents notifications describing transactions that ultimately rolled back.

---

## 97. Audit Ordering

Audit events for critical operations should correspond to the committed operation.

An audit record must not claim a successful state change if the core transaction rolled back.

---

## 98. Consistency During System Restart

After application/server restart:

* committed core transactions remain committed;
* incomplete transactions are rolled back by the database;
* durable queues retain pending secondary work;
* synchronization queues retain unsynced events;
* background jobs recover from durable state.

---

## 99. Consistency During Worker Failure

If a worker fails after the core transaction but before a secondary action:

* the core state remains valid;
* durable secondary state allows retry;
* duplicate secondary effects are prevented through idempotency.

---

## 100. Consistency During Network Failure

Network failure does not automatically imply transaction failure.

Clients must use operation identity to safely determine the result after reconnect/retry.

---

## 101. Consistency During Database Failure

If the database transaction cannot commit:

* core state must not be treated as committed;
* client receives failure or uncertain-result handling;
* retry uses the same identity.

---

## 102. Uncertain Transaction Result

When the client cannot determine whether a transaction committed:

* it must query or retry using the same operation identity;
* it must not create a new logical operation merely because the result is unknown.

---

## 103. Core Financial Integrity

Financial operations require especially strong consistency.

The system must prevent:

* duplicate payment;
* duplicate refund;
* duplicate debt repayment;
* duplicate overpayment;
* payment above allowed limits unless explicitly accepted as overpayment;
* inconsistent Cash Session totals.

---

## 104. Core Inventory Integrity

Inventory operations require:

* atomic stock changes;
* no negative stock;
* concurrency protection;
* movement history;
* correction history.

---

## 105. Core Order Integrity

An Order must have:

* stable UUID;
* valid Business;
* valid Branch;
* valid lifecycle state;
* consistent pricing snapshot;
* consistent inventory relationship;
* consistent payment relationship.

---

## 106. Core Cash Integrity

Cash Sessions must preserve:

* one authoritative lifecycle state;
* opening cash;
* expected cash;
* actual counted cash;
* difference;
* closing actor;
* correction history.

---

## 107. Core Report Integrity

Report versions must preserve:

* report definition;
* period;
* scope;
* snapshot;
* creation reason;
* creation source;
* immutable result.

---

## 108. Core Configuration Integrity

Configuration versions must preserve:

* previous version;
* new version;
* effective time;
* actor;
* approval state where applicable;
* historical context.

---

## 109. Core Subscription Integrity

Subscription state must preserve:

* tariff;
* tariff version;
* entitlement;
* effective time;
* expiry;
* lifecycle transition history.

---

## 110. Consistency Testing

Concurrency-sensitive operations must be tested with scenarios such as:

* simultaneous Order acceptance;
* simultaneous final-stock sales;
* duplicate payment;
* duplicate refund;
* simultaneous Cash Session opening;
* simultaneous session closing;
* correction-limit race;
* concurrent inventory purchase and sale;
* simultaneous debt repayments;
* permission change during request;
* employee deactivation during request;
* subscription expiry during request;
* renewal vs expiry;
* reactivation vs deletion;
* duplicate background jobs;
* duplicate synchronization events.

---

## 111. Failure Injection

Testing should include controlled failures at important boundaries:

* before transaction commit;
* after transaction commit;
* before notification;
* after notification scheduling;
* before synchronization response;
* after synchronization commit;
* during background job;
* during deletion stage.

The purpose is to verify idempotency and recovery.

---

## 112. Consistency Observability

The system should expose operational metrics for:

* transaction failures;
* deadlocks;
* lock waits;
* duplicate requests;
* idempotency hits;
* synchronization conflicts;
* background retries;
* report conflicts;
* deletion failures.

Sensitive Business data should not be unnecessarily exposed in operational metrics.

---

## 113. System-Wide Invariants

The following invariants apply to system-wide consistency and concurrency:

1. Server state is authoritative for current state.
2. Core business operations are atomic.
3. Partial core transactions are not accepted.
4. Secondary failures do not normally roll back committed core transactions.
5. Critical uniqueness is protected at the database/system level.
6. Idempotency is required for retry-sensitive operations.
7. Duplicate requests must not create duplicate core effects.
8. Stable UUIDs are preserved across retries.
9. Transaction UUIDs remain stable across retries.
10. Event UUIDs remain stable across synchronization retries.
11. Lost responses do not imply failed transactions.
12. Client retries must reuse operation identity.
13. Inventory cannot become negative.
14. Final inventory consumption is concurrency-safe.
15. Order acceptance and inventory deduction are atomic.
16. Failed inventory return rolls back the complete modification.
17. Payments validate current payable state.
18. Duplicate payments are prevented.
19. Duplicate refunds are prevented.
20. Refunds cannot exceed refundable amount.
21. Debt allocation cannot exceed outstanding debt.
22. Debt repayment and allocation remain consistent.
23. One Branch/register cannot have conflicting active Cash Sessions.
24. Cash Session opening is concurrency-safe.
25. Cash Session closing is concurrency-safe.
26. Cash correction limits are concurrency-safe.
27. Handover cannot create multiple active sessions.
28. Table occupancy remains consistent with operational Orders.
29. Draft Orders do not reserve table occupancy.
30. Accepted Orders participate in table occupancy.
31. Paid Orders remain historical even after payment.
32. Payment does not automatically change operational Order status.
33. Paid Orders cannot be ordinarily edited.
34. Concurrent stale Order modifications cannot silently overwrite newer state.
35. Price changes do not rewrite existing Order price snapshots.
36. Configuration changes are versioned.
37. Configuration effective time is deterministic.
38. Stale configuration cannot silently overwrite newer configuration.
39. Employee permissions are server-validated.
40. Employee deactivation is server-enforced.
41. Branch scope is server-enforced.
42. Subscription entitlement is server-enforced.
43. Trusted device state does not replace authorization.
44. Offline operations remain subject to server revalidation.
45. Offline conflicts are explicit.
46. Server does not silently accept conflicting offline state.
47. Configuration synchronization occurs after required transaction synchronization.
48. Reports use consistent snapshots.
49. Report versions are immutable.
50. Relevant report changes create new versions where required.
51. Notification failure does not roll back committed core transactions.
52. Critical audit events correspond to committed state.
53. Background jobs are idempotent.
54. Background jobs are recoverable.
55. Duplicate workers cannot create duplicate core effects.
56. Job ownership is concurrency-safe.
57. Deadlock recovery does not create duplicate effects.
58. Locks remain scoped as narrowly as practical.
59. Global locks are avoided for ordinary operations.
60. Tenant isolation applies to every operation.
61. Cross-tenant requests are rejected.
62. Cross-Branch access requires authorization.
63. Business UUID alone does not grant access.
64. Branch UUID alone does not grant access.
65. Client-provided scope cannot override server scope.
66. Historical data is not silently rewritten.
67. Corrections are represented as separate traceable operations where required.
68. Financial originals remain immutable.
69. Inventory history remains traceable.
70. Cash Session history remains traceable.
71. Report history remains immutable.
72. Configuration history remains traceable.
73. Subscription history remains traceable.
74. Audit history remains immutable.
75. Server time is authoritative for lifecycle decisions.
76. Client time cannot bypass lifecycle restrictions.
77. Clock rollback cannot extend authorization.
78. Active sessions do not automatically bypass changed permissions.
79. Subscription expiry cannot be bypassed by an existing session.
80. Renewal and expiry races are deterministic.
81. Reactivation and deletion races are deterministic.
82. Deleted Business data cannot be recreated through stale synchronization.
83. Business deletion cannot affect unrelated Businesses.
84. Background processing cannot bypass Business lifecycle rules.
85. Report generation cannot create inconsistent mixed-state reports.
86. Export cannot grant modification authority.
87. Secondary processing cannot create false core state.
88. Transaction failure must leave core state consistent.
89. Worker failure must leave recoverable job state.
90. Network failure must not create duplicate logical operations.
91. Database failure must not be interpreted as successful commit without verification.
92. Uncertain transaction results must be safely recoverable.
93. Core financial operations require strong consistency.
94. Core inventory operations require strong consistency.
95. Core Cash Session operations require strong consistency.
96. Core subscription lifecycle transitions require strong consistency.
97. Critical concurrency decisions must be deterministic.
98. Consistency mechanisms must not unnecessarily block unrelated Businesses.
99. POS-critical transactions must remain short and performant.
100. System-wide consistency must remain auditable.
101. System-wide concurrency rules must be testable.
102. Failure recovery must preserve historical integrity.
103. Retry logic must preserve operation identity.
104. Idempotency must be applied consistently across synchronous and asynchronous boundaries.
105. Core transaction boundaries must be explicitly documented.
106. Cross-module state must never be silently contradictory.
107. Server-side validation is mandatory for security-sensitive state transitions.
108. Offline continuity is allowed only within valid authorization boundaries.
109. Business correctness takes priority over UI convenience.
110. Data integrity takes priority over permissive failure.
111. Concurrency handling must preserve tenant isolation.
112. Concurrency handling must preserve Branch isolation.
113. Concurrency handling must preserve financial integrity.
114. Concurrency handling must preserve inventory integrity.
115. Concurrency handling must preserve historical integrity.
116. Every critical race condition must have a deterministic outcome.
117. Every retry-sensitive operation must have a defined idempotency strategy.
118. Every core operation must define rollback behavior.
119. Every secondary operation must define failure/retry behavior.
120. System-wide consistency must remain recoverable after restart, timeout, worker failure and network interruption.

---

## 114. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/01_System_Context_and_Boundaries.md`
* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/10_Kitchen_and_Printing.md`
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
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 115. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `27_System_Wide_Consistency_and_Concurrency.md`

**Next Document:** `28_Background_Jobs_and_Recovery.md`

