# API Design Principles and Standards

**Document ID:** API-02
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`

---

## 1. Purpose

This document defines the common design principles and technical standards that apply to the FastFood ERP API.

It establishes consistent rules for:

* HTTP methods;
* URL structure;
* resource naming;
* JSON representation;
* request and response conventions;
* headers;
* identifiers;
* dates and times;
* monetary values;
* enums;
* nullability;
* pagination;
* filtering;
* sorting;
* error representation;
* command endpoints;
* idempotency;
* concurrency;
* compatibility;
* API documentation.

The purpose is to ensure that all API modules follow one predictable contract style.

This document does not define individual business endpoint contracts.

---

## 2. Relationship to API Architecture

The API architecture is defined in:

`01_API_Architecture_Overview.md`

This document defines the standards used when implementing that architecture.

The hierarchy is:

```text
API Architecture
        ↓
API Design Principles and Standards
        ↓
API Foundation Contracts
        ↓
Business Endpoint Contracts
        ↓
OpenAPI Specification
        ↓
Implementation and Tests
```

A specific API endpoint may introduce additional rules when required by its business capability, but it must not violate the common standards without an explicit architectural decision.

---

## 3. Core Design Principles

The API follows these principles:

1. Consistency over individual endpoint preference.
2. Explicit contracts over implicit behavior.
3. Resource-oriented design for resources.
4. Command-oriented design for business operations.
5. HTTP semantics must be meaningful.
6. Server-side authority must be preserved.
7. Client input must always be treated as untrusted.
8. Business terminology must remain consistent across the system.
9. Responses must be predictable.
10. Errors must be machine-readable.
11. State-changing operations must be safely retryable where appropriate.
12. Historical data must remain historically correct.
13. API contracts must be backward-compatible unless a breaking change is explicitly versioned.
14. API design must support offline synchronization.
15. API behavior must remain suitable for POS workloads.
16. Standards must minimize unnecessary client complexity.
17. Security must be part of the contract, not an optional implementation detail.
18. Every public contract must be testable.

---

## 4. API Contract as a Public Boundary

The API is a public contract between the server and its clients.

Clients may include:

* Web frontend;
* POS frontend;
* trusted offline devices;
* administrative interfaces;
* future mobile clients;
* approved external integrations.

Internal implementation details must not become accidental API contracts.

The following must not be exposed merely because they exist internally:

* database table names;
* ORM model names;
* repository methods;
* internal service names;
* database foreign-key structure;
* internal filesystem paths;
* internal queue implementation;
* internal exception classes.

---

## 5. Predictability Principle

Equivalent operations should behave consistently across modules.

For example:

```text
GET    /products
GET    /orders
GET    /employees
```

should follow the same general rules for:

* authentication;
* pagination;
* filtering;
* sorting;
* response structure;
* errors.

Likewise, state-changing commands should consistently define:

* authorization;
* validation;
* idempotency;
* concurrency;
* audit behavior;
* response behavior.

---

## 6. HTTP Method Standards

The API uses HTTP methods according to their intended semantics.

### GET

Used for retrieving resources or read-only projections.

Examples:

```text
GET /api/v1/products
GET /api/v1/products/{product_id}
GET /api/v1/orders/{order_id}
```

GET must not intentionally create or modify business state.

### POST

Used for:

* resource creation;
* business commands;
* actions that do not map cleanly to simple resource replacement;
* asynchronous job creation;
* synchronization batches.

Examples:

```text
POST /api/v1/orders
POST /api/v1/orders/{order_id}/pay
POST /api/v1/sync/batches
```

### PATCH

Used for partial modification of resources where generic field-level modification is appropriate.

Example:

```text
PATCH /api/v1/products/{product_id}
```

PATCH must not be used to bypass business commands.

### PUT

May be used where complete replacement or deterministic idempotent replacement semantics are appropriate.

It should not be introduced merely as an alternative to PATCH.

### DELETE

Used only when the domain explicitly supports deletion.

Deletion must not be assumed to be appropriate for every resource.

For historical or auditable entities, the system should prefer domain-specific lifecycle operations such as:

```text
archive
deactivate
cancel
close
```

when required.

---

## 7. Safe and Idempotent HTTP Semantics

HTTP method semantics must not be confused with business idempotency.

For example:

```text
POST /orders/{id}/pay
```

may be made idempotent through an idempotency key even though POST itself is not inherently idempotent.

The API must explicitly define retry behavior for state-changing operations.

---

## 8. URL Naming Standard

Resource URLs use lowercase plural nouns.

Preferred:

```text
/api/v1/businesses
/api/v1/branches
/api/v1/employees
/api/v1/products
/api/v1/orders
/api/v1/payments
/api/v1/cash-sessions
```

Avoid:

```text
/api/v1/getProducts
/api/v1/createOrder
/api/v1/doPayment
```

HTTP methods communicate basic resource operations.

Business actions use explicit command paths where required.

---

## 9. URL Character Standard

URLs must use:

* lowercase path segments;
* hyphens for multi-word resource names;
* UUID identifiers;
* no unnecessary abbreviations.

Preferred:

```text
/cash-sessions
/recipe-versions
/shift-handovers
```

Avoid:

```text
/cash_sessions
/cashSessions
/cs
```

Query parameter naming follows the same consistency rules.

---

## 10. Resource Naming

Resource names must correspond to domain terminology.

The API should use the same terms as the Domain and Database documentation.

Examples:

```text
Business
Branch
Employee
Device
Product
Recipe
Recipe Version
Set
Inventory
Order
Order Item
Payment
Refund
Cash Register
Cash Session
Shift Handover
Attendance
Payroll
Notification
Report
Configuration
Subscription
```

A different API name should not be introduced merely for stylistic reasons.

---

## 11. Resource Identity

Resource identifiers use UUIDs where UUID identity is appropriate.

Example:

```json
{
  "id": "018f7e7c-..."
}
```

The API must distinguish:

* resource UUID;
* operation UUID;
* request ID;
* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID.

These identifiers must not be used interchangeably.

---

## 12. UUID Representation

UUIDs must be represented as strings.

Preferred:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Clients must not receive database-specific binary UUID representations.

Invalid UUID values must be rejected at the API boundary.

---

## 13. JSON Standard

JSON is the primary API representation.

Requests and responses should use:

```http
Content-Type: application/json
```

unless a different media type is explicitly required.

JSON objects must use stable field names.

---

## 14. JSON Field Naming

The API uses `snake_case` for JSON field names.

Example:

```json
{
  "business_id": "...",
  "branch_id": "...",
  "created_at": "...",
  "cash_session_id": "..."
}
```

The same convention must be used consistently across request and response schemas.

---

## 15. JSON Object Structure

Objects should represent meaningful domain concepts.

Avoid unnecessarily deeply nested structures.

Preferred:

```json
{
  "id": "...",
  "name": "Burger",
  "active": true
}
```

rather than exposing internal persistence structures.

Nested objects should be used when they materially improve contract clarity.

---

## 16. Arrays

Collections should be represented as JSON arrays.

Example:

```json
{
  "data": [
    {
      "id": "...",
      "name": "Burger"
    },
    {
      "id": "...",
      "name": "Pizza"
    }
  ]
}
```

The order of an array must be explicitly defined where order is meaningful.

---

## 17. Nullability

Nullability must be intentional.

A field should not alternate unpredictably between:

```json
null
```

and:

```json
""
```

for the same semantic condition.

The API contract must define whether a field is:

* required;
* optional;
* nullable;
* optional and nullable.

---

## 18. Missing vs Null

The API should distinguish between:

* field not supplied;
* field explicitly set to `null`;
* field containing an empty value.

This is especially important for PATCH requests.

Example:

```json
{}
```

may mean:

> Do not modify the field.

While:

```json
{
  "description": null
}
```

may mean:

> Explicitly clear the description.

This behavior must be documented for each mutable field where relevant.

---

## 19. Boolean Fields

Boolean fields must use JSON booleans.

Preferred:

```json
{
  "active": true
}
```

Avoid:

```json
{
  "active": "true"
}
```

or:

```json
{
  "active": 1
}
```

Boolean semantics must remain consistent.

---

## 20. Numeric Values

Numeric fields must have explicitly defined ranges and semantics.

For example:

```json
{
  "quantity": 2
}
```

The contract must define:

* minimum;
* maximum where applicable;
* decimal precision;
* whether zero is valid;
* whether negative values are valid.

Business rules remain enforced by the Application/Domain layers.

---

## 21. Monetary Values

Money must not rely on ambiguous floating-point representation.

Preferred representation:

```json
{
  "amount": "25000.00"
}
```

The API should standardize monetary values as decimal strings unless a specific contract explicitly defines another representation.

Each monetary field must have a defined currency context where required.

---

## 22. Money Precision

Monetary values must have deterministic precision.

The API must define:

* scale;
* rounding behavior;
* minimum unit;
* currency.

Client-side floating-point arithmetic must not become the authoritative financial calculation.

The server calculates authoritative financial values.

---

## 23. Financial Calculation Authority

Clients may send inputs such as:

```text
quantity
discount request
payment method
markup percentage
```

but the server calculates authoritative:

* subtotal;
* discount amount;
* final amount;
* payment state;
* refund amount;
* inventory financial effects.

Client-provided totals are never authoritative.

---

## 24. Percentage Values

Percentages must have one consistent representation.

The API should use numeric percentage points.

Example:

```json
{
  "markup_percent": 25
}
```

This means:

```text
25%
```

It must not be ambiguously represented as:

```json
{
  "markup_percent": 0.25
}
```

unless the contract explicitly defines fractional representation.

---

## 25. Date and Time Standard

The API uses ISO 8601-compatible timestamps.

Example:

```text
2026-10-06T10:30:00Z
```

UTC should be used for authoritative event timestamps unless the field explicitly represents a business-local date/time.

---

## 26. Date-Only Values

Date-only concepts must not be represented as timestamps when time is not semantically relevant.

Example:

```json
{
  "payroll_period": "2026-10"
}
```

or:

```json
{
  "work_date": "2026-10-06"
}
```

The API must distinguish:

* instant in time;
* local date;
* month;
* period.

---

## 27. Timezone Standard

The API must explicitly define timezone semantics for operations affected by local business time.

Relevant contexts include:

* Cash Sessions;
* Attendance;
* Payroll;
* reports;
* subscription boundaries;
* business-day calculations.

Server timestamps remain authoritative.

---

## 28. Enum Standards

Enums must use stable string values.

Example:

```json
{
  "status": "PAID"
}
```

Avoid numeric enum values such as:

```json
{
  "status": 4
}
```

String values are easier to document, debug and maintain.

---

## 29. Enum Compatibility

Existing enum meanings must not be silently changed.

Adding a new enum value may affect older clients.

Therefore:

* clients must tolerate documented unknown values where appropriate;
* enum additions must be reviewed for compatibility;
* removing or renaming values is a breaking change.

---

## 30. Enum Naming

Enum values should use uppercase `SCREAMING_SNAKE_CASE`.

Examples:

```text
PENDING
ACTIVE
PAID
CANCELLED
REFUNDED
READ_ONLY
DELETED
```

Domain-specific terminology must remain consistent.

---

## 31. Resource State Representation

State fields should represent the authoritative server state.

Example:

```json
{
  "status": "OPEN"
}
```

Clients must not infer authoritative state from unrelated fields when the API already provides an explicit state.

---

## 32. Timestamps and Audit Fields

Where appropriate, resources may expose:

```json
{
  "created_at": "...",
  "updated_at": "..."
}
```

Audit-sensitive resources may additionally expose:

```json
{
  "created_by": "...",
  "updated_by": "..."
}
```

Only information appropriate for the client and its authorization scope should be exposed.

---

## 33. Read and Write Models

The API may use different representations for:

* resource reads;
* resource creation;
* resource updates;
* business commands.

For example, a Product response may contain fields that are not accepted during creation.

This is preferable to forcing one universal schema onto all operations.

---

## 34. Request Schema Standards

Request schemas must define:

* required fields;
* optional fields;
* nullable fields;
* field types;
* allowed ranges;
* enum values;
* nested structures;
* format requirements;
* cross-field constraints where applicable.

Malformed requests should be rejected before entering the business workflow.

---

## 35. Response Schema Standards

Response schemas must define:

* returned fields;
* field types;
* nullability;
* enum values;
* pagination;
* nested relationships;
* metadata where applicable.

Undocumented response fields must not become required client dependencies.

---

## 36. Response Stability

Once a response field is public and relied upon by supported clients, removing or changing its meaning is considered a compatibility-sensitive change.

Compatible additions should not invalidate existing clients.

---

## 37. Response Envelope

The API should use a consistent envelope for resource and collection responses where appropriate.

Resource:

```json
{
  "data": {
    "id": "...",
    "name": "Burger"
  }
}
```

Collection:

```json
{
  "data": [],
  "pagination": {
    "has_more": false,
    "next_cursor": null
  }
}
```

The exact envelope must be standardized before public API contracts are finalized.

---

## 38. Metadata

Metadata may be included when it provides useful contract information.

Examples:

```json
{
  "data": [],
  "meta": {
    "request_id": "..."
  }
}
```

Metadata must not become an uncontrolled collection of unrelated internal values.

---

## 39. Request Headers

Common headers may include:

```text
Authorization
Content-Type
Accept
X-Request-ID
X-Business-ID
X-Branch-ID
X-Device-ID
Idempotency-Key
If-Match
If-None-Match
```

Not every endpoint requires every header.

The endpoint contract defines which headers are required or optional.

---

## 40. Authorization Header

When bearer-token authentication is used:

```http
Authorization: Bearer <token>
```

Credentials must never be placed in:

* URL query parameters;
* resource identifiers;
* ordinary request bodies unless the authentication protocol explicitly requires it.

---

## 41. Request ID Standard

`X-Request-ID` identifies one API request.

It is used for:

* tracing;
* logging;
* support;
* diagnostics.

It is not equivalent to:

* idempotency key;
* operation UUID;
* authentication credential.

---

## 42. Idempotency-Key Standard

`Idempotency-Key` identifies a retryable state-changing operation.

It must not be reused for unrelated operations.

The server must validate:

* key format;
* operation scope;
* actor/context where required;
* payload consistency.

Conflicting reuse must produce a deterministic conflict response.

---

## 43. Conditional Request Standard

`If-Match` and ETag may be used for optimistic concurrency.

Example:

```http
If-Match: "12"
```

If the resource has changed since version `12`, the server must reject the stale update.

The endpoint must define the exact concurrency semantics.

---

## 44. Content Negotiation

The API should support explicit media types where required.

For ordinary JSON APIs:

```http
Accept: application/json
```

Specialized representations such as file downloads should use their appropriate media types.

Clients must not assume every endpoint returns JSON.

---

## 45. File Download Responses

File downloads should use appropriate `Content-Type` values.

For example:

```text
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

