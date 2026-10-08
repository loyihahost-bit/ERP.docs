# API Pagination, Search, Filtering and Sorting

**Document ID:** API-11
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines pagination, search, filtering and sorting behavior for the FastFood ERP API.

The primary objectives are:

* prevent unbounded API responses;
* provide predictable list behavior;
* support large Business and Branch datasets;
* preserve Business and Branch isolation;
* provide stable pagination under concurrent changes;
* support efficient search and filtering;
* prevent unsafe query construction;
* maintain predictable API performance;
* support POS and administrative workloads without unnecessary database load.

The API must allow clients to retrieve large datasets incrementally without requiring the server to load or return the entire dataset at once.

---

# 2. Scope

This document covers:

* list endpoint behavior;
* pagination;
* cursor pagination;
* offset pagination;
* page size limits;
* deterministic ordering;
* filtering;
* date and time filters;
* status filters;
* Business and Branch filters;
* search;
* sorting;
* query parameter validation;
* query normalization;
* large dataset behavior;
* database query strategy;
* indexes;
* concurrent data changes;
* pagination consistency;
* security;
* information exposure;
* API performance;
* rate limiting implications;
* export boundaries;
* asynchronous large-data operations;
* observability;
* API invariants.

This document does not redefine:

* general request validation;
* general response contracts;
* authorization;
* error response architecture;
* CRUD semantics.

---

# 3. Core Principles

The API follows these principles:

1. List endpoints must never return unbounded datasets.
2. Pagination is mandatory for potentially large collections.
3. Cursor pagination is the preferred strategy for large or frequently changing datasets.
4. Offset pagination may be used for small administrative collections.
5. Every paginated result must have deterministic ordering.
6. Client-controlled sorting must use an allowlist.
7. Client-controlled filtering must use an allowlist.
8. Search must respect Business and Branch scope.
9. Search must not bypass authorization.
10. Pagination must not bypass authorization.
11. Query parameters must never become raw SQL.
12. Page size must be bounded server-side.
13. Large exports should use asynchronous processing rather than huge API responses.
14. Database indexes must support frequently used filters and ordering.
15. Pagination must remain compatible with concurrent inserts and updates.
16. API performance must remain within defined SLOs.
17. Query complexity must be bounded.
18. Internal database structure must not be exposed through API query parameters.

---

# 4. Collection Endpoints

Collection endpoints return multiple resources.

Examples:

```text
GET /api/v1/businesses
GET /api/v1/branches
GET /api/v1/employees
GET /api/v1/products
GET /api/v1/orders
GET /api/v1/inventory/transactions
GET /api/v1/notifications
GET /api/v1/audit-events
GET /api/v1/reports
```

The server determines whether pagination is required based on the resource characteristics.

For ERP operational collections, pagination should be the default.

---

# 5. Pagination Requirement

Potentially large collections must support pagination.

Examples include:

* Orders;
* Order Items where exposed as collections;
* Employees;
* Products;
* Inventory Transactions;
* Payments;
* Refunds;
* Cash Sessions;
* Audit Events;
* Notifications;
* Reports;
* Synchronization records.

The API must not return an unlimited number of rows merely because the client omitted pagination parameters.

---

# 6. Default Page Size

The initial API strategy is:

```text
Default page size: 50
Maximum page size: 100
```

The exact values may be configuration-driven.

A client requesting:

```text
limit=1000
```

must not receive 1,000 records if the configured maximum is 100.

The server should either:

* reject the request; or
* safely clamp it according to the API contract.

The behavior must be consistent.

---

# 7. Maximum Page Size

Every paginated endpoint must define a maximum page size.

The maximum exists to protect:

* PostgreSQL;
* application memory;
* network bandwidth;
* serialization;
* frontend memory;
* API latency.

Different resource classes may use different limits if justified.

For example:

```text
POS menu: optimized bounded payload
Orders: 100
Audit events: 100
Notifications: 100
```

---

# 8. Cursor Pagination

Cursor pagination is the preferred strategy for:

* large collections;
* high-volume Orders;
* Inventory Transactions;
* Audit Events;
* synchronization records;
* frequently changing collections.

Example:

```text
GET /api/v1/orders?limit=50&cursor=eyJ...
```

Response:

```json
{
  "data": [],
  "pagination": {
    "next_cursor": "eyJ...",
    "has_more": true
  }
}
```

---

# 9. Cursor Purpose

A cursor represents a position in a collection.

It must not expose internal database implementation details unnecessarily.

The cursor may contain encoded information such as:

```text
last ordering value
resource identifier
filter context
sort definition
```

The exact cursor representation is an API implementation detail.

---

# 10. Cursor Opaqueness

Clients must treat cursors as opaque values.

Clients must not:

* decode them;
* modify them;
* construct them manually;
* assume database IDs are encoded directly.

The server remains responsible for cursor interpretation.

---

# 11. Cursor Integrity

Cursors should be protected against tampering.

Possible mechanisms include:

* signed cursors;
* authenticated encoding;
* server-side cursor state where justified.

A modified or invalid cursor must be rejected safely.

Cursor validation must not expose internal implementation details.

---

# 12. Cursor and Query Consistency

A cursor must be associated with the relevant query context.

For example:

```text
Initial:
GET /orders?status=PAID&sort=-created_at

Next:
GET /orders?status=PAID&sort=-created_at&cursor=...
```

The cursor must not silently be reused for:

```text
GET /orders?status=CANCELLED&cursor=...
```

If the query context is incompatible, the server should return a controlled validation or cursor conflict error.

---

# 13. Cursor and Sorting

A cursor must be generated from the actual ordering definition.

If sorting is:

```text
created_at DESC
id DESC
```

the cursor must preserve enough information to continue from that position.

The server must not use a cursor that assumes a different ordering.

---

# 14. Stable Ordering

Every paginated endpoint must have deterministic ordering.

A timestamp alone may not be sufficient.

Preferred:

```text
created_at DESC
id DESC
```

The unique identifier acts as a tie-breaker.

This prevents records with identical timestamps from being unpredictably skipped or duplicated.

---

# 15. Cursor Ordering Example

Suppose:

