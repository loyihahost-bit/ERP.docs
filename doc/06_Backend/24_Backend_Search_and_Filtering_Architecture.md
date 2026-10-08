# Backend Search and Filtering Architecture

**Document ID:** BE-24
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This document defines the backend architecture for search, filtering, sorting, pagination and query optimization across FastFood ERP.

The system must allow users to find relevant business data quickly while preserving:

* Business isolation;
* Branch isolation;
* permission boundaries;
* subscription restrictions;
* historical integrity;
* query performance;
* predictable API behavior;
* database stability.

Search and filtering must be implemented as controlled application capabilities rather than unrestricted database queries.

---

## 2. Scope

This document covers:

* search;
* filtering;
* sorting;
* pagination;
* cursor pagination;
* offset pagination;
* query building;
* PostgreSQL search;
* exact search;
* prefix search;
* partial search;
* full-text search;
* identifier search;
* date/time filtering;
* numeric filtering;
* status filtering;
* Branch filtering;
* permission-aware filtering;
* tenant isolation;
* audit/history search;
* Order search;
* Product search;
* Employee search;
* Inventory search;
* Report search;
* configuration search;
* indexing;
* query limits;
* performance;
* caching;
* background search;
* export queries;
* security;
* observability;
* testing.

---

## 3. Search Principles

The backend follows these principles:

1. Search must always respect Business scope.
2. Branch scope must be applied before returning results.
3. Authorization is not a UI-only filter.
4. Client-provided Business UUID is not authoritative.
5. Client-provided Branch UUID is validated against access scope.
6. Search must not bypass subscription restrictions.
7. Search must not expose archived/deleted data unless authorized.
8. Search queries must be bounded.
9. API responses must use pagination.
10. Large datasets must not be returned in a single request.
11. Search must use appropriate indexes.
12. Expensive search must not block core POS transactions.
13. Search results must be deterministic.
14. Sorting must be explicit.
15. Search behavior must be consistent across endpoints.
16. Search must not expose hidden fields through filtering.
17. Search must not become an alternative authorization mechanism.
18. Search performance must be measurable.
19. Database remains authoritative.
20. Search optimization must never weaken data correctness or isolation.

---

## 4. Search vs Filtering

Search and filtering are related but different.

### Search

Search finds records based on textual or identifier input.

Examples:

```text
Burger
Lavash
EMP-1024
ORD-583921
```

### Filtering

Filtering narrows records based on structured conditions.

Examples:

```text
status = ACTIVE
branch = Branch A
created_at >= 2026-01-01
price >= 30000
```

An endpoint may support both:

```text
Search
+
Filters
+
Sorting
+
Pagination
```

---

## 5. Query Pipeline

The standard backend query pipeline is:

```text
HTTP Request
    ↓
Authentication
    ↓
Business Context
    ↓
Branch Scope
    ↓
Permission Check
    ↓
Subscription Check
    ↓
Input Validation
    ↓
Search/Filter Specification
    ↓
Repository Query
    ↓
Database
    ↓
Projection
    ↓
Pagination
    ↓
Response
```

The search layer must never bypass authorization.

---

## 6. Business Scope

Every Business-scoped query must include authoritative Business context.

Example:

```text
Authenticated Context
    ↓
business_id = B1
    ↓
Query only B1 records
```

The client must not be allowed to switch Business by simply sending:

```text
business_id=B2
```

The application must derive or validate Business context from authenticated authorization state.

---

## 7. Branch Scope

Branch filtering depends on the employee's permissions.

Examples:

```text
Employee A
    Branch A → allowed
    Branch B → denied
```

The query must enforce:

```text
WHERE business_id = current_business
AND branch_id IN authorized_branches
```

A Branch filter must never expand the employee's permissions.

---

## 8. All-Branch Access

An employee with valid All-Branch authority may search across multiple Branches.

Even in this case:

* Business scope remains mandatory;
* Branch identity must remain visible;
* filtering must remain explicit;
* audit/history results must retain Branch context.

---

## 9. Branch Filter Validation

If the client sends:

```text
branch_id = B2
```

the backend must verify:

1. B2 belongs to the current Business;
2. employee has access to B2;
3. subscription allows the requested operation;
4. requested resource is Branch-scoped.

Invalid Branch filters must not silently return unrestricted results.

---

## 10. Search Input Validation

Search input must be validated before query construction.

Validation should include:

* maximum length;
* allowed characters where appropriate;
* normalization;
* empty input handling;
* whitespace normalization;
* identifier format validation;
* numeric format validation.

Example:

```text
max_search_length = bounded configuration value
```

The system must not accept arbitrarily large search strings.

---

## 11. Search Normalization

For text search, normalization may include:

* trimming whitespace;
* Unicode normalization where required;
* case normalization;
* controlled transliteration where explicitly supported.

Normalization must not destroy meaningful Product or employee names.

---

## 12. Case-Insensitive Search

Human-readable search should normally be case-insensitive.

Example:

```text
burger
Burger
BURGER
```

