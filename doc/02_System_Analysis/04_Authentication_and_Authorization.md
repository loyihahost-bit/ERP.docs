# Authentication and Authorization

**Document ID:** SA-04
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines how FastFood ERP authenticates employees and determines whether they are authorized to perform specific operations.

It separates the following concepts:

* Authentication;
* Employee identity;
* Authorization;
* Role permissions;
* Employee overrides;
* Branch scope;
* Subscription entitlement;
* Employee status;
* Device trust;
* Current operational context.

The objective is to ensure that an authenticated user can perform only the operations permitted by the current system state.

---

## 2. Authentication and Authorization Separation

Authentication answers:

> Who is the user?

Authorization answers:

> What is this user allowed to do?

These are separate system responsibilities.

Conceptually:

```text
Authentication
      ↓
Employee Identity
      ↓
Business Context
      ↓
Branch Context
      ↓
Permission Resolution
      ↓
Subscription Entitlement
      ↓
Authorization Decision
      ↓
Operation
```

Successful authentication does not automatically grant operational access.

---

## 3. Employee Identity

Every normal operational user has an individual Employee identity.

Shared employee accounts must not be used for normal business operations.

The Employee identity is associated with:

* Employee UUID;
* Business UUID;
* account status;
* role assignment;
* permission overrides;
* Branch scope;
* authentication credentials;
* trusted devices where applicable.

Employee identity remains stable across the employee's operational history.

---

## 4. Employee Lifecycle

The employee lifecycle is:

```text
Created → Active → Inactive
```

### Created

The employee record exists but is not yet available for normal operational use.

### Active

The employee may authenticate and perform authorized operations.

### Inactive

The employee cannot perform new operational actions.

Historical activity remains preserved.

Deactivation does not delete:

* orders;
* payments;
* cash sessions;
* inventory operations;
* attendance;
* payroll;
* audit events;
* reports.

---

## 5. Authentication Context

After successful authentication, the system establishes an authenticated session context.

The context contains or references:

* Employee UUID;
* Business UUID;
* available Branches;
* current Branch;
* session identity;
* device identity where applicable;
* authentication state.

The client must not be trusted to define these values independently.

---

## 6. Business Context Validation

The authenticated employee belongs to a specific Business.

Every protected operation must verify that the requested entity belongs to the authenticated Business.

For example:

```text
Authenticated Employee
        ↓
Business A
        ↓
Requested Entity
        ↓
Entity belongs to Business A?
        ↓
Yes → Continue
No  → Reject
```

Cross-Business access is never permitted.

---

## 7. Branch Context

An employee may have access to one or more Branches.

The current Branch is part of the operational context.

Branch access must be validated independently from Business access.

An employee being a member of Business A does not automatically grant access to every Branch in Business A.

---

## 8. Authorization Model

FastFood ERP uses the following effective permission model:

```text
Role Permission
      +
Employee Override
      +
Branch Scope
      +
Subscription Entitlement
      +
Employee Status
      +
Device/Offline Authorization where applicable
      =
Effective Authorization
```

Each component must be evaluated according to the operation being performed.

---

## 9. Role Permissions

A Role defines a reusable set of permissions.

Examples include:

* POS access;
* order creation;
* order modification;
* payment;
* refund;
* inventory access;
* inventory adjustment;
* employee management;
* payroll access;
* report access;
* audit access.

A role is a permission template.

A role does not bypass:

* Business isolation;
* Branch scope;
* subscription limits;
* employee status;
* device trust;
* system business rules.

---

## 10. Employee Permission Overrides

An individual Employee may receive permission overrides.

Overrides are used when the employee's required access differs from the normal Role configuration.

For example:

```text
Role: Cashier
    ↓
Default Permissions

Employee Override
    ↓
Additional or Restricted Permission
```

Overrides must remain within the authority of the user assigning them.

A Manager cannot grant a permission that the Manager is not authorized to grant.

---

## 11. Permission Assignment Authority

Permission management itself is permission-controlled.

A user may manage permissions only if:

1. the user is active;
2. the user has employee/permission management authority;
3. the target employee belongs to the same Business;
4. the target Branch is within the user's authorized scope;
5. the requested permission is within the user's authority;
6. subscription entitlement allows the permission.

Permission changes must be audited.

---

## 12. Branch-Specific Permissions

