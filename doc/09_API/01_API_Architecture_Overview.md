# API Architecture Overview

**Document ID:** API-01
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This document defines the overall API architecture for FastFood ERP.

The API is the controlled communication boundary between ERP clients and the backend application.

The API provides access to authorized application capabilities for:

* Web frontend;
* POS clients;
* trusted devices;
* offline synchronization;
* background processes where API access is required;
* future external integrations.

The API must provide a stable and predictable contract without exposing:

* database implementation details;
* internal domain objects;
* repository implementation;
* infrastructure internals;
* security secrets;
* unrestricted business operations.

The API is not a direct database interface.

The API must expose business capabilities through controlled application use cases.

---

# 2. API Architectural Position

The API is positioned between external clients and the Backend Application layer.

```text
Client
   ↓
HTTP / API
   ↓
Request Context
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

The following architecture is prohibited:

```text
Client
   ↓
API
   ↓
Direct Database Mutation
```

The API is therefore an interface boundary, not the location where core business rules are implemented.

---

# 3. API Architecture Goals

The API architecture has the following goals:

1. Provide a stable client-server contract.
2. Protect Business and Branch isolation.
3. Preserve authorization boundaries.
4. Represent business operations explicitly.
5. Support reliable POS operation.
6. Support trusted offline synchronization.
7. Prevent duplicate financial and operational effects.
8. Preserve historical transaction integrity.
9. Support asynchronous operations.
10. Provide predictable error handling.
11. Support backward-compatible evolution.
12. Provide machine-readable API documentation.
13. Support automated contract testing.
14. Provide measurable performance and availability.
15. Support future integrations without compromising the core ERP.
16. Prevent API complexity from making normal POS workflows unnecessarily slow.

---

# 4. API Core Principles

## 4.1. API Is Not the Business Logic Layer

The API layer handles communication concerns.

Core business rules belong to the Application and Domain layers.

For example:

```text
POST /orders/{order_id}/pay
        ↓
API
        ↓
PayOrderUseCase
        ↓
Domain Validation
        ↓
Payment
        ↓
Order State Change
        ↓
Audit / Outbox
        ↓
Commit
```

The endpoint itself must not implement the payment rules.

---

## 4.2. Server Is Authoritative

The client is never authoritative for protected ERP state.

The server remains authoritative for:

* Business state;
* Branch state;
* Employee state;
* permissions;
* subscription state;
* Product state;
* Menu configuration;
* pricing;
* inventory;
* Orders;
* Payments;
* Cash Sessions;
* Payroll;
* Reports;
* Audit history;
* configuration versions.

Client-provided values are inputs to validation, not automatic truth.

---

## 4.3. Authorization Is Server-Side

The API must never rely on frontend checks as the security boundary.

The backend validates:

* authenticated actor;
* Employee status;
* Business scope;
* Branch scope;
* permissions;
* subscription entitlement;
* device restrictions;
* resource ownership;
* operational rules.

The client may hide unauthorized functionality in the UI, but the API must enforce the same restriction independently.

---

## 4.4. Business and Branch Isolation

Every protected request must execute within an authoritative security context.

Conceptually:

```text
Authenticated Actor
       ↓
Business Scope
       ↓
Branch Scope
       ↓
Permission
       ↓
Resource Scope
       ↓
Operation
```

A client must never be able to access another Business or Branch simply by changing:

```text
business_id
branch_id
employee_id
device_id
resource_id
```

All such identifiers are untrusted until validated by the server.

---

## 4.5. Explicit Business Commands

Simple resource operations may use normal HTTP methods.

Business operations with important state transitions should use explicit command endpoints.

Examples:

```text
POST /orders/{id}/accept
POST /orders/{id}/pay
POST /orders/{id}/refund
POST /cash-sessions/{id}/close
POST /recipes/{id}/approve
POST /handover/{id}/accept
```

This makes the following concerns explicit:

* authorization;
* validation;
* transaction boundary;
* idempotency;
* concurrency;
* audit;
* business state transition.

---

## 4.6. Historical Integrity

The API must preserve historical transaction information.

Current configuration must not reinterpret historical transactions.

For example:

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

API operations must therefore work with authoritative snapshots and historical versions where required.

---

## 4.7. Idempotent State-Changing Operations

Retryable state-changing operations must support idempotency.

This is particularly important for:

* payments;
* refunds;
* inventory transactions;
* Orders;
* cash operations;
* synchronization;
* configuration changes.

A repeated request must not create duplicate business effects.

---

## 4.8. Offline Compatibility

The API must support the project's offline-first operational model.

Offline-capable trusted devices may create authorized local operations.

When connectivity returns:

```text
Local Operation
      ↓
