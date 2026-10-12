# 05 — Application and Use-Case Testing

**Document ID:** TEST-05
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`
**Depends On:** TEST-01, TEST-02, TEST-03, TEST-04
**Related:** TEST-06, TEST-07, TEST-08, TEST-09, TEST-10, TEST-11, TEST-12, TEST-13, TEST-14

---

## 1. Purpose

This document defines the testing architecture for application services, use cases, commands, queries, workflows, and application-level orchestration.

Application testing verifies that the system correctly coordinates domain behavior with application responsibilities such as:

* loading required state;
* validating application-level preconditions;
* resolving business context;
* evaluating authorization context;
* invoking domain behavior;
* coordinating repositories;
* coordinating external boundaries;
* managing transaction boundaries;
* producing required side effects;
* returning the correct application result;
* handling failures consistently.

The central question is:

> Does the application layer correctly coordinate the domain and surrounding boundaries to complete a business use case?

---

# 2. Scope

This document covers:

* application services;
* use cases;
* commands;
* queries;
* application workflows;
* orchestration;
* application-level validation;
* authorization context propagation;
* tenant and branch context;
* repository coordination;
* domain service invocation;
* transaction boundaries;
* idempotency behavior where owned by the application layer;
* external side-effect coordination;
* notifications;
* audit event coordination;
* background-job dispatch;
* application-level error handling;
* application result mapping;
* retry-safe application behavior.

This document does not define:

* pure domain rule testing;
* database implementation testing;
* API contract testing;
* frontend testing;
* detailed concurrency testing;
* detailed financial testing;
* detailed inventory testing;
* infrastructure testing.

Those responsibilities belong to other testing documents.

---

# 3. Application Testing Role

The application layer connects external requests to domain behavior.

Conceptually:

```text
External Entry Point
        │
        ▼
Application Use Case
        │
        ├── Context
        ├── Authorization
        ├── Validation
        ├── State Loading
        ├── Domain Operation
        ├── Persistence Coordination
        └── Side Effects
                │
                ▼
             Result
```

Application tests verify that these responsibilities are coordinated correctly.

---

# 4. Application Testing Principles

## 4.1 Test Use-Case Behavior

Tests should describe what the application use case does.

Prefer:

```text id="u1t8k4"
when the cashier submits a valid order,
the application creates the order,
persists the required state,
and schedules the required downstream actions
```

over:

```text id="4f7s2q"
application_service calls repository.save()
```

The first describes application behavior.

---

## 4.2 Domain Rules Remain in the Domain

Application tests must not duplicate domain implementation.

For example:

```text id="v8zq6m"
Domain:
Refund cannot exceed refundable amount.
```

Application:

```text id="a5x2wp"
Refund use case:
- loads the order;
- checks application context;
- invokes refund behavior;
- persists the result;
- records required side effects.
```

The application test verifies orchestration.

The domain test verifies the business invariant.

---

## 4.3 Test Real Boundaries

Application tests should verify important interactions between:

* application services;
* domain objects;
* repositories;
* transaction boundaries;
* authorization context;
* external services;
* event/notification mechanisms.

Tests should use appropriate test doubles where the real dependency would make the test slow, unstable, or outside the intended boundary.

Test-double principles are defined in TEST-03.

---

## 4.4 Test Failure Paths as First-Class Behavior

Every important use case should test:

* successful execution;
* invalid input;
* missing resource;
* unauthorized operation;
* unavailable resource;
* domain rejection;
* dependency failure;
* transaction failure;
* side-effect failure where relevant;
* retry behavior where applicable;
* idempotent repetition where applicable.

---

# 5. Application Use Case Definition

A use case represents a meaningful application operation.

Examples include:

```text id="k3d9s2"
Create Order
Accept Order
Update Order Status
Pay Order
Refund Order
Open Cash Session
Close Cash Session
Handover Cash Session
Create Recipe
Submit Recipe for Approval
Approve Recipe
Adjust Inventory
Create Purchase Entry
Create Expense
Create Employee
Assign Employee to Branch
Update Permissions
Activate Menu Item
Change Product Price
Reactivate Subscription
Archive Product
```

The exact use-case catalog is maintained by the application architecture.

---

# 6. Use-Case Test Structure

A typical application test should verify:

```text id="z4q7pu"
Arrange
  ↓
