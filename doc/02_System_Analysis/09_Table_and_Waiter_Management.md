# Table and Waiter Management

**Document ID:** SA-09
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for table management, table occupancy, Table Visit/Session grouping, waiter assignment, and the relationship between tables and Orders.

The objective is to ensure that table state and waiter attribution remain consistent while allowing multiple orders and operational actions to occur during the same customer visit.

---

## 2. Table Management Scope

Table management applies to Hall/Dine-in operations.

The system must support:

* tables;
* table availability;
* occupied tables;
* Table Visit/Session grouping;
* multiple Orders for one table visit;
* primary waiter assignment;
* temporary second waiter assistance;
* order visibility by table;
* payment and order history;
* offline table operations;
* concurrent table operations.

Takeaway orders do not require a physical table.

---

## 3. Table Identity

Each table has a permanent Table UUID within its Branch.

The table identity must remain stable even when:

* the table becomes free;
* a new customer arrives;
* a new Table Visit/Session starts;
* previous Orders remain in history.

Table identity is not reused as an Order identity.

---

## 4. Branch Ownership

A Table belongs to exactly one Branch.

The system must validate Branch context before performing table operations.

A table cannot be moved to another Branch through normal operational actions.

Cross-branch table transfer is outside the current scope.

---

## 5. Table States

The operational table state is derived from its active Orders and Table Visit/Session.

Conceptually:

```text id="a2k6p8"
Available
   │
   ▼
Busy
   │
   ▼
Available
```

The system does not need to treat historical paid Orders as active occupancy.

---

## 6. Available State

A table is Available when it has no active open/unpaid operational Order associated with the current Table Visit/Session.

Historical Orders may still be linked to the table without making it Busy.

---

## 7. Busy State

A table is Busy when at least one relevant open/unpaid Order exists.

For example:

```text id="f7n3c2"
Table 12
├── Order A — Paid
├── Order B — Unpaid
└── Order C — Unpaid

Table State:
Busy
```

The existence of Order B or C keeps the table Busy.

---

## 8. Draft and Table Occupancy

A Draft Order does not make a table Busy.

Example:

```text id="v5r8m1"
Table 12
Draft Order
     ↓
Table remains Available
```

The Draft may contain table context, but it does not create operational occupancy.

This prevents abandoned or temporary Drafts from blocking a table.

---

## 9. Table Visit/Session

A Table Visit/Session represents one continuous operational customer visit at a table.

It groups related Orders created during the same visit.

A Table Visit/Session may contain:

* one Order;
* multiple Orders;
* paid Orders;
* unpaid Orders;
* additional operational Orders;
* waiter context.

---

## 10. Table Visit/Session Identity

Each Table Visit/Session has its own UUID.

It is different from:

* Table UUID;
* Order UUID;
* Cash Session UUID;
* Payment UUID.

The identifiers must not be reused interchangeably.

---

## 11. Creating a Table Visit/Session

A new Table Visit/Session is created when a customer visit begins and an operational Order requires table grouping.

A Draft alone does not necessarily create a finalized operational visit.

The system must avoid creating unnecessary permanent operational occupancy from abandoned Drafts.

---

## 12. Multiple Orders in One Visit

A single Table Visit/Session may contain multiple Orders.

Example:

```text id="q4h8s2"
Table 5
└── Visit #100
    ├── Order #A
    ├── Order #B
    └── Order #C
```

Each Order retains its own:

* Order UUID;
* lifecycle;
* payment state;
* status history;
* financial history.

The Table Visit/Session provides grouping, not identity replacement.

---

## 13. Additional Order After Acceptance

If a customer requests an additional product after the original Order has been Accepted, the system creates a new operational Order.

The new Order:

* receives a new Order UUID;
* receives a separate operational lifecycle;
* may receive a separate kitchen ticket;
* receives its own inventory transaction;
* remains linked to the same Table Visit/Session.

This prevents historical modification of the original accepted Order.

---

## 14. Order Visibility by Table

Authorized users working with a table may see all Orders associated with the active Table Visit/Session according to their permissions.

This includes:

* unpaid Orders;
* paid Orders;
* preparing Orders;
* ready Orders;
* served Orders;
* cancelled historical Orders where visibility is permitted.

Payment and operational status remain independent.

---

## 15. Table-Level Bill View

The system may present all relevant Orders of a Table Visit/Session as one customer bill view.

This does not merge their identities.

Conceptually:

```text id="m7c1x9"
Table Visit
├── Order A
├── Order B
└── Order C
       ↓
Combined Bill View
```

Each Order remains individually traceable.

---

## 16. Split Payment

If the customer wants to pay separately, the system uses payment portions against the same Order or relevant grouped Orders according to the payment workflow.

The system must not create artificial Orders merely to represent separate payments.

Split bill is a payment operation, not an Order lifecycle operation.

---

## 17. Payment and Table Occupancy

Payment does not automatically determine table occupancy.

The table remains Busy while at least one relevant open/unpaid Order remains.

A paid Order may remain visible in the Table Visit/Session history.

---

## 18. Freeing a Table

When the last active open/unpaid Order is no longer operationally active according to the table rules, the table becomes Available.

The previous Table Visit/Session is then considered closed for operational grouping.

Its history remains preserved.

---

## 19. New Visit After Table Is Freed

When the same table is used by another customer after the previous visit has ended, the system creates a new Table Visit/Session.

Example:

```text id="n3p6v8"
Table 5

Visit A
  └── Orders
      ↓
Table becomes Available
      ↓
Visit B
  └── New Orders
```

The new visit must not inherit the previous visit's active operational state.

Historical Orders remain linked to Visit A.

---

## 20. Table History

The system must preserve historical table usage.

History may include:

* Table UUID;
* Table Visit/Session UUID;
* Orders;
* primary waiter;
* assisting waiter;
* timestamps;
* status;
* payment references.

Historical table information must not be rewritten when a new visit starts.

---

## 21. Primary Waiter

A Table Visit/Session may have a Primary Waiter.

The Primary Waiter is the main waiter responsible for the customer visit.

The primary waiter remains associated with the visit unless explicitly changed through an authorized operation.

---

## 22. Waiter Assignment

Waiter assignment is subject to:

* employee status;
* Branch assignment;
* waiter-related permission;
* current Table Visit/Session;
* business rules.

A waiter from another Branch cannot be assigned to a Branch table unless the employee is explicitly assigned and authorized for that Branch.

---

## 23. Temporary Second Waiter

A second waiter may temporarily assist the Primary Waiter.

The Primary Waiter can assign the second waiter as temporary assistance once according to the business rule.

Example:

```text id="c8w4j2"
Primary Waiter
      │
      └── Temporary Help → Second Waiter
```

The second waiter does not automatically replace the Primary Waiter.

---

## 24. Temporary Waiter Scope

The temporary waiter relationship must be limited to the relevant operational context.

It must not automatically:

* transfer ownership of the visit;
* change the Primary Waiter;
* rewrite historical attribution;
* grant additional permissions;
* change Branch scope.

The assisting waiter operates only within their existing permissions.

---

## 25. Waiter and Order Attribution

An Order may retain waiter attribution from its Table Visit/Session.

For relevant reports, the system must be able to determine:

* Primary Waiter;
* assisting Waiter where applicable;
* Order;
* Branch;
* Table;
* Visit/Session.

This is especially important for business attribution such as overpayment reporting.

---

## 26. Waiter Changes

If an authorized user changes the Primary Waiter:

* the change is recorded;
* previous attribution remains in history;
* new attribution becomes effective from the change point;
* existing historical events are not rewritten.

The system must preserve the actor, time and reason where required.

---

## 27. Table and Cashier Relationship

A table does not belong to a Cashier.

The cashier relationship exists at the Order/payment/Cash Session level.

Therefore:

```text id="e5q7n1"
Table
  ↓
Table Visit
  ↓
Order
  ↓
Cash Session
```

A cashier change does not require moving the table itself.

---

## 28. Shift Handover

During cashier handover:

* existing open Orders remain associated with their original Order UUIDs;
* the Table Visit/Session remains unchanged;
* the new Cashier may continue authorized operations;
* later actions use the new Cash Session context.

The table does not reset because of cashier handover.

---

## 29. Table and Payment During Handover

If payment occurs around the Cash Session transition:

* payment before transition belongs to the previous Cash Session;
* payment after transition belongs to the new Cash Session;
* a payment operation in transition state must be handled according to the handover concurrency rules.

The Table Visit/Session itself remains unchanged.

---

## 30. Offline Table Operation

Trusted devices may perform permitted table operations while offline.

Offline operation must use:

* valid trusted-device authorization;
* valid offline employee authorization;
* valid Branch scope;
* valid offline entitlement;
* local operational state.

Offline table changes are later synchronized with the server.

