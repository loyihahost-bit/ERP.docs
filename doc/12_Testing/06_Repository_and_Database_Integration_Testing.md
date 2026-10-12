# 06 — Repository and Database Integration Testing

**Document ID:** TEST-06
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`
**Depends On:** TEST-01, TEST-02, TEST-03, TEST-04, TEST-05
**Related:** TEST-07, TEST-08, TEST-09, TEST-10, TEST-11, TEST-12, TEST-13, TEST-14, `docs/05_Database`, `docs/11_Security`, `docs/10_Deployment`

---

# 1. Purpose

This document defines the testing architecture for repository implementations and database integration with PostgreSQL.

Repository and database integration tests verify that the application's persistence boundary correctly stores, retrieves, updates, and protects business data in the real database technology used by the system.

The primary question is:

> Does the persistence implementation correctly preserve the domain and application semantics when interacting with PostgreSQL?

These tests provide evidence that cannot be obtained from pure unit or domain tests alone.

---

# 2. Scope

This document covers:

* repository implementations;
* PostgreSQL integration;
* persistence mapping;
* entity persistence and retrieval;
* value persistence;
* relationships;
* foreign keys;
* unique constraints;
* check constraints;
* indexes where behaviorally relevant;
* transactions;
* rollback;
* commit;
* transaction isolation expectations;
* locking behavior where applicable;
* database-generated values;
* timestamps;
* soft/archive state;
* query correctness;
* filtering and ordering;
* pagination at the persistence boundary;
* bulk operations;
* database errors;
* constraint violations;
* connection failures;
* migration compatibility;
* test database lifecycle;
* database test data;
* persistence performance boundaries where relevant.

This document does not define:

* pure domain testing;
* application orchestration;
* API contract testing;
* frontend testing;
* complete end-to-end workflows;
* full concurrency testing;
* production database deployment.

Those responsibilities belong to other documents.

---

# 3. Repository Testing Role

A repository is the persistence boundary between application/domain behavior and the database.

Conceptually:

```text
Application
     │
     ▼
Repository Interface
     │
     ▼
Repository Implementation
     │
     ▼
PostgreSQL
```

Repository tests verify that the implementation correctly fulfills the repository contract.

The repository must not silently change the business meaning of data.

---

# 4. Why Real PostgreSQL Integration Tests Are Required

Mocking a repository does not prove that PostgreSQL actually behaves as expected.

A fake repository cannot reliably detect:

* incorrect SQL;
* incorrect joins;
* incorrect column mappings;
* missing constraints;
* incorrect transaction behavior;
* foreign-key violations;
* PostgreSQL-specific data behavior;
* incorrect indexes;
* isolation problems;
* migration incompatibilities;
* database-specific type handling.

Therefore, repository implementations must have tests against a real PostgreSQL environment.

---

# 5. Testing Layers

Repository and database testing should operate at several levels.

```text
Repository Contract Tests
        │
        ▼
Repository Integration Tests
        │
        ▼
PostgreSQL Schema Tests
        │
        ▼
Transaction Tests
        │
        ▼
Database Constraint Tests
        │
        ▼
Migration Compatibility Tests
```

Not every test must cover every layer.

The lowest reliable level should be selected according to the behavior being verified.

---

# 6. Repository Contract

Repository interfaces define persistence expectations.

A repository contract may include:

```text id="k4x8q2"
create
get_by_id
find
update
archive
restore
list
count
exists
```

The exact contract depends on the domain.

Repository tests should verify that the concrete PostgreSQL implementation satisfies the intended contract.

---

# 7. Repository Contract Test Matrix

For each important repository operation, tests should consider:

| Operation      | Required Tests                                  |
| -------------- | ----------------------------------------------- |
| Create         | Valid persistence, generated identity, defaults |
| Get            | Existing, missing, scoped resource              |
| Update         | Valid update, unchanged fields                  |
| Archive        | Active → archived                               |
| Restore        | Archived → active where supported               |
| List           | Filtering, ordering, pagination                 |
| Exists         | True/false conditions                           |
| Count          | Correct filtered count                          |
| Delete         | Only where deletion is explicitly permitted     |
| Bulk operation | Correct affected records and failure behavior   |

---

# 8. Persistence Mapping Testing

The database representation must preserve the application/domain representation.

Tests should verify:

```text id="m8p2s6"
Domain Value
    ↓
