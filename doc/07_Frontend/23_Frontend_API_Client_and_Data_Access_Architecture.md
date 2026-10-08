# Frontend API Client and Data Access Architecture

**Document ID:** FA-23
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`

---

## 1. Purpose

This document defines the frontend API client and data access architecture for FastFood ERP.

The frontend must communicate with the backend through a controlled, predictable and typed data-access layer.

The architecture must provide:

* centralized API communication;
* authentication handling;
* Business and Branch scope propagation;
* request/response typing;
* error mapping;
* timeout handling;
* retry control;
* idempotency support;
* pagination;
* filtering;
* sorting;
* file operations;
* synchronization;
* offline requests;
* cache integration;
* request cancellation;
* concurrency handling;
* observability;
* security;
* testability.

UI components must not communicate with the backend through arbitrary direct HTTP calls.

---

## 2. Architectural Principle

The frontend follows this data-access flow:

```text
UI Component
    ↓
Feature Query / Mutation
    ↓
Application Data Access
    ↓
API Client
    ↓
HTTP Transport
    ↓
Backend API
    ↓
Application Layer
    ↓
Domain / Repository
    ↓
Database
```

The response travels back through the same controlled boundary:

```text
Database
    ↓
Backend API
    ↓
HTTP Client
    ↓
Response Validation / Mapping
    ↓
Server State
    ↓
Feature Selector
    ↓
UI
```

---

## 3. API Client Responsibilities

The API client is responsible for transport concerns.

It may handle:

* base URL;
* HTTP method;
* headers;
* authentication/session information;
* request IDs;
* operation IDs;
* timeout;
* serialization;
* deserialization;
* response validation;
* error normalization;
* retry policy;
* cancellation;
* telemetry.

The API client must not contain restaurant business rules.

---

## 4. Business Logic Boundary

The API client must not decide business outcomes.

Incorrect:

```text
API Client
    ↓
"If stock is low, reject Order"
```

Correct:

```text
API Client
    ↓
Send Order Command
    ↓
Backend
    ↓
Validate Inventory
    ↓
Accept / Reject
```

Business rules belong to the backend.

---

## 5. Data Access Layers

Frontend data access should be separated into:

```text
Transport Layer
      ↓
API Client
      ↓
Resource / Feature API
      ↓
Query / Mutation Layer
      ↓
State / Cache
      ↓
UI
```

Each layer has a specific responsibility.

---

## 6. Transport Layer

The transport layer performs low-level HTTP communication.

Responsibilities:

* HTTP requests;
* response handling;
* serialization;
* headers;
* timeout;
* cancellation;
* network error detection.

It must not know about:

* Orders;
* Products;
* Inventory rules;
* Cash Sessions;
* Payroll calculations.

---

## 7. API Client Layer

The API client adds application-independent concerns around transport.

Examples:

* authentication context;
* request ID;
* operation ID;
* error normalization;
* retry policy;
* response parsing;
* telemetry.

---

## 8. Feature API Layer

Feature APIs provide domain-oriented frontend operations.

Examples:

```text id="lq3n5x"
productsApi
ordersApi
paymentsApi
cashApi
inventoryApi
menuApi
settingsApi
reportsApi
notificationsApi
employeesApi
```

Example conceptual methods:

```text
productsApi.list()
productsApi.get(id)

ordersApi.createDraft()
ordersApi.accept()
ordersApi.cancel()

cashApi.openSession()
cashApi.closeSession()

inventoryApi.list()
inventoryApi.adjust()
```

These methods describe application operations rather than generic HTTP mechanics.

---

## 9. Query Layer

Queries provide read-oriented access.

Examples:

```text id="0n3w3n"
useProductsQuery()
useOrderQuery()
useCashSessionQuery()
useInventoryQuery()
useBranchMenuQuery()
```

The query layer controls:

* cache;
* loading state;
* stale state;
* refetch;
* pagination;
* query parameters.

---

## 10. Mutation Layer

Mutations represent server-changing commands.

Examples:

```text id="w9l2hd"
useCreateOrderMutation()
useAcceptOrderMutation()
usePaymentMutation()
useCloseCashSessionMutation()
useUpdatePriceMutation()
```

The mutation layer handles:

* request;
* operation UUID;
* loading;
* success;
* error;
* conflict;
* cache invalidation;
* authoritative response.

---

## 11. No Direct API Calls from Components

Components must not contain arbitrary HTTP calls.

Avoid:

```text id="0v14k5"
Component
   ↓
fetch(...)
```

Prefer:

```text id="8z9z0r"
Component
   ↓
Feature Query / Mutation
   ↓
