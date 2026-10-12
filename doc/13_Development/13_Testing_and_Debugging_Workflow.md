# Testing and Debugging Workflow

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

# 1. Purpose

This document defines the standard local workflow for running tests, investigating failures, debugging application behavior, and validating changes during FastFood ERP development.

The purpose is to ensure that developers do not treat successful code execution as proof of correctness.

A change is considered technically reliable only when the relevant behavior has been tested and failures can be investigated systematically.

This document focuses on the **developer workflow**.

Detailed testing architecture and testing policies are defined in:

`docs/12_Testing`

---

# 2. Scope

This document covers:

* local test preparation;
* test selection;
* test execution;
* unit testing workflow;
* domain testing workflow;
* application testing;
* repository and database testing;
* API testing;
* integration testing;
* frontend testing;
* end-to-end testing;
* offline and synchronization testing;
* concurrency testing;
* financial and inventory testing;
* security testing;
* debugging workflow;
* failure investigation;
* logs;
* database inspection;
* queue inspection;
* browser debugging;
* API debugging;
* test data;
* test isolation;
* flaky tests;
* test cleanup;
* local test environments;
* regression testing;
* test evidence;
* CI reproduction;
* completion criteria.

---

# 3. Core Principles

Local testing and debugging follow these principles:

1. Test behavior, not implementation alone.
2. Choose the smallest test scope that can prove the change.
3. Run focused tests before broad test suites.
4. Run broader regression tests before completing significant changes.
5. A passing test is evidence, not absolute proof.
6. A failing test must be investigated rather than ignored.
7. Test failures must be reproducible where possible.
8. Tests must be isolated from each other.
9. Tests must not depend on personal local state.
10. Production data must not be used for ordinary testing.
11. Debugging must not change production systems.
12. Database state must be inspectable during debugging.
13. Logs must provide useful diagnostic information without exposing secrets.
14. Security behavior must remain enabled during relevant tests.
15. Financial and inventory behavior requires stronger validation.
16. Offline and synchronization behavior requires controlled failure testing.
17. Test results must be reproducible enough for code review and CI.
18. Developers should fix root causes rather than suppress symptoms.
19. Debugging changes must not accidentally become production code.
20. Testing and debugging are part of development, not final cleanup.

---

# 4. Testing Workflow Overview

The normal local workflow is:

```text
Understand Change
      ↓
Identify Risk
      ↓
Choose Test Scope
      ↓
Prepare Test Environment
      ↓
Run Focused Tests
      ↓
Investigate Failures
      ↓
Fix Implementation
      ↓
Repeat Focused Tests
      ↓
Run Broader Regression Tests
      ↓
Review Results
      ↓
Document Significant Findings
      ↓
Ready for Review
```

Testing should begin as early as practical.

---

# 5. Test Scope Selection

The developer should select tests based on the change.

A useful decision model is:

```text
Small isolated logic change
        ↓
Unit/domain tests

Business workflow change
        ↓
Application/use-case tests

Database behavior change
        ↓
Repository/integration tests

API contract change
        ↓
API contract/integration tests

Frontend behavior change
        ↓
Component/integration tests

Critical user workflow
        ↓
End-to-end tests

Concurrency-sensitive change
        ↓
Concurrency tests

Offline/sync change
        ↓
Offline and synchronization tests
```

The affected behavior determines the required test level.

---

# 6. Before Running Tests

Before executing tests, confirm:

* the correct Git branch is checked out;
* dependencies are installed;
* the correct runtime version is active;
* local configuration is valid;
* required services are running;
* database migrations are current;
* test database is available;
* required environment variables exist.

For example:

```text id="0z4g2d"
Git branch
   ↓
Runtime
   ↓
Dependencies
   ↓
Environment
   ↓
Database
   ↓
Redis / worker if required
   ↓
Tests
```

---

# 7. Clean Test Environment

Tests should run against a controlled environment.

The developer should know:

* which database is being used;
* which Redis instance is being used;
* which environment configuration is active;
* whether external integrations are mocked;
* whether background workers are required.

Tests must never accidentally run against production resources.

---

# 8. Test Environment Separation

At minimum, development and testing state should be distinguishable.

Conceptually:

```text id="6a4kz7"
Development
    ↓
fastfood_dev

Testing
    ↓
fastfood_test
```

