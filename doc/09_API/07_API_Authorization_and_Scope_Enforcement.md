# API Authorization and Scope Enforcement

**Document ID:** API-07
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines authorization and scope enforcement for the FastFood ERP API.

The API must ensure that every protected operation is executed only when the authenticated actor is authorized to perform that operation within the correct:

* Business;
* Branch;
* resource;
* role;
* permission;
* employee override;
* operational context;
* subscription entitlement;
* device context where applicable;
* Cash Session context where applicable.

Authorization is a server-side responsibility.

The API must never rely on frontend visibility, client-provided identifiers or cached client permissions as authoritative authorization.

---

# 2. Scope

This document covers:

* authorization architecture;
* permission evaluation;
* role permissions;
* employee permission overrides;
* Branch scope;
* Business scope;
* resource scope;
* Manager authority;
* Owner authority;
* Super Admin platform scope;
* Employee status;
* subscription entitlement;
* device restrictions;
* Cash Session restrictions;
* authorization decision order;
* fail-closed behavior;
* authorization caching;
* scope enforcement;
* cross-Business protection;
* cross-Branch protection;
* resource ownership;
* command authorization;
* read authorization;
* mutation authorization;
* bulk authorization;
* synchronization authorization;
* background authorization context;
* external integration authorization;
* authorization errors;
* authorization audit;
* authorization observability;
* authorization performance;
* authorization invariants.

Authentication and request identity construction are defined in:

`06_API_Authentication_and_Request_Context.md`

---

# 3. Authorization Principle

Authentication establishes:

> Who is making the request?

Authorization establishes:

> What is this actor allowed to do in this context?

Scope enforcement establishes:

> Which Business, Branch and resources may this actor access or modify?

The API must evaluate all three dimensions before allowing protected operations.

```text
Authentication
      ↓
Actor Identity
      ↓
Authorization
      ↓
Scope Enforcement
      ↓
Business Rules
      ↓
Operation
```

---

# 4. Server-Side Authority

The server is authoritative for authorization.

The following client-provided values must never be treated as sufficient authorization:

```text
Business UUID
Branch UUID
Employee UUID
Role UUID
Permission UUID
Device UUID
Cash Session UUID
Product UUID
Order UUID
```

These identifiers are only references.

The server must verify their relationship to the authenticated actor and current authoritative state.

---

# 5. Authorization Decision Model

A protected API operation is allowed only when all applicable authorization conditions are satisfied.

Conceptually:

```text
ALLOW =
    Authenticated
    AND Employee Active
    AND Business Scope Valid
    AND Branch Scope Valid
    AND Permission Granted
    AND Subscription Allows Operation
    AND Device Constraints Satisfied
    AND Resource Scope Valid
    AND Operational Context Valid
    AND Business Rules Allow
```

Not every operation requires every condition.

The API must evaluate only conditions applicable to the operation while preserving fail-closed behavior.

---

# 6. Authorization Layers

Authorization is evaluated across several layers:

```text
1. Platform Authorization
2. Business Authorization
3. Branch Authorization
4. Permission Authorization
5. Resource Authorization
6. Operational Context Authorization
7. Subscription Entitlement
8. Business Rule Validation
```

These layers must not be collapsed into a single frontend permission check.

---

# 7. Platform Authorization

Super Admin operates at platform level.

Platform-level authorization may include:

* Business creation;
* subscription/tariff management;
* platform configuration;
* platform-level limits;
* platform administration.

Super Admin authorization must not automatically imply access to every Business's operational data unless that capability is explicitly defined.

Platform authority and Business operational authority are separate concepts.

---

# 8. Business Authorization

Business-level authorization determines whether an actor may operate within a Business.

An employee must have a valid relationship with the Business before accessing Business-scoped resources.

Example:

```text
Employee A
    ↓
Business A → Allowed

Employee A
    ↓
Business B → Denied
```

Changing:

```text
X-Business-ID
```

must not grant access to another Business.

---

# 9. Business Isolation

Every Business-scoped operation must enforce Business isolation.

For example:

```text
GET /api/v1/orders/{order_id}
```

must verify that:

```text
Order.Business
=
Authorized Business Context
```

An Order belonging to another Business must not be returned.

This applies to:

* reads;
* creates;
* updates;
* commands;
* reports;
* files;
* synchronization;
* configuration;
* background operations.

---

# 10. Branch Authorization

Branch scope determines which Branches an employee may access.

An employee may have:

* one Branch;
* multiple Branches;
* all Branches within a Business.

Branch scope is evaluated independently from Business scope.

```text
Business
   ├── Branch A
   ├── Branch B
   └── Branch C
```

An employee authorized for Branch A must not automatically access Branch B.

---

# 11. Branch Scope Examples

Example:

```text
Employee:
Business A

Allowed Branches:
Branch A
Branch C

Denied:
Branch B
```

Requests targeting Branch B must fail even if the employee has the required permission in general.

Permission alone does not grant Branch access.

---

# 12. Permission and Scope Are Separate

A valid permission does not automatically grant access to every Branch.

Example:

```text
Permission:
inventory.adjust

Branch Scope:
Branch A

Result:
Branch A → Allowed
Branch B → Denied
```

Therefore:

```text
Permission ≠ Scope
```

Both must be satisfied.

---

# 13. Role Permission Model

The effective permission model is based on:

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
Operational Rules
```

The role provides the base permission set.

Employee-specific configuration may modify that effective permission set according to the permission model.

---

# 14. Effective Permission

The API evaluates effective permissions rather than blindly trusting a role name.

Conceptually:

```text
Effective Permission
=
Role Permissions
+
Employee Overrides
```

subject to:

* employee status;
* Business scope;
* Branch scope;
* subscription;
* operational restrictions.

The exact override semantics are defined by the system permission model.

---

# 15. Permission Override

Employee-specific overrides may provide or restrict permissions where the system permits such configuration.

Examples:

```text
Role:
Manager

Employee Override:
Cannot refund

Effective:
Refund denied
```

or:

```text
Role:
Cashier

Employee Override:
Can apply discount

Effective:
Discount allowed
```

An override must not allow an employee to exceed the authority of the actor configuring the override.

---

# 16. Manager Authority

Managers operate within their assigned authority.

A Manager may manage employees and permissions only when:

* the Manager has the required permission;
* the target employee is within the Manager's permitted scope;
* the Manager's authority permits granting or modifying the requested permission.

A Manager must not grant permissions that exceed the Manager's own authority.

---

# 17. Permission Delegation Boundary

When one employee modifies another employee's permissions, the server must evaluate:

```text
Actor Authority
      ↓
