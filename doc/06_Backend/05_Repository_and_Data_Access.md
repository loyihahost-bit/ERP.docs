# Repository and Data Access

**Document ID:** BE-05
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/06_Backend/README.md`

---

## 1. Purpose

This document defines the Repository and Data Access architecture of FastFood ERP.

The Repository Layer provides controlled access to persistent data while keeping the Application and Domain Layers independent from the database implementation.

The primary database is PostgreSQL.

The current persistence technology is SQLAlchemy.

The Repository Layer must enforce data access boundaries without becoming the owner of business workflows.

---

## 2. Repository Principle

The Repository Layer answers:

> How is persistent data loaded and stored?

It does not answer:

> Is this business operation allowed?

Business rules belong to the Domain Layer.

Application workflows belong to the Application Layer.

Database persistence belongs to the Repository/Infrastructure Layer.

---

## 3. Layer Relationship

The dependency direction is:

```text id="rep814"
API
 ↓
Application
 ↓
Domain
 ↓
Repository Abstraction
 ↓
Infrastructure Repository
 ↓
SQLAlchemy
 ↓
PostgreSQL
```

The Domain Layer must not depend on SQLAlchemy.

The API Layer must not directly access SQLAlchemy repositories for business mutations.

---

## 4. Repository Responsibilities

Repositories are responsible for:

1. Loading persistent entities.
2. Saving persistent entities.
3. Updating persistent state.
4. Deleting data only where explicitly permitted.
5. Querying scoped data.
6. Applying persistence-specific filters.
7. Supporting locking where required.
8. Supporting efficient query patterns.
9. Translating persistence models to domain/application representations where appropriate.

Repositories are not responsible for:

* authentication;
* permission decisions;
* HTTP responses;
* notification delivery;
* business workflow orchestration;
* transaction ownership.

---

# 5. Repository Types

The architecture may use several repository categories.

### Entity Repository

Used for aggregate/entity persistence.

Examples:

```text id="rcw421"
OrderRepository
ProductRepository
EmployeeRepository
CashSessionRepository
RecipeRepository
```

### Query Repository

Used for optimized read operations.

Examples:

```text id="kz1c8f"
OrderListQuery
InventorySummaryQuery
DashboardQuery
CashReportQuery
```

### Specialized Repository

Used when a domain requires a specialized persistence operation.

Examples:

```text id="v2yls5"
InventoryLedgerRepository
ConfigurationVersionRepository
ReportVersionRepository
AuditRepository
```

---

# 6. Repository Interface

Application code should depend on repository abstractions rather than concrete SQLAlchemy implementations.

Conceptual example:

```text id="u0h1kl"
OrderRepository
    get()
    get_for_update()
    add()
    save()
```

Infrastructure provides the implementation.

---

# 7. Repository Location

Following the accepted project structure:

```text id="9d7q4k"
app/
├── application/
├── domain/
└── infrastructure/
    └── repositories/
```

Repository interfaces may be defined at the appropriate abstraction boundary.

Concrete implementations belong under Infrastructure.

---

# 8. Repository Naming

Use explicit domain-oriented names.

Preferred:

```text id="7b6vte"
OrderRepository
PaymentRepository
CashSessionRepository
InventoryRepository
ProductRepository
RecipeRepository
```

Avoid generic names such as:

```text id="z4n9k1"
BaseRepository
GenericRepository
UniversalCRUDRepository
```

unless a small technical abstraction genuinely reduces duplication without hiding business behavior.

---

# 9. Aggregate-Oriented Persistence

Repositories should normally operate around meaningful aggregates or entities.

For example:

```text id="t7a8g1"
OrderRepository
```

may load an Order with the data required for an Order use case.

It should not expose arbitrary table-level mutation to the Application Layer.

---

# 10. Business Scope

Every Business-owned query must apply Business isolation.

Conceptually:

```text id="0v9y5s"
WHERE business_id = current_business_id
```

The exact SQL is an implementation detail.

The important rule is:

> A repository must never accidentally return another Business's data.

---

# 11. Branch Scope

Branch-scoped data must include Branch isolation.

Conceptually:

```text id="n3h6s8"
Business
    +
