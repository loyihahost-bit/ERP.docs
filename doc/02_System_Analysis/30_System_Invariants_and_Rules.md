# System Invariants and Rules

**Document ID:** SA-30
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document consolidates the system-wide invariants and rules that must remain true across the FastFood ERP system.

The purpose is to provide a single system-level reference for rules that cross multiple modules and cannot safely be interpreted independently by one feature.

This document does not replace detailed module-specific documents.

Instead:

* module documents define detailed behavior;
* this document defines cross-module invariants;
* Business Analysis defines what the business requires;
* System Analysis defines how the system must preserve those requirements.

If a detailed module document conflicts with a system-wide invariant, the conflict must be resolved before implementation.

---

# 2. Rule Authority

The FastFood ERP rule hierarchy is:

```text
Business Requirements
        ↓
System Analysis
        ↓
System-Wide Invariants
        ↓
Module-Specific Rules
        ↓
Implementation
```

System-wide invariants must not be weakened merely for implementation convenience.

Business-specific configuration may change operational defaults where explicitly supported, but configuration must never violate system integrity, security, tenant isolation, financial correctness, or historical integrity.

---

# 3. Core System Principles

The system follows these principles:

1. Server authority is preserved for online state.
2. Offline operations are permitted only within explicitly authorized boundaries.
3. Core business transactions are atomic where required.
4. Duplicate operations are prevented through UUID-based idempotency.
5. Historical information is preserved.
6. Corrections are separate from original records.
7. Security validation is enforced server-side.
8. Business and Branch isolation is mandatory.
9. Subscription entitlement is enforced independently from frontend visibility.
10. Secondary failures must not unnecessarily roll back successful core transactions.
11. Conflicts must be explicit when automatic resolution is unsafe.
12. Failed operations must be recoverable where technically and logically possible.
13. POS performance must remain a first-class system requirement.
14. Error handling must not create silent data loss.
15. Important state changes must remain auditable.

---

# 4. Identity Invariants

## 4.1 UUID Identity

Important persistent entities must have stable UUID-based identity.

This includes, where applicable:

* Business;
* Branch;
* Employee;
* Device;
* Cash Register;
* Cash Session;
* Order;
* Payment;
* Refund;
* Debt repayment;
* Inventory transaction;
* Configuration version;
* Sync Event;
* Conflict;
* Background Job;
* Report Version;
* Notification;
* Audit Event.

## 4.2 No Client Transaction ID

The system does not use a separate Client Transaction ID as the primary transaction identity.

UUIDs provide identity and idempotency.

## 4.3 Identity Stability

Once an entity is created, its UUID must not change because of:

* synchronization;
* retry;
* migration;
* background processing;
* correction;
* report generation;
* device replacement.

---

# 5. Tenant Invariants

The system hierarchy is:

```text
Platform
    ↓
Business
    ↓
Branch
```

## 5.1 Business Isolation

Every tenant-owned operation must remain associated with exactly one Business.

## 5.2 Branch Context

Branch-scoped entities must belong to a valid Branch within the same Business.

## 5.3 Cross-Tenant Access

A request belonging to Business A must never read, modify, export, synchronize, or delete Business B data.

## 5.4 Background Jobs

Background jobs must preserve Business context.

A worker must never execute a job against another Business because context was lost.

## 5.5 Synchronization

Offline synchronization must preserve Business and Branch identity.

---

# 6. Employee Invariants

Employees have individual accounts.

Normal operational workflows must not depend on shared employee identities.

Employee lifecycle:

```text
Created
→ Active
→ Inactive
```

An inactive employee:

* cannot perform new authorized operations;
* remains present in historical records;
* does not disappear from audit history;
* cannot bypass deactivation through offline mode.

Previously completed operations remain valid.

---

# 7. Authorization Invariants

Effective authorization is determined by:

```text
Role Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
+
Employee Status
+
Device Trust where applicable
```

## 7.1 Server Enforcement

Frontend visibility is never sufficient authorization.

Every protected operation must be validated server-side.

## 7.2 No Permission Escalation

A Manager cannot grant permissions beyond the authority available to that Manager.

## 7.3 Branch Scope

An employee may have different permissions in different Branches.

Changing Branch context must recalculate effective permissions.

## 7.4 Immediate Important Checks

Important operations must validate current authorization rather than relying only on permissions loaded when the session began.

---

# 8. Device Trust Invariants

A device and employee are separate identities.

Trusted device status:

* does not automatically grant employee permissions;
* does not replace employee authentication;
* is Business-aware;
* is Branch-aware where required;
* may be revoked.

A new device must be registered online before it can operate offline.

Offline authorization must be:

* cryptographically protected;
* time-bounded;
* Business-aware;
* Branch-aware;
* employee-aware;
* permission-aware;
* subscription-aware.

---

# 9. Offline Invariants

Offline operation exists to preserve operational continuity, not to bypass server rules.

## 9.1 Trusted Devices Only

Offline operation is available only to authorized trusted devices.

## 9.2 First Use

A device cannot begin first-time operation offline.

## 9.3 Local Durability

