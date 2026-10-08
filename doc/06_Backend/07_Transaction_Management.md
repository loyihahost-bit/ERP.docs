# Transaction Management

**Document ID:** BE-07
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/06_Backend/README.md`

---

## 1. Purpose

This document defines how FastFood ERP manages database transactions.

Transaction management must guarantee that related business changes are committed atomically when required, while keeping transactions short enough for reliable POS performance.

The primary database is PostgreSQL.

The application uses SQLAlchemy for persistence.

The Application Layer owns transaction boundaries.

---

## 2. Core Principle

The system follows:

> One business operation should have one explicit transaction boundary when its required state changes must succeed or fail together.

The transaction boundary must be determined by the Application/Use Case Layer.

Repositories participate in the transaction but do not own its completion.

---

## 3. Transaction Ownership

The Application Layer owns:

* transaction start;
* transaction scope;
* commit;
* rollback;
* retry decisions where appropriate.

Repositories must not silently commit.

Conceptually:

```text id="txn001"
Use Case
   ↓
Begin Transaction
   ↓
Repository Operations
   ↓
Domain Operations
   ↓
Audit / Outbox
   ↓
Commit
```

---

## 4. Unit of Work

The backend should use a Unit of Work abstraction to coordinate a database session and transaction.

Conceptually:

```text id="txn002"
UnitOfWork
 ├── OrderRepository
 ├── InventoryRepository
 ├── PaymentRepository
 ├── AuditRepository
 └── OutboxRepository
```

All repositories participating in one use case should use the same transaction context.

---

## 5. Transaction Lifecycle

The normal lifecycle is:

```text id="txn003"
BEGIN
  ↓
Load required state
  ↓
Validate
  ↓
Execute domain operation
  ↓
Persist changes
  ↓
Create audit/outbox records
  ↓
COMMIT
```

On failure:

```text id="txn004"
BEGIN
  ↓
Operation
  ↓
ERROR
  ↓
ROLLBACK
```

No partial core state may remain after rollback.

---

## 6. Atomicity

Atomicity is required when multiple changes represent one business operation.

Example:

### Order Acceptance

```text id="txn005"
Validate Order
    +
Validate Inventory
    +
Deduct Inventory
    +
Change Order State
    +
Create Audit Event
    +
Create Outbox Event
        ↓
      COMMIT
```

If a required core step fails, the transaction must roll back.

---

## 7. Core Transaction vs Secondary Processing

The system distinguishes between:

### Core Transaction

Required to establish authoritative business state.

Examples:

* Order acceptance;
* payment recording;
* inventory deduction;
* Cash Session opening/closing;
* price configuration change;
* recipe approval.

### Secondary Processing

Can happen after the core transaction.

Examples:

* notification delivery;
* report generation;
* analytics;
* non-critical cache refresh;
* external message delivery.

Secondary failure must not normally roll back a successfully committed core transaction.

---

## 8. Outbox Principle

When a committed business operation must trigger asynchronous work, the transaction should create an Outbox record.

Example:

```text id="txn006"
Core Transaction
   ├── Business State
   ├── Audit
   └── Outbox Event
          ↓
       COMMIT
          ↓
    Background Worker
          ↓
 Notification / Report / Other Work
```

This prevents committed business changes from depending on unreliable external processing.

---

## 9. Transaction Boundary Example

### Record Payment

The payment use case may include:

```text id="txn007"
BEGIN
  ↓
Load Order
  ↓
Validate Order State
  ↓
Validate Payment
  ↓
Create Payment
  ↓
Update Order Financial State
  ↓
Create Audit Event
  ↓
Create Outbox Event if required
  ↓
COMMIT
```

Payment must not be committed separately from required Order financial state.

---

## 10. Transaction Boundary Example

### Close Cash Session

```text id="txn008"
BEGIN
  ↓
Lock Cash Session
  ↓
Validate Session State
  ↓
Validate Cash Count
  ↓
