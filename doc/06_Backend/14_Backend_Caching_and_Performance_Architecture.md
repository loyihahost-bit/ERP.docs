# Backend Caching and Performance Architecture

**Document ID:** BA-14
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the caching and performance architecture for FastFood ERP.

The primary objective is:

> The system must remain fast for daily POS and operational workflows while preserving transactional correctness, security and historical integrity.

Caching is an optimization mechanism.

Caching must never become the authoritative source of Business data.

PostgreSQL remains the authoritative transactional source.

---

# 2. Scope

This document covers:

* performance principles;
* caching principles;
* cache ownership;
* cacheable data;
* non-cacheable data;
* cache keys;
* cache invalidation;
* cache expiration;
* cache consistency;
* authorization-aware caching;
* Business and Branch isolation;
* POS performance;
* database performance;
* API performance;
* application performance;
* background jobs;
* reporting performance;
* synchronization performance;
* offline performance;
* Redis;
* local in-process cache;
* cache stampede prevention;
* cache failure;
* cache warming;
* pagination;
* batching;
* connection pooling;
* query optimization;
* concurrency;
* performance monitoring;
* load testing;
* graceful degradation;
* performance guardrails;
* system invariants.

---

# 3. Performance Principles

The architecture follows these principles:

1. Correctness has priority over cache speed.
2. PostgreSQL remains authoritative.
3. Cache is never the source of truth.
4. POS operations receive the highest performance priority.
5. Core transactions must remain short.
6. Expensive operations should be asynchronous where appropriate.
7. Database queries should be optimized before introducing complex caching.
8. Cache invalidation must be explicit.
9. Business and Branch isolation must exist in cache keys and access paths.
10. Authorization must not be bypassed by cached data.
11. Cache failure must not corrupt Business state.
12. Cache failure should degrade performance rather than correctness.
13. Cache entries must have bounded lifetime.
14. High-cardinality cache keys must be controlled.
15. Performance optimization must be measurable.
16. Premature optimization is prohibited.
17. Security controls must not be removed for performance.
18. Historical data must never be rewritten for cache convenience.

---

# 4. Performance Priority

The system prioritizes performance in the following order:

```text id="perfprio1"
1. POS Core Operations
2. Cash Operations
3. Inventory Operations
4. Authentication / Authorization
5. Synchronization
6. Normal Business Management
7. Reports
8. XLSX Export
9. Background / Cleanup Operations
```

Heavy background operations must not unnecessarily consume resources required by POS.

---

# 5. POS Performance Principle

POS operations must remain responsive on ordinary branch computers.

Important operations include:

* opening Cash Session;
* creating Order;
* adding Product;
* modifying Order;
* accepting Order;
* payment;
* closing Cash Session;
* handover;
* inventory validation.

These operations must avoid unnecessary:

* network round trips;
* expensive queries;
* large payloads;
* synchronous external calls;
* report generation;
* file generation.

---

# 6. Authoritative Data Principle

The following remain authoritative:

```text id="authsrc1"
PostgreSQL
Business Transactions
Historical Snapshots
Immutable Audit Records
Report Versions
```

The following are not authoritative:

```text id="nonauth1"
Redis
In-memory cache
Browser cache
Local performance cache
Derived metrics
Temporary files
```

---

# 7. Cache Architecture

Initial architecture:

```text id="cachearch1"
Application
   │
   ├── Local In-Process Cache
   │
   └── Redis Cache
          │
          ↓
      PostgreSQL
```

The cache sits between application logic and authoritative storage.

A cache miss must safely fall back to PostgreSQL.

---

# 8. Cache Types

The system may use:

### 8.1. In-Process Cache

Local memory cache inside an application process.

Suitable for:

* very small;
* frequently accessed;
* short-lived;
* non-sensitive;
* low-change data.

### 8.2. Distributed Cache

Redis or equivalent.

Suitable for:

* shared cache across application instances;
* permission-related derived data;
* menu configuration;
* frequently accessed Business configuration;
* short-lived session-related data where appropriate.

### 8.3. Client-Side Cache

Browser/local application cache may be used for offline operation.

Client-side cached data must not become server-authoritative.

---

# 9. Redis Role

Redis is optional infrastructure.

It may be introduced when measurable performance requirements justify it.

Redis must not be required for correctness of:

* Orders;
* Payments;
* Inventory;
* Cash Sessions;
* configuration;
* audit;
* synchronization.

If Redis is unavailable, the backend must fall back to PostgreSQL where possible.

---

# 10. Cacheable Data

Potentially cacheable data includes:

```text id="cacheable1"
Business configuration
Branch configuration
Menu configuration
Product catalog
Category list
Printer routing
Permission-derived data
Feature configuration
Subscription entitlement snapshot
Reference data
```

The exact cacheability depends on change frequency and authorization sensitivity.

---

# 11. Non-Cacheable Authoritative Operations

The system must not rely on stale cache for authoritative decisions involving:

* final inventory quantity;
* payment authorization;
* cash balance;
* Cash Session opening/closing;
* refund authorization;
* final Order financial state;
* historical transaction state;
* unique transaction creation;
* idempotency record creation;
* Business deletion state.

These operations must validate authoritative state.

---

# 12. Inventory Cache Restriction

Inventory quantities may be cached for display or optimization.

However:

**Cached stock quantity must never be the final authority for inventory deduction.**

Order acceptance must validate authoritative inventory state inside the transaction.

Example:

```text id="invperf1"
Cache:
Stock = 5

Authoritative DB:
Stock = 2

Order requires:
3

Result:
Rejected
```

The database state wins.

---

# 13. Cash Cache Restriction

Cash balances and Cash Session state may be displayed from cached data only when appropriate.

Opening, closing, handover and correction operations must use authoritative transactional state.

Cached Cash Session information must never authorize an invalid financial operation.

---

# 14. Payment Cache Restriction

Payment state must not rely on stale cache.

Payment operations must validate authoritative:

* Order;
* payment;
* financial state;
* idempotency;
* permissions.

---

# 15. Configuration Caching

Business and Branch configuration are good candidates for caching because they may be read frequently.

Examples:

```text id="cfgcache1"
Business Settings
Branch Settings
Menu Configuration
Printer Routing
Feature Configuration
```

Configuration changes must invalidate or update affected cache entries.

---

# 16. Configuration Authority

The flow remains:

```text id="cfgcache2"
PostgreSQL
   ↓
Authoritative Configuration
   ↓
Cache
   ↓
Application Reads
```

Not:

```text id="cfgcache3"
Cache
   ↓
PostgreSQL
```

The cache is derived from the database.

---

# 17. Menu Cache

The effective Branch menu may be cached.

A cache entry may contain:

```text id="menucache1"
Business
Branch
Configuration Version
Product Availability
Effective Price
Category
Operational Flags
```

The cache must be associated with the effective configuration version.

---

# 18. Menu Cache Invalidation

When Business-level or Branch-level menu configuration changes:

```text id="menucache2"
Configuration Change
      ↓
Database Commit
      ↓
Cache Invalidation / Update
      ↓
New Configuration Available
```

Cache invalidation must happen after the authoritative transaction is successfully committed.

---

# 19. Price Cache

Effective Product prices may be cached for fast POS lookup.

The cached price must identify:

* Business;
* Branch;
* Product;
* configuration version;
* effective state.

The cached price must never modify an existing Order Item price snapshot.

---

# 20. Price Cache and Cash Session

Because pricing becomes effective from the next Cash Session, the cache must respect the active configuration/session boundary.

An active Cash Session must not silently switch to a new pricing configuration merely because Redis was refreshed.

The application must resolve the effective configuration according to the business rule.

---

# 21. Permission Cache

Effective permissions may be cached because authorization checks occur frequently.

A permission cache entry should include sufficient identity context such as:

```text id="permcache1"
Employee
Business
Branch
Role Version
Permission Version
Employee Override Version
```

---

# 22. Permission Cache Invalidation

Permission-related changes must invalidate affected cache entries.

Examples:

* Role permission change;
* Employee override change;
* Employee deactivation;
* Branch scope change;
* permission template update.

Security-sensitive cache invalidation must prioritize correctness over latency.

---

# 23. Subscription Cache

Subscription entitlement may be cached for performance.

However, subscription state is an authorization boundary.

Therefore:

* cache lifetime must be bounded;
* critical state changes must invalidate cache;
* expired Business state must not remain authorized indefinitely.

The server remains authoritative.

---

# 24. Authentication Cache

Authentication/session data may use short-lived caching where appropriate.

The cache must not make revoked credentials permanently valid.

Revocation-sensitive data requires safe invalidation or short TTL.

---

# 25. Device Trust Cache

Trusted-device state may be cached for performance.

However:

* device revocation must invalidate the cache;
* revoked devices must not continue to receive authorization because of stale cache;
* offline authorization remains server-defined.

---

# 26. Cache Key Design

Cache keys must be deterministic.

Example:

```text id="key1"
menu:{business_id}:{branch_id}:{configuration_version}
```

Another:

```text id="key2"
permissions:{employee_id}:{business_id}:{branch_id}:{permission_version}
```

Keys must never rely on ambiguous concatenation.

---

# 27. Business Isolation in Cache Keys

Every Business-scoped cache entry must include Business identity.

Example:

```text id="key3"
product:{business_id}:{product_id}
```

is preferred over:

```text id="badkey1"
product:{product_id}
```

Business isolation must be explicit.

---

# 28. Branch Isolation in Cache Keys

Branch-specific data must include Branch identity.

Example:

```text id="key4"
price:{business_id}:{branch_id}:{product_id}
```

A Branch cache entry must never be accidentally shared with another Branch.

---

# 29. Cache Key Versioning

Cache keys may include a schema or representation version.

Example:

```text id="keyver1"
menu:v2:{business_id}:{branch_id}:{config_version}
```

This allows safe changes to cached representations.

---

# 30. Cache TTL

Cache entries should have explicit TTL values.

TTL depends on data type.

