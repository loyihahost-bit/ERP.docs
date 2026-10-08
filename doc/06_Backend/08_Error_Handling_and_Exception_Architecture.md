# Error Handling and Exception Architecture

**Document ID:** BE-08
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/06_Backend/README.md`

---

## 1. Purpose

This document defines the backend error-handling and exception architecture for FastFood ERP.

The system must provide:

* predictable error behavior;
* safe API responses;
* consistent error classification;
* clear separation between business errors and technical failures;
* reliable transaction rollback;
* safe retry behavior;
* useful logging;
* actionable error information for clients;
* protection against information leakage.

Error handling must not hide important failures or expose internal implementation details.

---

## 2. Core Principle

The backend follows:

> Expected business failures are handled as application results, while unexpected technical failures are treated as system errors.

The API must provide stable, machine-readable error responses.

Internal exceptions must not be exposed directly to clients.

---

## 3. Error Handling Layers

Error handling is distributed across the backend layers:

```text id="err001"
API Layer
    ↓
Application Layer
    ↓
Domain Layer
    ↓
Repository / Infrastructure
    ↓
Database / External Systems
```

Each layer has a defined responsibility.

---

## 4. API Layer Responsibility

The API layer is responsible for:

* converting application errors into HTTP responses;
* validating request structure;
* returning stable error codes;
* attaching request/operation identifiers;
* preventing internal exception leakage.

The API layer must not contain business-rule implementation.

---

## 5. Application Layer Responsibility

The Application Layer is responsible for:

* coordinating use cases;
* validating authorization context;
* invoking domain logic;
* translating lower-level failures;
* determining whether an operation is retryable;
* controlling transaction rollback behavior.

---

## 6. Domain Layer Responsibility

The Domain Layer should raise domain-specific errors when business invariants are violated.

Examples:

* invalid Order transition;
* insufficient stock;
* invalid Recipe state;
* invalid Set configuration;
* invalid Cash Session state.

Domain errors must not depend on HTTP concepts.

---

## 7. Repository Layer Responsibility

Repositories may encounter:

* missing records;
* uniqueness violations;
* foreign-key violations;
* optimistic concurrency conflicts;
* database errors.

Repositories should translate infrastructure-specific failures into application-understandable exceptions where appropriate.

Raw SQLAlchemy/PostgreSQL exceptions must not leak into API responses.

---

# 8. Error Classification

FastFood ERP uses the following primary error categories:

```text id="err002"
Validation Error
Authentication Error
Authorization Error
Not Found
Business Rule Violation
Conflict
Concurrency Failure
Idempotency Conflict
Subscription / Entitlement Error
Lifecycle Error
Infrastructure Error
External Dependency Error
Rate Limit
Internal Error
```

---

# 9. Validation Error

A Validation Error means that the submitted input does not satisfy the expected input format or basic constraints.

Examples:

* invalid UUID;
* missing required field;
* invalid date;
* negative quantity;
* invalid percentage;
* malformed request.

Validation errors should normally be rejected before business processing.

---

## 10. Business Validation vs Request Validation

The system distinguishes:

### Request Validation

Checks the structure and type of input.

Example:

```text
quantity = "abc"
```

### Business Validation

Checks whether the operation is allowed by business rules.

Example:

```text
quantity = 10
stock = 5
```

The first is a request validation error.

The second is a business rule violation.

---

# 11. Authentication Error

Authentication Error means the backend cannot establish a valid identity.

Examples:

* invalid credentials;
* expired authentication token;
* revoked session;
* invalid device authentication;
* invalid offline authorization.

Authentication failures must not reveal sensitive details such as whether a specific password or account exists when such disclosure is unnecessary.

---

# 12. Authorization Error

Authorization Error means the user is authenticated but is not allowed to perform the requested operation.

Examples:

* missing permission;
* wrong Branch scope;
* inactive employee;
* unauthorized Manager delegation;
* restricted Recipe access.

Authorization must fail closed.

---

# 13. Not Found

Not Found is returned when a resource cannot be resolved within the caller's authorized context.

For security-sensitive resources, the system may intentionally return Not Found instead of revealing that the resource exists outside the user's scope.

Example:

```text
Employee belongs to another Business
        ↓
Do not expose employee existence
        ↓
