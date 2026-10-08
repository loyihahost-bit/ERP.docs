# Database Documentation

**Document ID:** DB-README
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `README.md`

---

## 1. Purpose

This directory defines the database model, persistence rules, integrity constraints, security boundaries, operational strategies and recovery requirements of FastFood ERP.

The database is a critical source of system truth.

These documents define:

* database architecture;
* tenant and branch data isolation;
* identity and access persistence;
* product, recipe and inventory models;
* menu and pricing persistence;
* order and payment data;
* cash and shift data;
* employee and payroll data;
* audit and history;
* reports;
* offline synchronization;
* configuration;
* data lifecycle;
* integrity constraints;
* indexes and query strategy;
* migrations;
* backup and recovery;
* database security;
* database invariants and guardrails.

The database design must preserve **tenant isolation, historical integrity, transactional correctness, security and operational recoverability**.

---

## 2. Database Architecture Summary

FastFood ERP uses a PostgreSQL-based relational database.

The initial architecture uses:

```text
Application
    ↓
Service / Use Case Layer
    ↓
Repository / Data Access Layer
    ↓
PostgreSQL
```

The database is authoritative for server-side persistent state.

The initial architecture uses:

* one PostgreSQL database;
* one primary application schema by default;
* Business-based tenant isolation;
* Branch-level operational scoping;
* UUID-based entity identity;
* relational foreign keys;
* database constraints;
* transactional writes;
* targeted row locking;
* migration-controlled schema changes.

The system does **not** use a separate database for every Business or Branch in the initial architecture.

---

## 3. Core Database Principles

### 3.1. Business Isolation

Every Business-owned record must remain associated with the correct Business.

Cross-Business references are prohibited.

A Business UUID must never be reused.

### 3.2. Branch Isolation

Branch-scoped records must identify their Branch where applicable.

A Branch-scoped operation must never accidentally affect another Branch.

### 3.3. Historical Integrity

Historical business records must not be silently rewritten.

Important historical information is represented through:

* snapshots;
* versions;
* immutable history;
* correction records;
* audit records.

### 3.4. Transactional Integrity

Core business operations must be atomic where required.

Examples include:

* order acceptance;
* inventory deduction;
* payment recording;
* cash operations;
* shift handover;
* important configuration changes.

### 3.5. Application + Database Enforcement

Database constraints provide structural protection.

Application services enforce business rules.

Neither layer should be treated as a replacement for the other.

### 3.6. Server Authority

The server database remains authoritative after synchronization.

Offline devices may temporarily maintain local state, but synchronization must reconcile that state with authoritative server data.

---

# 4. Database Documentation Map

The database documentation is organized into the following sequence.

---

## 4.1. Foundation

### 01. Database Overview

`01_Database_Overview.md`

Defines the purpose, scope and high-level database responsibilities.

### 02. Database Architecture

`02_Database_Architecture.md`

Defines the overall PostgreSQL architecture, persistence boundaries, transaction ownership, connection management and architectural principles.

---

## 4.2. Tenant and Organizational Structure

### 03. Tenant and Business Data Model

`03_Tenant_and_Business_Data_Model.md`

Defines Business-level tenancy and Business-owned data relationships.

### 04. Identity and Access Data Model

`04_Identity_and_Access_Data_Model.md`

Defines users, employees, roles, permissions and access-related persistence.

### 05. Branch and Organizational Data Model

`05_Branch_and_Organizational_Data_Model.md`

Defines Branches and organizational relationships.

### 06. Subscription and Entitlement Data Model

`06_Subscription_and_Entitlement_Data_Model.md`

Defines subscription state, tariff relationships and entitlement persistence.

### 07. Device and Trust Data Model

`07_Device_and_Trust_Data_Model.md`

Defines trusted devices, device identity, authorization state and device-related persistence.

---

## 4.3. Product and Inventory Domain

### 08. Product and Category Data Model

`08_Product_and_Category_Data_Model.md`

Defines Products, categories, product identity and product classification.

### 09. Recipe and Recipe Version Data Model

`09_Recipe_and_Recipe_Version_Data_Model.md`

Defines Recipes, Recipe Versions, approval and historical recipe state.

### 10. Set and Set Version Data Model

`10_Set_and_Set_Version_Data_Model.md`

Defines Sets, Set components, Set Versions and historical Set configuration.

### 11. Inventory and Warehouse Data Model

`11_Inventory_and_Warehouse_Data_Model.md`