Branch
    ↓
Scoped Query
```

A Branch ID alone is never sufficient.

The repository must ensure that the Branch belongs to the current Business.

---

# 12. Scope Validation

Repositories may enforce scope as a defensive persistence boundary.

However, repository filtering is not a replacement for authorization.

The normal flow remains:

```text id="xq2f8r"
Authentication
 ↓
Authorization
 ↓
Business Scope
 ↓
Branch Scope
 ↓
Repository
```

---

# 13. Cross-Business Access

A repository must reject or return no result when an entity belongs to another Business.

Example:

```text id="8n0r4v"
Business A
    Product X

Business B request
    Product X
```

The request must not obtain Product X.

Cross-Business access is a security failure.

---

# 14. Cross-Branch Access

A Branch-scoped employee must not access another Branch's operational data unless their permission scope allows it.

Example:

```text id="3qz6h7"
Employee:
    Branch A

Request:
    Branch B inventory
```

The repository/query layer must not bypass the validated scope.

---

# 15. Transaction Ownership

The Application Layer owns transactions.

Repositories should not unexpectedly commit.

Preferred:

```text id="1e9c3p"
Application Use Case
    ↓
begin transaction
    ↓
Repository operations
    ↓
Domain operations
    ↓
Audit / Outbox
    ↓
commit
```

Repositories participate in the transaction.

---

# 16. Repository Flush

A repository may use `flush` or equivalent persistence operations when the application requires generated state before commit.

Example:

```text id="f9r3t2"
Create Order
    ↓
Repository.add()
    ↓
flush
    ↓
generated persistence state
    ↓
continue workflow
    ↓
commit
```

A flush is not the same as a business transaction commit.

---

# 17. Transaction Boundaries

A repository must not independently decide that a transaction is complete.

For example:

```text id="k6v8pd"
AcceptOrderUseCase
    ├── OrderRepository
    ├── InventoryRepository
    ├── AuditRepository
    └── OutboxRepository
```

All required operations must participate in the same transaction when atomicity requires it.

---

# 18. Query Methods

Repository methods should express the required data operation.

Preferred:

```text id="w5p8qa"
get_order_for_branch(...)
get_active_cash_session(...)
get_product_for_business(...)
get_inventory_item_for_update(...)
```

Avoid excessive generic methods such as:

```text id="m2c5jr"
get_by_any_field(...)
find_everything(...)
update_anything(...)
```

Generic methods can weaken business boundaries.

---

# 19. `get` vs `get_for_update`

Normal reads:

```text id="tq4g3j"
get(...)
```

Concurrency-sensitive operations:

```text id="q6f9a2"
get_for_update(...)
```

may use a database row lock.

Examples include:

* inventory deduction;
* cash session state;
* payment state;
* configuration version;
* other financial state.

Locks must be used only where required.

---

# 20. Row Locking

PostgreSQL row locking may be used for critical mutable resources.

Example:

```text id="wq4g6b"
Inventory Row
     ↓
SELECT ... FOR UPDATE
     ↓
Validate quantity
     ↓
Deduct
     ↓
Commit
```

This prevents conflicting operations from simultaneously consuming the same protected state.

---

# 21. Lock Ordering

When a transaction requires multiple locks, the application must use a predictable lock order where practical.

Example:

```text id="j3x7m1"
Business-scoped configuration
        ↓
Branch configuration
        ↓
Inventory
        ↓
Financial state
```

The exact ordering depends on the operation.

The purpose is to reduce deadlock risk.

---

# 22. Optimistic Concurrency

Configuration-heavy records should normally use optimistic concurrency.

Example:

```text id="c4h8y2"
Current Version = 7

Request A:
    expected_version = 7
    → succeeds
    → version 8

Request B:
    expected_version = 7
    → conflict
