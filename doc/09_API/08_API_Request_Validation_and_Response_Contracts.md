# API Request Validation and Response Contracts

**Document ID:** API-08
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines request validation and response contract architecture for the FastFood ERP API.

The API must accept only structurally valid requests and must return predictable, stable and authorized response representations.

The API contract must provide a clear boundary between:

* HTTP transport;
* structural validation;
* Application use cases;
* Domain validation;
* response serialization;
* authorization-aware data exposure.

Request validation must prevent malformed or unsafe input from reaching application logic.

Response contracts must prevent internal domain, database or infrastructure structures from being exposed directly to clients.

---

# 2. Scope

This document covers:

* request validation;
* request schemas;
* path parameters;
* query parameters;
* headers;
* request bodies;
* nested objects;
* primitive type validation;
* string validation;
* numeric validation;
* date/time validation;
* UUID validation;
* enum validation;
* collection validation;
* pagination input;
* filtering input;
* structural vs business validation;
* validation ordering;
* response contracts;
* response envelopes;
* resource representations;
* list responses;
* pagination metadata;
* command responses;
* asynchronous responses;
* empty responses;
* serialization;
* field exposure;
* sensitive field filtering;
* decimal and money representation;
* date/time representation;
* nullability;
* optional fields;
* compatibility;
* schema versioning;
* validation errors;
* response consistency;
* contract testing;
* OpenAPI;
* performance;
* security;
* invariants.

---

# 3. Validation Principle

The API must validate request structure before invoking the Application use case.

```text id="valflow1"
HTTP Request
    ↓
Transport Parsing
    ↓
Schema Validation
    ↓
Request Context
    ↓
Authorization
    ↓
Application Use Case
    ↓
Domain Validation
```

Structural validation belongs at the API boundary.

Business validation belongs to the Application/Domain layers.

---

# 4. Validation Responsibilities

The API validates:

* data type;
* required fields;
* field format;
* string length;
* numeric format;
* numeric range;
* enum values;
* UUID format;
* timestamp format;
* date format;
* collection size;
* nested object structure;
* pagination limits;
* supported query parameters.

The Application/Domain validates:

* resource existence;
* Business ownership;
* Branch scope;
* resource state;
* inventory availability;
* financial rules;
* permission-dependent business rules;
* configuration versions;
* workflow rules;
* transactional invariants.

---

# 5. Structural vs Business Validation

Example:

```text id="valsep1"
API Validation

quantity:
must be a positive number

Domain Validation

quantity:
must not exceed the permitted business operation
```

Another example:

```text id="valsep2"
API Validation

branch_id:
must be a valid UUID

Authorization/Application

branch_id:
must belong to the authorized Business and employee scope
```

A syntactically valid value is not automatically a valid business value.

---

# 6. Validation Must Be Server-Side

All API validation must be performed server-side.

The frontend may perform early validation for usability, but the server remains authoritative.

A request must not become valid merely because:

* frontend validation passed;
* client schema was correct;
* POS client marked the request as valid;
* offline client generated the request locally.

---

# 7. Validation Order

The recommended high-level order is:

```text id="valorder1"
1. HTTP method and route
2. Request size
3. Header parsing
4. Path parameter validation
5. Query parameter validation
6. Body parsing
7. Body schema validation
8. Request context construction
9. Authentication
10. Authorization
11. Application validation
12. Domain validation
13. Transaction execution
```

The implementation may optimize independent checks, but the security and correctness semantics must remain equivalent.

---

# 8. Request Size Limits

The API must enforce bounded request sizes.

Limits should exist for:

* complete HTTP request;
* JSON body;
* file upload;
* synchronization batch;
* bulk operation;
* nested collections.

Unbounded request bodies are prohibited.

---

# 9. HTTP Method Validation

Endpoints must accept only supported HTTP methods.

Example:

```text id="method1"
GET /api/v1/orders
POST /api/v1/orders
```

An unsupported method must return an appropriate HTTP error rather than being interpreted as another operation.

The API must not silently convert:

```text
POST
```

into:

```text
GET
```

or another method.

---

# 10. Path Parameter Validation

Path parameters must be validated before application execution.

Example:

```text id="path1"
GET /api/v1/orders/{order_id}
```

`order_id` must conform to the expected identifier format.

For UUID resources:

```text
order_id = valid UUID
```

A malformed UUID must not trigger an unnecessary database query.

---

# 11. UUID Validation

UUID fields must use a consistent representation.

Example:

```json
{
  "product_id": "018f7e7c-..."
}
```

The API must reject:

* malformed UUIDs;
* unsupported identifier formats;
* invalid UUID types.

A valid UUID does not imply resource authorization.

---

# 12. Query Parameter Validation

Query parameters must be explicitly defined.

Examples:

```text
GET /orders?status=PAID
GET /orders?limit=50
GET /orders?cursor=...
GET /orders?from=2026-10-01
GET /orders?to=2026-10-31
```

Unknown or unsupported parameters should be rejected or explicitly ignored according to the endpoint contract.

For security-sensitive endpoints, rejecting unsupported parameters is preferred.

---

# 13. Query Parameter Types

Query parameters must be converted to defined application types.

Examples:

```text
limit → integer
status → enum
branch_id → UUID
from → date/time
include_archived → boolean
```

The API must not pass raw query strings directly to business logic or database queries.

---

# 14. Boolean Parameters

Boolean query parameters must use a documented representation.

Example:

```text
include_archived=true
include_archived=false
```

Ambiguous representations should not be silently interpreted.

---

# 15. Numeric Validation

Numeric values must have explicit constraints.

Examples:

