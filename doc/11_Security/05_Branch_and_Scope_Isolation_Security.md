# 05 — Branch and Scope Isolation Security

**Document ID:** SEC-05
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent:** `docs/11_Security/README.md`
**Previous:** `04_Business_and_Tenant_Isolation_Security.md`
**Next:** `06_Data_Security_and_Data_Classification.md`

---

## 1. Purpose

This document defines the security policy for branch-level isolation, employee scope, and authorization boundaries inside a FastFood ERP business.

The purpose is to ensure that:

* employees access only the branches they are authorized to access;
* branch-specific data is not exposed across unauthorized branches;
* employee permissions are limited by both role and scope;
* branch access cannot be used to bypass functional permissions;
* functional permissions cannot be used to bypass branch boundaries;
* Owner, Manager, and other employees operate within explicitly defined authorization boundaries;
* multi-branch operations remain isolated while allowing authorized cross-branch management;
* authorization decisions remain consistent across online, offline, reporting, background, and synchronization operations.

This document defines **security policy and boundaries**, not implementation details.

Implementation-specific authorization mechanisms belong to the Architecture, Backend, API, Deployment, and related technical documentation.

---

# 2. Scope

This document covers:

* branch access;
* employee branch scope;
* role scope;
* functional permissions;
* branch-specific permissions;
* cross-branch access;
* Owner and Manager boundaries;
* employee visibility;
* branch-scoped reports;
* branch-scoped inventory and operations;
* branch-scoped financial operations;
* branch-scoped configuration;
* branch-scoped devices and peripherals;
* authorization boundaries for background and offline operations;
* scope changes;
* temporary scope;
* authorization conflicts;
* authorization failures;
* security auditing and verification.

This document does not define:

* authentication mechanisms;
* tenant isolation;
* password policies;
* session implementation;
* database implementation;
* API middleware implementation;
* infrastructure security;
* network security;
* encryption algorithms.

Those concerns are defined by their respective security and technical documents.

---

# 3. Security Model

FastFood ERP uses multiple authorization dimensions.

A user's effective access is determined by the combination of:

1. **Identity**
2. **Business/Tenant**
3. **Branch Scope**
4. **Role**
5. **Functional Permission**
6. **Resource Ownership**
7. **Operational Context**

Authorization must not depend on only one of these dimensions.

A user who has permission to perform an action does not automatically have permission to perform that action in every branch.

Likewise, a user who belongs to a branch does not automatically receive every permission available within that branch.

The general security rule is:

> Access is allowed only when the identity, business, branch scope, role, permission, and resource context all satisfy the required authorization policy.

---

# 4. Branch Security Boundary

## 4.1 Branch as an Authorization Boundary

Each branch is an independent operational scope inside a business.

Branch isolation applies to:

* orders;
* cash registers;
* employees;
* attendance;
* inventory;
* warehouses;
* recipes where branch restrictions apply;
* menu availability;
* prices where branch overrides exist;
* expenses;
* refunds;
* reports;
* operational configuration;
* devices;
* printers;
* branch notifications;
* branch audit information.

Branch data must not become visible merely because a user belongs to the same business.

---

## 4.2 Default Branch Isolation

The default rule is:

> An employee may access only branches explicitly included in the employee's authorized scope.

If no branch is assigned, branch-scoped operational access must be denied.

The system must not assume that:

* being an employee means access to every branch;
* being a Manager means access to every branch;
* being assigned to one branch means access to neighboring branches;
* knowing another branch's identifier grants access;
* having a valid account grants unrestricted branch access.

---

# 5. Employee Scope

Employee scope defines the operational boundaries within which an employee may act.

An employee may have:

* one branch;
* multiple selected branches;
* all branches, when explicitly authorized by the business security model.

Branch scope must be explicit.

It must not be inferred from:

* current device;
* current IP address;
* previous login;
* employee title alone;
* branch name entered by the employee;
* resource identifiers.

---

# 6. Role and Scope Are Independent

Role and branch scope represent different security dimensions.

For example:

* a Cook may access kitchen operations in Branch A but not Branch B;
* a Manager may manage employees in Branch A but not Branch B;
* an employee with report permission may view reports only for assigned branches;
* an employee with inventory permission may manage inventory only within authorized branches.

Therefore:

> Role permission does not expand branch scope.

And:

> Branch scope does not expand functional permission.

Both conditions must be satisfied.

---

# 7. Effective Authorization

The effective authorization boundary is conceptually:

