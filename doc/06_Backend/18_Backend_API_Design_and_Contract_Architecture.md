# Backend API Design and Contract Architecture

**Document ID:** BA-18
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This document defines the API design and contract architecture for FastFood ERP.

The API must provide a stable, secure and predictable interface between:

* Web frontend;
* POS clients;
* trusted offline devices;
* background workers where API interaction is required;
* future external integrations.

The API must expose application capabilities without exposing internal database structure or domain implementation details.

The API is not a direct CRUD interface to PostgreSQL.

Business operations must be represented through explicit application use cases.

---

## 2. API Design Principles

The API follows these principles:

1. API contracts must be explicit.
2. API routes must remain thin.
3. Business logic belongs to the Application and Domain layers.
4. Clients must never be trusted with Business or Branch authorization.
5. PostgreSQL is never exposed directly.
6. Resource identity uses UUIDs where appropriate.
7. Retryable operations use idempotency keys/operation UUIDs.
8. Historical financial data is never silently recalculated.
9. Errors must be structured and predictable.
10. API versioning must be explicit.
11. Pagination must be bounded.
12. Large operations should be asynchronous.
13. Offline synchronization has a dedicated API contract.
14. API behavior must remain compatible with the frontend and POS clients.
15. Security controls must not introduce unnecessary POS friction.
16. API performance must support the defined backend SLOs.
17. API contracts must be testable automatically.

---

## 3. API Architectural Position

The API is positioned between clients and the Application layer:

```text
Client
  ↓
HTTP / API
  ↓
Authentication
  ↓
Authorization
  ↓
Request Validation
  ↓
Application Use Case
  ↓
Domain
  ↓
Repository
  ↓
PostgreSQL
```

The API must not bypass the Application layer.

---

## 4. API Responsibilities

The API layer is responsible for:

* HTTP routing;
* request parsing;
* schema validation;
* authentication integration;
* authorization integration;
* request context creation;
* response serialization;
* HTTP status mapping;
* API error formatting;
* pagination;
* API-level rate limiting;
* idempotency header extraction;
* request correlation.

The API layer must not contain core business rules.

---

## 5. Application Layer Responsibilities

The Application layer is responsible for:

* use case execution;
* transaction boundaries;
* authorization orchestration;
* business scope validation;
* domain invocation;
* repository coordination;
* idempotency handling;
* audit/outbox creation;
* synchronization orchestration.

Example:

```text
POST /orders/{order_id}/accept
        ↓
AcceptOrderUseCase
        ↓
Domain validation
        ↓
Inventory deduction
        ↓
Order state change
        ↓
Audit / Outbox
        ↓
Commit
```

The route itself must not implement this workflow.

---

## 6. Domain Layer Responsibilities

The Domain layer owns business behavior and invariants.

Examples:

* Order state transitions;
* pricing rules;
* discount rules;
* markup rules;
* inventory rules;
* Recipe requirements;
* Cash Session rules;
* payroll calculations;
* configuration version rules.

The Domain layer must not depend on HTTP.

---

## 7. API Style

The backend primarily uses REST-style HTTP APIs.

REST-style resources should be used for:

* Business;
* Branch;
* Employee;
* Product;
* Recipe;
* Inventory;
* Order;
* Payment;
* Cash Session;
* Report;
* Notification;
* Configuration.

Explicit command endpoints may be used for business operations that are not simple CRUD.

Examples:

```text
POST /orders/{order_id}/accept
POST /orders/{order_id}/pay
POST /orders/{order_id}/refund
POST /cash-sessions/{session_id}/close
POST /recipes/{recipe_id}/approve
POST /handover/{handover_id}/accept
```

---

## 8. API Base Path

The API should use an explicit versioned base path:

```text
/api/v1
```

Example:

```text
/api/v1/orders
/api/v1/products
/api/v1/employees
```

The version identifies the public API contract version.

Internal Application/Domain changes do not require an API version change when the public contract remains compatible.

---

## 9. API Versioning Strategy

The initial strategy is URI versioning:

```text
/api/v1/...
```

A new major contract may use:

```text
/api/v2/...
```

A new version is required when an incompatible change is introduced.

Examples of potentially breaking changes:

* removing a required response field;
* changing a field type;
* changing semantic meaning;
* changing authentication requirements;
* changing error contract incompatibly;
* removing an endpoint;
* changing enum semantics incompatibly.

---

## 10. Backward Compatibility

Compatible changes may include:

* adding optional response fields;
* adding new endpoints;
* adding optional request fields;
* adding new non-breaking filters;
* improving error descriptions without changing error codes.

Clients must not depend on undocumented fields.

---

## 11. API Resource Identity

Resources should use UUID-based identifiers.

Example:

```json
{
  "id": "018f7e7c-..."
}
```

Client-provided UUIDs must not automatically grant authority.

The server validates:

* existence;
* Business ownership;
* Branch scope;
* resource state;
* authorization.

---

## 12. Operation UUID

Retryable business operations use an operation UUID.