```text
quantity > 0
percentage >= 0
percentage <= 100
limit >= 1
```

The API must reject:

* NaN;
* Infinity;
* malformed numeric values;
* unsupported numeric representations.

---

# 16. Money Representation

Financial values must use an explicit decimal representation.

Preferred API representation:

```json
{
  "amount": "25000.00"
}
```

The API must not rely on binary floating-point values for authoritative financial amounts.

Money fields must have documented:

* precision;
* scale;
* currency semantics where applicable;
* rounding rules where applicable.

---

# 17. Percentage Validation

Percentage fields must define their valid range.

For custom markup:

```text
0% ≤ markup ≤ 100%
```

The API must reject:

```text
markup < 0
markup > 100
```

Business-specific percentage rules remain in the Application/Domain layer.

---

# 18. String Validation

String fields must define:

* minimum length where required;
* maximum length;
* allowed character rules where necessary;
* whitespace behavior;
* normalization behavior where required.

The API must avoid arbitrary unlimited string lengths.

---

# 19. String Normalization

The API may normalize fields where the business contract explicitly permits it.

Examples:

* trimming leading/trailing whitespace;
* normalized email representation;
* normalized case for controlled identifiers.

The API must not silently alter business values where exact historical preservation is required.

---

# 20. Empty Strings

The contract must distinguish between:

```text id="empty1"
missing
```

and:

```text id="empty2"
""
```

An empty string must not automatically mean:

```text null
```

unless explicitly defined by the endpoint schema.

---

# 21. Nullability

Each field must explicitly define whether it may be:

* required and non-null;
* required but nullable;
* optional;
* optional and nullable.

Example:

```json
{
  "comment": null
}
```

must have a defined semantic meaning.

Clients must not infer null behavior from implementation details.

---

# 22. Required Fields

Required request fields must be explicitly documented.

Example:

```json
{
  "method": "CASH",
  "amount": "25000.00"
}
```

If `method` is required, omission must produce a structured validation error.

The API must not silently provide an undocumented default.

---

# 23. Optional Fields

Optional fields may be omitted when the operation supports them.

Example:

```json
{
  "comment": "Correction reason"
}
```

An omitted optional field and an explicitly provided `null` value may have different meanings.

The contract must define the difference.

---

# 24. Default Values

Defaults may be applied only when they are part of the API contract.

Examples:

```text
limit:
default 50

include_archived:
default false
```

Defaults must not hide missing mandatory business information.

---

# 25. Enum Validation

Enumerated fields must accept only documented values.

Example:

```json
{
  "method": "CASH"
}
```

If supported values are:

```text
CASH
CARD
```

then:

```text
BITCOIN
```

must be rejected.

Enum values are contract identifiers and should remain stable.

---

# 26. Enum Evolution

Adding a new enum value may affect older clients.

Therefore:

* clients should handle unknown values safely;
* API documentation must identify enum evolution expectations;
* incompatible enum changes may require API versioning.

Removing or changing the semantic meaning of an existing enum value is a breaking contract change.

---

# 27. Date Validation

Date-only fields must use an explicit date format.

Example:

```text
2026-10-06
```

Date-only values must not be interpreted through local timezone conversion.

---

# 28. Timestamp Validation

Timestamps should use ISO 8601.

Example:

```text
2026-10-06T10:30:00Z
```

Important server events use server-generated timestamps.

Client timestamps may be retained as metadata for offline synchronization but must not override server event time.

---

# 29. Timezone Handling

The API must distinguish:

* UTC timestamp;
* Business timezone;
* Branch timezone;
* date-only business values.

Reports, payroll and daily operational boundaries must not rely on ambiguous timestamps.

---

# 30. Future and Past Dates

Endpoints must define whether future or historical dates are permitted.

The API may structurally validate date format, while the Application/Domain layer validates business restrictions.

Example:

```text
API:
date = valid ISO date

Domain:
payroll period cannot be closed
```

---

# 31. Nested Object Validation

Nested request objects must be validated recursively.

Example:

```json
{
  "customer": {
    "phone": "...",
    "address": "..."
  }
}
```

The API must validate:

* object type;
* required nested fields;
* nested field types;
* nested field lengths;
* nested collection limits.

---

# 32. Collection Validation

Collections must have explicit limits.

Examples:

```text
order_items:
minimum 1
maximum defined by contract

sync_operations:
maximum 100

bulk_items:
maximum defined by endpoint
```

Unbounded arrays are prohibited.

---

# 33. Duplicate Collection Items

Where duplicate identifiers are not valid, the API should detect duplicates structurally.

Example:

```json
{
  "product_ids": [
    "A",
    "A"
  ]
}
```

may be rejected if the endpoint contract requires unique values.

Business-specific duplicate semantics remain in the Application layer.

---

# 34. Request Schema Separation

API request schemas should be separate from:

* database models;
* ORM entities;
* domain entities;
* repository models.

The API contract must not expose internal persistence structure.

---

# 35. DTO Boundary

The API should use explicit request and response DTO/schema models.

Conceptually:

```text id="dto1"
HTTP JSON
   ↓
Request Schema
   ↓
Application Command
   ↓
Domain
```

and:

```text id="dto2"
Domain/Application Result
   ↓
Response DTO
   ↓
HTTP JSON
```

---

# 36. No Direct ORM Serialization

ORM/database entities must not be serialized directly into public API responses.

Direct serialization can expose:

* internal fields;
* relationships;
* security-sensitive data;
* implementation details;
* unintended database structure.

Response schemas must be explicit.

---

# 37. Request Schema Versioning

Request schemas are part of the API contract.

