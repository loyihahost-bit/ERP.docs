# 07 — Authorization and Permission Security

**Document ID:** SEC-07
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent:** `docs/11_Security/README.md`
**Previous:** `06_Authentication_Security_Standards.md`
**Next:** `08_Data_Security_and_Data_Classification.md`

---

## 1. Purpose

This document defines the security policy for authorization and permission management in the FastFood ERP system.

It establishes requirements for:

* roles;
* permissions;
* role templates;
* branch-specific permissions;
* permission inheritance;
* permission overrides;
* authorization evaluation;
* privilege boundaries;
* privilege escalation prevention;
* delegation;
* Owner and Manager authority;
* permission changes;
* permission revocation;
* temporary access;
* emergency access;
* authorization failures;
* authorization auditing.

The purpose is to ensure that every authenticated identity can perform only the operations explicitly allowed by its effective authorization scope.

This document defines **security policy and authorization standards**, not implementation-specific mechanisms.

---

# 2. Scope

This document covers authorization for:

* Super Admin;
* Owner;
* Manager;
* Cashier;
* Cook;
* Waiter;
* other configurable employee roles;
* service identities;
* integration identities;
* background identities.

It covers:

* role-based access;
* permission assignment;
* branch-specific authorization;
* role templates;
* permission overrides;
* delegated administration;
* privileged actions;
* authorization conflicts;
* privilege escalation;
* permission lifecycle;
* authorization auditing;
* authorization threats;
* security invariants.

It does not define:

* password security;
* session implementation;
* token implementation;
* tenant isolation;
* database authorization implementation;
* API middleware implementation;
* infrastructure security.

Those concerns belong to their respective documents.

---

# 3. Authorization Model

Authorization determines whether an authenticated identity may perform a requested operation.

The effective authorization decision is based on multiple boundaries:

```text id="k5qg7r"
Authenticated Identity
        ↓
Business/Tenant
        ↓
Branch Scope
        ↓
Role
        ↓
Permission
        ↓
Resource Scope
        ↓
Action
```

Authorization must evaluate the relevant boundaries together.

A valid role alone is not sufficient.

A valid permission alone is not sufficient.

A valid branch assignment alone is not sufficient.

The complete authorization context must satisfy the security policy.

---

# 4. Core Authorization Principles

FastFood ERP authorization follows these principles:

1. Deny by default.
2. Grant the minimum required authority.
3. Separate authentication from authorization.
4. Separate role from branch scope.
5. Separate permission from resource ownership.
6. Prevent privilege escalation.
7. Prevent unauthorized delegation.
8. Make permission changes auditable.
9. Make privilege revocation effective.
10. Avoid hidden authorization paths.
11. Apply the same security policy to online and offline operations.
12. Apply authorization consistently across UI, API, background, synchronization, import, and export operations.

---

# 5. Role-Based Authorization

Roles represent groups of operational responsibilities.

Typical roles include:

* Super Admin;
* Owner;
* Manager;
* Cashier;
* Cook;
* Waiter;
* Other business-defined roles.

A role may provide a set of permissions, but the role itself must not bypass:

* business boundaries;
* branch boundaries;
* resource ownership;
* explicit permission restrictions.

Role names must never be treated as sufficient authorization evidence.

---

# 6. Role and Permission Separation

A role describes an employee's responsibility.

A permission describes a specific capability.

For example:

```text id="x6k0ye"
Role:
  Manager

Permissions:
  View Reports
  Manage Employees
  Manage Inventory
```

The Manager role does not automatically imply every possible administrative capability.

New security-sensitive functions must require explicit permission assignment.

---

# 7. Permission Granularity

Permissions should represent meaningful business capabilities.

Examples include:

* view orders;
* create orders;
* modify orders;
* process payments;
* process refunds;
* manage inventory;
* adjust inventory;
* view reports;
* manage employees;
* manage salaries;
* manage recipes;
* modify menu;
* manage branch settings;
* manage permissions.

Permissions should be granular enough to prevent unnecessary privilege expansion while remaining understandable to business administrators.

---

# 8. Least Privilege

Employees must receive only the permissions necessary for their responsibilities.

For example:

```text id="3c8x0z"
Cashier:
  Orders: Allowed
  Payments: Allowed
  Refunds: Restricted
  Payroll: Denied
  Permission Management: Denied
```

A user must not receive administrative permissions merely because they are convenient to configure.

Least privilege applies to:

* human users;
* service accounts;
* integrations;
* background workers;
* temporary access.

---

# 9. Branch and Permission Relationship

Branch scope and permissions are independent.

Example:

```text id="b5o3c1"
Employee:
  Branches: 1, 3
  Inventory Permission: Allowed
```

This means the employee may perform inventory operations only where both conditions are satisfied.

The employee must not automatically gain inventory access to Branch 2.

Therefore:

```text id="1d2y3f"
Effective Access =
  Authorized Branch
  AND
  Required Permission
```

---

# 10. Resource-Level Authorization

Permissions must not bypass resource ownership.

For example:

```text id="6o3r1a"
Permission:
  View Orders

Branch Scope:
  Branch 1

Requested Resource:
  Order belonging to Branch 2

Result:
  Denied
```

The existence of a broad permission does not override resource ownership.

---

# 11. Role Templates

Role templates may be used to simplify permission management.

A role template may define a standard permission set for:

* Cashier;
* Cook;
* Waiter;
* Manager;
* other configured roles.

Templates must not create hidden privileges.

When a role template changes:

* the resulting authorization impact must be understandable;
* affected employees must be identifiable;
* security-sensitive changes must be auditable;
* explicit employee-specific restrictions must remain governed.

---

# 12. Employee-Specific Permissions

The system may support employee-specific permissions.

This allows a business to customize authorization beyond the standard role template.

For example:

```text id="q3v1x6"
Role:
  Cashier

Additional Permission:
  View Selected Reports
```

Employee-specific permissions must remain inside the authority of the administrator making the change.

An employee-specific permission must not allow the employee to bypass business or branch boundaries.

---

# 13. Permission Overrides

Permission overrides are exceptions to the normal role-based permission set.

An override may:

* grant an additional permission;
* restrict a permission;
* apply to a selected branch;
* apply to a selected employee;
* apply to a defined scope.

Overrides must be:

* explicit;
* understandable;
* auditable;
* bounded;
* revocable.

An override must not create an unrestricted administrative path.

---

# 14. Override Precedence

When multiple authorization rules apply, the system must use a deterministic precedence model.

Security-sensitive restrictions must not be silently overridden by broader grants.

The conceptual rule is:

```text id="9d4v2h"
Explicit Security Restriction
        ↓
Resource / Branch Boundary
        ↓
Permission Requirement
        ↓
Role Permission
        ↓
Default
```

The exact implementation precedence belongs to technical authorization documentation, but the security outcome must remain deterministic and fail-safe.

---

# 15. Deny by Default

If no rule explicitly grants the required capability:

> Access is denied.

Access must also be denied when:

* authorization information is missing;
* the target branch is unclear;
* resource ownership cannot be verified;
* permission state is inconsistent;
* a required security restriction cannot be evaluated safely.

The system must never interpret uncertainty as permission.

---

# 16. Permission Conflicts

Permission conflicts may occur when an employee has multiple roles, overrides, or branch-specific rules.

For example:

```text id="7r2f1m"
Role Permission:
  Inventory = Allowed

Employee Override:
  Inventory = Denied
```

The resulting security policy must not unexpectedly grant access merely because a broader role permission exists.

Conflicting authorization states must resolve predictably.

---

# 17. Multiple Roles

If an employee can have multiple roles, the authorization model must prevent accidental privilege aggregation from creating unintended authority.

Multiple roles must not automatically mean:

> Every permission from every role without restriction.

Where permissions are combined, the resulting authority must remain within the business's intended authorization model.

Sensitive administrative permissions should require explicit consideration rather than accidental inheritance.

---

# 18. Permission Inheritance

Permission inheritance must be explicit.

A permission granted at one scope must not silently propagate to unrelated scopes.

For example:

```text id="r3m6v1"
Branch 1 Permission
```

must not automatically become:

```text id="r3m6v1"
Branch 2 Permission
Branch 3 Permission
All-Branch Permission
```

