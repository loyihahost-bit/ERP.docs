# Domain Overview

**Document ID:** DA-01
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/README.md`

## 1. Purpose

This document defines the high-level domain structure of FastFood ERP.

It identifies:

* major business domains;
* domain responsibilities;
* domain ownership;
* core domain entities;
* domain relationships;
* domain dependencies;
* core and supporting domains;
* cross-domain rules.

This document does not define database tables, API endpoints, framework modules, or deployment architecture.

---

## 2. Domain Model

FastFood ERP is organized around the following logical domains:

```text
Platform
   │
   ├── Subscription
   │
   └── Business
         │
         ├── Identity & Access
         │
         ├── Branch
         │
         ├── Order
         │
         ├── Cash
         │
         ├── Inventory
         │
         ├── Product & Recipe
         │
         ├── Menu & Pricing
         │
         ├── Payment & Refund
         │
         ├── Employee & Payroll
         │
         ├── Reporting
         │
         ├── Notification
         │
         ├── Audit & History
         │
         └── Data Lifecycle
```

These are logical domains. They do not imply separate microservices.

---

## 3. Domain Classification

### 3.1. Core Domains

The following domains directly represent the main restaurant operations:

1. Order
2. Cash
3. Inventory
4. Product & Recipe
5. Menu & Pricing
6. Payment & Refund

These domains contain the highest-value business operations.

### 3.2. Business Management Domains

1. Business
2. Branch
3. Employee & Payroll
4. Subscription
5. Reporting

### 3.3. Supporting Domains

1. Identity & Access
2. Notification
3. Audit & History
4. Data Lifecycle

### 3.4. Platform Domain

Platform administration is separated from tenant business operations.

It includes:

* Super Admin;
* business creation;
* tariff management;
* platform-level limits;
* platform-level configuration.

---

# 4. Business Domain

## Responsibility

The Business domain represents the tenant organization using FastFood ERP.

It owns:

* Business identity;
* business status;
* business settings;
* business-level configuration;
* business ownership relationship;
* business lifecycle metadata.

## Key Concepts

```text
Business
Business Settings
Business Owner
Business Status
Business Lifecycle
```

## Boundary

The Business domain does not own:

* individual orders;
* cash sessions;
* stock movements;
* payment transactions.

Those belong to their respective domains.

The Business domain establishes the ownership boundary for those resources.

---

# 5. Branch Domain

## Responsibility

The Branch domain represents a physical operational location belonging to a Business.

It owns:

* Branch identity;
* branch status;
* branch settings;
* operational configuration;
* branch-level scope.

A Branch belongs to exactly one Business.

## Key Concepts

```text
Branch
Branch Settings
Branch Status
Branch Configuration
```

Branch is a critical scope boundary for:

* employees;
* devices;
* cash;
* inventory;
* orders;
* attendance;
* branch menu;
* branch reports.

---

# 6. Identity and Access Domain

## Responsibility

The Identity and Access domain determines who the user is and what the user is allowed to do.

It owns:

* Employee identity;
* authentication identity;
* Roles;
* Permissions;
* Employee Overrides;
* Branch Scope;
* Effective Permissions;
* access state.

## Authorization Model

Effective authorization is determined from:

```text
Role Permissions
        +
Employee Overrides
        +
Branch Scope
        +
Subscription Entitlement
        +
Device Trust
```

Device trust does not replace employee authorization.

Subscription entitlement does not replace employee authorization.

Both are additional constraints.

---

# 7. Subscription Domain

## Responsibility

The Subscription domain controls which business capabilities are currently available to a Business.

It owns:

* Subscription;
* Tariff;
* Entitlements;
* Feature limits;
* Usage limits;
* Subscription state;
* Expiration;
* Grace period;
* Read-only transition;
* Reactivation state.

## Lifecycle

```text
Active
   ↓
Expired / Read-Only
   ↓
Deletion Eligible
   ↓
Deleting
   ↓