Calculate Difference
  ↓
Close Session
  ↓
Create Audit Event
  ↓
Create Notification Outbox Event
  ↓
COMMIT
```

Notification delivery occurs after commit.

---

## 11. Transaction Boundary Example

### Change Product Price

```text id="txn009"
BEGIN
  ↓
Load Current Configuration Version
  ↓
Validate Expected Version
  ↓
Create New Configuration Version
  ↓
Create Audit Event
  ↓
Create Outbox Event
  ↓
COMMIT
```

If the configuration version is stale, the transaction fails with a conflict.

---

# 12. Transaction Scope

Transactions should be:

* explicit;
* minimal;
* deterministic;
* short-lived;
* limited to required database operations.

A transaction should not remain open while waiting for:

* user interaction;
* external API responses;
* printer responses;
* email delivery;
* notification delivery;
* long-running calculations;
* large file generation.

---

# 13. No User Interaction Inside Transaction

The backend must never keep a database transaction open while waiting for a user.

Bad:

```text id="txn010"
BEGIN
  ↓
Ask user for confirmation
  ↓
Wait
  ↓
Continue
  ↓
COMMIT
```

Preferred:

```text id="txn011"
Request
  ↓
Validate
  ↓
Commit state
```

If confirmation is required, it must be represented as a separate application operation.

---

# 14. No External Network Calls Inside Core Transaction

Core database transactions should not depend on external network calls.

Bad:

```text id="txn012"
BEGIN
  ↓
Update Order
  ↓
Call external service
  ↓
Wait
  ↓
COMMIT
```

Preferred:

```text id="txn013"
BEGIN
  ↓
Update Order
  ↓
Create Outbox Event
  ↓
COMMIT
  ↓
Worker
  ↓
External Service
```

---

# 15. Transaction and Printing

Printing must not determine whether a core business transaction commits.

Example:

```text id="txn014"
Accept Order
   ↓
Commit
   ↓
Create Print Job
   ↓
Printer Worker
```

A printer failure must not undo a valid Order acceptance.

---

# 16. Transaction and Notifications

Notifications are secondary processing.

Example:

```text id="txn015"
Cash Session Closed
   ↓
Commit
   ↓
Notification Worker
   ↓
Owner Notification
```

Notification failure must not reopen or roll back the Cash Session.

---

# 17. Transaction and Reports

Reports should not execute inside operational transactions.

For example:

```text id="txn016"
Payment Transaction
   ↓
Commit
   ↓
Report data becomes available
   ↓
Report generation
```

Heavy report generation is asynchronous.

---

# 18. Transaction and Audit

Important business state changes and their corresponding audit events should be committed atomically.

Preferred:

```text id="txn017"
BEGIN
  ↓
Change Business State
  ↓
Create Audit Event
  ↓
COMMIT
```

This ensures that a committed important business change does not exist without its required audit record.

---

# 19. Transaction and Outbox

The same principle applies to required Outbox events.

```text id="txn018"
BEGIN
  ↓
Business Change
  ↓
Audit Event
  ↓
Outbox Event
  ↓
COMMIT
```

If the transaction rolls back, the Outbox event also disappears.

---

# 20. Rollback

Rollback must restore the database transaction to its state before the transaction began.

Application code must not continue using an invalid transaction after a database exception.

After rollback, the session should be:

* safely closed;
* reset;
* or replaced according to the Unit of Work lifecycle.

---

# 21. Commit Failure

A commit failure must be treated as an uncertain outcome until the system can establish the final state.

The client must not blindly retry a non-idempotent operation.

Operation UUID/idempotency mechanisms are required for retryable business commands.

---

# 22. Idempotent Transactions

Commands that may be retried must have a stable operation UUID.

Example:

```text id="txn019"
operation_id = UUID-X

First request
    ↓
Transaction executes
    ↓
COMMIT

Retry with UUID-X
    ↓
Existing operation found
    ↓