Sync Queue
      ↓
Synchronization API
      ↓
Server Validation
      ↓
Conflict / Acceptance
      ↓
Authoritative Server State
```

The API must not assume that every request originated from an online interactive session.

---

## 4.9. Core ERP Independence From AI

AI capabilities are exposed through controlled API boundaries.

However, the API must never make core ERP functionality dependent on AI availability.

The following operations must continue to function when AI is unavailable:

* POS;
* Order creation;
* Payment;
* Cash Session;
* Inventory transaction;
* Authentication;
* synchronization;
* core ERP state management.

AI is an intelligence capability, not a prerequisite for core transaction processing.

---

# 5. API Architectural Layers

The API architecture consists of several logical layers.

```text
┌─────────────────────────────────────┐
│              Clients                │
│ Web / POS / Trusted Devices / Sync  │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│           HTTP / API Layer           │
│ Routing / Parsing / Serialization    │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│          Security Context            │
│ Auth / Business / Branch / Device   │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         Request Validation           │
│ Schema / Format / Limits / Enums     │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         Application Layer            │
│ Use Cases / Transactions / Commands  │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│            Domain Layer              │
│ Rules / Invariants / State Changes   │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│       Repository / Infrastructure    │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│           PostgreSQL                 │
└─────────────────────────────────────┘
```

Each layer has a separate responsibility.

---

# 6. API Layer Responsibilities

The API layer is responsible for:

* HTTP routing;
* request parsing;
* schema validation;
* authentication integration;
* authorization integration;
* request context creation;
* response serialization;
* HTTP status mapping;
* error formatting;
* pagination;
* API-level rate limiting;
* idempotency header extraction;
* correlation identifiers;
* API documentation integration.

The API layer must not become a second Domain layer.

---

# 7. Application Layer Responsibilities

The Application layer owns use-case orchestration.

It is responsible for:

* use-case execution;
* transaction boundaries;
* authorization orchestration;
* Business/Branch validation;
* Domain invocation;
* repository coordination;
* idempotency;
* audit creation;
* outbox creation;
* synchronization processing.

Example:

```text
API
 ↓
AcceptOrderUseCase
 ↓
Validate Order
 ↓
Validate Inventory
 ↓
Apply Domain Rules
 ↓
Create Inventory Transactions
 ↓
Change Order State
 ↓
Create Audit / Outbox
 ↓
Commit
```

The API route must not reproduce this workflow.

---

# 8. Domain Layer Responsibilities

The Domain layer owns authoritative business behavior and invariants.

Examples include:

* Order lifecycle;
* payment rules;
* refund rules;
* pricing;
* discounts;
* markup;
* inventory rules;
* Recipe requirements;
* Set rules;
* Cash Session rules;
* payroll rules;
* configuration version rules.

The Domain layer must remain independent from HTTP.

---

# 9. API Contract Boundary

The API contract is a public architectural boundary.

The contract defines:

* endpoint;
* HTTP method;
* request schema;
* response schema;
* authentication requirement;
* authorization requirement;
* Business/Branch scope;
* status codes;
* error codes;
* idempotency behavior;
* concurrency behavior;
* pagination;
* retry semantics.

Internal implementation changes must not automatically become API contract changes.

---

# 10. API Versioning

The initial API versioning strategy is URI-based.

```text
/api/v1
```

Examples:

```text
/api/v1/orders
/api/v1/products
/api/v1/employees
/api/v1/reports
```

A new major version may be introduced when an incompatible public contract change is required.

Example:

```text
/api/v2
```

API versioning does not mean that every internal change requires a new version.

---

# 11. Backward Compatibility

Compatible API changes should generally include:

* adding optional response fields;
* adding optional request fields;
* adding new endpoints;
* adding supported filters;
* adding non-breaking enum values where clients can safely ignore them.

Breaking changes include:

* removing required fields;
* changing field types;
* changing semantic meaning;
* removing endpoints;
* changing authentication requirements incompatibly;
* changing error semantics incompatibly.

Breaking changes require an explicit migration strategy.

---

# 12. API Resource Model

The API represents major ERP concepts as resources.

Primary resources include:

```text
Business
Branch
Employee
Device
Product
Category
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
File
Configuration
Subscription
Synchronization Operation
```

Resource representation must remain independent from the underlying database schema.

A database table does not automatically become an API resource.

---

# 13. Resource Identity

Resources use stable UUID-based identifiers where appropriate.

Example:

```json
{
  "id": "018f7e7c-..."
}
```

UUIDs provide stable resource identity but do not provide authorization.

The server must still validate:

```text
UUID
 ↓
