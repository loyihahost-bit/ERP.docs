# Audit and Change History

**Document ID:** FF-BA-018
**Status:** Draft
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for audit logging, change history, correction history, permission history, and traceability across the FastFood ERP system.

The audit system must provide a reliable historical record of important business and administrative actions.

The system must make it possible to determine:

* who performed an action;
* what was affected;
* what changed;
* when it changed;
* why it changed where a reason is required;
* which business and branch were affected;
* what the previous and new values were when applicable.

---

## 2. Audit Principles

The audit system follows these principles:

1. Important business changes must be traceable.
2. Historical records must not be silently overwritten.
3. Corrections must preserve the original state.
4. Permission changes must remain historically traceable.
5. Audit records must respect business and branch isolation.
6. Audit history must not grant additional permissions.
7. Audit logging must not block normal POS operations unnecessarily.
8. Historical records should remain available according to the system's data lifecycle rules.

---

## 3. Audit Record

An audit record represents a historical event that is important for business, security, or operational traceability.

An audit record may contain:

* event identity;
* event type;
* business identity;
* branch identity where applicable;
* employee identity;
* device identity where applicable;
* related entity;
* related transaction UUID where applicable;
* timestamp;
* previous value;
* new value;
* reason/comment where required;
* action/result;
* relevant context.

The exact technical structure is defined later in Architecture and Database documentation.

---

## 4. Actor Identity

Every auditable action must identify the actor whenever an authenticated employee performs the action.

The actor may be:

* Owner;
* Manager;
* Cashier;
* Waiter;
* Cook;
* other authorized employee;
* Super Admin for platform-level actions;
* system process for automatic actions.

System-generated actions must be distinguishable from employee-generated actions.

---

## 5. Employee Identity Preservation

Employee records must remain identifiable after deactivation.

Historical records must continue to reference the employee who performed the original action.

Deactivating an employee must not replace their historical identity with a generic or anonymous value.

---

## 6. Business and Branch Context

Audit records must preserve the relevant business context.

Where an action belongs to a specific branch, the audit record must identify the branch.

Where an action is business-wide, the branch may be absent or represented according to the final data model.

A user must never be able to use audit history to access information outside their authorized business or branch scope.

---

## 7. Device Context

Where relevant, audit records may include the device involved in the action.

This is particularly important for:

* offline operations;
* trusted devices;
* POS activity;
* synchronization;
* authentication-related events.

Device identity must not replace employee identity.

Both may be relevant to establishing who performed an action and from where.

---

## 8. Transaction Identity

Where an auditable event belongs to a transaction, the transaction UUID must remain associated with the audit event.

The system uses the transaction UUID as the permanent transaction identity.

A separate Client Transaction ID is not required.

The same transaction UUID must remain traceable across offline creation, synchronization, corrections, and reporting.

---

## 9. Immutable Audit History

Audit records must not be silently edited or deleted through normal application operations.

If an earlier action needs to be corrected, a new event must describe the correction.

For example:

```text id="m5c1yr"
Original Action
      ↓
Correction
      ↓
New Audit Event
```

The original audit record remains part of the historical record.

---

## 10. Change History

Change history focuses on modifications to business data.

A change record should preserve, where applicable:

* affected entity;
* field or business attribute;
* old value;
* new value;
* actor;
* timestamp;
* reason;
* business;
* branch;
* related transaction.

This allows authorized users to understand how a record changed over time.

---

## 11. Old and New Values

When a value is changed, the system should preserve both the previous and new values where business traceability requires them.

Example:

```text id="p9c0ha"
Old Value: 100
New Value: 120
Reason: Approved price change
Actor: Authorized Employee
Time: Recorded Timestamp
```

The system must not replace the old value without preserving the historical change where the field is auditable.

---

## 12. Reason Requirements

Some business actions require a mandatory reason or comment.

Examples include:

* refunds;
* cash-session corrections;
* correction authorization;
* correction rejection;
* relevant manual adjustments;
* other explicitly defined business corrections.

The audit history must retain the supplied reason.

A required reason cannot be bypassed by performing the same action through another interface.

