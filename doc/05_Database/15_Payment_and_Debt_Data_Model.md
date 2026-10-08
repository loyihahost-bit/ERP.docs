# Payment and Debt Data Model

**Document ID:** DB-15
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* Payments;
* Payment Items/Portions;
* Cash payments;
* Card payments;
* Debt payments;
* Mixed payments;
* Partial payments;
* Overpayments;
* Debt Customers;
* Debt balances;
* Debt repayment allocation;
* Refund relationships;
* Payment corrections;
* Payment history;
* Offline payments;
* Synchronization;
* historical financial integrity.

The model must preserve financial history while supporting fast POS payment operations.

---

## 2. Design Principles

The Payment and Debt model follows these principles:

1. Every Payment has a UUID.
2. Payment UUIDs are never reused.
3. Payments belong to one Business.
4. Payments reference Orders within the same Business and Branch scope.
5. Payment state is separate from Order operational state.
6. Cash, Card, Debt, and Mixed payments are supported.
7. Partial payments are supported.
8. One Order may have multiple Payments.
9. Mixed payment is one logical payment with multiple portions.
10. Overpayment is explicitly recorded and never silently applied to the Order.
11. Debt is a separate financial obligation.
12. Debt Customers are not full CRM Customers.
13. Multiple debt Orders may belong to one Debt Customer.
14. Partial debt repayment is supported.
15. Debt repayment must preserve allocation history.
16. Completed Payments are not silently overwritten.
17. Payment corrections use controlled revisions/corrections.
18. Refunds are separate from Payments.
19. Refunds do not automatically return inventory.
20. Offline Payments use UUID-based idempotency.
21. Server validation is authoritative after synchronization.
22. Historical financial values remain immutable.
23. Payment records must support cashier and Cash Session attribution.
24. Financial operations must use exact monetary types.

---

## 3. Payment Ownership

Every Payment belongs to exactly one Business.

Conceptually:

```text id="7g4m2k"
Business
   ↓
Payment
```

If a Payment references an Order:

```text id="n6x8q1"
Payment.business_id
=
Order.business_id
```

Cross-Business Payment/Order relationships are forbidden.

---

## 4. Payment Identity

Every Payment has a UUID:

```text id="payment_uuid"
```

The UUID:

* is globally unique;
* is generated before synchronization where required;
* remains unchanged after synchronization;
* provides idempotency;
* is never reused.

No Client Transaction ID is required.

---

## 5. Payment Context

A Payment should preserve operational context.

Suggested fields:

```text id="w4k8p2"
id
business_id
branch_id
order_id
employee_id
device_id
cash_register_id
cash_session_id
payment_type
status
amount
currency
created_at
completed_at
updated_at
```

Some fields may be nullable depending on payment method and lifecycle.

---

## 6. Supported Payment Types

Current payment methods are:

```text id="d8p3m1"
CASH
CARD
DEBT
MIXED
```

Future payment methods may be added without changing the identity model.

---

## 7. Payment Status

The current core Payment lifecycle is:

```text id="q7m2x9"
PENDING
   ↓
COMPLETED
```

Exceptional states may include:

```text id="v4n8c2"
FAILED
CANCELLED
```

depending on the implementation.

A Payment that has already been completed must not be silently converted into another financial state.

---

## 8. Order Payment Relationship

One Order may have:

```text id="s5k2r8"
0 Payments
1 Payment
Multiple Payments
```

Multiple Payments are required for:

* partial payments;
* split payment portions;
* debt;
* correction scenarios.

The Order must not embed the complete Payment lifecycle.

---

## 9. Paymentable Amount

At payment creation time, the system calculates:

```text id="z6x3m7"
Remaining Amount =
Order Total
-
Completed Payments
+
Applicable Corrections
```

The exact authoritative calculation belongs to the Payment domain.

The current Order total must not be reconstructed from mutable Product prices.

---

## 10. Partial Payment

An Order may be partially paid.

Example:

```text id="m8p4v1"
Order Total = 100,000

Payment 1 = 40,000

Remaining = 60,000
```

The Order remains financially unsettled.

