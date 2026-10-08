# Backend Project Structure

**Document ID:** BE-02
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/06_Backend/README.md`

---

## 1. Purpose

This document defines the recommended source-code structure for the FastFood ERP backend.

The structure must:

* reflect the accepted backend architecture;
* keep domain boundaries clear;
* separate business logic from infrastructure;
* support independent testing;
* prevent uncontrolled dependencies;
* remain understandable for human developers and AI coding agents;
* support future growth without premature microservice separation.

The structure is designed for the initial **modular monolith** architecture.

---

# 2. Structural Principle

The backend source tree should be organized around:

1. Application boundaries;
2. Domain ownership;
3. Infrastructure boundaries;
4. API/transport boundaries;
5. Cross-cutting technical concerns.

The project must not become a collection of unrelated CRUD files.

The structure should make it obvious:

> Which module owns a business rule, where a use case starts, where persistence occurs, and which layer is allowed to depend on another layer.

---

# 3. Recommended Backend Root

The initial backend structure is:

```text
backend/
├── app/
├── migrations/
├── tests/
├── scripts/
├── configuration/
├── pyproject.toml
└── README.md
```

The exact repository root may differ, but the logical separation must remain.

---

# 4. Application Source Tree

The primary application source tree is:

```text
backend/
└── app/
    ├── api/
    ├── application/
    ├── domain/
    ├── infrastructure/
    ├── security/
    ├── background/
    ├── synchronization/
    ├── reporting/
    ├── shared/
    └── main.py
```

Each top-level package has a defined responsibility.

---

# 5. API Layer

```text
app/
└── api/
    ├── routes/
    ├── schemas/
    ├── dependencies/
    ├── errors/
    └── __init__.py
```

## 5.1. Routes

Contains HTTP endpoint definitions.

Example:

```text
api/routes/
├── auth.py
├── businesses.py
├── branches.py
├── employees.py
├── products.py
├── recipes.py
├── inventory.py
├── menu.py
├── orders.py
├── payments.py
├── cash.py
├── reports.py
├── notifications.py
└── synchronization.py
```

Routes should remain thin.

They should:

1. receive the request;
2. validate transport data;
3. obtain request context;
4. invoke an application use case;
5. map the result to an API response.

Routes must not implement complex business rules.

---

# 6. API Schemas

```text
app/api/schemas/
├── auth.py
├── business.py
├── branch.py
├── employee.py
├── product.py
├── recipe.py
├── inventory.py
├── menu.py
├── order.py
├── payment.py
├── cash.py
├── report.py
└── synchronization.py
```

Schemas represent transport-level input/output.

They are not automatically domain entities.

For example:

```text
API OrderRequest
       ≠
Domain Order
       ≠
Database OrderModel
```

This separation prevents transport concerns from leaking into the domain.

---

# 7. API Dependencies

```text
app/api/dependencies/
├── authentication.py
├── authorization.py
├── business_context.py
├── branch_context.py
├── device_context.py
└── transaction.py
```

These components may provide common request-level dependencies.

Examples:

* authenticated employee;
* Business context;
* Branch context;
* trusted device context;
* authorization context.

They must not replace the Application Layer.

---

# 8. Application Layer

```text
app/
└── application/
    ├── business/
    ├── identity/
    ├── subscription/
    ├── devices/
    ├── products/
    ├── recipes/
    ├── inventory/
    ├── menu/
    ├── orders/
    ├── tables/
    ├── payments/
    ├── cash/
    ├── handover/
    ├── attendance/
    ├── payroll/
    ├── notifications/
    ├── audit/
    ├── reports/
    ├── synchronization/
    ├── configuration/
    └── lifecycle/
```

Each application module contains use cases for its business area.

Example:

```text
application/orders/
├── create_order.py
├── add_order_item.py
├── modify_order.py
├── accept_order.py
├── cancel_order.py
└── get_order.py
```

---

# 9. Use Case Responsibilities

A use case represents an application-level operation.

A use case should coordinate:

* authorization requirements;
* domain objects;
* repositories;
* transaction boundaries;
* domain services;
* audit;
* outbox events.

Example:

```text
AcceptOrder
    ↓
