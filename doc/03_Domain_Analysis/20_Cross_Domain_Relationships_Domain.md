# Cross-Domain Relationships Domain

**Document ID:** DA-20
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/README.md`

## 1. Purpose

The Cross-Domain Relationships Domain defines how the major FastFood ERP domains interact without merging their responsibilities.

The system contains multiple independent business domains, including:

* Business;
* Identity and Access;
* Subscription;
* Branch;
* Device and Trust;
* Order;
* Cash;
* Inventory;
* Payment;
* Menu and Pricing;
* Kitchen;
* Employee and Payroll;
* Reporting;
* Notification;
* Audit;
* Synchronization;
* Data Lifecycle;
* Configuration.

Each domain owns its own business concepts and invariants.

Cross-domain relationships must therefore be explicit, deterministic, auditable, and resistant to partial failure.

This document defines the logical relationship model.

It does not define the final implementation architecture, database schema, API contracts, or infrastructure.

---

# 2. Core Principle

A domain must own its own state.

Another domain may:

* reference that state;
* request an operation;
* validate a prerequisite;
* react to a domain event;
* create a related record.

A domain must not silently modify another domain's internal state.

Conceptually:

```text
Domain A
   │
   ├── Request
   ├── Reference
   └── Event
          ↓
Domain B
   │
   └── Owns its state and invariants
```

---

# 3. Domain Map

The high-level relationship is:

```text
                    Business
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   Subscription     Branch       Identity & Access
        │              │              │
        │              ├────── Device & Trust
        │              │
        │              ├────── Cash
        │              ├────── Inventory
        │              └────── POS
        │
        └────────── Entitlements

POS / Order
    │
    ├── Menu & Pricing
    ├── Inventory
    ├── Kitchen
    ├── Payment
    ├── Cash
    └── Reporting

Employee
    ├── Identity & Access
    ├── Attendance
    └── Payroll

All important state changes
    ├── Audit
    ├── Notification
    └── Reporting

Offline Operations
    └── Synchronization
           │
           └── All sync-capable domains

Business lifecycle
    └── Data Lifecycle
```

---

# 4. Business Domain Relationships

The Business Domain represents the tenant boundary.

It is the root context for most business-owned data.

Business is related to:

* Branch;
* Employee;
* Subscription;
* Device;
* Order;
* Cash;
* Inventory;
* Menu;
* Payment;
* Reporting;
* Notification;
* Audit;
* Configuration;
* Synchronization;
* Data Lifecycle.

Every business-owned entity must remain associated with exactly one Business context.

Cross-business references are prohibited unless explicitly defined as platform-level references.

---

# 5. Business and Subscription

The Subscription Domain determines what the Business is entitled to use.

Conceptually:

```text
Business
   ↓
Subscription
   ↓
Entitlements
   ↓
Allowed Operations
```

Subscription does not own business operational data.

It determines whether an operation is permitted.

For example:

```text
Order Creation
     ↓
Business Active?
     ↓
Subscription Entitlement?
     ↓
Employee Permission?
     ↓
Device Trust?
     ↓
Operation Allowed
```

Subscription expiry must not delete operational data immediately.

Data Lifecycle owns deletion behavior.

---

# 6. Business and Branch

The Branch Domain represents operational locations inside a Business.

A Business may contain multiple Branches.

Branch-owned operational entities include:

* orders;
* cash sessions;
* inventory;
* employees' branch assignments;
* menu availability;
* branch prices;
* printers;
* reports;
* expenses;
* operational configuration.

Branch isolation must remain enforceable across:

* application operations;
* reports;
* exports;
* offline storage;
* synchronization;
* audit;
* notifications.

---

# 7. Identity and Access Relationships

Identity and Access determines:

* who the employee is;
* what role they have;
* what permissions they have;
* which branches they may access.

Other domains consume authorization decisions but do not redefine permission semantics.

For example:

```text
Cash Domain
    ↓
"Can this employee close this Cash Session?"
    ↓
Identity & Access
```

The Cash Domain still owns the Cash Session business rules.

---

# 8. Identity, Device and Trust

Employee authentication and device trust are independent security dimensions.

```text
Employee
   ↓
Authentication
   +
Device
   ↓
