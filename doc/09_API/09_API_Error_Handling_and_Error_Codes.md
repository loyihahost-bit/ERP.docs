# API Error Handling and Error Codes

**Document ID:** API-09
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the error handling architecture and public error contract for the FastFood ERP API.

The API must return errors that are:

* predictable;
* machine-readable;
* security-safe;
* consistent across endpoints;
* actionable by clients;
* compatible with retries where appropriate;
* traceable through request and operation context.

API errors must not expose internal implementation details.

The error contract is part of the public API contract.

---

# 2. Scope

This document covers:

* API error architecture;
* error categories;
* exception mapping;
* HTTP status mapping;
* stable error codes;
* validation errors;
* authentication errors;
* authorization errors;
* Business/Branch scope errors;
* subscription errors;
* business rule violations;
* conflicts;
* concurrency errors;
* idempotency errors;
* synchronization errors;
* rate limiting;
* infrastructure failures;
* external dependency failures;
* timeout handling;
* retryability;
* error details;
* field-level errors;
* request ID;
* operation UUID;
* logging;
* monitoring;
* security-safe error exposure;
* client behavior;
* error contract testing;
* error compatibility;
* performance;
* invariants.

---

# 3. Error Handling Principles

The API follows these principles:

1. Every public API error has a stable machine-readable error code.
2. HTTP status communicates the broad error category.
3. Clients should rely primarily on error codes, not human-readable messages.
4. Internal exceptions must not be exposed directly.
5. Error responses must not expose secrets or sensitive infrastructure details.
6. Authorization failures must fail closed.
7. Retryability must be deterministic.
8. Validation errors should identify invalid fields where safe.
9. Conflicts should provide enough information for recovery where safe.
10. Unexpected errors must be traceable internally.
11. Error handling must not rollback already committed core transactions.
12. Secondary failures must remain separate from committed business state.
13. Error contracts must remain backward compatible.
14. Error codes must not silently change semantic meaning.
15. API errors must preserve Business and Branch isolation.
16. Error handling must remain lightweight enough for POS operations.

---

# 4. Error Architecture

The API error flow is:

```text
Exception / Failure
        ↓
Application / Infrastructure Classification
        ↓
Error Mapping
        ↓
Stable Error Code
        ↓
HTTP Status
        ↓
Safe Error Details
        ↓
Response Serialization
        ↓
Client
```

Internal exception types are not automatically public API error codes.

---

# 5. Error Boundary

The API boundary converts internal failures into public API errors.

Example:

```text
Domain Exception
    ↓
Application Error
    ↓
API Error Mapper
    ↓
409 Conflict
STALE_VERSION
```

The API must not return:

```text
Python traceback
SQL exception
ORM exception
Redis stack trace
filesystem path
```

to the client.

---

# 6. Error Categories

The initial public error categories are:

```text
Validation
Authentication
Authorization
Scope
Subscription
Business Rule
Conflict
Idempotency
Synchronization
Rate Limit
Not Found
Infrastructure
External Dependency
Timeout
```

The exact public `code` identifies the specific semantic condition.

---

# 7. Error Response Contract

The standard error response is:

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

Required fields:

```text
code
message
request_id
```

`details` may be empty or omitted according to the common response schema.

The structure must remain consistent across API modules.

---

# 8. Error Code

The error code is the primary machine-readable identifier.

Example:

```text
ORDER_ALREADY_PAID
```

Error codes must:

* be unique within the public API;
* have stable meaning;
* use a predictable naming convention;
* be documented;
* be covered by tests.

Clients must not parse the human-readable message to determine behavior.

---

# 9. Error Code Naming

The preferred format is:

```text
UPPER_SNAKE_CASE
```

Examples:

```text
VALIDATION_ERROR
ACCESS_DENIED
RESOURCE_NOT_FOUND
STALE_VERSION
INSUFFICIENT_STOCK
ORDER_ALREADY_PAID
CASH_SESSION_CLOSED
SERVICE_UNAVAILABLE
```

Codes should describe semantic conditions rather than implementation details.

Preferred:

```text
SERVICE_UNAVAILABLE
```

Not:

```text
REDIS_CONNECTION_REFUSED
```

---

# 10. Error Code Stability

Once a public error code is released, its meaning must remain stable.

The following are breaking changes:

* reusing a code for another condition;
* changing its retry semantics;
* changing its security meaning;
* changing the expected client recovery behavior.

A new semantic condition should receive a new error code.

---

# 11. Error Code Ownership

Each error code should have:

* defined meaning;
* category;
* HTTP status;
* retryability;
* expected client behavior;
* security exposure policy.

Example:

```text
STALE_VERSION

Category:
Conflict

HTTP:
409

Retry:
Conditional

Client:
Refresh resource and retry after user decision
```

---

# 12. HTTP Status and Error Code

HTTP status provides broad protocol semantics.

The error code provides application semantics.

Example:

```text
409 Conflict
+
STALE_VERSION
```

The client should use both.

The client must not assume that every `409` means the same business condition.

---

# 13. Initial HTTP Error Mapping

| Category                 |                 HTTP |
| ------------------------ | -------------------: |
| Validation               |            400 / 422 |
| Authentication           |                  401 |
| Authorization            |                  403 |
| Resource not found       |                  404 |
| Conflict                 |                  409 |
| Rate limit               |                  429 |
| Internal failure         |                  500 |
| Temporary unavailable    |                  503 |
| Gateway/upstream timeout | 504 where applicable |

The exact mapping must remain consistent after clients depend on it.

---

