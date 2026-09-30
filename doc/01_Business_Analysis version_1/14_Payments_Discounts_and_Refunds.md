# Payments, Discounts and Refunds

**Document ID:** FF-BA-014
**Status:** Draft
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for payments, payment methods, discounts, refunds, payment-related order states, and their relationship with cash sessions.

The system must ensure that payment operations are:

* traceable;
* consistent with order state;
* protected by permissions;
* compatible with offline operation;
* correctly reflected in cash and business reports.

---

## 2. Payment Model

A payment represents the settlement of an order.

An order may be considered financially completed only after the required payment operation has been successfully recorded.

The payment must remain associated with its order.

Payment history must not be silently removed when an order is later corrected or refunded.

---

## 3. Supported Payment Methods

The current system supports:

* **Cash**
* **Card**

The system should be designed so that additional payment methods can be introduced later without changing the fundamental order model.

The current business scope does not require a large payment-method ecosystem.

---

## 4. Cash Payment

For a cash payment, the system records the amount paid through cash.

Cash payments affect the relevant cash session.

The system must preserve:

* order;
* cash session;
* branch;
* cashier;
* payment amount;
* payment time;
* payment status.

Cash payment information contributes to expected cash calculations for the relevant cash session.

---

## 5. Card Payment

Card payments are recorded separately from cash payments.

Card payment amounts must not be treated as physical cash during cash counting.

At cash session closing:

* card totals are calculated by the system;
* the cashier does not manually enter the card total;
* physical cash is counted separately.

This distinction is required for accurate cash reconciliation.

---

## 6. Payment and Cash Session

Each payment must be associated with the applicable branch and cash session when the payment is processed through the branch POS.

The cash session provides the operational context for:

* cashier;
* register;
* payment activity;
* cash reconciliation;
* reporting.

A payment must not be silently moved from one cash session to another.

---

## 7. Payment and Order State

Payment status is part of the order lifecycle.

A typical order flow is:

```text id="w0n2pj"
Order Created
      ↓
Order Accepted
      ↓
Order Prepared / Processed
      ↓
Payment Recorded
      ↓
Order Closed
```

The exact operational flow may vary by order type, but the system must maintain a consistent relationship between order state and payment state.

---

## 8. Order Closure

An order becomes financially closed after the required payment has been successfully recorded.

A completed payment must not be silently removed simply because the order is no longer active.

Historical payment information must remain available.

---

## 9. Payment Amount

The payment amount must correspond to the amount required for the order after applicable:

* product pricing;
* recipe-based customization;
* extras;
* discounts.

The final amount must be recorded with the order/payment history.

Historical payments must not be recalculated using later product or menu price changes.

---

## 10. Payment Validation

The system must validate that the payment operation is consistent with the order.

The system must prevent invalid states such as:

* closing an order without required payment;
* recording an unrelated payment;
* applying a payment to a different business or branch;
* creating a duplicate payment effect;
* creating a negative payment without an authorized refund operation.

---

## 11. Duplicate Payment Protection

A single payment operation must not be applied multiple times because of:

* repeated user actions;
* network interruptions;
* offline synchronization;
* application retries.

Each payment operation must have a unique transaction identity.

Synchronization must be idempotent.

---

## 12. Offline Payments

Authorized trusted devices may record supported payments while offline.

Offline payments must preserve:

* order identity;
* payment identity;
* business identity;
* branch identity;
* employee identity;
* device identity;
* cash session identity where applicable;
* payment amount;
* payment method;
* timestamp.

When the device reconnects, the payment must synchronize with the central system without creating duplicate effects.

---

## 13. Offline Cash Payments

Cash payments may be recorded while the authorized branch device is offline.

The offline system must still enforce:

* employee permissions;
* branch scope;
* cash session relationship;
* no-duplicate-payment rules;
* applicable order rules.

Offline operation must not allow the user to bypass established payment controls.

---

## 14. Offline Card Payments

Card payment recording may be supported offline only within the capabilities of the established offline POS model.

The ERP must not assume that an external card-processing network is available when the branch itself is offline.

Where an external card processor requires online connectivity, the card transaction must follow the processor's availability requirements.

The ERP should preserve the distinction between:

* ERP payment recording;
* external card authorization.

---

## 15. Payment Corrections

Payment-related corrections must be controlled.

A completed payment must not simply be overwritten.

If a correction is required, the system should preserve:

* original payment;
* correction action;
* responsible employee;
* reason;
* timestamp;
* resulting state.