Return previous result
```

This prevents duplicate business effects.

---

# 23. Transaction and Idempotency Record

When required, the idempotency record should be created in the same transaction as the core business operation.

Conceptually:

```text id="txn020"
BEGIN
  ↓
Create Idempotency Record
  ↓
Execute Business Operation
  ↓
Store Result
  ↓
COMMIT
```

The database uniqueness constraint protects against concurrent duplicate operations.

---

# 24. Concurrent Duplicate Requests

Two requests with the same operation UUID may arrive simultaneously.

The system must ensure that only one creates the authoritative business effect.

Possible flow:

```text id="txn021"
Request A ─┐
           ├── Unique Operation ID
Request B ─┘
           ↓
      One succeeds
      One observes existing operation
```

No duplicate payment, inventory deduction, or Order acceptance may occur.

---

# 25. Transaction Isolation

The system should use PostgreSQL's default transaction isolation unless a specific business operation requires stronger isolation.

Stronger isolation should not be selected globally without a documented reason.

---

# 26. Row-Level Locking

Row-level locks should be used for highly concurrent mutable state.

Examples:

* Inventory quantity;
* Cash Session;
* financial state;
* configuration version where necessary;
* other serialized resources.

Example:

```text id="txn022"
SELECT ...
FOR UPDATE
```

The exact locking strategy belongs to the relevant use case.

---

# 27. Inventory Transaction

Inventory deduction is a core transactional operation.

Example:

```text id="txn023"
BEGIN
  ↓
Lock Inventory Rows
  ↓
Check Available Quantity
  ↓
Calculate Required Quantity
  ↓
Deduct Stock
  ↓
Create Inventory Transaction
  ↓
Update Order State
  ↓
Audit / Outbox
  ↓
COMMIT
```

If any required inventory quantity is insufficient, the transaction must fail without leaving partial deductions.

---

# 28. Multiple Inventory Rows

An Order may require multiple inventory records.

The system should:

1. Determine all required inventory records.
2. Establish a deterministic lock order.
3. Lock the required records.
4. Validate all quantities.
5. Apply deductions.
6. Commit once.

This reduces partial updates and deadlock risk.

---

# 29. Cash Session Transaction

Cash Session state changes are serialized.

Example:

```text id="txn024"
BEGIN
  ↓
Lock Cash Register / relevant session state
  ↓
Validate current state
  ↓
Create or close session
  ↓
Audit
  ↓
Outbox
  ↓
COMMIT
```

Two employees must not successfully create conflicting active sessions for the same Register.

---

# 30. First Successful Operation Wins

For concurrency-sensitive operations such as Cash Session opening:

```text id="txn025"
Request A ─┐
           ├── Database constraint / lock
Request B ─┘
           ↓
First valid commit succeeds
Second request → conflict
```

The system must not create two authoritative active sessions when only one is allowed.

---

# 31. Payment Transaction

Payment recording must protect against duplicate financial effects.

The transaction should validate:

* Order;
* payment state;
* payment amount;
* payment method;
* employee;
* Branch;
* Cash Session where required;
* operation UUID.

Then commit the financial state atomically.

---

# 32. Refund Transaction

Refunds are separate transactions.

A refund transaction should:

```text id="txn026"
BEGIN
  ↓
Validate original Payment
  ↓
Validate refund permission
  ↓
Validate refund amount
  ↓
Create Refund
  ↓
Update financial state
  ↓
Audit
  ↓
Outbox if required
  ↓
COMMIT
```

Current Product price must not affect the refund amount.

---

# 33. Payment Correction

Payment correction must not silently mutate historical payment state.

Preferred:

```text id="txn027"
Original Payment
      ↓
Correction / Revision
      ↓
New authoritative state
```

The original historical record remains preserved.

The correction chain must be committed atomically with required audit records.

---

# 34. Order Acceptance

Order acceptance is one of the most important core transactions.

The transaction may include:

```text id="txn028"
Load Order
   ↓