An accepted offline transaction must be stored durably before synchronization is attempted.

## 9.4 UUID Preservation

Offline transactions retain their original UUID during synchronization.

## 9.5 Server Revalidation

Server-side validation remains authoritative when offline transactions synchronize.

## 9.6 No Silent Discard

A queued transaction must not be silently deleted because synchronization failed.

## 9.7 Subscription Boundaries

Offline authorization cannot extend beyond its permitted entitlement and time bounds.

---

# 10. Order Invariants

Supported current order types:

* Hall / Dine-in;
* Takeaway.

Phone Delivery remains future scope.

## 10.1 Order Identity

Every Order has a stable UUID.

## 10.2 Customer-Facing Number

The customer-facing 3-digit order number:

* is session-scoped;
* resets when a new Cash Session begins;
* is not the permanent order identity.

## 10.3 Draft

Draft orders:

* are editable;
* do not deduct inventory;
* do not reserve inventory;
* do not create operational table occupancy;
* do not create kitchen processing requirements.

A Draft may be lost after device restart according to the accepted business/system behavior.

## 10.4 Acceptance

Acceptance requires:

* valid authorization;
* valid Business and Branch;
* valid current configuration;
* sufficient stock;
* valid order state.

Order acceptance and inventory deduction form one core atomic operation.

If inventory deduction fails:

```text
Order remains unaccepted
Inventory remains unchanged
```

## 10.5 Lifecycle

The operational lifecycle is:

```text
Draft
→ Accepted
→ Preparing
→ Ready
→ Served
```

`Cancelled` is a terminal outcome.

There is no `Completed` order state.

## 10.6 Payment Independence

Payment does not automatically change operational order status.

A paid order may remain:

* Accepted;
* Preparing;
* Ready;
* Served.

## 10.7 Paid Order Editing

A fully paid order cannot be modified through ordinary editing.

Controlled correction/refund/cancellation workflows are used where authorized.

---

# 11. Order Modification Invariants

Before payment, permitted order modifications may include:

* product removal;
* quantity reduction;
* product quantity increase;
* adding a new operational product ticket.

## 11.1 Stock Increase

If an increase requires stock that is unavailable:

```text
Entire modification = Rejected
```

Partial modification is not permitted.

## 11.2 Inventory Return

When removing/reducing a product, the system asks whether the relevant inventory should be returned.

The decision is recorded.

## 11.3 Return Failure

If required inventory return fails:

```text
Entire modification = Rolled Back
```

## 11.4 New Product After Acceptance

A newly added product after acceptance becomes a new operational order/ticket with its own identity and kitchen ticket while remaining linked to the main/table context.

---

# 12. Table Invariants

A table is Busy when at least one open/unpaid order is associated with it.

Paid historical orders may remain visible without keeping the table Busy.

Table Visit/Session grouping represents a specific operational visit.

When the table is freed:

```text
Previous Table Visit
→ Closed

New customer/order
→ New Table Visit
```

Old grouping must not silently absorb a later visit.

---

# 13. Waiter Invariants

An order may have a primary waiter.

A second waiter may temporarily assist where permitted.

The primary waiter relationship is preserved unless an authorized operation changes it.

Waiter attribution is preserved for relevant:

* orders;
* overpayments;
* reports;
* historical records.

---

# 14. Kitchen and Printing Invariants

Kitchen printing is a secondary operation.

Order acceptance does not depend on successful physical printing.

If printing fails:

* order remains in its valid operational state;
* print state becomes failed/pending/retrying as applicable;
* retry uses the original ticket identity;
* failure remains observable.

A printer failure must never silently roll back a successful order transaction.

---

# 15. Inventory Invariants

## 15.1 Product Types

Inventory supports:

* Raw Material;
* Semi-Finished Product;
* Finished Product.

Dependencies may follow:

```text
Raw Material
    ↓
Semi-Finished Product
    ↓
Finished Product
```

## 15.2 No Negative Stock

Negative stock is never permitted.

## 15.3 Atomic Stock Consumption

Inventory consumption must be atomic with the corresponding core transaction.

## 15.4 Concurrency

Concurrent consumption of the same stock must be protected using appropriate database transaction and locking mechanisms.

Only valid transactions may consume available stock.

## 15.5 FIFO and Cost Methods

The system supports:

* FIFO;
* Average Cost;
* Last Purchase Cost.

The selected costing method must not change historical transactions.

---

# 16. Recipe Invariants

A recipe product cannot be destructively deleted.

Instead:

```text
Active Recipe
→ Archived Recipe
```

Historical recipe versions remain available.

New or changed recipes require appropriate approval before becoming effective.

Recipe changes become effective from the next Cash Session according to configuration rules.

Existing orders preserve their applicable configuration snapshot.

---

# 17. Set Invariants

Sets are independent bundle products.

A Set has:

* its own identity;
* selling price;
* component configuration;
* configuration version.

Mandatory unavailable components prevent Set sale.

Set composition changes do not silently alter already-created orders.

Set configuration changes become effective according to the next Cash Session configuration rule.

---

# 18. Menu and Pricing Invariants