Application Context
  ↓
Input
  ↓
Dependencies
  ↓
Act
  ↓
Use Case
  ↓
Assert
  ├── Result
  ├── Domain State
  ├── Persistence Intent
  └── Required Side Effects
```

The test should verify only the behavior relevant to the use case.

---

# 7. Application Test Categories

Application tests should be organized into several categories.

| Category                    | Purpose                                          |
| --------------------------- | ------------------------------------------------ |
| Command tests               | Verify state-changing use cases                  |
| Query tests                 | Verify application-level data retrieval behavior |
| Workflow tests              | Verify multi-step orchestration                  |
| Authorization-context tests | Verify correct context propagation               |
| Transaction tests           | Verify atomic application behavior               |
| Side-effect tests           | Verify notifications/events/jobs                 |
| Error-path tests            | Verify controlled failure behavior               |
| Idempotency tests           | Verify repeated requests where applicable        |
| Retry tests                 | Verify retry-safe behavior where applicable      |

---

# 8. Command Use-Case Testing

Commands change business state.

Examples:

* create order;
* pay order;
* refund order;
* close cash session;
* update recipe;
* adjust inventory;
* change price.

Command tests should verify:

1. required state is loaded;
2. application preconditions are evaluated;
3. correct domain operation is invoked;
4. resulting state is persisted;
5. required side effects are triggered;
6. result is returned correctly;
7. failure does not leave an invalid application state.

---

# 9. Query Use-Case Testing

Queries retrieve information without intentionally changing business state.

Examples:

* get order;
* list active products;
* retrieve inventory;
* retrieve branch report;
* retrieve employee list;
* retrieve menu;
* retrieve subscription status.

Query tests should verify:

* correct context;
* correct filtering;
* correct scope;
* required data loading;
* pagination behavior where applicable;
* empty result behavior;
* not-found behavior;
* result mapping;
* sensitive data boundaries.

Detailed API contract behavior is tested in TEST-07.

---

# 10. Application Context

Many FastFood use cases require context such as:

```text id="5jrx9k"
Identity
Business
Branch
Role
Permissions
Device
Session
Subscription State
```

Application tests must verify that the use case receives and uses the correct context.

Example:

```text id="g6h1q8"
Given:
- employee belongs to Branch A
- request context is Branch A

When:
- employee performs a branch operation

Then:
- the use case operates within Branch A
```

The complete security model is tested in TEST-14.

---

# 11. Tenant and Business Context

Every business-scoped use case must operate against the correct business context.

Tests should verify:

* business context is required where applicable;
* resources are resolved within the correct business;
* missing business context is rejected;
* mismatched business resources are rejected;
* queries do not silently fall back to another business.

Example:

```text id="j4nq0c"
Business A
   │
   ├── Branch 1
   └── Branch 2

Business B
   │
   └── Branch 1
```

A use case executing under Business A must not accidentally operate on Business B resources.

Detailed isolation testing belongs to TEST-14.

---

# 12. Branch Context

Branch-specific operations must receive explicit branch context when required.

Tests should cover:

* valid branch context;
* missing branch context;
* unauthorized branch context;
* branch-specific resource lookup;
* global resource lookup;
* branch override behavior;
* multi-branch Owner operations where allowed.

The application layer must not infer a branch from arbitrary client input when authoritative context is already available.

---

# 13. Application-Level Authorization Testing

Authorization testing is primarily defined in TEST-14, but use-case tests should verify that authorization is correctly enforced at the application boundary.

Example:

```text id="m5s7xz"
Given:
- employee lacks refund permission

When:
- Refund Order use case is executed

