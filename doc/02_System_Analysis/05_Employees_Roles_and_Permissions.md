# Employees, Roles and Permissions

**Document ID:** SA-05
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for Employees, Roles and Permissions.

It establishes:

* employee identity and lifecycle;
* employee creation and activation;
* role assignment;
* role permissions;
* employee permission overrides;
* Branch scope;
* permission inheritance;
* permission management authority;
* permission changes during active sessions;
* employee deactivation;
* multi-Branch employment;
* subscription limits related to employees;
* historical integrity.

The objective is to provide a simple and controlled permission model while preventing unauthorized access or privilege escalation.

---

## 2. Employee Identity

Every operational employee has an individual Employee identity.

An Employee belongs to one Business.

The same Employee identity may be assigned to multiple Branches within that Business.

Conceptually:

```text
Business
   │
   └── Employee
          ├── Branch A
          ├── Branch B
          └── Branch C
```

Employee identity must remain stable throughout the employee's lifecycle.

---

## 3. Employee UUID

Every Employee has a unique Employee UUID.

The Employee UUID is used to identify the employee in:

* orders;
* payments;
* cash sessions;
* inventory operations;
* attendance;
* payroll;
* audit records;
* corrections;
* notifications;
* synchronization events.

Historical records must reference the Employee UUID rather than relying only on mutable employee attributes such as name.

---

## 4. Employee Lifecycle

The employee lifecycle is:

```text
Created → Active → Inactive
```

### Created

The employee record has been created but is not yet available for normal operational work.

### Active

The employee may authenticate and perform authorized operations.

### Inactive

The employee cannot perform new protected operations.

Historical activity remains available according to normal access rules.

---

## 5. Employee Creation

Employee creation is a permission-controlled operation.

The creator must:

1. be authenticated;
2. be active;
3. have employee creation permission;
4. operate within the correct Business;
5. have authority over the target Branch;
6. assign only permitted roles and permissions;
7. respect subscription employee limits.

An employee must not be created with permissions exceeding the creator's authority.

---

## 6. Manager Employee Creation

Managers may create employees only when the required permission has been explicitly granted.

A Manager cannot:

* create an employee outside their Branch authority;
* grant permissions they cannot grant;
* bypass subscription employee limits;
* assign unauthorized administrative privileges.

This prevents privilege escalation through employee creation.

---

## 7. Employee Activation

An employee becomes operational only after reaching the appropriate active state.

Activation must verify:

* Business context;
* employee record validity;
* Branch assignment where required;
* subscription entitlement;
* required configuration.

An inactive employee cannot become active through a client-side state change alone.

---

## 8. Employee Deactivation

An authorized user may deactivate an employee.

Deactivation:

* prevents new protected operations;
* invalidates or restricts future authentication;
* affects future authorization checks;
* preserves historical records.

It must not delete the employee's previous activity.

The system must preserve:

* employee identity;
* previous roles;
* previous Branch assignments;
* previous permissions;
* historical actions.

---

## 9. Deactivation During Active Session

An employee may become inactive while an application session is still open.

The server must detect the current employee state during important operations.

After deactivation:

```text
Open Session
    ↓
Employee becomes Inactive
    ↓
Next Protected Operation
    ↓
Employee Status Check
    ↓
Reject
```

The existing session must not become a permanent bypass mechanism.

---

## 10. Employee Branch Assignment

An employee may be assigned to one or more Branches.

Each assignment establishes the Branch scope in which the employee may operate.

Example:

```text
Employee E-001

Branch A → Active Assignment
Branch B → Active Assignment
Branch C → No Assignment
```

Branch assignment does not automatically grant every permission available in the Branch.

---

## 11. Branch-Specific Employee Configuration

The same Employee may have different operational configurations in different Branches.

For example:

```text
Employee E-001

Branch A
Role: Manager
Permissions: Orders + Inventory

Branch B
Role: Cashier
Permissions: POS + Payments
```

The system resolves the effective configuration using the current Branch context.

---

## 12. Role Model

A Role is a reusable permission template.

Roles may represent business functions such as:

* Owner;
* Manager;
* Cashier;
* Waiter;
* Cook;
* custom employee roles.

The system must not rely solely on role names for authorization.

The actual permission set associated with the role determines access.

---

## 13. Role Assignment

Role assignment is permission-controlled.

A user assigning a role must have authority to:

* manage the target employee;
* assign the selected role;
* assign the role within the relevant Branch scope.

A user must not be able to assign a role that grants greater authority than the user is allowed to delegate.

---

## 14. Role Permissions

A Role contains a defined set of permissions.