Defines warehouses, stock, inventory transactions, FIFO-related persistence, purchases, adjustments and inventory history.

### 12. Menu and Pricing Data Model

`12_Menu_and_Pricing_Data_Model.md`

Defines Business menu, Branch menu configuration, prices, Branch overrides and pricing history.

---

## 4.4. Order and Financial Operations

### 13. Order and Order Item Data Model

`13_Order_and_Order_Item_Data_Model.md`

Defines Orders, Order Items, order snapshots, operational state and historical transaction information.

### 14. Table and Waiter Data Model

`14_Table_and_Waiter_Data_Model.md`

Defines halls, tables, table state and waiter-related operational relationships.

### 15. Payment and Debt Data Model

`15_Payment_and_Debt_Data_Model.md`

Defines payments, payment methods, mixed payments, debt and repayment information.

### 16. Cash Register and Cash Session Data Model

`16_Cash_Register_and_Cash_Session_Data_Model.md`

Defines Branch cash registers, Cash Sessions, opening, closing and cash reconciliation data.

### 17. Shift Handover Data Model

`17_Shift_Handover_Data_Model.md`

Defines cashier handover, cash counting, acceptance and discrepancy-related persistence.

---

## 4.5. Employees and Supporting Operations

### 18. Employee Attendance and Payroll Data Model

`18_Employee_Attendance_and_Payroll_Data_Model.md`

Defines attendance, payroll calculations, salary configurations, bonuses and payment history.

### 19. Notification Data Model

`19_Notification_Data_Model.md`

Defines notification events, recipients, delivery state, read state and notification history.

### 20. Audit and History Data Model

`20_Audit_and_History_Data_Model.md`

Defines immutable audit events, change history, correction chains and historical traceability.

### 21. Report and Report Version Data Model

`21_Report_and_Report_Version_Data_Model.md`

Defines report generation, report snapshots, immutable report versions and report history.

---

## 4.6. Distributed and Configuration State

### 22. Offline and Synchronization Data Model

`22_Offline_and_Synchronization_Data_Model.md`

Defines offline transaction persistence, synchronization state, idempotency and conflict-related data.

### 23. Configuration Data Model

`23_Configuration_Data_Model.md`

Defines system and business configuration, configuration versions, effective state and configuration history.

### 24. Data Lifecycle and Deletion Data Model

`24_Data_Lifecycle_and_Deletion_Data_Model.md`

Defines Business lifecycle, read-only state, deletion eligibility, deletion processing and historical deletion boundaries.

---

## 4.7. Database Engineering

### 25. Database Integrity and Constraints

`25_Database_Integrity_and_Constraints.md`

Defines foreign keys, uniqueness, check constraints, nullability and other structural integrity rules.

### 26. Database Indexes and Query Strategy

`26_Database_Indexes_and_Query_Strategy.md`

Defines indexing strategy, query patterns, high-frequency queries and performance considerations.

### 27. Database Migrations and Change Management

`27_Database_Migrations_and_Change_Management.md`

Defines schema migration strategy, Alembic usage, migration safety and expand/contract changes.

### 28. Database Backup and Recovery

`28_Database_Backup_and_Recovery.md`

Defines backup strategy, WAL/PITR, retention, restore procedures, recovery objectives and disaster recovery.

### 29. Database Security

`29_Database_Security.md`

Defines database-level security, access control, encryption, isolation, backup security and security monitoring.

### 30. Database Invariants and Guardrails

`30_Database_Invariants_and_Guardrails.md`

Defines the final database-wide invariants and guardrails that must remain true across all domains.

---

# 5. Recommended Reading Order

Agents and developers should normally read the documents in this order:

```text
01 Overview
   ↓
02 Architecture
   ↓
03 Tenant / Business
   ↓
04 Identity / Access
   ↓
05 Branch
   ↓
06 Subscription
   ↓
07 Device / Trust
   ↓
08 Product
   ↓
09 Recipe
   ↓
10 Set
   ↓
11 Inventory
   ↓
12 Menu / Pricing
   ↓
13 Orders
   ↓
14 Tables / Waiters
   ↓
15 Payments / Debt
   ↓
16 Cash Register / Sessions
   ↓
17 Shift Handover
   ↓
18 Attendance / Payroll
   ↓
19 Notifications
   ↓
20 Audit / History
   ↓
21 Reports
   ↓
22 Offline / Synchronization
   ↓
23 Configuration
   ↓
24 Data Lifecycle
   ↓
25 Integrity / Constraints
   ↓
26 Indexes / Query Strategy
   ↓
27 Migrations
   ↓
28 Backup / Recovery
   ↓
29 Security
   ↓
30 Invariants / Guardrails
```