An employee's effective permission set may differ by Branch.

Example:

```text
Employee E-100

Branch A
→ Inventory View
→ Inventory Adjustment

Branch B
→ Inventory View

Branch C
→ No Inventory Access
```

When the employee switches Branch, the system recalculates effective permissions.

Permissions from the previous Branch must not remain active merely because the same employee session continues.

---

## 13. Permission Resolution

The system resolves permissions for a specific operation.

Conceptually:

```text
Employee
   ↓
Role Permissions
   ↓
Employee Overrides
   ↓
Current Branch Scope
   ↓
Employee Status
   ↓
Subscription Entitlement
   ↓
Device/Offline Restrictions
   ↓
Final Authorization Decision
```

The result must be evaluated against the exact operation.

A user may be authorized to view an entity but not modify it.

---

## 14. Permission Granularity

Permissions should represent meaningful business operations rather than arbitrary technical actions.

Examples:

```text
orders.view
orders.create
orders.modify
orders.cancel

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

The final permission catalog is defined separately from this system behavior document.

---

## 15. View Permission vs Modify Permission

Read access and modification access are separate.

For example:

```text
Inventory View
      ≠
Inventory Adjustment
```

A user may be allowed to view inventory without being allowed to change it.

The same principle applies to:

* employees;
* payroll;
* reports;
* audit;
* products;
* recipes;
* menu;
* payments;
* cash sessions.

---

## 16. Business Rule Validation After Authorization

Permission approval does not automatically mean that an operation is valid.

After authorization, the system must validate relevant business rules.

Example:

```text
User Authorized
      ↓
Operation Allowed by Permission
      ↓
Business Rule Validation
      ↓
Current Entity State
      ↓
Subscription
      ↓
Execute or Reject
```

For example, a cashier may have permission to modify an order, but the system must still reject modification of an already paid order through the ordinary edit path.

---

## 17. Subscription Entitlement

Subscription entitlement is part of authorization.

A feature may be technically available but unavailable to the Business because the current subscription does not include it.

Therefore:

```text
Permission Granted
        +
Feature Entitled
        =
Operation Allowed
```

If the feature is not included in the current entitlement, the operation is rejected even if the employee's role contains the related permission.

---

## 18. Subscription Expiration

When a subscription expires:

* modifying operations are blocked according to lifecycle rules;
* viewing permitted data remains available;
* history remains accessible;
* allowed Excel exports remain available.

The client interface may hide or disable modifying controls, but the server must enforce the restriction.

Offline authorization must also respect subscription limits.

---

## 19. Employee Status During Active Session

An employee may become inactive while an application session is still open.

The system must not allow the stale session to continue performing protected operations indefinitely.

For important operations, the server checks current employee status.

If the employee is inactive:

```text
Operation
   ↓
Employee Status Check
   ↓
Inactive
   ↓
Reject
```

Historical operations remain unchanged.

---

## 20. Permission Changes During Active Session

Permissions may change while an employee is logged in.

The system must use current authoritative permissions for important operations.

The client may refresh its UI or request re-authentication when necessary, but the server remains authoritative.

Example:

```text
Old Permission
     ↓
Permission Changed
     ↓
New Server State
     ↓
Next Critical Operation
     ↓
Re-evaluate Permission
```

A stale client permission must never grant unauthorized access.

---

## 21. Branch Switching Authorization

When an employee switches Branch, the system validates:

1. Business ownership;
2. employee Branch assignment;
3. employee status;
4. Branch status;
5. effective permissions;
6. subscription entitlement;
7. device restrictions where applicable.

Only after successful validation does the new Branch become active.

---

## 22. Device Trust and Authorization

Device trust is separate from employee permissions.

A trusted device does not automatically grant additional permissions.

The system evaluates:

```text
Employee Authorization
        +
Device Trust
        +
Current Branch
        +