Examples include:

```text
orders.view
orders.create
orders.modify
orders.cancel

payments.view
payments.create
payments.edit
payments.refund

inventory.view
inventory.adjust
inventory.purchase

employees.view
employees.create
employees.edit

reports.view
reports.export

audit.view
audit.export
```

The final permission catalog may expand as additional system modules are defined.

---

## 15. Employee Permission Override

Employee Overrides allow an individual employee's permissions to differ from the assigned Role.

Conceptually:

```text
Role
   ↓
Default Permissions
   ↓
Employee Override
   ↓
Effective Permissions
```

An override may add or restrict access according to the supported permission model.

The resulting permissions must still respect:

* Branch scope;
* subscription entitlement;
* employee status;
* assigning user's authority.

---

## 16. Effective Permission Model

The effective permission set is determined by:

```text
Role Permission
      +
Employee Override
      +
Branch Scope
      +
Employee Status
      +
Subscription Entitlement
      +
Device/Offline Restrictions
```

The result is evaluated for the current operation.

A permission may be present in a role but unavailable because:

* the employee is not assigned to the Branch;
* the employee is inactive;
* the subscription does not include the feature;
* the current device/offline authorization does not permit it.

---

## 17. Permission Inheritance

Permissions must not be inherited implicitly from unrelated roles, employees or Branches.

For example:

```text
Employee A
Branch A
Manager Permissions
```

does not imply:

```text
Employee A
Branch B
Manager Permissions
```

unless Branch B explicitly provides the corresponding role/permission configuration.

This prevents accidental privilege expansion.

---

## 18. Permission Delegation

Permission delegation is itself a protected operation.

A user may grant or modify permissions only within their authority.

The system should evaluate:

```text
Actor Authority
      ↓
Target Employee
      ↓
Requested Permission
      ↓
Target Branch
      ↓
Subscription
      ↓
Allowed / Rejected
```

A Manager cannot grant Owner-level authority unless the system explicitly allows such delegation and the Manager has the corresponding authority.

---

## 19. Permission Removal

Permissions may be removed from:

* a Role;
* an Employee Override;
* a Branch-specific assignment.

Removing a permission affects future authorization decisions.

It does not invalidate historical operations that were performed while the permission was valid.

---

## 20. Permission Change During Active Session

Permission changes may occur while an employee is logged in.

The system must use the current authoritative permission state for important operations.

Example:

```text
Employee logged in
      ↓
Permission exists
      ↓
Permission removed by Owner
      ↓
Employee attempts protected operation
      ↓
Server re-evaluates permission
      ↓
Operation rejected
```

The client may refresh its visible UI after the change.

---

## 21. Role Change During Active Session

Changing an employee's role follows the same principle.

The employee does not retain old role authority indefinitely.

The server must use the current effective role/permission state for protected operations.

Historical actions remain associated with the previous authorization context.

---

## 22. Branch Switch and Permission Recalculation

When an employee changes Branch:

1. current Business is validated;
2. target Branch is validated;
3. employee assignment is validated;
4. Branch-specific role/permission configuration is loaded;
5. Employee Overrides are applied;
6. subscription entitlement is checked;
7. effective permissions are recalculated.

The previous Branch's permission set must not remain active.

---

## 23. Permission Scope

Permissions may be:

* Business-scoped;
* Branch-scoped;
* Entity-specific where required.

Examples:

### Business-scoped

* global product management;
* global recipe management;
* Business settings;
* Business-level employee management.

### Branch-scoped

* inventory;
* cash sessions;
* tables;
* branch orders;
* branch reports.

### Entity-specific

* correction of a particular cash session;
* editing a specific payment;
* modifying a specific order.

The system must apply the narrowest relevant scope.

---

## 24. Owner Permissions

Owner is a Business-level administrative role.

An Owner may have access to:

* Branch management;
* employee management;
* roles;
* permissions;
* products;
* recipes;
* menu;
* prices;
* inventory;
* expenses;
* reports;
* payroll;
* dashboard;
* Business settings.

Actual access remains subject to subscription entitlement and system-level restrictions.

Multiple Owners may exist when permitted by the subscription.

---

## 25. Manager Permissions

Manager access is controlled by assigned permissions.

A Manager may operate within one or more Branches depending on their assignments.

A Manager cannot automatically:

* manage every Branch;
* grant unrestricted permissions;
* bypass subscription restrictions;
* access unrelated Businesses.

Manager authority is always bounded by effective permission and Branch scope.

---

## 26. Cashier Permissions

Cashier is primarily an operational POS role.

Typical permissions may include:

* order creation;
* order viewing;
* payment creation;
* cash session operations;
* handover operations;
* permitted order modifications.

Additional permissions may be granted where business rules allow.

Cashier permissions do not automatically include:

* employee management;
* role management;
* unrestricted inventory adjustment;
* payroll administration;
* unrestricted audit access.

---

## 27. Waiter Permissions

Waiter permissions are configurable.

Depending on assigned permissions, a Waiter may access:

* tables;
* table visits;
* orders;
* waiter assignment;
* order status information.

A Waiter cannot assume authority beyond explicitly assigned permissions.

---

## 28. Cook Permissions

Cook permissions are configurable.

Typical access may include:

* kitchen order visibility;
* preparation status;
* ready status;
* relevant operational information.

Cook access does not automatically provide POS, payment, payroll or employee administration authority.

---

## 29. Custom Roles

The system may support custom roles.

A custom role consists of:

* Role identity;
* Business ownership;
* permissions;
* optional Branch scope;
* lifecycle state.

Creating or modifying custom roles requires appropriate authorization.

Custom roles must use the same effective permission model as standard roles.

---

## 30. Role Templates

An employee's effective permission configuration may be used as a basis for a role template when the relevant feature is available.

Creating a template must not automatically change existing employees.

The relationship is:

```text
Employee Permission Configuration
          ↓
Role Template
          ↓
Future or Selected Employees
```

Existing employees are affected only when an explicit role update is applied.

---

## 31. Applying Role Changes to Employees

When a role changes, the system must define which employees receive the change.

Possible behavior:

* update selected employees;
* update all employees assigned to the role.

The operation must be explicit.

Employee-specific overrides must be handled according to the permission model rather than silently overwritten.

The latest authorized configuration change becomes effective for future authorization checks.

---

## 32. Subscription Employee Limits

Subscription tariffs may limit the number of employees.

The system must enforce employee limits server-side.

When the limit is reached:

* new employee creation is blocked;
* existing employees remain intact;
* historical data remains preserved.

A subscription downgrade must not silently delete existing employees.

---

## 33. Employee Limit Downgrade

If the Business downgrades to a tariff with a lower employee limit:

* existing employee records remain preserved;
* new employee creation may be blocked;
* the system must clearly indicate the limit condition;
* historical employee activity remains accessible;
* no destructive automatic deletion occurs.

The exact administrative resolution is defined by subscription policy.

---

## 34. Employee Permissions and Subscription

Employee permissions cannot bypass subscription restrictions.

Example:

```text
Employee Permission
        +
Feature Not Entitled
        ↓
Operation Rejected
```

Subscription entitlement is therefore an upper boundary for available functionality.

---

## 35. Permission Change Audit

Important permission changes must be audited.

Examples:

* role created;
* role modified;
* role deleted/archived where applicable;
* employee role changed;
* permission added;
* permission removed;
* employee override changed;
* Branch scope changed;
* employee activated;
* employee deactivated.

Audit records must preserve the relevant old and new state.

---

## 36. Historical Permission Context

Historical operations must remain interpretable after later permission changes.

The system must preserve sufficient context to determine:

* who performed the operation;
* which Business;
* which Branch;
* which role/permission context was applicable;
* which device was used;
* which Cash Session was active where applicable.

Current permission state must not rewrite historical authorization.

---

## 37. Attendance and Payroll Relationship

Employee identity is shared across operational and administrative modules.

Attendance and payroll may reference the same Employee UUID.

Changing an employee's role or Branch assignment must not rewrite historical:

* attendance;
* payroll;
* salary calculations;
* finalized payroll periods.

Historical payroll calculations use their own snapshots.

---

## 38. Employee Deactivation and Open Operations

If an employee becomes inactive while they have operational work in progress:

* the employee cannot start new protected operations;
* existing historical records remain;
* open business operations must be handled according to the relevant module rules.

For example, an open Cash Session is not automatically deleted or reassigned merely because the employee becomes inactive.

A separate authorized operational process may be required.

---

## 39. Offline Employee Authorization

Offline operations use the employee's valid offline authorization.

The offline authorization must respect:

* Employee status;
* Branch scope;
* permissions;
* subscription entitlement;
* device trust;
* validity period.

The device must not create or expand permissions while offline.

---

## 40. Synchronization of Permission Changes

Permission and employee-state changes must synchronize to trusted offline devices according to synchronization rules.

When a device reconnects:

1. current server state is retrieved;
2. outdated authorization is identified;
3. future unauthorized operations are blocked;
4. valid offline operations are reconciled according to sync rules;
5. conflicts are recorded where necessary.

