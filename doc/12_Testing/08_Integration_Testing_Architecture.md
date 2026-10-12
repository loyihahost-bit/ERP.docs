# 08 — Integration Testing Architecture

**Document ID:** TEST-08
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`
**Depends On:** TEST-01, TEST-02, TEST-05, TEST-06, TEST-07
**Related:** TEST-09, TEST-10, TEST-11, TEST-12, TEST-13, TEST-14, TEST-16, TEST-18, TEST-19

---

## 1. Purpose

This document defines the integration testing architecture for the FastFood ERP system.

Integration testing verifies that independently testable components and subsystems work correctly together across real architectural boundaries.

The purpose is to detect failures that cannot be reliably identified by isolated unit, domain, application, repository, or API contract tests.

Integration tests verify interactions such as:

* application services with repositories;
* repositories with PostgreSQL;
* API layers with application services;
* transaction boundaries;
* database state changes;
* event publication and consumption;
* background jobs;
* Redis-backed coordination where applicable;
* external service adapters;
* authentication and authorization boundaries;
* offline synchronization components;
* inventory and order processing;
* financial and cash workflows;
* notification workflows;
* file/document processing;
* AI subsystem boundaries;
* printer/device integration boundaries;
* subscription and feature-access boundaries.

Integration testing must establish confidence that subsystem boundaries preserve the system's intended behavior.

---

# 2. Integration Testing Boundary

Integration testing sits between isolated component tests and complete end-to-end tests.

```text
Unit / Domain
     ↓
Application / Use Case
     ↓
Integration Boundaries
     ↓
Subsystems
     ↓
Complete System / E2E
```

The central question is:

> **Do the participating subsystems communicate and coordinate correctly across their real boundaries?**

Integration testing is not intended to prove every internal implementation detail.

---

# 3. What Integration Testing Proves

Integration tests primarily prove:

* data is transferred correctly between subsystems;
* contracts between internal components remain compatible;
* transactions behave correctly across boundaries;
* persistence and application behavior agree;
* events are produced and consumed correctly;
* background processing coordinates correctly;
* external adapters behave according to their contracts;
* failures propagate or recover according to policy;
* subsystem state remains consistent;
* retries do not create unintended duplicate effects;
* authorization context is preserved across subsystem boundaries;
* branch and business context is not lost;
* asynchronous workflows eventually reach the correct state where eventual consistency is intended.

---

# 4. What Integration Testing Does Not Replace

Integration tests do not replace:

### Unit Testing

Unit tests verify isolated behavior.

### Domain Testing

Domain tests verify business rules and invariants.

### Application Testing

Application tests verify use-case orchestration.

### Repository Testing

Repository tests verify persistence behavior against the database.

### API Contract Testing

API contract tests verify external API schemas and compatibility.

### End-to-End Testing

E2E tests verify complete user-visible workflows.

Each level provides different evidence.

---

# 5. Integration Test Definition

An integration test should involve at least one meaningful architectural boundary.

Examples:

```text
Application Service
        ↓
Repository
        ↓
PostgreSQL
```

or:

```text
Order Service
      ↓
Event / Queue
      ↓
Inventory Processing
```

or:

```text
API
 ↓
Application
 ↓
Database
```

A test that mocks every boundary is not an integration test.

---

# 6. Integration Boundary Types

The system may contain several integration boundary categories.

## 6.1 In-Process Boundaries

Examples:

* application service → repository;
* application service → domain service;
* application service → event publisher;
* service → policy component.

These may be tested together when their interaction is important.

---

## 6.2 Database Boundaries

Examples:

* application → repository → PostgreSQL;
* transaction → multiple repositories;
* persistence → database constraints.

These tests should use a real test database or an equivalent environment capable of reproducing relevant database behavior.

---

## 6.3 API Boundaries

Examples:

* API → application service;
* API → authentication context;
* API → database-backed workflow.

TEST-07 focuses on contract correctness.

TEST-08 verifies interaction between API and participating subsystems.

---

## 6.4 Asynchronous Boundaries

Examples:

```text
Application
    ↓
Queue
    ↓
Worker
    ↓
