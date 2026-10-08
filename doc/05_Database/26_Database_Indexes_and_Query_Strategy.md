# Database Indexes and Query Strategy

**Document ID:** DB-26
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

---

## 1. Purpose

This document defines the indexing strategy, query patterns, filtering rules, pagination strategy and database performance principles for FastFood ERP.

The primary goal is to ensure that the system remains fast for daily POS operations while supporting:

* multi-tenant data isolation;
* multi-branch operations;
* inventory transactions;
* orders;
* payments;
* cash sessions;
* synchronization;
* reports;
* audit history;
* notifications;
* payroll;
* lifecycle/deletion jobs.

The database must remain efficient without introducing unnecessary indexes or excessive write overhead.

---

# 2. Scope

This document covers:

* PostgreSQL indexing;
* primary-key indexes;
* unique indexes;
* foreign-key indexes;
* Business-scoped indexes;
* Branch-scoped indexes;
* composite indexes;
* partial indexes;
* covering indexes;
* expression indexes;
* full-text/search indexes where required;
* temporal indexes;
* operational query patterns;
* POS query strategy;
* inventory query strategy;
* order query strategy;
* payment query strategy;
* cash session query strategy;
* reporting query strategy;
* audit query strategy;
* notification query strategy;
* synchronization query strategy;
* lifecycle/deletion query strategy;
* pagination;
* sorting;
* query limits;
* query plans;
* EXPLAIN/ANALYZE;
* index maintenance;
* index migration;
* index testing;
* performance guardrails.

---

# 3. Core Query Principle

Indexes must be designed around actual query patterns.

The system must not create indexes simply because a column exists.

A useful index must support one or more important operations such as:

```text
WHERE
JOIN
ORDER BY
UNIQUE
GROUPING
range filtering
```

The priority is:

```text
Critical POS queries
        ↓
High-frequency operational queries
        ↓
Synchronization queries
        ↓
Common management queries
        ↓
Reporting queries
        ↓
Rare administrative queries
```

---

# 4. Database Authority

PostgreSQL is the authoritative database.

Application code must issue predictable, parameterized queries.

Query performance must be measured against PostgreSQL execution plans.

The application must not assume that an index is being used merely because one exists.

---

# 5. Tenant-First Query Strategy

FastFood ERP is multi-tenant.

Business scope is therefore one of the most important query dimensions.

Business-owned operational queries should normally include:

```text
business_uuid
```

when the table stores Business-owned data directly.

Typical pattern:

```sql
SELECT ...
FROM order
WHERE business_uuid = :business_uuid
  AND ...
```

---

# 6. Branch-First Operational Queries

Branch-heavy operational tables should normally support:

```text
business_uuid
branch_uuid
```

where both dimensions are part of the query.

Typical pattern:

```sql
SELECT ...
FROM order
WHERE business_uuid = :business_uuid
  AND branch_uuid = :branch_uuid
  AND ...
```

---

# 7. Why Composite Tenant Indexes Matter

An index only on:

```text
branch_uuid
```

may be sufficient for some queries.

However, when the application consistently validates both:

```text
business_uuid
branch_uuid
```

a composite index may provide better filtering and stronger alignment with query patterns.

The exact index must be validated using query plans.

---

# 8. Tenant Isolation Is Not an Index

Indexes improve performance.

They do not provide authorization.

The following are separate responsibilities:

```text
Tenant isolation
Authorization
Query filtering
Indexing
```

An index must never be considered a security boundary.

---

# 9. Primary Key Indexes

Every primary key automatically requires an efficient lookup path.

Typical:

```text
WHERE uuid = :uuid
```

must be fast.

Primary-key indexes must not be duplicated unnecessarily with another identical single-column index.

---

# 10. UUID Lookup Strategy

UUID primary keys are the primary identity lookup mechanism.

Typical queries:

```text
Get Product by UUID
Get Order by UUID
Get Payment by UUID
Get Cash Session by UUID
```

must use the primary key.

---

# 11. Foreign Key Indexes

Foreign-key columns should generally have supporting indexes when they are:

* frequently queried;
* frequently joined;
* used in deletion checks;
* used for Business/Branch filtering;
* used in reports;
* used by background jobs.

---

# 12. Foreign Key Indexing Rule

Every FK does not automatically require its own standalone index.

For example:

```text
business_uuid
branch_uuid
```

may already be covered by a composite index appropriate to the dominant query pattern.

Duplicate indexes should be avoided.

---

# 13. Composite Index Rule

Composite indexes should follow the most selective and commonly filtered query dimensions.

Typical operational ordering:

```text
business_uuid
branch_uuid
status
created_at
```

may be appropriate for a Branch-scoped status query.

The correct order must be determined from actual query patterns.

---

# 14. Leftmost Prefix Principle

For a composite index:

```text
(business_uuid, branch_uuid, status, created_at)
```

queries filtering by:

```text
business_uuid
```

or:

```text
business_uuid + branch_uuid
```

can generally benefit from the index.

A query filtering only by:

```text
status
```

should not automatically be expected to use this index efficiently.

---

# 15. Equality Before Range

A common index design pattern is:

```text
Equality columns
        ↓
Range column
        ↓
Ordering column
```

Example:

```text
business_uuid
branch_uuid
created_at
```

for:

```sql
WHERE business_uuid = ...
  AND branch_uuid = ...
  AND created_at >= ...
  AND created_at < ...
```

---

# 16. Equality Before Ordering

For queries such as:

```sql
WHERE business_uuid = :business
  AND branch_uuid = :branch
ORDER BY created_at DESC
LIMIT 50
```

an index such as:

```text
(business_uuid, branch_uuid, created_at DESC)
```

may be appropriate.

---

# 17. Index Direction

PostgreSQL can often scan B-tree indexes in either direction.

Therefore explicit `ASC`/`DESC` should be used when it materially improves a common multi-column ordering strategy.

Do not create both ascending and descending indexes without evidence.

---

# 18. POS Query Priority

POS queries have the highest performance priority.

Critical queries include:

* load Branch menu;
* load active Products;
* load Product configuration;
* create Order;
* load open Order;
* load Table status;
* validate stock;
* load active Cash Session;
* record Payment;
* load current employee permissions;
* load trusted Device context.

---

# 19. POS Query Principle

POS queries should avoid:

* large historical scans;
* unnecessary joins;
* expensive aggregations;
* loading unrelated Business data;
* loading full audit history;
* recalculating historical reports.

---

# 20. Menu Query Strategy

A typical Branch menu query may require:

```text
Business
Branch
Product
Category
Branch availability
effective configuration
```

The query should use indexed Business/Branch relationships.

---

# 21. Active Product Query

A common query is:

```sql
SELECT ...
FROM product
WHERE business_uuid = :business_uuid
  AND active = TRUE;
```

If this query is frequent and inactive Products are numerous, a partial index may be useful.

Conceptually:

```sql
CREATE INDEX ...
ON product (business_uuid)
WHERE active = TRUE;
```

---

# 22. Branch Menu Availability

Branch-specific availability should support efficient lookup by:

```text
business_uuid
branch_uuid
product_uuid
```

A likely composite uniqueness/index pattern is:

```text
UNIQUE(branch_uuid, product_uuid)
```

where Product Business consistency is separately enforced.

---

# 23. Menu Ordering

If Products are displayed in category/order sequence, the index should support the actual query.

Example pattern:

```text
branch_uuid
category_uuid
display_order
```

may be appropriate.

Do not index display order independently if it is always queried within Branch/category scope.

---

# 24. Product Search

Product search may use:

* exact code;
* barcode;
* normalized name;
* prefix search;
* full-text search.

The simplest exact identifier lookup should use B-tree indexes.

---

# 25. Product Code

If Product code is Business-scoped:

```text
UNIQUE(business_uuid, product_code)
```

already provides an index suitable for exact lookup.

An additional identical index is unnecessary.

---

# 26. Product Barcode

If barcode must be unique within Business:

```text
UNIQUE(business_uuid, barcode)
```

may provide the required lookup.

If barcode may be nullable, a PostgreSQL unique constraint naturally permits multiple NULL values unless `NULLS NOT DISTINCT` or another explicit rule is used.

---

# 27. Product Name Search

Simple B-tree indexes are not automatically optimal for arbitrary:

```text
ILIKE '%burger%'
```

queries.

For large datasets, appropriate PostgreSQL text-search/indexing strategies may be considered.

---

# 28. Category Query

Categories are usually small datasets.

The primary index and Business-scoped uniqueness may be sufficient.

Avoid over-indexing category tables.

---

# 29. Recipe Query Strategy

Common recipe queries include:

* Product → current Recipe;
* Recipe → active Version;
* Version → Components;
* Component → affected Products.

Indexes should support these relationships.

---

# 30. Recipe Version Lookup

Recommended query pattern:

```text
recipe_uuid
status
version_number
```

If only one effective version exists, a partial unique index may enforce that state.

---

# 31. Recipe Component Lookup

A Recipe Version's components should be efficiently loaded using:

```text
recipe_version_uuid
```

Typical:

```sql
SELECT ...
FROM recipe_component
WHERE recipe_version_uuid = :version_uuid;
```

---

# 32. Recipe Reverse Lookup

When a raw Product changes or becomes unavailable, the system may need to identify Recipes using it.

Support:

```text
component_product_uuid
```

with an index.

---

# 33. Set Query Strategy

Common Set queries:

* Branch → available Sets;
* Set → current Version;
* Set Version → components;
* Product → Sets containing Product.

Indexes should support both forward and reverse relationships.

---

# 34. Inventory Query Priority

Inventory is a high-frequency operational domain.

Critical queries include:

* current stock by Product;
* current stock by Warehouse;
* low stock;
* stock validation;
* stock movement creation;
* inventory history;
* discrepancy lookup.

---

# 35. Inventory Balance Lookup

The most important inventory query is typically:

```text
Warehouse + Product
```

A suitable unique/index strategy may be:

```text
UNIQUE(warehouse_uuid, product_uuid)
```

This both protects uniqueness and provides efficient lookup.

---

# 36. Inventory Business Scope

If Warehouse belongs to a Branch and Branch belongs to Business, direct Business filtering may be unnecessary for some queries.

However, if `business_uuid` is stored directly on Inventory Balance, a composite index may improve tenant-scoped access.

The chosen model must remain consistent.

---

# 37. Inventory Movement Query

Typical history query:

```sql
SELECT ...
FROM inventory_transaction
WHERE business_uuid = :business_uuid
  AND branch_uuid = :branch_uuid
  AND product_uuid = :product_uuid
ORDER BY created_at DESC
LIMIT 100;
```

A suitable composite index may be:

```text
(business_uuid, branch_uuid, product_uuid, created_at DESC)
```

---

# 38. Inventory Date Range

Inventory reports commonly use date ranges.

Indexes should support:

```text
business
branch
product
timestamp range
```

when this is a frequent access pattern.

---

# 39. Inventory Low Stock

Low-stock queries may require current balances rather than historical transactions.

The system should not scan all inventory transactions to determine current stock.

Current stock must be available from the authoritative inventory balance model.

---

# 40. Inventory Transaction Append Pattern

Inventory transactions are primarily append-oriented.

Indexes should therefore focus on:

* lookup;
* history;
* reporting;
* synchronization.

Avoid unnecessary indexes that provide little read value but increase every insert cost.

---

# 41. Inventory Concurrency

Indexes do not replace row locks.

For:

```text
current stock = 1
sale quantity = 1
```

concurrent sales must be serialized through transaction-level locking or atomic update logic.

---

# 42. Order Query Priority

Important Order queries include:

* open Orders;
* Orders by Table;
* Orders by Cash Session;
* Orders by display number;
* Orders by Branch;
* Orders by date;
* Orders by status;
* Order history.

---

# 43. Open Order Query

A common query:

```sql
SELECT ...
FROM orders
WHERE business_uuid = :business_uuid
  AND branch_uuid = :branch_uuid
  AND status IN (...)
ORDER BY created_at DESC;
```

A composite index should support the actual status set and ordering pattern.

---

# 44. Open Table Order

For determining whether a Table is occupied:

```text
branch_uuid
table_uuid
active/open status
```

should be efficiently queryable.

A partial index may be appropriate if only active Orders matter.

Conceptually:

```sql
CREATE INDEX ...
ON orders (branch_uuid, table_uuid)
WHERE status IN ('DRAFT', 'ACCEPTED', 'PREPARING', 'READY');
```

The exact lifecycle states must match the final model.

---

# 45. Table Occupancy

The POS must not scan historical Orders to determine whether a Table is currently occupied.

The query must target only relevant active Orders.

---

# 46. Cash Session Order Lookup

Orders by Cash Session are important for:

* session reports;
* customer-facing numbering;
* cashier reports;
* reconciliation.

Index:

```text
cash_session_uuid
```

and where needed:

```text
cash_session_uuid + created_at
```

---

# 47. Display Order Number

Customer-facing order numbers are scoped to Cash Session.

The uniqueness constraint should provide the exact lookup:

```text
(cash_session_uuid, display_order_number)
```

---

# 48. Order Date Queries

Order reports commonly use:

```text
business_uuid
branch_uuid
created_at
```

rather than scanning the complete Order table.

---

# 49. Order Status Index

A standalone `status` index is often low-selectivity.

It should not automatically be created.

Status should usually be combined with Business/Branch or use a partial index for highly selective active-state queries.

---

# 50. Order History Pagination

Order history should use deterministic pagination.

Preferred strategy:

```text
created_at
uuid
```

as a stable ordering pair.

---

# 51. Keyset Pagination

For large operational history, keyset pagination should be preferred over deep OFFSET pagination.

Example:

```sql
WHERE
    (created_at, uuid) < (:last_created_at, :last_uuid)
ORDER BY created_at DESC, uuid DESC
LIMIT 50;
```

---

# 52. Why Keyset Pagination

Deep OFFSET queries can become increasingly expensive:

```text
OFFSET 100000
```

requires PostgreSQL to process many preceding rows.

Keyset pagination allows the query to continue from the last known position.

---

# 53. Stable Pagination

Ordering must be deterministic.

Using only:

```text
created_at
```

may produce unstable pagination when timestamps are equal.

A unique tie-breaker such as UUID should be included.

---

# 54. Payment Query Strategy

Important payment queries include:

* payments by Order;
* payments by Cash Session;
* payments by Branch;
* payments by Employee;
* payment history;
* refunds;
* debt payments.

---

# 55. Payment by Order

An index on:

```text
order_uuid
```

is generally required.

If tenant validation is frequent:

```text
business_uuid
order_uuid
```

may be appropriate depending on the data model.

---

# 56. Payment by Cash Session

Payment reports commonly query:

```text
cash_session_uuid
created_at
```

A composite index may support session reconciliation.

---

# 57. Payment by Method

Payment method alone is usually low-selectivity.

Avoid a standalone index unless measured workload demonstrates value.

---

# 58. Refund Query Strategy

Refund history may be queried by:

* original Payment;
* Order;
* Branch;
* Employee;
* date.

Indexes should support these actual paths.

---

# 59. Debt Query Strategy

Debt operations commonly query:

```text
business_uuid
debt_customer_uuid
status
created_at
```

or:

```text
business_uuid
phone
```

where customer search is required.

---

# 60. Debt Phone Search

If phone lookup is common, a normalized phone field should be indexed.