# 14. Validation Error

Validation errors indicate malformed or structurally invalid requests.

Example:

```text
400 Bad Request
VALIDATION_ERROR
```

Possible details:

```json
{
  "fields": [
    {
      "field": "amount",
      "code": "INVALID_DECIMAL",
      "message": "Invalid monetary value."
    }
  ]
}
```

Validation errors should be deterministic.

---

# 15. Semantic Validation

Some requests are structurally valid but semantically invalid.

Example:

```text
422 Unprocessable Entity
```

may be used for:

```text
INVALID_OPERATION_STATE
INVALID_DATE_RANGE
INVALID_CONFIGURATION
```

The implementation must use one consistent policy for `400` vs `422`.

---

# 16. Authentication Errors

Authentication errors indicate that the API cannot establish a valid authenticated identity.

Examples:

```text
AUTHENTICATION_REQUIRED
AUTHENTICATION_FAILED
TOKEN_EXPIRED
TOKEN_INVALID
SESSION_REVOKED
```

These normally map to:

```text
401 Unauthorized
```

The API must avoid revealing unnecessary details about why a credential failed.

---

# 17. Authorization Errors

Authorization errors occur when an authenticated actor cannot perform an operation.

Examples:

```text
ACCESS_DENIED
PERMISSION_REQUIRED
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
RESOURCE_ACCESS_DENIED
```

These normally map to:

```text
403 Forbidden
```

Authorization must fail closed.

---

# 18. Resource Not Found

A resource may produce:

```text
404 Not Found
RESOURCE_NOT_FOUND
```

The API may intentionally use `404` instead of `403` when revealing the existence of a resource would create information leakage.

The choice must be consistent with the endpoint security policy.

---

# 19. Business Scope Errors

Business scope violations indicate that the authenticated actor cannot operate on the requested Business.

Example:

```text
403
BUSINESS_SCOPE_DENIED
```

The API must not allow:

```text
Business A actor
→
Business B resource
```

through client-controlled IDs.

---

# 20. Branch Scope Errors

Branch scope violations indicate that the actor cannot operate within the requested Branch.

Example:

```text
403
BRANCH_SCOPE_DENIED
```

A valid Branch UUID does not grant access to that Branch.

---

# 21. Subscription Errors

Subscription restrictions are part of authorization/business capability enforcement.

Example:

```text
SUBSCRIPTION_READ_ONLY
```

may indicate that:

* reading remains allowed;
* modification is blocked;
* export remains available where permitted.

The HTTP status should remain consistent with the authorization model.

---

# 22. Deleted Business

A Business in a terminal deletion state must not accept ordinary business operations.

Example:

```text
BUSINESS_DELETED
```

The API must not allow a stale client to recreate or mutate deleted Business state through old identifiers.

---

# 23. Business Rule Violation

Business rule errors indicate that the request is structurally valid and authorized but cannot be performed under current business state.

Examples:

```text
INSUFFICIENT_STOCK
ORDER_ALREADY_PAID
CASH_SESSION_CLOSED
PRODUCT_INACTIVE
RECIPE_NOT_APPROVED
SET_COMPONENT_UNAVAILABLE
REFUND_LIMIT_EXCEEDED
```

These should use stable business-specific error codes.

---

# 24. Business Rule HTTP Status

Business rule violations may use:

```text
422 Unprocessable Entity
```

when the request is syntactically valid but cannot be performed.

The exact status must follow the API-wide mapping policy.

---

# 25. Conflict Errors

Conflict errors indicate that the requested state cannot safely be applied because current server state differs from the client's expected state.

Examples:

```text
STALE_VERSION
CONFIGURATION_CONFLICT
RESOURCE_STATE_CONFLICT
SYNC_CONFLICT
```

Typical status:

```text
409 Conflict
```

---

# 26. Stale Version

Example:

```text
Client:
version = 12

Server:
version = 13
```

Response:

```text
409
STALE_VERSION
```

The server must not silently overwrite version 13.

---

# 27. Conflict Recovery

Conflict responses should provide safe recovery information where appropriate.

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

The API must not expose unauthorized or sensitive competing state.

---

# 28. Idempotency Errors

Idempotency-related conditions include:

```text
DUPLICATE_OPERATION
IDEMPOTENCY_KEY_REUSE_CONFLICT
OPERATION_ALREADY_PROCESSED
```

A repeated valid operation should normally return the original authoritative result rather than an error.

A conflicting reuse of an idempotency key must return:

```text
409 Conflict
IDEMPOTENCY_KEY_REUSE_CONFLICT
```

---

# 29. Duplicate Financial Operations

Duplicate prevention is especially important for:

* payments;
* refunds;
* cash corrections;
* inventory adjustments;
* synchronization;
* configuration changes.

The API must not allow retries to create duplicate financial effects.

---

# 30. Synchronization Errors

Synchronization uses dedicated error semantics.

Examples:

```text
SYNC_CONFLICT
INVALID_SYNC_OPERATION
UNAUTHORIZED_SYNC_OPERATION
TEMPORARY_SYNC_FAILURE
ALREADY_PROCESSED
```

Synchronization errors must distinguish:

* permanent rejection;
* conflict;
* retryable temporary failure;
* already processed operation.

---

# 31. Temporary Synchronization Failure

Example:

```text
503 Service Unavailable
TEMPORARY_SYNC_FAILURE
```

The client may retry with bounded backoff.

The client must not treat this as a permanent business rejection.

---

# 32. Rate Limit Error

Rate limiting returns:

```text
429 Too Many Requests
RATE_LIMITED
```

The response may include:

```http
Retry-After: 10
```

The client should respect the retry interval.

Rate limiting must not be used to bypass required authorization or validation.

---

# 33. Infrastructure Errors

Infrastructure errors include failures such as:

* database unavailable;
* cache unavailable;
* storage unavailable;
* queue unavailable.

Infrastructure details must not be exposed directly.

For example:

```text
PostgreSQL connection refused
```

should not be returned to the client.

Instead:

```text
503 Service Unavailable
SERVICE_UNAVAILABLE
```

may be returned where appropriate.

---

# 34. Database Failure

A database failure must be mapped according to whether the operation has safely committed.

If no authoritative commit occurred:

```text
503
SERVICE_UNAVAILABLE
```

may be returned.

If the commit outcome is uncertain, the operation must not be blindly retried unless idempotency makes the retry safe.

---

# 35. Transaction Failure

If a core transaction rolls back:

```text
No committed business effect
```

The API returns an appropriate error.

The client must not assume that a failed request partially committed unless the contract explicitly states otherwise.

---

# 36. Commit Outcome Uncertainty

A network failure may occur after the database commits but before the client receives the response.

Example:

```text
Client
 ↓
Payment request
 ↓
DB COMMIT
 ↓
Network failure
 ↓
Client receives no response
```

The client must use the same idempotency key to safely retry.

The server must return the original authoritative result.

---

# 37. External Dependency Errors

External services may fail independently.

Examples:

* email provider;
* printer service;
* external payment integration;
* storage provider.

External failure must be classified according to whether it affects the core business transaction.

---

# 38. Secondary Failure After Commit

Example:

```text
Order Transaction
    ↓
COMMIT
    ↓
Printer Failure
```

The API must not report the Order transaction as rolled back.

The Order remains authoritative.

Printing should be retried asynchronously where appropriate.

---

# 39. Notification Failure

Notification failure must not rollback the core transaction.

Example:

```text
Cash Session Close
      ↓
DB COMMIT
      ↓
Owner Notification Failure
```

The Cash Session remains closed.

The notification should be retried or marked failed separately.

---

# 40. File/Export Failure

For asynchronous exports:

```text
Export Job
   ↓
FAILED
```

The underlying Business data must remain unchanged.

The API should expose the job failure without exposing internal storage/provider details.

---

# 41. Timeout Errors

Timeouts must be bounded.

Possible public responses:

```text
504 Gateway Timeout
UPSTREAM_TIMEOUT
```

or:

```text
503 Service Unavailable
SERVICE_UNAVAILABLE
```

depending on where the timeout occurred.

The exact mapping must remain consistent.

---

# 42. Retryability Classification

Every important public error should have defined retry semantics.

Categories:

```text
DO_NOT_RETRY
RETRY_SAME_REQUEST
RETRY_WITH_BACKOFF
REFRESH_AND_RETRY
USER_ACTION_REQUIRED
```

This classification may be represented in documentation rather than exposed as a response field.

---

# 43. Do Not Retry

Examples:

```text
INVALID_UUID
VALIDATION_ERROR
ACCESS_DENIED
INSUFFICIENT_STOCK
PRODUCT_INACTIVE
ORDER_ALREADY_PAID
REFUND_LIMIT_EXCEEDED
```

Automatic retry is normally inappropriate.

---

# 44. Retry With Backoff

Examples:

```text
SERVICE_UNAVAILABLE
TEMPORARY_SYNC_FAILURE
UPSTREAM_TIMEOUT
RATE_LIMITED
```

The client should use bounded exponential backoff where appropriate.

---

# 45. Refresh and Retry

Examples:

```text
STALE_VERSION
CONFIGURATION_CONFLICT
```

The client should:

1. fetch current state;
2. show/resolve the conflict;
3. create a new valid operation;
4. retry with a new operation identity where required.

---

# 46. User Action Required

Some errors require user intervention.

Examples:

```text
PERMISSION_REQUIRED
INSUFFICIENT_STOCK
REFUND_APPROVAL_REQUIRED
STALE_VERSION
SUBSCRIPTION_READ_ONLY
```

The client must not automatically repeat the same operation indefinitely.

---

# 47. Error Retry and Idempotency

State-changing retries must use idempotency when the operation supports it.

Example:

```text
POST /orders/{id}/pay
Idempotency-Key: X
```

Retrying with `X` must not create a second payment.

---

# 48. Error Details

`details` should contain only information required for client recovery or user feedback.

Good:

```json
{
  "details": {
    "current_version": 13
  }
}
```

Bad:

```json
{
  "details": {
    "sql_query": "...",
    "database_host": "...",
    "stack_trace": "..."
  }
}
```

---

# 49. Sensitive Error Details

The API must never expose:

* database credentials;
* access tokens;
* refresh tokens;
* private keys;
* internal hostnames where unnecessary;
* SQL statements;
* filesystem paths;
* stack traces;
* secret configuration;
* internal service credentials.

---

# 50. Error Message

The human-readable `message` should:

* explain the condition;
* remain concise;
* avoid sensitive details;
* not be required for machine logic.

Messages may be improved without changing the error code.

---

# 51. Error Localization

API error codes remain language-neutral.

Example:

```text
INSUFFICIENT_STOCK
```

may be rendered by the frontend as:

```text
English
Uzbek
Russian
```

The API should not require clients to parse localized messages.

---

# 52. Field-Level Error Details

Validation errors may identify fields.

Example:

```json
{
  "fields": [
    {
      "field": "markup",
      "code": "OUT_OF_RANGE",
      "message": "Markup must be between 0 and 100."
    }
  ]
}
```

The field path must follow the request schema.

---

# 53. Nested Field Error Paths

Nested paths must be deterministic.

Examples:

```text
items[0].quantity
recipe.components[2].product_id
customer.phone
```

This allows frontend clients to associate errors with controls.

---

# 54. Multiple Errors

Multiple independent validation errors may be returned together.

This reduces unnecessary request/response cycles.

The API should not expose unrelated security-sensitive information merely to provide additional errors.

---

# 55. Error Response Headers

Relevant responses may include:

```text
X-Request-ID
Retry-After
```

Conditional or cache-related headers may also be returned where applicable.

---

# 56. Request ID

Every API error must contain or be traceable through a request ID.

Example:

```json
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "The service is temporarily unavailable.",
    "request_id": "01J..."
  }
}
```

The request ID allows support and operations teams to locate the corresponding server-side event.

---

# 57. Operation UUID

For state-changing operations, the operation UUID should be associated with the error where applicable.

It may be included in safe error details or server-side logs.

The operation UUID must not replace the request ID.

---

# 58. Error Correlation

Important failures should be traceable through:

```text
Request ID
Operation UUID
Correlation ID
Business UUID where safe
Branch UUID where safe
Employee UUID internally
Device UUID internally
```

Logs should preserve enough context to investigate the failure.

---

# 59. Error Logging

Unexpected errors must be logged internally.

Logs should include:

* timestamp;
* request ID;
* operation UUID where applicable;
* endpoint;
* HTTP method;
* status;
* error code;
* exception class;
* latency;
* Business context where appropriate;
* Branch context where appropriate.

Sensitive request values must not be logged.

---

# 60. Expected vs Unexpected Errors

Expected business errors should not be treated as application crashes.

Examples:

```text
INSUFFICIENT_STOCK
ORDER_ALREADY_PAID
STALE_VERSION
```

should be handled as controlled application outcomes.

Unexpected exceptions should be captured by the global error handler and mapped to a generic internal error.

---

# 61. Internal Error

Unexpected failures should normally return:

```text
500 Internal Server Error
INTERNAL_ERROR
```

The response must remain generic.

Example:

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred.",
    "request_id": "01J..."
  }
}
```

The client should not receive the underlying exception.

---

# 62. Internal Error Investigation

The request ID must allow operators to locate:

* exception;
* stack trace;
* transaction context;
* dependency failure;
* operation context;
* relevant logs.

The internal diagnostic record may contain significantly more information than the public response.

---

# 63. Error Aggregation

Error monitoring should group errors by stable:

* error code;
* endpoint;
* service/component;
* exception class internally.

It should avoid grouping only by arbitrary message text.

---

# 64. Error Metrics

Important metrics include:

```text
api_error_count
validation_error_count
authentication_failure_count
authorization_failure_count
conflict_count
idempotency_conflict_count
sync_error_count
rate_limit_count
internal_error_count
service_unavailable_count
timeout_count
```

Metrics must remain low-cardinality.

---

# 65. Error Rate Monitoring

Error rate should be monitored separately for:

* ordinary API requests;
* core POS commands;
* financial commands;
* synchronization;
* asynchronous jobs.

A large reporting failure must not hide a POS reliability problem.

---

# 66. POS Error Handling

POS errors should be:

* fast;
* clear;
* actionable;
* non-destructive;
* safe to retry where applicable.

Example:

```text
INSUFFICIENT_STOCK
```

should allow the cashier to understand that the item cannot currently be accepted.

The client must not display internal database or infrastructure errors to the cashier.

---

# 67. Financial Error Handling

Financial operations require stronger error semantics.

Examples:

```text
PAYMENT_ALREADY_PROCESSED
DUPLICATE_OPERATION
ORDER_ALREADY_PAID
REFUND_LIMIT_EXCEEDED
CASH_SESSION_CLOSED
```

A financial error must never leave the client uncertain about whether a duplicate financial effect may have occurred.

Idempotency and authoritative state lookup are required.

---

# 68. Inventory Error Handling

Inventory-related errors may include:

```text
INSUFFICIENT_STOCK
PRODUCT_NOT_AVAILABLE
RECIPE_NOT_APPROVED
INVENTORY_CONFLICT
```

The error must identify the business condition without exposing another Business's stock information.

---

# 69. Configuration Error Handling

Configuration errors may include:

```text
STALE_VERSION
CONFIGURATION_CONFLICT
INVALID_CONFIGURATION
APPROVAL_REQUIRED
```

Configuration changes must not silently overwrite newer versions.

---

# 70. Permission Error Handling

Permission-related errors may include:

```text
ACCESS_DENIED
PERMISSION_REQUIRED
BRANCH_SCOPE_DENIED
BUSINESS_SCOPE_DENIED
```

The API should avoid revealing unnecessary information about permissions the actor does not possess.

---

# 71. Subscription Error Handling

Subscription-related errors may include:

```text
SUBSCRIPTION_READ_ONLY
SUBSCRIPTION_EXPIRED
BUSINESS_DELETION_PENDING
BUSINESS_DELETED
```

The exact public code should reflect the client's required recovery behavior.

---

# 72. Synchronization Error Handling

Synchronization must distinguish:

```text
Accepted
Already Processed
Conflict
Invalid
Unauthorized
Temporary Failure
```

These outcomes may be represented in batch results rather than ordinary HTTP errors when the batch itself was structurally valid.

---

# 73. Batch Error Semantics

A valid batch containing some failed operations may still return:

```text
200 OK
```

with per-operation results if the batch was successfully processed.

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

A malformed or unauthorized batch request may instead fail at the HTTP level.

---

# 74. Error and Partial Commit

If a batch permits independent operations:

```text
Operation A → committed
Operation B → conflict
Operation C → invalid
```

the API must clearly report the result of each operation.

The client must not assume all-or-nothing semantics unless the endpoint explicitly defines a transactional batch.

---

# 75. Error and Transaction Boundary

The API error must reflect the actual transaction outcome.

If a transaction rolled back:

```text
business effect = not committed
```

If a transaction committed:

```text
business effect = authoritative
```

A later notification, printing or cache failure must not change the committed result.

---

# 76. Error and Outbox

If the core transaction commits but an Outbox consumer later fails:

```text
Core transaction
→ COMMITTED