Compatible changes may include:

* adding optional request fields;
* adding optional nested data;
* adding supported filters.

Breaking changes require explicit compatibility handling or a new API version.

---

# 38. Unknown Request Fields

The API must define how unknown fields are handled.

For security-sensitive operations, rejecting unknown fields is preferred.

Example:

```json
{
  "amount": "25000.00",
  "is_admin": true
}
```

If `is_admin` is not part of the contract, it must not be silently interpreted.

The endpoint should reject it or explicitly ignore it according to the documented schema policy.

---

# 39. Mass Assignment Protection

The API must not automatically map every incoming JSON field onto a domain or persistence object.

Example:

```json
{
  "name": "Burger",
  "business_id": "another-business",
  "created_by": "another-user"
}
```

Client-controlled fields such as:

* Business ownership;
* creator;
* audit actor;
* system status;
* internal version;

must not be assignable unless explicitly allowed.

---

# 40. Server-Managed Fields

Server-managed fields may include:

```text
id
business_id
created_at
updated_at
created_by
updated_by
version
status
audit metadata
```

The API must clearly distinguish client-controlled fields from server-managed fields.

---

# 41. Business and Branch Fields

Clients may provide Business/Branch references where the endpoint requires them.

However, these values remain subject to authorization and scope validation.

The API must not blindly copy:

```text
business_id
branch_id
```

into persistent records.

---

# 42. Actor Fields

Clients must not normally provide authoritative:

```text
employee_id
created_by
approved_by
paid_by
closed_by
```

The server derives actor identity from authenticated request context.

Where offline synchronization requires an actor identifier, it remains subject to server verification.

---

# 43. Device Fields

Client-provided Device IDs may be included for synchronization or diagnostic purposes.

They must not override the authenticated/trusted device context.

The server must validate device ownership and trust.

---

# 44. Request Context vs Request Body

The request body describes the requested operation.

Request context describes:

* actor;
* Business;
* Branch;
* Device;
* Cash Session;
* request;
* operation.

The body must not override authoritative context.

---

# 45. File Request Validation

File endpoints must validate:

* file size;
* MIME type;
* extension where applicable;
* file purpose;
* resource ownership;
* upload limits.

File validation must not rely only on client-provided MIME type.

File security is further defined in the backend file storage architecture.

---

# 46. Synchronization Request Validation

Synchronization requests require stricter structural validation.

Each operation should contain sufficient fields such as:

```text
operation_id
operation_type
entity_id
Business context where applicable
Branch context where applicable
device context
client timestamp
sequence where applicable
payload
```

The server must validate the structure before processing the operation.

Authorization and reconciliation are handled separately.

---

# 47. Offline Payload Validation

Offline payloads must not be trusted merely because they originated from a trusted device.

The server must validate:

* schema;
* operation type;
* resource identity;
* scope;
* authorization;
* idempotency;
* current server state;
* synchronization rules.

---

# 48. Request Validation and Idempotency

Idempotency keys must themselves be structurally validated.

Example:

```http
Idempotency-Key: 8d6c2d6e-...
```

The server must reject malformed idempotency identifiers.

Idempotency behavior is defined further in:

`10_API_Idempotency_and_Concurrency.md`

---

# 49. Request Validation and Concurrency

Version fields and conditional headers must be validated structurally.

Example:

```http
If-Match: "12"
```

The API validates the format.

The Application layer determines whether version `12` is still current.

A stale version produces a conflict rather than a schema validation error.

---

# 50. Header Validation

Supported headers must be explicitly defined.

Examples:

```text
Authorization
X-Request-ID
X-Business-ID
X-Branch-ID
X-Device-ID
Idempotency-Key
If-Match
If-None-Match
```

Header values must be validated before use.

Client-controlled headers are never authoritative by themselves.

---

# 51. Header Size Limits

Headers must have bounded sizes.

The API should reject oversized:

* request IDs;
* idempotency keys;
* context headers;
* authorization headers;
* custom metadata.

This prevents unnecessary memory consumption and abuse.

---

# 52. Content Type

JSON endpoints should require an appropriate content type.

Example:

```text
Content-Type: application/json
```

Unsupported content types should be rejected unless the endpoint explicitly supports them.

File endpoints may use multipart or another explicitly documented format.

---

# 53. Content Negotiation

If the API supports content negotiation, supported formats must be explicitly documented.

The API should avoid unnecessary response-format complexity during the initial implementation.

The default public representation should remain predictable.

---

# 54. Response Contract Principle

Every public endpoint must have an explicit response contract.

The response must define:

* status code;
* content type;
* response body;
* fields;
* field types;
* nullability;
* nested structures;
* pagination metadata where applicable;
* error behavior.

---

# 55. Response Envelope

The API may use a consistent envelope.

Single resource:

```json
{
  "data": {
    "id": "018f...",
    "name": "Burger"
  }
}
```

List:

```json
{
  "data": [],
  "pagination": {
    "next_cursor": "...",
    "has_more": true
  }
}
```