Lock required state
   ↓
Validate Order state
   ↓
Validate Product / Recipe / Set
   ↓
Validate Inventory
   ↓
Deduct Inventory
   ↓
Change Order status
   ↓
Create audit event
   ↓
Create kitchen/print outbox event
   ↓
COMMIT
```

Printing and kitchen notification occur after commit.

---

# 35. Order Modification

Modifying an Order depends on its current state.

For an editable Order:

```text id="txn029"
BEGIN
  ↓
Load Order
  ↓
Validate state
  ↓
Apply modification
  ↓
Recalculate authoritative financial snapshot
  ↓
Audit
  ↓
COMMIT
```

After the Order reaches a state where normal modification is prohibited, the relevant correction workflow must be used.

---

# 36. Configuration Transaction

Configuration changes use optimistic concurrency.

Example:

```text id="txn030"
BEGIN
  ↓
Load Version N
  ↓
Validate expected version
  ↓
Create Version N+1
  ↓
Audit
  ↓
Outbox
  ↓
COMMIT
```

A stale version produces a conflict.

---

# 37. Recipe Approval Transaction

Recipe approval may include:

```text id="txn031"
BEGIN
  ↓
Load Recipe Version
  ↓
Validate approval authority
  ↓
Validate Recipe state
  ↓
Approve Recipe
  ↓
Create audit event
  ↓
Create configuration/outbox event
  ↓
COMMIT
```

The approved Recipe Version becomes available according to the effective configuration rules.

---

# 38. Transaction and Branch Scope

Every transaction must operate within a validated Business context.

For Branch-scoped operations:

```text id="txn032"
Transaction Context
    Business
       +
    Branch
```

Cross-Branch state must not be accidentally modified.

---

# 39. Transaction and Business Lifecycle

Before executing a modifying transaction, the Application Layer must validate Business lifecycle state.

Example:

```text id="txn033"
ACTIVE
   ↓
modification allowed

READ_ONLY
   ↓
modification rejected
```

Offline synchronization must perform equivalent authoritative validation.

---

# 40. Transaction and Subscription

Subscription entitlement must be validated before a modifying use case executes.

A transaction must not create a new Business state that is forbidden by the current subscription.

---

# 41. Transaction and Offline Synchronization

Offline operations are not committed directly to the server database while offline.

After reconnect:

```text id="txn034"
Offline Operation
      ↓
Sync Request
      ↓
Authenticate Device
      ↓
Validate Business Lifecycle
      ↓
Validate Operation
      ↓
Idempotency Check
      ↓
Execute Server Transaction
      ↓
Commit
```

Each accepted operation becomes authoritative only after server-side validation.

---

# 42. Sync Batch Transactions

A synchronization batch may contain multiple operations.

The system must distinguish:

* batch;
* operation;
* transaction.

A batch does not necessarily mean that every operation must share one database transaction.

---

# 43. Partial Batch Success

Where operations are independent, the server may process them individually or in dependency groups.

Example:

```text id="txn035"
Batch
 ├── Operation A → Success
 ├── Operation B → Conflict
 ├── Operation C → Success
 └── Operation D → Retry
```

The entire batch must not be rolled back merely because one independent operation failed.

---

# 44. Dependent Synchronization Operations

Dependent operations may require ordered processing.

Example:

```text id="txn036"
Create Order
   ↓
Accept Order
   ↓