---

## 13. Permission Change History

Permission changes must be auditable.

A permission-change event should record:

* actor;
* target employee or role;
* business;
* branch scope;
* permission;
* previous state;
* new state;
* timestamp;
* change type.

Example:

```text id="s3fl2v"
Permission: View Recipes
Previous: Disabled
New: Enabled
Target: Employee
Branch: Branch A
Changed By: Owner
```

---

## 14. Permission Revert

Reverting a permission change must create a new historical event.

The system must not delete the previous permission-change record.

For example:

```text id="v7nd2x"
Grant Permission
      ↓
Revoke Permission
      ↓
Both Events Remain
```

This preserves the complete permission history.

---

## 15. Permission Conflict History

When permission changes affect multiple employees or branches, each affected target must remain traceable.

If a command changes the same permission for several employees, the audit history must allow the system to identify each affected employee.

This applies to:

* selected employees;
* role-based changes;
* branch-specific changes;
* multiple-branch changes.

---

## 16. Latest Explicit Permission Command

The permission model uses the latest explicit command for the same permission and scope as the effective configuration.

The audit history must preserve earlier commands even when they are superseded.

This makes it possible to determine why the current permission state exists.

---

## 17. Role History

Role-related changes should be auditable.

Examples include:

* role creation;
* role modification;
* role cloning;
* role permission changes;
* role assignment;
* role removal.

If a role is cloned, the history should preserve the relationship between the original configuration and the newly created independent role where applicable.

---

## 18. Employee History

Important employee lifecycle actions should be traceable.

Examples include:

* employee creation;
* branch assignment;
* role assignment;
* permission change;
* salary configuration change;
* attendance correction;
* deactivation;
* reactivation where supported.

Employee deletion should not remove historical business actions.

---

## 19. Authentication and Device History

Security-sensitive authentication events should be auditable.

Examples include:

* login;
* authentication failure where appropriate;
* trusted-device registration;
* trusted-device verification;
* trusted-device revocation;
* offline authorization;
* device-related security events.

The exact security event list will be refined in the Security documentation.

---

## 20. Order History

Important order changes should be traceable.

Examples include:

* order creation;
* order acceptance;
* item addition;
* item removal;
* quantity changes;
* customization;
* discount;
* cancellation;
* payment;
* refund;
* relevant correction.

The order's permanent UUID must remain unchanged throughout its lifecycle.

---

## 21. Historical Order Values

Historical orders must preserve the information necessary to understand the order as it existed at the time.

For example, later changes to:

* product price;
* menu price;
* recipe;
* discount configuration;

must not rewrite the historical order into the new state.

Reports must use the appropriate historical transaction values.

---

## 22. Cash Session History

Cash-session operations require strong auditability.

The system should preserve history for:

* session opening;
* session closing;
* opening cash;
* cash count;
* expected cash;
* actual cash;
* shortage;
* overage;
* handover;
* recalculation;
* correction;
* correction request;
* correction approval;
* correction rejection;
* additional correction authorization.

---

## 23. Cash Correction History

A cash-session correction must preserve:

* original value;
* corrected value;
* reason;
* employee;
* timestamp;
* correction number;
* resulting difference;
* relevant cash session.

The original cash-session result must remain available.

A correction must not rewrite the historical session as though the original result never existed.

---

## 24. Correction Request History

Correction requests must be retained.

The history should show:

* requesting employee;
* cash session;
* request time;
* correction count;
* previous result;
* requested change;
* reason;
* approver;
* approval/rejection;
* approval/rejection time;
* rejection explanation where applicable.

Rejected requests must remain in history.

---

## 25. Correction Authorization History

When an Owner or authorized Manager grants an additional correction opportunity, the system must record:

* requesting employee;
* authorizing employee;
* cash session;
* authorization reason;
* date/time;
* number of additional corrections granted;
* resulting correction action.

Each additional authorization grants exactly one additional correction according to the current business rule.

---

## 26. Cash Handover History

Cash handover must preserve:

* previous cashier;
* new cashier;
* cash session;
* handover start;
* physical cash entered;
* expected amount;
* difference;
* Confirm/Recalculate action;
* completion time.

A handover does not create a new cash session.

The same Cash Session UUID remains associated with the handover.

---

## 27. Inventory History

Important inventory operations should be traceable.

Examples include:

* stock receipt;
* purchase entry;
* prepared-in-branch production;
* stock adjustment;
* stock count;
* variance;
* inventory deduction;
* product availability change;
* archive;
* relevant manual correction.

Inventory history must preserve the relevant branch and product context.

---

## 28. Inventory Variance History

A stock count must preserve the relationship between:

* expected quantity;
* counted quantity;
* difference;
* resulting adjustment;
* employee;
* timestamp;
* reason/comment where applicable.

The system must preserve the historical variance rather than silently replacing it with the corrected stock quantity.

---

## 29. Recipe History

Recipe changes must be traceable.

The history should preserve:

* previous recipe version;
* new recipe version;
* components;
* quantities;
* approval;
* approver;
* modification employee;
* timestamp;
* relevant reason.

Archived recipes must remain available for historical traceability.

---

## 30. Product and Menu History

Important product and menu changes should be auditable.

Examples include:

* product creation;
* product archive;
* menu activation;
* menu deactivation;
* category changes;
* price changes;
* branch price override;
* product availability changes.

Historical transactions must not be rewritten because the current menu changed.

---

## 31. Payment and Refund History

Payment-related actions should be traceable.

Examples include:

* payment creation;
* payment correction;
* refund;
* refund approval;
* refund rejection where applicable;
* cancellation.

Refund history must preserve the reason and responsible employee.

Large refunds should remain linked to their corresponding alert where applicable.

---

## 32. Employee and Payroll History

Important employee and payroll changes should be traceable.

Examples include:

* salary configuration;
* salary model change;
* bonus;
* payroll calculation;
* payroll correction;
* attendance correction;
* branch assignment;
* employee deactivation.

Historical payroll information must remain associated with the relevant employee and payroll period.

---

## 33. Report History

Reports must preserve their own historical versions.

Audit history should identify:

* report generation;
* report version;
* reporting period;
* creator/system;
* version cause;
* relevant correction or business change.

Previous report versions must remain immutable.

---

## 34. Notification History

Important notification events may be auditable.

The system may preserve:

* notification type;
* recipient;
* related entity;
* creation time;
* read status;
* relevant action.

Performing an action through a notification must create the normal business audit event for that action.

---

## 35. Offline Audit Events

Offline transactions must preserve sufficient audit information locally to remain traceable after synchronization.

An offline event should preserve, where applicable:

* business UUID;
* branch UUID;
* employee UUID;
* device UUID;
* transaction UUID;
* timestamp;
* action;
* relevant data.

After synchronization, the central system must retain the event's historical context.

---

## 36. Synchronization History

Synchronization-related events should be traceable where they affect business data.

Examples include:

* synchronization started;
* synchronization completed;
* transaction accepted;
* transaction rejected;
* duplicate transaction detected;
* synchronization conflict;
* synchronization failure.

A rejected offline transaction must remain identifiable and must not silently disappear.

---

## 37. System-Generated Audit Events

Some events may be generated automatically by the system.

Examples include:

* monthly report generation;
* subscription state change;
* automatic report retry;
* notification generation;
* scheduled processing;
* data lifecycle actions.

System-generated events must be distinguishable from employee actions.

---

## 38. Audit Access

Audit history must be permission-controlled.

Authorized users may be allowed to:

* view audit history;
* view change history;
* view correction history;
* view permission history;
* export relevant audit information where permitted.

Access to audit history must follow business and branch scope.

---

## 39. Audit and Owner Access

The Owner should have access to relevant audit information for their business according to the permission model.

Owner access does not allow modification of audit records.

Audit records remain historical records.

---

## 40. Audit and Manager Access

Managers may access audit information only if the required permission has been granted.

Their access remains limited by branch scope and other applicable permissions.

A Manager must not gain broader business access simply because audit records exist.

---

## 41. Audit and Subscription

