# System Architecture

**Document ID:** ARCH-01
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This document defines the high-level system architecture of FastFood ERP.

It establishes:

* the major technical components;
* system boundaries;
* application boundaries;
* communication paths;
* data ownership;
* online and offline execution models;
* synchronous and asynchronous processing;
* security boundaries;
* external integration boundaries;
* deployment-independent architectural responsibilities.

This document does not define detailed database schemas, API endpoints, frontend components, or infrastructure configuration.

Those concerns are defined in later Architecture documents.

---

# 2. Architectural Goals

The system architecture must support the following primary goals:

1. Multi-tenant SaaS operation.
2. Multi-branch business operation.
3. Fast POS workflows.
4. Offline branch operation.
5. Reliable synchronization.
6. Strong tenant and branch isolation.
7. Secure authentication and authorization.
8. Historical data integrity.
9. Transactional consistency for critical operations.
10. Background processing for non-critical workloads.
11. Auditability.
12. Controlled scalability.
13. Failure isolation.
14. Deployment simplicity.
15. Future extensibility without premature complexity.

---

# 3. High-Level Architecture

FastFood ERP uses a **modular application architecture** with clear domain boundaries.

The initial system is not designed as a collection of independent microservices.

The primary architecture is:

```text
                           ┌─────────────────────┐
                           │       Users         │
                           │ Owner / Manager /   │
                           │ Cashier / Waiter /  │
                           │ Cook / Super Admin  │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │     Frontend        │
                           │                     │
                           │ POS / Admin /       │
                           │ Reports / Settings  │
                           │ Offline Client      │
                           └──────────┬──────────┘
                                      │
                              HTTPS / API
                                      │
                                      ▼
                    ┌──────────────────────────────────┐
                    │          Backend Application      │
                    │                                  │
                    │  API Layer                        │
                    │        ↓                         │
                    │  Application Layer               │
                    │        ↓                         │
                    │  Domain Modules                  │
                    │        ↓                         │
                    │  Infrastructure                  │
                    └──────────────┬───────────────────┘
                                   │
                 ┌─────────────────┼──────────────────┐
                 │                 │                  │
                 ▼                 ▼                  ▼
          ┌────────────┐    ┌────────────┐    ┌────────────┐
          │ Database   │    │ Cache      │    │ Job/Queue  │
          └────────────┘    └────────────┘    └─────┬──────┘
                                                     │
                                                     ▼
                                             ┌──────────────┐
                                             │ Workers      │
                                             └──────────────┘
```

The exact technology choices are documented separately.

---

# 4. System Boundary

The FastFood ERP system boundary contains all functionality required to operate the SaaS platform and restaurant branches.

Inside the system boundary:

* Business management;
* Branch management;
* Employee management;
* Authentication;
* Authorization;
* Device trust;
* Subscription management;
* POS;
* Orders;
* Tables;
* Kitchen workflow;
* Payments;
* Debt;
* Refunds;
* Cash sessions;
* Shift handover;
* Inventory;
* Products;
* Recipes;
* Sets;
* Menu;
* Pricing;
* Attendance;
* Payroll;
* Reports;
* Notifications;
* Audit;
* Configuration;
* Offline storage;
* Synchronization;
* Data lifecycle;
* Background jobs.

Outside the core system boundary:

* External payment processors;
* external identity providers;
* external messaging providers;
* external email providers;
* operating system printing services;
* physical printers;
* future online ordering channels;
* future customer applications;
* future third-party integrations.

External systems must interact through explicit integration boundaries.

---

# 5. SaaS Tenant Architecture

The system operates as a multi-tenant SaaS platform.

The primary hierarchy is:

```text
Platform
   │
   ├── Business A
   │      ├── Branch 1
   │      ├── Branch 2
   │      └── Branch N
   │
   ├── Business B
   │      ├── Branch 1
   │      └── Branch N
   │
   └── Business N
```

A Business represents a tenant.

A Branch represents an operational unit belonging to a Business.

All tenant-owned data must be associated with its Business context.

Branch-scoped data must additionally carry Branch context.

---

# 6. Tenant Isolation

Tenant isolation is a mandatory architectural boundary.

Every server-side operation involving Business data must establish the appropriate Business context.

Conceptually:

```text
Authenticated Actor
        ↓
Business Context
        ↓
Permission Validation
        ↓
Branch Context
        ↓
Operation
```

The system must never depend exclusively on frontend filtering for tenant isolation.

Tenant isolation must be enforced through backend application logic and database-level constraints/query boundaries where appropriate.

---

