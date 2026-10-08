# Database Architecture

**Document ID:** DB-02
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/01_Database_Overview.md`

## 1. Purpose

This document defines the concrete database architecture of FastFood ERP.

It translates the general database principles from:

`01_Database_Overview.md`

into a practical PostgreSQL architecture.

This document defines:

* PostgreSQL deployment model;
* logical database organization;
* schema strategy;
* table organization;
* domain ownership;
* persistence boundaries;
* connection management;
* transaction management;
* concurrency control;
* database access patterns;
* tenant and branch context;
* database security boundaries;
* read/write separation principles;
* reporting database boundaries;
* migration boundaries;
* database scalability direction.

It does not define every individual table or column. Detailed data models are defined by subsequent database documents.

---

# 2. Database Architecture Style

FastFood ERP uses a **single authoritative PostgreSQL database** for the initial architecture.

The application follows a modular database design while keeping transactional data inside one PostgreSQL instance.

Conceptually:

```text
                    ┌──────────────────────┐
                    │   FastFood ERP App   │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Database Access     │
                    │ SQLAlchemy / Repos   │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │      PostgreSQL      │
                    │                      │
                    │ Business Data        │
                    │ Operational Data     │
                    │ Financial Data       │
                    │ Inventory Data       │
                    │ Audit Data           │
                    │ Sync Data            │
                    │ Configuration Data   │
                    └──────────────────────┘
```

The architecture intentionally avoids separate databases for every domain.

---

# 3. Why a Single PostgreSQL Database

A single PostgreSQL database provides:

* strong ACID transactions;
* simple cross-domain transactional operations;
* reliable foreign keys;
* simpler deployment;
* simpler backup and recovery;
* lower infrastructure cost;
* easier local development;
* simpler reporting;
* simpler operational monitoring;
* predictable consistency.

This is particularly important because FastFood ERP has operations such as:

```text
Order Acceptance
    +
Inventory Deduction
```

and:

```text
Payment
    +
Cash Session
```

that may require atomic database transactions.

Splitting these operations across independent databases would introduce unnecessary distributed transaction complexity.

---

# 4. No Database-per-Tenant Model

The initial architecture does not create a separate PostgreSQL database for every Business.

Instead:

```text
PostgreSQL
    │
    ├── Business A
    ├── Business B
    ├── Business C
    └── Business N
```

Tenant isolation is implemented through:

* Business UUID;
* application authorization;
* scoped queries;
* foreign keys;
* repository boundaries;
* background-job context;
* report/export context;
* synchronization validation.

A future database-per-tenant strategy is not prohibited, but it is not required by the current architecture.

---

# 5. No Database-per-Branch Model

Branches do not receive separate databases.

Instead:

```text
Business
   │
   ├── Branch A
   ├── Branch B
   └── Branch C
```

Branch-scoped data references the appropriate Branch UUID.

This allows:

* cross-branch reports for authorized users;
* centralized Business configuration;
* simpler synchronization;
* simpler backup;
* easier business-level reporting.

Branch isolation remains mandatory at the application and query levels.

---

# 6. PostgreSQL Database Structure

The initial deployment uses one primary application database.

Conceptually:

```text
PostgreSQL Cluster
        │
        └── FastFood ERP Database
                │
                ├── Business Data
                ├── Identity Data
                ├── Subscription Data
                ├── Branch Data
                ├── Order Data
                ├── Cash Data
                ├── Inventory Data
                ├── Payment Data
                ├── Menu Data
                ├── Employee Data
                ├── Reporting Data
                ├── Notification Data
                ├── Audit Data
                ├── Synchronization Data
                ├── Configuration Data
                └── Lifecycle Data
```

The exact physical deployment may change as infrastructure grows, but the logical ownership model remains stable.

---

# 7. PostgreSQL Schema Strategy

The initial architecture uses a **single PostgreSQL application schema** unless a later architecture decision explicitly introduces additional schemas.

The default logical organization is therefore based on:

* table naming;
* domain ownership;
* foreign-key relationships;
* repository boundaries;
* migration organization.

The architecture does not require one PostgreSQL schema per domain.

This avoids unnecessary complexity while still preserving domain boundaries at the application level.

---

# 8. Why Not One PostgreSQL Schema per Domain

Separate PostgreSQL schemas for every domain could provide additional physical separation, but would also introduce:

* more migration complexity;
* more complicated foreign-key management;
* more complicated tooling;
* additional naming overhead;
* unnecessary abstraction for the initial system.

The primary requirement is clear ownership, not artificial physical separation.

Therefore:

> Domain boundaries are primarily enforced by application architecture and data ownership, while PostgreSQL provides shared transactional persistence.

---

# 9. Domain Ownership

Each table must have one primary domain owner.

Example:

```text
Order Domain
    ├── orders
    ├── order_items
    └── order-related state

