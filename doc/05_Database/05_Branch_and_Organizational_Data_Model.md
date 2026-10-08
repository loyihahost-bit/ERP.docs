# Branch and Organizational Data Model

**Document ID:** DB-05
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for Business organizational structure and Branch operations.

It establishes how the database represents:

* Business-to-Branch ownership;
* Branch identity;
* Branch lifecycle;
* Branch configuration scope;
* employee branch assignments;
* branch-specific permissions;
* branch operational isolation;
* branch-level inventory;
* branch-level cash operations;
* branch-level reporting;
* branch-aware offline and synchronization data.

The model must preserve strict Business isolation while allowing one Business to operate multiple Branches.

---

# 2. Organizational Hierarchy

The primary organizational hierarchy is:

```text
Platform
   ↓
Business
   ↓
Branch
   ↓
Operational Resources
```

Operational resources may include:

* employees;
* warehouses;
* inventory;
* cash registers;
* cash sessions;
* orders;
* payments;
* reports;
* branch configuration;
* trusted devices;
* branch-specific menu availability.

A Branch must never exist outside a Business.

---

# 3. Branch Identity

## 3.1 Branch

`Branch` represents one physical or operational location belonging to a Business.

Conceptual fields:

* `id`
* `business_id`
* `name`
* `code`
* `status`
* address/location metadata
* timezone where explicitly supported
* created timestamp
* updated timestamp
* deactivated timestamp

The Branch UUID is the authoritative identity.

---

## 3.2 Branch UUID

`branch.id` must be:

* UUID;
* globally unique;
* immutable;
* never reused.

Branch names and codes are descriptive identifiers and must not be used as primary identity references.

---

# 4. Business Ownership

Every Branch belongs to exactly one Business.

Conceptually:

```text
Business
   └── Branch
```

The database must prevent:

* a Branch referencing a nonexistent Business;
* a Branch belonging to multiple Businesses;
* cross-Business operational references.

The Business ID must be available in branch-scoped data or derivable through a guaranteed relationship.

---

# 5. Branch Lifecycle

Branch lifecycle:

```text
Created
   ↓
Active
   ↓
Inactive
   ↓
Archived
```

The exact operational states may be represented using status values rather than separate physical tables.

An inactive Branch:

* cannot accept new normal operations;
* cannot open new operational sessions;
* cannot accept new orders;
* cannot create new inventory transactions;
* cannot create new payments;
* cannot create new employee assignments.

Historical data remains available according to permissions and Business lifecycle rules.

---

# 6. Branch Creation

Branch creation is a Business-level operation.

The system must verify:

1. authenticated actor;
2. Business membership;
3. required permission;
4. subscription Branch entitlement;
5. valid Branch configuration;
6. unique Branch identity constraints.

Branch creation should initialize required operational configuration.

Examples may include:

* default branch settings;
* cash register configuration;
* menu availability defaults;
* printer configuration;
* notification configuration;
* warehouse configuration.

Initialization should be transactional where required.

---

# 7. Branch Limits

The number of active Branches is controlled by subscription entitlement.

Subscription downgrade must not automatically delete existing Branches.

If the Business exceeds a newly reduced Branch limit:

* existing Branches remain;
* historical data remains;
* new Branch creation is blocked;
* reactivation of additional inactive Branches may be restricted;
* authorized users can continue viewing existing data according to entitlement rules.

---

# 8. Branch Code

A Business may use a human-readable Branch code.

Example:

```text
BR-001
BR-002
BR-003
```

The code is not the Branch primary identity.

Uniqueness should normally be enforced within the Business:

```text
UNIQUE(business_id, code)
```

Changing a Branch code must not alter historical Branch UUID references.

---

# 9. Branch Name

Branch names are mutable descriptive data.

Changing a Branch name must not affect:

* Branch UUID;
* historical orders;
* payments;
* cash sessions;
* inventory transactions;
* audit records;
* report versions.