Outbox processing
→ FAILED / RETRYING
```

The original API operation must not be incorrectly reported as rolled back.

Secondary failure is handled asynchronously.

---

# 77. Error and Cache

Cache failure must not normally become a business correctness error.

Example:

```text
Redis unavailable
      ↓
PostgreSQL fallback
```

If the operation can continue safely, it should do so.

If authoritative state cannot be established, the operation must fail closed.

---

# 78. Error and External Integration

External dependency errors must be mapped according to business impact.

Example:

```text
Order accepted
+
Printer unavailable
```

must not become:

```text
Order rejected
```

if printing is secondary.

The API should expose the committed Order state and handle printing separately.

---

# 79. Error and File Storage

If a file upload fails before persistence:

```text
FILE_UPLOAD_FAILED
```

may be returned.

If a report job fails:

```text
REPORT_GENERATION_FAILED
```

may be represented as an asynchronous job failure.

Internal storage provider details remain hidden.

---

# 80. Error and Authentication Context

Authentication errors must not leak whether a specific employee, device or credential exists unless explicitly allowed by security policy.

For example, authentication failures may intentionally use a generic:

```text
AUTHENTICATION_FAILED
```

instead of revealing which credential component was invalid.

---

# 81. Error and Business Isolation

Errors must not reveal another Business's state.

Bad example:

```text
Order exists in Business B but you cannot access it.
```

Preferred where appropriate:

```text
RESOURCE_NOT_FOUND
```

This prevents resource enumeration.

---

# 82. Error and Branch Isolation

The same principle applies to Branch scope.

The API should not reveal:

* another Branch's inventory;
* another Branch's cash balance;
* another Branch's employees;
* another Branch's configuration;

through error details.

---

# 83. Error and Subscription Isolation

A client must not use error details to infer sensitive subscription information about another Business.

Subscription information is disclosed only within the actor's authorized scope.

---

# 84. Error Recovery Contract

Each important error must define a client recovery path.

Example:

```text
VALIDATION_ERROR
→ correct request

STALE_VERSION
→ refresh state

INSUFFICIENT_STOCK
→ modify/remove item

SERVICE_UNAVAILABLE
→ retry later

DUPLICATE_OPERATION
→ retrieve original result
```

The frontend/POS should not guess recovery behavior.

---

# 85. Error Recovery and User Experience

User-facing clients should translate API errors into clear actions.

For example:

```text
STALE_VERSION
→ "Configuration changed. Refresh and try again."

INSUFFICIENT_STOCK
→ "Insufficient stock for this product."

