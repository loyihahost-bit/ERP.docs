# Identity and Access Domain

**Document ID:** DA-03
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Identity and Access domain defines how FastFood ERP identifies users and determines what they are allowed to do.

It covers:

* employee identity;
* authentication identity;
* roles;
* permissions;
* employee overrides;
* branch scope;
* effective permissions;
* access lifecycle;
* device trust relationship;
* authorization decisions;
* access history.

This domain does not own business operations such as orders, payments, inventory, or cash.

It only determines whether an actor is allowed to perform an operation.

---

# 2. Domain Responsibility

The Identity and Access domain answers two fundamental questions:

1. **Who is acting?**
2. **What is this actor allowed to do in the current context?**

Conceptually:

```text id="6w1n0g"
Authentication
      ↓
Employee Identity
      ↓
Role Permissions
      +
Employee Overrides
      +
Branch Scope
      +
Subscription Entitlement
      +
Device Trust
      ↓
Effective Authorization
```

Authentication establishes identity.

Authorization establishes permission.

These are separate concerns.

---

# 3. Core Concepts

The domain contains the following major concepts:

```text id="r0x3c7"
Employee
Authentication Identity
Role
Permission
Employee Permission Override
Branch Scope
Effective Permission
Access State
Device Trust Relationship
Authorization Decision
```

Not every concept must become a standalone database table.

The final persistence structure will be defined during Database Analysis.

---

# 4. Employee Identity

An Employee represents an operational person belonging to a Business.

An Employee has one stable UUID.

The Employee UUID must remain stable throughout the employee's lifecycle.

It must not change because of:

* role changes;
* branch changes;
* permission changes;
* salary changes;
* device changes;
* password changes;
* deactivation;
* reactivation where allowed.

Employee identity belongs to exactly one Business.

---

# 5. Employee Lifecycle

The Employee domain uses the following basic lifecycle:

```text id="z6apm0"
Created
   ↓
Active
   ↓
Inactive
```

An inactive employee remains historically available.

Historical records must continue to reference the original Employee UUID.

Deactivation does not delete:

* orders;
* payments;
* cash sessions;
* inventory transactions;
* attendance;
* payroll;
* audit events.

---

# 6. Authentication Identity

Authentication identity represents the credentials or authentication mechanism used to prove that an employee is the actor.

Authentication may include:

* password;
* PIN;
* verification code;
* future authentication mechanisms.

Authentication credentials must not be treated as the Employee entity itself.

The system must separate:

```text id="n6v1f3"
Authentication Credential
        ↓
Authenticated Identity
        ↓
Employee
```

Changing authentication credentials must not create a new Employee.

---

# 7. Authentication vs Authorization

Authentication answers:

> Is this really the claimed employee?

Authorization answers:

> Is this employee allowed to perform this operation?

Example:

```text id="y7y1n1"
Employee authenticated
        ↓
Employee = Cashier A
        ↓
Permission check
        ↓
Can close cash session?
        ↓
Yes / No
```

A successful login does not imply unrestricted access.

---

# 8. Roles

A Role is a reusable permission template.

Examples include:

* Owner;
* Manager;
* Cashier;
* Waiter;
* Cook;
* custom business roles.

A role should primarily define a reusable permission set.

Role names alone must not be used as the authorization mechanism.

The system must evaluate actual permissions.

---

# 9. Permissions

A Permission represents a specific capability.

Examples:

```text id="td8o0p"
order.create
order.accept
order.modify
order.cancel

payment.create
payment.correct
refund.create

cash.session.open
cash.session.close
cash.correction.create

inventory.adjust
inventory.count
inventory.purchase

recipe.create
recipe.modify
recipe.approve

employee.create
employee.permission.manage

report.view
report.export
```

The exact permission catalog will be defined in the detailed security and architecture analysis.

Permissions should be granular enough to support business requirements without creating unnecessary complexity.

---

# 10. Employee Permission Overrides

An Employee may have permissions that differ from the permissions inherited from their Role.

Two common override types are:

```text id="j2d2uk"
Grant
Deny
```

The effective permission calculation must define how these overrides interact with role permissions.