Persistence Mapping
    ↓
PostgreSQL Value
    ↓
Persistence Mapping
    ↓
Domain Value
```

Important mapping areas include:

* identifiers;
* monetary values;
* quantities;
* percentages;
* timestamps;
* dates;
* booleans;
* enums/statuses;
* nullable values;
* JSON/document fields where used;
* relationships;
* archived state;
* version information.

A value that changes meaning during persistence is a persistence defect.

---

# 9. Round-Trip Persistence Testing

For important entities:

```text id="v7n3q1"
Create
  ↓
Persist
  ↓
Read
  ↓
Compare
```

Tests should verify that meaningful domain state survives the round trip.

For example:

```text id="a6x2p8"
Recipe
→ save
→ reload
→ recipe remains semantically equivalent
```

The test should compare business-relevant values rather than database implementation details.

---

# 10. Identity Testing

Database identity behavior must be verified.

Tests should cover:

* generated internal IDs;
* externally supplied IDs where supported;
* uniqueness;
* stable identity after update;
* historical references;
* relationship references.

Customer-facing identifiers must not be confused with internal database identity.

For example, a three-digit cashier-facing session number may reset according to business rules while the underlying database identifier remains unique.

---

# 11. Nullability Testing

Database nullability must reflect domain requirements.

Tests should verify:

* required fields reject null;
* optional fields accept null;
* null is not silently converted into an invalid default;
* application mapping preserves intentional null values.

The database should enforce constraints that are part of persistence integrity.

---

# 12. Default Value Testing

Database defaults should be tested when the schema owns the default.

Examples may include:

* creation timestamp;
* update timestamp;
* active state;
* version;
* generated identifier.

Tests should verify:

```text id="r3k9w5"
Insert without default-owned value
        ↓
Database applies expected default
```

Application code should not be required to duplicate a database default unless architecture explicitly requires it.

---

# 13. Foreign-Key Testing

Foreign keys protect relationships between persistent resources.

Tests should verify:

* valid parent-child relationship;
* invalid parent reference;
* required parent existence;
* behavior when referenced records are archived;
* behavior when deletion is attempted;
* cascade behavior where explicitly defined;
* restriction behavior where explicitly defined.

Example:

```text id="f8q2n7"
Business
   │
   └── Branch
```

A branch cannot reference a nonexistent business.

---

# 14. Unique Constraint Testing

Unique constraints must be tested where uniqueness is a database responsibility.

Examples:

* unique business identifiers;
* unique product codes within required scope;
* unique employee identifiers where applicable;
* unique active relationship;
* unique external transaction identifier.

Tests should verify:

```text id="x6m4v1"
First valid record
    ↓
Accepted

Equivalent conflicting record
    ↓