Resource
 ↓
Business
 ↓
Branch
 ↓
Authorization
```

UUIDs must never be treated as a substitute for access control.

---

# 14. API Context

Requests may require contextual information such as:

```text
Business
Branch
Employee
Device
Cash Session
Operation
Request
```

A conceptual request context is:

```text
Request
 ├── Request ID
 ├── Actor
 ├── Business
 ├── Branch
 ├── Device
 ├── Cash Session
 └── Operation
```

Only applicable context should be attached to a request.

The API must not require meaningless context fields merely for consistency.

---

# 15. Request Context Is Not Client Authority

Clients may provide context identifiers.

For example:

```http
X-Business-ID: <uuid>
X-Branch-ID: <uuid>
X-Device-ID: <uuid>
```

These values are context hints.

They do not automatically establish authority.

The server must independently verify them.

---

# 16. Authentication and Authorization Boundary

Authentication answers:

> Who is making the request?

Authorization answers:

> What may this actor do in this context?

The API architecture keeps these responsibilities separate.

```text
Authentication
      ↓
Actor Identity
      ↓
Business Scope
      ↓
Branch Scope
      ↓
Permission
      ↓
Subscription
      ↓
Resource
      ↓
Operation
```

Failure at any mandatory security boundary must prevent unauthorized execution.

---

# 17. Subscription Entitlement

Subscription state is part of API authorization for modifying operations.

When a Business enters read-only state:

```text
Read Operations
       ↓
Allowed
```

```text
Modifying Operations
       ↓
Blocked
```

Historical data and permitted exports remain accessible according to the subscription lifecycle rules.

Offline synchronization must not bypass subscription restrictions.

---

# 18. API Operation Categories

API operations are divided into several categories.

### 18.1. Read Operations

Examples:

```text
GET /products
GET /orders/{id}
GET /inventory
GET /reports/{id}
```

### 18.2. Resource Creation

Examples:

```text
POST /orders
POST /products
POST /employees
```

### 18.3. Resource Update

Examples:

```text
PATCH /products/{id}
PATCH /employees/{id}
```

### 18.4. Business Commands

Examples:

```text
POST /orders/{id}/accept
POST /orders/{id}/pay
POST /orders/{id}/refund
POST /cash-sessions/{id}/close
POST /recipes/{id}/approve
```

### 18.5. Asynchronous Operations

Examples:

```text
POST /reports
POST /exports
POST /sync/batches
```

The operation category determines its expected contract behavior.

---

# 19. Financial API Boundary

Financial operations require stronger correctness guarantees.

Examples:

* Payment;
* Refund;
* Cash Session;
* Cash correction;
* financial adjustments.

These operations must provide:

* authoritative server calculation;
* idempotency;
* transaction boundaries;
* concurrency protection;
* historical integrity;
* auditability.

Client-provided financial totals are never authoritative.

---

# 20. Inventory API Boundary

Inventory operations must preserve inventory integrity.

The API must not allow clients to arbitrarily replace authoritative stock values.

Inventory commands must operate through business rules.

Examples:

```text
Receipt
Exit
Adjustment
Count
Transfer
```

The server validates:

* Product;
* Branch;
* Warehouse;
* quantity;
* permissions;
* inventory state;
* Recipe requirements;
* business rules.

Negative stock remains prohibited.

---

# 21. Order API Boundary

Order APIs must preserve the Order lifecycle.

The API must distinguish between:

```text
Resource modification
```

and:

```text
Business state transition
```

For example:

```text
PATCH /orders/{id}
```

must not silently perform the equivalent of:

```text
Accept
Pay
Refund
Cancel
```

unless the operation is explicitly represented and authorized.

---

# 22. Configuration API Boundary

Configuration APIs cover configuration that affects operational behavior.

Examples:

* menu;
* pricing;
* Branch overrides;
* workflow configuration;
* operational settings.

Important configuration changes require:

* permission;
* version validation;
* concurrency control;
* effective boundary;
* audit;
* historical preservation.

Stale configuration updates must be rejected rather than silently overwriting newer state.

---

# 23. Synchronization API Boundary

Offline synchronization is a specialized API boundary.

It must support:

* operation UUID;
* device identity;
* employee identity;
* Business;
* Branch;
* operation type;
* payload;
* client timestamp;
* server validation;
* conflict detection;
* idempotency;
* partial success;
* retryability.

Conceptual flow:

```text
Offline Device
      ↓
