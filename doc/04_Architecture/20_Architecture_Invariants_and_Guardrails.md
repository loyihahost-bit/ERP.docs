# Architecture Invariants and Guardrails

**Document ID:** ARCH-20
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This document defines the architectural invariants and guardrails that must remain valid throughout implementation, testing, deployment, maintenance, and future evolution of FastFood ERP.

An invariant is a rule that must remain true regardless of:

* implementation language details;
* framework changes;
* database changes;
* UI changes;
* deployment topology;
* scaling strategy;
* offline/online state;
* background processing;
* future technology replacement.

A guardrail defines a boundary that prevents implementation decisions from violating the architecture.

This document is intended to be used by:

* developers;
* reviewers;
* architects;
* QA engineers;
* DevOps engineers;
* AI coding agents.

---

# 2. Core Architectural Principle

The system must preserve the following priority:

```text
Business Correctness
        ↓
Security
        ↓
Historical Integrity
        ↓
Operational Reliability
        ↓
Performance
        ↓
Implementation Convenience
```

Implementation convenience must never override business correctness, security, or historical integrity.

---

# 3. Architecture Boundaries

The system consists conceptually of:

```text
Client / POS
     ↓
API / Transport
     ↓
Application Layer
     ↓
Domain Modules
     ↓
Persistence / Infrastructure
     ↓
PostgreSQL
```

Secondary processing:

```text
Core Transaction
     ↓
Outbox / Durable State
     ↓
Queue
     ↓
Worker
     ↓
Secondary Operation
```

Offline processing:

```text
Trusted Device
     ↓
Local Storage
     ↓
Durable Local Queue
     ↓
Synchronization
     ↓
Server Validation
     ↓
PostgreSQL
```

These boundaries must remain explicit.

---

# 4. Authoritative State

## 4.1. Server Authority

PostgreSQL is authoritative for server-side business state.

## 4.2. Non-Authoritative Components

The following must not become permanent sources of business truth:

* frontend state;
* browser cache;
* Redis;
* queue messages;
* temporary files;
* report files;
* notification state in the client;
* printer state;
* worker memory.

## 4.3. Guardrail

If a component fails, authoritative business state must remain recoverable.

---

# 5. Tenant Isolation Invariant

Every Business-owned entity must be associated with the correct Business context.

A request must never be able to access another Business's data by manipulating:

* UUID;
* URL;
* query parameter;
* request body;
* synchronization payload;
* report filter;
* export identifier;
* device identifier.

Tenant isolation must be enforced server-side.

---

# 6. Branch Isolation Invariant

Branch-scoped data must respect Branch scope.

A user authorized for Branch A must not automatically access Branch B.

Branch access must be determined from:

```text
Employee
+
Role
+
Override
+
Branch Scope
+
Subscription Entitlement
```

Frontend filtering is not sufficient.

---

# 7. Authentication Invariant

Authentication answers:

> Who is the user?

Authentication must not automatically determine:

> What may the user do?

Authentication and authorization remain separate concerns.

---

# 8. Authorization Invariant

Every protected operation must be authorized server-side.

Effective authorization is based on:

```text
Role Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
+
Relevant Device Trust
```

The exact applicable checks depend on the operation.

---

# 9. Device Trust Invariant

Trusted device status must never be interpreted as unrestricted authorization.

A trusted device:

* identifies an approved device;
* permits eligible offline operation;
* participates in security checks.

It does not:

* create employee permissions;
* bypass branch scope;
* bypass subscription restrictions;
* bypass business isolation.

---

# 10. Subscription Invariant

Subscription entitlement is an independent authorization boundary.

A user may have a role permission but still be unable to perform an operation because the Business subscription does not include the feature.

Subscription restrictions must be enforced server-side.

---

# 11. Offline Authorization Invariant

Offline operation is allowed only when:

* the device is trusted;
* the employee is authorized;
* the Business is valid;
* the Branch is valid;
* the operation is permitted;
* offline authorization is valid;
* subscription conditions permit the operation;
* the authorization has not expired.

Offline operation must not become a permanent security bypass.

---

# 12. First-Time Device Invariant

A new device must not become an offline operational device without prior online registration and trust establishment.

First-time offline authentication is not supported.

---

# 13. Offline Grace Invariant

