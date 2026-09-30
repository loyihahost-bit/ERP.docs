# Notifications and Alerts

**Document ID:** FF-BA-017
**Status:** Accepted
**Version:** 2.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for notifications and alerts in the FastFood ERP system.

Notifications and alerts inform authorized users about important business events, operational conditions, warnings, required actions, exceptions, and system-generated changes.

The notification system must provide useful and actionable information without creating unnecessary interruptions or notification spam.

Notifications are informational and operational mechanisms. They do not replace the underlying business record or business workflow.

---

## 2. Notification Principles

The notification system follows these principles:

1. Notifications must be triggered by defined business events or conditions.
2. Notifications must respect employee permissions.
3. Notifications must respect business and branch scope.
4. Notifications must respect subscription entitlements where applicable.
5. Notifications must never grant permissions.
6. Important notification-related actions must remain traceable.
7. Notifications must reference the underlying business context.
8. Repeated unchanged conditions must not create uncontrolled notification spam.
9. Critical business transactions must not depend on successful notification delivery.
10. Notification processing must not noticeably slow down critical POS operations.
11. Historical notification information must remain available where auditability requires it.

---

## 3. Notification vs Alert

The system distinguishes between notifications and alerts.

### 3.1. Notification

A notification informs an authorized user that an event has occurred or that an action/result is available.

Examples:

* report generated;
* report version changed;
* salary becoming due;
* correction request created;
* cash-session discrepancy recorded.

### 3.2. Alert

An alert indicates a condition that may require attention.

Examples:

* low stock;
* out of stock;
* large refund;
* large inventory variance;
* branch loss;
* cash shortage.

The user interface may present notifications and alerts through a common notification center, but their business meanings remain different.

---

## 4. Notification Context

Every notification must have a clear business context.

Depending on the event, the context may include:

* Business;
* Branch;
* Employee;
* Device;
* Cash Register;
* Cash Session;
* Order;
* Payment;
* Refund;
* Inventory item;
* Warehouse;
* Payroll period;
* Report;
* Subscription;
* Correction request.

Example:

```text
Low Stock Alert
    ↓
Business
    ↓
Branch
    ↓
Warehouse
    ↓
Inventory Item
    ↓
Current Quantity / Threshold
```

The notification must contain enough context for the recipient to understand why it was generated.

---

## 5. Notification Scope

Notifications may be scoped to:

* business;
* branch;
* employee;
* cash session;
* order;
* payment;
* refund;
* inventory;
* payroll;
* report;
* subscription;
* correction.

A notification must never expose information outside the recipient's authorized scope.

Business-wide notifications may contain information from multiple branches only when the recipient has corresponding business-wide access.

---

## 6. Recipient Determination

Recipients are determined according to:

* notification type;
* business rules;
* employee permissions;
* business scope;
* branch scope;
* responsible employee;
* relevant management role;
* underlying entity ownership;
* subscription state where applicable.

The system must not send a notification merely because a user belongs to the same business.

The recipient must have a valid business reason and authorization to receive the information.

---

## 7. Notification Ownership

Every important notification must have an identifiable business owner or responsible context.

For example:

```text
Cash Discrepancy
    ↓
Cash Session
    ↓
Cashier
    ↓
Branch
    ↓
Owner / Authorized Management
```

This allows the recipient to identify the responsible transaction and related business context.

---

## 8. Notification Lifecycle

A notification may have the following lifecycle depending on its type:

```text
Created
   ↓
Unread
   ↓
Read
   ↓
Resolved / Historical
```

Not every notification requires every state.

Examples:

* Report Ready → Unread → Read
* Low Stock → Active → Resolved
* Correction Request → Pending → Approved/Rejected
* Cash Discrepancy → Unread → Read → Historical

The lifecycle must reflect the underlying business meaning.

---

## 9. Read and Resolution State

The system must distinguish between reading a notification and resolving the underlying condition where necessary.

Reading a notification does not resolve the underlying business issue.

For example:

```text
Low Stock Alert
    ↓
User reads alert
    ↓
Alert remains active
    ↓
Stock is replenished
    ↓
Underlying condition is resolved
```

The exact resolution state depends on the notification type.

---

## 10. Persistent Alerts

Operational alerts may remain active while their underlying condition continues.

Examples:

* low stock;
* out of stock;
* unresolved cash discrepancy;
* pending correction request;
* relevant system condition requiring action.