for XLSX files.

The API must not expose filesystem paths as download locations.

---

## 46. Error Contract Standard

All API errors must follow a predictable structure.

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

The exact error architecture is defined in:

`09_API_Error_Handling_and_Error_Codes.md`

This document establishes only the common contract standard.

---

## 47. Error Code Standard

Error codes must be:

* machine-readable;
* stable;
* unique within the API contract;
* documented;
* independent from localized human messages.

Preferred:

```text
ORDER_ALREADY_PAID
INSUFFICIENT_STOCK
STALE_VERSION
ACCESS_DENIED
SUBSCRIPTION_READ_ONLY
```

Avoid codes based on internal exception names.

---

## 48. Human-Readable Error Messages

The `message` field is intended for diagnostics and user-facing presentation where appropriate.

Clients must not use the message text as the primary programmatic decision mechanism.

Programmatic behavior must rely on:

```text
error.code
```

and documented details.

---

## 49. Error Details

`details` may contain structured information required for recovery.

Example:

```json
{
  "error": {
    "code": "STALE_VERSION",
    "message": "The configuration has changed.",
    "details": {
      "current_version": 13,
      "requested_version": 12
    }
  }
}
```

Details must not expose sensitive internal information.

---

## 50. HTTP Status Consistency

The same semantic error should use the same HTTP status category across API modules unless a documented exception exists.

