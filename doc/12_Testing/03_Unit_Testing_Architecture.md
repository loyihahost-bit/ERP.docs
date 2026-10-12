# Unit Testing Architecture

**Document ID:** TEST-03
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`

---

## 1. Purpose

This document defines the architecture and standards for unit testing in the FastFood ERP system.

It establishes:

* what qualifies as a unit test;
* unit test boundaries;
* test structure;
* isolation requirements;
* dependency control;
* mocks, stubs, fakes, and spies;
* deterministic testing;
* test data design;
* assertion quality;
* error and edge-case testing;
* test naming and organization;
* unit test maintainability;
* when a behavior belongs in unit testing and when it belongs at a higher testing level.

This document is a detailed implementation-independent policy.

It does not define a specific programming language, test framework, mocking library, or project directory implementation.

---

# 2. Unit Testing Role

Unit tests form the fastest and most granular layer of the FastFood ERP testing architecture.

Their primary purpose is to verify small, deterministic units of behavior independently from external infrastructure.

Typical unit-test targets include:

* domain calculations;
* business-rule evaluators;
* validators;
* state-transition logic;
* authorization policies;
* transformation functions;
* parsers;
* deterministic utility logic;
* data mapping logic;
* decision logic;
* pure application policies.

Unit tests should provide immediate feedback when a local behavior changes.

---

# 3. Definition of a Unit

A unit is the smallest practical component whose behavior can be meaningfully verified in isolation.

A unit may be:

* a function;
* a method;
* a domain object;
* a policy;
* a validator;
* a calculator;
* a small cohesive service.

A unit is defined by behavioral responsibility rather than by code size.

A large function that performs several unrelated responsibilities is not automatically a good unit simply because it is technically one function.

Likewise, several small functions may be tested together when they form one cohesive behavior.

---

# 4. Unit Test Boundary

A unit test should normally isolate the unit from:

* PostgreSQL;
* Redis;
* message queues;
* external APIs;
* file storage;
* physical printers;
* network services;
* operating-system services;
* real clocks where time is controllable;
* random external state;
* real authentication providers;
* real third-party services.

The unit itself should remain real.

Dependencies may be replaced by controlled test doubles when required.

```text
┌──────────────────────────────┐
│          Unit Test            │
│                              │
│   Real Unit Under Test       │
│          │                   │
│   ┌──────▼──────┐            │
│   │ Controlled  │            │
│   │ Dependencies│            │
│   └─────────────┘            │
│                              │
│ No external infrastructure   │
└──────────────────────────────┘
```

---

# 5. Unit Test Independence

A unit test must not depend on another unit test.

Tests must be independently executable.

A test should not require:

* another test to run first;
* a shared mutable result from another test;
* a previous database state;
* a previously created file;
* a previous authentication session;
* a global counter left by another test.

Test execution order must not determine correctness.

---

# 6. Isolation Requirements

Unit tests must isolate relevant external state.

The following should normally be controlled:

| Dependency              | Unit-Test Strategy                                 |
| ----------------------- | -------------------------------------------------- |
| Database                | Replace with test double                           |
| Redis                   | Replace with test double                           |
| Queue                   | Replace with controlled fake/mock                  |
| External API            | Replace with controlled double                     |
| File system             | Use controlled abstraction or in-memory substitute |
| Printer                 | Replace with printer abstraction double            |
| Clock                   | Inject controlled time                             |
| Randomness              | Inject deterministic source                        |
| Authentication provider | Replace with controlled test dependency            |
| Configuration           | Provide explicit test configuration                |

Isolation must not hide behavior that belongs to an integration test.

---

# 7. Unit Test Structure

Unit tests should follow a consistent conceptual structure:

```text
Arrange
   ↓
Act
   ↓