Example:

```http
Idempotency-Key: 8d6c2d6e-...
```

The backend treats the operation UUID as an idempotency identity.

The operation UUID is separate from:

* Employee UUID;
* Device UUID;
* Business UUID;
* Branch UUID;
* Resource UUID.

---

## 13. Idempotency Contract

Retryable commands must support idempotency.

Example:

```text
Request 1:
POST /orders/{id}/pay
Idempotency-Key: X

→ Payment successful

Request 2:
POST /orders/{id}/pay
Idempotency-Key: X

→ Same authoritative result
```

The second request must not create another payment.

---

## 14. Idempotency Rules

The server must store sufficient information to determine whether an operation has already been processed.

The system must detect:

* same operation UUID;
* same Business;
* same authenticated actor/device context where required;
* same operation type;
* conflicting payload reuse.

Reusing the same idempotency key with materially different payload must return a conflict.

---

## 15. Request ID

Every API request should receive a request identifier.

Example:

```http
X-Request-ID: 01J...
```

If the client provides a valid request ID, the server may preserve it subject to validation.

Request ID is used for:

* logging;
* tracing;
* debugging;
* support.

Request ID is not an authorization credential.

---

## 16. Correlation and Operation Context

Important requests should be traceable through:

```text
Request ID
Operation UUID
Business UUID
Branch UUID
Employee UUID
Device UUID
Cash Session UUID
```

Not every request requires every field.

The backend should include only applicable context.

---

## 17. Authentication

Authentication determines the actor identity.

The API may use:

* session-based authentication;
* access tokens;
* refresh tokens;
* trusted device credentials;
* offline signed authorization for synchronization.

The exact authentication mechanism follows:

`06_Authentication_and_Authorization.md`

---

## 18. Authorization

Every protected endpoint must validate:

1. authenticated actor;
2. Employee status;
3. Business scope;
4. Branch scope;
5. permission;
6. subscription entitlement;
7. device restrictions where required;
8. resource ownership/scope;
9. business rules.

The API must fail closed.

---

## 19. Business Context

The client may send Business context, but it is not authoritative.

Example:

```http
X-Business-ID: <uuid>
```

or request payload:

```json
{
  "business_id": "..."
}
```

The server must verify that the authenticated actor is allowed to operate within that Business.

A client cannot switch Business merely by changing a UUID.

---

## 20. Branch Context

Branch context may be represented by:

```http
X-Branch-ID: <uuid>
```

or an explicit request field.

The server must validate the employee's Branch scope.

When Branch context changes, the backend recalculates:

* permissions;
* menu configuration;
* pricing configuration;
* operational context.

---

## 21. Context Headers

Headers such as Business and Branch identifiers are context hints, not authorization credentials.

Example:

```http
X-Business-ID
X-Branch-ID
X-Device-ID
X-Request-ID
Idempotency-Key
```

The server must never trust these values without authorization validation.

---

## 22. Request Validation

Every request must be validated at the API boundary.

Validation includes:

* required fields;
* data types;
* UUID format;
* string length;
* numeric range;
* enum values;
* date/time format;
* pagination limits;
* nested object structure.

Business validation remains in the Application/Domain layers.

---

## 23. Validation Separation

Example:

```text
API validation:
quantity must be a positive number

Domain validation:
quantity cannot exceed available business rule limit
```

The API should reject malformed input.

The Domain should reject invalid business behavior.

---

## 24. Response Envelope

The API may use a consistent response structure where useful.

Successful resource example:

```json
{
  "data": {
    "id": "018f...",
    "name": "Burger"
  }
}
```

List example:

```json
{
  "data": [],
  "pagination": {
    "next_cursor": "...",
    "has_more": true
  }
}
```

The exact envelope should remain consistent across API modules.

---

## 25. Error Response Contract

Errors must use a predictable structure.

Example:

```json
{
  "error": {
    "code": "ORDER_ALREADY_PAID",
    "message": "The order has already been paid.",
    "request_id": "01J...",
    "details": {}
  }
}
```

The client should rely primarily on `code`, not human-readable `message`.

---

## 26. Error Codes

Error codes must be stable identifiers.

Examples:

```text
AUTHENTICATION_REQUIRED
AUTHENTICATION_FAILED
ACCESS_DENIED
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
SUBSCRIPTION_READ_ONLY
RESOURCE_NOT_FOUND
VALIDATION_ERROR
BUSINESS_RULE_VIOLATION
CONFLICT
STALE_VERSION
DUPLICATE_OPERATION
INSUFFICIENT_STOCK
ORDER_ALREADY_PAID
CASH_SESSION_CLOSED
INVALID_OFFLINE_AUTHORIZATION
SYNC_CONFLICT
RATE_LIMITED
INTERNAL_ERROR
SERVICE_UNAVAILABLE
```

Error codes must not expose sensitive internal details.

---

## 27. HTTP Status Mapping

Initial mapping:

| Situation                      | HTTP |
| ------------------------------ | ---: |
| Success                        |  200 |
| Created                        |  201 |
| Accepted / async operation     |  202 |
| No Content                     |  204 |
| Validation error               |  400 |
| Authentication required/failed |  401 |
| Authorization denied           |  403 |
| Resource not found             |  404 |
| Conflict                       |  409 |
| Semantic validation            |  422 |
| Rate limited                   |  429 |
| Internal error                 |  500 |
| Temporary unavailable          |  503 |

The exact mapping must remain stable once public clients depend on it.

---

## 28. Resource Not Found vs Authorization

The API may intentionally return `404` for resources the actor is not allowed to discover when this reduces information leakage.

For explicitly authenticated but unauthorized operations, `403` may be used.

The choice must be consistent with the security policy of each endpoint.

---

## 29. Pagination

List endpoints must use bounded pagination.

Preferred approach:

**Cursor-based pagination.**

Example:

```text
GET /api/v1/orders?limit=50&cursor=...
```

The server must enforce a maximum page size.

Example initial limits:

```text
default = 50
maximum = 100
```

Large datasets must not be returned in a single request.

---

## 30. Pagination Stability

Pagination must provide deterministic ordering.

A stable unique field should be included in the ordering where necessary.

Example:

```text
created_at DESC
id DESC
```

This prevents duplicate or missing records when multiple records share the same timestamp.

---

## 31. Filtering

Filtering should use explicit query parameters.

Example:

```text
GET /orders?status=PAID
GET /orders?branch_id=...
GET /orders?from=...&to=...
```

Filters must be:

* validated;
* authorization-aware;
* bounded;
* indexed where frequently used.

---

## 32. Sorting

Only supported sort fields may be accepted.

Example:

```text
GET /orders?sort=-created_at
```

The API must not directly inject client-provided SQL expressions into queries.

---

## 33. Search

Search endpoints must:

* validate input;
* enforce length limits;
* respect Business/Branch scope;
* avoid unbounded database scans where possible;
* use appropriate indexes.

Search must never bypass authorization.

---

## 34. Resource Creation

Creation endpoints should return the created resource or sufficient representation.

Example:

```http
POST /api/v1/products
```

Response:

```http
201 Created
```

The backend generates authoritative identifiers where appropriate.

---

## 35. Resource Update

Simple configuration updates may use:

```http
PATCH /api/v1/products/{product_id}
```

Only permitted fields may be updated.

Important business operations should use explicit command endpoints instead of generic PATCH.

---

## 36. Why Generic CRUD Is Limited

Operations such as:

```text
Accept Order
Pay Order
Refund Order
Close Cash Session
Approve Recipe
Approve Configuration
Adjust Inventory
```

are business operations rather than simple field updates.

They should therefore be represented explicitly.

This makes:

* authorization;
* audit;
* transaction boundaries;
* idempotency;
* validation;
* concurrency

clearer.

---

## 37. Optimistic Concurrency

Configuration resources should expose a version.

Example:

```json
{
  "id": "...",
  "version": 12
}
```

The update may include:

```http
If-Match: "12"
```

or an explicit version field.

If the current version is different:

```text
409 Conflict
STALE_VERSION
```

The server must not silently overwrite newer configuration.

---

## 38. ETag and Conditional Requests

ETag may be used for:

* Business configuration;
* Branch configuration;
* Menu;
* Product configuration;
* read-heavy resources.

Conditional requests can reduce unnecessary data transfer.

ETag must never replace authorization.

---

## 39. Cash Session API

Typical endpoints:

```text
POST /cash-sessions
GET  /cash-sessions/{id}
POST /cash-sessions/{id}/close
GET  /cash-sessions/{id}/report
```

The backend validates:

* Branch;
* Cash Register;
* employee;
* active session;
* permissions;
* state;
* idempotency;
* concurrency.

---

## 40. Order API

Typical endpoints:

```text
POST /orders
GET  /orders/{id}
PATCH /orders/{id}
POST /orders/{id}/accept
POST /orders/{id}/cancel
POST /orders/{id}/pay
POST /orders/{id}/refund
```

Ordinary `PATCH` must not bypass state or financial rules.

---

## 41. Order Item API

Order items may be managed through:

```text
POST /orders/{order_id}/items
PATCH /orders/{order_id}/items/{item_id}
DELETE /orders/{order_id}/items/{item_id}
```

The server must calculate authoritative pricing and validate:

* Product state;
* Branch availability;
* Recipe;
* Set configuration;
* inventory;
* permissions;
* Order state.

Client-provided totals must not be trusted as authoritative.

---

## 42. Pricing API

Pricing endpoints may include:

```text
GET   /products/{id}/price
PATCH /products/{id}/price
PATCH /branches/{branch_id}/products/{id}/price
```

Important price changes require:

* permission;
* version;
* audit;
* effective configuration;
* historical integrity.

---

## 43. Discount API

Discount application should be explicit:

```text
POST /orders/{order_id}/discounts
```

The server validates:

* permission;
* Branch scope;
* subscription;
* Order state;
* discount limits;
* financial calculation.

Discount must not mutate the Product's configured base price.

---

## 44. Payment API

Payment should be represented as a business command:

```text
POST /orders/{order_id}/payments
```

Request example:

```json
{
  "method": "CASH",
  "amount": 25000
}
```

The backend remains authoritative for:

* payment state;
* amount;
* Order status;
* duplicate prevention.

---

## 45. Refund API

Refund:

```text
POST /orders/{order_id}/refunds
```

Required information may include:

```json
{
  "amount": 25000,
  "reason": "Incorrect order"
}
```

The backend validates:

* permission;
* approval requirement;
* historical transaction amount;
* refund limits;
* idempotency.

---

## 46. Inventory API

Typical operations:

```text
GET  /inventory
POST /inventory/receipts
POST /inventory/exits
POST /inventory/adjustments
GET  /inventory/transactions
```

Inventory modification endpoints must use explicit business commands.

Client-provided final stock values must not overwrite authoritative inventory state without validation.

---

## 47. Recipe API

Typical endpoints:

```text
POST /recipes
PATCH /recipes/{id}
POST /recipes/{id}/submit
POST /recipes/{id}/approve
POST /recipes/{id}/archive
GET  /recipes/{id}/versions
```

Approval is a business operation.

The API must preserve historical Recipe Versions.

---

## 48. Menu API

Typical endpoints:

```text
GET   /menu
PATCH /menu/products/{product_id}
PATCH /branches/{branch_id}/menu/products/{product_id}
```

The backend must distinguish:

* Business menu;
* Branch availability;
* Product active state;
* inventory availability;
* equipment availability.

---

## 49. Employee API

Typical endpoints:

```text
GET  /employees
POST /employees
GET  /employees/{id}
PATCH /employees/{id}
POST /employees/{id}/deactivate
POST /employees/{id}/activate
```

Employee permissions should be managed through explicit permission operations rather than arbitrary JSON replacement.

---

## 50. Permission API

Example:

```text
GET  /employees/{id}/permissions
PUT  /employees/{id}/permissions
POST /employees/{id}/permissions/overrides
DELETE /employees/{id}/permissions/overrides/{permission}
```

The server must validate Manager authority before allowing permission changes.

---

## 51. Branch Switching API

If the client changes Branch context, the backend may provide:

```text
POST /session/branch-context
```

or equivalent session/context operation.

The server recalculates:

* effective permissions;
* Branch configuration;
* menu;
* pricing;
* device context.

Client-side Branch switching alone is not authoritative.

---

## 52. Report API

Reports should support asynchronous generation where necessary.

Example:

```text
POST /reports
GET  /reports/{id}
GET  /reports/{id}/versions
POST /reports/{id}/exports
GET  /exports/{id}
```

Large report generation should normally return:

```http
202 Accepted
```

with a job/report identifier.

---

## 53. Notification API

Typical endpoints:

```text
GET  /notifications
POST /notifications/{id}/read
POST /notifications/read-all
```

The API must ensure:

* recipient ownership;
* Business scope;
* Branch scope;
* correct notification state.

---

## 54. File API

File operations should use metadata resources.

Example:

```text
POST /files
GET  /files/{id}
GET  /files/{id}/download
DELETE /files/{id}
```

File authorization must be checked before access.

Raw filesystem paths must never be exposed.

---

## 55. Synchronization API

Offline synchronization should have a dedicated API:

```text
POST /sync/batches
GET  /sync/batches/{id}
```

A batch may contain multiple operations.

The server returns per-operation results where required.

Example:

```json
{
  "batch_id": "...",
  "results": [
    {
      "operation_id": "...",
      "status": "ACCEPTED"
    },
    {
      "operation_id": "...",
      "status": "CONFLICT"
    }
  ]
}
```

---

## 56. Synchronization Result States

Initial states:

```text
ACCEPTED
ALREADY_PROCESSED
REJECTED
CONFLICT
INVALID
UNAUTHORIZED
TEMPORARY_FAILURE
```

The client must not interpret `TEMPORARY_FAILURE` as a permanent business rejection.

---

## 57. Synchronization Idempotency

Every synchronization operation must have a stable operation UUID.

If the same operation is received again:

```text
ALREADY_PROCESSED
```

or the original authoritative result should be returned.

Duplicate synchronization must not duplicate:

* Orders;
* Payments;
* Inventory Transactions;
* Configuration changes.

---

## 58. Batch Limits

Synchronization batches must be bounded.

Initial target:

```text
maximum = 100 operations per batch
```

The exact limit may be configurable.

The server must reject or split oversized requests rather than allowing unbounded memory or transaction usage.

---

## 59. Partial Synchronization

A batch does not necessarily represent one database transaction.

Individual operations may succeed or fail independently.

Example:

```text
Operation 1 → ACCEPTED
Operation 2 → ACCEPTED
Operation 3 → CONFLICT
Operation 4 → INVALID
```

