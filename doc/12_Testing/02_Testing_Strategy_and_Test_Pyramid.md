# Testing Strategy and Test Pyramid

**Document ID:** TEST-02
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`

---

## 1. Purpose

This document defines the testing strategy and test pyramid for the FastFood ERP system.

It establishes:

* how testing effort is distributed across test levels;
* the responsibilities of unit, domain, application, integration, and end-to-end tests;
* how test balance is determined;
* when a behavior should be tested at one level or multiple levels;
* how risk, execution cost, feedback speed, and system boundaries influence test selection;
* how the test suite remains reliable as the system grows;
* how critical FastFood ERP workflows receive deeper verification without turning the entire suite into slow end-to-end tests.

This document builds on `TEST-01 Testing Architecture Overview`.

It does not replace the detailed testing architecture of individual test layers.

---

# 2. Testing Strategy

The FastFood ERP testing strategy is based on five principles:

1. **Fast feedback**
2. **High confidence**
3. **Risk-based depth**
4. **Appropriate test level**
5. **Explicit verification of critical boundaries**

The objective is not to maximize the number of tests.

The objective is to create the smallest practical test system that provides strong evidence that the software is correct, secure, consistent, and releasable.

---

# 3. The Test Pyramid

The default testing structure follows a pyramid.

```text
                         ┌───────────────┐
                         │   E2E / POS   │
                         │  Critical     │
                         │  Workflows    │
                         └───────┬───────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Integration / API     │
                    │  Real Boundaries        │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │ Application / Repository / DB Tests │
              └──────────────────┬──────────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │      Domain + Unit Tests            │
              │     Fast and Deterministic          │
              └─────────────────────────────────────┘
```

The lower layers should normally contain more tests because they are:

* faster;
* cheaper to execute;
* easier to diagnose;
* easier to isolate;
* more stable;
* suitable for broad scenario coverage.

The upper layers should contain fewer but more valuable scenarios.

---

# 4. The Pyramid Is a Guideline, Not a Fixed Ratio

The project must not enforce a universal numerical rule such as:

```text
70% Unit
20% Integration
10% E2E
```

Such a ratio can become misleading.

For example:

* a simple calculation may need many unit tests;
* a complex database transaction may require substantial integration testing;
* a critical POS workflow requires E2E coverage even if it is expensive;
* a concurrency problem may require specialized integration or load tests.

Therefore:

> Test distribution must be determined by risk and architectural boundaries rather than an arbitrary percentage.

---

# 5. Test Level Responsibilities

Each test level should answer a different question.

| Level           | Primary Question                                                |
| --------------- | --------------------------------------------------------------- |
| Unit            | Does this isolated behavior work correctly?                     |
| Domain          | Does the business rule remain correct?                          |
| Application     | Does the use case orchestrate the required behavior correctly?  |
| Repository / DB | Is persistence behavior correct?                                |
| API Contract    | Does the API satisfy its defined contract?                      |
| Integration     | Do real subsystems communicate correctly?                       |
| E2E             | Does the complete user workflow work?                           |
| Performance     | Does the system remain within defined performance requirements? |
| Resilience      | Does the system behave safely under failure?                    |
| Security        | Can defined security boundaries be bypassed?                    |

A test should be placed at the lowest level that can provide sufficient confidence.

---

# 6. Unit Test Strategy

Unit tests verify small isolated behaviors.

Typical targets:

* calculations;
* validators;
* parsers;
* deterministic transformations;
* policy decisions;
* state transitions;
* utility functions;
* small domain components.

Unit tests should normally have:

* no network dependency;
* no production database;
* no external service dependency;
* deterministic input;
* deterministic output;
* minimal setup;
* fast execution.

The goal is to detect local defects immediately.

Detailed architecture:

`TEST-03 Unit Testing Architecture`

---

# 7. Domain Test Strategy

Domain tests verify business rules independently from infrastructure.

Examples:

```text
Order State Transition
Recipe Validation
Discount Calculation
Stock Deduction Rule
FIFO Selection Rule
Cash Session State
Payroll Calculation
Refund Eligibility
Inventory Adjustment Rule
```

Domain tests should be especially strong for rules that represent business invariants.

For example:

```text
Required Ingredient Available
        ↓