Example strategy:

```text id="ttl1"
Static reference data
→ longer TTL

Menu configuration
→ medium TTL

Permission data
→ short TTL

Subscription state
→ short TTL

Temporary computation
→ very short TTL
```

Exact TTL values are implementation configuration.

---

# 31. TTL Is Not Authorization

A TTL alone must not be considered sufficient security for highly sensitive state.

For example, if an employee is deactivated, the system should invalidate their authorization cache rather than waiting for TTL expiration when practical.

---

# 32. Cache Invalidation Strategy

The system may use:

* explicit invalidation;
* versioned keys;
* TTL;
* cache-aside;
* write-through where justified.

The default strategy is:

**Cache-Aside + Explicit Invalidation + TTL**

---

# 33. Cache-Aside Pattern

Typical read:

```text id="aside1"
Application
   ↓
Cache GET
   ↓
Hit?
 ┌─┴─┐
Yes  No
 ↓    ↓
Return DB Query
        ↓
      Cache SET
        ↓
      Return
```

The application remains responsible for deciding whether cached data is safe to use.

---

# 34. Cache Write Pattern

For authoritative configuration:

```text id="writecache1"
Validate
   ↓
Database Transaction
   ↓
Commit
   ↓
Invalidate / Refresh Cache
```

Cache must not be updated before the authoritative transaction commits when doing so could expose uncommitted state.

---

# 35. Cache Failure

If Redis fails:

```text id="redisfail1"
Cache unavailable
      ↓
Application fallback
      ↓
PostgreSQL
```

The operation may become slower, but correctness must remain intact.

---

# 36. Cache Failure and POS

A Redis outage must not normally stop:

* Order creation;
* Order acceptance;
* payment;
* cash session;
* inventory transaction.

Performance may degrade temporarily.

---

# 37. Cache Failure and Security

Security-sensitive operations must not bypass authorization merely because the cache is unavailable.

Fallback behavior must be:

```text id="secfallback1"
Cache unavailable
      ↓
Authoritative lookup
      ↓
Authorization
```

not:

```text id="badfallback1"
Cache unavailable
      ↓
Allow request
```

---

# 38. Cache Stampede

A cache stampede occurs when many requests miss the same cache entry simultaneously.

The system should prevent or reduce stampedes using:

* request coalescing;
* short locking;
* jittered TTL;
* controlled cache warming;
* bounded database fallback.

---

# 39. Request Coalescing

For expensive cache entries:

```text id="coalesce1"
100 requests
    ↓
same cache miss
    ↓
1 database query
    ↓
cache populated
    ↓
100 requests receive result
```

The mechanism must be bounded and failure-safe.

---

# 40. Cache Penetration

Requests for non-existent data should not cause unlimited database queries.

Where useful, short-lived negative caching may be used.

Example:

```text id="negative1"
product:{business}:{id}
→ NOT_FOUND
```

Negative caching must use a short TTL.

---

# 41. Cache Avalanche

Large numbers of entries should not expire simultaneously when avoidable.

TTL jitter may be applied to reduce synchronized cache misses.

Example:

```text id="jitter1"
Base TTL = 300 sec
Actual TTL = 300 ± small random offset
```

The exact range is configuration.

---

# 42. Local In-Process Cache

A local cache may be used for very frequently accessed small data.

Advantages:

* extremely low latency;
* no network round trip;
* low Redis dependency.

Limitations:

* each instance has separate state;
* invalidation is harder;
* memory is limited.

Therefore local cache must use short TTLs or explicit safe invalidation.

---

# 43. Local Cache Use Cases

Suitable examples:

* static reference values;
* immutable application metadata;
* small configuration defaults;
* permission metadata with safe invalidation;
* feature definitions.

Large Business datasets should not be stored indiscriminately in application memory.

---

# 44. Distributed Cache Use Cases

Redis is more suitable for:

* shared menu cache;
* shared configuration cache;
* permission-derived cache;
* short-lived session metadata;
* distributed locks where explicitly justified.

Distributed locking must never replace database transactional correctness.

---

# 45. Redis as Lock Provider

Redis locks may be used for narrow coordination problems if justified.

However, authoritative financial correctness must remain in PostgreSQL.

For example:

```text id="redislock1"
Redis Lock
   ↓
Optimization / Coordination

PostgreSQL
   ↓
Authoritative State
```

A Redis lock failure must not result in unauthorized financial state changes.

---

# 46. Database as Performance Foundation

Before introducing cache, database performance should be optimized through:

* proper indexes;
* efficient queries;
* pagination;
* appropriate joins;
* query projection;
* connection pooling;
* transaction boundaries.

Cache must not hide fundamentally inefficient database design.

---

# 47. Query Projection

The application should select only required columns.

For example, POS menu loading should not retrieve:

* full audit history;
* full recipe history;
* unnecessary large text fields;
* unrelated employee data.

---

# 48. N+1 Prevention

Backend queries must avoid N+1 patterns.

Example:

```text id="nplus1"
Bad:
1 query for Products
+
1 query per Product for Category

Good:
Single optimized query / controlled batch
```

