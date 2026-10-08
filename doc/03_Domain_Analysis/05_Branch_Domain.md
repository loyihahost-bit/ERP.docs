# Branch Domain

**Document ID:** DA-05
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Branch domain represents a physical restaurant or fast-food location operating under a Business.

A Branch is an operational boundary within a Business.

This document defines:

* Branch identity;
* Branch ownership;
* Branch lifecycle;
* Branch configuration;
* operational scope;
* employee assignment;
* device relationship;
* cash relationship;
* inventory relationship;
* order relationship;
* branch-specific menu configuration;
* branch reporting scope;
* branch-level invariants.

This document does not define database tables or API endpoints.

---

# 2. Branch as an Operational Boundary

A Business may contain multiple Branches.

```text id="m4k1j9"
Business
   │
   ├── Branch A
   ├── Branch B
   ├── Branch C
   └── ...
```

Each Branch represents a separate operational environment.

Branch isolation applies to:

* employees where scoped;
* devices;
* cash;
* inventory;
* orders;
* menu availability;
* attendance;
* branch reports;
* branch notifications.

---

# 3. Branch Identity

Every Branch has a stable UUID.

The Branch UUID must remain unchanged during its lifetime.

It must not change because of:

* employee changes;
* menu changes;
* price changes;
* subscription renewal;
* device replacement;
* cash register replacement;
* configuration changes;
* synchronization.

A Branch UUID is unique within the Business and should be globally unique at the system level.

---

# 4. Branch Ownership

Every Branch belongs to exactly one Business.

```text id="w3b7qs"
Business UUID
      ↓
Branch UUID
```

A Branch cannot be shared between Businesses.

Ordinary operational workflows must not transfer a Branch from one Business to another.

If future business restructuring requires such functionality, it must be introduced as a separate controlled domain operation.

---

# 5. Branch Core Information

Conceptually, a Branch may contain:

```text id="g7h4qy"
Branch
├── UUID
├── Business UUID
├── Name
├── Status
├── Address / Location Information
├── Contact Information
├── Settings
├── Created At
├── Updated At
└── Lifecycle Metadata
```

Only branch-owned information should be stored directly on the Branch concept.

Operational transactions remain owned by their respective domains.

---

# 6. Branch Lifecycle

The Branch lifecycle must be distinct from:

* Business lifecycle;
* Subscription lifecycle;
* Employee lifecycle;
* Cash Session lifecycle;
* Device lifecycle.

A logical lifecycle is:

```text id="n4g9c1"
Created
   ↓
Active
   ↓
Inactive / Closed
```

The exact operational status model may be expanded later if business requirements require it.

---

# 7. Active Branch

An active Branch may participate in normal operations according to:

* Business subscription;
* employee authorization;
* branch configuration;
* device authorization;
* product/menu availability;
* inventory state;
* cash state.

Branch activation does not automatically grant access to employees.

---

# 8. Inactive Branch

An inactive Branch should not accept new normal operational transactions.

However, historical information remains available according to permissions.

The system must preserve:

* historical orders;
* payments;
* cash sessions;
* inventory movements;
* attendance;
* payroll;
* audit history;
* reports.

Deactivating a Branch must not destructively delete its history.

---

# 9. Branch and Subscription

Branch count is controlled by Subscription entitlement.

The domain model must not hard-code the initial maximum of 10 Branches.

Instead:

```text id="n1t5g6"
Create Branch
     ↓
Validate Business
     ↓
Validate Subscription Entitlement
     ↓
Validate Current Branch Usage
     ↓
Create Branch
```

If the subscription limit is reached, Branch creation is rejected.

---

# 10. Branch Downgrade Scenario

If a Business downgrades to a tariff with fewer allowed Branches than currently exist:

* existing Branches remain;
* no Branch is automatically deleted;
* new Branch creation is blocked;
* the Business is shown as exceeding the new entitlement;
* operations on existing Branches follow the entitlement policy.

The system must never silently delete Branches because of a subscription downgrade.

---

# 11. Branch Configuration

Branch configuration represents settings that are specific to the physical location.

Examples include:

* operational preferences;
* menu availability;
* branch-specific prices;
* printer routing;
* cash register configuration;
* inventory configuration;
* notification thresholds where permitted;
* equipment availability.

Business-level defaults may be inherited.

Branch-level configuration may override permitted Business-level defaults.

