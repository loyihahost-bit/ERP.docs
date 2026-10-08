# API Layers and Request Lifecycle

**Document ID:** API-03
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`

---

## 1. Purpose

This document defines the API layer architecture and complete request lifecycle for FastFood ERP.

It establishes:

* API layer responsibilities;
* request entry flow;
* middleware processing;
* request context creation;
* authentication;
* authorization;
* validation;
* application use-case execution;
* domain execution;
* transaction boundaries;
* repository interaction;
* response construction;
* error propagation;
* audit and outbox integration;
* idempotency handling;
* concurrency handling;
* asynchronous processing;
* request termination.

The objective is to ensure that every API request follows a predictable and controlled execution path.

---

# 2. Architectural Position

The API is an entry boundary into the backend application.

The standard request flow is:

```text
Client
  ↓
HTTP Request
  ↓
API Gateway / Reverse Proxy
  ↓
Application API
  ↓
Request Middleware
  ↓
Request Context
  ↓
Authentication
  ↓
Authorization
  ↓
Request Validation
  ↓
Idempotency / Concurrency Checks
  ↓
Application Use Case
  ↓
Domain Logic
  ↓
Repository / Infrastructure
  ↓
PostgreSQL / External Infrastructure
  ↓
Transaction Commit
  ↓
Outbox / Secondary Processing
  ↓
Application Result
  ↓
API Response Mapping
  ↓
HTTP Response
  ↓
Client
```

Not every request requires every stage.

For example, a simple public health endpoint does not require Business authorization.

---

# 3. Layer Model

The API architecture consists of the following logical layers:

```text
1. Edge / Reverse Proxy
2. API Transport Layer
3. Request Middleware
4. Security Context
5. Request Validation
6. Application Layer
7. Domain Layer
8. Data Access / Infrastructure
9. Transaction Boundary
10. Response Mapping
```

These are logical responsibilities.

They do not necessarily require separate physical services or processes.

The initial architecture remains compatible with the modular monolith approach.

---

# 4. Edge / Reverse Proxy Layer

The external HTTP connection may first reach:

* Nginx;
* load balancer;
* reverse proxy;
* deployment gateway.

This layer may handle:

* TLS termination;
* connection management;
* basic request size limits;
* basic rate limiting where appropriate;
* forwarding client information;
* request routing.

The reverse proxy must not implement business authorization.

---

# 5. API Transport Layer

The API transport layer is responsible for translating HTTP into application requests.

Responsibilities include:

* route matching;
* HTTP method handling;
* path parameter extraction;
* query parameter extraction;
* header extraction;
* body parsing;
* schema validation;
* response serialization;
* HTTP status mapping.

The transport layer must remain thin.

---

# 6. API Router

The router maps an HTTP request to an API operation.

Example:

```text
POST /api/v1/orders/{order_id}/accept
```

maps to:

```text
AcceptOrderEndpoint
```

The endpoint then invokes the appropriate Application use case.

The router must not contain business logic.

---

# 7. Endpoint Handler

An endpoint handler coordinates transport concerns.

Typical responsibilities:

```text
Receive request
    ↓
Read validated input
    ↓
Read request context
    ↓
Call Application use case
    ↓
Map result
    ↓
Return HTTP response
```

The handler must not:

* calculate inventory;
* calculate authoritative financial totals;
* modify database entities directly;
* decide permissions independently;
* create audit records manually;
* implement complex business workflows.

---

# 8. Request Middleware

Middleware processes requests before and/or after endpoint execution.

Possible middleware responsibilities include:

* request ID;
* correlation;
* logging;
* authentication integration;
* rate limiting;
* request size enforcement;
* security headers;
* tracing;
* timing;
* exception translation.

Middleware must not become a hidden location for business logic.

---

# 9. Middleware Ordering

Middleware order must be deterministic.

A typical sequence is:

```text
HTTP Request
    ↓
Request Size / Transport Protection
    ↓
Request ID
    ↓
Tracing / Correlation
    ↓
Security Headers
    ↓
Authentication Context
    ↓
Rate Limiting
    ↓
Routing
    ↓