---

# 49. Pagination

Large lists must use pagination.

Examples:

* Orders;
* Employees;
* Inventory transactions;
* Audit records;
* Notifications;
* Reports.

Pagination must use deterministic ordering.

---

# 50. Cursor Pagination

Cursor-based pagination may be preferred for very large or frequently changing datasets.

Offset pagination remains acceptable for small administrative lists.

The choice should depend on measured query behavior.

---

# 51. Database Connection Pool

The backend must use bounded PostgreSQL connection pools.

Pool size must account for:

* application instances;
* background workers;
* report workers;
* synchronization workers.

The total connection count must remain within PostgreSQL capacity.

---

# 52. Connection Pool Strategy

The system must avoid:

```text id="poolbad1"
Application Instances × Huge Pool
```

because scaling application instances can unexpectedly exhaust PostgreSQL connections.

Pool sizing must be calculated against total deployment capacity.

---

# 53. Transaction Performance

Transactions must remain:

* short;
* deterministic;
* narrowly scoped.

Never perform inside a core transaction:

* XLSX generation;
* external API calls;
* email;
* printing;
* long report generation;
* user interaction;
* unnecessary cache network calls.

---

# 54. Performance and Row Locks

Row locks should be used only where required for correctness.

Examples:

* inventory quantity;
* Cash Session;
* payment state;
* financial corrections.

The system must avoid broad table locks for normal POS operations.

---

# 55. Lock Ordering

When multiple rows must be locked, operations should use deterministic lock ordering.

This reduces deadlock risk.

The transaction architecture defines retry behavior for unavoidable deadlocks.

---

# 56. API Payload Size

API responses should contain only necessary data.

Large payloads increase:

* network latency;
* serialization cost;
* memory usage;
* client processing time.

POS responses should remain compact.

---

# 57. POS Menu Payload

The POS menu should preferably receive an optimized representation containing only operationally necessary fields.

Example:

```text id="menupayload1"
Product ID
Name
Category
Price
Availability
Image Reference
Required Operational Flags
```

It should not include full historical configuration.

---

# 58. API Compression

HTTP compression may be enabled where payload size justifies it.

Compression must be evaluated against CPU usage.

Very small POS responses may not benefit from compression.

---

# 59. Serialization Performance

The backend should avoid unnecessary serialization of large nested ORM objects.

Use explicit DTOs/read models.

This also reduces accidental data exposure.

---

# 60. Application Memory

Application memory should remain bounded.

Avoid:

* loading entire reports into memory unnecessarily;
* loading entire inventory history;
* storing unlimited cache entries;
* accumulating synchronization batches without bounds.

---

# 61. Batch Processing

Large background operations should use bounded batches.

Examples:

* synchronization;
* lifecycle deletion;
* report processing;
* cleanup.

A batch size should be configurable and measured.

---

# 62. Synchronization Performance

Offline synchronization must not monopolize database resources.

The system should:

* validate batches;
* process bounded operations;
* preserve dependency order;
* commit safely;
* release locks quickly;
* allow partial success.

---

# 63. Synchronization Priority

Normal POS traffic should have higher resource priority than bulk synchronization.

A synchronization burst must not make branch POS operations unusable.

---

# 64. Report Performance

Reports should use:

* optimized query projections;
* database aggregation;
* appropriate indexes;
* asynchronous processing for large requests.

Large XLSX generation must run in background workers.

---

# 65. Report Cache

Frequently requested reports may use caching.

However, cached report results must identify:

```text id="reportcache1"
Business
Branch
Period
Report Definition Version
Relevant Source State
```

Stale report cache must never overwrite an immutable report version.

---

# 66. Cache and Report Versions

A cached report result and a Report Version are different.

```text id="reportcache2"
Cache
→ performance optimization

Report Version
→ historical authoritative snapshot
```

Cache expiration must not delete report history.

---

# 67. Background Job Performance

Background workers must use bounded concurrency.

Separate resource groups may be used for:

```text id="workerperf1"
Critical Jobs
Normal Jobs
Heavy Jobs
```

Examples:

Critical:

* synchronization;
* lifecycle/security jobs where required.

Heavy:

* XLSX generation;
* large reports;
* cleanup.

---

# 68. Queue Isolation

Heavy jobs must not starve critical queues.

For example:

```text id="queueperf1"
POS-related background work
        ≠
Large XLSX export queue
```

The exact queue topology depends on the selected job system.

---

# 69. Cache Warming

Cache warming may be used for predictable high-demand data.

Examples:

* Branch menu at shift start;
* configuration after deployment;
* frequently used reference data.

Cache warming must be optional.

The application must still function correctly if warming fails.

---

# 70. Shift Start Optimization

Because menu/pricing configuration is frequently needed when a Cash Session starts, the system may preload:

* effective menu;
* pricing;
* Branch configuration;
* printer routing.

The preload must respect the Cash Session configuration boundary.

---

# 71. Authentication Performance

Authentication must be secure but should not perform unnecessary database work for every normal POS request.

