# 06. Backend Development Standards

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the coding and engineering standards for the FastFood ERP backend.

The backend is responsible for enforcing business rules, protecting data, coordinating application workflows, exposing controlled interfaces, and maintaining system consistency.

These standards define how backend code should be:

* structured;
* implemented;
* validated;
* tested;
* secured;
* optimized;
* reviewed;
* maintained.

The goal is to keep the backend predictable, maintainable, secure, testable, and scalable without introducing unnecessary complexity.

---

# 2. Scope

These standards apply to:

* domain logic;
* application services;
* use cases;
* repositories;
* database access;
* API endpoints;
* background jobs;
* scheduled tasks;
* authentication;
* authorization;
* tenant and branch isolation;
* inventory;
* recipes;
* POS;
* orders;
* payments;
* cash operations;
* payroll;
* subscriptions;
* offline synchronization;
* AI integration;
* external integrations;
* caching;
* queues;
* logging;
* configuration;
* backend tests.

---

# 3. Backend Engineering Principles

The backend follows these principles:

1. Business rules must be enforced server-side.
2. Domain rules must not depend on HTTP or framework details.
3. Application services coordinate use cases.
4. Infrastructure implements technical concerns.
5. API layers translate external requests into application operations.
6. Database access must remain controlled and explicit.
7. Authorization must be enforced before protected operations are executed.
8. Tenant and branch isolation must be enforced server-side.
9. Invalid states should be prevented as early as practical.
10. Transactions must protect consistency boundaries.
11. Concurrency must be considered for shared mutable resources.
12. Errors must be predictable and structured.
13. External systems must not silently become internal sources of truth.
14. Performance optimizations must be evidence-based.
15. Code must remain understandable to future developers.
16. Tests must verify important business behavior.
17. Logging must provide useful operational evidence without exposing secrets.
18. Configuration must not be hard-coded into business logic.
19. Dependencies must remain explicit.
20. Backend behavior must remain traceable to approved requirements and architecture.

---

# 4. Conceptual Backend Architecture

The backend should follow clear responsibility boundaries.

A conceptual structure is:

```text id="6b2z5a"
backend/
├── domain/
├── application/
├── infrastructure/
├── interfaces/
└── shared/
```

The exact physical structure may evolve, but responsibility boundaries must remain clear.

---

# 5. Domain Layer

The domain layer contains business concepts and rules.

Typical responsibilities include:

* entities;
* value objects;
* domain services;
* business invariants;
* domain events where required;
* domain-level policies.

Examples:

```text id="z9h5gq"
Order
CashRegister
InventoryItem
Recipe
RecipeVersion
Branch
Employee
Subscription
MenuItem
StockMovement
```

Domain code should not depend directly on:

* HTTP requests;
* controllers;
* framework-specific request objects;
* database sessions;
* Redis;
* message brokers;
* external API clients.

The domain should represent business behavior rather than infrastructure mechanics.

---

# 6. Application Layer

The application layer coordinates use cases.

Typical responsibilities include:

* receiving use-case commands;
* loading required domain objects;
* invoking domain behavior;
* coordinating repositories;
* managing transaction boundaries;
* invoking external services through abstractions;
* producing application results.

Examples:

```text id="l8rj8b"
CreateOrder
CloseCashRegister
ApproveRecipe
DeductInventory
RefundPayment
TransferCashier
SynchronizeOfflineTransaction
```

Application services should coordinate behavior rather than become large collections of unrelated business rules.

---

# 7. Infrastructure Layer

Infrastructure implements technical concerns.

Typical responsibilities include:

* database repositories;
* ORM mappings;
* cache clients;
* queue clients;
* file storage;
* email providers;
* external API clients;
* cryptographic services;
* device services;
* AI service adapters.

Infrastructure code may depend on technical libraries.

Domain code should not depend directly on infrastructure implementations.

---

# 8. Interface Layer

The interface layer exposes application capabilities.

Typical interfaces include:

* REST API;
* internal API;
* webhook handlers;
* CLI commands;
* background task entry points;
* synchronization endpoints.

Interfaces should remain thin.

They should:

1. receive input;
2. perform transport-level validation;
3. authenticate the request;
4. establish request context;
5. invoke the application layer;
6. translate the result into the appropriate output.

They should not contain large business workflows.

---

# 9. Shared Code

Shared code may contain truly cross-cutting functionality such as:

* common primitives;
* error types;
* identifiers;
* date/time utilities;
* serialization helpers;
* logging helpers;
* configuration primitives.

Shared code must not become a dumping ground.

A function belongs in shared code only when multiple independent areas genuinely require the same behavior.

---

# 10. Dependency Direction

Dependencies should move toward stable business concepts.

A preferred conceptual direction is:

```text id="h8svyq"
Interfaces
    ↓
Application
    ↓
Domain

Infrastructure
    ↓
Application / Domain abstractions
```