Error:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "request_id": "01J...",
    "details": {}
  }
}
```

The envelope should remain consistent across API modules.

---

# 56. Single Resource Response

A single resource response should contain only fields required by the public contract.

Example:

```json
{
  "data": {
    "id": "018f...",
    "name": "Burger",
    "active": true,
    "price": "30000.00"
  }
}
```

Internal database columns must not appear merely because they exist.

---

# 57. List Response

List responses must use bounded collections.

Example:

```json
{
  "data": [
    {
      "id": "018f...",
      "name": "Burger"
    }
  ],
  "pagination": {
    "next_cursor": "eyJ...",
    "has_more": true
  }
}
```

Large datasets must use pagination rather than oversized responses.

---

# 58. Pagination Metadata

Pagination metadata should define only the information required by the client.

Recommended:

```text
next_cursor
has_more
```

Additional metadata may be provided where useful.

The API should avoid expensive total-count queries unless the endpoint specifically requires them.

---

# 59. Empty List Response

An empty collection is still a successful response when the request is valid.

Example:

```json
{
  "data": [],
  "pagination": {
    "next_cursor": null,
    "has_more": false
  }
}
```

An empty list must not be treated as an error.

---

# 60. Empty Resource Response

When an endpoint intentionally returns no body:

```http
204 No Content
```

may be used.

The endpoint contract must explicitly define this behavior.

---

# 61. Created Resource Response

Creation endpoints should normally return:

```http
201 Created
```

with the created resource or an explicitly defined representation.

Example:

```text
POST /api/v1/products
```

must not return an ambiguous empty response when the client requires the created resource identity.

---

# 62. Mutation Response

For successful mutation operations, the API should return the authoritative resulting state when practical.

Example:

```text
PATCH /products/{id}
```

may return:

```json
{
  "data": {
    "id": "...",
    "version": 13,
    "active": true
  }
}
```

The returned state must represent committed authoritative state.

---

# 63. Business Command Response

Command endpoints should return a representation of the authoritative result.

Example:

```text
POST /orders/{id}/accept
```

may return:

```json
{
  "data": {
    "order_id": "...",
    "status": "ACCEPTED",
    "version": 8
  }
}
```

The response must not imply success before the core transaction commits.

---

# 64. Financial Response

Financial operations must return authoritative financial state.

Example:

```json
{
  "data": {
    "payment_id": "...",
    "order_id": "...",
    "amount": "25000.00",
    "status": "COMPLETED"
  }
}
```

The client-provided amount is not authoritative.

The response represents server-calculated and committed state.

---

# 65. Configuration Response

Configuration resources should expose version information where concurrency or synchronization requires it.

Example:

```json
{
  "data": {
    "id": "...",
    "version": 12,
    "status": "EFFECTIVE"
  }
}
```

Clients may use the version for optimistic concurrency.

---

# 66. Resource Version

Resources requiring optimistic concurrency should expose a version or equivalent concurrency token.

The version must change according to the defined mutation rules.

Clients must not modify the version directly unless the contract explicitly defines a conditional update mechanism.

---

# 67. Response Serialization

Response serialization should be performed through explicit response schemas.

The serializer should:

* select allowed fields;
* convert domain values;
* apply documented formatting;
* omit forbidden fields;
* preserve required nullability;
* produce valid JSON.

---

# 68. Sensitive Field Filtering

Response schemas must explicitly prevent exposure of:

* password hashes;
* access tokens;
* refresh tokens;
* private keys;
* internal secrets;
* database credentials;
* internal filesystem paths;
* security-sensitive internal metadata.

Sensitive fields must not appear accidentally because of generic serialization.

---

# 69. Role-Based Response Fields

Some response fields may depend on authorization.

Example:

```text
Employee A:
can view salary

Employee B:
cannot view salary
```

The response representation must be authorization-aware.

The API must not return sensitive fields and rely on the frontend to hide them.

---

# 70. Business/Branch Response Filtering

Responses must include only resources within the authorized scope.

For example:

```text
GET /orders
```

must return:

```text
Authorized Business
+
Authorized Branches
```

only.

Scope filtering must occur at data-access/query level where practical.

---

# 71. Historical Response Integrity

Historical response data must use historical snapshots where defined.

Examples:

```text
Historical Order Price
≠
Current Product Price
```

```text
Historical Recipe Version
≠
Current Recipe
```

```text
Historical Set Configuration
≠
Current Set Configuration
```

Response serialization must not reconstruct historical state from current configuration.

---

# 72. Decimal Serialization

Decimal values must use the standardized financial representation.

Example:

```json
{
  "amount": "25000.00",
  "discount": "5000.00"
}
```

The API must not expose inconsistent representations such as:

```text
25000
25000.0
25000.0000001
```

for the same financial field without an explicit contract.

---

# 73. Date/Time Serialization

Timestamps must use the documented ISO 8601 representation.

Example:

```json
{
  "created_at": "2026-10-06T10:30:00Z"
}
```

Date-only fields must remain date-only.

The API must not unexpectedly convert a date-only value into a timestamp.

---

# 74. Boolean Serialization

Boolean values must be JSON booleans.

Correct:

```json
{
  "active": true
}
```

Incorrect:

```json
{
  "active": "true"
}
```

unless an explicitly documented legacy contract requires another representation.

---

# 75. Identifier Serialization

UUID identifiers should use the standardized string representation.

Example:

```json
{
  "id": "018f7e7c-..."
}
```

The API must use one consistent representation across endpoints.

---

# 76. Enum Serialization

Response enum values must use stable machine-readable identifiers.

Example:

```json
{
  "status": "PAID"
}
```

Human-readable translated labels should not replace machine-readable enum values.

Localization belongs to the presentation layer.

---

# 77. Localization

API responses should generally remain language-neutral.

For example:

```json
{
  "error": {
    "code": "ORDER_ALREADY_PAID",
    "message": "The order has already been paid."
  }
}
```

The stable identifier is:

```text
ORDER_ALREADY_PAID
```

Clients may localize messages where required.

---

# 78. Response Messages

Human-readable response messages should support users and developers but must not be the primary machine contract.

Clients should depend on:

* HTTP status;
* stable error code;
* documented response fields.

Messages may be improved without changing the semantic error code.

---

# 79. Error Response Contract

Validation errors should use the common API error structure.

Example:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "request_id": "01J...",
    "details": {
      "fields": [
        {
          "field": "amount",
          "code": "INVALID_DECIMAL",
          "message": "Invalid monetary value."
        }
      ]
    }
  }
}
```