Endpoint
```

Exact framework ordering may differ, but security-sensitive dependencies must remain explicit.

---

# 10. Request ID Creation

Every API request receives a request ID.

If a valid client-provided request ID is accepted, it may be preserved.

Otherwise the server generates one.

Example:

```http
X-Request-ID: 01J...
```

The request ID is propagated to:

* application logs;
* error responses;
* traces;
* relevant background operations.

---

# 11. Operation ID

State-changing operations may additionally have an operation UUID.

Example:

```http
Idempotency-Key: 018f...
```

The operation UUID identifies the business operation.

It is distinct from:

```text
Request ID
Resource UUID
Employee UUID
Device UUID
```

Multiple HTTP retries may therefore reference one operation UUID.

---

# 12. Request Context

After authentication and initial request processing, the backend creates a request context.

A context may contain:

```text
Request ID
Operation UUID
Actor / Employee
Business
Branch
Device
Cash Session
Authentication state
Permission context
Subscription context
Correlation metadata
```

Only applicable fields are populated.

---

# 13. Context Authority

Request context values have different authority levels.

### Server-Derived

Authoritative:

* authenticated Employee;
* authorized Business;
* authorized Branch;
* device trust state;
* permission state;
* subscription state.

### Client-Provided

Untrusted until validated:

* Business ID;
* Branch ID;
* Employee ID;
* Device ID;
* timestamps;
* operation metadata.

Client-provided context must never replace server-derived identity.

---

# 14. Authentication Layer

Authentication establishes the identity of the actor.

The authentication layer may validate:

* access token;
* session;
* device credential;
* trusted-device context;
* synchronization authorization;
* offline authorization signature where applicable.

Authentication answers:

> Who is making this request?

It does not answer:

> What may this actor do?

---

# 15. Authentication Result

A successful authentication should produce a normalized identity context.

Example:

```text
Actor:
Employee UUID

Business:
Business UUID

Authentication:
Authenticated

Device:
Trusted Device UUID

Session:
Session UUID
```

The Application layer should not need to understand raw HTTP authentication mechanisms.

---

# 16. Authentication Failure

Authentication failures terminate the request before protected business execution.

Typical result:

```http
401 Unauthorized
```

Possible error codes:

```text
AUTHENTICATION_REQUIRED
AUTHENTICATION_FAILED
INVALID_TOKEN
SESSION_EXPIRED
INVALID_DEVICE_CREDENTIAL
```

The API must not reveal unnecessary security details.

---

# 17. Authorization Layer

Authorization determines whether the authenticated actor may perform the requested operation.

Authorization evaluates the applicable context.

At minimum:

```text
Employee Status
+
Business Scope
+
Branch Scope
+
Permission
+
Subscription Entitlement
+
Device Restrictions
+
Resource Scope
+
Operational Rules
```

---

# 18. Authorization Order

A typical authorization sequence is:

```text
Authenticated Actor
        ↓
Employee Active?
        ↓
Business Scope Valid?
        ↓
Branch Scope Valid?
        ↓
Permission Present?
        ↓
Subscription Allows Operation?
        ↓
Device Restrictions Satisfied?
        ↓
Resource Scope Valid?
        ↓
Application Execution
```

The exact order may be optimized, but no required authorization dimension may be skipped.

---

# 19. Authorization Failure

Unauthorized requests terminate before protected business state changes.

Typical responses:

```http
403 Forbidden
```

or:

```http
404 Not Found
```

when resource existence should not be disclosed.

Possible error codes:

```text
ACCESS_DENIED
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
PERMISSION_DENIED
SUBSCRIPTION_READ_ONLY
DEVICE_NOT_AUTHORIZED
```

---

# 20. Business Scope Enforcement

Business scope must be established before accessing Business-owned data.

Example:

```text
Authenticated Employee
        ↓
Business A
        ↓
GET /products/{product_id}
        ↓
Product belongs to Business B
        ↓
Access denied
```

A UUID match alone is insufficient.

---

# 21. Branch Scope Enforcement

Branch-scoped resources require Branch authorization.

Example:

```text
Employee:
Branch A only

Request:
GET /branches/B/orders

Result:
BRANCH_SCOPE_DENIED
```

The API must not rely on frontend Branch selection.

---

# 22. Permission Evaluation

Permission checks must use the authoritative permission model.

Relevant sources may include:

```text
Role Permissions
+
Employee Overrides
+
Branch Scope
+
Employee Status
+
Subscription Entitlement
```

Managers cannot grant permissions beyond their own authority.

The API must enforce this rule independently of frontend behavior.

---

# 23. Subscription Enforcement

A Business in read-only subscription state may continue to access permitted read operations.

Modifying operations must be blocked.

Example:

```text
GET /products
→ Allowed

PATCH /products/{id}
→ SUBSCRIPTION_READ_ONLY
```

The API must enforce this rule server-side.

---

# 24. Request Validation Layer

After security context is established, the API validates the request structure.

Validation includes:

* required fields;
* field types;
* UUID formats;
* string lengths;
* numeric ranges;
* enum values;
* date formats;
* nested object structure;
* pagination limits.

Malformed input should not reach the business workflow.

---

# 25. Structural vs Business Validation

Validation is divided into two categories.

### Structural Validation

Performed near the API boundary.

Examples:

```text
quantity must be numeric
UUID must be valid
limit must be within 1–100
status must be a supported enum
```

### Business Validation

Performed by Application/Domain logic.

Examples:

```text
Product cannot be sold because stock is insufficient
Cash Session is already closed
Recipe cannot be approved by this actor
Order cannot be paid because it is already paid
```

The API must not duplicate complex business rules merely for convenience.

---

# 26. Request Normalization

Validated request data may be normalized before entering the Application layer.

Examples:

* trimming allowed strings;
* canonicalizing UUID representation;
* normalizing supported enum values;
* converting validated date/time representations;
* applying default pagination values.

Normalization must not silently change business meaning.

---

# 27. Application Use Case Boundary

After validation, the endpoint invokes an Application use case.

Example:

```text
POST /api/v1/orders/{order_id}/accept
        ↓