The database must preserve each Payment independently.

---

## 11. Fully Paid Order

An Order becomes financially settled when its authoritative payment balance is zero after valid completed payments and corrections.

Payment state may then be represented as:

```text id="q4b8n1"
PAID
```

This does not automatically change the operational Order status.

---

## 12. Overpayment

The system allows overpayment when explicitly confirmed.

Example:

```text id="x2m7k5"
Order Total = 100,000
Customer pays = 120,000

Excess = 20,000
```

The excess must not silently become additional Order revenue.

It must be recorded as an explicit overpayment amount.

---

## 13. Overpayment Confirmation

If the entered payment exceeds the remaining Order amount:

1. The system detects the excess.
2. The cashier confirms the excess.
3. The system records the excess explicitly.
4. The excess is attributed to the appropriate Business/Branch financial context.

The original Order total remains unchanged.

---

## 14. Overpayment Storage

Conceptual fields may include:

```text id="j7v4q2"
order_amount
accepted_amount
applied_amount
overpayment_amount
overpayment_reason
```

The exact model may instead use a separate Overpayment entity.

Historical values must remain immutable after completion.

---

## 15. Overpayment Attribution

Overpayment should preserve:

* cashier;
* Waiter where applicable;
* Branch;
* Cash Session where applicable;
* Payment UUID;
* timestamp.

This allows financial reporting and investigation.

---

## 16. Cash Payment

A Cash Payment represents physical cash received.

The payment should reference:

* Branch;
* Cash Register;
* Cash Session;
* Cashier;
* Order;
* accepted amount.

Cash payment affects physical cash expectations for the Cash Session.

---

## 17. Cash Payment and Change

The cashier gives the customer full change before finalizing the accepted payment amount.

The database must preserve the final accepted amount used by the financial transaction.

If the customer intentionally pays more than the Order amount and the excess is confirmed, the excess is stored as overpayment/income according to the business rules.

---

## 18. Card Payment

Card Payment records the amount accepted through the ERP.

The current scope does not require direct external payment processor integration.

Therefore the system records:

```text id="r2m8w4"
ERP Card Payment
```

rather than claiming that the external bank transaction was automatically verified.

---

## 19. Card Payment Context

A Card Payment may preserve optional external reference information if available.

Conceptual fields:

```text id="k5v1q8"
external_reference
terminal_reference
payment_note
```

These fields are informational unless an actual payment integration is introduced later.

---

## 20. Debt Payment

A Debt Payment allows an Order to become a financial obligation rather than immediate settlement.

The system should create or associate a Debt record.

Conceptually:

```text id="p7n3x5"
Order
  ↓
Debt
  ↓
Debt Customer
```

The original Order remains historically intact.

---

## 21. Debt Customer

The current system does not implement full Customer CRM.

A Debt Customer is a limited financial identity used to manage debt.

Suggested fields:

```text id="h4m8q2"
id
business_id
name
phone
status
created_at
updated_at
```

Multiple Debt Customers may have the same phone number.

Phone uniqueness must not be required.

---

## 22. Historical Debt Customer Information

Debt Orders should retain the relevant name and phone snapshot.

Changing the Debt Customer profile must not rewrite historical Order information.

Example:

```text id="c6v2n9"
Debt Customer name = "Ali"

Historical Order:
name_snapshot = "Ali"
phone_snapshot = "..."
```

---

## 23. Debt Record

A Debt record represents an outstanding financial obligation.

Suggested fields:

```text id="m3q7k1"
id
business_id
branch_id
debt_customer_id
order_id
original_amount
outstanding_amount
status
created_at
updated_at
```

A Debt may be associated with one Order while one Debt Customer can have many Debt records.

---

## 24. Debt Status

Suggested states:

```text id="x8r4p2"
OPEN
PARTIALLY_PAID
SETTLED
CANCELLED
```

A settled Debt remains historically available.

---

## 25. Debt Amount Integrity

The outstanding balance must satisfy:

```text id="f5n2m8"
outstanding_amount >= 0
```

The balance must not become negative.