Examples:

```text
400 → malformed request
401 → authentication failure
403 → authorization denial
404 → unavailable resource
409 → state/concurrency conflict
422 → semantically invalid input
429 → rate limited
500 → unexpected server error
503 → temporarily unavailable
```

Detailed mapping is defined in the error architecture document.

---

## 51. Command Endpoint Standard

Business commands should use a consistent pattern:

```text
POST /{resource}/{id}/{action}
```

Examples:

```text
POST /orders/{order_id}/accept
POST /orders/{order_id}/pay
POST /cash-sessions/{session_id}/close
POST /recipes/{recipe_id}/approve
```

Command names must describe a domain action rather than an implementation detail.

---

## 52. Command Naming

Command names should be:

* lowercase;
* hyphen-separated when multiple words are required;
* expressed as domain actions.

Preferred:

```text
/close
/approve
/archive
/deactivate
/accept
/submit
```

Avoid:

```text
/doClose
/executeApproval
/processData
/runOperation
```

---

## 53. Command Response Standard

A command response must clearly communicate the authoritative result.

Depending on the operation, the response may contain:

* updated resource;
* operation result;
* created transaction;
* job identifier;
* synchronization result.

The response must not require the client to guess whether the operation succeeded.

---

## 54. Asynchronous Operation Standard

