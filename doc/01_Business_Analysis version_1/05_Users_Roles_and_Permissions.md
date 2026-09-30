# Users, Roles and Permissions

**Document ID:** BA-05
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

This document defines the business rules for users, employees, roles, permissions, permission overrides, and branch-level access in FastFood ERP.

The permission model must provide strong access control while remaining understandable and practical for business users.

The system must support both standardized role permissions and individual employee-specific permissions.

## 2. User and Employee Model

An employee represents a person working for a business.

An employee has an identity within the business and may be assigned to one or more branches.

Employee access is determined by:

**Employee Identity + Role + Permissions + Branch Scope**

An employee account must not automatically receive unrestricted access simply because the employee belongs to the business.

## 3. Platform and Business Roles

The system distinguishes between platform-level and business-level roles.

### Platform-Level

* Super Admin

### Business-Level

Examples include:

* Owner;
* Manager;
* Cashier;
* Waiter;
* Cook;
* Other custom roles.

Business roles are configurable through the permission system.

## 4. Super Admin

Super Admin is the highest platform-level role.

Super Admin may:

* create businesses;
* configure tariffs;
* configure tariff limits;
* manage platform-level functionality;
* perform authorized platform administration.

Super Admin is separate from the normal business role hierarchy.

Super Admin permissions must not be used as a reason to automatically grant operational permissions to business employees.

## 5. Owner

Owner is a protected business-level role.

Multiple Owners may exist within the same business, subject to the active tariff limit.

Owners may manage:

* employees;
* roles;
* permissions;
* branches;
* recipes;
* menu;
* inventory;
* prices;
* reports;
* payroll;
* other business functions according to the permission model.

Other employees must not be able to:

* promote themselves to Owner;
* assign themselves Owner permissions;
* remove or reduce an Owner's protected privileges.

## 6. Manager

Manager is a configurable business management role.

A Manager may receive selected permissions such as:

* employee management;
* report access;
* inventory management;
* cash correction;
* branch management;
* other authorized functions.

Manager capabilities are determined by assigned permissions and branch scope.

A Manager cannot grant a permission that the Manager does not possess.

## 7. Employee Roles

The system supports predefined and custom business roles.

Examples include:

* Cashier;
* Waiter;
* Cook;
* Manager;
* other custom roles.

The role itself represents a reusable permission configuration.

Employees assigned to the same role may still have individual permission overrides.

## 8. Role Permission

A Role Permission defines the default access granted to employees assigned to that role.

For example:

**Cashier Role → Create Order = Allowed**

This becomes the default permission for employees assigned to the Cashier role.

Role permissions are reusable and reduce the need to configure every employee individually.

## 9. Employee Permission Override

An individual employee may receive a permission override.

An override may:

* grant a permission that the role normally does not have;
* remove a permission that the role normally has.

The override applies only to the selected employee and relevant scope.

This allows controlled customization without creating unnecessary roles.

## 10. Branch Scope

Permissions may be limited by branch.

An employee may have:

* permission in one branch;
* permission in several selected branches;
* business-wide permission where explicitly authorized.

The effective permission must always consider the branch where the operation is being performed.

## 11. Effective Permission

The effective permission for an operation is determined by the applicable:

1. Employee identity;
2. Role;
3. Role permissions;
4. Employee overrides;
5. Branch scope;
6. Subscription feature availability.

The system must evaluate all applicable layers before allowing an operation.

Conceptually:

**Effective Access = Subscription Eligibility + Permission + Branch Scope**

## 12. Permission Categories

Permissions should be organized into understandable functional groups.

Possible groups include:

* Business Management;
* Branch Management;
* Employee Management;
* Role and Permission Management;
* POS;
* Orders;
* Cash Register;
* Cash Session;
* Inventory;
* Warehouse;
* Recipes;
* Menu;
* Pricing;
* Payments;
* Refunds;
* Reports;
* Payroll;
* Expenses;
* Notifications;
* Audit;
* Subscription-related visibility.

The exact permission catalog may grow as the system expands.

## 13. Recipe Permissions

Recipe access is a dedicated permission area.

Recipe permissions must be independent from general product visibility.

For example, an employee may be allowed to:

* see menu products;

while not being allowed to:

* see recipe components.

Recipe visibility must therefore be explicitly controlled.

## 14. Role Creation

