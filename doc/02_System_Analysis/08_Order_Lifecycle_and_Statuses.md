# Order Lifecycle and Statuses

**Document ID:** SA-08
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system lifecycle of an Order and the rules governing Order status transitions.

It establishes:

* Order states;
* valid transitions;
* transition authorization;
* transition conditions;
* Draft behavior;
* acceptance;
* preparation;
* ready state;
* served state;
* cancellation;
* modification boundaries;
* payment independence;
* inventory effects;
* offline transitions;
* concurrency;
* historical integrity.

The objective is to ensure that an Order cannot move into an invalid state or bypass required business rules.

---

## 2. Order Lifecycle Model

The operational Order lifecycle is:

```text id="q5n1xt"
Draft
  │
  ▼
Accepted
  │
  ▼
Preparing
  │
  ▼
Ready
  │
  ▼
Served
```

Cancellation is a controlled terminal operational outcome and is handled separately from the normal preparation flow.

Conceptually:

```text id="u6h0mq"
Draft ──────→ Accepted → Preparing → Ready → Served
   │
   └────────→ Cancelled

Accepted ───→ Cancelled
Preparing ──→ Cancelled
Ready ──────→ Cancelled
```

The exact cancellation availability depends on the current business rules and order state.

---

## 3. Order States

The system uses the following primary operational states:

1. Draft;
2. Accepted;
3. Preparing;
4. Ready;
5. Served;
6. Cancelled.

There is no `Completed` operational state.

Payment status is maintained separately.

---

## 4. Draft State

Draft represents an order that is still being prepared and has not yet become an operational order.

A Draft may be edited freely within the user's permissions.

Draft does not:

* deduct inventory;
* reserve inventory;
* notify kitchen;
* make a table operationally Busy;
* create a completed payment.

---

## 5. Draft Characteristics

A Draft may contain:

* product lines;
* quantities;
* extras;
* removals;
* pricing information;
* order type;
* table context;
* waiter context;
* customer information where applicable.

The Draft remains temporary until accepted.

---

## 6. Draft to Accepted Transition

The transition is:

```text id="w1s0y5"
Draft
  ↓
Validation
  ↓
Inventory Validation
  ↓
Atomic Inventory Deduction
  ↓
Accepted
```

The system must validate the complete current state before committing the transition.

---

## 7. Acceptance Conditions

An order may transition from Draft to Accepted only when:

* employee is active;
* Business context is valid;
* Branch context is valid;
* required permission exists;
* products are active and sellable;
* required configuration is valid;
* required inventory is available;
* table context is valid where applicable;
* subscription permits the operation;
* no conflicting order state exists.

---

## 8. Acceptance Atomicity

Order acceptance and inventory deduction are one core atomic transaction.

If the inventory deduction fails:

```text id="d8r0v2"
Draft
  ↓
Inventory Failure
  ↓
Rollback
  ↓
Draft remains unaccepted
```

The system must not leave the order in Accepted state without the corresponding inventory deduction.

---

## 9. Accepted State

Accepted means that:

* the order is operationally valid;
* inventory deduction has succeeded;
* the order can enter kitchen processing;
* the order may remain unpaid;
* further permitted operations may be performed.

Accepted is the first operational state.

---

## 10. Accepted to Preparing

The normal transition is:

```text id="7h4w6q"
Accepted
   ↓
Preparing
```

The transition indicates that preparation has started.

It may be triggered by:

* kitchen workflow;
* authorized employee;
* configured operational event.

The exact UI mechanism is defined by the Kitchen system.

---

## 11. Preparing State

Preparing indicates that the kitchen is processing the order.

While Preparing:

* kitchen workflow continues;
* order remains operationally open;
* payment may still be possible according to payment rules;
* inventory already consumed by acceptance remains consumed.

---

## 12. Preparing to Ready

The transition is:

```text id="x5g8t2"
Preparing
    ↓
Ready
```

Ready means the order has been prepared and is available for serving or pickup.

The transition does not automatically:

* complete payment;
* mark the order Served;
* create a refund;
* modify inventory.

---

## 13. Ready State

Ready represents an order that is prepared.

The order may remain Ready until the appropriate serving event occurs.

The system must preserve:

* status transition;
* actor/source;
* timestamp;
* operational context.

---

## 14. Ready to Served

The transition is:

```text id="a7k3m1"
Ready
  ↓
Served
```

Served indicates that the operational serving process has been completed.

Once Served:

* normal order modification is no longer available;
* inventory remains consumed;
* historical order state is preserved.