For implementation work, an Agent does not necessarily need to read every document for every task.

The relevant domain document should be read first, followed by its referenced cross-cutting documents.

---

# 6. Domain Dependency Map

The major database dependencies are:

```text
Business
 ├── Branch
 ├── Employee / Role / Permission
 ├── Subscription
 ├── Device
 ├── Product
 │    ├── Category
 │    ├── Recipe
 │    │    └── Recipe Version
 │    └── Set
 │         └── Set Version
 │
 ├── Warehouse
 │    └── Inventory
 │
 ├── Menu
 │    └── Pricing
 │
 ├── Order
 │    └── Order Item
 │
 ├── Payment
 │    └── Debt
 │
 ├── Cash Register
 │    └── Cash Session
 │         └── Shift Handover
 │
 ├── Attendance
 │    └── Payroll
 │
 ├── Notification
 ├── Audit / History
 ├── Report / Report Version
 ├── Offline / Synchronization
 ├── Configuration
 └── Data Lifecycle
```

This map represents logical ownership and dependency, not necessarily physical schema layout.

---

# 7. Cross-Cutting Database Concerns

The following concerns apply across multiple database domains.

## 7.1. UUID Identity

Persistent business entities use UUID-based identity.

UUIDs provide stable entity identity and support:

* offline creation;
* synchronization;
* idempotency;
* distributed request handling;
* historical references.

UUID identity must not be confused with human-facing numbers.

---

## 7.2. Tenant Scope

Business UUID is the primary tenant boundary.

Where a record is Branch-scoped, Branch UUID provides the additional operational boundary.

Queries must never rely on UI-selected Branch state alone.

The server must validate scope.

---

## 7.3. Historical Snapshots

Transactions that depend on mutable configuration must preserve the applicable historical state.

Examples:

* Order Item price;
* discount;
* payment information;
* Recipe Version;
* Set Version;
* configuration version;
* report version.

Current configuration must not reinterpret historical transactions.

---

## 7.4. Immutability

The following categories are generally immutable after creation:

* important audit events;
* historical report versions;
* completed payment revisions;
* historical configuration versions;
* historical inventory transactions;
* correction records.

Corrections must create a new state or correction record instead of silently modifying history.

---

## 7.5. Idempotency

Operations that may be retried must use stable operation UUIDs where appropriate.

This is particularly important for:

* offline synchronization;
* payment recording;
* order synchronization;
* configuration changes;
* audit/outbox processing.

Repeated delivery must not create duplicate business effects.

---

## 7.6. Transactions

The service/use-case layer owns business transactions.

The database provides:

* atomicity;
* consistency;
* isolation;
* durability;
* locking;
* constraint enforcement.

Core transaction boundaries must be explicit.

---

## 7.7. Concurrency

Concurrent updates must be controlled through appropriate mechanisms such as:

* optimistic version checks;
* unique constraints;
* row locks;
* transaction isolation;
* atomic updates.

Important configuration changes must not use uncontrolled silent last-write-wins behavior.

---

## 7.8. Offline Synchronization

Offline data is temporary local operational state.

After synchronization:

```text
Offline Device
      ↓
Synchronization
      ↓
Validation
      ↓
PostgreSQL
      ↓
Authoritative Server State
```

The database must reject stale, unauthorized or lifecycle-invalid events.

---

## 7.9. Auditability

Important changes must remain attributable to:

* Business;
* Branch where applicable;
* Employee;
* Device where applicable;
* transaction;
* timestamp;
* source.

Audit data must not be treated as ordinary mutable application data.

---

## 7.10. Data Lifecycle

Business deletion is a controlled lifecycle.

The live database must distinguish between:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

Deletion must be controlled, idempotent and auditable.

Database backup retention is separate from live Business deletion.

---

# 8. Core Database Invariants

The following high-level invariants apply to the entire database.

