# Notifications and Alerts

**Document ID:** FF-BA-017
**Status:** Draft
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for notifications and alerts in the FastFood ERP system.

Notifications inform authorized users about important business events, operational conditions, warnings, required actions, and system-generated changes.

The notification system must provide useful information without creating unnecessary interruptions.

---

## 2. Notification Principles

The notification system follows these principles:

1. Notifications must be triggered by defined business events or conditions.
2. Notifications must respect user permissions.
3. Notifications must respect business and branch scope.
4. Important actions must remain traceable.
5. Notifications must not replace the underlying business record.
6. Repeated conditions should not create uncontrolled notification spam.
7. Critical operational information should remain visible until appropriately handled where required.
8. Notification generation must not significantly affect POS performance.

---

## 3. Notification vs Alert

The system distinguishes between notifications and alerts.

### Notification

A notification informs a user that an event has occurred.

Examples:

* report generated;
* report changed;
* cash handover completed;
* salary becoming due.

### Alert

An alert indicates a condition that may require attention.

Examples:

* low stock;
* out of stock;
* large refund;
* large inventory variance;
* branch loss.

The exact presentation may be shared in the user interface, but the business meaning remains different.

---

## 4. Notification Scope

Notifications may be scoped to:

* business;
* branch;
* employee;
* cash session;
* order;
* inventory;
* report;
* subscription.

A notification must never expose information outside the recipient's authorized scope.

---

## 5. Recipient Determination

The system determines recipients according to:

* event type;
* user permissions;
* business scope;
* branch scope;
* responsible employee;
* relevant management role.

The Owner may receive notifications for important business events according to the defined business rules.

Employees should only receive notifications relevant to their responsibilities and permissions.

---

## 6. Notification Ownership

Every notification should have a clear business context.

For example:

```text
Low Stock
    ↓
Branch
    ↓
Warehouse
    ↓
Product
    ↓
Current Quantity / Threshold
```

This allows the recipient to understand why the notification was generated.

---

## 7. Subscription Notifications

The system must notify authorized users when a subscription is approaching expiration.

Subscription-related notifications may include:

* upcoming expiration;
* expiration;
* read-only state;
* approaching permanent deletion.

The exact notification schedule is controlled by the subscription lifecycle requirements.

---

## 8. Subscription Expiration

When a subscription expires, authorized users must be informed that modifying functions are restricted.

The notification should clearly indicate:

* subscription status;
* affected business;
* relevant date;
* available renewal/reactivation action where applicable.

Trusted devices must not bypass subscription restrictions.

---

## 9. Permanent Deletion Warning

If a business remains inactive after subscription expiration, the system must provide warnings before permanent data deletion according to the defined 60-day lifecycle.

The notification should make clear that failure to reactivate within the allowed period will result in permanent deletion.

---

## 10. Low Stock Alert

The system must support low-stock alerts.

A low-stock alert is generated when the available quantity of a product or inventory item reaches or falls below its configured low-stock threshold.

The alert should identify:

* branch;
* product/material;
* current quantity;
* configured threshold.

---

## 11. Out-of-Stock Alert

The system must support out-of-stock alerts.

An out-of-stock alert is generated when the available quantity reaches zero or the product becomes unavailable because required inventory is insufficient.

The alert should identify:

* branch;
* affected item;
* current availability;
* relevant inventory context.

---

## 12. Shopping List Relationship

Low-stock and out-of-stock conditions may contribute to the shopping list.

The shopping list is advisory.

A notification must not require the user to complete a shopping-list action before purchasing or recording inventory.

After purchasing, the user may manually record:

* quantity;
* price;
* source;
* purchase date.

---

## 13. Salary Due Alert

The system must support salary-due notifications.

The notification should inform authorized users when a salary or payroll obligation becomes due according to the configured payroll process.

Recipients depend on payroll permissions and branch scope.

The notification should provide enough information to identify the relevant payroll period or employee group without exposing unauthorized salary information.

---

## 14. Large Refund Alert

The system must support alerts for large refunds.

A large refund condition is determined by the configured business rule for identifying significant refunds.

The alert should provide relevant information such as:

* branch;
* order;
* refund amount;
* payment type;
* reason;
* responsible employee;
* time.

The system must not invent a fixed monetary threshold unless a separate business requirement defines one.

---

## 15. Large Inventory Variance Alert

The system must support alerts for significant inventory variance.

A variance may be identified after a stock count or relevant inventory adjustment.

The alert should provide information such as:

* branch;
* inventory item;
* expected quantity;
* counted quantity;
* difference;
* responsible employee;
* time;
* relevant reason/comment if available.