may resolve to the same Product search result.

PostgreSQL-compatible techniques may include:

* normalized columns;
* functional indexes;
* `citext` where appropriate;
* controlled lower-case comparison.

The chosen approach must be consistent across the system.

---

## 13. Exact Search

Exact search is preferred when searching stable identifiers.

Examples:

```text
employee_id
order_uuid
product_uuid
operation_uuid
event_uuid
customer-facing order number
product code
```

Exact search should use equality predicates and appropriate indexes.

---

## 14. Prefix Search

Prefix search is useful for operational identifiers.

Examples:

```text
BUR...
ORD-58...
EMP-10...
```

Prefix search should use indexes where practical.

Unbounded leading-wildcard searches such as:

```text
%burger%
```

must not become the default strategy for large tables.

---

## 15. Partial Text Search

Partial text search may be supported for human-facing fields such as:

* Product name;
* category name;
* employee name;
* Branch name.

For large datasets, PostgreSQL trigram or full-text mechanisms may be used after measured need.

The system must avoid applying expensive substring matching to every column.

---

## 16. Full-Text Search

Full-text search may be used where users need linguistic search across longer text.

Potential use cases:

* product descriptions;
* notes;
* expense comments;
* audit reasons;
* administrative documentation.

Full-text search is not required for simple names or identifiers.

The simplest correct search mechanism should be preferred.

---

## 17. Product Search

Product search may support:

* Product name;
* Product code;
* category;
* active state;
* Branch availability;
* recipe status.

Example:

```text
Search:
    "lavash"

Filters:
    category = FAST_FOOD
    active = true
    branch = Branch A
```

Final availability must still be validated by the relevant business operation.

---

## 18. POS Product Search

POS Product search is performance-sensitive.

The normal flow should prioritize:

1. Branch context;
2. active menu;
3. effective pricing;
4. Product availability;
5. search term.

The POS must not execute expensive historical queries for ordinary Product lookup.

---

## 19. POS Search Result

POS search results should return only fields required for the POS operation.

Example:

```text
product_id
name
category
image_reference
effective_price
availability_state
```

Large descriptions, audit history and historical pricing should not be loaded into the POS search response.

---

## 20. Order Search

Order search may support:

* customer-facing Order number;
* Order UUID;
* status;
* order type;
* Cash Session;
* employee;
* Branch;
* date range;
* payment status.

Example:

```text
Order No: 381
Status: COMPLETED
Date: Today
Branch: Branch A
```

---

## 21. Order Number Search

Customer-facing Order numbers are operational identifiers.

They may repeat according to the configured numbering lifecycle.

Therefore:

* Order UUID remains authoritative;
* Order number must be combined with appropriate context when uniqueness is not global;
* Branch and date/session context may be required.

---

## 22. Employee Search

Employee search may support:

* employee code;
* first name;
* last name;
* username/login identifier where applicable;
* role;
* active state;
* Branch assignment.

Sensitive authentication information must never be searchable.

Passwords, tokens and security secrets must never be returned.

---

## 23. Inventory Search

Inventory search may support:

* Product;
* warehouse;
* stock state;
* low-stock state;
* active state;
* product type;
* Branch.

Inventory quantity displayed by search is informational.

Final stock validation must use authoritative transaction logic.

---

## 24. Inventory Transaction Search

Inventory transaction history may support:

* Product;
* transaction type;
* date range;
* source;
* Branch;
* warehouse;
* employee;
* reference transaction.

Large inventory history queries must use pagination.

---

## 25. Recipe Search

Recipe search may support:

* Product;
* Recipe status;
* Recipe Version;
* approval state;
* active state.

Restricted Recipe information must remain permission-controlled.

Search must not expose Recipe components to employees who lack Recipe visibility permission.

---

## 26. Menu Search

Menu search may support:

* Product name;
* category;
* active state;
* Branch availability;
* price state.

Global menu and Branch menu queries must remain separate in authorization context.

---

## 27. Pricing Search

Pricing queries may support:

* Product;
* Branch;
* effective version;
* active state;
* price range;
* configuration version.

Historical pricing must be queried through history/version models rather than current Product state.

---

## 28. Audit Search

Audit search is highly sensitive.

Filters may include:

* event type;
* actor;
* Branch;
* Device;
* entity;
* operation UUID;
* source;
* result;
* date range.

Audit search must always enforce:

```text
Business Scope
+
Branch Scope
+
Audit Permission
```

---

## 29. History Search

History search may support:

* entity type;
* entity UUID;
* version;
* actor;
* date range;
* event type.

History queries must not expose hidden historical information merely because the user knows an entity UUID.

---

## 30. Configuration History Search

Configuration history may support:

* Product;
* Branch;
* configuration type;
* version;
* effective state;
* actor;
* date range.

Current configuration and historical configuration must not be mixed unintentionally.

---

## 31. Report Search

Report search may support:

* report type;
* Branch;
* period;
* report version;
* status;
* creation date.

Immutable report versions remain individually addressable.

---

