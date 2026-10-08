# Database Invariants and Guardrails

**Document ID:** DB-30
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

---

## 1. Purpose

This document defines the database invariants, guardrails and non-negotiable consistency rules for FastFood ERP.

An invariant is a condition that must remain true throughout the lifetime of the system.

A guardrail is a technical or architectural control that prevents, detects or limits operations that could violate an invariant.

The purpose of this document is to provide a final database-level reference for:

* data integrity;
* tenant isolation;
* Branch isolation;
* identity integrity;
* authorization boundaries;
* financial integrity;
* inventory integrity;
* historical integrity;
* configuration integrity;
* synchronization integrity;
* lifecycle integrity;
* backup and recovery integrity;
* security;
* concurrency;
* performance protection.

---

## 2. Scope

This document applies to all database-backed domains, including:

* Business;
* Branch;
* Employee;
* Role;
* Permission;
* Subscription;
* Device;
* Product;
* Category;
* Recipe;
* Recipe Version;
* Set;
* Set Version;
* Warehouse;
* Inventory;
* Menu;
* Pricing;
* Order;
* Order Item;
* Table;
* Payment;
* Debt;
* Cash Register;
* Cash Session;
* Shift Handover;
* Attendance;
* Payroll;
* Notification;
* Audit;
* Report;
* Configuration;
* Synchronization;
* Data Lifecycle;
* Backup and Recovery metadata.

---

## 3. Invariant Classification

Database invariants are classified into:

### 3.1. Structural Invariants

Rules enforced primarily through:

* primary keys;
* foreign keys;
* unique constraints;
* check constraints;
* not-null constraints;
* data types.

### 3.2. Transactional Invariants

Rules that must remain true within a transaction.

Examples:

* payment belongs to the correct Order;
* inventory deduction and Order acceptance are atomic;
* cash session state changes are consistent.

### 3.3. Application Invariants

Rules that require application/service-layer logic.

Examples:

* employee permission;
* subscription entitlement;
* Branch scope;
* approval workflow.

### 3.4. Historical Invariants

Rules protecting immutable historical information.

Examples:

* paid Order price;
* historical Payment;
* Audit Event;
* Report Version.

### 3.5. Security Invariants

Rules preventing unauthorized access or mutation.

### 3.6. Synchronization Invariants

Rules ensuring offline and online state converges safely.

### 3.7. Lifecycle Invariants

Rules controlling archival, deletion and Business lifecycle.

---

## 4. Defense-in-Depth Principle

No single control should be assumed to protect the entire system.

The preferred model is:

```text
API Authentication
        ↓
Business Context
        ↓
Branch Scope
        ↓
Permission
        ↓
Subscription Entitlement
        ↓
Service Validation
        ↓
Transaction
        ↓
Database Constraints
        ↓
Audit / History
```

A database constraint does not replace authorization.

Application authorization does not replace database integrity.

Audit does not replace transaction correctness.

---

# 5. Identity Invariants

## 5.1. Primary Identity

Every persistent entity requiring independent identity must have a stable primary identifier.

## 5.2. UUID Uniqueness

UUIDs used as entity identities must be globally unique.

## 5.3. UUID Immutability

An entity UUID must not change during its lifetime.

## 5.4. UUID Reuse

Deleted or archived entity UUIDs must never be reused.

## 5.5. Client Identity

Client-generated UUIDs must not automatically imply authorization.

## 5.6. Operation Identity

Retryable operations must have unique operation identifiers where idempotency is required.

## 5.7. Idempotency Identity

An idempotency UUID must represent one logical operation.

Repeated delivery of the same operation must not create duplicate business effects.

---

# 6. Business/Tenant Invariants

## 6.1. Business as Tenant Boundary

Business is the primary tenant boundary.

## 6.2. Business UUID

Every Business has one stable Business UUID.

## 6.3. Business UUID Never Reused

A Business UUID must never be assigned to another Business.

## 6.4. Business-Owned Records

Every Business-owned record must be directly or indirectly traceable to exactly one Business.

## 6.5. Cross-Business References

Business A must not reference Business B operational data unless the relationship is explicitly platform-level.

## 6.6. Cross-Business Foreign Keys

Foreign keys must not allow accidental cross-Business relationships.

## 6.7. Business Isolation

Queries must not return another Business's records.

## 6.8. Business Context

Every tenant-sensitive operation must execute with explicit Business context.

## 6.9. Missing Business Context

A tenant-sensitive operation without valid Business context must fail.

## 6.10. Business Context Leakage

Business context must never leak between pooled database connections or background jobs.

---

# 7. Branch Invariants

## 7.1. Branch Ownership

Every Branch belongs to exactly one Business.

## 7.2. Branch UUID

Every Branch has a stable UUID.

## 7.3. Branch-Business Consistency

A Branch UUID must never be used with a different Business UUID.

## 7.4. Branch Scope

Branch-scoped operations must validate the employee's Branch authority.

## 7.5. Cross-Branch Isolation

Branch A operations must not modify Branch B data without explicit authority.

## 7.6. Branch Configuration

Branch configuration affects only the selected Branch unless a Business-level operation explicitly changes it.

## 7.7. Branch Switching

Changing Branch context must recalculate:

* permissions;
* menu;
* pricing;
* operational scope;
* inventory scope.

## 7.8. Branch Deletion

Branch deletion must preserve required historical records.

## 7.9. Branch UUID Reuse

Branch UUIDs must not be reused.

---

# 8. Employee and Access Invariants

## 8.1. Employee Ownership

Every employee belongs to a Business.

## 8.2. Employee Branch Scope

