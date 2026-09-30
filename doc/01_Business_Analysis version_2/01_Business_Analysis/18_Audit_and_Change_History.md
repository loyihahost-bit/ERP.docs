# Audit and Change History

**Document ID:** FF-BA-018
**Status:** Accepted
**Version:** 2.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for audit logging, change history, correction history, permission history, and traceability across the FastFood ERP system.

The audit system must provide a reliable historical record of important business, financial, operational, security, and administrative actions.

The system must make it possible, where applicable, to determine:

* who performed an action;
* what was affected;
* what changed;
* when it changed;
* why it changed;
* which business and branch were affected;
* which device was involved;
* which transaction or session was involved;
* what the previous and new values were.

Audit history is a historical record and must not replace the underlying business data.

---

## 2. Audit Principles

The audit system follows these principles:

1. Important business changes must be traceable.
2. Historical records must not be silently overwritten.
3. Corrections must preserve the original state.
4. Permission changes must remain historically traceable.
5. Business and branch isolation must apply to audit history.
6. Audit history must not grant additional permissions.
7. Employee identity must remain associated with historical actions after deactivation.
8. Transaction UUIDs must remain traceable throughout the transaction lifecycle.
9. Offline actions must remain traceable after synchronization.
10. System-generated actions must be distinguishable from employee actions.
11. Audit processing must not unnecessarily slow down critical POS operations.
12. Mandatory audit events must be reliably recorded.
13. Audit history must follow the defined business data lifecycle.

---

## 3. Audit Record

An audit record represents a historical event that is important for business, financial, security, or operational traceability.

An audit record may contain:

* event UUID;
* event type;
* business UUID;
* branch UUID where applicable;
* employee UUID where applicable;
* device UUID where applicable;
* related entity type;
* related entity UUID;
* related transaction UUID where applicable;
* cash session UUID where applicable;
* timestamp;
* previous value where applicable;
* new value where applicable;
* reason/comment where required;
* action;
* result;
* relevant business context.

The exact technical structure is defined later in Architecture and Database documentation.

---

## 4. Actor Identity

Every auditable employee action must identify the actor.

Possible actors include:

* Owner;
* Manager;
* Cashier;
* Waiter;
* Cook;
* other authorized employee;
* Super Admin for platform-level actions;
* system process for automatic operations.

System-generated actions must be explicitly distinguishable from employee-generated actions.

An audit record must not use an anonymous actor when an authenticated employee identity is available.

---

## 5. Employee Identity Preservation

Employee records must remain identifiable after deactivation.

Historical records must continue to reference the employee who performed the original action.

Deactivation must not:

* replace the employee with a generic account;
* remove the employee identity from history;
* rewrite previous actions under another employee.

Employee deletion, where permitted by lifecycle rules, must not destroy historical business attribution.

---

## 6. Business Context

Audit records must preserve the relevant business context.

Every tenant-level audit event must be associated with the appropriate Business UUID.

A user must never be able to use audit history to access information belonging to another business.

Tenant isolation applies to:

* audit records;
* change history;
* correction history;
* permission history;
* audit reports;
* exports;
* offline audit data;
* synchronization data.

---

## 7. Branch Context

Where an action belongs to a specific branch, the audit record must identify the Branch UUID.

For business-wide actions, branch context may be absent where appropriate.

Branch scope must follow the same authorization model as the underlying business operation.

A user with access only to Branch A must not view Branch B audit history.

---

## 8. Device Context

Where relevant, audit records should include the Device UUID.

Device context is particularly important for:

* POS operations;
* trusted devices;
* offline operations;
* synchronization;
* authentication events;
* cash operations.

Device identity does not replace employee identity.

Where both are relevant, the audit record must preserve both.

---

## 9. Transaction Identity

Where an auditable event belongs to a transaction, the permanent transaction UUID must remain associated with the audit event.

The system uses UUID-based transaction identity and idempotency.

A separate Client Transaction ID is not required.

The same transaction UUID must remain traceable across:

* offline creation;
* synchronization;
* payment;
* inventory deduction;
* correction;
* cancellation;
* refund where applicable;
* reporting.

---

## 10. Immutable Audit History