Sale Allowed

Required Ingredient Missing
        ↓
Sale Blocked
```

The same rule should not need to be discovered for the first time through an E2E POS test.

Detailed architecture:

`TEST-04 Domain Testing Architecture`

---

# 8. Application Test Strategy

Application tests verify complete use-case behavior without requiring the full production system.

Examples:

```text
Create Order
Accept Order
Complete Payment
Refund Order
Close Cash Session
Transfer Cashier
Create Inventory Receipt
Approve Recipe
Change Employee Permission
Synchronize Operation
```

Application tests are useful for verifying that:

* authorization is evaluated;
* business rules are invoked;
* repositories are called correctly;
* transactions are coordinated;
* side effects occur;
* failures are handled.

They provide stronger confidence than isolated unit tests while remaining cheaper than full E2E tests.

Detailed architecture:

`TEST-05 Application and Use-Case Testing`

---

# 9. Repository and Database Test Strategy

Database behavior must not be simulated entirely through mocks.

Important persistence behavior should be tested against the actual database technology used by the system.

Testing should cover:

* persistence;
* retrieval;
* transactions;
* constraints;
* unique rules;
* foreign keys;
* transaction rollback;
* database-specific behavior;
* branch and tenant scope;
* concurrent database behavior where relevant.

A repository unit test with a mock does not prove that PostgreSQL behaves correctly.

Detailed architecture:

`TEST-06 Repository and Database Integration Testing`

---

# 10. API Contract Test Strategy

API contract tests verify that the public application boundary remains stable.

They should validate:

* request schema;
* response schema;
* required fields;
* data types;
* status codes;
* validation behavior;
* error contract;
* authorization responses;
* compatibility rules.

API contract testing protects frontend and other consumers from accidental backend contract changes.

Detailed architecture:

`TEST-07 API Contract and Schema Testing`

---

# 11. Integration Test Strategy

Integration tests verify interactions between real system components.

Examples:

```text
Application ↔ PostgreSQL
Application ↔ Redis
Application ↔ Queue
Application ↔ File Storage
Application ↔ External Service
Application ↔ Printer Layer
Synchronization ↔ Server
AI Service ↔ Application
```

Integration tests should focus on actual boundaries where defects are likely to occur.

They should not simply duplicate hundreds of unit tests through a slower environment.

Detailed architecture:

`TEST-08 Integration Testing Architecture`

---

# 12. End-to-End Test Strategy

End-to-end tests verify complete business workflows.

They should represent the most important real user journeys.

For FastFood ERP, examples include:

```text
Cashier Login
    ↓
Open Cash Session
    ↓
Create Order
    ↓
Send Order to Kitchen
    ↓
Order Processing
    ↓
Payment
    ↓
Order Completion
    ↓
Cash Session Reporting
```

Another critical workflow:

```text
Network Loss
    ↓
Offline Operation
    ↓
Local Recording
    ↓
Network Recovery
    ↓
Synchronization
    ↓
Server Validation
    ↓
Final State
```

E2E tests should be selective.

The suite should not attempt to test every business rule through the UI.

Detailed architecture:

`TEST-09 End-to-End and POS Testing`

---

# 13. Why E2E Tests Must Remain Limited

E2E tests have significant value but are expensive.

They are typically:

* slower;
* more complex;
* more sensitive to environment state;
* harder to diagnose;
* more vulnerable to infrastructure failures;
* more expensive to run frequently.

For example, if a discount calculation has 50 meaningful scenarios, it is usually inappropriate to test all 50 through the POS interface.

Instead:

```text
Discount Rule
    ↓
Many Domain / Unit Tests
    ↓
