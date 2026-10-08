# Database Architecture

**Document ID:** ARCH-07
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the database architecture for FastFood ERP.

The database must provide:

* strong Business and Branch isolation;
* reliable transactional consistency;
* historical integrity;
* safe concurrent operations;
* UUID-based entity identity;
* offline synchronization support;
* auditability;
* report versioning;
* controlled corrections;
* subscription and data lifecycle support;
* efficient POS operations;
* scalability without unnecessary infrastructure complexity.

The database is the authoritative persistent state for server-side business operations.

---

## 2. Database Architecture Principles

The database architecture follows these principles:

1. **Server authority**
2. **Business isolation**
3. **Branch isolation**
4. **Explicit ownership**
5. **Transactional integrity**
6. **Historical integrity**
7. **UUID identity**
8. **Idempotency**
9. **Concurrency safety**
10. **Controlled corrections**
11. **Append-only history where appropriate**
12. **Query performance without weakening consistency**
13. **Offline synchronization support**
14. **Background processing isolation**
15. **Data lifecycle awareness**

Database design must not turn business rules into uncontrolled database-side behavior that is difficult to test or maintain.

---

# 3. Database Role in the Architecture

The database belongs to the infrastructure layer.

The dependency direction is:

```text
API / Frontend
      ↓
Application Layer
      ↓
Domain Layer
      ↓
Repository / Query Interfaces
      ↓
Database Infrastructure
      ↓
Relational Database
```

Application and domain logic must not depend directly on database-specific implementation details.

Database-specific behavior is isolated behind repositories, query services, transaction infrastructure, and persistence mappings.

---

# 4. Database Model

FastFood ERP uses a relational database as the primary transactional database.

The relational model is preferred because the system requires:

* strong relationships;
* transactional consistency;
* constraints;
* concurrent updates;
* reporting queries;
* historical records;
* financial integrity;
* inventory consistency;
* permission relationships.

The primary database should support:

* ACID transactions;
* row-level locking;
* foreign keys;
* unique constraints;
* indexes;
* transactional isolation;
* JSON/JSONB-style fields where justified;
* reliable timestamp handling;
* backup and recovery.

PostgreSQL is the preferred relational database technology for the initial architecture.

Technology-specific implementation details are defined separately in:

`docs/04_Architecture/18_Technology_Selection.md`

---

# 5. Tenant Data Isolation

Business is the primary tenant boundary.

Most operational entities must contain or be deterministically associated with:

```text
Business
   ↓
Branch
   ↓
Operational Entity
```

Examples:

```text
Business
 ├── Branch
 │    ├── Employee
 │    ├── Cash Register
 │    ├── Cash Session
 │    ├── Order
 │    ├── Inventory
 │    └── Device
 │
 ├── Product
 ├── Recipe
 ├── Menu
 ├── Subscription
 └── Configuration
```

Every server-side query involving tenant-owned data must enforce Business scope.

Application authorization is the primary isolation mechanism.

Database constraints and query structure provide additional protection.

---

# 6. Branch Isolation

Branch-scoped operational data must include a Branch relationship.

Examples:

* Orders
* Cash Sessions
* Inventory
* Attendance
* Branch employees
* Branch menu availability
* Branch pricing overrides
* Branch printers
* Branch reports
* Branch-scoped notifications

A user operating in one Branch must never access another Branch's data without an explicitly authorized multi-Branch scope.

Branch isolation must be enforced consistently in:

* API queries;
* application services;
* repositories;
* background jobs;
* reports;
* exports;
* synchronization;
* administrative operations.

---

# 7. Business-Level vs Branch-Level Data

Not every entity belongs directly to a Branch.

### Business-level entities

Examples:

* Business
* Subscription
* Tariff
* Product
* Recipe
* Set
* Global Menu
* Role
* Business-level Permission Configuration
* Business-level Configuration
* Business-level Notification Configuration

### Branch-level entities

Examples:

* Cash Register
* Cash Session
* Inventory
* Order
* Attendance
* Branch Menu Configuration
* Branch Price Override
* Branch Printer
* Branch Report
* Branch Notification

### Hybrid entities

Some entities have Business ownership and Branch applicability.

For example:

```text
Product
   ↓
Business-owned
   ↓
Branch Menu Configuration
   ↓
Branch-specific availability
```

The database model must preserve this distinction explicitly.

---

# 8. UUID Identity

All major persistent entities use UUID identifiers.

Examples:

* Business UUID
* Branch UUID
* Employee UUID
* Device UUID
* Order UUID
* Payment UUID
* Cash Session UUID
* Inventory Transaction UUID
* Recipe Version UUID
* Report Version UUID
* Audit Event UUID
* Synchronization Event UUID

UUIDs provide:

* globally unique identity;
* offline entity creation;
* synchronization compatibility;
* idempotency;
* safe distributed generation;
* stable historical references.

A human-readable number must never replace the UUID as the primary identity.

---

# 9. Human-Readable Operational Numbers

Some entities may have human-facing numbers.

Example:

```text
Order UUID:
7f3...

Customer-facing Order Number:
124
```

The human-facing number is not the entity identity.

For example, the 3-digit customer-facing order number:

* belongs to the Cash Session context;
* may reset when a new Cash Session starts;
* may be reused in another session;
* must not be used as a foreign key.

The database must preserve the permanent UUID relationship.

---

# 10. Primary Keys

Major entities use UUID primary keys.

Example conceptual structure:

```text
orders
------
id UUID PRIMARY KEY
business_id UUID NOT NULL
branch_id UUID NOT NULL
cash_session_id UUID
employee_id UUID NOT NULL
device_id UUID
status ...
created_at ...
```

Primary keys must remain immutable.

An entity's UUID must never be changed after creation.

---

# 11. Foreign Keys

Foreign keys must be used for strong relationships where appropriate.

Examples:

```text
branch.business_id → business.id

order.business_id → business.id
order.branch_id → branch.id

cash_session.branch_id → branch.id

payment.order_id → order.id

inventory_transaction.product_id → product.id
```

Foreign keys provide structural integrity.

However, not every historical or external reference should necessarily use a hard foreign-key dependency.

This is especially relevant to:

* permanently deleted Businesses;
* historical snapshots;
* archived external references;
* audit records;
* synchronization events.

Such cases require explicit lifecycle rules.

---

# 12. Cross-Tenant Foreign Key Safety

A simple foreign key does not guarantee that two referenced records belong to the same Business.

For example:

```text
order.business_id = Business A
order.branch_id   = Branch B
```

must never be valid if Branch B belongs to Business C.

Therefore application validation and database-level structural design must prevent cross-tenant references.

Where useful, composite ownership keys may be used.

Conceptually:

```text
(branch_id, business_id)
```

can be validated against:

```text
(branch.id, branch.business_id)
```

This pattern may be applied to critical tenant-sensitive relationships.

---

# 13. Aggregate Persistence

Database tables should reflect aggregate ownership rather than creating uncontrolled direct relationships between all modules.

For example:

```text
Order
 ├── Order Items
 ├── Order Item Modifiers
 └── Order Status History
```

An Order aggregate should be persisted through the Order module's persistence boundary.

Other modules must not directly modify Order tables.

Similarly:

```text
Cash Session
 ├── Cash Entries
 ├── Corrections
 └── Closing Data
```

must be owned by the Cash module.

---

# 14. Module Ownership

Each module owns its authoritative tables.

| Module             | Primary Data Ownership                     |
| ------------------ | ------------------------------------------ |
| Business           | Business                                   |
| Identity & Access  | Employees, Roles, Permissions              |
| Subscription       | Subscriptions, Tariffs, Entitlements       |
| Branch             | Branches                                   |
| Order              | Orders, Order Items, Status History        |
| Cash               | Cash Registers, Cash Sessions, Corrections |
| Inventory          | Stock, Inventory Transactions, Adjustments |
| Payment            | Payments, Payment Portions, Refunds        |
| Menu & Pricing     | Products, Prices, Menu Configuration       |
| Kitchen            | Kitchen Tickets, Print Jobs                |
| Employee & Payroll | Attendance, Payroll                        |
| Reporting          | Reports, Report Versions                   |
| Notification       | Notifications                              |
| Audit              | Audit Events                               |
| Synchronization    | Sync Events, Conflicts                     |
| Data Lifecycle     | Lifecycle State and Deletion Jobs          |
| Configuration      | Configuration Versions                     |
| Device & Trust     | Devices, Trust State                       |

Cross-module writes must go through application services or explicit domain/application events.

---

# 15. Transaction Boundaries

Database transactions must correspond to business consistency boundaries.

For example:

```text
Accept Order
    ↓
Validate Order
    ↓
Validate Stock
    ↓
Deduct Inventory
    ↓
Persist Accepted Order
    ↓
Commit
```

Order acceptance and inventory deduction must succeed or fail together.

Kitchen notification is secondary:

```text
Core Transaction
    ↓
Commit
    ↓
Kitchen Event / Print Job
```

A printer failure must not roll back the successful order transaction.

---

# 16. Payment Transactions

Payment creation must use a transactional boundary.

Conceptually:

```text
Validate Order
    ↓
Validate Payment
    ↓
Validate Remaining Amount
    ↓
Create Payment
    ↓
Update Payment State
    ↓
Update Related Financial State
    ↓
Commit
```

The original payment record must remain historically recoverable.

Controlled corrections create separate records rather than silently rewriting the original financial state.

---

# 17. Inventory Transactions

Inventory must be transaction-based.

Stock should not be treated as an arbitrary mutable number.

Conceptually:

```text
Inventory Balance
        ↑
Inventory Transactions
        ↑
Purchase / Sale / Return / Adjustment / Production
```

Inventory transactions must record:

* UUID;
* Business;
* Branch;
* Product;
* quantity;
* transaction type;
* source;
* actor;
* device;
* timestamp;
* related transaction UUID;
* reason where required.

The system must prevent negative stock.

---

# 18. Inventory Concurrency

Concurrent stock operations must use database transaction mechanisms.

Example:

```text
Current Stock = 1

Cashier A → Sell 1
Cashier B → Sell 1
```

Only one operation may successfully consume the final available unit.

The second operation must fail or enter the defined conflict path.

Possible implementation techniques include:

* row-level locking;
* atomic conditional updates;
* transaction isolation;
* version checks.

The exact mechanism is an implementation decision, but the business invariant is mandatory.

---

# 19. Cash Session Consistency

A Branch normally has one active Cash Session for its physical register.

The database must prevent accidental concurrent active sessions.

Conceptually:

```text
Branch
   ↓
Cash Register
   ↓
Active Cash Session
```

The system must enforce:

```text
At most one active session per physical register
```

The database may use:

* unique constraints;
* partial unique indexes;
* transactional checks.

The first successful session-opening transaction wins.

Concurrent attempts must receive a conflict.

---

# 20. Order and Cash Session Relationship