```text
Order A → created_at 10:00:00 → ID A
Order B → created_at 10:00:00 → ID B
Order C → created_at 09:59:59 → ID C
```

The ordering should remain deterministic:

```text
A
B
C
```

The cursor must preserve both:

```text
created_at
id
```

to continue correctly.

---

# 16. Offset Pagination

Offset pagination may be used for:

* small administrative lists;
* low-volume collections;
* UI pages where direct page navigation is important;
* collections where dataset size is known to remain bounded.

Example:

```text
GET /api/v1/employees?limit=50&offset=100
```

Offset pagination should not be the default for high-volume transactional collections.

---

# 17. Offset Limit

Offset pagination must still enforce:

* maximum page size;
* maximum practical offset where necessary;
* deterministic sorting.

The API may reject excessively deep offsets when database performance becomes unacceptable.

---

# 18. Offset Pagination and Concurrent Changes

Offset pagination can become unstable when records are inserted or deleted between requests.

Example:

```text
Request 1:
offset=0

New record inserted

Request 2:
offset=50
```

The client may see:

* duplicate records;
* skipped records.

For frequently changing large datasets, cursor pagination is preferred.

---

# 19. Cursor Pagination and Concurrent Changes

Cursor pagination is more stable under concurrent inserts.

If a new Order is created after the cursor position:

```text
Existing page
    ↓
Cursor
    ↓
New Order
```

the new Order does not unexpectedly shift already-consumed results.

The exact consistency behavior depends on the ordering field and query semantics.

---

# 20. Pagination Consistency Model

The API does not guarantee a global immutable snapshot for every multi-page collection.

Instead, it provides:

* deterministic ordering;
* stable cursor progression;
* bounded page results;
* authorization at request time.

If a client requires an immutable historical dataset, it should use an appropriate report or versioned snapshot rather than repeatedly paging a live transactional table.

---

# 21. Report Snapshot Boundary

Reports requiring historical consistency should use:

```text
Report Version
```

rather than relying on a live paginated transactional collection.

Example:

```text
Live Orders
    ≠
Immutable Report Version
```

Pagination is therefore not a replacement for report versioning.

---

# 22. Filtering

Filtering allows clients to restrict collection results.

Examples:

```text
GET /orders?status=PAID
GET /orders?branch_id=...
GET /products?active=true
GET /employees?status=ACTIVE
```

Supported filters must be explicitly defined per endpoint.

Unknown filters must not be silently interpreted.

---

# 23. Filter Allowlist

Each endpoint must define an allowlist of filterable fields.

Example:

```text
Orders:
status
branch_id
cash_session_id
created_from
created_to
payment_status

Employees:
status
branch_id
role
```

The API must not accept arbitrary database column names.

---

# 24. Filter Field Mapping

Public API filter names should map to application/query fields.

Example:

```text
created_from
    ↓
Order.created_at >= value
```

The client must not provide:

```text
table.column
```

or SQL fragments.

---

# 25. Filter Operators

The API may support a controlled set of operators.

Examples:

```text
=
!=
>
>=
<
<=
IN
```

The exact operators depend on the resource.

Operator support must be explicit.

---

# 26. Operator Safety

The API must never accept raw expressions such as:

```text
WHERE ...
ORDER BY ...
```

from clients.

Filtering must be converted into structured query criteria.

This prevents:

* SQL injection;
* uncontrolled query complexity;
* accidental internal field exposure.

---

# 27. Boolean Filters

Boolean fields should use explicit values.

Example:

```text
active=true
```

Invalid values should be rejected rather than silently converted.

Examples:

```text
active=yes
active=random
```

must not produce ambiguous behavior.

---

# 28. Enum Filters

Enum filters must use supported values.

Example:

```text
status=PAID
```

If the supported states are:

```text
DRAFT
OPEN
ACCEPTED
PAID
CANCELLED
```

an unknown state must produce a validation error.

The API must not silently ignore invalid enum values.

---

# 29. Multi-Value Filters

Where useful, an endpoint may support multiple values.

Example:

```text
status=PAID,CANCELLED
```

or repeated parameters:

```text
status=PAID&status=CANCELLED
```

The selected representation must be standardized across the API.

---

# 30. Date Range Filtering

Date/time filters should support explicit ranges.

Example:

```text
GET /orders?created_from=2026-10-01T00:00:00Z
            &created_to=2026-10-07T00:00:00Z
```

The API must define whether range boundaries are:

* inclusive;
* exclusive;
* half-open.

For timestamp ranges, half-open intervals are generally preferred:

```text
[start, end)
```

---

# 31. Date-Only Filtering

Business concepts based on calendar dates must not accidentally shift because of timezone conversion.

Examples:

* attendance date;
* payroll period;
* report date.

Date-only values must be interpreted according to the Business/Branch timezone rules.

---

# 32. Timezone Handling

API timestamps use the defined API time format.

The server must distinguish:

* UTC timestamps;
* Business timezone;
* Branch timezone;
* date-only business concepts.

Filtering must not silently interpret a Branch-local date as UTC when the business rule requires local calendar semantics.

---

# 33. Business Scope Filtering

Business scope must not be client-controlled.

Example:

```text
GET /orders?business_id=B
```

does not grant access to Business B.

The server derives or validates Business context from authenticated authorization state.

Business filters may be used for authorized platform-level operations, but they remain server-authorized.

---

# 34. Branch Scope Filtering

Branch filters must be authorization-aware.

Example:

```text
GET /orders?branch_id=BRANCH-A
```

must verify that the actor has access to Branch A.

A user with only Branch B access cannot retrieve Branch A data by changing the query parameter.

---

# 35. Multi-Branch Users

An employee may have access to:

```text
Branch A
Branch C
Branch D
```

The API may allow filtering:

```text
branch_id=A
```

or:

```text
branch_id=C
```

depending on permissions.

If no Branch filter is provided, the endpoint must use the authorized default scope defined by the application context.

---

# 36. Branch Scope and Search

Search must always execute inside the authorized Business/Branch scope.

Unsafe:

```text
Search all Products
   ↓
Filter after retrieval
```

Safe:

```text
Authorized Business/Branch scope
   ↓
Search query
   ↓
Results
```