Once the underlying condition is resolved, the alert may become historical.

The system must preserve the historical occurrence where required for auditability.

---

## 11. Repeated Conditions

The system must avoid generating unlimited duplicate notifications for an unchanged condition.

For example, if an inventory item remains below its threshold, the system must not create a new notification every few seconds.

A new notification may be generated when:

* the condition changes materially;
* the condition becomes active again after being resolved;
* a defined notification policy requires a new reminder;
* the underlying business event is a new event rather than the continuation of the same condition.

The notification mechanism must support deduplication or equivalent business-level suppression.

---

## 12. Subscription Notifications

The system must notify authorized users about important subscription lifecycle events.

Subscription notifications may include:

* approaching expiration;
* expiration;
* transition to restricted/read-only operation;
* approaching permanent deletion;
* permanent deletion status where applicable.

The exact lifecycle and retention rules are defined by the subscription and data lifecycle documents.

---

## 13. Subscription Expiration

When a subscription expires, authorized users must be informed that modifying functions are restricted.

The notification should identify:

* business;
* subscription status;
* relevant expiration date;
* affected capabilities;
* available reactivation/renewal action where applicable.

Subscription expiration must affect business capabilities regardless of device state.

Trusted devices and offline authorization must not bypass subscription restrictions.

---

## 14. Permanent Deletion Warning

If a business remains inactive after subscription expiration, the system must provide warnings before permanent deletion according to the defined 60-day lifecycle.

Warnings should make clear:

* current subscription state;
* remaining allowed period where applicable;
* affected business;
* permanent deletion consequence;
* available reactivation action.

The deletion process and exact lifecycle rules are defined in `19_Data_Lifecycle_and_Deletion.md`.

---

## 15. Low Stock Alert

The system must support low-stock alerts.

A low-stock alert is generated when the available quantity of an inventory item reaches or falls below its configured low-stock threshold.

The alert should identify:

* business;
* branch;
* warehouse where applicable;
* product/material;
* current quantity;
* configured threshold.

Low-stock status is a warning condition.

It does not by itself block product sale.

---

## 16. Out-of-Stock Alert

The system must support out-of-stock alerts.

An out-of-stock condition occurs when available inventory is insufficient for the relevant operation or reaches zero according to the applicable inventory rule.

The alert should identify:

* business;
* branch;
* warehouse where applicable;
* affected product/material;
* current availability;
* relevant inventory context.

Actual inventory shortage must block an operation that requires unavailable stock according to inventory rules.

---

## 17. Shopping List Relationship

Low-stock and out-of-stock conditions may contribute to the advisory shopping list.

The shopping list does not replace inventory operations.

A notification must not require the user to complete a shopping-list action before:

* purchasing stock;
* recording a purchase;
* performing an authorized inventory operation.

After purchasing, the user may record:

* quantity;
* unit price;
* total;
* source/supplier;
* purchase date;
* batch;
* comment.

---

## 18. Salary Due Alert

The system must support salary/payroll due notifications.

The notification informs authorized users when a salary or payroll obligation becomes due according to the configured payroll process.

Recipients depend on:

* payroll permissions;
* business scope;
* branch scope;
* relevant payroll responsibility.

Salary-sensitive information must not be exposed to users who are not authorized to access it.

Where appropriate, the notification should identify:

* payroll period;
* branch;
* employee or employee group;
* due status.

---

## 19. Large Refund Alert

The system must support alerts for significant refunds.

The condition is determined by the configured business rule for identifying a large refund.

The system must not assume a fixed monetary threshold unless such a threshold is defined by a separate business requirement or business configuration.

The notification may include:

* branch;
* order;
* refund amount;
* payment method;
* refund type;
* reason;
* responsible employee;
* timestamp.

The refund remains a separate financial transaction and is not replaced by the notification.

---

## 20. Large Inventory Variance Alert

The system must support alerts for significant inventory variance.

A variance may be identified after:

* stock counting;
* inventory adjustment;
* relevant inventory reconciliation.

The notification may include:

* branch;
* warehouse;
* inventory item;
* expected quantity;
* counted quantity;
* difference;
* responsible employee;
* timestamp;
* reason/comment where available.

The threshold for a significant variance must remain configurable or be defined by a future business rule.

---

## 21. Branch Loss Alert

The system must support an alert for significant branch loss for the relevant business period, including current-day monitoring where applicable.