Sync Batch
      ↓
Operation Validation
      ↓
Authorization
      ↓
Business Rules
      ↓
Idempotency
      ↓
Conflict Detection
      ↓
Commit
      ↓
Operation Result
```

The server remains authoritative after synchronization.

---

# 24. Asynchronous API Boundary

Long-running operations must not unnecessarily occupy interactive HTTP requests.

Suitable operations include:

* large reports;
* XLSX generation;
* large exports;
* background cleanup;
* large synchronization workloads;
* other explicitly asynchronous processes.

Typical pattern:

```text
POST /reports
      ↓
202 Accepted
      ↓
Job ID
      ↓
GET /jobs/{id}
```

The job state is authoritative on the server.

---

# 25. API Error Architecture

Errors must have stable machine-readable codes.

Example:

```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "The requested quantity is not available.",
    "request_id": "01J...",
    "details": {}
  }
}
```

Clients should primarily depend on:

```text
error.code
```

rather than the human-readable message.

Error responses must not expose:

* stack traces;
* SQL errors;
* internal filesystem paths;
* credentials;
* secrets;
* internal security implementation details.

---

# 26. API Pagination and Query Boundaries

Large datasets must use bounded pagination.

The preferred approach is cursor-based pagination.

Example:

```text
GET /api/v1/orders?limit=50&cursor=...
```

Initial target:

```text
Default page size: 50
Maximum page size: 100
```

The exact limit may be configurable.

List endpoints must use deterministic ordering.

---

# 27. API Caching Boundary

Only suitable read-oriented operations may use API caching.

Potential candidates include:

* menu;
* Product reference data;
* configuration;
* permission-derived read data;
* short-lived subscription state.

The following must never rely on API cache as authoritative state:

* payment;
* inventory deduction;
* cash state;
* Order financial state;
* audit history.

Cache invalidation must not weaken authorization.

---

# 28. API Security Boundary

The API must enforce:

* HTTPS in production;
* explicit CORS;
* CSRF protection where cookie authentication requires it;
* security headers;
* request size limits;
* rate limiting;
* sensitive-data filtering;
* authentication protection;
* authorization checks;
* enumeration protection.

Security controls must fail closed when authoritative security state cannot be established.

---

# 29. API Integration Boundary

Future external integrations must not bypass the internal application architecture.

Conceptually:

```text
External System
      ↓
Integration API / Adapter
      ↓
Application Use Case
      ↓
Domain Rules
      ↓
ERP State
```

External systems must not receive direct database access.

External provider failures must not corrupt authoritative ERP state.

---

# 30. API and Frontend Boundary

The frontend communicates with the ERP through the API.

```text
Frontend
    ↓
API
    ↓
Application
    ↓
Domain
```

The frontend must not:

* connect directly to PostgreSQL;
* call internal repositories;
* bypass backend authorization;
* directly mutate authoritative ERP state;
* directly depend on AI providers.

Frontend state is a client-side representation of server-authoritative state.

---

# 31. API and AI Boundary

AI functionality follows the same API security model as the rest of the ERP.

```text
Frontend
   ↓
API
   ↓
Authorization
   ↓