The database should store a canonical normalized form separately from display formatting if required.

---

# 61. Cash Register Query Strategy

Cash Register queries are usually low-volume.

Primary keys and Branch FK indexes may be sufficient.

Avoid unnecessary indexes on small tables.

---

# 62. Active Cash Session Index

The most important Cash Session query is usually:

```text
Find active session for Register
```

A partial unique index is ideal:

```sql
CREATE UNIQUE INDEX ...
ON cash_session (cash_register_uuid)
WHERE status = 'OPEN';
```

This simultaneously:

* enforces integrity;
* provides lookup performance.

---

# 63. Cash Session History

For historical sessions:

```text
branch_uuid
created_at DESC
```

or:

```text
cash_register_uuid
created_at DESC
```

may be appropriate.

---

# 64. Handover Query Strategy

Handover queries may require:

* previous session;
* new session;
* previous Employee;
* next Employee;
* Branch;
* date.

Indexes should follow the primary navigation path rather than every possible column combination.

---

# 65. Employee Query Strategy

Employee queries commonly include:

* Business;
* Branch assignment;
* active status;
* login identity;
* role;
* permission scope.

---

# 66. Employee Active Query

A partial index may be useful for:

```text
business_uuid
```

where:

```text
status = 'ACTIVE'
```

is frequently queried.

---

# 67. Employee Branch Assignment

The association table should support:

```text
employee_uuid
branch_uuid
```

both directions.

This may require:

```text
UNIQUE(employee_uuid, branch_uuid)
```

plus an index beginning with `branch_uuid` if Branch → Employees is frequent.

---

# 68. Permission Query Strategy

Permission resolution is performance-sensitive because it may occur frequently.

The database should support efficient retrieval of:

* Employee roles;
* Role permissions;
* Employee overrides;
* Branch scope;
* Business scope.

---

# 69. Permission Caching

Permission results may be cached at the application layer.

The cache must not become the authoritative source.

Permission changes must invalidate or version the relevant cache.

---

# 70. Device Query Strategy

Trusted Device lookup commonly uses:

```text
device_uuid
```

and potentially:

```text
business_uuid + device_identifier
```

Device authentication paths must remain fast.

---

# 71. Device Revocation Query

If revocation is checked frequently, an appropriate index may support:

```text
business_uuid
status
```

or:

```text
device_uuid
status
```

depending on the authentication flow.

---

# 72. Subscription Query Strategy

Subscription checks are relatively frequent.

The database should efficiently retrieve the current subscription/entitlement state for a Business.

If only one current active subscription is allowed, a partial unique index may enforce that model.

---

# 73. Configuration Query Strategy

Configuration lookup is performance-sensitive for POS.

Typical query:

```text
business_uuid
branch_uuid
entity_type
entity_uuid
status
effective_at
```

The final index must reflect the actual configuration schema.

---

# 74. Effective Configuration

The POS should not scan all historical configurations.

The current effective configuration must be directly identifiable.

Possible strategies include:

* active-state partial indexes;
* current version pointer;
* effective timestamp index;
* materialized effective configuration.

---

# 75. Configuration History

Historical configuration queries can use:

```text
business_uuid
entity_uuid
created_at DESC
```

or:

```text
configuration_uuid
version_number DESC
```

depending on access pattern.

---

# 76. Audit Query Strategy

Audit tables can become very large.

Common filters:

* Business;
* Branch;
* Employee;
* event type;
* entity;
* transaction;
* Device;
* Cash Session;
* date range.

Indexes must prioritize the most common administrative query paths.

---

# 77. Audit Business + Date

A common audit query is:

```sql
WHERE business_uuid = :business
  AND created_at >= :start
  AND created_at < :end
ORDER BY created_at DESC;
```

A composite index:

```text
(business_uuid, created_at DESC)
```

is likely appropriate.

---

# 78. Audit Entity Lookup

For reconstructing an entity's history:

```text
entity_type
entity_uuid
created_at
```

may be indexed.

---

# 79. Audit Actor Lookup

For employee activity reports:

```text
business_uuid
employee_uuid
created_at
```

may be appropriate.

---

# 80. Audit Event Type

Event type alone may have low selectivity.

It should generally be combined with Business or date when frequently queried.

---

# 81. Audit Partitioning

Audit partitioning may be considered when data volume becomes sufficiently large.

Initial architecture should not introduce partitioning solely for theoretical scalability.

Partitioning must be justified by measured data volume and query behavior.

---

# 82. Report Query Strategy

Reports can generate expensive queries.

Report generation must not block normal POS operations.

Heavy queries should execute in background workers.

---

# 83. Report Date Range

Report queries must always have explicit date boundaries.

Avoid unbounded:

```sql
SELECT ...
FROM orders;
```

for production report generation.

---

# 84. Report Business Scope

Every report query must apply Business scope.

Branch reports must additionally apply Branch scope.

---

# 85. Report Aggregation

Indexes can reduce input rows but cannot eliminate expensive aggregation in all cases.

For large reports, consider:

* report snapshots;
* precomputed aggregates;
* background jobs;
* materialized views where justified.

---

# 86. Report Snapshot Strategy

Historical reports use immutable Report Versions.

Once generated, the system should not repeatedly recalculate the same historical report for ordinary viewing.

---

# 87. Report Generation Isolation

Report generation must run independently from interactive POS transactions.

A large report query must not hold locks on operational rows unnecessarily.

---

# 88. Notification Query Strategy

Common queries include:

```text
employee_uuid
unread
created_at
```

A partial index may be useful for unread notifications.

Conceptually:

```sql
CREATE INDEX ...
ON notification_recipient (employee_uuid, created_at DESC)
WHERE read_at IS NULL;
```

---

# 89. Notification History

Historical read notifications do not normally require the same priority as unread notifications.

Therefore a partial index can reduce index size and write overhead.

---

# 90. Synchronization Query Strategy

Synchronization queries are usually driven by:

* Device;
* Business;
* operation UUID;
* status;
* created time;
* retry state.

---

# 91. Sync Operation UUID

The idempotency lookup must be extremely fast.

A UNIQUE index on:

```text
operation_uuid
```

or the correct scoped combination should be used.

---

# 92. Sync Pending Queue

Pending synchronization jobs may use:

```text
business_uuid
device_uuid
status
created_at
```

A partial index can target pending states.

---

# 93. Sync Worker Query

Workers should fetch bounded batches.

Conceptually:

```sql
SELECT ...
FROM sync_operation
WHERE status IN (...)
ORDER BY created_at
LIMIT 100;
```

The exact query must use locking appropriate to the worker concurrency model.

---

# 94. FOR UPDATE SKIP LOCKED

For independent background workers processing queue-like records, PostgreSQL:

```sql
FOR UPDATE SKIP LOCKED
```

may be used.

This must be applied only where queue semantics are appropriate.

---

# 95. Sync Batch Size

Initial synchronization batches should remain bounded.

A practical starting range is approximately:

```text
50–100 operations
```

and must be tunable based on performance measurements.

---

# 96. Lifecycle Query Strategy

Lifecycle jobs commonly query:

```text
Business status
eligibility timestamp
deletion state
```

The lifecycle model should support efficient selection of eligible Businesses.

---

# 97. Deletion Eligibility Index

A suitable index may include:

```text
lifecycle_state
deletion_eligible_at
```

For example:

```text
(status, deletion_eligible_at)
```

or a partial index targeting eligible states.

---

# 98. Deletion Batch Query

Deletion workers must select a bounded set of eligible Businesses.

They must not scan the complete Business table on every iteration.

---

# 99. Background Job Index Strategy

Background jobs should generally use:

```text
status
next_run_at
created_at
```

where appropriate.

Partial indexes can target runnable jobs.

---

# 100. Job Retry Query

A retry worker may query:

```text
status = RETRYING
next_run_at <= now()
```

A partial composite index may support this pattern.

---

# 101. Date Range Strategy

Date filtering must use half-open ranges:

```text
>= start
< end
```

rather than:

```text
BETWEEN start AND end
```

when timestamps are involved.

This avoids boundary ambiguity.

---

# 102. Timestamp Indexing

Timestamp indexes are useful when combined with a selective Business/Branch/entity dimension.

A standalone timestamp index should only be created when global time-range queries are genuinely common.

---

# 103. Timezone Handling

All authoritative timestamps should use consistent timezone-aware storage.

Queries should convert user-local reporting periods into precise server/database boundaries.

---

# 104. Avoid Function Wrapping Indexed Columns

Avoid patterns such as:

```sql
WHERE DATE(created_at) = :date
```

when an indexed timestamp can be queried as a range.

Prefer:

```sql
WHERE created_at >= :start
  AND created_at < :end
```

---

# 105. Expression Indexes

Expression indexes may be used when the same normalized expression is queried frequently.

Example:

```text
lower(normalized_name)
```

However, they should not be added without a demonstrated query requirement.

---

# 106. Search Index Strategy

For Product/customer-like search, the system should distinguish:

* exact identifier lookup;
* prefix lookup;
* substring lookup;
* full-text search.

Each requires a different strategy.

---

# 107. Exact Search

Use B-tree indexes for:

```text
=
```

queries.

Examples:

* UUID;
* product code;
* barcode;
* phone;
* employee identifier.

---

# 108. Prefix Search

Prefix queries such as:

```text
name LIKE 'bur%'
```

may benefit from an appropriate B-tree strategy depending on collation and query form.

---

# 109. Substring Search

Queries such as:

```text
name ILIKE '%burger%'
```

may require PostgreSQL trigram indexing for large datasets.

This should be introduced only if Product search volume justifies it.

---

# 110. Full-Text Search

PostgreSQL full-text search may be used for more advanced searchable text.

It should not be introduced merely because search exists.

POS search should remain simple and fast.

---

# 111. Covering Indexes

`INCLUDE` columns may be used when they allow PostgreSQL to satisfy frequent read queries with index-only scans.

Example:

```text
INDEX (business_uuid, branch_uuid)
INCLUDE (status, name)
```

The actual benefit must be verified with execution plans.

---

# 112. Covering Index Caution

Do not include large columns such as:

* JSON payloads;
* images;
* long descriptions;
* audit snapshots

without strong evidence.

Large indexes increase storage and write cost.

---

# 113. JSONB Indexing

JSONB fields should not automatically receive GIN indexes.

JSONB indexing is justified only when structured JSON fields are frequently queried.

---

# 114. Audit JSONB

Audit payloads may contain flexible old/new state data.

The system should not index every JSONB key.

Common audit filtering fields should be stored as normal columns.

---

# 115. Normal Columns vs JSONB

If a value is frequently used for:

* filtering;
* sorting;
* joining;
* authorization;

it should generally be a dedicated relational column rather than only JSONB.

---

# 116. Index Selectivity

High-selectivity columns generally provide more useful filtering.

Examples:

* UUID;
* operation UUID;
* product code;
* device UUID.

Low-selectivity columns include:

* boolean flags;
* small status sets.

Low-selectivity indexes should be justified by workload.

---

# 117. Boolean Indexes

A standalone index on:

```text
active
```

is often not useful.

Instead, consider:

```text
business_uuid
WHERE active = TRUE
```

or another query-aligned composite/partial index.

---

# 118. Status Indexes

A standalone status index is often insufficient.

Prefer a query-specific index such as:

```text
business_uuid
branch_uuid
created_at
WHERE status IN (...)
```

when appropriate.

---

# 119. Partial Index Strategy

Partial indexes are valuable for operational subsets such as:

* active Products;
* open Orders;
* active Cash Sessions;
* unread Notifications;
* pending Sync operations;
* eligible Lifecycle jobs.

---

# 120. Partial Index Maintenance

Partial indexes must reflect actual application state values.

When status values change, migrations must update the index predicate accordingly.

---

# 121. Index Redundancy

The database schema must periodically be reviewed for duplicate or overlapping indexes.

Example:

```text
INDEX (business_uuid, branch_uuid)
INDEX (business_uuid, branch_uuid, created_at)
```

may both be justified, but the reason must be documented.

---

# 122. Write Cost

Every index adds write overhead.

For high-volume tables such as:

* Order;
* Order Item;
* Inventory Transaction;
* Payment;
* Audit Event;
* Sync Operation;

index count must be controlled.

---

# 123. High-Write Tables

Indexes on append-heavy tables must be selected carefully.

The priority is:

```text
critical lookup
+
required reporting
+
required integrity
```

not maximum indexing.

---

# 124. Historical Tables

Historical tables may tolerate more indexes if:

* writes are less frequent;
* reads are common;
* reports require them.

However, storage growth must still be monitored.

---

# 125. Audit Table Index Strategy

Audit indexes should be chosen around actual administrative investigations.

Typical priority:

1. Business + timestamp;
2. Entity + timestamp;
3. Employee + timestamp;
4. Transaction UUID;
5. Device UUID.

---

# 126. Inventory Transaction Index Strategy

Typical priority:

1. Warehouse + Product;
2. Product + timestamp;
3. Business + Branch + timestamp;
4. Source transaction UUID.

---

# 127. Order Index Strategy

Typical priority:

1. Business + Branch + active state;
2. Cash Session;
3. Table + active state;
4. Business + Branch + created_at;
5. source/order relationship.

---

# 128. Payment Index Strategy

Typical priority:

1. Order;
2. Cash Session;
3. Business + Branch + created_at;
4. Payment operation UUID;
5. Employee + date where reporting requires it.

---

# 129. Cash Session Index Strategy

Typical priority:

1. Register + active state;
2. Branch + created_at;
3. Cashier + date.

---

# 130. Payroll Index Strategy

Typical priority:

1. Business + Employee;
2. Payroll period;
3. Branch + period;
4. finalized status where relevant.

---

# 131. Attendance Index Strategy

Typical priority:

1. Employee + date;
2. Branch + date;
3. Business + date.

---

# 132. Notification Index Strategy

Typical priority:

1. Employee + unread;
2. Employee + created_at;
3. Business + created_at;
4. Notification type where justified.

---

# 133. Configuration Index Strategy

Typical priority:

1. Business + Branch + entity;
2. entity + version;
3. effective state;
4. effective timestamp.

---

# 134. Synchronization Index Strategy

Typical priority:

1. operation UUID;
2. Device + status;
3. Business + status;
4. retry timestamp;
5. created_at.

---

# 135. Lifecycle Index Strategy

Typical priority:

1. lifecycle state + eligibility timestamp;
2. deletion job status;
3. next retry timestamp.

---

# 136. Query Scope Rule

Operational queries should always have the narrowest practical scope.

Prefer:

```text
Business
→ Branch
→ Entity
→ Time Range
```

over:

```text
Entire database
→ Entity
```

---

# 137. Query Projection

POS queries should select only required columns.

Avoid:

```sql
SELECT *
```

for critical POS operations.

---

# 138. Selective Loading

POS screens should not load:

* audit payloads;
* historical versions;
* unrelated reports;
* large JSON objects

unless required.

---

# 139. Join Strategy

Joins should follow known domain relationships.

Avoid accidental N+1 query patterns.

---

# 140. N+1 Query Prevention

ORM code must detect and prevent:

```text
1 query for Orders
+
N queries for Order Items
```

when the UI requires the complete dataset.

However, eager loading must also remain bounded.

---

# 141. ORM Loading Strategy

SQLAlchemy loading strategy should be selected according to the use case:

* lazy loading where appropriate;
* joined loading for small one-to-one relationships;
* select-in loading for bounded collections;
* explicit queries for large historical datasets.

---

# 142. Query Result Limits

Interactive endpoints should use explicit limits.

Examples:

```text
50
100
200
```

depending on the screen.

Unbounded result sets should not be returned to POS clients.

---

# 143. Report Query Limits

Reports may process larger datasets, but the work should occur in controlled background jobs.

Interactive requests should not be allowed to trigger unbounded scans.

---

# 144. Search Result Limits

Product and employee searches should return bounded results.

For example:

```text
LIMIT 50
```

may be used for autocomplete-style operations.

The exact limit remains configurable.

---

# 145. Deterministic Ordering

Queries returning paginated or user-visible lists must have deterministic ordering.

Preferred:

```text
created_at DESC,
uuid DESC
```

or another stable unique ordering.

---

# 146. Avoid Random Ordering

Queries must not use:

```sql
ORDER BY RANDOM()
```

for normal application operations.

Randomized selection should use a dedicated strategy if ever required.

---

# 147. Count Query Strategy

Exact `COUNT(*)` over very large tables may be expensive.

The system should only calculate exact counts when the UI/report requires them.

Pagination endpoints should not automatically execute an expensive count query unless needed.

---

# 148. Existence Query

When only existence is required, use an existence-oriented query.

Prefer:

```sql
SELECT 1
...
LIMIT 1;
```

rather than loading full records.

---

# 149. Existence for Table Occupancy

Table occupancy should use an existence query over active Orders rather than loading all Orders.

---

# 150. Existence for Active Session

Active Cash Session lookup should retrieve only the required Session identity/context.

---

# 151. Query Batching

Bulk operations should use bounded batches.

Examples:

* synchronization;
* deletion;
* report preparation;
* audit export;
* inventory recalculation.

---

# 152. Bulk Insert

Bulk insert should be used for high-volume append operations where appropriate.

Examples:

* synchronization events;
* report rows;
* notification recipients;
* inventory transactions.

Business-critical validation must still occur before commit.

---

# 153. Bulk Update

Bulk updates must not bypass important business logic or historical integrity.

Bulk SQL is appropriate for controlled maintenance operations.

---

# 154. Bulk Delete

Bulk deletion must be limited to lifecycle-controlled deletion jobs.

Normal application workflows must not issue broad deletes.

---

# 155. Query Parameterization

All application queries must use parameterized SQL or ORM parameter binding.

String concatenation must not be used for user-controlled SQL values.

---

# 156. SQL Injection Protection

Indexes do not protect against SQL injection.

The application must use:

* SQLAlchemy parameters;
* safe query builders;
* validated identifiers;
* controlled dynamic SQL.

---

# 157. Dynamic Sorting

User-selected sorting fields must come from a predefined allowlist.

The application must not directly inject arbitrary column names into SQL.

---

# 158. Dynamic Filtering

Supported filters should be explicitly defined.

The application must not accept arbitrary SQL expressions from users.

---

# 159. Query Timeout

Long-running interactive queries should have controlled timeout behavior.

A slow report query must not hold an interactive POS request indefinitely.

---

# 160. Lock Timeout

Where appropriate, lock acquisition should have controlled timeout behavior.

A POS request must fail safely rather than waiting indefinitely for a conflicting administrative transaction.

---

# 161. EXPLAIN

Important queries must be inspected using:

```sql
EXPLAIN
```

and:

```sql
EXPLAIN ANALYZE
```

in a safe testing environment.

---

# 162. EXPLAIN ANALYZE Production Safety

`EXPLAIN ANALYZE` executes the query.

It must not be casually executed against production write queries.

Testing should use safe read queries or controlled environments.

---

# 163. Query Plan Review

Important queries should verify:

* index usage;
* row estimates;
* actual rows;
* execution time;
* sequential scans;
* sort operations;
* join strategy;
* buffer usage where needed.

---

# 164. Sequential Scan

Sequential scans are not automatically bad.

A sequential scan may be correct when:

* table is small;
* query returns most rows;
* index selectivity is poor.

The goal is not to eliminate every sequential scan.

---

# 165. Index Scan

Index scans are generally useful when:

* the predicate is selective;
* the table is large;
* only a small result set is needed.

---

# 166. Bitmap Scan

Bitmap scans may be useful for moderately selective queries combining multiple conditions.

The query planner should be allowed to choose the best strategy.

---

# 167. Query Planner Statistics

PostgreSQL statistics must remain current.

Autovacuum and analyze behavior must be monitored.

---

# 168. ANALYZE

Large data changes may require ANALYZE so the planner has current distribution statistics.

---

# 169. VACUUM

Vacuum is required to maintain PostgreSQL tables and indexes.

The system must monitor autovacuum effectiveness on high-write tables.

---

# 170. High-Write Table Maintenance

Special attention should be given to:

* Order;
* Order Item;
* Inventory Transaction;
* Payment;
* Audit;
* Sync Operation.

These tables may generate significant dead tuples.

---

# 171. Index Bloat

Index growth and bloat must be monitored.

Unnecessary or obsolete indexes should be removed through controlled migrations.

---

# 172. Concurrent Index Creation

Large production indexes may require:

```sql
CREATE INDEX CONCURRENTLY
```

to reduce blocking.

The migration process must account for the operational characteristics of concurrent index creation.

---

# 173. Concurrent Index Drop

Similarly, large obsolete indexes may require controlled removal strategies.

---

# 174. Migration Index Strategy

Index migrations must consider:

* table size;
* write traffic;
* lock duration;
* deployment method;
* rollback strategy.

---

# 175. Duplicate Index Detection

The schema review process should periodically identify:

* exact duplicate indexes;
* redundant prefix indexes;
* unused indexes;
* overlapping indexes.

---

# 176. Unused Index Review

Unused indexes should not be immediately deleted.

The review must consider:

* rare but critical administrative queries;
* scheduled reports;
* lifecycle jobs;
* future workload;
* cold-start statistics.

---

# 177. Index Naming

Indexes should follow predictable names.

Recommended:

```text
pk_<table>
uq_<table>_<columns>
ix_<table>_<columns>
ux_<table>_<columns>
```

Partial unique indexes may use:

```text
ux_<table>_<scope>_active
```

---

# 178. Index Documentation

Every non-obvious index should have a documented reason.

Example:

```text
ix_order_branch_active_created
Purpose:
Fast lookup of active Branch Orders ordered by creation time.
```

---

# 179. Index Review During Schema Changes

Whenever a table changes, its indexes must be reviewed.

New fields may change:

* filtering;
* sorting;
* uniqueness;
* reporting;
* query selectivity.

---

# 180. Index Review During Feature Changes

A new feature must not automatically create indexes for every new field.

The feature must identify its real query patterns first.

---

# 181. Index Review During Reporting Changes

New reports may require new indexes.

However, reports should first be tested against realistic datasets.

---

# 182. Index Review During Offline Sync

Synchronization changes may require indexes for:

* operation UUID;
* Device;
* status;
* retry time;
* created time.

---

# 183. Index Review During Lifecycle Changes

Lifecycle jobs may require indexes for:

* deletion eligibility;
* lifecycle state;
* deletion batch status;
* retry timestamp.

---

# 184. Indexes and Historical Retention

Historical data grows continuously.

Index strategy must account for long-term growth rather than only initial dataset size.

---

# 185. Partitioning Decision

Partitioning is not required by default.

It may become appropriate for very large append-heavy tables such as:

* Audit Events;
* Inventory Transactions;
* Orders;
* Synchronization Events.

Partitioning must be introduced only after measured workload and data volume justify it.

---

# 186. Partition Key

If partitioning is introduced, the partition key must align with actual query patterns.

Time-based partitioning may be appropriate for historical event tables.