Branch assignment must reference Branches belonging to the same Business.

## 8.3. Employee Deactivation

A deactivated employee cannot perform new authorized operations.

## 8.4. Historical Employee Identity

Historical records retain the original employee identity.

## 8.5. Role Permission

Role permissions define the baseline authorization.

## 8.6. Employee Override

Employee-specific overrides may modify effective permissions within allowed limits.

## 8.7. Permission Boundary

An employee cannot grant themselves additional authority.

## 8.8. Manager Boundary

A Manager cannot grant permissions beyond their own authorized scope.

## 8.9. Owner Boundary

Owner authority remains limited to the Business.

## 8.10. Super Admin Boundary

Super Admin is a platform-level role and is not a normal Business Owner.

## 8.11. Permission Evaluation

Effective permission is determined from:

```text
Role Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
+
Employee State
```

## 8.12. Frontend Permission

Frontend permission checks are not authoritative.

Server-side authorization is mandatory.

---

# 9. Subscription Invariants

## 9.1. Subscription Ownership

A subscription belongs to exactly one Business.

## 9.2. Entitlement Authority

Subscription state is authoritative for feature and limit enforcement.

## 9.3. Tariff Limits

Branch, employee, owner and feature limits must be validated server-side.

## 9.4. Expired Subscription

Expired subscription must not permit blocked modifying operations.

## 9.5. READ_ONLY State

READ_ONLY Businesses may remain accessible for permitted viewing, reporting and export.

## 9.6. Offline Bypass

Offline operation must not bypass subscription restrictions.

## 9.7. Historical Access

Subscription expiry must not rewrite historical data.

## 9.8. Deletion Eligibility

A Business becomes deletion-eligible only according to the defined lifecycle rules.

## 9.9. Deletion Retention

The current Business deletion retention period is 60 days unless changed by an approved business/system decision.

---

# 10. Device Invariants

## 10.1. Device Identity

Every trusted device has a stable Device UUID.

## 10.2. Device Ownership

A device belongs to a defined Business context.

## 10.3. Device Branch Scope

Where Branch-scoped, the device's authorized Branch scope must be explicit.

## 10.4. Trusted Device

Trusted-device status does not replace employee authorization.

## 10.5. Device Revocation

A revoked device cannot create new authorized synchronized operations.

## 10.6. Offline Authorization

Offline authorization must be:

* signed;
* time-bounded;
* Business-scoped;
* Branch-scoped where applicable.

## 10.7. Offline Grace

Offline operation is subject to the defined authorization/grace period.

## 10.8. Device Theft

Device loss or theft must allow server-side revocation.

## 10.9. Device Identity Reuse

Device UUIDs must not be reused for a different physical/device identity.

---

# 11. Product Invariants

## 11.1. Product Ownership

Every Product belongs to exactly one Business.

## 11.2. Product Identity

Menu changes must not create a new Product identity unless a genuinely new Product is created.

## 11.3. Product Category

Every active Product belongs to exactly one menu category.

## 11.4. Product Archive

Products with historical dependencies must be archived rather than physically deleted.

## 11.5. Historical Product Identity

Historical Orders retain the original Product identity.

## 11.6. Product Activation

Inactive Products cannot be newly sold.

## 11.7. Historical Product Data

Product deactivation must not remove historical Order, Inventory or Recipe references.

---

# 12. Recipe Invariants

## 12.1. Recipe Ownership

Every Recipe belongs to the same Business as its Product.

## 12.2. Recipe Versioning

Operational Recipe changes create a new Recipe Version.

## 12.3. Historical Recipe Version

Historical Inventory deductions must retain the Recipe Version used.

## 12.4. Recipe Approval

A required Recipe must be approved before normal sale.

## 12.5. Recipe History

Historical Recipe Versions must not be silently overwritten.

## 12.6. Recipe Deletion

A Recipe with historical dependencies must not be physically deleted.

## 12.7. Recipe Components

Recipe components must belong to the same Business context.

## 12.8. Circular Dependency

Recipe dependency cycles must be prohibited.

Example:

```text
A → B → A
```

must not be valid.

## 12.9. Quantity Validity

Recipe component quantities must satisfy defined positive/valid quantity constraints.

---

# 13. Set Invariants

## 13.1. Set Ownership

Every Set belongs to exactly one Business.

## 13.2. Set Versioning

Operational Set composition changes must create a new Set Version where required.

## 13.3. Set Price

A Set has its own selling price.

## 13.4. Set Component Integrity

Mandatory Set components must reference valid Products/configurations.

## 13.5. Component Substitution

Normal Set sale does not permit unauthorized component substitution.

## 13.6. Historical Set Sales

Historical Set Orders retain the applicable Set configuration and price snapshot.

---

# 14. Inventory Invariants

## 14.1. Inventory Ownership

Inventory belongs to a Business and appropriate Branch/Warehouse context.

## 14.2. Warehouse Ownership

A Warehouse belongs to exactly one Business.

## 14.3. Branch Ownership

A Branch Warehouse cannot belong to another Business.

## 14.4. Negative Stock

Negative stock is prohibited.

## 14.5. Atomic Deduction

Order acceptance and required inventory deduction must be atomic.

## 14.6. Insufficient Stock

A transaction requiring unavailable stock must not be accepted unless an explicitly approved business rule permits it.

Current business rule: negative stock is not allowed.

## 14.7. Inventory Transaction History

Inventory Transactions are historical records and must not be silently rewritten.

## 14.8. FIFO Integrity

FIFO layers must remain internally consistent.

## 14.9. Purchase Cost

Purchase cost must not automatically rewrite historical selling prices.