Assert
```

### Arrange

Prepare:

* inputs;
* unit state;
* controlled dependencies;
* expected conditions.

### Act

Execute the behavior being tested.

### Assert

Verify the observable result.

A test may contain additional preparation or verification when necessary, but the primary behavior should remain clear.

---

# 8. One Primary Behavior per Test

A unit test should normally verify one primary behavior.

This does not mean every test can contain only one assertion.

Multiple assertions are acceptable when they verify different aspects of the same behavior.

Good:

```text
Given a valid order
When the price is calculated
Then subtotal is correct
And discount is applied
And final total is correct
```

Less desirable:

```text
One test creates an order,
changes permissions,
updates inventory,
opens cash,
and verifies payroll.
```

Such a test is difficult to diagnose and belongs at a higher level or should be split into focused unit tests.

---

# 9. Behavior-Oriented Testing

Unit tests should describe behavior rather than implementation structure.

Prefer:

```text
should_reject_order_when_required_ingredient_is_missing
```

over:

```text
should_call_validate_inventory_method
```

The first verifies a business behavior.

The second primarily verifies an implementation detail.

Implementation-detail tests become fragile during safe refactoring.

---

# 10. Test Naming

Test names should communicate:

1. the condition;
2. the action;
3. the expected result.

Conceptually:

```text
should_<expected_behavior>_when_<condition>
```

Examples:

```text
should_reject_negative_quantity

should_apply_discount_when_order_meets_discount_rule

should_block_sale_when_required_stock_is_missing

should_allow_cash_close_when_balance_matches

should_reject_refund_without_required_permission

should_not_accept_expired_offline_operation
```

Exact naming syntax may follow the project's implementation language and testing framework.

---

# 11. Input Partitioning

Unit tests should cover meaningful input categories rather than only random examples.

For a quantity validator:

```text
Valid
0
Negative
Very Large
Non-Numeric
Missing
Boundary Value
```

The exact valid/invalid categories depend on the business rule.

Testing should focus on meaningful partitions.

---

# 12. Boundary Value Testing

Boundary values are especially important for business rules.

Examples:

* minimum allowed quantity;
* maximum allowed quantity;
* zero;
* first valid value;
* last valid value;
* expiration boundary;
* discount threshold;
* stock threshold;
* correction limit.

Example:

```text
Correction Limit = 3

Tests:
0 corrections
1 correction
2 corrections
3 corrections
4th correction
```

The test should verify the defined business behavior at and around the boundary.

---

# 13. Business Rule Testing

Business rules should be tested with explicit examples.

For example, if a sale requires all required recipe ingredients:

```text
All ingredients available
→ Sale allowed

One required ingredient unavailable
→ Sale blocked
```

The unit test should verify the rule directly.

It should not require a complete POS workflow to prove this simple business invariant.

---

# 14. Domain Invariants

Unit tests are an important first line of protection for domain invariants.

Examples:

### Inventory

```text
Negative stock is not permitted.
```

### Order

```text
Invalid state transitions are rejected.
```

### Cash

```text
A closed cash session cannot accept normal new cash operations.
```

### Permissions

```text
A permission evaluation cannot grant an unauthorized capability.
```

### Discounts

```text
A discount cannot violate the defined pricing rules.
```

The domain layer may require additional integration and E2E verification, but the invariant should be directly tested at the lowest appropriate level.

---

# 15. Dependency Injection and Testability

Where architecture uses dependencies, they should be replaceable without modifying the behavior under test.

Examples:

```text
Clock
Random ID Generator
Repository
Permission Provider
Inventory Provider
Exchange / Pricing Provider
Notification Sender
External Service Client
```

The unit should depend on an abstraction or controlled boundary where necessary.

Unit testing must not require production infrastructure merely to construct a simple business object.

---

# 16. Mocking Strategy

Mocks are allowed but should be used carefully.

A mock is useful when the test needs to control or verify an interaction with a dependency.

However:

> Mocking is a means of isolation, not a substitute for testing the real dependency.

Mock-heavy tests can create false confidence if the mocked behavior differs from the real system.

---

# 17. Mock Usage Rules

Mocks should normally be used when:

* the dependency is external;
* the dependency is slow;
* the dependency is nondeterministic;
* the dependency is unavailable in unit execution;
* the unit must test a specific failure;
* the unit must verify an interaction contract.

Mocks should not be used merely because a real dependency is inconvenient when the behavior actually belongs to integration testing.

---

# 18. Mocking Internal Implementation Details

Excessive mocking of internal components should be avoided.

For example, a test should not become:

```text
Call method A
→ verify A called B
→ verify B called C
→ verify C called D
```

if the actual business requirement is simply:

```text
Given X
When operation occurs
Then result Y is produced
```

Tests should primarily verify observable behavior.

---

# 19. Stub vs Mock

The project should distinguish between the purpose of test doubles.

### Stub

Provides controlled input or output.

Example:

```text
Inventory Provider
→ returns "ingredient available"
```

### Mock

Primarily verifies expected interaction.

Example:

```text
Notification Sender
→ verify notification was requested
```

A test should use the simplest double that provides sufficient isolation.

---

# 20. Fake

A fake is a lightweight implementation used for testing.

Examples:

* in-memory repository;
* fake clock;
* fake message publisher;
* fake printer;
* fake external service.

Fakes are useful when a reusable test implementation is clearer and more stable than many individual mocks.

However, an in-memory fake database does not replace PostgreSQL integration testing.

---

# 21. Spy

A spy records interactions for later inspection.

Example:

```text
Notification Spy
→ records sent notifications
```

Spies are appropriate when the test needs to verify that an important side effect was requested.

They should not turn every internal method call into a test requirement.

---

# 22. Choosing a Test Double

Use the following preference:

```text
No Dependency
     ↓
