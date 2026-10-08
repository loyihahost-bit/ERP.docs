# Debt and Payment Allocation

**Document ID:** SA-12
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for customer debt, debt customers, debt Orders, debt repayments, repayment allocation, customer balances, partial repayment, and offline debt operations.

The objective is to maintain an accurate and traceable relationship between customers, debt Orders, repayments, and outstanding balances without changing historical Order information.

---

## 2. Debt System Scope

The Debt system is responsible for:

* identifying debt customers;
* creating debt-related Orders;
* maintaining customer outstanding balances;
* recording repayments;
* allocating repayments to debt Orders;
* supporting partial repayment;
* supporting multiple debt Orders per customer;
* supporting offline debt repayment;
* preserving debt history;
* resolving debt synchronization conflicts.

The system does not provide a full CRM.

---

## 3. Customer Record

A customer record is required when debt management is used.

One debt customer record represents one customer within the Business.

The customer record may contain:

* Customer UUID;
* name;
* phone number;
* contact information where required;
* current balance;
* status;
* creation metadata;
* update metadata.

Customer data is Business-scoped.

---

## 4. Customer Identity

Customer UUID is the stable system identity.

Phone number is not the primary identity.

Therefore, duplicate phone numbers are allowed.

Example:

```text id="n6p2c8"
Customer A
Phone: +998 XX XXX XX XX

Customer B
Phone: +998 XX XXX XX XX
```

These remain two separate customer records if the Business creates them separately.

---

## 5. Historical Customer Information

Historical Orders must preserve the customer information relevant to the original transaction.

Later changes to the customer record must not silently rewrite historical Order information.

For example:

```text id="r4m8v1"
Historical Order
Name: Original Name
Phone: Original Phone

Current Customer Record
Name: Updated Name
Phone: Updated Phone
```

Both historical and current contexts remain traceable.

---

## 6. Customer and Business Isolation

A Customer belongs to exactly one Business.

A Customer from Business A cannot be used for a debt operation in Business B.

The system must validate Business context for every debt operation.

---

## 7. Customer and Branch Context

The Customer is Business-scoped, while debt transactions are operationally associated with the relevant Branch.

A customer may have debt Orders from multiple Branches of the same Business.

Branch permissions determine which employees can view or operate those records.

---

## 8. Debt Order

A Debt Order is an Order whose payable amount is recorded as customer debt.

The Order remains a normal Order with its own:

* Order UUID;
* lifecycle;
* Branch;
* employee context;
* pricing;
* inventory transaction;
* payment history.

Debt is a financial relationship, not a replacement for the Order identity.

---

## 9. Creating Debt

A debt transaction requires:

* valid Order;
* valid Customer;
* employee authorization;
* Business context;
* Branch context;
* payment permission;
* valid debt operation.

The debt amount is derived from the relevant unpaid amount according to the payment operation.

---

## 10. Debt Payment Method

`Debt` is one of the supported payment methods.

A Debt payment indicates that the customer is not immediately settling the relevant amount through Cash or Card.

The debt amount becomes part of the customer's outstanding balance.

---

## 11. Debt Balance

The customer's outstanding balance represents the amount still owed.

Conceptually:

```text id="c7x3m9"
Outstanding Balance
=
Total Debt
−
Allocated Repayments
```

The system must calculate the balance from authoritative debt transactions.

The balance must not become negative because of normal repayment allocation.

---

## 12. Multiple Debt Orders

One customer may have multiple debt Orders.

Example:

```text id="p8v4k2"
Customer A

Debt Order 1 → 50,000
Debt Order 2 → 80,000
Debt Order 3 → 30,000

Total Outstanding → 160,000
```

Each Order remains individually traceable.

---

## 13. Debt Order Balance

Each debt Order has its own outstanding amount.

Example:

```text id="h5n7r3"
Order 1
Original Debt: 100,000
Repaid:         40,000
Remaining:      60,000
```

A debt Order may be partially repaid.

---

## 14. Partial Repayment

Partial repayment is supported.

A customer does not need to pay the full outstanding balance at once.

Example:

```text id="q2m8w5"
Customer Balance: 200,000
Repayment:         70,000
Remaining:        130,000
```

The repayment is recorded without closing unrelated debt balances.

---

## 15. Repayment Identity

Every repayment operation must have a unique transaction UUID.

The repayment identity must remain stable across:

* retries;
* offline storage;
* synchronization;
* conflict handling.

The system must not create duplicate repayments for the same transaction UUID.

---

## 16. Repayment Payment Methods

A debt repayment may use supported settlement methods such as:

* Cash;
* Card.

If additional methods are introduced later, they must follow the same financial and audit rules.

Cash repayment affects the relevant Cash Session.

Card repayment remains separate from physical cash.

---

## 17. Repayment Context

A repayment should preserve:

* Repayment UUID;
* Customer UUID;
* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Cash Session UUID where applicable;
* payment method;
* amount;
* timestamp;
* source;
* status.

This context supports audit and reporting.

---

## 18. Repayment Validation

Before recording a repayment, the system validates:

1. Customer exists.
2. Customer belongs to the Business.
3. Employee is active.
4. Employee has repayment permission.
5. Branch scope is valid.
6. Subscription entitlement allows the operation.
7. Repayment amount is valid.
8. Customer has an applicable outstanding balance.
9. Cash Session is valid for Cash repayment.
10. Device authorization is valid where applicable.

Invalid repayments are rejected.

---

## 19. Repayment Allocation

A repayment must be allocated to one or more debt Orders.

Allocation identifies how the repayment reduces individual Order balances.

Example:

```text id="x6c1p8"
Repayment: 100,000

Debt Order A → 60,000
Debt Order B → 40,000
```

Customer balance decreases by 100,000.

---

## 20. Allocation Must Not Exceed Debt

The system must not allocate more than the outstanding amount of the selected debt Orders.

If the requested allocation exceeds available debt:

* the operation is rejected; or
* an explicitly supported business overpayment workflow must be used.

The system must not silently create negative debt balances.

---

## 21. Allocation Strategy

The system may support controlled allocation strategies such as:

* employee-selected Orders;
* oldest debt first;
* explicit customer-selected Orders.

The selected strategy must be deterministic and auditable.

The default strategy may be configurable later without changing the underlying financial model.

---

## 22. Manual Allocation

An authorized employee may select which debt Orders receive a repayment.

The system must show:

* selected debt Orders;
* current outstanding balance;
* allocated amount;
* remaining repayment amount.

The final allocation must be validated server-side.

---

## 23. Automatic Allocation

If automatic allocation is enabled, the system applies the defined allocation strategy.

For example:

```text id="b9v4m2"
Oldest Debt First

Order A → 50,000
Order B → 30,000
Order C → 20,000
```

The strategy must not cause an allocation above any Order's outstanding amount.

---

## 24. Multiple Branch Debt

A customer may have debt from multiple Branches of the same Business.

Example:

```text id="k5r8c3"
Customer A

Branch 1:
  Order A → 50,000

Branch 2:
  Order B → 70,000

Business Total:
  120,000
```

Access to each Branch's debt records remains permission-controlled.

---

## 25. Cross-Branch Repayment

A repayment performed in one Branch may be allocated to debt from another Branch of the same Business only when the employee has the required Business-level and Branch-level authority.

The system must not permit cross-Branch debt access merely because the employee can accept cash.

All cross-Branch allocation must be auditable.

---

## 26. Cash Repayment

A Cash debt repayment must be associated with the active Cash Session.

The repayment contributes to physical cash.

The Cash Session report must be able to identify debt repayments separately from ordinary sales payments.

---

## 27. Card Repayment

Card debt repayment is recorded separately from physical cash.

The system must preserve the Card repayment amount and transaction context.

External processor authorization is outside the current ERP scope unless separately integrated.

---

## 28. Repayment and Cash Session Closure

A Cash debt repayment cannot normally be recorded against a closed Cash Session.

If the repayment occurs during Cash Session transition, the system follows the same transition rules as ordinary Cash payments.

The system must not assign the repayment to the wrong Cash Session.

---

## 29. Debt and Order Payment State

A Debt Order remains financially outstanding until its debt balance reaches zero.

Partial repayments do not mark the Order fully settled.

Example:

```text id="w3m7n5"
Debt Order
Original: 100,000
Repaid:    70,000
Remaining: 30,000
Status: Outstanding
```

---

## 30. Fully Repaid Debt Order

When the debt balance reaches zero:

* the debt amount becomes fully settled;
* the Order remains historically preserved;
* repayment history remains available;
* the Order is not deleted;
* customer balance decreases accordingly.

The operational Order lifecycle is not rewritten merely because the debt is repaid.

---

## 31. Customer Balance Update

Customer balance changes must be atomic with repayment allocation.

The system must not commit:

* repayment without allocation;
* allocation without corresponding repayment;
* balance update without the underlying financial records.

All relevant financial effects must succeed or roll back together.

---

## 32. Concurrent Repayment