```

The stale request must not silently overwrite version 8.

---

# 23. Version Checks

Repositories may enforce version predicates at update time.

Conceptually:

```text id="1qv5ka"
UPDATE configuration
SET version = 8
WHERE id = X
AND version = 7
```

If no row is updated, the operation is treated as a concurrency conflict.

---

# 24. Historical Records

Historical records must not be silently overwritten.

Examples:

* Order Item price;
* Payment;
* Refund;
* Cash Session close;
* Recipe Version;
* Set Version;
* Configuration Version;
* Report Version;
* Audit Event.

Repositories must expose explicit correction/versioning operations instead of generic mutation.

---

# 25. Soft Delete and Archive

Where historical integrity is required, ordinary delete should not be used.

Examples:

```text id="4n8z6c"
Product
Employee
Recipe
Configuration
```

may use:

```text
active
archived
deleted_at
status
```

according to the relevant domain model.

The Repository must follow the domain lifecycle rules.

---

# 26. Physical Delete

Physical deletion is allowed only when the data lifecycle rules explicitly permit it.

Examples may include:

* expired temporary records;
* technical data;
* records inside controlled Business deletion workflows.

Business deletion must follow the Data Lifecycle specification.

It must not be implemented as an uncontrolled cascade.

---

# 27. Business Deletion

When a Business reaches deletion:

```text id="v6x1pt"
READ_ONLY
    ↓
DELETION_ELIGIBLE
    ↓
DELETING
    ↓
DELETED
```

The deletion process must be controlled and auditable.

Repositories must not provide an unrestricted:

```text
delete_business_cascade()
```

that bypasses lifecycle rules.

---

# 28. Repository and Historical Integrity

Repositories must make it difficult to accidentally mutate historical data.

For example, instead of:

```text id="e5q3n2"
payment.amount = new_amount
save(payment)
```

a correction workflow should create the appropriate revision/correction structure.

The exact mechanism belongs to the relevant domain and database model.

---

# 29. Persistence Models

SQLAlchemy models represent persistence state.

They should not automatically become the Domain Model.

Conceptually:

```text id="m8k2y4"
Database Model
      ↕
Mapping
      ↕
Domain Entity
```

This separation prevents database implementation details from leaking into business logic.

---

# 30. ORM Usage

SQLAlchemy may be used for:

* mapping;
* queries;
* relationships;
* transaction participation;
* locking;
* persistence.

The ORM must not determine business behavior.

Business rules remain in the Domain Layer.

---

# 31. Lazy Loading

Lazy loading should be used carefully.

It must not create unexpected database queries during:

* serialization;
* domain calculations;
* loops;
* reporting;
* POS-critical operations.

Important use cases should explicitly load required data.

---

# 32. N+1 Prevention

Repositories must avoid N+1 query patterns.

Example problem:

```text id="0h5v0x"
Load 100 Orders
    ↓
Query Product for each Order
    ↓
100 additional queries
```

Preferred:

```text id="7y5j2e"
Load required Orders
    +
required related data
```

using appropriate joins, eager loading, or optimized query projections.

---

# 33. Read Projections

For heavy read operations, repositories may return optimized projections rather than full entities.

Examples:

```text id="w8j6pe"
DashboardRow
OrderListRow
InventorySummaryRow
CashReportRow
```

These are suitable for read-only workflows.

They must still enforce Business/Branch scope.

---

# 34. Write vs Read Persistence

The backend may use different persistence patterns for reads and writes while retaining PostgreSQL as the authoritative database.

Example:

```text id="b0p9y2"
Write:
Domain Entity
    ↓
Repository
    ↓
PostgreSQL

Read:
Query Repository
    ↓
Optimized SQL
    ↓
