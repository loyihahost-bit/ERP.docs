# Payment Domain

**Document ID:** DA-09
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Payment domain manages the financial settlement of Orders and related financial operations.

It is responsible for:

* payment identity;
* payment lifecycle;
* payment methods;
* cash, card, debt, and mixed payments;
* partial payments;
* overpayments;
* debt repayment;
* refunds;
* payment corrections;
* payment history;
* payment attribution;
* payment concurrency;
* offline payment synchronization.

The Payment domain does not own:

* Order operational lifecycle;
* Cash Register physical state;
* Inventory;
* Product/Recipe definitions;
* Employee permissions;
* Reports;
* Notifications.

Those domains interact with Payment through explicit boundaries.

---

# 2. Payment Context

Every Payment belongs to a Business and Branch.

A Payment may additionally reference:

* Order;
* Employee;
* Device;
* Cash Register;
* Cash Session;
* payment method;
* related debt customer;
* related refund;
* related correction.

Historical context must remain reconstructable.

---

# 3. Payment Identity

Every Payment has a stable UUID.

The UUID is the authoritative identity of the Payment.

It is used for:

* idempotency;
* synchronization;
* audit correlation;
* historical reconstruction;
* duplicate prevention.

No Client Transaction ID is required.

---

# 4. Payment Lifecycle

The core Payment lifecycle is:

```text id="f3n8q1"
Pending
   ↓
Completed
```

Financial corrections and refunds are separate operations.

A completed Payment does not transition backward into Pending.

---

# 5. Payment Creation

Payment creation requires:

* authenticated employee;
* valid Business;
* valid Branch;
* valid Order;
* appropriate permission;
* valid paymentable Order state;
* amount validation;
* payment method validation;
* remaining amount validation.

The server must perform these checks.

---

# 6. Paymentable Order

Payment may begin once the Order reaches a paymentable operational state.

The Payment domain does not determine the Order's operational lifecycle.

It consumes the Order's current payment eligibility.

Payment completion does not automatically change:

* Preparing;
* Ready;
* Served

states.

---

# 7. Payment Amount

The payment amount must be explicitly recorded.

The system must distinguish between:

* Order total;
* amount already paid;
* remaining amount;
* current payment amount;
* confirmed overpayment.

---

# 8. Partial Payment

An Order may be partially paid.

Conceptually:

```text id="q7m2v5"
Order Total:      100,000
Paid:              60,000
Remaining:         40,000
```

The Order remains financially unsettled until the required amount is received.

---

# 9. Full Payment

When valid payments cover the required Order amount:

```text id="v4c9p2"
Remaining = 0
```

the Order becomes fully paid from the financial perspective.

This does not automatically change its operational status.

---

# 10. Payment Methods

The supported payment methods are:

```text id="s6w1k8"
Cash
Card
Debt
Mixed
```

These are business payment methods.

External payment processor integration is outside the current scope.

---

# 11. Cash Payment

A Cash Payment represents an amount received physically as cash.

The Payment domain records the financial transaction.

The Cash domain records the corresponding physical cash impact.

---

# 12. Card Payment

A Card Payment represents an amount recorded as card payment.

The current scope does not require external card processor authorization.

Therefore, the system must distinguish:

```text id="p5r8x2"
ERP Card Recording
```

from future:

```text id="m1c7q4"
External Processor Authorization
```

The second capability is outside the current scope.

---

# 13. Debt Payment

Debt allows an Order to be financially settled through a debt obligation.

Debt requires a customer debt record.

A customer debt record may contain:

* customer identity information;
* phone number;
* outstanding balance;
* associated debt Orders.

Duplicate phone numbers are allowed.

---

# 14. Debt Customer

The current model does not require a full CRM customer system.

The debt customer is a financial-domain record required for debt management.

Multiple debt Orders may belong to the same debt customer.

Historical Orders retain the customer information relevant at the time.

---

# 15. Debt Repayment

A debt customer may make a repayment later.

Repayment records:

* customer;
* amount;
* payment method;
* actor;
* Branch;
* timestamp;
* related debt allocation.

The repayment may be allocated across multiple debt Orders.

---

# 16. Partial Debt Repayment

Debt may be repaid partially.

Example:

```text id="r2k8m5"
Debt Balance: 500,000
Repayment:     200,000
Remaining:     300,000
```