If a repayment exceeds the outstanding amount, the excess must be handled through the explicit overpayment process rather than silently reducing the debt below zero.

---

## 26. Debt Repayment

A Debt Customer may repay one or more outstanding debts.

Example:

```text id="v3q9k5"
Debt A = 100,000
Debt B = 50,000

Repayment = 80,000
```

The repayment may be allocated across one or multiple debts according to the authorized allocation operation.

---

## 27. Debt Payment Allocation

A repayment should have explicit allocation records.

Suggested model:

```text id="n6m2r7"
Debt Repayment
      ↓
Debt Allocation
      ↓
Debt
```

Suggested allocation fields:

```text id="y8k4p1"
id
repayment_id
debt_id
allocated_amount
created_at
```

This preserves exactly how a repayment affected each Debt.

---

## 28. Repayment Allocation Integrity

The sum of allocations must not exceed the repayment amount.

Conceptually:

```text id="p2v7x4"
SUM(debt_allocations)
<= repayment.amount
```

The remaining amount may be treated as overpayment or unapplied balance according to the business rules.

---

## 29. Debt Repayment Payment Type

Debt repayment may use:

* Cash;
* Card.

The repayment itself is a financial transaction separate from the original debt creation.

The original Debt Order remains unchanged.

---

## 30. Debt Repayment Attribution

A repayment must preserve:

* Business;
* Branch;
* Employee;
* Device;
* Cash Register where applicable;
* Cash Session where applicable;
* Debt Customer;
* timestamp.

This is required for financial reconstruction.

---

## 31. Debt and Cash Session

Cash Debt repayment affects physical cash when the repayment is made in Cash.

The repayment should therefore reference the relevant Cash Session.

The original Debt creation does not necessarily represent immediate physical cash movement.

---

## 32. Debt and Card

Card debt repayment records the ERP financial event.

External card settlement remains outside the current scope unless a payment processor integration is added later.

---

## 33. Mixed Payment

A Mixed Payment is one logical Payment containing multiple payment portions.

Example:

```text id="c5m9v3"
Order = 100,000

Cash = 60,000
Card = 40,000

Logical Payment = 100,000
```

The database should preserve both the logical Payment and its portions.

---

## 34. Payment Portion

Suggested model:

```text id="z7p2m8"
Payment
   ↓
Payment Portion
```

Suggested fields:

```text id="k4v9q1"
id
payment_id
payment_method
amount
cash_session_id
cash_register_id
created_at
```

A Mixed Payment must have at least two valid portions with compatible payment methods.

---

## 35. Payment Portion Totals

For a completed Mixed Payment:

```text id="r8m3x5"
SUM(portion.amount)
=
payment.amount
```

The database/application transaction must enforce this invariant.

---

## 36. Payment Method Immutability

After a Payment is completed, its payment method and amount must not be silently overwritten.

Any correction must create a controlled correction/revision record.

The original Payment remains historical.

---

## 37. Payment Correction

A completed Payment may require correction because of:

* data entry error;
* wrong payment method;
* wrong amount;
* operational correction.

The original Payment must remain immutable.

Conceptually:

```text id="m5q8v2"
Original Payment
      ↓
Correction
      ↓
Corrected Financial State
```

---

## 38. Payment Revision

A Payment Revision may contain:

```text id="x4n7p9"
id
payment_id
previous_state
new_state
reason
actor_id
created_at
```

The exact implementation may use a dedicated correction entity.

Every correction must be auditable.

---

## 39. Payment Correction Authorization

Payment correction requires appropriate permission.

A Cashier must not silently rewrite a completed Payment.

Higher authorization may be required depending on the correction type and business configuration.

---

## 40. Payment and Order Correction

Correcting a Payment must not automatically rewrite historical Order Items.

If the correction affects the Order's financial state, the system creates the appropriate Payment/Correction records.

Historical Order values remain preserved.

---

## 41. Refund

Refunds are separate from Payment creation.

A Refund references the original Payment or relevant Payment portions.

Supported refund scopes include:

* full;
* partial;
* item;
* quantity.

Refunds do not delete the original Payment.

---

## 42. Refund and Inventory