Few Application Tests
    ↓
Few Critical E2E Scenarios
```

This provides broad rule coverage without creating an unnecessarily large E2E suite.

---

# 14. The Testing Layering Model

A feature should normally be verified progressively.

Example: refund.

```text
Unit
  ↓
Refund calculation / validation

Domain
  ↓
Refund eligibility and business rules

Application
  ↓
Refund use case and authorization

Database
  ↓
Refund persistence and transaction

API
  ↓
Refund endpoint contract

Integration
  ↓
Refund + financial components

E2E
  ↓
Staff performs complete refund workflow
```

Each layer provides different evidence.

---

# 15. Critical Behavior Should Not Rely on One Test Layer

Critical operations require layered verification.

Examples:

### Payment

```text
Domain
+
Application
+
Database
+
Concurrency
+
API
+
E2E
```

### Inventory deduction

```text
Domain
+
Application
+
Database
+
Concurrency
+
Inventory Integration
+
POS E2E
```

### Authorization

```text
Authorization Unit/Domain
+
Application
+
API
+
Security Integration
+
E2E where appropriate
```

### Offline synchronization

```text
Domain
+
Application
+
Persistence
+
Synchronization Integration
+
Concurrency
+
E2E
```

The exact test depth depends on risk.

---

# 16. Risk-Based Test Depth

Test depth should increase with risk.

A useful conceptual model is:

```text
Risk
  =
Impact × Probability × Exposure
```

Higher-risk behavior receives:

* more scenarios;
* more test layers;
* stronger failure testing;
* more negative cases;
* concurrency testing where relevant;
* security testing where relevant;
* release-gate status where appropriate.

---

# 17. High-Risk FastFood ERP Areas

The following areas normally require deeper testing.

## 17.1 Financial Operations

* payment;
* refunds;
* cash opening;
* cash closing;
* handover;
* shortages;
* corrections;
* financial reports.

---

## 17.2 Inventory

* recipe deduction;
* semi-finished products;
* FIFO;
* insufficient stock;
* inventory adjustment;
* shrink/loss;
* branch inventory;
* synchronization.

---

## 17.3 Security

* authentication;
* authorization;
* tenant isolation;
* branch isolation;
* resource ownership;
* device trust;
* privileged actions;
* file access;
* API access.

---

## 17.4 Offline and Synchronization

* offline authorization;
* unique operation identity;
* retry;
* replay;
* duplicate delivery;
* conflicts;
* ordering;
* reconnection;
* revocation.

---

## 17.5 POS

* order lifecycle;
* kitchen workflow;
* payment;
* cash session;
* printer-related behavior;
* cashier handover;
* offline operation.

---

# 18. Low-Risk UI Changes

A minor visual change should not require the entire E2E suite to run locally.

For example:

```text
Button Spacing Change
    ↓
Frontend Component Tests
    ↓
Relevant UI Integration Test
```

A complete POS E2E workflow may be unnecessary unless the change affects the workflow.

However, release CI may still execute the required critical E2E suite.

---

# 19. Negative Testing

Testing strategy must include invalid and unauthorized scenarios.

Examples:

```text
Invalid Input
Missing Permission
Wrong Branch
Wrong Tenant
Closed Cash Session
Missing Stock
Duplicate Payment
Duplicate Sync Operation
Expired Session
Revoked Device
Expired Subscription
Unavailable Dependency
Concurrent Modification
```

Negative testing is especially important for security and financial boundaries.

---

# 20. Happy Path vs Failure Path

A healthy test suite should not contain only successful scenarios.

For important functionality:

```text
Happy Path
+
Validation Failure
+
Authorization Failure
+
Business Rule Failure
+
Dependency Failure
+
Concurrency Failure
+
Recovery
```

The required set depends on the feature.

Critical operations should receive substantially more failure-path testing.

---

# 21. Test Duplication Control

Different test levels may intentionally verify the same critical behavior.

However, unnecessary duplication should be avoided.

Bad pattern:

```text
100 Unit Tests
100 Integration Tests
100 E2E Tests

