# Backend Testing and Quality Assurance Architecture

**Document ID:** BA-17
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This document defines the backend testing and quality assurance architecture for FastFood ERP.

The primary goal is to ensure that backend changes:

* do not break existing business behavior;
* do not violate Business or Branch isolation;
* do not compromise security;
* do not corrupt financial or inventory data;
* do not break offline synchronization;
* do not silently modify historical data;
* remain compatible with database constraints and migrations;
* meet defined performance and reliability targets.

Testing must validate not only whether individual functions work, but also whether the entire system preserves its business invariants under normal, concurrent, offline, retry and failure conditions.

---

## 2. Quality Principles

The backend follows these principles:

1. Correctness before feature completeness.
2. Business invariants must be testable.
3. Security boundaries must be tested explicitly.
4. Important business operations require integration tests.
5. Database constraints must be tested against real PostgreSQL behavior.
6. Offline synchronization requires dedicated tests.
7. Idempotency must be tested with repeated requests.
8. Concurrency must be tested explicitly for critical operations.
9. Historical data integrity must be protected by regression tests.
10. Performance must be measured against defined targets.
11. Tests must be deterministic where possible.
12. Flaky tests must not be accepted as normal.
13. Test environments must reproduce production-critical behavior.
14. A successful unit-test suite alone does not prove system correctness.
15. Every important production bug should result in a regression test.

---

## 3. Testing Scope

Backend QA covers:

* Domain logic;
* Application use cases;
* Repository behavior;
* PostgreSQL persistence;
* Authentication;
* Authorization;
* Business and Branch isolation;
* Subscription entitlement;
* Trusted devices;
* Offline authorization;
* Idempotency;
* Transactions;
* Concurrency;
* Orders;
* Payments;
* Refunds;
* Cash Sessions;
* Shift handover;
* Inventory;
* Recipes;
* Menu and pricing;
* Attendance;
* Payroll;
* Notifications;
* Audit;
* Reports;
* Configuration;
* Synchronization;
* File generation;
* Background jobs;
* Security;
* Database migrations;
* Performance;
* Failure recovery.

---

## 4. Testing Pyramid

The backend follows a layered testing model:

```text
                    End-to-End
                       /\
                      /  \
                Integration
                   /      \
                  /        \
             API / Contract
                /          \
               /            \
             Domain / Unit
```

The majority of tests should be fast unit/domain tests.

Integration tests validate real interactions between:

* Application;
* repositories;
* PostgreSQL;
* transaction boundaries;
* authorization;
* outbox;
* synchronization.

End-to-end tests cover only the most important complete business workflows.

---

## 5. Test Levels

### 5.1. Unit Tests

Unit tests validate isolated behavior without requiring external infrastructure.

Typical targets:

* domain entities;
* value objects;
* validators;
* business rules;
* permission calculations;
* price calculations;
* discount calculations;
* markup calculations;
* payroll calculations;
* status transitions;
* configuration version rules;
* synchronization conflict rules.

Unit tests should be:

* fast;
* deterministic;
* isolated;
* easy to diagnose.

---

## 6. Domain Unit Testing

Domain tests must verify business invariants directly.

Examples:

```text
Product cannot be normally sold without required approved Recipe.

Negative inventory is prohibited.

Markup cannot be below 0%.

Markup cannot exceed 100%.

Closed Cash Session cannot be reopened normally.

Paid Order cannot be modified through ordinary editing.

Historical Order price cannot change.

Branch A configuration cannot affect Branch B.

Inactive employee cannot perform authorized operations.

Expired subscription cannot perform modifying operations.
```

Domain tests should not depend on HTTP or PostgreSQL unless persistence behavior itself is being tested.

---

## 7. Application Use Case Tests

Application tests validate orchestration between domain behavior and infrastructure abstractions.

Examples:

* Create Order;
* Accept Order;
* Pay Order;
* Refund Order;
* Open Cash Session;
* Close Cash Session;
* Handover Cash;
* Approve Recipe;
* Change Product Price;
* Change Branch Price Override;
* Adjust Inventory;
* Create Employee;
* Update Permission;
* Generate Report;
* Synchronize Offline Transaction.

Application tests must verify:

* authorization;
* Business scope;
* Branch scope;
* subscription entitlement;
* transaction boundaries;
* repository interaction;
* idempotency;
* audit creation;
* outbox event creation where required.

---

## 8. Repository Tests

Repository tests validate persistence behavior.

They must verify:

* correct Business filtering;
* correct Branch filtering;
* entity retrieval;
* entity creation;
* update behavior;
* version checks;
* unique constraints;
* foreign-key constraints;
* historical record preservation;
* pagination;
* filtering;
* ordering;
* soft-delete/archive behavior;
* transaction participation.

Repositories must not silently commit transactions.

Tests must detect accidental commits.

---

## 9. PostgreSQL Integration Tests

Important persistence behavior must be tested against real PostgreSQL.

SQLite must not be considered sufficient for PostgreSQL-specific behavior.

PostgreSQL integration tests must cover:

* constraints;
* indexes;
* unique constraints;
* foreign keys;
* transactions;
* row-level locks;
* isolation behavior;
* numeric precision;
* timestamps;
* JSON/JSONB behavior where used;
* optimistic concurrency;
* PostgreSQL-specific queries.

A production-like PostgreSQL version should be used in CI.

---

## 10. API Tests

API tests validate the external backend contract.

They must cover:

* authentication;
* authorization;
* request validation;
* response schemas;
* HTTP status codes;
* pagination;
* filtering;
* error responses;
* idempotency;
* Business/Branch scope;
* rate limiting where applicable.

Expected error classes include:

```text
400 Validation Error
401 Authentication Error
403 Authorization Error
404 Resource Not Found
409 Conflict
422 Business Rule / Semantic Validation
429 Rate Limited
500 Internal Server Error
503 Temporary Infrastructure Failure
```

Exact status mapping must remain consistent across the API.

---

## 11. API Contract Testing

API request and response schemas must be validated automatically.

Contract tests must detect:

* removed fields;
* unexpected type changes;
* required fields becoming optional;
* optional fields becoming required;
* incompatible enum changes;
* incompatible error formats;
* pagination contract changes.

Breaking API changes require explicit versioning or migration strategy.

---

## 12. Authentication Testing

Authentication tests must verify:

* valid login;
* invalid password;
* inactive employee;
* suspended employee;
* revoked session;
* expired session/token;
* logout;
* password change;
* password reset;
* rate limiting;
* session invalidation;
* authentication context creation.

The system must never authenticate an employee from another Business merely because a valid employee UUID is supplied.

---

## 13. Authorization Testing

Authorization tests are mandatory for every protected use case.

Tests must verify:

* role permissions;
* employee overrides;
* Branch scope;
* all-Branch scope;
* Employee status;
* subscription entitlement;
* Super Admin boundary;
* Manager authority boundary;
* unknown permission denial;
* revoked permission;
* permission changes;
* stale authorization cache invalidation.

The following must always be denied:

```text
Business A → Business B resource

Branch A employee → unauthorized Branch B resource

Manager → permission beyond own authority

Inactive employee → modifying operation

Expired/read-only Business → modifying operation
```

---

## 14. Multi-Tenant Isolation Tests

Business isolation is a mandatory security test category.

For every important resource type, tests must attempt:

```text
Business A actor
        ↓
Business B resource
```

Expected result:

```text
Access Denied
```

This applies to:

* Employees;
* Branches;
* Products;
* Recipes;
* Inventory;
* Orders;
* Payments;
* Cash Sessions;
* Reports;
* Notifications;
* Audit records;
* Files;
* Configuration;
* Synchronization records.

Cross-Business access prevention target:

**100% of security tests must pass.**

A single confirmed cross-Business access defect is a release-blocking security issue.

---

## 15. Branch Isolation Tests

Branch-scoped permissions must be tested independently.

Example:

```text
Employee:
Business = B1
Allowed Branches = A

Request:
Branch = B

Expected:
403 / equivalent authorization denial
```

Tests must also verify that:

* Branch A price changes do not modify Branch B;
* Branch A inventory is not visible through Branch B scope;
* Branch A cash sessions are not accessible through Branch B;
* Branch switching recalculates permissions;
* cached Branch data cannot cross boundaries.

---

## 16. Subscription Testing

Subscription state must be part of authorization tests.

Test states include:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

Examples:

```text
ACTIVE → modification allowed

READ_ONLY → modification denied

READ_ONLY → viewing allowed

READ_ONLY → permitted export allowed

DELETING → normal business modification denied

DELETED → business data unavailable
```

Offline synchronization must not bypass subscription restrictions.

---

## 17. Trusted Device Testing

Tests must verify:

* trusted device registration;
* device verification;
* device revocation;
* employee/device association;
* Business/device association;
* offline authorization issuance;
* expired offline authorization;
* invalid signature;
* revoked device;
* unauthorized device;
* device replacement.

A device UUID alone must never be sufficient authentication.

---

## 18. Offline Authorization Tests

Offline authorization must be tested for:

* valid signature;
* invalid signature;
* expired authorization;
* future authorization;
* wrong Business;
* wrong Branch;
* wrong device;
* wrong employee;
* revoked device;
* subscription restriction;
* clock rollback;
* tampered payload.

Expected behavior:

```text
Invalid offline authorization
        ↓
Reject operation
```

The backend must never trust an offline client solely because the request contains a valid-looking UUID.

---

## 19. Idempotency Testing

Every retryable business command must have appropriate idempotency tests.

Example:

```text
Operation UUID = X

Request 1 → success

Request 2 → same Operation UUID

Expected:
No duplicate business effect
```

Tests must verify duplicate protection for:

* Order creation;
* Order acceptance;
* Payment;
* Refund;
* Inventory adjustment;
* Cash operations;
* Configuration changes;
* Synchronization;
* Notifications where applicable;
* Background jobs.

Idempotency records must not be silently deleted while the operation remains relevant.

---

## 20. Transaction Testing

Transaction tests must verify atomicity.

Example:

```text
Order Acceptance

Validate Order
Validate Recipe
Validate Stock
Deduct Inventory
Change Order State
Create Audit
Create Outbox Event
Commit
```

If a required step fails:

```text
No partial core state must remain.
```

Tests must verify rollback for:

* inventory failure;
* authorization failure;
* validation failure;
* database constraint failure;
* concurrency conflict;
* unexpected application failure.

---

## 21. Post-Commit Processing Tests

Secondary operations must not accidentally become part of the core transaction.

Examples:

* printing;
* notifications;
* email;
* report generation;
* file generation;
* cache invalidation;
* asynchronous jobs.

Tests must verify:

```text
Core transaction succeeds
        ↓
Post-commit job may fail
        ↓
Core business state remains committed
```

For example, printer failure must not rollback an accepted Order.

---

## 22. Order Testing

Order tests must cover:

* creation;
* item addition;
* item removal;
* quantity changes;
* order modification;
* acceptance;
* preparation;
* ready;
* completion;
* payment;
* cancellation;
* refund;
* archive;
* status transitions.

Tests must verify invalid transitions are rejected.

Example:

```text
PAID → ordinary modification
```

must be rejected.

---

## 23. Historical Order Integrity

Historical Order tests must verify:

* Product price snapshot;
* discount snapshot;
* markup snapshot;
* Recipe Version;
* Set Version;
* payment information;
* refund information.

Changing current configuration must never change historical transaction data.

Example:

```text
Order Item Price = 30,000

Change Product Price → 35,000

Expected:
Existing Order Item = 30,000
New Order Item = 35,000
```

---

## 24. Payment Testing

Payment tests must verify:

* valid payment;
* payment amount;
* payment method;
* duplicate payment;
* insufficient amount where applicable;
* already paid Order;
* cancelled Order;
* concurrent payment;
* refund relationship;
* historical payment integrity.

Two concurrent payment requests must not both successfully settle the same Order.

---

## 25. Refund Testing

Refund tests must verify:

* authorized employee;
* refund reason;
* required approval;
* refund amount;
* already refunded amount;
* duplicate refund request;
* concurrent refund;
* historical price;
* subscription state;
* audit event.