Long-running operations should return:

```http
202 Accepted
```

when processing continues after the initial request.

The response should provide an authoritative status identifier.

Example:

```json
{
  "data": {
    "job_id": "..."
  }
}
```

The client should poll or use the documented completion mechanism.

---

## 55. Pagination Standard

List endpoints must use bounded pagination.

Default target:

```text
limit = 50
maximum = 100
```

Cursor-based pagination is preferred for large or frequently changing datasets.

The pagination contract must define:

* limit;
* cursor;
* has_more;
* next_cursor.

---

## 56. Stable Ordering

Paginated results must use deterministic ordering.

When timestamps can collide, a unique secondary key should be used.

Example:

```text
created_at DESC
id DESC
```

This prevents records from moving unpredictably between pages.

---

## 57. Filtering Standard

Filters use query parameters.

Example:

```text
GET /orders?status=PAID
GET /orders?branch_id=...
GET /orders?from=...&to=...
```

Filters must be:

* documented;
* validated;
* authorization-aware;
* bounded;
* supported by appropriate query strategy.

Unknown filters should normally be rejected rather than silently ignored.

---

## 58. Sorting Standard

Sorting uses a documented parameter.

Example:

```text
GET /orders?sort=-created_at
```

The API must maintain an allowlist of sortable fields.

Clients must never provide raw SQL expressions.

---

## 59. Search Standard