The exact correction permissions must be determined by the applicable role and payment/refund permissions.

---

# Discounts

## 16. Discount Model

The system supports discounts as part of order processing.

A discount affects the final amount of the relevant order.

A discount does not modify the underlying product's global or branch price.

Example:

```text id="wq71yr"
Product Price
      ↓
Order
      ↓
Discount
      ↓
Final Amount
```

---

## 17. Discount Scope

A discount may apply to an applicable order or supported order component according to the configured business rules.

The discount must be associated with the transaction where it was applied.

The current system does not require a complex promotion engine.

---

## 18. Discount Permission

Applying discounts is permission-controlled.

Employees who can process orders do not automatically have unrestricted authority to apply discounts.

The Owner may grant or remove discount-related permissions through the permission system.

A Manager may use discount functionality only if the appropriate permission has been granted.

---

## 19. Discount Amount

The system must record the discount applied to the order.

The final order amount must be calculated using:

* applicable product prices;
* supported modifications;
* extras;
* discount;
* other applicable order-level adjustments.

The system must preserve the original values required to understand how the final amount was calculated.

---

## 20. Discount History

Important discount operations must be traceable.

The system should preserve:

* employee;
* order;
* branch;
* discount amount or applicable discount configuration;
* time;
* reason/comment where required.

A later change must not silently remove evidence that a discount was applied.

---

## 21. Discount and Historical Orders

Changing discount permissions or pricing rules must not alter historical orders.

Completed orders retain the discount information applicable when the order was processed.

Historical reports must use the recorded transaction values rather than recalculating them from current configuration.

---

## 22. Refund Model

A refund reverses or returns an amount associated with a previously processed order/payment.

Refunds are separate financial operations and must not be implemented by silently deleting the original payment.

The original order and payment history must remain available.

---

## 23. Refund Permission

Refunds are restricted to employees with the required permission.

A cashier or other employee cannot perform a refund solely because they can process ordinary payments.

The Owner controls refund-related permissions according to the established permission model.

---

## 24. Refund Reason

A refund requires a mandatory reason.

The refund cannot be completed without recording the reason.

The reason must remain part of the refund history.

This provides accountability for financial corrections.

---

## 25. Refund Approval

Where the permission model requires approval, the refund must follow the applicable authorization process.

The system must not allow an employee to bypass required approval through offline operation, device switching, or another interface.

The exact approval structure remains permission-driven rather than being tied to one hard-coded employee role.

---

## 26. Refund Amount

The refund amount must not exceed the amount that can legitimately be refunded from the relevant transaction.

The system must prevent invalid refund amounts.

The refund must reference the original order/payment context.

Partial refunds may be supported where the applicable business rules and implementation permit them.

A refund must never create an unexplained negative financial result.

---

## 27. Refund and Cash

A cash refund affects the cash position of the relevant branch.

The refund must be reflected in the relevant cash-session calculations where applicable.

The system must preserve the relationship between:

* original payment;
* refund;
* cash session;
* cashier;
* branch.

---

## 28. Refund of Card Payments

A card-payment refund must remain distinguishable from a cash refund.

The system must preserve the original payment method.

The ERP must not represent a card refund as a cash movement unless an explicitly authorized business operation requires such a conversion.

External card processor behavior is outside the current business-analysis scope.

---

## 29. Refund and Inventory

A refund does not automatically mean that inventory is returned.

Inventory handling depends on the operational condition of the returned product and the applicable business process.

The system must not automatically increase inventory solely because a financial refund was created unless a defined inventory operation is performed.

---

## 30. Refund Notifications

A large refund is one of the defined business alerts.

When the configured large-refund condition is met, the system must notify the appropriate authorized users.

The alert must respect:

* business scope;
* branch scope;
* notification permissions.

The exact monetary threshold is a configurable business rule and must not be hard-coded into this document.

---

## 31. Refund History

Refund records must preserve:

* original order;
* original payment;
* refund amount;
* payment method;
* reason;
* employee;
* branch;
* cash session where applicable;
* timestamp;
* approval information where applicable.

Refund history must remain available for reporting and auditing.

---

## 32. Order Cancellation vs Refund

Order cancellation and refund are different business concepts.

Cancellation concerns the order lifecycle.

Refund concerns the financial reversal of an already processed payment.

The system must not assume that every cancellation automatically creates a refund.

Similarly, a refund must not automatically erase the original order.

---

## 33. Payment and Cash Session Closing