Business-based partitioning must be evaluated carefully because tenant distribution may be uneven.

---

# 187. Partitioning and Foreign Keys

Partitioning must preserve required referential integrity.

The chosen PostgreSQL design must be validated before adoption.

---

# 188. Materialized Views

Materialized views may be used for expensive read-heavy reporting.

They must not become the authoritative operational source.

---

# 189. Cache vs Index

Application caching may reduce repeated database reads.

Caching must not be used as a replacement for appropriate indexes.

---

# 190. Redis

If Redis is introduced, it remains a cache/temporary infrastructure component.

PostgreSQL remains authoritative.

Cache invalidation must occur after authoritative database changes.

---

# 191. Query Cache Safety

Cached data must respect:

* Business;
* Branch;
* Employee permission;
* configuration version;
* lifecycle state.

A cache key must never allow cross-Business reuse.

---

# 192. Cache Key Example

A tenant-aware cache key may conceptually contain:

```text
business_uuid
branch_uuid
resource
version
```

where relevant.

---

# 193. POS Configuration Cache

Current menu/configuration may be cached.

The cache must be invalidated or versioned after:

* price change;
* menu change;
* Branch availability change;
* Recipe configuration change;
* Set configuration change.

---

# 194. Query Strategy for Configuration Changes

The POS should resolve the latest effective configuration efficiently without scanning all historical versions.

A current-version pointer or indexed effective state is preferred.

---

# 195. Query Strategy for Historical Prices

Historical Orders must read price snapshots from Order Items.

They must not query the current Product price for historical reconstruction.

---

# 196. Query Strategy for Historical Recipes

Historical inventory deductions must reference the Recipe Version used at transaction time.

They must not reconstruct old deductions from the current Recipe.

---

# 197. Query Strategy for Cash Reports

Cash Session reports should primarily query:

```text
Cash Session
Payments
Orders
Corrections
```

using indexed session identifiers.

They should not scan the entire Business history.

---

# 198. Query Strategy for Branch Reports

Branch reports should use:

```text
business_uuid
branch_uuid
date range
```

as the primary scope.

---

# 199. Query Strategy for Business Reports

Business-level reports aggregate across Branches.

The query must remain Business-scoped.

Branch filters may be optional.

---

# 200. Query Strategy for Employee Reports

Employee reports should filter by:

```text
business_uuid
employee_uuid
date range
```

rather than scanning all Businesses.

---

# 201. Query Strategy for Payroll Reports

Payroll queries should use:

```text
business_uuid
period
branch_uuid
employee_uuid
```

according to the report scope.

---

# 202. Query Strategy for Audit Export

Audit exports must:

* require permission;
* apply Business scope;
* apply optional Branch scope;
* use date ranges;
* process large exports asynchronously when needed.

---

# 203. Query Strategy for Excel Export

Excel exports must not load an unlimited result set into application memory.

Large exports should use streaming/batched reads.

---

# 204. Query Strategy for Deletion

Deletion workers should process one bounded Business or bounded child batch at a time.

They must not load all tenant data into memory.

---

# 205. Query Strategy for Synchronization

Synchronization must use:

* stable operation UUID;
* bounded batches;
* deterministic ordering;
* indexed pending-state queries;
* idempotent processing.

---

# 206. Query Strategy for Conflict Resolution

Conflict lookup should use stable identifiers:

```text
operation_uuid
entity_uuid
Business
```

rather than expensive historical scans.

---

# 207. Query Strategy for Notifications

Unread notification queries must use recipient-scoped indexes.

The system must not query all Business notifications and filter in application memory.

---

# 208. Query Strategy for Permissions

Permission resolution must load only relevant:

* Employee;
* Roles;
* Overrides;
* Branch scope;
* Subscription entitlement.

It must not retrieve unrelated Business permission data.

---

# 209. Query Strategy for Employee Branch Switching

When Branch context changes, the application should issue targeted queries for:

* Branch;
* Employee assignment;
* permissions;
* menu configuration;
* active Cash Session where relevant.

---

# 210. Query Strategy for Device Authentication

Device authentication must use indexed identifiers.

The system must not scan all Devices belonging to a Business.

---

# 211. Query Strategy for Subscription Validation

Subscription checks should resolve the current Business subscription efficiently.

Historical subscription records should not be scanned during every POS operation.

---

# 212. Query Strategy for Lifecycle Validation

Normal POS operations should not execute expensive lifecycle history queries.

Current lifecycle state must be directly available.

---

# 213. Query Strategy for Current State

Frequently accessed current state should be represented directly rather than reconstructed from complete history.

Examples:

```text
Current Inventory Balance
Current Cash Session
Current Product Configuration
Current Subscription
Current Employee Status
```

---

# 214. Current State vs History

The system should separate:

```text
Current Operational State
```

from:

```text
Historical Event Data
```

This allows fast POS queries while preserving complete history.

---

# 215. Query Strategy for Event History

Historical event tables should be queried only when history is required.

POS screens should not automatically load complete histories.

---

# 216. Database Read Path

The preferred operational read path is:

```text
Business Context
      ↓
Branch Context
      ↓
Current State
      ↓
Required Entity
      ↓
Small Related Dataset
```

---

# 217. Database Write Path

The preferred write path is:

```text
Validate
  ↓
Begin Transaction
  ↓
Lock Required Rows
  ↓
Write Core State
  ↓
Write History / Outbox
  ↓
Commit
  ↓
Secondary Processing
```

---

# 218. Query Consistency

Queries inside one critical transaction must observe the correct transaction state.

The application must not assume that separate queries outside the transaction remain consistent under concurrent writes.

---

# 219. Query Race Conditions

Typical race conditions include:

* two Cashiers opening a session;
* two sales consuming the last inventory unit;
* two employees editing configuration;
* duplicate payment submission;
* duplicate sync submission.

Indexes alone are insufficient.

The query must be combined with appropriate transaction/locking logic.

---

# 220. Query and Lock Ordering

Queries that lock multiple resources must follow consistent ordering.

This reduces deadlock risk.

---

# 221. SELECT FOR UPDATE

`SELECT ... FOR UPDATE` may be used when the application must lock a row before modifying it.

It should be limited to the transaction's required scope.

---

# 222. Atomic UPDATE

For simple state changes, an atomic conditional UPDATE may be preferable to:

```text
SELECT
→ application check
→ UPDATE
```

Example:

```sql
UPDATE inventory_balance
SET quantity = quantity - :qty
WHERE uuid = :uuid
  AND quantity >= :qty;
```

---

# 223. Affected Row Validation

After an atomic conditional UPDATE, the application must inspect the affected-row count.

Zero rows may indicate:

* insufficient stock;
* stale state;
* missing entity;
* concurrent modification.

---

# 224. Query Error Classification

Database query failures should be classified into application-level categories.

Examples:

```text
Duplicate
Conflict
Invalid Reference
Validation Error
Timeout
Deadlock Retry
Infrastructure Failure
```

---

# 225. Deadlock Retry

A transaction encountering a PostgreSQL deadlock may be safely retried when the operation is idempotent and retry-safe.

Retries must be bounded.

---

# 226. Serialization Failure Retry

If stronger isolation causes serialization failures, the application may retry the transaction where the operation is safe.

---

# 227. Query Retry Safety

A query must not be blindly retried if it may have partially committed external effects.

Core database transactions should remain isolated from external side effects.

---

# 228. External Side Effects

Database transactions should not remain open while waiting for:

* printer;
* payment processor;
* notification provider;
* external API.

---

# 229. Query Performance Budget

Critical POS operations should have explicit performance targets.

Targets should be measured rather than assumed.

Examples of candidate measurements:

```text
Menu load
Order creation
Order acceptance
Stock validation
Payment creation
Cash Session lookup
Employee authentication
```