Inventory Domain
    ├── inventory_transactions
    ├── stock_balances
    └── inventory-related state
```

A domain may own multiple tables.

A table should not have ambiguous ownership.

---

# 10. Cross-Domain References

Cross-domain references are allowed when required by the business model.

For example:

```text
orders.business_id
orders.branch_id
orders.employee_id
orders.cash_session_id
```

However, a domain must not freely modify another domain's owned state.

For example:

```text
Order Domain
    → may reference Inventory
    → may request Inventory operation
    → must not directly manipulate Inventory internals
```

The application service layer coordinates cross-domain operations.

---

# 11. Database as an Integrity Boundary

The database is the final persistence integrity boundary.

Application code performs:

* validation;
* authorization;
* business logic;
* workflow orchestration.

PostgreSQL provides:

* primary-key integrity;
* foreign-key integrity;
* unique constraints;
* check constraints;
* transaction atomicity;
* concurrency protection;
* persistence guarantees.

Both layers are required.

---

# 12. Connection Architecture

Application instances connect to PostgreSQL through a controlled connection pool.

Conceptually:

```text
Application Instance
       │
       ▼
SQLAlchemy Engine
       │
       ▼
Connection Pool
       │
       ▼
PostgreSQL
```

The application must not create a new unrestricted database connection for every operation.

Connection pooling is required for predictable performance.

---

# 13. Connection Pooling

The connection pool must be configured according to:

* available PostgreSQL connections;
* application worker count;
* expected POS concurrency;
* background worker concurrency;
* deployment resources.

The total connection demand must remain within PostgreSQL capacity.

Connection pool settings must be environment-specific.

Development and production must not necessarily use identical pool sizes.

---

# 14. Application Workers and Connections

If multiple Gunicorn workers or application instances are deployed, each process may maintain its own database connection pool.

Therefore:

```text
Total DB Connections
=
Application Worker Pools
+
Background Worker Pools
+
Administrative / Monitoring Connections
```

Connection limits must be calculated globally.

The system must not assume that each process can independently consume the full PostgreSQL connection capacity.

---

# 15. Background Worker Database Access

Background workers may access PostgreSQL through controlled database connections.

Workers must respect the same:

* Business context;
* Branch context;
* authorization rules where applicable;
* transaction rules;
* idempotency;
* tenant isolation.

A worker must never process a job without knowing the Business context of that job.

---

# 16. Transaction Architecture

Database transactions are used to protect business operations that must succeed or fail together.

A transaction boundary should be established around the complete core operation.

Example:

```text
BEGIN
    Validate
    ├── authorization
    ├── business state
    ├── inventory
    └── configuration

    Execute
    ├── update order
    ├── update inventory
    └── create transaction records

COMMIT
```

Secondary operations may execute after commit.

---

# 17. Transaction Ownership

The application service/use-case layer owns transaction boundaries.

Repositories should not independently commit business transactions unless explicitly designed as infrastructure-level operations.

This prevents:

```text
Service
 ├── Repository A → COMMIT
 ├── Repository B → COMMIT
 └── Repository C → FAIL
```

which could leave partial business state.

Instead:

```text
Service
 ├── Repository A
 ├── Repository B
 └── Repository C
       ↓
    COMMIT once
```

---

# 18. Transaction Scope

Transactions should be:

* atomic;
* as short as practical;
* limited to required database operations;
* free from unnecessary network calls;
* free from long-running external operations.

External calls such as printing or notification delivery should not normally remain inside the core database transaction.

---

# 19. Core and Secondary Processing

The architecture separates core transactional processing from secondary processing.

Example:

```text
Core Transaction
       │
       ├── Order persistence
       ├── Inventory deduction
       └── Transaction commit
                │
                ▼
          Secondary Processing
                │
                ├── Kitchen
                ├── Printer
                ├── Notification
                ├── Report update
                └── Audit delivery where applicable
