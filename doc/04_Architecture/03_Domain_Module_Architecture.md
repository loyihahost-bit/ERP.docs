# Domain Module Architecture

**Document ID:** ARCH-03
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/02_Application_Layer_Architecture.md`

---

## 1. Purpose

This document defines the technical module boundaries for the FastFood ERP domain model.

It translates the approved Domain Analysis into implementation-oriented modules while preserving:

* domain ownership;
* aggregate boundaries;
* cross-domain responsibilities;
* dependency direction;
* transaction boundaries;
* domain events;
* historical integrity;
* tenant isolation;
* branch isolation;
* offline and synchronization boundaries.

This document does not define database tables or concrete backend framework packages.

It defines which technical module owns which business responsibility.

---

# 2. Architectural Principle

Each domain module must have a clear responsibility.

A module:

* owns its domain state;
* enforces its domain invariants;
* exposes explicit application/domain contracts;
* does not directly modify another module's internal state;
* does not depend on another module's database tables as an implementation shortcut.

The preferred interaction is:

```text id="u2d7ka"
Module A
   ↓
Application Contract
   ↓
Module B
```

rather than:

```text id="j8p4qe"
Module A
   ↓
Direct Database Access
   ↓
Module B Tables
```

---

# 3. Domain Module Catalog

The architecture contains the following primary domain modules:

```text id="4x9q1b"
01. Business
02. Identity and Access
03. Subscription
04. Branch
05. Order
06. Cash
07. Inventory
08. Payment
09. Menu and Pricing
10. Kitchen
11. Employee and Payroll
12. Reporting
13. Notification
14. Audit
15. Synchronization
16. Data Lifecycle
17. Configuration
18. Device and Trust
```

These modules correspond to the approved Domain Analysis responsibilities.

---

# 4. Module Dependency Model

The architecture should maintain a controlled dependency graph.

A simplified model is:

```text id="q6r2mp"
Business
   │
   ├── Branch
   ├── Identity & Access
   ├── Subscription
   ├── Employee & Payroll
   ├── Configuration
   └── Device & Trust
            │
            ▼
        Order
       /     \
      ▼       ▼
Inventory   Payment
    │          │
    ▼          ▼
 Menu &       Cash
 Pricing
    │
    ▼
 Kitchen

Reporting
    ↑
Most Operational Domains

Notification
    ↑
Application / Domain Events

Audit
    ↑
Important State Changes

Synchronization
    ↔
Offline-Capable Domains

Data Lifecycle
    ↔