Audit records must not be silently edited or deleted through normal application operations.

If an earlier action requires correction, a new audit event must describe the correction.

Example:

```text
Original Action
      ↓
Correction
      ↓
New Audit Event
```

The original audit event remains part of the historical record.

The system must not rewrite the original event to make it appear as though the correction had always existed.

---

## 11. Change History

Change history focuses on modifications to business data.

Where applicable, a change record should preserve:

* affected entity;
* affected field or business attribute;
* previous value;
* new value;
* actor;
* timestamp;
* reason;
* business;
* branch;
* device;
* related transaction.

This allows authorized users to understand how a business record changed over time.

---

## 12. Old and New Values

When an auditable value changes, the system should preserve both the previous and new values.

Example:

```text
Old Value: 100
New Value: 120
Reason: Approved price change
Actor: Authorized Employee
Time: Recorded Timestamp
```

The system must not replace the old value without preserving the historical change where the field is considered auditable.

Sensitive values may be subject to additional security restrictions in later Security documentation.

---

## 13. Reason Requirements

Where a business rule requires a mandatory reason or comment, the audit history must retain it.

Examples include:

* refunds;
* cash-session corrections;
* additional correction authorization;
* correction rejection;
* inventory adjustments;
* relevant manual corrections;
* other explicitly defined corrective actions.

A mandatory reason cannot be bypassed by performing the same operation through another interface.

---

## 14. Permission Change History

Permission changes must be auditable.

A permission-change event should record:

* actor;
* target employee or role;
* business;
* branch scope;
* permission;
* previous effective state where applicable;
* new effective state;
* change type;
* timestamp.

Example:

```text
Permission: View Recipes
Previous: Disabled
New: Enabled
Target: Employee
Branch: Branch A
Changed By: Owner
```

The audit record must distinguish between:

* role permission changes;
* employee overrides;
* branch-scope changes;
* role assignment;
* permission removal.

---

## 15. Permission Revert

Reverting a permission change creates a new historical event.

The system must not delete or rewrite the previous permission-change event.

Example:

```text
Grant Permission
      ↓
Revoke Permission
      ↓
Both Events Remain
```

This preserves the complete permission history.

---

## 16. Permission Conflict History

When a permission command affects multiple employees or branches, every affected target must remain traceable.

This applies to:

* selected employees;
* multiple employees;
* selected branches;
* all permitted branches;
* role-based permission changes;
* employee-specific overrides.

A bulk operation may be represented as one logical command, but the audit history must allow each affected target to be identified.

---

## 17. Latest Explicit Permission Command

The permission model uses the latest explicit command for the same permission and scope as the effective configuration.

The audit history must preserve all previous commands even when they are superseded.

This makes it possible to determine why the current permission state exists.

The audit history must not treat a superseded permission command as though it never occurred.

---

## 18. Role History

Important role-related changes should be auditable.

Examples include:

* role creation;
* role modification;
* role cloning;
* role permission changes;
* role assignment;
* role removal;
* role deactivation where supported.

If a role is cloned, the history should preserve the relationship between the source configuration and the newly created independent role.

Changes to the cloned role must not silently rewrite the history of the original role.

---

## 19. Employee History

Important employee lifecycle actions should be traceable.

Examples include:

* employee creation;
* branch assignment;
* branch removal;
* role assignment;
* permission change;
* salary configuration change;
* attendance correction;
* deactivation;
* reactivation where supported.

Employee history must remain available after deactivation.

Historical business actions must continue to reference the original employee.

---

## 20. Authentication and Device History

Security-sensitive authentication and device events should be auditable.

Examples include:

* login;
* authentication failure where appropriate;
* trusted-device registration;
* trusted-device verification;
* trusted-device revocation;
* offline authorization issuance/use where applicable;
* device-related security events;
* suspicious clock rollback/tampering detection where recorded.

The exact security event list will be refined in Security documentation.

---

## 21. Order History

Important order changes must be traceable.

Examples include:

* order creation;
* draft modification;
* order acceptance;
* item addition;
* item removal;
* quantity change;
* ingredient removal;
* extra ingredient;
* unit-level customization;
* discount;
* cancellation;
* payment;
* refund;
* post-kitchen modification;
* relevant correction.