The calculation may consider:

* sales;
* refunds;
* expenses;
* inventory-related losses;
* other explicitly defined branch-level financial effects.

The system must not infer branch loss from a single transaction.

The exact calculation and threshold must be defined by business rules.

---

## 22. Cash Discrepancy Notifications

Cash-session discrepancies must generate relevant notifications.

A discrepancy may be:

* shortage;
* overage.

The notification must preserve the relationship to the relevant:

* business;
* branch;
* cash register;
* cash session;
* cashier.

The responsible cashier must be informed when their cash session has a discrepancy.

The Owner or another authorized management user must be informed according to cash-session business rules.

A notification does not change the discrepancy itself.

---

## 23. Cash Close Comment Notification

When a cashier closes a cash session and provides a relevant closing comment, the system may generate an Owner or authorized management notification according to the cash-session rules.

The notification should preserve:

* cash session;
* branch;
* cashier;
* comment;
* closing result;
* discrepancy where applicable;
* timestamp.

The notification does not replace the cash-session report or audit record.

---

## 24. Cash Handover Notifications

Cash handover follows the business workflow defined in `10_Shift_Handover.md`.

The handover process is:

```text
Previous Cashier
      ↓
Closes Previous Cash Session
      ↓
New Cashier Authenticates
      ↓
New Cashier Counts Physical Cash
      ↓
System Reveals Expected Amount
      ↓
New Cashier Accepts / Confirms Cash
      ↓
New Cash Session Opens
```

The handover notification must therefore be directed to the employee who must perform the relevant next action.

The notification must not create a separate business workflow that conflicts with the cash-session handover process.

The system does not use a separate Reject action for ordinary handover confirmation.

---

## 25. Cash Handover Discrepancy

If the new cashier enters a physical cash amount that differs from the expected amount, the discrepancy must remain associated with the relevant cash session and responsible state.

The notification may identify:

* previous cash session;
* previous cashier;
* new cashier;
* expected amount after entry;
* actual amount;
* difference;
* branch;
* timestamp.

The previous session remains historically associated with the previous cashier.

The new cashier does not automatically inherit responsibility for the previous cashier's discrepancy.

---

## 26. Cash Correction Notifications

Cash-session corrections may generate notifications where required.

A correction-related notification may identify:

* cash session;
* branch;
* correction count;
* original result;
* new result;
* difference;
* reason;
* responsible employee;
* timestamp.

Correction notifications must remain distinguishable from ordinary cash-session notifications.

A correction is a separate auditable action and does not reopen the closed cash session as an active session.

---

## 27. Additional Correction Authorization

The normal correction limit is defined by the cash-session business rules.

When the normal correction limit has been reached, the system permits one additional correction only through explicit authorization by an authorized Owner or Manager.

The authorized user may receive a correction request notification containing:

* cash session;
* requesting cashier;
* current correction count;
* previous result;
* discrepancy;
* reason;
* request time;
* relevant correction history.

The authorization itself must be recorded and consumed when the additional correction opportunity is used.

A notification does not itself authorize the correction.

---

## 28. Correction Approval and Rejection

Approval or rejection of an additional correction request must be recorded.

If the request is rejected:

* the requester may be informed where permitted;
* the rejection reason must be preserved;
* the rejected request remains in history;
* rejection does not itself reopen the cash session;
* any later correction opportunity requires a new valid authorization according to the cash correction rules.

The notification and authorization history must remain distinct from the cash-session correction records.

---

## 29. Report Generation Notifications

The system must support report-related notifications.

Relevant events include:

* scheduled report generation;
* successful report generation;
* report generation failure;
* successful retry;
* manual restart where applicable;
* report re-versioning caused by relevant business data changes.

Notification delivery must not block report generation or the underlying business transaction.

---

## 30. Report Ready Notification

After successful report generation, authorized users may receive a report-ready notification.

The notification should identify:

* report type;
* reporting period;
* branch or business scope;
* report version;
* availability;
* view/download action where permitted.

The notification must respect report permissions.

---

## 31. Report Generation Failure Notification

If automatic report generation fails after the available automatic retries, the system must notify the Owner or authorized reporting users.

The notification should identify:

* report type;
* reporting period;
* branch/business scope;
* failure status;
* retry status;
* available manual restart action where permitted.

The underlying failure must also be logged.