Load Order
    ↓
Validate Access
    ↓
Validate Order State
    ↓
Validate Product / Recipe
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
Commit
```

A use case must not become a giant function containing unrelated domain logic.

---

# 10. Domain Layer

The domain layer is organized by business domain.

```text
app/
└── domain/
    ├── business/
    ├── branch/
    ├── identity/
    ├── subscription/
    ├── device/
    ├── product/
    ├── recipe/
    ├── set/
    ├── inventory/
    ├── menu/
    ├── pricing/
    ├── order/
    ├── table/
    ├── payment/
    ├── debt/
    ├── cash/
    ├── handover/
    ├── attendance/
    ├── payroll/
    ├── notification/
    ├── audit/
    ├── report/
    ├── synchronization/
    ├── configuration/
    └── lifecycle/
```

The Domain Layer contains business concepts rather than HTTP or database implementation details.

---

# 11. Domain Module Structure

A domain module may use:

```text
domain/orders/
├── entities.py
├── value_objects.py
├── enums.py
├── rules.py
├── services.py
├── errors.py
└── events.py
```

Not every domain requires every file.

Files should only exist when they provide meaningful separation.

---

# 12. Domain Entities

Entities represent business objects with stable identity.

Examples:

```text
Business
Branch
Employee
Product
Recipe
Order
OrderItem
Payment
CashSession
InventoryItem
Report
```

Entities should represent domain state and behavior.

They should not depend directly on:

* HTTP request objects;
* Flask/FastAPI route objects;
* SQLAlchemy sessions;
* external API clients.

---

# 13. Value Objects

Value objects represent concepts where identity is determined by their value.

Examples may include:

```text
Money
Quantity
Percentage
DateRange
BusinessScope
BranchScope
Address
PhoneNumber
Price
```

Value objects should encapsulate validation where appropriate.

For example:

```text
Percentage
    0 <= value <= 100
```

may be enforced within the corresponding domain value object where that rule is universal.

---

# 14. Domain Services

Domain services are used when business logic:

* does not naturally belong to one entity;
* involves multiple domain objects;
* represents a domain operation.

Examples:

```text
PricingService
InventoryAvailabilityService
OrderAcceptanceService
CashReconciliationService
PayrollCalculationService
ConfigurationConflictService
```

Domain services must not become generic utility classes.

---

# 15. Domain Errors

Each domain may define domain-specific errors.

Example:

```text
OrderAlreadyAccepted
InsufficientStock
InactiveProduct
InvalidRecipe
CashSessionClosed
InvalidPayment
ConfigurationConflict
SubscriptionRestricted
UnauthorizedBranchOperation
```

These errors are translated by the application/API boundary into appropriate responses.

---

# 16. Domain Events

Domain events represent meaningful business occurrences.

Examples:

```text
OrderAccepted
PaymentRecorded
CashSessionClosed
InventoryAdjusted
RecipeApproved
PriceChanged
ShiftHandedOver
BusinessEnteredReadOnlyState
```

Events must be used intentionally.

Not every method call needs a domain event.

Events that must reliably trigger secondary processing should be persisted through the appropriate outbox mechanism.

---

# 17. Infrastructure Layer

Infrastructure contains implementations for external and technical concerns.

```text
app/
└── infrastructure/
    ├── database/
    ├── repositories/
    ├── cache/
    ├── storage/
    ├── messaging/
    ├── notifications/
    ├── crypto/
    ├── clock/
    ├── logging/
    └── external/