## 14.10. Last Purchase Cost

Last Purchase Cost must represent the applicable latest purchase state.

## 14.11. Inventory Adjustment

Manual stock adjustments require authorization.

## 14.12. Inventory Count

Physical count discrepancies must be represented explicitly.

## 14.13. Recipe Deduction

Recipe-based sales must deduct the correct Recipe components.

## 14.14. Semi-Finished Products

Semi-finished Products must preserve their component dependency.

---

# 15. Menu Invariants

## 15.1. Global Menu

Global Menu is Business-scoped.

## 15.2. Branch Menu

Branch Menu configuration is Branch-scoped.

## 15.3. Global-to-Branch

Global Product configuration does not automatically make a Product sellable in every Branch.

## 15.4. Branch Isolation

Disabling a Product in Branch A does not disable it in Branch B.

## 15.5. Inventory Separation

Menu availability and inventory availability are separate states.

## 15.6. Equipment Availability

Equipment failure does not alter Product identity, Recipe history or historical prices.

---

# 16. Pricing Invariants

## 16.1. Standard Price

A Product may have a Business-level standard selling price.

## 16.2. Branch Override

A Branch price override affects only that Branch.

## 16.3. Branch Override Authority

Branch price overrides require explicit permission.

## 16.4. Historical Price

Historical Order Item prices are immutable snapshots.

## 16.5. Existing Orders

Price changes must not silently modify existing Order Items.

## 16.6. Payment

Payment uses the authoritative Order financial amount.

## 16.7. Refund

Refund calculations use historical transaction values.

## 16.8. Discount Separation

Discounts are separate from Product base prices.

## 16.9. Markup

Custom markup must remain within:

```text
0%–100%
```

## 16.10. Markup Cost

Custom markup uses the applicable Last Purchase Cost.

## 16.11. Markup History

Transaction-specific markup does not rewrite the standard Product price.

---

# 17. Configuration Invariants

## 17.1. Configuration Version

Operational configuration changes must be versioned where historical behavior depends on the change.

## 17.2. Configuration Ownership

Configuration belongs to a defined Business and, where applicable, Branch.

## 17.3. Effective Boundary

Current Menu/Pricing configuration becomes operational from the defined Cash Session boundary.

## 17.4. Active Session

An active Cash Session must not silently switch configuration.

## 17.5. Open Order

An existing Order Item retains its price/configuration snapshot.

## 17.6. Stale Version

A stale configuration update must be rejected.

## 17.7. Last-Write-Wins

Silent last-write-wins is prohibited for important configuration.

## 17.8. Configuration Idempotency

Repeated configuration commands must not create duplicate configuration versions.

## 17.9. Configuration Audit

Important configuration changes must be auditable.

---

# 18. Order Invariants

## 18.1. Order Ownership

Every Order belongs to exactly one Business.

## 18.2. Branch Ownership

Every operational Order belongs to exactly one Branch.

## 18.3. Cash Session Association

Where required by business workflow, an Order must be associated with its originating Cash Session.

## 18.4. Order Identity

Order UUID is immutable.

## 18.5. Customer Order Number

The customer-facing short Order number is not the database identity.

## 18.6. Historical Price

Order Item price snapshots are immutable after authoritative creation unless an explicit correction workflow creates a new revision.

## 18.7. Order Total

Order financial totals must be derived from authoritative Order financial state.

## 18.8. Payment Separation

Payment is separate from operational Order status.

## 18.9. Paid Order

A paid Order cannot be silently edited as an ordinary open Order.

## 18.10. Cancellation

Cancellation is represented as an explicit state/event and not physical deletion.

## 18.11. Refund

Refund is a separate financial operation.

## 18.12. Historical Order

Historical Orders must remain reconstructable.

---

# 19. Order Item Invariants

## 19.1. Product Reference

An Order Item references a valid Product identity.

## 19.2. Price Snapshot

Order Item retains the applicable selling price at the time of addition/authorization.

## 19.3. Quantity

Order Item quantity must satisfy valid quantity constraints.

## 19.4. Recipe Snapshot

Where required, the applied Recipe Version must be reconstructable.

## 19.5. Configuration Snapshot

Where required, the applied menu/configuration version must be reconstructable.

## 19.6. Historical Integrity

Current Product configuration must not reinterpret historical Order Items.

---

# 20. Payment Invariants

## 20.1. Payment Ownership

Every Payment belongs to exactly one Business.

## 20.2. Order Ownership

A Payment must reference an Order from the same Business.

## 20.3. Branch Consistency

A Payment must not cross Branch boundaries where Branch scope is part of the transaction.

## 20.4. Payment Identity

Payment UUID is immutable.

## 20.5. Duplicate Payment

The same logical payment operation must not be applied twice.

## 20.6. Payment Revision

Corrections create new revision/state rather than silently overwriting the original.

## 20.7. Refund Separation

Refund is not the same database operation as deleting a Payment.

## 20.8. Historical Payment

Original payment history remains reconstructable.

## 20.9. Overpayment

Overpayment must be explicitly represented according to the payment rules.

---

# 21. Debt Invariants

## 21.1. Debt Ownership

Debt belongs to the correct Business.

## 21.2. Debt Customer

Debt records must remain within the Business boundary.

## 21.3. Debt Orders

Debt transactions must reference Orders belonging to the same Business.

## 21.4. Partial Repayment

Partial repayment must preserve previous debt history.

## 21.5. Debt History

Debt balance must remain reconstructable from authoritative transactions.

---

# 22. Cash Register Invariants

## 22.1. Register Ownership