AcceptOrderUseCase.execute(...)
```

The Application layer becomes responsible for the business workflow.

---

# 28. Use Case Input

The API should pass a structured application input object rather than raw HTTP objects.

Example:

```text
AcceptOrderCommand
    order_id
    actor_id
    business_id
    branch_id
    device_id
    operation_id
```

The Application layer should not depend on:

* HTTP request objects;
* framework-specific request classes;
* HTTP headers;
* route objects.

---

# 29. Application Authorization Orchestration

The Application layer may perform authorization orchestration in addition to API-level checks.

This is especially important when authorization depends on resource state.

Example:

```text
API:
Employee has inventory.adjust permission

Application:
Is this employee allowed to adjust this specific Branch inventory?
```

Authorization that depends on business state belongs in the Application/Domain boundary.

---

# 30. Application Transaction Boundary

The Application use case determines the transaction boundary.

Example:

```text
Accept Order
    ↓
BEGIN
    ↓
Validate Order
    ↓
Validate Inventory
    ↓
Deduct Inventory
    ↓
Change Order State
    ↓
Create Audit Event
    ↓
Create Outbox Event
    ↓
COMMIT
```

The API handler must not independently commit intermediate business operations.

---

# 31. Domain Execution

The Application layer invokes Domain behavior.

The Domain layer evaluates:

* invariants;
* state transitions;
* calculations;
* business policies;
* business constraints.

Example:

```text
AcceptOrderUseCase
        ↓
Order.accept()
        ↓
InventoryPolicy
        ↓
FinancialPolicy
```

The Domain layer remains independent from HTTP.

---

# 32. Repository Interaction

The Application and Domain layers use repository abstractions to access persisted state.

Example:

```text
Application
    ↓
OrderRepository
InventoryRepository
PaymentRepository
    ↓
Infrastructure
    ↓
PostgreSQL
```

API handlers must never call repositories directly.

---

# 33. Database Interaction

PostgreSQL remains the authoritative transactional source.

Database interaction must preserve:

* Business isolation;
* Branch isolation;
* transaction boundaries;
* concurrency control;
* constraints;
* historical integrity.

The API layer must not make database-specific assumptions that leak into the public contract.

---

# 34. Transaction Commit

A successful core transaction must commit authoritative state before the API reports successful completion.

Example:

```text
Business Transaction
        ↓
DB Commit
        ↓
Authoritative Success
        ↓
API Response
```

The system must not report success before the required authoritative transaction is committed.

---

# 35. Audit Integration

Business-significant state changes should create audit events as part of the appropriate transaction boundary.

Example:

```text
Price Change
    ↓
Validate
    ↓
Change Configuration
    ↓
Create Audit Event
    ↓
Commit
```

The API handler should not manually construct independent audit transactions that could become inconsistent with the business operation.

---

# 36. Outbox Integration

Secondary asynchronous effects should use the Outbox pattern where required.

Example:

```text
Order Accepted
      ↓
Core Transaction
      ├── Order State
      ├── Inventory Transaction
      ├── Audit Event
      └── Outbox Event
      ↓
COMMIT
      ↓
Background Worker
      ↓
Notification / Printing / Reporting
```

This ensures secondary processing does not become a hidden dependency of the core transaction.

---

# 37. Cache Interaction

Cache operations must respect transaction boundaries.

Preferred sequence:

```text
Validate
   ↓
Database Transaction
   ↓
Commit
   ↓
Cache Invalidation / Refresh
```

The API must not expose uncommitted configuration as authoritative state.

---

# 38. Idempotency Processing

For idempotent state-changing operations, idempotency handling must occur before duplicate business effects can be created.

Typical flow:

```text
Request
   ↓
Read Idempotency-Key
   ↓
Validate Operation Identity
   ↓
Check Existing Operation
   ↓
Already Processed?
 ┌──────┴──────┐
Yes            No
 ↓              ↓
Return Result   Execute Use Case
                  ↓
                Commit
                  ↓
                Store Result