```

---

# 18. Database Infrastructure

```text
infrastructure/database/
├── session.py
├── base.py
├── models/
├── transaction.py
└── configuration.py
```

Responsibilities include:

* SQLAlchemy setup;
* database session management;
* connection pooling;
* transaction integration;
* database configuration.

Database infrastructure must not contain business workflow logic.

---

# 19. Database Models

Database models should be separated from domain entities where necessary.

Example:

```text
infrastructure/database/models/
├── business.py
├── branch.py
├── employee.py
├── product.py
├── recipe.py
├── inventory.py
├── order.py
├── payment.py
├── cash.py
├── audit.py
└── report.py
```

A database model describes persistence.

A domain entity describes business behavior.

They may be closely related, but they must not be assumed to be the same abstraction.

---

# 20. Repository Implementations

Repository interfaces belong near the application/domain boundary according to the final implementation approach.

Infrastructure provides their concrete implementations.

Example:

```text
domain / application
        ↓
OrderRepository interface
        ↓
infrastructure/repositories/
        ↓
SqlAlchemyOrderRepository
```

This prevents the domain from becoming dependent on SQLAlchemy.

---

# 21. Repository Structure

A possible implementation is:

```text
infrastructure/repositories/
├── business_repository.py
├── employee_repository.py
├── product_repository.py
├── recipe_repository.py
├── inventory_repository.py
├── order_repository.py
├── payment_repository.py
├── cash_session_repository.py
├── audit_repository.py
└── report_repository.py
```

Repository classes must enforce the required scope and persistence rules.

---

# 22. Security Package

Security-related technical behavior is centralized under:

```text
app/
└── security/
    ├── authentication/
    ├── authorization/
    ├── tokens/
    ├── passwords/
    ├── devices/
    ├── offline/
    └── policies/
```

This package provides technical security mechanisms.

Business permissions still depend on the application/domain model.

---

# 23. Authentication

Authentication components may handle:

* credential verification;
* access token validation;
* refresh mechanisms where applicable;
* session identity;
* employee identity extraction.

Authentication must not determine business authorization by itself.

---

# 24. Authorization

Authorization evaluates:

```text
Role Permission
+
Employee Override
+
Branch Scope
+
Employee Status
+
Subscription Entitlement
+
Operational Context
```

The final decision must be made server-side.

---

# 25. Background Package

Background processing is separated from request handling.

```text
app/
└── background/
    ├── jobs/
    ├── workers/
    ├── scheduler/
    ├── retry/
    └── handlers/
```

Examples:

```text
GenerateReportJob
SendNotificationJob
ProcessOutboxJob
ProcessDeletionJob
ProcessSyncBatchJob
```

Background jobs must remain idempotent where retries are possible.

---

# 26. Synchronization Package

Offline synchronization has dedicated backend infrastructure:

```text
app/
└── synchronization/
    ├── ingestion/
    ├── validation/
    ├── conflicts/
    ├── idempotency/
    ├── batching/
    └── results/
```

Responsibilities include:

* receiving offline batches;
* validating device authorization;
* checking Business lifecycle;
* checking operation UUIDs;
* validating dependencies;
* detecting conflicts;
* returning deterministic results.

---

# 27. Reporting Package

Reporting-specific processing belongs in:

```text
app/
└── reporting/
    ├── queries/
    ├── builders/
    ├── generators/
    ├── exporters/
    └── versions/
```

Reporting code should not be mixed into POS transaction services.

---

# 28. Shared Package

Shared code must remain small and stable.

```text
app/
└── shared/
    ├── errors/
    ├── types/
    ├── pagination/
    ├── identifiers/
    ├── money/
    ├── time/
    └── utilities/
```

The shared package must not contain arbitrary domain logic.

If a helper is only meaningful to one domain, it belongs in that domain.

---

# 29. Main Application Entry Point

The application entry point may be:

```text
app/main.py
```

Its responsibilities should remain limited to:

* application creation;
* framework configuration;
* router registration;
* middleware registration;
* startup/shutdown integration.

It should not contain business logic.

---

# 30. Configuration Structure

Technical configuration may be separated into:

```text
configuration/
├── development/
├── testing/
├── staging/
└── production/
```

Actual secrets must not be committed to source control.

Environment-specific configuration should be injected through secure configuration mechanisms.

---

# 31. Database Migrations

Migrations remain outside the application package:

```text
backend/
└── migrations/
    ├── versions/
    ├── env.py
    └── script.py.mako