Then:
- refund operation is rejected
- domain mutation does not occur
- unauthorized side effects do not occur
```

The test verifies the use-case boundary.

The complete permission matrix and privilege-escalation testing are defined in TEST-14.

---

# 14. Application Validation

Application validation concerns conditions required before invoking domain behavior.

Examples:

* required identifier exists;
* required resource can be loaded;
* required business context exists;
* required branch context exists;
* request is not duplicated where idempotency applies;
* required dependency is available;
* required application precondition is satisfied.

Application validation must not replace domain validation.

For example:

```text id="f2v8r9"
Application:
Order exists.
```

Domain:

```text id="c6y2ka"
Completed order cannot be refunded outside the permitted refund rules.
```

Both may be tested at their appropriate levels.

---

# 15. Resource Loading Tests

Many use cases follow:

```text id="x8w1y4"
Load Resource
      ↓
Validate Context
      ↓
Execute Domain Behavior
      ↓
Persist Result
```

Tests should verify behavior when the resource is:

* found;
* not found;
* archived;
* inactive;
* outside the current business;
* outside the current branch;
* invalid for the requested operation.

The application layer must not convert a missing resource into a misleading successful result.

---

# 16. Domain Invocation Tests

Application tests should verify that the correct domain operation is executed.

For example:

```text id="e2v4n7"
RefundOrderUseCase
       │
       ▼
Order
       │
       ▼
refund(...)
       │
       ▼
Application persists result
```

The test should verify the business outcome rather than the exact internal call sequence unless call order itself is a business requirement.

---

# 17. Repository Coordination

Application use cases often coordinate repositories.

Example:

```text id="q7y5w2"
Order Repository
Inventory Repository
Payment Repository
Audit/Event Boundary
```

Application tests should verify that:

* required resources are loaded;
* correct resources are changed;
* unrelated resources are not changed;
* persistence occurs when required;
* no persistence occurs after a rejected operation;
* transaction boundaries protect multi-resource state where required.

Database behavior itself belongs to TEST-06.

---

# 18. Transaction Boundary Testing

When one use case modifies multiple persistent resources, application tests must verify the intended atomicity.

Example:

```text id="m1f6c8"
Create Order
   │
   ├── Create order state
   ├── Create order items
   ├── Reserve/consume required inventory
   └── Record required business event
```

If a failure occurs at a required atomic point:

```text id="w5z0de"
Either:
    complete required atomic state
or:
    leave the transaction in the defined safe state
```

Tests should verify that partial application state is not accepted where atomicity is required.

Detailed database transaction behavior is covered by TEST-06.

---

# 19. Side-Effect Testing

Application use cases may trigger side effects such as:

* notifications;
* audit events;
* background jobs;
* synchronization events;
* print jobs;
* cache invalidation;
* external integration requests.

Application tests should verify whether these side effects are:

* required;
* optional;
* synchronous;
* asynchronous;
* retryable;
* safely repeatable.

Example:

```text id="j2p8wq"
Close Cash Session
       │
       ├── Persist close result
       ├── Create required report state
       └── Notify Owner
```

The test should verify the required business outcome without depending unnecessarily on the actual notification provider.

---

# 20. Side-Effect Failure Testing

Side-effect failure requires an explicit policy.

For example:

```text id="e5r3nk"
Core business transaction succeeds
        │
        └── Notification fails
```

The application behavior must follow the defined architecture.

Possible policies include:

* business operation remains successful and notification is retried;
* business operation is considered incomplete;
* failure is recorded for recovery.

The test must verify the approved policy rather than assume that every side-effect failure should roll back the business transaction.

---

# 21. Event and Background Job Testing

If a use case schedules background work, application tests should verify:

* required event/job is created;
* correct business context is included;
* correct resource identity is included;
* duplicate scheduling behavior is defined;
* retry behavior is safe;
* invalid context is not propagated.

Example:

```text id="n6b8qa"
Order completed
      ↓
OrderCompleted event/job
      ↓
Background processing
```

The actual worker behavior is tested separately.

---

# 22. Notification Testing

Notifications are application-level side effects.

Tests should verify:

* notification is generated when required;
* correct recipient category is selected;
* correct business/branch context is associated;
* duplicate notifications are controlled where required;
* sensitive information is not unintentionally exposed;
* notification failure follows the defined failure policy.

Examples include:

* subscription ending;
* cash shortage;
* large refund;
* inventory discrepancy;
* branch loss;
* salary due.

---

# 23. Idempotency Testing

Use cases that may safely receive repeated requests must define their idempotency behavior.

Examples:

* payment submission;
* refund submission;
* synchronization;
* external callback processing;
* order acceptance;
* background job dispatch.

Test:

```text id="c4x7zm"
First request
    ↓