Employee overrides are explicitly scoped to the Business and, where applicable, Branch.

---

# 11. Branch Scope

An employee may work in:

* one Branch;
* multiple Branches;
* all permitted Branches.

Branch scope is independent from the role itself.

Example:

```text id="q7o5e3"
Employee
   │
   ├── Branch A → Manager permissions
   ├── Branch B → Cashier permissions
   └── Branch C → No access
```

This allows the same employee to have different operational authority in different branches.

---

# 12. Effective Authorization

The system must calculate effective authorization using all applicable constraints.

Conceptually:

```text id="1wz3e9"
Effective Permission
=
Role Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
+
Employee State
+
Device Trust
+
Current Security Context
```

All conditions must be satisfied.

A permission granted by a Role must not override:

* inactive employee state;
* invalid branch scope;
* expired subscription entitlement;
* invalid device authorization;
* security restrictions.

---

# 13. Permission Precedence

The authorization model must produce one deterministic result.

A simplified evaluation order is:

```text id="v8d5pu"
1. Authenticate actor
2. Validate Business context
3. Validate Employee state
4. Validate Branch scope
5. Evaluate Role permissions
6. Apply Employee overrides
7. Evaluate Subscription entitlement
8. Evaluate Device Trust where required
9. Evaluate operation-specific business rules
10. Allow or reject
```

The exact precedence of Grant and Deny overrides will be finalized in the security architecture.

It must never depend on UI behavior.

---

# 14. Business Scope

Every Employee belongs to one Business.

Every authorization decision must be evaluated inside a Business context.

The client must not be trusted to choose a Business arbitrarily.

The server must validate:

```text id="i1r7fl"
Authenticated Employee
        ↓
Employee Business
        =
Requested Business
```

If they do not match, access is rejected.

---

# 15. Branch Authorization

For branch-scoped operations:

```text id="qz6q0r"
Employee
   ↓
Business Match
   ↓
Branch Access
   ↓
Permission
   ↓
Operation
```

A user who can access Branch A must not automatically access Branch B.

An Owner may have Business-wide access according to configured permissions.

---

# 16. Subscription Entitlement

Permission alone does not guarantee that an operation is available.

The subscription entitlement is an additional constraint.

Example:

```text id="n8e5k1"
Employee has report.export
        ↓
Business subscription allows report export?
        ↓
Yes → Continue
No  → Reject
```

Subscription checks must be enforced server-side.

Frontend visibility is only a usability mechanism.

---

# 17. Device Trust

A trusted device represents an approved device associated with a Business and, where applicable, Branch and employee access context.

Device trust does not grant permissions.

Instead:

```text id="2p4p2c"
Employee Authorization
        +
Trusted Device
        ↓
Operation may proceed
```

A trusted device may be required for:

* offline operation;
* sensitive POS operations;
* local credential persistence;
* offline synchronization.

---

# 18. Device Revocation

A trusted device may be revoked.

After revocation:

* new offline authorization must not be issued;
* existing offline authorization must be bounded by its validity rules;
* synchronization must revalidate device state;
* unauthorized future operations must be rejected.

Device revocation must not delete historical transactions created by that device.

---

# 19. Employee Deactivation

When an employee becomes inactive:

1. New authorization must be rejected.
2. New operational actions must be rejected.
3. Existing historical operations remain valid.
4. Historical attribution remains unchanged.
5. Pending offline operations must be validated against the employee's effective deactivation time.
6. Unauthorized post-deactivation operations must be rejected or recorded as conflicts according to synchronization rules.

Employee deactivation must not rewrite previous records.

---

# 20. Role Changes

A role change affects future authorization.

Historical transactions must not be reinterpreted using the employee's current role.

Example:

```text id="w0e5f4"
Employee
   ↓
Cashier
   ↓
Creates Payment
   ↓
Later promoted to Manager
```

The historical payment remains attributed to the employee as the original actor.

The current Manager role does not change historical authorization context.

---

# 21. Permission Changes During Active Sessions

Permission changes may occur while an employee is logged in.

For important operations, the server must evaluate the current authorization state at operation time.

The client must not rely solely on permissions loaded during login.