Historical reports may use snapshots where required.

---

# 10. Branch Address and Metadata

Branch metadata may include:

* address;
* phone;
* notes;
* operating information;
* timezone configuration where supported.

These fields are descriptive and must not become security identifiers.

Sensitive operational metadata should be protected according to the security model.

---

# 11. Employee Branch Assignment

Employees may work in multiple Branches.

Relationship:

```text
Employee
    ↓
EmployeeBranch
    ↓
Branch
```

`EmployeeBranch` represents authorization and operational assignment.

It may contain:

* `employee_id`
* `branch_id`
* assignment status;
* effective start;
* effective end;
* assignment metadata.

---

# 12. Branch-Specific Employee Role

An employee may have different operational roles in different Branches.

Example:

```text
Employee A

Branch 1 → Cashier
Branch 2 → Manager
```

The database must therefore support Branch-aware role assignment.

The physical implementation may use:

* branch-specific role assignments;
* branch-scoped employee-role records;
* or another equivalent normalized structure.

---

# 13. Branch-Specific Permissions

Effective permission evaluation may depend on:

```text
Employee
+
Role
+
Permission
+
Branch
+
Subscription
```

A permission granted in Branch A must not automatically grant the same permission in Branch B.

Branch scope must therefore be represented explicitly when required.

---

# 14. Branch Switching

When an employee switches Branch context:

1. Business remains the same.
2. Active Branch changes.
3. Branch assignment is validated.
4. Branch-specific permissions are recalculated.
5. Branch-specific configuration is loaded.
6. Device scope is validated.
7. Subscription entitlement is re-evaluated where relevant.

The database must not permanently store an application session as though the employee had access to every Branch.

---

# 15. Branch Operational Context

Operational transactions should identify their Branch.

Examples:

```text
Order → branch_id
Payment → branch_id
CashSession → branch_id
InventoryTransaction → branch_id
Attendance → branch_id
Report → branch_id
AuditEvent → branch_id where applicable
```

This allows:

* branch isolation;
* branch reporting;
* authorization checks;
* offline validation;
* audit reconstruction.

---

# 16. Branch Isolation

Branch isolation must be enforced at multiple levels:

### Application

Every request is evaluated against the current Business and Branch scope.

### Database

Foreign keys and composite relationships prevent incompatible Business/Branch references.

### Reporting

Reports filter by authorized Branch scope.

### Offline

Offline authorization contains Business and Branch context.

### Synchronization

Synchronization events contain Branch context and are validated by the server.

---

# 17. Business and Branch Context

The system should treat Business and Branch as separate scopes.

```text
Business scope
     ↓
Branch scope
     ↓
Operational transaction
```

Some data is Business-wide.

Examples:

* global products;
* global recipes;
* global Sets;
* Business roles;
* Business configuration.

Other data is Branch-specific.

Examples:

* stock;
* warehouse;
* cash sessions;
* orders;
* attendance;
* branch price overrides;
* branch menu availability.

---

# 18. Branch Inventory Relationship

Each Branch may have its own inventory state.

Conceptually:

```text
Branch
   ↓
Warehouse
   ↓
Inventory
```

The same Product may exist in multiple Branches with different quantities.

Inventory quantity must never be treated as a single Business-wide stock value when the operation is Branch-specific.

---

# 19. Branch Warehouse

A Branch normally owns one or more logical warehouse locations according to the inventory model.

The initial operational model may use one primary warehouse per Branch while allowing future expansion.

Warehouse records must retain:

* Business;
* Branch;
* identity;
* status.

Cross-Branch stock movement is currently outside the operational scope.

---

# 20. Branch Cash Register

The current business model assumes one primary Cash Register per Branch.

Relationship:

```text
Branch
   ↓
Cash Register
   ↓
Cash Session
```

The database architecture must not prevent future support for multiple registers.

A Cash Register must belong to exactly one Branch.

