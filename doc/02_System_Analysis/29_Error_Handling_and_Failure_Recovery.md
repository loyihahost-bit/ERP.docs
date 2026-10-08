# Error Handling and Failure Recovery

**Document ID:** SA-29
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines how FastFood ERP detects, classifies, reports, handles, retries, rolls back, records, and recovers from system errors and operational failures.

The purpose is to ensure that:

* business data is not silently corrupted;
* financial and inventory operations remain consistent;
* users receive clear and actionable error messages;
* retryable failures can recover safely;
* non-retryable failures are not repeatedly retried;
* uncertain transaction results are handled safely;
* offline and synchronization failures do not create duplicate operations;
* background failures do not block normal POS operations;
* security-sensitive errors do not expose internal information;
* all important failures remain traceable through logs, audit records, UUIDs, and correlation identifiers.

Error handling is a system-wide concern and applies to online, offline, synchronized, background, administrative, and operational workflows.

---

## 2. Scope

This document covers:

1. Error classification
2. Error codes
3. User-facing errors
4. Internal errors
5. Validation failures
6. Authorization failures
7. Business rule failures
8. Tenant and Branch scope failures
9. Subscription and entitlement failures
10. Order failures
11. Payment failures
12. Inventory failures
13. Cash session failures
14. Debt and repayment failures
15. Refund and correction failures
16. Concurrency failures
17. Offline failures
18. Synchronization failures
19. Network failures
20. Database failures
21. Timeout handling
22. Deadlocks
23. Dependency failures
24. Background job failures
25. Printing failures
26. Notification failures
27. Report and export failures
28. Data deletion failures
29. Transaction rollback
30. Partial success
31. Retry policies
32. Idempotent recovery
33. Uncertain transaction results
34. Client recovery
35. Server recovery
36. Security and tampering failures
37. Error logging and observability
38. Audit requirements
39. Performance requirements
40. System invariants

---

# 3. Error Handling Principles

FastFood ERP follows these principles:

1. Core business data must remain consistent.
2. An operation must not appear successful when its core transaction failed.
3. An operation must not be executed twice because of a retry.
4. Error handling must not silently modify unrelated data.
5. Financial and inventory operations require stronger consistency than secondary operations.
6. Secondary failures must not unnecessarily roll back a successful core transaction.
7. Users must receive understandable messages.
8. Internal technical details must not be exposed to ordinary users.
9. Every important failure must be traceable.
10. Retry must depend on error classification.
11. Retry must be idempotent.
12. Uncertain transaction results must be resolved using transaction identity rather than blindly repeated.
13. Offline failures must preserve locally accepted transaction data where appropriate.
14. Synchronization failures must not silently discard queued operations.
15. Security failures must fail closed.
16. Recovery operations must themselves be auditable.
17. Error handling must not unnecessarily slow POS operations.
18. A failure in one Business or Branch must not affect another tenant.
19. Historical data must remain intact after failure.
20. Error handling must preserve the original business context.

---

# 4. Error Classification

Every system error must belong to a known error category.

The primary categories are:

| Category        | Description                                                |
| --------------- | ---------------------------------------------------------- |
| Validation      | Input or request data is invalid                           |
| Authentication  | User/device authentication failed                          |
| Authorization   | User lacks required permission                             |
| Scope           | Business or Branch context is invalid                      |
| Business Rule   | Operation violates a business rule                         |
| Subscription    | Operation is blocked by entitlement                        |
| Concurrency     | Current state changed concurrently                         |
| Conflict        | Local and server states cannot be automatically reconciled |
| Inventory       | Stock-related failure                                      |
| Payment         | Payment-related failure                                    |
| Cash            | Cash session/register failure                              |
| Debt            | Debt or repayment failure                                  |
| Refund          | Refund/correction failure                                  |
| Network         | Network connectivity failure                               |
| Timeout         | Operation exceeded allowed time                            |
| Database        | Database operation failed                                  |
| Dependency      | External/internal dependency failed                        |
| Synchronization | Sync operation failed                                      |
| Background Job  | Background processing failed                               |
| Printing        | Printer operation failed                                   |
| Notification    | Notification delivery failed                               |
| Reporting       | Report generation failed                                   |
| Export          | File/export operation failed                               |
| Lifecycle       | Entity lifecycle operation failed                          |
| Security        | Security validation or tampering detected                  |
| Storage         | Local or server storage failure                            |
| Internal        | Unexpected application error                               |

An error may contain both a primary category and a more specific error code.

---

# 5. Stable Error Codes

Every expected system error must have a stable machine-readable error code.

Examples:

```text
VALIDATION_INVALID_INPUT
AUTH_INVALID_CREDENTIALS
AUTH_DEVICE_NOT_TRUSTED
AUTH_PERMISSION_DENIED
SCOPE_INVALID_BUSINESS
SCOPE_INVALID_BRANCH
SUBSCRIPTION_FEATURE_DISABLED
SUBSCRIPTION_EXPIRED
ORDER_INVALID_STATE
ORDER_STOCK_INSUFFICIENT
ORDER_MODIFICATION_CONFLICT
PAYMENT_ALREADY_COMPLETED
PAYMENT_REMAINING_AMOUNT_EXCEEDED
INVENTORY_INSUFFICIENT_STOCK
INVENTORY_CONCURRENT_CHANGE
CASH_SESSION_ALREADY_OPEN
CASH_SESSION_ALREADY_CLOSED
CASH_SESSION_CORRECTION_LIMIT_REACHED
SYNC_CONFLICT
SYNC_DUPLICATE_TRANSACTION
SYNC_AUTHORIZATION_FAILED
NETWORK_UNAVAILABLE
REQUEST_TIMEOUT
DATABASE_TEMPORARY_FAILURE
BACKGROUND_JOB_FAILED
PRINTER_FAILED
REPORT_GENERATION_FAILED
DATA_DELETION_FAILED
SECURITY_TAMPERING_DETECTED
INTERNAL_UNEXPECTED_ERROR
```

Error codes must remain stable across compatible application versions.