```

A secondary failure must not automatically invalidate an already committed core transaction.

---

# 20. Order Transaction Boundary

Order acceptance is a core transaction.

At minimum, the transaction may include:

* order state transition;
* order item persistence;
* inventory validation;
* inventory deduction;
* transaction record creation;
* relevant operational state.

The transaction must either fully succeed or roll back.

---

# 21. Payment Transaction Boundary

Payment creation is a separate financial transaction.

It must validate and persist:

* payment identity;
* order relationship;
* Business;
* Branch;
* employee;
* cash session where applicable;
* payment method;
* amount;
* transaction state.

Payment must not require modifying unrelated operational order state unless explicitly defined.

---

# 22. Cash Session Transaction Boundary

Cash operations require controlled transactions for:

* session opening;
* session closure;
* handover;
* correction authorization;
* correction application.

A cash session transition must not leave the database in an ambiguous state.

---

# 23. Inventory Transaction Boundary

Inventory-changing operations must be atomic.

Examples:

* sale deduction;
* purchase;
* production;
* stock adjustment;
* return;
* waste/shrink;
* correction.

A stock-changing operation must preserve both:

```text
Inventory Movement
+
Resulting Stock State
```

according to the chosen inventory model.

---

# 24. Isolation Level

The default PostgreSQL transaction isolation level should remain appropriate for normal ERP operations without unnecessarily increasing contention.

The application should use the standard PostgreSQL transactional behavior by default.

Higher isolation or explicit locking should be used only where required.

Examples:

* last-unit inventory consumption;
* active cash session creation;
* critical financial state;
* concurrent correction.

Isolation must be chosen based on business correctness, not as a blanket rule.

---

# 25. Row-Level Locking

Row-level locking may be used for high-value concurrent state changes.

Typical examples:

```text
Inventory Stock
Cash Session
Critical Payment State
Critical Configuration Version
```

Locks must be:

* targeted;
* short-lived;
* deterministic where possible.

Broad table locks should be avoided in normal POS operations.

---

# 26. Deadlock Prevention

The application must avoid unnecessary deadlocks.

When multiple rows or tables must be locked, the application should use a consistent locking order.

For example:

```text
Business
   ↓
Branch
   ↓
Operational Resource
```

The exact order depends on the affected operation.

Deadlock-prone transaction structures must be tested under concurrency.

---

# 27. Unique Constraints

Database uniqueness must be enforced for identities that must never duplicate.

Examples may include:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Order UUID;
* Payment UUID;
* Transaction UUID;
* Synchronization Event UUID.

Business-specific uniqueness rules may also require composite unique constraints.

---

# 28. Composite Constraints

Some invariants depend on multiple fields.

Examples:

```text
Business + Branch
Business + Product
Business + Employee
Business + Device
Branch + Cash Register
Branch + Active Cash Session
```

Composite constraints should be used where they directly protect business integrity.

---

# 29. State Constraints

Where practical, the database may enforce basic valid state values.

For example:

```text
Order Status
    Draft
    Accepted
    Preparing
    Ready
    Served
```

However, complex workflow transitions should remain application-level rules.

The database should prevent obviously invalid persisted values without becoming the primary workflow engine.

---

# 30. Database State vs Workflow State

The database stores state.

The application determines valid transitions.

For example:

```text
Database:
order.status = "Accepted"
```

The application decides whether:

```text
Draft → Accepted
```

is valid for the current:

* employee;
* permission;
* inventory;
* branch;
* configuration;
* subscription;
* cash session;
* synchronization context.

---

# 31. Tenant Context

Every tenant-scoped operation must establish Business context before accessing data.

Conceptually:

```text
Authenticated Employee
        ↓
Business Context
        ↓
Branch Scope
        ↓
Database Query
```

The Business UUID must not be accepted blindly from the client.

It must be derived or validated from authenticated context and authorized membership.

---

# 32. Branch Context

Branch context follows the same principle.

A client request must not be able to access an arbitrary Branch UUID simply by changing a request parameter.

The application must verify:

```text
Employee
    +
Business
    +
Branch
    +