The order's permanent UUID must remain unchanged throughout its lifecycle.

---

## 22. Order Actor History

Historical order actions must preserve the actor and operational context applicable at the time of the action.

Where relevant, the audit record should preserve:

* employee;
* role/permission context;
* branch;
* device;
* cash register;
* cash session;
* timestamp.

If a cashier changes during an order's lifecycle, earlier actions remain associated with the original cashier/session and later actions are associated with the new cashier/session.

The order UUID remains unchanged.

---

## 23. Historical Order Values

Historical orders must preserve the information necessary to understand the order as it existed at the time.

Later changes to:

* product price;
* branch price override;
* recipe;
* discount configuration;
* menu configuration;

must not rewrite historical order values.

Reports must use historical transaction values and snapshots where required.

---

## 24. Cash Session History

Cash-session operations require strong auditability.

The system should preserve history for:

* session creation/opening;
* opening cash;
* session closing;
* physical cash entry;
* expected amount calculation;
* actual cash;
* shortage;
* overage;
* handover;
* cash confirmation;
* recalculation;
* correction;
* correction request;
* correction approval;
* correction rejection;
* additional correction authorization.

The historical record must preserve the relationship between the event and the relevant Cash Session UUID.

---

## 25. Cash Session Identity

A Cash Session is a distinct historical operational unit.

When a cashier handover occurs:

```text
Previous Cashier
      ↓
Previous Cash Session Closed
      ↓
New Cashier Authenticates
      ↓
New Cash Session Opens
```

The new cashier receives a **new Cash Session UUID**.

The physical Cash Register remains the same.

The handover history must therefore link:

* previous session;
* new session;
* previous cashier;
* new cashier;
* branch;
* cash register.

A handover must not make two separate cashier shifts appear as one cash session.

---

## 26. Cash Handover History

Cash handover must preserve:

* previous cashier;
* previous cash session UUID;
* new cashier;
* new cash session UUID;
* cash register;
* branch;
* handover start;
* physical cash entered;
* expected amount revealed after entry;
* difference;
* confirmation/recalculation action;
* completion time.

The previous session remains permanently associated with the previous cashier.

The new session remains associated with the new cashier.

Previous-session discrepancies do not automatically become new-session discrepancies.

---

## 27. Cash Correction History

A cash-session correction must preserve:

* cash session;
* correction number;
* original value;
* corrected value;
* original difference;
* new difference;
* reason;
* requesting employee;
* authorizing employee where applicable;
* timestamp;
* resulting state.

The original cash-session result must remain available.

A correction does not rewrite the original session as though the original result never existed.

A closed cash session remains historically closed.

---

## 28. Additional Correction Authorization History

When the normal correction limit has been reached, an authorized Owner or Manager may grant one additional correction opportunity.

The authorization history must record:

* requesting cashier;
* authorizing employee;
* cash session;
* current correction count;
* authorization reason;
* authorization time;
* number of additional corrections granted;
* subsequent correction, if used.

Each authorization grants exactly one additional correction opportunity according to the current business rule.

The authorization is consumed when that additional correction is used.

---

## 29. Correction Request History

Correction requests must be retained.

The history should show:

* requesting employee;
* cash session;
* request time;
* current correction count;
* previous result;
* requested change;
* reason;
* approver;
* approval/rejection;
* approval/rejection time;
* rejection explanation where applicable.

Rejected requests remain in history.

A rejected request must not be silently removed.

---

## 30. Inventory History

Important inventory operations must be traceable.

Examples include:

* stock receipt;
* purchase entry;
* prepared-in-branch production;
* stock deduction;
* stock adjustment;
* stock count;
* variance;
* inventory correction;
* product availability change;
* archive;
* equipment-broken state change where applicable.

Inventory history must preserve relevant:

* business;
* branch;
* warehouse;
* product;
* inventory item;
* employee;
* timestamp.

---

## 31. Inventory Variance History

A stock count must preserve the relationship between:

* expected quantity;
* counted quantity;
* difference;
* resulting adjustment;
* employee;
* branch;
* warehouse;
* timestamp;
* reason/comment where applicable.