Target Employee Scope
      ↓
Requested Permission
      ↓
Allowed Delegation
```

The server must reject privilege escalation.

Example:

```text
Manager A
Allowed:
inventory.view
inventory.adjust

Manager A
must not grant:
payroll.manage

if Manager A does not possess authority to delegate payroll.manage.
```

---

# 18. Owner Authority

Owner is a Business-level management role.

Owner may manage Business operations according to:

* Owner permissions;
* Business scope;
* Branch scope;
* subscription limits;
* system restrictions.

Multiple Owners may exist when permitted by the applicable subscription/tariff.

Owner authority remains limited to the Business context.

---

# 19. Employee Status

Employee status is an authorization condition.

An inactive employee cannot perform new protected business operations.

Example:

```text
Employee
    ↓
ACTIVE
    ↓
Authorization continues

Employee
    ↓
INACTIVE
    ↓
New protected operation denied
```

Historical records remain attributed to the original employee.

---

# 20. Subscription Entitlement

Authorization must consider the current Business subscription state.

Relevant states include:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

The subscription state is not merely a UI condition.

It is a server-side authorization boundary.

---

# 21. Read-Only Subscription

When a Business becomes `READ_ONLY`:

Allowed operations may include:

* viewing existing data;
* permitted reports;
* permitted exports;
* viewing historical configuration.

Modifying operations must be blocked unless explicitly defined as allowed lifecycle operations.

Example:

```text
GET /orders
→ Allowed

POST /orders
→ Denied

PATCH /products/{id}
→ Denied
```

---

# 22. Deleted Business

A Business in `DELETED` state cannot accept normal operational API requests.

The API must not allow:

* new Orders;
* new Payments;
* new Inventory Transactions;
* new Employees;
* new configuration;
* new synchronization operations.

Deleted Business data cannot be resurrected through an API request.

---

# 23. Device Authorization

Some operations require a trusted device context.

The API may enforce device restrictions for:

* POS;
* offline authorization;
* synchronization;
* sensitive operational commands.

A Device UUID alone does not prove authorization.

The device must be associated with an appropriate trusted-device state.

---

# 24. Device Scope

Where device-specific restrictions apply, the API must verify:

```text
Device
   ↓
Business
   ↓
Branch
   ↓
Employee / Session
   ↓
Allowed Capability
```

A trusted device for Branch A must not automatically authorize Branch B.

---

# 25. Cash Session Authorization

Cash-related operations may require a valid Cash Session.

Examples:

* payment;
* cash correction;
* Cash Session close;
* handover;
* cash-related reporting.

The API must verify applicable:

* Business;
* Branch;
* Cash Register;
* Cash Session;
* Employee;
* Session state;
* permission.

---

# 26. Operational Context

Authorization may depend on the current operational context.

Examples:

```text
Payment
→ active Cash Session may be required

Cash Session Close
→ actor must belong to session

Inventory Adjustment
→ Branch scope required

Configuration Change
→ permission + configuration version

Offline Sync
→ trusted device + offline authorization
```

Authorization must therefore not be reduced to a static permission list.

---

# 27. Resource Authorization

Resource-level authorization verifies that the target resource belongs to the authorized scope.

Example:

```text
GET /orders/{order_id}
```

The API must verify:

```text
Order.Business = Current Business
Order.Branch ∈ Allowed Branches
```

If either condition fails, access is denied.

---

# 28. Resource Relationship Validation

Resources may inherit scope through relationships.

Example:

```text
Order Item
   ↓
Order
   ↓
Branch
   ↓
Business
```

Access to an Order Item must therefore inherit the authorized scope of its parent Order.

The client must not be able to bypass scope by directly addressing the child resource.

---

# 29. Cross-Business Protection

Cross-Business access is prohibited.

Example:

```text
Authenticated:
Business A

Requested:
Product belonging to Business B

Result:
Denied
```

This must be enforced even when:

* UUID is valid;
* resource exists;
* user has a matching permission name;
* client sends a different Business header;
* resource ID was obtained from another source.

---

# 30. Cross-Branch Protection

Cross-Branch access is similarly prohibited unless the actor has explicit multi-Branch authority.

Example:

```text
Employee:
Branch A only

Request:
GET /inventory?branch_id=Branch B

Result:
Denied
```

For all-Branch employees:

```text
Branch A → Allowed
Branch B → Allowed
Branch C → Allowed
```

provided the required permission also exists.

---

# 31. Business-Global Resources

Some resources are Business-global rather than Branch-specific.

Examples may include:

* global Product definition;
* global Recipe;
* global category;
* Business-level menu;
* Business-level configuration.

Branch access rules must not incorrectly restrict Business-global resources, but the actor must still have valid Business scope and required permission.

---

# 32. Branch-Scoped Resources

Branch-scoped resources include examples such as:

* Branch menu configuration;
* Branch price override;
* inventory;
* Cash Register;
* Cash Session;
* Branch expenses;
* Branch attendance;
* Branch operational data.

Branch scope must be explicitly enforced.

---

# 33. Mixed-Scope Resources

Some resources contain both Business and Branch context.

Example:

```text
Product
Business = A

Branch Price Override
Business = A
Branch = B
```

The API must validate both:

```text
Business authorization
+
Branch authorization
```

A valid Business relationship does not automatically authorize the Branch-specific operation.

---

# 34. Permission Naming

Permissions should use stable machine-readable identifiers.

Examples:

```text
orders.view
orders.create
orders.modify
orders.accept
orders.cancel
orders.refund

payments.create
payments.refund

inventory.view
inventory.adjust
inventory.receive

menu.view
menu.manage
pricing.manage

employees.view
employees.manage
permissions.manage