The default offline authorization grace period is:

```text
3 days
```

unless an explicitly approved configuration changes this policy.

Offline authorization must be time-bounded.

---

# 14. UUID Identity Invariant

Important distributed entities use stable UUID identity.

Examples:

* Business;
* Branch;
* Employee;
* Device;
* Order;
* Payment;
* Cash Session;
* Transaction;
* Event;
* Audit Event;
* Conflict;
* Report Version.

An entity's UUID must not silently change during synchronization.

---

# 15. Transaction UUID Invariant

Every distributed business transaction that requires idempotency must have a stable Transaction UUID.

Retries must reuse the same Transaction UUID.

A retry must not generate a new identity for the same logical transaction.

---

# 16. No Client Transaction ID Invariant

The architecture does not require a separate Client Transaction ID.

Transaction UUID is the stable distributed transaction identity.

---

# 17. Idempotency Invariant

Operations that may be retried must be idempotent where business semantics allow it.

Examples:

* payment submission;
* order synchronization;
* inventory transaction synchronization;
* cash session synchronization;
* report generation request;
* notification processing;
* background jobs.

A repeated request must not create duplicate business effects.

---

# 18. Atomicity Invariant

Critical business operations must either complete fully or leave no partial core state.

For example:

```text
Order Acceptance
+
Inventory Deduction
```

must be one atomic core transaction.

The system must not intentionally leave:

```text
Order Accepted
Inventory Not Deducted
```

as a normal outcome.

---

# 19. Transaction Boundary Invariant

Core database transactions must be:

* explicit;
* short where practical;
* deterministic;
* isolated from external network calls;
* protected against unintended partial commits.

External calls should normally occur outside the critical database transaction.

---

# 20. Inventory Invariants

The system must guarantee:

1. Inventory cannot become negative through a valid operation.
2. Concurrent sales cannot consume the same stock unit twice.
3. Inventory deductions are tied to accepted operational transactions.
4. Inventory returns are explicit.
5. Inventory adjustments require permission.
6. Inventory corrections retain history.
7. Recipe changes do not silently rewrite historical transactions.
8. Offline inventory operations are revalidated during synchronization.

---

# 21. Order Invariants

An Order must:

* belong to one Business;
* belong to one Branch;
* have stable identity;
* retain relevant historical snapshots;
* follow its defined lifecycle;
* respect authorization;
* respect inventory requirements;
* respect applicable configuration;
* preserve payment relationships.

A Draft must not create operational inventory or table occupancy.

---

# 22. Order Lifecycle Invariant

The operational order lifecycle is:

```text
Draft
  ↓
Accepted
  ↓
Preparing
  ↓
Ready
  ↓
Served
```

Payment state is separate from operational order state.

The system must not silently introduce a second competing lifecycle without an architecture decision.

---

# 23. Draft Invariants

Draft orders:

* may be edited;
* do not deduct inventory;
* do not reserve inventory;
* do not notify the kitchen;
* do not create table occupancy.

Draft persistence must not be treated as guaranteed recovery after device restart unless explicitly supported by the implementation.

---

# 24. Accepted Order Invariant

Order acceptance must validate required business conditions before committing.

At minimum:

* authorization;
* Business;
* Branch;
* current configuration;
* inventory availability;
* relevant table/order context.

If required inventory deduction fails, the order must not become Accepted.

---

# 25. Order Modification Invariant

An Accepted unpaid order may be modified only through defined modification rules.

For quantity reduction or product removal:

* the system determines the removed amount;
* the user chooses whether inventory is returned where applicable;
* the decision is recorded;
* inventory return and order modification remain consistent.

If an increase cannot obtain sufficient stock, the entire modification must be rejected.

---

# 26. New Product After Acceptance

Adding a new product after an order has been Accepted creates a separate operational order/ticket linked to the main order/table context.

It must not silently mutate the original accepted transaction into an unrelated state.

---

# 27. Payment Invariants

Payment must:

* have stable identity;
* belong to a valid Order;
* respect Business and Branch;
* respect employee authorization;
* respect paymentable state;
* respect remaining amount rules;
* preserve historical information;
* support idempotent retries.

Duplicate payment creation must be prevented.

---

# 28. Payment Correction Invariant