Authorization scope must be part of the database query boundary.

---

# 37. Search

Search is intended for human-oriented retrieval of resources.

Examples:

```text
GET /products?search=burger
GET /employees?search=ali
GET /orders?search=100245
```

Search behavior must be explicitly defined per resource.

---

# 38. Search Fields

Each resource must define searchable fields.

Example:

### Product

* name;
* product code;
* optionally normalized search name.

### Employee

* display name;
* employee code.

### Order

* order number;
* controlled reference fields.

Search must not automatically search every database column.

---

# 39. Search Normalization

Search input may be normalized for usability.

Possible normalization includes:

* trimming surrounding whitespace;
* Unicode normalization;
* case normalization;
* controlled punctuation normalization.

The normalization strategy must be deterministic.

---

# 40. Search Length Limits

Search input must have bounded length.

Example initial policy:

```text
Minimum meaningful search length: implementation-defined
Maximum search length: 100 characters
```

Very large search strings must be rejected or safely truncated according to the API contract.

---

# 41. Empty Search

An empty search parameter should not accidentally trigger an expensive full-text operation.

For example:

```text
search=
```

should be treated consistently.

Possible behavior:

* ignore the search parameter;
* reject it;
* treat it as no search.

The selected behavior must be standardized.

---

# 42. Search Matching

The API may support:

* prefix search;
* substring search;
* exact search;
* full-text search.

The matching strategy depends on resource volume and database capabilities.

The API contract should not expose database-specific search syntax.

---

# 43. Product Search

POS product search is performance-sensitive.

It should prioritize:

* fast response;
* Branch availability;
* active state;
* effective pricing;
* compact response;
* local/cache-assisted reads where appropriate.

POS search should not query historical configuration unnecessarily.

---

# 44. Order Search

Order search may support:

```text
order number
phone reference
date range
status
payment status
```

Search fields containing personal or sensitive information must remain authorization-controlled.

---

# 45. Employee Search

Employee search must respect:

* Business scope;
* Branch scope;
* employee visibility permissions.

The API must not expose sensitive employee fields merely because a matching name exists.

---

# 46. Inventory Search

Inventory search may support:

* product;
* product code;
* warehouse;
* category;
* stock status.

Final stock correctness remains authoritative.

Search results are informational and do not replace transactional inventory validation.

---

# 47. Audit Search

Audit event search must be tightly controlled.

Supported filters may include:

* event type;
* actor;
* Branch;
* resource type;
* resource ID;
* date range;
* result.

Audit search must not expose unauthorized Business history.

---

# 48. Sorting

Clients may request supported sorting.

Example:

```text
GET /orders?sort=-created_at
```

The API must use a predefined sort allowlist.

---

# 49. Sort Allowlist

Example:

```text
Orders:
created_at
updated_at
order_number

Products:
name
created_at
updated_at

Employees:
name
created_at
```

Unsupported sort fields must be rejected.

---

# 50. Sort Direction

The API may support:

```text
field
-field
```

where:

```text
field
```

means ascending and:

```text
-field
```

means descending.

The exact syntax must remain consistent across API endpoints.

---

# 51. Sort Tie-Breaker

Every sort must eventually resolve to a unique deterministic order.

Example:

```text
created_at DESC
id DESC
```

If the client requests:

```text
sort=-created_at
```

the server may internally append:

```text
id DESC
```

as a deterministic tie-breaker.

---

# 52. Sort and Cursor Compatibility

Cursor pagination requires a stable sort definition.

Therefore:

```text
cursor + sort
```

must remain compatible.

Changing sort while reusing a cursor must result in a controlled error.

---

# 53. Default Sort

Every collection endpoint must define a default sort.

Examples:

```text
Orders:
created_at DESC, id DESC

Notifications:
created_at DESC, id DESC

Audit Events:
created_at DESC, id DESC

Products:
name ASC, id ASC
```

The default should reflect operational usefulness and query efficiency.

---

# 54. Null Sorting

If sortable fields can contain null values, the API must define their ordering.

For example:

```text
NULLS LAST
```

The behavior must remain deterministic.

Clients must not need to understand database-specific syntax.

---

# 55. Search + Filter + Sort

These operations must compose predictably.

Example:

```text
GET /orders
    ?status=PAID
    &branch_id=BRANCH-A
    &created_from=...
    &created_to=...
    &search=100245
    &sort=-created_at
    &limit=50
```

Processing conceptually:

```text
Authorization Scope
       ↓
Filters
       ↓
Search
       ↓
Sort
       ↓
Pagination
       ↓
Response
```

The actual query optimizer may choose a different execution strategy.

---

# 56. Query Scope Order

Security scope must be applied as part of the authoritative query.

The logical model is:

```text
Business / Branch Authorization Scope
        ↓
Resource Eligibility
        ↓
Filters
        ↓
Search
        ↓
Sort
        ↓
Pagination
```

The API must never retrieve unauthorized data first and filter it in application memory.

---

# 57. Query Complexity

Each endpoint must define supported query complexity.

The API should avoid allowing combinations that produce unbounded expensive queries.

Examples of controls:

* maximum page size;
* maximum date range;
* limited searchable fields;
* limited filter count;
* limited sort fields;
* maximum search length.

---

# 58. Filter Count

Where necessary, the API may limit the number of simultaneous filter conditions.

This prevents clients from constructing unnecessarily complex queries.

The limit should be based on measured query behavior.

---

# 59. Date Range Limits

Large live-data date ranges may be restricted.

Example:

```text
Orders endpoint:
maximum live query period = implementation-defined
```

For larger historical periods, the client should use:

* reports;
* report versions;
* asynchronous exports.

The exact period limit depends on measured database performance.

---

# 60. Large Dataset Strategy

The API must distinguish:

```text
Interactive Query
```

from:

```text
Large Data Extraction
```

Interactive queries should remain small and fast.

Large extraction should use:

```text
Report / Export Job
```

rather than a huge paginated API loop.

---

# 61. API vs Export

Pagination is intended for application interaction.

It is not the preferred mechanism for exporting millions of records.

For large exports:

```text
POST /reports/{id}/exports
        ↓
202 Accepted
        ↓
Background Job
        ↓
XLSX/File
```

The export architecture defines the exact workflow.

---

# 62. Query Performance

List queries should target:

```text
Normal indexed query p95 ≤ 100 ms
```

Interactive API endpoints should target:

```text
Normal authenticated API p95 ≤ 300 ms
```

Core POS commands should remain:

```text
p95 ≤ 500 ms
```

Pagination/search/filtering must not consume a disproportionate portion of the API latency budget.

---

# 63. Database Index Strategy

Frequently used filters and sort combinations should have appropriate indexes.

Examples:

```text
Orders:
business_id
branch_id
created_at

Orders:
business_id
branch_id
status
created_at

Inventory:
business_id
branch_id
product_id

Notifications:
employee_id
created_at
```

Exact indexes belong to the Database Index Strategy document.

---

# 64. Composite Indexes

Composite indexes should reflect actual query patterns.

Example:

```text
business_id
branch_id
status
created_at
```

may support:

```text
Business
+
Branch
+
Status
+
recent Orders
```

Indexes must be justified by measured or predictable workload.

---

# 65. Index and Sort Alignment

Where possible, query indexes should support both filtering and ordering.

For example:

```text
WHERE business_id = ?
  AND branch_id = ?
ORDER BY created_at DESC, id DESC
```

may benefit from an index aligned with the query pattern.

The final index design belongs to the Database section.

---

# 66. Search Index Strategy

For high-volume search, appropriate database search capabilities may be used.

Potential approaches include:

* B-tree indexes for exact/prefix patterns;
* PostgreSQL text search;
* trigram indexes where justified.

The API remains database-agnostic at the contract level.

The implementation must select the simplest suitable mechanism.

---

# 67. Search Performance

Search performance should have measurable targets.

Initial target for normal indexed search:

```text
p95 ≤ 150 ms
```

POS product search should target:

```text
p95 ≤ 100 ms
```

when using local/cache-assisted configuration where appropriate.

---

# 68. Search Fallback

If an advanced search index is temporarily unavailable, the API must not silently execute an unbounded database scan.

Possible behavior:

* return controlled temporary failure;
* use a safe simpler indexed strategy;
* defer to asynchronous search.

The fallback must remain bounded.

---

# 69. Query Timeout

List/search endpoints must have bounded database query timeouts.

An expensive query must not hold resources indefinitely.

If a query exceeds the allowed execution budget, the API should return a controlled temporary/timeout error according to the error architecture.

---

# 70. Pagination and Caching

Safe read-oriented list results may be cached where appropriate.

Cache keys must include relevant:

```text
Business
Branch
Authorization scope where necessary
Filters
Search
Sort
Cursor
Configuration version where relevant
```

However, high-cardinality arbitrary query caching should be avoided unless justified.

---

# 71. Cache Key Explosion

The system must avoid caching every possible combination of:

```text
search
filter
sort
cursor
```

because this can create excessive cache growth.

Caching should focus on predictable high-value queries.

---

# 72. Authorization and Cached Lists

A cached list must never be returned merely because the cache key matches.

Authorization must remain valid.

The system must not allow:

```text
Employee A
    ↓
cache
    ↓
Employee B receives A's restricted data
```

---

# 73. Pagination and Authorization Changes

If an employee's Branch access changes between page requests, the next request must use current authorization state.

A cursor does not grant permanent access to the underlying dataset.

---

# 74. Cursor and Authorization

A cursor must not be usable to retrieve data outside the current authorization scope.

If the underlying scope is no longer authorized:

```text
request
  ↓
authorization failure
```

The cursor must not override that decision.

---

# 75. Search and Sensitive Data

Search must not become a mechanism for discovering:

* unauthorized Employees;
* unauthorized Customers/contacts;
* hidden Products;
* private configuration;
* financial data;
* audit events.

Search results must contain only authorized fields.

---

# 76. Response Size

Even with pagination, each record should expose only necessary fields.

The API should use dedicated response DTOs/read models rather than serializing complete ORM objects.

This reduces:

* response size;
* serialization cost;
* accidental data exposure.

---

# 77. Field Selection

Generic arbitrary field selection such as:

```text
?fields=*
```

should not be enabled by default.

If field selection is introduced later, it must use an explicit allowlist.

It must never bypass response authorization.

---

# 78. Search Result Ranking

For basic ERP search, deterministic ordering is preferred over opaque relevance ranking unless a dedicated search capability is justified.

For example:

```text
exact product code
    ↓
prefix name
    ↓
other supported match
```

Any ranking rules must be documented and deterministic enough for users.

---

# 79. Exact Match Priority

Where useful, search may prioritize exact matches.

Example:

```text
Search:
burger

Possible:
Burger
Burger Cheese
Burger Double
```

The exact Product name may appear before broader matches.

The behavior must remain stable enough for POS use.

---

# 80. POS Search and Local Data

POS clients may maintain authorized local Product/Menu data.

When offline:

```text
Local authorized dataset
```

may support search.

When online:

```text
Current valid server/configuration state
```

remains authoritative.

The API search contract must remain compatible with local POS behavior.

---

# 81. Search and Offline Synchronization

Search indexes/configuration may be synchronized to trusted devices.

The synchronized data must respect:

* Business scope;
* Branch scope;
* offline authorization;
* configuration version;
* device authorization.

A stale local search result must not create unauthorized server operations.

---

# 82. Search and Configuration Version

For menu/product search, the effective configuration version may be included in the response where useful.

Example:

```json
{
  "configuration_version": 12,
  "data": []
}
```

This helps clients identify stale local state.

---

# 83. Filtering by Configuration State

Configuration resources may expose controlled filters such as:

```text
status=EFFECTIVE
status=APPROVED
```

The API must not expose arbitrary internal configuration states unless they are part of the public contract.

---

# 84. Filtering Historical Data

Historical data may require special filters.

Examples:

```text
created_from
created_to
effective_from
effective_to
version
```

Historical data must remain immutable.

Filtering must not reinterpret historical records using current configuration.

---

# 85. Audit Pagination

Audit events are expected to grow continuously.

Therefore:

* cursor pagination is preferred;
* deterministic chronological ordering is required;
* Business/Branch scope is mandatory;
* date range filtering should be strongly encouraged;
* large historical extraction should use reports/export.

---

# 86. Notification Pagination

Notifications may use cursor pagination.

Typical ordering:

```text
created_at DESC
id DESC
```

The API should support filters such as:

```text
read=true
read=false
```

The unread count may be provided separately through an optimized endpoint rather than loading all notifications.

---

# 87. Employee Pagination

Employee lists may use offset pagination initially if the dataset is small.

However, the API must still define:

* default limit;
* maximum limit;
* stable ordering;
* Branch filtering;
* status filtering;
* search.

The strategy may migrate to cursor pagination without changing the conceptual resource contract if necessary.

---

# 88. Product Pagination

Product collections may require:

* category filter;
* active state;
* Branch availability;
* search;
* sort.

POS product browsing should use optimized responses rather than administrative Product representations.

---

# 89. Order Pagination

Order collections should prefer cursor pagination.

Recommended default:

```text
created_at DESC
id DESC
```

Useful filters:

* Branch;
* Cash Session;
* status;
* payment status;
* order type;
* date range.

The API must avoid loading large Order Item graphs for every list row.

---

# 90. Order List Projection

An Order list response should generally include only fields required for the list.

For example:

```text
Order ID
Order Number
Order Type
Status
Payment Status
Total
Branch
Cashier
Created At
```

Full Order Items should be retrieved through the Order detail endpoint when needed.

---

# 91. Inventory Transaction Pagination

Inventory transaction lists should prefer cursor pagination.

Useful filters:

* Branch;
* Warehouse;
* Product;
* transaction type;
* date range;
* actor.

Inventory transaction history must remain immutable.

---

# 92. Payment Pagination

Payment collections should support bounded pagination.

Useful filters:

* Order;
* Branch;
* payment method;
* status;
* date range.

Payment list queries must not expose unauthorized financial information.

---

# 93. Cash Session Pagination

Cash Session collections may support:

* Branch;
* Cash Register;
* cashier;
* state;
* date range.

Ordering should generally prioritize most recent sessions.

---

# 94. Report Pagination

Reports may be paginated when listing report metadata.

The actual report content should not be returned as an enormous API list.

Large report content should use:

* report versions;
* file exports;
* asynchronous jobs.

---

# 95. API Rate Limiting and Query Complexity

Expensive search/filter combinations may require stricter rate limits.

For example:

```text
Simple Product lookup
→ normal limit

Large Audit search
→ stricter limit
```

Rate limiting must be based on measured resource cost where possible.

---

# 96. Abuse Protection

The API must prevent abusive query patterns such as:

* unlimited page sizes;
* deep offset scanning;
* repeated expensive searches;
* huge date ranges;
* high-frequency audit searches;
* wildcard-like searches without bounds.

Protection must preserve normal POS and administrative workflows.

---

# 97. Query Planning

The backend should monitor query plans for important endpoints.

Potential problems include:

* sequential scans on large transactional tables;
* missing composite indexes;
* inefficient joins;
* unnecessary sorting;
* excessive offset cost;
* high row counts before filtering.

Query optimization belongs to the database architecture, but API contracts must avoid encouraging pathological queries.

---

# 98. Query Result Limits

The API should enforce result limits before serialization.

The application should not retrieve thousands of rows and then truncate them in memory.

The database query itself should remain bounded.

---

# 99. N+1 Prevention

List endpoints must avoid:

```text
1 query for Orders
+
1 query per Order for Cashier
+
1 query per Order for Branch
```

Instead, the repository/query layer should use:

* optimized joins;
* controlled eager loading;
* batch loading;
* dedicated read models.

---

# 100. Query Projection

List queries should retrieve only fields needed for the response.

For example, an Order list should not load:

* complete audit history;
* complete Order Items;
* Recipe history;
* payment history;
* unrelated employee data.

---

# 101. Sorting Restrictions

The API must not support arbitrary expressions such as:

```text
sort=LOWER(name)
sort=random()
sort=(SELECT ...)
```

Only predefined application-level sort fields are allowed.

---

# 102. Filtering Restrictions

The API must not support arbitrary expressions such as:

```text
filter=...
where=...
sql=...
```

The query interface is a controlled application contract.

---

# 103. Search Injection Protection

Search values must be passed as query parameters through parameterized database operations.

The system must never concatenate search input into SQL.

---

# 104. Query Parameter Normalization

The API should normalize:

* whitespace;
* boolean representation;
* enum case where explicitly supported;
* date/time formats;
* numeric formats;
* repeated filter values.

Normalization must not change semantic meaning unexpectedly.

---

# 105. Invalid Query Parameters

Unknown or invalid query parameters should produce a predictable validation error.

Example:

```text
GET /orders?sort=secret_database_column
```

must not silently fall back to an arbitrary default.

This helps clients detect contract mistakes.

---

# 106. Unsupported Filter Combinations

Some filter combinations may be invalid or too expensive.

Example:

```text
audit events
+
unbounded date range
+
complex search
```

The API may reject the combination with a structured validation/business query error.

---

# 107. API Documentation

Each collection endpoint must document:

* supported filters;
* supported search fields;
* supported sorting fields;
* default sort;
* pagination type;
* default page size;
* maximum page size;
* cursor behavior;
* date/time semantics;
* authorization scope;
* query limitations.

Clients must not be expected to infer these rules.

---

# 108. OpenAPI Representation

OpenAPI should describe:

* query parameters;
* allowed enum values;
* pagination parameters;
* response pagination structure;
* cursor type;
* error responses.

Examples should be provided for commonly used filters.

---

# 109. Client Compatibility

Adding a new optional filter should be backward compatible.

Removing an existing filter may be breaking.

Changing the meaning of an existing filter is a breaking semantic change and requires API versioning or an explicit migration strategy.

---

# 110. Pagination Contract Stability

The API must avoid exposing implementation-specific cursor formats.

Cursor internals may change between API versions if the public contract remains:

```text
opaque cursor
```

Clients should only:

```text
receive cursor
→ send cursor back
```

---

# 111. Cursor Expiration