Authorized users may create custom roles if they have the required permission.

A role may be created from scratch or based on an existing permission configuration.

The resulting role must remain editable.

## 15. Role Cloning from Employee Permissions

A role may be created based on an existing employee's permission configuration.

This operation copies the current permission configuration as a starting point.

After copying, the new role can be edited.

Permissions may be:

* added;
* removed;
* changed.

The cloned role is therefore not permanently linked to the original employee.

## 16. Role Cloning from Existing Roles

A role may also be created from an existing role configuration.

The copied configuration becomes the initial state of the new role.

Subsequent changes to the source role must not silently modify the cloned role.

The new role becomes an independent permission configuration.

## 17. Employee Creation

An authorized user may create an employee if:

* the user has employee-management permission;
* the business has not reached its employee tariff limit;
* required employee information is provided.

During employee creation, the administrator may select:

* role;
* branch assignment;
* permission configuration;
* branch-specific permissions.

## 18. Manager Employee-Creation Restriction

A Manager may create employees only when the Owner has granted the Manager the required permission.

Having the Manager role alone does not automatically provide employee-creation permission.

## 19. Permission Granting Rule

A user may grant only permissions that the user themselves possesses.

A user cannot grant a permission above their own authority.

For example:

If Manager A does not possess the `Manage Payroll` permission, Manager A cannot grant `Manage Payroll` to another employee.

This rule applies regardless of the target employee's role.

## 20. Privilege Escalation Prevention

The permission model must prevent employees from using permission configuration to elevate themselves.

An employee must not be able to:

* grant themselves new permissions;
* grant themselves broader branch scope;
* elevate themselves to Owner;
* create a role that gives themselves unauthorized privileges.

Any permission-management action must therefore evaluate the actor's own effective permissions.

## 21. Owner Protection

Owner is a protected business role.

Business employees cannot use normal role or permission-management functionality to:

* remove Owner status from another Owner;
* reduce protected Owner permissions;
* grant themselves Owner status;
* create an equivalent unrestricted privilege set for themselves.

Owner protection is separate from ordinary employee permission customization.

## 22. Permission Changes

Permission changes must be explicit.

A permission change event must record at minimum:

* actor;
* target employee or role;
* business;
* branch scope;
* permission;
* previous value;
* new value;
* timestamp;
* change type.

The system must not silently replace permission history.

## 23. Latest Explicit Command Wins

For a specific permission and scope, the latest explicit permission command determines the current effective state.

Example:

1. 10:00 — Recipe View = OFF
2. 11:00 — Recipe View = ON
3. 12:00 — Recipe View = OFF

The effective state after 12:00 is:

**Recipe View = OFF**

The previous states remain in history.

## 24. Permission Revert

Reverting a previous permission change does not delete the history.

A revert creates a new permission event.

Example:

1. 10:00 — Recipe View = OFF
2. 11:00 — Ali = ON
3. 12:00 — Ali = OFF
4. 13:00 — Revert the 11:00 change

The system records the 13:00 revert as a new event.

The original 11:00 and 12:00 events remain unchanged.

## 25. Permission Change Scope

When changing permissions, the authorized user may apply the change to:

* all employees assigned to a role;
* selected employees;
* selected branches where permitted.

The scope of the change must be explicit.

A change intended for one employee must not silently affect other employees.

## 26. Multiple Employee Selection

The permission-management interface may allow an administrator to select multiple employees.

If a permission is changed for multiple selected employees, the action is treated as one explicit administrative command with each affected target recorded in the audit history.

The system must preserve which employees were affected.

## 27. Permission Conflict Resolution

When multiple permission sources apply to the same employee and permission, the system must use a deterministic rule.

For explicit permission commands, the latest applicable command wins.

The effective state must always be explainable through the permission history.

The system must avoid ambiguous permission states where administrators cannot determine why a user has access.

## 28. Branch-Specific Role Permissions

The same role may have different effective permissions across branches.

Example:

* Manager role in Branch A → Inventory Management allowed;
* Manager role in Branch B → Inventory Management denied.

The role model must support branch-specific configuration without requiring separate employee accounts.

## 29. New Branch Permission Initialization

When a business adds a new branch, existing role permission configuration may be used as the initial permission configuration for that branch.

The Owner may then modify the new branch's permissions.

This provides a consistent starting point while preserving branch-level customization.

## 30. Permission UI Principles