Not Found
```

---

# 14. Business Rule Violation

A Business Rule Violation means the request is structurally valid and authorized, but the requested operation violates a domain rule.

Examples:

* accepting an Order with insufficient stock;
* selling an inactive Product;
* closing an already closed Cash Session;
* exceeding the allowed markup range;
* modifying a paid Order through a prohibited workflow.

---

# 15. Conflict

A Conflict means the requested operation cannot be applied because the current state conflicts with the request.

Examples:

* stale configuration version;
* already-open Cash Session;
* duplicate unique business state;
* conflicting synchronization operation.

---

# 16. Concurrency Failure

Concurrency Failure occurs when simultaneous operations cannot safely modify the same state.

Examples:

```text
Two employees update the same configuration
```

or:

```text
Two requests attempt to open the same Cash Register
```

The system must preserve one authoritative state.

---

# 17. Idempotency Conflict

An Idempotency Conflict occurs when an operation UUID has already been used with incompatible request data.

Example:

```text
operation_id = X

First request:
amount = 100000

Retry:
amount = 200000
```

The second request must not execute as a new operation.

It must be rejected as an idempotency conflict.

---

# 18. Subscription / Entitlement Error

A modifying operation may fail because the Business does not have the required subscription entitlement.

Examples:

* feature not included in tariff;
* branch limit exceeded;
* employee limit exceeded;
* expired subscription;
* read-only Business state.

The response should clearly identify that the operation is not currently permitted without exposing internal entitlement implementation.

---

# 19. Lifecycle Error

Lifecycle errors occur when an operation is incompatible with the lifecycle state of a resource or Business.

Examples:

```text
Business = DELETED
        ↓
Modification rejected
```

```text
Cash Session = CLOSED
        ↓
Close operation rejected
```

```text
Product = ARCHIVED
        ↓
New sale rejected
```

---

# 20. Infrastructure Error

Infrastructure Error represents technical failures such as:

* database unavailable;
* connection pool exhaustion;
* database timeout;
* unexpected storage failure;
* internal service failure.

These errors must be logged with sufficient technical context but must not expose internal details to clients.

---

# 21. External Dependency Error

External Dependency Error represents failure of an external system.

Examples:

* external notification provider;
* email provider;
* file storage;
* future payment provider;
* future government integration.

External dependency failure must be separated from core business state where possible.

---

# 22. Rate Limit Error

Rate limiting protects:

* authentication endpoints;
* password operations;
* sensitive APIs;
* synchronization endpoints;
* expensive endpoints.

Rate-limit responses must not expose internal security thresholds unnecessarily.

---

# 23. Internal Error

Internal Error represents an unexpected condition that was not safely classified.

Examples:

* programming defect;
* unexpected null state;
* unhandled infrastructure exception;
* invariant failure caused by implementation error.

Internal errors must be logged with a correlation identifier.

The client receives a generic safe response.

---

# 24. Stable Error Code

Every API error should have a stable machine-readable code.

Example:

```json
{
  "error": {
    "code": "INVENTORY_INSUFFICIENT",
    "message": "The requested product cannot be accepted because required inventory is insufficient.",
    "request_id": "..."
  }
}
```

The exact response schema may evolve, but the error code must remain stable once exposed as a public API contract.

---

# 25. Error Response Structure

The recommended API structure is:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message.",
    "details": {},
    "request_id": "request-uuid",
    "operation_id": "operation-uuid"
  }
}
```

Not every response must contain every field.

Sensitive internal details must never be exposed.

---

# 26. Error Code Requirements

Error codes should be:

* stable;
* unique;
* machine-readable;
* documented;
* domain-oriented;
* independent of database implementation.

Avoid codes such as:

```text
SQL_ERROR_23505
```

as the public business error code.

The PostgreSQL error may be recorded internally, but the API should expose a meaningful application code.

---

# 27. Error Message Requirements

Client-facing messages should be:

* concise;
* understandable;
* actionable where possible;
* safe;
* free from internal implementation details.

Avoid:

```text
psycopg2.errors.UniqueViolation at repository.py:271
```

Prefer:

```text
A Branch with this code already exists.
```

---

# 28. Error Details

The `details` field may contain structured information when useful.

Example:

```json
{
  "error": {
    "code": "CONFIGURATION_CONFLICT",
    "message": "The configuration was changed by another user.",
    "details": {
      "expected_version": 10,
      "current_version": 11
    }
  }
}
```

Only information safe for the caller should be included.

---

# 29. Field Validation Errors

For request validation, field-specific errors may be returned.