payroll.view
payroll.manage
```

Permission names are API/domain identifiers and must not depend on translated UI labels.

---

# 35. Permission Categories

Permissions should be grouped logically.

Example categories:

```text
Business
Branch
Employees
Permissions
Products
Recipes
Menu
Pricing
Orders
Payments
Inventory
Cash
Attendance
Payroll
Reports
Notifications
Configuration
Audit
Synchronization
Files
```

The exact permission catalog is maintained separately from API routing.

---

# 36. Read Authorization

Read operations require authorization as well.

Examples:

```text
GET /employees
GET /inventory
GET /orders
GET /reports
GET /audit
```

The API must not assume that read access is harmless.

Sensitive data must be returned only within authorized scope.

---

# 37. Write Authorization

Write operations require:

```text
Permission
+
Scope
+
Resource State
+
Subscription
+
Operational Context
```

Examples:

```text
Product Price Change
→ pricing.manage
→ Business scope
→ Branch scope if Branch override
→ active subscription
→ valid configuration version
```

---

# 38. Business Command Authorization

Explicit commands must have dedicated authorization rules.

Examples:

```text
POST /orders/{id}/accept
POST /orders/{id}/pay
POST /orders/{id}/refund
POST /cash-sessions/{id}/close
POST /recipes/{id}/approve
```

The command must not inherit authorization merely from generic resource write permission.

---

# 39. Command-Specific Permissions

Examples:

```text
orders.accept
orders.refund
cash.close
recipes.approve
inventory.adjust
pricing.manage
permissions.manage
```

A user may have permission to view a resource without having permission to execute sensitive commands against it.

---

# 40. State-Aware Authorization

Authorization may depend on resource state.

Example:

```text
Order:
OPEN

orders.modify
→ may be allowed
```

But:

```text
Order:
PAID

orders.modify
→ denied
```

This is a combination of:

* authorization;
* operational state;
* domain rule.

The API/Application layer must evaluate both.

---

# 41. Authorization vs Business Rules

Authorization answers:

> Is this actor allowed to attempt this operation?

Business rules answer:

> Is this operation valid for the current state?

Example:

```text
Cashier has:
orders.refund
```

but:

```text
Order already fully refunded
```

The request may still fail because of a business-state rule.

Authorization and domain validation must remain conceptually separate.

---

# 42. Authorization Decision Order

The recommended order is:

```text
1. Authenticate
2. Resolve Business
3. Resolve Branch
4. Resolve Employee status
5. Resolve subscription entitlement
6. Resolve device restrictions
7. Resolve effective permissions
8. Validate resource scope
9. Validate operational context
10. Execute application use case
11. Apply domain rules
```

The exact implementation may optimize safe checks, but security semantics must remain equivalent.

---

# 43. Fail-Closed Authorization

When authoritative authorization cannot be established, the API must deny protected operations.

Examples:

```text
Unknown permission
→ Deny

Unknown Business membership
→ Deny

Unknown Branch scope
→ Deny

Revocation state unavailable
→ Deny when required for security

Invalid subscription state
→ Deny modifying operation
```

Authorization must never fail open.

---

# 44. Authorization Cache

Effective permissions may be cached for performance.

A cache entry should identify enough context to prevent accidental reuse.

Example:

```text
permissions:
{employee_id}:
{business_id}:
{branch_id}:
{role_version}:
{permission_version}
```

The exact key structure is implementation-specific.

---

# 45. Authorization Cache Invalidation

Permission cache must be invalidated when relevant authorization state changes.

Examples:

* role permission change;
* employee override change;
* employee deactivation;
* Branch scope change;
* employee transfer;
* subscription entitlement change;
* trusted device revocation where applicable.

Stale authorization must not remain valid indefinitely.

---

# 46. Cache Failure

If the authorization cache is unavailable:

```text
Authorization Cache
       ↓
Unavailable
       ↓
Authoritative Validation
       ↓
Allow / Deny
```

The system must not interpret cache failure as permission granted.

---

# 47. Authorization Cache Lifetime

Authorization cache entries must have bounded lifetime.

TTL alone is not sufficient for high-risk revocation scenarios.

Explicit invalidation should be preferred when an authorization change occurs.

---

# 48. Permission Versioning

Permission-related data should support versioning.

Example:

```text
Role Version
Permission Version
Employee Override Version
Scope Version
```

A permission cache may use these versions to detect stale authorization data.

---

# 49. Branch Scope Versioning

Branch assignment changes should invalidate relevant authorization context.

Example:

```text
Employee:
Branch A + Branch B

Changed to:
Branch A only
```

Requests to Branch B must immediately follow the new authoritative scope subject to the defined security propagation model.

---

# 50. Employee Transfer

When an employee is transferred between Branches:

```text
Old Branch Scope
      ↓
Revoked / Changed
      ↓
New Branch Scope
```

The API must not continue granting old Branch access because of stale permission data.

Historical operations remain associated with the original Branch and actor context.

---

# 51. Employee Deactivation

Deactivation must invalidate or otherwise safely terminate the employee's ability to perform new protected operations.

This includes:

* normal API operations;
* sensitive commands;
* permission management;
* synchronization where applicable;
* device/session operations where applicable.

Historical attribution remains intact.

---

# 52. Permission Management Authorization

Permission management is itself a protected operation.

Before modifying another employee's permissions, the API must verify:

```text
Actor
   ↓
Can manage permissions?
   ↓
Target employee within scope?
   ↓
Requested permission delegable?
   ↓
Subscription/limits satisfied?
```

Failure at any required step denies the operation.

---

# 53. Target Employee Scope

An employee may modify another employee's permissions only when the target employee is within the actor's management scope.

Example:

```text
Manager:
Branch A

Target:
Employee Branch A
→ Potentially allowed

Target:
Employee Branch B
→ Denied
```

All-Branch authority may allow broader management according to permission rules.

---

# 54. Subscription Limits and Authorization

Tariff limits may affect authorization.

Examples:

* maximum Owners;
* maximum Employees;
* maximum Branches;
* enabled features.

If a subscription does not permit a requested resource or feature, the operation must be rejected.

The API must not rely on the frontend to hide unavailable functionality.

---

# 55. Feature Entitlement

Feature availability is separate from permission.

Example:

```text
Employee has:
reports.export

Business subscription:
does not include advanced export

Result:
Denied
```

Therefore:

```text
Permission + Entitlement
```

are both required where applicable.

---

# 56. Authorization for Reports

Reports require scope-aware authorization.

The API must evaluate:

* report permission;
* Business scope;
* Branch scope;
* requested period;
* sensitive data restrictions;
* subscription entitlement;
* report availability.

An employee authorized for Branch A must not export Branch B data.

---

# 57. Authorization for Audit Data

Audit records may contain sensitive operational information.

Access requires explicit permission where defined.

Example:

```text
audit.view
```

Audit access must respect:

* Business scope;
* Branch scope where applicable;
* employee authority;
* subscription/read-only state.

---

# 58. Authorization for Files

File access must be authorized through the owning resource.

Example:

```text
File
 ↓