Human-readable messages may change without changing the error code.

---

# 6. Error Response Structure

System-generated errors should contain a consistent response structure.

A logical error response contains:

```text
error_code
message
category
severity
retryable
correlation_id
transaction_uuid
entity_uuid
details
```

Not every field is required for every error.

Sensitive internal details must not be included in the user-facing response.

---

# 7. Correlation and Transaction Identity

Important operations must remain traceable through stable identifiers.

Depending on the operation, the system may use:

* Request ID
* Correlation ID
* Transaction UUID
* Event UUID
* Order UUID
* Payment UUID
* Cash Session UUID
* Conflict UUID
* Background Job UUID
* Report Version UUID
* Audit Event UUID

The same transaction identity must be retained during retries.

A retry must not generate a new logical transaction identity.

---

# 8. User-Facing and Internal Errors

The system separates:

### User-facing error

Explains what the user needs to know or do.

Example:

> Payment cannot be completed because the order has already been fully paid.

### Internal error

Contains technical information useful for logs and operators.

Example:

```text
DB_DEADLOCK
transaction=...
table=...
retry_count=...
database_error=...
```

Internal details must not normally be shown to operational users.

---

# 9. Error Severity

Errors may be classified by severity:

### Info

Operation completed with a non-critical condition.

### Warning

Operation requires attention but the system remains operational.

### Error

Requested operation failed.

### Critical

System or data integrity is at serious risk and administrative attention may be required.

Critical errors must not automatically mean that POS becomes unavailable.

---

# 10. Validation Errors

Validation must occur before expensive or irreversible operations whenever possible.

Validation failures include:

* required field missing;
* invalid quantity;
* invalid price;
* invalid date;
* invalid UUID;
* invalid status transition;
* invalid payment amount;
* invalid Branch;
* invalid employee;
* invalid permission;
* invalid configuration;
* invalid report period.

Validation errors are normally non-retryable until the request is corrected.

The system should identify the affected field or business object where practical.

---

# 11. Authentication Errors

Authentication failures include:

* invalid credentials;
* expired authentication;
* inactive employee;
* revoked device;
* untrusted device;
* invalid offline authorization;
* expired offline authorization;
* invalid authentication token.

Authentication failures must not reveal whether a sensitive account or credential exists when such disclosure would create a security risk.

---

# 12. Authorization Errors

Authorization errors occur when:

* employee lacks permission;
* role does not provide permission;
* employee override does not allow operation;
* Branch scope does not allow operation;
* subscription entitlement does not allow operation;
* employee is inactive;
* operation requires additional authorization.

Authorization must be evaluated server-side.

Frontend visibility is not an authorization mechanism.

---

# 13. Business and Branch Scope Errors

An operation must fail when its Business or Branch context is invalid.

Examples:

* entity belongs to another Business;
* employee is not assigned to the Branch;
* device belongs to another Business;
* Cash Session belongs to another Branch;
* order belongs to another Business;
* report scope is outside employee authority.

The system must fail closed.

Cross-tenant access must never be converted into an empty successful response merely to hide the existence of data.

---

# 14. Subscription and Entitlement Errors

Modification operations must fail when the required entitlement is unavailable.

Examples:

```text
SUBSCRIPTION_EXPIRED
SUBSCRIPTION_FEATURE_DISABLED
SUBSCRIPTION_BRANCH_LIMIT_REACHED
SUBSCRIPTION_EMPLOYEE_LIMIT_REACHED
SUBSCRIPTION_FEATURE_NOT_INCLUDED
```

Read-only access that remains permitted must continue to work.

The frontend may hide unavailable functions, but the server must enforce entitlement independently.

Offline authorization must also contain sufficient entitlement information to prevent offline bypass.

---

# 15. Order Errors

Order errors may include:

* invalid order state;
* stock insufficiency;
* table state conflict;
* invalid waiter context;
* unauthorized modification;
* paid order modification attempt;
* cancellation authorization failure;
* inactive product;
* equipment-broken product;
* invalid Set configuration;
* configuration version mismatch;
* duplicate order submission.

When order acceptance fails because inventory cannot be deducted, the order must not become Accepted.

---

# 16. Inventory Errors

Inventory-related failures include:

* insufficient stock;
* concurrent stock change;
* invalid inventory adjustment;
* unauthorized manual stock exit;
* invalid recipe;
* invalid product dependency;
* inventory correction conflict;
* offline stock conflict.

No negative stock may be created.

When inventory deduction is part of a core order transaction, a failure must cause the whole core transaction to fail.

---

# 17. Payment Errors

Payment errors include:

* order not payable;
* payment already completed;
* invalid amount;
* unauthorized payment;
* payment concurrency conflict;
* invalid payment method;
* duplicate payment;
* offline payment conflict;
* invalid remaining amount;
* invalid debt allocation.

Payment creation must be idempotent.

If the client does not know whether payment succeeded, it must query the original payment identity rather than automatically creating another payment.

---

# 18. Overpayment Errors

Overpayment is a valid business condition when explicitly confirmed.

If:

```text
received amount > remaining order amount
```

the system must request confirmation where required.

After confirmation:

* the original order amount is settled;
* excess is recorded as separate overpayment;
* overpayment belongs to Business/Branch;
* cashier attribution is retained;
* waiter attribution is retained when applicable;
* the overpayment is included in relevant reports.

The system must not silently convert the excess into debt or cashier incentive.

---

# 19. Cash Session Errors

Cash errors include:

* another active session already exists;
* session already closed;
* invalid opening amount;
* invalid physical count;
* unauthorized correction;
* correction limit reached;
* invalid handover;
* invalid cashier context;
* offline authorization failure.

A closed Cash Session must never be reopened as an active session.

A correction after closure must use the correction mechanism.

---

# 20. Debt Errors

Debt-related failures include:

* customer not found;
* invalid debt order;
* repayment exceeds outstanding debt;
* invalid allocation;
* duplicate repayment;
* concurrent balance change;
* unauthorized repayment;
* synchronization conflict.

Customer balance and debt-order allocation must be updated atomically.