Completed payments must not be silently overwritten.

A correction or revision must preserve:

* original value;
* new value;
* actor;
* timestamp;
* reason;
* relevant transaction context.

---

# 29. Refund Invariants

Refunds:

* are separate financial operations;
* require authorization;
* require a reason;
* may be full or partial;
* may be item/quantity based where supported;
* must not automatically return inventory;
* must preserve the original payment;
* must be auditable.

---

# 30. Cancellation Invariant

Cancellation is not equivalent to refund.

Cancellation affects operational order state.

Refund affects financial state.

The system must preserve the distinction.

---

# 31. Overpayment Invariant

An amount above the remaining order balance must not silently disappear.

If overpayment is accepted:

* excess must be represented explicitly;
* it must be attributable to the relevant transaction;
* reporting must identify it;
* the original order amount must remain unchanged.

---

# 32. Cash Session Invariants

A Cash Session:

* belongs to one Branch;
* belongs to one physical Cash Register;
* has stable UUID identity;
* has an opening state;
* has a closing state;
* cannot be reopened as an active session after closure.

Corrections create separate correction records.

---

# 33. Single Active Cash Session Invariant

For the current one-register-per-branch model:

> A Branch cannot have two active Cash Sessions for the same physical register.

Concurrent opening attempts must be resolved transactionally.

---

# 34. Cash Handover Invariant

Cash handover must:

```text
Close Previous Session
        ↓
Authenticate New Cashier
        ↓
Count / Accept Cash
        ↓
Open New Session
```

The previous session remains historical.

The physical register remains the same.

The new Cash Session receives a new UUID.

---

# 35. Cash Correction Invariant

Corrections must:

* preserve the original result;
* record the new result;
* record reason;
* record actor;
* record timestamp;
* obey correction limits;
* require additional authorization when the limit is exceeded.

A correction does not reopen the historical session itself.

---

# 36. Inventory Correction Invariant

Manual inventory correction must require the appropriate permission and reason.

The original inventory movement must remain reconstructable.

---

# 37. Recipe Invariants

Recipes must:

* preserve version history;
* not be destructively deleted when referenced;
* require approval according to configuration;
* preserve historical versions;
* respect permissions;
* maintain raw → semi-finished → finished relationships.

---

# 38. Configuration Invariants

Configuration must:

* have explicit ownership;
* have explicit scope;
* be versioned where historical behavior matters;
* preserve previous versions;
* respect permissions;
* respect subscription entitlement;
* have deterministic effective behavior.

---

# 39. Price Invariants

Price changes must not silently alter already-created order snapshots.

Where the defined configuration boundary requires it, price changes become effective from the next Cash Session.

Historical prices must remain reconstructable.

---

# 40. Set Invariants

Sets must:

* have their own price;
* preserve composition;
* not permit unsupported component substitution;
* preserve historical composition;
* use explicit versioning when composition changes.

Underlying recipe changes must not silently rewrite an already-defined Set configuration.

---

# 41. Employee Invariants

Every operational employee must have an individual identity.

Normal operations must not rely on shared employee accounts.

Employee deactivation must prevent unauthorized new operations while preserving historical records.

---

# 42. Permission Invariants

Permissions must never:

* grant access outside Business scope;
* grant access outside allowed Branch scope;
* bypass subscription entitlement;
* allow unauthorized self-escalation;
* allow Managers to grant permissions beyond their authority.

---

# 43. Employee Override Invariant

Employee-specific overrides must not destroy the underlying role template.

The system must preserve enough information to determine:

* role permissions;
* employee override;
* effective permission.

---

# 44. Payroll Invariants

Payroll calculations must preserve the applicable calculation snapshot.

Finalized payroll must not be silently rewritten.

Corrections must be separate and auditable.

---

# 45. Report Invariants

Reports must:

* have explicit scope;
* have explicit period;
* have a consistent data snapshot;
* preserve version history where required;
* remain immutable after creation;
* link relevant new versions to the change causing them.

---

# 46. Report Version Invariant

A new report version must be created only when relevant underlying data changes.

A correction that does not affect the report's relevant metrics does not require a new report version.

---

# 47. Report Export Invariant

An exported report must correspond to a specific report version/snapshot.

Export must not silently generate a different dataset from the displayed version.