The system must preserve the historical variance rather than silently replacing it with the corrected stock quantity.

---

## 32. Inventory Costing History

Where inventory costing affects a business calculation, the historical context necessary to explain the calculation should be retained.

Relevant costing models include:

* FIFO;
* Average Cost;
* Last Purchase Cost.

Historical calculations must not be silently recalculated using a later inventory state when the original transaction requires its historical costing context.

---

## 33. Recipe History

Recipe changes must be traceable.

The history should preserve:

* previous recipe version;
* new recipe version;
* components;
* quantities;
* modification employee;
* approval;
* approver;
* timestamp;
* relevant reason.

Archived recipes must remain available for historical traceability.

Recipe changes must not rewrite historical orders or historical inventory operations.

---

## 34. Recipe Approval History

Recipe creation or modification requiring approval must preserve:

* requesting employee;
* proposed recipe;
* previous recipe where applicable;
* approval state;
* approver;
* approval/rejection time;
* reason/comment where applicable;
* effective cash session or effective point where applicable.

The approval history must remain distinct from the recipe's current configuration.

---

## 35. Product and Menu History

Important product and menu changes should be auditable.

Examples include:

* product creation;
* product archive;
* product activation/deactivation;
* category assignment/change;
* menu availability;
* branch menu enable/disable;
* global price change;
* branch price override;
* product availability change;
* equipment-broken state;
* Set creation;
* Set configuration/version change.

Historical transactions must not be rewritten because the current menu changed.

---

## 36. Set History

Set configuration changes must be traceable.

The history should preserve:

* Set identity;
* previous component configuration;
* new component configuration;
* selling price;
* actor;
* reason where applicable;
* timestamp;
* effective cash session.

Underlying recipe changes must not silently rewrite historical Set composition.

A Set configuration change creates a new configuration/version according to the business rules.

---

## 37. Payment and Refund History

Payment-related actions should be traceable.

Examples include:

* payment creation;
* payment portion creation;
* mixed payment;
* debt payment;
* debt repayment;
* payment correction;
* refund;
* refund approval where applicable;
* refund rejection where applicable;
* cancellation.

Payment history must preserve the original transaction context.

Completed payments must not be silently overwritten.

Corrections must be represented as separate auditable operations.

---

## 38. Refund History

Refund history must preserve:

* original order;
* original payment where applicable;
* refund UUID;
* refund type;
* refunded amount;
* refunded item/quantity where applicable;
* refund method;
* reason;
* actor;
* approval context where required;
* branch;
* cash session where applicable;
* timestamp.

Refunds remain separate financial operations.

A refund does not automatically create an inventory return.

---

## 39. Employee and Payroll History

Important employee and payroll changes should be traceable.

Examples include:

* salary configuration;
* salary model change;
* fixed salary;
* percentage salary;
* shift pay;
* daily pay;
* hybrid pay;
* bonus;
* payroll calculation;
* payroll correction;
* attendance correction;
* branch assignment;
* employee deactivation.

Salary changes must preserve:

* previous configuration;
* new configuration;
* effective date;
* actor;
* reason.

Historical payroll results must not be rewritten because a later salary configuration changed.

---

## 40. Payroll Calculation Snapshot

A finalized payroll result must retain sufficient historical information to explain how it was calculated.

The audit/history context should preserve, where applicable:

* payroll period;
* employee;
* branch;
* salary model;
* applicable rate/configuration;
* attendance inputs;
* bonuses;
* deductions where applicable;
* calculated result;
* calculation timestamp;
* actor/system source.

Later changes to salary configuration must not silently change a finalized payroll result.

---

## 41. Report History

Reports must preserve their historical versions.

Audit history should identify:

* report generation;
* report version;
* reporting period;
* business/branch scope;
* creator/system source;
* creation reason;
* relevant correction;
* relevant underlying business change.

Previous report versions remain immutable.

A new report version is created only when relevant underlying data changes.

---

## 42. Report Re-Versioning History

When relevant business data changes a report:

```text
Report Version 1
      ↓
Relevant Business Change
      ↓
Report Version 2
```