Trust
```

An authenticated employee on an untrusted device may be blocked.

A trusted device used by an unauthorized employee must also be blocked.

The final operation requires both conditions where trusted-device operation is mandatory.

---

# 9. Subscription and Authorization

Subscription entitlement and employee permission are separate.

Conceptually:

```text
Employee Permission
        +
Subscription Entitlement
        +
Branch Scope
        +
Device Trust
        =
Effective Operational Authorization
```

Neither Subscription nor Identity and Access should absorb the other's responsibilities.

---

# 10. Order and Menu/Pricing

The Order Domain consumes valid menu and pricing configuration.

At order creation, relevant configuration is resolved.

An operational order stores the necessary price/configuration snapshot required for historical integrity.

Later price changes must not silently modify existing orders.

Conceptually:

```text
Menu / Pricing
      ↓
Configuration Snapshot
      ↓
Order
```

The Order Domain owns the order state.

The Menu and Pricing Domain owns the configuration.

---

# 11. Order and Inventory

Order and Inventory have one of the most important cross-domain relationships.

For an Accepted order:

```text
Order Acceptance
      ↓
Inventory Validation
      ↓
Inventory Deduction
      ↓
Order Accepted
```

The core transaction must preserve atomic business behavior.

If required inventory cannot be deducted:

* the order must not become Accepted;
* no partial deduction may remain;
* the failure must be explicit.

Inventory owns stock quantities.

Order owns order lifecycle.

---

# 12. Order and Kitchen

Kitchen consumes operational order information.

The relationship is:

```text
Order
   ↓
Accepted
   ↓
Kitchen Notification / Ticket
   ↓
Preparation
```

Kitchen processing must not become the owner of Order state.

Printer failure must not automatically roll back a successful ERP order transaction.

Kitchen printing is a secondary operational process.

---

# 13. Order and Payment

Order and Payment are separate domains.

Order determines whether an order is payment-eligible.

Payment records the financial operation.

```text
Order
   ↓
Payment Eligibility
   ↓
Payment
```

Payment completion does not automatically redefine the operational order lifecycle.

An order may remain in its operational state after payment.

---

# 14. Payment and Cash

Payment determines the financial payment method.

Cash determines physical cash-session accounting.

For Cash payment:

```text
Payment
   ↓
Cash Portion
   ↓
Cash Session
```

Card payments do not become physical cash.

Mixed payments may contain both:

* cash portion;
* card portion.

Cash Session owns physical cash reconciliation.

Payment owns payment records.

---

# 15. Payment and Debt

Debt is a payment-related business relationship.

A debt customer may have:

* multiple debt orders;
* partial repayments;
* remaining balance.

Payment records the financial transaction.

Debt allocation determines which debt orders or balances are affected.

Historical debt information must remain reconstructable.

---

# 16. Payment and Refund

Refund is a separate financial operation related to an original payment/order.

```text
Original Payment
      ↓
Refund
```

A refund must not overwrite the original payment.

The original financial record remains immutable.

Refund permissions and reasons are independently enforced.

Refund does not automatically return inventory.

---

# 17. Order and Cash Session

Order operations may occur within a Cash Session.

The relevant context includes:

* Branch;
* Employee;
* Device;
* Cash Register;
* Cash Session.

The Order UUID remains stable across cashier handover.

Historical actions retain the original actor and session context.

Later actions use the new cashier/session context after handover.

---

# 18. Cash and Employee

Cash operations are performed by authenticated employees.

The Cash Domain owns:

* opening;
* closing;
* physical cash count;
* discrepancy;
* correction;
* handover.

Identity and Access determines whether the employee is authorized to perform each action.

---

# 19. Cash and Device

Cash Sessions may reference the Device UUID used for operations.

Device trust is not owned by Cash.

Cash operations require valid device trust where offline or trusted-device rules apply.

Device revocation must not delete historical Cash Session data.

---

# 20. Inventory and Menu/Pricing

Menu and Pricing determines what products may be sold and at what configured price.

Inventory determines whether the required stock exists.

```text
Menu
  ↓
Product
  ↓
Recipe / Set
  ↓
Inventory Availability
```

A product may be visible in the menu but unavailable for sale when required stock is insufficient or the product is otherwise operationally unavailable.

---

# 21. Inventory and Recipes

Recipe configuration defines ingredient relationships.

Inventory executes stock effects.

For example:

```text
Raw Material
      ↓