The client must receive enough information to retry only retryable operations.

---

## 60. API Rate Limiting

Rate limiting should apply to:

* authentication;
* password/reset operations;
* expensive reports;
* synchronization;
* file upload;
* public endpoints;
* administrative operations.

Core POS traffic should use appropriate limits that do not unnecessarily interrupt normal operation.

Rate limits may be scoped by:

* IP;
* Employee;
* Device;
* Business;
* endpoint;
* operation type.

---

## 61. Rate Limit Response

When rate limited:

```http
429 Too Many Requests
```

Response may include:

```http
Retry-After: 10
```

The error code should be:

```text
RATE_LIMITED
```

---

## 62. API Security Headers

The API should use appropriate security headers according to deployment architecture.

Examples may include:

* HSTS;
* content-type protection;
* frame protection;
* cache-control for sensitive responses.

Security headers must be compatible with the frontend and deployment architecture.

---

## 63. CORS

CORS must use an explicit allowed-origin configuration.

Production must not use unrestricted:

```text
Access-Control-Allow-Origin: *
```

for authenticated browser APIs unless explicitly justified.

Credentials must only be allowed for trusted origins.

---

## 64. CSRF

If browser authentication uses cookies, CSRF protection is required.

If token-based authentication is used in a way that is not automatically sent by the browser, CSRF exposure differs and must be evaluated accordingly.

The API architecture must not assume that authentication alone solves CSRF.

---

## 65. TLS

Production API traffic must use HTTPS.

Sensitive credentials and tokens must never be transmitted over plaintext HTTP.

Internal services should also use protected transport where required by the deployment architecture.

---

## 66. Sensitive Data Exposure

API responses must not expose:

* password hashes;
* secret keys;
* private signing keys;
* internal credentials;
* unnecessary security metadata;
* internal filesystem paths;
* database connection details.

Error responses must not expose stack traces in production.

---

## 67. API Logging

API logs should contain:

* timestamp;
* request ID;
* operation UUID where applicable;
* endpoint;
* HTTP method;
* response status;
* latency;
* Business scope;
* Branch scope where applicable;
* Employee/device context where appropriate.

Logs must not contain:

* passwords;
* access tokens;
* refresh tokens;
* private keys;
* sensitive secrets.

---

## 68. API Audit

Security-sensitive and business-significant API operations should generate audit events through the Application layer.

Examples:

* price change;
* permission change;
* refund;
* cash correction;
* inventory adjustment;
* recipe approval;
* employee deactivation;
* configuration change.

Not every GET request requires a business audit record.

---

## 69. API and Audit Separation

API access logging and business audit are different concepts.

API logging answers:

> What request reached the backend?

Business audit answers:

> What important business state changed, who changed it, and why?

Both may reference the same request/operation context.

---

## 70. API Performance

Initial API targets:

| Operation                            |   Target |
| ------------------------------------ | -------: |
| Ordinary authenticated API p95       | ≤ 300 ms |
| Ordinary authenticated API p99       | ≤ 800 ms |
| Core POS command p95                 | ≤ 500 ms |
| Authorization overhead p95           | ≤ 100 ms |
| Cached authorization lookup p95      |  ≤ 20 ms |
| Business/Branch scope validation p95 |  ≤ 50 ms |
| Idempotency lookup p95               |  ≤ 50 ms |
| Normal sync batch p95                |    ≤ 1 s |
| Normal indexed DB query p95          | ≤ 100 ms |

External dependencies are excluded from ordinary core API latency targets where appropriate.

---

## 71. API Availability SLO

Initial API availability target:

**≥ 99.9% monthly**

For critical security and data correctness:

* Business isolation: 100%;
* Branch authorization boundary: 100%;
* duplicate financial operation prevention: ≥ 99.99%;
* mandatory audit event creation: ≥ 99.99%.

Security controls must fail closed when authoritative authorization state cannot be established.

---

## 72. API Timeout Strategy

Every external or potentially slow operation must have bounded timeouts.

Examples:

* database query timeout;
* Redis timeout;
* storage timeout;
* email provider timeout;
* external API timeout.

API requests must not wait indefinitely.

Long operations should use asynchronous jobs.

---

## 73. Asynchronous API Operations

Operations suitable for asynchronous execution include:

* large report generation;
* XLSX export;
* large file processing;
* background data cleanup;
* subscription deletion;
* large synchronization jobs where required.

The API should return:

```http
202 Accepted
```

with a status resource.

---

## 74. Async Job Status

Example:

```text
POST /reports
        ↓
202 Accepted
        ↓
{
  "job_id": "..."
}
```

Client:

```text
GET /jobs/{job_id}
```

Possible states:

```text
PENDING
PROCESSING
COMPLETED
FAILED
CANCELLED
```

The job state must be authoritative on the server.

---

## 75. API Retry Rules

Clients may retry when:

* network connection failed;
* request timeout occurred;
* `503` returned;
* operation is explicitly documented as retryable.

Clients must use idempotency for retryable state-changing commands.