---

## 31. Offline Table Conflict

A typical conflict may occur when:

```text id="k2m8r5"
Device A:
Table 5 → New Accepted Order

Device B:
Offline Draft → Table 5
```

When Device B reconnects, the server validates the Draft against the current authoritative table/order state.

Because Draft does not occupy a table, the Draft may remain a Draft until acceptance is attempted.

---

## 32. Offline Draft and Table State

An offline Draft can be synchronized because it does not create operational occupancy.

When the Draft is later accepted:

1. server checks current table state;
2. server checks relevant Orders;
3. server validates permissions;
4. server validates inventory;
5. server validates the current Table Visit/Session;
6. server either accepts or rejects the operation.

---

## 33. Invalid Offline Table Context

If synchronization determines that the table context is no longer valid for the Draft:

* the Draft does not become an invalid Accepted Order;
* the server Accepted state remains authoritative;
* the synchronization result is recorded;
* the local Draft may be discarded according to the synchronization rule;
* the original offline event remains historically traceable where required.

---

## 34. Table Concurrency

Table occupancy must be protected against concurrent operational changes.

Example:

```text id="r6y2p9"
Device A:
Accept Order for Table 8

Device B:
Accept another Order for Table 8
```

The server must serialize or otherwise safely validate the operations so that Table Visit/Session grouping remains consistent.

---

## 35. Table Visit Creation Concurrency

Only one active Table Visit/Session should represent the same operational customer visit.

Concurrent requests attempting to create a new active visit must use transaction/concurrency controls.

The first valid operation establishes the active visit.

Other requests must reuse the valid active visit or be rejected according to the current state.

---

## 36. Table Freeing Concurrency

A table must not become Available while another valid open/unpaid Order still exists.

The system must evaluate the authoritative current state before changing occupancy.

Stale client information must not cause premature table release.

---

## 37. Table Visit Closure

Closing a Table Visit/Session is a logical operational action.

It must not:

* delete Orders;
* delete payments;
* delete waiter history;
* delete table history.

It only marks the end of the active grouping.

---

## 38. Table Configuration

Table configuration belongs to the Branch.

Configuration may include:

* table identifier;
* display name/number;
* hall/zone;
* active/inactive state;
* ordering/display properties.

Configuration changes must not rewrite historical Table Visit/Session information.

---

## 39. Inactive Tables

An inactive table cannot receive new operational Orders.

Existing historical Orders remain accessible according to permissions.

Deactivating a table must not silently delete or cancel active Orders.

The system should prevent deactivation when active operations make the action unsafe, or require an authorized controlled process.

---

## 40. Table Context and Order Types

Only Hall/Dine-in Orders require table context.

Takeaway Orders do not require a physical table.

Phone Delivery is planned for a future scope and must not be treated as a current table workflow.

---

## 41. Table Context Validation

Before accepting a table-based Order, the system validates:

* Table UUID;
* Business UUID;
* Branch UUID;
* Table active state;
* current Table Visit/Session;
* employee permissions;
* Order state;
* concurrency/version state.

Invalid or stale table context must be rejected.

---

## 42. Table Context and Historical Orders

Historical Orders retain their original:

* Table UUID;
* Table Visit/Session UUID;
* Branch UUID;
* waiter context;
* timestamps.

Later table configuration changes do not alter historical relationships.

---

## 43. Table and Inventory

Table state does not itself affect inventory.

Inventory deduction occurs when the relevant Order is Accepted.

Therefore:

```text id="b7n1s4"
Table Available/Busy
       ≠
Inventory Transaction
```

Inventory remains controlled by Order acceptance and inventory transaction rules.

---

## 44. Table and Kitchen

A table does not directly create a kitchen operation.

The Order creates the relevant operational kitchen event after acceptance.

Kitchen status and printing remain controlled by the Order and Kitchen systems.

---

## 45. Table and Cancellation

Cancelling an Order does not automatically delete the Table Visit/Session.

The system recalculates table occupancy based on remaining active Orders.

If no active open/unpaid Order remains, the table may become Available.

---

## 46. Table and Refund

Refund is a financial operation.

It does not directly control table occupancy.

A refund against a historical Order must not reopen a completed Table Visit/Session.

---

## 47. Table and Overpayment

If an Order contains an overpayment:

* the overpayment belongs to the Business/Branch;
* the accepted amount is attributed to the Cashier;
* if applicable, the Primary Waiter may also be recorded;
* the Table Visit/Session remains historical context;
* the overpayment does not change the Table lifecycle.