Refund does not automatically return inventory.

If inventory must be returned, a separate authorized inventory return/correction operation is required.

This prevents financial and physical stock operations from becoming silently coupled.

---

## 43. Refund Payment Methods

Current refund methods are:

```text id="j8v3q5"
CASH
CARD
```

Debt refund is not part of the current refund flow.

---

## 44. Refund Reason

Every Refund requires a reason.

Suggested fields:

```text id="c2m6r8"
reason
comment
actor_id
created_at
```

Refunds must be permission-controlled.

Large Refunds may trigger notifications.

---

## 45. Payment and Cash Register

Cash Payments affect Cash Session expected cash.

Card Payments do not represent physical cash.

Debt creation does not represent immediate cash inflow.

Debt repayment in Cash does represent physical cash inflow.

Mixed Payments affect the relevant financial contexts according to their portions.

---

## 46. Payment and Cash Session Attribution

For every applicable Cash Payment, the database must preserve:

```text id="v6n3m9"
cash_register_id
cash_session_id
employee_id
```

The Payment must belong to the correct Branch.

---

## 47. Payment During Cashier Handover

A payment occurring during a cashier transition may temporarily be pending until the Cash Session transition is complete.

Once assigned, the Payment must reference the correct Cash Session.

The original Order UUID remains unchanged.

---

## 48. Payment and Cash Session Concurrency

Only one valid Cash Session may accept a new Cash Payment for a Branch/Register at the relevant time.

Concurrent attempts must be serialized.

The first valid transaction wins.

---

## 49. Offline Payment

Trusted devices may create Payments offline if authorized.

Offline Payment must retain:

* Payment UUID;
* Order UUID;
* Employee;
* Device;
* Branch;
* payment type;
* amount;
* timestamp;
* local transaction state.

---

## 50. Offline Payment Validation

When synchronized, the server validates:

* Business;
* Branch;
* Order;
* paymentable amount;
* employee;
* permission;
* device trust;
* subscription;
* Cash Session where applicable;
* payment type;
* idempotency.

Invalid offline Payments become explicit conflicts or rejections.

---

## 51. Offline Payment Conflict

Example:

```text id="h7m2q4"
Server Order Remaining = 20,000

Offline Payment = 20,000

Another device already paid = 20,000
```

The server must not silently accept both as normal settlement.

The second transaction becomes a conflict or controlled overpayment case according to the financial rules.

---

## 52. Offline Cash Payment

Offline Cash Payments may be recorded against a trusted offline Cash Session.

The local device must retain enough information to reconcile physical cash later.

Synchronization must validate Cash Session state and authorization.

---

## 53. Offline Card Payment

Offline Card Payment means the ERP records a Card Payment locally.

It does not imply that an external card processor accepted the transaction.

External processor integration is outside the current scope.

---

## 54. Offline Debt Repayment

Authorized trusted devices may record Debt Repayments offline.

The server validates:

* Debt identity;
* outstanding balance;
* repayment amount;
* employee permission;
* Branch;
* Cash Session for Cash repayments.

Conflicts must remain explicit.

---

## 55. Idempotency

Payment synchronization must be idempotent.

Repeated submission of the same Payment UUID must not create:

* duplicate Payment;
* duplicate cash inflow;
* duplicate debt repayment;
* duplicate debt allocation.

The database unique identity constraint is the first protection.

---

## 56. Payment Transaction Boundary

Payment creation must atomically validate and persist the financial event.

Conceptually:

```text id="t8p4m2"
Validate Order
Validate Remaining Amount
Validate Method
Validate Context
Create Payment
Create Portions
Update Financial State
Commit
```

External notifications and reports remain secondary processing.

---

## 57. Debt Repayment Transaction Boundary

A Debt Repayment must atomically:

```text id="m2q7v5"
Validate Debt
Validate Outstanding Balance
Create Repayment
Create Allocations
Update Debt Balance
Commit
```

A partial database failure must roll back the complete repayment.

---

## 58. Overpayment Transaction Boundary

Overpayment confirmation must atomically record:

* accepted Payment;
* applied amount;
* overpayment amount;
* attribution;
* required explanation.