## 32. Subscription Search

Subscription administration search may support:

* Business;
* subscription status;
* tariff;
* expiry date;
* lifecycle state.

Super Admin scope must be clearly separated from Business employee scope.

---

## 33. Date Filtering

Date filtering must use explicit boundaries.

Example:

```text
created_at >= start
created_at < end
```

This avoids ambiguity around end-of-day timestamps.

Date-only business filters must use the relevant Business/Branch timezone.

---

## 34. Timezone

The database should store authoritative timestamps in UTC.

Business-facing date filters must be interpreted using the configured Business timezone.

Example:

```text
User selects:
2026-10-01

Business timezone:
Asia/Tashkent

Backend:
converts local calendar boundary → UTC
```

The system must not accidentally shift a date because of server timezone.

---

## 35. Date Range Limits

Search endpoints must impose reasonable maximum date ranges for interactive queries.

Example:

```text
Interactive audit search:
bounded date range

Large historical analysis:
background job
```

Exact limits should be configurable per endpoint category.

---

## 36. Numeric Filters

Numeric filters may support:

```text
=
>
>=
<
<=
BETWEEN
```

Examples:

```text
price >= 30000
quantity < 10
amount BETWEEN 50000 AND 100000
```

Numeric input must be validated and normalized before query execution.

---

## 37. Status Filters

Status values must come from defined enumerations.

The backend must reject unknown status values rather than silently ignoring them.

Example:

```text
status=UNKNOWN
```

must return validation error.

---

## 38. Multi-Filter Queries

Multiple filters should normally use logical AND.

Example:

```text
Branch = A
AND
Status = ACTIVE
AND
Created At >= date
```

OR conditions should only be supported where explicitly defined.

Complex arbitrary boolean expressions must not be accepted from clients.

---

## 39. Filter Whitelisting

The backend must define allowed filter fields per endpoint.

The client must not send arbitrary database column names.

Bad:

```text
?field=password_hash
```

Correct:

```text
?status=ACTIVE
```

This prevents accidental exposure and reduces query complexity.

---

## 40. Sort Whitelisting

Sorting fields must also be explicitly allowed.

Example:

```text
sort=created_at
sort=-created_at
sort=name
```

The client must not directly control:

* SQL expressions;
* arbitrary columns;
* SQL functions;
* raw `ORDER BY` fragments.

---

## 41. Stable Sorting

Search results must have deterministic ordering.

If sorting by a non-unique field:

```text
ORDER BY name, id
```

The unique identifier acts as a stable tie-breaker.

This is especially important for pagination.

---

## 42. Default Sorting

Every list endpoint should define a default sort.

Examples:

* newest first;
* name ascending;
* Product code ascending;
* Order creation time descending.

The default must be documented and stable.

---

## 43. Pagination

Interactive APIs must return paginated results.

Example:

```text
{
  "items": [...],
  "pagination": {
    "next_cursor": "...",
    "has_more": true
  }
}
```

The backend must enforce a maximum page size.

---

## 44. Page Size

Clients may request a page size within a bounded range.

Example:

```text
default = 25
maximum = 100
```

Exact values may vary by endpoint.

The server remains authoritative.

---

## 45. Cursor Pagination

Cursor pagination is preferred for large or frequently changing datasets.

Advantages:

* stable performance;
* avoids deep offset scans;
* better behavior under concurrent inserts;
* predictable continuation.

Cursor values must be opaque to clients.

---

## 46. Cursor Contents

A cursor may encode:

```text
sort_value
unique_id
query_version
```

The cursor must not expose sensitive database internals unnecessarily.

The server must validate cursor structure and version.

---

## 47. Cursor Query Consistency

A cursor must remain compatible with the query definition that created it.

If the client changes filters or sorting while reusing a cursor, the backend should reject the cursor as invalid.

---

## 48. Offset Pagination

Offset pagination may be used for:

* small administrative datasets;
* low-volume reference lists;
* simple internal queries.

Deep offsets on large tables should be avoided.

---

## 49. Pagination and Authorization

Authorization must be applied before pagination.

Incorrect:

```text
fetch first 100 rows
then remove unauthorized rows
```

Correct:

```text
apply authorization scope
then filter
then sort
then paginate
```

This prevents missing or leaking results.

---

## 50. Pagination and Tenant Isolation

Business and Branch restrictions must be part of the database query itself.

They must not be applied after fetching the page.

---

## 51. Search Projection

List queries should return only required columns.

Example:

```text
Product List:
id
name
code
category
active
price
```

Do not load:

* complete Recipe;
* complete audit history;
* large image content;
* unrelated relationships.

---

## 52. N+1 Prevention

Search/list queries must avoid N+1 database access.

If a list requires related data:

* use appropriate joins;
* select-in loading;
* projection queries;
* bounded secondary queries.

The implementation must be measured rather than relying on ORM defaults.

---

## 53. Search Query Object

Application services should use structured search specifications.

Example:

```text
ProductSearchQuery
├── text
├── category_id
├── branch_id
├── active
├── min_price
├── max_price
├── sort
├── cursor
└── limit
```

