# Payments, Discounts and Refunds

**Document ID:** FF-BA-014
**Status:** Accepted
**Version:** 2.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for:

* payment methods;
* payment recording;
* mixed payments;
* debt payments;
* discounts;
* refunds;
* payment corrections;
* payment and cash-session relationships;
* offline payment operations;
* financial auditability.

Payment operations must remain traceable, permission-controlled, tenant-isolated, and consistent with the established POS, cash-session, inventory, and audit models.

---

## 2. Payment Model

A payment represents a financial settlement or financial obligation associated with an order.

The current system supports:

* Cash;
* Card;
* Debt;
* Mixed payment.

Payment records are separate financial records associated with the relevant order.

A payment must not be implemented by changing or deleting the original order amount.

Historical payment information must remain available after:

* order correction;
* order cancellation;
* refund;
* cash-session closure;
* later price or menu changes.

Payment state and order lifecycle state are related but are not the same concept.

---

## 3. Supported Payment Methods

### 3.1. Cash

Cash represents physical money received by the branch.

Cash payments affect the applicable cash session and contribute to expected physical cash.

### 3.2. Card

Card represents payment recorded through a card-based payment process.

Card amounts are not treated as physical cash during cash counting.

### 3.3. Debt

Debt represents an unpaid customer obligation recorded against an identified debt customer.

Debt is supported as an order payment method without requiring a full accounts-receivable subsystem.

### 3.4. Mixed

Mixed payment allows one order to be settled using more than one supported payment method.

For example:

```text
Order Total
   ↓
Cash portion
   +
Card portion
   +
Debt portion
```

The sum of all payment portions must satisfy the applicable order settlement rules.

---

## 4. Payment Identity

Every payment operation must have a unique payment identity.

The payment identity must remain stable during:

* offline operation;
* synchronization;
* retry;
* correction;
* reporting.

The system uses UUID-based identity and idempotency.

A retry of the same operation must not create a second financial effect.

A separate later payment is a new payment operation and must have its own identity.

---

## 5. Payment Context

Each payment must preserve the operational context applicable when it was created.

Relevant context includes:

* Business;
* Branch;
* Order;
* Employee;
* Device;
* Cash Register where applicable;
* Cash Session where applicable;
* Payment Method;
* Payment Amount;
* Timestamp;
* Payment Status.

The exact context depends on the payment method and operational flow.

---

## 6. Payment and Order

Payment is associated with an order but is not itself the order lifecycle.

The order lifecycle remains defined by:

`08_POS_and_Order_Management.md`

Payment processing must respect the applicable order state and permissions.

The system must prevent financially invalid operations, including:

* payment against an unrelated order;
* payment against another business;
* payment against an unauthorized branch;
* duplicate payment effect;
* invalid payment amount;
* unauthorized negative payment.

A payment must not silently modify the historical order configuration.

---

## 7. Order Amount and Payment Amount

The amount requiring settlement is determined from the order's recorded transaction state.

Relevant components may include:

* product selling prices;
* branch price overrides;
* unit-level modifications;
* extras;
* removals;
* custom pricing/markup where applicable;
* discounts;
* other explicitly supported order-level adjustments.

The final payable amount must be stored with the transaction.

Later changes to:

* menu prices;
* recipes;
* branch price overrides;
* discount configuration;
* inventory cost;

must not recalculate historical payments.

---

## 8. Historical Price and Payment Snapshot

Payment history must use the values applicable when the order/payment was processed.

The system must preserve enough transaction information to determine:

* original item price;
* applicable modifications;
* discount;
* final order amount;
* payment amount;
* payment method.

Historical transactions must not depend on current menu configuration for financial reporting.

---

## 9. Cash Payments

For a cash payment, the system records the physical cash amount received.

Cash payment information contributes to the expected cash calculation of the applicable cash session.

The cash payment remains associated with:

* Branch;
* Cash Register;
* Cash Session;
* Cashier/Employee;
* Order.

The payment must not be silently moved to another cash session.

---

## 10. Card Payments

Card payments are recorded separately from cash payments.

Card payments:

* contribute to card payment totals;
* do not increase physical cash;
* remain associated with the applicable order and session context;
* are included in payment reports.

At cash-session closing, the cashier does not manually enter the card total.

The system derives the card total from recorded payment transactions.

---

## 11. Debt Payments

Debt is a supported payment method.

A debt customer has one customer record within the applicable business.

The same customer may have multiple debt orders.

Debt supports:

* multiple debt orders;
* partial repayment;
* remaining balance;
* payment history.

A customer may have duplicate phone numbers with another customer. Phone number uniqueness is not a required identity rule.

Historical orders must retain the customer information applicable to the original transaction.

Debt functionality does not imply a full CRM or accounts-receivable system.

---

## 12. Debt Customer Information

A debt customer record may contain the information required for debt tracking, including:

* customer name;
* phone number;
* debt history;
* repayment history;
* current outstanding balance.

The customer record must remain associated with the relevant business.

Cross-business customer access is prohibited.

---

## 13. Partial Debt Repayment

Debt may be repaid partially.

A repayment must:

* reference the relevant debt obligation;
* have its own transaction identity;
* record the amount;
* record the payment method;
* record the responsible employee;
* preserve timestamp and operational context.

A partial repayment must not silently rewrite the original debt order.

The remaining balance must remain traceable.

---

## 14. Mixed Payments

Mixed payment allows an order to contain multiple payment portions.

Example:

```text
Order Total = 100,000

Cash = 40,000
Card = 30,000
Debt = 30,000
```

Each portion must be recorded separately while remaining associated with the same order settlement.

The system must validate that the payment portions satisfy the applicable settlement rules.

Mixed payments must remain distinguishable in:

* cash reports;
* card reports;
* debt reports;
* order history;
* audit history.

Only the cash portion contributes to physical cash reconciliation.

---

## 15. Duplicate Payment Protection

A single payment operation must never create multiple financial effects because of:

* repeated button presses;
* application retries;
* network interruptions;
* offline synchronization;
* reconnect operations.

UUID-based idempotency must be applied to payment operations.

Server-side validation remains authoritative after synchronization.

---

## 16. Payment Validation

The system must validate:

* Business ownership;
* Branch scope;
* Order identity;
* Employee authorization;
* Payment method;
* Payment amount;
* Cash-session relationship where applicable;
* Duplicate-operation protection.

The system must reject invalid states such as:

* payment for another business;
* payment for an unauthorized branch;
* duplicate payment;
* invalid negative payment;
* payment exceeding the allowed settlement amount;
* payment without a valid transaction context.

---

## 17. Offline Payments

Authorized trusted devices may record supported payments while offline.

Offline payment operations must preserve:

* Business identity;
* Branch identity;
* Order UUID;
* Payment UUID;
* Employee identity;
* Device identity;
* Cash Session identity where applicable;
* Payment Method;
* Payment Amount;
* Timestamp;
* Offline authorization context.

The operation must be stored securely on the trusted device.

When connectivity returns, the operation is synchronized with the central system.

---

## 18. Offline Payment Validation

Offline operation does not bypass:

* employee permissions;
* branch scope;
* subscription entitlement;
* cash-session rules;
* duplicate-payment protection;
* order-state rules.

The server must revalidate synchronized financial operations.

If a synchronization conflict is detected, the system must not silently create a duplicate financial effect.

---

## 19. Offline Card Payments

The ERP may record card-payment information offline only where the established POS process permits it.

The ERP must not assume that an external card processor can authorize a card transaction while the branch has no connectivity.

The system must distinguish between:

1. ERP payment recording;
2. external card authorization.

External payment-processor availability and settlement remain outside the current business-analysis scope.

---

## 20. Payment Corrections

Completed payments must not simply be overwritten.

A correction must preserve:

* original payment;
* correction operation;
* actor;
* reason;
* timestamp;
* resulting state.

Where a financial correction requires a reversal or refund, the original payment remains in history and the new operation references it.

---

# Discounts

## 21. Discount Model

Discounts affect the final transaction amount.

A discount does not modify:

* global product price;
* branch price override;
* historical product price.

The conceptual calculation is:

```text
Product / Order Price
        ↓
Supported Modifications
        ↓
Discount
        ↓
Final Payable Amount
```

---

## 22. Discount Scope

The current system supports discounts as part of order processing.

Discounts may apply according to the configured business rules to:

* an order;
* a supported order component.

The exact supported discount mechanism is permission-controlled.

A complex promotion engine is outside the current scope.

---

## 23. Discount Permissions

Discount functionality is permission-controlled.

An employee who can create or process orders does not automatically receive unrestricted discount authority.

The permission model follows:

`Role Permission + Employee Override + Branch Scope + Subscription Entitlement`

A Manager may apply discounts only when the required permission is available.

Cashier discount authority is also determined by explicit permission.

---

## 24. Discount History

A discount operation must preserve:

* Order;
* Business;
* Branch;
* Employee;
* Discount amount or applicable configuration;
* Timestamp;
* Reason/comment where required.

A later configuration change must not alter the historical discount.

---

## 25. Discount and Historical Orders

Changing:

* discount permissions;
* discount rules;
* product prices;
* branch prices;

must not modify historical orders.

Historical reports must use recorded transaction values.

---

# Refunds

## 26. Refund Model

A refund is a separate financial operation associated with a previously processed payment/order.

A refund must never be implemented by:

* deleting the original payment;
* silently changing the original payment amount;
* deleting the original order.

The original transaction remains available.

The refund references the original financial context.

---

## 27. Refund Permissions

Refunds are restricted to employees with the required refund permission.

Refund authority is independent from ordinary payment authority.

A cashier cannot perform a refund merely because the cashier can accept payments.

Refund permission is controlled through the established role and employee permission model.

---

## 28. Refund Approval

Refund approval is permission-driven.

Where an approval requirement exists, the system must enforce it.

Approval cannot be bypassed through:

* offline mode;
* another device;
* another interface;
* synchronization manipulation.

The exact authorization structure is defined by the permission configuration rather than by a permanently hard-coded role.

---

## 29. Refund Reason

Every refund requires a mandatory reason.

The refund cannot be completed without the reason.

The reason must remain permanently associated with the refund record.

---

## 30. Refund Types

The current system supports:

* full refund;
* partial refund;
* item-level refund;
* quantity-level refund.

A partial refund may apply only to the eligible part of the original transaction.

The system must prevent refund amounts or quantities that exceed the refundable transaction state.

---

## 31. Refund Payment Methods

Refunds currently support:

* Cash;
* Card.

The original payment method must remain visible in the refund history.

A card refund must not be silently represented as a cash refund.

A mixed original payment may require the refund operation to explicitly identify the applicable refundable payment portion.

---

## 32. Refund and Inventory

Creating a refund does **not** automatically return inventory.

The current business rule is:

> Financial refund and inventory return are separate operations.

Therefore:

```text
Refund
  ≠
Inventory Return
```

Inventory must not increase merely because a refund was created.

This is consistent with the established POS cancellation/inventory rules.

Served items are not returned to inventory.

Where a permitted cancellation process returns eligible non-served inventory, that inventory operation is handled separately from the financial refund.

---

## 33. Refund and Cash

A cash refund affects the physical cash position of the applicable branch.

The cash movement must remain associated with:

* original payment;
* refund;
* branch;
* applicable cash session;
* responsible employee.

The refund must be included in the applicable cash-session calculations.

---

## 34. Refund and Card

A card refund remains distinguishable from a cash refund.

The system preserves:

* original payment method;
* original payment;
* refund amount;
* refund reason;
* responsible employee;
* timestamp.

External card-processor execution remains outside the current business-analysis scope.

---

## 35. Large Refund Alert

Large refunds are one of the defined business alert categories.

When the configured large-refund condition is reached, the system generates an alert for authorized recipients.

The alert must respect:

* Business scope;
* Branch scope;
* notification permissions.

The monetary threshold is configurable and is not hard-coded in this document.

---

## 36. Refund History

Every refund must preserve:

* Original Order;
* Original Payment;
* Refund UUID;
* Refund Amount;
* Payment Method;
* Reason;
* Employee;
* Branch;
* Cash Session where applicable;
* Timestamp;
* Approval information where applicable.