Business operation succeeds

Second equivalent request
    ↓
No duplicate business effect
```

Idempotency keys and transport-level details are covered by API and integration documents where applicable.

The application layer must still preserve business idempotency.

---

# 24. Repeated Use-Case Execution

Every critical command should be evaluated for repeated execution.

Possible outcomes:

1. second execution is rejected;
2. second execution returns the existing result;
3. second execution is safely ignored;
4. second execution performs a new valid operation.

The correct behavior depends on the use case.

Tests must encode the approved business behavior.

---

# 25. Error Mapping

Application errors should be distinguishable by category.

Typical categories include:

```text id="p4k9tx"
Validation Error
Not Found
Authorization Failure
Business Rule Rejection
Conflict
Dependency Failure
Infrastructure Failure
```

Application tests should verify that the use case produces the correct application-level error.

HTTP status mapping belongs to API testing.

---

# 26. No Partial Success

A use case must not report success when its required business outcome was not achieved.

Example:

```text id="f7r2sa"
Inventory adjustment:
- required stock update failed
- use case must not report successful adjustment
```

Likewise:

```text id="n2q8wl"
Refund:
- required refund state was not persisted
- use case must not report completed refund
```

The exact atomicity boundary depends on the use case.

---

# 27. Order Use-Case Testing

Important order use cases may include:

```text id="x7p2m4"
Create Order
Accept Order
Update Order Status
Add Item
Remove Item
Modify Item
Pay Order
Cancel Order
Complete Order
Archive Order
```

Tests should verify:

* correct business context;
* correct branch context;
* resource availability;
* domain rule invocation;
* persistence;
* required side effects;
* rejection behavior;
* duplicate operation behavior.

Detailed POS workflows belong to TEST-09.

---

# 28. Cash Use-Case Testing

Cash-related application use cases may include:

* open register;
* close register;
* handover;
* recount;
* correction;
* privileged reopen.

Tests should verify:

```text id="u8q3x1"
Application Context
      ↓
Cash Session Lookup
      ↓
Permission/Eligibility
      ↓
Domain Operation
      ↓
Persistence
      ↓
Required Notification/Report
```

A use case must not bypass the cash-session domain rules defined in TEST-04.

Detailed financial testing belongs to TEST-12.

---

# 29. Inventory Use-Case Testing

Inventory application tests should verify coordination between:

* product;
* recipe;
* inventory;
* branch;
* stock movement;
* purchase/adjustment operation.

Example:

```text id="r5k7v2"
Order completion
      ↓
Load recipe
      ↓
Determine required stock
      ↓
Execute domain inventory operation
      ↓
Persist result
```

The domain tests establish inventory correctness.

The application tests verify that the correct domain operations are coordinated.

Detailed inventory testing belongs to TEST-13.

---

# 30. Recipe Use-Case Testing

Recipe application workflows may include:

```text id="s8m3q1"
Create Recipe
      ↓
Edit Recipe
      ↓
Submit for Approval
      ↓
Approve
      ↓
Activate
```

Tests should verify:

* correct actor context;
* correct resource scope;
* required approval workflow;
* persistence;
* active version selection;
* archive/version coordination;
* required notifications/events.

The exact recipe business rules remain in domain tests.

---

# 31. Employee and Permission Use Cases

Examples:

* create employee;
* assign role;
* assign branch;
* modify permissions;
* create role template;
* update selected employee permissions.

Application tests should verify:

* correct employee context;
* correct Owner/Manager authority;
* selected target scope;
* correct application operation;
* resulting state;
* required audit/notification side effects.

Detailed authorization testing belongs to TEST-14.

---

# 32. Subscription Use-Case Testing

Examples:

* create subscription;
* change tariff;
* renew subscription;
* expire subscription;
* reactivate subscription;
* evaluate capability availability.

Tests should verify:

```text id="k1x8v5"
Subscription State
      ↓
Application Capability Decision
      ↓
