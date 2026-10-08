# System Context and Boundaries

**Document ID:** SA-01
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system context and boundaries of FastFood ERP.

It establishes:

* what belongs to FastFood ERP;
* what exists outside the system;
* which actors interact with the system;
* how Business and Branch context is established;
* which operations are controlled by the platform;
* which operations remain external;
* where system responsibility begins and ends.

This document provides the context required by the remaining System Analysis documents.

---

## 2. System Boundary

FastFood ERP is a multi-tenant SaaS ERP platform for restaurant and fast-food businesses.

The core system boundary includes:

* business and branch management;
* employee management;
* authentication and authorization;
* trusted devices;
* POS;
* orders;
* tables;
* waiters;
* kitchen operations;
* payments;
* cash sessions;
* inventory;
* products and recipes;
* menu and pricing;
* attendance and payroll;
* reports;
* notifications;
* audit and history;
* offline operation;
* synchronization;
* subscription enforcement;
* data lifecycle management.

The system does not currently include:

* online customer ordering;
* customer mobile applications;
* Telegram bot;
* full CRM;
* external payment automation;
* advanced delivery management;
* branch-to-branch inventory transfer;
* tax engine;
* predictive analytics;
* AI-based business recommendations.

These capabilities may be introduced later as separate requirements.

---

## 3. High-Level Context

The high-level system context is:

```text
                    ┌─────────────────────┐
                    │     Super Admin     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastFood ERP     │
                    │      Platform       │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
           ┌─────────┐   ┌──────────┐   ┌──────────┐
           │ Business│   │  Branch  │   │Subscription│
           │  Users  │   │Operations│   │ Entitlement│
           └────┬────┘   └─────┬────┘   └──────────┘
                │              │
                └──────┬───────┘
                       ▼
                ┌──────────────┐
                │ POS / ERP    │
                │ Operations   │
                └──────────────┘
```

The platform provides the shared SaaS environment, while each Business operates within its own tenant boundary.

---

## 4. Platform Boundary

The Platform represents the SaaS-level environment.

Platform-level responsibilities include:

* Business creation;
* subscription tariff management;
* platform-level limits;
* platform-level feature entitlement;
* platform administration;
* business lifecycle enforcement;
* permanent deletion processing;
* platform-level audit where required.

The Super Admin operates at the platform level.

Super Admin does not normally perform day-to-day restaurant operations such as:

* creating orders;
* processing normal cashier payments;
* managing branch inventory;
* performing employee attendance;
* managing restaurant tables.

These operations belong to the Business/Branch operational boundary.

---

## 5. Business / Tenant Boundary

A Business represents one restaurant business or restaurant network using FastFood ERP.

The Business boundary contains:

* branches;
* employees;
* roles;
* permissions;
* menu;
* products;
* recipes;
* inventory configuration;
* pricing;
* orders;
* payments;
* cash operations;
* payroll;
* reports;
* notifications;
* audit history.

All operational data belongs to exactly one Business.

Business isolation is mandatory.

A request associated with Business A must never return operational data belonging to Business B.

This isolation must be enforced at the server and data-access layers rather than relying only on frontend filtering.

---

## 6. Branch Boundary

A Branch is an operational unit inside a Business.

A Branch has its own operational context, including where applicable:

* employees;
* employee branch assignments;
* permissions;
* inventory;
* warehouse;
* cash register;
* cash sessions;
* POS activity;
* tables;
* kitchen operations;
* branch-specific menu availability;
* branch-specific prices;
* branch reports.

Some configuration is Business-wide and some is Branch-specific.

The system must clearly distinguish between:

```text
Business Scope
     │
     ├── Global Configuration
     │
     └── Branch Scope
            │
            ├── Operational Data
            ├── Local Configuration
            └── Branch Overrides
```

---

## 7. Multi-Branch Context

A Business may contain multiple Branches.

An Employee may be assigned to:

* one Branch;
* multiple Branches;
* all permitted Branches.

Permissions may differ between branches.

For example:

```text
Employee
   │
   ├── Branch A → Manager Permissions
   │
   ├── Branch B → Cashier Permissions
   │
   └── Branch C → No Operational Access
```

The system must calculate effective authorization using the current branch context.

Changing branch context may therefore change the employee's effective permissions.

---

## 8. Main System Actors

### 8.1. Super Admin

Super Admin operates at platform level.

Main responsibilities:

* create and manage Businesses;
* configure subscription tariffs;
* define platform limits;
* manage platform-level configuration;
* manage lifecycle enforcement;
* oversee platform-level operations.

Super Admin access does not automatically mean that every Business employee permission is granted for normal operational workflows.

---

### 8.2. Owner

Owner operates at Business level.

Owner may manage:

* branches;
* employees;
* roles;
* permissions;
* menu;
* recipes;
* prices;
* inventory;
* expenses;
* reports;
* payroll;
* dashboard;
* business settings.

Owner access is constrained by the Business subscription entitlement and system-level security rules.

---

### 8.3. Manager

Manager operates within the permissions granted by the Business.

Manager may perform management operations only within:

* assigned Business;
* assigned Branch scope;
* granted permissions;
* current subscription entitlement.

A Manager cannot grant permissions beyond their own authority.

---

### 8.4. Cashier

Cashier is a primary POS operational actor.

Cashier may perform permitted operations involving:

* orders;
* payments;
* cash sessions;
* cash handover;
* corrections where explicitly permitted.

Every relevant cashier operation is associated with the cashier identity and operational context.

---

### 8.5. Waiter

Waiter may interact with:

* tables;
* customer visits;
* orders;
* waiter assignments;

according to assigned permissions.

A waiter may assist another waiter temporarily when permitted by the system rules.

The system preserves the primary waiter assignment and the temporary helping assignment separately.

---

### 8.6. Cook

Cook interacts primarily with kitchen-related information and operations according to assigned permissions.

Cook access is branch-scoped where applicable.

---

### 8.7. Other Employees

The system must support additional employee types without requiring a new hard-coded authorization model for each employee type.

Authorization is based on:

* role permissions;
* employee overrides;
* branch scope;
* subscription entitlement.

---

## 9. Device Context

A device is an operational client used to access FastFood ERP.

A device may be:

* registered;
* trusted;
* revoked;
* associated with one or more permitted branches according to configuration.

Trusted device status does not replace employee authentication or authorization.

The effective operation context is:

```text
Employee
   +
Device
   +
Business
   +
Branch
   +
Permission
   +
Subscription
```

A trusted device with an invalid employee session must not be sufficient to perform protected operations.

---

## 10. Cash Register Context

A Branch normally has one physical Cash Register in the current business model.

The architecture must not prevent future support for multiple registers.

The operational hierarchy is:

```text
Branch
   ↓
Cash Register
   ↓
Cash Session
   ↓
Cashier Operations
```

The physical register remains the same across cashier handovers, while each cashier session has its own Cash Session UUID.

A closed Cash Session is historical and must not become active again.

---

## 11. POS Context

POS is part of the Branch operational boundary.

POS operations include:

* order creation;
* order acceptance;
* order modification;
* payment;
* table interaction;
* order status tracking;
* kitchen ticket generation.

The current order types are:

* Hall / Dine-in;
* Takeaway.

Phone Delivery remains outside the current active operational scope.

Online ordering is also outside the current scope.

---

## 12. Table Context

Tables belong to a Branch.

A table has a persistent identity, but customer usage is represented through a separate visit/session grouping.

Conceptually:

```text
Table
  │
  ├── Visit / Session 1
  │      ├── Order
  │      └── Order
  │
  ├── Visit / Session 2
  │      └── Order
  │
  └── Visit / Session 3
         ├── Order
         └── Order
```

