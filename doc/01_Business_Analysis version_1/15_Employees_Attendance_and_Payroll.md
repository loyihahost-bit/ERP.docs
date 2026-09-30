# Employees, Attendance and Payroll

**Document ID:** FF-BA-015
**Status:** Draft
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for employee management, branch assignment, attendance, salary configuration, payroll calculation, bonuses, and payroll-related permissions.

The system must support different employee compensation models while keeping employee identity, branch scope, permissions, attendance, and payroll information clearly separated.

---

## 2. Employee Model

An employee is a person who has an account in the FastFood ERP system and may perform authorized business operations.

An employee may have:

* a personal account;
* one or more roles;
* branch assignments;
* branch-specific permissions;
* attendance records;
* salary configuration;
* payroll records.

Employee identity must remain stable throughout the employee's operational history.

---

## 3. Employee Identity

Each employee must have an identifiable account.

Employees must use their own accounts when performing business operations.

Shared employee accounts should not be used for normal operational activities because important actions must be attributable to a specific employee.

Employee identity must remain associated with historical records such as:

* orders;
* payments;
* refunds;
* cash sessions;
* handovers;
* inventory operations;
* attendance;
* payroll operations;
* permission changes.

---

## 4. Employee Lifecycle

Employees may have an active or inactive status.

When an employee leaves the business or should no longer access the system, the employee should normally be deactivated rather than physically deleted.

Deactivation must prevent normal future access while preserving historical records.

Historical transactions must continue to identify the original employee.

---

## 5. Employee Creation

Authorized users may create employees according to their permissions.

The employee creation process may include:

* employee identity;
* account credentials;
* assigned role;
* branch assignment;
* permission configuration;
* salary configuration;
* attendance-related configuration.

An employee may only be created within the business and branch scope permitted to the creating user.

---

## 6. Manager Employee-Creation Permission

A Manager does not automatically have permission to create employees.

The Owner may grant employee-management permission to a Manager.

A Manager with the appropriate permission may create employees only within the scope allowed by the Owner's permission configuration.

A Manager must not use employee-management access to grant themselves broader authority.

---

## 7. Employee Roles

Employees may be assigned configurable roles.

Examples include:

* Manager;
* Cashier;
* Waiter;
* Cook;
* other business-defined roles.

The role itself provides a reusable permission configuration.

The actual effective permissions of an employee may differ from the role's default permissions because individual overrides are supported.

Detailed role and permission rules are defined in:

`05_Users_Roles_and_Permissions.md`

---

## 8. Branch Assignment

An employee may be assigned to:

* one branch;
* multiple branches;
* business-wide scope where explicitly authorized.

Branch assignment determines where the employee may operate.

Branch assignment and permission scope are related but are not identical.

An employee assigned to multiple branches may have different permissions in each branch.

---

## 9. Branch-Specific Employee Configuration

The same employee may have different operational permissions by branch.

For example:

```text id="xj4s8q"
Employee
├── Branch A → Cashier permissions
└── Branch B → Waiter permissions
```

The system must preserve the branch context of employee actions.

Employee actions must not be attributed to the wrong branch because the employee works in multiple locations.

---

## 10. Attendance Model

Attendance records represent when an employee is working or present according to the business's configured attendance process.

Attendance must remain associated with:

* employee;
* branch where applicable;
* date/time;
* attendance state;
* responsible action or system event.

The attendance model must remain practical for restaurant operations.

---

## 11. Role-Based Attendance Rules

Attendance behavior may depend on the employee's assigned role.

The business may define attendance rules according to employee role.

For example, different operational roles may use different attendance expectations.

The system must therefore not assume that every employee follows exactly the same attendance configuration.

---

## 12. Attendance History

Attendance records must be retained as historical business data.

The system should preserve:

* employee;
* branch;
* date;
* time;
* attendance state;
* applicable role or work configuration;
* correction information where applicable.

Historical attendance should not be silently overwritten.

---

## 13. Attendance Corrections

If an attendance record requires correction, the system should preserve the original state and the correction history.

Corrections should identify:

* original value;
* new value;
* responsible employee;
* correction time;
* reason/comment where required.

The exact attendance correction permission is determined by the permission model.

---

## 14. Salary Model

The system supports multiple employee compensation models.

Supported models are:

1. Fixed
2. Percentage
3. Shift
4. Hybrid
5. Daily Pay
6. Bonuses

These models may be used according to the business's requirements and employee configuration.

---

## 15. Fixed Salary

A fixed salary represents a predetermined salary amount for the applicable payroll period.

The employee's salary configuration defines the applicable fixed amount.