Business / Subscription / Data Ownership
```

This is a conceptual dependency model.

Actual implementation dependencies must follow the rules defined below.

---

# 5. Dependency Rules

The following rules are mandatory.

### Rule 1 — No Arbitrary Cross-Module Writes

A module must not directly update another module's internal state.

### Rule 2 — Explicit Contracts

Cross-module communication must use:

* application services;
* domain services;
* domain events;
* query interfaces;
* repositories through controlled abstractions.

### Rule 3 — No Circular Ownership

Two modules must not mutually own the same state.

### Rule 4 — Single Owner

Every important state has one authoritative domain owner.

### Rule 5 — Snapshot Where Required

Historical transactions should use snapshots rather than depending on mutable current configuration.

### Rule 6 — Events for Secondary Effects

Notifications, printing, heavy reporting, and similar secondary operations should normally use events or background jobs.

### Rule 7 — Strong Consistency Only Where Required

Not every cross-module operation requires one transaction.

### Rule 8 — Tenant Context Is Mandatory

Every Business-owned module must respect Business isolation.

### Rule 9 — Branch Context Is Explicit

Branch-scoped modules must enforce Branch scope.

### Rule 10 — Infrastructure Is Not a Domain

Database, queue, cache, printer, and external services must not become domain owners.

---

# 6. Business Module

## 6.1. Responsibility

The Business module owns the tenant-level business entity.

It represents:

* Business identity;
* Business lifecycle metadata;
* Business-level settings;
* business ownership relationship;
* business-level operational context.

## 6.2. Owns

```text id="q4v1m7"
Business
Business Status
Business Metadata
Business Identity
```

## 6.3. Does Not Own

The Business module does not own:

* employees;
* permissions;
* subscription;
* Branch operations;
* orders;
* payments;
* inventory.

Those belong to their respective modules.

## 6.4. Dependencies

Business is a foundational module.

Other modules may reference Business identity but must not modify Business state directly.

---

# 7. Identity and Access Module

## 7.1. Responsibility

This module owns identity and authorization concepts.

It manages:

* employee identity;
* role assignment;
* permission assignment;
* permission overrides;
* access scope.

## 7.2. Owns

```text id="9m7x3a"
Identity
Role
Permission
Role Assignment
Employee Permission Override
Access Scope
```

## 7.3. Does Not Own

It does not own:

* subscription entitlement;
* device trust;
* employee payroll;
* Branch configuration.

Those remain separate concerns.

## 7.4. Authorization Contract

Other modules request authorization through an explicit contract.

Example:

```text id="2q8n6c"
Can Employee X
perform Operation Y
within Branch Z?
```

The Identity module returns an authorization decision.

---

# 8. Subscription Module

## 8.1. Responsibility

The Subscription module owns commercial entitlement.

It manages:

* tariffs;
* subscriptions;
* feature entitlement;
* limits;
* subscription state;
* expiry;
* grace period;
* downgrade;
* reactivation eligibility.

## 8.2. Owns

```text id="c6p2z9"
Tariff
Subscription
Entitlement
Subscription Limit
Subscription Lifecycle
```

## 8.3. Important Boundary

Subscription entitlement is not the same as permission.

The effective authorization is determined by multiple boundaries:

```text id="x7m4q2"
Permission
+
Branch Scope
+
Subscription Entitlement
+
Device Trust
```

---

# 9. Branch Module

## 9.1. Responsibility

The Branch module owns Branch identity and lifecycle.

It manages:

* Branch identity;
* Branch status;
* Business-to-Branch relationship;
* Branch metadata.

## 9.2. Owns

```text id="4f8m2x"
Branch
Branch Status
Branch Metadata
```

## 9.3. Does Not Own

Branch does not own:

* Branch inventory;
* Branch cash;
* Branch orders;
* Branch employees.

Those are owned by their respective domains but reference Branch.

---

# 10. Order Module

## 10.1. Responsibility

The Order module owns operational order state.

It manages:

* order identity;
* order lifecycle;
* order items;
* table context;
* waiter context;
* order type;
* order status;
* order relationships.

## 10.2. Owns

```text id="p8w3n6"
Order
Order Item
Order Status
Order Context
Table Visit / Order Grouping
Order Snapshot
```

## 10.3. Lifecycle

```text id="m4v7z2"
Draft
  ↓
Accepted
  ↓
Preparing
  ↓
Ready
  ↓
Served
```

Payment does not own the operational order lifecycle.

---

# 11. Order Module Dependencies

Order may interact with:

```text id="k7m2p8"
Order
 ├── Identity & Access
 ├── Branch
 ├── Configuration
 ├── Menu & Pricing
 ├── Inventory
 ├── Kitchen
 ├── Payment
 ├── Cash
 ├── Audit
 └── Synchronization
```

However, Order remains the owner of Order state.

---

# 12. Inventory Module

## 12.1. Responsibility

The Inventory module owns stock state and inventory transactions.

It manages:

* warehouses;
* stock quantities;
* stock movements;
* purchases;
* adjustments;
* production;
* inventory discrepancies.

## 12.2. Owns

```text id="s6r4w9"
Warehouse
Stock
Stock Movement
Purchase
Inventory Adjustment
Production
Inventory Discrepancy
```

## 12.3. Critical Rule

No other module may directly modify stock quantities.

All stock changes must pass through Inventory operations.

---

# 13. Inventory and Order Boundary

Order acceptance may request an inventory deduction.

Conceptually:

```text id="m7q3x1"
Order
   ↓
Inventory
   ↓
Validate Stock
   ↓
Deduct Stock
   ↓
