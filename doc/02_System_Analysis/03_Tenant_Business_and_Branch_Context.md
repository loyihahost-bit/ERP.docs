# Tenant, Business and Branch Context

**Document ID:** SA-03
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines how FastFood ERP represents and enforces Business, Tenant and Branch context throughout the system.

It establishes:

* Business/Tenant isolation;
* Business context;
* Branch context;
* multi-branch access;
* employee branch assignments;
* branch-specific permissions;
* global versus branch-specific configuration;
* branch switching;
* cross-branch operations;
* data access boundaries;
* background job and synchronization context.

The objective is to ensure that every operation is executed within the correct Business and Branch context and that data from different tenants or branches is never mixed unintentionally.

---

## 2. Tenant Model

FastFood ERP is a multi-tenant SaaS system.

The primary tenant boundary is the **Business**.

Conceptually:

```text id="8q4jzv"
Platform
   │
   ├── Business A
   │      ├── Branch A1
   │      └── Branch A2
   │
   ├── Business B
   │      ├── Branch B1
   │      └── Branch B2
   │
   └── Business C
          └── Branch C1
```

Operational data belonging to one Business must never be accessible to another Business.

Tenant isolation applies to all relevant system layers.

---

## 3. Business Identity

Each Business has a unique permanent Business UUID.

The Business UUID is the primary tenant identity used to establish data ownership.

Business-scoped records must be associated with the correct Business context.

Where an entity is also Branch-scoped, both Business and Branch context must be valid.

Conceptually:

```text id="svb3by"
Business UUID
     │
     └── Branch UUID
            │
            └── Entity UUID
```

An entity must never reference a Branch belonging to another Business.

---

## 4. Business Context

After authentication, the system establishes the authenticated employee's Business context.

The Business context determines:

* which data may be accessed;
* which configuration applies;
* which subscription applies;
* which employees are available;
* which branches are available;
* which menu and recipe configuration applies;
* which reports may be generated;
* which notifications may be displayed.

The client must not be allowed to arbitrarily replace the authenticated Business context.

---

## 5. Business Isolation

Business isolation must be enforced server-side.

The system must not rely solely on:

* frontend filtering;
* URL parameters;
* client-side state;
* hidden UI elements.

Every protected operation must validate the Business context before accessing or modifying Business data.

For example:

```text id="6d2w9c"
Authenticated User
       ↓
Business Context
       ↓
Requested Entity
       ↓
Entity.Business UUID == Context.Business UUID
       ↓
Allowed / Rejected
```

If the Business context does not match, the operation must be rejected.

---

## 6. Branch Model

A Business may contain multiple Branches.

Each Branch has:

* unique Branch UUID;
* Business UUID;
* operational configuration;
* branch-specific employees or assignments;
* inventory context;
* cash register context;
* table context;
* order context;
* branch-specific reports;
* branch-specific settings where applicable.

A Branch always belongs to exactly one Business.

---

## 7. Branch Scope

Branch scope determines which operational data an employee may access.

An employee may have:

* one Branch;
* multiple Branches;
* all permitted Branches.

Branch scope is part of effective authorization.

Example:

```text id="gk4d0x"
Employee
   │
   ├── Branch A → Allowed
   ├── Branch B → Allowed
   └── Branch C → Denied
```

The employee must not access Branch C merely because Branch C belongs to the same Business.

---

## 8. Employee Multi-Branch Assignment

An employee may work in multiple branches.

The same employee identity is retained across all branches.

The system does not create a separate employee account for every branch.

Instead:

```text id="kgk2d8"
Employee
   │
   ├── Branch A
   │      └── Permission Set A
   │
   ├── Branch B
   │      └── Permission Set B
   │
   └── Branch C
          └── Permission Set C
```

The employee's effective permissions may therefore differ by branch.

---

## 9. Branch-Specific Permissions

Permissions are evaluated in the current Branch context.

For example:

```text id="2jsb7g"
Employee: E-001

Branch A
→ Inventory View
→ Inventory Adjustment

Branch B
→ Inventory View only

Branch C
→ No Inventory Access
```

The system must calculate effective permissions when the employee changes Branch context.

Permissions from one Branch must never leak into another Branch.

---

## 10. Global and Branch Configuration

FastFood ERP contains both Business-wide and Branch-specific configuration.