---

# 21. Refund and Correction Errors

Refunds and corrections must fail when:

* permission is missing;
* mandatory reason is missing;
* payment/order state is incompatible;
* amount exceeds refundable amount;
* requested item or quantity is invalid;
* required approval is missing;
* correction chain is invalid.

A failed refund must not partially modify the original payment.

A failed correction must not modify the original immutable record.

---

# 22. Concurrency Errors

Concurrency errors occur when two operations attempt to modify the same logical state.

Examples:

* two users attempt to accept the same order;
* two transactions attempt to consume the last stock unit;
* two requests attempt to open a Cash Session;
* two payments attempt to settle the same remaining amount;
* configuration changes while an operation is using an older version.

The system must use the appropriate combination of:

* database transactions;
* row-level locking;
* optimistic version checks;
* unique constraints;
* atomic conditional updates;
* idempotency keys based on UUID identity.

---

# 23. Concurrency Failure Handling

A concurrency failure must return a deterministic result.

The system must not silently overwrite another successful operation.

Example:

```text
Request A → consumes last stock unit → SUCCESS

Request B → same stock unit → REJECTED
```

Request B must receive an appropriate stock/concurrency error.

The user may refresh or recreate the operation using current state.

---

# 24. Stale State and Version Mismatch

Client state may become outdated because another device changed the same entity.

Examples:

* old menu version;
* old price;
* old recipe;
* old employee permission;
* old order state;
* old Cash Session state.

The server must validate the current authoritative version before committing a protected modification.

A stale request must not overwrite a newer valid state.

---

# 25. Network Errors

Network failures include:

* no connection;
* temporary connection loss;
* DNS failure;
* connection reset;
* server unreachable;
* interrupted request;
* response lost after server processing.

For offline-eligible operations, the client may continue using the offline workflow.

For online-only operations, the user receives a network-related failure.

The system must distinguish:

```text
request definitely not sent
request sent but result unknown
request definitely rejected
request successfully completed
```

This distinction is critical for safe retry.

---

# 26. Timeout Handling

Timeout does not automatically mean transaction failure.

A timeout may indicate:

1. server did not receive the request;
2. server received but did not process it;
3. server processed it but response was lost;
4. server is still processing it.

Therefore, retry behavior must depend on transaction identity and operation idempotency.

For critical operations:

```text
Timeout
    ↓
Check original transaction identity
    ↓
Determine existing result
    ↓
Retry only if safe
```

The client must not blindly create a second payment, order, refund, or inventory transaction after timeout.

---

# 27. Uncertain Transaction Result

When the final result is unknown, the transaction enters an unresolved/unknown state until the system can determine its result.

The system should query by stable UUID where possible.

Examples:

* Payment UUID
* Order UUID
* Inventory transaction UUID
* Cash Session UUID
* Refund UUID

The same UUID must be used for recovery.

---

# 28. Database Errors

Database failures include:

* connection failure;
* transaction failure;
* constraint violation;
* deadlock;
* timeout;
* unavailable database;
* serialization failure;
* storage failure.

Expected temporary database errors may be retried according to retry policy.

Permanent business constraint violations must not be retried indefinitely.

---

# 29. Deadlock Handling

Database deadlocks may occur under concurrent operations.

The system should:

1. detect the deadlock;
2. roll back the affected transaction;
3. retry the transaction when safe;
4. preserve the original transaction identity;
5. limit retry attempts;
6. log the event.

Repeated deadlocks must trigger observability alerts.

---

# 30. Transaction Rollback

Core operations must use transaction boundaries that preserve business consistency.

For example:

```text
Accept Order
    ├── Validate Order
    ├── Validate Stock
    ├── Deduct Inventory
    └── Mark Order Accepted
```

If any core step fails:

```text
ROLLBACK
```

The order must not remain partially accepted.

---

# 31. Modification Rollback

Accepted order modification may include:

* quantity reduction;
* product removal;
* inventory return;
* new quantity calculation.

If the required inventory return fails, the complete modification must roll back.

The system must not leave:

```text
Order modified
+
Inventory not correctly adjusted
```

as a silent partial result.

---

# 32. Payment Transaction Boundaries

Payment core processing must protect financial consistency.

If payment creation fails:

* no successful payment record may be created;
* order remaining amount must remain correct;
* cash session totals must remain correct.

Secondary operations such as notification may fail independently without reversing a successful payment.

---

# 33. Secondary Operation Failures

Some operations are secondary to the core transaction.

Examples:

* kitchen printing;
* notification delivery;
* report generation;
* analytics update;
* background indexing;
* non-critical derived data.

A failure in a secondary operation must not automatically roll back a successful core business transaction.

Example:

```text
Order accepted
    ↓
Inventory deducted
    ↓
Kitchen printer fails
```

The order remains Accepted.

Printer state becomes:

```text
Pending / Failed / Retrying
```

and the system may retry printing.

---

# 34. Printing Failure

Printer failure must not roll back a successful ERP transaction.

The system records:

* printer UUID;
* branch;
* related order/ticket UUID;
* attempt number;
* failure reason;
* timestamp;
* current print state.

The system may retry according to the printing retry policy.

Repeated failure must remain visible to authorized users.

---

# 35. Notification Failure

Notification failure must not roll back the operation that generated the notification.

Example:

```text
Cash Session closed successfully
        ↓
Owner notification failed
```

The Cash Session remains closed.

The notification job is retried independently.

---

# 36. Report and Export Failure

Report generation may fail because of:

* database issue;
* timeout;
* background worker failure;
* invalid report definition;
* storage failure.

The report must be marked appropriately:

```text
Pending
→ Generating
→ Generated
```

or:

```text
Generating
→ Failed
```

Failed reports may be retried according to the background job policy.

A failed Excel export must not modify the underlying report version.

---

# 37. Background Job Failure

Background jobs must have independent failure handling.

A job may enter:

```text
Pending
→ Running
→ Completed
```

or:

```text
Running
→ Retrying
→ Failed
```

A worker crash must not silently lose the job.