PostgreSQL
```

This does not require a separate database or microservice architecture.

---

# 35. Reporting Queries

Reports may use specialized query repositories.

Reporting queries must:

* respect Business scope;
* respect Branch scope;
* respect permissions;
* use historical snapshots;
* avoid mutating operational data.

Heavy reports should be executed asynchronously where required.

---

# 36. Audit Repository

Audit data requires special handling.

The Audit Repository should support:

* append;
* filtered query;
* historical retrieval;
* export support.

Normal update/delete operations on audit records must not be exposed.

---

# 37. Outbox Repository

The Outbox Repository should support:

* append event;
* retrieve pending events;
* mark processing;
* mark completed;
* retry;
* failure state.

Outbox state must support safe worker retries.

---

# 38. Idempotency Repository

Idempotency records should support:

* operation lookup;
* operation creation;
* result storage;
* status retrieval;
* conflict detection.

The uniqueness constraint should be enforced at the database level.

---

# 39. Synchronization Repository

Synchronization persistence may include:

```text id="4h0w3e"
SyncBatch
SyncOperation
SyncResult
Conflict
IdempotencyRecord
```

The repository must preserve:

* Business;
* Device;
* operation UUID;
* source;
* processing state;
* result.

---

# 40. Device Scope

Trusted device records are Business-scoped.

Repository operations must ensure that a device cannot be used against another Business.

A device UUID alone is not sufficient authorization.

---

# 41. Repository Security

Repositories must protect against:

* cross-Business reads;
* cross-Business writes;
* cross-Branch access;
* unscoped updates;
* accidental mass updates;
* accidental mass deletes.

Dangerous methods such as:

```text
update_all(...)
delete_all(...)
```

should not be exposed casually.

---

# 42. Mass Operations

Bulk operations may be used when explicitly designed.

They must include:

* Business scope;
* Branch scope where applicable;
* expected state/version;
* authorization at Application Layer;
* audit where required.

Bulk operations must not bypass important invariants.

---

# 43. Query Filters

Repository filters should be explicit.

Example:

```text id="7s9j3m"
OrderRepository.list(
    business_id=...,
    branch_id=...,
    status=...,
    date_range=...
)
```

Avoid hidden global state that silently determines Business scope.

The Application Layer should provide the validated context.

---

# 44. Pagination

Large list queries should support pagination.

The default approach should favor stable pagination.

Potential strategies:

* offset pagination for simple administrative screens;
* keyset/cursor pagination for large operational datasets.

The choice should be based on query size and UX requirements.

---

# 45. Sorting

Sorting must be deterministic.

If multiple records have the same primary sort value, a stable secondary field should be used.

Example:

```text id="4x4f3s"
ORDER BY created_at DESC, id DESC
```

This prevents inconsistent pagination.

---

# 46. Date and Time Queries

Business time should use explicit timezone handling.

Repositories must not rely on ambiguous server-local time.

Queries should use:

* UTC persistence where appropriate;
* Business/Branch timezone for user-facing date interpretation;
* explicit date boundaries.

The final database strategy is defined in the Database documents.

---

# 47. Money Persistence

Financial values must use exact numeric database types.

Do not store important monetary values as floating-point database types.

Repository mappings must preserve exactness between:

```text id="7q3m2v"
Domain Money
      ↕
Persistence Numeric
```

---

# 48. Quantity Persistence

Inventory quantities must use appropriate exact numeric precision.

The repository mapping must preserve the precision required by:

* recipes;
* inventory;
* purchase quantities;
* deductions;
* adjustments.

---

# 49. Transaction Isolation

PostgreSQL's default transaction isolation should be used unless a specific operation requires stronger behavior.

The Application Layer determines transaction scope.

Repositories may request row-level locks where required.

Higher isolation levels should be introduced only with a documented reason.

---

# 50. Deadlock Handling

Deadlocks are possible in concurrent operations.

The system should:

1. Detect the database deadlock.
2. Roll back the affected transaction.
3. Retry only when the operation is safe to retry.
4. Preserve idempotency.
5. Avoid indefinite retry loops.

Lock ordering should be designed to minimize deadlocks.

---

# 51. Connection Pooling

SQLAlchemy connection pooling should be used.

The pool must be configured according to deployment capacity.

The application must not create a new database connection for every repository call.

Connections must be returned correctly after transaction completion.

---

# 52. Session Management

A database session should normally correspond to the application transaction/unit of work.

The session must not be treated as a global application object.

Preferred:

```text id="o5w2d8"
Request / Job
    ↓
Unit of Work
    ↓
Database Session
    ↓
Use Case
    ↓
Commit / Rollback
    ↓