Permission
```

before executing branch-scoped operations.

---

# 33. Background Job Context

Background jobs must carry enough scope to safely identify their tenant.

A job should contain, where applicable:

* Job UUID;
* Business UUID;
* Branch UUID;
* actor/source;
* entity UUID;
* transaction UUID.

A worker must reject or safely fail jobs with invalid tenant context.

---

# 34. Reporting Database Strategy

The initial system does not require a separate reporting database.

Reports use the authoritative PostgreSQL database.

However, report processing must be isolated from critical POS transactions through:

* optimized queries;
* controlled query limits;
* background processing for heavy reports;
* consistent snapshots;
* appropriate indexes.

A separate reporting database may be introduced later if scale requires it.

---

# 35. Read and Write Workloads

The database serves two broad workload categories:

### Transactional

* orders;
* payments;
* inventory;
* cash;
* employee operations.

### Analytical / Reporting

* reports;
* dashboards;
* historical analysis;
* exports.

Transactional workloads have priority.

Reporting workloads must not consume enough database resources to degrade POS operations.

---

# 36. Future Read Replicas

The architecture permits future read replicas.

Potential future model:

```text
                PostgreSQL Primary
                     │
          ┌──────────┴──────────┐
          │                     │
       Writes              Replication
                                │
                         ┌──────┴──────┐
                         │             │
                     Read Replica  Read Replica
```

Read replicas must not be used for operations requiring immediate authoritative state.

For example, stock validation for an order must use authoritative transactional state.

---

# 37. Cache Boundary

Redis-compatible caching is outside PostgreSQL's authoritative data role.

Cache may store:

* frequently accessed configuration;
* temporary values;
* short-lived session-related data;
* rate-limiting state;
* background processing state.

Cache must not become the only source for:

* inventory;
* payments;
* cash balances;
* order state;
* subscription authority.

---

# 38. Database and Queue Boundary

The database stores authoritative business state.

The queue handles asynchronous processing.

For example:

```text
Database Transaction
       ↓
Durable Event / Outbox
       ↓
Queue
       ↓
Worker
       ↓
Secondary Processing
```

Queue loss must not mean business transaction loss.

---

# 39. Outbox Consideration

Where reliable event delivery is required, an outbox-style pattern should be used.

Conceptually:

```text
BEGIN
    Business State Change
    +
    Outbox Event
COMMIT
```

Then:

```text
Outbox
   ↓
Worker
   ↓
Queue / Processing
```

This ensures that the event describing a committed business change is persisted atomically with that change.

---

# 40. Database and Printer Boundary

Printer communication is not part of the core database transaction.

For example:

```text
Order Accepted
      ↓
Database COMMIT
      ↓
Printer Job
      ↓
Printed / Failed / Retrying
```

A printer failure must not automatically roll back the accepted order.

Printer processing requires its own persistent status where historical traceability is needed.

---

# 41. Database and Notification Boundary

Notifications are secondary processing.

Example:

```text
Cash Session Closed
      ↓
Database COMMIT
      ↓
Notification Created
      ↓
Notification Delivered
```

Notification delivery failure must not roll back the cash session.

---

# 42. Database and Audit Boundary

Important state changes require reliable audit records.

Where audit integrity is critical, the audit event should be persisted as part of the relevant transaction or through a reliable transactional outbox mechanism.

The selected approach must guarantee that an important committed state change cannot silently lose its audit trail.

---

# 43. Database and Synchronization Boundary

Synchronization writes must follow normal database integrity rules.

An incoming offline event must pass:

```text
Event Identity
    ↓
Business Validation
    ↓
Branch Validation
    ↓
Employee / Device Validation
    ↓
Permission Validation
    ↓
Subscription Validation
    ↓
Business Rule Validation
    ↓