Search parameters must have explicit limits.

The API should define:

* minimum search length where appropriate;
* maximum search length;
* searchable fields;
* case behavior;
* normalization rules;
* authorization scope.

Search must not become an unrestricted database query mechanism.

---

## 60. Expand and Include Behavior

The API should avoid uncontrolled relationship expansion.

If related resources need to be included, the mechanism must be explicit and bounded.

For example:

```text
?include=items
```

may be supported where appropriate.

The API must not allow arbitrary recursive object expansion.

---

## 61. Business and Branch Scope

Every Business-scoped endpoint must validate Business ownership through the authenticated server context.

Every Branch-scoped endpoint must validate Branch authorization.

The following values are context identifiers, not authority:

```text
business_id
branch_id
employee_id
device_id
```

This rule applies regardless of whether the values are sent through:

* URL;
* query;
* body;
* headers.

---

## 62. Subscription Entitlement

Modifying endpoints must evaluate applicable subscription entitlement.

A client must not bypass subscription restrictions by calling a lower-level API endpoint directly.

Read-only subscription behavior must be enforced server-side.

---

## 63. Authentication and Authorization Separation

Authentication answers:

> Who is the actor?

Authorization answers:

> What may the actor do?

The API contract must preserve this distinction.

A successfully authenticated actor is not automatically authorized to perform every operation.

---

## 64. Idempotency Standard

The following operations should support idempotency where retries may duplicate business effects:

* payments;
* refunds;
* inventory transactions;
* order commands;
* cash operations;
* configuration changes;
* synchronization operations;
* bulk mutations.

The endpoint documentation must identify whether idempotency is:

* required;
* optional;
* not applicable.

---

## 65. Concurrency Standard

Resources that may be changed concurrently must use an explicit concurrency strategy.

Supported strategies may include:

* optimistic version checks;
* ETag/If-Match;
* server-side state validation;
* targeted locking within the Application/Domain transaction.

Silent last-write-wins must not be used for important business configuration or financial state.

---

## 66. Historical Integrity Standard

API operations must preserve historical transaction state.

Current values must not silently rewrite:

* historical order prices;
* historical discounts;
* historical payments;
* historical refunds;
* historical inventory deductions;
* historical recipe versions;
* historical configuration versions.

Historical values must be represented through immutable snapshots or version references where required.

---

## 67. Soft Deletion and Lifecycle Operations

The API must not assume that `DELETE` is the correct lifecycle operation.

For entities requiring historical preservation, use explicit operations such as:

```text
/archive
/deactivate
/cancel
/close
```

Permanent deletion must be limited to domains where deletion is explicitly permitted.

Data lifecycle rules are defined by the relevant Business, System and Database documents.

---

## 68. API Security by Default

API contracts must assume that:

* clients are untrusted;
* headers are untrusted input;
* request bodies are untrusted input;
* query parameters are untrusted input;
* resource IDs are untrusted input;
* clients may retry;
* clients may be outdated;
* clients may be offline;
* malicious requests may be crafted manually.

Security must therefore be enforced on the server.

---

## 69. Sensitive Data Rules

API contracts must not expose:

* passwords;
* password hashes;
* access tokens;
* refresh tokens;
* signing private keys;
* database credentials;
* internal secrets;
* unnecessary infrastructure information.

Sensitive fields must be explicitly reviewed before inclusion in response schemas.

---

## 70. Logging Compatibility

API contracts must identify fields that must not appear in logs.

At minimum:

```text
password
access_token
refresh_token
secret
private_key
```

Request and response logging must be designed so that sensitive information cannot be accidentally recorded.

---

## 71. Caching Standard

Caching is permitted only where the cached representation remains safe.

Potentially cacheable resources include:

* menu;
* product reference data;
* read-only configuration;
* selected permission-derived data.

The following must not rely on cache as authoritative state:

* payment;
* inventory quantity;
* cash session state;
* order financial state;
* audit history.

---

## 72. Cache Isolation

Cache keys must include sufficient tenant and scope context.

For example, a cache key must not allow:

```text
Business A → cached response → Business B
```

Cross-Business cache leakage is a release-blocking security defect.

---

## 73. Offline Compatibility

API contracts must consider trusted offline clients.

State-changing endpoints used by offline synchronization must provide sufficient information for:

* operation identification;
* authorization;
* Business/Branch validation;
* device validation;
* conflict detection;
* duplicate prevention;
* reconciliation.

The offline synchronization contract is defined separately in:

`19_API_Offline_Synchronization_and_Reconciliation.md`

---

## 74. Client Compatibility

The API must support clients that may not update immediately.

Therefore, compatible API evolution should prefer:

* adding optional fields;
* adding new endpoints;
* adding optional query parameters;
* preserving existing enum meanings;
* preserving existing error codes;
* maintaining documented behavior.