The exact implementation may differ.

The critical requirement is that test execution must not corrupt normal development data.

---

# 9. Test Data Preparation

Test data should be created deliberately.

Prefer:

* test fixtures;
* factories;
* controlled seed data;
* setup functions;
* generated synthetic data.

Avoid depending on:

* manually created local records;
* previous test runs;
* arbitrary database state;
* personal development accounts.

---

# 10. Focused Testing First

After a change, start with the smallest relevant test.

Example:

```text id="u1l8e5"
Change:
Recipe ingredient deduction

First:
Recipe/domain tests

Then:
Application tests

Then:
Inventory integration tests

Then:
Relevant regression suite
```

This provides faster feedback than immediately running the entire test suite.

---

# 11. Full Regression Testing

Broader tests should be executed when the change affects:

* shared infrastructure;
* authentication;
* authorization;
* database schema;
* core domain behavior;
* financial logic;
* inventory;
* synchronization;
* shared frontend components;
* API contracts;
* deployment configuration.

The larger the impact radius, the broader the required test scope.

---

# 12. Test Execution

Project test commands should be documented and reproducible.

The preferred pattern is:

```text id="v1wqbe"
Local command
     ↓
Deterministic test environment
     ↓
Test execution
     ↓
Exit status
     ↓
Test report
```

Developers should avoid manually interpreting only a small portion of the output.

The complete result should be considered.

---

# 13. Test Output

A useful test execution should report:

* tests discovered;
* tests executed;
* passed tests;
* failed tests;
* skipped tests;
* errors;
* duration;
* relevant warnings.

If coverage is collected, it should be reported separately from functional success.

---

# 14. Exit Codes

Test commands must use meaningful exit codes.

Conceptually:

```text id="ynz1tm"
Exit 0 → success

Non-zero → failure
```

Scripts and CI should rely on the exit status rather than parsing human-readable output.

---

# 15. Unit Test Workflow

Unit tests validate isolated logic.

Typical workflow:

```text id="ck8r9j"
Change logic
   ↓
Write/update unit test
   ↓
Run focused unit test
   ↓
Inspect failure
   ↓
Fix implementation
   ↓
Repeat
```

Unit tests should remain fast enough to support frequent execution.

---

# 16. Domain Test Workflow

Domain tests validate business rules.

Examples:

* order state transitions;
* recipe calculations;
* stock availability;
* discount rules;
* payroll calculations;
* refund rules;
* cash register rules.

Domain tests should not require unnecessary external infrastructure.

---

# 17. Application Test Workflow

Application/use-case tests validate workflows across domain and application layers.

Examples:

```text id="e1g4fd"
Create Order
     ↓
Validate
     ↓
Check Stock
     ↓
Calculate Price
     ↓
Persist
     ↓
Emit Required Effects
```

The test should verify business behavior rather than only individual method calls.

---

# 18. Repository and Database Testing

Database-related changes require tests against a real supported database environment when appropriate.

Test:

* queries;
* constraints;
* transactions;
* relationships;
* unique rules;
* indexes where relevant;
* migration behavior;
* tenant isolation;
* branch isolation.

Mocks should not replace database integration tests when actual database behavior matters.

---

# 19. Migration Testing

When migrations change:

```text id="f3phq1"
Fresh database
      ↓
Apply all migrations
      ↓
Verify schema

Existing database
      ↓
Apply new migration
      ↓
Verify compatibility
```

Developers should test both fresh installation and upgrade paths when the change requires it.

---

# 20. API Testing

API changes should be tested at the appropriate level.

Validate:

* request validation;
* authorization;
* response schema;
* status codes;
* error behavior;
* pagination;
* filtering;
* idempotency;
* state transitions;
* tenant/branch scope.

The API contract must remain consistent with the documented architecture.

---

# 21. Frontend Testing

Frontend changes should be tested at the smallest appropriate level.

Possible levels:

```text id="gkqz4u"
Component
   ↓
Feature
   ↓
Page
   ↓
Application workflow
```

Test:

* user interactions;
* validation;
* loading states;
* errors;
* empty states;
* permissions;
* API failures;
* duplicate actions;
* unsaved changes;
* responsive behavior where relevant.

---

# 22. End-to-End Testing

End-to-end tests should validate important user workflows.

Examples:

### POS

