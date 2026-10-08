# API Architecture

**Document ID:** ARCH-06
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the API architecture of FastFood ERP.

The API is the controlled boundary between frontend clients, trusted devices, synchronization clients, and the backend application.

The API must provide:

* secure authentication;
* authorization;
* Business and Branch isolation;
* command and query operations;
* predictable request and response contracts;
* idempotent state-changing operations;
* offline synchronization;
* conflict handling;
* report and export access;
* consistent error handling;
* API versioning;
* pagination and filtering;
* observability;
* controlled performance.

The API must expose application capabilities without exposing internal database or domain implementation details.

---

# 2. API Architecture Principles

The API follows these principles:

1. **Backend authority**
2. **Explicit contracts**
3. **Business isolation**
4. **Branch isolation**
5. **Server-side authorization**
6. **Idempotent mutations**
7. **Stable resource identity**
8. **Command/query separation**
9. **Consistent error contracts**
10. **Versioned public contracts**
11. **Offline-aware synchronization**
12. **Historical integrity**
13. **Secure defaults**
14. **Pagination**
15. **Predictable performance**
16. **Observability**
17. **No direct database exposure**

---

# 3. API Consumers

The primary API consumers are:

```text
Web Frontend
Trusted POS Device
Trusted Offline Device
Synchronization Client
Administrative Interface
Background/Internal API Consumers
```

The API must identify the context of each request.

Not every consumer requires the same capabilities.

---

# 4. API Boundary

The API sits between clients and the Application Layer:

```text
Client
  ↓
API
  ↓
Authentication
  ↓
Execution Context
  ↓
Authorization
  ↓
Application Use Case
  ↓
Domain
  ↓
Infrastructure
```

The API must not directly call database repositories for business mutations.

---

# 5. API Versioning

The API should use explicit versioning.

Recommended structure:

```text
/api/v1/...
```

The version identifies the API contract, not the internal application version.

Internal refactoring should not require an API version change when the public contract remains compatible.

---

# 6. Breaking Changes

A breaking change includes:

* removing a required field;
* changing the meaning of a field;
* removing an endpoint;
* changing an enum incompatibly;
* changing response structure incompatibly;
* changing authorization semantics in a way that breaks supported clients.

Breaking changes require a new API version where compatibility cannot be preserved.

---

# 7. Resource Naming

Resource names should use stable domain concepts.

Examples:

```text
/businesses
/branches
/employees
/orders
/payments
/refunds
/cash-sessions
/inventory
/products
/recipes
/reports
/notifications
/devices
```

Naming must remain consistent.

Plural resource names are preferred for collection endpoints.

---

# 8. Resource Identity

Resources use UUID-based identities.

Examples:

```text
Business UUID
Branch UUID
Employee UUID
Order UUID
Payment UUID
Cash Session UUID
Device UUID
Report UUID
Conflict UUID
```

Customer-facing short numbers may exist for usability.

For example:

```text
Order Number: 123
Order UUID:   permanent UUID
```

The short order number is not the authoritative identity.

---

# 9. Business Context

Every authenticated Business operation must execute within a Business context.

The backend must determine the Business context from authenticated and authorized state.

The client must not be allowed to arbitrarily select another Business by modifying a request field.

Conceptually:

```text
Authenticated User
       ↓
Authorized Business
       ↓
Requested Resource
```

---

# 10. Branch Context

Branch-scoped operations must identify the relevant Branch.

Example:

```text
POST /api/v1/orders
```

The request may contain a Branch UUID where appropriate.

The backend must verify:

```text
Employee
   ↓
Business
   ↓
Branch Scope
   ↓
Permission
```

A valid Branch UUID alone does not grant access.

---

# 11. Business and Branch Isolation

The API must enforce isolation for:

* requests;
* responses;
* reports;
* exports;
* synchronization;
* notifications;
* audit;
* background operations.

A request authorized for Branch A must not return Branch B data.

A request authorized for Business A must never return Business B data.

---