Allowed / Restricted
```

The application layer must not silently treat expired functionality as active.

The underlying subscription domain rules are tested in TEST-04.

---

# 33. Offline Application Use Cases

Offline-supported use cases require additional application tests.

Tests should verify:

* offline-supported operation is accepted;
* unsupported operation is rejected;
* local context is valid;
* operation metadata is preserved;
* operation is safe for later synchronization;
* duplicate synchronization does not create duplicate business effects;
* rejected synchronization does not silently become successful.

Detailed synchronization testing is defined in TEST-10.

---

# 34. Application Testing and Concurrency

Application tests may verify basic consistency expectations, but dedicated race-condition testing belongs to TEST-11.

For example:

Application test:

```text id="r8d3m1"
Refund use case rejects an already fully refunded order.
```

Concurrency test:

```text id="y3m7p2"
Two refund requests execute concurrently
and cannot both consume the same refundable balance.
```

The second requires concurrency-focused testing.

---

# 35. Query Result Testing

Query use cases should verify:

* correct result shape at the application level;
* correct business filtering;
* correct scope;
* correct ordering where business-relevant;
* empty results;
* missing resources;
* archived vs active state;
* derived totals;
* report calculations where owned by the application layer.

Query tests should also verify that read operations do not accidentally mutate business state.

---

# 36. Reporting Use Cases

Reports often aggregate data from multiple domains.

Application tests should verify:

* correct date range;
* correct business context;
* correct branch scope;
* correct staff scope;
* correct inclusion/exclusion rules;
* correct aggregation orchestration;
* correct empty-state behavior;
* correct historical state usage.

The underlying repository/query implementation is covered by TEST-06.

---

# 37. Import Use-Case Testing

Import workflows should be tested at the application level for:

* permission/context validation;
* file/resource acceptance;
* parsing result coordination;
* validation result handling;
* partial/failed import policy;
* duplicate handling;
* domain operation invocation;
* transaction behavior;
* import summary/result.

File security and detailed file validation belong to the Security architecture.

---

# 38. Export Use-Case Testing

Export workflows should verify:

* authorization context;
* business/branch scope;
* requested data range;
* filtering;
* generated output intent;
* large export handling;
* asynchronous job creation where applicable;
* failure handling;
* audit requirements.

The actual file-generation implementation belongs to the relevant infrastructure/application component.

---

# 39. Application Test Data

Application tests should use explicit business scenarios.

Example:

```text id="j5q9x1"
Business:
Restaurant A

Branch:
Branch 1

Employee:
Cashier

Order:
Open

Inventory:
Available

Subscription:
Active
```

The test should make important preconditions visible.

Avoid large fixtures that contain unrelated state.

---

# 40. Application Test Doubles

Application tests may use:

* repository fakes;
* service stubs;
* external-service mocks;
* event collectors;
* notification test doubles;
* clock abstractions;
* job collectors.

Selection should follow TEST-03.

A test double should model the dependency behavior necessary for the use case.

It should not become a second implementation of the production system.

---

# 41. Application Test Independence

Application tests must be independent.

They must not rely on:

* execution order;
* shared mutable application state;
* previous test results;
* external production services;
* uncontrolled system time;
* random external data.

Each test establishes its own application context and required state.

---

# 42. Application Test Naming

Names should describe use-case behavior.

Prefer:

```text id="v5r2m8"
creates_order_and_persists_required_state
```

```text id="q8n4s1"
rejects_refund_when_employee_lacks_required_permission
```

```text id="m6x9p3"
does_not_persist_order_when_domain_validation_fails
```

```text id="a7k2w5"
publishes_required_notification_after_successful_cash_closure
```

```text id="c9f3z6"
does_not_duplicate_refund_when_same_request_is_replayed
```

Avoid implementation-only names.

---

# 43. Failure Scenario Matrix

Critical use cases should maintain a failure matrix.

| Failure                       | Expected Application Behavior       |
| ----------------------------- | ----------------------------------- |
| Resource missing              | Return controlled not-found result  |
| Wrong business                | Reject                              |
| Wrong branch                  | Reject                              |
| Authorization failure         | Reject before mutation              |
| Domain rejection              | No invalid persistence              |
| Repository failure            | Defined failure behavior            |
| Transaction failure           | No invalid partial state            |
| Notification failure          | Follow approved side-effect policy  |
| Job dispatch failure          | Follow retry/recovery policy        |
| Duplicate request             | Follow use-case idempotency policy  |
| Invalid subscription state    | Restrict operation                  |
| Unsupported offline operation | Reject or defer according to policy |

---

# 44. Application Workflow Testing

For multi-step workflows, tests should verify the business sequence.

Example:

```text id="t7m2x9"
Recipe Change
    │
    ▼