Deleted
```

Reactivation during the allowed period prevents deletion and restores the existing Business state.

---

# 8. Order Domain

## Responsibility

The Order domain represents customer orders and their operational lifecycle.

It owns:

* Order;
* Order Item;
* Order Type;
* Order lifecycle;
* Table context;
* Waiter assignment;
* Order modifications;
* Cancellation;
* Kitchen ticket relationship;
* order snapshots.

## Order Lifecycle

```text
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

Payment is related to the Order domain but does not own the Order lifecycle.

An order may be paid before reaching `Served`.

---

# 9. Cash Domain

## Responsibility

The Cash domain controls physical cash operations.

It owns:

* Cash Register;
* Cash Session;
* Opening Cash;
* Expected Cash;
* Actual Cash;
* Cash Difference;
* Cash Handover;
* Cash Corrections.

## Main Relationship

```text
Branch
  ↓
Cash Register
  ↓
Cash Session
  ↓
Cash Operations
```

A closed Cash Session remains historical.

Correction does not reopen the original session.

---

# 10. Inventory Domain

## Responsibility

The Inventory domain manages physical stock and stock movements.

It owns:

* Warehouse;
* Inventory Item;
* Stock Balance;
* Stock Movement;
* Purchase;
* Inventory Adjustment;
* Inventory Count;
* Stock Discrepancy.

## Core Rule

Inventory must never silently become negative.

Stock-changing operations must use controlled domain transactions.

Inventory state must remain reconstructable from its movement history.

---

# 11. Product and Recipe Domain

## Responsibility

This domain defines what products exist and how they are produced.

It owns:

* Raw Material;
* Semi-Finished Product;
* Finished Product;
* Product;
* Recipe;
* Recipe Version;
* Recipe Component;
* Set Product;
* Set Version.

## Recipe Structure

```text
Raw Material
      ↓
Semi-Finished Product
      ↓
Finished Product
```

A recipe may depend on other products.

Recipe versions remain historically available.

Products with historical dependencies are archived rather than destructively deleted.

---

# 12. Menu and Pricing Domain

## Responsibility

The Menu and Pricing domain controls which products can be sold and at what price.

It owns:

* Menu Category;
* Menu Product;
* Branch Menu Availability;
* Standard Price;
* Branch Price Override;
* Price Version;
* Product Availability;
* Discount Configuration;
* Equipment Availability.

## Configuration Rule

Configuration changes are versioned and respect cash-session activation rules.

Open orders retain their applicable price snapshot.

Historical orders must not change because a current price changes.

---

# 13. Payment and Refund Domain

## Responsibility

This domain manages financial transactions related to orders.

It owns:

* Payment;
* Payment Portion;
* Payment Method;
* Debt Customer;
* Debt Allocation;
* Debt Repayment;
* Refund;
* Overpayment;
* Payment Correction.

## Payment Methods

```text
Cash
Card
Debt
Mixed
```

## Financial Integrity

Original payment operations remain historically available.

Corrections are separate operations.

Refunds do not rewrite the original payment.

Overpayments are represented separately from the order's original payable amount.

---

# 14. Employee and Payroll Domain

## Responsibility

This domain manages employee operational and payroll information.

It owns:

* Employee Employment State;
* Attendance;
* Salary Configuration;
* Payroll Period;
* Payroll Calculation;
* Bonus;
* Payroll Correction.

Authorization remains owned by Identity and Access.

Payroll must not directly grant or remove permissions.

---

# 15. Reporting Domain

## Responsibility

The Reporting domain creates consistent historical views of business data.

It owns:

* Report Definition;
* Report Scope;
* Report Period;
* Report Snapshot;
* Report Version;
* Report Export.

Reports are derived from authoritative operational domains.

Reports do not become the source of truth for:

* orders;
* payments;
* inventory;
* cash;
* employees.

---

# 16. Notification Domain

## Responsibility

The Notification domain informs authorized users about important business conditions.

It owns:

* Notification;
* Notification Condition;
* Severity;
* Recipient;
* Notification State;
* Notification Cycle;
* Retry State.

Notifications are secondary effects.

A notification failure must not roll back the core transaction that generated the notification.

---

# 17. Audit and History Domain

## Responsibility

The Audit domain preserves important changes and security-relevant actions.

It owns:

* Audit Event;
* Actor;
* Event Type;
* Entity Reference;
* Old State;
* New State;
* Reason;
* Device Context;
* Cash Session Context;
* Transaction Context.

Audit records are immutable.

Audit history must be sufficient to reconstruct important historical operations.

---

# 18. Data Lifecycle Domain

## Responsibility

The Data Lifecycle domain controls Business data lifecycle.

It owns:

* Lifecycle State;
* Expiration;
* Deletion Eligibility;
* Deletion Job;
* Deletion Progress;
* Deletion Result.

It coordinates with Subscription and Background Jobs.

It must prevent:

* stale offline data from resurrecting deleted Business data;
* partial deletion from appearing as successful deletion;
* duplicate deletion execution.

---

# 19. Cross-Domain Ownership

The following ownership rules are mandatory.

| Concept            | Owning Domain      |
| ------------------ | ------------------ |
| Business           | Business           |
| Branch             | Branch             |
| Employee Identity  | Identity & Access  |
| Role               | Identity & Access  |
| Permission         | Identity & Access  |
| Subscription       | Subscription       |
| Order              | Order              |
| Order Item         | Order              |
| Cash Register      | Cash               |
| Cash Session       | Cash               |
| Inventory Balance  | Inventory          |
| Stock Movement     | Inventory          |
| Product            | Product & Recipe   |
| Recipe             | Product & Recipe   |
| Menu Availability  | Menu & Pricing     |
| Price              | Menu & Pricing     |
| Payment            | Payment & Refund   |
| Debt               | Payment & Refund   |
| Refund             | Payment & Refund   |
| Attendance         | Employee & Payroll |
| Payroll            | Employee & Payroll |
| Report Version     | Reporting          |
| Notification       | Notification       |
| Audit Event        | Audit & History    |
| Deletion Lifecycle | Data Lifecycle     |

---

# 20. Cross-Domain Transaction Examples

## 20.1. Order Acceptance

```text
Order
  ↓
Validate Product / Price
  ↓
Validate Inventory
  ↓
Inventory Deduction
  ↓
Order → Accepted
  ↓
Kitchen Event
```

Order acceptance and inventory deduction belong to one core transactional boundary.

Kitchen printing is secondary.

---

## 20.2. Payment

```text
Order
  ↓
Validate Paymentability
  ↓
Create Payment
  ↓
Update Financial State
  ↓
Cash / Card / Debt Context
```

Payment does not rewrite the Order lifecycle.

---

## 20.3. Cash Handover

```text
Previous Cash Session
        ↓
Close
        ↓
Cash Count
        ↓
Handover
        ↓
New Cash Session
```

The old Cash Session remains immutable as an historical session.

---

## 20.4. Recipe Approval

```text
Recipe Draft
     ↓
Validation
     ↓
Owner Approval
     ↓
New Recipe Version
     ↓
Future Activation
```

Existing historical orders continue to use their historical snapshots.

---

## 20.5. Subscription Expiration

```text
Subscription
     ↓
Expired
     ↓
Read-Only Business
     ↓
60-Day Lifecycle Window
     ↓
Deletion Eligible
```

Reactivation within the allowed period stops the deletion lifecycle.

---

# 21. Domain Dependency Principles

Domain dependencies must follow these rules:

1. A domain may consume another domain's published state or business event.
2. A domain must not directly modify another domain's internal state.
3. Cross-domain changes must use an explicit application/service boundary.
4. Shared identifiers are allowed.
5. Shared ownership is not allowed.
6. Historical snapshots may preserve information from another domain.
7. A report may read multiple domains but does not own their operational state.
8. Audit may observe changes across all domains but does not control them.
9. Notifications may react to domain events but do not own the originating business operation.