# 12. Authentication

Authentication identifies the caller.

Supported authentication mechanisms may include:

* authenticated employee session;
* access token;
* refresh token;
* trusted device credentials;
* signed offline authorization.

The exact token technology is defined by the Security Architecture and Technology Selection documents.

---

# 13. Authentication vs Authorization

These concepts remain separate.

```text
Authentication
    =
Who are you?

Authorization
    =
What may you do?
```

A valid authenticated session does not automatically authorize an operation.

---

# 14. Request Authentication Pipeline

A normal authenticated request follows:

```text
HTTP Request
    ↓
Extract Credentials
    ↓
Validate Authentication
    ↓
Identify Employee
    ↓
Identify Business
    ↓
Identify Device
    ↓
Build Execution Context
```

The request then proceeds to authorization.

---

# 15. Authorization Pipeline

For protected operations:

```text
Authentication
      ↓
Business Membership
      ↓
Branch Scope
      ↓
Employee Status
      ↓
Role Permission
      ↓
Employee Override
      ↓
Subscription Entitlement
      ↓
Device Trust
      ↓
Operation Authorization
```

Only the checks relevant to the operation need to execute.

---

# 16. Permission Checks

The API must check permissions server-side.

Examples:

```text
orders.create
orders.modify
orders.cancel
payments.create
refunds.create
inventory.adjust
recipes.modify
recipes.approve
employees.manage
payroll.view
reports.view
reports.export
cash.correct
devices.manage
```

Permission names are illustrative and may be refined during implementation.

---

# 17. Permission Context

The authorization result should conceptually contain:

```text
Employee
Business
Branch Scope
Effective Permissions
Subscription Entitlements
Device State
```

The API should not trust a client-provided permission list.

---

# 18. Subscription Enforcement

Subscription entitlement is an API authorization boundary.

The backend must validate:

* subscription status;
* expiry;
* grace period;
* feature entitlement;
* branch limit;
* employee limit;
* Owner limit;
* other configured tariff limits.

The frontend may hide unavailable features, but the API must reject unauthorized modifications.

---

# 19. Read-Only Subscription State

After subscription expiry, the API may continue allowing authorized read operations.

Examples:

```text
GET /orders
GET /inventory
GET /reports
GET /employees
GET /cash-sessions
```

Modification endpoints should return an appropriate subscription restriction error.

Read-only behavior remains subject to permission and Business/Branch scope.

---

# 20. Grace Period

The default subscription grace period is three days where applicable.

The API must evaluate grace period using authoritative server time.

Clients must not determine subscription expiry using their local system clock.

---

# 21. API Operation Types

API operations are conceptually divided into:

### Queries

Read data without changing business state.

### Commands

Change business state.

### Synchronization Operations

Submit offline operations and receive server validation results.

### Export Operations

Request generated files or report exports.

---

# 22. Query Endpoints

Examples:

```text
GET /api/v1/orders
GET /api/v1/orders/{order_id}
GET /api/v1/inventory
GET /api/v1/products
GET /api/v1/cash-sessions
GET /api/v1/reports
GET /api/v1/notifications
GET /api/v1/audit-events
```

Query endpoints must not perform hidden business mutations.

---

# 23. Command Endpoints

Examples:

```text
POST /api/v1/orders
POST /api/v1/orders/{order_id}/accept
POST /api/v1/orders/{order_id}/modify
POST /api/v1/orders/{order_id}/cancel

POST /api/v1/cash-sessions
POST /api/v1/cash-sessions/{session_id}/close
POST /api/v1/cash-sessions/handover

POST /api/v1/payments
POST /api/v1/refunds

POST /api/v1/inventory/adjustments
POST /api/v1/recipes/{recipe_id}/approve
```

Commands represent business operations rather than arbitrary database updates.

---

# 24. REST Resource vs Command Endpoint

Simple CRUD-like operations may use resource endpoints.

Business operations with explicit rules should use command-style endpoints.

For example:

```text
POST /orders
```