```

The exact implementation may integrate idempotency storage with the Application transaction.

---

# 39. Idempotency Conflict

If the same idempotency key is reused with materially different input:

```text
409 Conflict
```

Example:

```text
Operation X:
Pay Order A
Amount = 20,000

Retry:
Same Operation X
Amount = 30,000

Result:
IDEMPOTENCY_KEY_REUSE_CONFLICT
```

The server must not execute the second operation.

---

# 40. Concurrency Control

Concurrency must be handled according to the affected resource.

Possible mechanisms include:

* optimistic version checking;
* `If-Match`;
* database row locks;
* state validation;
* unique constraints;
* idempotency records.

Example:

```text
Configuration Version = 12

Client A → update version 12
Client B → update version 12

A succeeds → version 13
B fails → STALE_VERSION
```

---

# 41. Financial Concurrency

Financial operations require authoritative transactional validation.

Examples:

* payment;
* refund;
* cash session close;
* cash correction.

Cached values must not be used as the final authority.

---

# 42. Inventory Concurrency

Inventory deduction must use authoritative database state.

Example:

```text
Available = 2

Request A → quantity 2
Request B → quantity 2

Only one operation may successfully consume the available stock.
```

The implementation must prevent negative inventory.

---

# 43. Order State Concurrency

Order state transitions must be validated against current authoritative state.

Example:

```text
OPEN
  ↓
ACCEPTED
  ↓
PAID
```

A request attempting to pay an already paid Order must fail deterministically.

---

# 44. Response Mapping

After successful Application execution, the API maps the application result into the public response contract.

The response mapper may:

* select fields;
* transform internal DTOs;
* add pagination metadata;
* add request context metadata;
* convert internal statuses to public enum values.

It must not introduce new business decisions.

---

# 45. Response Serialization

The final application result is serialized according to the API contract.

Example:

```text
Application Result
      ↓
Response DTO
      ↓
JSON Serialization
      ↓
HTTP Response
```

Internal ORM objects should not be serialized directly.

---

# 46. Response Security Filtering

Before serialization, the API must ensure that only authorized fields are exposed.

Examples of fields that may require filtering:

* internal employee metadata;
* security state;
* private configuration;
* internal identifiers;
* sensitive audit details.

Response filtering must be server-side.

---

# 47. Successful Response Status

The API should use status codes according to operation semantics.

Examples:

```text
GET resource
→ 200 OK

POST resource creation
→ 201 Created

Successful command
→ 200 OK

Accepted asynchronous operation
→ 202 Accepted

Successful operation with no representation
→ 204 No Content
```

The endpoint contract defines the exact response behavior.

---

# 48. Error Propagation

Errors should propagate through controlled layers.

Example:

```text
Domain Error
      ↓
Application Error
      ↓
API Error Mapper
      ↓
HTTP Status + Error Code
```

Internal exceptions must not leak directly into HTTP responses.

---

# 49. Error Translation

The API translates known application/domain failures into stable public errors.

Example:

```text
Domain:
InsufficientStockError

API:
409 Conflict
INSUFFICIENT_STOCK
```

The public error contract must not depend on the internal exception class name.

---

# 50. Unexpected Errors

Unexpected errors must be handled by the global API exception boundary.

Production responses should contain:

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred.",
    "request_id": "..."
  }
}
```

Internal stack traces belong in protected logs, not client responses.

---

# 51. Transaction Failure

If a core transaction fails:

```text
DB Rollback
      ↓
No authoritative state change
      ↓
API Error Response
```

The API must not report successful business completion.

---

# 52. Secondary Failure After Commit

If a secondary operation fails after the core transaction commits:

```text
Core Transaction
      ↓
COMMIT SUCCESS
      ↓
Notification / Printing / Report Refresh
      ↓
Failure
```

The core transaction remains successful.

The secondary failure must be handled through retry, monitoring or recovery mechanisms.

---

# 53. Printer Failure

For operations such as Order acceptance:

```text
Order Transaction
      ↓
COMMIT
      ↓
Printing
      ↓
Printer Failure
```

Printer failure must not rollback the committed Order state.

The printing operation should be retried or surfaced through the appropriate operational mechanism.

---

# 54. Notification Failure

Notification delivery must not normally rollback the core business transaction.

Example:

```text
Refund
 ↓
Refund committed
 ↓
Owner notification fails
```

The refund remains authoritative.

Notification delivery is retried asynchronously.

---

# 55. Asynchronous Request Lifecycle

For long-running operations:

```text
Client
  ↓
POST /reports
  ↓
Authenticate
  ↓
Authorize
  ↓
Validate
  ↓
Create Job
  ↓
Commit Job
  ↓
202 Accepted
  ↓
Worker
  ↓
Process
  ↓
Update Job
```

The initial API request does not wait for the entire operation.

---

# 56. Job Status

The client may retrieve:

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

The job state is server-authoritative.

---