Return Result
```

The Application Layer coordinates the transaction.

Inventory remains the authoritative owner of stock.

---

# 14. Menu and Pricing Module

## 14.1. Responsibility

This module owns business-facing product/menu configuration.

It manages:

* products;
* categories;
* recipes;
* Sets;
* menu availability;
* prices;
* Branch price overrides;
* configuration versions.

## 14.2. Owns

```text id="v2x7m5"
Product
Category
Recipe
Recipe Version
Set
Set Version
Menu Entry
Price
Price Version
Branch Price Override
```

## 14.3. Important Distinction

Menu and Pricing owns **configuration**.

Inventory owns **physical stock**.

Order owns **transactional order state**.

Payment owns **financial settlement**.

---

# 15. Recipe Ownership

Recipes belong to Menu and Pricing from an architectural ownership perspective.

Recipe changes:

* are versioned;
* require required approval;
* preserve history;
* have defined effective boundaries.

Inventory consumes recipe information to calculate stock requirements but does not own recipe definitions.

---

# 16. Set Ownership

Sets are owned by Menu and Pricing.

A Set contains stable product composition.

Underlying product recipe changes do not silently change the Set configuration.

Set changes create a new configuration/version according to the configuration rules.

---

# 17. Configuration Module

## 17.1. Responsibility

Configuration is a cross-cutting domain for operational configuration that is not itself an operational transaction.

It manages:

* Branch settings;
* Business settings;
* printer routing;
* notification thresholds;
* configurable operational parameters;
* configuration versions;
* effective configuration.

## 17.2. Owns

```text id="h3q8m1"
Configuration
Configuration Version
Configuration Scope
Configuration Activation
Configuration History
```

## 17.3. Configuration vs Menu

Menu and Pricing owns product-specific commercial configuration.

Configuration owns broader system/Business/Branch operational configuration.

---

# 18. Kitchen Module

## 18.1. Responsibility

Kitchen owns kitchen operational workflow.

It manages:

* kitchen tickets;
* preparation state;
* kitchen routing;
* printer routing;
* kitchen-specific status.

## 18.2. Owns

```text id="q9m4z7"
Kitchen Ticket
Kitchen Status
Kitchen Routing
Print Job Reference
```

## 18.3. Important Boundary

Kitchen does not own the financial Order.

Order remains the source of truth for the customer order.

Kitchen receives operational information from Order.

---

# 19. Printing Boundary

Physical printers are infrastructure.

The Kitchen module owns the logical print requirement.

Infrastructure owns communication with the physical printer.

```text id="n5x2p7"
Kitchen
   ↓
Print Job
   ↓
Printing Infrastructure
   ↓
Physical Printer
```

---

# 20. Payment Module

## 20.1. Responsibility

Payment owns financial settlement records associated with orders.

It manages:

* payment;
* payment portions;
* payment status;
* payment revisions;
* payment corrections.

## 20.2. Owns

```text id="w8m3q6"
Payment
Payment Portion
Payment Revision
Payment State
```

## 20.3. Payment Methods

Supported methods:

* Cash;
* Card;
* Debt;
* Mixed.

---

# 21. Payment and Cash Boundary

Payment owns the payment record.

Cash owns the physical cash session.

For cash payment:

```text id="z6q4m2"
Payment
   ↓
Cash Session
   ↓
Physical Cash
```

Payment does not directly own cash session state.

Cash does not own the complete payment record.

---

# 22. Debt Boundary

Debt is part of the Payment domain responsibility.

The Payment module owns:

* debt balances;
* debt orders;
* repayment;
* payment allocation.

Customer identity required for debt must remain limited to the approved debt model.

There is no full CRM/customer domain in the current scope.

---

# 23. Refund Boundary

Refunds are financial operations associated with Payment.

Refund processing belongs to the Payment domain boundary.

Refunds:

* preserve original payment;
* create a separate financial operation;
* require permission;
* require reason;
* do not automatically return inventory.

---

# 24. Cash Module

## 24.1. Responsibility

Cash owns physical cash operations.

It manages:

* Cash Register;
* Cash Session;
* opening;
* closing;
* physical count;
* difference;
* corrections;
* handover.

## 24.2. Owns

```text id="b4m8x1"
Cash Register
Cash Session
Cash Count
Cash Difference
Cash Correction
Cash Handover
```

---

# 25. Cash Session Boundary

Cash Session is a major operational aggregate boundary.

The architecture must preserve:

```text id="x4m7q8"
Branch
  ↓
Cash Register
  ↓