Product
 ↓
Business
```

or:

```text
File
 ↓
Report
 ↓
Business / Branch
```

Possessing a file UUID must not grant access.

---

# 59. Authorization for Notifications

Notifications must be scoped to their intended recipient and Business context.

An employee must not retrieve another employee's private notifications merely by changing a notification UUID.

---

# 60. Authorization for Synchronization

Synchronization is a privileged operational API.

The server must validate:

* authenticated/trusted device context;
* Employee status;
* Business;
* Branch;
* offline authorization;
* operation capability;
* subscription state;
* operation type;
* resource scope;
* operation UUID;
* synchronization rules.

Offline synchronization must not bypass normal authorization.

---

# 61. Synchronization Scope

A synchronization operation claiming:

```text
Branch A
```

must not create or modify:

```text
Branch B
```

resources.

The server must derive or validate resource scope from authoritative state.

Client payload scope is not sufficient.

---

# 62. Synchronization and Employee Status

If an employee becomes inactive while offline, previously authorized offline operations may still reach the server later.

The server must apply the defined synchronization policy.

New unauthorized operations must not be accepted merely because the device retained an old local permission state.

Historical already-accepted operations must remain attributable to their original actor.

---

# 63. Background Job Authorization

Background jobs do not use normal user authorization headers.

Instead, a job receives an explicit authorized context.

Example:

```text
Job
 ├── Business
 ├── Branch where applicable
 ├── Job Type
 ├── Trigger
 └── Allowed Operation
```

The worker must operate only within the context assigned to the job.

---

# 64. Background Scope Isolation

A background worker processing:

```text
Business A
```

must not accidentally query or modify:

```text
Business B
```

Every Business-scoped background operation must preserve the same isolation principles as synchronous API requests.

---

# 65. External Integration Authorization

External integrations must use dedicated integration credentials or service identity.

An integration must not impersonate an employee by submitting:

```text
employee_id
```

alone.

Integration authorization must define:

* Business scope;
* allowed resources;
* allowed operations;
* credential state;
* rate limits;
* expiration/revocation.

---

# 66. Bulk Operation Authorization

Bulk operations require authorization for the entire requested operation.

Example:

```text
POST /employees/bulk-update
```

The server must verify:

* actor permission;
* target employee scope;
* Business scope;
* Branch scope;
* subscription constraints;
* item-level validity.

A bulk request must not use one authorized item to bypass restrictions on another item.

---

# 67. Partial Bulk Authorization

If a bulk operation supports partial processing, every item must receive an independent authorization and validation result where necessary.

Example:

```text
Employee A → ALLOWED
Employee B → DENIED
Employee C → ALLOWED
```

The API must not silently apply unauthorized items.

---

# 68. API Filters and Authorization

Authorization must be applied before or as part of resource selection.

The system must not:

```text
Query all Businesses
↓
Filter unauthorized data in application memory
```

where this creates unacceptable data exposure or performance risk.

Queries should include appropriate Business/Branch scope predicates.

---

# 69. Authorization-Aware Queries

Repository/application queries should receive authorized scope explicitly.

Conceptually:

```text
Repository Query
+
Business Scope
+
Branch Scope
+
Resource Constraints
```

The repository must not depend solely on the caller remembering to add a scope filter.

---

# 70. Scope Enforcement at Multiple Layers

Critical isolation should be reinforced across layers where practical.

```text
API
 ↓
Application
 ↓
Repository
 ↓
