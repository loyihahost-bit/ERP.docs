# Discounts, Refunds and Corrections

**Document ID:** SA-13
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for discounts, refunds, Order cancellation, financial corrections, and their relationships with Orders, Payments, Inventory, Cash Sessions, Reports, and Audit.

The objective is to ensure that financial changes are controlled, traceable, permission-based, and historically safe.

---

## 2. Scope

This document covers:

* discounts;
* discount authorization;
* order-level discount application;
* refund operations;
* full refunds;
* partial refunds;
* item-level refunds;
* quantity-level refunds;
* cash refunds;
* card refunds;
* cancellation;
* cancellation authorization;
* financial corrections;
* payment corrections;
* correction chains;
* inventory interaction;
* audit;
* report versioning;
* offline correction behavior.

---

## 3. Core Principles

The system follows these principles:

1. Original financial records are not silently overwritten.
2. Corrections are separate controlled operations.
3. Refunds are separate financial operations.
4. Cancellation is not the same as refund.
5. Discounts do not change the underlying product price.
6. Refunds do not automatically return inventory.
7. Served items never automatically return inventory.
8. Important financial operations require authorization.
9. All relevant operations are auditable.
10. Historical integrity has priority over convenience.

---

## 4. Discount Model

A discount changes the effective payable amount of an Order.

A discount does not modify:

* global product price;
* branch product price;
* historical product price;
* recipe cost;
* inventory valuation.

Conceptually:

```text id="d5n8q2"
Base Order Price
      ↓
Discount
      ↓
Final Payable Amount
```

---

## 5. Discount Scope

The current discount model applies at Order level.

A discount may affect the total payable amount of the Order without rewriting the underlying product price.

The system must preserve the original price snapshot of Order items.

---

## 6. Discount Permission

Discount application requires an explicit permission.

The system validates:

* Employee identity;
* Employee status;
* Business;
* Branch;
* Role Permission;
* Employee Override;
* Subscription Entitlement.

A user without discount permission cannot apply or modify a discount.

---

## 7. Discount Amount Validation

The system must validate the discount according to the configured business rules.

Invalid values must be rejected.

The system must prevent:

* negative discounts;
* invalid percentages;
* discounts exceeding the permitted amount;
* discounts that result in an invalid payable amount.

The exact configurable limits may be changed later without changing the underlying system model.

---

## 8. Discount and Product Price

Applying a discount must not change the base price of the product.

Example:

```text id="p7m3c9"
Product Price:       50,000
Discount:             5,000
Effective Price:     45,000

Product Price remains:
50,000
```

Historical product pricing remains preserved.

---

## 9. Discount Snapshot

The Order must retain sufficient discount information to reproduce the historical financial result.

The snapshot should include:

* discount type;
* discount value;
* calculated discount amount;
* actor;
* timestamp;
* relevant reason/comment;
* Order context.

Later configuration changes must not rewrite the historical discount.

---

## 10. Discount Modification

Before financial settlement, a discount may be changed or removed if the employee has the required permission.

The system must recalculate the Order payable amount.

The previous discount state must remain traceable where the change is considered a significant business operation.

---

## 11. Discount After Payment

A paid Order cannot receive an ordinary discount modification.

Any financial change after payment requires the appropriate controlled correction, refund, or other authorized financial operation.

The system must not silently alter the original paid amount.

---

## 12. Discount and Payment

Payment validation uses the effective payable amount after applicable discounts.

Example:

```text id="x8r4v2"
Order Base Total: 100,000
Discount:          10,000
Payable Amount:     90,000
```

Payment settlement is based on the effective payable amount.

---

## 13. Discount and Overpayment

If the final accepted payment exceeds the discounted payable amount, the excess follows the overpayment rules defined by the Payment System.

The system must not interpret the overpayment as an additional discount.

---

## 14. Discount and Inventory

A discount does not change inventory quantity.

Inventory deduction remains based on the accepted Order and its recipe/components.

Therefore:

```text id="m6q2k8"
Discount
   ↓
Financial Amount

Order Acceptance
   ↓
Inventory Quantity
```

These are separate system effects.

---

## 15. Refund Purpose

A refund reverses all or part of a previously completed financial payment.

A refund is a new financial operation.

It does not delete or overwrite the original payment.

---

## 16. Refund Eligibility

A refund requires:

* valid original financial transaction;
* valid Order;
* valid Business and Branch context;
* employee authorization;
* refund permission;
* valid refund amount;
* mandatory reason;
* valid refund method.