A Cash Register belongs to exactly one Branch.

## 22.2. Branch Consistency

A Cash Register cannot belong to another Business.

## 22.3. Cash Session Ownership

A Cash Session belongs to one Cash Register.

## 22.4. Cash Session Branch

The Cash Session Branch must match the Register Branch.

## 22.5. Cash Session Employee

The responsible cashier must belong to the same Business.

## 22.6. Open State

Only valid transitions may create or close an active Cash Session.

## 22.7. Closed Session

A closed Cash Session cannot be reopened as the same session.

## 22.8. Correction

Corrections create explicit correction records/events.

## 22.9. Physical Cash

Expected and actual cash values must remain distinguishable.

## 22.10. Session History

Closed session history is immutable.

---

# 23. Shift Handover Invariants

## 23.1. Previous Session

Handover closes or finalizes the previous cashier session according to the defined workflow.

## 23.2. Incoming Cashier

Incoming cashier must authenticate.

## 23.3. Cash Count

Handover records physical cash count.

## 23.4. Shortage

Shortage must remain attributable to the relevant session/handover.

## 23.5. Recount

Required recounts create explicit state/history.

## 23.6. Correction Limit

Correction limits must be enforced by the authoritative server.

---

# 24. Attendance and Payroll Invariants

## 24.1. Employee Ownership

Attendance and Payroll records belong to the same Business as the employee.

## 24.2. Branch Context

Branch context must be valid where attendance/payroll is Branch-scoped.

## 24.3. Payroll Authorization

Payroll modification requires appropriate permission.

## 24.4. Historical Payroll

Historical payroll calculations must remain reconstructable.

## 24.5. Employee Deactivation

Employee deactivation must not remove historical attendance/payroll data.

---

# 25. Notification Invariants

## 25.1. Notification Ownership

Notifications belong to the correct Business context.

## 25.2. Recipient Scope

Notification recipients must be authorized to receive the information.

## 25.3. Sensitive Payload

Notifications must not contain unnecessary sensitive information.

## 25.4. Delivery Failure

Notification failure must not roll back committed core business transactions.

## 25.5. Idempotency

The same logical notification event must not create uncontrolled duplicates.

---

# 26. Audit Invariants

## 26.1. Audit Immutability

Audit Events are immutable.

## 26.2. Audit Identity

Every Audit Event has a stable Event UUID.

## 26.3. Actor

Important actions must retain actor identity or explicit system actor identity.

## 26.4. Business Scope

Audit Events must preserve Business scope.

## 26.5. Branch Scope

Branch context must be retained where applicable.

## 26.6. Device Context

Device context must be retained where applicable.

## 26.7. Transaction Context

Important financial/operational events should reference the relevant transaction.

## 26.8. Old/New State

Important changes should preserve sufficient old/new state for reconstruction.

## 26.9. Audit Deletion

Ordinary application users cannot delete Audit Events.

## 26.10. Audit Export

Audit exports require appropriate authorization.

---

# 27. Report Invariants

## 27.1. Report Ownership

Reports belong to the correct Business.

## 27.2. Branch Scope

Branch reports contain only authorized Branch data.

## 27.3. Report Version

Report Versions are immutable.

## 27.4. Historical Report

A historical Report Version must not be silently rewritten.

## 27.5. Relevant Data Change

Relevant data changes may create a new Report Version.

## 27.6. Empty Report

An empty period may still produce a valid report.

## 27.7. Export

XLSX export must preserve the report's authorization scope.

---

# 28. Offline and Synchronization Invariants

## 28.1. Server Authority

The server/database remains authoritative after synchronization.

## 28.2. Offline Authorization

Offline operation requires valid trusted-device authorization.

## 28.3. Event Identity

Every synchronized operation requiring idempotency has a stable Event UUID.

## 28.4. Duplicate Event

Repeated delivery of the same Event UUID must not create duplicate business effects.

## 28.5. Event Ordering

Operations with explicit dependencies must respect dependency order.

## 28.6. Partial Success

A synchronization batch may partially succeed, but each event must have an explicit authoritative state.

## 28.7. Failed Event

Failed events must not be silently marked as successful.

## 28.8. Conflict

Conflicting events must have explicit conflict state.

## 28.9. Business Lifecycle

Synchronization must validate current Business lifecycle state.

## 28.10. Deleted Business

Offline events must not resurrect a deleted Business.

## 28.11. READ_ONLY Business

Offline events must not bypass READ_ONLY restrictions.

## 28.12. Configuration Priority

Transaction synchronization takes priority over configuration synchronization where transaction history depends on the older configuration.

## 28.13. Recovery Generation

Database recovery may require synchronization generation invalidation.

## 28.14. Stale Client

A stale client must resynchronize before continuing operations that depend on invalidated state.

---

# 29. Data Lifecycle Invariants

## 29.1. Lifecycle State

Business lifecycle state must be explicit.

## 29.2. Valid Lifecycle Transitions

Only valid lifecycle transitions may occur.

Example:

```text
ACTIVE
   ↓
READ_ONLY
   ↓
DELETION_ELIGIBLE
   ↓
DELETING
   ↓
DELETED
```

## 29.3. Deletion Idempotency

Repeated deletion commands must not produce inconsistent results.

## 29.4. Historical Protection

Historical records must be preserved until explicitly eligible for lifecycle deletion.

## 29.5. Cascading Deletion

Uncontrolled cascading deletion of critical historical domains is prohibited.

## 29.6. Backup Retention

Live-data deletion does not imply immediate deletion from retained backups.

## 29.7. Deleted Business

Deleted Business state must not be accidentally reactivated by synchronization.