Global menu configuration belongs to the Business.

Branches may enable or disable permitted global products.

Each product belongs to exactly one menu category.

Prices may exist as:

```text
Global Standard Price
+
Branch Override
```

Price changes become effective according to the next Cash Session configuration rule.

Open orders preserve their applicable price snapshot.

Later price changes must not silently rewrite historical order prices.

---

# 19. Discount Invariants

Discounts:

* are separate from base prices;
* require appropriate permission;
* affect transaction amount;
* do not rewrite the original product price;
* remain historically traceable.

Discount changes must not corrupt historical reports.

---

# 20. Custom Markup Invariants

Custom order markup is constrained to:

```text
0% – 100%
```

The configured final amount is based on:

```text
Cost × (1 + Markup / 100)
```

where cost uses Last Purchase Cost according to the accepted business rule.

Cashiers cannot arbitrarily change standard product prices through ordinary POS operation.

---

# 21. Payment Invariants

Supported payment methods:

* Cash;
* Card;
* Debt;
* Mixed.

Every Payment has a stable UUID.

## 21.1 Payment Lifecycle

The payment lifecycle is:

```text
Pending
→ Completed
```

Refund and correction are separate operations.

## 21.2 Payment Validation

Payment requires:

* valid order;
* valid Business;
* valid Branch;
* authorization;
* payable order state;
* valid remaining amount unless overpayment is explicitly permitted.

## 21.3 Idempotency

Repeated payment requests with the same Payment UUID cannot create duplicate payment records.

## 21.4 Uncertain Result

If payment result is unknown, the system checks the original Payment UUID before retrying.

---

# 22. Overpayment Invariants

When received/entered amount exceeds the order amount:

1. The system identifies the excess.
2. Confirmation is requested where required.
3. The original order amount remains the order settlement amount.
4. The excess becomes a separate overpayment.
5. Overpayment belongs to Business/Branch.
6. Cashier attribution is preserved.
7. Waiter attribution is preserved where applicable.
8. Overpayment remains visible in reports.
9. Overpayment is not treated as employee incentive.
10. Overpayment does not create customer debt.

---

# 23. Mixed Payment Invariants

Mixed payment remains one logical payment operation with internal portions.

Example:

```text
Order
    ↓
Payment
    ├── Cash Portion
    └── Card Portion
```

The Cash portion contributes to physical Cash Session totals.

The Card portion remains separately attributable.

The order itself is not split into multiple orders.

---

# 24. Debt Invariants

Debt is represented through a Customer record and debt orders.

One customer may have multiple debt orders.

Partial repayment is allowed.

Customer phone numbers are not required to be globally unique.

Historical orders preserve their customer information snapshot.

Debt repayment:

* has a stable identity;
* is idempotent;
* may be Cash or Card;
* may allocate against one or multiple debt orders;
* cannot exceed outstanding debt.

Customer balance and debt allocation must remain consistent.

---

# 25. Refund Invariants

Refunds are separate financial operations.

Refunds may be:

* full;
* partial;
* item-level;
* quantity-level.

Refund requires:

* authorization;
* mandatory reason;
* valid refundable amount;
* valid payment/order context.

Supported refund methods:

* Cash;
* Card.

Refund does not automatically return inventory.

Served items must never automatically return inventory.

---

# 26. Cancellation Invariants

Cancellation is distinct from refund.

Cancellation:

* requires authorization;
* requires a reason;
* preserves the original order;
* does not delete the order;
* remains auditable.

If inventory was previously deducted, the system may return eligible inventory according to cancellation rules.

Served items are never automatically returned to inventory.

---

# 27. Payment Correction Invariants

A completed payment is not silently rewritten.

A correction creates a separate revision/correction record.

The original payment remains immutable as historical evidence.

Every correction stores, where applicable:

* original value;
* new value;
* actor;
* reason;
* timestamp;
* related transaction;
* audit information.

---

# 28. Cash Register Invariants

Current business model uses one primary Cash Register per Branch.

The architecture must not prevent future multiple registers.

The Cash Register has a stable identity.

Cash Sessions are created under the register.

```text
Branch
    ↓
Cash Register
    ↓
Cash Session
```

---

# 29. Cash Session Invariants

Cash Session lifecycle:

```text
Not Open
→ Open
→ Closed
```

A closed Cash Session cannot return to Open state.

A new shift creates a new Cash Session UUID.

The physical Cash Register identity remains the same.

---

# 30. Cash Session Opening

Opening a session requires:

* authorized cashier;
* valid Business;
* valid Branch;
* valid register;
* valid trusted device where required;
* valid opening cash amount.

Opening cash amount becomes part of the session's historical record.

---

# 31. Cash Session Closing

Expected cash is hidden until the cashier enters physical cash count.

After physical count, the system calculates:

* expected cash;
* actual cash;
* difference;
* relevant order count;
* payment totals.

The physical cash count concerns cash only.

Card totals are derived separately.

---

# 32. Cash Discrepancy Invariants

Shortage and overage must be preserved historically.

A discrepancy cannot be silently deleted.

Corrections create separate correction records.