```text
Login
 ↓
Open Register
 ↓
Create Order
 ↓
Accept Order
 ↓
Process Payment
 ↓
Close Order
```

### Inventory

```text
Create Product
 ↓
Define Recipe
 ↓
Receive Stock
 ↓
Sell Product
 ↓
Verify Deduction
```

### Cash

```text
Open Register
 ↓
Process Transactions
 ↓
Close Register
 ↓
Count Cash
 ↓
Review Result
```

End-to-end testing should focus on critical workflows rather than reproducing every unit test.

---

# 23. Offline Testing

Offline behavior requires controlled network conditions.

A useful workflow is:

```text id="7o1j1d"
Online
  ↓
Perform operation
  ↓
Disconnect
  ↓
Perform offline operation
  ↓
Reconnect
  ↓
Synchronize
  ↓
Verify server state
```

Test:

* queueing;
* retries;
* duplicate delivery;
* ordering;
* conflict handling;
* partial synchronization;
* recovery.

---

# 24. Concurrency Testing

Concurrency-sensitive changes require controlled concurrent execution.

Examples:

* two cashiers attempting conflicting operations;
* simultaneous stock deductions;
* concurrent register changes;
* duplicate API requests;
* simultaneous synchronization.

The test should demonstrate the expected consistency rule.

---

# 25. Financial Testing

Financial workflows require strong validation.

Examples:

* payment totals;
* discounts;
* refunds;
* cash register totals;
* shortages;
* corrections;
* payroll calculations.

Financial tests should verify both:

1. returned result;
2. persisted state.

---

# 26. Inventory Testing

Inventory tests should verify:

* stock deduction;
* insufficient stock behavior;
* recipe expansion;
* semi-finished product dependencies;
* FIFO behavior;
* yield loss;
* inventory adjustment;
* shopping-list behavior;
* archive behavior.

Tests should verify actual database state where persistence is involved.

---

# 27. Security Testing

Security-sensitive changes require tests for:

* authentication;
* authorization;
* tenant isolation;
* branch isolation;
* role permissions;
* resource ownership;
* forbidden operations;
* token/session behavior;
* sensitive data exposure.

A successful request by an authorized user is not enough.

Unauthorized requests must also be tested.

---

# 28. Subscription Testing

Subscription restrictions should be tested locally where applicable.

Examples:

```text id="6z6q0a"
Active subscription
     ↓
Feature available

Expired subscription
     ↓
Feature blocked
     ↓
Data remains viewable
```

Tests should also cover:

* warning period;
* expiration;
* restricted functionality;
* reactivation;
* data retention rules.

---

# 29. Background Job Testing

When a change affects background jobs:

* test job creation;
* test successful execution;
* test failure;
* test retry;
* test idempotency;
* test duplicate execution;
* test relevant side effects.

A job that executes successfully once is not necessarily safe to retry.

---

# 30. Queue Debugging

When a background job fails:

```text id="8n8r3e"
Producer
  ↓
Queue
  ↓
Worker
  ↓
Job
  ↓
Database / External Service
```

Identify the exact stage where failure occurs.

Do not immediately retry repeatedly without understanding the failure.

Repeated retries can create duplicate effects.

---

# 31. Scheduler Testing

Scheduled jobs should be testable without waiting for their actual production schedule.

Developers should be able to invoke the job manually or through a controlled test mechanism.

Validate:

* scheduling;
* execution;
* duplicate execution;
* missed execution;
* failure recovery.

---

# 32. Debugging Workflow

When a test or application behavior fails, use a structured workflow:

```text id="u8w6qa"
Observe
  ↓
Reproduce
  ↓
Reduce
  ↓
Locate
  ↓
Understand
  ↓
Fix
  ↓
Retest
  ↓
Regression Test
```

Avoid changing multiple unrelated parts of the system at once.

---

# 33. Observe

First collect evidence.

Useful evidence includes:

* error message;
* stack trace;
* request;
* response;
* logs;
* database state;
* queue state;
* browser console;
* network request;
* environment configuration;
* test output.

Do not begin with assumptions about the cause.

---

# 34. Reproduce

A bug that cannot be reproduced should be investigated carefully.

Record:

* input;
* user role;
* branch;
* tenant;
* environment;
* database state;
* sequence of actions;
* timing;
* network state;
* feature flags.