The remaining debt remains outstanding.

---

# 17. Debt Allocation

A repayment may be allocated to one or more debt Orders.

The allocation must preserve:

* repayment UUID;
* Order UUID;
* allocated amount;
* allocation timestamp;
* actor.

The same repayment must not be allocated twice.

---

# 18. Offline Debt Repayment

Trusted authorized devices may record debt repayment offline where the offline authorization permits it.

The repayment receives a stable UUID.

Synchronization must prevent duplicate repayment.

The server revalidates:

* customer;
* repayment;
* amount;
* authorization;
* Branch;
* existing balance;
* allocation.

---

# 19. Mixed Payment

A Mixed Payment consists of multiple payment portions.

Example:

```text id="x9p4n7"
Cash  = 50,000
Card  = 30,000
Debt  = 20,000

Total = 100,000
```

The Payment domain maintains one logical Payment identity with internal portions.

---

# 20. Mixed Payment Integrity

The sum of all portions must equal the recorded Payment amount.

Invalid combinations must be rejected.

Each portion must retain its own method and amount.

Cash portions affect the Cash domain.

Debt portions affect debt state.

Card portions remain financial records.

---

# 21. Overpayment

The system may accept an amount greater than the remaining Order amount.

Overpayment requires explicit confirmation.

Example:

```text id="a8c2v6"
Order Total:       100,000
Already Paid:        0
Accepted Amount:   120,000
Overpayment:        20,000
```

The Order is settled for its required amount.

The additional 20,000 becomes a separate overpayment/additional income.

---

# 22. Overpayment Ownership

Confirmed overpayment belongs to the Business/Branch as additional income.

It must not silently increase the Order total.

The system preserves:

* Order amount;
* required payment;
* accepted amount;
* excess amount;
* cashier;
* waiter where applicable;
* Cash Session where applicable.

---

# 23. Cash Overpayment Workflow

For cash payment:

1. Cashier gives full required change to the customer.
2. Cashier enters the final accepted amount.
3. If the amount exceeds the Order requirement, the system requests confirmation.
4. Confirmed excess becomes overpayment.
5. The excess is attributed to the relevant Business/Branch.
6. Physical cash includes the accepted amount.

---

# 24. Payment Attribution

Payment history should preserve applicable attribution:

* cashier;
* waiter;
* employee;
* Branch;
* Device;
* Cash Register;
* Cash Session.

Attribution must not be overwritten when later corrections occur.

---

# 25. Payment Concurrency

Payment creation must be concurrency-safe.

The system must prevent:

* duplicate payment;
* double settlement;
* invalid simultaneous payments;
* payment exceeding allowed amount without explicit overpayment handling.

Payment UUID idempotency is mandatory.

---

# 26. Payment Idempotency

If the same Payment request is submitted more than once using the same Payment UUID:

```text id="j3v7q9"
First request  → creates Payment
Repeated request → returns existing result
```

It must not create another financial transaction.

---

# 27. Lost Response

If the server completes a Payment but the client does not receive the response:

* the client may retry using the same UUID;
* the server must recognize the existing Payment;
* a duplicate Payment must not be created.

---

# 28. Payment and Cash Session Concurrency

A Cash Payment must belong to a valid Cash Session where physical cash accounting applies.

During cashier handover:

* payments before the session boundary belong to the previous session;
* payments after the boundary belong to the new session;
* ambiguous transition requests remain pending until the session boundary is resolved.

---

# 29. Offline Payment

Offline Payment is allowed only on trusted devices with valid offline authorization.

Offline authorization must validate:

* Employee;
* Business;
* Branch;
* Device;
* permission;
* subscription state;
* authorization validity period.

---

# 30. Offline Payment Revalidation

During synchronization, the server revalidates:

* Payment UUID;
* Order UUID;
* amount;
* payment method;
* employee;
* Branch;
* Cash Session where applicable;
* remaining payment amount;
* existing payments;
* subscription;
* permission.

---

# 31. Offline Payment Conflict

If an offline Payment conflicts with a payment already committed on the server:

* the server does not silently overwrite either transaction;
* the offline Payment remains identifiable;
* a conflict record may be created;
* authorized resolution is required;
* the original transaction history remains preserved.

---

# 32. Payment Revision