Record Payment
```

If the first operation fails, dependent operations must not be committed as if the dependency existed.

---

# 45. Transaction Retry

Automatic retry is allowed only when:

* the failure is transient;
* the operation is safe to retry;
* idempotency is preserved;
* the transaction can be recreated cleanly.

Do not blindly retry:

* validation errors;
* authorization failures;
* business rule violations;
* permanent constraint violations.

---

# 46. Deadlock Retry

A database deadlock may be retried.

The retry should:

1. Roll back the failed transaction.
2. Start a fresh transaction.
3. Re-read required state.
4. Re-execute the operation.
5. Preserve the same operation UUID.
6. Stop after a bounded number of attempts.

The application must never reuse a broken transaction.

---

# 47. Serialization Conflict Retry

If a stronger isolation level is used for a specific operation and PostgreSQL reports a serialization conflict, the operation may be retried under the same idempotency rules.

The retry must use fresh database state.

---

# 48. Transaction Timeout

Long-running transactions should be detected and controlled.

Transactions should not remain open while:

* generating large reports;
* processing large exports;
* calling external services;
* waiting for printers;
* waiting for user confirmation.

Long-running business operations should be split into asynchronous workflows where appropriate.

---

# 49. Nested Transactions

Business workflows should not rely on arbitrary nested independent transactions.

If a nested operation is logically part of the parent transaction, it should normally use the same Unit of Work.

Savepoints may be used for narrowly defined technical recovery cases.

---

# 50. Savepoints

Savepoints may be used when a specific operation needs partial database rollback without ending the outer transaction.

They should not be used to hide business workflow complexity.

Example:

```text id="txn037"
BEGIN
  ↓
Core Work
  ↓
SAVEPOINT
  ↓
Optional Technical Operation
  ↓
ROLLBACK TO SAVEPOINT if needed
  ↓
Continue
  ↓
COMMIT
```

Use of savepoints must have a documented reason.

---

# 51. Transaction and Cache

Cache updates should not determine transaction success.

Preferred:

```text id="txn038"
BEGIN
  ↓
Update PostgreSQL
  ↓
COMMIT
  ↓
Invalidate / refresh cache
```

If cache invalidation fails, the committed database state remains authoritative.

---

# 52. Transaction and File Storage

File generation or upload should normally happen after the core transaction.

Example:

```text id="txn039"
Commit Report Version
       ↓
Background Worker
       ↓
Generate XLSX
       ↓
Store File
```

A file-storage failure must not roll back an already committed core transaction unless the file itself is part of the required atomic business state.

---

# 53. Transaction and Notifications

Notifications are delivered after successful commit.

The transaction should create an Outbox event when required.

```text id="txn040"
Business Change
   ↓
Outbox Event
   ↓
COMMIT
   ↓
Notification Worker
```

---

# 54. Transaction and Audit Failure

For important business changes, audit creation is part of the core transaction.

If required audit persistence fails:

```text id="txn041"
Business Change
+
Audit
    ↓
Audit failure
    ↓
ROLLBACK
```

This preserves historical integrity.

---

# 55. Secondary Audit

Technical/security logs that are not required for business audit may be handled separately.

Their failure must not necessarily roll back the business transaction.

The distinction between required business audit and secondary technical logging must remain explicit.

---

# 56. Transaction and Outbox Failure

If an Outbox record is required for a committed business event and cannot be persisted:

```text id="txn042"
Business Change
+
Required Outbox
    ↓
Outbox failure
    ↓
ROLLBACK
```

If the event is optional, the architecture may handle it separately.

Required vs optional event semantics must be explicit.

---

# 57. Transaction and Background Jobs

Background jobs must not share request transactions.

Each job should:

```text id="txn043"
Create Job Transaction
   ↓
Load Current State
   ↓
Perform Work
   ↓
Commit
```

Jobs should be independently retryable.

---

# 58. Transaction and Reports

Report generation should read committed state.

A report must not depend on uncommitted operational changes.

For versioned reports:

```text id="txn044"
Read Committed State
   ↓
Generate Report Version
   ↓
Persist Version
   ↓