---

# 12. Configuration Hierarchy

Where applicable:

```text id="t0qj1r"
Platform Policy
      ↓
Business Configuration
      ↓
Branch Configuration
      ↓
Operational Transaction Snapshot
```

A transaction must use the configuration valid at the time the transaction becomes operational.

Historical transactions must not change because current Branch configuration changes.

---

# 13. Branch and Employees

An Employee belongs to the Business and may be assigned to one or multiple Branches.

```text id="w4x6h2"
Business
   │
   ├── Employee A
   │      ├── Branch 1
   │      └── Branch 2
   │
   └── Employee B
          └── Branch 1
```

Branch assignment is part of access scope.

The Identity and Access domain determines whether the Employee may operate in the Branch.

The Branch domain owns the Branch itself, not the Employee's permission logic.

---

# 14. Different Permissions per Branch

The same Employee may have different permissions in different Branches.

Example:

```text id="q1q4j9"
Employee A

Branch A → Manager
Branch B → Cashier
Branch C → No Access
```

The Branch domain provides the scope.

Identity and Access calculates the effective permissions.

---

# 15. Branch and Devices

Devices are associated with a Business and may be associated with a Branch.

A device context must identify the Branch in which it is authorized to operate.

Conceptually:

```text id="c8v4e5"
Business
   ↓
Branch
   ↓
Trusted Device
```

A trusted device must not be allowed to silently switch to another Branch without an authorized process.

---

# 16. Device Replacement

Replacing a device does not change:

* Branch identity;
* cash register identity;
* orders;
* inventory;
* employees;
* historical transactions.

The old device may be revoked and the new device registered.

Historical operations retain the original Device UUID.

---

# 17. Branch and Cash

Cash is branch-scoped.

The current model assumes one primary Cash Register per Branch.

```text id="g6p0zn"
Branch
   ↓
Cash Register
   ↓
Cash Sessions
```

The architecture must remain capable of supporting multiple registers in the future.

However, the current business model must not require multiple registers.

---

# 18. Branch and Cash Sessions

Every Cash Session belongs to one Branch.

A Cash Session must also preserve:

* Cash Register;
* Cashier;
* Device where applicable;
* opening state;
* closing state;
* handover context.

A Cash Session cannot belong to multiple Branches.

---

# 19. Branch and Orders

Every Order belongs to exactly one Branch.

Conceptually:

```text id="s0j7w1"
Business
   ↓
Branch
   ↓
Order
```

The Order domain owns the Order.

The Branch domain establishes the operational scope.

An Order cannot move between Branches as an ordinary edit.

---

# 20. Branch and Tables

Tables and halls are branch-scoped.

A table belongs to one Branch.

```text id="e4y7v2"
Branch
   ↓
Hall
   ↓
Table
```

A table cannot simultaneously belong to multiple Branches.

Table state is determined by its current operational orders.

---

# 21. Branch and Waiters

Waiters are employees with applicable permissions.

A waiter may be assigned to orders within authorized Branch scope.

Historical order attribution must preserve:

* primary waiter;
* additional waiter where applicable;
* Branch;
* actor;
* timestamps.

Changing an employee's current Branch assignment must not rewrite historical order attribution.

---

# 22. Branch and Inventory

Inventory is branch-scoped.

```text id="t2p7s9"
Business
   ↓
Branch
   ↓
Warehouse
   ↓
Inventory
```

A Branch may have one or more warehouses according to the inventory model.

Stock cannot silently appear in another Branch.

Branch transfer is currently out of scope.

---

# 23. Branch and Products

Products are Business-owned.

Branches determine whether an eligible product is available for sale.

Therefore:

```text id="x7r3f2"
Business Product
       ↓
Branch Menu Configuration
       ↓
Available for Sale
```

A Branch does not create a completely separate Product identity merely because it enables or disables the product.

---

# 24. Branch Menu Availability

A Branch may enable or disable a Business-owned product according to permissions.

If a product is disabled in a Branch:

* it should not appear in normal new-order selection;
* historical orders remain unchanged;
* existing open orders retain their snapshots;
* disabling does not delete the Product.

---

# 25. Branch Pricing

A Branch may override the Business-level standard price where authorized.

Conceptually:

```text id="h9n4p8"
Global Product Price
        ↓
Branch Price Override
        ↓
Active Branch Price
        ↓
Order Price Snapshot
```