# 7. Branch Isolation

Branch operations require explicit Branch context where applicable.

Example:

```text
Business
   │
   ├── Branch A
   │     ├── Orders
   │     ├── Cash Sessions
   │     ├── Inventory
   │     ├── Employees
   │     └── Configuration
   │
   └── Branch B
         ├── Orders
         ├── Cash Sessions
         ├── Inventory
         ├── Employees
         └── Configuration
```

A user may have access to:

* one Branch;
* multiple Branches;
* all Branches.

The architecture must resolve the effective Branch scope before executing branch-sensitive operations.

---

# 8. Platform Context

Super Admin operates at the platform level.

Platform-level functionality includes:

* Business creation;
* subscription tariff management;
* platform-level limits;
* platform configuration;
* Business lifecycle management.

Super Admin is not automatically a Business employee.

Platform operations must remain separate from normal Business operational workflows.

---

# 9. Business Context

Business is the primary tenant context.

Business-owned functionality includes:

* Branches;
* Employees;
* Roles;
* Permissions;
* Menu;
* Products;
* Recipes;
* Sets;
* Pricing;
* Inventory configuration;
* Reports;
* Payroll;
* Expenses;
* Notifications;
* Business-level configuration.

The Business context is established before executing Business-scoped operations.

---

# 10. Branch Context

Branch context represents the operational environment where restaurant activity occurs.

Branch-sensitive operations include:

* Orders;
* Tables;
* Cash Sessions;
* Inventory;
* Kitchen;
* Employees;
* Attendance;
* Branch configuration;
* Branch pricing;
* Printers;
* Branch reports.

Some Business-level objects may be used by multiple Branches.

For example:

```text
Business Product
      │
      ├── Branch A → Enabled
      ├── Branch B → Enabled
      └── Branch C → Disabled
```

---

# 11. Identity Context

The architecture distinguishes between:

* User identity;
* Employee identity;
* Business membership;
* Branch scope;
* Role;
* Permission;
* Device identity;
* Device trust.

These concepts must not be merged into a single authorization mechanism.

Conceptually:

```text
Employee
   │
   ├── Business Membership
   │
   ├── Roles
   │
   ├── Permission Overrides
   │
   ├── Branch Scope
   │
   └── Device Relationships
```

---

# 12. Authorization Context

Effective authorization is calculated from multiple independent boundaries.

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
       ↓
Effective Operation Authorization
```

The architecture must not treat any single component as sufficient authorization.

For example:

* a trusted device does not grant permission;
* a permission does not bypass subscription restrictions;
* subscription entitlement does not grant employee access;
* Business membership does not automatically grant all Branch access.

---

# 13. Device Context

Each trusted device has its own stable Device UUID.

Devices are associated with:

* Business;
* Branch scope;
* trust state;
* security metadata;
* authorized offline state.

A device is not itself an employee.

An employee may use multiple trusted devices.

Multiple employees may use the same trusted physical workstation at different times, provided the system maintains individual employee identity and authorization.

---

# 14. Online Execution Model

Normal online operation follows:

```text
User
  ↓
Frontend
  ↓
HTTPS
  ↓
API
  ↓
Authentication
  ↓
Authorization
  ↓
Business / Branch Context
  ↓
Application Service
  ↓
Domain Logic
  ↓
Database Transaction
  ↓
Commit
  ↓
Response
```

Secondary operations may continue asynchronously after the core transaction commits.

---

# 15. Offline Execution Model

Offline execution occurs only on trusted devices with valid offline authorization.

Conceptually:

```text
User
  ↓
Offline Frontend
  ↓
Local Authorization
  ↓
Local Application State
  ↓
Encrypted Local Storage
  ↓
Durable Sync Queue
```

When connectivity returns:

```text
Durable Sync Queue
        ↓
Server
        ↓
Authentication / Device Validation
        ↓
Authorization
        ↓
Business / Branch Validation
        ↓
Subscription Validation
        ↓
Domain Validation
        ↓
Idempotency Check
        ↓
Apply / Conflict
```

Offline operation is therefore an extension of the main architecture rather than a separate application.

---

# 16. Server Authority

The server remains authoritative for current system state.

This includes:

* current permissions;
* current employee status;
* current subscription;
* current Branch state;
* current configuration;
* current inventory;
* current payment state;
* current order state;
* current cash state.

Offline operations retain their original UUID and historical context.

The server validates those operations during synchronization.

Server authority does not mean silently discarding valid offline transaction data.

Conflicts must be explicit.

---

# 17. POS Architecture

POS is a high-priority operational subsystem.

POS architecture must minimize unnecessary network dependency and processing overhead.

Conceptually:

```text
POS UI
  ↓