Clients must not blindly retry all `4xx` responses.

---

## 76. API Error Retryability

Errors should indicate whether retry is appropriate through stable error semantics.

Example:

```text
INSUFFICIENT_STOCK
→ Do not retry automatically

STALE_VERSION
→ Refresh and retry after user decision

SERVICE_UNAVAILABLE
→ Retry with bounded backoff

TEMPORARY_SYNC_FAILURE
→ Retry later
```

---

## 77. API Contract Testing

Every public API module must have contract tests.

Contract tests verify:

* endpoint;
* HTTP method;
* request schema;
* response schema;
* status code;
* error code;
* authentication requirement;
* authorization requirement;
* pagination behavior.

Contract tests run in CI.

---

## 78. API Schema Generation

The backend should expose a machine-readable API specification such as OpenAPI.

The specification should describe:

* endpoints;
* parameters;
* request bodies;
* response bodies;
* authentication;
* error schemas;
* pagination;
* enums.

Generated API documentation must reflect the implemented contract.

---

## 79. OpenAPI as Contract

The API specification should be treated as a controlled artifact.

Changes must be reviewed for:

* backward compatibility;
* security impact;
* frontend impact;
* mobile/POS impact;
* documentation impact.

The generated schema must not be manually changed in a way that diverges from implementation.

---

## 80. API Deprecation

Deprecated endpoints must have a documented migration path.

Deprecation should include:

* replacement endpoint;
* deprecation date;
* expected removal date;
* client impact;
* migration instructions.

Deprecated endpoints should not disappear without an explicit compatibility decision.

---

## 81. API Resource Naming

Resource names should be predictable and consistent.

Preferred:

```text
/businesses
/branches
/employees
/products
/recipes
/orders
/payments
/cash-sessions
/reports
/notifications
```

Avoid inconsistent combinations such as:

```text
/getProducts
/createOrder
/doPayment
```

HTTP methods communicate basic CRUD intent, while command endpoints communicate business actions.

---

## 82. Nested Resources

Nested resources may be used when the relationship is strong and the URL remains practical.

Example:

```text
/orders/{order_id}/items
/orders/{order_id}/payments
/branches/{branch_id}/employees
```

Deep nesting should be avoided.

Example:

```text
/businesses/{b}/branches/{br}/employees/{e}/orders/{o}/items/{i}
```

should generally be avoided in favor of direct resource endpoints plus authorization context.

---

## 83. Bulk APIs

Bulk endpoints may be used for bounded administrative operations.

Example:

```text
POST /employees/bulk-update
```

Bulk APIs must:

* have strict size limits;
* validate every item;
* return per-item results where needed;
* avoid unbounded transactions;
* support idempotency where state changes are retryable.

---

## 84. Batch vs Transaction

An API batch must not automatically mean one database transaction.

Example:

```text
100 sync operations
```

may produce:

```text
70 accepted
20 conflicts
10 invalid
```

This is preferable to one huge transaction when operations are independently processable.

---

## 85. API and Offline POS

Offline POS must not depend on a real-time API connection for already-authorized local operations.

When online:

```text
API
 ↓
Server authoritative configuration
 ↓
Trusted device
 ↓
Local encrypted storage
```

When offline:

```text
Local authorized operation
 ↓
Local transaction
 ↓
Sync queue
 ↓
API when connection returns
```

---

## 86. Offline API Reconciliation

Synchronization requests must contain enough context for server validation.

Possible metadata:

```text
operation_id
device_id
employee_id
branch_id
business_id
created_at
client_sequence
entity_id
operation_type
payload
signature
```

The server remains authoritative.

Client timestamps must not override server validation.

---

## 87. API and Configuration Versioning

Configuration APIs should expose version information.

Example:

```json
{
  "configuration_version": 12
}
```

Clients may use this value to determine whether local state is stale.

A stale configuration update must return a conflict rather than silently overwriting the newer version.

---

## 88. API and Historical Integrity

API operations must never use current configuration to reinterpret historical transactions.

Examples:

```text
Current Product Price
≠
Historical Order Item Price
```

```text
Current Recipe
≠
Historical Inventory Deduction Recipe Version
```

```text
Current Set Configuration
≠
Historical Set Order Configuration
```

---

## 89. API and Financial Precision

Money fields should use explicit decimal representation.

Example:

```json
{
  "amount": "25000.00"
}
```

The exact JSON representation must be standardized across the API.

Clients must not send floating-point values that can introduce ambiguity.

---

## 90. API Date/Time Contract

The API should use ISO 8601 timestamps.

Example:

```text
2026-10-06T10:30:00Z
```

Server-side timestamps are authoritative for important events.

Client timestamps may be retained as metadata where needed for offline synchronization.

---

## 91. API Timezone Contract

The API should distinguish:

* UTC timestamps;
* Business timezone;
* Branch timezone;
* date-only business concepts.

Reports and payroll must not rely on ambiguous local timestamps.

---

## 92. API Security Boundary