The system must preserve the salary configuration used for a payroll calculation.

Changing the current salary must not silently rewrite historical payroll results.

---

## 16. Percentage-Based Pay

Percentage-based compensation calculates employee pay based on an applicable percentage value.

The business must define what the percentage applies to within the supported payroll configuration.

The calculated result must be preserved as part of the payroll record.

Historical payroll must retain the values used during its calculation.

---

## 17. Shift-Based Pay

Shift-based compensation calculates pay according to completed or applicable work shifts.

The payroll calculation must use the relevant shift/attendance information.

A shift-based employee's payroll must preserve the information needed to understand how the amount was calculated.

---

## 18. Hybrid Compensation

Hybrid compensation combines multiple supported salary components.

For example, an employee may have:

* a fixed base amount;
* plus a percentage-based component;
* plus applicable bonuses.

The system must preserve each applicable component separately enough to explain the final payroll result.

---

## 19. Daily Pay

Daily pay compensates an employee according to applicable worked days.

The calculation must use the attendance information required by the business's configuration.

Historical payroll must preserve the number of applicable days and the resulting amount.

---

## 20. Bonuses

The system supports employee bonuses.

Bonuses may be added to an employee's payroll according to authorized business operations.

A bonus record should preserve:

* employee;
* amount;
* applicable payroll period;
* reason/comment;
* responsible user;
* timestamp.

A bonus must not silently modify the employee's base salary configuration.

---

## 21. Salary Configuration

Salary configuration is separate from employee permissions.

An employee may have permission to perform operational tasks without having permission to modify their own salary.

Employees must not be able to use normal operational access to increase their own compensation.

Salary changes must be permission-controlled.

---

## 22. Salary Changes

Authorized users may change an employee's salary configuration.

A salary change should preserve:

* previous configuration;
* new configuration;
* effective date;
* responsible user;
* reason/comment where required.

Historical payroll calculations must continue to use the configuration applicable at the relevant period.

---

## 23. Payroll Period

Payroll is calculated for a defined payroll period.

The system must associate payroll results with:

* employee;
* branch or business scope where applicable;
* payroll period;
* salary configuration;
* attendance information;
* bonuses;
* resulting amount.

The exact payroll period configuration may be determined by the business.

---

## 24. Payroll Calculation

A payroll calculation may combine:

* base salary;
* attendance;
* worked shifts;
* percentage-based compensation;
* daily pay;
* bonuses.

The applicable components depend on the employee's configured compensation model.

The system must preserve the calculation result and the underlying values required to explain it.

---

## 25. Payroll Finalization

Once payroll is finalized, its historical result must be preserved.

A later salary configuration change must not automatically recalculate finalized historical payroll.

If a finalized payroll result requires correction, the correction must be explicitly recorded.

The system must preserve the original payroll result.

---

## 26. Payroll Corrections

Payroll corrections must be traceable.

A correction should preserve:

* original payroll value;
* corrected value;
* reason;
* responsible user;
* timestamp;
* applicable employee;
* payroll period.

The system must not silently overwrite the original payroll result.

---

## 27. Employee Payroll Access

Payroll information is sensitive business information and must be permission-controlled.

Employees should not automatically have access to payroll information simply because they can log in.

The Owner may grant payroll-related access according to business requirements.

Managers may receive payroll permissions only when explicitly authorized.

---

## 28. Salary and Branch Scope

Salary configuration may be associated with the employee's business or applicable branch scope.

Where an employee works across multiple branches, the system must preserve the relevant scope of the compensation configuration.

The system must not accidentally apply a branch-specific salary configuration to another branch.

---

## 29. Employee Transfer Between Branches

An employee may be assigned to an additional branch or removed from a branch according to authorized management actions.

Changing branch assignment must not delete historical attendance or payroll records.

Historical records must remain associated with the branch context in which they occurred.

---

## 30. Employee Deactivation and Payroll

When an employee is deactivated:

* normal login access is blocked;
* future operational activity is prevented;
* historical orders remain associated with the employee;
* historical attendance remains available;
* historical payroll remains available.

Outstanding payroll obligations may still require authorized processing according to the business's payroll rules.

---

## 31. Payroll Notifications

Salary-related notifications are supported.

The system may generate a **salary due** alert when a configured payroll obligation becomes due.

Notifications must respect:

* business scope;
* branch scope;
* notification permissions.

The exact notification timing is a configurable business rule and is not fixed in this document.

---

## 32. Employee and Cash Operations

Employees involved in cash operations must use their own accounts.

Cashier identity must remain associated with:

* cash session;
* payment operations;
* cash handover;
* cash closing;
* discrepancy records.