Example:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid fields.",
    "details": {
      "price": "Price must be greater than or equal to zero.",
      "markup": "Markup must be between 0 and 100."
    }
  }
}
```

---

# 30. HTTP Status Mapping

The backend should use conventional HTTP status semantics.

Recommended mapping:

| Error Category             | HTTP Status |
| -------------------------- | ----------: |
| Validation Error           |         400 |
| Authentication Error       |         401 |
| Authorization Error        |         403 |
| Not Found                  |         404 |
| Conflict                   |         409 |
| Idempotency Conflict       |         409 |
| Concurrency Failure        |         409 |
| Subscription / Entitlement |  403 or 409 |
| Lifecycle Error            |         409 |
| Rate Limit                 |         429 |
| Infrastructure Error       |   500 / 503 |
| External Dependency Error  |   502 / 503 |
| Internal Error             |         500 |

The exact mapping must remain consistent across the API.

---

# 31. Do Not Overuse HTTP Status Codes

The system should not create dozens of HTTP status codes for minor business differences.

Business meaning should primarily be represented by stable application error codes.

---

# 32. Central Exception Mapping

Exception-to-response mapping should be centralized.

Conceptually:

```text id="err003"
Exception
    ↓
Exception Handler
    ↓
Error Classification
    ↓
Application Error Code
    ↓
HTTP Response
```

Individual API routes should not independently implement exception mapping.

---

# 33. Exception Hierarchy

The backend should use a controlled exception hierarchy.

Conceptually:

```text
ApplicationError
├── ValidationError
├── AuthenticationError
├── AuthorizationError
├── NotFoundError
├── BusinessRuleError
├── ConflictError
│   ├── ConcurrencyError
│   └── IdempotencyConflictError
├── EntitlementError
├── LifecycleError
├── InfrastructureError
├── ExternalDependencyError
└── InternalError
```

The exact Python implementation may differ, but the conceptual hierarchy must remain clear.

---

# 34. Domain Exceptions

Domain exceptions should describe domain violations.

Examples:

```text
InsufficientStockError
InvalidOrderStateError
InvalidCashSessionStateError
InvalidRecipeStateError
InvalidSetConfigurationError
```

They should not contain HTTP status codes.

---

# 35. Application Exceptions

Application exceptions represent use-case-level failures.

Examples:

```text
PermissionDeniedError
BusinessNotWritableError
SubscriptionEntitlementError
ConfigurationConflictError
DuplicateOperationError
```

---

# 36. Infrastructure Exceptions

Infrastructure exceptions may wrap lower-level technical failures.

Examples:

```text
DatabaseUnavailableError
DatabaseTimeoutError
StorageUnavailableError
MessageBrokerUnavailableError
```

The original exception may be retained internally for logging and debugging.

---

# 37. Exception Chaining

When translating exceptions, the original cause should remain available internally.

Conceptually:

```python
raise DatabaseUnavailableError(...) from exc
```

This preserves debugging context without exposing the original exception to the API client.

---

# 38. Database Exception Translation

The infrastructure layer should translate known database failures.

Examples:

```text
Unique violation
      ↓
Duplicate / Conflict

Foreign-key violation
      ↓
Invalid Reference / Business Error

Serialization failure
      ↓
Concurrency Retry

Deadlock
      ↓
Retryable Concurrency Failure
```

Unknown database failures become infrastructure/internal errors.

---

# 39. Unique Constraint Errors

A unique constraint violation should be mapped according to the affected business invariant.

Example:

```text
UNIQUE(branch_id, product_id)
        ↓
BRANCH_PRODUCT_ALREADY_EXISTS
```

The public error must not depend on PostgreSQL constraint names.

---

# 40. Foreign Key Errors

Foreign-key failures should normally indicate an invalid reference or unexpected integrity problem.

The application should prevent predictable foreign-key failures through business validation where practical.

Unexpected foreign-key failures must be logged as integrity/infrastructure problems.

---

# 41. Transaction Rollback on Exceptions

When a core transaction encounters an exception:

```text id="err004"
Exception
   ↓
Rollback
   ↓
Classify
   ↓
Log
   ↓