Semi-Finished Product
      ↓
Finished Product
      ↓
Order
      ↓
Inventory Deduction
```

Recipe ownership remains separate from stock ownership.

---

# 22. Inventory and Configuration

Inventory behavior may depend on configuration such as:

* product availability;
* recipes;
* Set composition;
* yield;
* thresholds;
* branch availability.

Configuration changes must not silently rewrite historical inventory movements.

New configuration becomes effective according to the established configuration activation rules.

---

# 23. Menu, Pricing and Configuration

Configuration is the common mechanism for controlled business settings.

Menu and Pricing consumes configuration versions.

Relevant configuration may include:

* product state;
* category;
* price;
* branch override;
* recipe version;
* Set version;
* availability.

Configuration changes must preserve historical versions.

---

# 24. Employee and Payroll

Employee Domain provides employee identity and employment context.

Payroll uses employee information to calculate salary.

```text
Employee
   ↓
Attendance
   ↓
Payroll Calculation
   ↓
Payroll Snapshot
```

Payroll must not rewrite historical attendance.

Finalized payroll remains immutable.

Corrections create separate historical records.

---

# 25. Employee and Branch

Employees may work in multiple branches.

Branch assignment determines where an employee may operate.

Effective permissions may differ between branches.

Branch scope must therefore be evaluated together with Identity and Access.

---

# 26. Employee and Device

Employees may use multiple trusted devices.

A device may be shared by multiple authorized employees.

The relationship is therefore many-to-many over time rather than permanent ownership.

Every important operational transaction must identify the employee independently from the device.

---

# 27. Reporting Relationships

Reporting consumes information from operational domains.

Reports may depend on:

* Order;
* Payment;
* Cash;
* Inventory;
* Employee;
* Payroll;
* Configuration;
* Audit;
* Correction;
* Notification.

Reporting does not become the owner of operational state.

Reports represent consistent snapshots of source-domain information.

---

# 28. Report Versioning and Corrections

When a relevant correction changes report results:

```text
Original Data
     ↓
Report Version 1
     ↓
Correction
     ↓
Report Version 2
```

Version 1 remains immutable.

Reporting therefore depends on Audit and Correction information to explain why a later version differs.

---

# 29. Notification Relationships

Notifications are generated by significant business conditions or events.

Examples:

```text
Inventory → Low Stock
Cash → Discrepancy
Payment → Large Refund
Subscription → Expiry
Payroll → Salary Due
Data Lifecycle → Deletion Warning
```

Notification does not own the source condition.

It represents the notification state associated with that condition.

---

# 30. Notification and Permissions

A notification may only be visible to an employee who has access to the related Business/Branch information.

A notification must not become a security bypass.

Opening a notification deep-link must perform normal authorization checks again.

---

# 31. Audit Relationships

Audit receives important state-changing events from multiple domains.

Examples include:

* permission changes;
* payment corrections;
* cash corrections;
* inventory adjustments;
* configuration changes;
* device revocation;
* subscription transitions;
* conflict resolution;
* data lifecycle actions.

Audit does not own the source-domain business state.

It records historical evidence.

---

# 32. Audit and Historical Integrity

Operational domains retain their own historical state.

Audit provides cross-domain evidence.

Therefore:

```text
Operational History
        +
Audit History
        =
Reconstructable Business History
```

Audit records must not be used as a replacement for domain state.

---

# 33. Offline Domain Relationships

Offline operation crosses multiple domains.

Potential offline domains include:

* Order;
* Payment;
* Cash;
* Inventory;
* Attendance;
* Payroll;
* Configuration;
* Notification;
* Audit.

The Offline Domain does not become the owner of those business objects.

It provides the execution and storage model required for temporary disconnected operation.

---

# 34. Synchronization Relationships

Synchronization is the transport and reconciliation mechanism between local and server state.

Conceptually:

```text
Domain Transaction
      ↓
Offline Queue
      ↓
Synchronization
      ↓
Server Validation
      ↓