An Order may move across Cash Sessions during cashier handover.

The Order UUID remains unchanged.

Historical information must preserve:

```text
Original Cash Session
Original Employee
Original Device
```

Later operations may reference:

```text
Current Cash Session
Current Employee
Current Device
```

The database must therefore distinguish:

* original creation context;
* later operational context.

Historical context must never be silently overwritten.

---

# 21. Historical Snapshots

Operational entities must preserve historical information that may change later.

Examples:

* product price;
* product name;
* recipe version;
* employee information relevant to a transaction;
* customer information attached to a historical order;
* payment information;
* configuration version.

For example:

```text
Product Current Price = 35,000

Historical Order Item Price = 32,000
```

Changing the current Product price must not change the historical Order Item.

---

# 22. Configuration Versioning

Configuration that affects operations must be versioned.

Examples:

* recipes;
* prices;
* Sets;
* printer routing;
* notification thresholds;
* permissions;
* branch menu configuration.

Conceptually:

```text
Configuration
   ↓
Version 1
Version 2
Version 3
   ↓
Effective Version
```

Historical versions are immutable.

Rollback is implemented by creating a new version based on an earlier state.

---

# 23. Recipe Versioning

Recipes must never be silently overwritten when historical transactions depend on them.

Conceptually:

```text
Recipe
 ├── Version 1
 ├── Version 2
 └── Version 3
```

An Order or Inventory Transaction must retain the relevant recipe/configuration snapshot or version reference.

This guarantees historical reconstruction.

---

# 24. Price Storage

The database must distinguish:

* global standard price;
* branch override;
* historical price;
* effective configuration version;
* order-time price snapshot.

An Order Item must contain the price actually used for that transaction.

Current Product price must never be used to reconstruct historical sales.

---

# 25. Soft Deletion and Archiving

Destructive deletion should be avoided for operational entities.

Typical lifecycle:

```text
Active
  ↓
Inactive
  ↓
Archived
```

Examples:

* Product
* Recipe
* Menu Item
* Employee
* Configuration
* Device

Deletion may be used only where:

* historical integrity is not affected;
* retention rules permit it;
* legal/business requirements allow it;
* no required references depend on the record.

---

# 26. Data Lifecycle Deletion

Business data has a defined lifecycle.

Conceptually:

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

The database must support controlled deletion workflows.

Deletion must:

* be performed by background processing;
* be dependency-aware;
* be idempotent;
* be retryable;
* prevent stale offline data from recreating the Business;
* invalidate trusted devices;
* preserve required system-level deletion history where permitted.

The Business UUID must never be reused.

---

# 27. Audit Database

Audit data must be separated logically from ordinary operational data.

Audit records are immutable.

Typical fields include:

```text
audit_event
------------
id
business_id
branch_id
actor_type
actor_id
device_id
cash_session_id
transaction_id
entity_type
entity_id
action
old_state
new_state
reason
result
source
client_timestamp
server_timestamp
created_at
```

Audit storage must support historical reconstruction without modifying previous records.

---

# 28. Audit and Transaction Reliability

Important state-changing operations must not succeed while silently losing their required audit information.

Possible implementation approaches include:

* same database transaction;
* transactional outbox;
* durable event persistence followed by asynchronous processing.

The selected implementation must guarantee that required audit information cannot disappear silently.

---

# 29. Synchronization Data

Synchronization requires durable server-side records.

Typical synchronization entities:

```text
sync_event
sync_batch
sync_conflict
sync_attempt
```

Each synchronization event must have stable identity.

Example:

```text
sync_event.id = UUID
transaction_id = UUID
device_id = UUID
business_id = UUID
branch_id = UUID
```

A synchronization request may be retried without creating duplicate business transactions.

---

# 30. Idempotency Constraints

UUID identity must be supported by database uniqueness constraints.

For example:

```text
orders.id UNIQUE
payments.id UNIQUE
inventory_transactions.id UNIQUE
sync_events.id UNIQUE
```

If the same operation arrives again:

```text
UUID already exists
        ↓
Do not create duplicate record
        ↓
Return existing result
```

Idempotency must not depend only on application memory.

---

# 31. Synchronization Conflicts

Conflicting operations must be stored explicitly.

Conceptually:

```text
sync_conflict
-------------
id
business_id
branch_id
transaction_id
entity_type
entity_id
conflict_type
local_state
server_state
status
resolution
resolved_by
resolved_at
reason
```

Conflict records must remain available for investigation and audit according to retention policy.

---

# 32. Timestamp Strategy

The system must distinguish:

* client timestamp;
* server timestamp.

Server time is authoritative for:

* subscription expiry;
* lifecycle transitions;
* permission changes;
* device trust;
* report periods;
* financial timestamps where authoritative server time is required.

Client timestamps are retained for diagnostic and offline context.

Clock anomalies must be detectable.

---

# 33. Timestamp Storage

Timestamps should use timezone-aware values.

The system should store timestamps in a consistent canonical representation, preferably UTC.

User-facing interfaces may convert timestamps to the configured Business or user timezone.

Database timestamps must not depend on the local timezone of the POS machine.

---

# 34. Database Constraints

Database constraints should protect fundamental invariants.

Examples:

### Required values

```text
business_id NOT NULL
branch_id NOT NULL
created_at NOT NULL
```

### Positive quantities where required

```text
quantity > 0
```

### Valid monetary values

```text
amount >= 0
```

### Unique identity

```text
UUID UNIQUE
```

### Valid lifecycle states

```text
status IN (...)
```