Return Safe Error
```

No partially committed core state should remain.

---

# 42. Expected vs Unexpected Exceptions

The system distinguishes:

### Expected

Examples:

* insufficient stock;
* missing permission;
* stale configuration;
* invalid Order state.

These should be handled without treating them as programming defects.

### Unexpected

Examples:

* broken invariant;
* unhandled null;
* unexpected database state;
* programming error.

These require logging and investigation.

---

# 43. Unexpected Exception Handling

Unexpected exceptions must:

1. Roll back the transaction.
2. Generate a safe internal error response.
3. Log the exception.
4. Include request/operation context.
5. Include stack trace internally.
6. Avoid exposing stack trace to the client.
7. Generate monitoring/alerting where appropriate.

---

# 44. Error Correlation

Every request should have a `request_id`.

Every retryable business operation should have an `operation_id`.

Where applicable, logs should also include:

* Business ID;
* Branch ID;
* Employee ID;
* Device ID;
* Cash Session ID;
* entity ID;
* transaction type.

This allows one failure to be traced across backend components.

---

# 45. Request ID vs Operation ID

These identifiers have different purposes.

### Request ID

Identifies one API request.

### Operation ID

Identifies one logical business operation across retries.

Example:

```text
Request A
request_id = R1
operation_id = O1

Network timeout

Request B
request_id = R2
operation_id = O1
```

The two requests represent the same business operation.

---

# 46. Error Logging

Logs should contain enough context to investigate the failure.

Recommended fields:

```text
timestamp
request_id
operation_id
Business ID
Branch ID
employee ID
device ID
error code
exception type
transaction type
endpoint
duration
retry count
source
```

---

# 47. Sensitive Data Protection

Logs must not contain:

* passwords;
* password hashes;
* authentication tokens;
* refresh tokens;
* private keys;
* full payment secrets;
* unnecessary personal information;
* raw authorization credentials.

Sensitive identifiers should be minimized or masked where appropriate.

---

# 48. Error Logging Levels

Recommended levels:

### DEBUG

Detailed development diagnostics.

### INFO

Normal significant application events.

### WARNING

Unexpected but recoverable conditions.

### ERROR

Failed operations requiring investigation.

### CRITICAL

System-level failures requiring immediate attention.

---

# 49. Business Errors Should Not Be Logged as Critical

Expected business failures should not generate critical alerts.

Example:

```text
Insufficient Stock
```

is a normal business outcome, not a system outage.

---

# 50. Authentication Failure Logging

Authentication failures may be logged for security monitoring.

The log must not reveal:

* submitted password;
* authentication token;
* private credential material.

Repeated failures may trigger rate limiting or security alerts.

---

# 51. Authorization Failure Logging

Important authorization failures may be logged with:

* employee;
* Business;
* Branch;
* attempted action;
* resource;
* result.

Sensitive authorization data should not be exposed.

---

# 52. Error Handling in Offline Synchronization

Synchronization requires additional error categories.

Examples:

```text
SYNC_AUTHENTICATION_FAILED
SYNC_DEVICE_REVOKED
SYNC_BUSINESS_READ_ONLY
SYNC_BUSINESS_DELETED
SYNC_CONFLICT
SYNC_DUPLICATE_OPERATION
SYNC_INVALID_DEPENDENCY
SYNC_STALE_CONFIGURATION
SYNC_VALIDATION_FAILED
SYNC_RETRYABLE_FAILURE
```

The client must be able to distinguish retryable from permanent failures.

---

# 53. Retry Classification

Every synchronization failure should be classified as:

```text
Retryable
Permanent
Conflict
Requires Reconciliation
```

Example:

```text
Database timeout
→ Retryable

Invalid permission
→ Permanent

Stale configuration
→ Conflict

Business deletion state
→ Requires lifecycle handling
```

---

# 54. Retryable Errors

Retryable errors may include:

* temporary database unavailability;
* temporary infrastructure failure;
* deadlock;
* serialization conflict;
* temporary external dependency failure.

Retries must be bounded and use backoff.

---

# 55. Non-Retryable Errors

Do not automatically retry:

* invalid credentials;
* missing permission;
* invalid product;
* insufficient stock;
* invalid Order state;
* invalid markup;
* deleted Business;
* invalid request.

Repeated retries only create unnecessary load.

---

# 56. Conflict Errors

Conflict errors require the client or synchronization layer to obtain current state and decide how to proceed.

Examples:

```text
CONFIGURATION_CONFLICT
CASH_SESSION_CONFLICT
SYNC_CONFLICT
IDEMPOTENCY_CONFLICT
```

The system must not silently apply last-write-wins to important business state.

---

# 57. Error Handling and Concurrency

Concurrency errors must be safe and explicit.

Example:

```text id="err005"
Employee A reads Version 10
Employee B reads Version 10