Cursors may expire where necessary.

Reasons include:

* security;
* storage limits;
* query version changes;
* deployment changes;
* excessive age.

If a cursor expires, the client must restart pagination from the first page.

The error must be predictable.

---

# 112. Cursor and Resource Deletion

If a resource is deleted or archived between pages, the next page may naturally omit it.

The API does not guarantee that a live collection remains unchanged across multiple requests.

Immutable report versions should be used where exact historical completeness is required.

---

# 113. Cursor and Updates

If a record's sort field changes after a page has been consumed, it may appear in a different logical position on later requests.

The API must document that live transactional collections are not immutable snapshots.

For exact snapshots, use versioned reporting.

---

# 114. Search Result Stability

Search results may change as underlying data changes.

The API guarantees deterministic ordering for each request but does not guarantee a frozen search result set across multiple pages unless a snapshot/version mechanism is explicitly provided.

---

# 115. Administrative UI Requirements

Administrative frontend screens should use pagination rather than loading entire collections.

Examples:

* Employees;
* Products;
* Orders;
* Inventory;
* Audit;
* Notifications.

The frontend should preserve:

* active filters;
* sort;
* cursor/page state;
* loading state;
* error state.

---

# 116. POS UI Requirements

POS UI should minimize interaction latency.

For Product search:

* debounce user input where appropriate;
* use local authorized data when available;
* use compact API responses;
* avoid unnecessary full collection reloads;
* prioritize exact/product-code matches;
* preserve Branch scope.

The frontend architecture defines the detailed UI behavior.

---

# 117. Backend Read Models

High-volume list endpoints may use dedicated read models.

A read model may contain:

```text
Order Summary
Product Summary
Employee Summary
Inventory Summary
```

This avoids loading complete domain aggregates for list views.

Read models remain derived representations and do not become authoritative business state.

---

# 118. Search and Read Models

Read models may support optimized search/filter queries.

The source of truth remains PostgreSQL transactional state.

If a read model becomes stale, the API must define whether:

* bounded staleness is acceptable;
* the query falls back to authoritative data;
* the endpoint reports temporary unavailability.

Financial correctness must never depend on stale read models.

---

# 119. Eventual Consistency

Eventually consistent search/read models may be used for:

* dashboards;
* non-critical analytics;
* notifications;
* derived insights.

They must not be used as the final authority for:

* payment;
* inventory deduction;
* cash state;
* authorization;
* historical financial state.

---

# 120. Performance Monitoring

The API should monitor:

```text
pagination_request_count
cursor_invalid_count
cursor_expired_count
search_request_count
filter_request_count
sort_request_count
query_timeout_count
deep_offset_count
large_page_rejection_count
```

Metrics should remain low-cardinality.

---

# 121. Query Latency Monitoring

Important measurements include:

* p50;
* p95;
* p99;
* database duration;
* serialization duration;
* response size;
* rows examined where available.

The system should identify endpoints where pagination/search behavior causes regressions.

---

# 122. Query Performance SLOs

Initial targets:

| Operation                          |   Target |
| ---------------------------------- | -------: |
| Normal indexed list query p95      | ≤ 100 ms |
| Normal authenticated list API p95  | ≤ 300 ms |
| Product/POS search p95             | ≤ 100 ms |
| Normal search query p95            | ≤ 150 ms |
| Cursor generation/validation p95   |  ≤ 20 ms |
| Pagination metadata generation p95 |  ≤ 20 ms |
| Normal API p99                     | ≤ 800 ms |

These targets apply to normal operating conditions.

---

# 123. Large Query Failure

If a query exceeds configured resource limits:

```text
Query
 ↓
Timeout / Resource Limit
 ↓
Controlled API Error
```

The API must not allow a single expensive query to consume unlimited database resources.

---

# 124. Background Extraction

If a user requires data beyond interactive API limits:

```text
Large Query
   ↓
Report / Export Job
   ↓
Background Worker
   ↓
File
```

This preserves interactive API performance.

---

# 125. Security and Query Isolation

Every query must preserve:

```text
Business isolation
Branch isolation
Employee visibility
Permission scope
Subscription restrictions
```

Query optimization must never remove required scope predicates.

---

# 126. Security and Search

Search endpoints must not reveal whether an unauthorized resource exists merely through different error behavior where that would create information leakage.

The endpoint should follow the API's established resource enumeration policy.

---

# 127. Security and Sorting

Sorting must not reveal hidden fields.

For example, if salary is not visible to the employee, the API must not allow:

```text
sort=salary
```

merely because the database contains that field.

---

# 128. Security and Filtering

Filtering must not allow users to infer restricted data.

Example:

```text
salary>10000000
```

must not be supported for an actor without salary visibility.

---

# 129. Auditability

Important administrative searches may be logged at the API access level where required by security policy.

Business audit records should remain reserved for meaningful business state changes.

Normal POS Product search should not create business audit records for every query.

---

# 130. Failure Recovery

If the search/index/cache layer fails:

* core business operations must remain correct;
* the API may use a safe fallback;
* expensive unbounded scans are prohibited;
* the failure must be observable.

A search optimization failure must not become a Business data corruption event.

---

# 131. API and Cache Failure

If cached list/search data becomes unavailable:

```text
Cache miss
   ↓
Safe query path
   ↓
PostgreSQL / read model
```

The system must not return another Business's cached data because of an incomplete cache key.

---

# 132. API and Subscription

READ_ONLY Businesses may continue to:

* view paginated data;
* search;
* filter;
* sort;
* export according to entitlement.

They cannot use list APIs as a mechanism to perform prohibited modifications.

DELETED Businesses must not expose normal operational data through live API resources.

---

# 133. API and Historical Data

Historical data retrieval must remain consistent with historical integrity rules.

Examples:

```text
Historical Order price
Historical Recipe Version
Historical Set Version
Historical Payment
Historical Cash Session
Historical Report Version
```

Search and filtering must not rewrite or recalculate these values from current configuration.

---

# 134. Query Complexity Budget

Each endpoint should have an implicit query complexity budget based on:

```text
Maximum rows
Maximum joins
Maximum filters
Maximum date range
Maximum search length
Maximum page size
Maximum execution time
```

