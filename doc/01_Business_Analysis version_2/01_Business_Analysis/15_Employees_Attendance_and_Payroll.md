# Employees, Attendance and Payroll

**Document ID:** FF-BA-015
**Status:** Accepted
**Version:** 2.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for:

* employee management;
* employee identity and lifecycle;
* branch assignment;
* role and permission context;
* attendance;
* salary configuration;
* payroll calculation;
* bonuses;
* payroll corrections;
* employee-related notifications;
* employee and payroll auditability.

The system must keep the following concepts separate while allowing them to work together:

```text
Employee Identity
      +
Role / Permissions
      +
Branch Scope
      +
Attendance
      +
Salary Configuration
      +
Payroll
```

Changing one of these concepts must not silently rewrite the others.

---

## 2. Employee Model

An employee is a person with an individual account within a Business.

An employee may have:

* one individual account;
* one or more roles;
* one or more branch assignments;
* branch-specific permissions;
* attendance records;
* salary configuration;
* payroll records;
* historical operational activity.

Employee identity must remain stable throughout the employee's operational history.

---

## 3. Individual Employee Identity

Employees must normally use their own accounts for operational activities.

Shared accounts are not permitted for normal employee operations because important actions must remain attributable to a specific employee.

Employee identity must remain associated with historical records such as:

* orders;
* order modifications;
* payments;
* discounts;
* refunds;
* cash sessions;
* shift handovers;
* inventory operations;
* attendance;
* payroll;
* permission changes;
* corrections;
* audit records.

---

## 4. Employee Lifecycle

An employee may have an active or inactive status.

Normal lifecycle:

```text
Created
   ↓
Active
   ↓
Inactive
```

When an employee leaves the Business or should no longer access the system, the employee should normally be deactivated rather than physically deleted.

Deactivation must:

* block normal future access;
* prevent new operational actions;
* preserve historical records;
* preserve the employee's identity in reports and audit history.

Deactivation must not delete historical attendance, payroll, orders, payments, or other business records.

---

## 5. Employee Creation

Authorized users may create employees within their permitted Business and Branch scope.

Employee creation may include:

* employee identity;
* account configuration;
* role assignment;
* branch assignment;
* permission configuration;
* salary configuration;
* attendance configuration.

The creator must not be able to grant authority beyond their own permitted management scope.

Employee creation is also subject to the Business subscription's employee capacity.

---

## 6. Manager Employee-Creation Authority

A Manager does not automatically have permission to create employees.

The Owner may grant employee-management permissions to a Manager.

A Manager with employee-creation permission may create employees only within:

* the Business they belong to;
* the Branch scope they are authorized to manage;
* the employee-management permissions granted to them.

A Manager must not use employee-management access to:

* grant themselves additional authority;
* grant permissions they are not authorized to delegate;
* bypass subscription limits.

---

## 7. Employee Roles

Employees may be assigned configurable roles.

Examples include:

* Owner;
* Manager;
* Cashier;
* Waiter;
* Cook;
* other business-defined roles.

A role provides a reusable permission configuration.

The employee's effective permissions are determined through:

`Role Permission + Employee Override + Branch Scope + Subscription Entitlement`

Detailed permission rules are defined in:

`05_Users_Roles_and_Permissions.md`

---

## 8. Employee and Permission Separation

Employee identity, role, and salary are separate concepts.

For example:

```text
Employee
├── Role / Permissions
├── Branch Scope
├── Attendance Configuration
└── Salary Configuration
```

Changing an employee's role does not automatically change salary.

Changing salary does not automatically grant permissions.

Changing branch assignment does not automatically grant permissions for the new branch.

---

## 9. Branch Assignment

An employee may be assigned to:

* one Branch;
* multiple Branches;
* Business-wide scope where explicitly authorized.

Branch assignment determines where the employee may operate.

Branch assignment alone does not grant every permission within that Branch.

An employee must satisfy both:

1. Branch Scope;
2. required Permission.

---

## 10. Branch-Specific Employee Configuration

The same employee may have different permissions in different Branches.

Example:

```text
Employee
├── Branch A → Cashier permissions
├── Branch B → Waiter permissions
└── Branch C → No operational access
```

The system must preserve the Branch context for every employee action.

An employee working in multiple Branches must not have an action incorrectly attributed to another Branch.

---

## 11. Employee Branch Changes

Authorized management users may:

* assign an employee to a new Branch;
* remove an employee from a Branch;
* modify the employee's permissions for a Branch.

Changing Branch assignment must not delete historical records.

Historical records must remain associated with the Branch where the original operation occurred.

---

# Attendance

## 12. Attendance Model

Attendance records represent employee work/presence according to the Business's configured attendance process.

Attendance must remain associated with:

* Employee;
* Branch where applicable;
* date;
* time;
* attendance state;
* applicable work configuration;
* responsible action or system event.

The attendance process must remain practical for restaurant operations.

---

## 13. Role-Aware Attendance

Attendance configuration may differ by employee role.

The system must not assume that every employee follows exactly the same attendance rules.

For example, the Business may configure different attendance expectations for:

* Cashiers;
* Waiters;
* Cooks;
* Managers;
* other employee types.

The exact operational rules are configurable rather than permanently hard-coded to one role.

---

## 14. Attendance History

Attendance records are historical business data.

The system must preserve, where applicable:

* Employee;
* Branch;
* date;
* start/end time;
* attendance state;
* applicable work configuration;
* correction information.

Historical attendance must not be silently overwritten.

---

## 15. Attendance Corrections

Attendance corrections must preserve the original record.

A correction should contain:

* original value/state;
* corrected value/state;
* responsible employee;
* correction timestamp;
* reason/comment where required.

The correction must be auditable.

The exact correction permission is determined by the established permission model.

---

## 16. Attendance and Payroll

Attendance may be used as an input to payroll calculations.

Depending on the employee's compensation model, payroll may use:

* worked days;
* completed shifts;
* applicable attendance periods;
* other attendance-derived values.

The attendance record used for payroll must remain identifiable.

Changing attendance after payroll finalization must not silently rewrite the finalized payroll result.

If a finalized payroll requires an attendance-related correction, the payroll correction process must be used.

---

# Salary Configuration

## 17. Supported Compensation Models

The system supports the following compensation models:

1. Fixed Salary
2. Percentage-Based Pay
3. Shift-Based Pay
4. Hybrid Compensation
5. Daily Pay
6. Bonuses

An employee may use one supported model or a configured combination where the Business rules allow it.

The model used for a payroll calculation must be preserved in the payroll history.

---

## 18. Fixed Salary

Fixed salary represents a predetermined amount for the applicable payroll period.

The salary configuration must preserve:

* amount;
* applicable scope;
* effective period/date;
* responsible configuration change.

Changing the current fixed salary must not modify historical payroll results.

---

## 19. Percentage-Based Pay

Percentage-based compensation calculates employee pay using a configured percentage.

The Business must define the base against which the percentage is calculated.

The calculation must preserve the values used, including:

* applicable percentage;
* calculation base;
* resulting amount;
* payroll period.

Historical payroll must not depend on the current percentage configuration.

---

## 20. Shift-Based Pay

Shift-based compensation calculates pay according to applicable completed/worked shifts.

The calculation must preserve the relevant shift information.

Where the employee works multiple Branches, the payroll calculation must retain the Branch context required by the applicable salary configuration.

---

## 21. Daily Pay

Daily pay compensates an employee according to applicable worked days.

The calculation must preserve:

* applicable daily rate;
* number of payable days;
* attendance information used;
* resulting amount.

Historical payroll must remain unchanged when the current daily rate changes.

---

## 22. Hybrid Compensation

Hybrid compensation combines multiple supported salary components.

Example:

```text
Fixed Base
   +
Percentage Component
   +
Applicable Bonuses
   =
Payroll Result
```

Each component must remain identifiable enough to explain the final payroll result.

---

## 23. Bonuses

Bonuses are separate payroll components.

A bonus may be added by an authorized user.

A bonus record must preserve:

* Employee;
* amount;
* payroll period;
* reason/comment;
* responsible user;
* timestamp;
* applicable Branch or Business scope where relevant.

A bonus must not silently modify the employee's base salary configuration.

---

## 24. Salary Configuration Scope

Salary configuration may be:

* Business-level;
* Branch-specific;
* employee-specific;

according to the applicable Business configuration.

If an employee works across multiple Branches, the system must not accidentally apply one Branch-specific salary configuration to another Branch.

The applicable salary configuration must be resolved according to its defined scope and effective period.

---

## 25. Salary Changes

Authorized users may modify salary configuration.

A salary change must preserve:

* previous configuration;
* new configuration;
* effective date;
* responsible user;
* reason/comment where required;
* applicable Branch/Business scope.

A salary change applies to the relevant future payroll calculation according to its effective date.

It must not silently recalculate finalized historical payroll.

---

## 26. Employee Salary Self-Modification

An employee must not be able to increase or otherwise modify their own compensation through ordinary operational permissions.

Salary management requires explicit salary/payroll permission.

Operational permissions such as:

* POS access;
* inventory access;
* order processing;

do not automatically grant salary-management authority.

---

# Payroll

## 27. Payroll Period

Payroll is calculated for a defined payroll period.

Each payroll result must be associated with:

* Employee;
* payroll period;
* applicable Branch/Business scope;
* salary configuration;
* attendance information where applicable;
* bonuses;
* calculation result.