Price changes follow the configured activation boundary.

Existing operational orders retain their applicable price snapshots.

---

# 26. Branch and Recipes

Recipes are Business-level concepts.

Branches use approved recipe versions according to the Business menu/configuration.

A Branch does not create an independent recipe merely because it uses the product.

Recipe changes become effective according to the defined configuration activation rules.

---

# 27. Branch and Inventory Consumption

When an accepted Order consumes inventory:

```text id="7r1b2h"
Branch Order
    ↓
Product / Recipe
    ↓
Branch Inventory
    ↓
Stock Deduction
```

The inventory deduction must occur within the appropriate atomic transaction boundary.

Stock from another Branch must not be consumed accidentally.

---

# 28. Branch and Payments

Payments are associated with the Branch through the Order and operational context.

Branch scope must be preserved for:

* payment;
* refund;
* debt;
* overpayment;
* payment correction.

Financial reports must not combine Branch data outside the requested scope.

---

# 29. Branch and Debt

Debt customer records are Business-owned according to the current model.

Debt orders and allocations retain their Branch context.

Therefore the system may distinguish:

```text id="m3n5q7"
Business
   ↓
Debt Customer
   ├── Branch A Debt Order
   ├── Branch B Debt Order
   └── Branch A Repayment
```

Branch-scoped users may only access debt information permitted by their scope.

---

# 30. Branch and Attendance

Attendance is branch-aware.

Employee attendance must preserve:

* Employee;
* Branch;
* date/time;
* attendance event;
* source/device where applicable.

If an Employee works in multiple Branches, attendance remains associated with the actual Branch context.

---

# 31. Branch and Payroll

Payroll may be Business-managed or Branch-scoped according to the configured employee/payroll model.

Where a payroll record is branch-scoped, its Branch context must remain explicit.

Historical payroll snapshots must preserve the applicable Branch context.

---

# 32. Branch and Reports

Reports may be:

* Business-wide;
* Branch-specific;
* multi-Branch within the same Business.

A Branch report must contain only authorized Branch data.

A user with access to Branch A must not automatically see Branch B data.

Business-wide reports require the appropriate Business-level permission.

---

# 33. Branch and Notifications

Notifications may be Branch-scoped.

Examples:

* low stock;
* stock-out;
* cash discrepancy;
* inventory variance;
* branch loss;
* printer failure;
* branch operational issue.

A Branch notification must be visible only to authorized recipients.

---

# 34. Branch and Audit

Important Branch changes must be auditable.

Examples:

* Branch created;
* Branch activated;
* Branch deactivated;
* Branch configuration changed;
* Branch menu changed;
* Branch price override changed;
* Branch device registered;
* Branch device revoked;
* Branch-level permission changed.

Audit events preserve the Branch UUID.

---

# 35. Branch Switching

An authorized employee may switch between accessible Branches.

Branch switching must:

1. Validate the Business.
2. Validate Branch access.
3. Recalculate effective permissions.
4. Load applicable Branch configuration.
5. Load applicable menu/pricing state.
6. Establish correct operational context.
7. Apply device restrictions where required.

Branch switching must not modify historical transactions.

---

# 36. Active Branch Context

The currently selected Branch is an operational context.

It is not a replacement for authorization.

The server must validate the active Branch on every protected operation.

The client may display a selected Branch, but the server remains authoritative.

---

# 37. Branch and Offline Operation

Offline authorization is Branch-bound.

A trusted device may operate offline only within its authorized Branch scope.

Offline operations must preserve:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* transaction UUID.

An offline device must not locally change Branch scope.

---

# 38. Offline Branch Switching

Branch switching while offline is allowed only when the device has valid offline authorization for the target Branch.

If the device does not have valid authorization for the target Branch:

* switching is rejected;
* no Branch-scoped operation is allowed.

When reconnecting, the server revalidates the Branch context.

---

# 39. Branch and Synchronization

Every synchronized event must be validated against its original Branch.

The server must verify:

```text id="j5h2v8"
Business matches
        +
Branch belongs to Business
        +
Employee authorized for Branch
        +
Device authorized for Branch
        +
Referenced resources belong to Branch
```

Cross-Branch synchronization errors must become explicit conflicts or rejections according to the operation.

---

# 40. Branch Concurrency

Branch operations may occur concurrently.