API Client
```

This makes data access:

* testable;
* reusable;
* observable;
* consistent.

---

## 12. API Base Configuration

The API base URL must come from application/environment configuration.

It must not be hardcoded throughout the frontend.

Example conceptual configuration:

```text id="kq3m3e"
API_BASE_URL
API_TIMEOUT
API_VERSION
ENVIRONMENT
```

Production and development environments must use separate configuration.

---

## 13. API Versioning

The frontend must use an explicit API version.

Example:

```text
/api/v1/...
```

The exact URL structure is defined by the API architecture.

The frontend must not silently assume compatibility with a newer API version.

---

## 14. API Contract

Frontend API types should follow the authoritative backend API contract.

The contract should define:

* endpoint;
* HTTP method;
* path parameters;
* query parameters;
* request body;
* response body;
* status codes;
* error codes;
* pagination;
* authentication requirements;
* idempotency requirements.

---

## 15. Typed Requests

Request payloads must use explicit types.

Example:

```text id="6r1k1v"
CreateOrderRequest
UpdateProductRequest
CloseCashSessionRequest
ChangePriceRequest
```

Avoid arbitrary objects:

```text
Record<string, unknown>
```

when a stable API contract exists.

---

## 16. Typed Responses

Responses should have explicit types.

Examples:

```text id="g1w0e8"
ProductResponse
OrderResponse
CashSessionResponse
InventoryItemResponse
ConfigurationResponse
ReportResponse
```

Typed responses reduce accidental UI assumptions.

---

## 17. DTO Mapping

API DTOs may differ from frontend models.

The preferred flow is:

```text id="9n7f1q"
API Response DTO
      ↓
Mapper
      ↓
Frontend Model
      ↓
State / UI
```

Mapping should happen at a controlled boundary.

---

## 18. Response Validation

Responses from the backend should be validated where runtime validation is required.

Validation is particularly important for:

* authentication;
* synchronization;
* offline data;
* financial operations;
* configuration;
* versioned data.

Invalid responses must not silently enter authoritative frontend state.

---

## 19. Error Architecture

API errors must be normalized into a consistent frontend error model.

Example:

```text id="9j2m4b"
ApiError
├── code
├── message
├── status
├── details
├── requestId
├── operationId
└── retryable
```

Feature components should not independently parse raw HTTP responses.

---

## 20. Standard Error Categories

The frontend should recognize at least:

```text
VALIDATION_ERROR
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
NOT_FOUND
CONFLICT
BUSINESS_RULE_VIOLATION
RATE_LIMITED
TEMPORARY_ERROR
NETWORK_ERROR
TIMEOUT
OFFLINE
SERVER_ERROR
```

Backend-specific error codes may be added without changing the overall structure.

---

## 21. HTTP Status Mapping

Typical mapping:

```text id="j8b1z5"
401 → Authentication Error
403 → Authorization Error
404 → Not Found
409 → Conflict
422 → Validation / Business Rule
429 → Rate Limited
5xx → Server / Temporary Error
```

The exact API contract remains authoritative.

---

## 22. Request ID

Every API request should carry a request identifier when required by the backend contract.

The identifier allows:

* tracing;
* support diagnostics;
* log correlation;
* error investigation.

The frontend should preserve the request ID returned by the backend when available.

---

## 23. Operation ID

Business-changing operations should use an operation UUID when required.

Example:

```text id="1f7f0n"
POST /orders/accept

X-Operation-ID:
550e8400-e29b-41d4-a716-446655440000
```

The operation ID identifies the business operation, not the employee.

---

## 24. Operation UUID Lifecycle

For a retryable command:

```text id="9ljq4g"
Create Operation UUID
        ↓
Send Request
        ↓
Timeout
        ↓
Retry Same Operation UUID
        ↓
Backend Idempotency Check
        ↓
One Authoritative Result
```

The frontend must not generate a new operation UUID for the same logical retry.

---

## 25. Idempotency

The API client must support idempotent commands.

Important operations include:

* Order acceptance;
* Payment;
* Refund;
* Cash Session operations;
* Inventory adjustment;
* Configuration changes;
* Synchronization operations.

Idempotency rules are defined by the backend contract.

---

## 26. Retry Policy

Automatic retries must be conservative.

Retry may be allowed for:

* temporary network failure;
* connection reset;
* timeout where operation is idempotent;
* temporary server failure.

Retry should not occur automatically for:

* 401;
* 403;
* validation error;
* business rule violation;
* permanent conflict;
* known permanent failure.

---

## 27. Financial Operation Retry

Financial operations require special handling.

Example:

```text id="p8w1z2"
Payment Request
    ↓
Network Timeout
    ↓
Unknown Server Result
```

The frontend must not create a second payment blindly.

It must retry using the same operation UUID or query the authoritative operation result according to the API contract.

---

## 28. Timeout Handling

Each API category should have an appropriate timeout.

Short operational requests should have relatively short timeouts.

Long-running operations such as:

* report generation;
* XLSX export;
* large imports

should use asynchronous job APIs rather than extremely long HTTP requests.

---

## 29. Cancellation

The API client should support request cancellation.

Useful cases:

* user changes search query;
* user leaves page;
* old report preview becomes irrelevant;
* navigation changes;
* duplicate read request is replaced.

Cancellation must not cancel a committed business operation accidentally.

---

## 30. Search Requests

Search should use controlled query parameters.

Example:

```text id="b7r2s4"
GET /products
    ?search=burger
    &branch_id=...
    &cursor=...
    &limit=...