Audit history follows the business data lifecycle.

When a subscription expires:

* normal modifying operations may be restricted;
* authorized users may continue to view available historical information;
* audit history remains part of the business data during the allowed retention period.

Trusted devices do not bypass subscription restrictions.

---

## 42. Audit and Data Deletion

When the business reaches permanent deletion after the defined retention period, audit history belonging to that business is deleted as part of the business data lifecycle.

The deletion process itself must be traceable at the platform level where required.

The normal application must not allow business users to selectively delete audit history.

---

## 43. Audit and Reporting

Reports may include audit-related information.

The report system must distinguish between:

* transactional data;
* correction history;
* audit history;
* report version history.

A report must not replace the underlying audit log.

---

## 44. Audit and Security

Audit information may contain sensitive business information.

Therefore:

* access must be permission-controlled;
* branch isolation must be enforced;
* unauthorized users must not view restricted history;
* audit records must not expose unrelated businesses;
* security-sensitive events should receive appropriate protection.

Detailed security implementation is defined later in Security and Architecture documentation.

---

## 45. Audit Performance

Audit logging must not noticeably slow down critical operations.

Critical workflows include:

* order creation;
* order acceptance;
* payment;
* inventory deduction;
* cash operations;
* handover.

Where appropriate, audit processing may be separated from non-critical user-facing processing while still preserving reliable event recording.

---

## 46. Audit Failure

Failure of a non-critical auxiliary audit process must not unnecessarily block ordinary POS activity.

However, actions that legally or operationally require mandatory traceability must not be completed without the required audit record.

The exact list of mandatory audit dependencies will be defined during system architecture and security analysis.

---

## 47. No Silent Overwrite

The system must not silently replace important historical information.

For example:

```text id="7s5m2c"
Original Cash Result
        ↓
Correction
        ↓
Original Result + Correction History
```

The system must not produce:

```text id="3a8rpn"
Only Corrected Result
```

when the original result is required for traceability.

---

## 48. Audit Record Retention

Audit records remain available according to the business data lifecycle.

During the active business lifecycle, important audit records must remain accessible to authorized users.

After permanent business deletion, the business's audit history is removed according to the data deletion rules.

---

## 49. Business Rules Summary

| Area           | Rule                                              |
| -------------- | ------------------------------------------------- |
| Audit          | Important actions must be traceable               |
| Actor          | Employee/system identity must be preserved        |
| Business       | Business context must be preserved                |
| Branch         | Branch context must be preserved where applicable |
| Device         | Device identity may be preserved where relevant   |
| Transaction    | Permanent transaction UUID remains traceable      |
| Old value      | Preserve where historical change requires it      |
| New value      | Preserve changed value                            |
| Reason         | Mandatory reasons must remain in history          |
| Permissions    | Permission changes are auditable                  |
| Revert         | Creates a new event; old event remains            |
| Cash           | Cash operations require strong history            |
| Corrections    | Original values remain available                  |
| Inventory      | Important stock changes are traceable             |
| Recipes        | Recipe versions remain historical                 |
| Orders         | Historical transaction values are preserved       |
| Reports        | Previous report versions remain immutable         |
| Notifications  | Important notification events may be retained     |
| Offline        | Offline events remain traceable after sync        |
| Audit access   | Permission and branch scoped                      |
| Audit deletion | Not allowed through normal business UI            |
| Subscription   | Audit history follows business lifecycle          |
| Performance    | Audit must not unnecessarily slow POS             |

---

## 50. Business Boundaries

The current Audit and Change History scope does **not** define:

* exact database audit table structure;
* exact event schema;
* cryptographic signing of every audit record;
* blockchain-based audit storage;
* external SIEM integration;
* government audit integration;
* advanced forensic investigation tools;
* arbitrary user-configurable audit rules.

These topics may be defined later in Architecture, Security, Database, and Operations documentation.

---

## 51. Related Documents

* `01_Product_Overview.md`
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
* `17_Notifications_and_Alerts.md`
* `19_Data_Lifecycle_and_Deletion.md`
* `20_Business_Rules.md`