Short-lived authenticated sessions/tokens may reduce repeated credential verification.

However:

* revocation;
* employee status;
* subscription;
* Branch scope;
* permission changes

must propagate according to the security model.

---

# 72. Authorization Performance

Effective permissions may be cached.

The cache must be invalidated when:

* role changes;
* employee override changes;
* Branch scope changes;
* employee deactivation;
* subscription entitlement changes.

Authorization remains server-side.

---

# 73. Security vs Performance

Performance optimization must never:

* disable permission checks;
* trust client-provided Branch IDs;
* trust client-provided prices;
* trust cached inventory for final deduction;
* bypass Business isolation;
* bypass subscription restrictions.

---

# 74. Offline Performance

Offline operation should be optimized locally because the device cannot depend on network latency.

Local data may include:

* authorized menu;
* product configuration;
* required operational configuration;
* employee/device authorization;
* local transaction queue.

The local cache remains subject to offline authorization and expiration.

---

# 75. Offline Cache Security

Offline local data must:

* use encrypted local storage;
* be tied to the trusted device;
* respect offline authorization lifetime;
* support revocation/synchronization controls;
* avoid exposing unnecessary Business data.

---

# 76. Offline Cache Consistency

The offline device uses:

**latest valid authorized local configuration**

not necessarily the newest server configuration.

After synchronization:

```text id="offlinecache1"
Server authoritative configuration
        ↓
Device synchronization
        ↓
Local cache update
```

---

# 77. Performance and Historical Integrity

Performance optimization must never mutate historical records.

For example:

```text id="histperf1"
Old Order Price
    ≠
Current Cached Product Price
```

The Order snapshot remains authoritative.

---

# 78. Performance and Audit

Caching must not bypass audit requirements.

If a price change requires an audit event:

```text id="auditperf1"
Price Change
 ↓
DB Transaction
 ↓
Audit
 ↓
Cache Invalidation
```

The cache does not replace the audit record.

---

# 79. Cache Invalidation After Commit

Important cache invalidation should occur after the authoritative database transaction commits.

If the transaction rolls back:

```text id="rollbackcache1"
DB Rollback
 ↓
Do not publish new configuration as authoritative
```

This prevents cache from containing state that never committed.

---

# 80. Outbox-Based Cache Invalidation

For distributed cache invalidation, an Outbox event may be used.

Example:

```text id="outboxcache1"
Configuration Transaction
       +
CacheInvalidation Event
       ↓
Atomic Commit
       ↓
Worker / Consumer
       ↓
Redis Invalidation
```

This may be preferred when multiple backend instances require reliable invalidation.

---

# 81. Cache Invalidation Failure

If invalidation fails:

* authoritative database remains correct;
* stale cache must have bounded TTL;
* retry should occur where appropriate;
* critical authorization/configuration cache may require stronger invalidation handling.

The system must not treat Redis invalidation failure as database corruption.

---

# 82. Versioned Cache Strategy

Where practical, versioned cache keys may reduce invalidation complexity.

Example:

```text id="versioncache1"
menu:{business}:{branch}:v12
```

New configuration:

```text id="versioncache2"
menu:{business}:{branch}:v13
```

The application switches to the new authoritative configuration after commit.

Old cache entries expire naturally or are explicitly cleaned.

---

# 83. Cache Consistency Levels

Different data may use different consistency levels.

### Strong

Used for:

* financial operations;
* inventory deduction;
* Cash Session operations;
* authorization-critical state.

### Bounded Staleness

Used for:

* menu display;
* non-critical configuration;
* reference data.

### Eventual

Used for:

* notifications;
* dashboards;
* operational aggregates where appropriate.

The consistency level must be explicit.

---

# 84. Performance and Eventual Consistency

Eventual consistency is not acceptable for operations where stale state could produce:

* financial loss;
* negative inventory;
* unauthorized access;
* duplicate payment;
* invalid Cash Session.

---

# 85. Cache Observability

Cache metrics should include:

```text id="cachemon1"
cache_hit_count
cache_miss_count
cache_error_count
cache_latency
cache_eviction_count
cache_invalidation_count
```

Metrics should be grouped by stable cache category.

Do not expose arbitrary Business/Product UUIDs as metric labels.

---

# 86. Cache Hit Rate

Cache hit rate is useful but not the only performance metric.

A high hit rate is not automatically good if:

* cached data is stale;
* authorization is unsafe;
* database queries are still slow;
* cache infrastructure is overloaded.

Correctness remains the priority.

---

# 87. Cache Latency

The system should monitor:

* Redis latency;
* local cache latency;
* serialization/deserialization time.

If cache access becomes slower than direct database access for a specific operation, the cache strategy should be reevaluated.

---

# 88. Database Performance Metrics

Important metrics include:

```text id="dbperf1"
query latency
slow queries
connection pool utilization
lock wait
deadlocks
transaction duration
rollback rate
database CPU
database memory
disk I/O
```

---

# 89. Application Performance Metrics

Important metrics include:

```text id="appp1"
request latency
request throughput
error rate
serialization duration
cache latency
queue wait time
worker duration
memory usage
CPU usage
```

---

# 90. Performance Budgets

Performance budgets should be established for critical operations after baseline measurement.

Examples:

```text id="budget1"
POS order creation
Order acceptance
Payment
Cash Session operation
Synchronization
```

The exact numerical targets should be based on real deployment measurements rather than arbitrary assumptions.

---

# 91. Performance Regression Detection

Performance testing should compare:

```text id="reg1"
Current Version
vs
Previous Baseline
```

Important regressions should be detected before production deployment.

---

# 92. Load Testing Scenarios

Load testing should include:

### POS Load

Many simultaneous order operations.

### Synchronization Load

Many devices synchronizing batches.

### Reporting Load

Multiple reports and exports.

### Administrative Load

Employees, menu, inventory and configuration operations.

### Mixed Load

POS + synchronization + reports + background jobs simultaneously.

---

# 93. Performance Test Priority

Mixed-load testing is especially important because the system must ensure that heavy administrative/reporting workloads do not degrade POS performance excessively.

---

# 94. Cache Testing

Cache tests should verify:

* hit;
* miss;
* expiration;
* invalidation;
* Redis failure;
* stale entry;
* concurrent miss;
* negative cache;
* Business isolation;
* Branch isolation.

---

# 95. Cache Security Testing

Security tests must verify:

```text id="cachesec1"
Business A cache
≠
Business B cache

Branch A cache
≠
Branch B cache

Employee A permissions
≠
Employee B permissions
```

A cache key collision must never expose another scope's data.

---

# 96. Cache Recovery

After Redis restart:

```text id="recovercache1"
Redis Empty
   ↓
Cache Miss
   ↓
PostgreSQL
   ↓
Cache Rebuild
```

The application must recover automatically without requiring manual reconstruction of authoritative data.

---

# 97. Cache Flush

A global cache flush must be treated as an operational event.

After a flush:

* PostgreSQL remains authoritative;
* cache repopulates naturally;
* performance may temporarily degrade;
* correctness must remain unchanged.

---

# 98. Deployment and Cache

Application deployment may invalidate local in-process caches.

This is acceptable.

Distributed cache entries should use versioned keys or controlled invalidation to avoid incompatible cached representations.

---

# 99. Schema Changes and Cache

When cached data structure changes:

* cache key version should change where necessary;
* old entries should not be interpreted using a new schema;
* deployment should remain compatible with active instances.

---

# 100. Configuration Changes and Cache

Important configuration changes must have a deterministic cache update strategy.

Example:

```text id="cfgperf1"
Price Change
 ↓
DB Commit
 ↓
Configuration Version N+1
 ↓
Cache Invalidation
 ↓
New POS Session
 ↓
Uses Version N+1
```

---

# 101. Performance and Report Versioning

Report generation must not depend on a stale cache when generating an authoritative historical report version.

If cached data is used, the system must ensure that the relevant source state is correctly identified.

---

# 102. Performance and File Export

XLSX generation must be asynchronous.

The API should return quickly with an Export Job reference rather than waiting for file generation.

---

# 103. Performance and Notifications

Notifications must be asynchronous.

A notification provider must not block a core transaction.

---

# 104. Performance and Printing

Printing must be asynchronous after Order acceptance.

A printer delay must not hold the Order transaction open.

---

# 105. Performance and External APIs

External API calls must use:

* timeout;
* bounded retry;
* circuit protection where appropriate;
* asynchronous processing when possible.

External services must not be part of core POS transaction latency unless explicitly required by the business rule.

---

# 106. Performance and Circuit Breaking

Circuit breaking may be used for unstable external dependencies.

A circuit breaker must not bypass mandatory business validation.

---

# 107. Performance and API Rate Limiting

Rate limiting may protect:

* authentication;
* synchronization;
* public endpoints;
* administrative APIs;
* expensive report generation.

Rate limits must not make normal POS operations unusable.

---

# 108. Performance and Synchronization Rate Limiting

Synchronization requests should use bounded batch sizes.

The system may apply backpressure when:

* database load is high;
* queue backlog is excessive;
* synchronization traffic threatens POS performance.

---

# 109. Backpressure

The system should use controlled backpressure rather than allowing unlimited work accumulation.

Possible mechanisms:

* queue limits;
* batch limits;
* concurrency limits;
* retry delays;
* rate limits.

---

# 110. Performance and Business Isolation

Performance optimizations must preserve Business isolation.

Examples:

* cache keys include Business;
* queries include Business scope;
* indexes support Business filtering;
* background jobs carry Business context.

Optimization must never remove a scope filter.

---

# 111. Performance and Branch Isolation

Branch-specific optimization must preserve Branch boundaries.

A Branch menu cache must not be reused for another Branch unless the data is explicitly Business-global.

---

# 112. Performance and Subscription

Cached entitlement state must not allow an expired Business to continue modifying data indefinitely.

Subscription cache invalidation must be treated as security-sensitive.

---

# 113. Performance and Employee Deactivation