---

## 48. Historical Integrity

The system must preserve the original relationship between:

```text id="p4x8c6"
Business
  ↓
Branch
  ↓
Table
  ↓
Table Visit/Session
  ↓
Order
  ↓
Payment
```

Later operational changes must not overwrite historical relationships.

---

## 49. Authorization

Table and waiter operations require authorization based on:

* Employee identity;
* Role Permission;
* Employee Override;
* Branch Scope;
* Subscription Entitlement;
* Employee Status;
* Device/Offline Authorization.

Trusted Device status alone does not grant table or waiter permissions.

---

## 50. Idempotency

Operations that may be retried because of network problems must use UUID-based idempotency.

Repeated requests must not create:

* duplicate Table Visits;
* duplicate waiter assignments;
* duplicate Orders;
* duplicate occupancy transitions.

---

## 51. Error Handling

The system should distinguish:

* Validation Error;
* Authorization Error;
* Conflict;
* Business Rule Violation;
* Temporary Infrastructure Error;
* Permanent Failure.

User-facing messages should describe the business-safe reason.

Technical details remain in logs and diagnostic systems.

---

## 52. Background Processing

Table state must not depend on slow background processing.

Core table operations are synchronous when required for immediate POS behavior.

Background services may process:

* notifications;
* audit delivery where applicable;
* synchronization;
* reporting;
* non-critical secondary events.

A background failure must not leave the table state silently inconsistent.

---

## 53. Performance

Table operations are part of the POS workflow and must remain fast.

The system should avoid unnecessary:

* remote calls;
* heavy calculations;
* blocking background work;
* repeated configuration loading.

Critical table state must be validated against authoritative server state when required.

---

## 54. System Invariants

The following invariants apply to Table and Waiter Management:

1. Every table has a permanent Table UUID.
2. Every table belongs to exactly one Branch.
3. A table cannot be moved across Branches through normal operations.
4. Draft Orders do not make a table Busy.
5. At least one active open/unpaid Order makes the table Busy.
6. Paid historical Orders do not keep a table Busy.
7. One operational customer visit is represented by one active Table Visit/Session.
8. A Table Visit/Session has its own UUID.
9. Table UUID, Visit UUID and Order UUID are different identities.
10. Multiple Orders may belong to one Table Visit/Session.
11. Each Order retains its own lifecycle and payment state.
12. Additional products after acceptance are represented by separate operational Orders.
13. Separate Orders may share the same Table Visit/Session.
14. The original Order UUID is never replaced by a later Order.
15. A new customer visit creates a new Table Visit/Session after the previous visit ends.
16. Historical visits remain preserved.
17. The Primary Waiter remains the main waiter unless explicitly changed.
18. A temporary second waiter does not automatically replace the Primary Waiter.
19. Waiter assistance does not grant additional permissions.
20. Waiter attribution remains historically traceable.
21. Cashier identity is not the same as table ownership.
22. Cashier handover does not reset the table or Table Visit/Session.
23. Payment does not automatically free a table.
24. A table becomes Available only when no relevant active open/unpaid Order remains.
25. Cancellation recalculates occupancy from the authoritative current state.
26. Refund does not reopen a completed Table Visit/Session.
27. Table configuration changes do not rewrite historical visits.
28. Inactive tables cannot receive new operational Orders.
29. Deactivating a table does not delete historical data.
30. Only Hall/Dine-in Orders require table context.
31. Takeaway Orders do not require a table.
32. Inventory is controlled by Order acceptance, not table state.
33. Kitchen operations are driven by Orders, not directly by tables.
34. Offline table operations require valid trusted-device authorization.
35. Server state is authoritative after synchronization.
36. Offline table conflicts are explicit.
37. Concurrent requests cannot create inconsistent active Table Visits.
38. A table cannot become Available while a valid active open/unpaid Order remains.
39. Retried requests must not create duplicate visits or assignments.
40. Historical table, waiter and Order relationships are immutable.
41. Table operations are subject to Business and Branch isolation.
42. Permission changes must take effect according to current authorization rules.
43. Table state must remain consistent with the authoritative Order state.
44. Business correctness and historical integrity take priority over stale client convenience.

---

## 55. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/10_Kitchen_and_Printing.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/15_Shift_Handover.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 56. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `09_Table_and_Waiter_Management.md`

**Next Document:** `10_Kitchen_and_Printing.md`