The exact dependency implementation may vary, but business logic should not become tightly coupled to transport or infrastructure details.

Avoid:

```text id="b1a4te"
Domain → HTTP framework
Domain → ORM
Domain → Redis
Domain → Flask request
Domain → external API
```

---

# 11. Controllers and API Handlers

Controllers or route handlers should remain thin.

A typical flow is:

```text id="f0h4gy"
HTTP Request
    ↓
Authentication
    ↓
Authorization
    ↓
Input Validation
    ↓
Application Use Case
    ↓
Domain Logic
    ↓
Repository / Infrastructure
    ↓
Application Result
    ↓
HTTP Response
```

A controller should not become the place where the entire business process is implemented.

Avoid large route handlers containing:

* database queries;
* permission logic;
* financial calculations;
* inventory deduction;
* recipe processing;
* complex state transitions.

---

# 12. Input Validation

Input validation should occur at appropriate boundaries.

Transport validation should handle issues such as:

* required fields;
* field types;
* basic formats;
* size limits;
* malformed requests.

Business validation belongs in the appropriate application/domain boundary.

For example:

```text id="q5g6h9"
"quantity must be a number"
```

is transport/input validation.

While:

```text id="k4c9bd"
"inventory cannot become negative"
```

is a business invariant.

Validation must not rely exclusively on frontend behavior.

---

# 13. Business Rule Enforcement

Business rules must be enforced server-side.

Examples include:

* permission restrictions;
* branch scope;
* tenant ownership;
* cash correction limits;
* inventory availability;
* recipe approval;
* refund authorization;
* subscription restrictions;
* payroll rules;
* offline transaction validation.

Frontend controls improve usability but are not security boundaries.

---

# 14. Authentication and Authorization

Authentication identifies the caller.

Authorization determines what the caller may do.

The backend must evaluate authorization before executing protected operations.

The conceptual authorization flow is:

```text id="5hsk2o"
Identity
  ↓
Tenant
  ↓
Branch Scope
  ↓
Role
  ↓
Functional Permission
  ↓
Resource Scope
  ↓
Action
```

Authorization must remain server-side.

Never assume:

```text id="q9upj1"
if frontend_button_hidden:
    user_cannot_execute_operation
```

An attacker may call the API directly.

---

# 15. Tenant Isolation

Every tenant-scoped operation must preserve tenant isolation.

Backend code must not accidentally allow:

```text id="q4k6v8"
Tenant A → Tenant B data
```

Repository and application boundaries should make tenant context explicit where required.

Queries should not silently operate across tenants.

Cross-tenant administrative operations must use explicit privileged paths.

---

# 16. Branch Isolation

Branch-scoped data must respect the authenticated user's branch scope.

For example:

```text id="0p9j8z"
User
  ↓
Allowed Branches
  ↓
Requested Resource
  ↓
Authorization
```

A branch identifier supplied by the client must never be treated as proof that the user is authorized to access that branch.

The server must validate the relationship.

---

# 17. Data Ownership

Every protected resource should have a clear ownership model.

The backend should know whether a resource is:

* tenant-owned;
* branch-owned;
* globally shared;
* user-owned;
* system-owned.

This ownership must be considered when:

* querying;
* creating;
* updating;
* deleting;
* exporting;
* synchronizing;
* caching.

---

# 18. Transactions

Transactions should protect meaningful consistency boundaries.

Use a transaction when multiple operations must succeed or fail together.

Examples:

```text id="0udx1p"
Create order
+
Deduct inventory
+
Record stock movement
```

or:

```text id="k0p6ca"
Close register
+
Persist closing state
+
Record closing result
```

The transaction boundary should be based on business consistency, not merely on the number of database statements.

---

# 19. Transaction Boundaries

Transactions should generally be coordinated at the application/use-case level.

Avoid scattering transaction management across many low-level repository methods when doing so makes the actual consistency boundary unclear.

Prefer:

```text id="z3a2fk"
Application Use Case
    ↓
Transaction Boundary
    ↓
Domain Operations
    ↓
Repositories
```

rather than:

```text id="h1u0jv"
Repository A → transaction
Repository B → transaction
Repository C → transaction
```

when all three operations must be atomic.

---

# 20. Concurrency

Shared mutable resources require concurrency analysis.

Important examples include:

* inventory quantities;
* cash registers;
* order submission;
* payment state;
* synchronization;
* stock adjustments;
* subscription state;
* counters;
* sequence numbers.

The backend must not assume that two requests will never execute simultaneously.

---

# 21. Inventory Concurrency

Inventory deduction is a critical consistency operation.

The implementation must ensure that concurrent orders cannot cause:

```text id="c5g8dr"
available quantity < 0
```

when negative stock is prohibited.

A correct design must protect:

```text id="y4i3qt"
check available quantity
        +
deduct quantity
```

as one consistency boundary.

Application logic alone is insufficient if concurrent requests can bypass the intended invariant.