```text
Identity
   ↓
Business/Tenant
   ↓
Branch Scope
   ↓
Role
   ↓
Functional Permission
   ↓
Resource Scope
   ↓
Action
```

An authorization decision must fail if any required boundary fails.

For example:

```text
Employee
  ├── Business: Restaurant A
  ├── Branch Scope: Branch 1, Branch 3
  ├── Role: Manager
  └── Permission: Inventory Management

Allowed:
  Branch 1 → Inventory Management
  Branch 3 → Inventory Management

Denied:
  Branch 2 → Inventory Management
  Branch 1 → Payroll Management
```

---

# 8. Branch Access Modes

Branch scope may conceptually contain the following access modes.

## 8.1 Single-Branch Scope

The employee is authorized for one branch.

Example:

```text
Employee: Cashier
Branch Scope: Branch 2
```

The employee must not access Branch 1 or Branch 3.

---

## 8.2 Multi-Branch Scope

The employee is authorized for explicitly selected branches.

Example:

```text
Employee: Manager
Branch Scope:
  - Branch 1
  - Branch 3
```

Access to Branch 2 remains denied.

---

## 8.3 All-Branch Scope

Certain authorized users may operate across all branches.

This scope must be explicit.

It must not be inferred solely from job title.

All-branch access represents a higher authorization level and should therefore be subject to stronger governance and auditing.

---

# 9. Employee-to-Branch Assignment

Employee branch assignments define where the employee may operate.

Assignment changes must be controlled.

The security policy requires:

* authorized personnel may assign branches;
* unauthorized employees cannot grant themselves branch access;
* branch assignment changes are auditable;
* removal of a branch immediately affects future authorization decisions;
* changes must not silently expand unrelated permissions.

An employee's previous access must not survive indefinitely after branch scope removal.

---

# 10. Role Scope

A role defines what type of operations an employee may perform.

Examples include:

* Cashier;
* Cook;
* Waiter;
* Manager;
* Owner;
* Other configured roles.

Role scope must remain subordinate to business and branch boundaries.

For example:

```text
Manager
+
Branch 1
+
Employee Management Permission
```

does not imply:

```text
Manager
+
All Branches
+
Employee Management
```

unless all-branch scope was explicitly granted.

---

# 11. Functional Permission Boundary

Functional permissions define what an employee may do.

Examples include:

* create orders;
* process payments;
* perform refunds;
* manage inventory;
* manage recipes;
* view reports;
* manage employees;
* manage salaries;
* modify menu configuration.

A functional permission does not automatically grant access to every branch.

The permission must be evaluated together with branch scope.

---

# 12. Branch-Specific Permissions

The system supports branch-specific authorization.

For example:

```text
Employee:
  Branch 1 → Inventory: Allowed
  Branch 2 → Inventory: Denied
  Branch 3 → Inventory: Allowed
```

This allows the business to create different operational responsibilities without creating unnecessary separate employee identities.

Branch-specific permission differences must remain explicit and auditable.

---

# 13. Resource Scope

Authorization must also consider the scope of the requested resource.

Examples:

* a Branch 1 order belongs to Branch 1;
* a Branch 2 cash register belongs to Branch 2;
* a Branch 3 warehouse belongs to Branch 3;
* a branch-specific report belongs to its associated branch.

An employee must not gain access by manipulating a resource identifier.

For example:

```text
Authorized:
  Employee → Branch 1 → Order 123

Unauthorized:
  Employee → Branch 1 → Order 456
                         ↓
                       Branch 2
```

Knowing or guessing `Order 456` must not bypass branch authorization.

---

# 14. Read Authorization

Read access must respect branch scope.

This includes:

* order lists;
* order details;
* sales reports;
* inventory reports;
* employee lists;
* attendance;
* payroll information;
* expenses;
* refunds;
* cash-register reports;
* branch configuration;
* audit information;
* exports.

A user with permission to view one branch must not automatically see records from another branch.

---

# 15. Write Authorization

Write operations require both:

1. permission to perform the operation;
2. authorization for the target branch.

Examples include:

* creating an order;
* changing an order;
* adjusting inventory;
* creating an expense;
* processing a refund;
* modifying branch configuration;
* changing employee assignments.

A valid functional permission must not be sufficient by itself.

---

# 16. Delete and Destructive Operations

Destructive operations require stricter authorization.

Where deletion is permitted, the employee must have:

* the required functional permission;
* authorized branch scope;
* authorization for the specific resource;
* any required approval.