Cash Session
```

A closed Cash Session cannot be reopened as an active session.

A correction creates a separate correction operation.

---

# 26. Employee and Payroll Module

## 26.1. Responsibility

This module owns employee operational and payroll information.

It manages:

* employee profile;
* employment status;
* attendance;
* salary configuration;
* payroll;
* bonuses;
* payroll finalization.

## 26.2. Owns

```text id="p2m9x5"
Employee
Employment Status
Attendance
Salary Configuration
Payroll Period
Payroll Calculation
Payroll Correction
```

Identity and Access remains responsible for permissions.

Employee and Payroll remains responsible for employment and payroll.

---

# 27. Identity vs Employee Boundary

The architecture must distinguish:

```text id="v8q3m6"
Identity & Access
→ Can this person perform an operation?

Employee & Payroll
→ What is this person's employment/payroll state?
```

The same employee identifier may be referenced by both modules.

Neither module should duplicate ownership of the employee's complete state.

---

# 28. Reporting Module

## 28.1. Responsibility

Reporting owns report definitions, generation state, versions, and exports.

It manages:

* report generation;
* report version;
* report snapshot;
* report history;
* Excel export jobs.

## 28.2. Owns

```text id="f7m2q9"
Report Definition
Report Instance
Report Version
Report Snapshot
Export Job
```

Reporting reads data from other domains but does not become the owner of their operational state.

---

# 29. Reporting Dependency Model

Reporting may consume data from:

```text id="q2m7x4"
Order
Payment
Cash
Inventory
Employee
Payroll
Configuration
Audit
Subscription
Branch
```

The data must be read through controlled query interfaces or optimized read models.

Reporting must not directly modify source-domain state.

---

# 30. Notification Module

## 30.1. Responsibility

Notification owns notification lifecycle.

It manages:

* notification;
* severity;
* recipient;
* read state;
* resolved state;
* retry state.

## 30.2. Owns

```text id="m5x8q2"
Notification
Notification Recipient
Notification State
Notification Delivery Attempt
```

Notifications are generally triggered by application/domain events.

---

# 31. Audit Module

## 31.1. Responsibility

Audit owns immutable audit history.

It records important:

* state changes;
* corrections;
* permission changes;
* configuration changes;
* security events;
* synchronization conflict resolutions.

## 31.2. Owns

```text id="c7m2x8"
Audit Event
Audit Context
Audit Change Set
Audit Reference
```

Audit records must be immutable.

---

# 32. Audit as a Cross-Cutting Module

Audit is not the owner of the state being audited.

Example:

```text id="w4q9m1"
Order
  └── owns Order state

Audit
  └── records Order state changes
```

The same principle applies to:

* Payment;
* Inventory;
* Cash;
* Employee;
* Configuration;
* Device;
* Subscription.

---

# 33. Device and Trust Module

## 33.1. Responsibility

This module owns device identity and trust state.

It manages:

* Device UUID;
* registration;
* trust;
* revocation;
* Business/Branch association;
* security metadata.

## 33.2. Owns

```text id="s8m3q6"
Device
Device Trust
Device Registration
Device Revocation
Device Security Metadata
```

---

# 34. Device vs Authentication Boundary

Authentication identifies the employee.

Device and Trust identifies the device.

Therefore:

```text id="n7q2m5"
Employee Authentication
        +
Device Trust
        ↓
Secure Operational Context
```

Neither one replaces the other.

---

# 35. Synchronization Module

## 35.1. Responsibility

Synchronization owns synchronization infrastructure and state.

It manages:

* sync events;
* sync queue;
* sync attempts;
* sync state;
* conflict records;
* conflict lifecycle.

## 35.2. Owns

```text id="x5m8q2"
Sync Event
Sync Batch
Sync Attempt
Sync Queue Entry
Sync Conflict
Sync Result
```

---

# 36. Synchronization Does Not Own Business Transactions

Synchronization transports and coordinates offline transactions.

It does not become the owner of:

* orders;
* payments;
* inventory;
* cash;
* employee state.

For example:

```text id="m4q7x8"
Sync
   ↓
Accept Order Use Case
   ↓
Order + Inventory
```

rather than:

```text id="a2z9m5"
Sync
   ↓
