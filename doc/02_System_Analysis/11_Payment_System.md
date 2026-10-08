# Payment System

**Document ID:** SA-11
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for payments, payment methods, partial payments, mixed payments, split bills, overpayments, debt payments, offline payments, payment corrections, and payment history.

The objective is to ensure that every payment is financially traceable, idempotent, permission-controlled, and consistent with the related Order, Business, Branch, Cash Session, Employee, and Device context.

---

## 2. Payment System Scope

The Payment system is responsible for:

* creating payments;
* validating payment eligibility;
* supporting payment methods;
* tracking payment state;
* calculating remaining amounts;
* supporting partial payments;
* supporting mixed payments;
* supporting split bill;
* recording overpayments;
* recording debt;
* supporting debt repayment;
* supporting controlled payment corrections;
* preserving payment history;
* supporting authorized offline payments;
* synchronizing offline payments.

The Payment system does not directly control:

* Order preparation status;
* kitchen printing;
* table occupancy;
* inventory deduction except through defined transaction boundaries;
* subscription lifecycle.

---

## 3. Payment Identity

Every payment operation has a unique Payment UUID.

The Payment UUID is the primary idempotency identity for payment creation and synchronization.

The system must not use a Client Transaction ID as the primary payment identity.

Payment identity remains stable across retries and synchronization.

---

## 4. Payment Context

Every payment must retain sufficient context to determine where and by whom it was created.

Relevant context includes:

* Payment UUID;
* Business UUID;
* Branch UUID;
* Order UUID;
* Employee UUID;
* Device UUID;
* Cash Register UUID where applicable;
* Cash Session UUID where applicable;
* payment method;
* amount;
* currency;
* timestamp;
* status;
* source;
* related transaction context.

---

## 5. Payment Lifecycle

The normal payment lifecycle is:

```text id="p8k4m2"
Pending
   ↓
Completed
```

`Refund` and `Correction` are not ordinary payment states.

They are separate financial operations against the original payment.

---

## 6. Pending Payment

A payment is `Pending` when the payment operation has been created but has not yet reached its final successful state.

Pending may occur because:

* the operation is being processed;
* an external payment confirmation is required;
* synchronization is incomplete;
* a temporary system condition exists.

A Pending payment must not be treated as a completed payment for remaining-balance purposes.

---

## 7. Completed Payment

A payment becomes `Completed` only after all required validation and processing succeeds.

A Completed payment contributes to the Order's paid amount according to its effective amount.

The original Completed payment record remains historically preserved.

---

## 8. Payment Eligibility

Before creating a payment, the system validates:

1. Employee identity.
2. Employee active status.
3. Business context.
4. Branch context.
5. Order existence.
6. Order belongs to the same Business.
7. Order belongs to the same Branch.
8. Order is in a payment-eligible state.
9. Employee has required payment permission.
10. Payment amount is valid.
11. Payment does not violate applicable remaining-amount rules.
12. Cash Session is valid when required.
13. Device authorization is valid where applicable.
14. Subscription entitlement allows the operation.

Failure of any required validation rejects the payment.

---

## 9. Paymentable Order State

Payment is allowed from the operational states defined by the Order system beginning with `Accepted`, subject to the Order's current financial state.

Payment does not require the Order to be:

* Preparing;
* Ready;
* Served.

Therefore, operational preparation and financial settlement remain independent.

---

## 10. Payment Does Not Change Order Lifecycle

Creating a payment must not automatically:

* mark the Order Ready;
* mark the Order Served;
* close the Table Visit/Session;
* create a kitchen event;
* change inventory.

Payment and Order lifecycle are separate concerns.

---

## 11. Payment Amount

The system stores the payment amount explicitly.

The amount must be:

* valid;
* non-negative;
* represented using the system's supported monetary precision;
* associated with the payment method.

A payment amount cannot be silently changed after completion.

---

## 12. Remaining Amount

The system calculates:

```text id="m5q7r3"
Remaining Amount
=
Order Payable Amount
−
Effective Completed Payments
```

The system must show:

* Order total;
* paid amount;
* remaining amount;
* payment status.

The remaining amount must be calculated from authoritative payment records.

---

## 13. Partial Payment

Partial payment is allowed.

Example:

```text id="c7v2n9"
Order Total:      100,000
Paid:              40,000
Remaining:         60,000
```

The Order remains financially unpaid until the required payable amount has been settled.