Local POS State
  ↓
Order Application Service
  ↓
Order Domain
  ↓
Inventory / Configuration
  ↓
Transactional Commit
  ↓
Kitchen / Print / Notification Events
```

The POS path must remain optimized for:

* order creation;
* order acceptance;
* order modification;
* payment;
* cash operations;
* table operations.

Heavy operations must not execute synchronously in the main POS path unless required for correctness.

---

# 18. Order and Inventory Boundary

Order acceptance and inventory deduction form a critical transaction boundary.

Conceptually:

```text
Accept Order
     │
     ├── Validate order
     ├── Validate configuration
     ├── Validate permissions
     ├── Validate inventory
     ├── Deduct inventory
     ├── Persist Accepted state
     │
     └── Commit
```

Kitchen notification and printing occur after the critical transaction or through a reliable event mechanism.

If inventory deduction fails, the order must not become Accepted.

---

# 19. Payment Boundary

Payment is a separate financial operation associated with an order.

```text
Order
  │
  └── Payment
       ├── Cash
       ├── Card
       ├── Debt
       └── Mixed
```

Payment creation must validate:

* Business;
* Branch;
* employee;
* permissions;
* order state;
* remaining amount;
* payment method;
* cash session where applicable.

Payment history must remain auditable.

---

# 20. Cash Architecture

Cash operations are associated with:

```text
Branch
  ↓
Cash Register
  ↓
Cash Session
  ↓
Cashier
```

A Cash Session is the operational accounting boundary for physical cash.

The architecture must distinguish:

* physical cash state;
* payment records;
* session state;
* correction transactions;
* handover operations.

A closed session must remain historically closed.

Correction does not mean reopening the original session.

---

# 21. Inventory Architecture

Inventory is a transactional domain.

Critical inventory operations include:

* sale deduction;
* inventory purchase;
* inventory adjustment;
* production of semi-finished products;
* inventory return where permitted;
* discrepancy adjustment.

Stock quantities must be changed through controlled application/domain operations.

Direct unrestricted modification of stock records must not be exposed through generic CRUD.

---

# 22. Configuration Architecture

Configuration affects operational behavior.

Examples:

* menu activation;
* product availability;
* price;
* recipe;
* Set;
* printer routing;
* notification thresholds;
* Branch configuration.

Configuration changes must be versioned and must respect effective-date/session boundaries where required.

Operational transactions must use the appropriate valid configuration snapshot.

---

# 23. Reporting Architecture

Reports operate on operational data but must not block normal POS operations.

Architecture:

```text
Operational Data
      ↓
Consistent Snapshot
      ↓
Report Calculation
      ↓
Report Version
      ↓
Excel Export
```

Small reports may be generated synchronously.

Heavy reports and large Excel exports should use background processing.

Report versions are immutable.

---

# 24. Audit Architecture

Important state-changing operations produce audit information.

Audit data may contain:

* actor;
* Business;
* Branch;
* Device;
* Cash Session;
* Transaction UUID;
* entity;
* previous state;
* new state;
* reason;
* timestamp;
* result;
* source.

Audit persistence must be reliable.

Audit failure must be handled according to the criticality of the audited operation.

---

# 25. Notification Architecture

Notifications are secondary processing.

Example:

```text
Core Transaction
      ↓
Commit
      ↓
Domain/Application Event
      ↓
Notification Processor
      ↓
Notification
```

Notification failure must not normally roll back a completed core business transaction.

Notification delivery must support retry and duplicate prevention.

---

# 26. Printing Architecture

Printing is external to the core transactional state.

```text
Committed Order
      ↓
Print Job
      ↓
Printer Routing
      ↓
Physical Printer
```

A printer may fail independently.

The system must retain the print job state and allow retry.

The ERP transaction remains authoritative.

---

# 27. Background Processing Architecture

Background workers process operations that do not need to block the user workflow.

Examples:

* report generation;
* Excel export;
* notification delivery;
* print retry;
* synchronization;
* subscription lifecycle;
* data deletion;
* cleanup;
* scheduled processing.

Workers must be independently retryable.

---

# 28. Event Boundary

Events are used to communicate that an important operation has occurred.

Examples:

```text
OrderAccepted
PaymentCompleted
CashSessionClosed
InventoryAdjusted
RecipeApproved
PriceChanged
SubscriptionExpired
BusinessDeletionStarted
```

Events should carry stable identifiers and sufficient context for reliable processing.

Events do not replace transactional writes.

---

# 29. Queue Architecture

Queue-backed operations must provide:

* durable state;
* retry;
* idempotency;
* failure handling;
* ordering where required;
* observability.

Typical queue-backed operations include:

```text
Sync Events
Report Jobs
Notification Jobs
Print Jobs
Deletion Jobs
```

Queue processing must not create duplicate financial or inventory effects.

---

# 30. Data Access Boundary

Application services must not expose unrestricted database access to the presentation layer.

The preferred flow is:

```text
Controller / API
      ↓