Directly modify Order table
```

---

# 37. Data Lifecycle Module

## 37.1. Responsibility

Data Lifecycle owns Business lifecycle and controlled deletion workflows.

It manages:

* lifecycle state;
* deletion eligibility;
* deletion jobs;
* deletion progress;
* deletion failures;
* reactivation protection.

## 37.2. Owns

```text id="p6m3x8"
Business Lifecycle
Deletion Request
Deletion Job
Deletion State
Deletion History
```

---

# 38. Data Lifecycle and Business Boundary

Business owns Business identity.

Data Lifecycle owns lifecycle processing.

Therefore:

```text id="v8m2q5"
Business
→ Business Identity

Data Lifecycle
→ Business Lifecycle Process
```

The Business UUID remains stable throughout the lifecycle until permanent deletion.

---

# 39. Module Ownership Matrix

The following high-level ownership must be preserved:

| Concern                      | Owner              |
| ---------------------------- | ------------------ |
| Business identity            | Business           |
| Employee identity/access     | Identity & Access  |
| Subscription                 | Subscription       |
| Branch identity              | Branch             |
| Orders                       | Order              |
| Stock                        | Inventory          |
| Products/recipes/Sets/prices | Menu & Pricing     |
| Kitchen workflow             | Kitchen            |
| Payments/debt/refunds        | Payment            |
| Cash sessions                | Cash               |
| Employment/payroll           | Employee & Payroll |
| Reports                      | Reporting          |
| Notifications                | Notification       |
| Audit history                | Audit              |
| Device trust                 | Device & Trust     |
| Synchronization state        | Synchronization    |
| Business deletion lifecycle  | Data Lifecycle     |
| Operational configuration    | Configuration      |

---

# 40. Aggregate Ownership

Each major aggregate must have one authoritative owner.

Examples:

```text id="c4m8q1"
Order Aggregate
→ Order Module

Cash Session Aggregate
→ Cash Module

Payment Aggregate
→ Payment Module

Inventory Aggregate
→ Inventory Module

Recipe Aggregate
→ Menu & Pricing Module

Device Aggregate
→ Device & Trust Module

Subscription Aggregate
→ Subscription Module
```

Other modules may reference these aggregates but must not own duplicate authoritative copies.

---

# 41. Cross-Domain References

Cross-domain references should generally use stable identifiers.

Examples:

```text id="n2q7m5"
Order
→ Employee UUID
→ Branch UUID
→ Device UUID
→ Cash Session UUID
→ Product UUID
```

The Order module does not need to duplicate the complete Employee or Device aggregate.

Historical snapshots may be stored where required for historical integrity.

---

# 42. Historical Snapshots

Mutable domain configuration must not be required to reconstruct historical transactions.

For example, an Order may preserve relevant:

* product name;
* price;
* quantity;
* configuration version;
* recipe/version reference;
* discount information.

This allows historical reporting even after current configuration changes.

---

# 43. Configuration Snapshot Boundary

Operational transactions should reference the configuration version used at the time of execution.

Example:

```text id="f8m2q6"
Order
 ├── Product
 ├── Price Snapshot
 ├── Recipe Version
 └── Configuration Version
```

This prevents later configuration changes from rewriting historical transactions.

---

# 44. Domain Events

Modules may publish domain events for meaningful state changes.

Examples:

```text id="x7q3m9"
OrderAccepted
PaymentCompleted
CashSessionClosed
InventoryAdjusted
RecipeApproved
PriceChanged
SubscriptionExpired
DeviceRevoked
BusinessDeletionStarted
```

Events must contain stable identifiers.

---

# 45. Event Ownership

The event producer owns the meaning of the event.

For example:

```text id="r6m2x8"
Order Module
   ↓