```

Alembic manages schema changes.

Migration files must be version-controlled.

---

# 32. Scripts

Operational or development scripts may be placed in:

```text
backend/
└── scripts/
    ├── development/
    ├── maintenance/
    └── migration/
```

Scripts must not become an alternative application architecture.

Business-critical operations should use application services rather than direct ad-hoc database modifications.

---

# 33. Test Structure

Tests should reflect the architecture.

```text
tests/
├── unit/
│   ├── domain/
│   └── application/
│
├── integration/
│   ├── database/
│   ├── repositories/
│   ├── transactions/
│   └── synchronization/
│
├── api/
│   ├── authentication/
│   ├── authorization/
│   └── endpoints/
│
├── concurrency/
│
└── fixtures/
```

Tests should not depend unnecessarily on production services.

---

# 34. Domain Test Ownership

Domain tests belong close to domain behavior.

Examples:

```text
tests/unit/domain/order/
tests/unit/domain/inventory/
tests/unit/domain/pricing/
tests/unit/domain/cash/
tests/unit/domain/payroll/
```

These tests should verify business rules without requiring HTTP or a real PostgreSQL instance unless integration behavior is specifically being tested.

---

# 35. Application Test Ownership

Application tests verify complete use cases.

Examples:

```text
tests/unit/application/orders/
tests/unit/application/payments/
tests/unit/application/cash/
tests/unit/application/inventory/
```

They should verify:

* authorization integration;
* use-case orchestration;
* transaction behavior;
* repository interactions;
* audit/outbox creation;
* failure behavior.

---

# 36. Import Dependency Rules

The following dependency direction is preferred:

```text
API
 ↓
Application
 ↓
Domain
 ↓
Abstractions
 ↑
Infrastructure
```

Infrastructure implements interfaces required by upper layers.

The following is prohibited:

```text
Domain
 ↓
HTTP Framework
```

and:

```text
Domain
 ↓
SQLAlchemy Session
```

and:

```text
API Route
 ↓
Direct Database Mutation
```

---

# 37. Allowed Dependency Examples

Allowed:

```text
API → Application
Application → Domain
Application → Repository Interface
Infrastructure → Repository Interface
Infrastructure → Database
Background → Application
Reporting → Application / Repository abstraction
```

Not preferred:

```text
Domain → API
Domain → Flask/FastAPI
Domain → SQLAlchemy
Domain → Redis
Domain → HTTP Client
```

The goal is to keep core business logic independent from infrastructure.

---

# 38. Cross-Domain Dependencies

Domains may depend on other domains where business rules require it.

For example:

```text
Order
 ├── Product
 ├── Pricing
 ├── Inventory
 └── Payment
```

However, dependencies must be explicit.

Avoid circular domain dependencies such as:

```text
Order → Inventory → Order
```

If a circular dependency appears, introduce an application-level orchestration or domain event where appropriate.

---

# 39. Module Ownership

Each business capability must have a clear owner.

Example:

| Capability               | Primary owner   |
| ------------------------ | --------------- |
| Product identity         | Product         |
| Recipe                   | Recipe          |
| Stock quantity           | Inventory       |
| Selling price            | Pricing/Menu    |
| Order lifecycle          | Order           |
| Payment                  | Payment         |
| Cash session             | Cash            |
| Handover                 | Handover        |
| Employee permissions     | Identity/Access |
| Subscription entitlement | Subscription    |
| Audit                    | Audit           |
| Reports                  | Report          |

A module must not silently become the owner of another module's state.

---

# 40. CRUD Boundary

Generic CRUD endpoints should not be used for important business operations when a domain workflow exists.

For example, prefer:

```text
POST /orders/{id}/accept
```

over:

```text
PATCH /orders/{id}
{
    "status": "accepted"
}
```

Similarly:

```text
POST /cash-sessions/{id}/close
```

is preferred over allowing a generic status mutation.

Business operations should represent business intent.

---

# 41. Model Boundary

The project may contain three distinct representations:

```text
API Schema
    ↓