Where business rules require archival instead of deletion, branch authorization must also apply to archival operations.

A user must not archive or delete another branch's resources merely because the user's role normally permits archival or deletion.

---

# 17. Owner Scope

The Owner has broader authority within the business but remains subject to the business security model.

Owner access may include:

* branch management;
* employee management;
* role and permission management;
* recipes;
* salaries;
* reports;
* configuration;
* menu management;
* operational oversight.

However, Owner privileges must still remain inside the correct business boundary.

Owner access must not become platform-level access.

The Owner must not automatically obtain access to:

* another business;
* Super Admin functions;
* platform infrastructure;
* unrelated tenant data.

---

# 18. Manager Scope

Managers operate below Owner authority.

A Manager may receive permissions such as:

* employee management;
* operational management;
* inventory management;
* reporting;
* branch operations.

Manager access must be restricted to:

* assigned branches;
* assigned functions;
* explicitly authorized resources.

A Manager must not use employee-management capabilities to grant themselves broader authorization.

A Manager must also not grant another employee permissions beyond the Manager's own authority.

---

# 19. Permission Delegation Boundary

An employee must not grant permissions that exceed their own authorization boundary.

For example:

```text
Manager
  Branch Scope: Branch 1
  Permission: Employee Management
```

The Manager may manage employees in Branch 1 according to their granted authority.

The Manager must not:

* grant Branch 2 access;
* grant platform-level privileges;
* grant permissions they do not possess;
* bypass Owner restrictions;
* create an unrestricted administrator.

Authorization delegation must remain bounded by the delegator's authority.

---

# 20. Branch Context Switching

Users with multiple branch assignments may switch between authorized branches.

Branch switching must not be treated as permission escalation.

When a branch context changes:

* the new branch must be within the user's authorized scope;
* available functions must be recalculated for that branch;
* branch-specific permissions must apply;
* branch-specific resources must be isolated;
* unauthorized branch identifiers must be rejected.

A branch switch must never allow access to a branch outside the user's assigned scope.

---

# 21. Cross-Branch Operations

Some business operations may legitimately require multiple branches.

Examples include:

* Owner reporting;
* authorized management reporting;
* selected multi-branch inventory oversight;
* authorized employee administration;
* cross-branch business analytics.

Cross-branch operations must be explicitly authorized.

The existence of a multi-branch report permission does not automatically authorize access to every operational resource in those branches.

For example:

```text
Allowed:
  Manager → View sales reports → Branch 1 + Branch 3

Denied:
  Manager → Modify Branch 3 inventory
```

if inventory modification was not granted for Branch 3.

---

# 22. Cross-Branch Reporting

Reports may aggregate multiple branches only when the user has access to all included branches.

The system must not produce an aggregate report that indirectly reveals unauthorized branch data.

This applies to:

* dashboards;
* charts;
* summaries;
* exports;
* comparisons;
* calendar reports;
* financial reports;
* inventory reports;
* staff reports.

A report's authorization boundary must be at least as restrictive as the data it contains.

---

# 23. Search and Filtering

Search must respect authorization boundaries.

Employees must not discover unauthorized resources through:

* global search;
* autocomplete;
* filters;
* sorting;
* reports;
* exports;
* identifiers;
* error responses.

A resource that cannot be viewed directly must not become discoverable through a search feature.

---

# 24. Export and Import Scope

Import and export operations are security-sensitive because they may move large amounts of data.

Exports must contain only data within the user's authorized scope.

Imports must not allow an employee to create or modify data in an unauthorized branch.

Examples:

```text
Authorized:
  Employee → Export Branch 1 inventory

Denied:
  Employee → Export Branch 2 inventory
```

Similarly:

```text
Authorized:
  Manager → Import employees for Branch 1

Denied:
  Manager → Import employees into Branch 2
```

unless Branch 2 is explicitly within the Manager's authorization.

---

# 25. Inventory and Warehouse Scope

Inventory and warehouse operations must respect branch ownership.

An employee authorized for Branch 1 inventory must not automatically access:

* Branch 2 warehouse;
* Branch 2 stock quantities;
* Branch 2 inventory adjustments;
* Branch 2 purchase records;
* Branch 2 discrepancies.

Cross-branch inventory operations require explicit authorization.

---

# 26. Cash Register Scope

Cash registers are branch-scoped resources.

A cashier assigned to Branch 1 must not:

* open Branch 2's register;
* close Branch 2's register;
* modify Branch 2's register data;
* view another branch's cash balance;
* perform another branch's cash corrections.

Register operations must remain bound to the authorized branch.

---

# 27. Order Scope

Orders belong to a branch.

Employees may access orders only when:

* the order belongs to an authorized business;
* the order belongs to an authorized branch;
* the employee has the required order permission;
* the requested operation is permitted for that role.

Changing an order's identifier, branch reference, or other client-controlled value must not bypass these rules.

---

# 28. Employee Data Scope

Employee information is also branch-sensitive.

An employee may view or manage another employee only when:

* the target employee belongs to an authorized business;
* the target employee is within an authorized branch scope;
* the actor has the required employee-management permission.

Sensitive employee information must receive additional authorization where required by business policy.

---

# 29. Attendance and Payroll Scope

Attendance and payroll records must follow branch and functional authorization.

For example:

```text
Employee:
  Branch 1
  Attendance Permission
```

does not automatically provide access to:

```text
Branch 2 Attendance
Branch 1 Payroll
Branch 2 Payroll
```

Payroll access must be separately authorized.

---

# 30. Recipe and Menu Scope

Recipes and menus may have global and branch-specific relationships.

Security must distinguish between:

* business-wide recipe information;
* branch-allowed menu items;
* branch-specific menu availability;
* branch-specific pricing;
* restricted recipe information.

An employee's access to a branch menu must not automatically expose restricted recipe information.

Recipe modification must remain subject to the required functional permission and branch/business scope.

---

# 31. Device and Peripheral Scope

Devices and peripherals are associated with operational branches.

Examples:

* POS devices;
* receipt printers;
* kitchen printers;
* cash-register devices;
* branch-specific terminals.

An employee or device authorized for one branch must not use branch-scoped device resources to operate another branch unless explicitly authorized.

Branch scope must therefore apply to operational device actions as well as human actions.

---

# 32. Offline Authorization

Offline operation must preserve branch authorization.

When a branch operates offline:

* employees may operate only within their previously authorized offline scope;
* unauthorized branch access must not become possible because connectivity is unavailable;
* locally stored branch data must remain isolated;
* synchronization must preserve original branch ownership;
* offline actions must not silently expand employee scope.

Offline operation must never be treated as an authorization bypass.

---

# 33. Synchronization Scope

Synchronization must preserve branch boundaries.

A synchronization process must not:

* merge records into the wrong branch;
* expose another branch's records to a local employee;
* transfer unauthorized branch data to a device;
* treat device ownership as branch authorization.

Every synchronized resource must retain its original business and branch context.

---

# 34. Background Processing

Background operations must respect the same authorization boundaries as interactive operations.

Examples include:

* report generation;
* notifications;
* scheduled processing;
* synchronization;
* inventory calculations;
* subscription processing;
* data archival.

A background process must operate only within the explicitly defined scope of the job.

A worker processing Branch 1 data must not accidentally process Branch 2 data because both belong to the same business.

---

# 35. Notifications

Notifications must respect branch scope.

Employees must not receive notifications containing unauthorized branch information.

For example:

```text
Branch 1 Manager
```

must not receive:

```text
Branch 2 inventory shortage
```

unless the Manager has explicit Branch 2 visibility.

This applies to:

* in-application notifications;
* operational alerts;
* report notifications;
* security events;
* subscription-related notifications where branch context is relevant.

---

# 36. Audit Scope

Authorization-sensitive events must record sufficient context to determine:

* who performed the action;
* which business was involved;
* which branch was involved;
* what permission was used;
* what resource was affected;
* whether the operation was allowed or denied;
* when the event occurred.

Audit records must themselves follow appropriate visibility rules.

Employees must not gain unrestricted access to security audit information merely because they can view operational records.

---

# 37. Scope Changes

Branch and permission changes are security-sensitive operations.

Changes may include:

* adding an employee to a branch;
* removing an employee from a branch;
* changing role;
* changing branch-specific permissions;
* granting all-branch scope;
* reducing branch scope;
* changing Manager authority.

The security model requires:

* authorized change;
* clear effective scope;
* auditable change;
* predictable effect on future requests.

---

# 38. Permission Revocation

When branch scope or permissions are removed:

> Future authorization decisions must reflect the reduced scope.

Revocation must not depend on the employee voluntarily logging out.

Previously authorized data already retained by the system must remain governed by its normal lifecycle and security policy.

New access after revocation must be denied.

---

# 39. Temporary Access