---

# 22. Idempotency

Operations that may be retried must define appropriate idempotency behavior.

This is particularly important for:

* payments;
* order submission;
* offline synchronization;
* external callbacks;
* webhooks;
* background jobs.

For example:

```text id="9qeqwq"
Client Transaction ID
        ↓
Server
        ↓
Already processed?
    ↙       ↘
  Yes        No
  ↓          ↓
Return       Process
existing     transaction
result
```

Retrying the same business operation must not accidentally create duplicate effects.

---

# 23. Offline Synchronization

Offline operations require explicit synchronization boundaries.

Backend code should account for:

* duplicate requests;
* retry;
* transaction identity;
* ordering;
* stale state;
* conflicts;
* partial synchronization;
* authentication constraints.

Offline support must not weaken tenant or branch isolation.

---

# 24. State Transitions

Important business entities should use explicit state transitions.

Avoid arbitrary status changes such as:

```text id="l3e4bd"
order.status = "anything"
```

without validating whether the transition is permitted.

A state transition should answer:

* current state;
* requested state;
* allowed transition;
* actor authorization;
* required conditions;
* side effects.

Example:

```text id="x7x5km"
Pending
   ↓
Accepted
   ↓
Preparing
   ↓
Ready
   ↓
Completed
```

The exact state model is defined by the relevant domain requirements.

---

# 25. Domain Invariants

Important invariants must be protected at the appropriate layer.

Examples:

### Inventory

```text
stock >= 0
```

when negative stock is prohibited.

### Cash

```text
correction_count <= allowed_limit
```

### Permissions

```text
resource_scope ⊆ authorized_scope
```

### Subscription

```text
expired_feature_access = blocked
```

where the approved subscription policy requires it.

### Recipe

```text
active_recipe = approved_recipe
```

where approval is required.

---

# 26. Error Handling

Errors should be predictable and structured.

The backend should distinguish between:

* validation errors;
* authentication failures;
* authorization failures;
* not-found conditions;
* business rule violations;
* conflict conditions;
* external service failures;
* infrastructure failures;
* unexpected internal errors.

Do not expose internal stack traces or sensitive implementation details to clients.

---

# 27. Business Errors

Business rule violations should be represented explicitly.

Examples:

```text id="d5kqca"
INSUFFICIENT_STOCK
REGISTER_ALREADY_CLOSED
REGISTER_CORRECTION_LIMIT_REACHED
UNAUTHORIZED_BRANCH
RECIPE_NOT_APPROVED
SUBSCRIPTION_FEATURE_DISABLED
DUPLICATE_TRANSACTION
```

Error identifiers should remain stable enough for clients to handle them when necessary.

Human-readable messages may change without changing the underlying error meaning.

---

# 28. HTTP Error Mapping

API layers should translate application errors into appropriate transport responses.

Conceptually:

```text id="0c1n9j"
Application Error
      ↓
API Error Mapper
      ↓
HTTP Status
+
Stable Error Code
+
Safe Message
```

Business logic should not need to construct HTTP responses.

Avoid:

```text id="wy4n8j"
raise HTTPException(...)
```

inside domain logic.

---

# 29. Exception Handling

Do not use broad exception handling as a substitute for proper error design.

Avoid:

```text id="o0cz8w"
try:
    do_operation()
except Exception:
    return success
```

This hides failures.

Instead:

* catch exceptions at meaningful boundaries;
* preserve useful context;
* convert expected failures into known application errors;
* allow unexpected failures to reach centralized error handling.

---

# 30. Logging

Backend logging should provide useful operational evidence.

Logs may include:

* request correlation identifiers;
* operation identifiers;
* tenant-safe context;
* branch-safe context;
* error codes;
* state transitions;
* external service failures;
* synchronization failures;
* security-relevant events.

Logs must not contain:

* passwords;
* authentication tokens;
* private keys;
* secrets;
* sensitive payment information;
* unnecessary personal data.

---

# 31. Audit Logging

Important security and business operations should be auditable where required.

Examples include:

* permission changes;
* role changes;
* refund approval;
* register corrections;
* inventory adjustments;
* recipe approval;
* subscription changes;
* privileged administrative operations.

Audit events should answer:

```text id="e9a3y7"
Who?
What?
When?
Where?
Which resource?
What changed?
Why, if required?
```

---

# 32. Logging Levels

Use logging levels intentionally.

Typical levels:

```text id="l8v0m2"
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Avoid logging everything at `ERROR`.

Avoid using `DEBUG` logs as permanent business auditing.

Production logging must remain useful without becoming unnecessarily expensive.

---

# 33. Database Access

Database access must remain controlled.

Avoid arbitrary database queries scattered throughout business code.

Repository or data-access abstractions should make ownership and query intent clear.

Queries should:

* select only required data where practical;
* respect tenant and branch scope;
* use appropriate indexes;
* avoid accidental N+1 behavior;
* avoid unnecessary repeated queries.

---

# 34. N+1 Query Prevention

Backend developers should identify query patterns that unintentionally perform:

```text id="1j0w2d"
1 query
+
N additional queries
```

for collections.

Where appropriate, use:

* eager loading;
* batching;
* aggregation;
* dedicated queries;
* prefetching.

Optimization must preserve correctness.

---

# 35. Query Safety

Database queries must be parameterized through the chosen database abstraction.

Never construct SQL using unsafe string interpolation with user-controlled input.

Avoid patterns equivalent to:

```text id="o1y4m7"
"SELECT * FROM users WHERE id = " + user_input
```

Use parameterized queries or safe ORM/query-builder mechanisms.

---

# 36. Data Loading

Load only what the use case requires when practical.

Avoid retrieving:

```text id="s6h5gk"
entire tenant
entire branch
entire order history
```

when the operation requires only a small subset.

This improves:

* performance;
* memory usage;
* security boundaries;
* response size.

---

# 37. Pagination

Large collections should use appropriate pagination.

Examples include:

* orders;
* inventory movements;
* audit records;
* employees;
* reports;
* notifications.

Do not expose unlimited collection endpoints without a justified reason.

Pagination behavior must remain stable and documented when clients depend on it.

---

# 38. Time and Date Handling

Time-sensitive backend operations must use consistent time handling.

Consider:

* server timezone;
* branch timezone;
* user display timezone;
* database storage;
* daylight-saving behavior where applicable;
* date boundaries for reports.

Business dates must not be derived from arbitrary client-provided timestamps without validation.

---

# 39. Monetary Values

Monetary values must use appropriate exact representations.

Do not use binary floating-point arithmetic for business-critical monetary calculations when it can introduce rounding errors.

The implementation should define:

* precision;
* scale;
* rounding rules;
* currency assumptions.

Financial calculations must be tested.

---

# 40. Identifiers

Backend identifiers should be:

* unique where required;
* stable;
* opaque where appropriate;
* safe for distributed/offline operations.

Internal database identifiers and client-facing transaction identifiers may have different purposes.

For offline synchronization, transaction identity must be designed for safe retry and deduplication.

---

# 41. Configuration

Configuration should be externalized.

Do not hard-code:

* credentials;
* environment-specific URLs;
* secrets;
* production database addresses;
* deployment-specific values.

Configuration should come from the approved configuration system.

Environment-specific behavior should be explicit.

---

# 42. Secrets

Secrets must never be committed to source control.

This includes:

* passwords;
* API keys;
* private keys;
* tokens;
* database credentials;
* encryption keys.

Use the project's approved secret-management process.

Example configuration files should contain placeholders only.

---

# 43. External Services

External integrations should be isolated behind explicit interfaces or adapters.

Examples:

```text id="kqj3y6"
Payment Provider
SMS Provider
Email Provider
Identity Provider
AI Service
Storage Provider
```

Business logic should not become tightly coupled to provider-specific request structures.

External failures must be handled explicitly.

---

# 44. External Service Reliability

External service calls should consider:

* timeouts;
* retries;
* idempotency;
* rate limits;
* failure handling;
* circuit protection where justified;
* logging;
* fallback behavior.

Retries must not duplicate financial or business operations.

---

# 45. Background Jobs

Background jobs should be:

* idempotent where practical;
* retry-safe;
* observable;
* bounded;
* failure-aware.

Examples include:

* notifications;
* report generation;
* synchronization;
* subscription checks;
* cleanup;
* scheduled calculations.

A job should not assume it will execute exactly once.

---

# 46. Queues

Queue-based processing should define:

* message identity;
* retry behavior;
* failure handling;
* dead-letter behavior where applicable;
* idempotency;
* ordering requirements;
* observability.

Queue processing must not silently lose business-critical operations.

---

# 47. Caching

Caching should be introduced only when useful.

Before adding a cache, determine:

* what is cached;
* who owns the source of truth;
* how stale data is acceptable;
* how invalidation works;
* what happens on cache failure;
* whether authorization scope affects the cached value.

Never allow a cache to bypass authorization.

Tenant- or branch-scoped data must not leak through shared cache keys.

---

# 48. Cache Invalidation

Cache invalidation must be part of the design.

For mutable data:

```text id="7kzj4c"
Write
 ↓
Source of Truth
 ↓