Application Service
      ↓
Domain
      ↓
Repository / Data Access
      ↓
Database
```

Queries may be optimized separately from transactional domain operations where appropriate.

Read models may be introduced for reports or dashboards without weakening domain integrity.

---

# 31. Read and Write Separation

The architecture may distinguish between:

### Command Path

Used for:

* creating orders;
* accepting orders;
* payments;
* refunds;
* inventory adjustments;
* cash operations;
* configuration changes.

### Query Path

Used for:

* dashboards;
* reports;
* history;
* lists;
* analytics within current scope.

This does not require full CQRS.

The separation exists to keep responsibilities clear and allow performance optimization where required.

---

# 32. Transaction Processing Model

Critical transaction flow:

```text
Request
  ↓
Validate Context
  ↓
Validate Authorization
  ↓
Load Required State
  ↓
Validate Invariants
  ↓
Modify State
  ↓
Record Required History
  ↓
Record Required Audit
  ↓
Commit Transaction
  ↓
Publish/Process Secondary Effects
```

If a required invariant fails before commit, the transaction must fail.

If a secondary effect fails after commit, it must be retried or marked failed without silently reversing the committed core transaction.

---

# 33. Concurrency Model

Concurrency must be handled by authoritative server-side mechanisms.

Important cases:

```text
Concurrent Sale
       ↓
Atomic Stock Validation
       ↓
Only Valid Transaction Commits
```

```text
Concurrent Cash Session Opening
       ↓
Database Constraint / Transaction
       ↓
One Successful Session
```

```text
Concurrent Configuration Update
       ↓
Version Validation
       ↓
Accepted / Rejected
```

```text
Duplicate Synchronization
       ↓
UUID Idempotency
       ↓
Existing Result Reused
```

Frontend timing must never be treated as a concurrency control mechanism.

---

# 34. Idempotency Architecture

Idempotency is mandatory for operations that can be retried.

Important examples:

* synchronization;
* payment requests;
* background jobs;
* report generation;
* notification delivery;
* print jobs;
* data deletion;
* external integration requests.

A stable UUID must allow the system to distinguish:

```text
New Operation
```

from:

```text
Retry of Existing Operation
```

---

# 35. External Integration Boundary

External integrations must not directly modify domain state.

Preferred model:

```text
Internal Application
        ↓
Integration Adapter
        ↓
External System
```

The adapter translates between internal contracts and external contracts.

Future integrations may include:

* payment providers;
* identity providers;
* messaging;
* email;
* online ordering;
* government systems.

External integration failures must be isolated from unrelated internal operations.

---

# 36. Security Boundary for External Systems

External systems must never receive unrestricted internal access.

Each integration must have:

* explicit credentials;
* limited permissions;
* scoped access;
* request validation;
* response validation;
* timeout handling;
* retry policy;
* audit where appropriate.

Secrets must never be stored in source code.

---

# 37. Performance Architecture

The architecture must optimize the critical path.

The most performance-sensitive workflows are:

1. POS order creation;
2. order acceptance;
3. payment;
4. cash operations;
5. table operations;
6. inventory validation;
7. cashier handover.

Performance principles:

* minimize unnecessary API calls;
* avoid synchronous heavy processing;
* use efficient database queries;
* use transactions only where needed;
* cache appropriate read-heavy data;
* process secondary work asynchronously;
* keep local offline operations responsive.

---

# 38. Failure Isolation Model

The architecture separates failures by responsibility.

```text
Core Transaction Failure
        ↓
Core Operation Fails
```

```text
Printer Failure
        ↓
Print Job Failed
        ↓
Retry
```

```text
Notification Failure
        ↓
Notification Failed
        ↓
Retry
```

```text
Report Failure
        ↓
Report Job Failed
        ↓
Retry
```

```text
Sync Conflict
        ↓
Conflict State
        ↓
Authorized Resolution
```

A subsystem must not convert an isolated failure into unnecessary system-wide failure.

---

# 39. Subscription Architecture Boundary

Subscription entitlement is a cross-cutting authorization boundary.

The effective permission for a modifying operation is conceptually:

```text
Employee Permission
        +