The following values must never be treated as sufficient authorization:

```text
Business UUID
Branch UUID
Employee UUID
Device UUID
Order UUID
Role UUID
Permission UUID
```

Each must be validated against the authenticated context and server state.

---

## 93. API Enumeration Protection

Where sensitive resources exist, the API should reduce resource enumeration risk through:

* UUID identifiers;
* authorization checks;
* appropriate 404 behavior;
* rate limiting;
* bounded search;
* no sequential sensitive identifiers exposed unnecessarily.

UUIDs are not considered a substitute for authorization.

---

## 94. API Caching

Only safe/read-oriented responses should be cached.

Potentially cacheable:

* menu;
* product reference data;
* configuration;
* permission-derived read data;
* short-lived subscription state.

Never rely on API cache as the authoritative source for:

* payment;
* inventory deduction;
* cash state;
* Order financial state;
* historical audit state.

---

## 95. Cache-Control

Sensitive responses should use appropriate cache-control behavior.

Examples:

```text
private
no-store
max-age
```

depending on the resource.

Browser caching must not expose one Business's data to another user.

---

## 96. API Observability

API metrics should include:

* request count;
* response status;
* p50;
* p95;
* p99;
* error rate;
* timeout rate;
* rate-limit count;
* authentication failures;
* authorization failures;
* Business scope denials;
* Branch scope denials;
* idempotency conflicts;
* synchronization conflicts.

Metrics should be labeled carefully to avoid high-cardinality explosions.

---

## 97. API Health Endpoints

The backend should provide health endpoints such as:

```text
GET /health/live
GET /health/ready
```

### Liveness

Checks whether the process is alive.

### Readiness

Checks whether the application can safely accept traffic.

Health endpoints must not expose sensitive internal details.

---

## 98. API Documentation

Every public endpoint should document:

* purpose;
* authentication;
* permissions;
* Business/Branch scope;
* request schema;
* response schema;
* errors;
* idempotency;
* pagination;
* retry behavior;
* concurrency behavior where applicable.

---

## 99. API Documentation Language

Documentation should use stable technical terminology.

For example:

```text
Business
Branch
Employee
Device
Cash Session
Order
Order Item
Recipe Version
Configuration Version
Operation UUID
```

Terminology must remain consistent with Domain and Database documentation.

---

## 100. API Change Management

Any API change must consider:

1. Domain behavior;
2. Application use case;
3. authorization;
4. database impact;
5. frontend impact;
6. offline client impact;
7. synchronization impact;
8. backward compatibility;
9. testing;
10. documentation.

API changes must not be made independently from these dependencies.

---

## 101. API Contract Change Workflow

Recommended workflow:

```text
Requirement
    ↓
API contract proposal
    ↓
Application use case validation
    ↓
Security review
    ↓
Database impact review
    ↓
OpenAPI/schema update
    ↓
Implementation
    ↓
Contract tests
    ↓
Integration tests
    ↓
Performance/security tests
    ↓
Documentation update
```

---

## 102. API Architecture Guardrails

The following are prohibited:

* API route directly modifying PostgreSQL;
* client-provided total treated as authoritative;
* Business ID trusted without validation;
* Branch ID trusted without validation;
* permission checked only in frontend;
* duplicate payment without idempotency;
* generic CRUD bypassing business rules;
* unbounded list responses;
* unbounded synchronization batches;
* sensitive information in errors;
* production stack traces;
* plaintext credentials;
* silent stale configuration overwrite;
* API cache used as financial authority.

---

## 103. Testing Requirements

The API architecture must be tested through:

* unit tests;
* application tests;
* repository integration tests;
* API contract tests;
* security tests;
* multi-tenant isolation tests;
* Branch isolation tests;
* idempotency tests;
* concurrency tests;
* synchronization tests;
* performance tests;
* end-to-end tests.

Critical API workflows must satisfy the quality gates defined in:

`17_Backend_Testing_and_Quality_Assurance_Architecture.md`

---

## 104. API Invariants

The following invariants apply to the API architecture:

1. API routes do not contain core business logic.
2. API routes do not directly mutate PostgreSQL.
3. Business authorization is server-side.
4. Branch authorization is server-side.
5. Client Business UUID is never authoritative.
6. Client Branch UUID is never authoritative.
7. Client Employee UUID is never sufficient authentication.
8. Client Device UUID is never sufficient authentication.
9. Protected endpoints require authentication.
10. Protected operations require authorization.
11. Unknown permissions fail closed.
12. Read-only subscription state blocks modifying operations.
13. Deleted Business cannot accept normal API operations.
14. Important retryable commands use idempotency.
15. Duplicate idempotent commands do not duplicate business effects.
16. Reuse of an idempotency key with a conflicting payload returns conflict.
17. Request ID is not an authorization credential.
18. Operation UUID is separate from resource UUID.
19. API errors use stable error codes.
20. API errors do not expose sensitive internal information.
21. Pagination is bounded.
22. List endpoints use deterministic ordering.
23. Client-controlled SQL expressions are never accepted.
24. Important business operations use explicit commands where appropriate.
25. Current configuration cannot reinterpret historical transactions.
26. Historical financial values remain authoritative.
27. Configuration changes use optimistic concurrency where required.
28. Stale configuration updates are rejected.
29. Synchronization has a dedicated API contract.
30. Synchronization operations are individually identifiable.
31. Synchronization retries do not duplicate business effects.
32. Synchronization cannot bypass authorization.
33. Synchronization cannot bypass subscription restrictions.
34. Server state remains authoritative after synchronization.
35. Offline client timestamps do not override server authority.
36. Batch size is bounded.
37. Bulk operations are bounded.
38. Long operations use asynchronous processing where appropriate.
39. API timeouts are bounded.
40. External dependency failure does not indefinitely block requests.
41. Printer failure does not rollback committed Order state.
42. Notification failure does not rollback committed core state.
43. Report generation does not unnecessarily block POS.
44. XLSX generation may be asynchronous.
45. File paths are never exposed as authoritative storage identifiers.
46. File access is authorization-controlled.
47. Sensitive API responses use appropriate cache controls.
48. API caches are never financial authority.
49. ETag/conditional requests never replace authorization.
50. CORS configuration is explicit.
51. Cookie-based browser authentication requires CSRF protection.
52. Production API traffic uses protected transport.
53. Passwords and tokens are never logged.
54. API security failures are observable.
55. Rate limits are bounded and documented.
56. Core POS traffic must not be unnecessarily disrupted by generic rate limits.
57. API contract changes are reviewed for backward compatibility.
58. Breaking API changes require explicit versioning or migration.
59. Deprecated endpoints have a migration path.
60. OpenAPI documentation must reflect the implemented contract.
61. API contracts are automatically tested.
62. Business/Branch isolation is a release-blocking security requirement.
63. Financial duplicate prevention is a release-blocking correctness requirement.
64. Historical integrity is a release-blocking requirement.
65. API performance must remain within defined SLO targets.
66. Security controls must fail closed.
67. API observability must not create uncontrolled high-cardinality metrics.
68. Health endpoints must not expose sensitive information.
69. API changes must consider offline clients.
70. API changes must consider synchronization compatibility.
71. API terminology must remain consistent with Domain and Database models.
72. Client-provided financial totals are never authoritative.
73. Server-side pricing is authoritative.
74. Server-side inventory state is authoritative.
75. Server-side payment state is authoritative.
76. API responses must expose only authorized data.
77. Resource enumeration must not bypass authorization.
78. Authentication and authorization responsibilities remain separate.
79. API contract must not expose database implementation details.
80. API design must preserve the modular monolith boundary.

---

## 105. Recommended API Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── router.py
│   │   ├── dependencies.py
│   │   ├── middleware.py
│   │   ├── errors.py
│   │   ├── pagination.py
│   │   ├── context.py
│   │   ├── v1/
│   │   │   ├── auth/
│   │   │   ├── businesses/
│   │   │   ├── branches/
│   │   │   ├── employees/
│   │   │   ├── devices/
│   │   │   ├── products/
│   │   │   ├── recipes/
│   │   │   ├── inventory/
│   │   │   ├── menu/
│   │   │   ├── orders/
│   │   │   ├── payments/
│   │   │   ├── cash/
│   │   │   ├── handover/
│   │   │   ├── attendance/
│   │   │   ├── payroll/
│   │   │   ├── notifications/
│   │   │   ├── reports/
│   │   │   ├── files/
│   │   │   ├── configuration/
│   │   │   └── synchronization/
│   │   └── schemas/
│   │
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── security/
│   ├── background/
│   ├── synchronization/
│   └── reporting/
│
├── tests/
│   ├── api/
│   ├── integration/
│   ├── security/
│   ├── e2e/
│   └── performance/
│
└── pyproject.toml
```

---

## 106. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/16_Reports_and_Dashboards.md`
* `docs/02_System_Analysis/18_Audit_and_Change_History.md`
* `docs/02_System_Analysis/19_Data_Lifecycle_and_Deletion.md`

### Database

* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/27_Database_Migrations_and_Change_Management.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/01_Backend_Architecture.md`
* `docs/04_Architecture/02_Backend_Project_Structure.md`
* `docs/04_Architecture/03_Application_and_Use_Case_Layer.md`
* `docs/04_Architecture/04_Domain_Service_and_Business_Logic.md`
* `docs/04_Architecture/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/07_Transaction_Management.md`
* `docs/04_Architecture/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/11_Configuration_and_Environment_Management.md`
* `docs/04_Architecture/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/17_Backend_Testing_and_Quality_Assurance_Architecture.md`

---

## 107. Status

**Backend Architecture Document:** Completed.

**Document Status:** Proposed.

**Current Document:** `18_Backend_API_Design_and_Contract_Architecture.md`

**Next Document:** `19_Backend_Deployment_and_Runtime_Architecture.md`