Cache Update / Invalidation
```

The system must define what happens when invalidation fails.

Caching must not silently produce permanently incorrect business data.

---

# 49. Performance Standards

Performance work should be evidence-based.

Do not optimize solely because a code pattern "looks slow."

Use:

* measurements;
* profiling;
* query analysis;
* load testing;
* application metrics.

Important performance areas include:

* database queries;
* API latency;
* serialization;
* large reports;
* inventory operations;
* synchronization;
* background jobs.

---

# 50. Resource Constraints

The backend should remain practical for the project's expected deployment environments.

Avoid unnecessary:

* memory consumption;
* CPU-heavy processing;
* excessive database connections;
* large synchronous workloads;
* expensive repeated queries.

Architecture should scale without assuming unlimited server resources.

---

# 51. API Response Design

API responses should be:

* predictable;
* consistent;
* appropriately sized;
* documented;
* safe.

Avoid returning internal database models directly when doing so exposes implementation details.

Use explicit response schemas where appropriate.

---

# 52. Request Size and Resource Limits

Backend endpoints should apply appropriate limits.

Examples include:

* request body size;
* file upload size;
* pagination size;
* batch size;
* synchronization batch size;
* report range.

Limits protect both reliability and security.

---

# 53. File Handling

Uploaded files must be treated as untrusted input.

The backend should validate:

* file type;
* size;
* extension where applicable;
* content where necessary;
* storage location;
* access permissions.

Do not expose uploaded files merely because a predictable URL exists.

---

# 54. Security by Default

Backend code should follow:

```text id="7s8jv2"
Default Deny
Least Privilege
Explicit Authorization
Validated Input
Controlled Data Access
Safe Error Handling
```

New functionality should not accidentally become accessible to all users.

New permissions should be explicit.

---

# 55. Deletion and Archiving

Business-critical records should not be physically deleted merely for convenience.

Where the business model requires history, use:

* archive;
* inactive status;
* versioning;
* soft deletion where appropriate.

Examples include:

* recipes;
* financial records;
* inventory history;
* audit records.

Deletion behavior must follow the approved domain rules.

---

# 56. Recipe Versioning

Recipe changes require special care.

Backend logic should preserve the approved relationship between:

```text id="r2n1z6"
Product
  ↓
Recipe Version
  ↓
Ingredients
  ↓
Stock Effects
```

Old approved recipes must remain usable for historical records when required.

New or changed recipes must follow the required approval process.

---

# 57. Inventory Operations

Inventory operations should create traceable stock movements where required.

Examples include:

* purchase;
* preparation;
* consumption;
* adjustment;
* waste;
* return;
* transfer.

The backend must preserve the relationship between the business event and its inventory effect.

---

# 58. Financial Operations

Financial operations should be explicit and auditable.

Examples include:

* payment;
* refund;
* register opening;
* register closing;
* cash handover;
* shortage;
* correction;
* payroll.

Avoid generic update operations that allow arbitrary manipulation of financial state.

---

# 59. Generic CRUD Caution

Generic CRUD patterns should not replace domain-specific operations where business rules are important.

Avoid exposing:

```text id="d6bq1a"
PATCH /cash-register/{id}
```

if that endpoint can arbitrarily modify financial state.

Prefer explicit operations such as:

```text id="8z2n1q"
Open Register
Close Register
Confirm Handover
Request Correction
Approve Correction
```

This makes business behavior explicit and easier to secure.

---

# 60. Service Class Size

Application services should remain focused.

A service that handles:

```text id="r5b6xw"
orders
inventory
payroll
reports
subscriptions
notifications
```

is a design warning.

Split responsibilities according to actual use cases and domain boundaries.

Avoid splitting every three lines into a separate class merely to satisfy an artificial size rule.

Responsibility is more important than file length.

---

# 61. Naming Standards

Names should describe domain meaning.

Prefer:

```text id="3w2u0f"
calculate_order_total()
approve_recipe()
deduct_inventory()
close_cash_register()
authorize_branch_access()
```

Avoid:

```text id="c9n7n6"
process()
handle()
do_it()
update_data()
manage()
```

Generic names may be acceptable for genuinely generic infrastructure operations.

---

# 62. Boolean Naming

Boolean values should clearly communicate state.

Prefer:

```text id="4o7n4f"
is_active
is_approved
has_permission
can_refund
requires_sync
```

Avoid ambiguous names such as:

```text id="a8u2r3"
active_flag
status_bool
check
```

unless the context makes the meaning unambiguous.

---

# 63. Function Design

Functions should:

* have one clear responsibility;
* use meaningful parameters;
* avoid hidden side effects;
* avoid excessive argument lists;
* return predictable results.

A function that performs several unrelated business operations should usually be decomposed.

---

# 64. Side Effects

Side effects should be explicit.

For example:

```text id="v0f0oc"
create_order()
```

should not unexpectedly:

* send unrelated emails;
* modify unrelated inventory;
* change user permissions;
* alter subscription state.

Required side effects should be part of the documented use-case behavior.

---

# 65. Dependency Injection

Dependencies should be explicit where dependency injection is used.

Examples:

```text id="8m2n1d"
OrderService(
    order_repository,
    inventory_service,
    payment_service,
)
```

Avoid hidden global dependencies where they make testing or reasoning difficult.

Dependency injection should not become ceremony for trivial code.

---

# 66. Circular Dependencies

Circular dependencies between modules should be avoided.

A circular dependency often indicates:

* unclear ownership;
* incorrect layer placement;
* overly coupled services;
* missing abstraction.

Resolve the architectural cause rather than hiding the cycle with import tricks.

---

# 67. Transactions and External Calls

Avoid holding database transactions open unnecessarily while waiting for slow external services.

For example:

```text id="czf5x4"
BEGIN TRANSACTION
    ↓