Breaking changes require explicit migration or versioning.

---

## 75. Unknown Fields

Clients should generally ignore unknown response fields unless the contract explicitly requires strict schema matching.

This allows compatible response evolution.

Servers should not silently accept unknown request fields when doing so could hide client errors or contract mismatches.

The request policy should be defined consistently by schema validation configuration.

---

## 76. API Documentation Standard

Every endpoint must document at least:

* HTTP method;
* path;
* purpose;
* authentication;
* authorization;
* Business/Branch scope;
* request schema;
* response schema;
* possible errors;
* idempotency requirements;
* concurrency requirements;
* retry behavior;
* asynchronous behavior where applicable.

---

## 77. OpenAPI Alignment

The API implementation and OpenAPI specification must remain synchronized.

OpenAPI should describe:

* paths;
* methods;
* parameters;
* headers;
* request bodies;
* response schemas;
* security requirements;
* error schemas;
* enums;
* pagination.

OpenAPI must not become an independently maintained description that diverges from implementation.

---

## 78. Contract Testing Standard

Every public endpoint must have contract coverage.

Contract tests should verify at minimum:

* method;
* path;
* request validation;
* response schema;
* status codes;
* error codes;
* authentication;
* authorization;
* pagination where applicable;
* idempotency where applicable.

Business-critical endpoints require additional integration and domain tests.

---

## 79. API Change Classification

API changes should be classified as:

### Non-Breaking

Examples:

* new endpoint;
* optional request field;
* optional response field;
* new filter;
* additional metadata.

### Compatibility-Sensitive

Examples:

* new enum value;
* changed default behavior;
* changed pagination behavior;
* changed performance characteristics;
* new required permission.

### Breaking

Examples:

* removing an endpoint;
* removing a required field;
* changing field type;
* changing semantic meaning;
* changing authentication requirements incompatibly;
* removing an enum value;
* changing an error code relied upon by clients.

Breaking changes require explicit versioning or migration.

---

## 80. Deprecation Standard

Deprecated endpoints must remain available for the documented compatibility period unless a security or correctness issue requires earlier removal.

Deprecation documentation must identify:

* deprecated endpoint;
* reason;
* replacement;
* migration path;
* expected removal date.

Deprecation must not be silent.

---

## 81. Performance Standards

API design must support the established performance targets.

Initial targets:

| Metric                               |   Target |
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

API design must not introduce unnecessary network round trips for ordinary POS workflows.

---

## 82. POS API Design Standard

POS operations require special attention to latency and reliability.

POS APIs should:

* minimize unnecessary round trips;
* return authoritative results;
* use bounded payloads;
* support safe retries;
* avoid unnecessary synchronous external dependencies;
* avoid large response objects;
* preserve transaction snapshots;
* support offline synchronization where applicable.

Security must not require unnecessary repeated verification during ordinary trusted POS operation.

---

## 83. Large Payload Standard

Large requests and responses must be explicitly bounded.

Examples include:

* synchronization batches;
* file uploads;
* bulk operations;
* report filters;
* large collection responses.

The API must reject or asynchronously process requests that exceed safe limits.

---

## 84. External Dependency Boundary

API endpoints must not wait indefinitely for external services.

External dependencies may include:

* email;
* storage;
* payment providers;
* future integrations;
* external notification systems.

Where external processing is not required to complete the core transaction, the operation should use asynchronous processing.

---

## 85. Core Transaction vs Secondary Effects

The API must distinguish between:

### Core State

Examples:

* Order;
* Payment;
* Inventory Transaction;
* Cash Session;
* Configuration.

### Secondary Effects

Examples:

* notification;
* email;
* report refresh;
* analytics update;
* non-critical external integration.

Failure of a secondary effect must not automatically rollback committed core state.

---

## 86. API Transaction Boundary

An API request does not automatically define the complete business transaction.

The Application layer determines transaction boundaries.

For example:

```text
POST /orders/{id}/accept
        ↓
Application transaction
        ↓
Order state
Inventory deduction
Audit
Outbox
        ↓
Commit
        ↓
Notifications / secondary processing
```

The API layer must not independently manage partial business transactions.

---

## 87. API Response Timing

The API should return a response as soon as the required authoritative work is complete.

It should not wait for unrelated secondary operations such as:

* email delivery;
* notification delivery;
* report regeneration;
* analytics processing.

This is especially important for POS operations.

---

## 88. Retry and Backoff Standard

Clients should use bounded retry with backoff for explicitly retryable failures.

Automatic retry is generally appropriate for:

```text
503 SERVICE_UNAVAILABLE
temporary synchronization failure
network timeout
```

Automatic retry is generally inappropriate for:

```text
400 validation error
403 authorization failure
409 stale configuration
422 business validation
```

unless the endpoint contract explicitly defines a recovery workflow.