---

## 15. No Completed State

The system does not use a separate `Completed` order state.

Financial completion is represented through the Payment lifecycle.

Therefore:

```text id="s7d4j1"
Operational Completion
→ Served

Financial Completion
→ Payment Completed
```

The two concepts remain separate.

---

## 16. Payment and Order Status

Payment does not automatically change the operational order state.

For example:

```text id="w4p9e2"
Order:
Preparing

Payment:
Completed
```

This is valid.

Likewise:

```text id="t8c4y1"
Order:
Served

Payment:
Pending
```

may remain possible according to debt/payment rules.

The system must not infer one lifecycle solely from the other.

---

## 17. Payment Availability

Payment may be created from an order state that is payable according to the payment rules.

The payment operation must verify:

* order identity;
* Business;
* Branch;
* payment status;
* remaining amount;
* employee permission;
* order financial state.

Payment creation does not modify the operational lifecycle unless a future explicit business rule introduces such behavior.

---

## 18. Draft Editing

While Draft:

* products may be added;
* products may be removed;
* quantities may change;
* extras may change;
* applicable prices may be recalculated.

No inventory return is required because Draft has not consumed inventory.

---

## 19. Accepted Order Modification

An unpaid Accepted order may be modified according to the permitted order-edit rules.

Examples:

* remove existing product;
* reduce quantity;
* add a new product;
* increase quantity;
* change permitted extras.

Every modification is subject to:

* permission;
* current order state;
* inventory rules;
* pricing rules;
* audit.

---

## 20. Product Removal

When an existing product is removed from an Accepted order:

1. order value is recalculated;
2. the system asks whether inventory should be returned;
3. inventory is returned only if confirmed;
4. the decision is recorded;
5. the modification is audited.

The operation must remain atomic where inventory is involved.

---

## 21. Quantity Reduction

Quantity reduction follows the same inventory-return logic.

Example:

```text id="2y5c7h"
Before:
Product A × 4

After:
Product A × 3

Removed:
1 unit
```

The system asks whether the removed quantity should be returned to inventory.

---

## 22. Increasing Quantity

Increasing quantity requires inventory validation.

If stock is insufficient:

```text id="x3v6c0"
Modification
    ↓
Stock Validation
    ↓
Insufficient
    ↓
Entire Modification Rejected
```

The system must not partially increase the order.

---

## 23. Adding a New Product After Acceptance

A completely new product added after the original Accepted order is treated as a new operational order/ticket.

It receives:

* new Order UUID;
* new operational lifecycle;
* separate kitchen ticket;
* separate inventory transaction.

It remains linked to the relevant original order/table context.

---

## 24. Modification and Inventory Return Failure

If a modification requires inventory return and the return fails:

```text id="p1v9z3"
Order Modification
      ↓
Inventory Return
      ↓
Failure
      ↓
Rollback
```

The order must remain in its previous valid state.

No partial modification may remain committed.

---

## 25. Cancellation

Cancellation is a controlled operation that prevents the order from continuing through the normal lifecycle.

Cancellation requires:

* authorized permission;
* mandatory reason;
* audit record.

The original Order UUID remains valid.

The order is not deleted.

---

## 26. Cancellation From Draft

A Draft may be discarded/cancelled without inventory reversal because Draft has not consumed inventory.

No financial refund is automatically created.

No inventory transaction is required.

---

## 27. Cancellation From Accepted

An Accepted order may be cancelled when the relevant permission and business rules allow it.

If inventory was previously deducted:

* the system may offer inventory return;
* the decision is recorded;
* inventory return is executed according to the inventory rules.

---

## 28. Cancellation From Preparing

Cancellation during Preparing is a controlled exception.

The system must:

* verify cancellation permission;
* require a reason;
* preserve the current state;
* apply the applicable inventory rule;
* record the cancellation;
* prevent further normal preparation transitions.

Cancellation does not automatically refund a payment.

---

## 29. Cancellation From Ready

An order in Ready state may be cancelled only through an authorized cancellation workflow.

The system must preserve:

* original order state;
* cancellation reason;
* actor;
* timestamp;
* inventory decision;
* financial state.

---

## 30. Cancellation From Served

A Served order is operationally complete.

Normal cancellation must not be used as a way to rewrite the served history.

If a financial or business correction is required after Served, the system uses the appropriate correction/refund process.

Served inventory is never automatically returned through normal cancellation.

---

## 31. Cancellation and Payment

Cancellation and payment are independent operations.

A cancelled order may have:

* no payment;
* a pending payment;
* a completed payment.