Refund history must remain available for:

* reports;
* audit;
* financial reconciliation;
* business review.

---

# Cancellation, Payment and Order State

## 37. Order Cancellation vs Refund

Order cancellation and refund are different operations.

### Cancellation

Cancellation changes the operational state of an order or order item.

### Refund

Refund reverses or returns a financial amount associated with a processed payment.

Therefore:

```text
Cancellation ≠ Refund
```

Cancellation does not automatically create a refund.

Refund does not automatically cancel or delete the original order.

---

## 38. Payment and Order Lifecycle

The order lifecycle is defined in:

`08_POS_and_Order_Management.md`

Payment is a separate financial state.

The system must support the distinction between:

* order preparation state;
* service/fulfillment state;
* payment state.

The system must not introduce an artificial requirement that every operational order state be identical to a payment state.

---

## 39. Payment and Cash Session

A payment processed through a branch POS is associated with the cash session active at the time of payment.

The relationship is immutable for historical purposes.

A payment must not be silently moved from one cash session to another after a cashier transition.

---

## 40. Cashier Handover

Cashier handover creates a new cash session.

Therefore, the following rule applies:

```text
Previous Cashier
      ↓
Previous Cash Session closes
      ↓
New Cashier authenticates
      ↓
New Cash Session opens
```

Payments processed **before** the transition belong to the previous cash session.

Payments processed **after** the transition belong to the new cash session.

The physical cash register identity remains the same.

The cash session UUID changes.

Detailed rules are defined in:

`10_Shift_Handover.md`

---

## 41. Open Orders During Handover

Open orders remain active during cashier transition.

The new cashier may continue them according to their permissions.

The order UUID does not change.

Historical actions remain associated with their original:

* employee;
* device;
* cash session.

New actions are associated with the new cashier and new cash session.

Payments before and after the transition retain their respective session context.

---

# Cash Reconciliation

## 42. Cash Session Closing

Cash-session reconciliation is based on recorded payment transactions.

The system calculates:

* cash received;
* card received;
* debt payments where applicable;
* mixed-payment cash portion;
* refunds;
* applicable cash adjustments;
* expected physical cash.

The cashier manually enters the physical cash amount.

The expected amount remains hidden until the physical cash amount is entered, according to the cash-session rules.

---

## 43. Physical Cash

Only physical cash is counted by the cashier.

The cashier does not manually enter:

* card total;
* debt total;
* total sales;
* system-calculated expected cash.

The system derives these values from transaction history.

Detailed reconciliation rules are defined in:

`09_Cash_Register_and_Cash_Sessions.md`

---

## 44. Cash Discrepancy

The system determines the discrepancy between:

* expected cash;
* physical cash entered by the cashier.

Possible results are:

* no difference;
* shortage;
* overage.

The discrepancy remains permanently associated with the relevant cash session.

Recount and explanation requirements follow the cash-session rules.

---

# Reporting and Audit

## 45. Payment Reports

Payment data contributes to business reports, including:

* total sales;
* cash payments;
* card payments;
* debt;
* mixed payments;
* discounts;
* refunds;
* net financial amounts;
* cash discrepancies;
* cashier activity.

Historical reports must use recorded transaction values.

Current menu or price configuration must not recalculate historical payment reports.

---

## 46. Financial Auditability

Important financial operations must be traceable.

The system must preserve, where applicable:

* actor;
* order;
* payment;
* refund;
* discount;
* branch;
* cash session;
* device;
* previous state;
* new state;
* amount;
* payment method;
* reason;
* timestamp.

Financial history must not be silently overwritten.

---

## 47. Historical Integrity

The following records must remain historically stable:

* original payment;
* original order amount;
* applied discount;
* refund;
* refund reason;
* payment method;
* cash session relationship;
* responsible employee.

Later configuration changes must not rewrite these historical records.

---

# Permissions, Subscription and Isolation

## 48. Permission and Subscription Controls

Financial functionality is controlled by two independent layers:

1. Subscription Entitlement;
2. Employee Permission.