Database Constraints
```

The layers have different responsibilities.

API validates request context.

Application enforces use-case authorization.

Repository applies scope-aware data access.

Database constraints protect structural integrity.

---

# 71. Defense in Depth

Business/Branch isolation must not rely on one control only.

The architecture should use:

* authenticated identity;
* authorization;
* scope validation;
* repository filtering;
* database constraints;
* tests;
* audit;
* observability.

No single layer should be treated as the entire security boundary.

---

# 72. Authorization and Database Constraints

Database constraints cannot replace API authorization.

For example:

```text
Foreign Key
```

can ensure a resource exists within a relationship but does not determine whether the current employee may access it.

Authorization remains an application responsibility.

---

# 73. Authorization and UI

Frontend permission checks improve usability but are not security controls.

The frontend may hide:

```text
Refund
```

when the user lacks:

```text
orders.refund
```

However, the backend must still reject:

```text
POST /orders/{id}/refund
```

when unauthorized.

---

# 74. Authorization and Direct API Access

Users may interact with the API through:

* browser;
* POS client;
* synchronization client;
* scripts;
* future mobile applications;
* future integrations.

Every protected API path must enforce authorization independently of client type.

---

# 75. Authorization and API Versioning

Authorization behavior is part of the API contract.

A version change must not silently weaken:

* Business isolation;
* Branch isolation;
* permission enforcement;
* subscription enforcement;
* resource authorization.

If an authorization behavior must change incompatibly, the change must be explicitly versioned and documented.

---

# 76. Authorization Error Contract

Authorization failures should use stable error codes.

Examples:

```text
AUTHENTICATION_REQUIRED
ACCESS_DENIED
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
RESOURCE_SCOPE_DENIED
PERMISSION_REQUIRED
SUBSCRIPTION_READ_ONLY
FEATURE_NOT_ENTITLED
EMPLOYEE_INACTIVE
DEVICE_NOT_TRUSTED
CASH_SESSION_REQUIRED
```

The exact error should reveal only information appropriate to the security policy.

---

# 77. HTTP Authorization Mapping

Initial mapping:

| Condition                                  |                              HTTP |
| ------------------------------------------ | --------------------------------: |
| Authentication missing/invalid             |                               401 |
| Authenticated but unauthorized             |                               403 |
| Resource intentionally hidden              |                               404 |
| Subscription blocks mutation               |                               403 |
| Stale authorization-sensitive state        | 409 or 403 according to operation |
| Invalid business rule after authorization  |                               422 |
| Temporary authorization dependency failure |             503 where appropriate |

The API must use consistent semantics.

---

# 78. 404 vs 403

The API may return `404` instead of `403` when revealing the existence of a resource would create information leakage.

Example:

```text
Order exists in another Business
```

The API may respond:

```text
404 RESOURCE_NOT_FOUND
```

instead of revealing that the resource exists.

This behavior must be applied consistently.

---

# 79. Authorization Audit

Important authorization-related events should be auditable.

Examples:

* permission changes;
* Branch scope changes;
* employee deactivation;
* trusted-device revocation;
* subscription entitlement changes;
* privileged access;
* permission delegation;
* authorization configuration changes.

Routine successful authorization checks do not require individual immutable business audit records unless explicitly required.

---

# 80. Authorization Logging

Operational logs may record:

```text
request_id
operation_id
employee_id
business_id
branch_id
permission
resource_type
result
reason_code
```

Logs must not expose:

* access tokens;
* refresh tokens;
* credentials;
* private keys;
* unnecessary sensitive resource contents.

---

# 81. Authorization Observability

Metrics should include:

```text
authorization_allow_count
authorization_denied_count
permission_denied_count
business_scope_denied_count
branch_scope_denied_count
subscription_denied_count
device_denied_count
authorization_cache_hit_count
authorization_cache_miss_count
```

Metrics must use controlled labels.

Raw Employee UUIDs, Business UUIDs or Branch UUIDs must not become uncontrolled metric dimensions.

---

# 82. Authorization Anomaly Detection

Repeated authorization failures may indicate:

* misconfiguration;
* stale client context;
* integration errors;
* attempted unauthorized access;
* compromised credentials.

The monitoring system may generate security alerts for unusual patterns.

Alerting must remain asynchronous and must not block normal authorization decisions.

---

# 83. Authorization Performance

Authorization must remain fast enough for POS operations.

Initial targets:

| Operation                            |                 Target |
| ------------------------------------ | ---------------------: |
| Authorization overhead p95           |               ≤ 100 ms |
| Cached authorization lookup p95      |                ≤ 20 ms |
| Business/Branch scope validation p95 |                ≤ 50 ms |
| Permission resolution p95            |                ≤ 50 ms |
| Authorization-related DB query p95   | ≤ 100 ms where indexed |

These are initial architectural targets and must be validated through production-like load testing.

---

# 84. POS Authorization Performance

POS authorization should avoid unnecessary repeated work.

Where safe, the system may reuse:

* authenticated session;
* trusted device context;
* active Branch context;
* effective permission context.

However, revocation-sensitive state must still be enforced according to the security model.

Security cannot be disabled merely for POS performance.

---

# 85. Authorization and Caching

Authorization caching must follow the caching architecture defined in:

`14_Backend_Caching_and_Performance_Architecture.md`

Important rules:

* cache is derived state;
* PostgreSQL remains authoritative;
* revocation invalidates relevant cache;
* cache failure does not grant access;
* Business/Branch scope remains explicit;
* cache entries have bounded lifetime.

---

# 86. Authorization and Concurrency

Authorization state may change concurrently with an API request.

Example:

```text
Request starts
    ↓
Employee has permission
    ↓
Permission revoked
    ↓
Request continues
```

The system must define transaction boundaries for security-sensitive operations.

For critical mutations, authoritative authorization must be evaluated sufficiently close to the protected operation to prevent unsafe stale decisions.

---

# 87. Permission Change Concurrency

When two administrators modify permissions concurrently:

* configuration versions must be validated;
* stale updates must be rejected;
* newer permission state must not be silently overwritten.

Example:

```text
Version 12
    ↓
Admin A updates → Version 13

Admin B submits Version 12
    ↓
409 STALE_VERSION
```

---

# 88. Branch Scope Change Concurrency

Branch assignment changes must use authoritative state.

A stale client must not restore an old Branch assignment by submitting outdated configuration.

Optimistic concurrency should be used where required.

---

# 89. Privilege Escalation Protection

The API must prevent privilege escalation through:

* role changes;
* permission overrides;
* Branch scope changes;
* Owner creation;
* Manager creation;
* employee updates;
* subscription configuration;
* device assignment.

Any operation capable of increasing authority must itself require sufficient authority.

---

# 90. Owner Creation

Creating an additional Owner is a privileged Business operation.

The API must validate:

* actor authority;
* target employee state;
* Business scope;
* Owner limit;
* subscription entitlement;
* permission configuration.

The frontend must not be able to bypass the Owner limit.

---

# 91. Manager Creation

Manager creation or role assignment must validate:

* actor permission;
* target employee scope;
* Business scope;
* subscription employee limits;
* permitted role assignment.

A Manager must not be created with authority exceeding the assigning actor's authority.

---

# 92. Permission Assignment Constraints

When assigning permissions:

```text
Requested Permission
        ↓
Supported Permission?
        ↓
Actor Can Grant?
        ↓
Target Within Scope?
        ↓
Subscription Allows Feature?
        ↓
Apply
```

Unsupported or unauthorized permission identifiers must be rejected.

---

# 93. API Authorization for Configuration

Configuration operations require both:

```text
Configuration Permission
+
Correct Configuration Scope
```

Examples:

```text
Global Price Change
→ Business scope + pricing.manage

Branch Price Override
→ Business scope + Branch scope + pricing.manage

Branch Menu Availability
→ Business scope + Branch scope + menu.manage
```

---

# 94. API Authorization for Inventory

Inventory operations require:

* inventory permission;
* Business scope;
* Branch scope;
* active employee;
* valid inventory context;
* subscription entitlement where applicable.

The API must not authorize inventory changes solely because a Product UUID is valid.

---

# 95. API Authorization for Financial Operations

Financial operations require stronger authorization controls.

Examples:

* payment;
* refund;
* cash correction;
* Cash Session close;
* cash handover;
* financial adjustment.

The API must validate:

```text
Actor
+
Permission
+
Business
+
Branch
+
Cash Session where applicable
+
Order/transaction scope
+
Current state
```

---

# 96. API Authorization for Payroll

Payroll access is sensitive.

The API must distinguish between:

* viewing payroll;
* creating payroll data;
* modifying payroll;
* approving payroll where applicable;
* exporting payroll.

Payroll access must respect Business/Branch scope and permission requirements.

---

# 97. API Authorization for Attendance

Attendance data is employee-related and must be scope-controlled.

An employee with attendance permission for Branch A must not automatically access Branch B attendance.

Managers may only manage employees within their permitted authority.

---

# 98. API Authorization for Reports and Exports

Export authorization must be at least as restrictive as the underlying data access.

A user who cannot view Branch B data must not obtain Branch B data through an XLSX export endpoint.

Export operations must re-evaluate:

* Business scope;
* Branch scope;
* permission;
* subscription;
* requested report definition.

---

# 99. API Authorization for Search

Search endpoints must enforce the same scope restrictions as direct resource access.

Example:

```text
GET /products?search=burger
```

must not return Products from another Business.

Similarly:

```text
GET /orders?search=...
```

must not reveal unauthorized Orders.

---

# 100. API Authorization for Aggregations

Dashboard and aggregate endpoints must enforce scope before aggregation.

The system must not:

```text
Aggregate all Business data
↓
Filter result afterward
```

when this risks exposing unauthorized aggregate information.

Scope should be applied to the underlying data query.

---

# 101. Authorization for Cross-Branch Reports

An employee with multiple Branch access may request aggregated data across allowed Branches.

Example:

```text
Allowed:
Branch A
Branch B