Durable job state and recovery mechanisms are defined in:

`28_Background_Jobs_and_Recovery.md`

---

# 38. Synchronization Errors

Synchronization errors include:

* invalid event;
* duplicate event;
* authorization failure;
* expired offline authorization;
* Business mismatch;
* Branch mismatch;
* stale configuration;
* inventory conflict;
* payment conflict;
* cash conflict;
* order conflict;
* tampered event;
* server validation failure.

A sync failure must not silently delete the local queued event.

---

# 39. Sync Conflict Handling

A conflict must create an explicit Conflict record when automatic resolution is unsafe.

Conflict processing:

```text
Local Event
    ↓
Server Validation
    ↓
Conflict Detected
    ↓
Conflict Record
    ↓
Authorized Resolution
    ↓
Resolution Audit
```

Conflict resolution must include:

* Conflict UUID;
* affected entity;
* local state;
* server state;
* reason;
* resolver;
* timestamp;
* resolution result.

---

# 40. Offline Failure Handling

Offline operations must be treated as durable local transactions.

If an offline operation cannot immediately synchronize:

* retain it in the local queue;
* preserve its UUID;
* preserve its business context;
* preserve its employee/device context;
* preserve its original timestamp;
* retry when possible.

Local failure must not cause silent loss of an accepted offline transaction.

---

# 41. Offline Storage Failure

If encrypted local storage becomes unavailable or corrupted:

* the system must stop creating unsafe new offline transactions;
* the user must be informed;
* recovery must not invent missing transactions;
* unsynchronized transactions must remain identifiable where possible;
* server synchronization must be attempted only with valid retained transaction data.

---

# 42. Security and Tampering Errors

Security failures include:

* invalid signature;
* modified offline authorization;
* invalid event signature;
* replay attempt;
* clock rollback;
* device revocation;
* unauthorized Business context;
* unauthorized Branch context;
* suspicious request sequence.

Security-sensitive operations must fail closed.

A suspected tampered transaction must not be accepted merely because retrying it would be convenient.

---

# 43. Security Error Messages

Security failures must not reveal sensitive internal information.

For example, instead of exposing:

```text
Signature verification failed because key version 17 is invalid
```

the user may receive:

> This operation could not be verified. Please reconnect and try again.

Detailed security information remains available to authorized system operators through logs and audit records.

---

# 44. Retry Classification

Errors must be classified as:

### Non-Retryable

Examples:

* invalid input;
* permission denied;
* subscription feature disabled;
* insufficient stock;
* invalid order state;
* refund amount too large.

Retrying the same request without changing state will normally fail again.

### Retryable

Examples:

* temporary network failure;
* temporary database failure;
* worker unavailable;
* printer temporarily unavailable;
* notification delivery failure.

### Conditionally Retryable

Examples:

* timeout;
* deadlock;
* serialization failure;
* temporary dependency failure;
* synchronization conflict.

These require checking the transaction state before retry.

---

# 45. Retry Policy

Retries must be:

* bounded;
* idempotent;
* observable;
* context-aware;
* safe.

A retry must not continue indefinitely.

A generic background retry pattern may use:

```text
Immediate attempt
→ short delay
→ retry
→ increasing backoff
→ retry limit
→ Failed
```

Exact retry counts and delays may be configured by system policy.

Critical business transactions must not depend on unlimited retries.

---

# 46. Idempotent Retry

Every retryable operation must preserve its logical identity.

Example:

```text
Payment UUID = P-123
```

If the request is retried:

```text
Attempt 1 → P-123
Attempt 2 → P-123
Attempt 3 → P-123
```

The server must not create:

```text
P-123
P-124
P-125
```

for the same logical payment.

---

# 47. Duplicate Requests

Duplicate requests may occur because of:

* user double-click;
* network retry;
* application retry;
* background worker retry;
* sync retry;
* lost server response.

The system must use UUID-based idempotency and appropriate unique constraints.

A duplicate request should return the existing result where safe.

---

# 48. Partial Success

Core operations must avoid partial success whenever business consistency requires atomicity.

For example:

```text
Order Accepted
+
Inventory Deduction
```

must be atomic.

However, independent secondary operations may succeed or fail separately.

Example:

```text
Order Accepted = SUCCESS
Inventory = SUCCESS
Kitchen Print = FAILED
Notification = FAILED
```

This is a valid partial result because the secondary operations do not define whether the order itself was accepted.

---

# 49. Client Recovery

The client must provide appropriate recovery actions based on error type.

Examples:

### Validation

Correct the input.

### Permission

Contact an authorized user.

### Network

Retry or continue offline where supported.

### Conflict

Refresh state or resolve conflict.

### Timeout

Check transaction status before retry.

### Subscription

Reactivate or wait for authorized entitlement.

### Device Trust

Complete device verification online.

### Printer Failure

Retry printing or use another configured printer.

The client must not offer an unsafe retry action merely because an operation failed.

---

# 50. Server Recovery

The server must recover from:

* application restart;
* worker restart;
* database connection loss;
* network interruption;
* dependency failure;
* background job interruption.

Durable state must be used to determine what was completed before restart.

The server must not infer successful completion solely from process memory.

---

# 51. Recovery After Application Restart

After restart:

1. load durable transaction state;
2. recover unfinished background jobs;
3. recover retryable jobs;
4. preserve transaction identities;
5. continue safe synchronization;
6. restore observability state;
7. avoid duplicate execution.

POS must become operational as quickly as possible without sacrificing consistency.

---

# 52. Recovery After Worker Failure

If a worker stops while processing a job:

* job lease/heartbeat eventually expires;
* another worker may claim the job;
* job identity remains unchanged;
* already-completed work must not be repeated unsafely;
* idempotency must protect duplicate execution.

---

# 53. Recovery After Lost Response

A lost response is not equivalent to failed execution.

Example:

```text
Client → Server: Payment P-123
Server → Database: SUCCESS
Server → Client: response lost
```

The client must query:

```text
Payment UUID = P-123
```

before creating another payment.

The same principle applies to other idempotent operations.

---