Completed Payments are not silently edited.

A controlled revision/correction operation may be created when authorized.

The correction records:

* original value;
* new value;
* reason;
* actor;
* timestamp;
* authorization;
* affected context.

---

# 33. Original Payment Immutability

The original Payment remains historically preserved.

A correction creates a new financial record rather than rewriting the original record in place.

This supports:

* audit;
* reconciliation;
* reports;
* historical reconstruction.

---

# 34. Refund

Refund is a separate financial operation.

Supported refund scopes include:

* full refund;
* partial refund;
* item refund;
* quantity refund.

A refund references the original financial context.

---

# 35. Refund Methods

Current refund methods are:

```text id="b6m2r8"
Cash
Card
```

The refund method must be explicitly recorded.

---

# 36. Refund Authorization

Refund requires the appropriate permission.

Approval may be required according to configured business rules.

A refund without required authorization must be rejected.

---

# 37. Refund Reason

Every refund requires a reason.

The reason is preserved for:

* audit;
* reports;
* management review;
* historical reconstruction.

---

# 38. Refund Does Not Automatically Return Inventory

Refund and inventory return are separate concepts.

A refund does not automatically return inventory.

If inventory must be restored, an explicit authorized inventory operation is required.

Served items must not be silently returned to inventory.

---

# 39. Cash Refund

A Cash refund affects the relevant Cash Session when cash is physically returned.

The Cash domain records the physical cash impact.

The Payment domain remains authoritative for the refund transaction.

---

# 40. Large Refund Alert

Large refunds may trigger a notification according to configured business thresholds.

The Notification domain owns notification lifecycle.

Payment remains authoritative for the refund event.

---

# 41. Cancellation vs Refund

Cancellation and refund are different operations.

### Cancellation

Cancels the operational Order.

### Refund

Returns financial value after a payment has occurred.

An Order may require both operations, but one does not automatically mean the other.

---

# 42. Payment and Order History

Payment history must preserve:

* original Order UUID;
* payment amount;
* method;
* cashier;
* Branch;
* Cash Session;
* timestamp;
* revisions;
* refunds;
* overpayments.

Historical payment records must remain reconstructable.

---

# 43. Payment and Inventory

Payment does not control inventory deduction.

Inventory is consumed when the Order is Accepted.

Therefore:

```text id="c7w4n9"
Order Accepted
      ↓
Inventory Consumption

Payment
      ↓
Financial Settlement
```

These operations have separate domain responsibilities.

---

# 44. Payment and Cash

Payment and Cash are separate domains.

Payment determines:

* financial amount;
* method;
* settlement;
* debt;
* refund;
* overpayment.

Cash determines:

* physical cash impact;
* Cash Session;
* expected cash;
* actual cash;
* cash discrepancy.

---

# 45. Payment and Reports

The Report domain may consume:

* payments;
* payment portions;
* refunds;
* debt;
* overpayments;
* payment corrections.

Payment remains the authoritative source for payment state.

---

# 46. Payment and Notifications

Payment may produce notification-triggering events such as:

* large refund;
* significant overpayment;
* debt-related threshold;
* payment correction.

Notification state is not owned by Payment.

---

# 47. Aggregate Boundaries

The Payment domain should conceptually contain:

* Payment;
* Payment Portion;
* Debt Customer;
* Debt Repayment;
* Debt Allocation;
* Refund;
* Payment Correction;
* Overpayment record.

It should not contain:

* Order lifecycle;
* Cash Session;
* Inventory;
* Product;
* Employee;
* Report;
* Notification.

---

# 48. Domain Services

Potential Payment domain services include:

```text id="t5n8q2"
Payment Creation Service
Payment Allocation Service
Debt Repayment Service
Overpayment Service
Refund Service
Payment Correction Service
Payment Reconciliation Service
Payment Conflict Resolver
```

These are logical domain services, not mandatory separate applications.

---

# 49. Domain Events

Potential events include:

```text id="z4m7p1"
PaymentCreated
PaymentCompleted
PaymentPartiallyApplied
PaymentFullySettled
DebtCreated
DebtRepaymentCreated
OverpaymentConfirmed
RefundCreated
PaymentCorrectionCreated
PaymentConflictDetected
```

Events represent facts that have already occurred.

---

# 50. Payment Invariants