All testing exactly the same scenarios
```

Better pattern:

```text
Unit
→ broad combinations

Integration
→ real boundary behavior

E2E
→ representative user journeys
```

The tests complement each other rather than repeating the same assertion at every level.

---

# 22. Example: Order Creation

Suppose the system creates a takeaway order.

### Unit tests

Verify:

* order validation;
* item quantity rules;
* price calculation.

### Domain tests

Verify:

* order state transitions;
* allowed order types;
* item rules.

### Application tests

Verify:

* authorization;
* order creation;
* inventory availability check;
* persistence coordination.

### Database tests

Verify:

* order persistence;
* relationships;
* transaction behavior.

### API tests

Verify:

* request schema;
* response schema;
* error behavior.

### Integration tests

Verify:

* order + inventory;
* order + kitchen workflow;
* order + printer integration where applicable.

### E2E test

Verify:

```text
Cashier
→ Creates takeaway order
→ Accepts order
→ Order reaches required processing state
→ Payment completes
→ Order is closed
```

This is a proper testing pyramid.

---

# 23. Example: Recipe-Based Inventory Deduction

### Unit

Test calculation of ingredient quantities.

### Domain

Test recipe rules and deduction invariants.

### Application

Test the order use case invoking inventory deduction.

### Database

Test transactional stock changes.

### Integration

Test order + recipe + inventory.

### Concurrency

Test simultaneous deductions.

### E2E

Test a real order causing expected stock changes.

This gives strong confidence without moving every possible recipe combination into E2E.

---

# 24. Example: Permission Enforcement

Permission testing should occur at multiple levels.

```text
Permission Rule
      ↓
Domain / Policy Test
      ↓
Application Authorization Test
      ↓
API Security Test
      ↓
Cross-Branch / Cross-Tenant Test
      ↓
E2E Critical Workflow Test
```

The frontend test may verify that unauthorized actions are hidden or disabled.

However:

> Frontend behavior is not proof that authorization is secure.

The actual security boundary must be tested at the server/API level.

---

# 25. Test Data Strategy and Pyramid Balance

Large E2E suites often become slow because they require large amounts of setup.

Therefore test data should be created at the appropriate level.

For example:

```text
Unit
→ Small in-memory data

Domain
→ Small business scenarios

Integration
→ Controlled database fixtures

E2E
→ Minimal realistic business dataset
```

E2E tests should not rebuild an unnecessarily large business environment for every scenario.

---

# 26. Test Environment Strategy

Different test layers may use different environments.

| Test Level  | Typical Environment              |
| ----------- | -------------------------------- |
| Unit        | Isolated process                 |
| Domain      | Isolated process                 |
| Application | Test runtime                     |
| Repository  | Test PostgreSQL                  |
| API         | Test application                 |
| Integration | Multi-service test environment   |
| E2E         | Production-like test environment |
| Performance | Dedicated controlled environment |
| Resilience  | Controlled failure environment   |

The environment must match the behavior being tested.

---

# 27. Test Execution Speed

The test suite should provide fast developer feedback.

A practical execution structure is:

```text
Local Development
    ↓
Fast Tests
    ↓
Relevant Integration Tests
    ↓
Developer Feedback

CI
    ↓
Full Automated Test Suite
    ↓
Security / Integration / E2E
    ↓