The goal is to turn:

```text id="6u3g4b"
"It sometimes fails"
```

into:

```text id="v2j4mn"
"Under condition X, operation Y fails after state Z."
```

---

# 35. Reduce

Reduce the problem to the smallest reproducible case.

For example:

```text id="3c2xna"
Full POS workflow
      ↓
Order creation
      ↓
Recipe calculation
      ↓
Stock deduction
      ↓
Specific failing calculation
```

This makes debugging faster and reduces unrelated noise.

---

# 36. Locate

Determine which layer is responsible.

Possible layers:

```text id="l1t7js"
Browser
  ↓
Frontend
  ↓
API
  ↓
Application
  ↓
Domain
  ↓
Repository
  ↓
Database
  ↓
External Service
```

Do not assume the layer based only on where the error appears.

---

# 37. Understand

Before changing code, determine:

* expected behavior;
* actual behavior;
* relevant requirement;
* relevant architecture;
* relevant business rule;
* state before failure;
* state after failure.

A fix should address the reason for the failure.

---

# 38. Fix

The fix should be as narrow as practical.

Avoid:

* unrelated refactoring;
* broad rewrites;
* temporary hacks;
* disabling validation;
* disabling security;
* suppressing exceptions;
* changing tests only to make them pass.

If the architecture itself is wrong, follow the ADR/change workflow rather than hiding the problem in implementation.

---

# 39. Retest

After fixing:

1. rerun the failed test;
2. rerun the directly related tests;
3. rerun broader regression tests according to risk.

Example:

```text id="f8xk1a"
Failed test
   ↓
Fix
   ↓
Same test
   ↓
Related suite
   ↓
Relevant regression suite
```

---

# 40. Regression Testing

Every bug fix should consider whether the bug could return.

Where practical, add or update a test that reproduces the original failure.

The expected workflow is:

```text id="h6w9ce"
Bug
 ↓
Reproduction test
 ↓
Failing test
 ↓
Fix
 ↓
Passing test
```

This creates permanent regression protection.

---

# 41. Debug Logging

Temporary debug logs may be useful.

However:

* do not log secrets;
* do not log passwords;
* do not log tokens;
* do not log unnecessary personal data;
* do not leave excessive debug output in production code.

Temporary debugging code should be removed or converted into appropriate structured diagnostics.

---

# 42. Debugger Usage

A debugger should be preferred over excessive print statements when it provides better visibility.

Useful debugging techniques include:

* breakpoints;
* conditional breakpoints;
* variable inspection;
* call-stack inspection;
* stepping;
* exception breakpoints.

The exact debugger depends on the developer environment.

---

# 43. Database Debugging

When debugging database behavior, inspect:

* executed operation;
* input values;
* transaction boundary;
* current record state;
* constraints;
* related records;
* isolation behavior.

Do not manually modify database state to make a failing test pass unless the modification is part of the test setup.

---

# 44. Transaction Debugging

For transactional failures, determine:

```text id="8f0b1n"
Transaction start
   ↓
Operation A
   ↓
Operation B
   ↓
Failure?
   ↓
Commit / Rollback
```

Verify whether partial state remains.

Critical financial and inventory operations should not leave invalid partial state.

---

# 45. API Debugging

For an API failure inspect:

1. HTTP method;
2. URL;
3. request headers;
4. authentication state;
5. tenant/branch context;
6. request body;
7. response status;
8. response body;
9. server logs;
10. database effects.

Sensitive headers and credentials must be redacted from shared evidence.

---

# 46. Frontend Network Debugging

When the frontend displays incorrect behavior, inspect the network layer.

Determine whether the issue is:

* request not sent;
* incorrect URL;
* incorrect method;
* incorrect payload;
* authorization failure;
* validation failure;
* server error;
* incorrect response handling;
* stale frontend state.

This prevents UI symptoms from being mistaken for backend failures.

---

# 47. Browser State Debugging

When behavior differs between users or sessions, inspect:

* cookies;
* local storage;
* session storage;
* cached assets;
* authentication state;
* service-worker state where applicable.

Clear browser state only when necessary.

Record whether the problem disappears after clearing state.

---

# 48. Authentication Debugging

Authentication failures should be separated into:

```text id="g5qj1h"
Identity
  ↓
Credential validation
  ↓
Session/token
  ↓
User resolution
  ↓
Tenant context
  ↓
Branch context
  ↓
Authorization
```

Do not treat every `401` or `403` as the same problem.

---

# 49. Authorization Debugging

When a permission failure occurs, inspect:

* user identity;
* role;
* permission;
* branch scope;
* resource ownership;
* action;
* subscription state;
* policy evaluation.

The expected authorization chain is:

```text id="l0n6wy"
Identity
 → Tenant
 → Branch Scope
 → Role
 → Permission
 → Resource Scope
 → Action
```

---

# 50. Tenant Isolation Debugging

Cross-tenant behavior requires special attention.

Tests should verify that:

```text id="w6y4js"
Tenant A user
     ↓
Tenant A resource → allowed

Tenant A user
     ↓
Tenant B resource → denied
```

A local developer must not bypass tenant isolation by directly manipulating IDs.

---

# 51. Branch Isolation Debugging

Where a user has limited branch scope:

```text id="w6v7xa"
Allowed branch
    ↓
Allowed

Unauthorized branch
    ↓
Denied
```

The same rule must be verified through the relevant application and API paths.

---

# 52. Offline Debugging

Offline failures should be investigated across:

```text id="6f1h5v"
Local State
   ↓
Offline Queue
   ↓
Transaction Identifier
   ↓
Sync Request
   ↓
Server Validation
   ↓
Persistence
   ↓
Sync Confirmation
```

Inspect each stage independently.

---

# 53. Synchronization Failure Debugging

For a synchronization failure, identify:

* local operation;
* operation identifier;
* synchronization attempt;
* server response;
* retry count;
* conflict state;
* final database state.

The same operation must not accidentally create duplicate financial or inventory effects.

---

# 54. Race Condition Debugging

Concurrency bugs may disappear when debugging because timing changes.

Use controlled tests rather than relying only on breakpoints.

Useful evidence includes:

* timestamps;
* transaction IDs;
* operation IDs;
* lock behavior;
* ordering;
* concurrent request logs.

The goal is to reproduce the condition under controlled concurrency.

---

# 55. Flaky Test Investigation

A flaky test is a test that sometimes passes and sometimes fails without an intentional input change.

Do not simply rerun it until it passes.

Investigate:

* shared state;
* test ordering;
* timing;
* concurrency;
* asynchronous cleanup;
* database isolation;
* random data;
* external dependencies;
* timezone;
* system clock;
* resource exhaustion.

A flaky test reduces confidence in the entire test suite.

---

# 56. Flaky Test Handling

When a flaky test is identified:

1. reproduce the flakiness;
2. identify likely cause;
3. isolate the test;
4. fix the underlying problem;
5. rerun repeatedly;
6. verify stability;
7. document the issue if necessary.

Temporarily disabling a flaky test should require explicit justification and tracking.

---

# 57. Test Isolation

Tests must not depend on execution order unless the test explicitly validates ordering.

Each test should control:

* data;
* authentication;
* tenant;
* branch;
* time;
* external dependencies;
* queue state.

---

# 58. Time-Dependent Tests

Tests involving time should use controlled time where practical.

Examples:

* subscription expiration;
* salary due date;
* scheduled notifications;
* report periods;
* daily register behavior.

Avoid tests that depend on the real current clock unless real-time behavior is specifically being tested.

---

# 59. Randomized Tests

Random data can reveal useful bugs but should remain reproducible.

When randomization is used, record the seed or equivalent reproduction information.

Example:

```text id="7r9c1x"
Failure:
Random test failed

Reproduction:
seed = <recorded seed>
```

---

# 60. Test Cleanup

Tests should clean up their state.

Cleanup may include:

* database records;
* temporary files;
* queue messages;
* cache entries;
* browser state;
* mock servers.

Cleanup must not remove data outside the test scope.

---

# 61. External Service Failures

Integration tests should simulate failures where appropriate.

Examples:

* timeout;
* connection failure;
* invalid response;
* rate limit;
* authentication failure;
* service unavailable.

The application should demonstrate the expected recovery behavior.

---

# 62. Test Evidence

Important test results should be reproducible and reviewable.

Evidence may include:

* test command;
* test result;
* relevant logs;
* screenshots where appropriate;
* API request/response;
* database verification;
* performance measurements.