If money must be returned, a separate Refund operation is required.

The original payment remains historically preserved.

---

## 32. Refund and Order Lifecycle

Refund is a financial operation.

It does not rewrite the original Order lifecycle.

Example:

```text id="6y9k2v"
Order:
Served

Payment:
Completed

Refund:
Completed
```

The system retains all three historical facts.

---

## 33. Served Items and Inventory

Once an item has been served, the system must never automatically return its consumed inventory merely because of a later status or financial operation.

Any inventory correction after serving requires a separate authorized inventory process where applicable.

---

## 34. Order Status Transition Authorization

Each transition requires appropriate authorization.

Examples:

```text id="5h0m9x"
Draft → Accepted
→ Order acceptance permission

Accepted → Preparing
→ Kitchen/operational permission

Preparing → Ready
→ Kitchen/operational permission

Ready → Served
→ Serving/operational permission

Any Cancel
→ Cancellation permission
```

The exact permission identifiers are defined in the permission catalog.

---

## 35. Invalid Transition

An invalid transition must be rejected.

Examples:

```text id="c9k1q4"
Draft → Ready
Draft → Served
Ready → Preparing
Served → Preparing
Served → Accepted
```

The system must not silently normalize invalid transitions.

---

## 36. Status Transition Validation

Before changing status, the server validates:

1. Employee status;
2. Business context;
3. Branch context;
4. permission;
5. current Order state;
6. required transition rules;
7. relevant inventory/payment conditions;
8. concurrency/version state;
9. subscription entitlement where applicable.

---

## 37. Status Transition Atomicity

A core status change must either:

* fully succeed; or
* fully fail.

If the transition has a related core transaction, the related changes must commit atomically.

For example, an order acceptance that includes inventory deduction must not commit one without the other.

---

## 38. Status Transition History

Important status transitions must be historically traceable.

The system should preserve:

* Order UUID;
* previous state;
* new state;
* actor;
* Device UUID;
* Branch;
* timestamp;
* source;
* reason where applicable;
* related transaction/event UUID.

Historical status information must not be overwritten.

---

## 39. Status and Table Occupancy

Order status contributes to table occupancy.

A table is Busy when at least one open/unpaid operational order exists according to the table rules.

A Draft alone does not make the table Busy.

When all relevant open/unpaid orders are no longer active, the table may become Available.

---

## 40. Status and Waiter Context

The Primary Waiter remains associated with the order throughout normal lifecycle changes unless explicitly changed.

Status transitions do not automatically remove waiter attribution.

Waiter information remains available for:

* operational visibility;
* reporting;
* historical attribution;
* relevant overpayment reporting.

---

## 41. Status and Kitchen Context

Kitchen workflow depends on the operational order status.

Typical flow:

```text id="0v3g8d"
Accepted
   ↓
Kitchen Receives Order
   ↓
Preparing
   ↓
Ready
```

Kitchen printing is not itself the source of truth for order status.

The ERP order state remains authoritative.

---

## 42. Kitchen Failure

A printer or kitchen communication failure must not automatically revert the Order status or inventory transaction.

For example:

```text id="k8p2m5"
Order Accepted
      ↓
Kitchen Print Failed
      ↓
Order remains Accepted
      ↓
Print Event = Failed/Retrying
```

The printer system handles retry independently.

---

## 43. Offline Status Transitions

Offline status transitions are permitted only where:

* the trusted device is valid;
* offline authorization allows the operation;
* the employee has the required permission;
* the local state permits the transition.

After synchronization, the server validates the transition against authoritative state.

---

## 44. Offline Transition Conflict

If the server determines that an offline status transition is no longer valid:

* the original event remains preserved;
* the transition is marked as conflict/failure;
* the current server state remains authoritative;
* authorized resolution is performed when necessary;
* the resolution is audited.

The system must not silently overwrite the historical offline event.

---

## 45. Status Transition Idempotency

Status transition requests use UUID-based identity where appropriate.

If the same transition request is submitted again:

```text id="9w2k3n"
Same Request UUID
      ↓
Existing Result
      ↓
Return Existing Result
```

No duplicate transition or duplicate side effect is created.

---

## 46. Concurrent Status Changes

Concurrent status changes on the same Order must be controlled.

Example:

```text id="4j7x2p"
Cashier/device A:
Accepted → Preparing

Kitchen/device B:
Accepted → Cancelled
```

The server must resolve the race according to authoritative concurrency rules.

A stale client must not silently overwrite a newer state.

---