# 54. Database Constraint Failures

Database constraints are an important final consistency boundary.

Examples:

* unique UUID violation;
* invalid foreign key;
* invalid state relation;
* invalid Business/Branch relation.

Expected constraint failures should be converted into deterministic application errors where possible.

Unexpected constraint failures must be logged as internal errors.

---

# 55. Dependency Failures

Internal or external dependencies may fail.

Examples:

* printer;
* notification service;
* storage;
* authentication provider;
* payment processor if introduced later;
* background worker.

Dependency failure must be isolated from unrelated core operations whenever possible.

---

# 56. External Payment Processor Boundary

If external card/payment processing is introduced later, the system must distinguish:

1. external authorization result;
2. ERP payment record;
3. synchronization/reconciliation state.

An uncertain external payment result must never automatically create a second charge.

This boundary must use provider transaction identity and ERP Payment UUID.

---

# 57. Error Logging

Errors must be logged with sufficient context for diagnosis.

Depending on sensitivity and operation, logs may contain:

* error code;
* category;
* severity;
* correlation ID;
* transaction UUID;
* entity UUID;
* Business UUID;
* Branch UUID;
* employee UUID;
* device UUID;
* Cash Session UUID;
* background Job UUID;
* timestamp;
* operation;
* retry count;
* failure source;
* recovery result.

Sensitive credentials, authentication secrets, payment secrets, and private security material must not be logged.

---

# 58. Audit vs Technical Logs

Technical logs and audit records have different purposes.

### Audit

Records business-significant actions and state changes.

### Technical logs

Record application behavior and failures useful for diagnosis.

A technical error does not automatically become a business audit event.

However, security-sensitive and business-significant failures may require both.

---

# 59. Error Audit Requirements

The following may require audit records:

* permission failure on sensitive operation;
* security/tampering event;
* conflict resolution;
* financial correction failure where business action was attempted;
* unauthorized administrative operation;
* device security event;
* subscription/deletion administrative action.

Routine validation errors do not necessarily require permanent business audit records.

---

# 60. Error Recovery Audit

When a failure is manually resolved, the resolution must be traceable.

Example:

```text
Original Error
    ↓
Recovery Action
    ↓
Authorized Employee
    ↓
Reason
    ↓
Timestamp
    ↓
Final Result
```

Recovery must not overwrite the original failure history.

---

# 61. User Messaging

User-facing messages should be:

* concise;
* understandable;
* actionable;
* non-technical where possible;
* localized according to supported language configuration;
* consistent for the same error code.

Example:

Bad:

> PostgreSQL serialization failure 40001.

Better:

> The data changed at the same time on another device. Refresh and try again.

Internal diagnostic information remains in logs.

---

# 62. Localization

Error messages should be separated from stable error codes.

The system may support multiple languages later without changing business logic.

Example:

```text
Error Code:
INVENTORY_INSUFFICIENT_STOCK
```

may have different localized messages.

The error code remains stable.

---

# 63. Error Message Safety

Messages must not reveal:

* passwords;
* authentication tokens;
* encryption keys;
* database credentials;
* internal SQL;
* stack traces;
* server paths;
* security configuration;
* sensitive tenant data;
* another Business's existence;
* another employee's private data.

Detailed diagnostics remain restricted to authorized operators.

---

# 64. Error Handling During POS Operations

POS operations have high performance priority.

Error handling must:

* fail quickly when validation is deterministic;
* avoid unnecessary network calls;
* avoid blocking UI on secondary operations;
* preserve transaction state;
* provide clear recovery actions;
* support offline operation where permitted.

A failed notification or printer operation must not freeze the POS.

---

# 65. Error Handling During Order Acceptance

Order acceptance follows:

```text
Validate
    ↓
Check authorization
    ↓
Check Business/Branch
    ↓
Check current configuration
    ↓
Check stock
    ↓
Atomic inventory deduction + acceptance
    ↓
Commit
    ↓
Secondary kitchen/notification processing
```

If any core validation or inventory operation fails:

```text
Order remains Draft
Inventory remains unchanged
```

unless another explicit operation already changed the state.

---

# 66. Error Handling During Payment

Payment processing follows:

```text
Validate payment
    ↓
Check authorization
    ↓
Check order state
    ↓
Check remaining amount
    ↓
Create Payment UUID
    ↓
Atomic financial update
    ↓
Commit
    ↓
Secondary reporting/notification
```

If the result is uncertain, the system resolves the original Payment UUID before retrying.

---

# 67. Error Handling During Cash Session Closure

Cash Session closure must:

1. validate session ownership and state;
2. validate authorization;
3. accept physical cash count;
4. calculate expected amount;
5. calculate difference;
6. persist closure atomically;
7. create required notifications/audit;
8. generate/report asynchronously where appropriate.

A failed notification must not reopen or invalidate a successfully closed Cash Session.

---

# 68. Error Handling During Handover

Handover must preserve session boundaries.

If handover fails:

* previous session remains in its previous valid state;
* new session is not partially created;
* open orders remain available according to existing state;
* cash must not be silently duplicated;
* previous session discrepancy remains attributed to the previous session.

If the new Cash Session is successfully created, a later notification failure must not roll it back.

---

# 69. Error Handling During Inventory Adjustment

Inventory adjustment must require:

* authorization;
* valid Branch;
* valid product;
* valid quantity;
* mandatory reason where required.

The adjustment must be atomic.

If persistence fails:

```text
Inventory quantity unchanged
Adjustment not finalized
```

---

# 70. Error Handling During Refund

Refund processing must validate:

* original payment;
* refundable amount;
* authorization;
* refund method;
* reason;
* Cash Session context where applicable.

If refund persistence fails:

* original payment remains unchanged;
* refund must not appear successful;
* no duplicate refund may be created during retry.

---

# 71. Error Handling During Reports

Reports must use the defined consistent snapshot model.

If report generation fails:

* no incomplete report version may be presented as final;
* failure is recorded;
* retry may be scheduled;
* original underlying transactional data remains unchanged.

---

# 72. Error Handling During Data Deletion