The threshold for what constitutes a "large" variance must remain configurable or be defined by a future business rule.

---

## 16. Branch Loss Alert

The system must support an alert for significant branch loss for the current day.

The alert may consider relevant business information such as:

* sales;
* refunds;
* expenses;
* inventory-related losses;
* other defined branch-level loss information.

The exact calculation must be defined by the business rules and must not be inferred from a single transaction.

---

## 17. Cash Discrepancy Notifications

Cash-session discrepancies must generate relevant notifications.

A discrepancy may be:

* shortage;
* overage.

The responsible cashier must be informed when their cash session has a discrepancy.

The Owner must be informed according to the cash-session rules.

The notification must preserve the relationship to the relevant cash session.

---

## 18. Cash Handover Notifications

Cash handover requires notifications to the relevant employees.

The previous cashier must receive the handover confirmation request.

The handover notification provides exactly two required actions:

* **Confirm**
* **Recalculate**

There is no separate Reject action.

The handover cannot be completed until one of the required actions is successfully performed.

---

## 19. Cash Correction Notifications

Cash-session corrections may generate notifications when relevant.

A correction-related notification may identify:

* cash session;
* correction count;
* previous result;
* new result;
* difference;
* reason;
* responsible employee;
* timestamp.

Correction requests and approvals must remain distinguishable from ordinary cash-session notifications.

---

## 20. Additional Correction Authorization

When a cashier reaches the allowed correction limit and requests another correction, the authorized Owner or Manager may receive a correction request notification.

The notification should include:

* cash session;
* requesting cashier;
* current correction count;
* previous result;
* discrepancy;
* reason;
* request time;
* relevant correction history.

Approval or rejection must be recorded.

---

## 21. Correction Rejection Notification

If a correction request is rejected, the requester must receive the rejection information where permitted.

The rejection must include the required explanation.

A rejected requester cannot automatically submit another request for the same case.

The rejecting authorized person may later reopen the correction ability according to the correction rules.

The original rejection and explanation remain in history.

---

## 22. Report Generation Notification

The system must support report-related notifications.

These include:

* notification that a scheduled report is expected;
* report generation completed;
* report generation failed after available automatic retries;
* report version changed because relevant business data changed.

---

## 23. Report Ready Notification

After successful report generation, authorized users should receive a report-ready notification.

The notification should identify:

* report type;
* reporting period;
* version;
* availability;
* view/download action where permitted.

---

## 24. Report Generation Failure Notification

If automatic report generation fails after the available retries, the system must notify the Owner or authorized reporting users.

The notification should identify:

* report type;
* reporting period;
* failure status;
* retry status;
* available manual restart action.

The underlying error must also be logged.

---

## 25. Report Change Notification

When a report is re-versioned because relevant data changed, the notification should identify important changes.

It may include:

* report period;
* report type;
* previous version;
* new version;
* reason;
* cash session;
* previous cash state;
* new cash state;
* change amount;
* responsible employee;
* timestamp.

If multiple metrics changed, the notification should summarize the important changes.

---

## 26. No-Change Rule

A correction that does not actually change the relevant business data must not create a report-change notification.

This prevents users from receiving notifications for changes that have no actual reporting impact.

---

## 27. Notification Status

A notification should have a lifecycle appropriate to its type.

Possible states may include:

* unread;
* read;
* resolved where applicable.

Not every notification requires a resolution state.

For example:

* report-ready notification may only require read status;
* low-stock alert may remain active until the underlying condition changes.

---

## 28. Persistent Alerts

Operational alerts may remain visible while their underlying condition continues.

For example:

```text
Low Stock
    ↓
Condition remains true
    ↓
Alert remains active
```

Once the condition is resolved, the alert may move to a historical state.

The system must preserve the historical occurrence where auditability requires it.

---

## 29. Repeated Conditions

The system should avoid generating unlimited duplicate notifications for the same unchanged condition.

For example, if an inventory item remains below its threshold, the system should not create a new notification every few seconds.

A new notification may be generated when the relevant condition meaningfully changes or according to a defined notification policy.

---

## 30. Notification History

Important notifications must remain traceable.

The system should retain:

* notification type;
* event;
* recipient;
* business;
* branch;
* related entity;
* creation time;
* read time where applicable;
* status;
* relevant message/context.

Notification history must not alter the underlying business record.

---

## 31. Notification and Permissions

A notification must never grant permission.

Receiving a notification does not automatically allow the user to:

* edit the related record;
* approve a refund;
* correct a cash session;
* modify inventory;
* change permissions;
* generate a report.

The user must separately possess the required permission.