The implementation should keep this budget bounded.

---

# 135. Endpoint-Specific Query Profiles

Every high-volume endpoint should define a query profile.

Example:

```text
Orders:
- cursor
- max 100
- indexed Branch filter
- indexed status filter
- date range
- created_at sorting
```

This prevents one generic query engine from accepting unlimited combinations.

---

# 136. Generic Query Builders

A shared query builder may be used internally.

However, it must operate from explicit endpoint metadata:

```text
Allowed Filters
Allowed Sorts
Allowed Search Fields
Pagination Strategy
Scope Rules
```

It must never expose arbitrary ORM/database fields to clients.

---

# 137. Query Builder Security

A generic query builder must:

* use parameterized values;
* use field allowlists;
* use operator allowlists;
* apply authorization scope;
* enforce limits;
* enforce sort allowlists;
* enforce search limits.

Generic does not mean unrestricted.

---

# 138. Testing Requirements

The API must test:

### Pagination

* default page size;
* maximum page size;
* cursor generation;
* cursor continuation;
* invalid cursor;
* expired cursor;
* stable ordering;
* empty collection;
* final page.

### Filtering

* valid filters;
* invalid filters;
* unauthorized filters;
* combined filters;
* date ranges;
* enum values.

### Search

* exact match;
* prefix match;
* normalization;
* empty search;
* maximum length;
* unauthorized results;
* search performance.

### Sorting

* allowed fields;
* invalid fields;
* ascending;
* descending;
* deterministic tie-breaking.

---

# 139. Concurrency Testing

Pagination/search tests should also include:

* concurrent inserts;
* concurrent updates;
* concurrent deletes/archives;
* Branch access changes;
* permission changes;
* configuration changes.

The goal is to verify that authorization and pagination behavior remain safe under live system changes.

---

# 140. Performance Testing

Performance tests must include:

* small dataset;
* medium dataset;
* large dataset;
* many concurrent users;
* concurrent POS traffic;
* concurrent synchronization;
* report workloads;
* expensive search attempts.

Mixed-load testing is required to verify that administrative queries do not degrade POS performance excessively.

---

# 141. API Documentation Requirements

Every list endpoint must document:

```text
Pagination Type
Default Limit
Maximum Limit
Default Sort
Supported Sorts
Supported Filters
Search Fields
Date Semantics
Authorization Scope
Cursor Behavior
Large Query Restrictions
```

This information should be reflected in OpenAPI where practical.

---

# 142. Recommended Query Contract

A standard list request may follow:

```text
GET /api/v1/orders
    ?limit=50
    &cursor=...
    &status=PAID
    &branch_id=...
    &created_from=...
    &created_to=...
    &search=100245
    &sort=-created_at
```

The server validates each parameter against the endpoint contract.

---

# 143. Recommended Response Contract

Example:

```json
{
  "data": [
    {
      "id": "018f...",
      "order_number": "100245",
      "status": "PAID",
      "total": "25000.00",
      "created_at": "2026-10-06T10:30:00Z"
    }
  ],
  "pagination": {
    "next_cursor": "eyJ...",
    "has_more": true
  }
}
```

The exact response schema is defined by the general API response contract.

---

# 144. Recommended Pagination Strategy

Initial recommendation:

```text
Small / bounded administrative lists
→ Offset or Cursor

Large transactional collections
→ Cursor

Historical immutable datasets
→ Report / Snapshot

Large exports
→ Async Export Job
```

The simplest strategy should be selected for each endpoint based on actual workload.

---

# 145. Recommended Initial Endpoint Strategy

| Resource                | Recommended              |
| ----------------------- | ------------------------ |
| Businesses              | Cursor or bounded offset |
| Branches                | Cursor or bounded offset |
| Employees               | Offset initially         |
| Products                | Cursor or bounded offset |
| Orders                  | Cursor                   |
| Payments                | Cursor                   |
| Refunds                 | Cursor                   |
| Inventory Transactions  | Cursor                   |
| Cash Sessions           | Cursor                   |
| Notifications           | Cursor                   |
| Audit Events            | Cursor                   |
| Reports                 | Cursor                   |
| Report Versions         | Cursor                   |
| Synchronization Records | Cursor                   |
| Reference Data          | Small bounded list       |

This is an initial architecture recommendation, not an immutable implementation requirement.

---

# 146. Architectural Guardrails

The following are prohibited:

* unbounded list responses;
* unlimited page sizes;
* arbitrary SQL filters;
* arbitrary SQL sorting;
* raw SQL passed through query parameters;
* authorization applied after data retrieval;
* Business filtering without server-side scope validation;
* Branch filtering without server-side scope validation;
* deep unrestricted offset scans;
* search across every database column by default;
* unlimited search input;
* unlimited date ranges for expensive live queries;
* exposing database column names as public API fields without review;
* using pagination as a substitute for large exports;
* returning full domain aggregates for every list item;
* using stale read models for financial authority;
* exposing hidden fields through sorting;
* exposing hidden fields through filtering.

---

# 147. System Invariants

The following invariants apply to API Pagination, Search, Filtering and Sorting:

1. Large collections are paginated.
2. Pagination is bounded.
3. Every paginated endpoint has a maximum page size.
4. Default page size is defined.
5. The server enforces page size limits.
6. Cursor pagination is preferred for large frequently changing collections.
7. Offset pagination is allowed only where appropriate.
8. Offset pagination remains bounded.
9. Every paginated collection has deterministic ordering.
10. Timestamp-only ordering is avoided where ties are possible.
11. Unique tie-breakers are used where required.
12. Cursors are opaque to clients.
13. Cursor contents are not part of the public implementation contract.
14. Cursor integrity is protected.
15. Cursor query context remains consistent.
16. Cursor cannot bypass authorization.
17. Cursor cannot cross Business scope.
18. Cursor cannot cross Branch scope.
19. Expired cursors are handled predictably.
20. Invalid cursors do not expose internal implementation details.
21. Live collection pagination does not promise an immutable global snapshot.
22. Immutable historical retrieval uses report/version mechanisms where required.
23. Supported filters are explicitly defined.
24. Unsupported filters are rejected.
25. Filter names are not arbitrary database column names.
26. Filter operators are allowlisted.
27. Raw SQL expressions are prohibited.
28. SQL injection through filtering is prohibited.
29. Boolean filters use defined representations.
30. Enum filters use defined values.
31. Date ranges use explicit semantics.
32. Date-only filters respect Business/Branch timezone rules.
33. Business scope is server-authoritative.
34. Branch scope is server-authoritative.
35. Search operates inside authorized scope.
36. Search fields are explicitly defined.
37. Search input length is bounded.
38. Search normalization is deterministic.
39. Empty search behavior is defined.
40. Search does not search arbitrary database columns by default.
41. Search cannot expose unauthorized resources.
42. Search cannot expose unauthorized fields.
43. Sorting fields are allowlisted.
44. Sorting direction is controlled.
45. Arbitrary SQL sorting is prohibited.
46. Every sort has deterministic tie-breaking where required.
47. Default sorting is defined.
48. Sort fields cannot expose hidden information.
49. Cursor and sort definitions remain compatible.
50. Search, filtering and sorting compose predictably.
51. Authorization scope is applied before returning results.
52. Unauthorized data is never retrieved merely to filter it later in application memory.
53. Pagination does not replace authorization.
54. Search does not replace authorization.
55. Filtering does not replace authorization.
56. Sorting does not replace authorization.
57. Query complexity is bounded.
58. Page size is bounded.
59. Search length is bounded.
60. Expensive date ranges may be restricted.
61. Expensive query combinations may be rejected.
62. Query execution has bounded time.
63. Query results are bounded before serialization.
64. Large exports use asynchronous processing where appropriate.
65. Large report retrieval uses report/version architecture where appropriate.
66. List responses expose only required fields.
67. Full domain aggregates are not loaded unnecessarily for list endpoints.
68. N+1 query patterns are avoided.
69. Query projections are used where appropriate.
70. Database indexes support important filter/sort patterns.
71. Index design remains part of the Database architecture.
72. Search indexes remain derived infrastructure.
73. Search failure cannot corrupt authoritative business state.
74. Cache cannot become authorization authority.
75. Cache cannot cross Business scope.
76. Cache cannot cross Branch scope.
77. High-cardinality query caching is controlled.
78. Pagination behavior remains safe under concurrent data changes.
79. New live records do not invalidate previously consumed pages unpredictably where cursor semantics prevent it.
80. Live collection pagination does not guarantee immutable snapshots.
81. Historical report versions remain immutable.
82. Current configuration cannot reinterpret historical records.
83. Product search respects Branch configuration.
84. POS search remains performance-sensitive.
85. Offline local search remains subject to offline authorization.
86. Local search does not grant server authority.
87. Query parameters do not become authorization credentials.
88. Query parameters do not become SQL expressions.
89. Database query scope preserves Business isolation.
90. Database query scope preserves Branch isolation.
91. Employee visibility restrictions are preserved.
92. Subscription restrictions are preserved.
93. Deleted Businesses do not expose normal live collections.
94. READ_ONLY Businesses may continue authorized reads.
95. Audit searches remain permission-controlled.
96. Financial lists remain permission-controlled.
97. Sorting cannot reveal hidden fields.
98. Filtering cannot reveal hidden fields.
99. Search cannot reveal hidden resources.
100. Query limits protect PostgreSQL resources.
101. Query limits protect application memory.
102. Query limits protect network bandwidth.
103. Query limits protect frontend memory.
104. Query performance remains observable.
105. Search performance remains observable.
106. Deep offset usage is observable where relevant.
107. Cursor failures are observable.
108. Query timeouts are observable.
109. Metrics remain low-cardinality.
110. UUIDs are not uncontrolled metric labels.
111. API contracts document supported query behavior.
112. OpenAPI reflects supported query parameters.
113. Adding optional filters remains backward compatible.
114. Removing or changing filter semantics is treated as a contract change.
115. Cursor implementation changes must not break the public opaque-cursor contract within a supported API version.
116. Large interactive queries do not monopolize resources required by POS.
117. Search does not unnecessarily block core POS operations.
118. Background extraction is preferred for very large datasets.
119. Query optimization does not remove security predicates.
120. Query optimization does not remove Business isolation.
121. Query optimization does not remove Branch isolation.
122. Read models remain derived data.
123. Eventual consistency is not used for financial authority.
124. Pagination is not a substitute for transactional correctness.
125. Search is not a substitute for authoritative validation.
126. Filtering is not a substitute for authorization.
127. Sorting is not a substitute for resource visibility.
128. The API must remain predictable under large datasets.
129. The API must remain predictable under concurrent changes.
130. The simplest safe query strategy is preferred when multiple strategies provide equivalent behavior.

---

# 148. Related Documents

### API

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/04_Architecture/09_API/05_API_Resource_Model_and_Naming.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/08_API_Request_Validation_and_Response_Contracts.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/12_API_CRUD_and_Command_Endpoint_Architecture.md`
* `docs/04_Architecture/09_API/13_API_POS_and_Order_Endpoints.md`
* `docs/04_Architecture/09_API/17_API_Report_File_and_Notification_Endpoints.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/04_Architecture/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### Frontend

* `docs/04_Architecture/07_Frontend/22_Frontend_State_Management_and_Data_Flow.md`
* `docs/04_Architecture/07_Frontend/23_Frontend_API_Client_and_Data_Access_Architecture.md`
* `docs/04_Architecture/07_Frontend/27_Frontend_Performance_and_Optimization_Architecture.md`

### System Analysis

* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/16_Reports_and_Dashboards.md`
* `docs/02_System_Analysis/18_Audit_and_Change_History.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 149. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `11_API_Pagination_Search_Filtering_and_Sorting.md`

**Previous Document:** `10_API_Idempotency_and_Concurrency.md`

**Next Document:** `12_API_CRUD_and_Command_Endpoint_Architecture.md`

---

## Final Principle

> The API must make large datasets predictable to clients and safe for the platform: scope first, bounded query, deterministic ordering, controlled search and filtering, stable pagination, and no query mechanism may bypass authorization or database integrity.