Evidence must not contain secrets or unnecessary sensitive data.

---

# 63. Debugging Evidence

When asking another developer for help, provide:

```text id="6gq5hv"
Problem
Expected behavior
Actual behavior
Reproduction steps
Environment
Relevant logs
Relevant test
What was already investigated
```

Avoid sending an entire repository when a focused reproduction is sufficient.

---

# 64. Local Test Command Documentation

The project should provide standard commands for common test scopes.

Conceptually:

```text id="j7v8pi"
Run unit tests
Run domain tests
Run backend tests
Run API tests
Run frontend tests
Run integration tests
Run end-to-end tests
Run full suite
Run coverage
```

The exact commands should be defined by the project tooling.

---

# 65. Test Selection by Change Risk

A useful mapping is:

| Change                   | Minimum validation                 |
| ------------------------ | ---------------------------------- |
| Pure utility logic       | Unit tests                         |
| Domain rule              | Domain tests                       |
| Use case                 | Application tests                  |
| Repository               | Database integration tests         |
| Migration                | Migration tests                    |
| API contract             | API contract tests                 |
| Frontend component       | Component tests                    |
| Critical UI workflow     | E2E test                           |
| Authentication           | Security tests                     |
| Authorization            | Security + integration tests       |
| Inventory                | Domain + integration tests         |
| Financial logic          | Domain + integration + regression  |
| Offline sync             | Sync + integration + failure tests |
| Concurrency              | Concurrency tests                  |
| Deployment configuration | Environment/deployment validation  |

The exact scope may be expanded according to risk.

---

# 66. Coverage

Coverage metrics are useful indicators but are not proof of correctness.

High coverage can still miss:

* incorrect business assumptions;
* authorization flaws;
* concurrency problems;
* synchronization failures;
* invalid state transitions.

Coverage should therefore support, not replace, meaningful behavioral tests.

---

# 67. Test Failure Classification

Failures should be classified before fixing.

Possible categories:

```text id="0y6v7x"
Product defect
Test defect
Environment problem
Dependency problem
Configuration problem
Data problem
Infrastructure problem
Flaky behavior
Expected behavior changed
```

This prevents developers from changing production code when the real problem is the test or environment.

---

# 68. Test Defects

A test may be incorrect when:

* expected behavior changed intentionally;
* setup is invalid;
* assertions are wrong;
* test depends on stale schema;
* test data is invalid;
* mocking no longer matches the contract.

A test should be changed only when the intended behavior has actually changed.

---

# 69. Environment Failures

If tests fail because the environment is incorrect:

1. identify the environment problem;
2. fix the environment;
3. rerun the test;
4. determine whether the application itself also fails.

Do not change application logic to compensate for a broken local environment.

---

# 70. Dependency Failures

When a dependency causes test failures:

* verify installed version;
* compare with project lock/configuration;
* inspect dependency changes;
* determine compatibility;
* update dependencies through the dependency-management workflow.

Do not silently install an arbitrary version and leave the project inconsistent.

---

# 71. Test Debugging with Git

When a regression is difficult to locate, Git history can help identify the introduction point.

Useful techniques include:

* inspecting recent commits;
* comparing branches;
* identifying changed files;
* binary search through commits when appropriate.

Historical debugging should remain traceable to the relevant change.

---

# 72. Regression Investigation

When a previously passing behavior breaks:

```text id="4o1e8m"
Identify last known good state
        ↓
Compare changes
        ↓
Reproduce failure
        ↓
Locate responsible change
        ↓
Determine root cause
        ↓
Fix
        ↓
Add regression test
```

---

# 73. Debugging Architecture Boundaries

If debugging reveals that a module is responsible for behavior outside its intended responsibility, do not automatically add more code to the module.

Consider whether the issue indicates:

* incorrect dependency direction;
* misplaced business rule;
* duplicated logic;
* missing abstraction;
* incorrect domain boundary.

Architectural problems should be handled through the appropriate architecture and ADR workflows.

---

# 74. Debugging and Documentation

If debugging reveals an important architectural or workflow fact that was previously undocumented, the relevant documentation should be updated.

Examples:

* hidden dependency;
* required local service;
* important failure mode;
* synchronization constraint;
* database invariant;
* security requirement.

The goal is to prevent the same discovery from being repeated by future developers.

---