Rejected
```

The application should correctly handle the database conflict.

---

# 15. Check Constraint Testing

Where PostgreSQL check constraints enforce data integrity, tests should verify both sides of the boundary.

Examples:

```text id="q5p7s2"
quantity >= 0
```

```text id="w8r3k6"
percentage within configured valid range
```

```text id="n4x9c1"
valid state value
```

The exact constraint must follow the approved database model.

---

# 16. Enum and Status Persistence

If domain statuses are persisted, tests should verify:

* valid status storage;
* valid status retrieval;
* invalid status rejection where enforced;
* migration behavior when statuses evolve;
* historical records remain interpretable.

Database representation must not make valid domain states impossible to retrieve.

---

# 17. Money Persistence

Financial values require special persistence testing.

Tests should verify:

* exact decimal behavior;
* no unintended floating-point conversion;
* correct precision;
* correct scale;
* negative-value handling according to domain rules;
* round-trip preservation;
* aggregation behavior.

Example:

```text id="b2m7q9"
Money
→ PostgreSQL
→ reload
→ exact business value preserved
```

Financial persistence must never silently introduce rounding that changes business meaning.

Detailed financial testing is covered by TEST-12.

---

# 18. Quantity Persistence

Inventory and recipe quantities must preserve their required precision.

Tests should verify:

* whole units;
* fractional units where supported;
* measurement precision;
* rounding behavior;
* zero;
* minimum valid value;
* maximum valid value;
* invalid negative values where prohibited.

Inventory-specific business testing is covered by TEST-13.

---

# 19. Timestamp and Date Testing

Persistence tests must verify:

* creation time;
* update time;
* business dates;
* timestamp precision;
* timezone handling;
* ordering by time;
* date-range boundaries.

Tests should avoid relying on uncontrolled system time.

Where the application owns time, it should use a controllable clock abstraction.

Where PostgreSQL owns timestamps, tests should verify the defined database behavior.

---

# 20. Soft Delete and Archive Testing

Where the architecture uses archival instead of deletion, repository tests must verify:

```text id="c7w2m8"
Active
  ↓
Archive
  ↓
Archived
```

Tests should verify:

* archive state is persisted;
* normal active queries exclude archived records where required;
* explicit historical queries can retrieve archived records;
* archived records remain identifiable;
* accidental hard deletion does not occur.

---

# 21. Repository Filtering

Repository filters must be tested against real PostgreSQL behavior.

Examples:

* business filter;
* branch filter;
* employee filter;
* active/archived filter;
* date range;
* status;
* product type;
* subscription state.

Tests should verify both:

```text id="j6p1v9"
matching records are returned
```

and:

```text id="m9x4r2"
non-matching records are excluded
```

---

# 22. Tenant and Branch Scoping

Repositories must preserve business and branch boundaries.

Tests should verify that:

```text id="z8c3k5"
Business A query
```

cannot accidentally return:

```text id="s2m7q4"
Business B data
```

Likewise, branch-scoped repositories must not silently return unrelated branch records.

Security architecture provides the broader policy.

Repository tests verify that persistence behavior supports that policy.

---

# 23. Ordering Testing

Ordering must be deterministic where the application depends on it.

Tests should verify:

* ascending order;
* descending order;
* date order;
* priority order;
* stable tie-breaking.

For example:

```text id="n7q4x8"
ORDER BY created_at, id
```

may be necessary where identical timestamps are possible.

The exact ordering strategy is defined by the repository contract.

---

# 24. Pagination Testing

Repository pagination should verify:

* first page;
* middle page;
* last page;
* empty page;
* page beyond available records;
* stable ordering;
* duplicate/missing records across pages.

Where cursor pagination is used, tests should also verify:

* valid cursor;
* expired/invalid cursor behavior where applicable;
* stable continuation;
* boundary records.

---

# 25. Query Result Completeness

Repository queries must return all fields required by the application contract.

Tests should detect:

* missing fields;
* incorrect mappings;
* incorrect joins;
* duplicate rows;
* unexpected null values;
* incorrect aggregation.

A query that returns technically valid SQL results but incomplete business data is still a repository defect.

---

# 26. Relationship Loading

Tests should verify relationship behavior where repositories expose related data.

Examples:

```text id="v4k8p2"
Order
 ├── Order Items
 └── Payment State
```

```text id="q9m3x7"
Recipe
 └── Recipe Components