Therefore:

```text id="s5p0a8"
Old Session
    ↓
Permission Changed
    ↓
Next Important Operation
    ↓
Server Re-evaluation
```

The operation is either allowed or rejected according to the current effective permissions.

---

# 22. Branch Switching

An employee with access to multiple branches may switch active branch context.

Branch switching must trigger recalculation of:

* effective permissions;
* branch configuration;
* menu availability;
* inventory context;
* cash context;
* device requirements where applicable.

The active branch must never be changed merely by modifying a frontend variable.

The server must validate the selected Branch.

---

# 23. Permission Management

Permission management itself is permission-controlled.

A Manager cannot grant permissions beyond their own authority.

An employee must not be able to:

* grant themselves additional permissions;
* grant permissions they cannot grant;
* expand their own branch scope;
* bypass subscription limits.

Owner permission management remains subject to Business and Subscription constraints.

---

# 24. Delegated Permission Management

A user may receive permission to manage selected employee permissions.

However, delegation must remain bounded.

Example:

```text id="4m8b2q"
Owner
   ↓
Manager
   ↓
Can manage selected permissions
   ↓
Cannot grant Owner-level authority
```

Delegation must not become a path to privilege escalation.

---

# 25. Role Templates

Employee permissions may be used to create or update role templates where permitted.

The resulting Role must be treated as its own configuration.

Changing a Role later does not necessarily rewrite historical permission state.

If a role change affects active employees, the effective permission must be recalculated.

---

# 26. Permission Versioning

Important permission configuration changes should preserve:

* previous configuration;
* new configuration;
* actor;
* timestamp;
* reason where required;
* affected employees or roles;
* Business;
* Branch scope.

This allows historical authorization changes to be reconstructed.

---

# 27. Authorization Decision Context

A permission decision may depend on:

```text id="u0v3lm"
Business
Branch
Employee
Role
Permission
Subscription
Device
Cash Session
Operation
Entity
Current State
```

Not every operation requires every context.

The authorization system should load only the context required for the specific operation.

---

# 28. Operation-Level Authorization

Authorization must be evaluated against the operation being performed.

For example:

```text id="h9u8ka"
Viewing Order
≠
Modifying Order
≠
Accepting Order
≠
Cancelling Order
≠
Refunding Payment
```

Having access to one operation must not automatically grant access to another.

---

# 29. Business Rules After Authorization

Authorization is not the final business check.

The system must also validate domain state.

Example:

```text id="j3m8x4"
Authenticated
   ↓
Authorized
   ↓
Order exists
   ↓
Order is modifiable
   ↓
Inventory available
   ↓
Operation allowed
```

A user may have permission to accept orders but still be unable to accept a particular order because its domain state is invalid.

---

# 30. Offline Authorization

Offline authorization must be explicitly issued for trusted devices.

It must contain sufficient security context to validate:

* Employee;
* Business;
* Branch;
* permissions;
* device;
* subscription entitlement;
* authorization validity;
* offline validity window.

Offline authorization must be cryptographically protected.

The local client must not be able to modify its permission set.

---

# 31. Offline Permission Changes

If permissions change while a device is offline:

* the device continues only within its previously valid offline authorization boundaries;
* it must not extend authorization beyond the signed authorization;
* synchronization revalidates the operation;
* unauthorized operations become rejected or conflict records.

Critical permission revocations should prevent future authorization renewal.

---

# 32. Offline Employee Deactivation

If an employee is deactivated while their device is offline, the device may temporarily contain valid previously issued offline authorization.

However:

* the authorization cannot exceed its expiration;
* synchronized operations are checked against the employee's effective deactivation time;
* operations after the deactivation boundary must not be silently accepted;
* conflicts must preserve the original event for investigation.

---

# 33. Authorization and Cash Sessions

Cash operations require both permission and appropriate session context.

Examples:

```text id="7p0s8m"
Open Cash Session
=
Authentication
+
Branch Scope
+
cash.session.open
+
Valid Device Context
+
Valid Branch State
```

Closing, handover, and corrections have separate permissions.

A cashier's ability to create orders does not automatically grant cash correction permission.