Multiple payment operations may be associated with the same Order.

---

## 14. Full Payment

A full payment settles the payable Order amount.

The system records the payment and updates the financial state.

This does not automatically change the operational Order status.

---

## 15. Multiple Payments

An Order may have multiple Completed payments.

Each payment remains separately identifiable.

Example:

```text id="w4k8p1"
Order #125
├── Cash Payment 40,000
├── Card Payment 30,000
└── Cash Payment 30,000
```

The system must preserve each payment's original context.

---

## 16. Mixed Payment

Mixed payment allows one logical customer payment to contain multiple payment portions.

Example:

```text id="h6n2s8"
Order Total: 100,000

Mixed Payment
├── Cash: 60,000
└── Card: 40,000
```

The system treats this as one logical payment operation with internal payment portions.

Each portion retains its method and amount.

---

## 17. Mixed Payment Validation

The system validates:

* every portion has a valid method;
* every portion has a valid amount;
* total portions form the intended payment amount;
* Cash portion is included in physical cash calculations;
* Card portion is not treated as physical cash;
* permissions are valid for the overall operation.

The mixed payment must not create duplicate financial effects.

---

## 18. Split Bill

Split bill is a payment operation.

The original Order remains one Order.

The system must not create multiple Orders merely because the customer wants to pay separately.

Example:

```text id="x9c4m6"
One Order
   ↓
Payment Portion A
Payment Portion B
Payment Portion C
```

Order identity remains unchanged.

---

## 19. Split Bill and Item Allocation

Where the user interface allows item-based bill splitting, the system may calculate suggested payment portions from selected items.

However, this must not duplicate or mutate the underlying Order items.

The final financial result remains associated with the original Order.

---

## 20. Payment Method

The supported payment methods are:

* Cash;
* Card;
* Debt;
* Mixed.

Other methods are outside the current System Analysis scope unless added later through a controlled requirement change.

---

## 21. Cash Payment

Cash payment contributes to the physical cash balance of the relevant Cash Session.

The payment must be associated with:

* Branch;
* Cash Register;
* Cash Session;
* Cashier;
* Device where applicable.

Cash payment therefore affects cash-session reporting.

---

## 22. Card Payment

Card payment is recorded separately from physical cash.

The ERP records the business payment result.

External card processor authorization, if introduced, remains an external responsibility unless separately integrated.

The ERP must not assume that every Card payment automatically has external processor verification.

---

## 23. Debt Payment

Debt payment allows an Order to become associated with a customer's outstanding balance.

Debt management is defined further in:

`12_Debt_and_Payment_Allocation.md`

A Debt payment must preserve:

* Customer identity;
* Order relationship;
* amount;
* outstanding balance;
* allocation information where applicable.

---

## 24. Debt Customer Identity

The current system uses one customer record per debt customer.

A customer may have:

* multiple debt Orders;
* multiple repayments;
* an outstanding balance.

Duplicate phone numbers are allowed.

Historical Orders retain the customer information relevant to their original transaction.

---

## 25. Payment to Debt Allocation

Debt repayment is separate from the original debt-creating payment.

A repayment must identify:

* customer;
* repayment amount;
* payment method;
* allocation to one or more debt Orders where applicable;
* employee;
* Branch;
* Cash Session when cash is used;
* timestamp.

The customer's balance and relevant debt Order balances are updated through an atomic financial operation.

---

## 26. Offline Debt Repayment

Authorized trusted devices may record debt repayments while offline if the current offline authorization permits the operation.

The repayment is stored locally and synchronized later.

The server revalidates:

* customer state;
* debt balance;
* payment permission;
* Branch scope;
* subscription entitlement;
* transaction UUID.

Conflicts are recorded rather than silently overwriting server state.

---

## 27. Overpayment

The system allows an amount greater than the Order's remaining amount when the business rules permit overpayment.

Example:

```text id="r3v8k5"
Order Remaining:       80,000
Accepted Amount:      100,000
Overpayment:            20,000
```

The excess is not treated as an unpaid Order balance or cashier incentive.

It is recorded as Business/Branch additional income or overpayment.

---

## 28. Cash Overpayment Workflow

For cash:

1. Cashier receives the customer's cash.
2. Cashier gives the customer the full applicable change.
3. Cashier enters the final accepted amount into the system.
4. If the entered amount exceeds the Order amount, the system requests confirmation.
5. After confirmation, the excess is recorded as overpayment/additional Business or Branch income.