When a table is freed, its previous visit grouping ends.

A new customer usage cycle creates a new visit/session grouping.

A table is considered Busy when it has at least one open/unpaid order.

Paid historical orders remain associated with their original visit/session.

---

## 13. Kitchen Context

Kitchen processing is part of the Branch operational environment.

The ERP system is responsible for:

* generating kitchen tickets;
* routing tickets to configured printers;
* tracking print state;
* retrying failed printing;
* preventing duplicate ticket generation.

Printer hardware itself remains an external physical dependency.

Printer failure must not invalidate a successfully committed ERP order transaction.

---

## 14. External Dependencies

The system may interact with external infrastructure or services.

Examples include:

* printer hardware;
* network infrastructure;
* physical payment terminals;
* hosting infrastructure;
* future external services.

The current system does not treat external payment processor authorization as part of the core payment model.

The ERP may record a Card payment, but external card authorization is a separate concern unless a future integration is explicitly introduced.

---

## 15. Internet and Network Boundary

Network availability is not assumed to be continuous.

The system therefore distinguishes between:

```text
Online
   ↓
Server available
   ↓
Authoritative server validation
```

and:

```text
Offline
   ↓
Trusted Device
   ↓
Valid Offline Authorization
   ↓
Permitted Local Operations
   ↓
Synchronization
```

A new device cannot perform first-time offline operation.

The device must first be registered and trusted while online.

---

## 16. Offline Boundary

Offline mode is intentionally limited.

The system may continue selected operational workflows offline, but the device must not be able to:

* bypass subscription limits;
* bypass permissions;
* create unauthorized employee access;
* operate beyond offline authorization validity;
* bypass critical business rules.

Offline transactions remain associated with their original:

* Business;
* Branch;
* Employee;
* Device;
* Cash Session;
* Transaction UUID.

When connectivity returns, these operations are synchronized and validated.

---

## 17. Data Access Boundary

All data access must respect the following hierarchy:

```text
Platform
   ↓
Business
   ↓
Branch
   ↓
Employee / Role / Permission
   ↓
Entity
```

Not every entity is branch-scoped.

For example:

* Business-level recipes may be global;
* Branch inventory is branch-specific;
* Branch price overrides are branch-specific;
* Orders belong to a Branch;
* Cash Sessions belong to a Branch;
* Reports may use Business or Branch scope.

The exact scope of each entity is defined by its dedicated System Analysis document.

---

## 18. Subscription Boundary

Subscription entitlement is a system boundary, not merely a UI feature.

An operation may be technically available in the application but still be rejected because the Business does not have the required entitlement.

The effective operation model is:

```text
Request
  ↓
Authentication
  ↓
Business Context
  ↓
Branch Context
  ↓
Permission
  ↓
Subscription Entitlement
  ↓
Business/System Rules
  ↓
Operation
```

Subscription expiry therefore affects modifying operations even when the user remains authenticated.

---

## 19. Reporting Boundary

Reports operate within explicit Business and/or Branch scope.

A report request must establish:

* report definition;
* period;
* business;
* branch scope;
* requesting employee;
* applicable permissions;
* subscription state.

Report generation must not expose data outside the requester's authorized scope.

Excel export must use the selected report version/snapshot.

---

## 20. Audit Boundary

Audit records belong to the system history and are separate from normal editable business data.

Audit data must preserve:

* actor;
* business;
* branch;
* device;
* transaction;
* entity;
* timestamp;
* old state;
* new state;
* reason;
* result;
* source.

Audit records are immutable.

Access to audit data is permission-controlled.

---

## 21. Notification Boundary

Notifications are generated by system/business events.

Examples include:

* low stock;
* subscription expiry;
* salary due;
* large refund;
* large inventory variance;
* branch loss;
* cash discrepancy.

Notifications do not become a replacement for the underlying business event.

For example:

```text
Cash Discrepancy
      ↓
Core Cash Data
      +
Notification
```