Release Gates
```

Developers should not need to wait for the entire production-like test environment for every small change.

---

# 28. Test Selection by Change Type

Testing should be intelligently related to the changed area.

Examples:

### Domain rule change

Run:

* unit;
* domain;
* affected application tests;
* relevant integration tests;
* relevant regression tests.

### Database schema change

Run:

* repository;
* database integration;
* migration validation;
* affected API/integration;
* relevant E2E.

### Authentication change

Run:

* authentication;
* authorization;
* security;
* API;
* device;
* relevant E2E;
* regression.

### Offline synchronization change

Run:

* synchronization;
* persistence;
* concurrency;
* security;
* integration;
* E2E.

### Frontend-only visual change

Run:

* affected frontend tests;
* relevant UI integration tests;
* required CI regression suite.

The final release gate remains governed by `TEST-19`.

---

# 29. Test Suite Tiers

The project should conceptually classify automated tests into execution tiers.

## Tier 1 — Fast Feedback

Includes:

* unit;
* domain;
* lightweight application tests.

Purpose:

> Immediate developer feedback.

---

## Tier 2 — Component and Boundary Validation

Includes:

* repository;
* database;
* API;
* integration tests.

Purpose:

> Verify subsystem boundaries.

---

## Tier 3 — Critical Workflow Validation

Includes:

* E2E;
* POS;
* critical synchronization workflows;
* security workflows.

Purpose:

> Verify complete business behavior.

---

## Tier 4 — Specialized Validation

Includes:

* performance;
* resilience;
* chaos;
* AI regression;
* extended security testing.

Purpose:

> Validate non-functional and specialized requirements.

---

# 30. Local vs CI Execution

Not every test must run at every development stage.

### Local

Prefer:

* fast tests;
* directly affected tests;
* selected integration tests.

### Pull Request / CI

Typically includes:

* full unit/domain suite;
* application tests;
* database tests;
* API contract tests;
* integration tests;
* frontend tests;
* required security tests.

### Release

Includes the required:

* full automated regression suite;
* critical E2E;
* security gates;
* migration validation;
* performance validation where required;
* resilience validation where required;
* AI regression where affected.

Exact blocking rules are defined in `TEST-19`.

---

# 31. Coverage Strategy

Coverage should be measured from several perspectives.

## Code Coverage

Examples:

* line;
* branch;
* function.

## Behavior Coverage

Examples:

* business scenarios;
* state transitions;
* error paths.

## Requirement Coverage

Examples:

* accepted requirements;
* domain rules;
* system constraints.

## Risk Coverage

Examples:

* financial;
* security;
* inventory;
* offline;
* synchronization;
* resilience.

A high code-coverage percentage does not compensate for missing high-risk scenarios.

---

# 32. Coverage Interpretation

Coverage reports should be interpreted carefully.

For example:

```text
95% Line Coverage
```

does not automatically mean:

```text
95% Correctness
```

Coverage can indicate which code executed.

It cannot prove that the executed assertions were sufficient.

Therefore the project prioritizes:

```text
Correct Assertions
+
Business Invariants
+
Boundary Testing
+
Failure Testing
+
Risk Coverage
```

---

# 33. Mutation and Assertion Quality

Where practical, the project may use mutation testing or similar techniques to evaluate whether tests actually detect meaningful behavioral changes.

The objective is not to maximize mutation scores blindly.

The objective is to identify:

* weak assertions;
* tests that execute code without verifying behavior;
* untested branches;
* missing business-rule protection.

Mutation testing is especially valuable for critical domain rules.

---

# 34. Contract Testing and E2E Relationship

Contract tests and E2E tests have different responsibilities.

```text
Contract Test
→ "Does the API follow the agreed interface?"

E2E
→ "Does the complete user workflow work?"
```

An API can satisfy its schema while still producing incorrect business behavior.

An E2E test can detect workflow failure but may not clearly identify a contract regression.

Both are therefore useful.

---

# 35. Integration and E2E Relationship

Integration tests verify subsystem boundaries.

E2E tests verify user workflows.

Example:

```text
Integration:
Order Service ↔ Inventory Service