may create a Draft.

But:

```text
POST /orders/{id}/accept
```

represents a specific business operation.

This keeps the API contract aligned with business behavior.

---

# 25. Order API

Conceptual order endpoints:

```text
POST   /api/v1/orders
GET    /api/v1/orders
GET    /api/v1/orders/{order_id}

POST   /api/v1/orders/{order_id}/accept
POST   /api/v1/orders/{order_id}/modify
POST   /api/v1/orders/{order_id}/cancel
```

The API must preserve the distinction between:

* Draft;
* Accepted;
* Preparing;
* Ready;
* Served.

---

# 26. Order Creation

Order creation must validate:

* Business;
* Branch;
* Employee;
* Device where applicable;
* permission;
* order type;
* table context where applicable;
* current configuration.

Creating a Draft does not deduct inventory.

---

# 27. Order Acceptance

Order acceptance is a transactional command.

The API must ensure:

```text
Permission
+
Current Configuration
+
Inventory
+
Order State
+
Branch State
```

are valid before accepting.

Successful acceptance results in server-confirmed Accepted state.

---

# 28. Order Modification

Accepted order modification must use a dedicated operation.

The API should not allow arbitrary replacement of the entire order document.

This protects:

* inventory;
* historical integrity;
* pricing;
* audit;
* concurrency.

---

# 29. New Product After Acceptance

Adding a new product after an order is Accepted may create a separate operational ticket/order linked to the existing order context.

The API must preserve:

* original order UUID;
* new operational order/ticket identity;
* table context;
* customer-facing relationship where applicable;
* audit history.

---

# 30. Order Cancellation

Cancellation is a separate business operation.

Example:

```text
POST /api/v1/orders/{order_id}/cancel
```

The request should include:

* reason;
* relevant inventory-return decision where applicable;
* optional comment.

Cancellation does not delete the order.

---

# 31. Payment API

Conceptual endpoints:

```text
POST /api/v1/payments
GET  /api/v1/payments
GET  /api/v1/payments/{payment_id}

POST /api/v1/payments/{payment_id}/revise
```

Payment operations must preserve historical integrity.

---

# 32. Payment Request

A payment request should contain conceptually:

```text
Order UUID
Payment Method
Amount
Portions if Mixed
Customer/Debt Context where applicable
Idempotency Identity
```

The backend validates the final financial result.

---

# 33. Payment Methods

The API supports:

```text
CASH
CARD
DEBT
MIXED
```

The API must reject unsupported methods.

---

# 34. Partial Payment

The API must allow partial payment where permitted.

The response should make clear:

```text
Total
Paid
Remaining
Payment Status
```

The frontend must not infer final payment state from a single submitted amount.

---

# 35. Mixed Payment

A Mixed payment contains multiple portions.

Conceptually:

```text
Payment
├── Cash Portion
├── Card Portion
└── Other Supported Portion
```

The payment remains one logical payment operation.

---

# 36. Overpayment

The API must explicitly handle overpayment.

If:

```text
Payment Amount > Remaining Amount
```

the request may require explicit confirmation or explanation according to business rules.

The excess must not silently disappear.

---

# 37. Refund API

Conceptual endpoint:

```text
POST /api/v1/refunds
```

The request should contain:

* Order/Payment reference;
* refund type;
* amount or item/quantity;
* method;
* reason;
* comment;
* idempotency identity.

Refunds are separate financial operations.

---

# 38. Refund Inventory Rule

The refund API must not automatically return inventory.

Inventory return, if ever required by a separate business operation, must be explicit and authorized.

---

# 39. Cash Session API

Conceptual endpoints:

```text
POST /api/v1/cash-sessions
GET  /api/v1/cash-sessions
GET  /api/v1/cash-sessions/{session_id}

POST /api/v1/cash-sessions/{session_id}/close
POST /api/v1/cash-sessions/handover
POST /api/v1/cash-sessions/{session_id}/corrections
```

---

# 40. Cash Session Opening