Call external API
    ↓
Wait
    ↓
Commit
```

may create unnecessary lock contention.

When a workflow requires both local and external state, use an explicit consistency strategy rather than assuming a single database transaction can control both systems.

---

# 68. Security-Sensitive Timing

Operations involving security or financial state should avoid unnecessary timing-sensitive behavior where practical.

Examples include:

* credential verification;
* token validation;
* privileged operations.

Use established secure libraries and patterns rather than implementing cryptographic primitives manually.

---

# 69. Cryptography

Do not implement cryptographic algorithms manually.

Use approved, well-maintained libraries.

Developers should understand:

* what is being protected;
* key lifecycle;
* storage;
* rotation;
* expiration;
* failure behavior.

Cryptography must not be treated as a simple helper function.

---

# 70. Dependency Management

Backend dependencies must be:

* explicitly declared;
* version-controlled;
* reviewed;
* kept reasonably current;
* tested after upgrades.

Security-sensitive dependency updates should receive appropriate priority.

Unused dependencies should be removed.

---

# 71. Type Safety

Where the chosen backend language supports type checking, type information should be used consistently.

Types should communicate:

* expected input;
* output;
* optional values;
* domain identifiers;
* collections;
* error/result boundaries.

Do not disable type checking broadly to make implementation easier.

---

# 72. Code Duplication

Avoid unnecessary duplication of business rules.

If the same rule is implemented separately in:

```text id="u9p1xq"
API
Background Job
CLI
```

the implementations may eventually diverge.

Shared business behavior should have a clear authoritative location.

However, abstraction should be introduced only when the shared behavior is genuinely the same.

---

# 73. Comments

Comments should explain:

* why something is necessary;
* a non-obvious business constraint;
* a technical limitation;
* a compatibility requirement;
* a subtle concurrency decision.

Avoid comments that merely repeat the code.

Prefer:

```text id="7bq2y1"
# The transaction boundary must include both availability
# validation and deduction to prevent concurrent overselling.
```

over:

```text id="x2k4s7"
# Deduct stock.
```

---

# 74. TODOs

TODO comments should not become permanent hidden requirements.

A meaningful TODO should identify:

* what remains;
* why it remains;
* relevant issue/reference when available.

Avoid:

```text id="7q0b6m"
# TODO fix later
```

Prefer:

```text id="2g4x5q"
# TODO: replace temporary provider adapter after the approved
# integration contract is available. Ref: INT-014
```

---

# 75. Testing Requirements

Backend tests should exist at appropriate levels.

Important levels include:

```text id="4qjv8d"
Unit
Domain
Application
Repository / Database
API
Integration
End-to-End
```

Not every function requires every test level.

Critical business rules require stronger evidence.

---

# 76. Testability

Backend code should be structured so important behavior can be tested without requiring unnecessary infrastructure.

Good testability usually comes from:

* clear boundaries;
* explicit dependencies;
* deterministic logic;
* isolated domain rules;
* controlled external integrations.

Avoid architecture that makes every unit test require a full production environment.

---

# 77. Test Data

Tests must use controlled test data.

Do not use:

* production credentials;
* production customer data;
* production payment information;
* real secrets.

Fixtures should represent realistic business states without exposing real user data.

---

# 78. Regression Prevention

When fixing a bug, add a regression test when practical.

Preferred sequence:

```text id="u7g8j9"
Bug
 ↓
Reproduction
 ↓
Regression Test
 ↓
Fix
 ↓
Verification
```

The test should fail for the old incorrect behavior and pass for the corrected behavior.

---

# 79. Backend Health

The backend should expose appropriate health information for operational monitoring.

Health checks should distinguish between:

* process availability;
* critical dependency availability;
* readiness to receive traffic.

Health endpoints must not expose sensitive internal information.

---

# 80. Observability

Production backend behavior should be observable through appropriate:

* logs;
* metrics;
* traces where justified;
* health checks;
* audit records.

Observability must not become a source of sensitive-data leakage.

---

# 81. Background Cleanup

Cleanup tasks must be designed carefully.

Examples include:

* expired temporary data;
* synchronization artifacts;
* old cache entries;
* subscription retention workflows.

Destructive cleanup must respect approved retention policies.

For FastFood, data deletion after subscription expiration must follow the approved business policy and must not occur merely because a scheduled job encounters an unexpected state.

---

# 82. Subscription Enforcement

Subscription restrictions must be enforced at backend authorization/use-case boundaries.

A frontend-disabled button is not sufficient.

The backend must determine whether the requested functionality is currently available under the tenant's subscription.

Historical data access must follow the approved subscription policy.

---

# 83. Permission Changes

Permission changes are security-sensitive operations.

The backend should:

* validate who may modify permissions;
* validate affected scope;
* prevent privilege escalation;
* invalidate or refresh authorization state when required;
* record important permission changes.

A user must not be able to grant themselves permissions through a client-controlled request.

---

# 84. Branch-Specific Permissions

When permissions differ by branch, backend checks must evaluate the effective branch scope.

For example:

```text id="r0t6o9"
Employee
 ├── Branch A → Allowed
 ├── Branch B → Denied
 └── Branch C → Allowed