The exact field-level schema must remain stable.

---

# 80. Field-Level Validation Errors

When useful, validation errors should identify:

* field;
* validation code;
* human-readable message.

Example:

```json
{
  "field": "markup",
  "code": "OUT_OF_RANGE"
}
```

The API must not expose internal stack traces or implementation details.

---

# 81. Nested Validation Errors

Nested fields should use a deterministic path.

Example:

```text
items[0].quantity
customer.phone
recipe.components[2].product_id
```

This allows clients to associate validation errors with UI fields.

---

# 82. Multiple Validation Errors

The API may return multiple independent structural validation errors in one response.

Example:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "details": {
      "fields": [
        {
          "field": "amount",
          "code": "REQUIRED"
        },
        {
          "field": "method",
          "code": "INVALID_ENUM"
        }
      ]
    }
  }
}
```

The API should avoid returning only the first error when multiple independent errors can be safely reported.

---

# 83. Validation Error Status

Initial validation mapping:

```text
400 Bad Request
```

may be used for malformed request structure.

```text
422 Unprocessable Entity
```

may be used for semantically invalid input after successful parsing.

The API must use one consistent policy across endpoints.

---

# 84. Authorization vs Validation Error

The API must distinguish:

```text
Malformed request
```

from:

```text
Unauthorized request
```

and:

```text
Valid request but invalid business operation
```

Examples:

```text
Invalid UUID
→ Validation

No permission
→ Authorization

Insufficient stock
→ Business Rule