unless the authorization model explicitly grants that scope.

---

# 19. All-Branch Permissions

All-branch permissions represent a high-impact authorization capability.

They must be explicitly granted.

A user with:

```text id="m9p2x5"
View Reports
All Branches
```

does not automatically receive:

```text id="m9p2x5"
Modify Inventory
All Branches
```

Each sensitive capability must remain independently governed.

---

# 20. Owner Authorization

The Owner is the highest normal business-level authority.

Owner capabilities may include:

* employee management;
* role management;
* permission management;
* recipe management;
* salary management;
* reports;
* branch management;
* menu management;
* business configuration.

Owner authority remains limited by the business boundary.

Owner access must not become Super Admin authority.

The Owner must not gain access to:

* another business;
* platform infrastructure;
* unrelated tenant data;
* Super Admin-only capabilities.

---

# 21. Manager Authorization

Managers operate within authority delegated by the Owner or the business authorization model.

Managers may receive permissions for:

* employee management;
* operational management;
* inventory;
* reports;
* branch operations.

A Manager must not:

* grant themselves Owner-level authority;
* grant another employee permissions beyond their own authority;
* modify permissions outside their authorized scope;
* bypass Owner restrictions;
* create an unrestricted administrator.

---

# 22. Delegated Authorization

Delegated administration is allowed only within explicitly defined boundaries.

The delegator must have authority to grant the permission being delegated.

The following rule applies:

> No identity may grant another identity a privilege that the delegating identity is not authorized to grant.

Example:

```text id="g6s1x2"
Manager:
  Branch Scope: Branch 1
  Permission: Employee Management

Allowed:
  Configure authorized employees in Branch 1

Denied:
  Grant Branch 2 access
  Grant Owner privileges
  Grant Super Admin privileges
```

---

# 23. Permission Management Security

Permission-management functionality is itself a privileged capability.

Only authorized identities may:

* create roles;
* modify role permissions;
* assign sensitive permissions;
* create overrides;
* modify branch scope;
* grant all-branch access;
* revoke administrative permissions.

Permission management actions must be auditable.

---

# 24. Privilege Escalation

Privilege escalation occurs when an identity obtains authority beyond its intended authorization.

The system must protect against both:

### 24.1 Vertical Privilege Escalation

A lower-privileged employee obtains higher-level capabilities.

Example:

```text id="7g3x9m"
Cashier
    ↓
Manager
    ↓
Owner
```

without authorized role assignment.

### 24.2 Horizontal Privilege Escalation

An employee accesses another employee's resources or branch scope without becoming a higher-level role.

Example:

```text id="p2k6z8"
Branch 1 Manager
    ↓
Branch 2 Manager Resources
```

Both forms must be prevented.

---

# 25. Privilege Escalation Prevention

The authorization model must prevent escalation through:

* modified request parameters;
* manipulated resource identifiers;
* hidden UI actions;
* direct API requests;
* imports;
* exports;
* background jobs;
* synchronization;
* offline operation;
* role changes;
* permission overrides;
* branch switching.

Authorization must be enforced independently of whether the normal UI exposes the action.

---

# 26. Client-Side Authorization Is Not Sufficient

Hiding a button or page does not constitute authorization.

For example:

```text id="x2g7b9"
UI:
  "Manage Permissions" hidden
```

does not mean the user is unauthorized unless the underlying authorization policy also denies the operation.

The authoritative security boundary must exist outside the presentation layer.

Technical enforcement details belong to backend/API documentation.

---

# 27. API and Direct Request Protection

A user must not gain unauthorized authority by directly constructing a request that is not available through the normal UI.

Authorization must apply equally to:

* normal application actions;
* direct requests;
* imported operations;
* automated requests;
* background-triggered operations.

The interface must never be the only authorization control.

---

# 28. Import Authorization

Imports can modify large amounts of data and therefore require authorization.

An employee must not use import functionality to:

* create unauthorized users;
* assign unauthorized roles;
* grant unauthorized permissions;
* change another branch's data;
* bypass normal approval requirements.

Bulk operations must respect the same authorization boundaries as individual operations.