# 57. File Generation Lifecycle

For XLSX export:

```text
POST /exports
      ↓
Validate
      ↓
Authorize
      ↓
Create Export Job
      ↓
202 Accepted
      ↓
Worker
      ↓
Generate XLSX
      ↓
Store File
      ↓
Mark Job Completed
      ↓
Client Downloads File
```

File generation must not unnecessarily hold an HTTP request open.

---

# 58. Offline Synchronization Lifecycle

Offline synchronization follows a dedicated flow:

```text
Offline Device
      ↓
Create Local Operation UUID
      ↓
Queue Operation
      ↓
Network Available
      ↓
POST /sync/batches
      ↓
Authenticate Device
      ↓
Validate Signature / Authorization
      ↓
Validate Business / Branch Scope
      ↓
Validate Operation
      ↓
Check Idempotency
      ↓
Apply Operation
      ↓
Return Per-Operation Result
```

The server remains authoritative.

---

# 59. Synchronization Failure

A synchronization operation may produce:

```text
ACCEPTED
ALREADY_PROCESSED
REJECTED
CONFLICT
INVALID
UNAUTHORIZED
TEMPORARY_FAILURE
```

The client must only retry operations that are explicitly retryable.

Permanent business conflicts must not be retried indefinitely.

---

# 60. Request Timeout

The API must use bounded timeouts.

If the server cannot complete the request within the applicable boundary:

```text
Timeout
   ↓
Request terminates
```

The client must not assume that timeout means the business operation was definitely not committed.

For state-changing operations, the client must use the operation/idempotency identity to determine the authoritative result.

---

# 61. Timeout and Idempotency

Example:

```text
Client
  ↓
POST /orders/{id}/pay
Idempotency-Key: X
  ↓
Server processes successfully
  ↓
Network timeout
  ↓
Client retries X
  ↓
Server returns original result
```

This prevents duplicate financial effects.

---

# 62. Request Cancellation

If a client disconnects, the server must distinguish:

* HTTP connection cancellation;
* business transaction cancellation;
* already committed business state.

A disconnected client must not cause an already committed transaction to be incorrectly considered failed.

---

# 63. API Lifecycle for Read Requests

A typical read request:

```text
GET /api/v1/orders/{id}

HTTP Request
    ↓
Request Context
    ↓
Authentication
    ↓
Authorization
    ↓
Path Validation
    ↓
Application Query
    ↓
Repository
    ↓
PostgreSQL / Cache
    ↓
Authorized Result
    ↓
Response Mapping
    ↓
200 OK
```

Reads should not create business side effects.

---

# 64. API Lifecycle for Simple Mutation

A simple authorized mutation:

```text
PATCH /api/v1/products/{id}

HTTP Request
    ↓
Authentication
    ↓
Authorization
    ↓
Validation
    ↓
Concurrency Check
    ↓
Application Use Case
    ↓
Domain Validation
    ↓
Database Transaction
    ↓
Audit
    ↓
Commit
    ↓
Cache Invalidation
    ↓
Response
```

---

# 65. API Lifecycle for Business Command

Example:

```text
POST /api/v1/orders/{id}/accept

Request
    ↓
Authentication
    ↓
Authorization
    ↓
Validation
    ↓
Idempotency
    ↓
Application Use Case
    ↓
Domain Rules
    ↓
Inventory Validation
    ↓
Inventory Deduction
    ↓
Order State Change
    ↓
Audit
    ↓
Outbox
    ↓
Commit
    ↓
Response
```

---

# 66. API Lifecycle for Financial Command

Example:

```text
POST /api/v1/orders/{id}/payments

Request
    ↓
Authentication
    ↓
Authorization
    ↓
Validation
    ↓
Idempotency
    ↓
Current Order State
    ↓
Financial Validation
    ↓
Payment Transaction
    ↓
Order State Update
    ↓
Audit
    ↓
Commit
    ↓
Response
```

The final financial result is authoritative only after successful commit.

---

# 67. API Lifecycle for Configuration Change

Example:

```text
PATCH /api/v1/products/{id}/price

Request
    ↓
Authentication
    ↓
Authorization
    ↓
Subscription Check
    ↓
Validation
    ↓
Version Check
    ↓
Application Use Case
    ↓
Configuration Version Creation
    ↓
Audit
    ↓
Commit
    ↓
Cache Invalidation
    ↓
Response
```

Stale configuration updates must not silently overwrite newer state.

---

# 68. API Lifecycle for Bulk Operations

Bulk operations should follow:

```text
Request
    ↓
Authentication
    ↓
Authorization
    ↓
Batch Validation
    ↓
Size Limit
    ↓
Application Batch Processing
    ↓
Bounded Operations
    ↓
Per-Item Result
    ↓
Response
```