Invalid refund requests are rejected.

---

## 17. Refund Methods

The current supported refund methods are:

* Cash;
* Card.

The refund method must be explicitly recorded.

---

## 18. Full Refund

A full refund reverses the relevant refundable financial amount.

Example:

```text id="c9v5n3"
Original Payment: 100,000
Refund:           100,000
Remaining Net:          0
```

The original payment remains unchanged in history.

---

## 19. Partial Refund

Partial refunds are supported.

Example:

```text id="w2k7p4"
Original Payment: 100,000
Refund:            30,000
Net Payment:       70,000
```

The refund must not exceed the refundable amount.

---

## 20. Item-Level Refund

A refund may apply to a specific item where the applicable business rules allow it.

The system records:

* Order;
* item;
* quantity;
* refundable amount;
* refund amount;
* reason;
* actor;
* timestamp.

The original Order item record remains historically preserved.

---

## 21. Quantity-Level Refund

A partial quantity may be refunded.

Example:

```text id="h8m4q1"
Product:
Quantity Sold: 5

Refund:
Quantity: 2
```

The remaining quantity remains part of the original Order history.

The refund operation represents the financial adjustment.

---

## 22. Refund Amount Validation

The system must validate that the refund does not exceed the refundable amount.

For item/quantity refunds, the system must also validate the remaining refundable quantity or amount.

Repeated refunds must be evaluated against authoritative historical refund records.

---

## 23. Refund Reason

A refund requires a reason.

The reason is part of the financial history.

Examples may include:

* customer return;
* service issue;
* incorrect Order;
* approved business correction;
* other configured reason.

The reason list may be configurable later.

---

## 24. Refund Authorization

Refund permission is explicit.

Depending on the configured permission model, refund may require:

* Manager authorization;
* Owner authorization;
* another explicitly authorized employee.

The system must not infer refund authority from Cashier status alone.

---

## 25. Refund and Cash Session

A Cash refund affects physical cash when the refund method is Cash.

The refund must be associated with the applicable Cash Session.

The Cash Session must be valid for the refund operation.

A closed Cash Session cannot receive an ordinary new refund.

Controlled historical corrections use a separate correction process.

---

## 26. Card Refund

A Card refund is recorded separately from physical cash.

The ERP records the business refund operation.

External card processor reversal is outside the current scope unless a future integration is explicitly introduced.

---

## 27. Refund and Inventory

Refund does not automatically return inventory.

This separation is intentional.

Example:

```text id="q4n8s6"
Refund
   ↓
Financial Adjustment

Inventory
   ↓
No Automatic Return
```

If inventory must be returned, a separate authorized inventory operation is required.

---

## 28. Served Item Rule

A served item must never automatically return to inventory because of a refund or cancellation.

Any inventory adjustment involving served products requires a separate controlled inventory operation according to inventory rules.

---

## 29. Refund and Order Lifecycle

Refund does not automatically change the Order lifecycle.

For example:

```text id="v7c2m5"
Order → Served
Payment → Completed
Refund → Created
```

The Order remains historically Served.

The refund is a financial event.

---

## 30. Refund and Table Visit

A refund does not reopen a completed Table Visit/Session.

The table remains based on its operational state rather than historical financial reversals.

---

## 31. Refund and Waiter Attribution

Refund history retains the original Order and applicable waiter context.

The employee performing the refund is separately recorded.

This allows reports to distinguish:

* original waiter;
* original cashier;
* refund actor.

---

## 32. Refund and Overpayment

If the original payment contained an overpayment, refund calculations must distinguish:

* Order payable amount;
* original payment amount;
* overpayment amount;
* previous refunds;
* remaining refundable amount.

The system must not silently convert an overpayment into an ordinary Order refund.

---

## 33. Cancellation

Cancellation is an operational Order action.

It is different from refund.

Cancellation may apply to an Order before or during its operational lifecycle according to permissions and business rules.

The cancellation:

* records a mandatory reason;
* preserves the Order;
* records the actor;
* records timestamp;
* may require inventory return decision;
* changes operational state to Cancelled.

---

## 34. Cancellation Authorization

Cancellation requires the relevant permission.

The system validates:

* employee;
* Order state;
* Business;
* Branch;
* subscription entitlement;
* required reason;
* inventory state where applicable.

---

## 35. Cancellation and Inventory

If inventory was already deducted, the system may ask whether the inventory should be returned according to the Order rules.

The decision must be explicit and auditable.

If inventory return is selected:

* inventory return is part of the controlled cancellation operation where applicable;
* failure causes the relevant operation to roll back.

If inventory return is not selected:

* the Order remains cancelled;
* inventory remains as previously recorded.

Served items never automatically return inventory.

---

## 36. Cancellation and Payment

Cancellation and refund are separate.

If an Order has already been financially settled, cancelling the Order does not automatically modify the payment.

A separate refund or correction may be required.

This prevents one action from silently changing multiple financial records.

---

## 37. Paid Order Cancellation

A paid Order cannot be treated as an ordinary unpaid cancellation.

The system must determine whether:

* cancellation is permitted;
* refund is required;
* financial correction is required.

The original payment remains preserved.

---

## 38. Cancellation and Kitchen

If the Order has already entered kitchen processing:

* cancellation must generate the appropriate kitchen update;
* previously printed tickets remain historical;
* physical print output cannot be erased;
* kitchen status history remains preserved.

Printer failure must not prevent the cancellation from being recorded.

---

## 39. Financial Correction

A correction is used when an existing financial or operational result must be adjusted through a controlled process.

A correction is not an overwrite.

The system creates a new operation linked to the original record.

---

## 40. Correction Chain

Corrections must form a traceable chain.

Example:

```text id="r5m9c2"
Original Transaction
       ↓
Correction #1
       ↓
Correction #2
```

Each correction references its parent/original event.

The original transaction remains immutable.

---

## 41. Correction Context

A correction must preserve:

* Correction UUID;
* original transaction UUID;
* affected entity;
* Business;
* Branch;
* actor;
* timestamp;
* old effective state;
* new effective state;
* reason;
* authorization;
* source;
* result.

---

## 42. Correction Authorization

Corrections require explicit permission.

The system must not allow an employee to correct a transaction merely because they created the original transaction.

Correction authority is determined by the current permission model.

---

## 43. Payment Correction

Payment correction follows the same immutable-history principle.

Example:

```text id="n6w3p8"
Original Payment
      ↓
Payment Correction
      ↓
Effective Financial Result
```

The original payment remains visible in history.

The correction is separately auditable.

---

## 44. Refund vs Correction

The system distinguishes:

### Refund

A financial reversal of a completed payment.

### Correction

A controlled adjustment of an existing financial result or transaction record.

A refund should be used when money is returned to the customer.

A correction should be used when the recorded transaction requires controlled adjustment without treating the operation as an ordinary refund.

---

## 45. Correction of Overpayment

An overpayment may require correction when the original accepted amount was incorrect.

The system must preserve:

* original accepted amount;
* original overpayment amount;
* correction;
* actor;
* reason;
* timestamp.

The Business/Branch ownership of the original overpayment remains historically visible.

---

## 46. Correction and Report Versioning

If a correction changes a report metric:

* a new report version is created;
* previous versions remain immutable;
* the correction is linked to the new version.

If the correction does not change relevant report metrics:

* no unnecessary report version is created.

---

## 47. Correction and Audit

Every important correction must create audit information.

The audit should identify:

* original transaction;
* correction;
* actor;
* reason;
* old state;
* new state;
* timestamp;
* Business;
* Branch;
* Device where applicable;
* source.

---

## 48. Offline Refund

Offline refund is permitted only where the offline authorization explicitly allows the operation.

Because refunds are high-impact financial operations, the offline permission must be independently validated.

If the trusted device lacks valid offline refund authority, the operation is blocked.

---

## 49. Offline Correction

Offline correction is subject to the same restriction.

A correction cannot bypass:

* employee permission;
* Branch scope;
* subscription entitlement;
* authorization rules;
* correction limits;
* historical integrity.

The offline operation is synchronized and server-validated later.

---

## 50. Offline Conflict

A conflict may occur when an offline financial operation references a state that has already changed on the server.

Example:

```text id="c8q4m7"
Offline:
Refund 50,000

Server:
Original payment already corrected
```

The system must create an explicit conflict.

It must not silently apply the refund or silently overwrite the correction.

---

## 51. Conflict Resolution

Financial conflicts must preserve:

* original offline operation;
* server state;
* conflict reason;
* resolution decision;
* resolving actor;
* resolution time;
* resulting financial state.

Resolution is a separate auditable operation.

---

## 52. Discount, Refund and Correction Dependencies

The system must preserve the dependency chain:

```text id="m7p2v9"
Product Price
      ↓
Order Price Snapshot
      ↓
Discount
      ↓
Effective Payable Amount
      ↓
Payment
      ↓
Refund / Correction
```