```

Tests should verify:

* required relationships exist;
* missing relationships are handled correctly;
* no unrelated data is accidentally included;
* cardinality is preserved.

---

# 27. Transaction Testing

Transactions are a core database integration concern.

Tests must verify that operations requiring atomicity behave atomically.

Conceptually:

```text id="r6x2m8"
BEGIN
   │
   ├── Operation A
   ├── Operation B
   └── Operation C
        │
        ▼
     COMMIT
```

If a required operation fails:

```text id="p8q4v1"
BEGIN
   │
   ├── Operation A
   ├── Operation B
   └── Failure
        │
        ▼
     ROLLBACK
```

---

# 28. Commit Testing

Tests should verify that successful transaction completion makes all required changes visible after commit.

Example:

```text id="m3v7q9"
Transaction succeeds
       ↓
Commit
       ↓
New connection reads
       ↓
Expected state exists
```

This verifies that persistence is not merely visible inside the transaction.

---

# 29. Rollback Testing

Rollback tests are mandatory for critical multi-step operations.

Example:

```text id="x4k8s2"
Create order
   ↓
Create items
   ↓
Inventory operation fails
   ↓
ROLLBACK
```

After rollback, tests must verify that no invalid partial state remains.

For example:

* no incomplete order;
* no orphaned order items;
* no partial inventory movement;
* no false payment state.

---

# 30. Nested Transaction and Savepoint Behavior

Where nested transactional behavior or savepoints are used, tests should verify the defined semantics.

Tests should determine:

* what is rolled back;
* what remains committed;
* how errors propagate;
* whether the outer transaction can continue;
* whether the final state matches the transaction contract.

This behavior must not be assumed from the application framework.

---

# 31. Transaction Boundary Ownership

The architecture must define where transaction ownership lives.

Typical boundary:

```text id="j7m2x5"
Application Use Case
        │
        ▼
Transaction Boundary
        │
        ├── Repository A
        ├── Repository B
        └── Repository C
```

Tests should verify the approved transaction boundary.

Repositories should not independently commit partial operations when the use case requires a shared atomic transaction.

---

# 32. Transaction Failure Testing

Database integration tests should simulate failures such as:

* constraint violation;
* connection failure;
* statement failure;
* transaction rollback;
* deadlock where applicable;
* timeout where applicable.

The expected application behavior must be verified.

---

# 33. Database Isolation Testing

Where business correctness depends on transaction isolation, tests should verify the required behavior.

Potential concerns include:

* dirty reads;
* non-repeatable reads;
* phantom reads;
* lost updates;
* concurrent modification;
* visibility after commit.

The exact isolation requirement must come from the architecture.

Concurrency-specific scenarios are expanded in TEST-11.

---

# 34. Locking Tests

Where explicit row or advisory locking is part of the persistence architecture, tests should verify:

* lock acquisition;
* lock conflict;
* lock release;
* timeout behavior;
* transaction interaction;
* safe recovery after failure.

Tests must not assume that locking exists simply because an operation is expected to be safe.

The database behavior must provide evidence.

---

# 35. Constraint Enforcement vs Application Validation

Some rules should be enforced before database access.

Other integrity rules should also be protected by database constraints.

For example:

```text id="c9w5m2"
Application validation
        +
Database constraint
        =
Defense in depth
```

Tests should verify both where the architecture requires both.

A race condition can invalidate application-only validation.

Database constraints can provide the final persistence integrity boundary.

---

# 36. Database Error Mapping

Repository implementations must translate database-specific failures into appropriate application-facing persistence errors.

Examples:

```text id="n6q2x8"
Unique violation
Foreign-key violation
Check violation
Connection failure
Timeout
Serialization failure
Deadlock
```

Tests should verify that:

* the original database integrity is preserved;
* the application receives a meaningful error category;
* sensitive database details are not leaked;
* transaction state is correctly handled.

---

# 37. Connection Failure Testing

Repository tests should verify behavior when PostgreSQL becomes unavailable.

Examples:

```text id="f3k7p9"
Connection unavailable
        ↓
Repository operation fails
        ↓
Transaction is safely handled
        ↓