The system must safely handle concurrent repayments against the same customer or debt Order.

Example:

```text id="d8p4v6"
Repayment A → 80,000
Repayment B → 80,000

Available Debt → 100,000
```

The system must prevent both operations from incorrectly consuming the same debt balance.

The server must use appropriate transaction isolation, locking, or version checks.

---

## 33. Concurrent Allocation

Two repayments must not allocate the same debt amount twice.

The system validates current outstanding balances within the same transaction that applies the allocation.

Stale client balances cannot be trusted for final allocation.

---

## 34. Repayment Correction

A completed repayment must not be silently overwritten.

If a correction is required:

* the original repayment remains immutable;
* a separate correction operation is created;
* the correction references the original repayment;
* actor, time and reason are recorded;
* relevant customer and debt balances are recalculated through controlled logic.

---

## 35. Repayment Refund/Reverse

If a repayment needs to be reversed, the reversal is a separate financial operation.

The original repayment remains part of history.

The reversal must:

* reference the original repayment;
* preserve the original amount;
* record the reversed amount;
* record actor;
* record reason;
* update applicable debt balances atomically.

---

## 36. Debt History

The system must preserve:

* Customer creation;
* Debt Orders;
* debt amounts;
* repayments;
* allocations;
* corrections;
* reversals;
* timestamps;
* employees;
* Branches;
* Cash Sessions;
* Devices where applicable.

Historical records must not be silently deleted or rewritten.

---

## 37. Historical Order Customer Data

Changing a Customer record must not rewrite historical Order customer information.

This is required for historical integrity and reporting.

The system may show the current Customer relationship together with the original Order snapshot where appropriate.

---

## 38. Offline Debt Repayment

Trusted devices may record debt repayments while offline if:

* employee is authorized;
* device is trusted;
* offline authorization is valid;
* Business/Branch scope is valid;
* subscription entitlement permits the operation.

The repayment remains locally stored until synchronization.

---

## 39. Offline Repayment Validation

Offline devices use the latest valid local debt state.

However, local state is not authoritative after reconnection.

The server validates:

* Customer UUID;
* Repayment UUID;
* Business;
* Branch;
* Employee;
* Device;
* payment method;
* amount;
* debt balance;
* allocation;
* Cash Session;
* subscription;
* transaction dependencies.

---

## 40. Offline Repayment Conflict

A conflict may occur when:

```text id="s6n2c9"
Offline Device:
Repay 100,000

Server:
Customer debt already reduced
```

The system must not silently apply the repayment twice.

The result becomes a synchronization conflict.

Authorized users resolve the conflict through a separate resolution event.

---

## 41. Conflict Resolution

Debt conflicts must preserve:

* original offline event;
* server state;
* conflict reason;
* resolution decision;
* resolving employee;
* resolution timestamp;
* resulting state.

The original conflict event must remain immutable.

---

## 42. Repayment Idempotency

If the same Repayment UUID is received repeatedly:

* no duplicate repayment is created;
* no duplicate allocation occurs;
* no duplicate cash effect occurs;
* the previously recorded result is returned or reused.

This applies to online retries and offline synchronization.

---

## 43. Debt Synchronization Ordering

Debt repayment synchronization may depend on:

* Customer synchronization;
* original Debt Order;
* previous repayment;
* Cash Session;
* Employee;
* Branch;
* Business context.

Dependent events must wait for required prerequisites.

---

## 44. Debt Reporting

Reports must be able to show:

* customer outstanding balance;
* debt Orders;
* original debt amounts;
* repayments;
* remaining debt;
* repayment allocations;
* repayment methods;
* Branch;
* Cash Session;
* employee;
* corrections;
* reversals;
* unresolved conflicts.

Access is permission-controlled.

---

## 45. Debt Notifications

The system may generate notifications for relevant debt events, such as:

* significant outstanding debt;
* unresolved debt conflict;
* repayment discrepancy;
* failed debt synchronization.

Notification failure must not roll back a committed repayment.

---

## 46. Subscription and Entitlement

Debt operations are subject to:

* Business subscription;
* Employee Status;
* Role Permission;
* Employee Override;
* Branch Scope;
* Device/Offline Authorization.

If the subscription becomes read-only:

* new debt operations are blocked;
* existing debt history remains viewable where permitted;
* allowed Excel export remains available;
* offline authorization cannot bypass the restriction.

---

## 47. Security and Access

Debt information may contain sensitive business and customer information.

Access must be restricted by:

* Business;
* Branch;
* Employee permissions;
* subscription entitlement;
* device authorization where applicable.

