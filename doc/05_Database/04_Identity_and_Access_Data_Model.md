# Identity and Access Data Model

**Document ID:** DB-04
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* user identity;
* employee accounts;
* roles;
* permissions;
* employee permission overrides;
* branch scope;
* authentication state;
* account lifecycle;
* authorization-related relationships.

The database model must preserve a strict separation between:

1. Identity
2. Authentication
3. Authorization
4. Branch scope
5. Device trust
6. Subscription entitlement

A trusted device or valid authentication session must never independently grant business permissions.

---

## 2. Design Principles

The identity and access data model follows these principles:

* Every normal operational user has an individual identity.
* Shared operational accounts are not supported.
* Employee identity is different from employee permissions.
* Authentication proves who the user is.
* Authorization determines what the user may do.
* Branch scope determines where the user may operate.
* Subscription entitlement determines which capabilities are available.
* Device trust determines whether the device may participate in trusted/offline operation.
* Historical employee actions must remain attributable after account deactivation.
* Permission changes must be auditable.
* Deleted identities must not cause historical records to lose their original actor reference.
* UUIDs are used for stable identity references.

---

# 3. Identity Model

## 3.1 Identity

`Identity` represents the system-level account used for authentication.

Conceptual fields:

* `id`
* `username` or login identifier
* `status`
* `created_at`
* `updated_at`
* `last_authenticated_at`
* `deactivated_at`

The exact authentication credential structure is defined by the security architecture.

The identity does not directly represent a Business, Branch, Role, or Device.

---

## 3.2 Identity UUID

`identity.id` must be:

* UUID;
* globally unique;
* immutable;
* never reused.

The UUID is the stable database reference to the identity.

Human-readable login values must not be used as primary keys.

---

# 4. Employee Model

## 4.1 Employee

`Employee` represents a person's operational relationship with a Business.

Conceptual fields:

* `id`
* `business_id`
* `identity_id`
* employee profile fields
* `status`
* `created_at`
* `updated_at`
* `deactivated_at`

The employee belongs to exactly one Business.

An Identity may be associated with an Employee according to the supported account model, but Business ownership and employee membership must remain explicitly scoped.

---

## 4.2 Employee and Identity Separation

The following concepts must not be merged:

```text
Identity
    ↓
Employee
    ↓
Role / Permissions
    ↓
Branch Scope
```

Identity answers:

> Who is authenticating?

Employee answers:

> Which Business employee is this identity acting as?

Authorization answers:

> What may this employee do?

Branch scope answers:

> Where may the employee do it?

---

# 5. Employee Lifecycle

Employee lifecycle:

```text
Created
   ↓
Active
   ↓
Inactive
```

An inactive employee:

* cannot perform new authorized operations;
* cannot authenticate for normal operational activity;
* cannot use offline authorization after the effective deactivation point;
* remains available for historical references.

Employee records must not be physically deleted merely because the employee leaves the Business.

---

# 6. Business Ownership

An Employee may have an Owner role.

The Owner role is an authorization concept and must not be represented by deleting or bypassing the normal employee model.

Multiple Owners may exist within the same Business.

The allowed number of Owners is controlled by subscription entitlement.

Therefore:

```text
Business
   ↓
Employee
   ↓
Role = Owner
```

The Business table must not contain a single hard-coded owner identity.

---

# 7. Role Model

## 7.1 Role

A Role represents a reusable authorization template.

Conceptual fields:

* `id`
* `business_id` or platform scope where applicable
* `name`
* `status`
* `created_at`
* `updated_at`

Examples include:

* Owner
* Manager
* Cashier
* Waiter
* Cook
* Custom roles

The system must support custom roles where permitted.

---

## 7.2 Role Ownership

Business-level operational roles belong to the Business.

A role from Business A must never be usable by an Employee belonging to Business B.

Platform-level roles, such as Super Admin, are separate from Business operational roles.

---

# 8. Permission Model

## 8.1 Permission

A Permission represents one atomic capability.

Examples:

```text
order.create
order.modify
order.cancel
payment.create
payment.refund
cash.session.open
cash.session.close
inventory.adjust
recipe.modify
employee.create
employee.permission.manage
report.view
report.export
```

The exact permission catalog is defined by System Analysis and authorization configuration.

Permission identifiers should be stable machine-readable values.

Human-readable labels must not be used as authorization keys.

---

# 9. Role-Permission Relationship

A Role may have multiple permissions.

A Permission may belong to multiple Roles.

Therefore:

```text
Role
  ↕
RolePermission
  ↕
Permission
```

`RolePermission` represents the assignment rather than duplicating permission definitions inside each role.

The relationship must be uniquely constrained so the same permission cannot be assigned twice to the same role.

---

# 10. Employee Permission Override

The system supports employee-level permission overrides.

Conceptually:

```text
Role Permissions
       +
Employee Overrides
       ↓
Effective Permissions
```

An Employee Override may:

* grant a permission;
* deny a permission.

The exact precedence rules are defined by the authorization model.

The database must preserve the source of the effective permission.

---

# 11. Permission Precedence

Effective authorization is conceptually calculated from:

```text
Role Permission
        +
Employee Override
        +
Branch Scope
        +
Subscription Entitlement
```

The database must not store a permanently materialized "final permission" as the only authorization source.

Effective permissions may be calculated or cached, but authoritative permission assignments remain separately stored.

---

# 12. Branch Scope

Employees may operate in:

* one Branch;
* multiple Branches;
* all permitted Business Branches.

A branch assignment must be explicitly represented.

Conceptual relationship:

```text
Employee
    ↓
EmployeeBranch
    ↓
Branch
```

The relationship may include:

* assignment status;
* effective start;
* effective end;
* branch-specific role/permission configuration where required.

---

# 13. Branch-Specific Permissions

The same employee may have different permissions in different branches.

Example:

```text
Employee A
 ├── Branch 1 → Cashier
 └── Branch 2 → Manager
```

The database must therefore not assume that one Employee has one globally fixed operational permission set.

Authorization queries must include the active Branch context.

---

# 14. Role Assignment

An Employee may have one or more role assignments according to the authorization model.

Role assignment should be represented independently from the Role definition.

Conceptual model:

```text
Employee
    ↓
EmployeeRole
    ↓
Role
```

If a role assignment is branch-specific, the relationship must retain the corresponding Branch scope.

---

# 15. Permission Scope

Permissions may be:

* Business-wide;
* Branch-specific;
* resource-specific where required by the authorization model.

The database must prevent a branch-scoped permission assignment from silently becoming a Business-wide permission.

---

# 16. Manager Delegation

A Manager may manage employees only when the Manager has the required permission.

The database must not treat the Manager role itself as unlimited authority.

A Manager cannot grant:

* permissions they do not possess;
* permissions beyond their Branch scope;
* permissions blocked by subscription entitlement.

Authorization enforcement remains an application-level responsibility supported by database relationships and constraints.

---

# 17. Permission Change History

Permission changes must be historically reconstructable.

Changes include:

* role permission added;
* role permission removed;
* employee override added;
* employee override removed;
* role assigned;
* role removed;
* branch assignment added;
* branch assignment removed.

Historical records must not be silently overwritten.

Audit records provide the authoritative change history.

---

# 18. Authentication State

Authentication-related data may include:

* credential metadata;
* credential version;
* authentication status;
* failed-attempt metadata;
* last successful authentication;
* account security timestamps.

Sensitive authentication secrets must never be stored in plaintext.

Password hashes must use the approved password hashing strategy.

Authentication secrets are not part of normal employee profile data.

---

# 19. Session Data

Authenticated sessions may be represented separately from Identity.

Conceptual relationship:

```text
Identity
   ↓
Authentication Session
```

A session may include:

* session UUID;
* identity UUID;
* issued time;
* expiration time;
* revocation time;
* authentication context;
* security metadata.

Session storage must not become the source of authorization truth.

Current authorization must still be validated against active Business, Employee, Branch, Role, Permission, and Subscription state where required.

---

# 20. Device Relationship

Device trust is a separate domain.

Conceptual relationship:

```text
Employee
   ↕
EmployeeDevice
   ↕
Device
```

A trusted device does not automatically receive all Employee permissions.

Device trust answers:

> Is this device authorized to participate in trusted/offline operation?

Employee authorization answers:

> What may this employee do?

Both checks must succeed where required.

---

# 21. Offline Authorization Relationship

Offline authorization must reference sufficient identity context to prevent unauthorized replay.

Conceptually:

```text
Business
Employee
Branch
Device
Permissions
Subscription
        ↓
Offline Authorization
```

The database stores authoritative server-side state and authorization history.

Cryptographically protected offline authorization artifacts themselves may be stored on the client rather than the authoritative database.

---

# 22. Subscription Interaction

Permission assignments and subscription entitlement are separate.

Example:

```text
Employee has permission:
    inventory.adjust

Subscription allows:
    inventory management

Effective:
    ALLOWED
```

If the subscription blocks the feature:

```text
Employee has permission:
    inventory.adjust

Subscription allows:
    inventory management = NO

Effective:
    DENIED
```

The database must not delete permissions when subscription entitlement changes.

---

# 23. Subscription Downgrade

When a Business is downgraded:

* employee records remain;
* role assignments remain;
* permission assignments remain;
* branch assignments remain;
* historical authorization remains;
* newly prohibited operations are blocked.

The database must preserve data rather than destructively modifying authorization assignments.

---

# 24. Employee Limit

Subscription employee limits are entitlement rules.

If the Business exceeds a newly reduced employee limit:

* existing employees remain;
* historical records remain;
* existing assignments remain unless explicitly changed;
* new employee creation may be blocked.

The database must not automatically delete employees because of a tariff downgrade.

---

# 25. Deactivation

Employee deactivation must preserve:

* Employee UUID;
* Identity reference;
* historical orders;
* payments;
* cash sessions;
* inventory operations;
* attendance;
* payroll;
* audit records;
* reports;
* synchronization history.

New operational transactions must reject the inactive employee.

---

# 26. Historical Actor References

Operational records should reference the Employee UUID where the employee is the business actor.

Examples:

```text
Order → employee_id
Payment → employee_id
CashSession → employee_id
InventoryTransaction → employee_id
Attendance → employee_id
AuditEvent → employee_id
```

Historical references must remain resolvable after employee deactivation.

---

# 27. Actor Snapshot

Where historical reporting requires stable display information, selected actor information may be snapshotted.

For example:

* employee display name at transaction time;
* role at transaction time;
* branch context at transaction time.

Snapshots must not replace the authoritative Employee UUID.

---

# 28. Cross-Business Isolation

An Employee may belong to only one Business.

A role, permission assignment, branch assignment, device relationship, or session context must not cross Business boundaries.

Database queries must always validate:

```text
business_id
```

before operating on Business-scoped authorization data.

---

# 29. Branch Isolation

A Branch-scoped authorization record must reference the correct Business.

Conceptually:

```text
Business
  └── Branch
       └── EmployeeBranch
            └── Employee
```

Cross-business branch assignments must be impossible.

---

# 30. Unique Constraints

The database should enforce uniqueness where business rules require it.

Examples:

* Identity UUID;
* Employee UUID;
* Role UUID;
* Permission UUID;
* Business + role name where applicable;
* Role + permission;
* Employee + Branch assignment;
* Employee + role assignment where applicable.

Exact uniqueness rules must be finalized with the physical schema.

---

# 31. Foreign Key Strategy

Foreign keys should protect core identity relationships.

Important relationships include:

```text
Employee → Business
Employee → Identity
EmployeeBranch → Employee
EmployeeBranch → Branch
EmployeeRole → Employee
EmployeeRole → Role
RolePermission → Role
RolePermission → Permission
Session → Identity
```

Foreign keys must not allow a record from one Business to reference an incompatible Business-scoped record.

Where PostgreSQL composite constraints are appropriate, they should be used to enforce tenant consistency at the database boundary.

---

# 32. Deletion Strategy

Normal identity and employee records must use logical lifecycle states rather than destructive deletion.

Deletion is especially restricted when historical records depend on the identity.

The database must preserve historical actor references.

Physical deletion is allowed only as part of the controlled Business data deletion lifecycle when the entire Business is permanently deleted.

---

# 33. Concurrency

Permission and role changes may occur concurrently.

The system must prevent:

* duplicate role assignments;
* duplicate permission assignments;
* stale updates silently overwriting newer changes;
* permission changes being lost;
* branch assignments being duplicated.

Optimistic versioning or appropriate database constraints should be used where necessary.

---

# 34. Authorization Cache

Effective permissions may be cached for performance.

However:

* cache is not authoritative;
* permission changes must invalidate affected cache entries;
* Business and Branch context must be part of cache keys;
* subscription state must not be ignored;
* stale authorization must not permit prohibited operations.

A cache failure must not corrupt authorization data.

---

# 35. Indexing

Important indexes should support:

* Employee by Business;
* Employee by Identity;
* Employee by status;
* EmployeeBranch by Employee;
* EmployeeBranch by Branch;
* EmployeeRole by Employee;
* EmployeeRole by Role;
* RolePermission by Role;
* RolePermission by Permission;
* active sessions by Identity;
* audit records by Employee.

Indexes must reflect actual query patterns and should be reviewed during performance testing.

---

# 36. Audit Integration

Authorization changes are high-value audit events.

Audit records should identify:

* actor;
* Business;
* Branch where applicable;
* target Employee;
* target Role;
* target Permission;
* previous state;
* new state;
* reason where required;
* timestamp;
* Device UUID;
* source;
* Transaction UUID where applicable.

Ordinary permission reads do not require audit events unless classified as sensitive access.

---

# 37. Reporting Integration

Reports may use identity and employee data to show:

* cashier;
* waiter;
* manager;
* employee;
* branch;
* payroll employee;
* attendance employee;
* correction actor;
* authorization actor.

Historical report versions must retain enough snapshot data to prevent later employee profile changes from rewriting historical meaning.

---

# 38. Offline and Synchronization Integration

Offline operations may reference:

* Employee UUID;
* Business UUID;
* Branch UUID;
* Device UUID;
* Transaction UUID.

When synchronized, the server must verify:

1. Business exists and is active for the operation.
2. Employee exists.
3. Employee was active at the operation time.
4. Employee had the required permission.
5. Employee had the required Branch scope.
6. Device was trusted.
7. Subscription permitted the operation.
8. Transaction UUID has not already been processed.

Invalid offline authorization must result in rejection or explicit conflict handling.

It must never silently create unauthorized state.

---

# 39. Employee Deactivation and Offline Events

If an employee is deactivated while an offline device still contains pending operations:

* the server validates the effective deactivation time;
* operations created after the effective deactivation point are rejected or conflicted;
* already valid historical operations remain attributable;
* stale offline authorization cannot reactivate the employee.

---

# 40. Identity and Data Lifecycle

Business deletion eventually removes Business-scoped identity and authorization data as part of the controlled deletion process.

Before permanent deletion:

* active sessions are invalidated;
* trusted devices are invalidated;
* offline authorization becomes unusable;
* pending synchronization cannot recreate the Business;
* historical deletion follows the Data Lifecycle rules.

UUIDs must never be reused after deletion.

---

# 41. Security Requirements

The database layer must support:

* least-privilege database credentials;
* encrypted connections where required;
* protected secrets;
* parameterized queries;
* tenant-scoped queries;
* authorization validation;
* immutable audit records;
* secure password hashes;
* controlled session state;
* safe migration procedures.

The database must never rely solely on frontend authorization.

---

# 42. Database Authority vs Application Authority

The database enforces structural integrity.

The application enforces complex authorization decisions.

### Database responsibilities

* foreign keys;
* uniqueness;
* non-null requirements;
* valid references;
* tenant consistency;
* lifecycle constraints where practical;
* optimistic version constraints.

### Application responsibilities

* effective permission calculation;
* role inheritance/precedence;
* branch authorization;
* subscription entitlement;
* authentication policy;
* session policy;
* device trust;
* Manager delegation;
* operation-level authorization.

---

# 43. Recommended Logical Entity Set

The identity and access database model conceptually contains:

```text
Business
 ├── Identity
 │
 ├── Employee
 │    ├── EmployeeBranch
 │    ├── EmployeeRole
 │    └── EmployeePermissionOverride
 │
 ├── Role
 │    └── RolePermission
 │
 ├── Permission
 │
 ├── AuthenticationSession
 │
 └── Device / EmployeeDevice
```

Some entities belong to other domain models but participate in authorization relationships.

---

# 44. Core Invariants

The following invariants are mandatory:

1. Every Employee belongs to exactly one Business.
2. An Employee cannot belong to two Businesses.
3. Every operational account is individually attributable.
4. Identity UUIDs are immutable.
5. Identity UUIDs are never reused.
6. Employee UUIDs are immutable.
7. Employee deactivation does not erase history.
8. An inactive Employee cannot perform new authorized operations.
9. Role definitions are separate from Employee assignments.
10. Permission definitions are separate from Role assignments.
11. Role-Permission assignments are unique.
12. Employee permission overrides are explicit.
13. Effective permissions are not determined by role alone.
14. Branch scope is part of authorization.
15. A trusted device does not grant permissions.
16. Authentication does not grant authorization.
17. Subscription entitlement can restrict an otherwise valid permission.
18. Subscription downgrade does not delete permissions.
19. Employee-limit downgrade does not delete employees.
20. Cross-Business authorization references are forbidden.
21. Cross-Business branch assignments are forbidden.
22. Manager authority cannot exceed effective permissions.
23. Manager cannot grant permissions they do not possess.
24. Employee history remains attributable after deactivation.
25. Historical actor references must remain stable.
26. Authentication secrets are never stored in plaintext.
27. Sessions do not become authorization truth.
28. Authorization cache is not authoritative.
29. Cache keys must preserve Business scope.
30. Branch-scoped permissions require valid Branch context.
31. Permission changes must be auditable.
32. Role changes must be auditable.
33. Branch assignment changes must be auditable.
34. Employee deactivation must be auditable.
35. Offline operations must carry stable identity references.
36. Offline operations must be revalidated by the server.
37. Stale offline authorization cannot reactivate an Employee.
38. Invalid offline authorization cannot create authorized state.
39. Business deletion invalidates identity access.
40. Business deletion invalidates trusted device access.
41. Pending synchronization cannot resurrect deleted authorization state.
42. Database constraints must protect core identity relationships.
43. Application authorization must not be bypassed by frontend state.
44. Historical report versions must preserve historical actor meaning.
45. UUIDs must not be replaced by mutable usernames as operational references.
46. Identity and Employee are separate concepts.
47. Employee and Role are separate concepts.
48. Role and Permission are separate concepts.
49. Permission and Subscription Entitlement are separate concepts.
50. Device Trust and Authorization are separate concepts.

---

## Related Documents

* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/10_Security_Architecture.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/README.md`
* `adr/ADR-001-Documentation-First.md`