This is preferable to passing raw query strings into repositories.

---

## 54. Repository Search Interface

Repositories may expose controlled methods such as:

```text
search_products(criteria)
search_orders(criteria)
search_employees(criteria)
search_inventory(criteria)
search_audit_events(criteria)
```

The repository must translate approved criteria into database queries.

---

## 55. Generic Query Builder

A generic unrestricted query builder should not be exposed to the Application layer.

The system should prefer endpoint/domain-specific search specifications.

This provides:

* security;
* predictable performance;
* easier testing;
* controlled indexing;
* clearer API contracts.

---

## 56. SQL Injection Protection

Search and filter values must always use parameterized queries.

The application must never concatenate user input into SQL.

The ORM/query builder may generate SQL, but dynamic SQL fragments must remain controlled and whitelisted.

---

## 57. Searchable Fields

Each resource should explicitly define searchable fields.

Example:

```text
Product:
- name
- code

Employee:
- name
- employee_code

Order:
- order_number
- order_uuid
```

The system must not automatically make every database column searchable.

---

## 58. Hidden Fields

Fields excluded from API visibility must not become indirectly searchable.

For example, if an employee cannot see a confidential field, the system must not allow:

```text
search=confidential_value
```

to reveal whether it exists.

---

## 59. Archived Data

Archived records may require separate filtering.

Example:

```text
active=true
```

must not accidentally include archived Products.

Default list behavior should normally exclude archived data unless the endpoint explicitly supports historical/archived access.

---

## 60. Deleted Data

Soft-deleted or lifecycle-controlled records must follow lifecycle rules.

Search must not resurrect deleted Business data.

Deleted records may remain available only to controlled lifecycle/recovery processes where permitted.

---

## 61. Subscription State

Search availability depends on Business lifecycle.

In read-only subscription state:

* read/search operations may remain available;
* modifying operations remain blocked.

After permanent deletion:

* Business data must no longer be available through ordinary search APIs.

---

## 62. Permission-Aware Search

Search results must reflect the employee's actual permissions.

Example:

```text
Employee:
inventory.view = allowed
recipe.view = denied
```

Inventory search may return Products but must not expose restricted Recipe information.

---

## 63. Search and Permission Changes

Permission changes must take effect according to the authorization/cache propagation rules.

Cached search results must not allow an employee to continue viewing data after access is revoked beyond the defined security SLO.

---

## 64. Search Cache

Search results may be cached only when:

* data is safe to cache;
* Business/Branch scope is included;
* authorization context is included where required;
* invalidation/TTL is defined.

Caching must not become an authorization bypass.

---

## 65. POS Search Cache

POS Product search is a good candidate for short-lived local/distributed caching.

Cache may include:

* active menu;
* effective price;
* Product reference data;
* Branch availability.

Final transactional validation remains authoritative.

---

## 66. Audit Search Cache

Audit search should generally avoid long-lived caching because:

* access is sensitive;
* data may change;
* permissions may change;
* audit integrity is important.

If cached, the cache must be short-lived and authorization-aware.

---

## 67. Search Cache Failure

If Redis or another cache fails:

```text
Cache failure
    ↓
Database query
    ↓
Correct result
```

Performance may degrade.

Correctness and authorization must remain intact.

---

## 68. Database Index Strategy

Indexes must be designed from actual query patterns.

Common examples:

```text
business_id
business_id + branch_id
business_id + status
business_id + created_at
business_id + branch_id + created_at
business_id + entity_id
business_id + operation_id
```

Exact indexes must be determined from workload and query plans.

---

## 69. Composite Index Ordering

Composite indexes should generally place highly selective and commonly filtered scope columns first where appropriate.

Example:

```text
(business_id, branch_id, created_at)
```

may support:

```text
Business
+
Branch
+
Date range
```

The correct order must be validated through PostgreSQL query plans.

---

## 70. Partial Indexes

Partial indexes may be used for frequently queried states.

Example:

```text
WHERE active = true
```

This can be useful for POS menu queries when the inactive population is large.

Partial indexes must be introduced only when workload justifies them.

---

## 71. Covering Indexes

`INCLUDE` columns may be used where they significantly reduce table access for high-frequency read queries.

The system must avoid excessive index width.

---

## 72. Text Search Indexes

For large-scale partial text search, PostgreSQL trigram indexes may be used where justified.

Example conceptual pattern:

```text
GIN/GiST trigram index
```

Full-text search may use PostgreSQL text-search indexes.

The chosen strategy must be based on measured query performance and language requirements.

---

## 73. Query Plan Validation

Important search queries should be validated using:

```text
EXPLAIN
EXPLAIN ANALYZE
```

Testing should verify:

* expected index usage;
* acceptable row estimates;
* no unnecessary sequential scans;
* bounded execution time.

Production query plans should be monitored for regressions.

---

## 74. Search Performance Budgets

Initial targets:

| Search Type                   |         Target |
| ----------------------------- | -------------: |
| POS Product search            |    p95 ≤150 ms |
| Normal list/filter query      |    p95 ≤300 ms |
| Normal detail/history query   |    p95 ≤300 ms |
| Audit search                  |    p95 ≤500 ms |
| Complex administrative search |    p95 ≤800 ms |
| Search authorization overhead |    p95 ≤100 ms |
| Cursor pagination             |    p95 ≤300 ms |
| Search API error rate         |          <0.1% |
| Core search availability      | ≥99.9% monthly |

These are initial targets and must be validated with realistic datasets.

---

## 75. Search Load

Load testing must include realistic data volumes.

Examples:

```text
Business:
1–10 Branches initially

Products:
thousands

Orders:
hundreds of thousands+

Inventory Transactions:
millions possible

Audit Events:
millions possible
```

The system must be designed so that data growth does not automatically degrade POS operations.

---

## 76. Search and POS Priority

Search workloads must not starve critical transactions.

Priority:

```text
1. Payment
2. Cash
3. Inventory transaction
4. Order acceptance
5. POS Product search
6. Synchronization
7. Administrative search
8. Reports
9. Large exports
```

Heavy historical search should use controlled resources.

---

## 77. Connection Pool Protection

Search endpoints must respect database connection pool limits.

A large number of simultaneous search requests must not exhaust the pool and block critical POS operations.

Where necessary:

* separate worker pools;
* query timeouts;
* concurrency limits;
* queueing.

---

## 78. Query Timeout

Interactive search queries must have bounded database execution time.

A query that exceeds the allowed time should fail predictably rather than consume resources indefinitely.

The timeout should be endpoint-specific and configurable.

---

## 79. Expensive Search

Expensive operations include:

* broad audit search;
* large date-range history;
* complex text search;
* cross-Branch aggregation;
* large report preparation;
* XLSX export.

These should move to background processing when they exceed interactive performance limits.

---

## 80. Search and Reporting

Interactive search and reporting queries must remain separate concerns.

Reports may use:

* dedicated projections;
* optimized SQL;
* background jobs;
* report snapshots.

The normal search API must not become a reporting engine.

---

## 81. Export

Large filtered datasets must not be returned synchronously merely because the user requested an export.

Correct flow:

```text
Search Criteria
    ↓
Authorization
    ↓
Export Job
    ↓
Background Query
    ↓
XLSX Generation
    ↓
Protected File
```

The original search/filter criteria must be stored with the export job.

---

## 82. Export Scope

Export jobs must capture:

* Business;
* Branch scope;
* employee;
* filters;
* sorting;
* report/version context;
* creation time;
* job UUID.

If permissions change before execution, the job must revalidate authorization.

---

## 83. Search Snapshot

For sensitive or long-running exports, the query should use a deterministic data/report snapshot where required.

This prevents the exported file from silently mixing inconsistent states.

---

## 84. Background Search

Background search/query jobs must have:

* job UUID;
* Business scope;
* Branch scope;
* actor;
* filters;
* retry policy;
* timeout;
* result status.

A background job must not bypass ordinary authorization.

---

## 85. Search Errors

Search errors are classified as:

```text
VALIDATION_ERROR
AUTHORIZATION_ERROR
NOT_FOUND
CONFLICT
QUERY_TIMEOUT
TEMPORARY_DATABASE_ERROR
SEARCH_UNAVAILABLE
```

Unknown filter fields should return validation errors.

Unauthorized access should not be converted into a successful unrestricted search.

---

## 86. Search Observability

The backend should measure:

* request latency;
* query latency;
* rows scanned;
* rows returned;
* database execution time;
* cache hit/miss;
* timeout count;
* error rate;
* pagination depth;
* query frequency;
* slow query patterns.

Sensitive search terms should not automatically be written into logs.

---

## 87. Slow Query Monitoring

Slow queries must be identifiable by:

* endpoint;
* resource;
* filter class;
* query fingerprint;
* execution time.

Raw sensitive search values should be excluded from telemetry.

---

## 88. Query Fingerprinting

Monitoring should prefer normalized query fingerprints rather than storing full user-provided search strings.

Example:

```text
product_search_by_name
order_search_by_number
audit_search_by_event_and_date
```

This improves privacy and makes performance aggregation easier.

---

## 89. Search Audit

Not every search operation needs a business audit event.

However, sensitive operations may require audit.

Examples:

* audit export;
* financial history export;
* security history access;
* privileged cross-Branch investigation.

Routine Product search should not create a durable audit record for every keystroke.

---

## 90. Search Rate Limiting

Search APIs may require rate limits to prevent:

* accidental overload;
* automated scraping;
* abuse;
* expensive-query attacks.

Limits must be designed so normal POS usage remains unaffected.

---

## 91. Search Abuse Protection

The backend should protect against:

* extremely long search strings;
* repeated expensive searches;
* pathological wildcard patterns;
* deep pagination;
* excessive date ranges;
* repeated export jobs.

The system should reject or defer abusive workloads.

---