Repository
```

Integration tests verify that the complete asynchronous boundary works as intended.

---

## 6.5 External Service Boundaries

Examples may include:

* identity services;
* payment services;
* messaging services;
* delivery services;
* government services;
* third-party APIs.

The system should normally test its adapter and integration behavior without depending on uncontrolled production services.

---

## 6.6 Device and Peripheral Boundaries

Examples:

* printer communication;
* POS device communication;
* trusted device integration;
* local branch hardware.

Tests should verify the software boundary and failure behavior without requiring uncontrolled physical hardware for every CI run.

---

# 7. Integration Test Strategy

Integration tests should be:

* purposeful;
* deterministic;
* isolated;
* representative;
* failure-aware;
* repeatable;
* environment-controlled;
* risk-based.

Not every interaction requires the same level of integration testing.

The most important integration boundaries are those where incorrect coordination could cause:

* financial loss;
* inventory corruption;
* incorrect orders;
* unauthorized access;
* cross-branch data exposure;
* duplicate operations;
* synchronization errors;
* incorrect subscription enforcement;
* operational downtime.

---

# 8. Real Dependencies vs Test Doubles

Integration testing should use real dependencies when their behavior is part of the integration being tested.

For example:

```text
Repository ↔ PostgreSQL
```

should normally use a real PostgreSQL test environment rather than mocking SQL behavior.

Similarly, an integration involving a queue should use the actual queue technology or a sufficiently faithful integration environment when queue semantics matter.

Test doubles remain appropriate for boundaries that are:

* expensive;
* unavailable;
* externally controlled;
* destructive;
* non-deterministic;
* unsuitable for CI.

The decision must be based on what behavior the test is intended to prove.

---

# 9. Integration Test Levels

Integration tests can be organized into levels.

## Level 1 — Component Integration

A small number of closely related components interact.

Example:

```text
Application Service
        ↓
Repository
```

---

## Level 2 — Subsystem Integration

Several components form a meaningful subsystem.

Example:

```text
Order Application
      ↓
Order Repository
      ↓
PostgreSQL
      ↓
Order Event
```

---

## Level 3 — Cross-Subsystem Integration

Multiple business subsystems participate.

Example:

```text
Order
  ↓
Inventory
  ↓
Payment
  ↓
Notification
```

---

## Level 4 — External Integration

FastFood interacts with an external system.

Example:

```text
FastFood
   ↓
External Provider
```

The test scope must remain targeted to the integration boundary rather than becoming a full E2E test.

---

# 10. Application-to-Database Integration

Application/database integration is one of the most important integration areas.

Typical flow:

```text
API / Application
       ↓
Use Case
       ↓
Repository
       ↓
PostgreSQL
       ↓
Repository
       ↓
Application Result
```

Tests should verify that:

* application input is correctly persisted;
* persisted state can be retrieved;
* transactions behave correctly;
* database constraints interact correctly with application behavior;
* multiple repositories participate correctly when required;
* failures produce the expected application outcome.

TEST-06 defines deeper repository/database testing.

TEST-08 verifies the broader subsystem interaction.

---

# 11. Multi-Repository Transaction Integration

Some use cases require multiple persistence operations.

Example:

```text
Create Order
     ↓
Save Order
     ↓
Save Order Items
     ↓
Reserve / Deduct Inventory
     ↓
Save Audit Information
```

Integration tests must verify whether these operations are intended to share one transaction.

Tests should cover:

### Successful Transaction

All intended changes are committed.

### Partial Failure

A failure causes the correct rollback or compensating behavior.

### Retry

A retry does not create unintended duplicate state.

### Recovery

The resulting state remains consistent after a recoverable failure.

The exact transaction ownership is defined by application and persistence architecture.

---

# 12. Event Integration Testing

Events may connect independent subsystems.

Example:

```text
Order Accepted
      ↓
Event Published
      ↓
Consumer
      ↓
Inventory / Kitchen / Notification
```

Tests should verify:

* event is emitted when required;
* event contains required information;
* event identity is stable;
* consumer accepts the event;
* consumer produces expected state changes;
* duplicate delivery is handled according to policy;
* invalid events are rejected or quarantined;
* failed processing can be retried safely.

Events must not be considered successful merely because they were placed onto a queue.

The downstream effect must be verified where required.

---

# 13. Eventual Consistency

Some integrations may intentionally use eventual consistency.

In these cases, tests must not incorrectly require immediate consistency.

Instead, they should verify:

```text
Initial State
     ↓