Each stage must remain historically traceable.

---

## 53. Idempotency

Discount, refund and correction operations that may be retried must have unique UUID-based identities.

Repeated requests must not create duplicate:

* discounts;
* refunds;
* corrections;
* financial effects.

---

## 54. Concurrency

The system must protect against concurrent:

* refunds;
* corrections;
* payment edits;
* cancellations;
* discount changes.

Final validation must use authoritative server state.

Stale client state must not overwrite a newer financial state.

---

## 55. Error Handling

Errors are classified as:

* Validation Error;
* Authorization Error;
* Conflict;
* Business Rule Violation;
* Temporary Infrastructure Error;
* Permanent Failure.

The user receives a business-safe message.

Technical details remain in structured logs.

Retryable operations must be protected by idempotency.

---

## 56. Core Transaction Boundaries

The following operations must be atomic when they represent one business transaction:

* applying a valid pre-payment discount;
* creating a refund;
* creating a financial correction;
* cancelling an Order with required inventory return;
* updating related financial state.

If a required core operation fails, its related changes roll back.

---

## 57. Secondary Operations

Secondary operations may include:

* notifications;
* report version generation;
* background processing;
* synchronization bookkeeping;
* non-critical audit delivery through reliable mechanisms.

Secondary failure must not silently corrupt or roll back a successfully committed core operation.

---

## 58. Reporting

Reports must be able to distinguish:

* gross Order amount;
* discounts;
* net payable amount;
* payments;
* overpayments;
* refunds;
* cancellations;
* corrections;
* effective financial result;
* actors;
* reasons;
* timestamps.

Historical report versions remain immutable.

---

## 59. Performance

Discounts and normal refund/correction workflows must remain responsive.

The system should avoid blocking POS with:

* report regeneration;
* notification delivery;
* heavy audit queries;
* background synchronization;
* external processor communication.

Heavy processing should run asynchronously where appropriate.

---

## 60. System Invariants

The following invariants apply to Discounts, Refunds and Corrections:

1. Discounts do not change product base prices.
2. Discounts affect the effective payable amount.
3. Discounts are Order-level in the current model.
4. Discount application requires permission.
5. Discount values must pass server-side validation.
6. Historical discount information is preserved.
7. Paid Orders cannot receive ordinary discount modifications.
8. Refund is a separate financial operation.
9. Refund does not overwrite the original payment.
10. Full refunds are supported.
11. Partial refunds are supported.
12. Item-level refunds are supported where applicable.
13. Quantity-level refunds are supported.
14. Refund amount cannot exceed the refundable amount.
15. Refund requires a mandatory reason.
16. Refund requires appropriate authorization.
17. Cash refunds affect the relevant Cash Session.
18. Card refunds remain separate from physical cash.
19. Refund does not automatically return inventory.
20. Served items never automatically return inventory.
21. Refund does not reopen a completed Table Visit/Session.
22. Refund does not automatically change the Order lifecycle.
23. Cancellation and refund are separate operations.
24. Cancellation requires a mandatory reason.
25. Cancellation preserves the original Order.
26. Cancellation may include a controlled inventory return decision.
27. Inventory return failure rolls back the relevant cancellation transaction.
28. Paid Order cancellation does not silently change the original payment.
29. Financial corrections are separate operations.
30. Original financial records remain immutable.
31. Corrections reference original transactions.
32. Correction chains remain traceable.
33. Correction authority is permission-controlled.
34. Overpayment corrections preserve the original overpayment history.
35. Refunds and corrections are separately distinguishable.
36. Offline refund requires valid offline authorization.
37. Offline correction requires valid offline authorization.
38. Offline financial conflicts are explicit.
39. Conflict resolution is a separate auditable event.
40. Duplicate retries cannot create duplicate refunds or corrections.
41. Concurrent financial operations use authoritative server state.
42. Important discounts, refunds, cancellations and corrections are auditable.
43. Report versions are created only when relevant metrics change.
44. Previous report versions remain immutable.
45. Secondary failures do not silently corrupt committed financial operations.
46. Core financial operations are atomic.
47. Business and Branch isolation applies to all operations.
48. Subscription entitlement applies to modifying operations.
49. Historical financial relationships remain traceable.
50. Technical diagnostics remain outside user-facing business errors.

---

## 61. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/12_Debt_and_Payment_Allocation.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/15_Shift_Handover.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 62. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `13_Discounts_Refunds_and_Corrections.md`

**Next Document:** `14_Cash_Register_and_Cash_Session.md`