The permission interface should remain simple even though the underlying model is powerful.

When an Owner creates or configures an employee:

* branch names should be clearly visible;
* the selected branch should be visually identifiable;
* selected permissions should be visually distinguishable;
* unselected permissions should remain available for configuration;
* the interface should make the current effective configuration understandable.

The UI must not expose unnecessary internal implementation details.

## 31. Role Permission Templates

The system may provide role templates for common employee types.

Examples include:

* Cashier;
* Waiter;
* Cook;
* Manager.

Templates are starting configurations.

Authorized users may customize them according to their own permissions and business requirements.

## 32. Permission Changes and Audit

Every important permission change must be auditable.

The audit history must preserve:

* who made the change;
* who or what was affected;
* permission changed;
* old state;
* new state;
* branch scope;
* timestamp;
* reason where required.

Permission history must not be silently deleted when a role or employee changes.

## 33. Employee Deactivation

When an employee leaves the business or should no longer access the system, the employee should be deactivated rather than deleting historical operational identity.

Historical transactions must continue to identify the original employee.

Deactivation must prevent new unauthorized access while preserving historical references.

## 34. Employee Identity and Historical Records

Orders, cash sessions, corrections, inventory operations, and other auditable events must retain the employee identity that performed the action.

Changing an employee's role later must not rewrite historical records.

Historical operations must represent the permissions and identity context relevant to the original event.

## 35. Permission and Subscription Interaction

Permissions do not override subscription restrictions.

A user may have permission for a function but still be unable to use it if the business's subscription does not include that function.

Therefore:

**Permission ≠ Subscription Entitlement**

Both must be satisfied where applicable.

## 36. Permission and Trusted Device Interaction

Trusted-device status does not grant business permissions.

A trusted device only establishes that the device is authorized for the relevant business and offline operation.

The employee's own permissions must still be validated.

## 37. Permission and Offline Operation

Offline transactions must use the employee's locally authorized permission state.

The offline authorization must be bounded by the server-issued authorization period.

When synchronization occurs, the server validates that the transaction was created under an acceptable employee, branch, device, and permission context.

Offline mode must not become a mechanism for bypassing permission restrictions.

## 38. Permission Change During Offline Operation

If an employee's permissions are changed while a trusted device is offline, the device may temporarily operate using its valid previously issued offline authorization until synchronization or authorization refresh according to the offline security rules.

Once the device reconnects, the server becomes authoritative.

Transactions must then be validated against the server-side business rules.

The detailed synchronization conflict policy belongs to the Offline Operation and Synchronization document.

## 39. Business Rules Summary

| Rule                                            | Requirement                            |
| ----------------------------------------------- | -------------------------------------- |
| Super Admin                                     | Platform-level role                    |
| Owner                                           | Protected business-level role          |
| Multiple Owners                                 | Supported within tariff limit          |
| Manager                                         | Permission-based                       |
| Custom roles                                    | Supported                              |
| Role permissions                                | Supported                              |
| Employee overrides                              | Supported                              |
| Branch-specific permissions                     | Supported                              |
| Multi-branch employees                          | Supported                              |
| Role cloning                                    | Supported                              |
| Employee-based role cloning                     | Supported                              |
| Permission addition/removal after cloning       | Supported                              |
| Latest explicit command                         | Determines current state               |
| Permission revert                               | Creates new event                      |
| Permission history                              | Preserved                              |
| Self-escalation                                 | Not allowed                            |
| Granting unavailable permissions                | Not allowed                            |
| Owner self-promotion                            | Not allowed                            |
| Owner privilege reduction by ordinary employees | Not allowed                            |
| Employee deactivation                           | Supported                              |
| Historical employee identity                    | Preserved                              |
| Subscription restrictions                       | Override ordinary feature availability |
| Trusted device                                  | Does not grant permissions             |
| Offline permission bypass                       | Not allowed                            |

## 40. Business Model Boundary

This document defines business-level permission behavior.

Detailed technical implementation belongs to later documents, including:

* authentication architecture;
* authorization middleware;
* permission database model;
* role inheritance implementation;
* branch scope enforcement;
* API authorization;
* frontend permission handling;
* offline permission snapshots;
* audit event storage.

Technical implementation must preserve the permission rules defined in this document.

## Related Documents

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `adr/ADR-001-Documentation-First.md`