The original difference remains immutable.

---

# 33. Cash Correction Invariants

A Cash Session permits:

* maximum 3 normal corrections;
* one additional correction after explicit authorization.

After the authorized additional correction is consumed, further administrative intervention is required.

"Reopen" means:

```text
Create correction opportunity
```

not:

```text
Reopen closed Cash Session
```

---

# 34. Cash Handover Invariants

Handover follows:

```text
Previous Cashier
    ↓
Close Previous Cash Session
    ↓
New Cashier Authenticates
    ↓
Count / Accept Cash
    ↓
Open New Cash Session
```

The previous session remains historical and permanently closed.

The new cashier receives a new Cash Session UUID.

Open orders continue and retain their Order UUID.

Actions before handover remain attributed to the previous cashier/session.

Actions after handover belong to the new cashier/session.

---

# 35. Cash Session Concurrency

Only one active primary Cash Session may exist for a Branch under the current model.

If two requests attempt to open sessions concurrently:

```text
First valid request
→ SUCCESS

Second request
→ REJECTED
```

This must be enforced server-side.

---

# 36. Multiple Trusted Devices

Multiple trusted devices may operate within the same Cash Session where authorized.

Every action retains:

* employee;
* device;
* register;
* Cash Session;
* transaction identity.

The device identity must not be confused with Cash Session identity.

---

# 37. Attendance Invariants

Attendance records must preserve:

* employee;
* Branch;
* role context where relevant;
* timestamps;
* status;
* corrections.

Corrections do not silently rewrite the original attendance history.

Inactive employees cannot create new valid attendance events after their effective deactivation boundary.

---

# 38. Payroll Invariants

Payroll is period-based.

Payroll lifecycle:

```text
Draft
→ Calculated
→ Finalized
```

Finalized payroll is immutable.

Corrections create separate correction records.

Payroll calculation uses a consistent snapshot of:

* attendance;
* salary configuration;
* bonuses;
* relevant employee data.

Salary configuration changes preserve old and new versions with effective dates.

---

# 39. Report Invariants

A report is identified by:

```text
Report Definition
+
Period
+
Scope
```

Each generated report has a Report Version UUID.

Reports use a consistent transactional snapshot.

Finalized report versions are immutable.

If relevant underlying data changes:

```text
Version N
→ Version N+1
```

The previous version remains available according to access and lifecycle rules.

A correction that does not change relevant report metrics does not require a new report version.

---

# 40. Report Generation Invariants

Monthly reports are generated according to the defined month-end schedule.

An open Cash Session that affects the report may cause generation to wait until required session closure.

Manual report periods cannot exceed one calendar month.

Invalid date ranges are rejected.

Empty reports are still valid reports and must represent zero/empty results correctly.

---

# 41. Excel Export Invariants

Excel export uses `.xlsx`.

Export must represent the selected report snapshot.

An export failure must not modify the report.

Large exports may run as background jobs.

Export operations may be audited where required.

---

# 42. Notification Invariants

Notifications represent important system conditions or events.

Notification states may include:

```text
Active
→ Read
→ Resolved / Expired
```

Read state is recipient-specific.

Duplicate active notifications for the same logical condition must be prevented.

When a condition resolves, the notification history remains.

If the condition occurs again later, a new notification cycle may begin.

Notification failure does not roll back the operation that created the condition.

---

# 43. Audit Invariants

Important state-changing operations must be auditable.

Audit records may include:

* Event UUID;
* Business;
* Branch;
* actor;
* Device;
* Cash Session;
* Transaction;
* entity;
* old state;
* new state;
* reason;
* source;
* result;
* timestamp.

Audit records are immutable.

Ordinary reads are not normally audited unless classified as sensitive operations.

---

# 44. Historical Integrity Invariants

The system must preserve historical meaning.

The following must not be silently overwritten:

* original order;
* original payment;
* original refund;
* original Cash Session result;
* original inventory transaction;
* original recipe version;
* original price snapshot;
* original payroll finalization;
* original report version;
* original audit record;
* original correction source.

Corrections are additive historical events.

---

# 45. Synchronization Invariants

Synchronization must preserve:

* Event UUID;
* Transaction UUID;
* Business;
* Branch;
* Employee;
* Device;
* original event context.

Queue states include:

```text
Pending
→ Syncing
→ Synced
```

or:

```text
Pending
→ Syncing
→ Retrying
→ Failed
```

or:

```text
Pending
→ Syncing
→ Conflict
```

---

# 46. Synchronization Ordering

Dependent transactions must be synchronized in dependency order.

Where required:

```text
Transaction
    ↓
Dependent Event
```

must be processed before:

```text
Configuration Update
```

that would make the transaction invalid without a proper historical interpretation.

Transaction synchronization takes priority over configuration synchronization where previously defined.

---

# 47. Synchronization Conflict Invariants

A conflict must be explicit when automatic resolution is unsafe.

Examples:

* inventory conflict;
* payment conflict;
* order conflict;
* Cash Session conflict;
* configuration conflict;
* employee authorization conflict.

Conflict resolution requires:

* authorization;
* reason;
* result;
* audit.

The server remains authoritative for current server state.

Offline transaction history is not silently discarded.

---

# 48. Configuration Invariants

Configuration includes:

* menu;
* price;
* recipe;
* Set;
* equipment availability;
* employee permissions;
* notification thresholds;
* subscription entitlement.

Configuration changes are versioned where historical integrity requires it.

Changes become effective according to their defined effective boundary.

For menu/recipe/price/Set changes, the accepted operational boundary is generally the next Cash Session.

Existing open orders preserve their configuration snapshot.

---

# 49. Subscription Invariants

Subscription lifecycle:

```text
Active
→ Expired / Read-Only
→ Deletion Eligible
→ Deleting
→ Deleted
```

Subscription expiry blocks modifying functions according to entitlement rules.

Read-only operations remain available where permitted.

Existing data is not immediately deleted at expiry.

The deletion countdown begins from the exact:

```text
subscription_expired_at
```

---

# 50. Grace Period Invariants

Subscription renewal has a default grace period of 3 days according to the accepted business rule.

The grace period must not silently extend entitlement beyond the configured lifecycle policy.

Server time determines the effective lifecycle state.

---

# 51. Subscription Downgrade Invariants

Downgrading a tariff:

* preserves existing data;
* preserves historical data;
* does not destructively remove employees;
* does not destructively remove features' historical records;
* blocks operations beyond the new entitlement.

If employee limits are exceeded after downgrade:

* existing employee data remains;
* new employee creation is blocked where required;
* management state clearly indicates the entitlement violation.

---

# 52. Reactivation Invariants

Reactivation within the permitted 60-day period restores existing Business data and configuration.

Reactivation and deletion must be resolved atomically when they occur concurrently.

If reactivation wins before deletion becomes irreversible:

```text
Deletion must not continue
```

---

# 53. Data Deletion Invariants

After the permitted lifecycle period:

```text
Permanent Deletion Eligible
→ Deleting
→ Deleted
```

Deletion is performed through background processing.

Deletion must be:

* durable;
* idempotent;
* resumable;
* observable.

Partial failure must not restart already-completed deletion work unnecessarily.

Stale offline events must never recreate deleted tenant data.

---

# 54. Background Job Invariants

Every important background job has a stable Job UUID.

Lifecycle:

```text
Pending
→ Running
→ Completed
```

or:

```text
Running
→ Retrying
→ Failed
```

Workers use durable job state.

Worker restart must not silently lose jobs.

Duplicate execution must be controlled through idempotency.

Background processing must not unnecessarily block POS.

---

# 55. Error Handling Invariants

Expected errors have stable error codes.

Errors are classified as:

* retryable;
* non-retryable;
* conditionally retryable.

Retry must preserve transaction identity.

A timeout does not automatically mean that the transaction failed.

The system must determine the result where possible before repeating critical operations.

---

# 56. Core vs Secondary Operations

Core operations define business correctness.

Examples:

* order acceptance;
* inventory deduction;
* payment creation;
* debt repayment;
* refund;
* Cash Session closure;
* inventory adjustment.

Secondary operations include:

* printing;
* notifications;
* report generation;
* derived data;
* background processing.

A secondary failure must not unnecessarily roll back a successful core transaction.

---

# 57. Atomicity Invariants

Where business correctness requires atomicity:

```text
All Core Changes
or
No Core Changes
```

Examples:

```text
Order Acceptance
+
Inventory Deduction
```

```text
Debt Repayment
+
Debt Allocation
```

```text
Inventory Adjustment
+
Stock Update
```

---

# 58. Concurrency Invariants

The system must safely handle concurrent requests.

Required mechanisms may include:

* database transactions;
* row-level locking;
* optimistic version checks;
* unique constraints;
* atomic conditional updates;
* idempotency.

Examples include:

* last stock unit;
* Cash Session opening;
* payment completion;
* order modification;
* configuration changes.

---

# 59. Race Condition Invariants

A race condition must not produce:

* negative stock;
* duplicate payment;
* duplicate refund;
* duplicate Cash Session;
* duplicate debt repayment;
* inconsistent order state;
* inconsistent report version;
* duplicate background job.

The server must determine the valid winner according to transactional rules.

---

# 60. Error Recovery Invariants

Recovery must not silently change business meaning.

A failed:

* payment cannot silently become debt;
* refund cannot silently become discount;
* inventory conflict cannot silently choose arbitrary stock;
* cash shortage cannot silently disappear;
* report cannot silently overwrite its previous version.

Recovery actions must remain traceable.

---

# 61. Performance Invariants

Security, audit, error handling, and consistency must not create unnecessary POS latency.

The system should:

* keep core POS transactions short;
* use background processing for heavy work;
* avoid synchronous report generation;
* avoid synchronous notification delivery;
* avoid blocking printing;
* use efficient database operations;
* batch synchronization;
* limit retry loops.

---

# 62. POS Availability Invariants

The POS must continue operating during temporary failures where business rules permit.

Temporary failure of:

* notification;
* printer;
* report generation;
* background worker