Session released
```

---

# 53. Unit of Work

A Unit of Work may coordinate:

* database session;
* repositories;
* transaction;
* commit;
* rollback.

Example:

```text id="9f1h5k"
with unit_of_work:
    use_case.execute(...)
```

The Unit of Work is an infrastructure/application mechanism, not a domain concept.

---

# 54. Repository Exceptions

Infrastructure exceptions should not leak directly into the API.

Example:

```text id="8j0g5a"
SQLAlchemy IntegrityError
        ↓
Repository / Unit of Work
        ↓
Application-level Conflict
        ↓
API response
```

The mapping must preserve useful business meaning.

---

# 55. Unique Constraints

The database should enforce important uniqueness rules.

Examples may include:

* Business-specific codes;
* operation UUID;
* configuration version;
* customer-facing order number within required scope;
* device identity;
* relevant employee identity;
* other domain-specific unique keys.

Application validation improves usability, but database constraints remain authoritative for concurrent writes.

---

# 56. Foreign Keys

Foreign keys should enforce valid persistence relationships where practical.

Examples:

```text id="1s6w8k"
Order → Business
Order → Branch
Order Item → Order
Payment → Order
Inventory Transaction → Product
Recipe Version → Product
```

Cross-Business references must be prevented by the overall data model.

---

# 57. Cross-Tenant Constraints

Where a simple foreign key cannot guarantee same-Business ownership, the system should use appropriate composite constraints or application/database mechanisms.

The goal is:

```text id="v9t6n4"
Business A
    Product A

Order A
    Product A
```

while preventing:

```text
Business A
    Order A

Business B
    Product B

Order A → Product B
```

---

# 58. Repository Testing

Repositories should be tested against real PostgreSQL behavior where correctness depends on database semantics.

Important tests include:

* Business isolation;
* Branch isolation;
* foreign keys;
* unique constraints;
* transaction rollback;
* row locking;
* optimistic concurrency;
* idempotency;
* pagination;
* indexes;
* deletion lifecycle.

SQLite-only tests must not be treated as sufficient for PostgreSQL-specific behavior.

---

# 59. Repository Test Layers

Recommended levels:

### Unit

Test pure mapping/helper logic.

### Integration

Test repository behavior against PostgreSQL.

### Application Integration

Test:

```text
Use Case
+
Repository
+
Transaction
```

### End-to-End

Test:

```text
API
+
Authentication
+
Application
+
Domain
+
Repository
+
PostgreSQL
```

---

# 60. Performance Testing

Important repository queries should be measured.

Focus areas:

* POS order loading;
* menu loading;
* inventory validation;
* inventory deduction;
* payment retrieval;
* Cash Session retrieval;
* dashboard queries;
* report queries;
* synchronization batches.

Slow queries should be investigated using PostgreSQL query plans.

---

# 61. Index Awareness

Repositories must be designed with database indexes in mind.

Common filtering dimensions include:

```text id="w5k9sx"
business_id
branch_id
employee_id
device_id
created_at
updated_at
status
operation_id
entity_id
cash_session_id
```

Indexes are defined in the Database documents.

The Repository Layer must not create ad-hoc indexes at runtime.

---

# 62. Query Result Size

Repository methods must avoid loading unbounded datasets into memory.

Examples:

Bad:

```text id="7k2p1n"
get_all_orders_for_business()
```

for a Business with a large history.

Preferred:

```text id="3f5r7a"
list_orders(
    business_id,
    date_range,
    pagination
)
```

---

# 63. Repository Caching

Repositories may use cache adapters for read-heavy operations.

However:

> Cache is never the authoritative source of business state.

Critical state must be validated from PostgreSQL.

Examples that should not rely exclusively on cache:

* inventory;
* payment;
* cash;
* permissions;
* subscription lifecycle;
* historical transactions.

---

# 64. Cache Invalidation

When cache is used, changes must invalidate or refresh affected entries.

Cache failure must degrade to database access where safe.

The system must not lose committed business state because a cache entry is missing.

---

# 65. Background Repository Usage

Background workers may use the same repository abstractions.

Each job must create its own transaction/session context.

A background worker must not reuse a request-scoped database session.

---

# 66. Offline Synchronization Persistence

Synchronization repositories must preserve operation order where dependencies exist.

Example:

```text id="6m2w9v"
Create Order
      ↓