Application / Domain Object
    ↓
Persistence Model
```

Mapping may be required between them.

This prevents:

* database columns becoming API contracts accidentally;
* API changes from directly changing database behavior;
* ORM models becoming the domain model.

---

# 42. Dependency Injection

Dependencies should be provided explicitly where practical.

Examples:

```text
UseCase
  ├── Repository
  ├── AuthorizationService
  ├── AuditService
  ├── Clock
  └── TransactionManager
```

Dependency injection must remain understandable.

Avoid creating a giant global service container that hides dependencies.

---

# 43. Transaction Manager

A transaction manager may provide:

```text
begin
commit
rollback
```

Application use cases control transaction boundaries.

Repositories should not independently commit transactions in the middle of a larger use case.

This prevents partial commits such as:

```text
Order committed
Inventory not committed
```

when both are required to be atomic.

---

# 44. Repository Transaction Rule

Repositories should normally:

* read/write within the transaction supplied by the application;
* avoid unexpected commits;
* avoid unexpected rollbacks;
* not control unrelated transaction boundaries.

The Application Layer determines the lifecycle of the transaction.

---

# 45. Event Boundary

Events should be divided into:

### Domain Events

Internal business occurrences.

### Outbox Events

Persisted events that require reliable asynchronous processing.

### Integration Events

Events intended for external systems.

These concepts must not be mixed automatically.

---

# 46. Logging Boundary

Logging utilities belong to infrastructure/shared technical layers.

Domain entities should not directly write application logs.

Instead:

```text
Domain
 ↓
Domain Event / Error
 ↓
Application
 ↓
Logging / Observability
```

This prevents domain code from becoming coupled to a logging framework.

---

# 47. Exception Boundary

Exceptions should be translated at defined boundaries.

Example:

```text
Database Exception
       ↓
Infrastructure Error
       ↓
Application Error
       ↓
API Error
```

Internal exceptions must not leak database schema or SQL details to clients.

---

# 48. Naming Conventions

Python modules should use:

```text
snake_case.py
```

Classes:

```text
PascalCase
```

Functions:

```text
snake_case
```

Constants:

```text
UPPER_SNAKE_CASE
```

Use business terminology consistently with the accepted documentation.

For example:

```text
CashSession
OrderItem
RecipeVersion
ShiftHandover
Business
Branch
```

Do not randomly alternate between different names for the same concept.

---

# 49. File Size and Responsibility

A file should normally have one clear responsibility.

Large files should be split when they contain unrelated concerns.

However, artificial fragmentation should be avoided.

The goal is:

> One meaningful responsibility per module, not one class per file regardless of complexity.

---

# 50. Avoiding Utility Sprawl

A generic:

```text
utils.py
helpers.py
common.py
```

file must not become a dumping ground.

If functionality belongs to a specific domain, place it there.

If functionality is genuinely shared, place it under `shared/` with a clear name.

For example:

```text
shared/money/
shared/time/
shared/identifiers/
```

is preferable to:

```text
shared/utils.py
```

containing unrelated functions.

---

# 51. Backend Package Initialization

Each package should expose only the interfaces needed by other packages.

Avoid importing the entire application tree from package initialization files.

This reduces:

* circular imports;
* startup complexity;
* hidden dependencies.

---

# 52. API Versioning Boundary

API versioning should remain at the transport boundary.

For example:

```text
/api/v1/
```

The domain model should not contain version-specific API logic.

Different API versions may map to the same application use case when behavior remains compatible.

---

# 53. Background Worker Entry Point

Workers should have a dedicated entry point.

Example:

```text
app/background/worker.py
```

Workers should load the same application configuration and use the same domain/application services where appropriate.

They must not duplicate business rules.

---

# 54. Scheduled Job Ownership

Scheduled jobs should be defined under:

```text
app/background/scheduler/
```

Examples:

* subscription expiry notifications;
* deletion eligibility checks;
* monthly report generation;
* cleanup tasks;
* maintenance.

Schedules are operational concerns.

The actual business operation should remain implemented by the appropriate application service.

---

# 55. Synchronization Worker Ownership

Synchronization workers should use:

```text
app/synchronization/
```

rather than implementing synchronization logic directly in API routes.

This permits:

* API-triggered synchronization;
* background synchronization;
* retry;
* batch processing;

without duplicating rules.

---

# 56. Reporting Ownership

Report calculation logic should be separated from report transport.

For example:

```text
Report Query
    ↓