Application receives controlled failure
```

Tests should verify that an unavailable database does not produce false success.

---

# 38. Connection Pool Testing

Where a connection pool is used, integration testing should verify:

* connections are acquired;
* connections are released;
* failed transactions do not leak connections;
* transaction state is not accidentally reused;
* pool exhaustion produces controlled failure.

These tests should focus on correctness rather than reproducing production capacity testing.

Performance/load testing belongs to TEST-17.

---

# 39. Migration Testing

Every database schema change should be testable through the migration process.

Migration tests should verify:

* migration applies successfully;
* expected schema exists;
* required constraints exist;
* required indexes exist;
* existing data remains valid;
* application can operate against the resulting schema;
* rollback behavior where rollback is supported;
* migration ordering is correct.

---

# 40. Forward Migration Testing

A fresh environment should be able to reach the expected schema.

Example:

```text id="w2m8q4"
Empty PostgreSQL
    ↓
Migration 001
    ↓
Migration 002
    ↓
...
    ↓
Current Schema
```

The final schema must satisfy the database architecture.

---

# 41. Upgrade Migration Testing

Migration testing must also cover realistic existing data.

Example:

```text id="s7q3v9"
Previous Schema
      ↓
Existing Test Data
      ↓
New Migration
      ↓
New Schema
      ↓
Data Integrity Verification
```

Tests should verify that historical business data remains usable.

---

# 42. Migration Safety

Destructive changes require stronger testing.

Examples:

* column removal;
* type changes;
* constraint tightening;
* data transformation;
* index replacement;
* relationship changes.

Tests should verify that the migration cannot silently destroy required business data.

Deployment migration strategy is defined in the Deployment documentation.

---

# 43. Schema Constraint Tests

The database test suite should explicitly verify important structural constraints.

Examples:

```text id="e4q8m1"
Required FK exists
Required unique constraint exists
Required check constraint exists
Required index exists
Required nullable behavior exists
```

These tests protect against accidental schema regressions.

---

# 44. Index Testing

Indexes should be tested when they are part of an important correctness or performance expectation.

Tests may verify:

* required index exists;
* unique index behavior;
* composite uniqueness;
* expected query path where appropriate.

The test suite should not become tightly coupled to PostgreSQL query-plan details unless performance architecture explicitly requires it.

Detailed load testing is covered by TEST-17.

---

# 45. Bulk Operation Testing

Bulk operations require additional persistence tests.

Examples:

* bulk import;
* bulk status update;
* inventory import;
* employee import;
* price import.

Tests should verify:

* affected row count;
* validation behavior;
* transaction policy;
* partial failure policy;
* duplicate handling;
* rollback behavior where required.

A bulk operation must not silently report complete success when only part of the required operation succeeded.

---

# 46. Database Trigger Testing

If database triggers are used, they become part of the persistence behavior and must be tested.

Tests should verify:

* trigger executes when expected;
* trigger does not execute when not expected;
* resulting state is correct;
* failure behavior is correct;
* recursion or unintended side effects are controlled.

Triggers should not hide critical business behavior that belongs in the domain/application architecture.

---

# 47. Database Generated Data

Where PostgreSQL generates values, tests should verify:

* generated IDs;
* generated timestamps;
* generated values;
* default states;
* generated columns where used.

Application behavior must remain compatible with database-generated values.

---

# 48. JSON and Structured Database Fields

If JSON/JSONB or similar structured fields are used, tests should verify:

* valid serialization;
* valid deserialization;
* required fields;
* schema evolution;
* missing fields;
* unexpected fields;
* null handling;
* indexing behavior where required.

Structured data must not become an uncontrolled alternative to proper relational modeling.

---

# 49. Repository Security Boundary

Repository tests should support the security architecture by verifying:

* business scope;
* branch scope;
* resource ownership;
* restricted records;
* privileged records;
* archive state.

However, repository tests must not be considered the only authorization boundary.

Server-side authorization must remain enforced at the application/security boundary.

---

# 50. Audit Data Persistence

Where audit records are persisted, repository tests should verify:

* required identity;
* business context;
* branch context where applicable;
* action;
* target resource;
* timestamp;
* result/status;
* required metadata.

Audit integrity requirements are further defined by the Security documentation.

---

# 51. Historical Data Testing

Historical records are especially important for:

* orders;
* payments;
* refunds;
* cash sessions;
* inventory movements;
* recipe versions;
* prices;
* subscription history;
* audit events.

Repository tests should verify that historical records are not unintentionally overwritten by current configuration.

Example:

```text id="x7p4m2"
Product price changes today
        ↓