---

# 230. Performance Baseline

A baseline dataset should be created for performance testing.

It should contain realistic quantities of:

* Businesses;
* Branches;
* Products;
* Orders;
* Order Items;
* Inventory Transactions;
* Payments;
* Audit Events.

---

# 231. Realistic Data Distribution

Performance testing must not rely only on tiny development databases.

Important queries should be tested against realistic data distributions.

---

# 232. Query Regression Tests

Critical SQL queries should have performance regression tests.

A schema or index change must not silently make critical POS queries significantly slower.

---

# 233. Index Regression Tests

Index migrations should verify:

* expected index exists;
* index predicate is correct;
* query plan remains acceptable;
* write performance remains acceptable.

---

# 234. Query Observability

Production monitoring should identify:

* slow queries;
* high-frequency queries;
* expensive report queries;
* lock waits;
* deadlocks;
* sequential scans on large tables;
* excessive database connections.

---

# 235. Slow Query Logging

PostgreSQL slow query logging should be configured according to operational requirements.

Thresholds should avoid excessive log volume while capturing problematic queries.

---

# 236. Query Statistics

`pg_stat_statements` may be used to identify:

* most expensive queries;
* most frequently executed queries;
* cumulative execution time;
* average execution time.

---

# 237. Index Usage Monitoring

Index usage statistics should be reviewed periodically.

Unused indexes may be candidates for removal after proper analysis.

---

# 238. Index Storage Monitoring

Index size should be monitored for high-volume tables.

Unexpected growth may indicate:

* excessive indexing;
* data growth;
* bloat;
* inefficient data distribution.

---

# 239. Autovacuum Monitoring

Autovacuum must be monitored especially for:

* Orders;
* Payments;
* Inventory Transactions;
* Audit;
* Synchronization tables.

---

# 240. Query Strategy and Scaling

The initial architecture uses one PostgreSQL authoritative database.

If read volume increases substantially, future scaling may include:

```text
Primary PostgreSQL
        ↓
Read Replicas
```

where appropriate.

---

# 241. Read Replica Rule

Read replicas must not be used for operations requiring immediate authoritative state unless replication guarantees are sufficient.

Critical POS operations must remain on the authoritative primary.

---

# 242. Reporting Read Replica

Heavy reporting may eventually be routed to read replicas.

Historical report correctness must still be preserved.

---

# 243. Cache and Read Replica

Cache, read replica and materialized views are optimization layers.

They must not replace the authoritative primary database for critical writes.

---

# 244. Query Strategy Invariants

The following invariants apply to indexes and queries.

1. Indexes are designed around real query patterns.
2. Indexes are not treated as authorization.
3. Business scope is applied to Business-owned queries.
4. Branch scope is applied to Branch-owned queries.
5. Primary keys provide identity lookup.
6. Duplicate primary-key indexes are not created.
7. Foreign keys are indexed when query workload requires it.
8. Composite indexes follow actual filtering patterns.
9. Equality dimensions generally precede range dimensions.
10. Range dimensions generally precede secondary ordering dimensions.
11. Composite index order is intentional.
12. Standalone low-selectivity indexes are avoided unless justified.
13. Boolean indexes are used only when workload supports them.
14. Status indexes are query-specific.
15. Partial indexes are used for operational subsets where beneficial.
16. Active Cash Session lookup is indexed.
17. Active Product lookup can use partial indexes when justified.
18. Open Order lookup is indexed.
19. Table occupancy queries target active Orders only.
20. Cash Session order lookup is indexed.
21. Product code lookup is indexed.
22. Product barcode lookup is indexed where required.
23. Recipe Version lookup is indexed.
24. Recipe component lookup is indexed.
25. Reverse recipe dependency lookup is indexed.
26. Set component lookup is indexed.
27. Reverse Set dependency lookup is indexed where required.
28. Inventory Balance Product/Warehouse lookup is indexed.
29. Inventory history is indexed by actual report dimensions.
30. Inventory transaction inserts are not burdened by unnecessary indexes.
31. Inventory concurrency does not rely only on indexes.
32. Order Branch/date access is indexed.
33. Order active-state access is optimized.
34. Order Table occupancy is optimized.
35. Order Cash Session lookup is optimized.
36. Customer-facing Order Number is efficiently unique.
37. Historical Order pagination is deterministic.
38. Keyset pagination is preferred for deep history.
39. Payment Order lookup is indexed.
40. Payment Cash Session lookup is indexed.
41. Payment operation UUID is uniquely indexed.
42. Refund lookup paths are indexed.
43. Debt Customer lookup is indexed according to actual search needs.
44. Cash Register Branch lookup is indexed.
45. Active Cash Session lookup uses an efficient partial index.
46. Employee Branch assignment supports both directions where needed.
47. Permission resolution uses efficient scoped queries.
48. Device authentication uses indexed identifiers.
49. Subscription current-state lookup is indexed.
50. Configuration current-state lookup is indexed.
51. Configuration history lookup is indexed.
52. Audit Business/date queries are indexed.
53. Audit entity history is indexed.
54. Audit actor history is indexed where required.
55. Notification unread lookup is optimized.
56. Synchronization operation UUID lookup is unique and fast.
57. Synchronization pending-state queries are indexed.
58. Lifecycle eligibility queries are indexed.
59. Background job retry queries are indexed.
60. Timestamp ranges use half-open intervals.
61. Timestamp columns are not unnecessarily wrapped in functions.
62. User-visible lists have deterministic ordering.
63. Interactive queries use bounded result sets.
64. POS queries avoid SELECT *.
65. POS queries avoid unnecessary historical joins.
66. POS queries avoid expensive aggregations.
67. N+1 ORM queries are prevented.
68. ORM eager loading remains bounded.
69. Search queries use an appropriate index strategy.
70. Exact search uses B-tree where appropriate.
71. Substring search uses specialized indexing only when justified.
72. JSONB is not indexed indiscriminately.
73. Frequently filtered JSON data should become relational columns where appropriate.
74. Covering indexes are introduced only when beneficial.
75. Large columns are not unnecessarily included in indexes.
76. Every index adds write cost.
77. High-write tables receive controlled indexing.
78. Historical tables may use additional indexes where justified.
79. Duplicate indexes are periodically reviewed.
80. Redundant indexes are removed through controlled migration.
81. Index naming follows a predictable convention.
82. Non-obvious indexes have documented purpose.
83. Index migrations consider table size.
84. Large production indexes use safe migration techniques.
85. Index removal considers rare critical queries.
86. Query plans are measured.
87. EXPLAIN is used for query analysis.
88. EXPLAIN ANALYZE is used carefully.
89. Sequential scans are not automatically considered failures.
90. Query planner statistics remain current.
91. ANALYZE is performed when required.
92. VACUUM/autovacuum remains healthy.
93. Index bloat is monitored.
94. High-write tables receive maintenance attention.
95. Query timeouts are controlled.
96. Lock timeouts are controlled where appropriate.
97. Long transactions are avoided.
98. External operations do not execute inside core database transactions.
99. Deadlock-prone operations use predictable lock order.
100. Row-level locks are used for high-contention state.
101. Atomic UPDATE is preferred for simple conditional state changes.
102. Affected-row counts are validated.
103. Deadlocks may be retried only when safe.
104. Serialization failures may be retried only when safe.
105. Query retries are idempotent.
106. Query errors are classified safely.
107. Query errors do not reveal cross-Business information.
108. Performance baselines use realistic datasets.
109. Critical queries have regression tests.
110. Index changes are performance-tested.
111. Slow queries are observable.
112. Query statistics are monitored.
113. Index usage is monitored.
114. Index storage is monitored.
115. Autovacuum behavior is monitored.
116. Read replicas are not used for authoritative writes.
117. Cache is not authoritative.
118. Materialized views are not authoritative.
119. Reporting may scale independently from POS.
120. Critical POS queries remain optimized before reporting optimization.
121. Tenant isolation remains mandatory in every query path.
122. Branch isolation remains mandatory in Branch-scoped queries.
123. Background jobs use bounded queries.
124. Deletion jobs use bounded queries.
125. Synchronization uses bounded batches.
126. Excel exports use streaming/batched reads where necessary.
127. Report queries use explicit date boundaries.
128. Unbounded production scans are avoided.
129. Current state is queried directly.
130. Historical state is not reconstructed unnecessarily.
131. Historical snapshots are used for historical financial queries.
132. Configuration history is not scanned during ordinary POS operations.
133. Current inventory is not reconstructed from all inventory transactions.
134. Current Cash Session is not reconstructed from all historical sessions.
135. Current subscription is not reconstructed from all historical subscriptions.
136. Current Employee status is directly available.
137. Permission caches remain secondary to authoritative data.
138. Cache keys remain tenant-aware.
139. Configuration caches are version-aware.
140. Read replica lag is considered for consistency-sensitive queries.
141. Query design remains compatible with future scaling.
142. Partitioning is introduced only after measured need.
143. Materialized views are introduced only for justified read-heavy workloads.
144. Indexing remains simpler than necessary only where performance remains acceptable.
145. Indexing is not increased merely for theoretical optimization.
146. Query strategy is reviewed with every major feature.
147. Query strategy is reviewed with major data-model changes.
148. Query strategy is reviewed with major reporting changes.
149. Query strategy is reviewed with major synchronization changes.
150. Query strategy remains aligned with database integrity constraints.
151. Query strategy remains aligned with tenant isolation.
152. Query strategy remains aligned with transaction boundaries.
153. Query strategy must not weaken historical integrity.
154. Query strategy must not weaken security.
155. Query strategy must not make POS unnecessarily dependent on powerful hardware.
156. Database performance must remain measurable.
157. Performance optimizations must remain explainable.
158. Critical indexes must have a clear purpose.
159. Query optimization must preserve correctness.
160. Correctness has priority over micro-optimization.