A trusted device alone does not grant access to debt records.

---

## 48. Debt Audit

Important debt operations must be audited.

Examples include:

* Debt Order creation;
* repayment;
* repayment allocation;
* repayment correction;
* repayment reversal;
* cross-Branch allocation;
* conflict resolution;
* relevant customer changes.

Audit context should include:

* Event UUID;
* Customer UUID;
* Order UUID;
* Repayment UUID;
* Business UUID;
* Branch UUID;
* Employee/System actor;
* Device UUID;
* Cash Session UUID where applicable;
* timestamp;
* old state;
* new state;
* reason;
* source;
* result.

---

## 49. Debt and Reports Versioning

If a debt correction or repayment changes relevant report metrics:

* a new report version is created;
* the previous report remains immutable;
* the correction or repayment is linked to the relevant version.

No unnecessary report version is created when relevant report metrics do not change.

---

## 50. Performance

Debt operations are part of normal business operations and must remain responsive.

The system should avoid:

* scanning the entire customer history for every repayment;
* blocking POS on report generation;
* synchronous notification delivery;
* unnecessary remote calls.

Large historical reports and exports should run in the background.

---

## 51. Error Handling

Debt errors must be classified as:

* Validation Error;
* Authorization Error;
* Conflict;
* Business Rule Violation;
* Temporary Infrastructure Error;
* Permanent Failure.

The user receives a business-safe message.

Technical details remain in structured logs.

Retryable operations must use idempotency.

---

## 52. Core Transaction Boundary

The following operations must be atomic where they form one financial state change:

* repayment creation;
* repayment allocation;
* debt balance update;
* Cash Session financial effect where applicable.

If the transaction fails, all related core changes roll back.

---

## 53. Secondary Operations

After a successful debt transaction, secondary processing may include:

* notifications;
* report updates;
* background calculations;
* audit delivery through reliable mechanisms;
* synchronization bookkeeping.

Secondary failures must not roll back a committed debt transaction.

---

## 54. System Invariants

The following invariants apply to Debt and Payment Allocation:

1. Every Customer has a unique Customer UUID within the Business.
2. Phone number is not the primary Customer identity.
3. Duplicate phone numbers are allowed.
4. Customer records are Business-scoped.
5. A Customer cannot be used across different Businesses.
6. A customer may have multiple debt Orders.
7. Each debt Order retains its own Order UUID.
8. Debt does not replace Order identity.
9. Debt balances are calculated from authoritative financial records.
10. Customer outstanding balance cannot become negative through normal allocation.
11. Debt Orders may be partially repaid.
12. One repayment may be allocated to multiple debt Orders.
13. One debt Order may receive multiple repayments.
14. Repayment allocation cannot exceed outstanding debt.
15. Repayment UUID provides idempotency.
16. Duplicate repayment requests do not create duplicate financial effects.
17. Cash repayments affect the relevant Cash Session.
18. Card repayments do not affect physical cash.
19. Cash repayment cannot normally use a closed Cash Session.
20. Customer balance and repayment allocation update atomically.
21. Concurrent repayments cannot consume the same debt balance twice.
22. Concurrent allocation validates authoritative current debt state.
23. Completed repayments remain historically preserved.
24. Repayment correction is a separate financial operation.
25. Repayment reversal is a separate financial operation.
26. Original repayment records remain immutable.
27. Historical Order customer information is not silently rewritten.
28. Customer record changes do not alter historical financial records.
29. Offline debt repayment requires trusted-device authorization.
30. Offline repayment is server-revalidated during synchronization.
31. Offline debt conflicts are explicit.
32. Conflict resolution is recorded as a separate event.
33. Server state is authoritative after synchronization.
34. Debt synchronization respects event dependencies.
35. Cross-Branch repayment requires explicit authority.
36. Branch access does not automatically grant Business-wide debt access.
37. Debt operations respect subscription entitlement.
38. Debt operations respect employee status and permissions.
39. Trusted Device status alone does not grant debt permission.
40. Important debt operations are auditable.
41. Debt history is not silently deleted or overwritten.
42. Debt corrections may create new report versions when relevant metrics change.
43. Secondary notification/report processing does not roll back committed debt transactions.
44. Core repayment and allocation effects are atomic.
45. Technical debt diagnostics remain in structured logs.
46. Historical customer, debt, repayment and allocation relationships remain traceable.

---

## 55. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/11_Payment_System.md`
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

## 56. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `12_Debt_and_Payment_Allocation.md`

**Next Document:** `13_Discounts_Refunds_and_Corrections.md`