AI Application Use Case
   ↓
AI Runtime
```

The AI model does not receive unrestricted API or database authority.

AI results must pass through application-level validation and governance where required.

AI recommendations do not automatically become ERP transactions.

---

# 32. API and Database Boundary

The API does not expose database structure.

The following are internal implementation details:

* table names;
* database joins;
* repository implementation;
* database connection details;
* internal SQL expressions;
* migration structure.

API resources and contracts should be designed around business capabilities rather than database tables.

---

# 33. API Observability

API observability must support operational diagnosis without exposing sensitive data.

Core metrics include:

* request count;
* response status;
* latency;
* p50;
* p95;
* p99;
* error rate;
* timeout rate;
* authentication failures;
* authorization failures;
* scope denials;
* idempotency conflicts;
* synchronization conflicts;
* rate limiting.

Important requests should be traceable using request and operation identifiers.

---

# 34. API Performance Targets

Initial API performance targets are:

| Operation                        |       Target |
| -------------------------------- | -----------: |
| Ordinary authenticated API       | p95 ≤ 300 ms |
| Ordinary authenticated API       | p99 ≤ 800 ms |
| Core POS command                 | p95 ≤ 500 ms |
| Authorization overhead           | p95 ≤ 100 ms |
| Cached authorization lookup      |  p95 ≤ 20 ms |
| Business/Branch scope validation |  p95 ≤ 50 ms |
| Idempotency lookup               |  p95 ≤ 50 ms |
| Normal synchronization batch     |    p95 ≤ 1 s |
| Normal indexed database query    | p95 ≤ 100 ms |

These targets are architectural targets rather than guarantees for every endpoint.

External provider latency may be excluded from core internal API SLOs where explicitly documented.

---

# 35. API Availability Target

Initial API availability target:

**≥ 99.9% monthly**

Critical correctness boundaries require stronger guarantees.

Target zero-tolerance conditions include:

* cross-Business data leakage;
* unauthorized Branch access;
* duplicate financial execution;
* unauthorized financial state changes;
* invalid approval execution.

These are release-blocking correctness and security requirements.

---

# 36. API Retry Architecture

Retry behavior must be explicit.

Retryable conditions may include:

```text
Network failure
503 Service Unavailable
Temporary synchronization failure
Transient infrastructure failure
```

Non-automatic retry conditions include:

```text
INSUFFICIENT_STOCK
ACCESS_DENIED
INVALID_REQUEST
BUSINESS_RULE_VIOLATION
ORDER_ALREADY_PAID
```

State-changing retries must use idempotency where applicable.

Clients must not blindly retry all failed requests.

---

# 37. API Contract Testing

The API contract must be automatically testable.

Contract tests should validate:

* endpoint;
* HTTP method;
* request schema;
* response schema;
* HTTP status;
* error code;
* authentication requirement;
* authorization requirement;
* Business/Branch scope;
* pagination;
* idempotency;
* concurrency behavior where applicable.

Contract tests must run in CI.

---

# 38. OpenAPI

The API must have a machine-readable OpenAPI specification.

The specification should describe:

* endpoints;
* parameters;
* request schemas;
* response schemas;
* authentication;
* authorization requirements where representable;
* errors;
* pagination;
* enums;
* deprecation status.

OpenAPI is a controlled contract artifact.

Implementation and specification must not silently diverge.

---

# 39. API Change Management

An API change must be evaluated against:

1. Business requirements;
2. System Analysis;
3. Domain behavior;
4. Application use cases;
5. Database impact;
6. Frontend impact;
7. offline client impact;
8. synchronization compatibility;
9. security;
10. backward compatibility;
11. testing;
12. documentation.

API changes must not be treated as isolated endpoint changes.

---

# 40. API Deprecation

Deprecated endpoints must have a migration path.

A deprecation decision should define:

* replacement endpoint;
* deprecation date;
* expected removal date;
* affected clients;
* migration requirements.

An endpoint must not be silently removed when active clients depend on it.

---

# 41. API Architecture and POS Performance

POS is a high-priority API consumer.

The API architecture must avoid unnecessary overhead in the POS critical path.

The following must be optimized:

* authentication context resolution;
* permission resolution;
* Business/Branch scope validation;
* pricing lookup;
* inventory validation;
* idempotency lookup;
* database queries;
* serialization.

Heavy operations should be moved out of the synchronous POS path.

Examples:

```text
Report generation
XLSX export
Large analytics
Heavy AI processing
Large file processing
```

must normally use asynchronous processing where appropriate.

---

# 42. API Failure Isolation

Failure in secondary functionality must not unnecessarily rollback successful core ERP transactions.

Examples:

```text
Order committed
    ↓