The Order total remains unchanged.

---

## 59. Payment State Reconstruction

The system should be able to reconstruct Order financial state from:

* original Order total;
* completed Payments;
* Payment corrections;
* Refunds;
* explicit overpayments.

The current Product price must never be required.

---

## 60. Historical Payment Integrity

The following values must remain historically reconstructable:

* Payment UUID;
* Order UUID;
* amount;
* method;
* currency;
* Branch;
* employee;
* Device;
* Cash Session;
* creation/completion time;
* correction history;
* refund relationships;
* debt relationships;
* overpayment data.

---

## 61. Suggested `payments` Fields

```text id="z5n8r1"
id
business_id
branch_id
order_id
employee_id
device_id
cash_register_id
cash_session_id
payment_type
status
amount
currency
applied_amount
overpayment_amount
created_at
completed_at
updated_at
```

---

## 62. Suggested `payment_portions` Fields

```text id="q8m3v6"
id
payment_id
payment_method
amount
cash_register_id
cash_session_id
created_at
```

For a non-Mixed Payment, a single logical portion may be used internally or the portion table may be omitted depending on implementation.

---

## 63. Suggested `debt_customers` Fields

```text id="m4x7p2"
id
business_id
name
phone
status
created_at
updated_at
```

Phone number must not be globally unique.

---

## 64. Suggested `debts` Fields

```text id="v9q2k5"
id
business_id
branch_id
debt_customer_id
order_id
original_amount
outstanding_amount
status
created_at
updated_at
```

A Debt should retain the originating Order relationship.

---

## 65. Suggested `debt_repayments` Fields

```text id="n5m8r3"
id
business_id
branch_id
debt_customer_id
employee_id
device_id
cash_register_id
cash_session_id
payment_method
amount
status
created_at
completed_at
```

---

## 66. Suggested `debt_allocations` Fields

```text id="x7p4v1"
id
repayment_id
debt_id
allocated_amount
created_at
```

Allocation rows should be immutable after completion except through controlled correction.

---

## 67. Suggested `payment_corrections` Fields

```text id="k3m9q6"
id
payment_id
previous_amount
new_amount
previous_method
new_method
reason
actor_id
device_id
created_at
```

The exact structure may use immutable correction events instead of before/after columns.

---

## 68. Foreign Key Rules

Important relationships include:

```text id="c8v2m5"
payment.business_id → business.id
payment.order_id → order.id
payment.employee_id → employee.id
payment.device_id → device.id
payment.cash_session_id → cash_session.id

debt.business_id → business.id
debt.debt_customer_id → debt_customer.id
debt.order_id → order.id

debt_repayment.debt_customer_id → debt_customer.id
debt_allocation.debt_id → debt.id
```

All referenced records must satisfy Business and Branch ownership rules.

---

## 69. Payment Amount Constraints

The database must enforce:

```text id="w4q8m1"
amount >= 0
applied_amount >= 0
overpayment_amount >= 0
```

For normal completed Payments:

```text id="r7n2v5"
applied_amount + overpayment_amount = amount
```

---

## 70. Debt Amount Constraints

The database must enforce:

```text id="j5m8q3"
original_amount >= 0
outstanding_amount >= 0
```

A Debt must never have a negative outstanding balance.

---

## 71. Payment Portion Constraints

Each Payment Portion must satisfy:

```text id="p3v7x9"
amount > 0
```

For completed Mixed Payments:

```text id="k8m2q4"
SUM(portions.amount) = payment.amount
```

---

## 72. Debt Allocation Constraints

Each Debt Allocation must satisfy:

```text id="v2q6m8"
allocated_amount > 0
```

The total allocations of a Repayment must not exceed the Repayment amount.

The total allocation against a Debt must not exceed its outstanding balance unless the excess is explicitly handled by an approved overpayment process.

---

## 73. Duplicate Payment Prevention

The Payment UUID must be unique.

Additional application-level duplicate detection may use:

* Order;
* employee;
* device;
* amount;
* timestamp;
* synchronization identity.

These are supporting checks only.