---

# 30. Referential Integrity Guardrails

## 30.1. Foreign Keys

Foreign keys must be used wherever they provide meaningful structural integrity.

## 30.2. Required References

Required relationships must not permit orphaned records.

## 30.3. Optional References

Optional references must explicitly allow null where business rules permit.

## 30.4. Cross-Tenant Foreign Keys

Cross-tenant relationships must be structurally prevented where practical.

## 30.5. Composite Ownership

Where required, composite foreign keys should ensure:

```text
Business UUID
+
Referenced Entity UUID
```

belong to the same Business.

## 30.6. Orphan Prevention

Historical and operational records must not become silently orphaned.

---

# 31. Numeric and Financial Guardrails

## 31.1. Money Precision

Money values must use an exact numeric representation rather than floating-point storage.

## 31.2. Negative Money

Negative values are permitted only where the domain explicitly requires them.

## 31.3. Quantity Precision

Inventory quantities must use an appropriate precision.

## 31.4. Zero Quantity

Zero quantity must be explicitly allowed or rejected according to domain semantics.

## 31.5. Percentage Range

Defined percentages must respect their domain limits.

Example:

```text
Markup: 0–100%
```

## 31.6. Rounding

Rounding rules must be deterministic.

## 31.7. Historical Amount

Historical financial amounts must not be recalculated from current prices.

---

# 32. Timestamp Guardrails

## 32.1. Server Authority

Authoritative event timestamps are generated by trusted server/database time.

## 32.2. Client Timestamp

Client timestamps may be retained as contextual metadata but cannot replace authoritative timestamps.

## 32.3. Time Zone

Business-facing timestamps must follow the defined Business/Branch timezone rules.

## 32.4. Ordering

Timestamp alone must not be treated as a unique event identity.

## 32.5. Clock Rollback

Suspicious client clock rollback must be detectable during synchronization.

---

# 33. Concurrency Guardrails

## 33.1. Optimistic Concurrency

Configuration and other important mutable resources should use version validation.

## 33.2. Stale Update

Stale updates must be rejected.

## 33.3. Silent Overwrite

Silent overwriting of newer important state is prohibited.

## 33.4. Row Locks

Row-level locking should be used where required for financial/inventory consistency.

## 33.5. Lock Scope

Locks must be as narrow as practical.

## 33.6. Deadlock Prevention

Transactions must acquire locks in predictable order where multiple resources are involved.

## 33.7. POS Protection

Administrative operations must not unnecessarily block normal POS transactions.

---

# 34. Transaction Guardrails

## 34.1. Core Transaction Atomicity

Core business operations must commit as one logical transaction where required.

## 34.2. Core Domains

Examples include:

* Order acceptance;
* inventory deduction;
* Payment;
* cash state change;
* configuration commit.

## 34.3. Secondary Processing

Secondary operations may use outbox/background processing.

## 34.4. Secondary Failure

Secondary failure must not roll back a successfully committed core transaction unless explicitly designed otherwise.

## 34.5. Audit Persistence

Required audit state must be committed consistently with the protected business operation.

---

# 35. Security Guardrails

## 35.1. Least Privilege

Database roles must have only required privileges.

## 35.2. Runtime Role

Application runtime must not use superuser privileges.

## 35.3. Migration Role

Schema migration privileges are separated from runtime privileges.

## 35.4. Backup Role

Backup privileges are separated from application privileges.

## 35.5. Credential Protection

Credentials must not be stored in source code.

## 35.6. Secret Logging

Secrets must not appear in logs.

## 35.7. Encryption

Sensitive database and backup storage should use encryption at rest where supported.

## 35.8. TLS

Production network database connections must use encrypted transport where required.

## 35.9. SQL Injection

All user-controlled values must use safe parameter binding.

## 35.10. IDOR

Entity lookup must always preserve Business/Branch authorization.

---

# 36. Backup and Recovery Guardrails

## 36.1. Backup Independence

Backups must not depend solely on the production host.

## 36.2. Backup Encryption

Backups must be encrypted.

## 36.3. Backup Integrity

Backups must be verifiable.

## 36.4. WAL Continuity

Continuous WAL archiving must detect archive gaps.

## 36.5. Restore Testing

Backups must be periodically restored in a controlled environment.

## 36.6. Recovery Validation

A successful database restore is not sufficient until application/domain integrity is validated.

## 36.7. Security State

Recovery must preserve security state.

## 36.8. Idempotency State

Recovery must preserve synchronization/idempotency state.

## 36.9. Stale Clients

Recovery must account for clients with local state newer than the restored database.

---

# 37. Migration Guardrails

## 37.1. Version Control

Every production schema migration must be version-controlled.

## 37.2. Migration Order

Migrations must execute in deterministic order.

## 37.3. Migration History

Migration history must be preserved.

## 37.4. Destructive Changes

Destructive migrations require explicit recovery planning.

## 37.5. Expand/Contract

Breaking schema changes should use expand/contract where practical.

## 37.6. Backup Before Destructive Change

Appropriate backup/recovery capability must exist before destructive migrations.

## 37.7. Application Compatibility

Application versions and database schema versions must remain compatible during deployment.

---

# 38. Performance Guardrails

## 38.1. POS Latency

Database security and integrity controls must not introduce unnecessary POS latency.

## 38.2. Index Support

Common tenant and authorization filters must have appropriate indexes.

## 38.3. Query Bounds

Unbounded queries should be avoided.

## 38.4. Pagination

Large result sets must support pagination or controlled batch processing.

## 38.5. Export Limits