Stale version
→ Conflict
```

---

# 85. Response Headers

Responses may include standard headers such as:

```text
X-Request-ID
ETag
Cache-Control
Retry-After
Location
```

Only headers relevant to the endpoint should be included.

---

# 86. ETag

ETag may be used for read-heavy resources and conditional requests.

Example:

```http
ETag: "resource-version-12"
```

A matching conditional request may avoid unnecessary transfer.

ETag must not replace:

* authorization;
* resource scope validation;
* business state validation.

---

# 87. Cache-Control

Response cache behavior must be explicitly defined.

Examples:

```text
Cache-Control: private
Cache-Control: no-store
Cache-Control: max-age=...
```

Sensitive responses must not be cached in a way that could expose data across users, Businesses or Branches.

---

# 88. Response Compression

Compression may be enabled for sufficiently large responses.

It should not be required for correctness.

Small POS responses may remain uncompressed where compression overhead is unnecessary.

---

# 89. Large Response Handling

Large datasets must use:

* pagination;
* asynchronous jobs;
* streaming where explicitly justified;
* file export for report/download use cases.

The API must not return unbounded JSON responses.

---

# 90. Asynchronous Response Contract

Long-running operations should return:

```http
202 Accepted
```

Example:

```json
{
  "data": {
    "job_id": "...",
    "status": "PENDING"
  }
}
```

The client then queries a status resource.

---

# 91. Async Job Result

A completed job may return:

```json
{
  "data": {
    "job_id": "...",
    "status": "COMPLETED",
    "result": {
      "file_id": "..."
    }
  }
}
```

The job result must be authorization-controlled.

---

# 92. Partial Success Response

Operations supporting independent item processing may return per-item results.

Example:

```json
{
  "data": {
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
}
```

This is especially relevant to synchronization and bounded bulk operations.

---

# 93. Response Status Consistency

The same semantic result should use consistent HTTP status codes across endpoints.

For example:

```text
Validation
→ 400/422 according to contract

Unauthorized
→ 403

Conflict
→ 409

Accepted async operation
→ 202
```

Endpoints must not arbitrarily invent alternative status meanings.

---

# 94. Response Ordering

For lists, response ordering must follow the endpoint's documented ordering.

If ordering is:

```text
created_at DESC
id DESC
```

the response must consistently follow it.

Stable ordering is required for deterministic pagination.

---

# 95. Response Field Ordering

JSON object field order must not be treated as semantically significant.

The API may use a consistent serialization order for readability, but clients must not depend on it.

---

# 96. Response Size

Response payloads should remain bounded and purpose-specific.

The API should avoid returning:

* full audit history inside ordinary resource responses;
* full recipe history inside Product responses;
* full payment history inside Order list responses;
* unnecessary nested Business data.

Related data should be requested through dedicated endpoints or controlled expansions where supported.

---

# 97. Embedded Resource Data

Embedded related resources may be returned where they materially improve client performance.

However:

* authorization must apply to embedded data;
* response size must remain bounded;
* circular relationships must be avoided;
* historical snapshots must remain authoritative.

The default should favor explicit resource representations over deeply nested graphs.

---

# 98. Response Expansion

If the API supports an `include` or `expand` mechanism, allowed values must be explicitly defined.

Example:

```text
GET /orders/{id}?include=items
```

The API must reject arbitrary field expansion.

Expansion must not bypass authorization.

---

# 99. API Contract Stability

Public response fields should remain stable.

A field should not change meaning silently.

For example:

```text
price
```

must not change from:

```text
Product base price
```

to:

```text
Final discounted Order price
```

without an explicit contract change.

---

# 100. Backward-Compatible Response Changes

Generally compatible:

* adding optional response fields;
* adding new optional metadata;
* adding new response links where clients ignore them safely.

Potentially breaking:

* removing fields;
* changing field types;
* changing nullability;
* changing enum semantics;
* changing units;
* changing monetary precision;
* changing field meaning.

---

# 101. Response Contract and Historical Data

Current configuration must not be used to reinterpret historical API responses.

For historical resources, the response must use:

* transaction snapshots;
* historical configuration versions;
* historical financial values;
* immutable audit data.

The current Product/Menu/Recipe configuration is not a substitute.

---

# 102. API Contract and Security

The response contract must follow least exposure.

Only data necessary for the authorized client operation should be returned.

The API must not expose additional fields simply because they are available in the database.

---

# 103. API Contract and Business Isolation

Every response must preserve Business isolation.

No response may contain:

* another Business's resources;
* another Business's aggregates;
* another Business's configuration;
* another Business's notifications;
* another Business's files.

unless the authenticated actor has an explicitly defined platform-level capability.

---

# 104. API Contract and Branch Isolation

Branch-scoped responses must contain only authorized Branch data.

For multi-Branch employees, responses may contain multiple authorized Branches when the endpoint explicitly supports it.

Unauthorized Branch data must never appear as hidden metadata.

---

# 105. API Contract and Subscription

Response visibility may depend on subscription state.

For example:

```text
READ_ONLY
→ historical data visible
→ mutation unavailable
```

The response contract should clearly distinguish current state from allowed actions.

The frontend must not infer subscription authorization solely from missing buttons.

---

# 106. API Contract and Permissions

Sensitive response fields may require additional permissions.

Example:

```text
Employee salary
Payroll details
Audit details
Cost information
```

The API should return only fields the actor is authorized to view.

---

# 107. API Contract and Offline Clients

Offline-capable clients require stable response schemas.

Responses used for local persistence must contain sufficient information for:

* local state;
* synchronization;
* version tracking;
* operation references;
* configuration identity.

The API must not change offline-critical fields without compatibility planning.

---

# 108. API Contract and Synchronization

Synchronization responses must provide enough information for deterministic client handling.

Examples:

```text
operation_id
status
server_entity_id where applicable
server_version where applicable
conflict information where safe
retryability
```

The response must not require the client to guess whether an operation succeeded.

---

# 109. API Contract and Idempotency

For an already-processed idempotent operation, the API should return the original authoritative result where safely possible.

Example:

```text
First request
→ Payment COMPLETED

Retry
→ Same Payment COMPLETED result
```

The client must not interpret the retry as a new financial operation.

---

# 110. API Contract and Concurrency

Conflict responses must provide enough information for the client to recover.

Example:

```json
{
  "error": {
    "code": "STALE_VERSION",
    "message": "The resource was changed by another operation.",
    "request_id": "01J...",
    "details": {
      "current_version": 13
    }
  }
}
```

Only safe and necessary information should be exposed.

---

# 111. API Contract and Error Consistency

All API modules should use the common error contract.

The same error concept must not be represented differently across endpoints without a documented reason.

Example:

```text
INSUFFICIENT_STOCK
```

should not become:

```text
STOCK_ERROR
```

in another endpoint if both represent the same public semantic condition.

---

# 112. API Contract and Localization

Machine-readable identifiers remain stable across languages.

Example:

```text
PERMISSION_REQUIRED
```

may have localized UI messages:

```text
English
Uzbek
Russian
```

The API contract itself remains language-neutral.

---

# 113. API Contract and Documentation

Every public request/response schema must be represented in the API specification.

The documentation should include:

* field type;
* required/optional status;
* nullable status;
* enum values;
* examples;
* validation constraints;
* response status;
* error codes.

---

# 114. OpenAPI Schema

OpenAPI should represent:

```text
paths
parameters
requestBody
responses
schemas
security
headers
examples
enums
pagination
errors
```

The OpenAPI schema must be generated or maintained in a controlled manner so that it does not diverge from implementation.

---

# 115. Contract Testing

Contract tests must verify:

* valid request;
* invalid request;
* required fields;
* field types;
* response schema;
* status codes;
* error codes;
* pagination;
* authorization-sensitive fields;
* enum behavior;
* backward compatibility.

---

# 116. Schema Testing

Schema tests should detect:

* accidental field removal;
* type changes;
* nullability changes;
* enum changes;
* undocumented fields;
* incorrect status codes;
* incompatible response changes.

Breaking contract changes must fail CI unless explicitly approved.

---

# 117. Request Validation Testing

Validation tests should cover:

```text
missing fields
wrong types
invalid UUID
invalid enum
invalid decimal
out-of-range number
invalid date
invalid timestamp
oversized string
oversized collection
unknown field
duplicate item
invalid header
oversized request
```

---

# 118. Response Contract Testing

Response tests should verify:

* required fields exist;
* field types are correct;
* sensitive fields are absent;
* scope restrictions are respected;
* historical snapshots are correct;
* monetary values use the defined format;
* timestamps use the defined format;
* pagination metadata is correct.

---

# 119. Security Contract Testing

Security tests must verify that malformed or crafted requests cannot:

* bypass authorization;
* inject Business/Branch ownership;
* assign actor identity;
* modify server-managed fields;
* expose sensitive response fields;
* bypass subscription restrictions.

---

# 120. Performance and Validation

Validation should remain lightweight for normal POS requests.

The API should avoid:

* unnecessary schema transformations;
* repeated parsing;
* large nested response generation;
* expensive validation that belongs in background processing.

Initial targets:

| Operation                                         |                       Target |
| ------------------------------------------------- | ---------------------------: |
| Request structural validation p95                 |                      ≤ 20 ms |
| Response serialization p95 for normal POS payload |                      ≤ 20 ms |
| Normal API response payload                       | bounded by endpoint contract |
| Core POS API p95                                  |                     ≤ 500 ms |

These are architectural targets and must be validated under realistic load.

---

# 121. Validation Failure Performance

Malformed requests should fail early.

For example:

```text
Invalid UUID
```

should not cause:

```text
Database query
+
Domain execution
+
Transaction
```

Early rejection reduces unnecessary resource consumption.

---

# 122. Validation and Abuse Protection

Validation limits protect against:

* oversized requests;
* deeply nested JSON;
* huge arrays;
* excessive strings;
* invalid repeated requests.

Rate limiting and request size limits provide additional protection.

Validation is not a substitute for authentication or authorization.

---

# 123. Validation and Logging

Validation failures may be logged or metered for operational/security analysis.

Logs must not contain complete sensitive request bodies.

Especially avoid logging:

* passwords;
* tokens;
* secrets;
* private keys;
* payment-sensitive credentials.

---

# 124. Validation and Observability

Metrics may include:

```text
validation_error_count
schema_error_count
invalid_uuid_count
invalid_enum_count
invalid_request_size_count
```

Metrics must remain low-cardinality.

Do not use arbitrary field values as metric labels.

---

# 125. Validation and API Evolution

When a request schema evolves:

```text
Existing Client
      ↓
Compatible Contract
      ↓
New Optional Capability
```

should be preferred over forcing all clients to upgrade simultaneously.

This is especially important for:

* POS clients;
* offline devices;
* synchronization;
* older browser sessions.

---

# 126. Validation and Offline Compatibility

Offline clients may synchronize requests after a delay.

Therefore:

* old operation schemas may need compatibility handling;
* schema versions may be retained where necessary;
* unsupported old operations must receive deterministic errors;
* the server must never guess the meaning of an unknown operation payload.

---

# 127. Request Schema Version

Where synchronization or long-lived clients require explicit schema versioning, the request may contain:

```json
{
  "schema_version": 1
}
```

Schema versioning must be introduced only where it solves a real compatibility requirement.

The API URI version remains the primary public contract version.

---

# 128. Response Schema Version

Normal synchronous API responses should rely on the API version rather than adding unnecessary per-response schema versions.

Explicit response versioning may be used for long-lived asynchronous or offline payloads where required.

---

# 129. Contract Ownership

Each API module should have a clearly owned contract.

Conceptually:

```text
API Endpoint
    ↓
Request Schema
    ↓
Application Command
    ↓
Domain
    ↓
Response DTO
```

Changes should be reviewed by the responsible architecture/application owners.

---

# 130. Contract Change Review

Before changing a public schema, verify:

1. frontend impact;
2. POS impact;
3. offline client impact;
4. synchronization impact;
5. database impact;
6. authorization impact;
7. historical integrity;
8. backward compatibility;
9. OpenAPI changes;
10. contract tests;
11. performance impact.

---

# 131. API Response Design Guardrails

The implementation must prohibit:

* direct ORM serialization;
* direct database model exposure;
* unbounded list responses;
* undocumented response fields becoming public contract;
* sensitive fields in generic serializers;
* client-controlled server-managed fields;
* floating-point authoritative money values;
* ambiguous timestamps;
* unstable enum semantics;
* current configuration replacing historical snapshots;
* unauthorized embedded resources;
* response data from another Business;
* response data from unauthorized Branches.

---

# 132. System Invariants

The following invariants apply to API Request Validation and Response Contracts:

1. Every public endpoint has an explicit request contract.
2. Every public endpoint has an explicit response contract.
3. Request structure is validated server-side.
4. Frontend validation never replaces server validation.
5. API structural validation is separate from domain business validation.
6. Malformed requests are rejected before unnecessary application processing.
7. Path parameters are validated before resource lookup where possible.
8. Query parameters are explicitly defined.
9. Request bodies use explicit schemas.
10. Nested objects are recursively validated.
11. Collections are bounded.
12. Request size is bounded.
13. Header sizes are bounded.
14. UUID fields use a consistent representation.
15. Valid UUIDs do not imply authorization.
16. Numeric fields have explicit ranges where required.
17. NaN and Infinity are rejected.
18. Money uses explicit decimal representation.
19. Authoritative money values are not represented as binary floating-point numbers.
20. Percentage ranges are explicitly defined.
21. String lengths are bounded.
22. Empty strings and null values have defined semantics.
23. Required fields are explicitly documented.
24. Optional fields have defined omission semantics.
25. Defaults are part of the public contract when used.
26. Enum values are stable machine-readable identifiers.
27. Enum semantic changes are treated as compatibility-sensitive.
28. Date-only values are not implicitly converted through timezone logic.
29. Timestamps use the defined ISO 8601 representation.
30. Server timestamps are authoritative for important events.
31. Client timestamps cannot override authoritative server event time.
32. API schemas are separate from ORM/database models.
33. ORM entities are never serialized directly as public API responses.
34. Client input cannot mass-assign protected server-managed fields.
35. Business ownership is server-controlled.
36. Branch ownership is server-controlled.
37. Actor identity is server-controlled.
38. Audit actor identity is server-controlled.
39. Device identity is server-controlled.
40. Server-managed versions cannot be arbitrarily overwritten by clients.
41. Unknown fields follow an explicit endpoint policy.
42. Sensitive endpoints should prefer rejecting unknown fields.
43. File requests have bounded size.
44. Synchronization requests have bounded batch size.
45. Offline payloads are validated before processing.
46. Idempotency keys have a defined format.
47. Concurrency/version headers have a defined format.
48. Response schemas expose only authorized data.
49. Sensitive fields are never exposed through generic serialization.
50. Response field visibility may depend on authorization.
51. Business scope is enforced in response data.
52. Branch scope is enforced in response data.
53. Historical responses use authoritative historical snapshots.
54. Current configuration cannot reinterpret historical transactions.
55. Single-resource responses use a predictable representation.
56. List responses use bounded collections.
57. Large lists use pagination.
58. Empty lists are valid successful responses when applicable.
59. No-content responses use 204 only when explicitly defined.
60. Creation responses use 201 when a resource is created.
61. Long-running operations use asynchronous response contracts where appropriate.
62. Async jobs expose deterministic status.
63. Partial-result operations return per-operation status where required.
64. Response status codes are semantically consistent.
65. Pagination ordering is deterministic.
66. JSON field ordering is not semantically significant.
67. Response payloads remain bounded.
68. Related resources do not create uncontrolled nested graphs.
69. Resource expansion is explicitly controlled.
70. Response fields do not silently change semantic meaning.
71. Compatible response changes do not remove or reinterpret existing fields.
72. Breaking response changes require explicit compatibility handling.
73. API error responses use stable error codes.
74. Validation errors can identify affected fields where useful.
75. Nested validation errors use deterministic field paths.
76. Authorization errors are distinct from structural validation errors.
77. Business rule violations are distinct from malformed input.
78. Conflict errors are distinct from schema errors.
79. Human-readable messages are not the primary machine contract.
80. API responses remain language-neutral at the contract level.
81. Sensitive responses use appropriate cache-control behavior.
82. ETag never replaces authorization.
83. API compression does not change semantic response data.
84. Response serialization is explicit and controlled.
85. OpenAPI reflects the implemented contract.
86. Contract tests validate request schemas.
87. Contract tests validate response schemas.
88. Contract tests validate status codes.
89. Contract tests validate error codes.
90. Contract tests detect incompatible schema changes.
91. Security tests verify server-managed field protection.
92. Security tests verify Business isolation.
93. Security tests verify Branch isolation.
94. Security tests verify sensitive response filtering.
95. Validation metrics remain low-cardinality.
96. Validation failures do not expose secrets.
97. Validation should remain lightweight for normal POS operations.
98. Request validation failures should occur before unnecessary database work.
99. API versioning remains the primary public contract versioning mechanism.
100. Additional schema versioning is introduced only where justified.
101. Offline clients receive deterministic responses for unsupported schemas.
102. Synchronization clients cannot rely on undocumented response fields.
103. API contracts remain compatible with POS clients.
104. API contracts remain compatible with offline synchronization.
105. API contracts preserve historical integrity.
106. API contracts preserve Business isolation.
107. API contracts preserve Branch isolation.
108. API contracts preserve authorization boundaries.
109. API contracts preserve financial precision.
110. API contracts preserve server authority.
111. API contracts do not expose database implementation details.
112. API request validation does not contain core business rules.
113. Response serialization does not contain core business rules.
114. Application commands remain separate from HTTP schemas.
115. API contracts are documented and testable.
116. Contract changes are reviewed before release.
117. Security-sensitive schema changes require dedicated testing.
118. Performance targets are validated under realistic load.
119. The API must never trust client validation as authoritative.
120. The API must never expose unauthorized data merely because it exists in the underlying model.

---

# 133. Recommended API Schema Structure

A possible implementation structure is:

```text
app/
├── api/
│   ├── schemas/
│   │   ├── common.py
│   │   ├── errors.py
│   │   ├── pagination.py
│   │   ├── auth.py
│   │   ├── businesses.py
│   │   ├── branches.py
│   │   ├── employees.py
│   │   ├── products.py
│   │   ├── recipes.py
│   │   ├── inventory.py
│   │   ├── menu.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   ├── cash.py
│   │   ├── reports.py
│   │   ├── files.py
│   │   ├── notifications.py
│   │   ├── configuration.py
│   │   └── synchronization.py
│   │
│   ├── v1/
│   └── ...
│
├── application/
├── domain/
└── infrastructure/
```

Exact module names may be refined during implementation.

---

# 134. Related API Documents

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/04_Architecture/09_API/05_API_Resource_Model_and_Naming.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/11_API_Pagination_Search_Filtering_and_Sorting.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/03_Application_and_Use_Case_Layer.md`
* `docs/04_Architecture/06_Backend/04_Domain_Service_and_Business_Logic.md`
* `docs/04_Architecture/06_Backend/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/17_Backend_Testing_and_Quality_Assurance_Architecture.md`

### Database Architecture

* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Frontend Architecture

* `docs/04_Architecture/07_Frontend/22_Frontend_State_Management_and_Data_Flow.md`
* `docs/04_Architecture/07_Frontend/23_Frontend_API_Client_and_Data_Access_Architecture.md`
* `docs/04_Architecture/07_Frontend/24_Frontend_Offline_Storage_and_Local_Persistence_Architecture.md`
* `docs/04_Architecture/07_Frontend/25_Frontend_Offline_Synchronization_and_Conflict_Resolution.md`

---

# 135. Status

**API Architecture Section:** In Progress

**Document Status:** Proposed

**Current Document:** `08_API_Request_Validation_and_Response_Contracts.md`

**Previous Document:** `07_API_Authorization_and_Scope_Enforcement.md`

**Next Document:** `09_API_Error_Handling_and_Error_Codes.md`

---

## Final Principle

> Requests must be structurally valid before they enter application processing, and responses must expose only the explicitly defined, authorized and stable public contract.