Add Item
      ↓
Accept Order
      ↓
Payment
```

The repository must store sufficient information to reconstruct and validate the dependency chain.

---

# 67. Configuration Persistence

Configuration versions should be persisted immutably.

Preferred:

```text id="q9r7m3"
Configuration V1
Configuration V2
Configuration V3
```

rather than:

```text
single row repeatedly overwritten
```

Current effective configuration may be efficiently indexed/materialized, but historical versions must remain reconstructable.

---

# 68. Report Persistence

Reports use versioned persistence.

A Report Version should preserve:

* report identity;
* period;
* creation time;
* creator/system source;
* relevant data state;
* result reference;
* version identity.

Previous versions must remain immutable.

---

# 69. Data Access and Audit

Important persistence changes should be auditable through the Application Layer.

The Repository itself should not independently generate business audit events for every SQL statement.

Audit should represent business actions rather than low-level database activity.

---

# 70. Data Access and Notifications

Repositories must not send notifications.

Example:

Bad:

```text id="x3w7q1"
PaymentRepository.save()
    ↓
send_notification()
```

Preferred:

```text id="q7f5m8"
PaymentUseCase
    ↓
save Payment
    ↓
create Outbox Event
    ↓
Notification Worker
```

---

# 71. Data Access and File Storage

Repositories should not directly generate XLSX/PDF files.

Reporting/export workflows should use:

```text id="2m5p8c"
Application
 ↓
Report Query
 ↓
Report Generator
 ↓
File Storage
```

The database remains the source of report data.

---

# 72. Repository Guardrails

The following are prohibited:

1. Direct database access from API routes.
2. Direct database access from Domain entities.
3. Repository-owned hidden transactions.
4. Unexpected commits inside repository methods.
5. Unscoped Business queries.
6. Unscoped Branch queries.
7. Generic unrestricted update methods.
8. Generic unrestricted delete methods.
9. Silent mutation of historical records.
10. SQL queries embedded in Domain entities.
11. Business logic hidden inside SQL queries where it should remain explicit.
12. Notifications from repositories.
13. File generation from repositories.
14. External API calls from repositories.
15. Cache as authoritative state.
16. SQLite-only confidence for PostgreSQL-specific behavior.
17. Unbounded list queries.
18. N+1 query patterns in operational workflows.
19. Runtime schema/index modification.
20. Repository methods that bypass lifecycle restrictions.

---

# 73. Repository Invariants

1. Business-owned data is always Business-scoped.
2. Branch-owned data is always Branch-scoped where applicable.
3. Cross-Business access is prohibited.
4. Repository transactions participate in Application-owned transaction boundaries.
5. Historical records are not silently overwritten.
6. Important concurrency rules are enforced through version checks or locks.
7. Database uniqueness constraints protect important identities.
8. Foreign keys protect valid relationships where practical.
9. Repository methods do not perform unauthorized business operations.
10. Critical financial state uses exact numeric persistence.
11. Critical inventory state uses appropriate precision.
12. Large queries are bounded or paginated.
13. Query ordering is deterministic.
14. PostgreSQL remains authoritative.
15. Cache is never authoritative.
16. Background jobs use independent sessions.
17. Synchronization persistence preserves operation identity.
18. Configuration history remains reconstructable.
19. Report versions remain immutable.
20. Audit records are append-oriented.
21. Physical deletion follows lifecycle rules.
22. Business deletion cannot bypass controlled lifecycle.
23. Repository errors are translated before reaching API consumers.
24. Database constraints remain active protection against concurrent invalid writes.
25. Repository implementation remains replaceable without changing business rules.

---

# 74. Example Repository Flow

Example: inventory deduction.

```text id="0k8p3d"
AcceptOrderUseCase
        ↓
InventoryRepository.get_for_update()
        ↓
Inventory Domain Validation
        ↓