---

# 21. Branch Cash Sessions

Cash Sessions are Branch-scoped.

Every Cash Session must identify:

* Business;
* Branch;
* Cash Register;
* cashier Employee;
* session UUID;
* status;
* opening/closing data.

Cash Session UUID remains stable throughout its lifecycle.

A closed session is never converted back into an active session.

Corrections are separate transactions.

---

# 22. Branch Orders

Every operational Order belongs to exactly one Branch.

The Order must retain:

* Business UUID;
* Branch UUID;
* Employee context;
* Device context where applicable;
* Cash Session context where applicable.

An Order must never be transferred between Branches as a normal operation.

Branch transfer is currently out of scope.

---

# 23. Branch Payments

Every operational Payment must belong to the same Business and Branch as its Order.

The database must prevent a payment from:

* Business A being applied to Business B;
* Branch A being applied to Branch B.

Payment correction must preserve the original Branch context.

---

# 24. Branch Menu Availability

Global Products may be enabled or disabled for individual Branches.

Conceptual relationship:

```text
Business Product
       ↓
BranchProduct
       ↓
Branch
```

Branch-specific availability may include:

* active/inactive;
* branch price override;
* availability status;
* effective configuration version.

Disabling a product in a Branch must not delete the global Product.

Historical Orders remain unchanged.

---

# 25. Branch Pricing

A Product may have:

* Business/global standard price;
* Branch-specific override.

Conceptually:

```text
Product
   ↓
Global Price
   ↓
Branch Price Override
```

Branch override requires appropriate permission.

Price changes follow configuration effective-time rules.

Open Orders retain their price snapshots.

---

# 26. Branch Configuration

Branch-specific configuration may include:

* printer routing;
* menu availability;
* price overrides;
* operational settings;
* notification thresholds;
* employee assignments;
* branch-specific workflow settings.

Configuration must remain versioned and historically reconstructable.

---

# 27. Branch Configuration Boundary

Branch configuration must not silently override Business-wide configuration without a deterministic rule.

Effective configuration is conceptually:

```text
Business Configuration
        +
Branch Configuration
        +
Permission
        +
Subscription Entitlement
        ↓
Effective Configuration
```

The exact precedence is defined by the Configuration Domain.

---

# 28. Branch Devices

Trusted devices may be scoped to:

* Business;
* Branch;
* Employee relationship.

A device trusted for Branch A must not automatically become trusted for Branch B.

Device trust is separate from employee authorization.

The Device Domain defines the complete lifecycle.

---

# 29. Branch Attendance

Attendance records may reference:

* Business;
* Branch;
* Employee;
* attendance event;
* timestamp;
* source device where applicable.

Attendance must preserve the Branch where the employee performed the operation.

Historical attendance must not change when the employee later receives a different Branch assignment.

---

# 30. Branch Payroll

Payroll configuration may be Business-level or Branch-scoped according to the payroll model.

Where salary rules are Branch-specific, the Branch context must be explicit.

Payroll records must preserve the Branch context used for calculation.

Finalized payroll must not be silently recalculated because a Branch configuration later changes.

---

# 31. Branch Expenses

Expenses may be associated with a Branch.

A Branch expense should contain:

* Business;
* Branch;
* creator;
* amount;
* date;
* category;
* comment;
* status where applicable.

Owner-level permissions control creation and modification.

Historical expense records remain attributable.

---

# 32. Branch Reports

Reports may be:

* Business-wide;
* Branch-specific;
* multi-Branch.

Report scope must be explicitly stored.

A Branch report must not expose data from unauthorized Branches.

A multi-Branch report must include only Branches within the requester's effective scope.

---

# 33. Branch Report Versioning

A report version must preserve:

* Business;
* Branch scope;
* reporting period;
* report definition;
* creation source;
* creation timestamp;
* relevant data state.

If Branch data changes and the change affects a report, a new report version may be generated.