Event / Message
     ↓
Processing
     ↓
Expected Final State
```

The test must have a deterministic way to observe completion.

Tests must not use arbitrary long sleeps to wait for asynchronous processing.

A controlled polling or synchronization mechanism should be used.

---

# 14. Queue Integration

Where queues are part of the architecture, integration tests should verify:

* message publication;
* message structure;
* queue routing;
* consumer processing;
* acknowledgement behavior;
* retry behavior;
* failure handling;
* duplicate delivery;
* dead-letter or quarantine behavior where defined;
* message ordering where required;
* idempotent processing.

The test must verify the behavior that matters to the application rather than internal queue implementation details.

---

# 15. Background Worker Integration

Worker integration should verify:

```text
Application
     ↓
Job / Message
     ↓
Worker
     ↓
Business Operation
     ↓
Persistent Result
```

Examples include:

* notification processing;
* report generation;
* synchronization;
* subscription checks;
* scheduled maintenance;
* asynchronous inventory operations.

Tests must verify both successful and failed worker execution.

---

# 16. Scheduler Integration

Scheduled operations may affect business state.

Examples:

* subscription expiration processing;
* notifications;
* cleanup;
* data lifecycle operations;
* recurring reports;
* background synchronization.

Tests should verify:

* job is triggered;
* correct application operation is executed;
* repeated execution is safe;
* execution failure is recoverable;
* scheduler retries do not create duplicates.

Exact scheduling configuration is outside this document.

---

# 17. Redis and Cache Integration

If Redis or another cache is part of a subsystem boundary, integration tests should verify only behavior that depends on the cache contract.

Examples:

* cache population;
* cache retrieval;
* invalidation;
* expiration;
* stale-data handling;
* cache failure fallback;
* consistency between source of truth and cache.

The database or authoritative source must remain the source of business truth where architecture requires it.

A cache must not silently become the authoritative source merely because an integration test passes.

---

# 18. Cache Failure Testing

Integration tests should verify behavior when cache infrastructure is:

* unavailable;
* slow;
* returning expired data;
* temporarily inconsistent;
* cleared unexpectedly.

The expected result may be:

```text
Cache Available
    ↓
Normal Fast Path
```

or:

```text
Cache Failure
    ↓
Authoritative Source
    ↓
Correct Result
```

depending on subsystem requirements.

---

# 19. API-to-Application Integration

API integration tests should verify:

```text
HTTP Request
    ↓
API Layer
    ↓
Application Use Case
    ↓
Result
    ↓
HTTP Response
```

Tests should verify:

* request mapping;
* context propagation;
* application invocation;
* response mapping;
* validation boundaries;
* error mapping;
* transaction behavior;
* relevant audit/event behavior.

TEST-07 remains responsible for detailed schema and contract validation.

---

# 20. Authentication Context Propagation

Integration tests should verify that authenticated context survives subsystem boundaries.

For example:

```text
Request
 ↓
Identity
 ↓
Business Context
 ↓
Branch Scope
 ↓
Application
 ↓
Repository / Event
```

The system must not accidentally lose:

* identity;
* business context;
* branch context;
* authorization context;
* operation identity.

Detailed security policy belongs to the Security documentation and TEST-14.

Integration testing verifies that required context is correctly propagated.

---

# 21. Tenant and Branch Context Integration

FastFood is a multi-business and multi-branch system.

Integration tests must verify that subsystem interactions preserve the correct scope.

Example:

```text
Business A / Branch 1
        ↓
Order
        ↓
Inventory
```

must not accidentally produce:

```text
Business B / Branch X
        ↓
Inventory Change
```

Integration tests should cover:

* business context propagation;
* branch context propagation;
* cross-branch operations where explicitly allowed;
* rejection of invalid scope;
* background job scope;
* event scope;
* asynchronous processing scope.

---

# 22. Order Integration

Order processing is a high-risk integration area.

A representative flow may be:

```text
Order Request
     ↓