Domain Processing
```

Synchronization must not bypass domain invariants.

Every synchronized transaction must be validated against the owning domain.

---

# 35. Conflict Resolution

Conflict resolution is cross-domain but domain-aware.

Examples:

* Inventory stock conflict → Inventory rules;
* Order/table conflict → Order/Branch rules;
* Payment conflict → Payment rules;
* Cash conflict → Cash rules;
* Configuration conflict → Configuration rules;
* Device revocation conflict → Device rules.

A generic synchronization mechanism must not decide business outcomes independently of the owning domain.

---

# 36. Data Lifecycle Relationships

Data Lifecycle controls Business-level expiration and deletion.

When a Business enters deletion lifecycle, dependent domains must respond.

Conceptually:

```text
Data Lifecycle
      ↓
Business Deletion
      ↓
Subscription
Branch
Identity
Device
Order
Cash
Inventory
Payment
Reports
Notifications
Audit
Configuration
Synchronization
```

Deletion must respect dependency ordering and historical requirements.

---

# 37. Configuration and Operational Domains

Configuration defines future operational behavior.

Operational domains consume effective configuration.

For example:

```text
Configuration Version
       ↓
Cash Session Activation
       ↓
Operational Context
       ↓
Orders / Payments / Inventory
```

An active operational context must not be silently changed by a configuration update that is defined to become effective later.

---

# 38. Cross-Domain Transaction Boundaries

Not every cross-domain operation requires one physical database transaction.

The logical requirement is that business invariants remain correct.

Examples of strongly coupled operations include:

* Order acceptance + inventory deduction;
* Payment creation + cash impact where applicable;
* Cash session closing + final cash reconciliation.

Examples of secondary operations include:

* kitchen printing;
* notifications;
* heavy reporting;
* audit propagation where an outbox/event mechanism is appropriate.

Failure of a secondary operation must not unnecessarily roll back the primary business transaction.

---

# 39. Domain Events

Cross-domain communication may use domain events.

Examples:

* `OrderAccepted`;
* `PaymentCompleted`;
* `CashSessionClosed`;
* `InventoryAdjusted`;
* `RecipeApproved`;
* `ConfigurationActivated`;
* `DeviceRevoked`;
* `SubscriptionExpired`;
* `BusinessDeletionEligible`;
* `BusinessDeleted`.

Events should describe completed domain facts.

They must not be used as an uncontrolled command mechanism.

---

# 40. Command vs Event

A command requests an action.

An event states that something happened.

Example:

```text
Command:
AcceptOrder

        ↓

Order Domain validates

        ↓

Event:
OrderAccepted
```

Another domain may react to `OrderAccepted`, but it must not reinterpret the event as permission to bypass its own rules.

---

# 41. Cross-Domain Consistency

Consistency requirements differ by operation.

### Strong consistency is required where:

* stock deduction determines order acceptance;
* payment amount must be validated against remaining balance;
* Cash Session state changes;
* critical authorization decisions occur.

### Eventual consistency is acceptable where:

* notifications are delivered;
* dashboards update;
* heavy reports are generated;
* background synchronization progresses;
* secondary printer processing occurs.

The exact technical implementation is defined in Architecture.

---

# 42. Historical Snapshot Principle

When an operational transaction depends on configuration, the relevant configuration state must be snapshotted or otherwise historically reconstructable.

Examples:

* order price;
* recipe version;
* Set composition;
* branch price;
* discount;
* employee permission context where required;
* Cash Session context.

Later configuration changes must not rewrite historical transactions.

---

# 43. Cross-Domain Authorization

Every domain operation must validate authorization through the common security model.

Conceptually:

```text
Authentication
    ↓
Business Context
    ↓
Branch Scope
    ↓
Role / Permission
    ↓
Employee Override
    ↓
Subscription Entitlement
    ↓
Device Trust
    ↓
Domain Invariants
    ↓
Operation
```

Not every operation requires every layer in exactly the same way, but no domain may silently bypass mandatory security boundaries.

---

# 44. Tenant Isolation

Cross-domain relationships must preserve Business isolation.

A request from Business A must never:

* read Business B data;
* modify Business B state;
* create Business B transactions;
* synchronize Business B offline events;
* export Business B reports;
* access Business B notifications.

Business isolation must be enforced server-side.

---

# 45. Branch Isolation

Branch-scoped operations must respect Branch scope.

Examples include:

* inventory;
* cash;
* orders;
* branch menu;
* branch prices;
* branch reports;
* branch employees;
* branch notifications.

A user with access to one branch must not automatically receive access to another branch.

---

# 46. Error Propagation

Cross-domain failures must be explicit.

Examples:

```text
Order → Inventory
Inventory rejects stock
        ↓