---

# 22. Core vs Secondary Operations

### Core

These operations require strong consistency:

* Order acceptance;
* Inventory deduction;
* Payment creation;
* Cash session transition;
* Inventory adjustment;
* Refund creation;
* Debt allocation;
* Critical configuration activation.

### Secondary

These should not block core operations unnecessarily:

* Kitchen printing;
* Notifications;
* Report generation;
* Excel export;
* Dashboard refresh;
* Analytics calculations;
* Background synchronization processing.

If a secondary operation fails, the original core operation must remain valid unless the business rule explicitly requires otherwise.

---

# 23. Offline Domain Model

Offline operation does not create duplicate business identities.

The same domain identities are preserved:

```text
Business UUID
Branch UUID
Employee UUID
Device UUID
Order UUID
Payment UUID
Cash Session UUID
Inventory Transaction UUID
```

Offline-created operations retain their UUIDs when synchronized.

The server validates them according to the same domain rules as online operations.

---

# 24. Historical Snapshots

Some domain information must be copied into historical transactions because current domain state may change.

Examples:

### Order

* product identity;
* product name;
* price;
* discount;
* applicable configuration;
* recipe/configuration reference.

### Payment

* payment amount;
* method;
* related order;
* actor;
* cash session;
* timestamps.

### Report

* report definition;
* period;
* scope;
* source state;
* version.

Historical snapshots must not be treated as replacements for current domain entities.

---

# 25. Domain Invariants

The following high-level invariants apply across the domain model:

1. Every tenant-owned resource belongs to exactly one Business.
2. Branch resources belong to the correct Business.
3. Cross-business access is forbidden.
4. Branch scope must be validated.
5. Effective permissions must be evaluated server-side.
6. Subscription entitlement must be evaluated server-side.
7. Trusted devices do not independently grant permissions.
8. UUIDs remain stable across synchronization.
9. Core transactions must be atomic.
10. Historical records must not be silently overwritten.
11. Corrections must preserve original operations.
12. Inventory cannot silently become negative.
13. Payment cannot silently exceed allowed financial rules.
14. Closed cash sessions cannot become active again.
15. Reports must reference consistent source data.
16. Audit records are immutable.
17. Offline operations cannot bypass authorization.
18. Stale offline data cannot resurrect deleted business data.
19. Secondary failures must not unnecessarily roll back core transactions.
20. Domain ownership must remain unambiguous.

---

# 26. Domain Model and Future Architecture

The domain boundaries defined here are logical boundaries.

The Architecture phase may implement them using:

* modular monolith;
* modular backend packages;
* application services;
* domain services;
* repositories;
* event handlers;
* background workers.

The initial architecture should not introduce distributed microservices solely because logical domains exist.

The selected architecture must preserve the domain boundaries while minimizing unnecessary operational complexity.

---

# 27. Completion Criteria

This document is considered complete when:

* all major domains are identified;
* each domain has a clear responsibility;
* ownership is explicit;
* core and supporting domains are distinguished;
* cross-domain transaction boundaries are understood;
* historical requirements are represented;
* offline implications are represented;
* domain dependencies are defined;
* no domain owns another domain's internal state;
* future Architecture work can use this document as a stable domain map.

---

## Related Documents

### Previous Analysis

* `docs/01_Business_Analysis/README.md`
* `docs/02_System_Analysis/README.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Domain Analysis

* `docs/03_Domain_Analysis/README.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/09_Product_and_Recipe_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`
* `docs/03_Domain_Analysis/11_Payment_and_Refund_Domain.md`
* `docs/03_Domain_Analysis/12_Employee_and_Payroll_Domain.md`
* `docs/03_Domain_Analysis/13_Reporting_Domain.md`
* `docs/03_Domain_Analysis/14_Notification_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`

### Next Phase

* `docs/04_Architecture/`