```

The frontend must not construct SQL fragments.

---

## 31. Pagination

The API client must support pagination metadata.

Example:

```text id="6s3v7e"
{
  data: [...],
  nextCursor: "...",
  hasMore: true
}
```

The exact response format follows the API contract.

Cursor pagination is preferred for large or frequently changing datasets where supported.

---

## 32. Pagination State

Pagination parameters must be part of query state.

Changing:

* search;
* filters;
* sorting;
* Branch;

must reset or correctly recalculate pagination.

---

## 33. Filtering

Filters should be typed and validated before sending.

Example:

```text id="v3g8c6"
branch_id
employee_id
status
date_from
date_to
category_id
```

Only supported filters may be sent to the backend.

---

## 34. Sorting

Sorting should use an explicit field/direction model.

Example:

```text id="g0s8n4"
sort:
  field: created_at
  direction: desc
```

The frontend must not send arbitrary SQL expressions.

---

## 35. Branch Context Propagation

Branch-scoped API requests should receive the current Branch context through the approved request mechanism.

The frontend must not assume that simply sending `branch_id` grants access.

The backend must validate:

* Business scope;
* Branch scope;
* employee permissions;
* subscription entitlement.

---

## 36. Business Context Propagation

Business context must be propagated consistently.

Where the API contract requires Business identification, the client must provide it.

However, client-provided Business identifiers are never authoritative authorization evidence.

---

## 37. Context Change

When Business or Branch context changes:

1. stop or invalidate incompatible queries;
2. update context;
3. clear incompatible cache;
4. refresh permissions;
5. refresh subscription state;
6. load relevant Branch configuration;
7. load relevant menu;
8. restore the new operational state.

---

## 38. Authentication Headers

Authentication credentials/session information must be attached centrally.

Individual feature APIs must not manually implement authentication headers.

This prevents inconsistent authentication behavior.

---

## 39. Authentication Failure

If the backend returns authentication failure:

```text id="h0g8q2"
API Response
   ↓
401
   ↓
API Client
   ↓
Session Manager
   ↓
Refresh / Re-authenticate
```

The exact refresh behavior depends on the authentication architecture.

---

## 40. Authorization Failure

A `403` must not be treated as a network error.

The UI should display an appropriate access message.

The client must not retry automatically.

---

## 41. Read-Only Subscription

When subscription state is read-only:

* read requests remain available where permitted;
* modifying requests should be blocked by UI where possible;
* backend remains authoritative;
* the API client must not attempt bypass techniques.

---

## 42. Rate Limiting

When the API returns rate-limit information, the client should respect it.

For retryable rate-limit responses:

* use server-provided retry timing where available;
* avoid rapid retry loops;
* inform the user when necessary.

---

## 43. Network Error

Network errors should be normalized.

The UI should distinguish:

```text id="f4y0av"
No Internet
Backend Unreachable
Timeout
Request Cancelled
Offline Mode
```

These conditions have different recovery strategies.

---

## 44. Offline API Adapter

Offline-capable operations should not pretend to use the normal online API.

Conceptually:

```text id="q6w9bp"
Feature Command
      ↓
Data Access Layer
      ↓
Online?
 ┌────┴────┐
Yes        No
 ↓          ↓
API       Offline Adapter
            ↓
       Secure Local Queue
```

Only explicitly supported offline operations may use the Offline Adapter.

---

## 45. Offline Authorization

Before accepting an offline operation, the frontend must verify locally available offline authorization information according to the security architecture.

It must not invent or extend offline authorization.

The backend remains authoritative after synchronization.

---

## 46. Offline Operation UUID

Every queued offline command requiring idempotency must have an operation UUID.

The UUID must survive:

* application restart;
* reconnect;
* synchronization retry.

---

## 47. Offline Queue Data Access

The offline queue should provide operations such as:

```text id="j3b4g7"
enqueue()
peek()
markUploading()
markAccepted()
markRetryable()
markConflict()
markRejected()
removeAfterFinalization()
```

The implementation must preserve operation integrity.

---

## 48. Synchronization API

Synchronization should use dedicated APIs.

Conceptually:

```text id="0l8y8x"
POST /sync/batch
```

The frontend should not emulate synchronization by replaying ordinary UI API requests one by one unless explicitly defined by the backend architecture.

---

## 49. Partial Synchronization

The client must support partial results.

Example:

```text id="7v6z1r"
Operation 1 → Accepted
Operation 2 → Conflict
Operation 3 → Retry
Operation 4 → Rejected
```

Each operation must receive its own final synchronization state.

---

## 50. Configuration API

Configuration APIs should expose:

* current version;
* effective configuration;
* pending configuration where applicable;
* status;
* permissions;
* approval state;
* conflict information.

The frontend must preserve configuration version metadata.

---

## 51. Optimistic Concurrency

Configuration mutation requests should include the version expected by the client.

Example:

```text id="6a4g6y"
expected_version = 17
```

If the backend reports a conflict, the frontend must enter conflict handling rather than retrying the stale request blindly.

---

## 52. File Uploads

File upload must use a dedicated file-data-access abstraction.

Examples:

* Product images;
* documents;
* report files;
* attachments where supported.

The abstraction should handle:

* file validation;
* size limits;
* content type;
* upload progress where useful;
* cancellation;
* retry;
* authorization.

---

## 53. File Security

The frontend must not assume that:

* file extension is safe;
* MIME type is authoritative;
* uploaded filename is trusted.

Backend validation remains mandatory.

The frontend should provide user-friendly validation before upload to reduce unnecessary requests.

---

## 54. File Downloads

Downloads must respect authorization and Business scope.

The frontend must not construct arbitrary storage URLs.

Preferred flow:

```text id="f0g6g8"
Frontend
   ↓