```

The server must enforce these differences for every protected operation.

---

# 85. API Idempotency and Retries

Any endpoint that may be retried by:

* mobile clients;
* POS clients;
* offline clients;
* proxies;
* background workers;

should define whether repeated requests are safe.

Financial and order-creation operations require particular attention.

---

# 86. Response Consistency

Equivalent endpoints should use consistent:

* error structures;
* pagination conventions;
* identifiers;
* timestamps;
* status representations.

Inconsistency increases frontend complexity and integration errors.

---

# 87. Backward Compatibility

When changing backend behavior, consider:

* existing clients;
* offline clients;
* cached requests;
* queued jobs;
* background workers;
* external integrations.

Do not assume all clients update simultaneously.

Breaking behavior must be explicitly planned.

---

# 88. Safe Deployment Compatibility

Backend changes should consider whether the old and new application versions can temporarily coexist during deployment.

Important cases include:

* database migrations;
* API contracts;
* background jobs;
* queues;
* cache formats;
* synchronization protocols.

Where rolling deployment is used, compatibility must be designed intentionally.

---

# 89. Performance and Correctness

Performance improvements must not weaken business correctness.

For example, reducing inventory query time is not a valid optimization if it allows:

```text id="8x3q5d"
negative stock
```

or duplicate deductions.

Correctness has priority over premature optimization.

---

# 90. Simplicity

Backend code should be as simple as practical.

Avoid unnecessary:

* abstractions;
* design patterns;
* service layers;
* wrappers;
* generic frameworks;
* configuration systems.

Complexity must solve a real engineering problem.

The correct standard is:

> Use the simplest architecture that preserves the required correctness, security, scalability, and maintainability.

---

# 91. Production Data Safety

Development and testing must not directly manipulate production data unless an explicitly authorized operational process exists.

Never:

* copy production secrets into local configuration;
* commit production databases;
* use real credentials in tests;
* use real customer data as fixtures;
* expose production data through debugging tools.

---

# 92. Backend Change Checklist

Before considering a backend change complete:

### Architecture

* [ ] Responsibility is in the correct layer.
* [ ] Dependency direction remains valid.
* [ ] No unnecessary coupling was introduced.

### Business

* [ ] Approved business rules are preserved.
* [ ] Important invariants are enforced.
* [ ] State transitions are valid.

### Security

* [ ] Authentication requirements are satisfied.
* [ ] Authorization is server-side.
* [ ] Tenant isolation is preserved.
* [ ] Branch isolation is preserved.
* [ ] No privilege escalation is possible.

### Data

* [ ] Database access is scoped correctly.
* [ ] Transactions cover required consistency boundaries.
* [ ] Concurrency was considered.
* [ ] Migrations are safe.

### API

* [ ] Request validation is correct.
* [ ] Response structure is appropriate.
* [ ] Error mapping is consistent.
* [ ] Compatibility impact is understood.

### Reliability

* [ ] External failures are handled.
* [ ] Retries are safe.
* [ ] Idempotency is considered.
* [ ] Background jobs are retry-safe where needed.

### Performance

* [ ] Query count is reasonable.
* [ ] Large collections are paginated.
* [ ] Resource usage is acceptable.
* [ ] Performance changes are evidence-based.

### Testing

* [ ] Relevant unit/domain tests exist.
* [ ] Application behavior is tested.
* [ ] Database/API/integration tests are added where required.
* [ ] Regression behavior is covered.

### Operations

* [ ] Useful logging exists.
* [ ] Sensitive data is not logged.
* [ ] Health/observability impact is considered.
* [ ] Configuration is externalized.

---

# 93. Backend Anti-Patterns

The following patterns should be treated as design warnings or violations when they contradict project requirements.

## 93.1 Fat Controllers

```text id="qgk8p5"
Controller
 ├── business logic
 ├── database queries
 ├── financial calculations
 ├── authorization
 └── external integrations
```

Controllers should coordinate rather than own the entire business process.

---

## 93.2 Frontend-Only Authorization

```text id="3z0lq9"
Button hidden
=
operation protected
```

This is incorrect.

Authorization must be enforced server-side.

---

## 93.3 Generic CRUD for Sensitive Operations

```text id="b8k9o1"
PATCH /cash-register/{id}
```

must not provide unrestricted manipulation of financial state.

---

## 93.4 Silent Exception Handling

```text id="6m0n4y"
except Exception:
    pass