---

# 48. Notification Invariants

Notifications must:

* belong to a Business where applicable;
* respect Branch scope;
* respect recipient permissions;
* avoid duplicate active notifications for the same condition;
* preserve relevant history;
* not block core POS transactions.

Notification failure must not roll back the originating business transaction.

---

# 49. Audit Invariants

Important state-changing operations must be auditable.

Audit records must preserve, where applicable:

* actor;
* Business;
* Branch;
* Device;
* Cash Session;
* Transaction;
* timestamp;
* operation;
* old state;
* new state;
* reason;
* result;
* source.

Audit records must be protected against ordinary modification.

---

# 50. Audit vs Logging Invariant

Technical logs and business audit records are different.

Logs are for:

* troubleshooting;
* monitoring;
* performance;
* operational diagnosis.

Audit is for:

* accountability;
* historical reconstruction;
* security;
* business change history.

They must not be treated as interchangeable.

---

# 51. Synchronization Invariants

Synchronization must:

1. preserve transaction identity;
2. validate authorization;
3. validate Business scope;
4. validate Branch scope;
5. validate device trust where required;
6. validate employee state;
7. validate subscription state;
8. validate payload integrity;
9. prevent duplicate application;
10. preserve conflicts explicitly.

---

# 52. Synchronization Ordering Invariant

Synchronization must respect business dependencies.

For example:

```text
Configuration
    ↓
Order
    ↓
Payment
```

must not be interpreted as an arbitrary ordering rule.

Actual dependency rules must be defined by operation semantics.

Transaction synchronization takes priority over configuration synchronization when required for safe recovery.

---

# 53. Sync Batch Invariant

Synchronization batches must remain bounded.

The typical initial target is:

```text
50–100 operations
```

subject to:

* payload size;
* processing cost;
* server capacity;
* operation type.

---

# 54. Partial Sync Invariant

A failed operation must not automatically cause already-successful operations in the same batch to be repeated.

Each operation must have an explicit result.

---

# 55. Conflict Invariant

If a conflict cannot be safely resolved automatically:

```text
Conflict
```

must be persisted.

The system must not silently choose an arbitrary state.

Conflict resolution requires:

* authorized actor;
* explicit decision;
* reason;
* audit.

---

# 56. Clock Invariants

The system must distinguish:

* server timestamp;
* client timestamp;
* synchronization timestamp.

Suspicious clock rollback must be detectable.

Critical lifecycle decisions must not rely solely on an untrusted client clock.

---

# 57. Background Processing Invariants

Background jobs must:

* have stable identity;
* be retryable where appropriate;
* be idempotent where necessary;
* preserve failure state;
* have bounded retries;
* support dead-letter/manual intervention where appropriate;
* not corrupt core business state.

---

# 58. Queue Invariant

A queue is a processing mechanism.

It is not the permanent source of business truth.

If a queue is unavailable, durable business state must remain intact.

---

# 59. Worker Invariant

Workers must not consume unlimited resources.

Worker concurrency must be bounded.

Heavy jobs must not starve POS operations.

---

# 60. Cache Invariants

Cache must:

* have a defined scope;
* have a defined lifetime;
* have invalidation rules;
* avoid sensitive data leakage;
* tolerate failure;
* never become the sole source of critical business state.

---

# 61. Cache Invalidation Invariant

When configuration changes affect cached data, the relevant cache must be:

* invalidated;
* versioned;
* or otherwise prevented from returning stale authoritative configuration.

---

# 62. Data Lifecycle Invariants

Business lifecycle:

```text
Active
  ↓
Expired / Read-Only
  ↓
Deletion Eligible
  ↓
Deleting
  ↓
Deleted
```

The transition must be deterministic.

---

# 63. Sixty-Day Retention Invariant

The deletion countdown begins from the exact:

```text
subscription_expired_at
```

timestamp.

It must not depend on:

* the date a user notices expiry;
* the date a notification is sent;
* the date an administrator opens the Business.

---

# 64. Reactivation Invariant

If reactivation occurs before permanent deletion:

* the same Business identity is retained;
* historical data is retained;
* configuration is retained;
* relevant devices and access state are restored according to security rules.

Reactivation must not create a duplicate Business.

---

# 65. Deletion Invariant