This prevents accidental overpayment entry from silently becoming business income.

---

## 29. Overpayment Attribution

An overpayment record should preserve:

* Overpayment UUID;
* Payment UUID;
* Order UUID;
* Business UUID;
* Branch UUID;
* Cash Session UUID where applicable;
* Cashier UUID;
* Waiter UUID where applicable;
* original Order amount;
* entered/accepted amount;
* overpayment amount;
* date/time;
* payment method;
* confirmation status;
* reason/comment where required.

The overpayment belongs to the Business/Branch.

Reports may attribute the overpayment to the Cashier and, where applicable, the Waiter who served the customer.

---

## 30. Overpayment and Remaining Balance

The Order amount is considered settled according to the required payable amount.

The excess is stored separately.

The system must not create a negative remaining Order balance.

Example:

```text id="j8p2w6"
Order:          80,000
Accepted:      100,000
Order settled:  80,000
Overpayment:    20,000
Remaining:           0
```

---

## 31. Duplicate Payment Prevention

Payment creation must be idempotent.

If the same Payment UUID is received more than once:

* the system must not create another payment;
* the previously recorded result is returned or reused;
* no duplicate cash, debt, or financial effect is created.

This applies to:

* API retries;
* client timeouts;
* offline synchronization;
* background retries;
* duplicate requests.

---

## 32. Payment Concurrency

The system must safely handle concurrent payment attempts against the same Order.

The system must ensure that two valid payment operations cannot accidentally create an inconsistent financial state.

Payment validation and balance update must use appropriate transaction isolation, locking, or version checks.

---

## 33. Payment During Cash Session Transition

If a payment occurs during Cash Session transition:

* a payment completed before the transition belongs to the previous Cash Session;
* a payment completed after the transition belongs to the new Cash Session;
* a payment caught in the transition state remains pending until the transition is resolved according to the handover rules.

The system must not silently assign a payment to the wrong Cash Session.

---

## 34. Payment and Cash Session

Cash payments require a valid Cash Session unless an explicitly authorized business rule provides another controlled path.

The Cash Session must belong to:

* the same Branch;
* the same Cash Register;
* the relevant cashier/session context.

Closed sessions cannot receive ordinary new payments.

Corrections against historical payments are separate operations.

---

## 35. Payment and Table Visit

Payment retains its Order context.

The system may therefore determine:

```text id="u5m9c2"
Payment
  ↓
Order
  ↓
Table Visit/Session
  ↓
Table
```

Payment does not create a new Table Visit/Session.

Payment does not reopen a completed visit.

---

## 36. Payment and Waiter Attribution

Where an Order has waiter context, payment-related reporting may retain the relevant waiter attribution.

For overpayment, the system specifically preserves the applicable waiter where present.

Historical attribution must not be changed merely because another employee later performs a payment correction.

---

## 37. Payment and Inventory

Payment does not directly deduct inventory.

Inventory deduction occurs according to the Order acceptance transaction.

Therefore:

```text id="z6q3n7"
Order Acceptance
      ↓
Inventory Deduction

Payment
      ↓
Financial Settlement
```

These are related but separate system responsibilities.

---

## 38. Payment and Order Modification

Unpaid Orders may be modified according to Order rules.

A paid Order cannot be ordinarily edited.

Once financial settlement has occurred, changes require the appropriate cancellation, refund, or correction workflow.

---

## 39. Payment Correction

A completed payment cannot simply be overwritten.

A correction is a separate controlled operation.

The system preserves:

* original payment;
* corrected financial result;
* correction reason;
* actor;
* timestamp;
* relevant authorization;
* relationship between original and correction.

---

## 40. Payment Revision

Controlled payment editing is implemented as a revision/correction process.

Conceptually:

```text id="b2r7m5"
Original Payment
      ↓
Correction / Revision
      ↓
New Effective Result
```

The original record remains immutable.

The correction may affect current calculations while preserving the historical original.

---

## 41. Payment Correction Authorization

Payment correction requires the relevant permission.

Depending on the operation, approval may also be required.

The system must validate:

* employee;
* Branch;
* Business;
* payment state;
* correction permission;
* reason;
* affected financial records.

---

## 42. Refund Relationship

A refund is not a modification of the original payment record.

Instead:

```text id="n8c4v1"
Original Payment
      ↓
Refund Operation
```

The original payment remains historical.

Refund rules are defined in:

`13_Discounts_Refunds_and_Corrections.md`

---

## 43. Refund Does Not Automatically Return Inventory

A refund is a financial operation.

It does not automatically return inventory.

Inventory return requires a separate explicitly authorized inventory operation where applicable.

Served items never automatically return to inventory.

---

## 44. Offline Payment

Trusted devices may create permitted payments while offline.

Offline payment requires:

* trusted device;
* valid offline authorization;
* active employee authorization;
* valid Branch scope;
* valid subscription entitlement;
* valid Order context;
* Payment UUID.

The payment is stored locally until synchronization.

---

## 45. Offline Payment Validation

Offline validation uses the latest valid locally available state.

The system must enforce the offline authorization limits.

When synchronization occurs, the server validates:

* Payment UUID;
* Business;
* Branch;
* Employee;
* Device;
* subscription;
* Order state;
* payment eligibility;
* amount;
* remaining amount;
* payment method;
* Cash Session where applicable;
* related dependencies.

---

## 46. Offline Payment Conflict

A conflict may occur if the server state changed while the payment was offline.

Example:

```text id="s7k2d4"
Offline:
Payment 100,000

Server:
Order already fully paid
```

The server must not silently duplicate the payment.

Instead:

* the payment event remains traceable;
* the synchronization result becomes a Conflict;
* authorized users resolve the conflict;
* the resolution is recorded separately.

---

## 47. Offline Card Payment

Offline Card payment requires a distinction between:

1. ERP recording of a Card payment.
2. External processor authorization.

The ERP may record the business payment event according to offline rules, but it must not falsely claim external processor authorization if no external verification occurred.

---

## 48. Payment Synchronization

Offline payments use the general synchronization lifecycle:

```text id="q4m8v2"
Pending
   ↓
Syncing
   ↓
Synced
```

Alternative outcomes:

```text id="e6c1p9"
Retrying
Conflict
Failed
```

Payment synchronization must be idempotent.

---

## 49. Payment Dependency Ordering

Payment synchronization may depend on:

* Business context;
* Branch context;
* Employee;
* Device;
* Order;
* Cash Session;
* Customer for Debt;
* previous payment state.

Dependent events must wait until required prerequisites are successfully synchronized.

---

## 50. Payment Source

The system must distinguish payment source where relevant:

* Online;
* Offline;
* Sync;
* System.

This information supports audit, troubleshooting, and historical analysis.

---

## 51. Payment Timestamps

The system should retain:

* client/payment event time;
* server received time;
* synchronization time where applicable.

Offline time does not replace server-side synchronization time.

Clock anomalies are handled according to the system-wide security and synchronization rules.

---

## 52. Payment Audit

Important payment operations must be auditable.

Audit context should include:

* Event UUID;
* Payment UUID;
* Order UUID;
* Business UUID;
* Branch UUID;
* Employee/System actor;
* Device UUID;
* Cash Session UUID where applicable;
* timestamp;
* old state;
* new state;
* amount;
* payment method;
* reason where applicable;
* source;
* result.

Payment correction must additionally preserve the original/new financial context.

---

## 53. Payment History

Payment history must preserve:

* original payment;
* payment method;
* amount;
* Order relationship;
* Cash Session;
* employee;
* device;
* timestamps;
* corrections;
* refunds;
* overpayment;
* synchronization history where required.

Historical records must not be silently overwritten.

---

## 54. Payment Reporting

Reports must be able to distinguish:

* total payments;
* payment methods;
* cash payments;
* card payments;
* debt;
* mixed payments;
* partial payments;
* overpayments;
* refunds;
* payment corrections;
* payment discrepancies;
* cashier attribution;
* waiter attribution where applicable.

Cash reports must use Cash Session context.

---

## 55. Payment and Report Versioning

If a payment correction changes a relevant report metric:

* a new report version is created;
* the previous report version remains immutable;
* the correction is linked to the new report version.

If a correction does not affect any relevant report metric, no unnecessary new report version is required.

---

## 56. Payment and Notifications

Important payment events may trigger notifications.

Examples include:

* large refund;
* payment discrepancy;
* relevant overpayment;
* unresolved payment conflict;
* failed payment synchronization.

Notification failure must not roll back the payment transaction.

---

## 57. Payment Performance

Payment is a critical POS operation.