The history must preserve the relationship between the versions and the underlying change.

Where a correction has no reporting impact, no unnecessary report version or report-change event should be created.

---

## 43. Notification History

Important notification events may be retained as part of historical traceability.

The history may preserve:

* notification type;
* recipient;
* business;
* branch;
* related entity;
* creation time;
* read time;
* resolution time where applicable;
* status;
* action reference.

Performing an action through a notification must create the normal audit event for the underlying business action.

The notification record does not replace the underlying audit event.

---

## 44. Offline Audit Events

Offline transactions must preserve sufficient audit information locally to remain traceable after synchronization.

An offline event should preserve, where applicable:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Cash Register UUID;
* Cash Session UUID;
* transaction UUID;
* timestamp;
* action;
* relevant data/context.

The local event must remain associated with its original transaction identity.

---

## 45. Synchronization History

Synchronization-related events should be traceable where they affect business data.

Examples include:

* synchronization started;
* synchronization completed;
* transaction accepted;
* transaction rejected;
* duplicate transaction detected;
* validation failure;
* synchronization conflict;
* synchronization failure;
* server-authoritative correction.

A rejected offline transaction must remain identifiable.

It must not silently disappear from the local or server history.

---

## 46. System-Generated Audit Events

Some events are generated automatically by the system.

Examples include:

* monthly report generation;
* report retry;
* subscription state change;
* notification generation;
* scheduled processing;
* data lifecycle processing;
* synchronization processing.

System-generated events must be distinguishable from employee actions.

Where a system event is triggered by an employee action, the relationship to the original actor should be preserved where relevant.

---

## 47. Audit Access

Audit history must be permission-controlled.

Authorized users may be allowed to:

* view audit history;
* view change history;
* view correction history;
* view permission history;
* view security history;
* view relevant report history;
* export audit information where explicitly permitted.

Access must follow:

* business scope;
* branch scope;
* employee permissions;
* subscription restrictions.

---

## 48. Owner Audit Access

The Owner may access relevant audit information for their business according to the permission model.

Owner access does not allow:

* editing audit records;
* deleting audit records;
* rewriting historical events;
* removing another employee's historical actions.

Audit records remain historical records.

---

## 49. Manager Audit Access

A Manager may access audit information only when the required permission has been granted.

Manager access remains limited by:

* branch scope;
* business scope;
* assigned permissions;
* subscription state.

A Manager does not gain broader business access merely because audit records contain information from other branches.

---

## 50. Audit and Subscription

Audit history follows the business subscription lifecycle.

When a subscription expires:

* modifying operations may be restricted;
* authorized historical information remains viewable according to the subscription lifecycle;
* audit history remains part of the business data during the allowed retention period;
* Excel export remains available where the read-only lifecycle permits it.

Trusted devices and offline operation must not bypass subscription restrictions.

---

## 51. Audit and Data Deletion

When a business reaches permanent deletion after the defined retention period, its business audit history is deleted as part of the business data lifecycle.

The deletion process itself must be traceable at the platform level where required.

Business users must not be able to selectively delete audit history through the normal application.

---

## 52. Audit and Reporting

Reports may include audit-related information.

The report system must distinguish between:

* transactional data;
* correction history;
* audit history;
* report version history.

A report is not a replacement for the underlying audit history.

Historical reports must preserve their own version integrity.

---

## 53. Audit and Security

Audit information may contain sensitive business and security information.

Therefore:

* access must be permission-controlled;
* business isolation must be enforced;
* branch isolation must be enforced;
* unauthorized users must not view restricted history;
* audit records must not expose unrelated businesses;
* security-sensitive events require appropriate protection;
* device context must not be treated as employee authorization.

Detailed security implementation is defined later in Security and Architecture documentation.

---

## 54. Audit Performance

Audit processing must not noticeably slow down critical operations such as:

* order creation;
* order acceptance;
* payment;
* inventory deduction;
* cash operations;
* cash handover;
* synchronization.

Where appropriate, non-critical auxiliary processing may be separated from the critical transaction path.

However, mandatory audit events must remain reliably associated with the transaction.

The architecture must not sacrifice historical integrity merely to reduce latency.

---