Authorized Download Request
   ↓
Backend / File Service
   ↓
Authorized File Response
```

---

## 55. XLSX Export

Large exports should use asynchronous export APIs.

Example:

```text id="r7x6za"
Create Export
   ↓
Job ID
   ↓
Poll / Push Status
   ↓
READY
   ↓
Download
```

The frontend should not generate large business reports locally unless explicitly required.

---

## 56. Report API

Report requests should include:

* report type;
* period;
* Branch scope;
* filters;
* requested version where applicable.

The backend determines the authoritative report result.

---

## 57. Notifications API

Notification APIs should support:

* list;
* unread count;
* mark read;
* relevant filtering;
* pagination.

Notification actions must not grant permissions.

---

## 58. Audit API

Audit data access must be:

* authorized;
* paginated;
* scoped;
* filterable;
* read-only.

The frontend must never modify audit records.

---

## 59. Cache Integration

The API/data-access layer integrates with frontend server-state caching.

Typical flow:

```text id="apq6j5"
Query
  ↓
Cache
  ↓
Fresh?
 ├── Yes → Return
 └── No → API
             ↓
          Response
             ↓
          Cache
             ↓
           UI
```

---

## 60. Cache Key Architecture

Cache keys must be deterministic.

Example:

```text id="j7m6p4"
products:
  businessId
  branchId
  filters
  sorting
  pagination
```

Equivalent queries should produce equivalent keys.

---

## 61. Cache Scope

Cache keys must include all scope dimensions that affect the result.

Depending on the resource this may include:

* Business;
* Branch;
* employee;
* permission context;
* configuration version;
* query filters.

Sensitive state must not be accidentally shared between users or Businesses.

---

## 62. Cache Invalidation

Mutation success should invalidate only affected resources where practical.

Examples:

```text id="7w0v8c"
Update Product
    ↓
Invalidate Product Detail
Invalidate Product List
Invalidate Relevant Menu
```

Unrelated resources should remain cached.

---

## 63. Cache vs Historical Data

Historical data should not be overwritten in cache by current state.

Example:

```text id="z1q7mv"
Current Price Cache
        ≠
Historical Order Item Price
```

Historical transaction data must retain its own authoritative snapshot.

---

## 64. Request Deduplication

Identical simultaneous read requests may be deduplicated.

Example:

```text id="1j5h6f"
Component A ─┐
Component B ─┼→ Same Query
Component C ─┘
                 ↓
             One Request
```

This reduces unnecessary backend traffic.

---

## 65. Request Ordering

Where operation ordering matters, requests must be serialized or coordinated.

Examples:

* Cash Session open → cash operations;
* configuration update → approval;
* offline synchronization;
* sequential correction operations.

The frontend must not assume that HTTP completion order equals business operation order.

---

## 66. Concurrency Control

The data-access layer must handle concurrent requests safely.

Examples:

```text id="a5u1rx"
Request A → Product Version 10
Request B → Product Version 11
```

The frontend must apply responses according to request/version context.

Older responses must not overwrite newer authoritative state.

---

## 67. Stale Response Protection

Each query should be associated with:

* query key;
* request parameters;
* request lifecycle;
* current context.

If a response no longer matches the active query, it must not replace current state.

---

## 68. API Client Observability

The API client should expose telemetry for:

* request count;
* latency;
* error rate;
* timeout rate;
* retry count;
* cancellation count;
* endpoint;
* status;
* Business/Branch scope where safe;
* request ID;
* operation ID.

Sensitive information must not be logged.

---

## 69. Frontend Logging

Logs should not include:

* passwords;
* tokens;
* offline authorization secrets;
* sensitive personal data;
* payment credentials;
* secret configuration.

Operational logs should use safe identifiers.

---

## 70. Correlation

Where supported, frontend requests should preserve:

```text id="t8g9i5"
request_id
operation_id
correlation_id
```

These identifiers allow frontend/backend troubleshooting.

---

## 71. API Performance Targets

The frontend data-access layer should target:

| Metric                                  |                             Target |
| --------------------------------------- | ---------------------------------: |
| API client overhead                     |                        p95 ≤ 20 ms |
| Request construction                    |                         p95 ≤ 5 ms |
| Response mapping                        |                        p95 ≤ 20 ms |
| Error normalization                     |                        p95 ≤ 10 ms |
| Cached query access                     |                        p95 ≤ 50 ms |
| POS Product search                      |                       p95 ≤ 150 ms |
| Normal API query end-to-end UI handling | p95 ≤ 300 ms after server response |
| Mutation state update                   | p95 ≤ 100 ms after server response |
| Offline queue insertion                 |                        p95 ≤ 50 ms |
| Request cancellation handling           |                        p95 ≤ 50 ms |
| API data-access fatal errors            |                 < 0.1% of sessions |

These targets exclude external network latency and backend processing unless explicitly stated.

---

## 72. POS API Performance

POS requests have higher priority than administrative requests.

Target:

```text
Core POS command p95 ≤ 500 ms
```

The frontend must avoid:

* unnecessary sequential requests;
* repeated permission requests;
* redundant menu requests;
* large response payloads;
* expensive client-side transformations.

---

## 73. API Payload Discipline

API requests/responses should remain appropriately sized.

The frontend should request only necessary fields where the API supports projections.

Large datasets should use:

* pagination;
* filtering;
* summary endpoints;
* dedicated detail endpoints.

---

## 74. Batch Requests

Batch APIs may be used for:

* synchronization;
* reference data;
* efficient initial loading;
* controlled bulk operations.

Batching must not combine unrelated business transactions merely for convenience.

---

## 75. Bulk Operations

Bulk operations require explicit backend API support.

The frontend must not emulate bulk operations through uncontrolled parallel requests.

Example:

```text
Wrong:
100 × independent uncontrolled requests