OrderAccepted
```

The Notification module may consume the event.

The Reporting module may consume the event.

The Audit module may consume the event.

But neither consumer becomes the owner of Order state.

---

# 46. Strong Consistency Boundaries

The following operations require strong consistency:

### Order + Inventory

```text id="m8q2x4"
Accept Order
+
Deduct Inventory
```

### Payment

```text id="q6m3x8"
Create Payment
+
Update Financial State
```

### Cash Session

```text id="x2m7q5"
Close Cash Session
+
Record Cash Difference
```

### Inventory Adjustment

```text id="p4q8m1"
Validate Stock
+
Apply Adjustment
```

### Critical Configuration Activation

Where an activation boundary affects an immediate operational transaction, activation must be atomic.

---

# 47. Eventual Consistency Boundaries

The following are normally eventually consistent:

* notifications;
* printer jobs;
* heavy reports;
* large exports;
* background synchronization;
* cleanup;
* non-critical background processing.

The exact consistency requirement is defined by each workflow.

---

# 48. Cross-Domain Transaction Example

Order acceptance:

```text id="j7m3q8"
Application Service
       │
       ├── Identity & Access
       ├── Subscription
       ├── Configuration
       ├── Order
       └── Inventory
              │
              ▼
           Commit
              │
              ▼
       Secondary Events
          ├── Kitchen
          ├── Printing
          ├── Notification
          └── Audit
```

The Application Layer coordinates the operation.

No individual module becomes the owner of the complete workflow.

---

# 49. Payment Transaction Example

```text id="k5q2m8"
Application Service
       │
       ├── Identity & Access
       ├── Subscription
       ├── Order
       ├── Payment
       └── Cash
              │
              ▼
           Commit
              │
              ▼
       Secondary Effects
```

Payment remains the owner of the payment record.

Cash remains the owner of physical cash session state.

---

# 50. Inventory Transaction Example

```text id="m7x3q1"
Application Service
       │
       ├── Identity & Access
       ├── Inventory
       ├── Menu & Pricing
       └── Configuration
              │
              ▼
           Commit
```

Inventory owns stock movement.

Menu & Pricing supplies product/recipe information.

---

# 51. Circular Dependency Prevention

The architecture must avoid cycles such as:

```text id="q4m8x2"
Order → Payment → Order → Payment
```

Instead, cross-domain workflows should be coordinated by the Application Layer.

Example:

```text id="v7m2q9"
Application Service
      ├── Order
      └── Payment
```

This keeps domain ownership clear.

---

# 52. Shared Kernel Policy

A minimal shared kernel may contain only genuinely universal technical/domain primitives.

Examples may include:

* UUID value types;
* money representation;
* percentage representation;
* date/time abstractions;
* Business ID;
* Branch ID;
* Employee ID;
* Device ID;
* Transaction ID.

The shared kernel must remain intentionally small.

Business-specific logic must not be placed into the shared kernel merely for convenience.

---

# 53. Common Infrastructure vs Domain Shared Code

Technical utilities such as:

* logging;
* serialization;
* database transaction handling;
* cryptography;
* queue adapters;

belong to Infrastructure/Common technical libraries.

They must not become a place for arbitrary business rules.

---

# 54. Domain Service Policy

A domain service should be introduced when:

* a rule belongs to a domain;
* the rule does not naturally belong to one aggregate;
* the operation requires multiple entities within the same domain.

Cross-domain orchestration should normally remain in the Application Layer.

---

# 55. Repository Ownership

Repositories belong conceptually to the module whose aggregate they persist.

Example:

```text id="x3m7q2"
Order Module
   └── OrderRepository

Inventory Module
   └── InventoryRepository

Payment Module
   └── PaymentRepository
```

A module must not use another module's repository to bypass its public application/domain contract.

---

# 56. Query Ownership

Read queries should be owned by the module responsible for the information.

For example:

```text id="m8q2x7"
Order Query
→ Order Module

Inventory Query
→ Inventory Module

Cash Session Query
→ Cash Module
```

Composite dashboards may use a dedicated Reporting query layer.

---

# 57. Reporting as a Composite Consumer

Reporting is allowed to aggregate information from multiple domains.

For example:

```text id="q5m7x2"
Branch Performance
      │
      ├── Orders
      ├── Payments
      ├── Cash
      ├── Inventory
      └── Payroll
```

Reporting must consume data without becoming the owner of source-domain state.

---

# 58. Notification as an Event Consumer

Notification should normally consume events.

Example:

```text id="x8m3q6"
Cash Difference Detected
          ↓
Notification
          ↓
Owner / Authorized Recipient
```

Notification does not directly inspect and mutate Cash state.

---

# 59. Audit as an Event Consumer

Audit may consume important events.

Example:

```text id="m2q7x8"
PriceChanged
    ↓