Employee A → Version 11 → success
Employee B → Version 11 → conflict
```

Employee B receives a conflict and must refresh.

---

# 58. Error Handling and Idempotency

A timeout does not prove that an operation failed.

Example:

```text id="err006"
Client
  ↓
Server executes
  ↓
COMMIT
  ↓
Network failure
  ↓
Client sees timeout
```

The client retries with the same operation UUID.

The server returns the existing operation result rather than creating a duplicate.

---

# 59. Error Handling and Transactions

The error architecture must cooperate with transaction management.

Typical flow:

```text id="err007"
Request
  ↓
Begin Transaction
  ↓
Execute Use Case
  ↓
Exception?
  ├── No → Commit
  └── Yes
        ↓
      Rollback
        ↓
      Classify
        ↓
      Respond
```

---

# 60. Error Handling and Audit

Important failed operations may require audit/security records depending on their type.

Examples:

* failed privileged configuration attempt;
* unauthorized permission change;
* device revocation attempt;
* sensitive authentication failure.

However, normal validation failures do not necessarily require business audit records.

---

# 61. Error Handling and Outbox

An Outbox event must be created only when its corresponding business state is committed.

If the core transaction rolls back:

```text
Business State → Rollback
Outbox Event   → Rollback
```

No worker should process an event for a transaction that never committed.

---

# 62. Error Handling and Background Jobs

Background jobs must classify failures.

A job should track states such as:

```text
Pending
Running
Succeeded
Retrying
Failed
Dead Letter
```

The exact state model may vary by job type.

---

# 63. Background Job Retry

Retries should use:

* bounded attempts;
* exponential or controlled backoff;
* idempotent operation design;
* error classification;
* dead-letter handling for permanent failures.

A permanently failing job must not retry forever.

---

# 64. Dead-Letter Handling

A job that cannot be processed after the allowed retry policy may enter a dead-letter state.

The system should preserve:

* job ID;
* operation ID;
* failure reason;
* retry count;
* last error;
* timestamp;
* relevant Business/Branch context.

Manual or administrative recovery may then be performed.

---

# 65. Error Handling and Reports

Report failures should not corrupt report history.

If report generation fails:

```text
Report Request
   ↓
Generation Failure
   ↓
Report Version remains valid only if successfully created
```

The system must not mark an incomplete report as successfully generated.

---

# 66. Error Handling and File Export

If XLSX generation fails:

* the underlying business/report state remains unchanged;
* the export job may retry;
* temporary files should be cleaned up;
* the final export must not be presented as successful.

---

# 67. Error Handling and Notifications

Notification delivery failure should normally not affect the underlying business operation.

Example:

```text
Salary Due Event
   ↓
Core state committed
   ↓
Notification delivery fails
   ↓
Notification retry
```

---

# 68. Error Handling and Printing

Printing failures should be isolated from the business transaction.

Example:

```text
Order Accepted
   ↓
COMMIT
   ↓
Print Job
   ↓
Printer unavailable
```

The Order remains accepted.

The print job may be retried or marked failed.

---

# 69. User-Facing Error Messages

POS errors should be concise and actionable.

Example:

```text
Insufficient stock for this product.
```

Not:

```text
InventoryTransactionRepository.update() failed due to SQLAlchemy IntegrityError.
```

---

# 70. POS Error Priority

For POS operations, errors should prioritize:

1. What happened?
2. Why can the operation not continue?
3. What can the user do next?

Example:

```text
Product cannot be added.

Reason:
Required ingredient is out of stock.

Action:
Remove the item or wait for stock replenishment.
```

---

# 71. Error Message Localization

The backend error code must remain language-independent.

Human-readable messages may later be localized.

Recommended architecture:

```text
Error Code
    ↓
Client Localization
    ↓
Localized Message
```

The backend may provide a default message, but clients should not depend on message text for logic.

---

# 72. Client Must Use Error Codes

Frontend logic must use:

```text
error.code
```

rather than:

```text
error.message
```

Example:

```text
if code == INVENTORY_INSUFFICIENT:
    show stock message