Large exports must be bounded and preferably processed asynchronously.

## 38.6. Connection Pool

Database connections must be bounded.

## 38.7. Background Work

Heavy work must not consume all database resources required by POS transactions.

## 38.8. Reporting

Heavy reporting should be isolated from core transaction performance where practical.

---

# 39. Deletion Guardrails

## 39.1. No Silent Destruction

Data must not be physically deleted without an explicit lifecycle or approved operation.

## 39.2. Historical Data

Historical financial, operational and audit records must be protected.

## 39.3. Archive First

Archive/deactivate should be preferred where historical identity is required.

## 39.4. Deletion Workflow

Business deletion must be a controlled workflow.

## 39.5. Deletion Audit

Deletion operations must be auditable.

## 39.6. Backup Awareness

Deletion workflows must account for retained backups.

---

# 40. Guardrails by Enforcement Layer

| Rule Type                | Primary Enforcement    | Secondary Guardrail              |
| ------------------------ | ---------------------- | -------------------------------- |
| UUID uniqueness          | Database               | Application                      |
| Business ownership       | Database + Application | Repository                       |
| Branch ownership         | Database + Application | Service                          |
| Permission               | Application            | Audit                            |
| Subscription entitlement | Application            | Transaction                      |
| Negative stock           | Database/Application   | Transaction                      |
| Historical price         | Database/Application   | Audit                            |
| Audit immutability       | Database/Application   | Restricted role                  |
| Cross-tenant access      | Application            | RLS/constraints where applicable |
| SQL injection            | Application            | Parameter binding                |
| Duplicate operation      | Application/Database   | Unique idempotency key           |
| Configuration conflict   | Application            | Version constraint               |
| Lifecycle transition     | Application            | Database state constraint        |
| Financial atomicity      | Transaction            | Database constraints             |
| Backup integrity         | Infrastructure         | Restore test                     |
| Offline replay           | Application            | Idempotency constraints          |

---

# 41. Database Constraint Strategy

The database should enforce rules that are:

* deterministic;
* structural;
* inexpensive;
* universally applicable;
* independent of UI.

Examples:

```text
PRIMARY KEY
FOREIGN KEY
UNIQUE
NOT NULL
CHECK
INDEX
```

Business workflows that require external context should remain in the service layer.

---

# 42. Check Constraint Strategy

Check constraints should protect simple impossible states.

Examples include:

```text
quantity > 0
percentage >= 0
percentage <= 100
amount >= 0
```

where the domain explicitly requires those rules.

Complex business workflows should not be forced into unnecessarily complex database constraints.

---

# 43. Unique Constraint Strategy

Unique constraints should protect logical uniqueness.

Examples:

* Business code where required;
* Branch code within Business;
* Product code within Business;
* device identity;
* idempotency key within appropriate scope;
* configuration version identity.

---

# 44. Composite Constraint Strategy

Composite constraints should be used where multiple values together define ownership.

Example:

```text
business_uuid
+
branch_uuid
```

can be used to ensure Branch references remain within the correct Business context.

---

# 45. Nullability Strategy

A field should be nullable only when absence has explicit business meaning.

Avoid using null as an undefined security or lifecycle state.

---

# 46. Enum/State Guardrails

Lifecycle and operational states must use controlled values.

Invalid states must not be accepted.

Example:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

must not be replaced by arbitrary free-text states.

---

# 47. State Transition Guardrails

A valid state value does not automatically mean a valid state transition.

For example:

```text
DELETED → ACTIVE
```

must not be allowed merely because both are valid enum values.

Transition rules belong to application/domain logic and, where practical, database-level protections.

---

# 48. Auditability Guardrail

Every important mutation must answer:

```text
Who?
What?
Where?
When?
From what?
To what?
Why?
Through which device?
Under which Business/Branch?
```

Not every field change requires a separate audit event, but security-sensitive and business-critical changes must remain attributable.

---

# 49. Historical Reconstruction Guardrail

The system should be able to reconstruct important historical business state without relying exclusively on current configuration.

This includes:

* historical Order price;
* historical Payment amount;
* historical Recipe Version;
* historical Set Version;
* historical configuration;
* historical Cash Session;
* historical inventory transaction.

---

# 50. No Current-State Reinterpretation

Current state must never be used to reinterpret historical transactions when historical snapshots are required.

Examples:

```text
Current Product Price
    ≠
Historical Order Price
```

```text
Current Recipe
    ≠
Historical Inventory Deduction Recipe
```

```text
Current Menu
    ≠
Historical Sale Availability
```

---

# 51. Security State Reconstruction

After backup restoration, the system must reconstruct:

* active employees;
* permissions;
* device trust;
* revocations;
* Business lifecycle;
* subscription restrictions;
* synchronization generations.

A restore must not unintentionally weaken security.

---

# 52. Recovery Epoch Guardrail

If database recovery can invalidate client assumptions, a recovery epoch/generation should be changed.

Clients must detect the changed generation and reconcile their local state.

---

# 53. Outbox Guardrails

Outbox records must:

* belong to the correct Business where applicable;
* have stable event identity;
* be idempotently processed;
* preserve ordering dependencies where required;
* not expose another Business's data.

---

# 54. Background Job Guardrails

Every tenant-sensitive background job must include sufficient context to identify:

```text
Business
Branch
Entity
Operation
Idempotency Key
```

A worker must not infer tenant context from mutable global state.

---

# 55. Data Export Guardrails

Every export operation must validate:

* actor;
* Business;
* Branch;
* permission;
* subscription;
* date range;
* requested dataset.

Exports must not bypass database security controls.

---

# 56. Security and Performance Balance