SERVICE_UNAVAILABLE
→ "Service temporarily unavailable. Please try again."
```

The API itself remains language-neutral.

---

# 86. Error Recovery and Offline Clients

Offline clients must distinguish:

```text
temporary failure
```

from:

```text
permanent rejection
```

A temporary synchronization failure may remain queued.

A permanent business rejection must not be retried indefinitely.

---

# 87. Error Recovery and Retry Limits

Clients and workers must use bounded retries.

No error should result in:

```text
infinite retry loop
```

Retries should use:

* maximum attempts;
* backoff;
* jitter where appropriate;
* dead-letter/failure handling for background processing.

---

# 88. Error Recovery and Idempotency

When retrying a state-changing operation:

```text
same operation
→ same operation UUID
```

must be used when the operation is still semantically the same.

A new operation UUID should be used when the user intentionally creates a new operation after resolving a conflict.

---

# 89. Error Compatibility

Error responses are part of backward compatibility.

Compatible changes may include:

* improving human-readable messages;
* adding optional safe details;
* adding new error codes for new conditions.

Breaking changes include:

* removing required error fields;
* changing error code semantics;
* changing retry behavior unexpectedly;
* changing status semantics without compatibility handling.

---

# 90. Deprecated Error Codes

An error code should not be removed immediately when older clients may depend on it.

If deprecation is necessary:

* document replacement;
* define transition period;
* update clients;
* update contract tests;
* remove only through an explicit compatibility decision.

---

# 91. Error Code Registry

The API should maintain a controlled error code registry.

Example structure:

```text
Error Code
Category
HTTP Status
Retryability
Meaning
Client Recovery
Security Exposure
```

Example:

```text
STALE_VERSION
Conflict
409
REFRESH_AND_RETRY
Resource changed
Refresh current state
Safe current version only
```

---

# 92. Initial Error Code Registry

The initial registry should include at least:

### General

```text
VALIDATION_ERROR
RESOURCE_NOT_FOUND
CONFLICT
INTERNAL_ERROR
SERVICE_UNAVAILABLE
UPSTREAM_TIMEOUT
RATE_LIMITED
```

### Authentication

```text
AUTHENTICATION_REQUIRED
AUTHENTICATION_FAILED
TOKEN_EXPIRED
TOKEN_INVALID
SESSION_REVOKED
```

### Authorization

```text
ACCESS_DENIED
PERMISSION_REQUIRED
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
RESOURCE_ACCESS_DENIED
```

### Subscription

```text
SUBSCRIPTION_READ_ONLY
SUBSCRIPTION_EXPIRED
BUSINESS_DELETION_PENDING
BUSINESS_DELETED
```

### Concurrency / Idempotency

```text
STALE_VERSION
CONFIGURATION_CONFLICT
DUPLICATE_OPERATION
IDEMPOTENCY_KEY_REUSE_CONFLICT
```

### Orders / POS

```text
ORDER_ALREADY_PAID
ORDER_NOT_EDITABLE
ORDER_INVALID_STATE
PRODUCT_INACTIVE
PRODUCT_UNAVAILABLE
```

### Inventory

```text
INSUFFICIENT_STOCK
INVENTORY_CONFLICT
RECIPE_NOT_APPROVED
SET_COMPONENT_UNAVAILABLE
```

### Cash / Financial

```text
CASH_SESSION_CLOSED
CASH_SESSION_NOT_ACTIVE
PAYMENT_ALREADY_PROCESSED
REFUND_LIMIT_EXCEEDED
REFUND_APPROVAL_REQUIRED
FINANCIAL_OPERATION_CONFLICT
```

### Synchronization

```text
SYNC_CONFLICT
INVALID_SYNC_OPERATION
UNAUTHORIZED_SYNC_OPERATION
TEMPORARY_SYNC_FAILURE
ALREADY_PROCESSED
```

The registry may grow as new business capabilities are introduced.

---

# 93. Error Code Granularity

Error codes should be specific enough to support correct client behavior but not so specific that they expose internal implementation.

Good:

```text
PAYMENT_ALREADY_PROCESSED
```

Too implementation-specific:

```text
POSTGRES_UNIQUE_CONSTRAINT_PAYMENT_OPERATION_ID
```

Too generic:

```text
ERROR
```

---

# 94. Error Code and Domain Exceptions

Domain exceptions may map to public API errors.

Example:

```text
Domain:
OrderAlreadyPaidError

API:
ORDER_ALREADY_PAID
```

The Domain exception name does not have to equal the public error code.

The mapping should be explicit.

---

# 95. Global Exception Handler

The API should have a centralized exception handling mechanism.

Responsibilities:

* catch known application errors;
* map to stable codes;
* map HTTP status;
* serialize safe details;
* attach request ID;
* log unexpected failures;
* prevent stack traces from reaching clients.

Endpoint-specific handlers should be used only when a genuinely endpoint-specific response is required.

---

# 96. Exception Handling Order

The global handler should distinguish:

```text
Known API/Application Error
        ↓
Known HTTP/Domain Mapping
        ↓
Validation Error
        ↓
Infrastructure Error
        ↓
Unexpected Exception
```

Unexpected exceptions must reach a final safe fallback.

---

# 97. Error Handler Safety

The global error handler itself must be resilient.

If error serialization fails, the API should still return a minimal safe error response where possible.

The handler must not recursively expose its own failure.

---

# 98. Error Handling Performance

Error handling must remain lightweight.

Initial targets:

| Operation                           |  Target |
| ----------------------------------- | ------: |
| Known application error mapping p95 | ≤ 10 ms |
| Validation error serialization p95  | ≤ 20 ms |
| Normal API error response p95       | ≤ 50 ms |

These targets exclude upstream failures outside application control.

---

# 99. Error Handling Observability

The system should monitor:

* error count;
* error rate;
* error category;
* endpoint;
* HTTP status;
* error code;
* latency;
* retry volume.

High-cardinality arbitrary values must not be used as metric labels.

---

# 100. Error Alerts

Operational alerts should focus on meaningful conditions.

Examples:

```text
INTERNAL_ERROR rate increase
SERVICE_UNAVAILABLE increase
database-related failures
authentication failure spike
authorization denial anomaly
synchronization conflict spike
payment failure spike
POS error latency increase
```

A normal `INSUFFICIENT_STOCK` business error should not be treated as a system outage merely because it occurs.

---

# 101. Error Logging Levels

Suggested classification:

```text
INFO / DEBUG
Expected business error where useful

WARNING
Temporary dependency failure
Retryable infrastructure problem
Unexpected conflict spike

ERROR
Unexpected application failure
Failed core infrastructure operation

CRITICAL
System-wide correctness or security failure
```

Exact levels depend on the observability architecture.

---

# 102. Error Log Redaction

Logs must redact:

* passwords;
* tokens;
* refresh tokens;
* secrets;
* private keys;
* sensitive payment credentials;
* full authorization headers;
* sensitive personal information where not required.

Error details must not become an accidental secret-storage mechanism.

---

# 103. Error and Audit

Not every API error requires a business audit event.

Business audit is appropriate when:

* a meaningful state change occurred;
* a correction was attempted and must be tracked;
* a security-sensitive action occurred;
* a privileged operation was denied and policy requires recording it.

Ordinary validation failures do not automatically require immutable business audit records.

---

# 104. Error and Security Events

Security-sensitive failures may generate security telemetry.

Examples:

* repeated authentication failures;
* suspicious Business scope attempts;
* repeated Branch scope violations;
* invalid trusted-device attempts;
* synchronization authorization failures.

Security telemetry is separate from normal business audit.

---

# 105. Error and Rate Limiting

Rate limiting may produce metrics and security events.

The API must distinguish:

```text
normal user mistake
```

from:

```text
abnormal repeated abuse
```

without exposing internal detection logic to clients.

---

# 106. Error and Health Endpoints

Health endpoints should use minimal error responses.

They must not expose:

* database credentials;
* dependency URLs;
* internal hostnames;
* stack traces.

Readiness may return unavailable status when the service cannot safely accept traffic.

---

# 107. Error and Graceful Degradation

When optional infrastructure fails, the API should degrade safely.

Example:

```text
Redis unavailable
→ database fallback