---

# 34. Authorization and Inventory

Inventory permissions must be granular.

Examples:

* View inventory;
* Create purchase;
* Perform stock adjustment;
* Perform inventory count;
* Confirm discrepancy;
* View cost information.

An employee may be allowed to view inventory without being allowed to change it.

---

# 35. Authorization and Recipes

Recipe operations should distinguish:

* View recipe;
* Create recipe;
* Modify recipe;
* Approve recipe;
* Archive recipe.

Restricted recipe visibility must be permission-controlled.

Recipe modification and recipe approval should not automatically be treated as the same authority.

---

# 36. Authorization and Payments

Payment permissions should distinguish:

* Create payment;
* View payment;
* Correct payment;
* Create refund;
* Approve refund;
* Manage debt;
* View financial reports.

A cashier may have normal payment creation permission without having refund or correction authority.

---

# 37. Authorization and Reports

Report access must consider:

* report permission;
* Business scope;
* Branch scope;
* report type;
* subscription entitlement.

Export permission may be separate from view permission.

Example:

```text id="m0w4op"
report.view
      ≠
report.export
```

---

# 38. Authorization and Payroll

Payroll information is sensitive.

Access should distinguish:

* attendance access;
* payroll calculation;
* payroll viewing;
* payroll correction;
* salary configuration.

An employee's general management permission does not automatically grant access to salary information.

---

# 39. Sensitive Information

The Identity and Access domain contains security-sensitive information.

Examples:

* authentication credentials;
* permission configuration;
* device trust;
* authorization tokens;
* security events.

Sensitive credentials must not be stored in plaintext.

Sensitive values must not be unnecessarily exposed through:

* API responses;
* logs;
* audit records;
* reports;
* error messages.

---

# 40. Audit Requirements

Important Identity and Access changes must generate audit records.

Examples:

* Employee created;
* Employee deactivated;
* Role assigned;
* Role changed;
* Permission granted;
* Permission denied;
* Branch scope changed;
* Device trusted;
* Device revoked;
* Authentication security event;
* Privileged access change.

Routine successful reads do not normally require audit events unless explicitly classified as sensitive.

---

# 41. Historical Authorization

Historical records must preserve the actor and context relevant to the original operation.

The system must not determine historical authorization solely from today's permissions.

For example:

```text id="5xyj4g"
Payment Created
      ↓
Actor = Employee A
      ↓
Role at the time = Cashier
      ↓
Current Role = Manager
```

The historical transaction remains associated with the original actor and operation context.

---

# 42. Authorization Caching

Authorization results may be cached for performance only when:

* cache invalidation is reliable;
* permission changes invalidate affected authorization state;
* employee deactivation invalidates access;
* subscription changes invalidate entitlement state;
* branch scope changes invalidate branch access;
* device revocation invalidates applicable trust state.

Security correctness has priority over cache performance.

---

# 43. Concurrency

Identity and Access changes may race with operational actions.

Examples:

* permission revoked while a payment is being created;
* employee deactivated while an order is being accepted;
* branch access removed while a report is being generated;
* subscription expires while a configuration update is submitted.

Important operations must use server-side authorization at the appropriate transaction boundary.

A stale client authorization must not bypass a newer security state.

---

# 44. Idempotency

Security operations that may be retried should be idempotent where applicable.

Examples:

* device registration;
* device revocation;
* role assignment;
* permission update;
* employee deactivation;
* permission synchronization.

Repeated processing must not create duplicate security state.

---

# 45. Domain Services

Potential Identity and Access domain services include:

```text id="o8u0pp"
Authentication Service
Authorization Service
Effective Permission Resolver
Branch Access Resolver
Permission Management Service
Device Trust Service
Authorization Context Builder
```

These are logical services.

They do not require separate deployed services.

---

# 46. Domain Events

Potential domain events include:

```text id="c5x1ru"
EmployeeCreated
EmployeeActivated
EmployeeDeactivated
RoleAssigned
RoleChanged
PermissionGranted
PermissionRevoked
BranchAccessChanged
DeviceTrusted
DeviceRevoked
AuthenticationSecurityEventRecorded
```