---

# 29. Export Authorization

Exports can expose large quantities of sensitive business information.

Export permission must be separately controlled where appropriate.

A user with permission to view one resource type must not automatically receive unrestricted export authority.

Exports must respect:

* business scope;
* branch scope;
* role;
* permission;
* data sensitivity.

---

# 30. Financial Authorization

Financial operations require appropriate permission boundaries.

Examples include:

* refunds;
* cash corrections;
* register corrections;
* expenses;
* salary management.

A user who can view financial data does not automatically gain permission to modify it.

Sensitive financial actions may require:

* elevated permission;
* approval;
* additional authorization;
* audit logging.

---

# 31. Inventory Authorization

Inventory permissions must distinguish between:

* viewing stock;
* receiving stock;
* adjusting stock;
* correcting discrepancies;
* managing inventory configuration.

A user with read access must not automatically receive adjustment authority.

Inventory adjustments must remain within the user's authorized branch and permission scope.

---

# 32. Recipe and Menu Authorization

Recipe and menu permissions must distinguish between:

* viewing;
* creating;
* modifying;
* approving;
* publishing;
* archiving.

A user authorized to view recipes must not automatically modify them.

A user authorized to modify a recipe must not automatically approve their own changes if business policy requires independent approval.

---

# 33. Refund and Approval Boundaries

Refunds and other sensitive operations may require approval according to business policy.

The permission to initiate an operation does not automatically imply permission to approve the same operation when separation of duties is required.

The authorization model should support separation between:

```text id="d5k2x8"
Initiate
   ↓
Review / Approve
   ↓
Complete
```

This reduces the risk of a single compromised or malicious account performing an entire sensitive workflow without oversight.

---

# 34. Separation of Duties

Where practical, high-impact operations should use separation of duties.

Examples include:

* refund initiation and approval;
* sensitive permission changes;
* high-impact financial corrections;
* privileged administrative changes.

Separation of duties must be applied where the business risk justifies it without making ordinary branch operations unnecessarily difficult.

---

# 35. Temporary Permissions

Temporary permissions may be granted for legitimate operational needs.

Temporary permissions must have:

* explicit authorization;
* defined scope;
* defined purpose;
* controlled duration where applicable;
* auditability;
* revocation capability.

Temporary access must not silently become permanent.

---

# 36. Emergency Privileges

Emergency authorization may be used only for exceptional situations.

Emergency privileges must:

* be explicitly granted;
* be limited to the required capability;
* be limited to the required scope;
* be auditable;
* be removed when no longer required.

Emergency access must not become a normal method of bypassing permission management.

---

# 37. Permission Revocation

Permissions must be revocable.

Revocation may occur because of:

* employee role change;
* branch transfer;
* employee termination;
* security incident;
* permission policy change;
* temporary access expiration;
* business restructuring.

After revocation, new unauthorized operations must be denied.

---

# 38. Role Changes

Changing an employee's role is a security-sensitive action.

Role changes may modify effective permissions.

Therefore:

* the change must be authorized;
* resulting permissions must be predictable;
* high-impact changes should be auditable;
* obsolete permissions must not remain unintentionally.

Role changes must not create hidden privilege accumulation.

---

# 39. Permission Accumulation

Over time, employees may receive multiple role changes and overrides.

The system must prevent unintended privilege accumulation.

For example:

```text id="u4q8m1"
Role A
  → Permission X

Role B
  → Permission Y

Role C
  → Permission Z

Employee no longer needs:
  X
  Y
  Z
```

Changing or removing the relevant role must not leave obsolete permissions active without explicit justification.

Authorization lifecycle management must therefore account for permission cleanup.

---

# 40. Permission Review

Sensitive permissions should be periodically reviewed.

Review should consider:

* current role;
* current branch scope;
* current responsibilities;
* temporary permissions;
* employee-specific overrides;
* high-risk privileges.

The purpose is to identify:

* excessive permissions;
* obsolete permissions;
* unexpected all-branch access;
* unnecessary administrative authority.

---

# 41. Authorization Changes and Audit

The following events should be auditable:

* role creation;
* role modification;
* permission assignment;
* permission removal;
* permission override;
* branch scope change;
* role change;
* temporary privilege grant;
* emergency privilege grant;
* permission revocation;
* high-impact authorization failures.

Audit records should identify:

* actor;
* target identity;
* affected business;
* affected branch where applicable;
* permission or role involved;
* action;
* timestamp;
* result.

---

# 42. Authorization Failure Handling

When authorization fails, the system must avoid exposing unnecessary security information.

It should not reveal:

* hidden permissions;
* another employee's roles;
* another branch's existence;
* internal security configuration;
* confidential resource information.

The failure should be sufficient for legitimate operation while minimizing attacker reconnaissance.

---

# 43. Authorization Consistency

Authorization must remain consistent across:

* web interfaces;
* APIs;
* background workers;
* scheduled operations;
* synchronization;
* offline operation;
* imports;
* exports;
* device operations.

A permission granted or denied in one access path must not silently produce a different security result in another path.

---

# 44. Offline Authorization

Offline operation must preserve previously established authorization boundaries.

Offline mode must not allow an employee to:

* create unrestricted privileges;
* expand branch scope;
* modify central permission structures without appropriate synchronization;
* access another branch's data;
* bypass approval requirements.

When authorization changes occur centrally while a branch is offline, synchronization must reconcile the authorization state according to the established security policy.

---

# 45. Background Authorization

Background jobs must operate under explicit authorization context.

A background job must not receive broad privileges merely because it needs to process data automatically.

Each job should have a defined purpose and scope.

For example:

```text id="w7s3n2"
Inventory Job
  Scope: Branch 1
  Purpose: Inventory calculation
```

must not silently become:

```text id="w7s3n2"
All Branches
All Permissions
```

---

# 46. Service and Integration Authorization

Service and integration identities must receive only the permissions required for their purpose.

An integration that needs:

```text id="p8k4v6"
Read Orders
```

must not automatically receive:

```text id="p8k4v6"
Manage Employees
Manage Permissions
Manage Payroll
```

Service authorization must remain explicit and auditable.

---

# 47. Security Threat Model

Authorization security must address at least the following threats.

### 47.1 Vertical Privilege Escalation

A low-privileged user obtains higher-level permissions.

### 47.2 Horizontal Privilege Escalation

A user accesses another user's or branch's resources.

### 47.3 Self-Privilege Grant

An employee attempts to grant permissions to themselves.

### 47.4 Unauthorized Delegation

A Manager grants authority beyond their own scope.

### 47.5 Role Manipulation

An employee attempts to modify their own role.

### 47.6 Permission Override Abuse

An employee attempts to create or exploit an override.

### 47.7 Identifier-Based Bypass

A user manipulates resource identifiers to reach unauthorized resources.

### 47.8 Client-Side Bypass

A user invokes hidden or unavailable functionality directly.

### 47.9 Permission Accumulation

Obsolete permissions remain after role or responsibility changes.

### 47.10 Offline Authorization Bypass

An employee uses offline operation to circumvent current authorization.

### 47.11 Bulk Operation Abuse

An employee uses imports or exports to bypass normal authorization controls.

### 47.12 Background Scope Abuse

A worker or scheduled process operates outside its intended authorization scope.

---

# 48. Security Monitoring

The system should monitor for:

* repeated privilege escalation attempts;
* repeated authorization failures;
* unusual permission changes;
* unexpected all-branch grants;
* rapid role changes;
* unauthorized delegation attempts;
* suspicious bulk exports;
* unexpected administrative actions.

Monitoring should prioritize high-risk events rather than generating excessive noise.

---

# 49. Incident Response

A confirmed authorization violation must be treated as a security incident.

Response may include:

* identifying the affected identity;
* identifying affected branches;
* reviewing permission changes;
* revoking excessive privileges;
* terminating affected sessions where appropriate;
* reviewing audit events;
* determining affected data;
* correcting authorization state;
* preserving relevant evidence.

The broader incident-response policy governs the full response process.

---

# 50. Security Invariants

The following authorization invariants are mandatory.

### Invariant 1 — Authentication Is Not Authorization

A valid identity does not automatically receive operational permissions.

### Invariant 2 — Deny by Default