Changing the responsible cashier does not change the employee's historical identity.

Detailed cash rules are defined in:

`09_Cash_Register_and_Cash_Sessions.md`

and

`10_Shift_Handover.md`.

---

## 33. Employee and Inventory Operations

Employees performing inventory operations must have the appropriate inventory permissions.

Inventory actions must preserve employee identity.

Examples include:

* purchase entry;
* stock adjustment;
* stock count;
* semi-finished preparation;
* inventory correction.

Detailed inventory requirements are defined in:

`11_Inventory_and_Warehouse.md`

---

## 34. Employee and Order Operations

Employee identity must be retained for important order operations.

Examples include:

* order creation;
* order modification;
* order acceptance;
* payment;
* discount;
* refund;
* cancellation;
* handover-related actions.

This supports operational accountability.

---

## 35. Employee and Offline Operation

Authorized employees may perform supported operations offline through trusted devices.

Offline authorization must remain tied to:

* employee;
* device;
* business;
* branch;
* permissions;
* applicable authorization period.

An employee must not gain additional permissions merely because the device is offline.

---

## 36. Permission Changes and Payroll

Permission changes do not automatically change an employee's salary.

Salary configuration and authorization are separate business concepts.

For example:

```text id="k2v7ca"
Employee
├── Role / Permissions
└── Salary Configuration
```

Changing one does not automatically modify the other.

---

## 37. Employee History

The system must preserve historical employee identity even when:

* role changes;
* permissions change;
* branch assignment changes;
* salary changes;
* employee becomes inactive.

Historical business records must continue to reference the employee responsible for the original operation.

---

## 38. Auditability

Important employee, attendance, salary, and payroll changes must be traceable.

The system should preserve:

* actor;
* affected employee;
* branch;
* previous value;
* new value;
* action type;
* reason/comment where required;
* timestamp.

No important employee or payroll configuration should be silently overwritten.

---

## 39. Subscription and Employee Limits

Employee creation and management are subject to the business's subscription limits.

The subscription may define the maximum number of employees allowed.

If the employee limit is reached, creation of additional employees must be blocked until the business has sufficient subscription capacity.

Existing historical employee data must not be deleted simply because a tariff is downgraded.

---

## 40. Permissions and Subscription

Employee-related functionality is controlled by two independent layers:

1. subscription entitlement;
2. employee permissions.

A user must satisfy both conditions to perform a protected operation.

Examples include:

* employee creation;
* salary management;
* payroll management;
* attendance management;
* employee permission management.

---

## 41. Performance Requirements

Employee, attendance, and payroll operations must remain lightweight.

The system should avoid unnecessary calculations during normal POS operations.

Payroll calculations may process larger datasets, but must not negatively affect normal restaurant operations.

The system should remain suitable for the project's lightweight hardware requirements.

---

## 42. Business Rules Summary

| Area                 | Rule                                        |
| -------------------- | ------------------------------------------- |
| Employee identity    | Individual account                          |
| Employee deletion    | Deactivation preferred                      |
| Roles                | Configurable                                |
| Branch assignment    | One or multiple branches                    |
| Branch permissions   | Can differ by branch                        |
| Attendance           | Role-aware                                  |
| Salary models        | Fixed, percentage, shift, hybrid, daily pay |
| Bonuses              | Supported                                   |
| Salary changes       | Permission-controlled                       |
| Payroll              | Period-based                                |
| Payroll history      | Preserved                                   |
| Payroll corrections  | Must be traceable                           |
| Salary access        | Permission-controlled                       |
| Manager access       | Only when explicitly authorized             |
| Cash operations      | Employee identity preserved                 |
| Inventory operations | Permission-controlled and auditable         |
| Offline operation    | Supported for authorized trusted devices    |
| Employee limits      | Controlled by subscription                  |
| Subscription         | Separate from employee permissions          |
| Audit                | Important changes preserved                 |

---

## 43. Business Boundaries

The current Employees, Attendance and Payroll scope does **not** define:

* biometric attendance hardware;
* facial recognition;
* GPS-based employee tracking;
* automatic tax/payroll filing;
* government payroll integration;
* pension calculations;
* insurance calculations;
* employee benefits management;
* loans or salary advances;
* recruitment;
* applicant tracking;
* employee performance scoring;
* complex HR management.

These capabilities may be considered in future documentation if business requirements justify them.

---

## 44. Related Documents

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
* `16_Reports_and_Dashboards.md`
* `17_Notifications_and_Alerts.md`
* `18_Audit_and_Change_History.md`
* `20_Business_Rules.md`