After employee deactivation:

* cached permissions must be invalidated;
* active authorization must respect the new employee state;
* stale cache must not allow new operations.

---

# 114. Performance and Trusted Devices

Device authorization caches must be invalidated when:

* device revoked;
* Business state changes;
* employee/device relationship changes;
* offline authorization expires.

---

# 115. Performance and Error Handling

Cache failures should produce controlled fallback behavior.

Example:

```text id="cacheerr1"
Redis Timeout
 ↓
Log Warning
 ↓
Metric Increment
 ↓
Database Fallback
```

The user should not receive an infrastructure stack trace.

---

# 116. Performance and Recovery

If a performance problem occurs, recovery should prioritize:

1. Protect POS.
2. Protect PostgreSQL.
3. Reduce heavy background work.
4. Reduce synchronization concurrency if necessary.
5. Pause expensive reports/exports.
6. Restore cache where useful.
7. Investigate root cause.

---

# 117. Operational Performance Controls

Operators may need controlled ability to:

* reduce worker concurrency;
* pause heavy queues;
* disable optional cache;
* flush cache;
* disable non-critical background processing;
* limit report generation.

Such controls must not disable mandatory security or transactional correctness.

---

# 118. Performance Guardrails

The implementation must prohibit:

* unbounded cache growth;
* unbounded worker concurrency;
* unbounded report generation;
* unlimited synchronization batches;
* unlimited API payload size;
* unlimited retry loops;
* cache as financial authority;
* cache as inventory authority;
* cache as authorization bypass;
* long external calls inside core transactions.

---

# 119. Recommended Cache Layers

Initial recommendation:

```text id="layers1"
Layer 1
In-Process Cache
        ↓
Layer 2
Redis
        ↓
Layer 3
PostgreSQL
```

Not every data type must use all three layers.

The simplest safe strategy should be preferred.

---

# 120. Recommended Initial Cache Targets

Initial caching candidates:

```text id="targets1"
1. Business configuration
2. Branch configuration
3. Effective menu
4. Effective pricing
5. Reference data
6. Permission-derived data
7. Feature configuration
8. Short-lived subscription entitlement
```

Inventory, payments and cash remain authoritative database operations.

---

# 121. Recommended Backend Structure

The performance and caching components should fit the existing structure:

```text id="struct14"
app/
├── application/
│   ├── configuration/
│   ├── products/
│   ├── menu/
│   ├── orders/
│   └── reports/
│
├── infrastructure/
│   ├── cache/
│   │   ├── local.py
│   │   ├── redis.py
│   │   ├── keys.py
│   │   ├── invalidation.py
│   │   └── serialization.py
│   │
│   ├── database/
│   ├── monitoring/
│   └── storage/
│
├── background/
├── synchronization/
├── reporting/
└── shared/
    └── performance/
```

Exact module names may be refined during implementation.

---

# 122. Cache Interface

Application code should depend on an abstraction where practical.

Example:

```text id="cacheiface1"
Cache
├── get()
├── set()
├── delete()
├── invalidate()
└── get_or_set()
```

The application should not be tightly coupled to Redis commands.

---

# 123. Cache Serialization

Cached values should use a controlled serialization format.

The system must validate:

* schema/version;
* required fields;
* expiration;
* scope.

Corrupt cache entries should be discarded and rebuilt from PostgreSQL.

---

# 124. Cache Error Handling

Cache errors should be classified as:

```text id="cacheclass1"
Timeout
Connection Error
Serialization Error
Invalid Entry
Unavailable
```

The application should apply the appropriate fallback.

---

# 125. Cache Observability

Every important cache subsystem should provide:

* hit/miss metrics;
* latency;
* errors;
* invalidation count;
* eviction count.

Logs should be used for unusual cache failures, not every successful cache read.

---

# 126. Cache and Request Context

Where a cache operation is security-sensitive, logs should be able to associate the event with:

```text id="cachectx1"
request_id
operation_id
business_id
branch_id
employee_id
```

Do not log complete cache values.

---

# 127. Performance Documentation

Every significant optimization should document:

* problem;
* baseline;
* change;
* expected effect;
* measured result;
* correctness implications.

Optimization without measurable reasoning should be avoided.

---

# 128. Performance Change Review

A performance change must verify:

* Business isolation;
* Branch isolation;
* authorization;
* historical integrity;
* transaction correctness;
* offline behavior;
* synchronization behavior.

Performance is not an independent concern from correctness.

---

# 129. Performance Regression Guardrails

Before accepting a major performance optimization, test:

```text id="regguard1"
Correctness
Security
Concurrency
Failure Recovery
Load
Latency
Memory
Database Load
```

---

# 130. System Invariants

The following invariants apply to Caching and Performance:

1. PostgreSQL remains the authoritative transactional source.
2. Cache is never authoritative business state.
3. Cache failure cannot corrupt authoritative data.
4. Cache failure must fall back safely where possible.
5. Cache cannot bypass authorization.
6. Cache cannot bypass Business isolation.
7. Cache cannot bypass Branch isolation.
8. Cached inventory is not authoritative for final deduction.
9. Cached cash state is not authoritative for financial operations.
10. Cached payment state is not authoritative for payment completion.
11. Cached subscription state cannot authorize indefinitely after expiry.
12. Revoked employees must not remain authorized because of stale permission cache.
13. Revoked devices must not remain trusted because of stale device cache.
14. Business configuration cache must identify Business scope.
15. Branch configuration cache must identify Branch scope.
16. Permission cache must identify relevant identity and scope versions.
17. Price cache must identify effective configuration version.
18. Menu cache must identify effective configuration version.
19. Cache entries must have bounded lifetime.
20. Cache invalidation must be explicit for important state changes.
21. Authoritative database changes must commit before publishing derived cache state.
22. Cache invalidation failure must not corrupt database state.
23. Cache keys must be deterministic.
24. Cache keys must prevent cross-Business collisions.
25. Cache keys must prevent cross-Branch collisions.
26. Cache representations must be versionable.
27. Cache serialization must be validated.
28. Corrupt cache entries must be safely discarded.
29. Cache growth must be bounded.
30. Local in-process cache must not be treated as globally shared state.
31. Distributed cache must not be required for transactional correctness.
32. Redis must remain optional infrastructure where possible.
33. Cache stampedes must be controlled for expensive entries.
34. Cache penetration must be controlled where necessary.
35. Cache avalanche risk should be reduced.
36. Cache warming failure must not prevent correct operation.
37. Cache flush must not delete authoritative data.
38. Cache metrics must remain low-cardinality.
39. UUIDs must not become uncontrolled metric labels.
40. Database performance must be optimized before unnecessary cache complexity.
41. N+1 queries must be avoided.
42. Large lists must use bounded pagination.
43. Query projections should select only required fields.
44. Database connection pools must be bounded.
45. Total database connections must remain within deployment capacity.
46. Core transactions must remain short.
47. External API calls must not block core transactions unnecessarily.
48. XLSX generation must not occur inside core transactions.
49. Printing must not occur inside core transactions.
50. Notifications must not occur inside core transactions.
51. Large reports must run asynchronously.
52. Synchronization batches must be bounded.
53. Synchronization must not monopolize database resources.
54. POS operations have higher performance priority than heavy background work.
55. Background worker concurrency must be bounded.
56. Heavy queues must not starve critical queues.
57. API payloads must remain bounded.
58. Large responses must use appropriate pagination or asynchronous processing.
59. Application memory usage must remain bounded.
60. Performance optimization must be measurable.
61. Performance optimization must preserve security.
62. Performance optimization must preserve Business isolation.
63. Performance optimization must preserve Branch isolation.
64. Performance optimization must preserve historical integrity.
65. Performance optimization must preserve transaction correctness.
66. Performance optimization must preserve offline authorization rules.
67. Performance optimization must preserve synchronization correctness.
68. Historical Order prices cannot be replaced by cached current prices.
69. Historical Recipe versions cannot be replaced by cached current recipes.
70. Historical Set configurations cannot be replaced by cached current configurations.
71. Report versions cannot be replaced by cached report results.
72. Audit records cannot be replaced by cache entries.
73. Cache cannot become a source of historical truth.
74. Authorization fallback must fail closed.
75. Security-sensitive stale state must have bounded lifetime.
76. Redis locks cannot replace PostgreSQL transactional correctness.
77. Lock ordering must remain deterministic where multiple locks are required.
78. Deadlocks must be observable and safely retried where appropriate.
79. Monitoring must exist for cache latency and failures.
80. Monitoring must exist for database performance.
81. Monitoring must exist for worker performance.
82. Monitoring must exist for synchronization performance.
83. Monitoring must exist for report/export performance.
84. Cache infrastructure failure must be distinguishable from database failure.
85. Application must remain operational in degraded cache conditions where possible.
86. Heavy background operations must be controllable during resource pressure.
87. Performance degradation must not silently disable security controls.
88. Performance architecture must remain compatible with future horizontal scaling.
89. Performance architecture must remain compatible with future read replicas.
90. Additional infrastructure must be introduced only when justified by measured need.
91. Simplicity is preferred when two performance strategies provide equivalent correctness.
92. Correctness and historical integrity have priority over cache hit rate.

---

# 131. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend

* `docs/06_Backend/01_Backend_Architecture.md`
* `docs/06_Backend/02_Backend_Project_Structure.md`
* `docs/06_Backend/06_Authentication_and_Authorization.md`
* `docs/06_Backend/07_Transaction_Management.md`
* `docs/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/06_Backend/11_Configuration_and_Environment_Management.md`
* `docs/06_Backend/12_Reporting_and_Export_Architecture.md`
* `docs/06_Backend/13_Backend_Health_Observability_and_Monitoring.md`

---

# 132. Status

**Backend Architecture Document:** Completed.

**Document Status:** Accepted.

**Current Document:** `14_Backend_Caching_and_Performance_Architecture.md`

**Next Document:** `15_Backend_File_Storage_and_Document_Management.md`