Validate Context
    │
    ▼
Load Current Recipe
    │
    ▼
Apply Domain Change
    │
    ▼
Create New Version
    │
    ▼
Submit/Require Approval
    │
    ▼
Persist
    │
    ▼
Notify Required Actors
```

Tests should not unnecessarily assert every internal function call.

They should assert the observable application outcome and required boundaries.

---

# 45. Application Test Depth

Not every use case requires the same depth.

High-risk use cases require stronger testing.

### Highest priority

* payment;
* refund;
* cash close;
* cash correction;
* inventory deduction;
* recipe activation;
* permission changes;
* subscription transitions;
* synchronization;
* destructive/archive operations.

### Medium priority

* normal CRUD operations;
* reports;
* menu configuration;
* employee configuration.

### Lower-risk

* simple read-only queries with limited business logic.

Risk-based prioritization follows TEST-02.

---

# 46. Regression Testing

Every confirmed application-level defect should result in a regression test where practical.

Example:

```text id="w4p8k2"
Defect:
Refund was persisted but required notification was not scheduled.

Regression:
Given a successful refund,
Then the required notification intent must exist.
```

Regression tests should be placed at the lowest reliable test level.

If the defect is purely application orchestration, the regression should normally be an application test.

---

# 47. Application Testing and End-to-End Testing

Application tests provide fast evidence for use-case behavior.

End-to-end tests verify that the complete system can execute the workflow.

Example:

Application:

```text id="p8w3m5"
Refund use case
→ authorization
→ domain operation
→ persistence
→ notification intent
```

End-to-end:

```text id="x6r2k9"
Cashier UI
→ API
→ application
→ domain
→ database
→ resulting UI/report
```

Application tests should cover the majority of orchestration behavior so that E2E tests remain focused on critical real workflows.

---

# 48. Application Testing and Integration Testing

Application tests may isolate repositories and external services.

Integration tests verify that the actual components work together.

For example:

```text id="b7n4q1"
Application Test:
Use case + repository test double