Use Real Value

Simple Controlled Dependency
     ↓
Stub / Fake

Interaction Must Be Verified
     ↓
Mock / Spy

Real Infrastructure Behavior Required
     ↓
Integration Test
```

The test should use the least complex mechanism necessary.

---

# 23. Mock Verification Rules

When a mock is used, verify only interactions that are part of the meaningful contract.

Good:

```text
Refund requires an audit event.
→ Verify audit event was requested.
```

Weak:

```text
Verify private helper A called helper B
with exactly the same internal sequence.
```

The second test may break during harmless refactoring.

---

# 24. Avoid Overspecified Mocks

Mocks should not unnecessarily verify:

* exact internal call order;
* unrelated method calls;
* private implementation details;
* incidental logging;
* irrelevant parameter formatting.

Overspecified mocks increase maintenance cost.

A refactor that preserves business behavior should not require rewriting large numbers of unit tests.

---

# 25. External Service Failures

Unit tests should explicitly simulate external dependency failures when the unit has defined failure behavior.

Examples:

```text
External API Timeout
→ Expected controlled failure

Notification Service Failure
→ Business operation remains consistent

Printer Service Unavailable
→ Correct application response

Repository Failure
→ Transaction/application behavior handled correctly
```

The complete real failure behavior may additionally require integration or resilience testing.

---

# 26. Time Control

Time must not make unit tests nondeterministic.

Time-dependent behavior should use a controllable clock or equivalent abstraction when necessary.

Important examples:

* subscription expiration;
* session expiration;
* token validity;
* offline validity windows;
* payroll dates;
* cash session timestamps;
* synchronization timestamps.

Example:

```text
Given current time = T
And expiration = T + 1 day
When operation occurs at T + 1 day + 1 second
Then operation is expired
```

This is preferable to waiting for real time during a test.

---

# 27. Randomness Control

Random values should be controlled when they affect test outcomes.

Examples:

* generated identifiers;
* random retry delays;
* random tokens;
* sampling;
* AI test inputs where deterministic evaluation is required.

Tests should not fail because a random value happened to produce an unexpected scenario unless randomness itself is what is being tested.

---

# 28. ID Testing

The system may use multiple identifiers for different purposes.

Unit tests should verify identifier-related rules when they belong to the unit.

Examples:

* uniqueness assumptions;
* format validation;
* operation identity;
* idempotency identity;
* public vs internal identifiers.

Tests must not assume that a user-visible identifier is itself an authorization mechanism.

Security behavior belongs to the authorization and security testing layers.

---

# 29. Financial Unit Tests

Financial calculations should have strong unit coverage.

Examples:

* subtotal;
* discount;
* final total;
* refund amount;
* payroll calculation;
* percentage-based payment;
* bonus calculation;
* cash discrepancy calculation.

Example:

```text
Input:
Subtotal
Discount
Payment

Expected:
Correct final amount
```

These calculations should be tested independently from the database and UI.

Detailed financial integration testing is defined in `TEST-12`.

---

# 30. Inventory Unit Tests

Inventory calculations should be tested at unit/domain level where appropriate.

Examples:

* recipe quantity calculation;
* semi-finished dependency calculation;
* FIFO selection logic;
* shrink/loss calculation;
* threshold evaluation;
* required ingredient validation.

Example:

```text
Recipe:
1 kg meat
200 g mayonnaise