Order acceptance fails
```

But:

```text
Order → Notification
Notification fails
        ↓
Order remains successful
Notification retries
```

Failure behavior must therefore depend on whether the dependency is core or secondary.

---

# 47. Idempotency

Cross-domain operations that may be retried must support idempotency where appropriate.

Important identities include:

* Entity UUID;
* Transaction UUID;
* Event UUID;
* Payment UUID;
* Device UUID;
* Report identity/version;
* Conflict UUID.

Repeated processing must not create duplicate business effects.

---

# 48. Concurrency

Cross-domain operations must account for concurrent changes.

Examples:

* two devices accepting the same last-stock item;
* simultaneous payments;
* concurrent Cash Session operations;
* configuration change during order creation;
* employee permission change during operation;
* device revocation during synchronization.

The owning domain must remain authoritative for its state.

---

# 49. Cross-Domain Historical Reconstruction

The system should be able to reconstruct important historical operations using linked identifiers.

A significant transaction should allow navigation conceptually through:

```text
Business
  ↓
Branch
  ↓
Employee
  ↓
Device
  ↓
Cash Session
  ↓
Transaction
  ↓
Order / Payment / Inventory
  ↓
Audit
```

Not every entity will contain every reference, but relevant context must remain reconstructable.

---

# 50. Domain Boundary Rules

The following boundaries are mandatory:

1. Business owns tenant identity.
2. Subscription owns entitlement state.
3. Identity owns authentication and authorization concepts.
4. Branch owns operational location context.
5. Device owns device trust state.
6. Order owns order lifecycle.
7. Cash owns Cash Session state.
8. Inventory owns stock state.
9. Payment owns payment state.
10. Menu and Pricing owns selling configuration.
11. Kitchen owns preparation/printing context.
12. Employee and Payroll owns employment and payroll state.
13. Reporting owns report snapshots and versions.
14. Notification owns notification state.
15. Audit owns audit records.
16. Synchronization owns synchronization state.
17. Data Lifecycle owns Business lifecycle and deletion orchestration.
18. Configuration owns controlled configuration versions.

---

# 51. Domain Invariants

## Business and Tenant

1. Every business-owned entity has a Business context.
2. Cross-business operational references are prohibited.
3. Business isolation applies to all domains.
4. Business UUID is globally unique.
5. Business UUID is never reused.
6. Domain operations must validate Business context.
7. Synchronization must preserve Business isolation.
8. Reports must preserve Business isolation.
9. Offline storage must preserve Business isolation.
10. Audit records must preserve Business context.

## Branch

11. Branch belongs to exactly one Business.
12. Branch-scoped operations must validate Branch access.
13. Branch isolation applies across domains.
14. Branch scope must not be inferred from employee identity alone.
15. Multi-branch employees may have different permissions per branch.
16. Cross-branch operations require explicit business rules.
17. Branch history must remain reconstructable.
18. Branch deletion must follow lifecycle rules.

## Identity and Access

19. Authentication and authorization are separate concerns.
20. Permissions are evaluated independently from device trust.
21. Subscription entitlement is independent from employee permission.
22. Employee overrides must remain within authorization boundaries.
23. Domain operations must not grant permissions implicitly.
24. Permission changes must affect subsequent protected operations according to system rules.
25. Historical actor identity must remain available.

## Device

26. Device identity is independent from employee identity.
27. Trusted device state is independent from permission state.
28. Revoked devices cannot bypass trust restrictions.
29. Offline authorization cannot permanently bypass server security.
30. Device replacement creates a new device identity.

## Order

31. Order owns order lifecycle.
32. Order history cannot be silently rewritten by configuration changes.
33. Accepted order inventory effects must remain consistent.
34. Order cancellation is not deletion.
35. Order UUID remains stable through cashier handover.
36. Payment does not automatically redefine operational order status.

## Inventory

37. Inventory owns stock quantities.
38. Negative stock is prohibited.
39. Stock deduction must be atomic where required.
40. Inventory conflicts must follow Inventory rules.
41. Historical stock movements must remain reconstructable.
42. Recipe configuration must not silently rewrite historical stock movements.

## Payment

43. Payment owns payment state.
44. Original payment records remain historically preserved.
45. Refunds are separate financial operations.
46. Payment conflicts must follow Payment rules.
47. Cash payment effects must remain associated with the relevant Cash Session.
48. Debt allocation must remain historically reconstructable.

## Cash

49. Cash owns Cash Session lifecycle.
50. Cash Session identity remains stable after creation.
51. Closed sessions cannot silently become active.
52. Cash corrections are separate historical operations.
53. Cash discrepancies remain associated with the relevant session.
54. Cash handover must preserve previous-session history.

## Configuration

55. Configuration owns configuration versions.
56. Configuration changes do not silently rewrite historical transactions.
57. Configuration activation follows defined effective boundaries.
58. Operational domains consume effective configuration.
59. Configuration rollback creates a new version rather than rewriting history.

## Reporting

60. Reporting does not become the source of operational truth.
61. Report versions are immutable.
62. Report corrections create new versions only when relevant results change.
63. Report access respects Business and Branch scope.
64. Report generation must not block core POS operations.

## Notification

65. Notification does not own the source business condition.
66. Notification visibility requires authorization.
67. Notification failure must not roll back unrelated core transactions.
68. Duplicate notification creation must be controlled.

## Audit

69. Audit does not replace operational domain state.
70. Important state changes must remain auditable.
71. Audit records are immutable.
72. Audit records preserve relevant actor and context identifiers.

## Synchronization

73. Synchronization does not bypass domain invariants.
74. Server-side domain validation remains authoritative.
75. Offline events must be idempotent.
76. Conflicts must be explicit.
77. Conflict resolution must use the owning domain's rules.
78. Synchronization must preserve historical transaction identity.

## Data Lifecycle

79. Business deletion affects all dependent domains.
80. Deleted business data cannot be resurrected through synchronization.
81. Device trust becomes invalid after Business deletion.
82. Data lifecycle state transitions must be deterministic.
83. Deletion must respect domain dependencies.

## Cross-Domain Transactions

84. Core atomic operations must preserve their business invariants.
85. Secondary failures must not unnecessarily roll back successful core operations.
86. Cross-domain retries must be idempotent.
87. Concurrent cross-domain operations must produce deterministic results.
88. Partial failure must never silently create inconsistent business state.
89. Domain ownership must remain clear during cross-domain workflows.

## Historical Integrity

90. Historical transactions must retain relevant configuration context.
91. Historical actor identity must remain reconstructable.
92. Historical Device UUID must remain reconstructable where relevant.
93. Historical Cash Session UUID must remain reconstructable where relevant.
94. Corrections must preserve original state.
95. Audit history must preserve important state transitions.

## Security

96. Every protected cross-domain operation must respect authorization boundaries.
97. Device trust cannot replace employee authorization.
98. Subscription entitlement cannot be bypassed through offline mode.
99. Branch scope cannot be bypassed through cross-domain references.
100. No cross-domain mechanism may weaken tenant isolation.

---

# 52. Completion Criteria

The Cross-Domain Relationships Domain is considered complete when:

* all major domains have explicit ownership boundaries;
* Business isolation is defined;
* Branch isolation is defined;
* authentication, authorization, device trust, and subscription are separated;
* Order/Inventory relationship is defined;
* Order/Payment relationship is defined;
* Payment/Cash relationship is defined;
* Menu/Pricing/Configuration relationships are defined;
* Employee/Payroll relationships are defined;
* Reporting relationships are defined;
* Notification relationships are defined;
* Audit relationships are defined;
* Offline and Synchronization boundaries are defined;
* Data Lifecycle dependencies are defined;
* core versus secondary cross-domain operations are distinguished;
* idempotency and concurrency responsibilities are defined;
* historical reconstruction requirements are defined;
* cross-domain invariants are documented.

---

# 53. Related Documents

## Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

## System Analysis

* `docs/02_System_Analysis/01_System_Context_and_Boundaries.md`
* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

## Domain Analysis

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

## Future Layers

* `docs/04_Architecture/`
* `docs/05_Database/`
* `docs/06_Backend/`
* `docs/09_API/`
* `docs/11_Security/`
* `docs/12_Testing/`
* `docs/14_Operations/`
* `adr/`