## 92. Deep Pagination

Deep offset pagination should be limited.

Example:

```text
page=50000
```

on a large table should not be allowed to consume large database resources.

Cursor pagination should be preferred for large datasets.

---

## 93. Search Result Limits

Every endpoint must define:

* default page size;
* maximum page size;
* maximum result count for synchronous requests;
* maximum date range where applicable;
* query timeout.

These values must be configurable.

---

## 94. Empty Search

An empty text search must have explicit behavior.

For example:

```text
Product search with empty text
```

may return the first page of active Products according to default sorting.

For expensive resources such as Audit, empty search may require additional filters such as a date range.

---

## 95. Search Term Length

Very short search terms may create inefficient queries.

The endpoint may define minimum lengths for partial text search.

Example:

```text
"b" → may use prefix/reference search only
"bu" → allowed
"burger" → normal search
```

Exact identifier searches remain possible even when text minimum length is not met.

---

## 96. Unicode and Uzbek Text

The system must correctly support Uzbek and other Unicode text.

Search behavior should account for:

* `oʻ`;
* `gʻ`;
* apostrophe variants;
* uppercase/lowercase;
* Unicode normalization.

If normalization is implemented, it must be tested against actual Product and employee names.

---

## 97. Search Language Strategy

The initial system should prefer simple normalized text search.

Advanced linguistic stemming or multilingual full-text search should be introduced only when actual requirements justify it.

The architecture must allow future enhancement without requiring redesign of the entire API.

---

## 98. Search and Archived Products

Product search should distinguish:

```text
ACTIVE
INACTIVE
ARCHIVED
```

Default POS search should return only operationally sellable Products.

Administrative search may optionally include inactive/archived Products according to permission.

---

## 99. Search and Recipe Visibility

A Product may appear in search even when its Recipe is restricted.

The backend must return only the Product information the employee is authorized to see.

Recipe search remains separately permission-controlled.

---

## 100. Search and Inventory Availability

Search result availability must not be confused with transactional stock authority.

For example:

```text
Product search → available=true
```

does not guarantee that an Order can be accepted later.

Order acceptance performs authoritative inventory validation.

---

## 101. Search and Price

Displayed Product price is a configuration/read concern.

The authoritative price used for an Order must be resolved by the Order operation.

Search result price must not be trusted as the final financial value.

---

## 102. Search and Offline Mode

Offline POS search may use local trusted-device configuration.

The local search index/cache contains:

* last valid Product data;
* effective menu;
* effective pricing;
* local availability information.

Offline search must not imply server authority.

---

## 103. Offline Search Updates

After synchronization:

```text
Transactions
    ↓
Configuration
    ↓
Local Search State
```

Transaction synchronization takes priority over configuration synchronization.

Stale local search data must not rewrite historical offline Order prices.

---

## 104. Search and Synchronization Conflicts

A search index/cache conflict must not change authoritative Business state.

The server remains authoritative after synchronization.

If local search data is stale:

* refresh configuration;
* invalidate cache;
* rebuild local index where necessary.

---

## 105. Search Consistency

Search results are generally read models and may be eventually consistent for non-critical data.

Examples:

* dashboard counts;
* search cache;
* notification status.

Critical operations remain authoritative against PostgreSQL.

---

## 106. Search and Cache Invalidation

When Product/menu/pricing configuration changes:

```text
Commit
  ↓
Invalidate relevant cache
  ↓
Refresh on next read
```

Cache invalidation must include:

* Business;
* Branch;
* configuration version.

---

## 107. Search Versioning

Search cache/index data may include configuration or schema version.

Example:

```text
search_version = 42
```

Old versions must not accidentally be treated as current authoritative configuration.

---

## 108. Search Recovery

After cache restart or search index rebuild:

1. PostgreSQL remains authoritative.
2. Search cache/index may be empty.
3. Queries fall back to authoritative data.
4. Cache/index is rebuilt gradually.
5. POS operation continues.

Search recovery must not require manual database repair.

---

## 109. Testing

Testing must include:

### Unit Tests

* search specification;
* filter validation;
* sort validation;
* pagination;
* cursor encoding;
* date conversion;
* normalization.

### Integration Tests

* PostgreSQL search;
* index usage;
* Business isolation;
* Branch isolation;
* permission filtering;
* pagination;
* concurrent changes.

### Security Tests

* cross-Business query;
* cross-Branch query;
* unauthorized field filtering;
* hidden-field probing;
* search injection;
* export authorization.

### Performance Tests

* large Product search;
* large Order search;
* large audit search;
* deep pagination;
* concurrent POS/search load;
* cache failure.

---

## 110. Performance Testing Dataset

Performance tests should use realistic datasets.

Minimum test scenarios should include:

```text
10 Branches
10,000+ Products
1,000,000+ Orders
5,000,000+ Inventory Transactions
5,000,000+ Audit Events
```

Exact production scale may exceed these values.

The purpose is to ensure search architecture remains stable as data grows.

---

## 111. Query Regression Testing