Transaction
```

Only then may it modify authoritative server state.

---

# 44. Database and Data Lifecycle

Business lifecycle state must be stored persistently.

Example:

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

Deletion jobs must be idempotent.

A partially completed deletion must be safely resumable.

---

# 45. Database Deletion Safety

Permanent deletion must not be implemented as an ordinary application delete operation.

Before deletion, the system must verify:

* Business lifecycle state;
* retention period;
* absence of valid reactivation;
* deletion authorization/system state;
* job identity;
* deletion lock.

Deletion must be auditable.

---

# 46. Database Security Boundaries

Production database access must be restricted.

Application users should have only the privileges necessary for application operation.

Administrative database access must be separated from ordinary application credentials.

Database credentials must not be embedded in source code.

Secrets must be provided through secure environment/configuration mechanisms.

---

# 47. Database Credentials

The application must use dedicated credentials.

Different operational roles may be used for:

* application runtime;
* migration execution;
* administrative operations;
* backup;
* monitoring.

The exact privilege model may evolve with deployment requirements.

---

# 48. SQL Injection Protection

Application queries must use parameterized SQL through SQLAlchemy or equivalent safe mechanisms.

User-provided values must never be concatenated directly into SQL statements.

Raw SQL is permitted only when:

* technically justified;
* parameterized;
* reviewed;
* tested;
* consistent with architecture.

---

# 49. Database Logging

Database logging should support diagnosis without exposing sensitive data unnecessarily.

Logs should avoid:

* passwords;
* authentication tokens;
* private secrets;
* unnecessary personal data;
* sensitive payment information.

Slow query logging may be enabled in production according to performance requirements.

---

# 50. Schema Naming

Database names should use a consistent naming convention.

Recommended conventions:

* lowercase;
* `snake_case`;
* descriptive names;
* singular/plural convention selected consistently;
* explicit foreign-key names where needed;
* predictable timestamp names.

The exact convention must be documented before implementation begins.

---

# 51. Timestamp Columns

Entities requiring lifecycle tracking should use explicit timestamps.

Common fields may include:

```text
created_at
updated_at
deleted_at
effective_from
effective_until
```

Not every table requires every field.

Historical and synchronization entities may additionally require:

```text
client_created_at
server_received_at
processed_at
```

The meaning of every timestamp must be explicit.

---

# 52. Version Columns

Optimistic concurrency may use version fields where appropriate.

Example:

```text
version = 1
```

After a successful update:

```text
version = 2
```

A stale update can then be rejected rather than silently overwriting newer state.

Versioning is particularly useful for:

* configuration;
* editable operational records;
* synchronization;
* conflict detection.

---

# 53. Monetary Columns

Monetary database columns must use exact numeric types.

Conceptually:

```text
NUMERIC(precision, scale)
```

The final precision and scale must be selected consistently for the system's supported currencies and business values.

Floating-point database columns must not be used for authoritative financial amounts.

---

# 54. Quantity Columns

Inventory quantity columns must use exact numeric-compatible types suitable for configured units and precision.

Examples:

```text
1 piece
0.500 kg
250.000 g
1.250 L
```

The final scale must support the required recipe and inventory precision without introducing floating-point drift.

---

# 55. Database Normalization

The database should generally follow normalized relational design.

Normalization should prevent:

* duplicated authoritative data;
* update anomalies;
* inconsistent relationships.

However, controlled denormalization may be used where justified for:

* historical snapshots;
* reporting performance;
* immutable transaction data;
* operational performance.

Denormalized data must have a clearly defined source of truth.

---

# 56. Historical Snapshots

Some operational records must intentionally store snapshots.

Examples:

* order item price;
* applied discount;
* recipe version;
* configuration version;
* customer information captured at order time;
* report state.

A snapshot is not considered accidental duplication when it is required for historical reconstruction.

---

# 57. Database and Customer Data

The current system does not implement a full customer CRM.

Customer-related data may exist for operational purposes such as:

* delivery phone;
* delivery address;
* debt customer identity;
* historical order information.

The database must not introduce a full CRM model unless it becomes an approved product requirement.

---

# 58. Database and Product Data

Products are business-level entities.

A product may have:

* product identity;
* category;
* standard price;
* active state;
* recipe relationship;
* set relationship where applicable;
* image reference;
* configuration history.

Branch-specific availability and price overrides are separate concerns.

---

# 59. Database and Inventory Data

Inventory is branch-scoped.

The same Business product may have different stock quantities across branches.

Conceptually:

```text
Product
   │
   ├── Branch A → Stock
   ├── Branch B → Stock
   └── Branch C → Stock