```

Messages may change without breaking application logic.

---

# 73. API Error Documentation

Public API documentation should define:

* endpoint;
* possible error codes;
* HTTP status;
* retryability;
* required client action.

Example:

| Code                     | Status | Retry         |
| ------------------------ | -----: | ------------- |
| `VALIDATION_ERROR`       |    400 | No            |
| `AUTHENTICATION_FAILED`  |    401 | No            |
| `PERMISSION_DENIED`      |    403 | No            |
| `RESOURCE_NOT_FOUND`     |    404 | No            |
| `CONFIGURATION_CONFLICT` |    409 | After refresh |
| `IDEMPOTENCY_CONFLICT`   |    409 | No            |
| `RATE_LIMITED`           |    429 | Later         |
| `SERVICE_UNAVAILABLE`    |    503 | Yes           |

---

# 74. Error Security

Error handling must not become an information disclosure mechanism.

Do not expose:

* database schema;
* SQL queries;
* file paths;
* stack traces;
* internal service names;
* infrastructure topology;
* secret configuration;
* private credentials.

---

# 75. Security-Sensitive Error Responses

Authentication endpoints may intentionally return generic errors.

Example:

```text
Invalid credentials.
```

instead of:

```text
Employee exists but password is wrong.
```

This reduces account enumeration risk.

---

# 76. Development vs Production

Development environments may provide richer debugging information.

Production responses must remain safe.

Development stack traces must never accidentally be enabled in production.

---

# 77. Global Exception Handler

The API should have a global exception handler for unexpected failures.

Conceptually:

```text id="err008"
Unexpected Exception
        ↓
Rollback
        ↓
Log Full Context
        ↓
Generate Error ID
        ↓
Return Generic 500
```

The client should receive enough information to report the issue without receiving internal implementation details.

---

# 78. Error ID

For unexpected errors, the system may provide an error identifier separate from the request ID.

Example:

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred.",
    "request_id": "req-123",
    "error_id": "err-456"
  }
}
```

Support and operations can use this identifier to locate the internal failure.

---

# 79. Error Recovery

Recovery strategy depends on the error category.

| Category             | Recovery                              |
| -------------------- | ------------------------------------- |
| Validation           | Correct request                       |
| Authentication       | Re-authenticate                       |
| Authorization        | Obtain permission / correct scope     |
| Business Rule        | Change operation                      |
| Conflict             | Refresh / reconcile                   |
| Concurrency          | Retry with current state              |
| Idempotency Conflict | Stop and investigate request mismatch |
| Infrastructure       | Retry if transient                    |
| External Dependency  | Retry / fallback                      |
| Internal             | Investigate                           |

---

# 80. Error Handling Invariants

1. API errors use stable machine-readable codes.
2. Internal exceptions are never directly exposed to clients.
3. Domain exceptions do not depend on HTTP.
4. API routes do not implement independent exception mapping.
5. Validation errors are distinguished from business rule violations.
6. Authentication errors are distinguished from authorization errors.
7. Conflicts are explicit.
8. Important concurrency conflicts are not silently resolved.
9. Retryable operations use idempotency.
10. Failed core transactions are rolled back.
11. Unexpected exceptions trigger rollback.
12. Required audit persistence participates in the core transaction.
13. Required Outbox persistence participates in the core transaction.
14. Notification failure does not normally roll back business state.
15. Printer failure does not roll back Order acceptance.
16. Report generation failure does not corrupt operational state.
17. File export failure does not corrupt report state.
18. Database implementation details are hidden from API clients.
19. Stack traces are never exposed in production.
20. Passwords and tokens are never logged.
21. Request IDs are available for tracing.
22. Operation IDs remain stable across retries.
23. Sync failures are classified as retryable, permanent, conflict, or reconciliation-required.
24. Background retries are bounded.
25. Permanent failures do not retry forever.
26. Client logic depends on error codes rather than message text.
27. Error messages are concise and actionable.
28. Security-sensitive endpoints minimize information disclosure.
29. Business errors do not generate unnecessary critical alerts.
30. Error handling preserves historical and transactional integrity.

---

# 81. Recommended Backend Structure

The error architecture should be represented in the backend approximately as:

```text id="err009"
app/
├── api/
│   └── errors/
│       ├── handlers.py
│       ├── responses.py
│       └── mapping.py
│
├── application/
│   └── errors/
│       ├── exceptions.py
│       ├── codes.py
│       └── classification.py
│
├── domain/
│   └── errors/
│       ├── order.py
│       ├── inventory.py
│       ├── cash.py
│       ├── recipe.py
│       └── configuration.py
│
└── infrastructure/
    └── errors/
        ├── database.py
        ├── storage.py
        └── external.py
```