Opening a Cash Session must validate:

* Branch;
* Cash Register;
* Employee;
* Device;
* permission;
* active session constraint;
* opening cash;
* subscription state.

Concurrent opening attempts must be handled transactionally.

---

# 41. Cash Session Closing

Closing must validate:

* session is active;
* cashier authorization;
* physical cash count;
* current session state;
* correction rules where applicable.

The API must return:

```text
Expected Amount
Actual Amount
Difference
Order Count
Payment Totals
Session Status
```

where permitted.

---

# 42. Cash Handover API

Handover should be represented as a controlled operation.

Conceptually:

```text
POST /api/v1/cash-sessions/handover
```

The backend performs:

```text
Close Previous Session
      ↓
Validate New Cashier
      ↓
Validate Physical Cash
      ↓
Open New Session
```

The previous Cash Session remains closed.

---

# 43. Inventory API

Conceptual endpoints:

```text
GET  /api/v1/inventory
GET  /api/v1/inventory/movements

POST /api/v1/inventory/purchases
POST /api/v1/inventory/adjustments
POST /api/v1/inventory/production
```

Inventory mutations require explicit permissions.

---

# 44. Inventory Concurrency

Inventory-changing API requests must use server-side concurrency control.

The API must not rely on:

```text
GET stock
+
Client calculates
+
POST new stock
```

as the authoritative transaction model.

The backend must perform atomic validation and modification.

---

# 45. Product and Recipe API

Conceptual endpoints:

```text
GET  /api/v1/products
POST /api/v1/products

GET  /api/v1/recipes
POST /api/v1/recipes
POST /api/v1/recipes/{recipe_id}/approve
```

Archive/deactivation should be preferred over destructive deletion where historical references exist.

---

# 46. Menu and Pricing API

Conceptual endpoints:

```text
GET  /api/v1/menu
GET  /api/v1/products/{product_id}
POST /api/v1/menu/configurations
POST /api/v1/prices
POST /api/v1/prices/{price_id}/activate
```

The exact endpoint model may evolve during implementation.

The API must preserve effective configuration versions.

---

# 47. Employee API

Conceptual endpoints:

```text
GET  /api/v1/employees
POST /api/v1/employees
GET  /api/v1/employees/{employee_id}

POST /api/v1/employees/{employee_id}/activate
POST /api/v1/employees/{employee_id}/deactivate
POST /api/v1/employees/{employee_id}/permissions
```

Employee management is permission-controlled.

---

# 48. Permission API

Permission APIs must distinguish:

* Role configuration;
* Employee override;
* Branch scope.

A Manager must not be able to grant permissions beyond the authority granted to the Manager.

The backend must validate this.

---

# 49. Payroll API

Conceptual endpoints:

```text
GET  /api/v1/payroll
POST /api/v1/payroll/runs
POST /api/v1/payroll/runs/{run_id}/finalize
POST /api/v1/payroll/corrections
```

Finalized payroll records are immutable historical states.

Corrections use separate operations.

---

# 50. Reports API

Conceptual endpoints:

```text
GET  /api/v1/reports
POST /api/v1/reports
GET  /api/v1/reports/{report_id}
GET  /api/v1/reports/{report_id}/versions
GET  /api/v1/reports/{report_id}/versions/{version_id}
```

Large reports may be generated asynchronously.

---

# 51. Report Generation

For small reports:

```text
Request
  ↓
Generate
  ↓
Return Result
```

For heavy reports:

```text
Request
  ↓
Create Job
  ↓
202 Accepted
  ↓
Background Generation
  ↓
Report Ready
```

The API must not block the POS critical path.

---

# 52. Excel Export API

Conceptual endpoint:

```text
POST /api/v1/reports/{report_version_id}/exports
```

For large exports:

```text
POST
  ↓
Export Job
  ↓
Processing
  ↓
Ready
  ↓
Authorized Download
```

The exported file must represent the selected immutable report version.

---

# 53. Notification API

Conceptual endpoints:

```text
GET  /api/v1/notifications
POST /api/v1/notifications/{notification_id}/read
POST /api/v1/notifications/{notification_id}/resolve
```

Notification actions must remain permission-aware.

---

# 54. Audit API

Conceptual endpoint:

```text
GET /api/v1/audit-events
```

Supported filters may include:

```text
Branch
Employee
Event
Entity
Transaction
Device
Cash Session
Source
Result
Date Range
```

Audit records are read-only through the public API.

---

# 55. Device API

Conceptual endpoints:

```text
POST /api/v1/devices/register
GET  /api/v1/devices
GET  /api/v1/devices/{device_id}
POST /api/v1/devices/{device_id}/revoke
```

Device registration must occur online before offline use.

---

# 56. Device Trust

The API must verify:

* Device UUID;
* Business;
* Branch;
* employee association;
* trust state;
* revocation state;
* offline authorization state.

A trusted device does not bypass employee permissions.

---

# 57. Synchronization API

Synchronization should have a dedicated API boundary.

Recommended conceptual endpoint:

```text
POST /api/v1/sync/batches
```

The request contains a batch of offline operations.

The server returns per-operation results.

---

# 58. Synchronization Request

Conceptually:

```text
SyncBatch
├── Batch UUID
├── Device UUID
├── Business UUID
├── Branch UUID
├── Client Metadata
└── Operations[]
```

Each operation contains:

```text
Transaction UUID
Operation Type
Entity UUID
Payload
Dependencies
Client Timestamp
```

The server validates all relevant fields.

---

# 59. Synchronization Response

A synchronization response should identify the result of each operation.

Possible statuses:

```text
SYNCED
DUPLICATE
REJECTED
CONFLICT
RETRY
```

The response should contain enough information for the device to update its durable queue.

---

# 60. Synchronization Idempotency

The server must recognize previously processed Transaction UUIDs.

If the same valid operation is submitted again:

```text
First Request
    ↓
Business Effect

Repeated Request
    ↓
Existing Result
```

The business effect must not be executed twice.

---

# 61. Synchronization Dependencies

The API must preserve dependency ordering.

Example:

```text
Transaction A: Create Order
Transaction B: Accept Order
Transaction C: Payment
```

The backend must not successfully process C if required dependencies do not exist.

---

# 62. Synchronization Conflict

A conflict response should include a Conflict UUID.

Example:

```text
{
  "status": "CONFLICT",
  "conflict_id": "...",
  "transaction_id": "...",
  "entity_id": "..."
}
```

Conflict resolution occurs through a separate authorized operation.

---

# 63. Conflict Resolution API

Conceptual endpoint:

```text
POST /api/v1/sync/conflicts/{conflict_id}/resolve
```

The request should include:

* resolution decision;
* reason;
* optional resolution data;
* idempotency identity.

The backend validates authorization and current conflict state.

---

# 64. Synchronization Security

Synchronization requests must validate:

* authentication;
* device trust;
* Business;
* Branch;
* Employee;
* permission;
* subscription bounds;
* offline authorization;
* transaction UUID;
* payload integrity;
* timestamp/clock rules.

The client must not be able to modify these security fields arbitrarily.

---

# 65. Idempotency API

State-changing API requests should support an idempotency identity.

The system uses UUID-based transaction identity.

Conceptually:

```text
POST /payments

Transaction UUID:
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

The exact transport header/body representation may be selected during implementation.

---

# 66. Idempotency Scope

Idempotency must be scoped to prevent accidental collisions.

Conceptually:

```text
Business
+
Operation Type
+
Transaction UUID
```

may form the logical uniqueness boundary.

The exact database key is an implementation detail.

---

# 67. Duplicate Requests

If a request is retried after a network failure and the operation already succeeded, the API should return the original result where possible.

The client should not receive an ambiguous:

```text
"Maybe successful"
```

state when the server can determine the original result.

---

# 68. HTTP Status Model

The API should use consistent HTTP status codes.

Examples:

```text
200 OK
201 Created
202 Accepted
204 No Content