Report Builder
    ↓
Report Version
    ↓
XLSX Exporter
```

The API should only initiate and return report-related results.

---

# 57. File Storage Ownership

File storage logic belongs in:

```text
infrastructure/storage/
```

Business modules should request file operations through an abstraction rather than directly manipulating filesystem paths.

This allows future migration from local storage to object storage without rewriting domain logic.

---

# 58. External Service Ownership

External services must be accessed through dedicated infrastructure adapters.

Example:

```text
infrastructure/external/
├── email/
├── payment/
├── government/
└── ai/
```

External integrations must not be called directly from domain entities.

---

# 59. Security-Critical Code Placement

Security-sensitive functionality must have clearly defined ownership.

Examples:

```text
app/security/
    Authentication
    Tokens
    Passwords
    Device Trust
    Offline Authorization
```

Authorization decisions may require application/domain context.

Security code must not be duplicated across individual routes.

---

# 60. Business Context Object

A reusable server-side context object may represent:

```text
BusinessContext
    business_id
    branch_id
    employee_id
    device_id
```

Only applicable fields should be populated.

The context must be derived from authenticated state and validated scope.

It must not be treated as permission by itself.

---

# 61. Multi-Branch Queries

Repository methods handling Branch-scoped data should make scope explicit.

Bad:

```text
get_orders()
```

Preferred:

```text
get_orders(branch_id=...)
```

or a validated context-aware repository method.

The exact implementation may vary, but accidental global queries must be difficult to write.

---

# 62. Tenant Query Safety

Business-owned repository queries must include Business scope where required.

Bad:

```text
SELECT * FROM orders WHERE id = :id
```

when `id` alone is not a sufficient security boundary.

Preferred conceptual behavior:

```text
SELECT *
FROM orders
WHERE id = :id
  AND business_id = :business_id
```

The exact implementation should use safe parameterization and repository abstractions.

---

# 63. Database Session Context

A database connection obtained from a pool must not accidentally retain request-specific security context.

Any connection/session-level context must be:

* explicitly initialized;
* correctly scoped;
* cleared or reset;
* tested under connection reuse.

This is especially important if PostgreSQL Row-Level Security or session variables are introduced.

---

# 64. Performance-Critical Module Boundaries

POS-critical paths should avoid unnecessary layers that provide no value.

For example:

```text
Order Acceptance
```

may use:

```text
API
 → Use Case
 → Domain Service
 → Repository
 → Database
```

but must not unnecessarily execute:

```text
API
 → 8 generic services
 → multiple network calls
 → cache
 → queue
 → database
```

The architecture must remain clean without becoming ceremonially complex.

---

# 65. Code Generation and AI Agents

The project structure must be friendly to AI coding agents.

An Agent should be able to determine:

```text
Requirement
   ↓
System Analysis
   ↓
Domain
   ↓
Database
   ↓
Backend Module
   ↓
Use Case
   ↓
Repository
   ↓
Test
```

Agents must not infer architecture solely from existing code.

Documentation remains the authoritative architectural guide.

---

# 66. Change Workflow

A backend feature should normally follow:

```text
Requirement
    ↓