1. A Business must never access another Business's data.
2. A Branch must belong to exactly one Business.
3. Branch-scoped data must remain within its Business.
4. Business UUIDs are never reused.
5. Historical transaction data must remain reconstructable.
6. Important historical records must not be silently overwritten.
7. Core financial operations must remain atomic.
8. Inventory must never become negative.
9. Historical prices must not change when current prices change.
10. Historical Recipe Versions must remain identifiable.
11. Historical Set Versions must remain identifiable.
12. Payment history must remain traceable.
13. Closed Cash Sessions must not be reopened.
14. Audit records must remain immutable.
15. Report versions must remain immutable.
16. Offline retries must be idempotent.
17. Stale synchronization must not overwrite newer authoritative state.
18. Offline data must not bypass Business lifecycle restrictions.
19. Subscription restrictions must not be bypassed through direct database operations.
20. Database schema changes must be migration-controlled.
21. Important database access must be security-controlled.
22. Backup and recovery procedures must preserve database integrity.
23. Deletion must not break unrelated Business data.
24. Referential integrity must remain valid.
25. Database constraints must protect structural invariants.
26. Application services must enforce business invariants that cannot be expressed safely through database constraints alone.

The complete invariant set is defined in:

`30_Database_Invariants_and_Guardrails.md`

---

# 9. Database Implementation Guidance

The implementation should follow these rules.

### 9.1. ORM

SQLAlchemy may be used as the primary application data-access technology.

ORM models must reflect the accepted database model rather than becoming the source of business rules.

### 9.2. Migrations

Alembic must be used for schema changes.

Production schema changes must never depend on manually editing the database.

### 9.3. Transactions

Business-critical service operations must define explicit transaction boundaries.

### 9.4. Queries

High-frequency POS queries must remain lightweight.

Historical analysis must not unnecessarily slow operational transactions.

### 9.5. Indexes

Indexes should be created according to real query patterns.

Indexes must not be added blindly to every column.

### 9.6. Constraints

Important structural rules should be enforced at database level whenever practical.

### 9.7. Security

Database credentials, secrets and encryption keys must never be stored in source code.

Database access must use least privilege.

### 9.8. Backups

Backups must be automated, monitored and periodically restored in a controlled environment.

A backup that has never been successfully restored must not be treated as proven recovery capability.

---

# 10. Database vs Application Responsibility

Not every rule belongs exclusively to the database.

### Database responsibilities

* foreign keys;
* uniqueness;
* check constraints;
* referential integrity;
* transactional atomicity;
* locking;
* structural consistency;
* durable persistence.

### Application responsibilities

* authorization;
* subscription entitlement;
* workflow validation;
* business-specific state transitions;
* permission evaluation;
* offline authorization;
* conflict resolution;
* complex domain calculations.

### Shared responsibility

Some rules require both layers.

Examples:

* tenant isolation;
* historical integrity;
* concurrency;
* idempotency;
* financial correctness;
* lifecycle deletion;
* synchronization consistency.

The implementation must avoid relying on application code alone for rules that can be safely protected structurally by PostgreSQL.

---

# 11. Performance Principles

Database performance must support normal POS hardware.

The system should prioritize:

* short transactions;
* efficient indexes;
* bounded queries;
* predictable query plans;
* appropriate connection pooling;
* minimal locking;
* asynchronous secondary processing;
* efficient synchronization batches.

Heavy operations such as:

* large report generation;
* historical analysis;
* export preparation;
* notification processing;
* background reconciliation

should not block normal POS transactions unnecessarily.

Future scaling options may include:

* read replicas;
* partitioning;
* specialized reporting storage;
* caching.

These are not required for the initial architecture unless justified by measured workload.

---

# 12. Recovery and Operational Safety

Database recovery must account for the entire system state.

Recovery design includes:

```text
PostgreSQL
   +
WAL / PITR
   +
Backups
   +
Application State
   +
Outbox / Background Jobs
   +
Offline Synchronization State
   +
Idempotency
```

Restoring the database alone must not create duplicate financial or synchronization effects.

Recovery procedures must therefore consider:

* transaction identity;
* synchronization state;
* outbox processing;
* device state;
* report versions;
* audit history;
* configuration versions.

---

# 13. Security Boundary

The database is not considered secure merely because it is not publicly exposed.

Security must include:

* least-privilege database users;
* protected credentials;
* encrypted transport;
* controlled network access;
* tenant isolation;
* secure backups;
* audit protection;
* migration controls;
* sensitive-data protection;
* restore controls.

Detailed rules are defined in:

`29_Database_Security.md`

---

# 14. Change Management

Database changes must follow:

```text
Requirement
   ↓
System / Domain Analysis
   ↓
Database Model Change
   ↓
Migration Design
   ↓
Migration
   ↓
Testing
   ↓
Deployment
```

A schema change must not silently contradict an accepted Business Analysis or System Analysis rule.

When a requirement changes, related documentation must be reviewed before changing the database implementation.

---

# 15. Agent Navigation Rules