Examples:

* two employees creating orders;
* two devices accessing the same table;
* order acceptance while inventory changes;
* cash handover while a payment is submitted;
* menu configuration update while an order is being created.

Concurrency control belongs to the appropriate operational domain, while Branch provides the scope.

---

# 41. Branch Deactivation

Branch deactivation must preserve historical information.

After deactivation:

* new operational actions are blocked;
* existing history remains available;
* reports remain accessible according to permission;
* audit history remains available;
* synchronization of valid historical events follows lifecycle rules.

The exact treatment of already-open orders or sessions must follow the relevant Order and Cash domain rules.

---

# 42. Branch Aggregate Boundary

The Branch must not become a giant aggregate containing:

* all Orders;
* all Inventory;
* all Employees;
* all Payments;
* all Reports.

These remain separate aggregates.

Branch is an operational ownership and scope boundary.

---

# 43. Domain Services

Potential Branch domain services include:

```text id="6q0c4p"
Branch Creation Service
Branch Activation Service
Branch Deactivation Service
Branch Configuration Service
Branch Context Resolver
Branch Access Context Service
```

These are logical services and do not imply separate deployment.

---

# 44. Domain Events

Potential Branch events include:

```text id="m0j6s4"
BranchCreated
BranchActivated
BranchDeactivated
BranchConfigurationChanged
BranchMenuConfigurationChanged
BranchPriceConfigurationChanged
BranchDeviceContextChanged
BranchOperationalStateChanged
```

Events represent facts.

The Branch state remains authoritative.

---

# 45. Branch Invariants

### Identity

1. Every Branch has one stable UUID.
2. Every Branch belongs to exactly one Business.
3. Branch identity never changes during its lifecycle.
4. A Branch cannot be shared between Businesses.

### Subscription

5. Branch creation requires sufficient subscription entitlement.
6. Branch count limits come from Subscription.
7. Downgrade does not silently delete existing Branches.
8. Exceeding a new Branch limit blocks additional creation.

### Scope

9. Branch-scoped data must belong to exactly one Branch.
10. Cross-Branch access requires explicit authorization.
11. Client-selected Branch context is never trusted without server validation.
12. Branch switching requires valid access.

### Employees

13. Employee Branch assignment is independent from Employee identity.
14. The same Employee may access multiple Branches.
15. Different permissions may apply in different Branches.
16. Branch changes do not rewrite historical employee attribution.

### Orders

17. Every Order belongs to one Branch.
18. Orders cannot silently move between Branches.
19. Historical Orders retain their original Branch.

### Cash

20. Every Cash Session belongs to one Branch.
21. A Cash Register belongs to one Branch in the current model.
22. Closed Cash Sessions remain historical.

### Inventory

23. Inventory is Branch-scoped.
24. Stock cannot silently cross Branch boundaries.
25. Branch transfer is not part of the current domain scope.

### Menu and Pricing

26. Products are Business-owned.
27. Branch availability is separately configurable.
28. Branch price overrides do not change the global product price.
29. Historical order price snapshots remain unchanged.

### Offline

30. Offline authorization is Branch-bound.
31. Offline devices cannot invent new Branch access.
32. Offline events retain their original Branch UUID.
33. Synchronization validates Branch ownership and authorization.

### Historical Integrity

34. Branch deactivation does not delete historical data.
35. Historical reports retain their original Branch scope.
36. Audit events preserve Branch context.

### Security

37. Cross-Business Branch access is forbidden.
38. Unauthorized Branch switching is forbidden.
39. Branch scope must be enforced server-side.
40. Branch scope cannot be used to bypass subscription or employee permissions.

---

# 46. Completion Criteria

The Branch domain is considered complete when:

* Branch identity is defined;
* Business ownership is defined;
* Branch lifecycle is defined;
* subscription limits are defined;
* employee scope is defined;
* device scope is defined;
* cash relationship is defined;
* order relationship is defined;
* inventory relationship is defined;
* menu and pricing relationship is defined;
* reporting scope is defined;
* offline behavior is defined;
* synchronization behavior is defined;
* deactivation behavior is defined;
* aggregate boundaries are clear;
* branch invariants are documented.

---

## Related Documents

### Previous

* `docs/03_Domain_Analysis/README.md`
* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`

### Business Analysis

* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`

### Future

* `docs/04_Architecture/`