Historical order remains
        ↓
Original transaction price preserved
```

---

# 52. Test Database Environment

Repository integration tests should execute against a dedicated PostgreSQL test environment.

The test environment should:

* use a controlled schema;
* be isolated from development/production data;
* be reproducible;
* support migration execution;
* allow deterministic cleanup;
* use controlled credentials;
* avoid external production dependencies.

---

# 53. Database Test Isolation

Tests must not contaminate one another.

Possible strategies include:

* transaction rollback;
* isolated schema;
* isolated database;
* deterministic cleanup;
* disposable database instance.

The selected strategy must preserve test reliability.

For tests involving transaction behavior itself, the isolation mechanism must not hide the behavior being tested.

---

# 54. Test Data Lifecycle

Database test data should be:

1. created intentionally;
2. scoped to the test;
3. used only for the required scenario;
4. cleaned or discarded;
5. never copied from production without approved anonymization.

Large shared fixtures should be avoided unless they represent a stable domain baseline.

---

# 55. Database Test Data Examples

Useful test data may include:

```text id="q8m3v6"
Business A
Business B

Branch A1
Branch A2
Branch B1

Active Product
Archived Product

Approved Recipe
Archived Recipe

Open Cash Session
Closed Cash Session

Paid Order
Unpaid Order
Refunded Order

Available Stock
Insufficient Stock