Preferred:
Dedicated bulk API
```

where the backend provides appropriate transactional semantics.

---

## 76. Parallel Requests

Independent read requests may run in parallel.

Example:

```text
Dashboard
├── Sales Summary
├── Inventory Summary
├── Cash Summary
└── Notifications
```

However, parallel requests must not violate dependencies.

---

## 77. Sequential Dependencies

When request B depends on authoritative result A:

```text
Request A
   ↓
Authoritative Result
   ↓
Request B
```

Example:

```text
Open Cash Session
      ↓
Load Active Cash Session
```

The frontend must not assume A succeeded before receiving its result.

---

## 78. API Availability Failure

When the backend is unavailable:

* display a clear state;
* preserve safe local UI state;
* retry only when appropriate;
* enter offline mode only for supported operations;
* never fabricate successful server results.

---

## 79. API Client Security

The API client must:

* use HTTPS in production;
* avoid insecure transport;
* centralize authentication;
* validate response boundaries;
* avoid exposing credentials;
* prevent arbitrary endpoint construction;
* respect authorization failures;
* prevent cross-Business data reuse.

---

## 80. Endpoint Construction

Feature code should use defined endpoint builders.

Avoid arbitrary user-controlled URLs.

Example:

```text id="5h2e9r"
productsApi.get(productId)
```

rather than:

```text
request(userProvidedUrl)
```

---

## 81. CSRF / Browser Security

The API client must follow the backend/browser security model for:

* cookies;
* CSRF;
* authorization headers;
* CORS;
* same-site policies.

The frontend must not independently weaken these protections.

---

## 82. Request Headers

Common headers may include:

```text
Authorization
Content-Type
Accept
X-Request-ID
X-Operation-ID
X-Device-ID
```

Only headers defined by the API/security contract should be used.

---

## 83. Device Identity

Where the API requires device identification, the frontend may provide the registered device UUID.

Device UUID is contextual identity only.

It does not replace authentication or trusted-device validation.

---

## 84. Subscription Enforcement

The API client may prevent obviously disallowed modifying calls in read-only mode.

However:

```text
Frontend Block
    +
Backend Authorization
```

are both required.

The frontend must never remove or alter entitlement information to enable blocked functionality.

---

## 85. API Contract Evolution

When backend API changes:

1. update API contract;
2. update frontend types;
3. update mappers;
4. update queries/mutations;
5. update tests;
6. validate backward compatibility where required;
7. deploy according to compatibility rules.

Breaking changes require explicit versioning or migration strategy.

---

## 86. Backward Compatibility

During rolling deployments, frontend and backend versions may temporarily differ.

The API contract should therefore support controlled compatibility where required.

The frontend must not depend on undocumented backend fields.

---

## 87. Feature Flags

API-dependent features may be gated by feature flags.

Feature flags are not equivalent to permissions or subscription entitlements.

The final authorization decision remains backend-controlled.

---

## 88. API Mocking and Testing

The API client architecture must support mocked backend responses.

Tests should cover:

* successful requests;
* validation errors;
* authorization errors;
* conflicts;
* timeouts;
* network failures;
* retries;
* cancellation;
* pagination;
* synchronization;
* offline behavior.

---

## 89. Contract Tests

Frontend and backend API contracts should be tested to detect:

* renamed fields;
* missing fields;
* incompatible types;
* incorrect error codes;
* pagination changes;
* authentication changes;
* version incompatibility.

---

## 90. Data Access Test Boundaries

Testing should follow the architecture:

```text
API Client
    ↓
Transport Tests

Feature API
    ↓
Resource Tests

Query/Mutation
    ↓