Audit
```

For critical transactional operations, audit persistence may also be included within the core transaction where required.

---

# 60. Synchronization as an Application Boundary

Synchronization may invoke application commands on behalf of an offline device.

Example:

```text id="q8m4x1"
Sync Event
   ↓
Resolve Use Case
   ↓
Application Command
   ↓
Domain Validation
   ↓
Transaction
```

The synchronization module must not bypass authorization or domain invariants.

---

# 61. Offline Domain Boundaries

Only domains explicitly supporting offline operation may process offline commands.

Potential offline-capable domains include:

* Order;
* Inventory;
* Payment;
* Cash;
* Attendance;
* selected Employee operations;
* selected Configuration reads;
* Synchronization.

Offline capability does not mean that the domain becomes independent from the server.

---

# 62. Tenant Isolation Across Modules

Every Business-owned module must enforce Business context.

Example:

```text id="c6m2q9"
Order.BusinessId
Inventory.BusinessId
Payment.BusinessId
Cash.BusinessId
Employee.BusinessId
```

Cross-domain operations must verify that referenced entities belong to the same Business unless the operation is explicitly platform-level.

---

# 63. Branch Isolation Across Modules

Branch-scoped entities must maintain Branch context.

Examples:

```text id="m8q3x7"
Order.BranchId
CashSession.BranchId
Inventory.BranchId
KitchenTicket.BranchId
Attendance.BranchId
```

Cross-Branch operations are allowed only where explicitly defined.

Current architecture does not introduce Branch Transfer as a normal operational workflow.

---

# 64. Security Boundary

Security is cross-cutting but does not become a domain owner.

Security concerns include:

* authentication;
* authorization;
* device trust;
* encryption;
* session security;
* audit;
* synchronization security.

Identity & Access owns authorization concepts.

Device & Trust owns device trust.

Audit owns historical security records.

Infrastructure owns cryptographic implementation.

---

# 65. Subscription Boundary

Subscription is cross-cutting but remains a separate domain.

Modules request entitlement information rather than directly implementing tariff logic.

Example:

```text id="v5m2q8"
Order
   ↓
Subscription Entitlement
   ↓
Allowed / Rejected
```

The Order module should not contain tariff definitions.

---

# 66. Data Lifecycle Boundary

When a Business enters deletion lifecycle:

```text id="x7q4m2"
Data Lifecycle
      ↓
Coordinate Deletion
      ↓