---

# 245. Recommended Initial Index Map

The following is a starting strategy, not a requirement to create every index blindly.

| Domain                 | Query Need              | Suggested Index                                 |
| ---------------------- | ----------------------- | ----------------------------------------------- |
| Business               | Code lookup             | `(code)` or Business-scoped unique              |
| Branch                 | Business + code         | `(business_uuid, code)`                         |
| Employee               | Business + active       | `(business_uuid, status)` or partial            |
| Employee Branch        | Employee lookup         | `(employee_uuid, branch_uuid)`                  |
| Employee Branch        | Branch lookup           | `(branch_uuid, employee_uuid)`                  |
| Device                 | Device identity         | `(uuid)` / unique identifier                    |
| Product                | Business + code         | `(business_uuid, code)`                         |
| Product                | Active Products         | Partial Business index                          |
| Category               | Business + code         | `(business_uuid, code)`                         |
| Recipe                 | Product                 | `(product_uuid)`                                |
| Recipe Version         | Recipe + version        | `(recipe_uuid, version_number)`                 |
| Recipe Component       | Version                 | `(recipe_version_uuid)`                         |
| Recipe Component       | Product dependency      | `(product_uuid)`                                |
| Set Version            | Set + version           | `(set_uuid, version_number)`                    |
| Set Component          | Version                 | `(set_version_uuid)`                            |
| Set Component          | Product dependency      | `(product_uuid)`                                |
| Inventory Balance      | Warehouse + Product     | Unique `(warehouse_uuid, product_uuid)`         |
| Inventory Transaction  | Product + time          | `(product_uuid, created_at DESC)`               |
| Order                  | Branch + active         | Partial composite                               |
| Order                  | Cash Session            | `(cash_session_uuid, created_at)`               |
| Order                  | Table + active          | Partial composite                               |
| Order                  | Branch + time           | `(business_uuid, branch_uuid, created_at DESC)` |
| Order Item             | Order                   | `(order_uuid)`                                  |
| Payment                | Order                   | `(order_uuid, created_at)`                      |
| Payment                | Cash Session            | `(cash_session_uuid, created_at)`               |
| Payment                | Operation               | Unique operation UUID                           |
| Debt Customer          | Business + phone        | `(business_uuid, normalized_phone)`             |
| Debt Repayment         | Customer                | `(debt_customer_uuid, created_at)`              |
| Cash Register          | Branch                  | `(branch_uuid)`                                 |
| Cash Session           | Active register         | Partial unique                                  |
| Cash Session           | Branch + time           | `(branch_uuid, created_at DESC)`                |
| Attendance             | Employee + time         | `(employee_uuid, clock_in)`                     |
| Payroll                | Employee + period       | `(employee_uuid, payroll_period)`               |
| Configuration          | Entity                  | `(business_uuid, branch_uuid, entity_uuid)`     |
| Configuration Version  | Configuration + version | Unique                                          |
| Audit                  | Business + time         | `(business_uuid, created_at DESC)`              |
| Audit                  | Entity + time           | `(entity_uuid, created_at DESC)`                |
| Audit                  | Employee + time         | `(employee_uuid, created_at DESC)`              |
| Report Version         | Report + version        | Unique                                          |
| Notification Recipient | Employee + unread       | Partial                                         |
| Sync Operation         | Operation UUID          | Unique                                          |
| Sync Operation         | Device + status         | Composite/partial                               |
| Lifecycle              | State + eligibility     | Composite/partial                               |

---

# 246. Index Creation Policy

An index should normally be created when at least one of the following is true:

1. It enforces a required uniqueness rule.
2. It supports a critical POS query.
3. It supports a high-frequency operational query.
4. It supports a high-volume synchronization query.
5. It supports a lifecycle worker query.
6. It materially improves an important report.
7. It prevents expensive full-table scans for a known large dataset.

An index should not be created solely because a column is frequently selected.

---

# 247. Index Removal Policy

An index may be removed only after checking:

* query statistics;
* scheduled jobs;
* reports;
* administrative tools;
* rare critical paths;
* unique constraint dependencies;
* foreign-key behavior.

Removal must use a controlled migration.

---

# 248. Production Performance Principle

The database must optimize for real operational behavior:

```text
Fast POS
+
Safe Transactions
+
Strong Tenant Isolation
+
Predictable Reports
+
Reliable Synchronization
+
Controlled Historical Queries
```

The goal is not to maximize the number of indexes.

The goal is to provide the correct indexes for the correct queries.

---

# 249. Final Database Query Architecture

The intended architecture is:

```text
                    PostgreSQL
                        │
        ┌───────────────┼────────────────┐
        │               │                │
   Current State     History         Background
        │               │                │
   POS Queries      Reports         Sync/Lifecycle
        │               │                │
   Fast Indexed     Indexed         Bounded Queries
   Lookups          Ranges          + Idempotency
        │               │                │
        └───────────────┼────────────────┘
                        │
                 Application Layer
                        │
             Business / Branch Scope
                        │
                 Authorization
```

---

# 250. Status

**Database Analysis:** Completed.

**Document Status:** Accepted.

**Current Document:** `26_Database_Indexes_and_Query_Strategy.md`

**Next Document:** `27_Database_Migrations_and_Change_Management.md`

---

# 251. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`

### Domain Analysis

* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`
* `docs/03_Domain_Analysis/13_Reporting_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### Architecture

* `docs/04_Architecture/01_System_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/08_Offline_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/14_Caching_Architecture.md`
* `docs/04_Architecture/16_Scalability_and_Performance_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`

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
* `docs/05_Database/27_Database_Migrations_and_Change_Management.md`
* `docs/05_Database/28_Database_Backup_and_Recovery.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