Order Application
     ↓
Order Persistence
     ↓
Inventory Processing
     ↓
Kitchen / Printer Event
     ↓
Payment
     ↓
Order Completion
```

Integration tests should verify the intended subset of this flow at the subsystem level.

Examples:

* order creation persists correctly;
* order items remain associated with the order;
* inventory interaction receives correct information;
* kitchen event is produced correctly;
* payment completion updates order state;
* failures do not create invalid partial state.

Complete cashier workflows belong to TEST-09.

---

# 23. Inventory Integration

Inventory is another high-risk subsystem boundary.

Integration tests should verify interactions between:

```text
Order
  ↓
Recipe
  ↓
Inventory
  ↓
Stock Movement
```

and:

```text
Purchase / Adjustment
       ↓
Inventory
       ↓
Stock State
```

Tests should verify:

* correct product identity;
* correct branch;
* correct quantity;
* recipe-derived consumption;
* semi-finished dependencies;
* stock movement creation;
* insufficient stock behavior;
* transaction consistency.

Detailed inventory rules are tested by TEST-13.

---

# 24. Recipe Integration

Recipe processing may involve:

```text
Product
   ↓
Recipe
   ↓
Ingredient
   ↓
Semi-Finished Product
   ↓
Inventory
```

Integration tests should verify that subsystem boundaries preserve relationships.

Examples:

* product references the correct recipe;
* recipe references correct components;
* semi-finished products resolve correctly;
* inventory receives the intended consumption information;
* archived recipes are handled according to policy.

---

# 25. Financial Integration

Financial integration boundaries require high test depth.

Examples:

```text
Order
  ↓
Payment
  ↓
Cash Register
  ↓
Report
```

and:

```text
Refund
  ↓
Approval
  ↓
Payment Adjustment
  ↓
Cash / Financial Record
```

Integration tests must verify consistency across participating subsystems.

Detailed financial testing is defined by TEST-12.

---

# 26. Cash Register Integration

Cash register integration tests should cover:

* opening;
* active register state;
* order/payment interaction;
* handover;
* closing;
* discrepancy;
* correction;
* reporting;
* notification.

The test must verify that state transitions across subsystems remain consistent.

---

# 27. Notification Integration

Notifications may be triggered by business events.

Examples:

* subscription ending;
* low stock;
* large refund;
* cash shortage;
* salary due;
* inventory variance;
* branch loss.

Integration tests should verify:

```text
Business Event
      ↓
Notification Creation
      ↓
Correct Recipient / Scope
      ↓
Notification State
```

Tests should also verify failure handling when the notification delivery mechanism is unavailable.

---

# 28. File and Report Integration

Reports, imports, and exports may cross multiple subsystem boundaries.

Example:

```text
Request
  ↓
Authorization
  ↓
Query / Application
  ↓
Report Generation
  ↓
File Creation
  ↓
Storage
  ↓
Download
```

Integration tests should verify:

* correct data source;
* correct business/branch scope;
* generated structure;
* file creation;
* storage integration;
* failure cleanup;
* download availability.

Detailed file security belongs to the Security documentation.

---

# 29. Import Integration

Import workflows may involve:

```text
Upload
  ↓
File Validation
  ↓
Parsing
  ↓
Application Validation
  ↓
Database Transaction
  ↓
Result
```

Integration tests should verify:

* valid file processing;
* invalid file handling;
* partial failure policy;
* transaction behavior;
* duplicate handling;
* result reporting;
* scope preservation.

Imports must not create partial business state when the contract requires atomic behavior.

---

# 30. Offline Synchronization Integration

Offline synchronization is a major integration boundary.

A representative flow is:

```text
Offline Device
      ↓
Pending Operations
      ↓
Synchronization
      ↓
Server Validation
      ↓
Application
      ↓
Database
      ↓
Sync Result
      ↓