### Business-wide examples

* global products;
* recipes;
* categories;
* global menu;
* standard prices;
* roles;
* Business-level settings;
* subscription configuration.

### Branch-specific examples

* inventory;
* warehouse state;
* cash sessions;
* tables;
* branch menu availability;
* branch price overrides;
* branch employees;
* branch operational settings.

The system must explicitly define which configuration level owns each setting.

---

## 11. Configuration Resolution

When both Business-level and Branch-level configuration exist, the system resolves the effective configuration according to the relevant business rule.

A typical model is:

```text id="y8fbyh"
Business Configuration
        ↓
Branch Override
        ↓
Effective Branch Configuration
```

A Branch override affects only that Branch.

For example:

```text id="9ujg4x"
Global Product Price
        │
        ├── Branch A → Global Price
        ├── Branch B → Override Price
        └── Branch C → Global Price
```

Changing the Branch B price must not modify the global price or Branch A/C prices.

---

## 12. Branch Switching

An employee with multiple Branch assignments may switch the active Branch.

The system must validate:

1. employee is active;
2. employee belongs to the Business;
3. target Branch belongs to the same Business;
4. employee has access to the Branch;
5. current subscription permits the operation;
6. required Branch configuration is available.

After successful switching:

* current Branch context changes;
* effective permissions are recalculated;
* branch-specific configuration is refreshed;
* branch-specific operational data is refreshed;
* stale Branch data must no longer be used.

---

## 13. Branch Switching and Active Operations

The application must prevent unsafe context switching during operations where the current Branch context is critical.

For example, the system should not allow an employee to switch Branch context in the middle of a transaction that has not yet been safely completed.

The system may:

* require the current operation to finish;
* save a valid temporary state;
* reject the context switch;
* request explicit confirmation.

The exact UI behavior may be refined during Frontend Analysis, but the system must never attach a transaction to the wrong Branch.

---

## 14. Order Branch Ownership

Every Order belongs to exactly one Business and one Branch.

Conceptually:

```text id="z8zqgl"
Order
 ├── Business UUID
 └── Branch UUID
```

An order created in Branch A cannot be silently moved to Branch B.

Branch context is preserved for:

* order history;
* payments;
* cash sessions;
* inventory deductions;
* kitchen operations;
* audit events;
* reports.

---

## 15. Payment Branch Ownership

Payments inherit the operational context of their related order unless a separate business rule explicitly defines another context.

Payment records must preserve:

* Business;
* Branch;
* Order;
* Employee;
* Device;
* Cash Session where applicable.

A payment from Branch A must not be assigned to a Branch B cash session.

---

## 16. Inventory Branch Ownership

Branch inventory is operationally isolated.

A stock quantity in Branch A cannot automatically satisfy a sale in Branch B.

The current system does not include automatic branch-to-branch inventory transfer.

Therefore:

```text id="q4u2h5"
Branch A Inventory
       ≠
Branch B Inventory
```

Inventory operations must always use the correct Branch context.

---

## 17. Cash Session Branch Ownership

A Cash Session belongs to:

* one Business;
* one Branch;
* one Cash Register;
* one operational cashier session.

A Cash Session cannot be reassigned to another Branch.

During cashier handover:

* the physical register remains associated with the same Branch;
* the previous Cash Session remains historical;
* a new Cash Session is created.

---

## 18. Table Branch Ownership

Tables belong to one Branch.

A table cannot simultaneously belong to multiple Branches.

Table visits and orders inherit the table's Branch context.

A customer visit in Branch A must never appear as an active table visit in Branch B.

---

## 19. Employee Context

Employee identity is Business-scoped.

An employee cannot belong to multiple Businesses under the same employee identity unless a future explicit platform requirement introduces such functionality.

Within one Business, the employee may have multiple Branch assignments.

The employee's current operational context is:

```text id="lcz0bj"
Business
   +
Employee
   +
Current Branch
   +
Effective Permissions
```

---

## 20. Role Scope

Roles may be Business-level or applied within a Branch scope according to the permission model.

The role itself does not automatically grant unrestricted access to every Branch.

Effective access is determined through:

* role permission;
* employee override;
* branch scope;
* subscription entitlement.

Therefore:

```text id="7n2xcy"
Role Permission
       +
Employee Override
       +
Branch Scope
       +
Subscription
       =
Effective Permission
```