```

Stock quantities must never be treated as global Business-level quantities.

---

# 60. Database and Menu Data

The global menu defines Business-level product availability.

Branch configuration determines whether a product is available in a specific branch.

The database must distinguish:

```text
Global Product
```

from:

```text
Branch Availability
```

and:

```text
Branch Price Override
```

---

# 61. Database and Employee Data

Employees belong to a Business.

Branch assignments may associate an employee with one or more Branches.

Permission scope must not be inferred only from the employee's existence.

Effective permission depends on:

```text
Role
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
```

---

# 62. Database and Device Data

Devices have stable Device UUIDs.

Device records must preserve:

* Business;
* Branch scope;
* trust state;
* registration information;
* revocation state;
* relevant security metadata.

A replaced device receives a new Device UUID.

---

# 63. Database and Cash Register Data

A Branch normally has one Cash Register.

The database structure must still avoid making multiple registers impossible in the future.

Conceptually:

```text
Branch
   ↓
Cash Register
   ↓
Cash Session
```

The Cash Session is the operational period and primary reconciliation unit.

---

# 64. Database and Report Data

Reports should reference:

* Business;
* Branch where applicable;
* period;
* definition;
* version;
* source;
* creation time.

Report versions must remain immutable.

The database must support retrieval of the exact report snapshot represented by a historical version.

---

# 65. Database and Notification Data

Notifications must support recipient-specific state.

For example:

```text
Notification
    ↓
Recipient A → Unread
Recipient B → Read
```

A notification must not be duplicated merely because an authorized user has multiple devices.

---

# 66. Database and Audit Data

Audit events are append-oriented and immutable.

Audit records must remain available for authorized historical reconstruction.

They should be optimized for:

* filtering;
* pagination;
* date range queries;
* Business;
* Branch;
* employee;
* entity;
* transaction;
* event type.

---

# 67. Database and Subscription Data

Subscription entitlement must be stored independently from ordinary employee permissions.

A user may have a permission that is currently unavailable because the Business subscription does not include the feature.

Therefore:

```text
Permission
    +
Subscription Entitlement
    ↓
Effective Capability
```

---

# 68. Database and Configuration Data

Configuration is versioned where required.

Configuration records must preserve:

* owner;
* scope;
* state;
* version;
* effective period;
* actor;
* reason;
* historical relationship.

A configuration change must not silently modify already finalized historical transactions.

---

# 69. Database and Offline Configuration

Offline devices may use the latest valid synchronized configuration.

The database must provide version identifiers that allow the device to determine whether its local configuration is stale.

Transaction synchronization takes priority over configuration synchronization when required to preserve transaction correctness.

---

# 70. Database Performance Priorities

Database performance priorities are:

1. Order operations.
2. Payment operations.
3. Cash operations.
4. Inventory operations.
5. Authentication and authorization support.
6. Synchronization.
7. Operational dashboards.
8. Reports and exports.
9. Background processing.

Heavy analytical operations must not unnecessarily interfere with POS workloads.

---

# 71. Query Design Rules

Queries should:

* filter by Business where applicable;
* filter by Branch where applicable;
* use appropriate indexes;
* select only required columns where practical;
* paginate large datasets;
* avoid unnecessary joins;
* avoid N+1 access patterns;
* use deterministic ordering.

Unbounded queries are prohibited for user-facing large collections.

---

# 72. Pagination

Large collections must support server-side pagination.

Examples:

* orders;
* payments;
* inventory movements;
* employees;
* audit events;
* notifications;
* reports;
* synchronization records.

Pagination must have deterministic ordering.

---

# 73. Sorting

Sorting must be explicit.

Where multiple records may have identical timestamps, secondary deterministic ordering should be used.

Example:

```text
created_at DESC
+
UUID DESC
```

This prevents unstable pagination.

---

# 74. Database Health

Production database monitoring should include:

* connection usage;
* query latency;
* slow queries;
* transaction duration;
* lock contention;
* disk usage;
* replication status if applicable;
* backup status;
* failed connections;
* database errors.

---

# 75. Database Availability Strategy

The initial system does not require multi-primary PostgreSQL architecture.

The primary objective is:

* reliable primary database;
* tested backups;
* tested recovery;
* controlled deployment;
* monitoring.

High availability mechanisms may be added when operational requirements justify them.

---

# 76. Future Database Scaling

Potential future stages include:

### Stage 1

```text
Single PostgreSQL Primary
```

### Stage 2

```text
PostgreSQL Primary
+
Read Replica
```

### Stage 3

```text
Primary
+
Multiple Read Replicas
+
Reporting Workload Separation
```

### Stage 4

Only if justified:

```text
Partitioning
+
Archival
+
Specialized Reporting Infrastructure
```

Database sharding is not an initial requirement.

---

# 77. Partitioning

Partitioning must not be introduced prematurely.

Potential future partition candidates may include very large append-oriented tables such as:

* audit events;
* synchronization events;
* historical operational records.

Partitioning should only be introduced after measurable scale or operational requirements justify it.

---

# 78. Archival

Historical data may eventually require archival strategies.

Archival must preserve:

* historical integrity;
* references;
* auditability;
* report reconstruction where required.

Archiving must not be confused with Business deletion.

---

# 79. Database Migration Architecture

Schema changes are managed through Alembic migrations.

Each migration must be:

* version controlled;
* deterministic;
* reviewable;
* testable;
* ordered.

Production migration execution must be controlled.

---

# 80. Backward Compatibility

Schema changes must consider currently running application versions.

Where rolling deployments are possible, migrations should follow a compatible sequence:

```text
Expand
   ↓