400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Unprocessable Entity
429 Too Many Requests

500 Internal Server Error
502 Bad Gateway
503 Service Unavailable
```

Exact mapping should remain documented and stable.

---

# 69. Business Error Codes

HTTP status alone is not enough.

Responses should include stable machine-readable error codes.

Example:

```text
{
  "error": {
    "code": "INVENTORY_INSUFFICIENT",
    "message": "Insufficient stock.",
    "details": {}
  }
}
```

Error codes should remain stable even if human-readable messages change.

---

# 70. Error Categories

Recommended categories:

```text
AUTHENTICATION_REQUIRED
AUTHORIZATION_DENIED
SUBSCRIPTION_RESTRICTED
VALIDATION_FAILED
RESOURCE_NOT_FOUND
BUSINESS_RULE_VIOLATION
CONCURRENCY_CONFLICT
IDEMPOTENCY_CONFLICT
SYNC_CONFLICT
DEVICE_NOT_TRUSTED
OFFLINE_AUTHORIZATION_EXPIRED
INFRASTRUCTURE_ERROR
```

The exact final catalog belongs to API implementation documentation.

---

# 71. Error Response Structure

A standard error response may contain:

```text
Error
├── Code
├── Message
├── Details
├── Correlation ID
└── Retry Information where applicable
```

Sensitive internal details must not be exposed.

---

# 72. Validation Errors

Validation failures should identify the affected field where possible.

Example:

```text
{
  "error": {
    "code": "VALIDATION_FAILED",
    "fields": {
      "quantity": "Must be greater than zero."
    }
  }
}
```

The frontend can then display field-specific errors.

---

# 73. Conflict Errors

HTTP `409 Conflict` should be used for state conflicts where appropriate.

Examples:

* concurrent order modification;
* active Cash Session already exists;
* stale configuration version;
* synchronization conflict;
* duplicate state transition.

The response should explain the conflict category without exposing sensitive internals.

---

# 74. Rate Limiting

Rate limiting should protect:

* authentication;
* password/credential attempts;
* device registration;
* synchronization;
* report generation;
* exports;
* expensive APIs.

POS-critical operations should use carefully designed limits so legitimate operational traffic is not disrupted.

---

# 75. Request Size Limits

The API must enforce payload limits.

Large requests can cause:

* memory pressure;
* slow parsing;
* denial-of-service risk;
* database pressure.

Synchronization batches and exports should have explicit size/count limits.

---

# 76. Pagination

Collection endpoints must support pagination.

Example:

```text
GET /api/v1/orders?page=2&page_size=50
```

The exact pagination mechanism may use cursor-based pagination for large/high-volume collections.

---

# 77. Pagination Requirements

Pagination must provide:

* stable ordering;
* maximum page size;
* deterministic results;
* scope-aware filtering.

Audit and synchronization records should prefer pagination strategies suitable for large datasets.

---

# 78. Filtering

Filtering should use explicit query parameters.

Examples:

```text
GET /orders?status=ACCEPTED
GET /orders?branch_id=...
GET /payments?method=CASH
GET /audit-events?employee_id=...
```

Clients must not inject arbitrary SQL or backend query expressions.

---

# 79. Sorting

Sorting must use an allowlisted set of fields.

Example:

```text
?sort=created_at
```

The API must reject unsupported or unsafe sort expressions.

---

# 80. Date and Time

API timestamps should use a consistent machine-readable format.

Server timestamps are authoritative for:

* payment;
* cash;
* subscription;
* audit;
* synchronization;
* configuration activation;
* deletion lifecycle.

Client timestamps may be retained as metadata for offline operations.

---

# 81. Clock Anomaly Handling

Offline synchronization may include client timestamps.

The backend should detect suspicious:

* clock rollback;
* unrealistic future timestamps;
* repeated timestamp anomalies.

Clock anomalies should not silently rewrite server time.

---

# 82. Correlation ID

Each request should receive or generate a Correlation ID.

The ID should appear in:

* logs;
* relevant API errors;
* background processing context;
* operational tracing.

Correlation ID is not the same as Transaction UUID.

---

# 83. API Observability

The API should measure:

* request count;
* latency;
* error rate;
* status codes;
* endpoint usage;
* synchronization throughput;
* conflict rate;
* report generation;
* export jobs;
* rate-limit events.

Metrics should be aggregated without exposing sensitive data.

---

# 84. API Logging

API logs should contain useful technical metadata:

```text
Timestamp
Correlation ID
Business UUID
Branch UUID
Employee UUID
Device UUID
Endpoint
Method
Status
Duration
Error Code
```

Sensitive credentials must never be logged.

---

# 85. API Security Headers

The deployment should configure appropriate HTTP security controls.

Examples include:

* secure transport;
* content-type protections;
* origin policy;
* clickjacking protection;
* appropriate cache controls.

Exact header configuration belongs to Deployment/Security Architecture.

---

# 86. CORS

Cross-origin access must be explicitly configured.

The API should not use permissive wildcard configuration in production unless specifically justified.

Allowed origins should be controlled by deployment configuration.

---

# 87. File Download Security

Report and Excel downloads must be authorized.

A user must not be able to change:

```text
/report-version/{id}
```

and obtain another Business's file.

File access must revalidate:

* Business;
* Branch;
* permission;
* subscription/read-only policy;
* report ownership.

---

# 88. API and Historical Integrity

The API must not expose generic endpoints that allow destructive rewriting of historical records.

For example:

```text
PUT /payments/{id}
```

must not be used to silently rewrite completed payments.

Instead:

```text
POST /payments/{id}/revise
```

or another controlled correction operation should be used.

---

# 89. API and Audit

Important mutations should result in audit records.

Examples:

```text
Payment Created
Refund Created
Cash Session Closed
Cash Correction Created
Inventory Adjusted
Permission Changed
Employee Deactivated
Configuration Activated
Conflict Resolved
Device Revoked
```

Audit behavior belongs to backend application architecture, not frontend responsibility.

---

# 90. API and Notifications

API requests should not synchronously depend on notification delivery.

For example:

```text
POST /cash-sessions/{id}/close
```

should not fail merely because an Owner notification cannot currently be delivered.

The core operation commits first.

---

# 91. API and Background Jobs

Expensive operations should return a job/resource reference.

Example:

```text
POST /reports
```

may return:

```text
202 Accepted
{
  "report_job_id": "..."
}
```

The client can then query the job/report state.

---

# 92. API and Caching

Safe GET responses may be cached where appropriate.

However, cache keys must include relevant context such as:

```text
Business
Branch
Resource
Configuration Version
Permission Context where necessary
```

Transactional mutations must not depend on stale cached data.

---

# 93. API Contract Stability

Public API contracts should change deliberately.

Each contract should define:

* request schema;
* response schema;
* error schema;
* authorization requirements;
* Business/Branch scope;
* idempotency behavior;
* pagination behavior;
* side effects.

---

# 94. API Documentation

The API should be documented using a machine-readable contract such as OpenAPI.

Documentation should include:

* endpoints;
* methods;
* parameters;
* request schemas;
* response schemas;
* error codes;
* authentication;
* authorization;
* examples;
* version.

Generated API documentation must not replace domain/business documentation.

---

# 95. API Testing

API testing should include:

### Contract Tests

Validate request and response schemas.

### Authorization Tests

Verify permission and scope boundaries.

### Integration Tests

Verify database and application behavior.

### Idempotency Tests

Verify duplicate requests.

### Concurrency Tests

Verify simultaneous operations.

### Synchronization Tests

Verify offline operations and conflicts.

### Security Tests

Verify tenant isolation and authentication boundaries.

---

# 96. Critical API Test Scenarios

At minimum:

```text
Business Isolation
Branch Isolation
Permission Denial
Subscription Restriction
Order Acceptance
Duplicate Order Request
Duplicate Payment Request
Concurrent Inventory Sale
Concurrent Cash Session Open
Cash Handover
Refund
Overpayment
Recipe Approval
Configuration Version Conflict
Offline Sync
Duplicate Sync
Sync Conflict
Conflict Resolution
Report Generation
Excel Export Authorization
Device Revocation
Subscription Expiry
```

---

# 97. API Anti-Patterns

The following patterns are prohibited:

### Direct Database API

```text
API
 ↓