Active Subscription
Expired Subscription
```

Data should be minimal and explicit.

---

# 56. Repository Integration Test Naming

Names should describe persistence behavior.

Prefer:

```text id="p4x8m1"
persists_and_reloads_recipe_without_losing_component_quantities
```

```text id="v7q2n5"
rejects_duplicate_product_code_within_required_scope
```

```text id="m3k9w6"
rolls_back_order_and_inventory_changes_when_transaction_fails
```

```text id="x8r4c2"
excludes_archived_products_from_active_product_query
```

```text id="a6q1z9"
preserves_historical_order_price_after_product_price_change
```

---

# 57. Repository Test Categories

A repository test suite should contain at least:

```text id="n5x8q3"
CRUD / persistence tests
Mapping tests
Constraint tests
Scope tests
Query tests
Transaction tests
Rollback tests
Failure tests
Migration tests
Historical-state tests
```

Additional categories should be added according to the repository's risk.

---

# 58. Database Integration Test Matrix

| Area          | Example Evidence                       |
| ------------- | -------------------------------------- |
| Persistence   | Entity survives save/reload            |
| Mapping       | Domain values survive round trip       |
| Relationships | FK and joins behave correctly          |
| Constraints   | Invalid state is rejected              |
| Transactions  | Required operations commit atomically  |
| Rollback      | Failed operation leaves safe state     |
| Scope         | Business/branch filtering is preserved |
| History       | Historical values remain stable        |
| Archive       | Archived state is respected            |
| Queries       | Filters/order/pagination are correct   |
| Migration     | Schema upgrades safely                 |
| Failure       | DB failures become controlled errors   |

---

# 59. Repository and Domain Test Boundary

The distinction must remain clear.

### Domain test

```text id="b8m4q1"
Stock cannot become negative.
```

### Repository test

```text id="j5x7p3"
Negative stock persistence is rejected by the persistence boundary
where the database schema requires that constraint.
```

### Application test

```text id="r2n9k6"
Inventory use case loads stock,
invokes domain behavior,
and persists the resulting state.
```

These tests provide different evidence.

---

# 60. Repository and Application Test Boundary

Application test:

```text id="q4v8m2"
Refund use case
→ load order
→ invoke refund
→ persist
→ produce required side effect
```

Repository test:

```text id="s6x1p9"
Refund repository
→ save
→ reload
→ verify persisted refund state
```

The repository test must not attempt to reproduce the entire application workflow.

---

# 61. Database and End-to-End Test Boundary

End-to-end tests prove that the complete system can reach the database through real application boundaries.

Repository integration tests provide much faster and more precise feedback about persistence behavior.

Therefore:

* repository defects should normally be diagnosed at repository level;
* complete workflow defects should be covered at E2E level;
* both levels remain necessary.

---

# 62. Failure-Oriented Database Testing

Critical repository tests should deliberately exercise:

* missing parent;
* duplicate unique value;
* invalid check value;
* invalid transaction state;
* rollback;
* connection interruption;
* transaction timeout;
* serialization failure where relevant;
* deadlock handling where relevant;
* invalid migration;
* incompatible schema.

The purpose is to verify safe failure, not merely successful SQL execution.

---

# 63. Performance-Aware Repository Testing

Repository tests should remain fast enough for regular CI.

They should not become full load tests.

However, tests should detect obvious persistence problems such as:

* accidental N+1 query behavior where architecture identifies it as a risk;
* unexpectedly huge result sets;
* missing required filtering;
* unbounded query behavior.

Detailed performance/load testing belongs to TEST-17.

---

# 64. Parallel Test Execution

Repository tests may run in parallel only when database isolation is preserved.

Parallel tests must not:

* modify the same uncontrolled records;
* share mutable transaction state;
* depend on execution order;
* corrupt shared schema state.

Migration tests may require controlled sequential execution.

---

# 65. Regression Testing

Every confirmed persistence defect should produce a regression test where practical.

Example:

```text id="c8m2v7"
Defect:
Repository query returned archived products in active menu results.