Commit
```

---

# 59. Transaction and Monthly Reports

Monthly automatic reports should run only after the relevant operational period is ready according to the report rules.

If the final Cash Session is still open, the report workflow should wait or create the appropriate pending state rather than reading incomplete financial state as final.

---

# 60. Transaction and Historical Integrity

Transactions must not rewrite historical records merely to simplify current state.

Historical data should be preserved through:

* snapshots;
* revisions;
* versions;
* corrections;
* immutable audit records.

---

# 61. Transaction Error Categories

Transaction failures should map into meaningful categories:

```text id="txn045"
Validation Error
Authorization Error
Business Rule Violation
Conflict
Concurrency Failure
Temporary Infrastructure Error
Permanent Infrastructure Error
```

The API must not expose raw SQLAlchemy/PostgreSQL errors.

---

# 62. Constraint Violation Handling

Database constraint violations should be translated into application-level errors.

Example:

```text id="txn046"
Unique Constraint Violation
        ↓
Repository / Unit of Work
        ↓
Conflict
        ↓
Application Result
        ↓
API
```

---

# 63. Transaction Logging

Transaction logs should include safe operational metadata:

* request ID;
* operation ID;
* Business ID;
* Branch ID;
* employee ID where appropriate;
* transaction type;
* duration;
* outcome;
* error category.

Sensitive financial or authentication secrets must not be logged unnecessarily.

---

# 64. Transaction Metrics

The system should monitor:

* transaction duration;
* commit latency;
* rollback rate;
* deadlock rate;
* retry rate;
* lock wait time;
* serialization conflict rate;
* database connection usage.

These metrics help identify performance problems without weakening business consistency.

---

# 65. Transaction Performance

POS-critical transactions should remain short.

The system should:

1. Load only required data.
2. Lock only required rows.
3. Avoid network calls.
4. Avoid large queries.
5. Avoid report generation.
6. Avoid file generation.
7. Avoid notification delivery.
8. Commit promptly.

---

# 66. Transaction Ordering

Where multiple state changes are required, the application should use a deterministic order.

Typical pattern:

```text id="txn047"
Load / Lock
    ↓
Validate
    ↓
Domain State Change
    ↓
Persistence
    ↓
Audit
    ↓
Outbox
    ↓
Commit
```

This makes transaction behavior easier to reason about and test.

---

# 67. Transaction Boundaries by Operation

| Operation            | Transaction                 | Locking                       |
| -------------------- | --------------------------- | ----------------------------- |
| Create Order         | Yes                         | Limited                       |
| Modify Order         | Yes                         | Order                         |
| Accept Order         | Yes                         | Inventory + Order as required |
| Record Payment       | Yes                         | Financial state               |
| Refund               | Yes                         | Payment/financial state       |
| Open Cash Session    | Yes                         | Register/session              |
| Close Cash Session   | Yes                         | Session                       |
| Cash Handover        | Yes                         | Session/register              |
| Inventory Adjustment | Yes                         | Inventory                     |
| Change Price         | Yes                         | Version check                 |
| Approve Recipe       | Yes                         | Recipe/version                |
| Permission Change    | Yes                         | Employee/permission state     |
| Generate Report      | Separate report transaction | Read-oriented                 |
| Send Notification    | No core transaction         | Background job                |
| Generate XLSX        | No core transaction         | Background job                |

---

# 68. Transaction and Permission Changes

Permission changes are transactional.

Example:

```text id="txn048"
BEGIN
  ↓
Validate actor authority
  ↓
Validate target employee
  ↓
Update permission state
  ↓
Create audit
  ↓
Invalidate relevant authorization state
  ↓
COMMIT
```

If authorization cache invalidation is asynchronous, the committed database state remains authoritative.

---

# 69. Transaction and Device Revocation

Device revocation must be atomic with the authoritative device state and required audit event.

```text id="txn049"
BEGIN
  ↓
Set Device = REVOKED
  ↓
Audit
  ↓
Outbox if required
  ↓