Requested production:
5 units

Expected ingredient requirement:
5 kg meat
1 kg mayonnaise
```

Actual database deduction must additionally be tested through repository and integration tests.

---

# 31. Recipe Unit Tests

Recipe tests should cover:

* valid recipe;
* missing components;
* invalid quantities;
* zero quantities where prohibited;
* negative quantities;
* nested semi-finished dependencies;
* yield/loss rules;
* recipe state;
* archived recipe restrictions;
* approval-related domain rules.

Unit tests verify calculations and domain behavior.

Persistence and approval workflow integration belongs to higher test levels.

---

# 32. Permission Unit Tests

Permission policies should have direct unit tests where the policy is represented as deterministic logic.

Examples:

```text
Owner + Branch A
→ Allowed

Employee + Branch B
→ Denied

Manager + Authorized Permission
→ Allowed

No Permission
→ Denied
```

The full server-side authorization boundary must additionally be tested at application/API/security levels.

---

# 33. State Transition Testing

State machines and lifecycle rules should be tested directly.

Example order lifecycle:

```text
Created
  ↓
Accepted
  ↓
Preparing
  ↓
Ready
  ↓
Completed
```

Tests should verify:

* valid transitions;
* invalid transitions;
* terminal states;
* repeated transitions;
* failure transitions;
* permission-dependent transitions where applicable.

---

# 34. Error Testing

Unit tests must verify meaningful error behavior.

Tests should cover:

* invalid input;
* invalid state;
* missing required data;
* unauthorized policy result where applicable;
* dependency failure;
* boundary violation;
* duplicate operation;
* unsupported operation.

Tests should verify the error contract rather than fragile implementation details.

---

# 35. Error Message Testing

Exact user-facing error text should only be asserted when the exact text is itself part of the contract.

Otherwise prefer assertions on:

* error type;
* error category;
* error code;
* failure state;
* safe response behavior.

This allows wording to change without breaking unrelated tests.

---

# 36. Collection and Ordering Tests

Where business behavior depends on ordering, tests must explicitly verify it.

Examples:

* FIFO inventory selection;
* priority ordering;
* report sorting;
* operation sequence;
* status ordering.

Where ordering is not part of the contract, tests should not unnecessarily require a particular order.

---

# 37. Null, Missing, and Empty Values

Tests should distinguish between:

* missing;
* null;
* empty;
* zero;
* false;
* invalid.

These values may have different business meanings.

The distinction must be tested when the domain or application behavior treats them differently.

---

# 38. Immutability and Mutation

Where business objects or state are expected to remain immutable, unit tests should verify that contract.

For example:

```text
Completed financial record
→ Cannot be silently mutated into a different financial state.
```

Where controlled mutation is permitted, tests should verify allowed transitions and prevent unintended mutation.

---

# 39. Side Effects

A unit test should identify meaningful side effects.

Examples:

* event creation;
* notification request;
* audit request;
* state change;
* repository update.

Tests should verify side effects when they are part of the unit's contract.

Incidental side effects should not be unnecessarily asserted.

---

# 40. Pure Functions

Pure deterministic functions should be tested directly.

Typical examples:

* price calculation;
* discount calculation;
* recipe calculation;
* quantity conversion;
* validation;
* status mapping.

Pure functions generally require no mocks.

They should form a large portion of the fast test layer.

---

# 41. Test Fixtures

Fixtures may be used to simplify repeated setup.

Fixtures should:

* be minimal;
* be explicit;
* avoid hidden state;
* remain reusable;
* not contain unnecessary fields;
* not create unrelated dependencies.

Large global fixtures should be avoided when small local fixtures are sufficient.

---

# 42. Test Builders and Factories

Builders or factories may be used for complex domain objects.

For example:

```text
OrderBuilder
EmployeeBuilder
RecipeBuilder
InventoryItemBuilder
CashSessionBuilder
```

Builders should provide sensible defaults while allowing tests to override only relevant fields.

A builder must not hide critical business conditions.

If a test depends on a specific permission or branch scope, that condition should remain visible in the test.

---

# 43. Fixture Data and Business Meaning

Test data should communicate business meaning.

Prefer:

```text
required_ingredient_missing
authorized_manager
closed_cash_session
expired_subscription
```

over opaque values that require investigation.

Good test data reduces the time required to understand a failed test.

---

# 44. Unit Test Organization

Tests should generally follow the system's logical ownership.

A conceptual organization may be:

```text
tests/
├── unit/
│   ├── domain/
│   ├── application/
│   ├── policies/
│   ├── calculations/
│   └── utilities/
```

The exact directory structure may be adjusted to the implementation architecture.

The important rule is that unit tests must remain distinguishable from integration and E2E tests.

---

# 45. Test Naming and Organization Must Follow Architecture

Test location should communicate architectural ownership.

For example:

```text
Domain Rule
→ Domain Unit Test