State Integration Tests

UI
    ↓
Component / E2E Tests
```

---

## 91. Recovery Testing

The API client must be tested under:

* network interruption;
* backend restart;
* timeout;
* duplicate request;
* delayed response;
* stale response;
* expired session;
* revoked device;
* Branch switch;
* Business switch;
* synchronization conflict.

---

## 92. Offline Testing

Offline data access must verify:

* operation UUID persistence;
* queue durability;
* encrypted storage;
* retry behavior;
* partial synchronization;
* conflict handling;
* subscription restrictions;
* device authorization;
* reconnect behavior.

---

## 93. Data Access and Audit

The frontend API client must preserve operation identifiers needed for backend audit.

It must not create fake audit records.

The backend remains responsible for authoritative audit creation.

---

## 94. Data Access and Historical Integrity

The API client must preserve immutable historical values.

It must not transform:

```text
historical_price
```

into:

```text
current_product_price
```

or otherwise replace historical snapshots with current configuration.

---

## 95. Data Access and Cash Sessions

Cash-related API calls must respect Cash Session lifecycle.

Examples:

```text
openSession()
closeSession()
handover()
getCurrentSession()
```

The frontend must not infer a session as closed merely because a local request was sent.

---

## 96. Data Access and Orders

Order APIs should distinguish:

* draft;
* active;
* accepted;
* paid;
* cancelled;
* refunded where applicable.

The frontend must use backend state transitions rather than manually assigning authoritative statuses.

---

## 97. Data Access and Inventory

Inventory APIs must preserve backend transaction semantics.

The frontend must not calculate a final stock deduction and assume it is authoritative.

The backend validates:

* stock availability;
* Recipe;
* Set;
* transaction;
* concurrency.

---

## 98. Data Access and Menu/Pricing

Menu/pricing API responses should include sufficient configuration/version information for the frontend to identify:

* current price;
* Branch override;
* configuration version;
* effective state;
* pending state where applicable.

The frontend must not infer effective pricing from stale local configuration.

---

## 99. Data Access and Configuration

Configuration mutation requests should carry:

* expected version;
* operation UUID;
* relevant scope;
* changed values;
* reason where required.

The backend determines whether the change is valid.

---

## 100. Data Access and Reports

Report API responses should preserve:

* report version;
* period;
* scope;
* creation time;
* data state;
* generation status.

Historical report versions must not be overwritten by current data.

---

## 101. Data Access and Notifications

Notification APIs are read/interaction APIs.

They must not be used as authoritative sources for:

* permissions;
* subscription;
* payment;
* inventory;
* security state.

---

## 102. Data Access and Audit/History

Audit/history endpoints are read-only from the frontend perspective.

The frontend may filter and inspect them but must not mutate historical records.

---

## 103. Data Access and File Storage

The frontend should treat file storage as an external service boundary.

It should not assume:

* physical storage path;
* provider;
* filename uniqueness;
* permanent URL.

File references should use backend-approved identifiers.

---

## 104. Data Access and Background Jobs

Long operations should use job APIs.

Example:

```text id="v5g1cc"
POST /reports/export
        ↓
job_id
        ↓
GET /jobs/{job_id}
        ↓
READY
        ↓
download
```

The frontend must not keep long-running synchronous requests open unnecessarily.

---

## 105. Data Access and Notifications

Background operation completion may result in a notification.

Example:

```text id="e1q8b9"
XLSX Export
   ↓
Background Job
   ↓
Completed
   ↓
Notification
   ↓
Frontend
```

The frontend may refresh operation state based on the notification/event.

---

## 106. Request Queueing

The API client may queue requests only when the operation explicitly supports queuing.

Offline commands should use the dedicated synchronization queue.

Ordinary online requests should not silently become offline transactions.

---

## 107. Duplicate Prevention

The data-access layer should prevent accidental duplicate commands caused by:

* double-click;
* repeated submit;
* retry;
* reconnect;
* browser refresh.

UI button disabling is helpful but insufficient.

Backend idempotency remains authoritative.

---

## 108. Double Submit Protection

For critical commands:

```text
User Click
   ↓
Mutation Pending
   ↓
Disable duplicate action
   ↓
Request
   ↓
Result
```

The operation UUID remains the final duplicate-protection mechanism.

---

## 109. Browser Refresh During Mutation

If a mutation is interrupted by browser refresh:

* the frontend must not assume failure;
* the operation result should be recoverable through the API where supported;
* idempotency must prevent duplicate business effects.

This is especially important for:

* payments;
* refunds;
* Cash Session operations;
* Order acceptance;
* inventory adjustments.

---

## 110. Data Access and State Management

The API client must integrate with the state architecture defined in:

`22_Frontend_State_Management_and_Data_Flow.md`

The responsibilities remain:

```text
API Client
→ transport and API communication

Query/Mutation
→ server-state lifecycle

State Layer
→ state ownership and derived state