Previous versions remain immutable.

---

# 34. Branch Audit Context

Important actions should include Branch context when applicable.

Examples:

* order creation;
* payment;
* cash session;
* inventory adjustment;
* recipe approval;
* price override;
* employee assignment;
* permission change;
* refund;
* correction.

Business-level actions may have no Branch context.

The absence of Branch context must be intentional rather than caused by missing data.

---

# 35. Branch Notifications

Notifications may be:

* Business-wide;
* Branch-specific;
* employee-specific.

Examples of Branch-scoped notifications:

* low stock;
* inventory variance;
* cash shortage;
* branch loss;
* branch-specific subscription/operational alerts where applicable.

Notification recipient visibility must respect Branch authorization.

---

# 36. Branch Synchronization

Every offline Branch operation must carry sufficient context to validate:

```text
Business
Branch
Employee
Device
Transaction
```

The server must verify that:

* Branch still belongs to the Business;
* Employee still has Branch access;
* Device remains trusted;
* operation remains permitted;
* subscription permits the operation.

A stale event must not create state in another Branch.

---

# 37. Branch Conflict Handling

Branch conflicts must remain explicit.

Examples:

* employee removed from Branch;
* Branch deactivated;
* product disabled in Branch;
* stock changed concurrently;
* cash session changed;
* permission changed.

Conflict resolution must preserve:

* original event;
* conflict UUID;
* Branch context;
* resolution actor;
* resolution reason;
* final result.

---

# 38. Branch Deactivation

Before deactivating a Branch, the system must evaluate active operational state.

Examples:

* open Cash Session;
* unpaid Orders;
* pending Payments;
* pending synchronization;
* pending inventory operations.

The system should prevent unsafe deactivation or require an authorized controlled procedure.

Deactivation must not destroy historical data.

---

# 39. Branch Reactivation

A deactivated Branch may be reactivated if:

* Business is active;
* subscription permits the Branch;
* required configuration is valid;
* required authorization exists.

Reactivation preserves:

* Branch UUID;
* historical records;
* configuration history;
* employee history;
* inventory history;
* report history.

---

# 40. Branch Deletion

Normal Branch deletion should not be destructive.

The default behavior is:

```text
Active
  ↓
Inactive
  ↓
Archived
```

Permanent deletion is governed by Business-level Data Lifecycle and deletion rules.

Branch deletion must not be used to erase operational history.

---

# 41. Cross-Branch Data Integrity

The database must prevent incompatible references.

Examples:

```text
Order.business_id = Payment.business_id
Order.branch_id   = Payment.branch_id

CashSession.business_id = Branch.business_id
CashSession.branch_id   = Branch.id

InventoryTransaction.business_id = Branch.business_id
InventoryTransaction.branch_id   = Branch.id
```

Where PostgreSQL composite foreign keys are practical, they should be used.

---

# 42. Branch-Aware UUID References

UUID references do not replace scope validation.

A valid UUID from another Business is still unauthorized.

Therefore:

```text
UUID existence
      ≠
authorization
```

Every Branch-scoped operation must validate Business and Branch ownership.

---

# 43. Concurrency

Branch-scoped operations may occur concurrently.

The database must safely handle:

* two cashiers accepting orders;
* simultaneous stock consumption;
* concurrent payments;
* concurrent session operations;
* simultaneous configuration changes;
* employee assignment changes.

Branch isolation must not be implemented only as application filtering.

Core database constraints and transaction boundaries remain authoritative.

---

# 44. Indexing

Important indexes should support:

* Branch by Business;
* Branch by status;
* EmployeeBranch by Branch;
* Orders by Business + Branch + created time;
* Payments by Business + Branch;
* Cash Sessions by Business + Branch;
* Inventory by Business + Branch + Product;
* Reports by Business + Branch + period;
* Audit records by Business + Branch + timestamp;
* Notifications by Business + Branch + status.