Regression:
Given an archived product,
When active products are queried,
Then the archived product is excluded.
```

Regression tests protect the persistence contract.

---

# 66. Repository Testing Anti-Patterns

## 66.1 Mocking PostgreSQL Completely

If the purpose is to verify PostgreSQL behavior, a mock database does not provide sufficient evidence.

---

## 66.2 Testing Only CRUD

Correct CRUD behavior does not prove transaction, constraint, scope, migration, or historical correctness.

---

## 66.3 Using Production Data

Production data must not be used directly as ordinary integration-test data.

---

## 66.4 Ignoring Rollback

A successful transaction test without failure/rollback testing is incomplete for critical multi-step operations.

---

## 66.5 Ignoring Constraints

Application validation alone does not prove database integrity.

---

## 66.6 Depending on Query Plans

Repository correctness tests should not become fragile because a PostgreSQL optimizer changes an internal query plan unless the plan itself is an explicit performance requirement.

---

# 67. Mandatory Repository and Database Testing Rules

The following rules are mandatory:

1. Repository implementations must be tested against real PostgreSQL.
2. Important persistence mappings must have round-trip tests.
3. Important foreign keys must be tested.
4. Important unique constraints must be tested.
5. Important check constraints must be tested.
6. Business and branch scope behavior must be tested at the persistence boundary where applicable.
7. Critical multi-step transactions must have commit and rollback tests.
8. Required transaction boundaries must be explicitly tested.
9. Database failure behavior must be tested for critical operations.
10. Migration paths must be tested.
11. Historical business data must have persistence regression protection.
12. Archive behavior must be tested where archival is part of the architecture.
13. Monetary values must preserve required precision.
14. Inventory and recipe quantities must preserve required precision.
15. Tests must not depend on production data.
16. Database test environments must be isolated.
17. Repository tests must remain deterministic.
18. Repository tests must not replace domain or application tests.
19. Critical persistence defects should produce regression tests.
20. Database constraints must not be treated as optional documentation; when defined as integrity requirements, their enforcement must be tested.

---

# 68. Repository and Database Testing Invariants

The testing architecture must preserve these invariants:

```text id="u4m8q2"
Persisted domain state can be retrieved without unintended semantic changes.
```

```text id="x7p3n9"
Required database constraints reject invalid persistent state.
```

```text id="r5k1v8"
Critical transactions do not leave invalid partial state.
```

```text id="m9q4c6"
Rollback removes all changes that belong to the failed atomic operation.
```

```text id="j2w8s5"
Business and branch scope is preserved at the persistence boundary.
```

```text id="a6x3p7"
Historical business meaning is not silently overwritten by current configuration.
```

```text id="n8v5k2"
Database failures cannot be reported as successful business operations.
```

```text id="q1r7m4"
Schema migrations preserve required business data and integrity.
```

```text id="z6c9w3"
Repository integration tests provide evidence from the real PostgreSQL behavior.
```

```text id="f8p2x5"
Repository tests do not become substitutes for domain or application tests.
```

---

# 69. Acceptance Criteria

This document is considered correctly implemented when:

* repository contracts have clear integration-testing expectations;
* repository implementations are tested against PostgreSQL;
* persistence mappings have round-trip coverage;
* relationships and constraints are tested;
* business and branch scope is protected;
* transaction commit behavior is tested;
* rollback behavior is tested;
* critical database failures are tested;
* migration paths are tested;
* historical and archived data behavior is tested;
* financial and quantity precision is protected;
* test databases are isolated and reproducible;
* repository tests remain distinct from domain and application tests;
* persistence defects can be converted into regression tests.

---

# 70. Relationship to the Testing Architecture

```text id="k8q3m7"
TEST-01
Testing Architecture Overview
        │
        ▼
TEST-02
Testing Strategy and Test Pyramid
        │
        ▼
TEST-03
Unit Testing Architecture
        │
        ▼
TEST-04
Domain Testing Architecture
        │
        ▼
TEST-05
Application and Use-Case Testing
        │
        ▼
TEST-06
Repository and Database Integration Testing
        │
        ├── TEST-07 API Contract / Schema
        ├── TEST-08 Integration Testing
        ├── TEST-09 End-to-End / POS
        ├── TEST-10 Offline / Synchronization
        ├── TEST-11 Concurrency / Consistency
        ├── TEST-12 Financial / Cash
        ├── TEST-13 Inventory / Recipe
        └── TEST-14 Authentication / Authorization
```

The responsibility boundary is:

```text id="p6v2x8"
TEST-04
Business rules are correct
        ↓
TEST-05
Use cases orchestrate them correctly
        ↓
TEST-06
Persistence preserves them correctly
        ↓
TEST-08
Real subsystem boundaries work together
        ↓
TEST-09
Critical user workflows work end-to-end
```

---

# 71. Final Rule

Repository and database integration testing must prove that the persistence layer does not change, corrupt, weaken, or silently reinterpret the business state defined by the domain and application layers.

A sufficiently tested persistence boundary provides evidence that:

```text id="s9m4q1"
Business state is persisted correctly.
Business state can be reconstructed correctly.
Required relationships are preserved.
Database constraints reject invalid persistent state.
Transactions commit complete atomic operations.
Failures roll back required state safely.
Business and branch scope remains correct.
Historical state remains meaningful.
Schema changes preserve required data.
PostgreSQL-specific behavior is verified where relevant.
```

The domain layer defines what the business state means.

The application layer defines how a use case coordinates that state.

The repository and database layer must prove that **the state survives persistence without losing its business meaning or integrity**.