Constraints should protect structural invariants.

Complex business workflows should remain in application/domain services.

---

# 35. Monetary Values

Money must not be stored using floating-point types.

Use an exact numeric representation appropriate for the selected database implementation.

Conceptually:

```text
amount NUMERIC(...)
```

Currency must be explicit where multi-currency support could be introduced later.

For the current product scope, the business currency configuration must be represented consistently.

---

# 36. Quantity Precision

Inventory quantities may require fractional values.

Examples:

```text
1 kg
0.250 kg
1.5 L
0.020 kg
```

The database must therefore support appropriate decimal precision.

Floating-point arithmetic must not be used for authoritative inventory quantities.

The exact precision and scale are implementation decisions based on supported units.

---

# 37. JSON / Flexible Data

Structured relational columns should be preferred for frequently queried business data.

JSON/JSONB-style fields may be used for:

* extensible configuration;
* metadata;
* selected snapshots;
* external integration payloads;
* diagnostic information.

JSON must not become a replacement for relational modeling.

Frequently queried fields should have explicit columns.

---

# 38. Indexing Strategy

Indexes must support real query patterns.

Important index dimensions include:

* Business;
* Branch;
* status;
* created_at;
* updated_at;
* employee;
* device;
* Cash Session;
* Order;
* Product;
* transaction UUID;
* report period;
* synchronization state.

Typical compound index:

```text
(branch_id, status, created_at)
```

Indexes must be based on actual query patterns rather than added indiscriminately.

---

# 39. Tenant-Aware Indexing

For tenant-owned tables, Business and Branch should be considered when designing indexes.

Example:

```text
(business_id, branch_id, created_at)
```

or:

```text
(branch_id, status, created_at)
```

The exact index order depends on the query pattern.

The objective is to avoid full-table scans for normal operational queries.

---

# 40. Partial and Specialized Indexes

Where supported, specialized indexes may improve performance.

Example:

```text
Active Cash Sessions
```

can use a partial unique index representing:

```text
WHERE status = 'OPEN'
```

Similar strategies may be used for:

* active devices;
* unresolved conflicts;
* pending synchronization;
* active configurations.

Such indexes must correspond to stable business invariants.

---

# 41. Unique Constraints

Unique constraints should protect identity and critical uniqueness rules.

Examples:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Payment UUID;
* Order UUID;
* Sync Event UUID;
* one active Cash Session per Register;
* unique configuration version identity.

Business-level uniqueness should not be assumed unless explicitly required.

For example, duplicate phone numbers for debt customers are allowed.

---

# 42. Query Architecture

Read operations should not always load complete aggregates.

The architecture supports dedicated query models/read queries.

Example:

```text
POS Order List
```

does not need to load:

* full audit history;
* all configuration versions;
* complete inventory history.

Instead, a projection/query can return only required fields.

This protects POS performance.

---

# 43. Write vs Read Optimization

The database architecture distinguishes:

```text
Write Model
    ↓
Authoritative transactional state

Read Model
    ↓
Optimized query representation
```

The initial system may use the same relational database for both.

Separate databases are not required unless scale justifies them.

---

# 44. Reporting Data

Reports must use consistent database snapshots.

Report generation must not read partially committed business transactions.

For heavy reports:

```text
Operational Database
       ↓
Background Report Job
       ↓
Consistent Read
       ↓
Report Version
```

Report generation must not block normal POS transactions unnecessarily.

---

# 45. Report Version Storage

Reports are immutable versions.

Conceptually:

```text
report
  ↓
report_version_1
report_version_2
report_version_3
```

Each version should preserve:

* report identity;
* Business;
* Branch/scope;
* period;
* creation time;
* creator/source;
* reason;
* relevant data state;
* generation status;
* file reference where applicable.

A new relevant correction may create a new report version.

---

# 46. Background Job Persistence

Background jobs require durable state.

Examples:

* report generation;
* notification retry;
* synchronization processing;
* deletion processing;
* subscription lifecycle;
* data cleanup;
* export generation.

Job state should include:

```text
Pending
Running
Retrying
Completed
Failed
```

Jobs must be idempotent where possible.

---

# 47. Database Connection Management

The backend must use a controlled database connection pool.

The pool must:

* limit concurrent connections;
* prevent connection exhaustion;
* recover broken connections;
* support transaction boundaries;
* release connections reliably.

A connection must not remain open while performing unrelated external operations.

---

# 48. Transaction Scope

Transactions should be as short as practical.

Avoid:

```text
BEGIN
   database work
   network request
   printer request
   external API request
   long calculation
COMMIT
```

Prefer:

```text
BEGIN
   validate
   update
   persist
COMMIT

Then:

background / external processing
```

This reduces lock duration and improves POS concurrency.

---

# 49. Row Locking

Row-level locking may be used for highly concurrent resources.

Important candidates include:

* inventory stock;
* Cash Session state;
* payment allocation;
* debt balance;
* configuration activation;
* report generation identity.

Locks must be acquired in a predictable order to reduce deadlock risk.

---

# 50. Deadlock Handling

Deadlocks are possible in concurrent systems.

The application must:

* detect database deadlock errors;
* retry safe transactions where appropriate;
* avoid retrying non-idempotent operations blindly;
* record persistent failures;
* expose stable application errors.

Transaction design should minimize deadlock probability.

---

# 51. Isolation Levels

The database must use an isolation level appropriate for each operation.

Normal operations should avoid unnecessarily expensive isolation.

Critical operations may require stronger guarantees.

Examples:

* order acceptance;
* inventory deduction;
* payment allocation;
* cash session opening;
* cash session closing;
* correction authorization.

The selected isolation level must guarantee business invariants without creating unnecessary contention.

---

# 52. Optimistic Concurrency

Optimistic concurrency may be used for configuration and administrative records.

Example:

```text
Version = 5

Client reads Version 5

Another user saves Version 6

First client attempts save using Version 5
        ↓
Reject as stale
```

This prevents silent overwrites.

It is particularly useful for:

* menu configuration;
* prices;
* recipes;
* Sets;
* notification configuration;
* permissions.

---

# 53. Database-Level vs Application-Level Rules

Not every business rule should be implemented as a database trigger.

### Prefer database constraints for:

* identity;
* uniqueness;
* referential integrity;
* basic value validity;
* structural invariants.

### Prefer application/domain logic for:

* authorization;
* subscription entitlement;
* workflow;
* approval;
* correction rules;
* conflict resolution;
* notification decisions;
* complex business calculations.

This keeps business behavior testable and understandable.

---

# 54. Database Triggers

Triggers should be used sparingly.

They may be considered for:

* technical integrity;
* automatic metadata;
* low-level protection where application enforcement is insufficient.

Business workflows should not depend heavily on hidden triggers.

Hidden database behavior makes:

* debugging;
* testing;
* migrations;
* synchronization

more difficult.

---

# 55. Migration Strategy

Database schema changes must use versioned migrations.

Every schema change must be:

* versioned;
* reviewable;
* reproducible;
* testable;
* reversible where technically possible;
* compatible with deployment strategy.

Migration history must be stored in the database.

---

# 56. Backward-Compatible Migrations

Production migrations should preferably follow:

```text
Expand
   ↓
Deploy compatible code
   ↓
Migrate data
   ↓
Switch usage
   ↓
Contract
```

Avoid migrations that require long application downtime.

This is particularly important for a POS system where branch operations should continue with minimal interruption.

---

# 57. Data Backfill

Large data migrations must not block operational traffic unnecessarily.

Backfills should:

* run in batches;
* be restartable;
* report progress;
* avoid long locks;
* be idempotent;
* support failure recovery.

Background migration jobs may be used where appropriate.

---

# 58. Backup Strategy

The database must support reliable backups.

Backup strategy must include:

* regular automated backups;
* backup verification;
* retention policy;
* recovery testing;
* protection against accidental deletion;
* documented restoration procedure.

A backup that has never been restored successfully must not be considered fully verified.

---

# 59. Recovery Objectives

Database operations should define:

* Recovery Point Objective (RPO);
* Recovery Time Objective (RTO).

Exact production values depend on infrastructure and service requirements.

Architecture must support recovery without violating:

* historical integrity;
* transaction identity;
* synchronization correctness;
* tenant isolation.

---

# 60. Point-in-Time Recovery

Where supported by the selected database platform, point-in-time recovery should be considered for production.

This protects against:

* accidental deletion;
* corrupted deployment;
* operator mistakes;
* destructive migrations.

Recovery procedures must be tested periodically.

---

# 61. Backup Security

Backups contain sensitive Business data.

They must therefore have:

* access control;
* encryption at rest where supported;
* secure storage;
* controlled retention;
* restricted operator access;
* auditability.

Backup credentials must not be stored in application source code.

---

# 62. Data Retention

Retention depends on domain requirements.

Examples:

| Data                   | Retention Principle                       |
| ---------------------- | ----------------------------------------- |
| Orders                 | Historical                                |
| Payments               | Historical                                |
| Inventory Transactions | Historical                                |
| Cash Sessions          | Historical                                |
| Audit                  | Long-term according to policy             |
| Report Versions        | Historical                                |
| Notifications          | Lifecycle-defined                         |
| Sync Events            | Operational retention                     |
| Temporary Jobs         | Cleanup after completion/failure          |
| Deleted Business Data  | Permanent deletion according to lifecycle |

Retention policies must not silently destroy data required for historical integrity.

---

# 63. Database Security

Database access must follow least privilege.

Application services should not use unrestricted database administrator credentials.

Separate credentials/roles should be considered for:

* application runtime;
* migration execution;
* reporting;
* operational administration;
* backup/recovery.

Database credentials must be managed securely.

---

# 64. Encryption

Sensitive data should be protected both:

```text
In Transit
```

and:

```text
At Rest
```

Database-level encryption may be used for storage protection.

Application-level encryption may be used for especially sensitive values where required.

Encryption keys must be managed outside application source code.

---

# 65. Password and Authentication Data

Passwords must never be stored as plaintext.

Authentication secrets must be stored using secure password hashing mechanisms.

Database architecture must not expose:

* plaintext passwords;
* authentication tokens;
* private cryptographic keys.

Device trust and offline authorization secrets require additional protection.

---

# 66. Sensitive Snapshots

Historical snapshots may contain sensitive information.

Examples:

* employee information;
* customer phone/address;
* payment metadata;
* permission state.

Snapshot storage must follow the same security and retention principles as the underlying business data.

---

# 67. Customer Information

The current product does not maintain a full CRM.

Delivery/customer information attached to an order is therefore transaction data.

Historical order information may contain:

* customer name;
* phone;
* delivery address.

This information must remain associated with the historical order when required for business records.

It must not automatically become a permanent global customer profile.

---

# 68. Database Performance for POS

POS operations have priority over heavy analytical workloads.

Critical operations must be optimized:

* login/session validation;
* product lookup;
* order creation;
* order acceptance;
* inventory validation;
* payment;
* cash operations.

Heavy reports, exports, and maintenance tasks should be isolated through background processing where necessary.

---

# 69. Query Performance Requirements

Common POS queries should use indexed access paths.

Examples:

```text
Find active products
Find current menu
Find open orders
Find table state
Find active cash session
Find available stock
Find current employee permissions
Find pending synchronization events
```

Slow queries must be identified through observability.

Query optimization must be evidence-based.

---

# 70. Pagination

Large datasets must not be loaded completely into memory.

Administrative and reporting lists should use pagination.

Examples:

* Orders;
* Employees;
* Inventory Transactions;
* Audit Events;
* Payments;
* Notifications;
* Synchronization Conflicts.

Cursor/keyset pagination should be considered for large time-ordered datasets.

---

# 71. Sorting and Filtering

Filtering and sorting should use indexed database fields where practical.

Users must not be given unrestricted arbitrary SQL.

Allowed filters should be explicitly defined by the query API.

This protects:

* security;
* performance;
* predictability.

---

# 72. Full-Text Search

Full-text search should be introduced only where needed.

Simple indexed search is preferred for:

* product code;
* product name;
* employee name;
* order number.

A dedicated search engine is not required unless future scale justifies it.

---

# 73. Caching and Database Consistency

Caching must not become an alternative source of truth.

The database remains authoritative.

Cacheable information may include:

* menu configuration;
* product catalog;
* permissions;
* subscription entitlement;
* frequently accessed read models.

Cache invalidation must follow configuration/version changes.

---

# 74. Offline Database

Offline POS devices may use a local embedded database.

The local database is not equivalent to the server database.

It acts as:

```text
Local Operational Store
        ↓
Offline Queue
        ↓
Synchronization
        ↓
Server Database
```

Local data must be:

* encrypted;
* Business/Branch scoped;
* Device scoped;
* protected from replay;
* synchronized through UUID-based operations.

---

# 75. Local Database Schema

The offline database should contain only data required for offline operation.

Possible categories:

* trusted employee/device state;
* authorized permissions;
* current valid menu/configuration;
* product data;
* recipe data required for local validation;
* current inventory state;
* open orders;
* cash session state;
* pending synchronization events;
* conflict state;
* local audit context.

Unnecessary server-wide data must not be replicated.

---

# 76. Local vs Server Authority

The server database remains authoritative for general current state.

Offline transactions retain their original identity.

Example:

```text
Offline Order UUID
      ↓
Local Database
      ↓
Sync
      ↓
Server validates
      ↓
Existing UUID reused
```

The server must not silently replace the offline Order UUID.

---

# 77. Sync Ordering and Database Constraints

Synchronization must respect business dependencies.

Example:

```text
Create Order
      ↓
Accept Order
      ↓
Inventory Deduction
      ↓
Payment
```

An operation depending on another operation must not be applied first.

Database constraints must reject invalid state transitions.

---

# 78. Duplicate Synchronization

If the same synchronization event arrives multiple times:

```text
Existing UUID
      ↓
Detect duplicate
      ↓
Return previous result
```

The database must prevent duplicate financial or inventory effects.

This is one of the most important protections in the offline architecture.

---

# 79. Transactional Outbox

Where asynchronous events are required, a transactional outbox pattern may be used.

Conceptually:

```text
Business Transaction
       ↓
Database Transaction
 ├── Business State
 └── Outbox Event
       ↓
Commit
       ↓
Background Worker
       ↓
Event Processing
```

This is useful for:

* notifications;
* kitchen events;
* report generation;
* audit processing where appropriate;
* synchronization-related events.

The outbox record must share the same transaction as the state change when atomic event publication is required.

---

# 80. Event Deduplication

Consumers of outbox/events must be idempotent.

Each event must have stable identity.

Example:

```text
event_id UUID UNIQUE
```

If a worker receives the same event twice, the consumer must not create duplicate business effects.

---

# 81. Data Integrity Checks

Periodic integrity checks may validate:

* orphan records;
* invalid Business/Branch relationships;
* impossible stock balances;
* duplicate active sessions;
* inconsistent report metadata;
* unresolved lifecycle states;
* synchronization anomalies.

Integrity checks must normally run as background jobs.

They must not block POS operations.

---

# 82. Database Monitoring

The production database must be monitored for:

* connection usage;
* CPU;
* memory;
* storage;
* query latency;
* lock waits;
* deadlocks;
* slow queries;
* replication/backup status where applicable;
* failed transactions;
* table/index growth.

Database observability belongs to the broader Operations architecture.

---

# 83. Schema Growth

The initial system may operate with a relatively small number of Branches.

The database architecture must still support future growth.

The design must avoid assumptions such as:

```text
one Business = one Branch
```

or:

```text
one Employee = one Branch
```

or:

```text
one Device = one Employee
```

Relationships must support the already-defined multi-Branch model.

---

# 84. Partitioning

Partitioning is not required by default.

It may be introduced later for very large tables such as:

* Audit Events;
* Inventory Transactions;
* Orders;
* Synchronization Events;
* Notifications.

Partitioning must be introduced only when:

* data volume justifies it;
* query patterns are understood;
* operational complexity is acceptable.

---

# 85. Read Replicas

Read replicas are not required for the initial architecture.

They may be introduced later for:

* heavy reporting;
* analytics;
* large read workloads.

Critical transactional reads must continue using an authoritative source where stale data would violate business rules.

---

# 86. Multi-Database Strategy