Printer failure
```

must not automatically rollback the Order.

Similarly:

```text
Order committed
    ↓
Notification failure
```

must not rollback the committed Order.

The same principle applies to other secondary asynchronous operations.

---

# 43. API Architectural Boundaries

The API architecture establishes the following boundaries:

```text
API
 │
 ├── HTTP Contract
 │
 ├── Security Context
 │
 ├── Request Validation
 │
 └── Response Contract
        │
        ▼
Application
 │
 ├── Use Cases
 ├── Transactions
 ├── Authorization Orchestration
 ├── Idempotency
 ├── Audit
 └── Outbox
        │
        ▼
Domain
 │
 ├── Business Rules
 └── Invariants
        │
        ▼
Infrastructure
 │
 ├── Repository
 ├── Storage
 ├── External Providers
 └── PostgreSQL
```

Each layer must maintain its responsibility.

---

# 44. Prohibited API Patterns

The following patterns are prohibited:

* direct API-to-database mutation;
* trusting client Business ID;
* trusting client Branch ID;
* frontend-only authorization;
* client-controlled financial totals;
* duplicate payment without idempotency;
* generic CRUD bypassing business rules;
* unbounded list responses;
* unbounded synchronization batches;
* silent stale configuration overwrite;
* API cache as financial authority;
* unrestricted LLM/database access;
* production stack traces;
* sensitive secrets in responses;
* sensitive credentials in logs;
* unrestricted CORS for authenticated production APIs;
* external systems directly modifying PostgreSQL.

---

# 45. Core API Invariants

The following invariants apply to the API architecture:

1. The API is a controlled application boundary.
2. The API does not directly implement core Domain business logic.
3. The API does not directly mutate PostgreSQL.
4. Protected endpoints require authentication.
5. Protected operations require authorization.
6. Business scope is always server-validated.
7. Branch scope is always server-validated.
8. Client-provided UUIDs never grant authority.
9. Subscription restrictions are enforced server-side.
10. Read-only Businesses cannot perform unauthorized modifying operations.
11. Important state-changing operations support idempotency where required.
12. Duplicate idempotent requests do not duplicate business effects.
13. Conflicting idempotency-key reuse is rejected.
14. Historical financial state cannot be reinterpreted using current configuration.
15. Client-provided financial totals are never authoritative.
16. Server-side pricing is authoritative.
17. Server-side inventory is authoritative.
18. Server-side payment state is authoritative.
19. Configuration concurrency must prevent silent stale overwrites.
20. Offline synchronization has a dedicated API contract.
21. Synchronization operations are individually identifiable.
22. Synchronization retries cannot duplicate business effects.
23. Server state remains authoritative after synchronization.
24. API list responses are bounded.
25. API sorting is restricted to supported fields.
26. Client-controlled SQL expressions are never accepted.
27. Long-running operations use asynchronous processing where appropriate.
28. API timeouts are bounded.
29. External dependency failure cannot block requests indefinitely.
30. Core POS operation must not depend on AI availability.
31. Printer failure must not rollback committed core ERP state.
32. Notification failure must not rollback committed core ERP state.
33. API errors use stable machine-readable codes.
34. API errors do not expose sensitive implementation details.
35. Production stack traces are not exposed.
36. Sensitive credentials are never logged.
37. Production API traffic uses protected transport.
38. Production CORS configuration is explicit.
39. Cookie-based authentication requires appropriate CSRF protection.
40. Rate limiting must not unnecessarily disrupt normal POS operation.
41. API contracts are automatically tested.
42. OpenAPI must represent the implemented public contract.
43. Breaking API changes require explicit versioning or migration.
44. Deprecated endpoints require a migration path.
45. API resources do not expose database implementation details.
46. Frontend does not bypass the API.
47. External integrations do not bypass the Application layer.
48. AI does not bypass API authorization.
49. API caching is never authoritative for financial state.
50. ETag or conditional requests never replace authorization.
51. Business isolation is a release-blocking security requirement.
52. Branch isolation is a release-blocking security requirement.
53. Duplicate financial prevention is a release-blocking correctness requirement.
54. Historical integrity is a release-blocking requirement.
55. API performance must remain within defined SLO targets.
56. API observability must not create uncontrolled high-cardinality metrics.
57. Security failures must fail closed.
58. API changes must consider offline clients.
59. API changes must consider synchronization compatibility.
60. API terminology must remain consistent with Domain and Database architecture.
61. API contracts must remain independent from database table structure.
62. Core ERP operation must remain available when secondary services fail.
63. API architecture must preserve the modular monolith boundary.
64. API architecture must support future external integrations without exposing internal implementation.
65. API architecture must preserve the simplicity and speed of daily POS operations.

---

# 46. Relationship With Other Architecture Sections

### Backend Architecture

`docs/04_Architecture/06_Backend/`

The Backend Architecture defines:

* Application layer;
* Domain layer;
* Repository layer;
* transactions;
* authentication;
* authorization;
* background processing;
* security;
* observability.

This API section defines the external contract exposed by those capabilities.

### Frontend Architecture

`docs/04_Architecture/07_Frontend/`

Frontend clients consume the API and must follow the API contract.

### AI Architecture

`docs/04_Architecture/08_AI/`

AI capabilities are exposed through controlled Backend/API boundaries.

### Database Architecture

`docs/04_Architecture/05_Database/`

Database remains an internal authoritative persistence layer and is never directly exposed through the API.

### Security Architecture

`docs/04_Architecture/11_Security/`

API security controls must follow the centralized ERP security model.

### Testing Architecture

`docs/04_Architecture/12_Testing/`

API contract, integration, security, concurrency, synchronization and performance tests must follow the testing architecture.

### Operations Architecture

`docs/04_Architecture/14_Operations/`

API monitoring, incident handling, deployment and recovery follow operational architecture.

---

# 47. Recommended API Section Reading Order

The API Architecture section should be read in the following order:

```text
01 Overview
      ↓