Deploy Compatible Code
   ↓
Migrate Data
   ↓
Switch Behavior
   ↓
Contract
```

Destructive schema changes should be delayed until old code no longer requires the affected structure.

---

# 81. Database Testing

Database behavior must be tested at multiple levels:

### Unit / Domain

Business rules independent of PostgreSQL where practical.

### Integration

Actual PostgreSQL behavior including:

* constraints;
* transactions;
* locking;
* indexes;
* migrations.

### Concurrency

Concurrent operations such as:

* last-stock sale;
* cash session opening;
* payment creation.

### Recovery

* backup restore;
* migration recovery;
* failure handling.

---

# 82. Database Test Environment

Automated tests should use a PostgreSQL-compatible environment that closely matches production behavior.

SQLite should not be treated as a complete substitute for PostgreSQL when testing:

* locking;
* constraints;
* transaction behavior;
* PostgreSQL-specific types;
* PostgreSQL-specific queries.

---

# 83. Database Documentation Rules

Every important database design decision must be documented.

Database documents must distinguish:

* business requirement;
* domain ownership;
* database implementation;
* performance optimization;
* infrastructure decision.

Database documentation must not silently introduce new business behavior.

---

# 84. Database Architecture Invariants

The following rules are mandatory:

1. PostgreSQL remains the authoritative transactional database.
2. Business data remains tenant-isolated.
3. Branch data remains branch-isolated.
4. Critical operations use database transactions.
5. Application services own business transaction boundaries.
6. Repositories must not independently commit partial business workflows.
7. UUIDs remain stable.
8. Transaction UUIDs remain stable.
9. Duplicate critical operations are prevented.
10. Historical records remain reconstructable.
11. Critical financial values use exact numeric types.
12. Negative inventory is prohibited.
13. Active cash session concurrency is controlled.
14. Database queries remain scope-aware.
15. Background jobs carry valid Business context.
16. Reporting must not unnecessarily block POS operations.
17. Cache is not authoritative.
18. Queue is not authoritative.
19. Offline data is validated before becoming authoritative server state.
20. Schema changes are migration-controlled.
21. Production migrations must be reviewed.
22. Destructive schema changes require explicit approval.
23. Database credentials must be protected.
24. Raw SQL must be parameterized.
25. Database backups must be tested through restoration.
26. Future scaling must not compromise transaction correctness.

---

# 85. Completion Criteria

This document is complete when:

* PostgreSQL is established as the authoritative database;
* tenant architecture is defined;
* branch architecture is defined;
* schema strategy is defined;
* domain ownership is defined;
* connection pooling strategy is defined;
* transaction ownership is defined;
* concurrency strategy is defined;
* reporting boundary is defined;
* cache and queue boundaries are defined;
* migration architecture is defined;
* security boundary is defined;
* scalability direction is defined.

Detailed table-level design remains in the following database documents.

---

# 86. Next Document

The next document is:

`03_Tenant_and_Business_Data_Model.md`

It will define the database model for:

* Business;
* tenant identity;
* Business lifecycle;
* Business-level settings;
* Business ownership;
* platform relationship;
* tenant-level metadata;
* tenant-level constraints;
* Business UUID usage;
* relationships to Branch, Subscription, Employee, Product, Configuration, and other domains.