must not unnecessarily stop order entry or payment operations.

Offline operation provides continuity when network availability is lost and the device remains authorized.

---

# 63. Security Invariants

Security must fail closed.

The system must reject:

* invalid authentication;
* invalid authorization;
* invalid Business context;
* invalid Branch context;
* invalid device trust;
* invalid offline authorization;
* invalid signature;
* replayed protected event;
* detected tampering.

Security mechanisms must not be bypassed because the system is offline.

---

# 64. Sensitive Information Invariants

User-facing errors and logs must not expose:

* passwords;
* authentication tokens;
* encryption keys;
* database credentials;
* sensitive payment credentials;
* private security material;
* another tenant's data;
* internal stack traces.

Detailed diagnostics are restricted to authorized operational users.

---

# 65. Data Consistency Across Modules

Cross-module operations must preserve consistent relationships.

Examples:

```text
Order
    ↔ Inventory
    ↔ Payment
    ↔ Cash Session
    ↔ Employee
    ↔ Branch
```

and:

```text
Recipe
    ↔ Product
    ↔ Inventory
    ↔ Menu
```

and:

```text
Employee
    ↔ Role
    ↔ Permission
    ↔ Branch
    ↔ Attendance
    ↔ Payroll
```

and:

```text
Subscription
    ↔ Entitlement
    ↔ Business
    ↔ Branch
    ↔ Employee
    ↔ Feature Access
```

Cross-module state must not contradict the authoritative transaction state.

---

# 66. Historical Reconstruction

The system must allow authorized users or system processes to reconstruct important historical events.

For a financial operation, the system should be able to determine:

* who performed it;
* when;
* which Business;
* which Branch;
* which Device;
* which Cash Session;
* which Order;
* which Payment;
* which configuration version;
* whether it was online/offline;
* whether a correction occurred.

---

# 67. Source of Truth

The server is the authoritative source for current server state.

Local offline data is authoritative only as the device's durable record of an operation that was validly created under its offline authorization.

During synchronization:

```text
Offline Transaction
        ↓
Server Validation
        ↓
Accepted / Rejected / Conflict
```

The system must not silently overwrite valid historical offline transaction data.

---

# 68. Current State vs Historical State

The system distinguishes:

### Current State

What is currently valid.

### Historical State

What was valid when an operation occurred.

Historical snapshots are required where later configuration changes would otherwise alter interpretation.

Examples:

* order price;
* recipe version;
* Set composition;
* employee permission context where required;
* report version;
* payment information.

---

# 69. Configuration Effective Boundaries

Configuration changes must not unpredictably affect operations already in progress.

For operational configuration such as:

* price;
* recipe;
* Set;
* menu availability;

the accepted boundary is generally the next Cash Session.

An active session continues using its valid configuration snapshot.

---

# 70. Subscription and Offline Boundary

Offline operation cannot become a mechanism for indefinite operation after entitlement expires.

The device must obey the offline authorization's:

* expiry;
* Business;
* Branch;
* employee;
* permission;
* subscription constraints.

After the authorization expires, modifying operations require online reauthorization.

---

# 71. Data Retention Invariants

Data retention must distinguish:

* operational data;
* financial records;
* historical configuration;
* audit records;
* report versions;
* notification history;
* synchronization data;
* technical logs;
* deletion metadata.

Business lifecycle rules must not accidentally delete information required to preserve historical integrity before the defined deletion stage.

---

# 72. Auditability of Corrections

Every correction must be distinguishable from the original operation.

A correction must not modify the original record in a way that removes evidence of its previous state.

Correction chains must remain traceable.

---

# 73. Report Integrity

Reports must reflect their defined snapshot.

A report version must not change because:

* a later order was created;
* a later price changed;
* a later recipe changed;
* a later correction occurred

unless the correction affects the relevant report definition and therefore requires a new version.

---

# 74. Notification Integrity

A notification represents a condition or event.

Notification read state must not be interpreted as condition resolution.

Similarly:

```text
Read ≠ Resolved
```

Condition resolution is determined by the underlying business state.

---

# 75. Printer Integrity

A printer represents a delivery mechanism for an already-created operational transaction.

Therefore:

```text
ERP Transaction
≠
Physical Print Result
```

A print failure does not mean the ERP transaction failed.

---

# 76. Background Processing Integrity

Background jobs operate on durable business state.

A job failure must not be interpreted as failure of the underlying core transaction unless the job itself is the authoritative operation.

For example:

```text
Report Job Failed
≠
Business Transaction Failed
```

---

# 77. Recovery Integrity

Recovery must preserve the distinction between:

```text
Original Operation
Correction
Retry
Conflict Resolution
Administrative Intervention
```

These are separate system events.

---

# 78. Cross-Device Consistency

Multiple trusted devices may operate within the same Business/Branch.

The system must assume that devices can have different local states.

Server validation and synchronization must reconcile these differences.

One device must not silently overwrite another device's valid transaction.

---

# 79. Offline Draft Invariants

An offline Draft may synchronize because Draft does not occupy a table and does not reserve stock.

When the Draft is later accepted:

* current server state is checked;
* table state is revalidated;
* inventory is revalidated;
* configuration is revalidated.

If the table context became invalid because an Accepted order already exists, the server state wins and the invalid Draft is discarded according to the defined conflict rule.

---

# 80. Session Boundary Invariants

Cash Session is an important operational boundary.

The system uses Cash Session boundaries for:

* customer-facing order numbering;
* configuration effective timing;
* cashier attribution;
* cash reconciliation;
* payment attribution;
* reports.

Changing cashier does not change the physical Cash Register identity.

---

# 81. Order and Payment Independence

Order lifecycle and payment lifecycle are independent.

Therefore:

```text
Order Status
≠
Payment Status
```

Payment completion does not automatically mean Served.

Order Served does not automatically imply a specific payment method.

---

# 82. Order and Inventory Independence Outside Core Acceptance

Inventory is tightly coupled to the core order acceptance transaction.

However:

* kitchen printing;
* table state display;
* notifications;
* reporting

are secondary consequences and must not corrupt the core order/inventory transaction.

---

# 83. Business Configuration vs System Invariants

Business owners may configure operational behavior where the system explicitly supports configuration.

However, configuration cannot disable fundamental invariants such as:

* tenant isolation;
* UUID identity;
* audit integrity;
* no negative stock;
* authorization;
* subscription enforcement;
* historical integrity;
* financial consistency;
* idempotency.

---

# 84. Default Values

Defaults are operational defaults, not immutable architectural requirements, unless explicitly stated otherwise.

Configurable defaults must be stored and versioned when changing them would affect historical interpretation.

Examples:

* notification thresholds;
* subscription grace period where policy allows;
* employee limits within tariff;
* feature configuration.

---

# 85. System Rule Conflict Resolution

If two module rules appear to conflict:

1. identify the affected business requirement;
2. identify the system invariant;
3. identify which rule is more specific;
4. preserve historical integrity;
5. preserve security and tenant isolation;
6. preserve financial/inventory correctness;
7. document the resolution;
8. update affected documents.

Conflicts must not be resolved silently during implementation.

---

# 86. Rule Change Management

Changes to system-wide invariants require:

* documented reason;
* affected documents identified;
* impact analysis;
* version update;
* related ADR where architectural consequences exist;
* consistency review across dependent modules.

A rule change must not be implemented in only one module if other modules depend on it.

---

# 87. Implementation Independence

These invariants define system behavior, not a mandatory implementation framework.

Implementation may use different:

* programming languages;
* databases;
* queue technologies;
* frontend frameworks;
* deployment models;

as long as the observable system behavior preserves these invariants.

---

# 88. Testing Invariants

Every critical invariant must have automated tests where practical.

Testing levels may include:

* unit tests;
* integration tests;
* database transaction tests;
* concurrency tests;
* API tests;
* offline tests;
* synchronization tests;
* security tests;
* end-to-end tests;
* recovery/failure tests.

---

# 89. Concurrency Testing

The system must explicitly test races such as:

```text
Two users → last stock unit
Two requests → Cash Session opening
Two requests → same payment
Two devices → same order modification
Two corrections → same Cash Session
Two configuration changes → same product
```

The expected winner/rejection behavior must be deterministic.

---

# 90. Failure Testing

The system must test:

* network interruption;
* request timeout;
* lost response;
* database failure;
* worker crash;
* printer failure;
* notification failure;
* synchronization conflict;
* storage failure;
* security tampering;
* subscription expiry;
* employee deactivation;
* device revocation;
* deletion failure.

---

# 91. Recovery Testing

Recovery tests must verify:

1. no duplicate transaction;
2. no silent data loss;
3. no invalid partial core transaction;
4. no negative inventory;
5. no unauthorized operation;
6. no tenant leakage;
7. correct audit trail;
8. correct final state;
9. correct retry behavior;
10. correct conflict handling.

---

# 92. Performance Testing

Performance tests must ensure that:

* POS remains responsive;
* core transactions remain short;
* background jobs are isolated;
* synchronization does not block POS;
* reports do not block POS;
* audit logging remains efficient;
* error logging does not create excessive overhead.

---

# 93. Observability Invariants

Important system operations must be diagnosable through:

* correlation IDs;
* transaction UUIDs;
* job UUIDs;
* error codes;
* audit events;
* technical logs;
* metrics.

A production failure should be traceable without modifying historical business data.

---

# 94. Administrative Intervention

Some failures require authorized human intervention.

Examples:

* unresolved financial conflict;
* exhausted Cash Session correction authorization;
* security incident;
* persistent deletion failure;
* unrecoverable synchronization conflict.

Administrative intervention must:

* require appropriate permission;
* record reason;
* preserve original state;
* create an audit record;
* produce a deterministic final state.

---

# 95. No Silent Recovery

The system must not silently:

* delete failed transactions;
* change payment amounts;
* alter inventory quantities;
* reopen closed sessions;
* change historical prices;
* change old recipes;
* overwrite reports;
* erase audit history;
* bypass permissions;
* bypass subscription restrictions.