Printer unavailable
→ Order remains committed

Notification provider unavailable
→ notification queued/retried
```

When authoritative state cannot be safely determined, the API must fail closed.

---

# 108. Error and Cache Failure

Cache failures should normally not produce a public cache-specific error.

Bad:

```text
REDIS_CONNECTION_ERROR
```

Preferred:

```text
Continue through authoritative fallback
```

or, if safe execution is impossible:

```text
SERVICE_UNAVAILABLE
```

---

# 109. Error and Database Availability

If PostgreSQL is unavailable, the API cannot perform authoritative transactional operations.

The API should return a controlled temporary-unavailability response rather than pretending that the operation succeeded.

---

# 110. Error and Read Replicas

If read replicas are introduced later, stale-read failures must not be exposed as authoritative business success.

Operations requiring strong consistency must use the authoritative transactional source.

---

# 111. Error and Historical Integrity

An error response must never cause the client to reconstruct historical data from current state.

For example:

```text
Current Product Price
```

must not be used to recover a failed historical Order response.

Historical resources must remain based on authoritative snapshots.

---

# 112. Error and Performance

Error handling must not add unnecessary latency to successful POS operations.

The system should avoid:

* synchronous external error reporting in the request path;
* expensive stack processing for expected business errors;
* excessive logging of normal validation failures;
* large error payloads.

---

# 113. Error Payload Size

Error responses must remain bounded.

An error should not return:

* full request body;
* full database record;
* complete stack trace;
* unlimited validation errors.

Validation errors may be capped to a reasonable number.

---

# 114. Client Error Handling Contract

Clients should implement a common error handler based on:

```text
HTTP Status
+
Error Code
+
Retryability
+
Safe Details
+
Request ID
```

Clients must not depend on endpoint-specific undocumented messages.

---

# 115. POS Client Error Handling

POS should provide a simple operational presentation:

```text
Business condition
+
Action
```

Example:

```text
Insufficient stock
→ Remove item or wait for stock.
```

Infrastructure details remain hidden from the cashier.

---

# 116. Frontend Error Handling

The frontend should map stable API error codes to localized user-facing messages.

Example:

```text
ORDER_ALREADY_PAID
→ Order is already paid.

STALE_VERSION
→ The data changed. Refresh and try again.