---

## 32. Notification and Branch Scope

If a user has access only to Branch A, a Branch B alert must not be shown to that user.

If a user has business-wide access, notifications may include permitted branch information.

Branch-specific notification data must follow the same isolation rules as normal application data.

---

## 33. Notification and Offline Operation

Offline devices may display locally available notifications or operational warnings based on locally available data.

However, an offline notification must not bypass server-side authorization.

Server-generated notifications become authoritative after synchronization.

Events created offline must preserve:

* business identity;
* branch identity;
* employee identity;
* device identity;
* relevant transaction identity;
* timestamp.

---

## 34. Notification Synchronization

When a device reconnects to the server, locally generated relevant events and notification state must synchronize according to the synchronization rules.

Duplicate events must not create uncontrolled duplicate notifications.

The synchronization process must remain idempotent.

---

## 35. Notification Actions

Where a notification requires an action, the action must open or reference the relevant business context.

Examples:

```text
Cash Handover
    → Open Cash Handover

Low Stock
    → Open Inventory

Report Ready
    → Open Report

Correction Request
    → Open Correction Request
```

The notification itself does not replace the underlying business workflow.

---

## 36. Notification Security

Notifications may contain business-sensitive information.

Therefore:

* unauthorized users must not receive restricted information;
* branch scope must be enforced;
* payroll information must be permission-controlled;
* cash information must respect cash-session permissions;
* report information must respect report permissions.

Notifications displayed on a trusted device remain subject to the user's current authorization.

---

## 37. Notification Performance

Notification generation must not noticeably slow down:

* POS;
* order creation;
* payment processing;
* inventory operations;
* cash operations.

Heavy notification processing should be separated from critical transaction processing where appropriate.

---

## 38. Notification Failure

Failure to deliver a non-critical notification must not cause the underlying business transaction to fail.

For example:

```text
Refund completed
    ↓
Notification delivery fails
    ↓
Refund remains completed
```

The notification failure should be logged and retried where appropriate.

Critical business transactions must not depend solely on successful notification delivery.

---

## 39. Auditability

Important notification events should be auditable.

The system should preserve:

* event type;
* notification creation;
* recipient;
* related entity;
* timestamp;
* status;
* relevant action where applicable.

Actions performed from a notification must be audited as normal business actions.

---

## 40. Business Rules Summary

| Area                 | Rule                                                 |
| -------------------- | ---------------------------------------------------- |
| Notifications        | Inform users about relevant business events          |
| Alerts               | Identify conditions requiring attention              |
| Permissions          | Notifications never grant permissions                |
| Branch scope         | Notifications respect branch authorization           |
| Subscription         | Expiration and deletion lifecycle generates warnings |
| Low stock            | Alert when quantity reaches configured threshold     |
| Out of stock         | Alert when item becomes unavailable                  |
| Salary               | Notify authorized users when salary becomes due      |
| Large refund         | Alert for significant refunds                        |
| Inventory variance   | Alert for significant variance                       |
| Branch loss          | Alert for significant current-day branch loss        |
| Cash discrepancy     | Notify relevant cashier/Owner                        |
| Cash handover        | Previous cashier receives Confirm/Recalculate        |
| Correction request   | Notify authorized approver                           |
| Report ready         | Notify authorized users                              |
| Report failure       | Retry, then notify and allow manual restart          |
| Report changes       | Notify when relevant report data changes             |
| No-change correction | No report-change notification                        |
| Duplicate alerts     | Avoid uncontrolled repetition                        |
| Offline              | Notifications cannot bypass authorization            |
| Security             | Sensitive notification data is permission-controlled |
| Performance          | Notifications must not block critical operations     |

---

## 41. Business Boundaries

The current Notifications and Alerts scope does **not** define:

* SMS integration;
* Telegram notifications;
* WhatsApp notifications;
* email delivery;
* push notification provider selection;
* external notification services;
* user-defined arbitrary automation rules;
* AI-generated notifications;
* advanced notification scheduling;
* customer-facing notifications.

These may be defined in future documentation if required.

---

## 42. Related Documents

* `01_Product_Overview.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `06_Authentication_and_Trusted_Devices.md`
* `07_Offline_Operation_and_Synchronization.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `10_Shift_Handover.md`
* `11_Inventory_and_Warehouse.md`
* `14_Payments_Discounts_and_Refunds.md`
* `15_Employees_Attendance_and_Payroll.md`
* `16_Reports_and_Dashboards.md`
* `18_Audit_and_Change_History.md`
* `19_Data_Lifecycle_and_Deletion.md`
* `20_Business_Rules.md`