---

## 21. Cross-Branch Reporting

Authorized users may access reports across multiple Branches when their permissions allow it.

A Business-level report may aggregate data from multiple Branches.

A Branch-level report must contain only data belonging to the selected Branch.

Example:

```text id="knzj6m"
Business Report
 ├── Branch A
 ├── Branch B
 └── Branch C

Branch Report
 └── Branch B only
```

Report scope must be explicit.

---

## 22. Cross-Branch Employee Management

An Owner or authorized Manager may manage employees across multiple Branches if their permission scope allows it.

The system must distinguish between:

* employee identity;
* branch assignment;
* branch permission;
* role;
* employee override.

Changing an employee's Branch assignment must not erase historical activity from previously assigned branches.

---

## 23. Historical Branch Context

Historical records must preserve the Branch context that existed when the operation occurred.

Examples include:

* orders;
* payments;
* cash sessions;
* inventory movements;
* attendance;
* payroll;
* reports;
* audit events;
* corrections.

If an employee later moves from Branch A to Branch B, their historical Branch A operations remain associated with Branch A.

Historical records must not be dynamically reassigned based on current employee assignments.

---

## 24. Background Job Context

Background jobs must carry sufficient Business and Branch context when processing scoped data.

For example:

```text id="t1n6fj"
Background Job
   │
   ├── Business UUID
   ├── Branch Scope
   ├── Entity UUID
   └── Job UUID
```

A background worker must not process an entity without validating its Business/Branch context.

This is especially important for:

* reports;
* notifications;
* synchronization;
* subscription lifecycle;
* deletion;
* exports.

---

## 25. Synchronization Context

Offline synchronization events preserve the original operational context.

An offline event must contain or reference:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Transaction UUID;
* Entity UUID;
* Cash Session UUID where applicable.

When synchronized, the server validates that the original context remains valid.

A device must not change the Business or Branch identity of an offline event merely because the user is currently viewing another Branch.

---

## 26. Device and Branch Context

A trusted device may be associated with permitted operational Branches.

Device trust does not override employee branch scope.

For example:

```text id="xm7x2q"
Trusted Device
     +
Employee
     +
Branch Access
     =
Valid Operational Context
```

A trusted device assigned to Branch A does not automatically allow an employee without Branch B permission to access Branch B.

---

## 27. Subscription and Branch Limits

Subscription entitlement may limit the number of Branches available to a Business.

The system must enforce such limits at the Business level.

When a Business reaches its Branch limit:

* creation of additional Branches is blocked;
* existing Branches are not deleted automatically;
* historical data remains preserved;
* downgrade must not cause destructive deletion.

The exact tariff limit is defined by subscription configuration.

---

## 28. Business and Branch Deactivation

Business or Branch status changes must affect new operations according to the relevant lifecycle rules.

A deactivated Branch must not accept new operational transactions when the system rules prohibit them.

Historical data remains accessible according to:

* Business lifecycle;
* Branch state;
* employee permission;
* subscription state.

Deactivation must not silently delete historical Branch data.

---

## 29. Cross-Branch Operations

The current system does not support automatic inventory transfer between branches.

Similarly, operational transactions such as Orders and Cash Sessions remain owned by their original Branch.

If a future requirement introduces cross-branch operations, they must be modeled as explicit transactions with:

* source Branch;
* destination Branch;
* authorization;
* transaction identity;
* audit history;
* inventory effects.

They must not be implemented as silent changes to Branch ownership.

---

## 30. Tenant Isolation in API

Every API operation involving Business data must establish tenant context before performing the operation.

Conceptually:

```text id="btyd11"
Request
   ↓
Authentication
   ↓
Business Context
   ↓
Branch Context
   ↓
Authorization
   ↓
Business Rule
   ↓
Database Operation
```

The API must never trust arbitrary Business or Branch identifiers supplied by the client without validating them against the authenticated context.

---

## 31. Tenant Isolation in Database Access

Database access must enforce Business ownership and applicable Branch scope.

Queries involving tenant data must be designed so that cross-tenant access cannot occur accidentally.

Important records should maintain explicit ownership relationships where required.

Database constraints should protect relationships such as:

```text id="v9okqy"
Branch.Business UUID
        =
Entity.Business UUID
```