Relevant Analysis Document
    ↓
Domain Decision
    ↓
Database Impact Check
    ↓
Backend Module
    ↓
Use Case
    ↓
Repository / Infrastructure
    ↓
Tests
    ↓
API
```

When no requirement change exists and the task is purely technical, the upstream analysis documents may only need to be checked rather than modified.

---

# 67. Example: New Order Feature

For a new Order feature:

```text
System Analysis
       ↓
Order Domain
       ↓
Order Database Model
       ↓
application/orders/
       ↓
domain/order/
       ↓
OrderRepository
       ↓
API route/schema
       ↓
Tests
```

The feature should not be implemented by adding unrelated code to a generic `services.py`.

---

# 68. Example: New Pricing Rule

For a pricing rule:

```text
System Analysis
       ↓
Menu/Pricing Domain
       ↓
Pricing Database Model
       ↓
application/menu/
       ↓
domain/pricing/
       ↓
Repository
       ↓
API
       ↓
Tests
```

Historical price snapshots must be considered before implementation.

---

# 69. Example: Offline Feature

For an offline synchronization feature:

```text
System Analysis
       ↓
Offline Domain
       ↓
Offline Database Model
       ↓
synchronization/
       ↓
Application Use Case
       ↓
Repository
       ↓
Idempotency
       ↓
Conflict Handling
       ↓
Tests
```

Offline behavior must never bypass:

* Business lifecycle;
* permissions;
* device trust;
* subscription restrictions.

---

# 70. Project Structure Invariants

The following rules are mandatory:

1. Backend starts as a modular monolith.
2. API routes remain thin.
3. Business logic belongs in Application/Domain layers.
4. Database access belongs in repositories/infrastructure.
5. Domain logic must not depend on HTTP frameworks.
6. Domain logic must not depend directly on SQLAlchemy sessions.
7. Application use cases own transaction boundaries.
8. Repositories must not unexpectedly commit transactions.
9. Business scope must be enforced server-side.
10. Branch scope must be enforced server-side.
11. Authorization must not depend only on frontend behavior.
12. Historical transactions must not be silently modified.
13. Retryable operations must support idempotency.
14. Background jobs must reuse authoritative business logic.
15. Secondary processing must not unnecessarily block core POS operations.
16. Shared code must remain small and purposeful.
17. Generic utility modules must not become dumping grounds.
18. Cross-domain dependencies must remain explicit.
19. Circular dependencies must be avoided.
20. Database models must not automatically become API contracts.
21. API schemas must not automatically become domain entities.
22. Technical configuration must remain separate from Business configuration.
23. Secrets must not be committed to source control.
24. Tests must reflect architectural boundaries.
25. Schema changes must use migrations.
26. External integrations must be isolated behind infrastructure boundaries.
27. Cache must not become the authoritative source of business state.
28. Local process memory must not contain authoritative business state.
29. The project structure must remain understandable to AI coding agents.
30. Backend implementation must remain consistent with accepted upstream documentation.

---

# 71. Final Project Tree

The logical backend structure is:

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── dependencies/
│   │   └── errors/
│   │
│   ├── application/
│   │   ├── business/
│   │   ├── identity/
│   │   ├── subscription/
│   │   ├── devices/
│   │   ├── products/
│   │   ├── recipes/
│   │   ├── inventory/
│   │   ├── menu/
│   │   ├── orders/
│   │   ├── tables/
│   │   ├── payments/
│   │   ├── cash/
│   │   ├── handover/
│   │   ├── attendance/
│   │   ├── payroll/
│   │   ├── notifications/
│   │   ├── audit/
│   │   ├── reports/
│   │   ├── synchronization/
│   │   ├── configuration/
│   │   └── lifecycle/
│   │
│   ├── domain/
│   │   ├── business/
│   │   ├── branch/
│   │   ├── identity/
│   │   ├── subscription/
│   │   ├── device/
│   │   ├── product/
│   │   ├── recipe/
│   │   ├── set/
│   │   ├── inventory/
│   │   ├── menu/
│   │   ├── pricing/
│   │   ├── order/
│   │   ├── table/
│   │   ├── payment/
│   │   ├── debt/
│   │   ├── cash/
│   │   ├── handover/
│   │   ├── attendance/
│   │   ├── payroll/
│   │   ├── notification/
│   │   ├── audit/
│   │   ├── report/
│   │   ├── synchronization/
│   │   ├── configuration/
│   │   └── lifecycle/
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── models/
│   │   │   ├── session.py
│   │   │   ├── transaction.py
│   │   │   └── configuration.py
│   │   ├── repositories/
│   │   ├── cache/
│   │   ├── storage/
│   │   ├── messaging/
│   │   ├── notifications/
│   │   ├── crypto/
│   │   ├── clock/
│   │   ├── logging/
│   │   └── external/
│   │
│   ├── security/
│   │   ├── authentication/
│   │   ├── authorization/
│   │   ├── tokens/
│   │   ├── passwords/
│   │   ├── devices/
│   │   ├── offline/
│   │   └── policies/
│   │
│   ├── background/
│   │   ├── jobs/
│   │   ├── workers/
│   │   ├── scheduler/
│   │   ├── retry/
│   │   └── handlers/
│   │
│   ├── synchronization/
│   │   ├── ingestion/
│   │   ├── validation/
│   │   ├── conflicts/
│   │   ├── idempotency/
│   │   ├── batching/
│   │   └── results/
│   │
│   ├── reporting/
│   │   ├── queries/
│   │   ├── builders/
│   │   ├── generators/
│   │   ├── exporters/
│   │   └── versions/
│   │
│   ├── shared/
│   │   ├── errors/
│   │   ├── types/
│   │   ├── pagination/
│   │   ├── identifiers/
│   │   ├── money/
│   │   └── time/
│   │
│   └── main.py
│
├── migrations/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   └── application/
│   ├── integration/
│   │   ├── database/
│   │   ├── repositories/
│   │   ├── transactions/
│   │   └── synchronization/
│   ├── api/
│   ├── concurrency/
│   └── fixtures/
│
├── scripts/
│   ├── development/
│   ├── maintenance/
│   └── migration/
│
├── configuration/
│   ├── development/
│   ├── testing/
│   ├── staging/
│   └── production/
│
├── pyproject.toml
└── README.md
```