Data deletion is a background lifecycle operation.

If deletion partially fails:

* already completed deletion steps remain recorded;
* remaining work is retried safely;
* deleted data is not recreated;
* deletion job retains its identity;
* failure remains observable;
* retry is idempotent.

If reactivation wins before deletion starts or completes, the deletion process must stop according to the lifecycle rules.

---

# 73. Error Handling and Data Lifecycle

Expired Businesses may enter:

```text
Active
→ Expired / Read-Only
→ Deletion Eligible
→ Deleting
→ Deleted
```

Error handling must respect lifecycle state.

A stale offline operation must never resurrect a deleted Business.

---

# 74. Subscription Expiry Errors

When subscription expires:

* modifying operation is rejected;
* data viewing may remain available;
* permitted Excel exports remain available;
* existing orders and sessions are preserved;
* offline authorization cannot bypass expiry.

During the configured grace period, eligible renewal processing may continue according to subscription rules.

---

# 75. Employee Deactivation Errors

If an employee becomes inactive:

* new operations must be rejected;
* offline operations after the effective deactivation timestamp must not be accepted;
* previously completed operations remain historical;
* queued operations are validated during synchronization.

---

# 76. Device Revocation Errors

A revoked device must not receive new trusted authorization.

Offline operations already created before revocation are subject to server-side validation during synchronization.

The system must not use device revocation as a reason to silently delete valid historical transactions.

---

# 77. Recovery Priority

Recovery priority follows business impact.

Suggested priority:

1. Financial consistency
2. Inventory consistency
3. Order consistency
4. Cash consistency
5. Security integrity
6. Synchronization recovery
7. Reports
8. Notifications
9. Printing
10. Non-critical derived data

This does not mean lower-priority operations are ignored. They are processed independently without blocking critical POS operations.

---

# 78. Error Isolation

A failure in one area must not unnecessarily affect unrelated operations.

Examples:

```text
Printer failure
≠
POS failure
```

```text
Notification failure
≠
Cash Session rollback
```

```text
Report generation failure
≠
Order creation failure
```

```text
One Branch sync conflict
≠
Other Branch operations blocked
```

---

# 79. Tenant Isolation During Errors

Errors must preserve Business isolation.

A request from Business A must never expose:

* Business B's error details;
* Business B's entity identifiers where sensitive;
* Business B's transaction state;
* Business B's reports;
* Business B's audit information.

Background jobs and recovery workers must also preserve tenant context.

---

# 80. Error Handling in Background Processing

Background jobs must preserve:

* Business context;
* Branch context where applicable;
* actor context where required;
* transaction UUID;
* entity UUID;
* job UUID;
* retry count.

A background worker must not execute a job against a different Business because of missing context.

---

# 81. Error Handling in Synchronization

Synchronization must preserve:

```text
Business
Branch
Employee
Device
Transaction
Event
```

context.

An event that fails validation must remain identifiable.

Invalid events must not be transformed into successful events through retry.

---

# 82. Automatic vs Manual Recovery

### Automatic recovery

Suitable for:

* temporary network failures;
* temporary database failures;
* worker interruption;
* printer retry;
* notification retry;
* transient synchronization transport failure.

### Manual recovery

Required when:

* business conflict cannot be safely resolved;
* financial correction requires authorization;
* security tampering is detected;
* deletion requires administrative intervention;
* correction limits are exhausted;
* data integrity requires human review.

---

# 83. Recovery Must Be Explicit

Recovery must never silently change business meaning.

Examples:

* failed payment must not silently become debt;
* failed refund must not silently become discount;
* inventory conflict must not silently choose a quantity;
* cash shortage must not silently disappear;
* report correction must not overwrite previous version;
* deleted data must not silently reappear.

---

# 84. Error Recovery State

Where an operation requires asynchronous recovery, the system may maintain a recovery state.

Example:

```text
Pending
Processing
Retrying
Conflict
Resolved
Failed
```

The exact state model depends on the module.

Recovery state must not replace the authoritative business state.

---

# 85. Recovery and Historical Integrity

Recovery operations must preserve:

* original event;
* original transaction;
* original actor;
* original timestamp;
* original state;
* failure;
* recovery action;
* final result.

The system must not rewrite history to make a failure appear never to have happened.

---

# 86. Observability

The system should expose operational metrics for:

* error count;
* error rate;
* error category;
* error code;
* retry count;
* retry success rate;
* failed job count;
* sync conflict count;
* database deadlock count;
* timeout count;
* printer failure count;
* notification failure count;
* report failure count;
* deletion failure count;
* security event count.

Metrics should be grouped by Business/Branch only where appropriate and should preserve tenant isolation.

---

# 87. Error Correlation

Related errors should be connected using correlation identifiers.

Example:

```text
Order UUID
   ↓
Inventory Transaction UUID
   ↓
Kitchen Ticket UUID
   ↓
Notification Job UUID
   ↓
Audit Event UUID
```

This allows operators to reconstruct what happened without modifying the original records.

---

# 88. Error Monitoring

Repeated failures should be detectable.

Examples:

* repeated database deadlocks;
* repeated printer failures;
* repeated sync conflicts;
* repeated authorization failures;
* repeated security validation failures;
* repeated background job failures.

Monitoring should support operational investigation without adding significant load to POS operations.

---

# 89. Error Rate Limiting

Repeated requests that are clearly abusive or invalid may be rate-limited.

Rate limiting must not prevent legitimate POS recovery operations.

Security-sensitive endpoints may require stricter protection.

---

# 90. Error Handling and Performance

Error handling must be efficient.

The system should avoid:

* unnecessary database queries;
* unnecessary network calls;
* large synchronous logs;
* synchronous report generation;
* blocking notification delivery;
* blocking printer operations;
* repeated full-state synchronization.

Heavy diagnostics and recovery work should use background processing where safe.

---

# 91. Error Handling and Offline Performance

Offline operations must not depend on immediate server communication.

The local system should:

1. validate using available authorized local state;
2. create the transaction UUID;
3. persist the transaction;
4. enqueue synchronization;
5. continue POS operation.