Report:
A + B

Result:
Allowed
```

If the request includes Branch C:

```text
A + B + C
```

the API must either:

* reject the request;
* or explicitly process only authorized Branches if the endpoint contract permits partial scope.

Silent scope expansion is prohibited.

---

# 102. Authorization for All-Branch Access

All-Branch access is a defined scope, not an implicit property of seniority.

An employee may have all-Branch authority only when explicitly granted.

The API must not infer:

```text
Owner → all Branches
Manager → all Branches
```

without the configured scope.

---

# 103. Branch Context Switching

When a user changes Branch context:

```text
Old Branch Context
       ↓
New Branch Context
       ↓
Recalculate Authorization
```

The previous Branch authorization must not automatically carry over.

The API must validate the new Branch independently.

---

# 104. Request Context Immutability

Once the server has established authoritative:

* Employee;
* Business;
* Branch;
* Device;
* Cash Session;

the request context must not be changed by downstream client input.

Application use cases may derive additional context, but must not replace authenticated identity.

---

# 105. Scope Propagation

Authorization context must propagate to:

* Application use case;
* Domain operation where relevant;
* Repository;
* audit;
* outbox;
* background job;
* synchronization;
* report generation.

Only necessary fields should be propagated.

---

# 106. Repository Scope Contract

Repositories handling Business-scoped resources should require explicit scope context where appropriate.

Conceptually:

```text
repository.get_order(
    business_id,
    order_id
)
```

is safer than:

```text
repository.get_order(order_id)
```

when the latter could accidentally permit cross-Business access.

The exact interface may vary by implementation.

---

# 107. Authorization and Soft Deletion

Archived or soft-deleted resources may remain historically accessible according to their resource policy.

Authorization must distinguish:

```text
Active
Archived
Deleted
```

A user must not regain modification rights merely because an archived resource remains readable.

---

# 108. Authorization and Historical Data

Historical data may be immutable but is still access-controlled.

For example:

```text
Historical Order
```

may be readable to an authorized employee but not to an employee outside the Business/Branch scope.

Immutability does not remove authorization requirements.

---

# 109. Authorization and Audit History

Audit records are historical and immutable.

However, access to audit history must still be permission-controlled.

A user must not access another Business's audit trail merely because the record is immutable.

---

# 110. Authorization and Read-Only Mode

Read-only subscription mode changes mutation authorization but does not automatically remove all read permissions.

Example:

```text
READ_ONLY
+
orders.view
→ Allowed

READ_ONLY
+
orders.create
→ Denied
```

The API must apply both subscription state and permission.

---

# 111. Authorization and Deletion Lifecycle

When a Business enters:

```text
DELETION_ELIGIBLE
```

or:

```text
DELETING
```

normal operational access must be restricted according to lifecycle policy.

Once:

```text
DELETED
```

normal Business authorization must fail.

The lifecycle system remains authoritative.

---

# 112. Authorization Recovery

Authorization failures caused by temporary infrastructure problems must not result in fail-open behavior.

If authorization dependencies become unavailable:

```text
Protected operation
      ↓
Cannot establish authority
      ↓
Deny / controlled unavailable response
```

The API may return `503` when the failure is infrastructure-related rather than a true permission denial.

---

# 113. Authorization and Transactions

For sensitive mutations, authorization and the protected operation must be coordinated with the application transaction boundary.

Example:

```text
Authorize
   ↓
Validate state
   ↓
Begin transaction
   ↓
Perform protected mutation
   ↓
Audit / Outbox
   ↓