InventoryRepository.save()
        ↓
AuditRepository.add()
        ↓
OutboxRepository.add()
        ↓
Commit
```

All required operations participate in one transaction.

---

# 75. Example Configuration Flow

```text id="g6q2r1"
ChangePriceUseCase
        ↓
ConfigurationRepository.get_current_version()
        ↓
Validate expected version
        ↓
Domain creates new version
        ↓
ConfigurationRepository.add(new_version)
        ↓
AuditRepository.add()
        ↓
OutboxRepository.add()
        ↓
Commit
```

A stale expected version produces a conflict.

---

# 76. Example Query Flow

```text id="3h7m5a"
GetOrderListUseCase
        ↓
Authorization
        ↓
OrderQueryRepository.list(
    business_id,
    branch_id,
    date_range,
    pagination
)
        ↓
Projection
        ↓
Application Result
        ↓
API Response
```

The query does not modify operational state.

---

# 77. Repository and Domain Separation

The following distinction must remain clear:

```text
Domain:
    Order can be accepted.

Application:
    Execute AcceptOrder workflow.

Repository:
    Load and persist Order.

Database:
    Enforce persistence constraints.
```

No single layer should absorb all four responsibilities.

---

# 78. Repository and Application Separation

The Application Layer decides:

* which repository methods are needed;
* in what order;
* within which transaction;
* under which authorization context.

The Repository decides:

* how to execute the persistence operation;
* which SQL/ORM strategy to use;
* how to map persistence data.

---

# 79. Repository and Database Separation

The Repository Layer should not assume that all business correctness can be guaranteed by SQL.

Database constraints protect:

* identity;
* relationships;
* uniqueness;
* structural integrity;
* concurrency primitives.

Business workflows remain explicit in Application + Domain layers.

---

# 80. Migration Compatibility

Repository implementations must remain compatible with the database migration strategy.

Schema changes should follow:

```text id="4m6x2v"
Expand
   ↓
Deploy compatible code
   ↓
Migrate data if required
   ↓
Switch behavior
   ↓
Contract
```

Repositories should not assume destructive schema changes can happen atomically with application deployment.

---

# 81. Failure Recovery

If a repository operation fails:

```text id="k8s2v1"
Database Error
    ↓
Rollback
    ↓
Translate Error
    ↓
Retry if safe
    ↓
Return controlled result
```

The system must not continue using a broken transaction/session.

---

# 82. Repository Observability

Important repository operations should be observable through:

* request ID;
* operation ID;
* Business ID;
* Branch ID;
* query timing;
* transaction timing;
* error category.

Sensitive values must not be written directly into logs.

---

# 83. Performance Guardrails

For POS-critical repository operations:

1. Queries must be bounded.
2. Required indexes must exist.
3. N+1 patterns must be avoided.
4. Transactions must remain short.
5. Unnecessary joins must be avoided.
6. Large historical data must not be loaded unnecessarily.
7. Cache may be used for safe read-heavy data.
8. Reports must not block normal POS operations.
9. Background work should handle large exports.
10. Query plans should be reviewed for slow operations.

---

# 84. Recommended Repository Structure

```text id="5v8q1z"
app/infrastructure/repositories/
├── business/
├── identity/
├── subscription/
├── devices/
├── products/
├── recipes/
├── inventory/
├── menu/
├── orders/
├── tables/
├── payments/
├── cash/
├── handover/
├── attendance/
├── payroll/
├── notifications/
├── audit/
├── reports/
├── synchronization/
├── configuration/
└── lifecycle/
```

Query-specific implementations may be separated where useful.

---

# 85. Status

**Database:** PostgreSQL

**ORM:** SQLAlchemy

**Repository Pattern:** Required

**Transaction Owner:** Application / Unit of Work

**Business Isolation:** Required

**Branch Isolation:** Required

**Concurrency:** Optimistic + targeted row locking

**Historical Data:** Immutable/versioned where required

**Cache:** Non-authoritative

**Repository Layer:** Infrastructure-owned

**Next Document:** `06_Authentication_and_Authorization.md`