E2E:
Cashier creates order
→ Inventory is deducted
→ Kitchen receives order
→ Payment completes
```

Integration tests should contain detailed boundary scenarios.

E2E tests should contain representative complete workflows.

---

# 36. Test Balance for FastFood ERP

The expected balance is conceptually:

```text
High Volume
────────────────────────
Unit + Domain
Application
Repository / DB
────────────────────────
Integration + API
────────────────────
Critical E2E / POS
────────────────
Performance
Resilience
Security
AI
```

The bottom of the pyramid provides broad fast feedback.

The middle verifies system boundaries.

The top verifies critical user journeys.

Specialized tests operate across the pyramid where required.

---

# 37. Critical E2E Workflow Set

The initial critical E2E set should prioritize:

### POS

* cashier authentication;
* cash opening;
* order creation;
* order acceptance;
* kitchen workflow;
* payment;
* order completion;
* cash closing.

### Cash

* handover;
* shortage;
* recount;
* correction;
* refund.

### Inventory

* recipe-based deduction;
* insufficient stock;
* inventory receipt;
* adjustment.

### Security

* unauthorized action;
* cross-branch access;
* cross-tenant access;
* permission change.

### Offline

* offline operation;
* reconnect;
* synchronization;
* duplicate prevention;
* conflict handling.

The exact scenario list may evolve with the implemented system.

---

# 38. Regression Suite Strategy

The regression suite should grow from real system risk.

A new regression test should be added when:

* a serious defect is discovered;
* a security issue is found;
* a financial or inventory invariant fails;
* an important synchronization bug is found;
* an API compatibility problem occurs;
* a production incident reveals missing validation.

The suite should not grow through indiscriminate duplication.

---

# 39. Flaky Test Management

Flaky tests weaken the pyramid.

A flaky test must not become an accepted source of random CI failure.

The project should:

1. identify the cause;
2. determine whether the test or product is unstable;
3. fix the underlying issue;
4. isolate the test if necessary;
5. explicitly track temporary quarantine;
6. remove quarantine as soon as practical.

Repeated retries must not hide a real defect.

---

# 40. Test Stability

A test suite is considered healthy when:

* results are reproducible;
* failures are diagnosable;
* test data is isolated;
* execution order does not affect results;
* tests do not unnecessarily depend on external services;
* environment assumptions are explicit;
* test duration remains manageable.

Stability is part of test quality.

---

# 41. Parallel Test Execution

Tests may run in parallel where safe.

Parallelization must not introduce:

* shared database corruption;
* tenant mixing;
* branch mixing;
* shared file conflicts;
* shared device state;
* port conflicts;
* timing dependencies.

Test isolation must come before aggressive parallelization.

---

# 42. Test Balance and System Growth

As the system grows, test distribution must be reviewed.

Adding a new feature should not automatically produce:

```text
10 Unit Tests
+
10 Integration Tests
+
10 E2E Tests
```

Instead, determine:

1. What business behavior was added?
2. What invariant was introduced?
3. What boundaries are affected?
4. What risk does the feature introduce?
5. Which test layer provides the strongest evidence?
6. Which existing regression tests are affected?
7. Does a new release gate become necessary?

---

# 43. Test Debt

Testing debt includes:

* missing critical tests;
* obsolete tests;
* weak assertions;
* flaky tests;
* excessive E2E duplication;
* untested failure paths;
* outdated fixtures;
* stale API contracts;
* missing regression coverage;
* tests that no longer represent current architecture.

Testing debt must be managed like technical debt.

Critical testing debt must not be ignored merely because the application currently appears functional.

---

# 44. When a Test Belongs at a Higher Level

A behavior should move or be additionally tested at a higher level when its correctness depends on a real boundary.

Examples:

### Database Transaction

Unit tests cannot prove actual PostgreSQL transaction behavior.

Use database integration tests.

### API Contract

Internal application tests cannot prove the external API contract.

Use API contract tests.

### Printer Integration

A pure unit test cannot prove communication with the real printer boundary.

Use integration testing.

### Complete POS Workflow

Unit tests cannot prove the entire cashier journey.

Use E2E.

---

# 45. When a Test Should Stay at a Lower Level

A behavior should remain at a lower level when it does not require higher-level infrastructure.

Examples:

* price calculation;
* discount formula;
* recipe quantity calculation;
* validation;
* state transition;
* payroll calculation.

Testing these exclusively through E2E would create:

* slow execution;
* difficult diagnosis;
* unnecessary setup;
* excessive duplication.

---

# 46. Test Balance Decision Model

For each behavior, use the following decision process:

```text
Does it contain a business rule?
        │
        ├── Yes → Unit / Domain
        │
        ↓