This is the logical target structure. Individual directories should only be created when the corresponding functionality actually exists.

---

# 72. Related Documents

### Backend

* `README.md`
* `01_Backend_Architecture.md`
* `03_Application_and_Use_Case_Layer.md`
* `04_Domain_Service_and_Business_Logic.md`
* `05_Repository_and_Data_Access.md`
* `06_Authentication_and_Authorization.md`
* `16_Offline_and_Synchronization_Backend.md`
* `17_Background_Jobs_and_Scheduling.md`
* `22_Backend_Security.md`
* `23_Backend_Concurrency_and_Idempotency.md`
* `24_Backend_Invariants_and_Guardrails.md`

### Architecture

* `../04_Architecture/README.md`

### Database

* `../05_Database/README.md`
* `../05_Database/02_Database_Architecture.md`
* `../05_Database/25_Database_Integrity_and_Constraints.md`
* `../05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `../05_Database/27_Database_Migrations_and_Change_Management.md`
* `../05_Database/29_Database_Security.md`
* `../05_Database/30_Database_Invariants_and_Guardrails.md`

---

# 73. Status

**Backend Architecture:** Accepted

**Project Structure:** Accepted

**Architecture Style:** Modular Monolith

**Primary Database:** PostgreSQL

**Persistence:** SQLAlchemy / Repository Boundary

**Migration Tool:** Alembic

**Application Model:** Layered + Domain-Oriented

**Next Document:** `03_Application_and_Use_Case_Layer.md`