Payment UUID remains the authoritative idempotency identity.

---

## 74. Order Payment State

The database may maintain a current payment summary for fast POS reads.

If maintained, it must be derived from authoritative Payment records and updated atomically.

A cached or denormalized payment state must not become the only source of truth.

---

## 75. Payment Concurrency

Two concurrent Payments against the same remaining Order amount must be serialized.

Example:

```text id="n7x3m9"
Remaining = 50,000

Device A → 50,000
Device B → 50,000
```

Only one normal settlement may consume the available amount.

The second must be rejected or handled as an explicitly confirmed overpayment.

---

## 76. Debt Concurrency

Two concurrent Debt Repayments against the same outstanding Debt must be serialized.

The database must prevent:

```text id="q5m8v2"
Debt Outstanding = 50,000

Repayment A = 50,000
Repayment B = 50,000

Final Debt = -50,000
```

Such a state is invalid.

---

## 77. Correction Concurrency

Two users must not silently modify the same completed Payment at the same time.

Optimistic concurrency or locking must be used.

Stale corrections must be rejected.

---

## 78. Refund Relationship

Refund records should reference:

```text id="r8m4q1"
original_payment_id
order_id
employee_id
branch_id
amount
reason
```

The exact Refund model is defined further by the database sequence.

Refunds remain separate from Payment creation.

---

## 79. Payment History

Payment history must be append-oriented.

A correction creates a new historical record rather than silently modifying the original completed Payment.

The system must support reconstruction of the financial state at a given time.

---

## 80. Reporting

The Payment model supports:

* sales settlement;
* Cash Session reports;
* Cashier reports;
* Card totals;
* Debt balances;
* Debt repayments;
* Overpayments;
* Refunds;
* Partial payments;
* Mixed payments;
* Branch financial reports.

Reports must use immutable financial records.

---

## 81. Audit

Important Payment operations must create audit events.

Examples:

* Payment created;
* Payment completed;
* Payment corrected;
* Overpayment confirmed;
* Debt created;
* Debt repayment recorded;
* Debt allocation changed through authorized correction;
* Refund created;
* Payment conflict resolved.

Audit records remain separate from Payment history.

---

## 82. Data Lifecycle

During subscription expiry:

* historical Payments remain readable;
* Debt balances remain readable;
* allowed reports remain available;
* new modifying financial operations may be blocked.

During Business deletion:

* Payments;
* Debt;
* Debt Customers;
* Repayments;
* Allocations;
* Corrections

are deleted according to the controlled dependency-aware lifecycle.

---

## 83. Offline and Synchronization

Payment-related offline events must use:

* UUID identity;
* durable local storage;
* encrypted local storage;
* offline authorization;
* synchronization state;
* server-side validation;
* explicit conflict records.

Transaction synchronization must occur before configuration synchronization.

---

## 84. Cache

Current payment summaries may be cached.

Cache is not authoritative.

Financial settlement must always use authoritative database state.

---

## 85. Indexing Strategy

Recommended indexes:

```text id="y5m8q2"
payments(business_id, branch_id, created_at)
payments(order_id, created_at)
payments(cash_session_id, created_at)
payments(employee_id, created_at)
payments(device_id, created_at)
payments(status, created_at)

payment_portions(payment_id)

debt_customers(business_id, phone)
debts(business_id, branch_id, status)
debts(debt_customer_id, status)
debt_repayments(debt_customer_id, created_at)
debt_allocations(debt_id, created_at)
```

Indexes must support POS and debt lookup without excessive write overhead.

---

## 86. Security Requirements

The Payment database model must support:

* Business isolation;
* Branch isolation;
* employee attribution;
* Device attribution;
* Cash Session attribution;
* permission-controlled corrections;
* subscription entitlement;
* offline authorization;
* audit;
* synchronization validation.

Financial authorization must remain separate from Device Trust.

---

## 87. Performance Requirements

Payment operations are high-frequency POS operations.

Therefore:

* paymentable amount must be quickly available;
* Order payment summaries should be indexed;
* Payment writes must use short transactions;
* debt lookup must be efficient;
* historical reporting must not block payment operations;
* heavy debt reports should use background/reporting paths where necessary.