```

This hides failures and is unacceptable for meaningful backend operations.

---

## 93.5 Hidden Global State

Business behavior should not depend on unexplained global mutable state.

---

## 93.6 Unbounded Queries

Avoid endpoints that can return unlimited records without pagination or a justified bounded result.

---

## 93.7 Unsafe Caching

A shared cache must not allow:

```text id="1o6v1g"
Tenant A → Tenant B data
```

or:

```text id="c0r9h3"
Branch A → Branch B data
```

---

## 93.8 Business Logic in SQL Only

Important business rules should not become impossible to understand because they are scattered across complex database expressions.

Database constraints are valuable, but application/domain behavior should remain explicit.

---

## 93.9 Business Logic Only in the API Layer

The same business operation may be triggered through:

* API;
* background worker;
* synchronization;
* administrative tools.

Business rules must therefore not exist only inside HTTP handlers.

---

# 94. Relationship with Other Development Documents

This document defines backend implementation standards.

It works together with:

* `01_Development_Architecture_Overview.md`;
* `02_Repository_Structure_and_Conventions.md`;
* `03_Git_Branching_and_Version_Control_Strategy.md`;
* `04_Commit_Message_and_Change_Standards.md`;
* `05_Pull_Request_and_Code_Review_Process.md`;
* `08_Database_Development_and_Migration_Workflow.md`;
* `09_API_Development_and_Contract_Change_Workflow.md`;
* `10_Documentation_First_Development_Workflow.md`;
* `11_ADR_and_Architecture_Decision_Workflow.md`;
* `13_Testing_and_Debugging_Workflow.md`;
* `14_Dependency_and_Package_Management.md`;
* `15_Configuration_and_Feature_Flag_Development.md`;
* `18_Development_Guardrails_and_Quality_Rules.md`.

Backend standards must also remain consistent with the approved Security, Architecture, Database, API, Testing, and Deployment documentation.

---

# 95. Backend Development Invariants

The following rules are mandatory project invariants:

1. Backend code must enforce business rules server-side.
2. Domain logic must remain independent of transport concerns.
3. Application services must coordinate use cases.
4. Infrastructure concerns must remain separated from business rules.
5. API handlers must remain appropriately thin.
6. Authorization must be enforced server-side.
7. Tenant isolation must never rely on client input.
8. Branch isolation must be enforced server-side.
9. Protected resources must have clear ownership.
10. Important consistency boundaries must use appropriate transactions.
11. Concurrent operations must preserve business invariants.
12. Inventory must not become negative where the approved rule prohibits it.
13. Retryable operations must have appropriate idempotency behavior.
14. Offline synchronization must preserve transaction identity and consistency.
15. Important state transitions must be validated.
16. Expected business errors must be represented predictably.
17. Internal implementation details must not leak through API errors.
18. Secrets must never be stored in source code.
19. Sensitive information must not be unnecessarily logged.
20. Database queries must respect tenant and branch scope.
21. Large collections must be appropriately bounded or paginated.
22. Monetary calculations must use suitable exact representations.
23. External service calls must have explicit failure behavior.
24. Background jobs must be safe to retry where required.
25. Caches must never bypass authorization or data isolation.
26. Performance optimizations must be evidence-based.
27. Tests must protect important business behavior.
28. Bug fixes should include regression tests where practical.
29. Architecture-significant changes must follow the ADR process.
30. Database changes must follow the migration workflow.
31. API changes must follow the API contract workflow.
32. Configuration must be externalized appropriately.
33. Production data and credentials must not enter development artifacts.
34. Generic CRUD must not bypass domain-specific authorization or business rules.
35. Backend code must remain understandable and maintainable.
36. Complexity must be justified by a real engineering requirement.
37. Correctness takes priority over premature optimization.
38. Every backend change must remain consistent with accepted project architecture.
39. Backend behavior must remain traceable to requirements and tests.
40. The final implementation must preserve security, data integrity, and business correctness.

---

# 96. Final Principle

The FastFood backend is the authoritative enforcement layer for business behavior and system integrity.

Frontend applications, offline clients, background workers, integrations, and administrative tools may all initiate operations.

The backend must therefore remain capable of independently enforcing:

```text id="5mbq3c"
Identity
    ↓
Tenant
    ↓
Branch Scope
    ↓
Permission
    ↓
Business Rule
    ↓
Transaction
    ↓
Data Integrity
    ↓
Observable Result
```

The backend should be secure by default, explicit about business behavior, careful with data consistency, efficient without premature optimization, and simple enough for future developers to understand.

**Final rule:**

> Backend code must make correct behavior easy to enforce, incorrect behavior difficult to create, and important business decisions visible in the architecture and implementation.