Security controls must be selected so that:

* POS operations remain fast;
* ordinary queries remain indexed;
* historical data remains safe;
* offline operation remains practical;
* administrative operations do not block routine transactions.

Security must be implemented through efficient controls rather than excessive verification at every step.

---

# 57. Operational Guardrails

The production database should monitor:

* replication/WAL state where applicable;
* backup status;
* connection usage;
* long-running queries;
* failed authentication;
* unusual administrative activity;
* storage capacity;
* failed migrations;
* integrity checks;
* synchronization anomalies.

---

# 58. Integrity Verification

Periodic integrity verification should check, where practical:

* foreign-key consistency;
* orphan records;
* Business ownership;
* Branch ownership;
* inventory consistency;
* configuration version chains;
* audit consistency;
* report version relationships;
* synchronization/idempotency state.

---

# 59. Security Verification

Security verification should include:

* cross-Business access tests;
* cross-Branch access tests;
* privilege escalation tests;
* IDOR tests;
* SQL injection tests;
* device revocation tests;
* READ_ONLY tests;
* DELETED Business synchronization tests;
* backup access tests;
* restore security tests.

---

# 60. Failure Handling

If an invariant violation is detected:

1. Stop or isolate the affected operation where safe.
2. Preserve evidence.
3. Record the incident.
4. Identify affected Business/Branch.
5. Determine whether the violation is structural, transactional or application-level.
6. Prevent further propagation.
7. Repair through an explicit controlled operation.
8. Preserve historical evidence.
9. Audit the correction.
10. Verify the invariant after repair.

---

# 61. Repair Principle

Repair must not silently overwrite history.

Preferred pattern:

```text
Detected Invalid State
        ↓
Preserve Evidence
        ↓
Controlled Correction
        ↓
New Correction Event
        ↓
Audit
        ↓
Verification
```

---

# 62. No Manual Production Editing

Direct manual SQL modifications to production business data should be avoided.

If emergency database intervention is required:

* authorized administrator;
* explicit reason;
* backup/recovery consideration;
* controlled SQL;
* audit/logging;
* post-change validation

are required.

---

# 63. Emergency Database Change

Emergency changes must be documented after the immediate incident is contained.

The documentation should include:

* reason;
* affected data;
* operator;
* commands/actions;
* timestamp;
* recovery point;
* validation;
* follow-up migration if necessary.

---

# 64. Testing Strategy

The invariant layer must be tested at:

### Unit level

Individual business rules.

### Integration level

Database constraints and transaction behavior.

### Security level

Tenant and authorization boundaries.

### Synchronization level

Offline/reconnect behavior.

### Recovery level

Backup restore and historical integrity.

### Performance level

Impact of constraints and security checks on POS workflows.

---

# 65. CI Guardrails

CI should reject changes that introduce known violations such as:

* missing Business ownership;
* missing foreign keys where required;
* unsafe destructive migration;
* unindexed critical tenant query;
* direct SQL interpolation;
* removal of audit requirements;
* removal of idempotency protection;
* unauthorized cascade deletion.

---

# 66. Code Review Guardrails

Database-related pull requests should verify:

* Business scope;
* Branch scope;
* permission implications;
* lifecycle implications;
* audit implications;
* migration safety;
* backup/recovery implications;
* synchronization implications;
* index/query impact.

---

# 67. Schema Review Checklist

Before accepting a new table:

* [ ] Does the table belong to a Business?
* [ ] Does it require Branch scope?
* [ ] Is ownership explicit?
* [ ] Are foreign keys defined?
* [ ] Are cross-Business references prevented?
* [ ] Are required fields NOT NULL?
* [ ] Are valid ranges protected?
* [ ] Is deletion behavior defined?
* [ ] Is historical retention defined?
* [ ] Is auditability defined?
* [ ] Are indexes sufficient?
* [ ] Does the table contain sensitive data?
* [ ] Does backup/recovery need special treatment?
* [ ] Does offline synchronization reference it?
* [ ] Does it require idempotency?

---

# 68. New Domain Invariant Checklist

For every new domain entity, the design must answer:

1. Who owns it?
2. Which Business owns it?
3. Which Branch owns it, if any?
4. Who can read it?
5. Who can modify it?
6. What is immutable?
7. What can be archived?
8. What can be deleted?
9. What must be audited?
10. What must be versioned?
11. What happens offline?
12. What happens after recovery?
13. What happens after subscription expiry?
14. What happens when the Business is deleted?
15. What prevents cross-tenant access?
16. What prevents duplicates?
17. What prevents invalid states?
18. What happens under concurrency?
19. What indexes are required?
20. What backup data is required?

---

# 69. Global Invariant Set

The following rules apply across the entire database:

1. Every persistent entity has a stable identity where independent identity is required.
2. Primary identities are unique.
3. Primary identities are immutable.
4. Identity values are never silently reused.
5. Every Business-owned record is traceable to one Business.
6. Cross-Business references are prohibited unless explicitly defined.
7. Branches belong to exactly one Business.
8. Business and Branch scope are validated together.
9. UUID possession never grants authorization.
10. Frontend authorization is never authoritative.
11. Server-side authorization is mandatory.
12. Subscription entitlement is part of authorization.
13. Deactivated employees cannot create new authorized operations.
14. Revoked devices cannot create new authorized synchronization events.
15. Offline authorization is time-bounded.
16. Offline data cannot bypass Business lifecycle restrictions.
17. Business lifecycle state is explicit.
18. Invalid lifecycle transitions are rejected.
19. Historical business transactions are preserved.
20. Historical financial values are immutable snapshots.
21. Current configuration does not rewrite historical transactions.
22. Current prices do not reinterpret historical Payments.
23. Current Recipes do not reinterpret historical Inventory Transactions.
24. Audit Events are immutable.
25. Report Versions are immutable.
26. Important configuration is versioned.
27. Important configuration changes are audited.
28. Stale configuration updates are rejected.
29. Silent last-write-wins is prohibited for important configuration.
30. Core transactions are atomic.
31. Duplicate retryable operations are prevented.
32. Inventory cannot become negative.
33. Inventory deductions are attributable.
34. Financial transactions are attributable.
35. Cash Sessions are immutable after closure except through explicit correction workflows.
36. Refunds are explicit transactions.
37. Cancellations are explicit states/events.
38. Deletion does not substitute for correction.
39. Business deletion is controlled.
40. Critical historical records are not removed by uncontrolled cascades.
41. Backups are separate from live-data lifecycle.
42. Backups are protected as production-equivalent sensitive data.
43. Restore must preserve security state.
44. Restore must account for offline clients.
45. Recovery may require synchronization generation changes.
46. Tenant context cannot leak through connection pooling.
47. Background jobs must carry explicit tenant context.
48. Database runtime access is least-privileged.
49. Migration privileges are separated.
50. Backup privileges are separated.
51. Database credentials are protected.
52. Secrets are not logged.
53. Production PostgreSQL is not publicly exposed.
54. Network database connections are encrypted where required.
55. SQL values are parameterized.
56. Dynamic SQL is restricted.
57. Security-sensitive state changes are auditable.
58. Security failures fail closed.
59. Unknown authorization does not become authorization success.
60. Database constraints protect structural integrity.
61. Application rules protect contextual business integrity.
62. Transaction boundaries protect atomicity.
63. Audit protects historical accountability.
64. Backup protects recoverability.
65. Monitoring protects operational visibility.
66. Performance safeguards protect POS responsiveness.
67. Schema changes are version-controlled.
68. Destructive migrations require recovery planning.
69. Large operations are bounded.
70. Core POS transactions must not depend on expensive historical queries.
71. Heavy reporting must not unnecessarily block core operations.
72. Security must not be bypassed for performance convenience.
73. Performance must not be degraded by unnecessary security work.
74. Every correction preserves evidence.
75. Every invariant violation is investigated and controlled.
76. Production manual data changes are exceptional.
77. Emergency changes are documented.
78. New entities require explicit ownership design.
79. New sensitive fields require explicit security review.
80. New deletion behavior requires lifecycle review.
81. New synchronization behavior requires idempotency review.
82. New financial behavior requires historical integrity review.
83. New configuration behavior requires concurrency review.
84. New schema changes require migration review.
85. New backup dependencies require recovery review.
86. Database security is defense-in-depth.
87. No single layer is assumed to be sufficient.
88. The database remains the authoritative transactional store.
89. Cache state is never authoritative.
90. Client state is never authoritative.
91. Export files are never authoritative.
92. Report snapshots do not replace transactional history.
93. Backup copies do not replace live lifecycle management.
94. Deleted Business identifiers are never reused.
95. Historical identity remains attributable.
96. System-generated operations have explicit system identity.
97. Security state is included in backup/recovery validation.
98. Synchronization state is included in backup/recovery validation.
99. Data integrity is preserved across normal and failure paths.
100. Historical integrity has priority over UI convenience.

---

# 70. Database Guardrail Priority

When requirements conflict, the following priority should normally apply:

```text
1. Data Integrity
2. Tenant Isolation
3. Security
4. Financial Integrity
5. Historical Integrity
6. Authorization
7. Recoverability
8. Synchronization Correctness
9. Operational Availability
10. Performance
11. UI Convenience
```

This priority does not mean performance is unimportant.

The architecture must optimize implementation so that higher-priority protections do not unnecessarily damage normal POS performance.

---

# 71. Final Database Design Principle

The database must be designed so that invalid states are difficult to create, easy to detect and controlled to repair.

The preferred architecture is:

```text
Strong Identity
      ↓
Explicit Ownership
      ↓
Tenant / Branch Isolation
      ↓
Database Constraints
      ↓
Transactional Integrity
      ↓
Authorization
      ↓
Immutable History
      ↓
Idempotency
      ↓
Backup / Recovery
      ↓
Monitoring
```

The database must preserve not only the current state, but also the ability to explain how important business state was created, changed, corrected and recovered.

---

# 72. Status

**Document Status:** Accepted
**Version:** 1.0
**Current Document:** `30_Database_Invariants_and_Guardrails.md`
**Previous Document:** `29_Database_Security.md`
**Database Section:** Completed

---

## Related Documents

### Database

* `docs/05_Database/01_Database_Overview.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/05_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `docs/05_Database/10_Set_and_Set_Version_Data_Model.md`
* `docs/05_Database/11_Inventory_and_Warehouse_Data_Model.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/14_Table_and_Waiter_Data_Model.md`
* `docs/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/17_Shift_Handover_Data_Model.md`
* `docs/05_Database/18_Employee_Attendance_and_Payroll_Data_Model.md`
* `docs/05_Database/19_Notification_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/27_Database_Migrations_and_Change_Management.md`
* `docs/05_Database/28_Database_Backup_and_Recovery.md`
* `docs/05_Database/29_Database_Security.md`

### System Analysis

* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Architecture

* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/15_Observability_and_Operations_Architecture.md`
* `docs/04_Architecture/16_Scalability_and_Performance_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`

### ADR

* `adr/ADR-001-Documentation-First.md`