---

## 88. Transaction Boundaries

### Create Payment

```text id="u7m2q8"
Validate Order
Validate Remaining Amount
Validate Method
Validate Context
Create Payment
Create Portions
Update Financial Summary
Commit
```

### Create Debt

```text id="p4v8m1"
Validate Debt Customer
Validate Order
Create Debt
Commit
```

### Repay Debt

```text id="x2q7m5"
Validate Debt
Validate Balance
Create Repayment
Create Allocations
Update Balance
Commit
```

### Correct Payment

```text id="m8v3r6"
Validate Permission
Validate Current Version
Create Correction
Update Derived Financial State
Commit
```

---

## 89. Failure Handling

If Payment creation fails:

```text id="q6m2p8"
No partial Payment
No partial Cash effect
No partial Debt settlement
```

If Debt Repayment fails:

```text id="n4v7x2"
No partial allocation
No partial balance update
```

If synchronization response is lost:

```text id="r8m3k5"
Retry using the same Payment UUID
```

If notification/report generation fails:

```text id="c7q2m9"
Financial transaction remains committed
```

---

## 90. Historical Integrity

The following must remain immutable or reconstructable:

* Payment UUID;
* original amount;
* payment method;
* Order reference;
* Cash Session;
* employee;
* Device;
* Debt Customer snapshot;
* Debt amount;
* repayment allocations;
* overpayment;
* corrections;
* refund relationships.

Current configuration must not rewrite financial history.

---

## 91. Database Invariants

The following invariants are mandatory:

1. Every Payment belongs to exactly one Business.
2. Every Payment UUID is globally unique.
3. Payment UUIDs are never reused.
4. Payment and Order Business ownership must match.
5. Payment and Order Branch ownership must match.
6. Payment employee must belong to the same Business.
7. Payment Device must belong to the correct Business/Branch scope.
8. Payment Cash Session must belong to the Payment Branch.
9. Payment Cash Register must belong to the Payment Branch.
10. Supported methods are Cash, Card, Debt, and Mixed.
11. Payment status is separate from Order operational status.
12. Payment amount cannot be negative.
13. Applied amount cannot be negative.
14. Overpayment amount cannot be negative.
15. Applied amount plus overpayment must equal Payment amount.
16. Order total is not rewritten by Payment.
17. Partial payments are supported.
18. Multiple Payments may belong to one Order.
19. Completed Payment values are not silently overwritten.
20. Payment corrections preserve the original Payment.
21. Payment corrections require authorization.
22. Payment corrections require a reason.
23. Payment method changes require controlled correction.
24. Payment amount changes require controlled correction.
25. Cash Payments affect the relevant Cash Session.
26. Card Payments do not represent physical cash.
27. Debt creation does not represent immediate physical cash.
28. Cash Debt repayment affects the relevant Cash Session.
29. Mixed Payment contains explicit portions.
30. Mixed Payment portion totals equal Payment amount.
31. Payment Portions must have positive amounts.
32. Overpayment requires explicit confirmation.
33. Overpayment does not increase Order total.
34. Overpayment is historically attributed.
35. Debt Customers belong to exactly one Business.
36. Debt Customer phone numbers are not globally unique.
37. Historical Debt Customer information remains reconstructable.
38. Debt belongs to one Business.
39. Debt Order belongs to the same Business.
40. Debt Customer belongs to the same Business as Debt.
41. Debt outstanding balance cannot be negative.
42. Debt original amount cannot be negative.
43. Debt status is controlled.
44. One Debt Customer may have multiple Debts.
45. Debt Repayment belongs to one Business.
46. Debt Repayment belongs to one Debt Customer.
47. Debt Repayment amount cannot be negative.
48. Debt Allocations reference valid Debts.
49. Debt Allocations reference valid Repayments.
50. Debt Allocation amount must be positive.
51. Debt allocation totals cannot exceed repayment amount.
52. Debt allocation cannot silently over-settle a Debt.
53. Debt Repayment updates Debt balance atomically.
54. Concurrent Debt Repayments must be serialized.
55. Debt balance cannot become negative.
56. Refund is separate from Payment creation.
57. Refund does not delete original Payment.
58. Refund requires authorization.
59. Refund requires a reason.
60. Refund does not automatically return inventory.
61. Offline Payments require trusted authorization.
62. Offline Payments use UUID identity.
63. Repeated Payment synchronization is idempotent.
64. Duplicate Payment UUIDs cannot create duplicate financial transactions.
65. Server validation is authoritative after synchronization.
66. Offline payment conflicts must be explicit.
67. Concurrent Payments against one remaining balance must be serialized.
68. Second settlement cannot silently overwrite the first.
69. Payment corrections cannot silently overwrite each other.
70. Historical Payment state remains reconstructable.
71. Current Product price is never required to reconstruct Payment history.
72. Payment history remains available during subscription expiry.
73. Subscription downgrade does not delete Payment history.
74. Business deletion follows the controlled lifecycle.
75. Business deletion is dependency-aware.
76. Deletion operations are idempotent.
77. Deleted Business data cannot be accessed through stale devices.
78. Deleted UUIDs are never reused.
79. Audit records remain separate from Payment records.
80. Financial transactions are atomic.
81. Notification failure does not roll back committed financial transactions.
82. Report generation failure does not roll back committed financial transactions.
83. Cache is never the authoritative financial state.
84. Payment queries enforce Business isolation.
85. Debt queries enforce Business isolation.
86. Branch-scoped financial queries enforce Branch isolation.
87. Cash Session attribution remains historically available.
88. Employee attribution remains historically available.
89. Device attribution remains historically available.
90. Historical Debt Customer data remains available.
91. Historical repayment allocations remain available.
92. Historical overpayment data remains available.
93. Historical corrections remain available.
94. Payment UUID is the permanent financial event identity.
95. No Client Transaction ID is required as a second authoritative identity.
96. Heavy financial reports must not block normal POS payment operations.
97. Database constraints and application validation must enforce the same ownership boundaries.
98. Financial state must be reconstructable from authoritative records.
99. Payment state must never be inferred solely from cached data.
100. Original financial events remain immutable; corrections are represented separately.