Does it coordinate multiple components?
        │
        ├── Yes → Application / Integration
        │
        ↓
Does it depend on a real infrastructure boundary?
        │
        ├── Yes → Integration / DB / API
        │
        ↓
Is it a critical user workflow?
        │
        ├── Yes → E2E
        │
        ↓
Is it security / performance / resilience / AI specific?
        │
        ├── Yes → Specialized testing
```

More than one answer may apply.

Critical behavior may intentionally exist at multiple levels.

---

# 47. Anti-Patterns

The following testing strategies are prohibited or strongly discouraged.

## 47.1 E2E-Only Testing

```text
Feature
→ E2E
```

This produces slow and difficult-to-diagnose feedback.

---

## 47.2 Unit-Only Testing

Unit tests cannot prove:

* database behavior;
* API contracts;
* real integration;
* deployment behavior;
* complete workflows.

---

## 47.3 Mock Everything

Excessive mocking creates false confidence.

A test may pass while the real dependency fails.

---

## 47.4 Coverage-Driven Testing

Writing meaningless tests solely to increase coverage is not acceptable.

---

## 47.5 Test Duplication

Repeating the same assertion through every layer without additional value increases maintenance cost.

---

## 47.6 Ignoring Failure Paths

Testing only successful workflows creates false confidence.

---

## 47.7 Ignoring Security Because E2E Works

A workflow functioning for an authorized user does not prove that unauthorized users are blocked.

---

## 47.8 Ignoring Concurrency

Sequential tests cannot prove correctness under concurrent execution.

---

## 47.9 Permanent Quarantine

A quarantined flaky or failing test must not become permanently invisible.

---

# 48. Relationship with Security Testing

Security testing follows the same pyramid principle but has additional requirements.

For example:

```text
Authorization Rule
    ↓
Policy / Domain Test
    ↓
Application Test
    ↓
API Security Test
    ↓
Cross-Tenant / Cross-Branch Test
    ↓
Critical E2E
```

Security boundaries must be tested at the boundary where enforcement occurs.

Detailed security testing:

`TEST-14 Authentication, Authorization and Security Testing`

---

# 49. Relationship with Performance Testing

Performance testing is not simply a larger version of functional testing.

Functional tests answer:

> Is the result correct?

Performance tests answer:

> Is the result produced within the required resource and latency constraints under the expected workload?

Performance testing therefore operates separately from the functional pyramid.

Detailed policy:

`TEST-17 Performance, Load and SLO Testing`

---

# 50. Relationship with Resilience Testing

Resilience tests verify behavior when normal assumptions fail.

Examples:

```text
Database Failure
Redis Failure
Queue Failure
Network Failure
Process Crash
External API Timeout
Printer Failure
```

These tests should not replace ordinary functional tests.

They extend them.

Detailed policy:

`TEST-18 Resilience and Chaos Testing`

---

# 51. Relationship with CI Quality Gates

The pyramid defines test organization.

CI defines when tests become mandatory.

The relationship is:

```text
Testing Strategy
       ↓
Test Layers
       ↓
Test Suites
       ↓
CI Execution
       ↓
Quality Gates
       ↓