---

## 89. API Observability Standard

Every request should be traceable through stable identifiers.

At minimum:

```text
request_id
```

State-changing operations should additionally expose or internally correlate:

```text
operation_id
```

where applicable.

Metrics should include:

* request count;
* latency;
* status;
* error rate;
* timeout rate;
* retry rate;
* idempotency conflicts;
* authorization failures;
* synchronization conflicts.

---

## 90. High-Cardinality Protection

Observability labels must not blindly include high-cardinality identifiers such as:

* Business UUID;
* Employee UUID;
* Device UUID;
* Order UUID;
* Request UUID.

These may be present in logs and traces, but metrics must use carefully selected dimensions.

---

## 91. API Health Contract

Health endpoints should be simple and safe.

Recommended:

```text
GET /health/live
GET /health/ready
```

Liveness indicates that the process is alive.

Readiness indicates that the application can safely receive traffic.

Health responses must not reveal:

* database credentials;
* internal connection strings;
* stack traces;
* infrastructure secrets.

---

## 92. Localization

API machine-readable values must remain language-neutral.

For example:

```text
ORDER_ALREADY_PAID
```

must not become language-specific.

Human-readable messages may later support localization without changing the machine-readable error code.

---

## 93. API Documentation Language

Technical API documentation should use stable English terminology consistent with architecture documentation.

Canonical terms include:

```text
Business
Branch
Employee
Device
Cash Session
Order
Order Item
Payment
Refund
Recipe Version
Configuration Version
Operation UUID
Subscription
Synchronization
```

Synonyms should not be introduced unnecessarily.

---

## 94. Standards for Optional Features

Optional API features should not become mandatory dependencies.

Examples:

* ETag;
* advanced search;
* response expansion;
* caching;
* asynchronous processing.

If a feature is not required for a specific endpoint, its absence must not break the standard API workflow.

---

## 95. API Design Review Checklist

Every new endpoint should be reviewed against:

### Contract

* Is the resource/action correctly identified?
* Is the HTTP method appropriate?
* Is the URL consistent?
* Are request fields defined?
* Are response fields defined?

### Security

* Is authentication required?
* Is authorization defined?
* Is Business scope enforced?
* Is Branch scope enforced?
* Are sensitive fields excluded?

### Correctness

* Is idempotency required?
* Is concurrency relevant?
* Is historical integrity affected?
* Are business rules enforced server-side?

### Performance

* Is the endpoint suitable for the expected workload?
* Are payloads bounded?
* Are queries indexed?
* Are unnecessary round trips avoided?
* Should the operation be asynchronous?

### Compatibility

* Is the change backward-compatible?
* Does it affect offline clients?
* Does it affect synchronization?
* Does it require OpenAPI updates?
* Does it require contract tests?

---

## 96. Prohibited API Design Patterns

The following patterns are prohibited:

* route handlers containing core business logic;
* direct database mutation from API routes;
* trusting client-provided totals;
* trusting Business or Branch IDs without validation;
* authorization performed only in the frontend;
* generic PATCH used to bypass business commands;
* unrestricted list responses;
* unrestricted search;
* unrestricted synchronization batches;
* arbitrary SQL expressions in query parameters;
* sensitive information in errors;
* secrets in logs;
* silent stale configuration overwrite;
* cache used as financial authority;
* API versioning by undocumented behavior;
* silent breaking changes;
* database schema exposed as the public API model.

---

## 97. Cross-Module Consistency

All API modules must follow these standards unless a specific documented exception exists.

This applies to:

* POS;
* Orders;
* Payments;
* Cash;
* Inventory;
* Products;
* Recipes;
* Menu;
* Employees;
* Attendance;
* Payroll;
* Reports;
* Notifications;
* Configuration;
* Subscription;
* Synchronization;
* External integrations.

Module-specific documents define business-specific behavior.

This document defines the shared contract language.

---

## 98. Relationship to Backend Architecture

The API must remain consistent with:

`docs/04_Architecture/06_Backend_Authentication_and_Authorization.md`

`docs/04_Architecture/03_Application_and_Use_Case_Layer.md`

`docs/04_Architecture/04_Domain_Service_and_Business_Logic.md`

`docs/04_Architecture/05_Repository_and_Data_Access.md`

`docs/04_Architecture/07_Transaction_Management.md`

The API must not duplicate responsibilities owned by these layers.

---

## 99. Relationship to Frontend Architecture

The API contract must support:

* frontend state management;
* POS workflows;
* optimistic UI where safe;
* offline storage;
* synchronization;
* error recovery;
* role-aware UI.

The frontend must not be required to reproduce server-side business rules merely to make the API contract work.

Frontend validation may improve usability, but server validation remains authoritative.

---

## 100. Relationship to Database Architecture

The API must not expose the database model as its contract.