Application Policy
→ Application Unit Test

Repository
→ Repository / DB Integration Test

API Contract
→ API Contract Test

POS Workflow
→ E2E Test
```

A unit-test directory should not become a dumping ground for tests that require real infrastructure.

---

# 46. Unit Test Execution

Unit tests should normally be executable without:

* production database;
* external network;
* production credentials;
* deployed services;
* physical devices.

This makes them suitable for:

* local development;
* pre-commit validation;
* rapid CI stages;
* frequent execution.

---

# 47. Unit Test Performance

Unit tests should be fast enough to run frequently.

Slow unit tests often indicate:

* hidden infrastructure dependencies;
* excessive setup;
* excessive fixture size;
* unnecessary sleeps;
* expensive serialization;
* uncontrolled external calls.

When a test requires real infrastructure, it should normally be classified at the appropriate integration level instead of remaining incorrectly labeled as a unit test.

---

# 48. No Sleep-Based Synchronization

Unit tests should not use arbitrary waiting merely to make asynchronous behavior appear stable.

Avoid:

```text
perform action
→ sleep
→ check result
```

Prefer:

* deterministic synchronization;
* controlled fake time;
* explicit completion signals;
* direct invocation where appropriate.

Real asynchronous infrastructure belongs in integration or resilience testing.

---

# 49. Unit Testing Asynchronous Logic

Asynchronous application logic may still have unit tests if its dependencies can be controlled.

Tests should verify:

* successful completion;
* failure;
* cancellation;
* timeout behavior;
* duplicate invocation where relevant;
* correct result handling.

Actual queue or distributed-worker behavior belongs to integration and resilience testing.

---

# 50. Unit Tests and Transactions

Unit tests should not attempt to prove actual database transaction semantics.

They may verify that application logic requests the correct transactional operation.

Actual behavior such as:

* commit;
* rollback;
* isolation;
* constraint enforcement;
* concurrent transaction behavior

must be verified through database integration tests.

---

# 51. Unit Tests and Security

Unit tests can verify deterministic security policies.

Examples:

* permission evaluation;
* policy decisions;
* scope calculation;
* allowed/denied state.

However, unit tests cannot prove complete security isolation.

Security must also be tested at:

* application;
* API;
* database;
* integration;
* E2E

boundaries where applicable.

Detailed security testing:

`TEST-14 Authentication, Authorization and Security Testing`

---

# 52. Unit Tests and Offline Logic

Offline business logic can have unit tests for:

* operation validation;
* sequence calculation;
* expiration calculation;
* idempotency decision;
* conflict classification;
* retry policy.

Actual synchronization with the server must be tested at integration and E2E levels.

Detailed policy:

`TEST-10 Offline and Synchronization Testing`

---

# 53. Unit Tests and Concurrency

Unit tests may verify deterministic concurrency-related policies, such as:

* conflict classification;
* idempotency rules;
* retry decisions;
* version comparison.

They cannot prove actual database or distributed concurrency behavior.

Real race conditions require:

* integration tests;
* concurrency tests;
* database tests;
* performance/resilience tests where appropriate.

Detailed policy:

`TEST-11 Concurrency and Consistency Testing`

---

# 54. AI Unit Testing

AI-related deterministic components may have unit tests for:

* input validation;
* preprocessing;
* output parsing;
* threshold logic;
* result mapping;
* fallback behavior.

Actual model accuracy and inference behavior require specialized AI testing.

Detailed policy:

`TEST-16 AI Model and Inference Testing`

---

# 55. Frontend Unit Testing

Frontend components may have unit tests for:

* formatting;
* local validation;
* deterministic state logic;
* utility functions;
* isolated components.

Frontend unit tests must not be treated as proof of backend authorization.

Detailed policy:

`TEST-15 Frontend Testing Architecture`

---

# 56. Test Quality

A unit test is valuable only when its assertions can detect meaningful regressions.

Weak:

```text
function executes without exception
```

when the function is expected to produce a specific result.

Strong:

```text
Given defined input
When business operation executes
Then expected business result is produced
And invalid state is rejected
```

Tests should prove behavior rather than merely execute code.

---

# 57. Assertion Strategy

Assertions should be:

* specific;
* meaningful;
* stable;
* proportional to the behavior;
* understandable when failed.

Avoid overly broad assertions that make failures difficult to diagnose.

Prefer asserting the relevant result rather than the entire object when unrelated fields are not part of the behavior.

---

# 58. Snapshot Testing

Snapshot-style testing may be used when the output structure itself is meaningful and stable.

It should not be used as a replacement for explicit business assertions.

Large snapshots can hide important changes.

For critical financial, security, inventory, or authorization behavior, explicit assertions are preferred.

---

# 59. Randomized and Property-Based Unit Testing

Where suitable, property-based or randomized unit testing may be used for mathematical or invariant-heavy logic.

Examples:

* quantity conversions;
* financial calculations;
* recipe proportions;
* identifier properties;
* ordering invariants.

Randomized tests must remain reproducible by recording the relevant seed or equivalent diagnostic information when a failure occurs.

---

# 60. Mutation Testing

Mutation testing may be applied to important unit-tested logic.

It is particularly useful for:

* financial calculations;
* inventory calculations;
* authorization policies;
* state transitions;
* critical validation rules.

The objective is to determine whether tests fail when meaningful logic is intentionally changed.

---

# 61. Unit Test Failure Diagnosis

A unit-test failure should normally indicate a small area of responsibility.

A good unit test makes it easy to determine:

* what behavior failed;
* what input caused the failure;
* what was expected;
* what was produced.

If a test failure requires reconstructing a complete distributed workflow, the test may belong at a higher level.

---

# 62. Unit Test Maintenance

When production code is safely refactored without changing behavior:

> Unit tests should generally continue to pass.

Tests that fail merely because an internal method, helper, or call sequence changed should be reviewed for excessive coupling to implementation details.

Tests should change when behavior or contract changes, not merely because internal structure changes.

---

# 63. Regression Tests

When a unit-level defect is discovered, a regression test should be added at the lowest level capable of reliably reproducing the defect.

If the defect involves a higher boundary, an additional higher-level regression test may also be required.

Example:

```text
Calculation bug
→ Unit regression test