and:

```text id="v3r9cz"
Branch.Business UUID
        =
Related Entity Business UUID
```

The exact database implementation will be defined in `docs/05_Database/`.

---

## 32. Tenant Isolation in Reports and Exports

Reports and Excel exports must respect the same Business and Branch boundaries as normal API operations.

An export must never include:

* another Business's data;
* an unauthorized Branch;
* an employee's restricted information;
* data outside the reporter's permission scope.

Export generation must therefore carry explicit scope information.

---

## 33. Tenant Isolation in Notifications

Notifications must belong to the correct Business.

Branch-scoped notifications must also contain Branch context.

A notification generated in Branch A must not appear to an employee who has access only to Branch B.

Business-level notifications may be visible across multiple Branches when the recipient's permissions allow it.

---

## 34. Tenant Isolation in Audit

Audit records must preserve:

* Business UUID;
* Branch UUID where applicable;
* Actor;
* Device;
* Entity;
* Transaction.

Audit search and filtering must enforce the requester's authorized Business and Branch scope.

A user must never be able to query another Business's audit history.

---

## 35. Tenant Isolation in Offline Storage

Offline data is stored within the trusted device context.

Local records must preserve:

* Business identity;
* Branch identity;
* Employee identity;
* Device identity;
* transaction identity.

Offline storage must not allow records from one Business to be accidentally submitted under another Business context.

Local encryption and secure device handling are defined in the security and offline documents.

---

## 36. Context Validation on Every Critical Operation

Critical operations must validate context at the time the operation is executed.

Examples:

```text id="8t2f7e"
Order Accept
    ↓
Business Match
    ↓
Branch Match
    ↓
Employee Permission
    ↓
Subscription
    ↓
Inventory
    ↓
Execute
```

The system must not assume that context from an earlier screen remains valid.

This is especially important after:

* branch switching;
* permission changes;
* employee deactivation;
* subscription changes;
* synchronization;
* device revocation.

---

## 37. Context Changes During Active Sessions

A user's Business or Branch context may change while an application session is active.

Examples include:

* permission change;
* employee deactivation;
* branch assignment change;
* subscription expiration;
* device revocation.

The next protected operation must be validated against the current authoritative state.

The client must not continue using stale authorization indefinitely.

---

## 38. System Invariants

The following invariants apply to Business and Branch context:

1. Every operational entity belongs to exactly one Business.
2. Every Branch belongs to exactly one Business.
3. A Branch cannot belong to another Business.
4. Cross-Business operational access is prohibited.
5. Business context is determined from authenticated identity and server-side context.
6. Client-supplied Business identifiers cannot override authenticated Business context.
7. Branch scope is part of effective authorization.
8. An employee may work in multiple Branches within the same Business.
9. An employee's permissions may differ between Branches.
10. Switching Branch recalculates effective permissions.
11. Branch A configuration must not modify Branch B unless an explicit Business-wide rule applies.
12. Branch inventory is operationally isolated.
13. Cash Sessions belong to one Branch.
14. Orders belong to one Branch.
15. Tables belong to one Branch.
16. Historical records retain their original Branch context.
17. Employee reassignment must not rewrite historical records.
18. Background jobs must preserve tenant and applicable Branch context.
19. Offline events preserve their original Business and Branch context.
20. Synchronization cannot silently move an offline transaction to another Branch.
21. Reports must respect Business and Branch scope.
22. Excel exports must respect Business and Branch scope.
23. Notifications must respect Business and Branch visibility.
24. Audit queries must respect Business and Branch authorization.
25. Subscription Branch limits must be enforced server-side.
26. Branch limits must not cause automatic destructive deletion.
27. Cross-Branch inventory transfer is outside the current system scope.
28. Branch context must be validated for every critical branch-scoped operation.
29. Stale client context must never override authoritative server context.
30. Tenant isolation must be enforced independently of frontend navigation.

---

## 39. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`

### System Analysis

* `docs/02_System_Analysis/README.md`
* `docs/02_System_Analysis/01_System_Context_and_Boundaries.md`
* `docs/02_System_Analysis/02_Application_Structure_and_Navigation.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`

---

## 40. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `03_Tenant_Business_and_Branch_Context.md`

**Next Document:** `04_Authentication_and_Authorization.md`