Permanent deletion must:

* be authorized by lifecycle rules;
* be performed by controlled background processing;
* be idempotent;
* support retry;
* preserve operational safety;
* invalidate trusted devices;
* prevent stale offline events from resurrecting data.

---

# 66. Business UUID Reuse Invariant

A deleted Business UUID must never be reused for another Business.

This protects:

* synchronization;
* audit history;
* external references;
* debugging;
* security.

---

# 67. Historical Integrity Invariant

The system must preserve enough information to reconstruct important historical states.

At minimum, relevant history must remain available for:

* orders;
* payments;
* refunds;
* cash sessions;
* inventory;
* configuration;
* permissions;
* employees;
* reports;
* audit events.

---

# 68. No Silent Historical Rewrite

The system must not silently change historical records merely because:

* a product price changed;
* a recipe changed;
* a permission changed;
* an employee was deactivated;
* a configuration changed;
* a Business subscription changed.

Historical records must preserve their original applicable context.

---

# 69. Error Handling Invariants

Errors must have predictable behavior.

Every important operation should end in one of:

```text
Success
Safe Rejection
Recoverable Pending State
```

An operation must not leave ambiguous state without a recoverable representation.

---

# 70. Lost Response Invariant

If the client does not receive a response after submitting a transaction, it must not automatically assume failure and create a new transaction.

The same Transaction UUID must be retried.

---

# 71. Database Failure Invariant

A database failure must never result in the system falsely reporting a committed transaction.

The client must receive a safe failure or pending/retry state.

---

# 72. Application Crash Invariant

An application crash must not leave critical business state partially committed.

Database transactions must provide atomicity.

Durable background state must support recovery.

---

# 73. Network Failure Invariant

Network failure must not:

* duplicate payments;
* duplicate orders;
* duplicate inventory deductions;
* silently lose durable offline transactions.

---

# 74. Printer Failure Invariant

Printer failure must not roll back a successfully committed ERP transaction.

Printer processing must be represented independently.

---

# 75. Notification Failure Invariant

Notification failure must not roll back the originating business transaction.

The notification should be retried according to background processing policy.

---

# 76. External Service Invariant

External services must not be required inside a critical database transaction unless the architecture explicitly proves that requirement necessary.

The preferred pattern is:

```text
Commit Core State
      ↓
Publish / Queue
      ↓
External Processing
```

---

# 77. API Invariants

API endpoints must:

* validate input;
* authenticate where required;
* authorize;
* enforce Business scope;
* enforce Branch scope;
* enforce subscription entitlement;
* call application use cases;
* return stable error codes;
* preserve idempotency where required.

---

# 78. API Versioning Invariant

Breaking API changes must not silently appear under an existing API contract.

Breaking changes require:

* versioning;
* compatibility strategy;
* migration;
* or explicit architecture decision.

---

# 79. Frontend Invariants

The frontend must not be the final authority for:

* permissions;
* subscription status;
* inventory;
* payment validity;
* cash session validity;
* synchronization acceptance.

UI restrictions improve usability but do not replace server validation.

---

# 80. Frontend Offline Invariant

Offline frontend state must be treated as temporary operational state until synchronized and validated by the server.

The frontend must clearly distinguish:

* local pending;
* synchronized;
* conflict;
* failed.

---

# 81. Database Access Invariants

Database access must:

* use parameterized queries;
* respect module ownership;
* use explicit transactions;
* avoid uncontrolled N+1 queries;
* avoid unnecessary full-table scans;
* enforce tenant/branch filtering;
* respect authorization boundaries.

---

# 82. Migration Invariants

Database migrations must:

* be version-controlled;
* be tested;
* be deterministic;
* preserve existing data unless destructive behavior is explicitly approved;
* support deployment compatibility where required.

---

# 83. Deployment Invariants

Production deployment must provide:

* controlled configuration;
* secure secrets;
* health checks;
* rollback strategy;
* migration safety;
* logging;
* monitoring;
* backup strategy.

---

# 84. Configuration Invariants

Secrets must never be hardcoded into:

* source code;
* frontend bundles;
* public configuration files;
* Git history.

Environment-specific configuration must remain separate.

---

# 85. Dependency Invariants

Production dependencies must be:

* explicitly declared;
* version controlled;
* security reviewed;
* reproducibly installed.

An unmaintained dependency should not be introduced without justification.

---

# 86. Security Invariants

Security-sensitive decisions must be server-authoritative.

The system must protect against:

* tenant escape;
* branch escape;
* privilege escalation;
* replay;
* duplicate transactions;
* unauthorized device use;
* expired subscription bypass;
* stale offline authorization;
* malicious synchronization payloads.

---

# 87. Cryptography Invariants

The system must:

* use established cryptographic libraries;
* use appropriate algorithms;
* protect private keys;
* rotate keys where required;
* avoid custom cryptographic algorithms.

---

# 88. Password Invariants

Passwords must:

* never be stored plaintext;
* use strong password hashing;
* never be logged;
* never appear in API responses;
* never be included in audit payloads.

---

# 89. Sensitive Data Invariant

Sensitive information must be minimized.

Logs, audit records, reports, and synchronization payloads must not contain unnecessary secrets or sensitive data.

---

# 90. Performance Invariants

POS operations have priority over heavy background processing.

The system must protect POS from:

* large report generation;
* synchronization storms;
* mass exports;
* cleanup jobs;
* large imports;
* background recalculation.

---

# 91. Database Performance Invariant

The system must prefer:

* appropriate indexes;
* short transactions;
* bounded queries;
* pagination;
* keyset pagination where useful;
* controlled connection pools.

Over-indexing and uncontrolled database access are prohibited.

---

# 92. Resource Limit Invariant

The following must have reasonable bounds:

* request size;
* synchronization batch size;
* worker concurrency;
* database connections;
* export size;
* upload size;
* pagination limits;
* retry count.

---

# 93. Observability Invariants

Important operations should be traceable using:

* Correlation ID;
* Transaction UUID;
* Event UUID;
* Business UUID;
* Branch UUID;
* Device UUID where relevant.

Technical logs and audit events must remain distinguishable.

---

# 94. Monitoring Invariant

The system must monitor at least:

* application health;
* database health;
* queue health;
* worker health;
* synchronization failures;
* synchronization conflicts;
* backup status;
* storage capacity;
* error rates;
* important latency metrics.

---

# 95. Recovery Invariants

Every critical subsystem must have a failure and recovery strategy.

At minimum:

* application;
* PostgreSQL;
* cache;
* queue;
* workers;
* storage;
* synchronization;
* reporting;
* deployment;
* backup;
* Business deletion.

---

# 96. Backup Invariants

Backups must:

* be automated where appropriate;
* be monitored;
* be protected;
* be tested through restoration;
* have defined retention.

A backup that has never been successfully restored must not be assumed reliable.

---

# 97. Scaling Invariants

Scaling must preserve:

* tenant isolation;
* transaction correctness;
* idempotency;
* authorization;
* historical integrity.

Adding more application instances must not create duplicate business effects.

---

# 98. Technology Change Invariant

Replacing a technology must not silently change business semantics.

For example:

```text
Flask → another framework
```

must not imply:

```text
Different authorization rules
Different payment behavior
Different inventory behavior
```

Technology is replaceable; business behavior is not.

---

# 99. Architecture Review Invariant

A significant architecture change must be reviewed against:

* Business Analysis;
* System Analysis;
* Domain Analysis;
* Architecture;
* Security;
* Database;
* API;
* Testing;
* Deployment;
* Operations.

Affected documents must be updated.

---

# 100. AI Coding Agent Guardrails

AI coding agents working on FastFood ERP must follow these rules.

### 100.1. Do Not Invent Business Rules

If a requested implementation requires an unknown business rule, the agent must not silently invent one.

### 100.2. Do Not Bypass Architecture

An agent must not implement a shortcut that bypasses:

* Application Layer;
* Domain rules;
* authorization;
* tenant isolation;
* branch scope;
* subscription checks.

### 100.3. Do Not Modify Historical Data Silently

Historical corrections must use the defined correction model.

### 100.4. Do Not Introduce New Infrastructure Without Justification

An agent must not add:

* a new database;
* a new queue;
* a new service;
* a new distributed platform

without architectural justification.

### 100.5. Preserve Idempotency

Retryable operations must remain idempotent.

### 100.6. Preserve Offline Compatibility