Release Decision
```

Detailed release rules:

`TEST-19 CI Quality Gates and Release Testing`

---

# 52. Relationship with Test Data

Test balance depends heavily on test data management.

Fast tests should use small controlled datasets.

Integration tests should use realistic boundary data.

E2E tests should use minimal realistic business scenarios.

Performance tests should use workload-sized datasets.

Detailed policy:

`TEST-20 Test Data and Test Environment Management`

---

# 53. Test Suite Health Metrics

The project may track:

* total test count;
* test execution time;
* failure rate;
* flaky test rate;
* coverage;
* critical scenario coverage;
* regression coverage;
* CI duration;
* E2E duration;
* escaped defect rate;
* release-blocking failures.

Metrics are indicators, not goals by themselves.

Optimizing a metric while reducing actual confidence is not considered improvement.

---

# 54. Quality vs Speed

The test strategy must balance:

```text
Fast Feedback
       +
Strong Confidence
       +
Maintainability
       +
Infrastructure Cost
       +
Business Risk
```

A faster test suite is not better if it removes important protection.

A very comprehensive suite is not better if it becomes so slow or unstable that developers stop relying on it.

The correct target is:

> Maximum practical confidence for the available engineering and infrastructure cost.

---

# 55. Test Pyramid Evolution

The test pyramid should evolve with the architecture.

During early implementation of a feature:

```text
Unit / Domain
```

may dominate.

As infrastructure integration becomes available:

```text
Repository
API
Integration
```

coverage grows.

As the complete product becomes operational:

```text
Critical E2E
POS
Offline
```

coverage becomes increasingly important.

Specialized testing grows according to risk.

The pyramid is therefore a living architecture rather than a fixed test-count target.

---

# 56. Mandatory Strategy Rules

The following rules apply to the entire testing system.

1. Unit and domain tests should provide the broadest fast feedback.
2. Integration tests must verify important real boundaries.
3. E2E tests must focus on critical user workflows.
4. No critical business invariant may rely exclusively on E2E coverage.
5. No infrastructure boundary may rely exclusively on mocks.
6. Security boundaries must be tested where they are enforced.
7. Financial operations require layered testing.
8. Inventory operations require layered testing.
9. Offline and synchronization require dedicated testing.
10. Concurrency-sensitive behavior requires concurrency testing.
11. API contracts require explicit contract testing.
12. Failure paths must be tested for important workflows.
13. Coverage percentages must not replace risk-based analysis.
14. E2E test count must remain controlled to preserve feedback speed.
15. Test duplication must provide meaningful additional confidence.
16. Flaky tests must be actively managed.
17. Tests must be deterministic where practical.
18. Test environments and data must remain isolated from production.
19. Release gates must prioritize critical security, financial, integrity, and data-loss risks.
20. Test strategy must evolve when architecture or business rules change.

---

# 57. Acceptance Criteria

This document is accepted when:

* the test pyramid is clearly defined;
* unit, domain, application, integration, and E2E responsibilities are separated;
* test distribution is explicitly risk-based rather than percentage-based;
* the purpose of each test level is clear;
* the relationship between mocks and real integrations is defined;
* critical FastFood ERP workflows receive layered testing;
* E2E testing is intentionally limited to valuable workflows;
* financial, inventory, security, offline, and synchronization areas receive deeper testing;
* coverage is treated as evidence rather than proof;
* flaky and duplicated tests are addressed;
* local and CI execution strategies are distinguished;
* performance, resilience, AI, and security testing are connected to the main strategy;
* the document provides a stable foundation for TEST-03 through TEST-20.

---

# 58. Final Test Pyramid Rule

The FastFood ERP testing strategy follows one central rule:

> **Test each behavior at the lowest level that can provide reliable evidence, move upward when a real boundary or complete workflow must be verified, and add deeper testing when business risk requires it.**

The goal is not to maximize unit tests, integration tests, or E2E tests individually.

The goal is to maintain a balanced test system in which:

```text
Fast Tests
    +
Reliable Integration Tests
    +
Focused Critical E2E Tests
    +
Specialized Security / Performance / Resilience / AI Tests
    =
Practical Release Confidence
```

The testing pyramid must therefore remain **risk-driven, fast enough to use continuously, deep enough to protect critical business behavior, and stable enough to be trusted for every release**.