Temporary branch access may be granted when supported by business policy.

Temporary access must have:

* explicit authorization;
* defined scope;
* defined purpose;
* defined duration where applicable;
* auditability;
* automatic expiration when applicable.

Temporary access must not silently become permanent branch access.

---

# 40. Emergency Access

Emergency access may exist for exceptional operational situations.

Emergency access must:

* be explicitly controlled;
* be limited to the required scope;
* be auditable;
* avoid unnecessary privilege expansion;
* expire or be revoked when the emergency ends.

Emergency access must not become a normal authorization mechanism.

---

# 41. Authorization Conflicts

Authorization conflicts may occur when different rules produce different results.

Examples:

```text
Role: Manager
Branch: Branch 1
Permission: Inventory = Allowed
Resource: Branch 2
```

The result is **Denied**.

Another example:

```text
Role: Manager
Branch: Branch 1
Permission: Inventory = Denied
Resource: Branch 1
```

The result is also **Denied**.

The general rule is:

> A missing or denied authorization boundary cannot be overridden by another broader permission.

---

# 42. Deny-by-Default

Branch authorization follows deny-by-default principles.

Access must be denied when:

* branch scope is missing;
* branch scope is ambiguous;
* target branch cannot be determined safely;
* permission is missing;
* resource ownership is uncertain;
* authorization state is inconsistent;
* the request attempts unauthorized scope expansion.

The system must not guess an employee's intended branch.

---

# 43. Authorization Failure Handling

Authorization failures should not expose sensitive information.

A denied request should not reveal:

* whether an unauthorized resource exists;
* another branch's internal identifiers;
* confidential employee information;
* inventory values;
* financial values;
* security configuration.

Authorization failures must be handled consistently across user interfaces, APIs, reports, imports, exports, offline operations, and background processing.

---

# 44. Common Threats

Branch and scope isolation must defend against:

### 44.1 Cross-Branch Access

An employee attempts to access another branch.

### 44.2 Identifier Manipulation

An employee changes a resource identifier to target another branch.

### 44.3 Permission Escalation

An employee attempts to grant themselves additional branch or functional permissions.

### 44.4 Manager Privilege Expansion

A Manager attempts to use employee-management capabilities to obtain authority beyond their own scope.

### 44.5 Branch Context Confusion

A user or system component accidentally operates under the wrong branch context.

### 44.6 Cross-Branch Data Leakage

Reports, notifications, exports, caches, or background jobs expose another branch's information.

### 44.7 Offline Scope Bypass

A device operating offline attempts to access unauthorized branch data.

### 44.8 Synchronization Scope Leakage

Synchronization transfers records across incorrect branch boundaries.

### 44.9 Stale Authorization

Removed branch access continues to permit new operations.

### 44.10 Aggregate Data Leakage

A multi-branch summary indirectly exposes data from unauthorized branches.

---

# 45. Security Control Model

The security control model is:

```text
Business Boundary
        ↓
Branch Boundary
        ↓
Employee Scope
        ↓
Role
        ↓
Functional Permission
        ↓
Resource Ownership
        ↓
Action Authorization
```

Every sensitive operation must respect the complete chain.

---

# 46. Performance and Scalability

Security controls must remain compatible with the ERP's performance requirements.

Branch isolation must not require unnecessary heavy processing for ordinary operations.

The system should prefer:

* clear authorization boundaries;
* predictable scope evaluation;
* bounded branch assignments;
* explicit permissions;
* efficient authorization decisions;
* minimal repeated security computation.

Security must not be weakened to achieve performance.

Likewise, security must not introduce unnecessary complexity that provides no meaningful protection.

---

# 47. Multi-Branch Scaling

The initial system may support a limited number of branches, but branch authorization must remain conceptually scalable.

Adding branches must not require redesigning the security model.

The security model must continue to support:

* additional branches;
* additional employees;
* additional roles;
* branch-specific permissions;
* multi-branch managers;
* centralized owners.

Authorization must remain based on explicit scope rather than hard-coded branch assumptions.

---

# 48. Security Monitoring

The system should monitor important scope-related security events, including:

* repeated unauthorized branch access attempts;
* unexpected scope changes;
* unusual privilege expansion;
* unauthorized permission changes;
* repeated cross-branch authorization failures;
* suspicious export attempts;
* unexpected branch switching patterns.

Monitoring must support investigation without unnecessarily exposing operational data.

---

# 49. Security Incident Response