Bulk requests must not automatically become unlimited database transactions.

---

# 69. API Lifecycle for External Integration

When an external integration is involved:

```text
Client
    ↓
API
    ↓
Authentication
    ↓
Authorization
    ↓
Validation
    ↓
Application
    ↓
Core Transaction
    ↓
Outbox
    ↓
Commit
    ↓
Background Worker
    ↓
External Provider
```

External services should not unnecessarily become part of the core database transaction.

---

# 70. Request Lifecycle and Business Isolation

At every stage where Business-owned data is accessed, the Business scope must remain available.

The request must never transition from:

```text
Business A
```

to:

```text
Business B
```

merely because a client-supplied identifier changes.

Business context is preserved throughout:

```text
API
 ↓
Application
 ↓
Repository
 ↓
Database
```

---

# 71. Request Lifecycle and Branch Isolation

Branch scope follows the same principle.

A Branch-scoped request must preserve:

```text
Business
+
Branch
+
Actor
```

throughout the Application and data-access layers.

A Branch ID must not be accepted independently from Business authorization.

---

# 72. Request Lifecycle and Device Context

For trusted POS/offline operations, Device context may be required.

The server validates:

* Device identity;
* trust state;
* Business ownership;
* Branch association;
* employee relationship;
* offline authorization where applicable.

Device identity is never sufficient by itself for authorization.

---

# 73. Request Lifecycle and Cash Session

Cash-related operations may require active Cash Session context.

Example:

```text
Payment
    ↓
Employee
    ↓
Branch
    ↓
Cash Register
    ↓
Cash Session
```

The Application layer validates whether the session is:

* active;
* owned by the appropriate operational context;
* valid for the requested operation.

---

# 74. Request Lifecycle and Historical State

When a request operates on historical data, the API must use the authoritative historical representation.

Examples:

```text
Refund
    ↓
Historical Order Price

Inventory History
    ↓
Historical Recipe Version

Report
    ↓
Applicable Report Version
```

Current configuration must not reinterpret historical state.

---

# 75. Request Lifecycle and Caching

A read may use:

```text
Application
   ↓
Cache
   ↓
Cache Hit
   ↓
Response
```

or:

```text
Application
   ↓
Cache Miss
   ↓
PostgreSQL
   ↓
Cache
   ↓
Response
```

For authoritative state-changing decisions, the Application must validate authoritative database state where required.

---

# 76. Request Lifecycle and Auditability

Important state changes must preserve:

```text
Request ID
Operation UUID
Business
Branch
Employee
Device
Resource
Timestamp
Result
```

The exact audit context depends on the operation.

The API must provide enough context for the Application layer to create a correct audit record.

---

# 77. Request Lifecycle and Observability

A request should be traceable across:

```text
HTTP
 ↓
Application
 ↓
Database
 ↓
Outbox
 ↓
Background Worker
 ↓
External Integration
```

Where applicable, correlation identifiers should be propagated.

---

# 78. Request Lifecycle and Background Jobs

A background job originating from an API request should retain appropriate context.

Example:

```text
Request ID
Operation ID
Business ID
Actor ID
```

However, a background worker must not blindly inherit expired authorization.

The worker must use its own server-side authorization and job ownership rules.

---

# 79. API Context vs Worker Context

HTTP request context and background job context are different.

HTTP:

```text
Request
Actor
Device
Session
```

Worker:

```text
Job
Business
Operation
System Actor
```

A worker must not depend on an HTTP request remaining alive.

---

# 80. Response After Commit

For authoritative state-changing operations, successful responses should be generated from committed application results.

The server should not return an optimistic success based only on client input.

Example:

```text
Client:
amount = 25,000

Server:
authoritative payment = 25,000
status = PAID

Response:
committed result
```

---

# 81. Response Consistency

The response should represent the authoritative state resulting from the operation.

For example, after payment:

```json
{
  "data": {
    "order_id": "...",
    "status": "PAID",
    "paid_amount": "25000.00"
  }
}
```

The client should not need to reconstruct the authoritative state from request parameters.

---

# 82. Error Recovery Lifecycle

A recoverable request follows:

```text
Request
  ↓
Validation / Execution
  ↓
Known Failure
  ↓
Stable Error Code
  ↓
Client Recovery
```

Examples:

```text
STALE_VERSION
→ Refresh resource

TEMPORARY_FAILURE
→ Retry later

INSUFFICIENT_STOCK
→ Modify order or inventory

SUBSCRIPTION_READ_ONLY
→ Subscription action required
```

---

# 83. Failure Isolation

A failure in one subsystem should not unnecessarily break unrelated API operations.

Examples:

```text
Redis unavailable
→ PostgreSQL fallback

Printer unavailable
→ Order remains committed

Notification provider unavailable
→ Notification retry

Report worker unavailable
→ POS continues
```