A protected operation requires both.

Trusted device status does not grant financial permission.

Offline authorization does not bypass:

* subscription restrictions;
* employee permissions;
* branch scope.

---

## 49. Business and Branch Isolation

Payment, discount, debt, and refund records must be isolated by Business.

Branch operations must remain within the authorized Branch Scope.

An employee must not be able to:

* apply payment to another business;
* refund another business's order;
* access unauthorized branch financial data;
* manipulate another branch's cash session.

Isolation applies to:

* online operations;
* offline operations;
* synchronization;
* reports;
* exports;
* background processing.

---

# Performance and Reliability

## 50. POS Performance

Payment operations are part of the POS critical path.

The system must remain responsive during:

* payment confirmation;
* cash payment;
* card payment recording;
* debt recording;
* mixed payment;
* discount application;
* refund initiation;
* order financial closure.

Security, audit, and idempotency mechanisms must not introduce unnecessary POS delays.

---

## 51. Atomic Financial Effects

Operations that create a financial effect must be processed consistently.

The system must prevent partial application such as:

* payment recorded twice;
* order closed without the required payment;
* cash effect created without the payment record;
* duplicate refund;
* duplicate debt repayment.

Offline synchronization must preserve the same business rules as online processing.

---

# 52. Business Rules Summary

| Area                 | Rule                                                       |
| -------------------- | ---------------------------------------------------------- |
| Payment methods      | Cash, Card, Debt, Mixed                                    |
| Cash                 | Contributes to physical cash reconciliation                |
| Card                 | Separate from physical cash                                |
| Debt                 | Supported with customer-level debt tracking                |
| Mixed payment        | Multiple payment portions for one order                    |
| Payment identity     | Unique UUID-based transaction identity                     |
| Duplicate payment    | Must be prevented                                          |
| Historical payment   | Must be preserved                                          |
| Offline payment      | Supported on authorized trusted devices                    |
| Payment validation   | Business, branch, order, permission and idempotency checks |
| Discount             | Affects transaction amount, not base product price         |
| Discount permission  | Explicit permission required                               |
| Refund               | Separate financial operation                               |
| Refund types         | Full, partial, item-level, quantity-level                  |
| Refund methods       | Cash and Card                                              |
| Refund permission    | Explicit permission required                               |
| Refund reason        | Mandatory                                                  |
| Refund approval      | Permission-driven where required                           |
| Refund history       | Preserved                                                  |
| Refund and inventory | Not automatically linked                                   |
| Served inventory     | Never returned through refund                              |
| Large refund         | Alert supported                                            |
| Cancellation         | Separate from refund                                       |
| Cash session         | Payment belongs to active session at processing time       |
| Handover             | New cashier opens a new cash session                       |
| Historical session   | Payment is never silently moved between sessions           |
| Debt repayment       | Partial repayment supported                                |
| Cash discrepancy     | Expected vs physical cash                                  |
| Audit                | Financial operations preserved                             |
| Subscription         | Independent from employee permission                       |
| Branch isolation     | Required                                                   |
| POS performance      | Financial consistency without unnecessary delay            |

---

# 53. Business Boundaries

The current Payments, Discounts and Refunds scope does **not** define:

* external payment gateway implementation;
* bank API integration;
* card-terminal hardware integration;
* automatic card settlement reconciliation;
* installment payment systems;
* loyalty points;
* complex promotion engines;
* customer wallets;
* full accounts-receivable management;
* multi-currency payments;
* tax calculation engine;
* automated physical inventory return caused by refunds.

These capabilities may be considered in future documentation if business requirements justify them.

---

## 54. Related Documents

* `01_Product_Overview.md`
* `03_Subscription_and_Tariffs.md`
* `05_Users_Roles_and_Permissions.md`
* `06_Authentication_and_Trusted_Devices.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `10_Shift_Handover.md`
* `11_Inventory_and_Warehouse.md`
* `13_Menu_and_Pricing.md`
* `16_Reports_and_Dashboards.md`
* `17_Notifications_and_Alerts.md`
* `18_Audit_and_Change_History.md`
* `20_Business_Rules.md`