Device
```

Integration tests should verify:

* operation transfer;
* authentication context;
* business/branch context;
* ordering;
* duplicate handling;
* retries;
* conflict handling;
* accepted operations;
* rejected operations;
* quarantine behavior;
* final synchronized state.

Detailed offline behavior is defined by TEST-10.

---

# 31. Device and Printer Integration

Device integration may include:

* POS terminals;
* printers;
* trusted devices;
* local branch devices.

Integration tests should verify software-facing behavior such as:

```text
Order Accepted
      ↓
Print Request
      ↓
Printer Adapter
      ↓
Success / Failure
```

Tests should cover:

* successful communication;
* unavailable device;
* timeout;
* retry;
* duplicate request;
* failure reporting;
* recovery.

Physical hardware should not be required for every automated CI test.

Hardware-specific tests may exist separately.

---

# 32. External Service Integration

External services should be integrated through defined boundaries.

Tests should verify:

* request mapping;
* authentication configuration;
* response mapping;
* timeout behavior;
* unavailable provider;
* malformed provider response;
* retry policy;
* duplicate response;
* provider error mapping.

External services should normally be replaced with controlled test environments, simulators, or contract-compatible test doubles unless a real integration environment is specifically required.

---

# 33. Integration Failure Propagation

Integration tests must explicitly define what happens when a dependency fails.

For each important dependency:

```text
Dependency Failure
       ↓
Expected Application Behavior
```

Possible outcomes include:

* transaction rollback;
* retry;
* fallback;
* queued retry;
* partial completion;
* user-visible failure;
* operation quarantine;
* administrative alert.

The test must verify the approved behavior rather than assuming all failures require rollback.

---

# 34. Timeout Testing

Timeouts are part of integration behavior.

Tests should cover:

* dependency response within timeout;
* dependency response after timeout;
* repeated timeout;
* retry after timeout;
* operation identity after timeout.

A timeout must not accidentally result in:

```text
Unknown Client State
+
Duplicate Business Operation
```

where idempotency is required.

---

# 35. Retry Integration Testing

Retries must be tested as real integration behavior.

Tests should verify:

* retry after transient failure;
* maximum retry policy;
* duplicate prevention;
* eventual success;
* permanent failure;
* dead-letter/quarantine behavior where applicable.

Retries must not transform transient infrastructure failures into duplicate financial or inventory operations.

---

# 36. Idempotency Across Boundaries

Integration tests should verify idempotency when an operation crosses a retryable boundary.

Example:

```text
Client
  ↓
API
  ↓
Application
  ↓
Queue
  ↓
Worker
```

If a message is delivered twice, the resulting business state must remain consistent with the approved idempotency policy.

This is particularly important for:

* payments;
* refunds;
* orders;
* inventory deductions;
* synchronization;
* external service calls.

Detailed concurrency behavior belongs to TEST-11.

---

# 37. Integration Consistency

Integration tests should verify consistency across related subsystem states.

Example:

```text
Order = Paid
Payment = Completed
Cash Record = Updated
```

must not unexpectedly become:

```text
Order = Paid
Payment = Failed
Cash Record = Missing
```

unless the architecture explicitly defines such an intermediate state.

Tests must distinguish:

* temporary states;
* final states;
* recoverable states;
* invalid states.

---

# 38. State Transition Integration Testing

Subsystem interactions often change state.

Tests should verify valid transitions across boundaries.

Example:

```text
Order Created
     ↓
Accepted
     ↓
Preparing
     ↓
Ready
     ↓