Core transactional correctness has priority.

---

# 84. Request Lifecycle Performance

The request lifecycle must avoid unnecessary stages for simple operations.

For example, a simple authenticated read should not perform:

* report generation;
* unnecessary external calls;
* unnecessary synchronization;
* heavy audit processing.

Each lifecycle stage must have a measurable reason to exist.

---

# 85. POS Request Optimization

For POS-critical operations:

* minimize network round trips;
* keep payloads compact;
* use efficient queries;
* use safe local/offline state where authorized;
* avoid unnecessary serialization;
* avoid synchronous notifications;
* avoid synchronous printing;
* avoid synchronous report generation.

The target remains:

**Core POS command p95 ≤ 500 ms** under the defined normal operating load.

---

# 86. Request Lifecycle SLOs

The lifecycle must support the following initial targets:

| Stage                                |   Target |
| ------------------------------------ | -------: |
| Ordinary authenticated API p95       | ≤ 300 ms |
| Ordinary authenticated API p99       | ≤ 800 ms |
| Core POS command p95                 | ≤ 500 ms |
| Authorization overhead p95           | ≤ 100 ms |
| Business/Branch scope validation p95 |  ≤ 50 ms |
| Idempotency lookup p95               |  ≤ 50 ms |
| Normal indexed DB query p95          | ≤ 100 ms |

These are architectural targets and must be validated through production-like testing.

---

# 87. Request Lifecycle Invariants

The following invariants apply to API layers and request lifecycle:

1. API routes remain thin.
2. API routes do not contain core business logic.
3. API routes do not directly modify PostgreSQL.
4. HTTP transport concerns remain separate from business logic.
5. Authentication establishes actor identity.
6. Authentication does not automatically grant authorization.
7. Authorization is server-side.
8. Business scope is server-validated.
9. Branch scope is server-validated.
10. Client-provided identifiers are never authoritative.
11. Subscription entitlement is server-enforced.
12. Request context contains only applicable information.
13. Request IDs remain distinct from operation IDs.
14. Operation UUIDs remain distinct from resource UUIDs.
15. Request validation occurs before business execution.
16. Structural validation is distinct from business validation.
17. Complex business rules remain in Application/Domain layers.
18. Application use cases do not depend on HTTP framework objects.
19. Domain logic does not depend on HTTP.
20. Repository access does not originate directly from API handlers.
21. Transaction boundaries are controlled by the Application layer.
22. Core transaction success is reported only after required commit.
23. Audit state changes are integrated with the appropriate transaction boundary.
24. Secondary effects use asynchronous processing where appropriate.
25. Outbox events are committed consistently with their triggering business operation.
26. Cache invalidation must not publish uncommitted authoritative state.
27. Idempotent operations cannot duplicate business effects.
28. Conflicting idempotency-key reuse is rejected.
29. Important concurrent updates use explicit concurrency control.
30. Financial operations use authoritative transactional state.
31. Inventory deduction uses authoritative inventory state.
32. Order state transitions use authoritative current state.
33. Historical transactions are not reinterpreted using current configuration.
34. Errors are translated into stable public error contracts.
35. Unexpected exceptions do not expose stack traces.
36. Transaction rollback prevents partial authoritative state.
37. Secondary failures do not automatically rollback committed core state.
38. Printer failure does not rollback committed Order state.
39. Notification failure does not rollback committed core state.
40. Long-running operations use asynchronous processing where appropriate.
41. API timeouts are bounded.
42. Client timeout does not prove that the business operation was not committed.
43. Retryable commands use idempotency to determine authoritative results.
44. Synchronization operations have stable operation identity.
45. Synchronization cannot bypass authorization.
46. Synchronization cannot bypass Business or Branch isolation.
47. Offline timestamps do not override server authority.
48. Batch operations are bounded.
49. Bulk operations are bounded.
50. Business context remains consistent through Application and Repository layers.
51. Branch context remains consistent through Application and Repository layers.
52. Device context is validated where required.
53. Cash Session context is validated for cash operations.
54. Background workers do not depend on active HTTP requests.
55. Background workers use their own valid execution context.
56. API responses represent authoritative committed results.
57. Response serialization does not introduce business decisions.
58. Unauthorized response fields are never exposed.
59. Cache is never the final authority for financial state.
60. Observability context is propagated where appropriate.
61. Metrics do not create uncontrolled high-cardinality labels.
62. POS-critical requests avoid unnecessary synchronous secondary work.
63. API lifecycle stages remain measurable.
64. API lifecycle complexity must not be introduced without architectural justification.
65. API request processing preserves Business isolation.
66. API request processing preserves Branch isolation.
67. API request processing preserves historical integrity.
68. API request processing preserves transaction correctness.
69. API request processing preserves offline compatibility.
70. API request processing remains compatible with defined API SLOs.