UI
→ presentation and user interaction
```

No layer should absorb another layer's responsibilities without architectural justification.

---

## 111. Recommended Structure

The frontend may use:

```text id="8xq6s2"
frontend/
└── src/
    ├── core/
    │   ├── api/
    │   │   ├── client/
    │   │   │   ├── httpClient
    │   │   │   ├── request
    │   │   │   ├── response
    │   │   │   ├── errors
    │   │   │   ├── retry
    │   │   │   ├── timeout
    │   │   │   └── cancellation
    │   │   ├── auth/
    │   │   ├── context/
    │   │   ├── pagination/
    │   │   ├── uploads/
    │   │   ├── downloads/
    │   │   └── synchronization/
    │   │
    │   ├── cache/
    │   ├── errors/
    │   ├── events/
    │   └── telemetry/
    │
    ├── features/
    │   ├── products/
    │   │   ├── api/
    │   │   ├── queries/
    │   │   ├── mutations/
    │   │   ├── mappers/
    │   │   └── types/
    │   ├── orders/
    │   ├── payments/
    │   ├── cash/
    │   ├── inventory/
    │   ├── menu/
    │   ├── reports/
    │   ├── notifications/
    │   └── settings/
    │
    └── offline/
        ├── api/
        ├── queue/
        ├── storage/
        ├── sync/
        └── conflicts/
```

---

## 112. API Client Dependency Rules

The dependency direction should be:

```text
UI
 ↓
Feature Query / Mutation
 ↓
Feature API
 ↓
Core API Client
 ↓
Transport
```

The following is prohibited:

```text
UI
 ↓