Subscription
```

All required conditions must be satisfied.

Device registration and trust rules are defined in:

`docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`

---

## 23. Offline Authorization

Offline authorization is a bounded authorization mechanism.

It must contain enough information to prevent an offline device from bypassing current security rules.

Offline authorization is associated with:

* Employee;
* Business;
* Branch;
* Device;
* permissions;
* subscription entitlement;
* validity period;
* authorization version;
* cryptographic protection.

An offline device must not create permissions locally.

---

## 24. Offline Permission Changes

If permissions change while a device is offline, the device may temporarily operate only within the bounds of its valid offline authorization.

After reconnecting:

* current server permissions are retrieved;
* outdated authorization is reconciled;
* unauthorized operations are rejected;
* relevant conflicts are recorded where necessary.

Offline authorization must never become an independent source of permanent authority.

---

## 25. Authorization for Critical Operations

Critical operations require current authorization and business rule validation.

Examples include:

* accepting an order;
* modifying an accepted order;
* cancelling an order;
* creating a payment;
* editing a payment;
* issuing a refund;
* changing inventory;
* closing a cash session;
* performing a correction;
* managing employees;
* changing permissions;
* approving recipes;
* changing prices;
* generating protected reports;
* exporting protected data.

---

## 26. Authorization Failure

Authorization failures must not expose sensitive internal information.

The user should receive a safe business-level response such as:

```text
You do not have permission to perform this operation.
```

The system may record additional technical details in structured logs and audit records where appropriate.

---

## 27. Error Classification

Authorization-related failures are categorized separately from other failures.

Relevant categories include:

* Authentication Failure;
* Authorization Failure;
* Business Rule Violation;
* Conflict;
* Subscription Restriction;
* Employee Inactive;
* Device Restriction;
* Validation Error.

The system must not incorrectly report an authorization failure as a generic server failure.

---

## 28. Authorization and Concurrency

Authorization is evaluated together with current entity state for critical operations.

For example:

```text
Permission Check
      ↓
Entity State Check
      ↓
Concurrency Validation
      ↓
Transaction
```

A permission decision must not allow an operation that becomes invalid before the transaction is committed.

Critical operations must rely on authoritative server/database state.

---

## 29. Authorization and Idempotency

Retrying an authorized request must not create duplicate business effects.

Where an operation uses an idempotency UUID:

```text
Request UUID
    ↓
Authorization
    ↓
Idempotency Check
    ↓
Existing Result?
   ├── Yes → Return Existing Result
   └── No  → Execute Operation
```

The exact ordering may be refined during API/System Architecture analysis, but duplicate requests must never bypass authorization.

---

## 30. Authorization and Audit

Important authorization-related changes must be audited.

Examples:

* role permission change;
* employee override change;
* Branch scope change;
* employee activation/deactivation;
* permission assignment;
* permission removal;
* subscription entitlement changes;
* device authorization/revocation.

Audit records must identify:

* actor;
* target employee;
* Business;
* Branch where applicable;
* timestamp;
* old state;
* new state;
* reason where required;
* source;
* related transaction/event UUID.

---

## 31. Permission Changes and Existing Operations

Changing permissions does not rewrite historical operations.

For example:

```text
Employee had permission
        ↓
Performed operation
        ↓
Permission removed later
        ↓
Historical operation remains valid
```

The system evaluates the authorization state that applied to the operation while preserving current permissions separately.

---

## 32. Historical Authorization Context

Important historical records should preserve enough context to establish who performed an operation and under which operational conditions.

This includes, where applicable:

* Employee UUID;
* Role/permission context;
* Branch UUID;
* Device UUID;
* Cash Session UUID;
* transaction UUID;
* timestamp;
* source Online/Offline/Sync/System.

Current permissions must not be used to reinterpret historical activity.

---

## 33. System-Generated Operations

Some operations are performed by the system rather than a human employee.

These operations use:

```text
Actor = SYSTEM
```

Examples include:

* subscription lifecycle transitions;
* report generation;
* notification processing;
* deletion jobs;
* synchronization processing;
* background maintenance.

System operations must still have an appropriate Business/Branch scope where applicable and must be auditable when they change important business state.

---

## 34. Authorization Scope by Operation

The system should evaluate authorization at the smallest meaningful business scope.

Examples:

### Business-scoped

* global product management;
* Business settings;
* subscription-related configuration;
* Business-level reporting.

### Branch-scoped

* inventory;
* cash sessions;
* tables;
* branch orders;
* branch reports;
* branch employees.

### Entity-scoped

* modifying a specific order;
* editing a specific payment;
* correcting a specific cash session;
* approving a specific recipe.

The system must not grant broader access than the operation requires.

---

## 35. Authorization in Reports and Exports

Report access requires:

* valid authentication;
* Business access;
* Branch scope where applicable;
* report permission;
* subscription/read-only entitlement.

Excel export is separately permission-controlled where required.

A user authorized to view a report is not automatically authorized to export all underlying data.

---

## 36. Authorization in Notifications

Notification visibility is permission-controlled.

A notification may be displayed only if:

* it belongs to the user's Business;
* the user is an authorized recipient;
* the Branch is within the user's scope where applicable;
* the notification type is permitted.

A notification action must perform authorization checks again before opening or modifying the target entity.

---

## 37. Authorization in Audit

Audit visibility is permission-controlled.

A user may only view audit records within the user's authorized Business and Branch scope.

Audit filters must not provide a way to bypass normal tenant isolation.

Exporting audit data is also a protected operation.

---

## 38. Authorization in Background Jobs

Background jobs must not rely on a user's current session.

Each job must contain or resolve its own authorization context.

For system-generated jobs:

```text
Actor = SYSTEM
Business Context
Branch Context if applicable
Job UUID
```

For user-requested jobs:

```text
Requesting Employee
Business Context
Branch Scope
Requested Operation
Job UUID
```

The job worker must validate the stored scope before processing protected data.

---

## 39. Authorization Decision Model

A simplified authorization decision can be represented as:

```text
Authenticated?
    ↓