Changes to transactional models must consider offline synchronization.

### 100.7. Preserve API Compatibility

Breaking API changes require explicit review.

### 100.8. Update Documentation

When an implementation changes an architectural decision, the corresponding documentation and ADR must be updated.

---

# 101. Code Review Guardrails

Code review should verify:

1. Correct domain ownership.
2. Correct Business isolation.
3. Correct Branch isolation.
4. Correct authorization.
5. Correct subscription enforcement.
6. Correct transaction boundary.
7. Correct idempotency.
8. Correct audit behavior.
9. Correct historical behavior.
10. Correct offline behavior.
11. Correct synchronization behavior.
12. Correct error handling.
13. Correct resource usage.
14. Correct testing.
15. Correct observability.

---

# 102. Testing Guardrails

Every critical invariant should have automated tests where practical.

Tests should cover:

* normal operation;
* unauthorized operation;
* concurrent operation;
* retry;
* duplicate request;
* network failure;
* database failure;
* offline operation;
* synchronization;
* conflict;
* recovery;
* subscription expiry;
* employee deactivation;
* device revocation.

---

# 103. Architecture Violation Handling

If an implementation violates an invariant, the violation must be treated as an architecture issue rather than merely a code-style issue.

The response should be:

1. identify the violated invariant;
2. identify affected components;
3. assess data/security impact;
4. correct the implementation;
5. add or strengthen tests;
6. update documentation if necessary.

---

# 104. Guardrail Priority

When two requirements conflict, use the following priority:

```text
1. Data Integrity
2. Security
3. Financial Correctness
4. Historical Integrity
5. Tenant/Branch Isolation
6. Operational Reliability
7. POS Continuity
8. Performance
9. Developer Convenience
```

This ordering may be overridden only by an explicit architecture decision.

---

# 105. Architecture Invariant Catalog

The following categories are considered mandatory architecture guardrail groups:

```text
Identity
Authentication
Authorization
Tenant Isolation
Branch Isolation
Subscription
Device Trust
Offline
UUID / Idempotency
Transactions
Orders
Inventory
Payments
Cash
Employees
Payroll
Configuration
Reports
Notifications
Audit
Synchronization
Background Jobs
Data Lifecycle
Security
API
Frontend
Database
Deployment
Observability
Performance
Recovery
Technology Evolution
```

---

# 106. Completion Criteria

This document is considered complete when:

* architectural invariants are explicitly defined;
* tenant isolation rules are defined;
* branch isolation rules are defined;
* authorization rules are defined;
* offline rules are defined;
* transaction rules are defined;
* financial rules are defined;
* inventory rules are defined;
* synchronization rules are defined;
* historical integrity rules are defined;
* failure/recovery rules are defined;
* performance guardrails are defined;
* security guardrails are defined;
* deployment guardrails are defined;
* AI coding-agent guardrails are defined;
* code-review guardrails are defined;
* testing guardrails are defined.

---

# 107. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Domain Analysis

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### Architecture

* `docs/04_Architecture/01_System_Architecture.md`
* `docs/04_Architecture/02_Application_Layer_Architecture.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/04_Backend_Architecture.md`
* `docs/04_Architecture/05_Frontend_Architecture.md`
* `docs/04_Architecture/06_API_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/08_Offline_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/10_Security_Architecture.md`
* `docs/04_Architecture/11_Deployment_Architecture.md`
* `docs/04_Architecture/12_Event_and_Message_Architecture.md`
* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/14_Caching_Architecture.md`
* `docs/04_Architecture/15_Observability_and_Operations_Architecture.md`
* `docs/04_Architecture/16_Scalability_and_Performance_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`
* `docs/04_Architecture/18_Technology_Selection.md`
* `docs/04_Architecture/19_Architecture_Decisions_and_Tradeoffs.md`

---

# 108. Architecture Layer Completion

With this document, the initial Architecture document set is considered complete at the guardrail level.

The next architectural work should focus on:

```text
Architecture
     ↓
Database Design
     ↓
Backend Design
     ↓
Frontend Design
     ↓
API Contracts
     ↓
Security Implementation
     ↓
Testing Strategy
     ↓
Deployment Implementation
```

Implementation must preserve the invariants defined in this document.