COMMIT
```

Future authentication/synchronization checks use the new state.

---

# 70. Transaction and Employee Deactivation

Employee deactivation should atomically update the authoritative employee state and required audit information.

Session revocation may then be performed as part of the security workflow.

---

# 71. Transaction and Business Read-Only

Changing Business lifecycle to `READ_ONLY` must be atomic with required lifecycle audit/history.

After commit, modifying use cases must reject the Business.

---

# 72. Transaction and Business Deletion

Business deletion is a controlled lifecycle process.

It must not be one uncontrolled giant transaction for the entire Business.

Large deletion may be processed in bounded phases while maintaining:

* lifecycle state;
* deletion progress;
* idempotency;
* audit;
* recovery.

---

# 73. Deletion Transaction Example

```text id="txn050"
Mark Business DELETING
    ↓
COMMIT

Background Deletion Batch
    ↓
Delete eligible data
    ↓
Record progress
    ↓
COMMIT

Next Batch
    ↓
Continue
```

This avoids excessively long database transactions.

---

# 74. Transaction and Backup

Database backups operate independently from application transactions.

Backup consistency is provided by PostgreSQL/database backup mechanisms.

Application transactions must not wait for backup completion.

---

# 75. Transaction and Migration

Schema migrations must not be executed as part of ordinary request transactions.

Deployment migration strategy is defined separately.

Application code must remain compatible with supported migration phases.

---

# 76. Transaction Testing

Every important transactional use case should test:

* successful commit;
* validation failure;
* authorization failure;
* domain failure;
* database failure;
* rollback;
* duplicate request;
* concurrency;
* retry;
* audit persistence;
* Outbox persistence.

---

# 77. Atomicity Test

Example:

```text id="txn051"
Given:
    Order requires inventory A and B

When:
    A is sufficient
    B is insufficient

Then:
    Order is not accepted
    A is not deducted
    B is not deducted
    Order state is unchanged
```

---

# 78. Payment Idempotency Test

```text id="txn052"
Given:
    operation_id = X

When:
    same payment request is submitted twice

Then:
    exactly one Payment is created
    financial state changes once
    second request returns the existing result
```

---

# 79. Cash Session Concurrency Test

```text id="txn053"
Given:
    one Register
    no active Cash Session

When:
    two valid open requests arrive concurrently

Then:
    one request succeeds
    one request receives a conflict
    only one active Cash Session exists
```

---

# 80. Configuration Concurrency Test

```text id="txn054"
Given:
    configuration version = 10

Request A:
    expected version = 10

Request B:
    expected version = 10

Then:
    one creates version 11
    the other receives a conflict
    version 11 is not overwritten
```

---

# 81. Rollback Test

```text id="txn055"
Given:
    Order acceptance requires multiple writes

When:
    required persistence operation fails

Then:
    all core writes roll back
    no partial inventory deduction remains
    Order state remains consistent
```

---

# 82. Outbox Atomicity Test

```text id="txn056"
Given:
    business change requires an Outbox event

When:
    Outbox persistence fails

Then:
    core transaction rolls back
```

This applies only where the event is classified as required.

---

# 83. Transaction Invariants

1. Application Layer owns transaction boundaries.
2. Repositories do not silently commit.
3. Core business changes are atomic where required.
4. Required audit records are committed with the business change.
5. Required Outbox records are committed with the business change.
6. Secondary processing does not normally control core transaction success.
7. Transactions do not wait for user interaction.
8. Transactions do not depend on external network calls.
9. Transactions do not depend on printer availability.
10. Transactions do not generate large reports.
11. Transactions remain short.
12. Critical mutable state uses appropriate locking.
13. Configuration uses optimistic concurrency where appropriate.
14. Duplicate retryable operations use idempotency.
15. Database constraints protect important uniqueness rules.
16. Failed transactions are rolled back completely.
17. Broken sessions are not reused after transaction failure.
18. Deadlock retries use fresh transactions.
19. Retry loops are bounded.
20. Authorization is validated before protected modification.
21. Business lifecycle is validated before modification.
22. Offline synchronization creates authoritative state only after server validation.
23. Independent sync operations may partially succeed.
24. Dependent sync operations preserve dependency order.
25. Historical records are not silently mutated.
26. Cache does not determine transaction success.
27. Notification failure does not normally roll back core state.
28. File-generation failure does not normally roll back committed business state.
29. Business deletion uses bounded transactions.
30. Transaction behavior is observable and testable.

---

# 84. Recommended Transaction Structure

The preferred implementation pattern is:

```text id="txn057"
Application Use Case
        ↓