Commit
```

The implementation must prevent authorization checks from becoming detached from critical state validation.

---

# 114. Authorization and Idempotency

Idempotency does not bypass authorization.

For a repeated request:

```text
Same Idempotency-Key
```

the server must still apply the correct authentication and authorization policy.

An idempotency record must not become a mechanism for unauthorized replay.

---

# 115. Authorization and Retry

A client may retry an authorized command.

The server must ensure:

* authorization;
* scope;
* idempotency;
* current state.

A retry must not create a new business effect merely because the first response was lost.

---

# 116. Authorization and Rate Limiting

Rate limiting is an additional protection layer.

It must not replace authorization.

Example:

```text
Rate limit passes
≠
Permission granted
```

The request still requires complete authorization.

---

# 117. Authorization and API Gateways

An API gateway or reverse proxy may perform coarse controls such as:

* IP filtering;
* authentication token forwarding;
* rate limiting;
* request size limits.

Fine-grained Business/Branch/resource authorization remains an application responsibility.

---

# 118. Authorization and Service Boundaries

The initial architecture is a modular monolith.

Authorization should therefore use a shared application security model rather than duplicated independent authorization implementations.

Future service extraction must preserve the same authorization semantics.

---

# 119. Authorization Policy Centralization

Authorization rules should be centralized enough to prevent inconsistent endpoint behavior.

Examples:

```text
can_view_order()
can_modify_order()
can_refund_order()
can_manage_inventory()
can_manage_permissions()
can_manage_pricing()
```

The exact implementation may use policy objects, services or application authorization components.

The API routes should not independently implement authorization logic.

---

# 120. Authorization Policy Reuse

The same authorization policy should be reusable by:

* REST endpoints;
* synchronization;
* background operations where applicable;
* report generation;
* exports;
* future integrations.

This reduces the risk that one access path bypasses another.

---

# 121. Authorization Testing

Authorization must be tested across:

* Business isolation;
* Branch isolation;
* permissions;
* overrides;
* Manager authority;
* Owner authority;
* Super Admin scope;
* employee deactivation;
* subscription expiry;
* device restrictions;
* Cash Session context;
* resource ownership;
* bulk operations;
* synchronization;
* exports;
* search;
* reports.

---

# 122. Negative Authorization Testing

Security tests must explicitly verify denied cases.

Examples:

```text
Business A → Business B resource
Branch A → Branch B resource
Cashier → Owner-only operation
Manager → unauthorized permission
Inactive Employee → protected operation
Read-only Business → mutation
Untrusted Device → restricted operation
Expired offline authorization → sync
```

All must fail according to the defined contract.

---

# 123. Privilege Escalation Testing

Tests must attempt:

* assigning higher role;
* granting forbidden permission;
* expanding Branch scope;
* changing Owner status;
* bypassing subscription limits;
* changing Business UUID;
* changing Branch UUID;
* changing Employee UUID;
* reusing privileged operation IDs.

No client-side modification must grant additional authority.

---

# 124. Cross-Tenant Testing

Automated tests must verify that:

```text
Business A
```

cannot access:

```text
Business B
```

through:

* direct resource ID;
* list endpoint;
* search;
* filter;
* report;
* export;
* synchronization;
* file;
* notification;
* audit;
* configuration;
* background job.

Business isolation is a release-blocking security requirement.

---

# 125. Cross-Branch Testing

Tests must verify that:

```text
Branch A
```

cannot access:

```text
Branch B
```

when the actor lacks Branch B scope.

This must be tested through both direct resource and aggregate endpoints.

---

# 126. Authorization Performance Testing

Load tests must measure:

* permission lookup;
* scope validation;
* authorization cache;
* concurrent authorization;
* permission changes under load;
* Branch switching;
* POS authorization.

The target is to preserve POS responsiveness while maintaining security.

---

# 127. Authorization Failure Monitoring

Important authorization failures should be observable without logging secrets.

The system should distinguish:

```text
Invalid Authentication
Permission Denied
Business Scope Denied
Branch Scope Denied
Subscription Denied
Device Denied
Resource Scope Denied
Infrastructure Failure
```

This supports both security monitoring and operational debugging.

---

# 128. Authorization Documentation

Every protected endpoint must document:

* required permission;
* Business scope;
* Branch scope;
* resource scope;
* subscription restrictions;
* device requirements;
* Cash Session requirements;
* possible authorization errors.

The contract must remain consistent with the actual implementation.

---

# 129. Authorization Change Management

Changes to authorization behavior require review of:

1. Permission catalog;
2. Role behavior;
3. Employee overrides;
4. Business scope;
5. Branch scope;
6. Subscription entitlement;
7. Device trust;
8. API contracts;
9. Frontend behavior;
10. synchronization;
11. audit;
12. security tests.

Authorization changes are security-sensitive changes.

---

# 130. Authorization Guardrails

The implementation must prohibit:

* frontend-only authorization;
* trusting client Business UUID;
* trusting client Branch UUID;
* trusting client Employee UUID;
* trusting client Device UUID;
* permission checks based only on role name;
* cross-Business resource access;
* cross-Branch access without scope;
* Manager privilege escalation;
* stale permission cache granting indefinite access;
* cache failure causing fail-open authorization;
* subscription restrictions enforced only in UI;
* synchronization bypassing authorization;
* exports bypassing data authorization;
* search bypassing scope;
* reports bypassing scope;
* background jobs operating without explicit scope;
* external integrations impersonating employees through UUIDs;
* authorization logic duplicated inconsistently across routes.

---

# 131. System Invariants

The following invariants apply to API Authorization and Scope Enforcement:

1. Authorization is enforced server-side.
2. Authentication and authorization remain separate concerns.
3. A valid authentication state does not imply permission for every operation.
4. A permission does not automatically imply access to every Business.
5. A permission does not automatically imply access to every Branch.
6. Business scope is mandatory for Business-scoped resources.
7. Branch scope is mandatory for Branch-scoped resources.
8. Resource scope must be validated against the authorized context.
9. Client-provided Business UUID is never authoritative.
10. Client-provided Branch UUID is never authoritative.
11. Client-provided Employee UUID is never sufficient authorization.
12. Client-provided Device UUID is never sufficient authorization.
13. Client-provided Role UUID is never sufficient authorization.
14. Client-provided Permission UUID is never sufficient authorization.
15. Cross-Business access is prohibited unless an explicit platform-level capability permits it.
16. Cross-Branch access requires explicit Branch scope.
17. Business-global resources still require Business authorization.
18. Branch-specific resources require Branch authorization.
19. Mixed-scope resources require all applicable scopes.
20. Effective permissions include applicable Role Permissions.
21. Employee Overrides are evaluated according to the permission model.
22. Permission delegation cannot exceed the actor's authority.
23. Managers cannot grant permissions beyond their authority.
24. Owner authority remains Business-scoped.
25. Super Admin platform authority does not automatically imply Business operational authority.
26. Inactive employees cannot perform new protected operations.
27. Historical records remain attributed to inactive employees.
28. READ_ONLY subscription blocks modifying operations where defined.
29. READ_ONLY subscription does not automatically remove permitted read access.
30. DELETED Business cannot perform normal operational API operations.
31. Subscription entitlement is a server-side authorization boundary.
32. Feature entitlement is separate from employee permission.
33. Trusted-device restrictions are server-enforced.
34. A trusted device for one Branch does not automatically authorize another Branch.
35. Cash Session requirements are enforced server-side.
36. Operational context may be required in addition to permission.
37. Read operations are authorization-controlled.
38. Write operations are authorization-controlled.
39. Business commands have explicit authorization requirements.
40. Resource state may affect whether an authorized command is valid.
41. Authorization and domain business rules remain separate concerns.
42. Authorization must fail closed when authority cannot be established.
43. Authorization cache failure must never grant access.
44. Authorization cache entries have bounded lifetime.
45. Permission changes invalidate or safely supersede stale authorization state.
46. Employee deactivation invalidates or safely supersedes stale authorization state.
47. Branch scope changes invalidate or safely supersede stale authorization state.
48. Subscription changes invalidate or safely supersede relevant authorization state.
49. Permission cache keys preserve identity and scope isolation.
50. Authorization cache is not authoritative.
51. PostgreSQL remains authoritative for persistent authorization state.
52. Permission changes use concurrency protection where required.
53. Stale permission updates are rejected.
54. Privilege escalation is prohibited.
55. Owner creation is subject to authority and subscription limits.
56. Manager creation is subject to authority and subscription limits.
57. Permission assignment is subject to actor authority.
58. Target employees must be within the actor's management scope.
59. Reports must enforce Business and Branch authorization.
60. Exports must not bypass authorization.
61. Search must not bypass authorization.
62. Aggregations must apply scope before calculating results.
63. Audit access is authorization-controlled.
64. File access is authorization-controlled.
65. Notification access is recipient/scope controlled.
66. Synchronization cannot bypass authorization.
67. Synchronization operations are validated against Business and Branch scope.
68. Offline authorization cannot permanently grant server-side authority.
69. Background jobs receive explicit authorization context.
70. Background jobs cannot operate across Business boundaries unintentionally.
71. External integrations use dedicated authorization context.
72. External integrations cannot impersonate employees using UUIDs alone.
73. Bulk operations must authorize every affected resource where required.
74. Partial bulk processing must not silently apply unauthorized items.
75. Repository queries must preserve Business and Branch scope.
76. Scope enforcement should exist at multiple architectural layers.
77. Database constraints do not replace authorization.
78. Frontend authorization does not replace backend authorization.
79. Direct API access must enforce the same authorization rules as browser access.
80. Authorization behavior is part of the public API contract.
81. Authorization changes must preserve Business isolation.
82. Authorization changes must preserve Branch isolation.
83. Historical data remains access-controlled.
84. Historical immutability does not remove authorization requirements.
85. Idempotency does not bypass authorization.
86. Retries do not bypass authorization.
87. Rate limiting does not replace authorization.
88. API gateways do not replace application authorization.
89. Authorization policies should be centrally reusable.
90. Authorization logic must not be independently duplicated across routes.
91. Authorization failures must be observable.
92. Authorization metrics must avoid uncontrolled high-cardinality labels.
93. Sensitive authorization logs must not contain credentials or tokens.
94. Security-sensitive authorization changes require dedicated testing.
95. Cross-Business isolation is a release-blocking security requirement.
96. Cross-Branch isolation is a release-blocking security requirement.
97. Privilege escalation is a release-blocking security requirement.
98. Authorization performance must remain within defined SLO targets.
99. Authorization optimization must not weaken security.
100. Authorization must remain compatible with offline synchronization.
101. Authorization must remain compatible with background processing.
102. Authorization must remain compatible with future horizontal scaling.
103. Authorization semantics must remain consistent across API versions.
104. Authorization errors use stable machine-readable codes.
105. Authorization behavior must be documented for every protected endpoint.
106. Server-side authorization remains authoritative regardless of client type.
107. Scope must be derived or verified from authoritative server state.
108. The API must never treat client-controlled scope as trusted authority.

---

# 132. Recommended Authorization Structure

The backend may organize authorization components approximately as:

```text
app/
├── security/
│   ├── authentication/
│   ├── authorization/
│   │   ├── policies/
│   │   ├── permissions/
│   │   ├── scopes/
│   │   ├── resources/
│   │   ├── entitlement.py
│   │   ├── decisions.py
│   │   └── context.py
│   └── device_trust/
│
├── application/
│   └── ...
│
├── api/
│   └── ...
│
└── infrastructure/
    └── cache/