---

## 92. Related Documents

### Database

* `02_Database_Architecture.md`
* `03_Tenant_and_Business_Data_Model.md`
* `04_Identity_and_Access_Data_Model.md`
* `05_Branch_and_Organizational_Data_Model.md`
* `07_Device_and_Trust_Data_Model.md`
* `13_Order_and_Order_Item_Data_Model.md`
* `16_Cash_Register_and_Cash_Session_Data_Model.md`
* `17_Shift_Handover_Data_Model.md`
* `20_Audit_and_History_Data_Model.md`

### Domain

* `06_Order_Domain.md`
* `07_Cash_Domain.md`
* `09_Payment_Domain.md`
* `15_Audit_Domain.md`
* `20_Cross_Domain_Relationships_Domain.md`

### System Analysis

* `07_POS_and_Order_System.md`
* `11_Payment_System.md`
* `12_Debt_and_Payment_Allocation.md`
* `13_Discounts_Refunds_and_Corrections.md`
* `14_Cash_Register_and_Cash_Session.md`
* `15_Shift_Handover.md`
* `27_System_Wide_Consistency_and_Concurrency.md`

### Architecture

* `07_Database_Architecture.md`
* `08_Offline_Architecture.md`
* `09_Synchronization_Architecture.md`
* `17_Failure_Recovery_Architecture.md`
* `20_Architecture_Invariants_and_Guardrails.md`

---

## 93. Final Rule

The Payment and Debt Data Model must provide fast financial settlement while preserving immutable historical financial events.

The central rule is:

```text id="w3m8q5"
Original Payment is immutable.
Corrections are separate.
Debt balance is explicit.
Overpayment is explicit.
Refund is separate.
Historical financial state must always be reconstructable.
```

Payment, Debt, Cash, Order, Refund, Inventory, Audit, Offline Synchronization, and Reporting must remain explicitly connected but independently controlled database concerns.