Unit of Work
        ↓
BEGIN
        ↓
Authorization / Scope already established
        ↓
Load / Lock
        ↓
Domain Validation
        ↓
Domain State Changes
        ↓
Repository Persistence
        ↓
Audit
        ↓
Outbox
        ↓
COMMIT
        ↓
Background Processing
```

---

# 85. Anti-Patterns

The following patterns are prohibited:

### Repository Commit

```text id="txn058"
repository.save()
repository.commit()
```

The repository must not own the use-case transaction.

### Network Inside Transaction

```text id="txn059"
BEGIN
call_external_api()
COMMIT
```

### Notification Inside Transaction

```text id="txn060"
BEGIN
save()
send_notification()
COMMIT
```

### Printer Inside Transaction

```text id="txn061"
BEGIN
accept_order()
wait_for_printer()
COMMIT
```

### Unbounded Transaction

```text id="txn062"
BEGIN
process_thousands_of_records_for_hours
COMMIT
```

Large workloads must use bounded batches where appropriate.

---

# 86. Transaction Architecture Summary

```text id="txn063"
                    ┌─────────────────────┐
                    │ Application Use Case│
                    └──────────┬──────────┘
                               │
                         Unit of Work
                               │
                            BEGIN
                               │
              ┌────────────────┼────────────────┐
              │                │                │
         Domain Logic     Repositories      Validation
              │                │                │
              └────────────────┼────────────────┘
                               │
                       Audit / Outbox
                               │
                            COMMIT
                               │
                  ┌────────────┴────────────┐
                  │                         │
          Background Jobs             Notifications
          Reports / Exports           Printing
```

The database transaction establishes authoritative state.

Background processing operates after successful commit.

---

# 87. Related Documents

### Backend

* `README.md`
* `01_Backend_Architecture.md`
* `02_Backend_Project_Structure.md`
* `03_Application_and_Use_Case_Layer.md`
* `04_Domain_Service_and_Business_Logic.md`
* `05_Repository_and_Data_Access.md`
* `06_Authentication_and_Authorization.md`
* `08_Error_Handling_and_Exception_Architecture.md`
* `09_Events_Outbox_and_Background_Jobs.md`
* `23_Backend_Concurrency_and_Idempotency.md`
* `24_Backend_Invariants_and_Guardrails.md`

### Database

* `../05_Database/02_Database_Architecture.md`
* `../05_Database/25_Database_Integrity_and_Constraints.md`
* `../05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `../05_Database/27_Database_Migrations_and_Change_Management.md`
* `../05_Database/28_Database_Backup_and_Recovery.md`

### System Analysis

* `../02_System_Analysis/07_POS_and_Order_System.md`
* `../02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `../02_System_Analysis/16_Inventory_Transaction_System.md`
* `../02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `../02_System_Analysis/22_Audit_and_History.md`
* `../02_System_Analysis/23_Offline_Operation.md`
* `../02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `../02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `../02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `../02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`

---

# 88. Status

**Primary Database:** PostgreSQL

**ORM:** SQLAlchemy

**Transaction Owner:** Application / Unit of Work

**Isolation:** PostgreSQL default unless stronger isolation is explicitly justified

**Concurrency:** Optimistic concurrency + targeted row locking

**Idempotency:** Required for retryable commands

**Audit:** Atomic with important business changes

**Outbox:** Atomic with required asynchronous events

**External Calls:** Outside core transactions

**Notifications:** Post-commit

**Printing:** Post-commit

**Reports:** Separate/background processing

**Business Deletion:** Bounded transactional batches

**Next Document:** `08_Error_Handling_and_Exception_Architecture.md`