Business
Identity
Subscription
Branch
Order
Payment
Inventory
Audit
Reports
Notifications
Devices
Synchronization
```

Each module remains responsible for its own data cleanup behavior.

Data Lifecycle coordinates the overall process.

---

# 67. Module Failure Isolation

A failure in one secondary module must not unnecessarily stop another module.

Examples:

```text id="m3q8x7"
Notification Failure
≠
Order Failure
```

```text id="x2m7q4"
Printer Failure
≠
Kitchen State Failure
```

```text id="q6m3x8"
Report Failure
≠
Payment Failure
```

However, a required strong-consistency dependency may fail the complete transaction.

---

# 68. Module State Ownership Matrix

| Module             | Primary State           | Other Modules May Read | Other Modules May Directly Write |
| ------------------ | ----------------------- | ---------------------- | -------------------------------- |
| Business           | Business                | Yes                    | No                               |
| Identity & Access  | Roles/Permissions       | Yes                    | No                               |
| Subscription       | Entitlement             | Yes                    | No                               |
| Branch             | Branch                  | Yes                    | No                               |
| Order              | Orders                  | Yes                    | No                               |
| Inventory          | Stock                   | Yes                    | No                               |
| Menu & Pricing     | Products/Recipes/Prices | Yes                    | No                               |
| Kitchen            | Kitchen State           | Yes                    | No                               |
| Payment            | Payments/Debt/Refunds   | Yes                    | No                               |
| Cash               | Cash Sessions           | Yes                    | No                               |
| Employee & Payroll | Employment/Payroll      | Yes                    | No                               |
| Reporting          | Reports                 | Yes                    | No                               |
| Notification       | Notifications           | Yes                    | No                               |
| Audit              | Audit History           | Yes                    | No                               |
| Synchronization    | Sync State              | Yes                    | No                               |
| Data Lifecycle     | Lifecycle State         | Yes                    | No                               |
| Configuration      | Configuration           | Yes                    | No                               |
| Device & Trust     | Device Trust            | Yes                    | No                               |

The "No" in the final column means that another module must not bypass the owning module's contract to directly mutate its internal state.

---

# 69. Module Interface Types

Cross-module interaction may use:

### Command

For requesting a state-changing operation.

### Query

For retrieving information.

### Domain Event

For notifying other modules of meaningful state changes.

### Application Event

For completed application-level workflows.

### Domain Service

For rules within a domain.

### Shared Value Object

For genuinely universal values.

The architecture must choose the simplest suitable interaction mechanism.

---

# 70. Module Versioning

Module contracts should evolve carefully.

Changes affecting:

* event payloads;
* application commands;
* query contracts;
* synchronization contracts;

must preserve compatibility where required.

Breaking changes must be documented through ADRs and related implementation documentation.

---

# 71. Module Testing Boundaries

Each module should support isolated tests for:

* domain invariants;
* aggregate behavior;
* state transitions;
* authorization contracts;
* application use cases.

Cross-module integration tests must cover critical workflows.

Examples:

```text id="q4m7x2"
Order + Inventory
Order + Payment
Payment + Cash
Order + Kitchen
Subscription + Authorization
Device + Synchronization
Configuration + Order
Reporting + Operational Data
```

---

# 72. Architecture Rules for Developers

Developers should ask the following before modifying a domain module:

1. Which module owns this state?
2. Is this operation a command or query?
3. Does another module need to be involved?
4. Is the interaction synchronous or event-driven?
5. Does it require one transaction?
6. Is idempotency required?
7. Does Business scope apply?
8. Does Branch scope apply?
9. Does subscription entitlement apply?
10. Does the operation need audit?
11. Does the operation support offline execution?
12. Does historical integrity require a snapshot?

---

# 73. Domain Module Anti-Patterns

The following patterns are prohibited or strongly discouraged.

### 73.1. Shared Table Ownership

Two modules must not both claim ownership of the same authoritative state.

### 73.2. Direct Cross-Module Table Updates

A module must not modify another module's tables directly.

### 73.3. Circular Domain Dependencies

Domain A should not require Domain B while Domain B requires Domain A as a permanent architectural dependency.

### 73.4. God Module

A single module must not own unrelated business responsibilities.

### 73.5. Generic Shared Business Service

A common service containing arbitrary rules from many domains must not replace explicit domain ownership.

### 73.6. Hidden Event Side Effects

Events must have documented producers and consumers.

### 73.7. Duplicate State

A module must not maintain a second authoritative copy of another module's mutable state.

---

# 74. Future Microservice Extraction

The modular boundaries intentionally allow future extraction if operational requirements justify it.

Potential future candidates could include:

* Reporting;
* Synchronization;
* Notification;
* background processing.

However, extraction is not required by the current architecture.

The initial system should remain a modular application unless scale or operational requirements justify separate deployment.

---

# 75. Architectural Traceability

This document is derived from:

### Domain Analysis

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`
* `docs/03_Domain_Analysis/11_Kitchen_Domain.md`
* `docs/03_Domain_Analysis/12_Employee_and_Payroll_Domain.md`
* `docs/03_Domain_Analysis/13_Reporting_Domain.md`
* `docs/03_Domain_Analysis/14_Notification_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/18_Configuration_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### Previous Architecture

* `docs/04_Architecture/01_System_Architecture.md`
* `docs/04_Architecture/02_Application_Layer_Architecture.md`

---

# 76. Related Documents

### Next Architecture

* `docs/04_Architecture/04_Backend_Architecture.md`

### Supporting Architecture

* `docs/04_Architecture/06_API_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/08_Offline_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/10_Security_Architecture.md`
* `docs/04_Architecture/12_Event_and_Message_Architecture.md`

---

# 77. Final Status

**Status:** Accepted

This document establishes the technical domain module boundaries for FastFood ERP.

Each major business responsibility has a clear architectural owner, while cross-domain workflows are coordinated through the Application Layer.

The architecture intentionally preserves modularity without requiring premature microservice decomposition.

**Next document:**

`docs/04_Architecture/04_Backend_Architecture.md`