### Identity

1. Every Payment has a stable UUID.
2. Payment UUID is the authoritative payment identity.
3. Payment UUID is used for idempotency.
4. Payment history preserves Business and Branch context.
5. No Client Transaction ID is required.

### Payment Lifecycle

6. Payment starts in Pending when creation is not yet complete.
7. A completed Payment cannot return to Pending.
8. Refunds and corrections are separate operations.
9. Completed Payments are not silently edited.
10. Original Payment records remain historically identifiable.

### Amounts

11. Payment amount is explicitly stored.
12. Remaining amount is derived from valid payment history.
13. Partial payment is supported.
14. Full settlement occurs when the required amount is covered.
15. Payment completion does not automatically change Order operational status.
16. Overpayment is not silently added to Order total.
17. Confirmed overpayment is represented separately.

### Methods

18. Supported methods are Cash, Card, Debt, and Mixed.
19. Mixed Payment portions must have valid methods.
20. Mixed Payment portion totals must equal the logical Payment amount.
21. Cash portions affect physical cash.
22. Card portions do not affect physical cash.
23. Debt portions affect debt state.

### Debt

24. Debt requires a valid debt customer.
25. One debt customer may have multiple debt Orders.
26. Duplicate phone numbers are allowed.
27. Debt repayment may be partial.
28. Debt repayment has a stable UUID.
29. Debt repayment cannot be allocated twice.
30. Debt allocation preserves Order-level allocation history.
31. Offline debt repayment is subject to server revalidation.

### Overpayment

32. Overpayment requires explicit confirmation.
33. Overpayment does not modify the original Order price.
34. Overpayment belongs to Business/Branch as additional income.
35. Overpayment attribution is preserved.
36. Cash overpayment increases physical cash by the accepted amount.

### Refunds

37. Refund is separate from cancellation.
38. Refund requires authorization.
39. Refund requires a reason.
40. Full refund is supported.
41. Partial refund is supported.
42. Item and quantity refund are supported.
43. Cash refund affects physical cash.
44. Card refund is represented separately.
45. Refund does not automatically return inventory.
46. Served item inventory is never silently restored.

### Corrections

47. Payment correction preserves the original payment.
48. Correction requires appropriate authorization.
49. Correction preserves original and new values.
50. Correction preserves actor, reason, and timestamp.
51. Correction does not silently rewrite historical financial records.

### Concurrency

52. Payment creation is concurrency-safe.
53. Duplicate Payment UUID requests are idempotent.
54. Repeated requests do not create duplicate payments.
55. Lost server responses can be safely retried.
56. Simultaneous settlement attempts cannot silently double-settle an Order.
57. Cash-session transition does not create ambiguous payment ownership.

### Offline

58. Offline payment requires a trusted device.
59. Offline payment requires valid authorization.
60. Offline payment retains its UUID during synchronization.
61. Server revalidates offline payment state.
62. Offline conflicts are preserved rather than silently overwritten.
63. Offline payment synchronization is idempotent.

### Security and Scope

64. Payment operations require authentication.
65. Payment operations require applicable permission.
66. Business scope is validated.
67. Branch scope is validated.
68. Device trust is validated for offline operations.
69. Subscription entitlement is enforced where applicable.

### History

70. Payment history is reconstructable.
71. Refund history is reconstructable.
72. Debt history is reconstructable.
73. Overpayment history is reconstructable.
74. Payment correction history is reconstructable.
75. Original financial events remain identifiable after correction.

---

# 51. Completion Criteria

The Payment domain is considered complete when:

* Payment identity is defined;
* payment lifecycle is defined;
* payment methods are defined;
* partial and full settlement are defined;
* debt is defined;
* debt repayment and allocation are defined;
* Mixed Payment is defined;
* overpayment is defined;
* refund is defined;
* cancellation boundary is defined;
* payment correction is defined;
* Cash interaction is defined;
* Inventory boundary is defined;
* offline behavior is defined;
* synchronization/conflict handling is defined;
* concurrency rules are defined;
* historical integrity is defined;
* aggregate boundaries are clear.

---

## Related Documents

### Previous Domain Documents

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`

### Business Analysis

* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/12_Debt_and_Payment_Allocation.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`

### Future

* `docs/04_Architecture/`
* `docs/05_Database/`