Agents working on database-related implementation should follow these rules.

### Rule 1 — Read the relevant domain document first

For example:

```text
Payment task
→ 15_Payment_and_Debt_Data_Model.md
```

### Rule 2 — Read dependencies

For a payment task, related documents may include:

```text
13_Order_and_Order_Item_Data_Model.md
16_Cash_Register_and_Cash_Session_Data_Model.md
20_Audit_and_History_Data_Model.md
```

### Rule 3 — Check cross-cutting constraints

For changes affecting persistence, also review where relevant:

```text
25_Database_Integrity_and_Constraints.md
26_Database_Indexes_and_Query_Strategy.md
27_Database_Migrations_and_Change_Management.md
29_Database_Security.md
30_Database_Invariants_and_Guardrails.md
```

### Rule 4 — Do not invent database behavior

If a required behavior is not defined, the Agent must not silently introduce a conflicting business rule.

The appropriate requirement or analysis document must be updated first when necessary.

### Rule 5 — Preserve historical integrity

Do not solve corrections by deleting or silently overwriting historical records.

### Rule 6 — Preserve tenant isolation

Every query and mutation involving Business-owned data must respect Business scope.

### Rule 7 — Check migration impact

Every schema change must consider:

* existing records;
* foreign keys;
* indexes;
* constraints;
* migrations;
* rollback/recovery;
* offline synchronization;
* historical data.

---

# 16. Related Documentation

### Business Analysis

* `../01_Business_Analysis/README.md`
* `../01_Business_Analysis/02_Business_Model.md`
* `../01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `../01_Business_Analysis/08_POS_and_Order_Management.md`
* `../01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `../01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `../01_Business_Analysis/12_Products_and_Recipes.md`
* `../01_Business_Analysis/13_Menu_and_Pricing.md`
* `../01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `../01_Business_Analysis/16_Reports_and_Dashboards.md`
* `../01_Business_Analysis/18_Audit_and_Change_History.md`
* `../01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `../02_System_Analysis/README.md`
* `../02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `../02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `../02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `../02_System_Analysis/07_POS_and_Order_System.md`
* `../02_System_Analysis/16_Inventory_Transaction_System.md`
* `../02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `../02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `../02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `../02_System_Analysis/22_Audit_and_History.md`
* `../02_System_Analysis/23_Offline_Operation.md`
* `../02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `../02_System_Analysis/25_Subscription_and_Entitlement.md`
* `../02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `../02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `../02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `../02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `01_Database_Overview.md`
* `02_Database_Architecture.md`
* `03_Tenant_and_Business_Data_Model.md`
* `04_Identity_and_Access_Data_Model.md`
* `05_Branch_and_Organizational_Data_Model.md`
* `06_Subscription_and_Entitlement_Data_Model.md`
* `07_Device_and_Trust_Data_Model.md`
* `08_Product_and_Category_Data_Model.md`
* `09_Recipe_and_Recipe_Version_Data_Model.md`
* `10_Set_and_Set_Version_Data_Model.md`
* `11_Inventory_and_Warehouse_Data_Model.md`
* `12_Menu_and_Pricing_Data_Model.md`
* `13_Order_and_Order_Item_Data_Model.md`
* `14_Table_and_Waiter_Data_Model.md`
* `15_Payment_and_Debt_Data_Model.md`
* `16_Cash_Register_and_Cash_Session_Data_Model.md`
* `17_Shift_Handover_Data_Model.md`
* `18_Employee_Attendance_and_Payroll_Data_Model.md`
* `19_Notification_Data_Model.md`
* `20_Audit_and_History_Data_Model.md`
* `21_Report_and_Report_Version_Data_Model.md`
* `22_Offline_and_Synchronization_Data_Model.md`
* `23_Configuration_Data_Model.md`
* `24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `25_Database_Integrity_and_Constraints.md`
* `26_Database_Indexes_and_Query_Strategy.md`
* `27_Database_Migrations_and_Change_Management.md`
* `28_Database_Backup_and_Recovery.md`
* `29_Database_Security.md`
* `30_Database_Invariants_and_Guardrails.md`

---

# 17. Status

**Database Documentation:** Completed

**Documents:** 30

**Database Architecture:** Accepted

**Database Design Principle:**

> The database must preserve tenant isolation, transactional correctness, historical integrity, security and recoverability while remaining efficient enough for everyday POS operations.

**Current Section:** `docs/05_Database/`

**Next Documentation Section:** `docs/06_Backend/`