Paid / Completed
```

A subsystem must not produce a state that another subsystem cannot correctly interpret.

---

# 39. Integration Test Data

Integration test data should represent realistic subsystem relationships.

Examples:

* business;
* branch;
* employee;
* role;
* product;
* recipe;
* ingredient;
* inventory;
* order;
* payment;
* register;
* subscription;
* device.

Data should be created using controlled fixtures or builders.

Tests must avoid relying on implicit database state.

---

# 40. Test Environment

Integration tests should run in an environment capable of reproducing relevant system boundaries.

Typical components may include:

```text
Application
PostgreSQL
Redis / Cache
Queue
Worker
Scheduler
External Service Test Doubles
File Storage
```

Not every integration test requires every component.

The environment should contain only dependencies needed by the specific test suite.

---

# 41. Database Isolation

Integration tests must prevent state leakage between tests.

Possible strategies include:

* isolated database;
* isolated schema;
* transaction rollback;
* deterministic fixture reset;
* isolated test containers;
* dedicated test environment.

The selected strategy must preserve realistic database behavior.

---

# 42. Parallel Integration Tests

Integration tests should support parallel execution where safe.

Parallel tests must not accidentally share:

* business records;
* branch records;
* register state;
* inventory;
* queue messages;
* filesystem paths;
* external mock state.

If a test requires exclusive access, that requirement must be explicit.

---

# 43. Time and Asynchronous Processing

Integration tests involving:

* queues;
* workers;
* schedulers;
* expiration;
* synchronization;
* notifications

must use controlled time and deterministic synchronization.

Avoid:

```text id="6r2d5q"
sleep(10)
```

as the primary synchronization strategy.

Prefer deterministic mechanisms that know when the expected processing has completed.

---

# 44. Integration Observability

Integration tests should make failures diagnosable.

Useful evidence may include:

* request identifiers;
* operation identifiers;
* event identifiers;
* database state;
* queue state;
* worker result;
* relevant logs;
* integration response;
* final subsystem state.

Tests should avoid exposing sensitive information in failure output.

---

# 45. Security Boundary Integration

Integration testing should verify that security context survives subsystem boundaries.

Examples:

```text
API
 ↓
Application
 ↓
Repository
```

and:

```text
Application
 ↓
Queue
 ↓
Worker
```

The correct business and branch scope must remain attached to the operation.

Tests should verify that a background worker cannot accidentally process an operation under an unrelated scope.

Detailed security behavior is covered by TEST-14 and the Security documentation.

---

# 46. Failure-Oriented Integration Testing

Integration testing must intentionally exercise failure paths.

Examples:

* database unavailable;
* database transaction failure;
* queue unavailable;
* worker failure;
* Redis unavailable;
* external API timeout;
* printer unavailable;
* file storage failure;
* notification failure;
* duplicate event;
* malformed event;
* partial dependency failure.

The goal is not to make every test simulate every failure.

The goal is to ensure that important integration boundaries have explicit failure evidence.

---

# 47. Integration Test Categories

Recommended categories include:

```text
tests/
└── integration/
    ├── database/
    ├── api/
    ├── events/
    ├── queues/
    ├── workers/
    ├── cache/
    ├── external/
    ├── offline/
    ├── devices/
    ├── files/
    └── workflows/
```

The exact project structure may differ.

The organization should make the integration boundary obvious.

---

# 48. Test Naming

Integration test names should describe the interaction.

Good examples:

```text
creates_order_and_persists_items
publishes_order_accepted_event_after_commit
processes_inventory_event_and_creates_stock_movement
retries_failed_notification_without_duplicate_business_effect
preserves_branch_scope_through_background_processing
rolls_back_order_and_inventory_changes_when_transaction_fails
```

Avoid names focused only on internal methods.

---

# 49. Integration Test Matrix

| Boundary          |  Success |  Failure |                     Retry |     Duplicate |    Scope |   Consistency |
| ----------------- | -------: | -------: | ------------------------: | ------------: | -------: | ------------: |
| Application → DB  | Required | Required |             As applicable | As applicable | Required |      Required |
| API → Application | Required | Required |             As applicable | As applicable | Required |      Required |
| Event → Consumer  | Required | Required |                  Required |      Required | Required |      Required |
| Queue → Worker    | Required | Required |                  Required |      Required | Required |      Required |
| Cache → Source    | Required | Required |             As applicable | As applicable | Required |      Required |
| External API      | Required | Required |                  Required |      Required | Required |      Required |
| Offline Sync      | Required | Required |                  Required |      Required | Required |      Required |
| Printer / Device  | Required | Required |                  Required |      Required | Required | As applicable |
| File / Report     | Required | Required | Required where applicable | As applicable | Required |      Required |

---

# 50. Risk-Based Integration Coverage

Higher integration coverage is required for boundaries that can cause:

### Critical Risk

* financial corruption;
* inventory corruption;
* unauthorized access;
* cross-tenant access;
* duplicate payments;
* duplicate refunds;
* duplicate inventory deductions;
* synchronization corruption.

### High Risk

* order processing;
* cash register;
* subscription enforcement;
* employee permissions;
* recipe processing;
* reporting.

### Lower Risk

* non-critical presentation metadata;
* optional notifications;
* cosmetic integrations.

Risk classification determines test depth.

It does not eliminate the requirement to test important boundaries.

---

# 51. Regression Testing

Every integration defect should result in a regression test when practical.

The regression test should be placed at the lowest integration level capable of reliably reproducing the defect.

If the defect crosses several real subsystems, an integration regression test is appropriate.

If the defect is purely domain logic, it belongs lower in the testing architecture.

---

# 52. Flaky Integration Tests

Integration tests may be more vulnerable to environmental instability than unit tests.

Flakiness can originate from:

* asynchronous timing;
* shared infrastructure;
* uncontrolled external services;
* resource exhaustion;
* race conditions;
* test data leakage.

A flaky integration test must not simply be retried indefinitely.

The root cause must be investigated.

Repeated automatic retries may hide real reliability defects.

---

# 53. Performance Considerations

Integration tests are normally slower than unit tests.

Therefore:

* keep boundaries purposeful;
* avoid unnecessary full-system setup;
* reuse environment setup safely;
* parallelize isolated tests;
* separate expensive suites where appropriate;
* run critical integration tests earlier;
* avoid duplicating the same behavior across many layers.

Integration tests should provide meaningful additional confidence.

---

# 54. CI Strategy

A recommended CI structure is:

```text
Fast Tests
    ↓