Important queries should have baseline measurements.

A schema/index change must verify:

* latency;
* query plan;
* row estimates;
* database CPU;
* database I/O;
* connection usage.

A query regression that affects POS-critical resources requires review before deployment.

---

## 112. Database Maintenance

Large searchable tables require operational maintenance.

Examples:

* VACUUM;
* ANALYZE;
* index monitoring;
* bloat monitoring;
* partition maintenance where applicable.

Database maintenance must be planned so it does not unnecessarily impact POS operations.

---

## 113. Search and Read Replicas

Read replicas may be introduced in the future.

However, they must not be used for operations requiring immediate authoritative state.

Examples that should remain authoritative:

* Order acceptance validation;
* payment;
* refund;
* cash;
* inventory deduction;
* permission-sensitive decisions.

A replica may serve suitable read-only search after acceptable replication lag is established.

---

## 114. Replica Lag

If read replicas are introduced, the system must monitor replication lag.

Search requiring fresh state must fall back to the primary database when necessary.

The system must never present stale replica data as authoritative financial state.

---

## 115. Search Service Separation

A separate search engine is not required initially.

PostgreSQL should remain the primary search/query engine.

A dedicated search engine may be introduced later only if:

* PostgreSQL search is proven insufficient;
* workload justifies operational complexity;
* synchronization and consistency can be controlled;
* Business/Branch isolation can be preserved.

---

## 116. Future Search Engine

If a dedicated search engine is introduced:

```text
PostgreSQL
   ↓
Outbox / Change Events
   ↓
Search Index
```

PostgreSQL remains authoritative.

The search engine is a derived read model.

Index rebuild must always be possible from authoritative data.

---

## 117. Search Index Rebuild

A search index must be rebuildable.

The rebuild process should:

1. identify scope;
2. read authoritative data;
3. build in bounded batches;
4. validate counts/checksums where appropriate;
5. switch version;
6. remove obsolete index only after validation.

A failed rebuild must not corrupt authoritative data.

---

## 118. Search Security

Search infrastructure must inherit the same security principles as the backend:

* least privilege;
* Business isolation;
* Branch isolation;
* encrypted transport where applicable;
* secret protection;
* restricted administrative access;
* audit for sensitive operations.

Search infrastructure must not become a data-exfiltration path.

---

## 119. Search and Privacy

Search logs should avoid storing:

* passwords;
* tokens;
* unnecessary personal data;
* sensitive financial values;
* full confidential notes.

If search terms themselves may contain sensitive data, telemetry should use hashes, fingerprints or redacted representations where appropriate.

---

## 120. System Invariants

The following invariants apply to Search and Filtering:

1. Every Business-scoped search is restricted to the authenticated Business.
2. Client-provided Business UUID cannot override authoritative Business context.
3. Branch filters are validated against Business ownership.
4. Branch filters are validated against employee permissions.
5. Unauthorized Branch data cannot appear through search.
6. Search never expands employee permissions.
7. Subscription restrictions remain enforced.
8. Search cannot access permanently deleted Business data.
9. Archived data is not included by default unless explicitly requested.
10. Hidden fields cannot be exposed through search filters.
11. Authentication secrets are never searchable.
12. Passwords are never searchable.
13. Tokens are never searchable.
14. Search input has a maximum length.
15. Search filters are whitelisted.
16. Sort fields are whitelisted.
17. Raw SQL fragments are never accepted from clients.
18. Search values use parameterized queries.
19. Search results are paginated.
20. Page size has a server-enforced maximum.
21. Deep pagination is controlled.
22. Cursor values are opaque.
23. Cursor queries are tied to their original query definition.
24. Search ordering is deterministic.
25. Non-unique sorts have a stable tie-breaker.
26. Every list endpoint has a defined default sort.
27. Authorization is applied before pagination.
28. Business isolation is applied before pagination.
29. Branch isolation is applied before pagination.
30. Search projections return only required fields.
31. N+1 queries are avoided.
32. Search does not load unrelated large objects unnecessarily.
33. Product search does not load complete historical state.
34. POS search remains lightweight.
35. POS search does not perform expensive historical queries.
36. Search result price is not authoritative for financial transaction creation.
37. Search result inventory availability is not authoritative for Order acceptance.
38. Final Order validation uses authoritative state.
39. Audit search requires audit permission.
40. History search requires history permission where applicable.
41. Audit search respects Business scope.
42. Audit search respects Branch scope.
43. Sensitive audit data is not exposed to unauthorized users.
44. Export authorization is revalidated at job execution.
45. Export operations are auditable where required.
46. Large exports are processed asynchronously.
47. Large historical queries are bounded.
48. Expensive search does not block core POS transactions.
49. Database connection pools are protected from search overload.
50. Search queries have bounded execution time.
51. Pathological search patterns are rejected or controlled.
52. Search rate limits may be applied.
53. Search cache is never authoritative.
54. Search cache cannot bypass authorization.
55. Cache keys include Business scope where applicable.
56. Branch scope is included in cache identity where applicable.
57. Cache invalidation follows configuration changes.
58. Cache failure does not break correctness.
59. Offline search uses only locally authorized configuration.
60. Offline search does not claim server authority.
61. Offline transaction history is preserved during configuration refresh.
62. Transaction synchronization takes priority over configuration synchronization.
63. PostgreSQL remains authoritative.
64. Search indexes are derived data.
65. Search index can be rebuilt from authoritative data.
66. Search index failure does not corrupt PostgreSQL.
67. Dedicated search infrastructure is optional.
68. Read replicas are not authoritative for critical financial decisions.
69. Replica lag is monitored when replicas are used.
70. Current Business timezone is used for date-only filtering.
71. Database timestamps remain authoritative in UTC.
72. Date ranges use explicit inclusive/exclusive boundaries.
73. Unknown status filters return validation errors.
74. Invalid filter fields return validation errors.
75. Invalid sort fields return validation errors.
76. Search APIs do not accept arbitrary boolean expressions.
77. Search APIs do not expose arbitrary database columns.
78. Search result visibility follows employee permissions.
79. Recipe search remains permission-controlled.
80. Historical pricing is queried through historical/version models.
81. Historical Order prices are not recalculated from current Product prices.
82. Current inventory quantity is not reconstructed from search results.
83. Search does not create business side effects.
84. Routine Product search does not create durable audit records per keystroke.
85. Sensitive search/export operations may be audited.
86. Search telemetry avoids unnecessary sensitive values.
87. Query fingerprints may be used instead of raw search terms for monitoring.
88. Search performance is measured by endpoint/query class.
89. Slow query regressions are observable.
90. Search changes must not silently degrade POS latency.
91. Index changes are validated through query plans.
92. Over-indexing is avoided.
93. Database maintenance includes searchable-table maintenance.
94. Search result ordering remains deterministic during concurrent writes.
95. Cursor pagination remains consistent with its query definition.
96. Background search jobs retain Business and Branch scope.
97. Background search jobs retain actor context where applicable.
98. Background jobs cannot bypass authorization.
99. Search architecture must scale without weakening tenant isolation.
100. Search optimization must never weaken correctness, authorization or historical integrity.