The Business may configure the payroll period according to its operating requirements.

---

## 28. Payroll Calculation

Payroll may combine:

* fixed salary;
* percentage-based compensation;
* shift-based compensation;
* daily pay;
* attendance-derived values;
* bonuses.

The applicable components depend on the employee's salary configuration.

The payroll result must preserve the inputs required to explain the calculation.

---

## 29. Payroll Calculation Snapshot

When payroll is calculated, the system must retain the relevant calculation snapshot.

The snapshot should preserve:

* salary configuration used;
* effective salary values;
* attendance values used;
* shift values used;
* percentage values;
* calculation base;
* bonuses;
* resulting amount.

Later configuration changes must not alter the historical calculation snapshot.

---

## 30. Payroll Finalization

Payroll may move through a lifecycle such as:

```text
Draft / Calculating
       ↓
Calculated
       ↓
Finalized
```

Once payroll is finalized, its result becomes historical financial/business data.

A finalized payroll result must not be silently recalculated because of later:

* salary changes;
* attendance changes;
* role changes;
* branch changes;
* bonus configuration changes.

---

## 31. Payroll Corrections

If finalized payroll requires correction, the original result must remain available.

A correction must preserve:

* original payroll result;
* corrected result;
* reason;
* responsible user;
* timestamp;
* affected Employee;
* payroll period.

The correction must be recorded as a separate historical operation rather than silently overwriting the original result.

---

## 32. Payroll Access

Payroll information is restricted business information.

Access is permission-controlled.

An employee does not automatically gain access to payroll information simply because they can log into the ERP.

The Owner may grant payroll-related permissions.

Managers may receive payroll access only when explicitly authorized.

Employees must not automatically see other employees' salary information.

---

## 33. Employee Payroll Access vs Self-Access

The system may distinguish between:

* viewing an employee's own permitted payroll information;
* managing payroll for other employees.

These are separate permission concepts.

A user with permission to view their own payroll information must not automatically receive permission to modify or view other employees' payroll information.

---

## 34. Payroll and Branch Scope

Payroll records must preserve the applicable Branch/Business context.

Where an employee works across multiple Branches, the system must distinguish compensation and attendance information according to the configured salary scope.

A Branch-specific payroll configuration must not be applied to another Branch without an applicable rule.

---

## 35. Employee Deactivation and Payroll

When an employee is deactivated:

* normal login access is blocked;
* future operational activity is prevented;
* historical orders remain associated with the employee;
* historical attendance remains available;
* historical payroll remains available.

Outstanding payroll obligations may still be processed by authorized users.

Deactivation must not delete historical compensation information.

---

# Employee Operational Context

## 36. Employee and Cash Operations

Employees involved in cash operations must use their own accounts.

Cashier identity must remain associated with:

* cash session;
* payments;
* cash closing;
* handover;
* discrepancy;
* applicable corrections.

Cashier transition does not change the historical identity of previous transactions.

Detailed rules are defined in:

`09_Cash_Register_and_Cash_Sessions.md`

and

`10_Shift_Handover.md`.

---

## 37. Employee and Order Operations

Employee identity must be preserved for important order operations, including:

* order creation;
* order modification;
* order acceptance;
* payment;
* discount;
* cancellation;
* refund;
* handover-related actions.

This provides operational accountability.

---

## 38. Employee and Inventory Operations

Inventory operations require the appropriate inventory permissions.

Employee identity must be preserved for operations such as:

* purchase entry;
* stock adjustment;
* inventory count;
* inventory correction;
* semi-finished production;
* other authorized inventory operations.

Detailed requirements are defined in:

`11_Inventory_and_Warehouse.md`

---

## 39. Employee and Offline Operations

Authorized employees may perform supported operations offline through trusted devices.

Offline authorization must remain bound to:

* Employee;
* Device;
* Business;
* Branch;
* Permissions;
* Subscription entitlement;
* authorization validity period.

Offline operation must not grant additional authority.

A device being trusted does not independently grant employee permissions.

---

# Notifications

## 40. Salary Due Notification

The system supports a **salary due** notification/alert.

The notification may be generated when a configured payroll obligation becomes due.

The notification must respect:

* Business scope;
* Branch scope;
* notification permissions.

The exact timing and threshold are configurable business rules.

---

# Subscription and Limits

## 41. Employee Subscription Limits

Employee creation and management are subject to subscription capacity.

A tariff may define:

* maximum employee count;
* enabled employee-related functions;
* other applicable limits.

When the employee limit is reached, creating an additional employee must be blocked unless sufficient subscription capacity becomes available.

---

## 42. Subscription Expiry

Subscription entitlement and employee permission are independent controls.

When a Business subscription expires:

* modifying functionality is restricted according to subscription rules;
* existing data remains viewable according to the subscription lifecycle;
* employee history remains preserved;
* authorized exports remain available according to subscription rules.

Offline operation must not bypass an expired subscription.

---

## 43. Subscription Downgrade

A subscription downgrade must not silently delete historical employee data.

If the new tariff has a lower employee limit than the current number of employees, the system must prevent further employee creation beyond the permitted capacity.

Existing historical records remain preserved.

The exact handling of active employees exceeding a new tariff capacity is governed by subscription rules rather than destructive deletion.

---

# Audit and Historical Integrity

## 44. Employee History

The system must preserve historical employee identity even when:

* role changes;
* permissions change;
* Branch assignment changes;
* salary changes;
* attendance is corrected;
* employee becomes inactive.

Historical business records must continue to reference the employee responsible for the original operation.

---

## 45. Auditability

Important employee, attendance, salary, and payroll changes must be traceable.

Audit information should include:

* actor;
* affected Employee;
* Business;
* Branch;
* action type;
* previous value/state;
* new value/state;
* reason/comment where required;
* timestamp.

Important configuration changes must not be silently overwritten.

---

## 46. Historical Payroll Integrity

Historical payroll must retain the configuration and inputs used to produce the result.

Current:

* salary;
* role;
* permissions;
* Branch assignment;
* attendance configuration;

must not retroactively rewrite finalized payroll.

If historical payroll must change, an explicit correction must be recorded.

---

# Performance

## 47. POS Performance

Employee and payroll functionality must not introduce unnecessary overhead into POS operations.

Normal POS operations must not require:

* loading payroll data;
* recalculating historical payroll;
* loading unrelated attendance data;
* loading unnecessary employee records.

Employee and permission checks used by POS must remain lightweight.

---

## 48. Payroll Performance

Payroll calculations may process larger datasets than ordinary POS operations.

However, payroll processing must not unnecessarily block normal restaurant operations.

The system should support efficient calculation for:

* employee attendance;
* shifts;
* salary components;
* bonuses;
* payroll periods.

---

# 49. Business Rules Summary

| Area                        | Rule                                                 |
| --------------------------- | ---------------------------------------------------- |
| Employee identity           | Individual account                                   |
| Shared accounts             | Not permitted for normal operational activity        |
| Employee deletion           | Deactivation preferred                               |
| Employee history            | Preserved                                            |
| Roles                       | Configurable                                         |
| Effective permissions       | Role + Override + Branch Scope + Subscription        |
| Branch assignment           | One or multiple Branches                             |
| Branch permissions          | May differ by Branch                                 |
| Attendance                  | Role-aware and historical                            |
| Attendance correction       | Original state preserved                             |
| Salary models               | Fixed, Percentage, Shift, Hybrid, Daily Pay          |
| Bonuses                     | Supported as separate payroll components             |
| Salary changes              | Permission-controlled and effective-date based       |
| Self salary modification    | Not allowed through ordinary operational permissions |
| Payroll                     | Period-based                                         |
| Payroll snapshot            | Required for historical integrity                    |
| Payroll finalization        | Historical result preserved                          |
| Payroll correction          | Separate and auditable                               |
| Payroll access              | Permission-controlled                                |
| Employee deactivation       | Blocks future normal access, preserves history       |
| Cash operations             | Employee identity preserved                          |
| Inventory operations        | Permission-controlled and auditable                  |
| Offline employee operations | Trusted-device authorization required                |
| Salary due                  | Notification supported                               |
| Employee limit              | Subscription-controlled                              |
| Subscription                | Independent from employee permissions                |
| Audit                       | Important changes preserved                          |
| Performance                 | Payroll must not slow normal POS operations          |

---

# 50. Business Boundaries

The current Employees, Attendance and Payroll scope does **not** define:

* biometric attendance hardware;
* facial recognition;
* GPS-based employee tracking;
* government payroll filing;
* government payroll API integration;
* pension calculations;
* insurance calculations;
* employee benefits management;
* salary advances;
* employee loans;
* recruitment;
* applicant tracking;
* employee performance scoring;
* complex HR management;
* full tax/payroll compliance engine.

These capabilities may be considered in future documentation if business requirements justify them.

---

## 51. Related Documents

* `01_Product_Overview.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `06_Authentication_and_Trusted_Devices.md`
* `07_Offline_Operation_and_Synchronization.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `10_Shift_Handover.md`
* `11_Inventory_and_Warehouse.md`
* `13_Menu_and_Pricing.md`
* `14_Payments_Discounts_and_Refunds.md`
* `16_Reports_and_Dashboards.md`
* `17_Notifications_and_Alerts.md`
* `18_Audit_and_Change_History.md`
* `20_Business_Rules.md`