Refund calculations must use historical transaction values rather than current Product prices.

---

## 26. Cash Session Testing

Cash Session tests must cover:

* open;
* active state;
* close;
* expected cash;
* actual cash;
* discrepancy;
* correction;
* duplicate open;
* duplicate close;
* concurrent open;
* concurrent close;
* closed-session modification.

Important invariant:

```text
A Cash Register must not have two active Cash Sessions
```

unless future multi-register/multi-session rules explicitly permit it.

---

## 27. Cash Concurrency Testing

Concurrency tests must execute simultaneous requests.

Example:

```text
Cashier A → Open Session
Cashier B → Open Session
```

Expected:

```text
Exactly one operation succeeds.
```

The second operation must receive a deterministic conflict.

Similar tests are required for:

* closing;
* cash handover;
* corrections;
* payment;
* refund.

---

## 28. Inventory Testing

Inventory tests must verify:

* purchase;
* stock increase;
* manual exit;
* stock deduction;
* stock adjustment;
* low-stock threshold;
* out-of-stock;
* negative stock prevention;
* FIFO;
* cost calculation;
* warehouse scope;
* Branch scope;
* Recipe deduction;
* Set deduction.

Negative stock must never be created through normal operations.

---

## 29. Inventory Concurrency Testing

Concurrent stock deductions must be tested.

Example:

```text
Available stock = 1

Order A → deduct 1
Order B → deduct 1
```

Expected:

```text
One succeeds
One fails due to insufficient stock
```

The final stock must never become negative.

---

## 30. Recipe Testing

Recipe tests must cover:

* creation;
* editing;
* approval;
* activation;
* archival;
* versioning;
* ingredient quantities;
* semi-finished dependencies;
* finished Product dependencies;
* insufficient stock;
* historical Recipe Version.

Historical inventory deductions must retain the Recipe Version used at the time.

---

## 31. Menu and Pricing Testing

Tests must cover:

* global Product activation;
* Branch availability;
* standard price;
* Branch override;
* effective configuration;
* Cash Session boundary;
* price snapshot;
* configuration version;
* stale update conflict;
* concurrent price changes;
* offline stale configuration.

Example:

```text
Price A → active session

Price B → created

Current session → Price A
Next session → Price B
```

---

## 32. Configuration Concurrency Testing

Configuration uses optimistic concurrency.

Test:

```text
Employee A reads Version 10
Employee B reads Version 10

Employee A → updates → Version 11

Employee B → updates using Version 10
```

Expected:

```text
Employee B → Conflict
```

The stale update must never silently overwrite Version 11.

---

## 33. Attendance Testing

Attendance tests must verify:

* check-in;
* check-out;
* duplicate check-in;
* duplicate check-out;
* employee status;
* Branch scope;
* attendance correction;
* correction permission;
* historical attendance;
* timezone behavior.

Attendance calculations must use Business/Branch timezone rules where applicable.

---

## 34. Payroll Testing

Payroll tests must verify:

* fixed salary;
* percentage salary;
* daily salary;
* shift-based salary;
* hybrid salary;
* bonuses;
* attendance dependency;
* payroll period;
* correction;
* rounding;
* historical payroll records.

Financial calculations must use deterministic decimal arithmetic.

Floating-point arithmetic must not be used for authoritative monetary calculations.

---

## 35. Notification Testing

Notification tests must verify:

* correct recipient;
* Business scope;
* Branch scope;
* severity;
* notification type;
* duplicate prevention;
* read/unread state;
* asynchronous processing;
* retry;
* failure;
* security-sensitive notifications.

Notifications must not grant permissions.

---

## 36. Outbox Testing

Outbox tests must verify:

```text
Core transaction
+
Required Outbox record
```

are committed atomically when required.

Tests must verify:

* event creation;
* event identity;
* retry;
* duplicate processing;
* processing state;
* failure recovery;
* eventual delivery.

A failed external notification must not create duplicate business transactions.

---

## 37. Background Job Testing

Background jobs must be tested for:

* successful execution;
* retry;
* timeout;
* duplicate execution;
* idempotency;
* permanent failure;
* temporary failure;
* dead-letter handling where applicable;
* graceful shutdown;
* recovery after worker restart.

Jobs must not depend on process-local memory for authoritative state.

---

## 38. Synchronization Testing

Offline synchronization requires a dedicated test suite.

Tests must cover:

* single event;
* batch;
* duplicate event;
* out-of-order event;
* stale event;
* invalid event;
* unauthorized device;
* invalid signature;
* Business mismatch;
* Branch mismatch;
* operation UUID collision;
* partial batch success;
* retry;
* conflict;
* server-authoritative state.

---

## 39. Synchronization Ordering

Transaction synchronization must be tested before configuration synchronization when both are pending.

Example:

```text
Offline Order
Price Version A

Server:
Price Version B

Sync:
1. Order transaction
2. Configuration update
```

The Order must retain Price Version A.

---

## 40. Synchronization Conflict Testing

Conflict tests must verify:

* conflicting versions are preserved;
* the conflict is identifiable;
* automatic silent overwrite does not occur;
* authorized resolution is required where necessary;
* resolution is audited;
* final state is deterministic.

Conflict resolution must never destroy historical evidence.

---

## 41. Report Testing

Report tests must verify:

* correct period;
* Business scope;
* Branch scope;
* permissions;
* source data;
* immutable version;
* version creation;
* unchanged version after unrelated data changes;
* new version after relevant corrections;
* empty report behavior;
* export.

Historical reports must not unexpectedly change without a new version.

---

## 42. Excel Export Testing

XLSX export tests must verify:

* correct columns;
* correct data;
* correct period;
* correct Business/Branch scope;
* correct permissions;
* correct historical version;
* file integrity;
* large dataset behavior;
* unauthorized export rejection.

Export generation should normally run asynchronously.

---

## 43. File Security Testing

File tests must verify:

* authorization;
* Business isolation;
* Branch isolation;
* file ownership;
* path traversal protection;
* invalid file type;
* size limits;
* malicious filenames;
* unauthorized download;
* deleted resource references;
* signed/protected download access where used.