---

## 121. Recommended Backend Structure

```text
app/
├── application/
│   ├── search/
│   │   ├── queries/
│   │   ├── specifications/
│   │   ├── pagination/
│   │   ├── sorting/
│   │   └── services/
│   ├── products/
│   ├── orders/
│   ├── inventory/
│   ├── audit/
│   └── history/
│
├── domain/
│   └── ...
│
├── infrastructure/
│   ├── database/
│   │   ├── repositories/
│   │   ├── query/
│   │   └── indexes/
│   ├── cache/
│   └── search/
│       ├── postgres/
│       └── indexing/
│
├── reporting/
│   ├── queries/
│   └── exports/
│
├── background/
│   ├── search/
│   └── exports/
│
└── shared/
    ├── pagination/
    ├── filtering/
    ├── sorting/
    └── identifiers/
```

The exact directory structure may evolve, but search/query responsibilities must remain separated from domain business logic.

---

## 122. API Contract Principles

Search/list endpoints should use a consistent structure.

Example conceptual request:

```text
GET /products
    ?search=burger
    &branch_id=...
    &active=true
    &sort=name
    &limit=25
    &cursor=...
```

Example conceptual response:

```text
{
  "items": [],
  "pagination": {
    "next_cursor": "...",
    "has_more": true
  }
}
```

The exact API format belongs to:

`18_Backend_API_Design_and_Contract_Architecture.md`.

This document defines the search behavior behind those contracts.

---

## 123. Relationship With Other Backend Documents

This document depends on and extends:

* `01_Backend_Architecture.md`
* `02_Backend_Project_Structure.md`
* `05_Repository_and_Data_Access.md`
* `06_Authentication_and_Authorization.md`
* `07_Transaction_Management.md`
* `10_Notifications_and_External_Integrations.md`
* `14_Backend_Caching_and_Performance_Architecture.md`
* `16_Backend_Security_Hardening_and_Application_Security.md`
* `19_Backend_Deployment_and_Runtime_Architecture.md`
* `22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `23_Backend_Audit_and_History_Architecture.md`

It also relates to:

* Database indexes;
* Database query strategy;
* Order data model;
* Product data model;
* Inventory data model;
* Audit/history data model;
* Report architecture;
* Offline synchronization.

---

## 124. Related Database Documents

Relevant database documents include:

* `docs/05_Database/01_Database_Overview.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

---

## 125. Related System Analysis Documents

Relevant System Analysis documents include:

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

Exact filenames must remain aligned with the repository's final structure.

---

## 126. Status

**Backend Architecture:** In progress.

**Document Status:** Proposed.

**Current Document:** `24_Backend_Search_and_Filtering_Architecture.md`

**Previous Document:** `23_Backend_Audit_and_History_Architecture.md`

**Next Document:** `25_Backend_Queue_and_Worker_Architecture.md`