Indexes must be validated against real query patterns.

---

# 45. Security

Branch data must be protected against:

* cross-Business access;
* cross-Branch access;
* manipulated Branch IDs;
* unauthorized Branch switching;
* stale offline authorization;
* unauthorized exports;
* unauthorized report access.

The frontend must never be considered a security boundary.

---

# 46. Database vs Application Responsibilities

### Database responsibilities

* Business → Branch foreign keys;
* Branch identity;
* uniqueness;
* lifecycle state;
* structural tenant consistency;
* Branch-aware relationships;
* referential integrity.

### Application responsibilities

* Branch authorization;
* employee Branch access;
* subscription Branch limits;
* Branch switching;
* Branch-level permissions;
* operational eligibility;
* deactivation workflow;
* effective configuration.

---

# 47. Recommended Logical Entity Set

```text
Business
   │
   ├── Branch
   │    ├── Warehouse
   │    ├── CashRegister
   │    ├── BranchProduct
   │    ├── BranchConfiguration
   │    └── EmployeeBranch
   │
   └── Employee
```

Operational domains reference Branch through explicit UUID relationships.

---

# 48. Core Invariants

The following invariants are mandatory:

1. Every Branch belongs to exactly one Business.
2. Branch UUID is immutable.
3. Branch UUID is never reused.
4. Branch name is not the primary identity.
5. Branch code is not the primary identity.
6. Branch code uniqueness is Business-scoped where enabled.
7. An Employee may belong to multiple Branches.
8. Employee Branch assignments are explicit.
9. Branch permissions are scope-aware.
10. Branch A permissions do not automatically apply to Branch B.
11. Trusted devices do not grant Branch permissions.
12. Branch switching requires authorization.
13. Every Branch-scoped operational transaction identifies its Branch.
14. Every Branch-scoped transaction belongs to the same Business as its Branch.
15. Cross-Business Branch references are forbidden.
16. Orders belong to one Branch.
17. Payments belong to the same Branch as their Order.
18. Cash Registers belong to one Branch.
19. Cash Sessions belong to one Branch.
20. Inventory belongs to a Branch operational context.
21. Branch stock is not implicitly Business-global.
22. Branch menu availability does not delete global Products.
23. Branch price overrides do not modify the global Product price.
24. Open Orders preserve price snapshots.
25. Branch configuration is versioned.
26. Branch configuration changes do not rewrite historical transactions.
27. Branch reports contain explicit scope.
28. Report versions are immutable.
29. Branch audit context is preserved where applicable.
30. Branch notifications respect recipient scope.
31. Offline operations contain Branch context.
32. Offline Branch events are server-validated.
33. Stale offline events cannot move data into another Branch.
34. Branch deactivation does not delete historical data.
35. Branch reactivation preserves Branch UUID.
36. Branch deletion follows controlled lifecycle rules.
37. Branch transfer is not a normal supported operation.
38. Subscription downgrade does not automatically delete Branches.
39. Exceeding a reduced Branch limit blocks new creation rather than destroying existing data.
40. Branch authorization cannot be bypassed by modifying the client-supplied Branch UUID.
41. Business scope must be validated before Branch scope.
42. Branch scope must be validated before Branch-scoped authorization.
43. Branch UUID existence does not imply Branch authorization.
44. Branch-specific configuration must have deterministic precedence.
45. Concurrent Branch operations must remain transactionally safe.
46. Branch database queries must use appropriate tenant/Branch indexes.
47. Historical actor and Branch references remain attributable after employee changes.
48. Branch reports must not expose unauthorized Branch data.
49. Branch audit records must preserve the Branch context of the original operation.
50. Permanent Branch data deletion is governed by Business data lifecycle rules.

---

## Related Documents

* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/08_Offline_Architecture.md`
* `docs/04_Architecture/10_Security_Architecture.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/README.md`
* `adr/ADR-001-Documentation-First.md`