```

Exact module names may be refined during implementation.

---

# 133. Authorization Decision Result

Authorization components should return a structured decision rather than only a Boolean where practical.

Conceptually:

```text
AuthorizationDecision
├── allowed
├── reason_code
├── permission
├── business_scope
├── branch_scope
└── resource_scope
```

Sensitive internal details must not be exposed directly to API clients.

---

# 134. Authorization Policy Example

Conceptually:

```text
can_refund_order(actor, order)
```

may evaluate:

```text
Actor authenticated
        ↓
Employee active
        ↓
Business matches
        ↓
Branch allowed
        ↓
orders.refund granted
        ↓
Subscription permits operation
        ↓
Order state permits refund attempt
        ↓
ALLOW
```

The actual refund business rules remain in the Application/Domain layers.

---

# 135. Recommended Authorization Evaluation Boundary

The preferred architecture is:

```text
API
 ↓
Request Context
 ↓
Authorization Policy
 ↓
Application Use Case
 ↓
Domain Rules
 ↓
Repository
```

The API should not contain complex permission logic.

The Domain should not become responsible for HTTP authorization.

The Application layer coordinates authorization with the use case.

---

# 136. Relationship with Previous API Documents

This document depends on:

* `01_API_Architecture_Overview.md`
* `02_API_Design_Principles_and_Standards.md`
* `03_API_Layers_and_Request_Lifecycle.md`
* `04_API_Versioning_and_Backward_Compatibility.md`
* `05_API_Resource_Model_and_Naming.md`
* `06_API_Authentication_and_Request_Context.md`

It specifically extends the request context established by Document 06.

Authentication establishes the actor.

This document determines what that actor may do and within which scope.

---

# 137. Related Backend Architecture

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/17_Backend_Testing_and_Quality_Assurance_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`

---

# 138. Related Database Architecture

* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

---

# 139. Related Frontend Architecture

* `docs/04_Architecture/07_Frontend/05_Authentication_and_Session_UI.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/20_Offline_Mode_and_Synchronization_UI.md`
* `docs/04_Architecture/07_Frontend/28_Frontend_Security_and_Client_Side_Protection_Architecture.md`

Frontend authorization improves UX but never replaces this API authorization model.

---

# 140. Related API Documents

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/04_Architecture/09_API/05_API_Resource_Model_and_Naming.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/08_API_Request_Validation_and_Response_Contracts.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/21_API_Security_CORS_CSRF_and_Data_Protection.md`

---

# 141. Status

**API Architecture Section:** In Progress

**Document Status:** Proposed

**Current Document:** `07_API_Authorization_and_Scope_Enforcement.md`

**Previous Document:** `06_API_Authentication_and_Request_Context.md`

**Next Document:** `08_API_Request_Validation_and_Response_Contracts.md`

---

## Final Principle

> Authentication establishes who the actor is. Authorization establishes what the actor may do. Scope enforcement establishes where the actor may do it. The server remains authoritative for all three.