Synchronization occurs independently.

---

# 92. Error Handling and Configuration Changes

If configuration changes while a device is offline:

* existing valid offline configuration may continue until synchronization;
* transaction processing uses the configuration version available to the authorized offline device;
* server validates the transaction on synchronization;
* configuration conflicts become explicit when automatic resolution is unsafe.

---

# 93. Error Handling and Report Versions

A report generation failure must not create a misleading final version.

A report version becomes final only after successful generation.

If relevant underlying data later changes:

```text
Previous Report Version
        ↓
New Report Version
```

The previous version remains immutable.

---

# 94. Error Handling and Notifications

Notification failure must not change the state that generated the notification.

Example:

```text
Inventory reaches low threshold
        ↓
Low-stock condition recorded
        ↓
Notification creation/delivery
        ↓
Delivery failure
```

The low-stock business condition remains valid.

---

# 95. Error Handling and Audit

Important errors and recovery actions must remain traceable.

Audit should answer:

* What failed?
* Which transaction was involved?
* Who initiated it?
* Which Business and Branch were involved?
* Which device was involved?
* Which Cash Session was involved?
* When did it happen?
* What recovery occurred?
* Who performed the recovery?
* What was the final result?

---

# 96. Error Handling and Security

Security failures must prioritize protection over convenience.

If authorization cannot be verified:

```text
REJECT
```

If offline signature cannot be verified:

```text
REJECT
```

If Business scope cannot be verified:

```text
REJECT
```

If transaction integrity cannot be verified:

```text
REJECT / CONFLICT
```

The system must not weaken validation simply to complete an operation.

---

# 97. Error Handling and API Consistency

API responses should use consistent error structures.

The same logical error should produce the same stable error code across:

* web application;
* POS;
* offline sync;
* background jobs;
* administrative interfaces.

Implementation-specific database or framework errors must be translated into domain-level errors when appropriate.

---

# 98. Error Handling and Frontend State

The frontend must not assume that a successful button click means successful server processing.

After a request:

```text
Loading
→ Success
```

or:

```text
Loading
→ Error
```

or:

```text
Loading
→ Unknown
→ Status Check
```

must be represented explicitly where necessary.

---

# 99. Error Handling and User Retry

Retry buttons should be shown only when retry is safe.

Examples:

### Safe

> Try again

for a temporary network failure.

### Unsafe without status check

> Pay again

after a payment timeout.

In the second case the UI should first verify the original payment state.

---

# 100. Error Handling and Double Actions

The UI should reduce accidental duplicate operations through:

* disabled duplicate submission while processing;
* clear processing state;
* idempotent backend operations;
* transaction UUID;
* deterministic duplicate handling.

UI protection is supplementary. Backend idempotency remains mandatory.

---

# 101. Error Recovery and Transaction Boundaries

Every important operation must have a defined transaction boundary.

At minimum:

### Order acceptance

Order + inventory deduction.

### Payment

Payment + relevant financial state.

### Cash session closure

Cash session closure + calculated financial state.

### Inventory adjustment

Inventory adjustment + stock quantity.

### Debt repayment

Repayment + debt allocation/balance.

### Refund

Refund financial state.

### Configuration change

Configuration version/state.

Secondary operations may execute outside these core transactions.

---

# 102. Error Handling and Atomicity

Atomicity is required when partial completion would violate business correctness.

The system must prefer:

```text
ALL CORE CHANGES
or
NO CORE CHANGES
```

rather than leaving partially applied core transactions.

---

# 103. Error Handling and Event Ordering

When an operation creates dependent events, event ordering must be preserved.

Example:

```text
Order Accepted
    ↓
Inventory Transaction
    ↓
Kitchen Event
    ↓
Notification
```

A dependent event must not be processed as successful if its required predecessor did not complete.

---

# 104. Error Handling and Idempotency

Idempotency must exist at every boundary where duplicate execution is possible.

Relevant boundaries include:

* API requests;
* offline transactions;
* synchronization;
* background jobs;
* printer jobs;
* notifications;
* report generation;
* Excel export;
* deletion jobs.

---

# 105. Error Handling and Recovery Testing

The system must test failure scenarios including:

* network loss;
* timeout;
* database restart;
* worker restart;
* deadlock;
* duplicate request;
* lost response;
* offline queue restart;
* sync conflict;
* stock race;
* payment race;
* Cash Session race;
* printer failure;
* notification failure;
* report failure;
* deletion failure;
* security tampering;
* device revocation;
* employee deactivation;
* subscription expiry.

---

# 106. Failure Injection

Development and testing environments should support controlled failure injection where practical.

Examples:

```text
Force network failure
Force database timeout
Force printer failure
Force worker crash
Force notification failure
Force sync conflict
```

This validates that recovery behavior is deterministic.

---

# 107. Error Recovery Acceptance Criteria

An error-handling implementation is considered acceptable when:

1. Core transactions cannot silently partially commit.
2. Duplicate retries cannot create duplicate financial operations.
3. Inventory cannot become negative.
4. Failed payments cannot silently modify order balances.
5. Closed Cash Sessions cannot reopen.
6. Offline transactions remain durable until synchronization is resolved.
7. Sync conflicts are explicit.
8. Background failures do not block POS.
9. Secondary failures do not roll back successful core transactions.
10. Security failures fail closed.
11. Errors are traceable.
12. Historical data remains intact.
13. Recovery actions are auditable.
14. Tenant isolation remains intact.
15. Error handling does not create unnecessary POS latency.

---

# 108. System Invariants

The following invariants are mandatory.

## Error Classification

1. Every expected error has a stable error code.
2. Error codes are machine-readable.
3. Error categories are deterministic.
4. Retryability is explicitly classified.
5. Unknown internal errors are not exposed as technical details to ordinary users.

## Security

6. Authorization failures fail closed.
7. Invalid Business scope is rejected.
8. Invalid Branch scope is rejected.
9. Invalid device trust is rejected.
10. Invalid offline authorization is rejected.
11. Tampered events are rejected or placed into conflict handling.
12. Security-sensitive information is not exposed in user messages.
13. Credentials and secrets are never written to ordinary logs.