The system must not silently discard valid historical offline events merely because permissions changed later.

---

## 41. Permission Checks for Background Operations

Background jobs must operate within an explicit Business and Branch scope.

If a job was initiated by an employee, the system should retain the initiating Employee identity for audit purposes.

System-generated jobs use:

```text
Actor = SYSTEM
```

Background processing must not accidentally execute with broader permissions than the operation requires.

---

## 42. Permission Checks for Reports

Report access requires:

* active employee;
* Business access;
* appropriate Branch scope;
* report permission;
* subscription/read-only entitlement.

Report generation must not expose data outside the employee's authorized scope.

---

## 43. Permission Checks for Exports

Excel export is a protected operation.

A user may need:

* report view permission;
* export permission;
* Business/Branch access;
* subscription/read-only entitlement.

Exported data must match the authorized report scope.

The export operation itself may be audited according to the Audit rules.

---

## 44. Permission Checks for Notifications

Notifications are shown according to:

* Business;
* Branch;
* recipient scope;
* permission;
* notification type.

A notification action must perform authorization again before modifying the target entity.

---

## 45. Permission Checks for Audit

Audit access is explicitly permission-controlled.

An employee may be allowed to:

* view audit records;
* filter audit records;
* inspect a specific entity's history;
* export audit records.

These are separate capabilities where required.

---

## 46. Authorization Failure Behavior

If an employee lacks permission:

* the operation is rejected;
* no partial business change is made;
* the user receives a safe error;
* the failure may be logged where appropriate.

The system must not execute part of an unauthorized operation before discovering the missing permission.

---

## 47. Privilege Escalation Prevention

The system must prevent employees from gaining authority indirectly.

Examples of prohibited escalation include:

* Manager granting themselves Owner permissions;
* Manager assigning a higher role than they can delegate;
* Employee modifying their own permission overrides;
* Employee changing their own Branch scope;
* Employee creating another account with greater privileges;
* Client modifying permission identifiers in requests;
* Offline device creating additional permissions.

All such operations require server-side authorization.

---

## 48. Concurrent Permission Changes

Permission changes may occur concurrently.

The system must protect against inconsistent final state.

For example:

```text
Owner A changes permission
        +
Owner B changes same permission
        ↓
Concurrency handling
        ↓
One authoritative final state
```

The final state must be deterministic and auditable.

The exact concurrency mechanism is defined in:

`docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`

---

## 49. System Invariants

The following invariants apply to Employees, Roles and Permissions:

1. Every normal operational employee has an individual identity.
2. An Employee belongs to one Business.
3. An Employee may be assigned to multiple Branches within that Business.
4. Employee UUID remains stable throughout the employee lifecycle.
5. Employee history is never deleted merely because the employee becomes inactive.
6. Only authorized users may create employees.
7. Managers require explicit permission to create employees.
8. A user cannot grant permissions beyond their authority.
9. Employee status is part of authorization.
10. Inactive employees cannot perform new protected operations.
11. Role permissions are reusable permission templates.
12. Role names alone do not determine authorization.
13. Employee Overrides may modify the effective permission set.
14. Branch scope is part of effective authorization.
15. Permissions do not automatically transfer between Branches.
16. Branch switching recalculates effective permissions.
17. Subscription entitlement limits available functionality.
18. Subscription downgrade does not automatically delete employees.
19. Permission changes do not rewrite historical operations.
20. Historical operations retain their original Employee and Branch context.
21. Offline devices cannot create or expand employee permissions.
22. Permission changes are enforced server-side.
23. Frontend permission visibility is not a security boundary.
24. Employee self-escalation is prohibited.
25. Role delegation is authority-controlled.
26. Important permission changes are audited.
27. Background jobs operate within explicit Business/Branch scope.
28. Reports and exports respect employee permissions and scope.
29. Notifications respect employee visibility and scope.
30. Audit access is explicitly permission-controlled.
31. Permission failures produce no partial business operation.
32. Concurrent permission changes produce one authoritative final state.
33. Historical attendance and payroll are not rewritten by later employee changes.
34. Current authorization must not invalidate already valid historical records.
35. Authentication, authorization, Branch scope and subscription entitlement remain separate checks.

---

## 50. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/15_Employees_Attendance_and_Payroll.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`

### System Analysis

* `docs/02_System_Analysis/01_System_Context_and_Boundaries.md`
* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/19_Attendance_and_Payroll.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 51. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `05_Employees_Roles_and_Permissions.md`

**Next Document:** `06_Device_Trust_and_Security_Context.md`