SUBSCRIPTION_READ_ONLY
→ This subscription is read-only.
```

The frontend must not duplicate business decision logic merely to predict errors.

---

# 117. API Error Documentation

Every public error code must be documented with:

* code;
* HTTP status;
* meaning;
* retryability;
* client recovery;
* security considerations.

This documentation should be part of the OpenAPI/API contract documentation where appropriate.

---

# 118. Error Contract Testing

Contract tests must verify:

* error code;
* HTTP status;
* required fields;
* field-level details;
* request ID;
* safe serialization;
* retry-related headers where applicable.

Tests must ensure that internal exception details are not exposed.

---

# 119. Error Security Testing

Security tests must verify:

* cross-Business errors do not reveal resource existence;
* cross-Branch errors do not reveal protected state;
* authentication failures do not leak credential details;
* stack traces are not exposed;
* SQL errors are not exposed;
* infrastructure hostnames are not exposed;
* sensitive request values are not logged;
* authorization failures fail closed.

---

# 120. Error Compatibility Testing

Compatibility tests should verify that:

* existing error codes remain stable;
* required error fields remain present;
* status mappings remain stable;
* client recovery semantics remain stable;
* deprecated codes are handled according to migration policy.

---

# 121. Error Handling Guardrails

The implementation must prohibit:

* raw exception responses;
* stack traces in production responses;
* SQL errors exposed to clients;
* secret values in error details;
* unstable error code semantics;
* client behavior based only on messages;
* infinite retries;
* retrying permanent business errors;
* silently retrying financial operations without idempotency;
* authorization failures that fail open;
* cross-Business error disclosure;
* cross-Branch error disclosure;
* unbounded validation error payloads;
* expensive synchronous error reporting in POS transactions.

---

# 122. System Invariants

The following invariants apply to API Error Handling and Error Codes:

1. Every public API error has a stable machine-readable error code.
2. Error codes have unique public meanings.
3. Error code semantics cannot silently change.
4. HTTP status and error code have separate responsibilities.
5. Clients must not rely on human-readable error messages for machine behavior.
6. Internal exceptions are never exposed directly.
7. Production API responses never expose stack traces.
8. SQL errors are never exposed to clients.
9. Infrastructure details are not exposed unnecessarily.
10. Secrets are never included in error responses.
11. Passwords are never included in error responses.
12. Tokens are never included in error responses.
13. Private keys are never included in error responses.
14. Error responses use the common public structure.
15. Request ID is available for every API error.
16. State-changing operations remain traceable through operation identity where applicable.
17. Validation errors are distinguishable from authorization errors.
18. Authorization errors are distinguishable from business rule violations.
19. Business rule violations are distinguishable from infrastructure failures.
20. Conflict errors are distinguishable from validation errors.
21. Retryable failures are distinguishable from permanent failures.
22. Permanent business failures are not retried indefinitely.
23. Financial retries use idempotency where supported.
24. Duplicate financial effects are prohibited.
25. Idempotency key reuse with conflicting payload is a conflict.
26. Stale configuration versions are rejected rather than silently overwritten.
27. Error recovery information does not expose unauthorized state.
28. Error details are minimal and purpose-specific.
29. Field-level validation errors use deterministic paths.
30. Nested validation errors use deterministic paths.
31. Validation error payloads are bounded.
32. HTTP error mappings are consistent across API modules.
33. Authentication failures normally use 401.
34. Authorization failures normally use 403.
35. Resource discovery may use 404 where required for security.
36. Conflict conditions normally use 409.
37. Rate limiting normally uses 429.
38. Unexpected application failures normally use 500.
39. Temporary service failures normally use 503.
40. Upstream timeout mapping is consistent with the API gateway policy.
41. Error messages remain secondary to stable error codes.
42. Error codes remain language-neutral.
43. Error localization is a client responsibility where applicable.
44. Cross-Business error responses cannot reveal protected Business state.
45. Cross-Branch error responses cannot reveal protected Branch state.
46. Authentication failures do not unnecessarily reveal credential existence.
47. Subscription errors respect Business authorization scope.
48. Deleted Businesses cannot be revived through error recovery.
49. Cache failures do not automatically become business failures.
50. Cache failure cannot cause authorization fail-open.
51. Database failures cannot be reported as successful business operations.
52. Commit outcome uncertainty is handled through idempotent recovery where applicable.
53. A committed transaction is not reported as rolled back because of a later secondary failure.
54. Printer failure does not rollback a committed Order.
55. Notification failure does not rollback committed business state.
56. Export failure does not mutate source Business data.
57. Outbox failure does not invalidate a committed core transaction.
58. Batch operations report partial results when partial processing is supported.
59. Clients can distinguish retryable synchronization failure from permanent rejection.
60. Offline clients do not retry permanent business failures indefinitely.
61. Retry attempts are bounded.
62. Error logging does not expose secrets.
63. Error logs contain sufficient correlation context for investigation.
64. Error metrics remain low-cardinality.
65. Expected business errors are not treated as application crashes.
66. Unexpected exceptions are captured by centralized error handling.
67. Global error handling has a safe fallback.
68. Error serialization failure does not expose internal exception data.
69. Error payloads remain bounded.
70. Error handling does not unnecessarily delay successful POS operations.
71. Error handling does not perform expensive synchronous external reporting.
72. API error contracts are documented.
73. API error contracts are covered by automated tests.
74. Security tests verify error information leakage.
75. Compatibility tests verify stable error semantics.
76. Deprecated error codes follow an explicit migration policy.
77. Error codes describe public semantic conditions, not infrastructure implementation.
78. Domain exceptions are explicitly mapped to public API errors.
79. Public error codes do not expose database implementation details.
80. Business and Branch isolation remain enforced during error generation.
81. Error responses expose only authorized recovery information.
82. Error handling never replaces authorization.
83. Error handling never replaces validation.
84. Error handling never replaces transaction correctness.
85. Error handling never replaces idempotency.
86. Error handling preserves historical integrity.
87. Error handling preserves financial precision.
88. Error handling preserves synchronization correctness.
89. Error handling preserves subscription restrictions.
90. Error handling preserves trusted-device restrictions.
91. Error handling remains compatible with offline clients.
92. Error handling remains compatible with POS clients.
93. Error handling remains compatible with frontend clients.
94. Error handling remains compatible with asynchronous jobs.
95. Error handling remains observable.
96. Error handling remains deterministic.
97. Error recovery actions are documented for important public errors.
98. Error codes are centrally controlled.
99. New semantic conditions receive new error codes rather than reusing unrelated codes.
100. The API must fail closed when authoritative security or transactional state cannot be established.

---

# 123. Recommended Error Registry Structure

A controlled registry may be maintained as:

```text
api/
├── errors/
│   ├── registry.py
│   ├── codes.py
│   ├── mappings.py
│   └── policies.py
│
├── schemas/
│   └── errors.py
│
└── middleware/
    └── exception_handler.py
```

Exact implementation names may be refined later.

The registry should define, at minimum:

```text
code
category
http_status
retryability
description
client_recovery
security_exposure
```

---

# 124. Related API Documents

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/04_Architecture/09_API/05_API_Resource_Model_and_Naming.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/08_API_Request_Validation_and_Response_Contracts.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/08_Error_Handling_and_Exception_Architecture.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/17_Backend_Testing_and_Quality_Assurance_Architecture.md`

### Database Architecture

* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Frontend Architecture

* `docs/04_Architecture/07_Frontend/26_Frontend_Error_Handling_and_Recovery_Architecture.md`
* `docs/04_Architecture/07_Frontend/29_Frontend_Testing_and_Quality_Assurance_Architecture.md`

---

# 125. Status

**API Architecture Section:** In Progress

**Document Status:** Proposed

**Current Document:** `09_API_Error_Handling_and_Error_Codes.md`

**Previous Document:** `08_API_Request_Validation_and_Response_Contracts.md`

**Next Document:** `10_API_Idempotency_and_Concurrency.md`

---

## Final Principle

> API errors must be predictable for clients, safe for users, traceable for operators, and precise enough to preserve correctness without exposing internal implementation details.