A failed notification must not make a successfully completed report appear failed.

---

## 32. Report Change Notification

When a report receives a new version because relevant underlying business data changed, the system may generate a report-change notification for authorized users.

The notification may identify:

* report type;
* reporting period;
* branch/business scope;
* previous version;
* new version;
* change reason;
* affected cash session where applicable;
* previous state;
* new state;
* change amount;
* responsible employee;
* timestamp.

Where multiple metrics changed, the notification should summarize the relevant changes rather than exposing unnecessary detail.

---

## 33. No-Change Rule

A correction or other business action that does not actually change the relevant data used by a report must not create a report-change notification.

It must also not create an unnecessary new report version.

This prevents users from receiving notifications for actions that have no reporting impact.

---

## 34. Notification Actions

Where a notification requires or supports an action, the action must open or reference the relevant business context.

Examples:

```text
Cash Handover
    → Open relevant handover/session

Low Stock
    → Open relevant inventory context

Report Ready
    → Open relevant report

Correction Request
    → Open correction request

Salary Due
    → Open relevant payroll context
```

The notification itself does not replace the underlying business workflow.

---

## 35. Notification Permissions

A notification must never grant permission.

Receiving a notification does not automatically allow the user to:

* edit the related record;
* approve a refund;
* perform a cash correction;
* modify inventory;
* change permissions;
* access restricted payroll information;
* generate or modify a report.

The user must separately possess the required permission.

The underlying business operation must perform its own authorization check.

---

## 36. Notification and Subscription Entitlement

Notifications must respect subscription entitlements.

If a feature is unavailable because the business subscription does not include it, the notification system must not provide a notification that effectively bypasses that restriction.

Subscription expiration must not be bypassed through:

* notification actions;
* trusted devices;
* offline mode;
* synchronization.

---

## 37. Notification and Branch Scope

If an employee has access only to Branch A, a Branch B notification must not be shown to that employee.

If an employee has business-wide access, notifications may include information from permitted branches.

Branch-specific notification data must follow the same tenant and branch isolation rules as normal application data.

---

## 38. Notification and Employee Scope

Notifications containing employee-specific information must respect employee permissions.

Examples include:

* payroll;
* attendance;
* salary;
* employee-related correction actions.

A notification must not reveal salary or payroll information merely because the recipient is a Manager.

The relevant payroll permission must still apply.

---

## 39. Notification and Offline Operation

Trusted offline devices may display locally available notifications and operational warnings based on locally available authorized data.

Offline notifications must not bypass:

* employee permissions;
* branch scope;
* subscription restrictions;
* trusted-device requirements;
* transaction authorization rules.

The local notification state is not automatically authoritative over the server state.

Server-side state becomes authoritative after synchronization.

---

## 40. Offline Events

Business events created while offline must preserve sufficient identity and context for later synchronization.

Relevant information may include:

* business identity;
* branch identity;
* employee identity;
* device identity;
* cash register identity;
* cash session identity;
* order identity;
* payment identity;
* inventory transaction identity;
* event timestamp;
* local UUID.

The UUID is used for event identity and idempotency.

The system must not introduce a separate Client Transaction ID solely for notifications.

---

## 41. Notification Synchronization

When a trusted device reconnects:

1. locally generated relevant events are synchronized;
2. the server validates the events;
3. duplicate events are identified using their unique identities;
4. authoritative notification state is established;
5. applicable notifications are synchronized back to the device.

Synchronization must be idempotent.

Duplicate synchronization must not create uncontrolled duplicate notifications.

Server-side authorization and business validation remain authoritative.

---

## 42. Notification History

Important notifications must remain traceable.

The system should retain:

* notification type;
* underlying event;
* business;
* branch where applicable;
* recipient;
* related entity;
* creation time;
* read time where applicable;
* resolution time where applicable;
* status;
* relevant message/context;
* action reference where applicable.

Notification history must not modify the underlying business record.

---

## 43. Notification Security

Notifications may contain sensitive business information.

Therefore:

* unauthorized users must not receive restricted information;
* branch scope must be enforced;
* tenant isolation must be enforced;
* payroll information must be permission-controlled;
* cash information must respect cash-session permissions;
* report information must respect report permissions;
* refund information must respect financial permissions;
* inventory information must respect inventory permissions.

Notifications displayed on a trusted device remain subject to the employee's current authorization.