If notification delivery fails, the core business transaction remains valid.

---

## 22. Data Lifecycle Boundary

Business lifecycle is controlled at the platform level.

The lifecycle is:

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

During read-only retention:

* data can be viewed;
* history can be viewed;
* permitted reports can be viewed;
* permitted Excel exports can be generated.

Modifying operations remain blocked.

After the defined retention period, the Business becomes eligible for permanent deletion according to the Data Lifecycle rules.

---

## 23. System Responsibilities

FastFood ERP is responsible for:

* enforcing business and system rules;
* protecting tenant isolation;
* authenticating users;
* authorizing operations;
* maintaining operational state;
* maintaining historical integrity;
* maintaining inventory consistency;
* maintaining payment and cash integrity;
* maintaining audit history;
* managing offline synchronization;
* enforcing subscription entitlement;
* generating reports;
* managing notifications;
* executing lifecycle operations.

---

## 24. External Responsibilities

External systems, infrastructure or physical devices remain responsible for their own operation.

Examples:

### Printer

The printer is responsible for physically printing a ticket.

FastFood ERP is responsible for:

* creating the print job;
* routing it;
* tracking the state;
* retrying when appropriate.

### Network

The network is responsible for connectivity.

FastFood ERP is responsible for continuing permitted offline operations when connectivity is unavailable.

### Payment Terminal

The physical terminal is responsible for external card processing when such integration exists.

FastFood ERP is responsible for recording the ERP payment state.

---

## 25. Boundary Enforcement

System boundaries must be enforced at authoritative system layers.

Frontend filtering alone is insufficient.

The following layers must participate where applicable:

```text
Frontend
   ↓
API
   ↓
Application / Domain Rules
   ↓
Database Access
   ↓
Database Constraints
```

Security-sensitive boundaries must be validated server-side.

This includes:

* Business isolation;
* Branch scope;
* Employee status;
* Permission;
* Subscription entitlement;
* Inventory rules;
* Payment rules;
* Cash session rules;
* Entity state;
* synchronization rules.

---

## 26. Cross-Boundary Operations

Some operations affect multiple bounded contexts.

For example:

### Order Acceptance

```text
POS
 ↓
Order
 ↓
Inventory
 ↓
Kitchen Event
```

The Order and Inventory core transaction must remain atomic.

Kitchen printing is secondary.

### Payment

```text
POS
 ↓
Payment
 ↓
Cash Session / Financial State
```

Payment state is preserved separately from operational order status.

### Shift Handover

```text
Previous Cash Session
        ↓
Cash Reconciliation
        ↓
New Cash Session
```

The previous session remains permanently historical while the new session becomes active.

Cross-boundary operations must have explicit transaction and consistency rules.

---

## 27. System Context Invariants

The following invariants apply to this document:

1. Every operational record belongs to a Business.
2. Branch-scoped records belong to a Branch within the same Business.
3. Cross-business data access is prohibited.
4. Branch context must be validated for branch-scoped operations.
5. Employee permissions are evaluated within the current branch context.
6. Trusted device status does not grant permissions.
7. Subscription entitlement is part of operation authorization.
8. Offline mode cannot bypass system boundaries.
9. Cash Sessions belong to a specific Cash Register and Branch.
10. Orders belong to a specific Branch.
11. Tables belong to a specific Branch.
12. Inventory belongs to the relevant Business/Branch context.
13. Audit records preserve operational context.
14. Reports must respect Business and Branch scope.
15. Notifications must respect Business and Branch visibility.
16. External service failure must not silently alter committed core business state.
17. Historical context must remain recoverable.
18. Cross-boundary operations must define explicit consistency behavior.

---

## 28. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/README.md`
* `docs/02_System_Analysis/02_Application_Structure_and_Navigation.md`
* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`

---

## 29. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Next Document:** `02_Application_Structure_and_Navigation.md`