Integration Test:
Use case + real PostgreSQL repository
```

Both provide different evidence.

Integration testing is defined in TEST-08 and TEST-06.

---

# 49. Application Test Quality Rules

A high-quality application test should:

* have a clear use-case purpose;
* establish explicit context;
* contain meaningful business state;
* verify the application outcome;
* verify important side effects;
* verify failure behavior;
* avoid unnecessary implementation coupling;
* remain deterministic;
* execute quickly enough for regular CI;
* remain understandable to future maintainers.

---

# 50. Anti-Patterns

The following patterns are prohibited or strongly discouraged.

## 50.1 Reimplementing the Domain

Application tests must not duplicate domain calculations merely to compare results.

---

## 50.2 Testing Only Successful Execution

A use case is not sufficiently tested if only the happy path is covered.

---

## 50.3 Verifying Every Internal Call

Over-specifying every repository/service call makes tests fragile.

Verify behavior and important interaction boundaries.

---

## 50.4 Using Real External Services

Application tests should not depend on production payment, notification, messaging, or third-party services.

---

## 50.5 Hidden Global State

Shared mutable state creates unreliable application tests.

---

## 50.6 Treating API Tests as Application Tests

HTTP status codes and JSON schema belong to API testing.

Application tests should operate at the application boundary.

---

## 50.7 Treating E2E as the Only Evidence

Critical orchestration should be covered before reaching E2E.

---

# 51. Mandatory Application Testing Rules

The following rules are mandatory:

1. Every critical use case must have application-level tests.
2. Use-case tests must verify successful execution.
3. Critical use cases must also test relevant failure paths.
4. Application tests must preserve the business context.
5. Business/tenant context must be tested where applicable.
6. Branch context must be tested where applicable.
7. Authorization decisions must be tested at the application boundary.
8. Domain rules must remain owned by domain tests.
9. Required persistence behavior must be verified.
10. Required transaction boundaries must be tested.
11. Required side effects must be tested.
12. Side-effect failure behavior must be explicitly defined and tested where relevant.
13. Critical repeated requests must have defined idempotency behavior.
14. Application tests must not rely on production external services.
15. Application tests must remain deterministic.
16. Confirmed application defects should produce regression tests where practical.
17. High-risk financial, inventory, cash, permission, subscription, and synchronization use cases require stronger test depth.
18. A use case must never report success when its required business outcome was not achieved.
19. Application tests must not bypass domain rules.
20. Application tests must not replace integration and end-to-end tests where real boundaries must be verified.

---

# 52. Application Testing Invariants

The application testing architecture must preserve these invariants:

```text id="h6x2p8"
A use case operates within an explicit business context.
```

```text id="r3m7k1"
Branch-scoped operations use the correct branch context.
```

```text id="z8q4v6"
Unauthorized operations do not produce business mutations.
```

```text id="m2f9w5"
Domain rules remain authoritative for business invariants.
```

```text id="c7n1x4"
Required application state changes are persisted consistently.
```

```text id="p5k8s2"
Required atomic operations do not report false success after failure.
```

```text id="v4q6j9"
Critical side effects follow their defined success and failure policy.
```

```text id="a1w7e3"
Repeated requests follow the defined idempotency behavior.
```

```text id="n9r5b2"
Application failures do not silently create invalid business state.
```

```text id="t3y8m6"
Application tests verify orchestration without reimplementing domain rules.
```

---

# 53. Acceptance Criteria

This document is considered correctly implemented when:

* application/use-case testing has a clear boundary from domain testing;
* command and query use cases have defined testing responsibilities;
* business and branch context are explicitly testable;
* application-level authorization behavior is testable;
* repository coordination is testable;
* transaction boundaries are testable;
* side effects and their failure policies are testable;
* idempotency behavior is testable for applicable use cases;
* failure paths are treated as first-class behavior;
* critical FastFood workflows have application-level testing expectations;
* application tests do not duplicate domain rules;
* application tests do not replace database, integration, API, security, or E2E testing;
* high-risk use cases receive risk-based additional coverage.

---

# 54. Relationship to the Testing Architecture

```text id="d4q8x7"
TEST-01
Testing Architecture Overview
        │
        ▼
TEST-02
Testing Strategy and Test Pyramid
        │
        ▼
TEST-03
Unit Testing Architecture
        │
        ▼
TEST-04
Domain Testing Architecture
        │
        ▼
TEST-05
Application and Use-Case Testing
        │
        ├── TEST-06 Repository / Database Integration
        ├── TEST-07 API Contract / Schema
        ├── TEST-08 Integration Testing
        ├── TEST-09 End-to-End / POS
        ├── TEST-10 Offline / Synchronization
        ├── TEST-11 Concurrency / Consistency
        ├── TEST-12 Financial / Cash
        ├── TEST-13 Inventory / Recipe
        └── TEST-14 Authentication / Authorization
```

The responsibility boundary is:

```text
TEST-03
How isolated tests are constructed
        ↓
TEST-04
Whether business rules are correct
        ↓
TEST-05
Whether use cases correctly orchestrate those rules
        ↓
TEST-06/08
Whether real technical boundaries work together
        ↓
TEST-09
Whether critical real user workflows work end-to-end
```

---

# 55. Final Rule

Application testing must prove that the system correctly turns an application request into a complete and valid business operation.

A sufficiently tested use case provides evidence that:

```text id="k7p2m9"
The correct context is established.
The correct authorization boundary is applied.
Required state is loaded.
Domain behavior is invoked correctly.
Required state changes are persisted.
Required side effects are coordinated.
Failures are handled according to policy.
Repeated operations follow defined behavior.
The use case never reports false success.
```

The domain layer proves that business rules are correct.

The application layer proves that those rules are **correctly orchestrated into real business use cases**.