SQL Table
```

### Generic Update Everything

```text
PUT /entity/{id}
{
  "any_field": "anything"
}
```

for sensitive domain entities.

### Client Authorization

```text
Client says:
"I have permission"
```

### Client-Provided Business Authority

```text
business_id = arbitrary user input
```

without server validation.

### Silent Conflict Resolution

```text
Conflict
 ↓
Overwrite
```

### Non-Idempotent Payment Retry

```text
Retry
 ↓
Second Payment
```

### Historical Mutation

```text
Update Original Payment
```

### Unbounded Query

```text
GET /orders
```

returning unlimited records.

---

# 98. Standard API Request Lifecycle

A standard authenticated mutation follows:

```text
HTTP Request
     ↓
Routing
     ↓
Request Validation
     ↓
Authentication
     ↓
Execution Context
     ↓
Business Scope
     ↓
Branch Scope
     ↓
Permission
     ↓
Subscription
     ↓
Device Trust
     ↓
Idempotency
     ↓
Application Command
     ↓
Domain Operation
     ↓
Transaction
     ↓
Audit / Outbox
     ↓
Response
```

The exact order may vary where technically necessary.

---

# 99. Standard API Query Lifecycle

```text
HTTP Request
     ↓
Routing
     ↓
Request Validation
     ↓