## Transactions

14. Core operations are atomic where required.
15. Failed core transactions do not silently partially commit.
16. Rollback preserves business consistency.
17. Transaction UUID remains stable across retries.
18. Duplicate transaction identities cannot create duplicate operations.
19. Lost responses do not automatically create duplicate transactions.

## Orders

20. Failed order acceptance does not create an Accepted order.
21. Failed inventory deduction prevents order acceptance.
22. Failed accepted-order modification rolls back the complete modification when required.
23. Paid orders cannot be modified through ordinary edit operations.
24. Invalid lifecycle transitions are rejected.
25. Cancellation does not delete the original order.

## Inventory

26. Negative stock is never created.
27. Concurrent stock consumption is serialized or rejected safely.
28. Inventory conflicts are explicit.
29. Failed inventory adjustments do not change stock.
30. Inventory history remains traceable.

## Payments

31. Duplicate payment requests are idempotent.
32. A payment cannot exceed the allowed amount unless the overpayment rule explicitly permits it.
33. Confirmed overpayment is recorded separately.
34. Payment timeout does not automatically create a second payment.
35. Payment failure does not corrupt order balance.
36. Payment corrections preserve the original record.
37. Refunds are separate financial operations.

## Cash

38. Only one active primary Cash Session exists per Branch under the current model.
39. A closed Cash Session cannot become active again.
40. Cash Session correction does not rewrite original results.
41. Correction limits are enforced.
42. Handover preserves previous-session history.
43. Cash discrepancies remain attributed to the correct session.
44. Cash handling failures cannot silently duplicate physical cash.

## Debt

45. Debt repayment cannot exceed outstanding debt.
46. Debt allocation and balance updates are atomic.
47. Duplicate repayments are prevented.
48. Debt conflicts are explicit.

## Synchronization

49. Sync events retain their UUID.
50. Sync retries are idempotent.
51. Failed events are not silently deleted.
52. Duplicate events do not duplicate business operations.
53. Server validation remains authoritative.
54. Conflicts are explicitly represented.
55. Conflict resolution is authorized and audited.
56. Transaction events are processed before dependent configuration changes where required.

## Offline

57. Offline authorization cannot bypass subscription limits.
58. Offline authorization cannot bypass permissions.
59. Offline operations retain their original identity.
60. Local transaction persistence occurs before synchronization is attempted.
61. Offline failures do not silently discard accepted transactions.
62. Stale offline events cannot resurrect deleted data.
63. Device revocation is respected during server reconciliation.

## Background Jobs

64. Background jobs have durable identities.
65. Worker failure does not silently delete jobs.
66. Retry limits are enforced.
67. Duplicate jobs are prevented.
68. Job recovery is idempotent.
69. Failed jobs remain observable.
70. Background processing does not block normal POS operations unnecessarily.

## Printing and Notifications

71. Printer failure does not roll back a successful core transaction.
72. Notification failure does not roll back a successful core transaction.
73. Printer retries preserve ticket identity.
74. Notification retries preserve notification identity.

## Reports

75. Failed report generation does not create a misleading final version.
76. Report versions are immutable after finalization.
77. Report export failure does not modify the report version.
78. Report generation does not modify source business transactions.
79. Exact report versions remain recoverable according to lifecycle rules.

## Data Lifecycle

80. Deletion jobs are idempotent.
81. Partial deletion can resume safely.
82. Deletion failures remain observable.
83. Reactivation and deletion are resolved atomically.
84. Deleted Businesses cannot be resurrected by stale offline events.

## Audit

85. Important failures are traceable.
86. Recovery actions are traceable.
87. Original historical records are not overwritten to hide failures.
88. Audit records preserve actor and context.
89. Security-sensitive failures can be investigated.

## Tenant Isolation

90. Errors cannot expose another Business's data.
91. Background jobs preserve Business context.
92. Sync preserves Business and Branch context.
93. Error logs are protected from cross-tenant exposure.
94. Report errors cannot reveal another tenant's information.

## Performance

95. Error handling does not unnecessarily block POS.
96. Secondary failures are isolated from core operations.
97. Heavy recovery processing uses background execution where appropriate.
98. Retry loops are bounded.
99. Error logging does not create uncontrolled storage growth.
100. Failure recovery remains predictable under normal operational load.

---

# 109. Relationship With Other Documents

This document depends on and extends the following System Analysis documents:

* `01_System_Context_and_Boundaries.md`
* `03_Tenant_Business_and_Branch_Context.md`
* `04_Authentication_and_Authorization.md`
* `05_Employees_Roles_and_Permissions.md`
* `06_Device_Trust_and_Security_Context.md`
* `07_POS_and_Order_System.md`
* `08_Order_Lifecycle_and_Statuses.md`
* `09_Table_and_Waiter_Management.md`
* `11_Payment_System.md`
* `12_Debt_and_Payment_Allocation.md`
* `13_Discounts_Refunds_and_Corrections.md`
* `14_Cash_Register_and_Cash_Session.md`
* `15_Shift_Handover.md`
* `16_Inventory_Transaction_System.md`
* `17_Products_Recipes_and_Sets.md`
* `18_Menu_Pricing_and_Configuration.md`
* `19_Attendance_and_Payroll.md`
* `20_Reports_and_Report_Versioning.md`
* `21_Notifications_and_Alerts.md`
* `22_Audit_and_History.md`
* `23_Offline_Operation.md`
* `24_Synchronization_and_Conflict_Resolution.md`
* `25_Subscription_and_Entitlement.md`
* `26_Data_Lifecycle_and_Deletion.md`
* `27_System_Wide_Consistency_and_Concurrency.md`
* `28_Background_Jobs_and_Recovery.md`

This document provides the cross-cutting failure and recovery rules used by those modules.

---

# 110. Next Document

The next System Analysis document is:

`docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

That document will consolidate the final system-level invariants and rules across all System Analysis modules.