PostgreSQL transaction bug
→ Database integration regression test

API authorization bug
→ API/security regression test

Complete POS workflow bug
→ E2E regression test
```

---

# 64. Unit Test Anti-Patterns

The following patterns should be avoided.

### 64.1 Testing Private Implementation

Tests should not depend unnecessarily on private implementation details.

### 64.2 Mocking Everything

Excessive mocking creates false confidence.

### 64.3 Shared Mutable State

Tests must not depend on hidden global state.

### 64.4 Large Setup

Large setup often indicates the test is testing too much.

### 64.5 Arbitrary Sleeps

Timing-based synchronization creates flaky tests.

### 64.6 Exact Incidental Calls

Do not verify irrelevant internal call sequences.

### 64.7 Coverage-Only Assertions

Executing code without meaningful assertions is not useful coverage.

### 64.8 Real Production Services

Unit tests must not depend on production infrastructure.

### 64.9 Production Credentials

Unit tests must never require production credentials.

### 64.10 Hidden Business Conditions

Critical assumptions must remain visible in the test scenario.

---

# 65. Unit Test Decision Rules

When deciding whether a test is a unit test, ask:

1. Can the behavior execute without real infrastructure?
2. Can external dependencies be controlled?
3. Is the behavior small and cohesive?
4. Is the expected result deterministic?
5. Can the test run independently?
6. Does the test verify behavior rather than infrastructure?
7. Can it execute quickly?
8. Does it avoid production state?

If the answer is mostly yes, unit testing is appropriate.

If the behavior fundamentally depends on a real boundary, use the appropriate integration or higher-level test.

---

# 66. Unit Testing Balance

Unit tests should provide broad coverage of:

```text
Business Calculations
Domain Rules
Validation
State Transitions
Policy Decisions
Deterministic Transformations
Edge Cases
Error Conditions
```

They should not attempt to replace:

```text
Database Tests
API Contract Tests
Integration Tests
E2E Tests
Performance Tests
Resilience Tests
Security Boundary Tests
```

The testing pyramid depends on these layers working together.

---

# 67. Unit Testing and Release Gates

Unit tests form an early and mandatory quality gate.

A normal code change should not proceed through the pipeline with known failing unit tests unless an explicitly approved exception mechanism exists.

Critical unit-test failures involving:

* financial rules;
* inventory rules;
* security policies;
* authorization;
* data integrity;
* core state transitions

should be treated as release-blocking failures.

Detailed CI policy:

`TEST-19 CI Quality Gates and Release Testing`

---

# 68. Unit Testing and Code Review

Code review should consider whether new or changed behavior has appropriate unit coverage.

Review questions include:

* What behavior changed?
* What business rule changed?
* What edge cases exist?
* What failure cases exist?
* Is the test at the correct level?
* Is the test isolated?
* Are mocks necessary?
* Does the test assert behavior?
* Is a higher-level test also required?

---

# 69. Unit Testing Invariants

The following rules are mandatory.

1. Unit tests must be independently executable.
2. Unit tests must not depend on production infrastructure.
3. The unit under test must remain real.
4. External dependencies must be controlled where isolation requires it.
5. Mocking must not replace required integration testing.
6. Tests should verify behavior rather than implementation details.
7. Tests should be deterministic where practical.
8. Time and randomness must be controllable when they affect test outcomes.
9. Shared mutable state must not influence test results.
10. Business invariants must be directly tested at the lowest appropriate level.
11. Boundary values must be tested where business behavior changes at boundaries.
12. Invalid and failure conditions must be tested.
13. Critical calculations require meaningful assertions.
14. Financial and inventory rules require strong unit/domain coverage.
15. Authorization policies may be unit-tested, but unit tests do not prove complete authorization security.
16. Offline logic may be unit-tested, but unit tests do not prove synchronization correctness.
17. Database transaction behavior must be verified through database integration tests.
18. External service behavior must be verified through appropriate integration tests.
19. Test doubles must be simpler than the real dependency where practical.
20. Mocks must not unnecessarily couple tests to internal call sequences.
21. Fixtures must remain controlled and understandable.
22. Test failures must be diagnosable.
23. Flaky tests must be investigated rather than permanently ignored.
24. Refactoring without behavior change should not require widespread test rewrites.
25. Unit tests must remain fast enough for frequent execution.
26. Unit tests must never require production credentials or production data.
27. Unit tests must not be treated as proof of complete system correctness.
28. Critical unit-test failures must participate in release quality gates.

---

# 70. Acceptance Criteria

This document is accepted when:

* the definition and boundary of a unit test are clear;
* unit-test isolation rules are defined;
* Arrange–Act–Assert structure is established;
* test naming and organization principles are defined;
* mocks, stubs, fakes, and spies are distinguished;
* mocking rules prevent excessive implementation coupling;
* time and randomness can be controlled;
* business invariants and boundary conditions are addressed;
* financial, inventory, permission, and state-transition logic have clear unit-testing expectations;
* database, API, integration, E2E, performance, and resilience boundaries are clearly separated;
* test data and fixture principles are defined;
* flaky and slow unit tests have defined handling;
* regression and mutation-testing expectations are established;
* unit tests are connected to CI and release gates;
* the document remains implementation-independent while providing enough architectural guidance for implementation.

---

# 71. Final Unit Testing Rule

The FastFood ERP unit-testing architecture follows one central rule:

> **A unit test must isolate a meaningful piece of behavior, control its external dependencies, verify observable results, and execute quickly enough to provide continuous feedback.**

Mocks and test doubles exist to support isolation, not to create an artificial system in which every dependency is assumed to work.

The resulting model is:

```text
Real Unit
   +
Controlled Dependencies
   +
Deterministic Inputs
   +
Meaningful Assertions
   +
Focused Failure Cases
   =
Reliable Unit Test
```

Unit testing provides the foundation of the testing pyramid, but it must remain connected to domain, integration, security, performance, resilience, and end-to-end testing rather than attempting to replace them.