Missing or uncertain permission must result in denial.

### Invariant 3 — Least Privilege

Employees receive only the authority required for their responsibilities.

### Invariant 4 — Branch Independence

Functional permissions do not automatically grant additional branch scope.

### Invariant 5 — Resource Ownership

Permissions cannot bypass business, branch, or resource ownership boundaries.

### Invariant 6 — No Self-Escalation

An employee cannot grant themselves additional authority.

### Invariant 7 — Delegation Boundary

An employee cannot grant another identity privileges beyond the employee's own delegation authority.

### Invariant 8 — Owner Boundary

Owner authority remains inside the business boundary and does not become platform authority.

### Invariant 9 — Manager Boundary

Managers cannot escalate themselves or other employees beyond their delegated authority.

### Invariant 10 — Override Control

Permission overrides must be explicit, bounded, auditable, and revocable.

### Invariant 11 — Revocation

Revoked permissions must not authorize new operations.

### Invariant 12 — No Client-Side Bypass

Hidden or unavailable UI functionality cannot be treated as an authorization boundary.

### Invariant 13 — Cross-Channel Consistency

Authorization must remain consistent across UI, API, offline, background, synchronization, import, and export paths.

### Invariant 14 — No Identifier Bypass

Resource identifiers cannot be used to circumvent authorization.

### Invariant 15 — Auditability

Security-sensitive authorization changes must be auditable.

### Invariant 16 — No Implicit Privilege Accumulation

Role changes and overrides must not create unintended permanent privilege accumulation.

---

# 51. Relationship to Other Security Documents

This document builds on:

* `01_Security_Architecture_Overview.md`
* `02_Security_Principles_and_Threat_Model.md`
* `03_Identity_and_Access_Security.md`
* `04_Business_and_Tenant_Isolation_Security.md`
* `05_Branch_and_Scope_Isolation_Security.md`
* `06_Authentication_Security_Standards.md`

It complements technical authorization requirements documented in:

* Architecture;
* Backend;
* API;
* Database;
* Frontend;
* Deployment;
* Testing.

This document defines **what authorization security must guarantee**, while technical documentation defines **how those guarantees are implemented**.

---

# 52. Final Authorization Rules

The FastFood ERP authorization model follows these final rules:

1. Every protected operation requires an authorization decision.
2. Authorization is separate from authentication.
3. Roles do not automatically grant unrestricted authority.
4. Permissions must represent explicit capabilities.
5. Least privilege is mandatory.
6. Branch scope and functional permissions remain independent.
7. Resource ownership cannot be bypassed.
8. Permission overrides must be explicit and auditable.
9. No employee may grant themselves additional authority.
10. No employee may delegate authority beyond their own authorization.
11. Managers cannot escalate themselves or other employees beyond their delegated scope.
12. Owner authority remains within the business boundary.
13. All-branch permissions require explicit authorization.
14. Sensitive permissions should support separation of duties where appropriate.
15. Temporary and emergency privileges must be bounded and revocable.
16. Role and permission changes must be auditable.
17. Revoked privileges must not authorize new operations.
18. Client-side restrictions are not sufficient security controls.
19. Imports, exports, offline operations, synchronization, and background jobs must respect authorization.
20. Authorization must fail closed when required security context cannot be safely established.
21. Authorization must remain consistent across all system access paths.
22. Privilege escalation must be prevented both vertically and horizontally.

---

# 53. Acceptance Criteria

This document is accepted when:

* role-based authorization is defined;
* permissions are separated from roles;
* branch scope and functional permission boundaries are defined;
* role templates are governed;
* employee-specific permissions are governed;
* permission overrides are defined;
* override precedence is governed;
* Owner and Manager authority boundaries are defined;
* delegation security is defined;
* vertical and horizontal privilege escalation are addressed;
* temporary and emergency privileges are governed;
* permission revocation is defined;
* permission accumulation is addressed;
* imports, exports, offline, background, and synchronization authorization are covered;
* authorization auditing requirements are defined;
* authorization threats are documented;
* security invariants are explicit;
* implementation details remain outside the security policy document.

**Status: Accepted**

**End of SEC-07**