Database changes should not automatically require API changes when the public behavior remains compatible.

The API should expose business concepts rather than:

```text
table names
foreign-key implementation
internal indexes
ORM relations
database-specific identifiers
```

---

## 101. Relationship to Security Architecture

Security-sensitive API rules are further defined in:

`21_API_Security_CORS_CSRF_and_Data_Protection.md`

The API standards in this document establish the baseline.

Security-specific requirements may impose stricter rules.

---

## 102. Relationship to Offline Synchronization

Offline API behavior is further defined in:

`19_API_Offline_Synchronization_and_Reconciliation.md`

The common standards require that offline-related APIs preserve:

* operation identity;
* idempotency;
* authorization;
* scope validation;
* conflict handling;
* server authority;
* historical integrity.

---

## 103. Relationship to OpenAPI and Contract Testing

Detailed contract publication and testing are defined in:

`23_API_OpenAPI_Contract_Testing_and_Documentation.md`

The implementation must not introduce undocumented public behavior.

---

## 104. API Standards Invariants

The following invariants apply to API design standards:

1. Public API contracts use stable domain terminology.
2. API URLs use predictable resource naming.
3. Resource paths use lowercase naming.
4. Multi-word path segments use hyphens.
5. JSON fields use `snake_case`.
6. UUIDs are represented as strings.
7. Resource UUIDs and operation UUIDs remain distinct.
8. Client identifiers never grant authorization.
9. JSON booleans use actual boolean values.
10. Nullability is explicitly defined.
11. Missing and null fields have defined semantics where relevant.
12. Money representation is deterministic.
13. Floating-point financial values are not authoritative.
14. Server-side financial calculations are authoritative.
15. Percentage representation is consistent.
16. Timestamps use defined ISO 8601-compatible semantics.
17. Authoritative event timestamps are server-controlled.
18. Date-only values are not represented as ambiguous timestamps.
19. Enum values are stable strings.
20. Enum meanings are not silently changed.
21. GET requests do not intentionally mutate business state.
22. Business commands use explicit command semantics where appropriate.
23. Generic CRUD cannot bypass business rules.
24. Request schemas define required and optional fields.
25. Response schemas define stable public fields.
26. Error codes are machine-readable and stable.
27. Error messages are not the primary programmatic contract.
28. Sensitive information is excluded from API errors.
29. Pagination is bounded.
30. Paginated results use deterministic ordering.
31. Sorting uses an allowlist.
32. Filtering is authorization-aware.
33. Search is bounded and authorization-aware.
34. Arbitrary SQL expressions are prohibited.
35. Business scope is server-validated.
36. Branch scope is server-validated.
37. Subscription entitlement is server-enforced.
38. Authentication and authorization remain separate.
39. Retryable state-changing operations use idempotency where required.
40. Conflicting idempotency-key reuse returns a deterministic conflict.
41. Important concurrent updates use explicit concurrency control.
42. Silent last-write-wins is prohibited for important business configuration.
43. Historical transactions are not reinterpreted by current configuration.
44. Lifecycle operations preserve historical integrity.
45. Soft deletion or archive is preferred where history must remain.
46. Offline synchronization has explicit operation identity.
47. Offline clients cannot bypass server authority.
48. API contracts remain compatible with supported clients.
49. Breaking changes require explicit migration or versioning.
50. Deprecated endpoints have documented migration paths.
51. OpenAPI must reflect the implemented contract.
52. Public endpoints require contract tests.
53. Sensitive credentials are never logged.
54. API caches are never authoritative for financial state.
55. Cache keys preserve Business and scope isolation.
56. Large payloads are bounded.
57. Long-running operations use asynchronous processing where appropriate.
58. External dependencies have bounded timeouts.
59. Secondary failures do not unnecessarily rollback committed core state.
60. POS APIs minimize unnecessary latency and round trips.
61. API observability avoids uncontrolled metric cardinality.
62. Health endpoints do not expose sensitive information.
63. API machine-readable values remain language-neutral.
64. API standards are shared across modules.
65. Exceptions to standards require explicit documentation.
66. API design must remain consistent with Application and Domain boundaries.
67. API design must not expose database implementation details.
68. API design must preserve multi-tenant isolation.
69. API design must preserve Branch isolation.
70. API design must preserve financial correctness.
71. API design must preserve historical integrity.
72. API design must remain compatible with offline operation.
73. API design must remain compatible with synchronization.
74. API design must remain within defined performance targets.
75. API design must remain testable through automated contract validation.

---

## 105. Status

**API Architecture Section:** In Progress

**Document Status:** Proposed

**Current Document:** `02_API_Design_Principles_and_Standards.md`

**Previous Document:** `01_API_Architecture_Overview.md`

**Next Document:** `03_API_Layers_and_Request_Lifecycle.md`