Authentication
     ↓
Business Scope
     ↓
Branch Scope
     ↓
Permission
     ↓
Query Handler
     ↓
Read Model / Repository
     ↓
Response
```

---

# 100. Offline Sync Lifecycle

```text
Offline Device
      ↓
POST /sync/batches
      ↓
Authenticate Device
      ↓
Validate Offline Authorization
      ↓
Validate Business / Branch
      ↓
Validate Employee / Permission
      ↓
Validate Transaction UUID
      ↓
Validate Dependencies
      ↓
Execute or Detect Conflict
      ↓
Persist Result
      ↓
Return Per-Operation Result
```

---

# 101. API Architecture Completion Criteria

The API architecture is considered complete when:

* API versioning is defined;
* resource naming is consistent;
* Business isolation is enforced;
* Branch isolation is enforced;
* authentication is separated from authorization;
* permissions are server-side;
* subscription entitlement is server-side;
* state-changing operations are idempotent;
* critical commands have explicit endpoints;
* historical records cannot be silently rewritten;
* errors have stable machine-readable codes;
* pagination is enforced;
* filtering and sorting are controlled;
* synchronization has a dedicated API;
* conflicts are explicit;
* report/export processing is controlled;
* file access is authorized;
* rate limiting exists;
* API observability exists;
* API contracts are documented;
* critical API workflows are tested.

---

# 102. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`

### Domain Analysis

* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### Architecture

* `docs/04_Architecture/01_System_Architecture.md`
* `docs/04_Architecture/02_Application_Layer_Architecture.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/04_Backend_Architecture.md`
* `docs/04_Architecture/05_Frontend_Architecture.md`

---

# 103. Next Architecture Document

The next architecture document is:

`docs/04_Architecture/07_Database_Architecture.md`

It will define:

* database architecture;
* schema organization;
* tenant isolation;
* branch isolation;
* aggregate persistence;
* table ownership;
* relationships;
* indexes;
* constraints;
* transaction boundaries;
* concurrency control;
* historical data;
* snapshots;
* audit persistence;
* synchronization persistence;
* migrations;
* backup considerations;
* database performance.