---

# 88. Recommended Request Lifecycle

The standard protected request lifecycle is:

```text
HTTP Request
    ↓
Reverse Proxy / TLS
    ↓
Request Size Protection
    ↓
Request ID
    ↓
Tracing / Correlation
    ↓
Routing
    ↓
Authentication
    ↓
Request Context
    ↓
Authorization
    ↓
Structural Validation
    ↓
Idempotency / Concurrency Preparation
    ↓
Application Use Case
    ↓
Domain Logic
    ↓
Repository / Infrastructure
    ↓
PostgreSQL Transaction
    ↓
Audit / Outbox
    ↓
Commit
    ↓
Cache Invalidation / Secondary Processing
    ↓
Response Mapping
    ↓
HTTP Response
```

The exact execution order may vary for specific endpoint types, but the responsibility boundaries must remain intact.

---

# 89. Recommended Read Request Lifecycle

```text
HTTP Request
    ↓
Request Context
    ↓
Authentication
    ↓
Authorization
    ↓
Validation
    ↓
Application Query
    ↓
Cache / Repository
    ↓
Authorized Result
    ↓
Response Mapping
    ↓
HTTP Response
```

---

# 90. Recommended Command Request Lifecycle

```text
HTTP Request
    ↓
Authentication
    ↓
Authorization
    ↓
Validation
    ↓
Idempotency
    ↓
Application Use Case
    ↓
Domain Rules
    ↓
Transaction
    ↓
Audit / Outbox
    ↓
Commit
    ↓
Response
```

---

# 91. Recommended Asynchronous Lifecycle

```text
HTTP Request
    ↓
Authentication
    ↓
Authorization
    ↓
Validation
    ↓
Create Job
    ↓
Commit
    ↓
202 Accepted
    ↓
Background Worker
    ↓
Processing
    ↓
Result Storage
    ↓
Client Status Request
```

---

# 92. Recommended Synchronization Lifecycle

```text
Trusted Device
    ↓
Sync Batch
    ↓
Authentication
    ↓
Device Validation
    ↓
Business / Branch Validation
    ↓
Operation Validation
    ↓
Idempotency
    ↓
Application Processing
    ↓
Conflict / Business Rule Evaluation
    ↓
Commit Accepted Operations
    ↓
Per-Operation Results
    ↓
Device Reconciliation
```

---

# 93. API Layer Ownership Summary

| Concern                     | Primary Owner                  |
| --------------------------- | ------------------------------ |
| HTTP routing                | API                            |
| Request parsing             | API                            |
| Schema validation           | API                            |
| Request ID                  | API/Middleware                 |
| Authentication              | Security/API                   |
| Authorization orchestration | API/Application                |
| Business rules              | Domain                         |
| Use-case workflow           | Application                    |
| Transaction boundary        | Application                    |
| Persistence                 | Repository/Infrastructure      |
| Database constraints        | PostgreSQL                     |
| Audit creation              | Application/Domain integration |
| Outbox creation             | Application                    |
| Cache                       | Infrastructure                 |
| Response mapping            | API                            |
| Error mapping               | API                            |
| Async processing            | Background/Worker              |
| Synchronization             | Synchronization/Application    |
| OpenAPI                     | API Contract                   |

---

# 94. Architectural Guardrails

The following patterns are prohibited:

```text
API Route
   ↓
SQL Query
```

```text
API Route
   ↓
Direct ORM Mutation
```

```text
API Route
   ↓
Business Calculation
```

```text
Frontend Permission
   ↓
Assumed Server Authorization
```

```text
Cache
   ↓
Final Financial Decision
```

```text
HTTP Request
   ↓
External Service
   ↓
Database Transaction
```

when the external service is not required for core correctness.

The preferred architecture is:

```text
API
 ↓
Application
 ↓
Domain
 ↓
Repository
 ↓
Database
```

with secondary processing separated through events/jobs where appropriate.

---

# 95. Related Documents

### API

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`
* `docs/04_Architecture/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/08_API_Request_Validation_and_Response_Contracts.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

### Backend Architecture

* `docs/04_Architecture/03_Application_and_Use_Case_Layer.md`
* `docs/04_Architecture/04_Domain_Service_and_Business_Logic.md`
* `docs/04_Architecture/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/07_Transaction_Management.md`
* `docs/04_Architecture/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/16_Backend_Security_Hardening_and_Application_Security.md`

### Database

* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

---

# 96. Status

**API Architecture Section:** In Progress

**Document Status:** Proposed

**Current Document:** `03_API_Layers_and_Request_Lifecycle.md`

**Previous Document:** `02_API_Design_Principles_and_Standards.md`

**Next Document:** `04_API_Versioning_and_Backward_Compatibility.md`