02 Design Principles
      ↓
03 Request Lifecycle
      ↓
04 Versioning
      ↓
05 Resource Model
      ↓
06 Authentication
      ↓
07 Authorization
      ↓
08 Contracts
      ↓
09 Errors
      ↓
10 Idempotency / Concurrency
      ↓
11 Query / Pagination
      ↓
12 CRUD / Commands
      ↓
13–18 Business API Contracts
      ↓
19 Synchronization
      ↓
20 Async / Batch
      ↓
21 Security
      ↓
22 External Integration
      ↓
23 OpenAPI / Contract Testing
      ↓
24 Performance / Observability / SLO
```

---

# 48. API Architecture Status

**Architecture Section:** API

**Current Document:** `01_API_Architecture_Overview.md`

**Document Status:** Proposed

**Version:** 1.0

**API Architecture Boundary:** Defined

**Core API Principles:** Defined

**API Layer Responsibilities:** Defined

**Business/API Boundary:** Defined

**Security Boundary:** Defined

**Offline Synchronization Boundary:** Defined

**AI/API Boundary:** Defined

**Performance Direction:** Defined

**Detailed Endpoint Contracts:** Deferred to subsequent API documents.

---

# 49. Final Principle

FastFood ERP API architecture must provide a stable communication boundary without becoming a second business-logic layer.

The API:

```text
Authenticates
    ↓
Authorizes
    ↓
Validates
    ↓
Routes
    ↓
Invokes
    ↓
Serializes
    ↓
Observes
```

The Application and Domain layers:

```text
Orchestrate
    ↓
Validate Business Rules
    ↓
Execute Transactions
    ↓
Preserve Invariants
    ↓
Persist Authoritative State
```

The central architectural principle is:

> **The API exposes capabilities; the Application executes use cases; the Domain enforces business rules; the Database persists authoritative state.**

The API must remain secure, versionable, testable, observable and performant while preserving Business/Branch isolation, offline continuity, financial correctness and historical integrity.