The initial architecture should prefer one primary relational database.

Additional databases should be introduced only when there is a clear architectural reason.

Possible future separation:

```text
Primary Transaction Database
        ↓
Reporting / Analytics Store
```

This is a scaling option, not a mandatory initial design.

---

# 87. Database Anti-Patterns

The following are prohibited or strongly discouraged:

### Direct cross-module table writes

```text
Order module → UPDATE inventory tables directly
```

### Shared unrestricted database access

```text
Every module → Every table
```

### Floating-point money

```text
FLOAT / DOUBLE for authoritative money
```

### Human number as primary identity

```text
Order Number → Primary Key
```

### Silent historical overwrite

```text
UPDATE old payment
```

without preserving the original state.

### Uncontrolled cascade deletion

```text
DELETE Business
→ unexpectedly delete historical records
```

### Database as business workflow engine

Large hidden trigger-based workflows should be avoided.

### Arbitrary SQL from users

Users must not execute unrestricted queries.

### Long-running transactions

External requests must not remain inside database transactions.

---

# 88. Database Error Handling

Database errors must be mapped into application-level errors.

Examples:

```text
UniqueViolation
ForeignKeyViolation
ConcurrencyConflict
DeadlockDetected
SerializationFailure
ConnectionFailure
Timeout
```

The API must expose stable machine-readable error codes rather than raw database errors.

Database implementation details must not leak to clients.

---

# 89. Transaction Retry Policy

Some database failures are safely retryable.

Examples:

* deadlock;
* serialization failure;
* temporary connection failure.

Other errors are not automatically retryable.

Examples:

* validation failure;
* unique business conflict;
* permission failure;
* insufficient stock.

Retry logic must therefore classify database failures before retrying.

---

# 90. Database Timeouts

Database operations must have reasonable timeouts.

A slow query must not indefinitely occupy:

* a backend worker;
* a database connection;
* a transaction;
* a POS request.

Timeouts should produce controlled application errors and observability records.

---

# 91. Data Import

Excel import is supported for relevant business data.

Imports must not directly manipulate tables.

Preferred flow:

```text
Upload
   ↓
Validate
   ↓
Parse
   ↓
Application Commands
   ↓
Database Transaction(s)
```

Imported data must pass the same business rules as manually created data.

---

# 92. Excel Export

Exports should read through authorized query services.

Export operations must enforce:

* Business scope;
* Branch scope;
* permissions;
* subscription read-only rules;
* historical access rules.

Large exports should run as background jobs.

---

# 93. Security Boundary

The database must never be treated as the only authorization boundary.

Authorization must occur before data access.

The normal flow is:

```text
Authenticate
    ↓
Resolve Employee
    ↓
Resolve Business
    ↓
Resolve Branch Scope
    ↓
Resolve Permissions
    ↓
Resolve Subscription Entitlement
    ↓
Execute Query/Command
```

Database filtering provides defense in depth.

---

# 94. Data Access Layer

The backend should expose repositories/query interfaces rather than allowing application services to construct arbitrary database operations everywhere.

Example:

```text
OrderRepository
InventoryRepository
PaymentRepository
CashSessionRepository
ReportRepository
AuditRepository
```

Repositories own aggregate persistence.

Dedicated query services own optimized read queries.

---

# 95. Unit of Work

A Unit of Work coordinates database changes belonging to one application transaction.

Example:

```text
Unit of Work
 ├── Order change
 ├── Inventory change
 ├── Payment-related state
 └── Audit/outbox state
```

Commit happens once the complete consistency boundary succeeds.

Rollback must revert all transactional changes.

---

# 96. Database Testing

Database behavior must be tested at several levels.

### Unit-level

Test domain rules without a real database where possible.

### Integration-level

Test:

* repositories;
* constraints;
* transactions;
* locking;
* migrations;
* indexes;
* idempotency.

### Concurrency-level

Test:

* last-stock sale;
* simultaneous Cash Session opening;
* concurrent payment;
* configuration update;
* synchronization duplicates.

### Recovery-level

Test:

* database failure;
* rollback;
* retry;
* migration failure;
* restore.

---

# 97. Seed Data

Seed data must be controlled and versioned.

Examples:

* system permissions;
* default roles;
* predefined configuration values.

Business-specific data must not be confused with immutable system seed data.

Production seed changes must use migrations or controlled administrative processes.

---

# 98. Development Database

Development environments should allow isolated databases or schemas per developer/test environment.

Production data must never be copied into development without appropriate anonymization and authorization.

Test data must not contain real authentication secrets.

---

# 99. Production Database Access

Production database access must be restricted.

Direct manual modification of production business data should be prohibited except through controlled administrative procedures.

If emergency intervention is required:

* authorization is required;
* action must be recorded;
* reason must be documented;
* historical integrity must be preserved.

---

# 100. Database Architecture Invariants

The following invariants are mandatory:

1. Every major persistent entity has a stable UUID.
2. UUIDs are immutable.
3. Business isolation is mandatory.
4. Branch isolation is mandatory for branch-scoped data.
5. Cross-Business references are forbidden.
6. Cross-Branch access requires authorization.
7. Operational tables have explicit ownership.
8. Cross-module direct writes are prohibited.
9. Financial operations are transactional.
10. Inventory operations are transactional.
11. Negative stock is prohibited.
12. Concurrent stock consumption is safely controlled.
13. One active Cash Session per physical register is enforced.
14. Cash Session identity is never reused.
15. Historical transaction prices are preserved.
16. Historical recipe/configuration versions are preserved.
17. Historical payment state is preserved.
18. Corrections do not silently overwrite originals.
19. UUIDs provide synchronization idempotency.
20. Duplicate synchronization must not duplicate business effects.
21. Client timestamps do not replace authoritative server timestamps.
22. Money uses exact numeric representation.
23. Inventory quantities use appropriate decimal precision.
24. Foreign keys protect required structural relationships.
25. Database constraints protect fundamental invariants.
26. Complex business workflows remain in application/domain layers.
27. Database triggers are used sparingly.
28. Long-running external operations do not occur inside transactions.
29. Transactions remain as short as practical.
30. Deadlocks are detected and safely handled.
31. Safe transaction failures may be retried.
32. Unsafe operations are not blindly retried.
33. Background jobs have durable state.
34. Background jobs are idempotent where possible.
35. Outbox events have stable identity.
36. Event consumers are idempotent.
37. Audit records are immutable.
38. Required audit data cannot silently disappear.
39. Report versions are immutable.
40. Report generation does not block POS unnecessarily.
41. Large exports run asynchronously where appropriate.
42. Pagination is used for large datasets.
43. Arbitrary user SQL is prohibited.
44. Database errors are mapped to stable application errors.
45. Database credentials follow least privilege.
46. Authentication secrets are never stored in plaintext.
47. Backups are protected.
48. Backups are tested through restoration.
49. Recovery procedures preserve identity and integrity.
50. Schema changes use versioned migrations.
51. Production migrations prefer backward-compatible deployment.
52. Large data backfills are restartable.
53. Destructive deletion is avoided where history is required.
54. Business deletion follows the Data Lifecycle model.
55. Deleted Business UUIDs are never reused.
56. Stale offline data cannot recreate deleted Business data.
57. Offline local databases are not treated as server authority.
58. Synchronization uses stable UUIDs.
59. Synchronization follows dependency order.
60. Configuration versions are immutable.
61. Optimistic concurrency may protect administrative configuration.
62. Stale configuration updates are rejected.
63. Cache is never the authoritative source of business state.
64. Read replicas must not be used where stale data would violate critical rules.
65. Partitioning is introduced only when justified by scale.
66. One primary relational database is preferred initially.
67. Query performance is monitored.
68. Lock contention is monitored.
69. Connection pools are bounded.
70. Database timeouts are enforced.
71. Imports use application validation.
72. Exports use authorization checks.
73. Audit and historical data follow retention rules.
74. Sensitive data receives appropriate protection.
75. Database access is never the sole authorization boundary.
76. Repository boundaries protect aggregate ownership.
77. Unit of Work coordinates transactional changes.
78. Integration tests verify database constraints.
79. Concurrency tests verify critical invariants.
80. Recovery tests verify failure handling.
81. Seed data is version-controlled.
82. Production database changes are controlled.
83. Emergency database intervention is audited.
84. Business-level and Branch-level configuration remain distinguishable.
85. Historical snapshots remain reconstructable.
86. Operational state and configuration state remain distinct.
87. Current state changes do not rewrite historical transactions.
88. Report versions reference relevant underlying data state.
89. Synchronization conflicts are explicitly persisted.
90. Conflict resolution requires authorization and audit.
91. Subscription lifecycle state is persisted.
92. Data deletion cannot bypass lifecycle checks.
93. Device trust state is persisted and revocable.
94. Employee deactivation is enforced against future operations.
95. Permission changes take effect according to server-authoritative rules.
96. Database design supports multiple Branches per Business.
97. Database design supports employees working across multiple Branches.
98. Database design supports multiple trusted devices.
99. Database design supports offline-generated UUIDs.
100. Database architecture must preserve historical integrity, transactional correctness, tenant isolation, and operational performance.

---

# 101. Completion Criteria

This document is considered implemented when:

* database technology is selected;
* schema ownership is mapped to modules;
* aggregate persistence boundaries are defined;
* Business and Branch isolation is enforced;
* UUID identity is implemented;
* critical constraints are implemented;
* transaction boundaries are implemented;
* inventory concurrency is protected;
* Cash Session uniqueness is enforced;
* historical snapshots are implemented;
* configuration versioning is implemented;
* synchronization persistence is implemented;
* idempotency constraints are implemented;
* audit persistence is reliable;
* report version persistence is implemented;
* background job persistence is implemented;
* database migrations are versioned;
* backup and recovery procedures exist;
* database security controls are implemented;
* integration and concurrency tests pass;
* production monitoring is available.

---

# 102. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`

### Domain Analysis

* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`
* `docs/03_Domain_Analysis/13_Reporting_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/18_Configuration_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`

### Architecture

* `docs/04_Architecture/01_System_Architecture.md`
* `docs/04_Architecture/02_Application_Layer_Architecture.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/04_Backend_Architecture.md`
* `docs/04_Architecture/05_Frontend_Architecture.md`
* `docs/04_Architecture/06_API_Architecture.md`

### Next Architecture Document

`docs/04_Architecture/08_Offline_Architecture.md`

---

# 103. Final Status

Database Architecture is **Accepted v1.0**.

The database architecture provides the persistence foundation for:

* multi-tenant Business isolation;
* multi-Branch operations;
* POS transactions;
* inventory consistency;
* cash management;
* payments;
* historical integrity;
* offline synchronization;
* reporting;
* audit;
* subscription lifecycle;
* data deletion;
* scalable future operation.

The database remains the authoritative server-side source of persistent business state while supporting controlled offline operation and synchronization.