## 47. Status and Payment Concurrency

Payment and status changes may occur concurrently.

The system must maintain separate lifecycle state while validating financial conditions.

For example:

```text id="n5r8w2"
Order status update
      +
Payment creation
      ↓
Authoritative validation
      ↓
Valid independent outcomes
```

A payment must not be accepted against an invalid or unauthorized financial state.

---

## 48. Status and Subscription Expiration

If subscription entitlement expires while an order is active:

* existing order data remains preserved;
* new modifying operations are subject to read-only restrictions;
* operational state is not silently deleted;
* the system applies the current subscription lifecycle rules.

The system must not corrupt an open order merely because subscription state changed.

---

## 49. Status and Employee Deactivation

If the employee who created or previously modified an order becomes inactive:

* the order remains unchanged;
* historical actor attribution remains;
* another authorized employee may continue the order according to current permissions;
* the inactive employee cannot perform new protected operations.

Employee deactivation does not cancel an order automatically.

---

## 50. Status and Branch Context

An Order remains associated with its original Branch throughout its lifecycle.

Branch switching by the employee does not move the Order to another Branch.

An employee must continue the order only if the new Branch context and permission model explicitly allow access to that order.

---

## 51. Status and Historical Pricing

Status transitions do not recalculate historical pricing.

Changing:

* product price;
* Branch price override;
* recipe;
* Set composition;
* menu configuration

must not rewrite the financial snapshot of an existing order.

---

## 52. Status and Inventory

The normal inventory effect occurs at acceptance.

Later status transitions do not repeatedly deduct inventory.

Conceptually:

```text id="5p9c2x"
Draft
→ No Inventory Effect

Accepted
→ Inventory Deducted

Preparing
→ No New Deduction

Ready
→ No New Deduction

Served
→ No New Deduction
```

This prevents duplicate stock consumption.

---

## 53. Status and Corrections

Corrections do not rewrite the original status history.

A correction creates a separate auditable operation where required.

The original event remains preserved.

---

## 54. Status and Reporting

Reports use the authoritative status history and transaction snapshot.

Reports may include:

* current status;
* status transition history;
* cancellation count;
* preparation metrics;
* served orders;
* unpaid orders;
* payment state.

Report generation must not modify order lifecycle state.

---

## 55. System Invariants

The following invariants apply to Order lifecycle and statuses:

1. Every Order has one permanent Order UUID.
2. The operational lifecycle is Draft → Accepted → Preparing → Ready → Served.
3. Cancelled is a controlled terminal operational outcome.
4. There is no `Completed` operational Order state.
5. Payment lifecycle is separate from Order lifecycle.
6. Payment does not automatically change Order operational status.
7. Draft does not deduct inventory.
8. Draft does not reserve inventory.
9. Draft does not make a table Busy.
10. Draft acceptance requires current validation.
11. Order acceptance and inventory deduction are atomic.
12. Negative stock is prohibited.
13. Accepted is the first operational state.
14. Invalid status transitions are rejected.
15. Status transitions require appropriate authorization.
16. Important status changes remain historically traceable.
17. Accepted unpaid orders may be modified according to permission and business rules.
18. Product removal and quantity reduction require explicit inventory-return handling.
19. Insufficient stock rejects the entire increase/modification.
20. Failed inventory return rolls back the complete modification.
21. New products after acceptance are separate operational orders/tickets.
22. Related orders may share Table Visit/Session context without sharing Order UUID.
23. Served inventory is not automatically returned.
24. Cancellation does not delete the Order.
25. Cancellation and Refund are separate operations.
26. Refund does not rewrite the original Order lifecycle.
27. Paid orders cannot be ordinarily edited.
28. Kitchen printing failure does not roll back a committed Order.
29. ERP Order status is authoritative over printer state.
30. Offline status transitions require valid trusted-device authorization.
31. Server state is authoritative after synchronization.
32. Offline conflicts are explicit and auditable.
33. Status transition retries must be idempotent.
34. Concurrent status changes cannot silently overwrite authoritative state.
35. Employee deactivation does not automatically cancel existing Orders.
36. Branch switching does not move an Order between Branches.
37. Later configuration changes do not rewrite existing Order pricing.
38. Inventory is normally deducted only once at acceptance.
39. Corrections do not erase original status history.
40. Status history must preserve sufficient actor, device, Branch and timestamp context.

---

## 56. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/10_Kitchen_and_Printing.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 57. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `08_Order_Lifecycle_and_Statuses.md`

**Next Document:** `09_Table_and_Waiter_Management.md`