# 75. Debugging and AI Tools

AI tools may assist with:

* interpreting stack traces;
* suggesting hypotheses;
* generating test cases;
* identifying likely failure locations;
* explaining unfamiliar code;
* comparing logs.

AI output must be treated as a hypothesis.

Developers must verify:

* actual code;
* actual runtime behavior;
* actual database state;
* actual tests;
* actual requirements.

Secrets and sensitive data must not be unnecessarily provided to AI tools.

---

# 76. Test-Driven and Test-First Development

Test-first development is encouraged when appropriate.

For a clear business rule:

```text id="4z2f6k"
Requirement
   ↓
Failing test
   ↓
Implementation
   ↓
Passing test
   ↓
Refinement
```

The project does not require every change to use strict test-driven development.

The appropriate testing approach depends on the change.

---

# 77. Debugging Completion Criteria

A debugging task is complete when:

* the problem is understood;
* the root cause is identified;
* the fix is implemented;
* the original failure is no longer reproducible;
* relevant regression tests pass;
* no unrelated behavior is broken;
* temporary debugging code is removed;
* documentation is updated when required.

---

# 78. Test Completion Criteria

A change is ready for review when:

* relevant focused tests pass;
* required broader tests pass;
* failures have been investigated;
* new behavior has appropriate tests;
* regression coverage exists for important bugs;
* test data is controlled;
* no production resources were used accidentally;
* relevant logs contain no sensitive information;
* required manual validation is complete.

---

# 79. Local Testing Checklist

```text id="gk4b8a"
[ ] Correct branch checked out
[ ] Correct runtime active
[ ] Dependencies installed
[ ] Development/test environment selected
[ ] Test database available
[ ] Required services running
[ ] Relevant test scope identified
[ ] Focused tests executed
[ ] Failures investigated
[ ] Root cause identified
[ ] Fix implemented
[ ] Failed test rerun
[ ] Related tests rerun
[ ] Regression tests considered
[ ] Broader suite executed when required
[ ] No production resources used
[ ] No secrets exposed in logs/evidence
[ ] Temporary debug code removed
[ ] Documentation updated when necessary
```

---

# 80. Bug Fix Checklist

```text id="7n3q0v"
[ ] Bug reproduced
[ ] Expected behavior identified
[ ] Actual behavior identified
[ ] Root cause investigated
[ ] Reproduction test added where practical
[ ] Fix implemented
[ ] Original failure passes
[ ] Related tests pass
[ ] Regression suite reviewed
[ ] Security implications checked
[ ] Data implications checked
[ ] Performance implications checked
[ ] Debugging artifacts removed
```

---

# 81. Test Failure Decision Tree

```text
Test Failed
    ↓
Can it be reproduced?
    ├── No → Investigate environment/flakiness
    └── Yes
          ↓
Is expected behavior correct?
    ├── No → Update requirement/test intentionally
    └── Yes
          ↓
Is the test correct?
    ├── No → Fix test
    └── Yes
          ↓
Application defect
          ↓
Fix implementation
          ↓
Run regression tests
```

---

# 82. Development Test Strategy

The preferred local strategy is:

```text
Fast feedback
    ↓
Focused tests
    ↓
Related tests
    ↓
Regression tests
    ↓
Full suite when required
```

This balances developer productivity with confidence.

---

# 83. Critical Workflow Validation

The following areas deserve stronger local validation because errors can affect business integrity:

* authentication;
* authorization;
* tenant isolation;
* branch isolation;
* cash register;
* payments;
* refunds;
* inventory;
* recipes;
* synchronization;
* subscription restrictions;
* payroll;
* financial reports.

Changes affecting these areas should not rely only on superficial UI testing.

---

# 84. Test Environment Recovery

If the local test environment becomes corrupted:

```text id="r7w1kn"
Stop tests
   ↓
Inspect environment
   ↓
Reset test state
   ↓
Recreate test database if necessary
   ↓
Reapply migrations
   ↓
Restore test fixtures
   ↓
Run focused test
```

Test-environment recovery must not affect development or production data.

---

# 85. Test and Debugging Invariants

The following rules are mandatory:

1. Tests must validate intended behavior.
2. Tests must be reproducible where practical.
3. Tests must use isolated state.
4. Tests must not use production data.
5. Tests must not use production credentials.
6. Test databases must be separated from production.
7. Focused tests should be run before broad suites when practical.
8. Significant changes require appropriate regression testing.
9. Critical business rules require behavioral tests.
10. Financial behavior requires persisted-state verification.
11. Inventory behavior requires persisted-state verification.
12. Authorization behavior must test both allowed and denied actions.
13. Tenant isolation must be tested.
14. Branch isolation must be tested.
15. Offline behavior must be tested under controlled connectivity changes.
16. Synchronization retries must be tested.
17. Duplicate synchronization must be tested.
18. Concurrency-sensitive behavior requires concurrency tests.
19. Background jobs must be tested for failure and retry behavior.
20. Scheduled jobs must be manually testable.
21. External integrations must have controlled failure tests where appropriate.
22. Test failures must be investigated rather than ignored.
23. Flaky tests must be investigated.
24. Tests must not depend on execution order unless intentionally required.
25. Test data must be controlled.
26. Time-dependent tests should use controlled time where practical.
27. Randomized tests should be reproducible.
28. Temporary debugging code must not remain accidentally.
29. Logs must not expose secrets.
30. Debugging must identify root causes.
31. Bug fixes should add regression protection where practical.
32. Test failures must be classified before modifying production code.
33. CI failures should be reproducible locally when practical.
34. Coverage must not be treated as proof of correctness.
35. AI suggestions must be verified against actual behavior.
36. Architecture problems must not be hidden inside local fixes.
37. Important discoveries must update documentation.
38. Local tests must not accidentally affect external production systems.
39. Test completion must include relevant regression validation.
40. Testing is part of development, not a final optional step.

---

# 86. Relationship to Other Development Documents

### DEV-01 — Development Architecture Overview

Defines the overall development lifecycle.

### DEV-06 — Backend Development Standards

Defines backend implementation practices that are tested through this workflow.

### DEV-07 — Frontend Development Standards

Defines frontend behavior that must be validated locally.

### DEV-08 — Database Development and Migration Workflow

Defines database changes and migration validation.

### DEV-09 — API Development and Contract Change Workflow

Defines API contract changes and compatibility.

### DEV-10 — Documentation-First Development Workflow

Defines documentation before significant implementation changes.

### DEV-11 — ADR and Architecture Decision Workflow

Defines architectural decisions discovered during development or debugging.

### DEV-12 — Local Development Environment

Defines the environment in which these tests and debugging workflows execute.

### DEV-14 — Dependency and Package Management

Defines dependency versions and dependency changes.

### DEV-15 — Configuration and Feature Flag Development

Defines configuration and feature-flag behavior.

### DEV-16 — AI-Assisted Development Guidelines

Defines safe AI usage during development and debugging.

### DEV-17 — Developer Tooling and Automation

Defines scripts and automation used to execute development workflows.

### DEV-18 — Development Guardrails and Quality Rules

Defines overarching development quality rules.

---

# 87. Relationship to Testing Documentation

This document provides the developer workflow for using the testing architecture.

The `docs/12_Testing` section defines the broader testing strategy and architecture, including:

* test pyramid;
* test levels;
* testing architecture;
* integration testing;
* end-to-end testing;
* offline testing;
* concurrency testing;
* financial testing;
* inventory testing;
* security testing;
* AI testing;
* performance testing;
* resilience testing;
* CI quality gates;
* test data and environments.

This document explains how a developer executes and debugs those tests locally.

---

# 88. Final Principle

Testing and debugging are not separate from development.

They are the mechanism through which developers determine whether an implementation actually satisfies the intended system behavior.

The preferred workflow is:

```text id="y9l8x0"
Understand
   ↓
Change
   ↓
Test
   ↓
Observe
   ↓
Reproduce
   ↓
Debug
   ↓
Fix
   ↓
Retest
   ↓
Regress
   ↓
Review
```

A developer should not ask only:

> Does the code run?

The more important questions are:

> Does it behave correctly?

> Does it preserve existing behavior?

> Does it protect data and security boundaries?

> Does it remain correct under failure?

> Does it remain correct when retried, duplicated, disconnected, or executed concurrently?

> Can another developer reproduce and verify the result?

**Final rule:**

**Every meaningful change must be validated at the appropriate test level, and every important failure must be investigated to its root cause rather than hidden or bypassed.**