Raw HTTP Client
```

Feature APIs must not directly depend on UI components.

---

## 113. API Client and Domain Separation

The frontend must not duplicate backend Domain Services.

For example, the frontend should not implement authoritative:

* inventory deduction rules;
* payroll calculation;
* payment validation;
* cash reconciliation;
* recipe validation;
* subscription lifecycle;
* permission granting.

The frontend may perform local validation for usability.

---

## 114. API Client and Security Separation

The API client participates in security but does not define security policy.

Backend remains authoritative for:

* authentication;
* authorization;
* Business isolation;
* Branch isolation;
* subscription entitlement;
* trusted devices;
* offline authorization;
* idempotency;
* audit.

---

## 115. API Client and Performance

The data-access architecture must support the performance principle:

> Fast operations should remain fast without sacrificing correctness.

The frontend should prefer:

* cached reference data;
* compact responses;
* selective invalidation;
* request deduplication;
* pagination;
* controlled concurrency;
* background processing.

---

## 116. API Client and Accessibility

Data loading and error states must remain accessible.

The UI should provide:

* meaningful loading indicators;
* accessible error messages;
* retry controls;
* clear offline status;
* keyboard-accessible operation controls.

Technical request details should not be required to understand the current application state.

---

## 117. AI-Agent Development Rules

AI coding agents must follow these rules:

1. Do not add raw HTTP requests inside components.
2. Reuse the central API client.
3. Reuse standard error mapping.
4. Reuse operation UUID handling.
5. Reuse authentication handling.
6. Reuse Business/Branch context propagation.
7. Reuse query/cache conventions.
8. Do not invent new retry policies for individual endpoints.
9. Do not bypass offline synchronization.
10. Do not bypass subscription restrictions.
11. Do not bypass permission checks.
12. Do not directly access backend storage.
13. Do not silently transform historical values.
14. Do not create duplicate API clients.
15. Add tests for new endpoints and mutations.

Before adding a new data-access mechanism, inspect the existing `core/api` architecture first.

---

## 118. Change Management

A data-access architecture change should identify:

* affected endpoint;
* API version;
* request type;
* response type;
* mapper;
* query/mutation;
* cache impact;
* authentication impact;
* permission impact;
* Business/Branch scope;
* offline impact;
* synchronization impact;
* error handling;
* retry behavior;
* performance impact;
* testing requirements.

Breaking API changes require explicit migration planning.

---

## 119. System Invariants

The following invariants apply to the frontend API client and data-access architecture:

1. All API communication uses the centralized data-access architecture.
2. UI components do not perform arbitrary HTTP requests.
3. API clients do not contain authoritative business rules.
4. Backend remains authoritative for business decisions.
5. Authentication handling is centralized.
6. Authorization failures are handled explicitly.
7. Business context is validated by the backend.
8. Branch context is validated by the backend.
9. Subscription entitlement is validated by the backend.
10. Client-provided identifiers never replace backend authorization.
11. API request types are explicit.
12. API response types are explicit.
13. DTO mapping occurs at a defined boundary.
14. Invalid responses are not silently accepted.
15. API errors are normalized.
16. Error handling uses stable categories.
17. Request IDs are preserved where supported.
18. Operation UUIDs are reused for safe retries.
19. Duplicate business effects are prevented through backend idempotency.
20. Financial operations are not blindly retried.
21. Timeouts do not imply business-operation failure.
22. Unknown mutation results are recoverable through authoritative APIs where supported.
23. Automatic retries are limited to safe/retryable cases.
24. Authorization errors are not blindly retried.
25. Validation errors are not blindly retried.
26. Important conflicts are not silently overwritten.
27. Configuration updates use optimistic concurrency where required.
28. Stale configuration versions become conflicts.
29. Cache is not authoritative.
30. Cache keys include required Business scope.
31. Cache keys include required Branch scope.
32. Historical transaction state is not replaced by current state.
33. Query invalidation follows successful mutations.
34. Unrelated cache entries are not unnecessarily invalidated.
35. Identical read requests may be deduplicated.
36. Stale responses cannot overwrite newer state.
37. Pagination is used for large datasets.
38. Filters are typed.
39. Sorting fields are controlled.
40. Arbitrary SQL expressions are never sent from the frontend.
41. Bulk operations require explicit backend support.
42. Ordinary online requests do not silently become offline commands.
43. Only explicitly supported operations may work offline.
44. Offline commands use persistent operation UUIDs.
45. Offline authorization is not invented by the frontend.
46. Offline data is securely persisted.
47. Synchronization uses dedicated APIs.
48. Partial synchronization results are handled individually.
49. Synchronization conflicts remain explicit.
50. Business and Branch state is isolated.
51. Authentication state is isolated from UI state.
52. Logout clears protected state.
53. Session expiration is handled explicitly.
54. Re-authentication does not automatically close Cash Sessions.
55. Read-only subscription state does not bypass backend restrictions.
56. File downloads use authorized backend mechanisms.
57. File storage paths are not exposed as trusted frontend data.
58. Large exports use asynchronous processing.
59. Report data remains backend-authoritative.
60. Audit records cannot be modified through the frontend.
61. Notification state does not grant authorization.
62. Cash Session state is backend-authoritative.
63. Payment state is backend-authoritative.
64. Inventory deduction is backend-authoritative.
65. Order status transitions are backend-authoritative.
66. Menu/pricing effective state is backend-authoritative.
67. Configuration versions are preserved.
68. Historical prices remain immutable.
69. Historical financial snapshots remain immutable.
70. Operation ordering is respected where required.
71. Independent read operations may run in parallel.
72. Dependent operations wait for authoritative results.
73. Request cancellation does not cancel committed business operations.
74. API client logs never expose secrets.
75. Request telemetry is safe and privacy-aware.
76. Device UUID is contextual identity, not authentication.
77. API version is explicit.
78. Undocumented backend fields are not required by the frontend.
79. Breaking API changes require explicit migration handling.
80. API client dependencies follow the defined architecture.
81. Feature APIs do not depend on UI components.
82. UI does not depend directly on transport implementation.
83. API client does not implement Domain Services.
84. Frontend validation improves usability but does not replace backend validation.
85. Data-access failures do not fabricate successful results.
86. Browser refresh does not create duplicate business transactions.
87. Double submit protection uses both UI controls and backend idempotency.
88. Offline queue state survives application restart where required.
89. Synchronization retries preserve operation identity.
90. Data-access state remains compatible with frontend state architecture.
91. Data-access state remains compatible with backend API contracts.
92. API performance remains within defined targets.
93. POS data access receives priority over non-operational workloads.
94. Large payloads are avoided where possible.
95. Large client-side transformations do not block the main UI thread.
96. API requests remain observable.
97. Critical errors remain diagnosable through request/operation identifiers.
98. Data-access changes include appropriate tests.
99. Security boundaries cannot be bypassed through API-client changes.
100. Data-access architecture must preserve historical integrity over UI convenience.

---

## Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/02_Frontend_Project_Structure.md`
* `docs/04_Architecture/07_Frontend/05_Authentication_and_Session_UI.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/10_Order_Management_UI.md`
* `docs/04_Architecture/07_Frontend/11_Cash_Register_and_Cash_Session_UI.md`
* `docs/04_Architecture/07_Frontend/12_Inventory_and_Warehouse_UI.md`
* `docs/04_Architecture/07_Frontend/18_Audit_and_History_UI.md`
* `docs/04_Architecture/07_Frontend/19_Subscription_and_Entitlement_UI.md`
* `docs/04_Architecture/07_Frontend/20_Offline_Mode_and_Synchronization_UI.md`
* `docs/04_Architecture/07_Frontend/21_Settings_and_Business_Configuration_UI.md`
* `docs/04_Architecture/07_Frontend/22_Frontend_State_Management_and_Data_Flow.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/02_Database_Architecture.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/23_Configuration_Data_Model.md`
* `docs/04_Architecture/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/04_Architecture/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### API

* `docs/09_API/README.md`
* `docs/09_API/01_API_Architecture.md`
* `docs/09_API/02_API_Authentication_and_Authorization.md`
* `docs/09_API/03_API_Error_and_Response_Standards.md`
* `docs/09_API/04_API_Versioning_and_Compatibility.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## Status

**Frontend Architecture:** Proposed

**Version:** 1.0

**Current Document:** `23_Frontend_API_Client_and_Data_Access_Architecture.md`

**Previous Document:** `22_Frontend_State_Management_and_Data_Flow.md`

**Next Document:** `24_Frontend_Offline_Storage_and_Local_Persistence_Architecture.md`