Events represent facts that occurred.

They must not replace the authoritative access state.

---

# 47. Aggregate Boundaries

The Employee/Identity aggregate must remain independent from operational aggregates.

Identity changes must not require loading:

* all Orders;
* all Payments;
* all Inventory;
* all Reports.

For example, deactivating an employee changes access state.

It does not rewrite historical orders created by that employee.

---

# 48. Security Boundary

The Identity and Access domain is one of the primary security boundaries of FastFood ERP.

Every protected operation must pass through:

```text id="r6x6jh"
Authentication
      ↓
Tenant Validation
      ↓
Branch Scope
      ↓
Effective Permission
      ↓
Subscription Constraint
      ↓
Device Constraint
      ↓
Domain Rule
```

The exact sequence may be optimized in implementation, but no required security constraint may be skipped.

---

# 49. Performance Principles

Authorization must be fast enough for POS operations.

The implementation should avoid:

* loading unnecessary employee data;
* loading complete role graphs;
* loading full audit history;
* repeated expensive permission calculations within one request.

Permission resolution should use efficient representations and safe caching where appropriate.

Security must not require heavy hardware at the POS.

---

# 50. Domain Invariants

### Identity

1. Every Employee has one stable UUID.
2. An Employee belongs to exactly one Business.
3. Authentication identity does not replace Employee identity.
4. Changing credentials does not create a new Employee.

### Authentication

5. Authentication must establish the actor before protected operations.
6. Authentication does not grant authorization.
7. Invalid authentication must prevent protected operations.
8. Authentication credentials must remain protected.

### Authorization

9. Authorization is evaluated server-side.
10. Permissions are operation-specific.
11. Business scope must always be enforced.
12. Branch scope must be enforced for branch-scoped operations.
13. Subscription entitlement is an additional authorization constraint.
14. Device trust does not grant permissions.
15. Inactive employees cannot perform new authorized operations.
16. Employees cannot grant themselves permissions.
17. Managers cannot grant authority beyond their delegated scope.

### Roles and Overrides

18. Roles provide reusable permission templates.
19. Employee overrides may modify effective permissions.
20. Override evaluation must be deterministic.
21. Permission changes must not rewrite historical transactions.

### Devices

22. Trusted devices are Business-scoped.
23. Device revocation cannot delete historical operations.
24. Offline authorization must be cryptographically protected.
25. Offline authorization cannot be extended by local client modification.

### Offline

26. Offline operations remain bound to the original Employee.
27. Offline operations remain bound to the original Business.
28. Offline operations remain bound to the authorized Branch.
29. Synchronization revalidates authorization.
30. Post-deactivation offline operations cannot be silently accepted.

### Historical Integrity

31. Historical actors remain identifiable.
32. Historical role state must not be inferred only from current permissions.
33. Permission changes must remain auditable.
34. Security history must remain reconstructable.

### Concurrency

35. Important authorization changes must be safe against concurrent operations.
36. Revoked access must not be bypassed by stale client state.
37. Duplicate security operations must not create duplicate state.

### Security

38. Cross-business authorization is forbidden.
39. Cross-branch authorization is forbidden unless explicitly permitted.
40. Client-provided permissions are never trusted.
41. Client-provided Business scope is never trusted without server validation.
42. Sensitive security data must not be unnecessarily exposed.

---

# 51. Completion Criteria

The Identity and Access domain is considered complete when:

* Employee identity is defined;
* authentication and authorization are separated;
* roles are defined;
* permissions are defined;
* employee overrides are defined;
* branch scope is defined;
* subscription constraints are defined;
* device trust is defined;
* offline authorization is defined;
* permission changes are defined;
* employee lifecycle is defined;
* historical attribution is defined;
* concurrency behavior is defined;
* audit requirements are defined;
* domain boundaries are clear.

---

## Related Documents

### Previous

* `docs/03_Domain_Analysis/README.md`
* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`

### Business Analysis

* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/15_Employees_Attendance_and_Payroll.md`

### System Analysis

* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/12_Employee_and_Payroll_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`

### Future

* `docs/04_Architecture/`
* `docs/11_Security/`