A confirmed branch-isolation violation must be treated as a security incident.

Potential actions include:

* identifying affected business and branches;
* identifying affected identities;
* reviewing authorization changes;
* reviewing relevant audit events;
* limiting compromised access;
* correcting authorization state;
* determining affected data;
* preserving evidence;
* applying appropriate remediation.

Incident handling follows the broader security incident response policy.

---

# 50. Verification Requirements

Branch and scope isolation must be verified through security testing.

Verification should cover:

* single-branch employees;
* multi-branch employees;
* all-branch users;
* Owner;
* Manager;
* restricted roles;
* branch-specific permissions;
* cross-branch requests;
* cross-branch reports;
* imports;
* exports;
* offline operation;
* synchronization;
* background processing;
* notifications;
* device operations;
* revoked branch access;
* changed permissions.

Testing must verify both positive and negative authorization cases.

---

# 51. Security Invariants

The following invariants are mandatory.

### Invariant 1 — Business Boundary

No employee may cross the authorized business boundary.

### Invariant 2 — Branch Boundary

No employee may access a branch outside their authorized branch scope.

### Invariant 3 — Permission Boundary

Branch access does not automatically grant functional permissions.

### Invariant 4 — Scope Boundary

Functional permissions do not automatically grant additional branch scope.

### Invariant 5 — Resource Ownership

A resource must remain accessible only within its authorized ownership and scope.

### Invariant 6 — Manager Boundary

Managers cannot grant themselves or others authority beyond their own authorization.

### Invariant 7 — Owner Boundary

Owner privileges remain inside the business boundary and do not become platform-level privileges.

### Invariant 8 — Cross-Branch Reporting

Aggregated reports may include only branches the user is authorized to view.

### Invariant 9 — Offline Boundary

Offline operation cannot bypass branch authorization.

### Invariant 10 — Synchronization Boundary

Synchronization cannot move data across unauthorized branch boundaries.

### Invariant 11 — Revocation

Removed branch access must deny future unauthorized operations.

### Invariant 12 — Deny by Default

Ambiguous or incomplete authorization must result in denial.

### Invariant 13 — Auditability

Security-sensitive scope changes and authorization events must be auditable.

### Invariant 14 — No Identifier Bypass

Knowledge or manipulation of resource identifiers cannot bypass branch authorization.

---

# 52. Relationship to Other Documents

This document depends on and complements:

* `01_Security_Architecture_Overview.md`
* `02_Security_Principles_and_Threat_Model.md`
* `03_Identity_and_Access_Security.md`
* `04_Business_and_Tenant_Isolation_Security.md`

It provides security policy boundaries for topics described technically in:

* Architecture documentation;
* Backend documentation;
* API documentation;
* Database documentation;
* Frontend documentation;
* Deployment documentation;
* Testing documentation.

This document must not duplicate their implementation details.

---

# 53. Final Security Rules

The FastFood ERP branch authorization model follows these final rules:

1. Every employee has an explicit authorization scope.
2. Branch access must be explicitly granted.
3. Role and branch scope are separate security dimensions.
4. Functional permission does not grant branch access.
5. Branch access does not grant functional permission.
6. Resource ownership must always be respected.
7. Cross-branch access requires explicit authorization.
8. Cross-branch reporting requires authorization for every included branch.
9. Managers cannot exceed their own authorization boundaries.
10. Owners remain inside their business boundary.
11. Offline operation cannot bypass scope restrictions.
12. Synchronization cannot cross branch boundaries incorrectly.
13. Exports and imports must respect branch scope.
14. Notifications and background processing must respect branch scope.
15. Branch and permission changes must be auditable.
16. Revoked scope must not permit new unauthorized operations.
17. Ambiguous authorization must fail closed.
18. Resource identifiers must never act as authorization.
19. Security controls must remain effective as the system scales.
20. Branch isolation is a security boundary, not merely a UI filtering rule.

---

# 54. Acceptance Criteria

This document is accepted when:

* branch isolation is explicitly defined;
* employee scope is explicitly defined;
* role and branch authorization are separated;
* functional permission boundaries are defined;
* Owner and Manager boundaries are defined;
* cross-branch operations are governed;
* reports, imports, and exports respect branch scope;
* offline and synchronization boundaries are defined;
* resource ownership is protected;
* authorization revocation is defined;
* common branch-scope threats are documented;
* security invariants are explicit;
* implementation duplication with technical documentation is avoided.

**Status: Accepted**

**End of SEC-05**