Branch Scope
        +
Device Trust
        +
Subscription Entitlement
        ↓
Operation Allowed
```

When subscription expires:

* modifying operations are blocked;
* existing data remains accessible according to policy;
* permitted reports and Excel exports remain available;
* active sessions are not silently destroyed;
* offline authorization is bounded by subscription state and offline authorization rules.

---

# 40. Data Lifecycle Architecture

Business lifecycle is:

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

Deletion must be:

* controlled;
* background processed;
* dependency-aware;
* retryable;
* idempotent;
* protected against concurrent reactivation.

A deleted Business must not be resurrected by stale synchronization data.

---

# 41. Backup Boundary

Backups are an infrastructure concern but must respect application lifecycle semantics.

A backup does not automatically make deleted application data logically active again.

Recovery procedures must distinguish between:

* infrastructure recovery;
* application lifecycle state;
* Business deletion state;
* audit/history requirements.

Backup and disaster recovery details are defined in Deployment and Operations documentation.

---

# 42. Deployment Independence

The logical architecture must not depend on one specific deployment topology.

The same logical components may initially run on a small number of servers and later be separated.

For example:

```text
Initial
────────────────────────
Frontend
Backend
Database
Worker
```

Later:

```text
Frontend
    │
    ▼
Backend Cluster
    │
    ├── Database
    ├── Cache
    └── Worker Pool
```

Logical boundaries must therefore be established before physical scaling.

---

# 43. Scalability Direction

The architecture should scale in the following order:

```text
Optimize Code
      ↓
Optimize Database
      ↓
Add Caching
      ↓
Move Heavy Jobs to Workers
      ↓
Scale Application Instances
      ↓
Scale Specialized Components
```

Microservices are not the default scaling mechanism.

A component should be separated only when operational requirements justify it.

---

# 44. Architecture Anti-Patterns

The following patterns are prohibited or strongly discouraged:

### 44.1. Frontend-Only Authorization

```text
Frontend says user can do it
        ↓
Backend trusts frontend
```

Not allowed.

### 44.2. Direct Database Manipulation From UI

Frontend must not directly modify persistent business data.

### 44.3. Generic CRUD for Critical Transactions

Financial, inventory, cash, and order state changes must use controlled application operations.

### 44.4. Silent Conflict Resolution

Conflicts must not be silently overwritten.

### 44.5. Silent Data Loss

Failed synchronization must retain the original transaction/event until resolved.

### 44.6. Printer-Driven Transactions

A printer response must not determine whether an ERP transaction is committed.

### 44.7. Heavy POS Requests

Large reports, exports, cleanup, or deletion jobs must not unnecessarily block POS operations.

### 44.8. Premature Microservices

The number of business domains alone is not sufficient justification for separate deployable services.

---

# 45. Architecture Traceability

This architecture is derived from:

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/01_System_Context_and_Boundaries.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`

### Domain Analysis

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

---

# 46. Related Architecture Documents

* `docs/04_Architecture/README.md`
* `docs/04_Architecture/02_Application_Layer_Architecture.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/04_Backend_Architecture.md`
* `docs/04_Architecture/05_Frontend_Architecture.md`
* `docs/04_Architecture/06_API_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/08_Offline_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/10_Security_Architecture.md`
* `docs/04_Architecture/11_Background_Processing_Architecture.md`
* `docs/04_Architecture/12_Event_and_Message_Architecture.md`
* `docs/04_Architecture/13_Caching_Architecture.md`
* `docs/04_Architecture/14_Printing_and_Device_Integration_Architecture.md`
* `docs/04_Architecture/15_Observability_Architecture.md`
* `docs/04_Architecture/16_Deployment_Architecture.md`
* `docs/04_Architecture/17_Scalability_and_Performance_Architecture.md`
* `docs/04_Architecture/18_Failure_Recovery_Architecture.md`
* `docs/04_Architecture/19_Configuration_and_Secrets_Architecture.md`
* `docs/04_Architecture/20_Architecture_Integration_and_Traceability.md`

---

# 47. Final Status

**Status:** Accepted

This document establishes the high-level system architecture for FastFood ERP.

It defines the main system boundaries, logical components, execution models, transaction boundaries, security boundaries, offline architecture, background processing, concurrency principles, and scalability direction.

Detailed implementation decisions must be defined in the corresponding Architecture documents and ADRs.

**Next document:**

`docs/04_Architecture/02_Application_Layer_Architecture.md`