The system should avoid blocking the cashier with:

* heavy report generation;
* notification delivery;
* printer communication;
* background synchronization;
* unrelated configuration processing.

Core payment validation and commit must remain fast.

---

## 58. Error Handling

Payment errors must be classified as:

* Validation Error;
* Authorization Error;
* Conflict;
* Business Rule Violation;
* Temporary Infrastructure Error;
* Permanent Failure.

The user receives a business-safe message.

Technical details remain in structured logs.

Retryable failures must use safe idempotent retry mechanisms.

---

## 59. Core Transaction Boundary

Payment creation must be atomic for its own financial effects.

A successful payment transaction must not leave only part of its required financial state committed.

For example, a completed Cash payment must not be committed without the corresponding payment record and Cash Session relationship.

If a core payment transaction fails, its atomic changes are rolled back.

---

## 60. Secondary Operations

After the core payment transaction succeeds, secondary operations may include:

* notifications;
* report refresh;
* audit delivery through reliable mechanisms;
* synchronization bookkeeping;
* background calculations.

Failure of these secondary operations must not roll back a committed payment.

---

## 61. Subscription and Permission Enforcement

Payment operations are subject to:

* Business subscription entitlement;
* Employee Status;
* Role Permission;
* Employee Override;
* Branch Scope;
* Device/Offline Authorization.

Frontend visibility is not sufficient for authorization.

The backend/server must enforce payment permissions.

---

## 62. System Invariants

The following invariants apply to the Payment System:

1. Every payment has a unique Payment UUID.
2. Payment UUID is the primary idempotency identity.
3. Client Transaction ID is not the primary payment identity.
4. Payment context contains Business and Branch identity.
5. Payment must reference a valid Order.
6. Payment must belong to the same Business as the Order.
7. Payment must belong to the same Branch as the Order.
8. Payment requires valid employee authorization.
9. Payment requires valid subscription entitlement.
10. Cash payments require the relevant Cash Session context.
11. Closed Cash Sessions cannot receive ordinary new payments.
12. Payment lifecycle is `Pending → Completed`.
13. Refund is a separate financial operation.
14. Correction is a separate financial operation.
15. Original completed payment records remain immutable.
16. Partial payment is supported.
17. Multiple payments may belong to one Order.
18. Mixed payment may contain multiple payment portions.
19. Cash portions contribute to physical cash.
20. Card portions do not contribute to physical cash.
21. Debt payments are linked to customer debt context.
22. Debt repayment is separate from the original debt-creating payment.
23. Split bill does not split the original Order into multiple Orders.
24. Payment does not automatically change operational Order status.
25. Payment does not automatically mark an Order Served.
26. Payment does not directly deduct inventory.
27. Overpayment is recorded separately from the Order payable amount.
28. Overpayment belongs to the Business/Branch.
29. Overpayment is not cashier personal income.
30. Overpayment may be attributed to Cashier and applicable Waiter.
31. Order remaining balance cannot become negative because of overpayment.
32. Duplicate Payment UUID processing must not create duplicate financial effects.
33. Payment retries must be idempotent.
34. Concurrent payments must be safely validated.
35. Offline payment requires trusted-device authorization.
36. Offline payment is revalidated by the server during synchronization.
37. Offline payment conflicts are explicit.
38. Server state is authoritative after synchronization.
39. Payment source is traceable.
40. Client and server timestamps are preserved where required.
41. Payment corrections preserve the original financial state.
42. Refunds preserve the original payment.
43. Refund does not automatically return inventory.
44. Served items never automatically return inventory.
45. Important payment operations are auditable.
46. Payment history is not silently overwritten.
47. Payment correction can create a new report version when relevant metrics change.
48. Unrelated secondary service failures do not roll back a committed payment.
49. Payment errors expose business-safe information to users.
50. Technical payment diagnostics remain in structured logs.
51. Core payment effects are atomic.
52. Heavy background work must not block POS payment processing.
53. Payment operations respect Business and Branch isolation.
54. Payment permissions are enforced server-side.
55. Trusted Device status alone does not grant payment permission.
56. Historical payment context remains traceable after corrections, refunds, and synchronization.

---

## 63. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/12_Debt_and_Payment_Allocation.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/15_Shift_Handover.md`
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

## 64. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `11_Payment_System.md`

**Next Document:** `12_Debt_and_Payment_Allocation.md`