Employee Active?
    ↓
Business Match?
    ↓
Branch Allowed?
    ↓
Permission Granted?
    ↓
Subscription Entitled?
    ↓
Device/Offline Authorization Valid?
    ↓
Business Rule Valid?
    ↓
Operation Allowed
```

Any failed required condition results in rejection.

---

## 40. Security Principle

Authorization must be enforced on the server.

The frontend may:

* hide unavailable navigation;
* disable unavailable buttons;
* show permission-aware screens;
* refresh permission state.

However, frontend behavior is not an authorization boundary.

The backend remains authoritative.

---

## 41. Performance Considerations

Authorization must be secure without unnecessarily slowing normal POS operations.

The system should avoid expensive authorization processing on every harmless UI action.

However, critical business operations must always perform the required authoritative checks.

Where safe, commonly used authorization context may be efficiently resolved or cached, but stale authorization must never allow a protected operation.

---

## 42. System Invariants

The following invariants apply to authentication and authorization:

1. Authentication identifies the Employee.
2. Authentication does not automatically grant operational permissions.
3. Authorization is evaluated separately from authentication.
4. Every protected operation is validated server-side.
5. Employee identity is individual and Business-scoped.
6. Inactive employees cannot perform new protected operations.
7. Historical employee activity remains preserved after deactivation.
8. Business isolation is always enforced.
9. Branch scope is part of effective authorization.
10. An employee may have different permissions in different Branches.
11. Branch switching recalculates effective permissions.
12. Role permissions alone do not determine final authorization.
13. Employee overrides are included in permission resolution.
14. A user cannot grant permissions beyond their own authority.
15. Subscription entitlement is part of effective authorization.
16. Device trust does not grant additional business permissions.
17. Trusted devices cannot bypass employee or Branch authorization.
18. Offline authorization is bounded and cryptographically protected.
19. Offline authorization cannot permanently create or expand permissions.
20. Current server state is authoritative after reconnection.
21. Critical operations validate current authorization and entity state.
22. Historical operations are not invalidated by later permission changes.
23. Authorization failures do not expose sensitive internal details.
24. Important permission changes are audited.
25. System-generated operations use `SYSTEM` as actor where applicable.
26. Reports and exports respect Business and Branch authorization.
27. Notifications respect Business, Branch and recipient permissions.
28. Audit access is permission-controlled.
29. Background jobs preserve authorization scope.
30. Frontend visibility is not a security boundary.
31. Authorization must not be bypassed through offline mode.
32. Authorization must not be bypassed through synchronization.
33. Authorization must not be bypassed through retry or duplicate requests.
34. Tenant isolation and authorization remain enforced independently of UI navigation.

---

## 43. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`

### System Analysis

* `docs/02_System_Analysis/01_System_Context_and_Boundaries.md`
* `docs/02_System_Analysis/02_Application_Structure_and_Navigation.md`
* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 44. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `04_Authentication_and_Authorization.md`

**Next Document:** `05_Employees_Roles_and_Permissions.md`