At cash session closing, the system calculates the expected amounts based on the session's payment activity.

The cashier manually enters only the physical cash amount.

The system displays the relevant expected values after the physical cash amount has been entered.

The payment records remain the source for calculating:

* cash received;
* card received;
* refunds;
* applicable adjustments;
* expected cash.

---

## 34. Payment Discrepancy

A cash discrepancy is determined from the expected cash amount and the physical cash amount entered by the responsible cashier.

Possible outcomes include:

* no difference;
* shortage;
* overage.

The discrepancy must remain associated with the relevant cash session.

The cashier may be required to recount and provide an explanation according to the cash session rules.

Detailed cash reconciliation rules are defined in:

`09_Cash_Register_and_Cash_Sessions.md`

---

## 35. Payment and Shift Handover

During a cashier handover, payment history remains part of the same cash session.

The new cashier does not receive a new cash session merely because responsibility changes.

Open orders transfer to the new cashier while retaining their existing order and payment history.

Detailed handover rules are defined in:

`10_Shift_Handover.md`

---

## 36. Payment and Reports

Payment data contributes to business reports.

Reports may include:

* total sales;
* cash payments;
* card payments;
* discounts;
* refunds;
* net amounts;
* cash discrepancies;
* cashier activity.

Historical reports must use historical transaction values.

Current product prices or current discount settings must not retroactively change historical payment reports.

---

## 37. Auditability

Important payment, discount, and refund operations must be traceable.

The system should preserve:

* actor;
* order;
* payment;
* refund;
* branch;
* cash session;
* previous state where applicable;
* new state;
* amount;
* reason;
* timestamp.

Financial history must not be silently overwritten.

---

## 38. Permissions and Subscription

Payment, discount, and refund functionality is subject to two independent control layers:

1. business subscription entitlement;
2. employee permission.

A user must satisfy both conditions to perform a protected operation.

Trusted devices do not grant financial permissions.

Offline authorization does not bypass subscription or permission restrictions.

---

## 39. Business and Branch Isolation

Payment, discount, and refund records must be isolated by business.

Branch-specific financial operations must remain within the authorized branch scope.

Employees must not be able to:

* apply payments to another business;
* refund another business's orders;
* access another branch's financial information without authorization.

This isolation must apply to:

* online operations;
* offline operations;
* synchronization;
* reports;
* exports;
* background processing.

---

## 40. Performance Requirements

Payment operations are part of the POS critical path.

They must remain fast and reliable on normal restaurant hardware.

The system should avoid unnecessary processing during:

* payment confirmation;
* cash payment recording;
* card payment recording;
* discount application;
* order closure.

Financial consistency must be preserved without introducing unnecessary POS delays.

---

## 41. Business Rules Summary

| Area                 | Rule                                         |
| -------------------- | -------------------------------------------- |
| Payment methods      | Cash and Card                                |
| Cash                 | Affects physical cash reconciliation         |
| Card                 | Separate from physical cash                  |
| Payment identity     | Unique transaction identity                  |
| Duplicate payment    | Must be prevented                            |
| Order closure        | Requires successful payment where applicable |
| Offline payment      | Supported for authorized trusted devices     |
| Discount             | Affects order amount, not product base price |
| Discount permission  | Explicit permission required                 |
| Refund               | Separate financial operation                 |
| Refund permission    | Explicit permission required                 |
| Refund reason        | Mandatory                                    |
| Refund approval      | Permission-driven where required             |
| Refund history       | Preserved                                    |
| Cash refund          | Affects relevant cash position               |
| Card refund          | Retains original payment-method context      |
| Refund and inventory | Not automatically linked                     |
| Cancellation         | Separate from refund                         |
| Large refund         | Alert supported                              |
| Cash discrepancy     | Calculated from expected vs physical cash    |
| Handover             | Same cash session                            |
| Audit                | Financial changes preserved                  |
| Subscription         | Separate from employee permissions           |
| Branch isolation     | Required                                     |

---

## 42. Business Boundaries

The current Payments, Discounts and Refunds scope does **not** define:

* external payment gateway implementation;
* bank API integration;
* card terminal hardware integration;
* automatic card settlement reconciliation;
* installment payments;
* loyalty points;
* complex promotion engines;
* customer wallets;
* credit sales;
* accounts receivable;
* multi-currency payments;
* tax calculation engine.

These capabilities may be considered in future documentation if business requirements justify them.

---

## 43. Related Documents

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