The exact file structure may evolve without changing the conceptual boundaries.

---

# 82. Testing Strategy

Error handling must be tested at multiple levels.

### Unit Tests

Test:

* domain exceptions;
* error classification;
* validation;
* retryability;
* error-code mapping.

### Integration Tests

Test:

* database constraint translation;
* transaction rollback;
* concurrency conflicts;
* deadlocks;
* idempotency;
* Outbox behavior.

### API Tests

Test:

* HTTP status;
* response schema;
* error code;
* safe message;
* request ID;
* operation ID.

### Security Tests

Test:

* information disclosure;
* authentication failure behavior;
* authorization failure behavior;
* rate limiting;
* token leakage prevention.

---

# 83. Example End-to-End Failure

Consider Order acceptance with insufficient inventory:

```text id="err010"
POS
 ↓
POST /orders/{id}/accept
 ↓
Authentication
 ↓
Authorization
 ↓
Begin Transaction
 ↓
Load Order
 ↓
Validate Order
 ↓
Lock Inventory
 ↓
Check Stock
 ↓
Insufficient Stock
 ↓
Rollback
 ↓
BusinessRuleError
 ↓
Error Mapper
 ↓
HTTP 409
```

Example response:

```json
{
  "error": {
    "code": "INVENTORY_INSUFFICIENT",
    "message": "The order cannot be accepted because required inventory is insufficient.",
    "request_id": "..."
  }
}
```

No partial inventory deduction occurs.

---

# 84. Example Concurrency Failure

```text id="err011"
Employee A
  ↓
Reads configuration version 10

Employee B
  ↓
Reads configuration version 10

Employee A
  ↓
Creates version 11
  ↓
COMMIT

Employee B
  ↓
Attempts update using version 10
  ↓
CONFLICT
```

The second request receives a stable conflict error.

It must not overwrite version 11.

---

# 85. Example Unknown Failure

```text id="err012"
POS Request
   ↓
Use Case
   ↓
Unexpected Exception
   ↓
Rollback
   ↓
Internal Logging
   ↓
Monitoring Alert
   ↓
Safe API Response
```

Example:

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred.",
    "request_id": "req-123",
    "error_id": "err-456"
  }
}
```

The actual stack trace remains internal.

---

# 86. Architecture Summary

The error architecture follows:

```text id="err013"
Client Request
      ↓
Request Validation
      ↓
Authentication
      ↓
Authorization
      ↓
Application Use Case
      ↓
Domain / Repository
      ↓
Exception?
 ┌────┴─────┐
No         Yes
 ↓           ↓
Commit    Rollback
 ↓           ↓
Success   Classify
             ↓
        Safe Error Code
             ↓
        API Error Response
```

Unexpected technical failures are logged and monitored.

Expected business failures are returned predictably.

---

# 87. Related Documents

### Backend

* `README.md`
* `01_Backend_Architecture.md`
* `02_Backend_Project_Structure.md`
* `03_Application_and_Use_Case_Layer.md`
* `04_Domain_Service_and_Business_Logic.md`
* `05_Repository_and_Data_Access.md`
* `06_Authentication_and_Authorization.md`
* `07_Transaction_Management.md`
* `09_Events_Outbox_and_Background_Jobs.md`
* `23_Backend_Concurrency_and_Idempotency.md`
* `24_Backend_Invariants_and_Guardrails.md`

### Database

* `../05_Database/25_Database_Integrity_and_Constraints.md`
* `../05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `../05_Database/28_Database_Backup_and_Recovery.md`
* `../05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `../02_System_Analysis/07_POS_and_Order_System.md`
* `../02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `../02_System_Analysis/16_Inventory_Transaction_System.md`
* `../02_System_Analysis/22_Audit_and_History.md`
* `../02_System_Analysis/23_Offline_Operation.md`
* `../02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `../02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `../02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`

---

# 88. Status

**Document ID:** BE-08

**Document Status:** Accepted

**Error Model:** Classified Application Errors

**API Error Contract:** Stable Machine-Readable Error Codes

**Transaction Behavior:** Rollback on Core Failure

**Retry Model:** Explicitly Classified and Bounded

**Idempotency:** Required for Retryable Business Commands

**Logging:** Structured and Security-Aware

**Production Stack Traces:** Prohibited

**Next Document:** `09_Events_Outbox_and_Background_Jobs.md`