A trusted device does not grant notification access independently of the employee account.

---

## 44. Notification Delivery Failure

Failure to deliver a non-critical notification must not fail the underlying business transaction.

Example:

```text
Refund Transaction
      ↓
Refund Successfully Recorded
      ↓
Notification Delivery Fails
      ↓
Refund Remains Completed
      ↓
Notification Failure Is Logged / Retried
```

Notification delivery must be treated as a secondary operation where possible.

Appropriate failed deliveries may be retried.

Critical business transactions must never depend solely on notification delivery.

---

## 45. Notification Performance

Notification generation must not noticeably slow down:

* POS;
* order creation;
* payment processing;
* inventory operations;
* cash-session operations;
* cash handover;
* other critical operational transactions.

Notification processing should be separated from critical transaction processing where appropriate.

The business transaction must be committed according to its own rules independently of notification delivery.

---

## 46. Notification Auditability

Important notification events should be auditable.

The system should preserve:

* event type;
* notification creation;
* recipient;
* related entity;
* timestamp;
* status;
* action reference where applicable;
* relevant authorization context where applicable.

Actions performed from a notification must be audited as normal business actions.

A notification record must not become the sole audit record for a business transaction.

---

## 47. Business Rules Summary

| Area                     | Rule                                                                         |
| ------------------------ | ---------------------------------------------------------------------------- |
| Notifications            | Inform authorized users about relevant business events                       |
| Alerts                   | Identify conditions requiring attention                                      |
| Permissions              | Notifications never grant permissions                                        |
| Subscription             | Subscription lifecycle generates relevant warnings                           |
| Branch scope             | Notifications respect branch authorization                                   |
| Tenant isolation         | Notifications never cross business boundaries                                |
| Low stock                | Alert when quantity reaches the configured threshold                         |
| Out of stock             | Alert when inventory is unavailable for the relevant operation               |
| Shopping list            | Low/out-of-stock conditions may contribute to an advisory shopping list      |
| Salary                   | Notify authorized users when salary/payroll becomes due                      |
| Large refund             | Alert for refunds meeting the configured significant-refund rule             |
| Inventory variance       | Alert for significant inventory variance                                     |
| Branch loss              | Alert for significant branch-level loss according to defined rules           |
| Cash discrepancy         | Notify the responsible cashier and authorized management                     |
| Cash close comment       | May notify Owner/authorized management according to cash rules               |
| Cash handover            | Notifications follow the new-cashier authentication/count/accept workflow    |
| Correction request       | Notify authorized Owner/Manager when additional authorization is required    |
| Correction authorization | Notification does not itself grant authorization                             |
| Report ready             | Notify authorized users when a report is available                           |
| Report failure           | Retry, then notify authorized users and allow manual restart where permitted |
| Report changes           | Notify when relevant report data changes                                     |
| No-change correction     | No report-change notification or unnecessary new report version              |
| Persistent alerts        | Remain active while the underlying condition continues                       |
| Duplicate alerts         | Avoid uncontrolled repetition                                                |
| Offline                  | Notifications cannot bypass authorization or subscription restrictions       |
| Synchronization          | Notification/event synchronization must be idempotent                        |
| Security                 | Sensitive notification information is permission-controlled                  |
| Performance              | Notification processing must not block critical operations                   |
| Audit                    | Important notification events remain traceable                               |

---

## 48. Business Boundaries

The current Notifications and Alerts scope does not define:

* SMS integration;
* Telegram notifications;
* WhatsApp notifications;
* email delivery;
* external push notification provider selection;
* external notification services;
* user-defined arbitrary automation rules;
* AI-generated notifications;
* advanced notification scheduling;
* customer-facing notifications;
* marketing notifications.

These may be defined in future documentation if required.

---

## 49. Related Documents

* `01_Product_Overview.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `06_Authentication_and_Trusted_Devices.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `10_Shift_Handover.md`
* `11_Inventory_and_Warehouse.md`
* `12_Products_and_Recipes.md`
* `13_Menu_and_Pricing.md`
* `14_Payments_Discounts_and_Refunds.md`
* `15_Employees_Attendance_and_Payroll.md`
* `16_Reports_and_Dashboards.md`
* `18_Audit_and_Change_History.md`
* `19_Data_Lifecycle_and_Deletion.md`
* `20_Business_Rules.md`
* `adr/ADR-001-Documentation-First.md`

---