If recovery changes business state, the change must be explicit and traceable.

---

# 96. System-Wide State Integrity

At any stable committed point, the following relationships must remain logically consistent:

```text
Business
    ↓
Branch
    ↓
Employee / Device / Register
    ↓
Cash Session
    ↓
Orders
    ↓
Payments
    ↓
Reports / Audit
```

and:

```text
Product
    ↓
Recipe / Set
    ↓
Inventory
    ↓
Order
```

and:

```text
Subscription
    ↓
Entitlement
    ↓
Allowed Operations
```

---

# 97. Final System Invariant Set

The following high-level rules summarize the entire System Analysis stage:

1. Every important entity has stable identity.
2. Every tenant-owned entity has valid Business context.
3. Every Branch-scoped entity has valid Branch context.
4. Authorization is server-enforced.
5. Subscription entitlement is server-enforced.
6. Device trust does not replace authorization.
7. Offline operation cannot bypass security.
8. Offline operation cannot bypass subscription limits.
9. Core transactions are atomic where required.
10. Duplicate operations are prevented.
11. Transaction UUIDs remain stable across retries.
12. Timeouts do not automatically imply failure.
13. Lost responses do not create duplicate transactions.
14. Negative inventory is impossible.
15. Payment duplication is prevented.
16. Cash Session duplication is prevented.
17. Closed Cash Sessions remain closed.
18. Corrections do not rewrite history.
19. Refunds are separate financial operations.
20. Overpayments belong to Business/Branch.
21. Order and payment lifecycles remain independent.
22. Historical prices remain stable.
23. Historical recipes remain stable.
24. Report versions remain immutable.
25. Audit records remain immutable.
26. Notification failure does not roll back core operations.
27. Printer failure does not roll back core operations.
28. Background failures do not silently lose durable work.
29. Sync failures do not silently delete queued transactions.
30. Conflicts are explicit.
31. Conflict resolution is authorized.
32. Security failures fail closed.
33. Tenant data never crosses Business boundaries.
34. Stale offline events cannot resurrect deleted data.
35. Deletion is durable and idempotent.
36. Reactivation and deletion races are resolved safely.
37. POS remains operational during non-critical secondary failures.
38. Heavy work is moved to background processing where appropriate.
39. Error handling is deterministic.
40. Important operations remain auditable.

---

# 98. Relationship With Other System Analysis Documents

This document consolidates rules from the complete System Analysis set:

* `01_System_Context_and_Boundaries.md`
* `02_Application_Structure_and_Navigation.md`
* `03_Tenant_Business_and_Branch_Context.md`
* `04_Authentication_and_Authorization.md`
* `05_Employees_Roles_and_Permissions.md`
* `06_Device_Trust_and_Security_Context.md`
* `07_POS_and_Order_System.md`
* `08_Order_Lifecycle_and_Statuses.md`
* `09_Table_and_Waiter_Management.md`
* `10_Kitchen_and_Printing.md`
* `11_Payment_System.md`
* `12_Debt_and_Payment_Allocation.md`
* `13_Discounts_Refunds_and_Corrections.md`
* `14_Cash_Register_and_Cash_Session.md`
* `15_Shift_Handover.md`
* `16_Inventory_Transaction_System.md`
* `17_Products_Recipes_and_Sets.md`
* `18_Menu_Pricing_and_Configuration.md`
* `19_Attendance_and_Payroll.md`
* `20_Reports_and_Report_Versioning.md`
* `21_Notifications_and_Alerts.md`
* `22_Audit_and_History.md`
* `23_Offline_Operation.md`
* `24_Synchronization_and_Conflict_Resolution.md`
* `25_Subscription_and_Entitlement.md`
* `26_Data_Lifecycle_and_Deletion.md`
* `27_System_Wide_Consistency_and_Concurrency.md`
* `28_Background_Jobs_and_Recovery.md`
* `29_Error_Handling_and_Failure_Recovery.md`

---

# 99. System Analysis Completion

With this document, the planned System Analysis document set is complete.

The System Analysis stage establishes:

* system boundaries;
* application structure;
* tenant and Branch context;
* authentication and authorization;
* employee and permission behavior;
* device trust;
* POS and order behavior;
* order lifecycle;
* tables and waiters;
* kitchen and printing;
* payments;
* debt;
* discounts;
* refunds and corrections;
* Cash Sessions;
* shift handover;
* inventory;
* products, recipes and Sets;
* menu and pricing;
* attendance and payroll;
* reports;
* notifications;
* audit;
* offline operation;
* synchronization;
* subscription entitlement;
* data lifecycle;
* concurrency;
* background jobs;
* error handling;
* system-wide invariants.

The next analysis phase may proceed to architecture and technical design documents without reopening already-decided System Analysis questions unless a documented architectural decision exposes a genuine unresolved business or system conflict.

---

# 100. Final Principle

FastFood ERP must remain:

> **Operationally simple, transactionally correct, secure, auditable, recoverable, and capable of continuing essential Branch operations even when network connectivity is temporarily unavailable.**

Complexity belongs inside the system architecture, not in the user's daily workflow.