Unit / Domain
    ↓
Application
    ↓
Repository / DB
    ↓
API Contract
    ↓
Focused Integration
    ↓
Critical Integration
    ↓
E2E
```

Integration tests should be divided into suitable groups.

For example:

### Fast Integration

* API → application;
* application → repository;
* basic event flows.

### Critical Integration

* payment;
* refund;
* inventory deduction;
* order completion;
* cash register;
* synchronization.

### Extended Integration

* external integrations;
* worker/scheduler;
* device;
* file/report workflows.

---

# 55. Release Integration Testing

Before production release, critical subsystem boundaries must have current passing evidence.

At minimum, release validation should cover:

* database interaction;
* order flow integration;
* payment integration;
* inventory integration;
* authentication context;
* authorization boundary;
* event/queue processing where used;
* offline synchronization where changed;
* critical external integrations;
* background processing where changed.

The exact release gate is defined by TEST-19.

---

# 56. Integration Defect Classification

Integration failures should be classified as:

### Contract Defect

Two subsystems disagree about the expected structure or behavior.

### Coordination Defect

Subsystems work individually but fail when combined.

### Transaction Defect

Related state changes are not coordinated correctly.

### Infrastructure Defect

The required dependency is unavailable or incorrectly configured.

### Data Defect

Invalid or inconsistent test data causes misleading behavior.

### Timing / Concurrency Defect

The integration fails because of race, ordering, timeout, or retry behavior.

### Test Defect

The test itself does not represent the intended integration contract.

---

# 57. Anti-Patterns

The following practices should be avoided.

## 57.1 Mocking Every Dependency

If every boundary is mocked, the test may prove only that mocks behave as configured.

---

## 57.2 Full System for Every Integration Test

Not every integration test needs the complete application stack.

This makes tests unnecessarily slow and difficult to diagnose.

---

## 57.3 Testing Only Happy Paths

Integration failures frequently occur at boundaries.

Failure paths are mandatory for high-risk integrations.

---

## 57.4 Arbitrary Sleeps

Fixed delays make tests slow and flaky.

Use deterministic synchronization.

---

## 57.5 Shared Mutable Test Data

Shared state creates hidden dependencies and false failures.

---

## 57.6 Production Dependencies in Normal CI

Normal CI should not depend on uncontrolled production services.

---

## 57.7 Ignoring Scope

Integration tests that do not verify business and branch context can miss serious isolation defects.

---

## 57.8 Testing Implementation Instead of Interaction

Tests should verify meaningful boundary behavior rather than internal call sequences unless those sequences are themselves contractual.

---

# 58. Integration Test Review Checklist

For each important integration test, reviewers should ask:

* [ ] What boundary is being tested?
* [ ] Why is this behavior not sufficiently covered at a lower level?
* [ ] Are the relevant real dependencies present?
* [ ] Is the test deterministic?
* [ ] Is test data isolated?
* [ ] Is business scope preserved?
* [ ] Is branch scope preserved?
* [ ] Is transaction behavior verified where relevant?
* [ ] Is failure behavior tested?
* [ ] Is retry behavior tested where relevant?
* [ ] Is duplicate behavior tested where relevant?
* [ ] Is final state verified?
* [ ] Is the test sufficiently diagnostic?
* [ ] Is the test duplicated elsewhere unnecessarily?

---

# 59. Mandatory Integration Testing Rules

The following rules are mandatory.

1. Integration tests must verify real architectural boundaries.
2. Integration tests must not be reduced to mocked unit tests.
3. Important database interactions must use realistic database behavior.
4. Important asynchronous boundaries must be tested.
5. High-risk financial and inventory integrations require failure testing.
6. Business and branch context must survive subsystem boundaries.
7. Retryable operations must be tested for duplicate effects where relevant.
8. Transaction behavior must be tested where multiple state changes are coordinated.
9. Event consumers must be tested against realistic event structures.
10. Integration tests must use controlled test data.
11. Integration tests must be deterministic.
12. Arbitrary sleeps must not be the primary synchronization mechanism.
13. External production systems must not be required for normal CI.
14. Integration failures must be diagnosable.
15. Critical integration tests must participate in release validation.
16. Integration defects should produce regression tests where practical.
17. Tests must not be weakened merely to accommodate an undocumented subsystem change.
18. Security and scope context must not be lost across asynchronous or background boundaries.

---

# 60. Integration Invariants

### Integration Invariant 1

Subsystems must agree on the data and behavior required at their boundaries.

### Integration Invariant 2

A successful integration must produce a valid final subsystem state.

### Integration Invariant 3

Failed multi-step operations must follow their defined rollback or recovery policy.

### Integration Invariant 4

Retries must not create unintended duplicate business effects.

### Integration Invariant 5

Business and branch scope must remain associated with the operation throughout the integration flow.

### Integration Invariant 6

Asynchronous processing must eventually produce the defined result when the operation is designed for eventual consistency.

### Integration Invariant 7

Invalid messages or requests must not silently create invalid business state.

### Integration Invariant 8

Integration tests must remain deterministic and isolated.

### Integration Invariant 9

High-risk integration boundaries must have both success and failure evidence.

### Integration Invariant 10

Integration testing must provide confidence that independently correct subsystems remain correct when combined.

---

# 61. Acceptance Criteria

This document is considered correctly implemented when:

* integration boundaries are explicitly identified;
* integration tests have a clear scope;
* real dependencies are used where their behavior matters;
* test doubles are used deliberately rather than universally;
* database integration is covered;
* API/application integration is covered;
* event and queue integration is covered where applicable;
* background workers are covered where applicable;
* external integration boundaries are covered;
* business and branch context propagation is tested;
* transaction and consistency behavior is tested;
* retries and duplicate processing are tested where relevant;
* failure paths are covered;
* offline synchronization integration is covered;
* high-risk financial and inventory integrations receive stronger coverage;
* integration tests are deterministic;
* CI includes appropriate integration suites;
* critical integration tests participate in release readiness.

---

# 62. Final Integration Testing Rule

An integration test must answer a specific architectural question:

> **Do these independently testable subsystems still behave correctly when connected through their real boundary?**

The testing progression is:

```text
Unit
  ↓
Domain
  ↓
Application
  ↓
Repository / Database
  ↓
API Contract
  ↓
Integration
  ↓
End-to-End
```

Each level adds a different type of evidence.

The goal of integration testing is not to repeat lower-level tests. Its purpose is to prove that subsystem boundaries preserve:

* data meaning;
* transaction behavior;
* business context;
* branch scope;
* event behavior;
* retry safety;
* consistency;
* failure handling;
* and operational correctness.

**The system is not considered integration-safe merely because each subsystem passes its isolated tests. The boundaries between those subsystems must also be proven.**