The original filename must never be trusted as a storage path.

---

## 44. Audit Testing

Important operations must create audit records.

Tests must verify audit context such as:

* Event UUID;
* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Cash Session UUID where applicable;
* Operation UUID;
* old state;
* new state;
* timestamp;
* source;
* result.

Audit records must be immutable.

---

## 45. Historical Integrity Testing

Regression tests must verify that current changes cannot modify historical:

* Orders;
* Order Items;
* Payments;
* Refunds;
* Cash Sessions;
* Inventory Transactions;
* Recipe Versions;
* Menu configurations;
* Price snapshots;
* Payroll;
* Reports;
* Audit records.

Any unintended historical mutation is a release-blocking defect.

---

## 46. Database Migration Testing

Every migration must be tested for:

* upgrade;
* downgrade where supported;
* schema correctness;
* existing-data compatibility;
* constraints;
* indexes;
* data preservation;
* rollback behavior;
* performance impact.

Production migration strategy follows expand/contract where necessary.

---

## 47. Migration Compatibility

For large or sensitive tables:

```text
Old application
      ↓
Expand schema
      ↓
Deploy compatible application
      ↓
Backfill
      ↓
Validate
      ↓
Contract old structure
```

Tests must ensure that rolling deployment or temporary mixed application versions does not corrupt data.

---

## 48. Security Regression Testing

Security tests must be part of normal CI.

Required categories:

* authentication bypass;
* authorization bypass;
* Business isolation;
* Branch isolation;
* privilege escalation;
* IDOR/BOLA;
* SQL injection;
* path traversal;
* SSRF;
* command injection;
* unsafe deserialization;
* insecure file access;
* rate-limit bypass;
* replay attacks;
* offline authorization tampering.

Security tests must fail closed.

---

## 49. Input Validation Testing

Every external input boundary must be tested for:

* empty input;
* null;
* invalid type;
* excessive length;
* negative values;
* zero;
* maximum values;
* unexpected enum;
* malformed UUID;
* malformed date/time;
* invalid decimal;
* duplicated fields;
* unknown fields where prohibited.

Validation must happen before dangerous processing.

---

## 50. Property-Based Testing

Property-based testing may be used for complex deterministic business rules.

Good candidates:

* price calculations;
* discounts;
* markup;
* payroll;
* pagination;
* inventory quantity calculations;
* FIFO;
* state transitions;
* synchronization ordering;
* idempotency.

Example invariant:

```text
0% <= Markup <= 100%
```

Any generated input outside the allowed range must be rejected.

---

## 51. Invariant Testing

System invariants should have executable tests wherever practical.

Examples:

```text
Stock >= 0

Closed Cash Session cannot become active

Historical Order price remains unchanged

Business A cannot access Business B

Branch A cannot modify Branch B

Duplicate operation cannot create duplicate effect

Deleted Business cannot accept new transaction

Inactive Employee cannot perform new modifying operation
```

Important invariants should be tested both at application level and database level where appropriate.

---

## 52. State Transition Testing

Important domain states must have explicit transition tests.

Example:

```text
Order

DRAFT
  ↓
ACCEPTED
  ↓
PREPARING
  ↓
READY
  ↓
COMPLETED
  ↓
PAID
  ↓
ARCHIVED
```

Invalid transitions must be rejected.

The exact state machine follows the accepted Order Lifecycle specification.

---

## 53. Negative Testing

Testing must deliberately attempt invalid operations.

Examples:

* insufficient stock;
* inactive Product;
* unauthorized discount;
* unauthorized refund;
* closed Cash Session;
* expired subscription;
* inactive employee;
* stale configuration;
* duplicate operation;
* invalid offline authorization;
* wrong Business;
* wrong Branch;
* invalid Recipe;
* invalid Set;
* malformed request.

A feature is not considered adequately tested merely because its successful path works.

---

## 54. Concurrency Test Strategy

Critical concurrent operations must have dedicated tests.

Required targets:

* Cash Session;
* Payment;
* Refund;
* Inventory deduction;
* Inventory adjustment;
* Configuration updates;
* Recipe approval;
* Synchronization;
* Idempotency;
* Shift handover.

Concurrency tests should run requests in parallel against the same PostgreSQL database.

Expected outcomes must be deterministic.

---

## 55. Race Condition Testing

Tests should deliberately create timing races.

Example:

```text
Read Version
       ↓
Delay
       ↓
Another request updates
       ↓
Original request continues
```

The system must detect stale state where optimistic concurrency is required.

For database-locked resources, tests must verify correct lock behavior instead of relying on timing assumptions.

---

## 56. Performance Testing

Performance testing is a separate QA category.

It includes:

* load testing;
* stress testing;
* concurrency testing;
* endurance testing;
* database query testing;
* synchronization testing;
* report testing;
* API latency testing.

Performance tests must use production-like data volumes where practical.

---

## 57. Performance Targets

Initial backend targets:

### API

* Ordinary authenticated API p95 ≤ **300 ms** under normal load.
* Ordinary authenticated API p99 ≤ **800 ms** under normal load.
* Validation and authorization overhead should normally remain below **100 ms p95**.
* Core POS command p95 ≤ **500 ms**, excluding external printer/network operations.

### Database

* Normal indexed business query p95 ≤ **100 ms**.
* Critical POS query p95 ≤ **150 ms**.
* Database transaction duration for ordinary core operations should normally remain below **300 ms p95**.
* Long-running transactions must be explicitly justified.

### Synchronization

* Normal synchronization request p95 ≤ **1 second** for a bounded batch.
* Sync processing must not block ordinary online POS operations.
* Retry processing must be bounded and observable.

### Background Jobs

* Job pickup delay p95 ≤ **30 seconds** for normal-priority jobs.
* Critical security/background events should become visible within **60 seconds**.

These are initial engineering targets and must be validated through load testing and adjusted using measured production data.

---

## 58. Availability SLOs

Initial backend SLO targets:

| Area                                    |          Target |
| --------------------------------------- | --------------: |
| Core API availability                   | ≥ 99.9% monthly |
| Authentication subsystem                | ≥ 99.9% monthly |
| Authorization subsystem                 | ≥ 99.9% monthly |
| Database availability                   | ≥ 99.9% monthly |
| Synchronization endpoint                | ≥ 99.9% monthly |
| Required audit event creation           |        ≥ 99.99% |
| Duplicate operation prevention          |        ≥ 99.99% |
| Cross-Business isolation                |            100% |
| Unauthorized Branch access prevention   |            100% |
| Invalid offline authorization rejection |            100% |
| Expired offline authorization rejection |            100% |

Security correctness targets are treated differently from ordinary availability targets: a security boundary must not be allowed to fail open for availability reasons.

---

## 59. Error Budget

For a 99.9% monthly availability SLO, the approximate monthly error budget is:

**43 minutes 12 seconds**

The error budget may be consumed by:

* infrastructure failure;
* deployment failure;
* dependency failure;
* unexpected application errors.

Security violations, data corruption and cross-tenant isolation failures are not considered acceptable error-budget consumption.

They require incident handling regardless of availability SLO status.

---

## 60. Test Coverage Targets

Coverage is a quality signal, not the only quality metric.

Initial targets:

* Domain/business logic: **≥ 90%**
* Application/use cases: **≥ 85%**
* Security-critical code: **≥ 90%**
* Repository/data access: **≥ 80%**
* API endpoints: **≥ 80%**
* Overall backend: **≥ 80%**

Critical business paths may require higher effective coverage through integration and end-to-end tests even when line coverage is already high.

Coverage must not be increased artificially with meaningless tests.

---

## 61. Critical Path Coverage

The following workflows require unit + integration + API coverage and, where practical, end-to-end coverage:

1. Login;
2. Branch context selection;
3. Open Cash Session;
4. Create Order;
5. Accept Order;
6. Inventory deduction;
7. Payment;
8. Refund;
9. Close Cash Session;
10. Cash handover;
11. Price configuration;
12. Recipe approval;
13. Inventory adjustment;
14. Offline synchronization;
15. Report generation;
16. Subscription state transition;
17. Business deletion lifecycle.

---

## 62. End-to-End Testing

End-to-end tests should cover complete high-value workflows rather than every API endpoint.

Example:

```text
Login
 ↓
Select Branch
 ↓
Open Cash Session
 ↓
Create Order
 ↓
Accept Order
 ↓
Inventory Deduction
 ↓
Payment
 ↓
Close Cash Session
 ↓
Report
```

Another important flow:

```text
Online Device
 ↓
Trusted Device
 ↓
Offline Authorization
 ↓
Offline Order
 ↓
Synchronization
 ↓
Server Validation
 ↓
Historical Transaction
```

---

## 63. Test Database Isolation

Tests must not share mutable state unexpectedly.

Each test environment should use one of:

* transaction rollback;
* isolated database/schema;
* isolated test container;
* deterministic fixture reset.

Parallel tests must not corrupt each other's data.

Business and Branch UUIDs must be generated independently for test isolation.

---

## 64. Test Data Strategy

Test data should include:

* multiple Businesses;
* multiple Branches;
* multiple employees;
* multiple roles;
* multiple permission combinations;
* active/inactive employees;
* active/read-only subscriptions;
* trusted/untrusted devices;
* products;
* recipes;
* sets;
* inventory;
* orders;
* payments;
* refunds;
* cash sessions;
* historical versions.

Test data should include both normal and boundary cases.

---

## 65. Test Data Safety

Production data must not be copied into ordinary development/test environments unless it has been properly anonymized and approved.

Tests must not contain:

* production passwords;
* production tokens;
* private keys;
* real customer personal data;
* production API credentials.

Test secrets must be separate from production secrets.

---

## 66. Fixtures

Fixtures should provide reusable setup for:

* Business;
* Branch;
* Employee;
* Role;
* Permission;
* Device;
* Subscription;
* Product;
* Recipe;
* Inventory;
* Order;
* Payment;
* Cash Session.

Fixtures should remain small and composable.

Large universal fixtures must be avoided because they make tests slow and difficult to understand.

---

## 67. Test Naming

Test names must describe business behavior.

Preferred:

```text
test_manager_cannot_grant_permission_beyond_own_authority
test_payment_cannot_settle_same_order_twice
test_branch_price_override_does_not_affect_other_branch
test_offline_order_preserves_original_price_snapshot
```

Avoid:

```text
test_function_1
test_update
test_api
```

Tests should communicate the invariant being protected.

---

## 68. Test Organization

Recommended structure:

```text
tests/
├── unit/
│   ├── domain/
│   ├── application/
│   ├── security/
│   └── shared/
│
├── integration/
│   ├── repositories/
│   ├── transactions/
│   ├── synchronization/
│   ├── background/
│   └── database/
│
├── api/
│   ├── authentication/
│   ├── authorization/
│   ├── orders/
│   ├── inventory/
│   ├── cash/
│   └── configuration/
│
├── e2e/
│   ├── pos/
│   ├── cash/
│   ├── offline/
│   └── lifecycle/
│
├── performance/
├── security/
├── migrations/
└── fixtures/
```

---

## 69. CI Test Pipeline

The CI pipeline should execute tests in stages.

### Stage 1 — Fast Checks

* formatting;
* linting;
* static analysis;
* type checking;
* import validation.

### Stage 2 — Unit Tests

* domain;
* application;
* security;
* shared logic.

### Stage 3 — Integration Tests

* PostgreSQL;
* repositories;
* transactions;
* concurrency;
* synchronization.

### Stage 4 — API Tests

* authentication;
* authorization;
* endpoints;
* contracts.

### Stage 5 — Security Tests

* isolation;
* authorization;
* injection;
* replay;
* rate limiting.

### Stage 6 — End-to-End Tests

Critical workflows.

### Stage 7 — Build and Migration Validation

* application build;
* migration upgrade;
* schema validation.

Performance/load tests may run in a separate pipeline depending on execution cost.

---

## 70. Pull Request Quality Gates

A change should not be merged when:

* required tests fail;
* security tests fail;
* migration validation fails;
* type checking fails where enforced;
* critical coverage decreases without justification;
* Business/Branch isolation tests fail;
* critical invariant tests fail;
* new flaky tests are introduced without resolution.

---

## 71. Release Quality Gates

A production release requires:

1. CI success;
2. migration validation;
3. critical integration tests;
4. critical security tests;
5. critical E2E tests;
6. no known release-blocking defects;
7. acceptable performance results;
8. rollback strategy;
9. observability readiness.

---

## 72. Flaky Test Policy

Flaky tests must not be ignored.

A test is considered flaky when it produces different results without a relevant code/data/environment change.

When detected:

1. identify the cause;
2. quarantine only when necessary;
3. create an issue;
4. assign ownership;
5. fix or remove the underlying nondeterminism.

Retries must not be used to hide real failures.

---

## 73. Time and Clock Testing

The backend must use an injectable clock abstraction.

Tests must simulate:

* current time;
* future time;
* expired subscription;
* offline authorization expiry;
* Cash Session boundaries;
* payroll period;
* report period;
* deletion eligibility;
* clock rollback.

Tests must not depend on the real system clock unnecessarily.

---

## 74. Timezone Testing

Tests must cover:

* UTC storage;
* Business timezone;
* Branch timezone where applicable;
* day boundaries;
* month boundaries;
* report periods;
* payroll periods;
* Cash Session dates.

Date-only business concepts must not shift unexpectedly because of timezone conversion.

---

## 75. Money Testing

Authoritative financial calculations must use decimal/numeric arithmetic.

Tests must verify:

* rounding;
* precision;
* discount;
* markup;
* payment;
* refund;
* payroll;
* inventory cost;
* report totals.

Example:

```text
30,000 × 10% = 3,000

30,000 - 5,000 = 25,000
```

Floating-point rounding must not change authoritative financial results.

---

## 76. Failure Injection Testing

Important infrastructure failures should be simulated.

Examples:

* PostgreSQL connection failure;
* Redis unavailable;
* notification provider failure;
* email failure;
* printer failure;
* storage failure;
* worker restart;
* network timeout;
* synchronization interruption.

Expected system behavior must be deterministic and documented.

---

## 77. Graceful Degradation Testing

When a non-authoritative dependency fails:

```text
Redis unavailable
→ PostgreSQL remains authoritative

Printer unavailable
→ Order remains committed

Email unavailable
→ In-app notification remains available

Report worker unavailable
→ Core POS remains operational
```

Failure of secondary services must not unnecessarily stop core POS operations.

---

## 78. Recovery Testing

Recovery tests must verify:

* worker restart;
* queue retry;
* outbox retry;
* synchronization retry;
* Redis restart;
* temporary database connectivity loss;
* incomplete background job;
* partial synchronization batch.

Recovery must not create duplicate business effects.

---

## 79. Disaster Recovery Testing

At appropriate intervals, test:

* database backup restoration;
* application recovery;
* migration compatibility;
* data integrity;
* audit/history preservation;
* Business lifecycle state;
* synchronization state.

A backup is not considered valid merely because it was successfully created. Restoration must be tested.

---

## 80. Performance Regression Testing

Performance regression tests should compare important operations against a baseline.

Track at least:

* p50 latency;
* p95 latency;
* p99 latency;
* throughput;
* database query latency;
* transaction duration;
* CPU;
* memory;
* connection pool utilization;
* queue delay.

A significant regression requires investigation even when functional tests pass.

---

## 81. Load Test Scenarios

Representative load scenarios should include:

### Scenario A — POS

Multiple Branches simultaneously:

```text
Create Order
Add Items
Accept Order
Payment
```

### Scenario B — Mixed Operations

```text
POS
+
Inventory
+
Cash
+
Notifications
+
Background Jobs
```

### Scenario C — Synchronization

Many trusted devices synchronizing bounded batches simultaneously.

### Scenario D — Reporting

Large report generation while normal POS traffic continues.

The objective is to verify that heavy reporting does not degrade critical POS operations beyond agreed SLOs.

---

## 82. Security Performance Testing

Security controls must be measured for performance impact.

Targets:

* cached authorization lookup p95 ≤ **20 ms**;
* Business/Branch scope validation p95 ≤ **50 ms**;
* idempotency lookup p95 ≤ **50 ms**;
* ordinary security processing overhead p95 ≤ **100 ms**.

Security controls must not be removed merely to improve performance.

Instead, optimize:

* indexes;
* caching;
* query shape;
* authorization context;
* batching;
* connection management.

---

## 83. Test Observability

Test runs should produce:

* test result;
* duration;
* failure reason;
* environment;
* database version;
* application version;
* migration version.

CI should preserve logs for failed integration/security tests.

Performance tests should preserve metrics sufficient for comparison with previous runs.

---

## 84. Defect Classification

Defects should be classified as:

### Critical

Examples:

* cross-Business access;
* financial corruption;
* duplicate payment;
* negative stock;
* historical data corruption;
* authentication bypass;
* privilege escalation.

### High

Examples:

* important workflow unavailable;
* synchronization corruption;
* incorrect cash state;
* major report inconsistency.

### Medium

Examples:

* limited administrative workflow failure;
* non-critical report discrepancy;
* recoverable background job issue.

### Low

Examples:

* cosmetic API/documentation issue;
* minor non-critical validation message.

Critical and High defects require explicit resolution before production release unless formally accepted by authorized stakeholders.

---

## 85. Regression Test Policy

Every production defect with meaningful business impact should produce a regression test.

Example:

```text
Production bug:
Branch B received Branch A price

Required:
1. Fix isolation logic
2. Add regression test
3. Add cross-Branch test
4. Add cache isolation test if cache involved
```

The goal is to prevent recurrence, not merely repair the current instance.

---

## 86. Testing Cache Behavior

Cache tests must verify:

* correct cache key;
* Business isolation;
* Branch isolation;
* permission isolation;
* configuration version;
* invalidation;
* TTL;
* stale data handling;
* Redis failure fallback.

Example:

```text
Business A / Branch A / Product X
        ↓
Cache

Business B / Branch A / Product X
        ↓
Must never receive A's cached data
```

---

## 87. Testing Authorization Cache Invalidation

When a permission changes:

```text
Permission Version A
        ↓
Employee permission updated
        ↓
Permission Version B
```

Tests must verify that the employee cannot continue using stale authorization beyond the defined propagation target.

Initial target:

**Online authorization cache invalidation ≤ 30 seconds.**

Sensitive operations may require immediate authoritative validation.

---

## 88. Testing Historical Configuration

Configuration tests must verify that:

* previous versions remain readable;
* previous versions remain immutable;
* new version references previous version;
* effective version is deterministic;
* historical Order does not use current configuration;
* rollback creates a new version rather than deleting history.

---

## 89. Testing Subscription Deletion Lifecycle

Lifecycle tests must cover:

```text
ACTIVE
 ↓
EXPIRED / READ_ONLY
 ↓
60-day eligibility
 ↓
DELETION_ELIGIBLE
 ↓
DELETING
 ↓
DELETED
```

Tests must verify:

* modification blocked after expiry;
* permitted viewing remains available;
* permitted export remains available;
* deletion notification;
* deletion job;
* retry;
* partial deletion recovery;
* backup behavior;
* deleted Business cannot accept new operations.

---

## 90. Testing Background Deletion

Deletion must be tested in bounded batches.

Example:

```text
Business
 ↓
Employees batch
 ↓
Orders batch
 ↓
Inventory batch
 ↓
Audit/history according to retention policy
 ↓
Files
 ↓
Final Business state
```

A worker failure must allow safe continuation without duplicating or corrupting deletion.

---

## 91. Test Environment Levels

Recommended environments:

```text
Development
Testing / CI
Staging
Production
```

### Development

Fast local feedback.

### Testing / CI

Deterministic automated tests.

### Staging

Production-like configuration and infrastructure.

### Production

Real workloads and real operational data.

Production tests must be carefully controlled and must not intentionally corrupt business data.

---

## 92. Test Configuration

Test environments must explicitly define:

* APP_ENV;
* database URL;
* Redis configuration;
* storage configuration;
* worker configuration;
* test secrets;
* external integration mocks/sandboxes;
* timezone;
* feature flags.

Production secrets must never be reused in tests.

---

## 93. Mocking Policy

Mocks should be used for:

* external providers;
* email;
* printer adapters;
* cloud storage adapters;
* third-party APIs;
* time where controlled behavior is required.

Mocks should not replace PostgreSQL for tests that depend on:

* constraints;
* transactions;
* locks;
* isolation;
* database queries.

Important database behavior requires real integration tests.

---

## 94. Contract Tests for External Providers

External adapters should have contract tests.

Examples:

* email provider;
* storage provider;
* printer agent;
* payment provider if introduced;
* identity provider if introduced.

Provider replacement must not require changing core domain behavior.

---

## 95. Testing Architecture Boundaries

Automated checks should detect prohibited dependencies.

Examples:

```text
Domain → HTTP dependency
Domain → SQLAlchemy dependency
Domain → Redis dependency
API → direct DB mutation
Repository → unexpected commit
```

Architecture tests or static analysis should prevent these dependencies.

---

## 96. Dependency Security Testing

CI should regularly inspect dependencies for:

* known vulnerabilities;
* outdated critical packages;
* malicious package changes;
* license concerns where applicable.

Security updates must be evaluated for compatibility before deployment.

---

## 97. Static Analysis

The backend should use appropriate static checks for:

* type correctness;
* unreachable code;
* unsafe patterns;
* import boundaries;
* unused code;
* formatting;
* linting;
* security-sensitive patterns.

Static analysis is complementary to runtime tests.

---

## 98. Test Review Requirements

New tests should be reviewed for:

* correct behavior;
* meaningful assertions;
* deterministic execution;
* correct fixture scope;
* security implications;
* Business/Branch isolation;
* maintainability.

A test that merely executes code without meaningful assertions does not provide sufficient quality protection.

---

## 99. Test Maintenance

Tests must evolve with the system.

When business rules change:

1. update domain tests;
2. update application tests;
3. update integration tests;
4. update API contracts;
5. update E2E scenarios where required;
6. update documentation and invariants.

Obsolete tests must be removed rather than kept only to preserve coverage numbers.

---

## 100. Quality Metrics

Engineering quality should be monitored using:

* test pass rate;
* test duration;
* flaky test rate;
* coverage;
* defect escape rate;
* regression defect rate;
* API p95/p99;
* database latency;
* transaction duration;
* synchronization latency;
* background job delay;
* security test pass rate;
* migration success rate.

Coverage alone must not be treated as the primary quality metric.

---

## 101. Quality SLOs

Initial quality targets:

| Metric                                                |     Target |
| ----------------------------------------------------- | ---------: |
| CI critical test pass rate                            |       100% |
| Critical security test pass rate                      |       100% |
| Cross-Business isolation tests                        |       100% |
| Unauthorized Branch access tests                      |       100% |
| Critical invariant tests                              |       100% |
| Critical workflow regression tests                    |       100% |
| Required migration tests                              |       100% |
| Overall backend line coverage                         |      ≥ 80% |
| Domain/business logic coverage                        |      ≥ 90% |
| Security-critical code coverage                       |      ≥ 90% |
| Flaky test rate                                       |       < 1% |
| Critical defect escape                                | 0 accepted |
| Critical historical-data corruption                   | 0 accepted |
| Duplicate financial transaction due to backend defect | 0 accepted |

---

## 102. Release Blocking Conditions

A release must be blocked when:

* Business isolation is compromised;
* Branch isolation is compromised;
* authentication bypass exists;
* privilege escalation exists;
* financial duplication is possible;
* historical financial data can be modified incorrectly;
* inventory can become negative through a valid business path;
* critical synchronization corruption exists;
* required migrations fail;
* critical tests fail;
* critical SLO regression has no accepted explanation.

---

## 103. Definition of Done

A backend feature is considered complete only when:

* domain behavior is implemented;
* application use case is tested;
* persistence behavior is tested where applicable;
* authorization is tested;
* Business/Branch isolation is tested;
* error behavior is tested;
* idempotency is tested where applicable;
* concurrency is tested where applicable;
* audit behavior is tested where required;
* historical integrity is tested where applicable;
* API contract is tested;
* documentation is updated;
* performance impact is evaluated;
* security impact is evaluated.

---

## 104. Testing Invariants

The following invariants apply to backend QA:

1. Tests must not depend on production secrets.
2. Production data must not be used directly in ordinary tests.
3. Domain business rules must be independently testable.
4. Critical business operations require integration coverage.
5. PostgreSQL-specific behavior must be tested against PostgreSQL.
6. API contracts must be tested.
7. Business isolation must be explicitly tested.
8. Branch isolation must be explicitly tested.
9. Authorization must be tested for both allow and deny paths.
10. Unknown permissions must fail closed.
11. Inactive employees cannot perform new modifying operations.
12. Read-only subscription state blocks modifying operations.
13. Offline authorization must be cryptographically validated.
14. Expired offline authorization must be rejected.
15. Invalid offline authorization must be rejected.
16. Device UUID alone is not authentication.
17. Duplicate operation UUID must not create duplicate business effects.
18. Core transaction failure must not leave partial authoritative state.
19. Required outbox creation must remain atomic with the relevant transaction.
20. Printer failure must not rollback a committed Order.
21. Notification failure must not rollback a committed core transaction.
22. Historical Order prices must remain immutable.
23. Historical payment data must remain immutable.
24. Historical refund data must remain immutable.
25. Historical inventory deductions must remain attributable to their Recipe Version.
26. Historical configuration versions must remain immutable.
27. Current configuration must not reinterpret historical transactions.
28. Negative inventory must not be created through valid business operations.
29. Concurrent inventory deduction must not create negative stock.
30. Concurrent payment must not settle the same Order twice.
31. Concurrent Cash Session opening must not create unauthorized duplicate active sessions.
32. Stale configuration updates must be rejected.
33. Important configuration conflicts must not use silent last-write-wins.
34. Branch-specific configuration must not leak across Branches.
35. Business-specific cache entries must not leak across Businesses.
36. Authorization cache invalidation must meet its defined propagation target.
37. Reports must respect Business and Branch scope.
38. XLSX exports must respect authorization.
39. File downloads must respect Business and Branch scope.
40. Audit records must remain immutable.
41. Security events must remain observable.
42. Background job retries must be idempotent where required.
43. Synchronization retries must not duplicate business effects.
44. Synchronization must not bypass authorization.
45. Synchronization must not bypass subscription restrictions.
46. Server state remains authoritative after synchronization.
47. Partial synchronization batches must report per-operation results where required.
48. Database migrations must preserve existing valid data.
49. Migration changes must be tested before production deployment.
50. Performance regressions must be measurable.
51. Security controls must not be removed solely for performance.
52. Core POS operations have priority over heavy reporting.
53. Heavy report generation must not unnecessarily block POS.
54. Redis failure must not compromise data correctness.
55. Cache failure must degrade performance rather than correctness.
56. Tests must be deterministic where practical.
57. Flaky tests must be investigated.
58. Retries must not hide real test failures.
59. Critical security tests must pass before release.
60. Critical historical-integrity tests must pass before release.
61. Critical business invariant tests must pass before release.
62. Every meaningful production defect should result in a regression test.
63. Test coverage must represent meaningful behavior rather than artificial execution.
64. Static analysis must be part of the quality pipeline.
65. Dependency security checks must be part of the quality pipeline.
66. Test environments must use separate secrets.
67. Time-dependent behavior must use controllable clocks.
68. Money calculations must use deterministic decimal arithmetic.
69. Timezone-dependent behavior must be explicitly tested.
70. Critical failure recovery paths must be tested.
71. Backup restoration must be tested periodically.
72. Release quality gates must be reproducible.
73. A successful unit test suite alone is not sufficient evidence of production readiness.
74. A feature is incomplete when its security and failure behavior are untested.
75. Quality must protect correctness, security, performance and historical integrity simultaneously.

---

## 105. Recommended Backend Test Structure

```text
backend/
├── app/
│   ├── api/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── security/
│   ├── background/
│   ├── synchronization/
│   ├── reporting/
│   └── shared/
│
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── security/
│   │   └── shared/
│   │
│   ├── integration/
│   │   ├── repositories/
│   │   ├── transactions/
│   │   ├── synchronization/
│   │   ├── background/
│   │   └── database/
│   │
│   ├── api/
│   │   ├── authentication/
│   │   ├── authorization/
│   │   ├── orders/
│   │   ├── inventory/
│   │   ├── cash/
│   │   └── configuration/
│   │
│   ├── security/
│   ├── e2e/
│   ├── performance/
│   ├── migrations/
│   └── fixtures/
│
└── pyproject.toml
```

---

## 106. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/20_Business_Rules.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/16_Reports_and_Dashboards.md`
* `docs/02_System_Analysis/18_Audit_and_Change_History.md`
* `docs/02_System_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/20_Business_Rules.md`

### Database

* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/27_Database_Migrations_and_Change_Management.md`
* `docs/05_Database/28_Database_Backup_and_Recovery.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend

* `docs/04_Architecture/01_Backend_Architecture.md`
* `docs/04_Architecture/02_Backend_Project_Structure.md`
* `docs/04_Architecture/03_Application_and_Use_Case_Layer.md`
* `docs/04_Architecture/04_Domain_Service_and_Business_Logic.md`
* `docs/04_Architecture/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/07_Transaction_Management.md`
* `docs/04_Architecture/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/11_Configuration_and_Environment_Management.md`
* `docs/04_Architecture/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/16_Backend_Security_Hardening_and_Application_Security.md`

---

## 107. Status

**Backend Architecture Document:** Completed.

**Document Status:** Proposed.

**Current Document:** `17_Backend_Testing_and_Quality_Assurance_Architecture.md`

**Next Document:** `18_Backend_API_Design_and_Contract_Architecture.md`