## 55. Audit Failure

Not every audit-related auxiliary operation should be allowed to block POS activity.

However, actions that require mandatory auditability must not be treated as successfully completed if the required audit event cannot be reliably recorded.

The exact list of mandatory audit dependencies will be finalized during Architecture, Database, and Security analysis.

For non-mandatory auxiliary history, failure should be logged and handled according to operational recovery rules.

---

## 56. No Silent Overwrite

The system must not silently replace important historical information.

Correct model:

```text
Original Cash Result
        ↓
Correction
        ↓
Original Result + Correction History
```

Incorrect model:

```text
Original Cash Result
        ↓
Overwrite
        ↓
Only Corrected Result
```

The original result must remain available whenever it is required for historical integrity.

---

## 57. Historical Integrity Across Business Configuration

Changes to current configuration must not rewrite historical transactions.

This applies to:

* product prices;
* branch price overrides;
* recipes;
* Sets;
* menu availability;
* permissions;
* salary configuration;
* payroll configuration;
* subscription configuration.

Current configuration determines future operations.

Historical transactions preserve the configuration and values applicable at the time of the transaction.

---

## 58. Audit Record Retention

Audit records remain available according to the business data lifecycle.

During the active business lifecycle:

* important audit records must remain available to authorized users;
* historical corrections must remain traceable;
* permission changes must remain traceable;
* transaction history must remain linked to its original actor and context.

After permanent business deletion, the business's audit history is removed according to the data deletion rules.

---

## 59. Business Rules Summary

| Area                     | Rule                                                             |
| ------------------------ | ---------------------------------------------------------------- |
| Audit                    | Important actions must be traceable                              |
| Actor                    | Employee or system identity must be preserved                    |
| Employee                 | Deactivation does not remove historical identity                 |
| Business                 | Business context must be preserved                               |
| Branch                   | Branch context must be preserved where applicable                |
| Device                   | Device context is preserved where relevant                       |
| Transaction              | Permanent transaction UUID remains traceable                     |
| Old value                | Preserve where historical change requires it                     |
| New value                | Preserve changed value                                           |
| Reason                   | Mandatory reasons remain in history                              |
| Permissions              | Permission changes are auditable                                 |
| Permission revert        | Creates a new event; previous event remains                      |
| Roles                    | Role configuration and assignment changes are auditable          |
| Orders                   | Historical transaction values are preserved                      |
| Cash                     | Cash operations require strong history                           |
| Handover                 | Previous and new cash sessions remain distinct                   |
| Corrections              | Original values remain available                                 |
| Correction authorization | Additional authorization is separately recorded                  |
| Inventory                | Important stock changes are traceable                            |
| Recipes                  | Recipe versions remain historical                                |
| Sets                     | Set configuration versions remain historical                     |
| Payments                 | Payment history is preserved                                     |
| Refunds                  | Refund history preserves reason and financial context            |
| Payroll                  | Historical payroll results preserve calculation context          |
| Reports                  | Previous report versions remain immutable                        |
| Notifications            | Important notification events may be retained                    |
| Offline                  | Offline events remain traceable after synchronization            |
| Sync                     | Accepted/rejected/conflicted events remain identifiable          |
| System events            | Automatic events are distinguishable from employee actions       |
| Audit access             | Permission and scope controlled                                  |
| Audit modification       | Not allowed through normal business UI                           |
| Audit deletion           | Not allowed through normal business UI                           |
| Subscription             | Audit history follows business lifecycle                         |
| Performance              | Audit processing must not unnecessarily slow critical operations |
| Historical integrity     | Current configuration must not rewrite historical transactions   |

---

## 60. Business Boundaries

The current Audit and Change History scope does not define:

* exact database audit table structure;
* exact event schema;
* exact audit event taxonomy;
* cryptographic signing of every audit record;
* blockchain-based audit storage;
* external SIEM integration;
* government audit integration;
* advanced forensic investigation tools;
* arbitrary user-configurable audit rules;
* external compliance certification.

These topics may be defined later in Architecture, Security, Database, and Operations documentation.

---

## 61. Related Documents

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
* `adr/ADR-001-Documentation-First.md`

---

