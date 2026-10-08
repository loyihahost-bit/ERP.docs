# API Idempotency and Concurrency

**Document ID:** API-10
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines idempotency and concurrency behavior for the FastFood ERP API.

The primary objectives are:

* prevent duplicate business effects caused by retries;
* protect financial operations from duplicate execution;
* safely handle concurrent requests;
* preserve historical integrity;
* support reliable offline synchronization;
* prevent stale configuration from overwriting newer state;
* provide deterministic behavior under network failures;
* preserve correctness when clients, workers or devices retry operations;
* keep concurrency controls compatible with POS performance requirements.

The API must remain safe when the same logical operation is submitted:

* more than once;
* concurrently;
* after a timeout;
* after a connection failure;
* from multiple trusted devices;
* through synchronization retries.

Idempotency and concurrency are related but distinct concerns.

**Idempotency answers:**

> What happens if the same operation is submitted again?

**Concurrency control answers:**

> What happens when multiple valid operations attempt to change the same state at the same time?

---

# 2. Scope

This document covers:

* operation UUIDs;
* idempotency keys;
* idempotency records;
* request fingerprinting;
* replay behavior;
* duplicate detection;
* financial operation protection;
* Order operations;
* Payment operations;
* Refund operations;
* Inventory operations;
* Cash Session operations;
* Configuration operations;
* offline synchronization;
* optimistic concurrency;
* pessimistic locking;
* database constraints;
* race conditions;
* transaction boundaries;
* uncertain commit outcomes;
* retry safety;
* concurrent requests;
* distributed workers;
* cache limitations;
* idempotency expiration;
* cleanup;
* observability;
* performance;
* failure recovery;
* API invariants.

This document does not redefine:

* authentication;
* authorization;
* general error codes;
* generic request validation;
* general transaction architecture.

Those concerns are defined by related architecture documents.

---

# 3. Core Principles

The architecture follows these principles:

1. Important state-changing operations must be retry-safe.
2. Operation UUIDs must uniquely identify logical operations.
3. The same operation must not create duplicate business effects.
4. Idempotency must be enforced server-side.
5. Client-generated identifiers are never sufficient authorization.
6. Idempotency must be scoped correctly.
7. Conflicting reuse of an operation UUID must be rejected.
8. Financial operations require the strongest duplicate protection.
9. Inventory operations must preserve stock correctness.
10. Cash operations must preserve financial correctness.
11. Configuration changes must reject stale versions.
12. Optimistic concurrency is preferred where conflicts are expected to be uncommon.
13. Database constraints remain authoritative for uniqueness.
14. Row locks are used only where required for correctness.
15. Redis or other caches cannot be the authoritative idempotency store.
16. Idempotency records and business effects must have a reliable transactional relationship.
17. Retry behavior must remain deterministic.
18. Unknown commit outcomes must be handled safely.
19. Historical records must never be overwritten to simplify retries.
20. Concurrency failures must be observable.
21. POS operations must remain performant.
22. Offline synchronization must use the same correctness principles.
23. Idempotency must not become an authorization bypass.
24. Concurrency protection must not depend solely on application memory.

---

# 4. Idempotency vs Concurrency

These mechanisms solve different problems.

### Idempotency

Protects against:

```text
Same logical operation
        ↓
Retry
        ↓
Duplicate request
        ↓
Same business effect
```

Example:

```text
Pay Order
Operation UUID = OP-123

Request 1 → Payment created
Request 2 → OP-123 already processed
```

The second request must not create another payment.

### Concurrency

Protects against:

```text
Operation A ─┐
             ├── Same state
Operation B ─┘
```

Example:

```text
Employee A closes Cash Session
Employee B closes same Cash Session
```

Only one valid state transition may succeed.

---

# 5. Operation UUID

Every retryable state-changing operation should have an Operation UUID.

Example:

```http
Idempotency-Key: 0192f8c0-...
```

The Operation UUID identifies the logical operation rather than the HTTP request.

It is separate from:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Order UUID;
* Payment UUID;
* Inventory Transaction UUID;
* Request ID.

---

# 6. Request ID vs Operation UUID

These identifiers must not be confused.

### Request ID

Identifies one HTTP request.

```text
Request 1 → REQ-A
Request 2 → REQ-B
```

### Operation UUID

Identifies one logical operation.

```text
Request 1 → OP-123
Request 2 → OP-123
```

Therefore:

```text
REQ-A ─┐
       ├── OP-123
REQ-B ─┘
```

Two HTTP requests may represent the same operation.

---

# 7. Operation Identity

An idempotency record should contain sufficient scope to uniquely identify the operation.

Conceptually:

```text
Business
Branch where applicable
Actor where required
Device where required
Operation Type
Operation UUID
```

The exact identity model may vary by operation.

The system must prevent accidental cross-scope reuse.

---

# 8. Idempotency Key Requirements

For protected operations, the API should require:

```http
Idempotency-Key: <UUID>
```

The key must:

* be syntactically valid;
* have bounded length;
* be associated with the request operation;
* remain stable during retries;
* not be regenerated for every retry.

A client must generate a new Operation UUID for a genuinely new operation.

---

# 9. Operation UUID Reuse

If the same Operation UUID is submitted again with the same logical request:

```text
Return original authoritative result
```

If the same Operation UUID is submitted with a materially different request:

```text
Reject as conflict
```

Example:

```text
Operation UUID = OP-123

First:
Pay 25,000

Retry:
Pay 25,000

→ Replay original result
```

But:

```text
Operation UUID = OP-123

First:
Pay 25,000

Second:
Pay 30,000

→ Conflict
```

---

# 10. Request Fingerprint

The server should calculate a deterministic fingerprint for idempotent operations.

The fingerprint may include:

```text
Operation Type
Resource Identifier
Normalized Request Payload
Business Scope
Branch Scope
Relevant Actor/Device Context
```

The fingerprint prevents accidental reuse of one Operation UUID for another operation.

Sensitive values must not be logged merely because they participate in the fingerprint.

---

# 11. Payload Normalization

Fingerprint calculation should operate on normalized input.

For example:

```text
{
  "amount": "25000.00"
}
```

and an equivalent representation must resolve consistently according to the API contract.

Normalization must happen after structural validation.

The fingerprint must not depend on irrelevant transport details such as:

* header ordering;
* JSON property ordering;
* whitespace;
* unrelated tracing headers.

---

# 12. Idempotency Record

The server should maintain an idempotency record containing sufficient information to determine operation state.

Conceptually:

```text
Operation UUID
Business UUID
Branch UUID
Operation Type
Resource UUID
Request Fingerprint
Status
Created At
Completed At
Result Reference
Response Metadata
```

The exact persisted representation belongs to the Database Architecture.

---

# 13. Idempotency States

Recommended logical states:

```text
RECEIVED
PROCESSING
COMPLETED
FAILED_RETRYABLE
FAILED_FINAL
```

The exact state model may be simplified by implementation.

The system must nevertheless distinguish:

* operation currently being processed;
* operation already completed;
* operation permanently rejected;
* operation safely retryable.

---

# 14. Idempotency State Ownership

The authoritative idempotency state must be persisted in durable server-side storage.

Application memory alone is insufficient.

Example:

```text
Application Instance A
       ↓
Idempotency Store

Application Instance B
       ↓
same Idempotency Store
```

This is required for horizontal scaling.

---

# 15. Database Authority

The authoritative relationship between:

```text
Idempotency
+
Business Effect
```

must ultimately be protected by PostgreSQL transactions and constraints.

Redis may be used for optimization or coordination, but not as the sole source of idempotency correctness.

---

# 16. Basic Idempotent Command Flow

Typical flow:

```text
Request
  ↓
Validate
  ↓
Authenticate / Authorize
  ↓
Determine Operation UUID
  ↓
Check Idempotency
  ↓
Create / Claim Operation
  ↓
Execute Application Use Case
  ↓
Commit Business Transaction
  ↓
Store authoritative result
  ↓
Return response
```

The exact implementation must ensure that concurrent requests cannot both successfully claim the same operation.

---

# 17. Atomic Operation Claim

Two concurrent requests using the same Operation UUID must not both enter business execution.

Example:

```text
Request A ─┐
           ├── Operation OP-123
Request B ─┘
```

Expected behavior:

```text
A → claims OP-123
B → sees OP-123 already processing/completed
```

The claim must be protected by an authoritative uniqueness mechanism.

---

# 18. Unique Constraint

The database should enforce uniqueness for the appropriate idempotency identity.

Conceptually:

```text
UNIQUE(
    business_id,
    operation_type,
    operation_uuid
)
```

Additional scope fields may be required depending on the operation.

Application-level checks alone are insufficient because two requests may pass the check simultaneously.

---

# 19. Concurrent Duplicate Requests

Example:

```text
Request A:
OP-100

Request B:
OP-100
```

Possible result:

```text
A → PROCESSING
B → DUPLICATE / WAIT / REPLAY
```

Only one request may execute the business effect.

The second request must never independently execute the same financial or inventory operation.

---

# 20. Replay Behavior

If an operation is already completed:

```text
Request
  ↓
Idempotency lookup
  ↓
COMPLETED
  ↓
Return original authoritative result
```

The system should avoid recomputing a different result from current configuration.

For financial operations, replay must refer to the original transaction result.

---

# 21. Replay and Historical Integrity

A replay must return the historical result associated with the original operation.

For example:

```text
Original Payment:
25,000

Current Order:
possibly different state

Replay:
returns original Payment result
```

Current Product prices, configuration or inventory state must not reinterpret the completed operation.

---

# 22. Idempotency and Financial Operations

The strongest idempotency guarantees apply to:

* payments;
* refunds;
* cash adjustments;
* cash session operations;
* inventory adjustments;
* inventory receipts/exits;
* other financial corrections.

Duplicate financial effects are release-blocking correctness failures.

---

# 23. Payment Idempotency

Payment requests must use an Operation UUID.

Example:

```text
POST /orders/{order_id}/payments

Idempotency-Key: OP-900
```

If the client retries after timeout:

```text
OP-900
```

must resolve to the original payment result.

A retry must never create a second payment.

---

# 24. Payment Concurrency

Two different operations may attempt to pay the same Order.

Example:

```text
OP-A → Pay Order
OP-B → Pay same Order
```

These are not idempotent duplicates because their Operation UUIDs differ.

Concurrency rules must ensure:

```text
One valid payment transition
```

wins according to the Order/payment business rules.

The second operation must receive an appropriate conflict or business-rule result.

---

# 25. Payment and Order State

Payment processing must validate authoritative Order state.

A cached Order state is insufficient.

The transaction must prevent:

```text
Request A → sees UNPAID
Request B → sees UNPAID

A pays
B also pays
```

without concurrency protection.

---

# 26. Refund Idempotency

Refund requests must use an Operation UUID.

Repeated submission of the same refund request must not create another refund.

Example:

```text
Refund OP-55
First → 10,000 refunded
Retry → original refund result
```

A different refund Operation UUID must be evaluated independently against remaining refundable amount.

---

# 27. Refund Concurrency

Two different refund operations against the same Order may race.

The system must ensure:

```text
Total Refund ≤ Authoritative Refundable Amount
```

This must be enforced transactionally.

Application-level pre-check alone is insufficient.

---

# 28. Inventory Idempotency

Inventory transactions must be idempotent.

Examples:

* receipt;
* exit;
* adjustment;
* production;
* recipe deduction;
* correction.

Retrying an inventory transaction must not deduct or add stock twice.

---

# 29. Inventory Concurrency

Two operations may simultaneously modify the same inventory item.

Example:

```text
Stock = 5

Order A requires 3
Order B requires 3
```

The system must not allow both operations to commit if that would produce invalid negative stock.

Authoritative inventory state must be checked transactionally.

---

# 30. Inventory Locking

Where required, inventory rows may be locked during the critical deduction operation.

Conceptually:

```text
BEGIN
  Lock Inventory Row
  Validate Quantity
  Deduct Quantity
  Create Inventory Transaction
COMMIT
```

The lock must remain limited to the smallest necessary transaction scope.

---

# 31. Cash Session Idempotency

Cash Session commands such as:

* open;
* close;
* correction;
* handover;

must be protected against duplicate execution.

Example:

```text
Close Session OP-700

Request 1 → closes
Request 2 → replay
```

The second request must not create another close event.

---

# 32. Cash Session Concurrency

Two employees must not independently close the same active Cash Session.

The authoritative Cash Session state must be checked transactionally.

Example:

```text
ACTIVE
   ↓
Close A → CLOSED
Close B → conflict
```

---

# 33. Shift Handover Concurrency

Handover operations must prevent:

* two incoming cashiers accepting the same handover;
* the same outgoing cashier creating conflicting transfers;
* duplicate cash transfer records.

The handover state transition must be atomic.

---

# 34. Order Concurrency

Orders may receive concurrent operations such as:

* add item;
* remove item;
* modify item;
* accept;
* cancel;
* pay;
* refund.

The system must distinguish:

```text
Same operation
→ idempotency

Different operations
→ concurrency rules
```

---

# 35. Open Order Updates

For mutable open Orders, optimistic concurrency may be preferred.

Example:

```json
{
  "order_id": "...",
  "version": 12
}
```

Request:

```http
If-Match: "12"
```

If current version is 13:

```text
409 Conflict
STALE_VERSION
```

The stale request must not silently overwrite version 13.

---

# 36. Order Item Concurrency

Two clients modifying the same Order should not silently overwrite each other.

Example:

```text
Client A → Order version 12
Client B → Order version 12

A → version 13
B → stale
```

B must refresh current state before applying another mutation.

---

# 37. Order Acceptance Concurrency

Order acceptance is a business command and must be protected against concurrent execution.

Potential race:

```text
Accept A
Accept B
```

Only one authoritative acceptance transition should occur.

Idempotency handles repeated A.

Concurrency rules handle independent B.

---

# 38. Configuration Concurrency

Configuration operations must use optimistic concurrency.

Examples:

* Product price;
* Branch price override;
* menu availability;
* category;
* Set configuration;
* Recipe configuration;
* Business settings.

A stale configuration update must not overwrite a newer configuration.

---

# 39. Configuration Version

A configuration resource should expose a version.

Example:

```json
{
  "id": "...",
  "version": 18
}
```

Update:

```http
If-Match: "18"
```

Current version:

```text
19
```

Result:

```text
409 CONFLICT
STALE_VERSION
```

---

# 40. Why Optimistic Concurrency

Optimistic concurrency is preferred for configuration because:

* concurrent edits are relatively uncommon;
* long locks would reduce usability;
* users can review current state before retrying;
* POS performance remains unaffected.

---

# 41. Pessimistic Locking

Pessimistic row locking should be used only when required by business correctness.

Good candidates include:

* inventory deduction;
* financial balance transitions;
* Cash Session state;
* payment state;
* refundable amount;
* tightly controlled counters.

Locks must not be used indiscriminately across large datasets.

---

# 42. Lock Scope

Locks should be:

* row-level where possible;
* acquired late;
* held briefly;
* released at transaction completion.

Long-running work must not occur while holding critical database locks.

---

# 43. Lock Ordering

When multiple rows must be locked, the application must use deterministic ordering.

Example:

```text
Lock Product A
Lock Product B
```

must use the same ordering for competing transactions.

This reduces deadlock probability.

---

# 44. Deadlocks

Deadlocks may still occur despite deterministic ordering.

The system must:

* detect database deadlock errors;
* rollback the affected transaction;
* retry only operations that are safe to retry;
* preserve idempotency;
* use bounded retry attempts.

A deadlock retry must not create duplicate business effects.

---

# 45. Retry After Deadlock

A safe pattern:

```text
Operation UUID = OP-123

Transaction A
   ↓
Deadlock
   ↓
Rollback
   ↓
Retry same OP-123
   ↓
Commit once
```

A new Operation UUID must not be generated for an automatic retry of the same logical operation.

---

# 46. Unique Constraints as Concurrency Protection

Database uniqueness constraints are important concurrency controls.

Examples:

* one active Cash Session where required;
* unique operation UUID;
* unique Business-scoped code;
* unique active device relationship;
* unique configuration identity;
* unique payment reference where applicable.

The application must handle uniqueness violations as controlled conflicts.

---

# 47. Database Constraints Are Final Authority

Application pre-check:

```text
Does record exist?
```

is not sufficient.

The authoritative database constraint must still protect against:

```text
Request A checks
Request B checks
A inserts
B inserts
```

The constraint prevents invalid duplication.

---

# 48. Check-Then-Act Race

Unsafe:

```text
Check stock
    ↓
Do other work
    ↓
Deduct stock
```

Another transaction may modify stock between the check and deduction.

Safe:

```text
Begin transaction
    ↓
Lock / atomic conditional update
    ↓
Validate
    ↓
Deduct
    ↓
Commit
```

---

# 49. Atomic Conditional Updates

Where appropriate, concurrency can use atomic database conditions.

Example conceptual operation:

```text
UPDATE inventory
SET quantity = quantity - :required
WHERE id = :id
  AND quantity >= :required
```

The affected row count determines whether the deduction succeeded.

The exact SQL implementation belongs to the repository/data-access layer.

---

# 50. Idempotency and Transactions

For core business commands, idempotency state and business effect must have a reliable relationship.

The system must avoid:

```text
Idempotency marked completed
       ↓
Business transaction rolled back
```

or:

```text
Business transaction committed
       ↓
Idempotency state lost
       ↓
Retry executes duplicate effect
```

The implementation must design for these failure windows.

---

# 51. Atomic Persistence

Where practical, the idempotency record and core business effect should be committed within the same authoritative transaction.

Example:

```text
BEGIN
  Claim Operation
  Execute Business Effect
  Store Result Reference
COMMIT
```

This gives PostgreSQL one authoritative commit boundary.

---

# 52. Long-Running Operations

Not every operation can remain inside one database transaction.

For asynchronous operations:

```text
Operation
   ↓
Persist durable job
   ↓
Return 202
   ↓
Worker processes operation
```

The job itself must remain idempotent.

Worker retries must reuse the same logical Operation UUID.

---

# 53. Async Job Idempotency

Example:

```text
Export Job OP-500

Worker A → processing
Worker B → duplicate delivery
```

Only one logical export result should be produced unless the business explicitly permits multiple outputs.

Worker execution must use durable job state and uniqueness protection.

---

# 54. Offline Synchronization

Offline synchronization relies heavily on idempotency.

Each local operation must contain:

```text
operation_id
device_id
employee_id
business_id
branch_id
operation_type
entity_id
payload
client_created_at
sequence
```

The server validates all fields against authoritative state.

---

# 55. Sync Retry

Example:

```text
Offline device
   ↓
OP-100
   ↓
Server processes
   ↓
Network failure before response
   ↓
Device retries OP-100
```

The server must recognize:

```text
OP-100 already processed
```

and return the original result.

The device must not create a new Operation UUID.

---

# 56. Synchronization and Concurrency

Offline operations can arrive concurrently from multiple devices.

Example:

```text
Device A → OP-A
Device B → OP-B
```

If both modify the same authoritative resource, normal concurrency rules apply.

Idempotency does not mean that two different offline operations are automatically compatible.

---

# 57. Sync Sequence

Client sequence numbers may assist ordering, but they do not replace server validation.

The server must determine whether an operation is:

* valid;
* stale;
* duplicate;
* conflicting;
* unauthorized;
* permanently invalid.

Client sequence numbers are metadata, not authority.

---

# 58. Stale Offline Configuration

An offline device may submit a transaction using an older valid configuration.

The server must evaluate the operation according to offline rules.

If the operation was authorized under a valid offline configuration:

* the original transaction snapshot must be preserved;
* current configuration must not rewrite it.

---

# 59. Subscription and Idempotency

If a Business becomes READ_ONLY or DELETED while a request is retried:

The server must evaluate current authorization and lifecycle state according to the applicable business rules.

A stale idempotency record must not be used as an authorization bypass.

Replay of an already committed historical operation may return its original result when policy allows, but a new business effect must not be created.

---

# 60. Idempotency and Authorization

Idempotency is not an authorization mechanism.

The server must perform appropriate authorization checks before allowing a new operation.

A client cannot obtain access to another Business's operation by guessing or reusing an Operation UUID.

---

# 61. Idempotency and Business Isolation

Operation UUIDs must be scoped so that:

```text
Business A
OP-123

Business B
OP-123
```

cannot accidentally collide.

Business isolation remains mandatory even when operation UUIDs are globally generated.

---

# 62. Idempotency and Branch Isolation

Branch-specific operations must retain Branch context.

Example:

```text
Branch A
OP-123

Branch B
OP-123
```

must not resolve to the wrong Branch operation.

The exact uniqueness scope depends on the operation model.

---

# 63. Idempotency and Device Context

Device identity may be included in operation context where required.

However:

```text
Device UUID ≠ Authorization
```

A revoked or unauthorized device cannot execute an operation merely because its Operation UUID is valid.

---

# 64. Operation UUID Lifetime

Idempotency records require a defined retention policy.

The retention period must be long enough to cover realistic:

* client retries;
* offline synchronization;
* network recovery;
* delayed worker execution.

Critical financial operations may require longer retention than temporary non-financial operations.

---

# 65. Idempotency TTL

Idempotency TTL must not be selected arbitrarily.

It should consider:

```text
Operation Type
Retry Window
Offline Window
Business Risk
Financial Importance
Storage Cost
```

Financial and synchronization operations require stronger retention guarantees.

---

# 66. Expired Operation UUID

After an idempotency record expires, the same Operation UUID may become ambiguous.

Therefore the API must define safe behavior.

Possible strategies:

* reject reuse;
* retain tombstone metadata;
* require a new operation;
* retain financial idempotency records longer.

The selected strategy must be explicit per operation class.

---

# 67. Tombstones

For highly sensitive operations, a lightweight tombstone may be retained after detailed result data expires.

Example:

```text
OP-123
→ permanently used
```

This prevents accidental reuse of an old Operation UUID.

Tombstone retention must follow the data lifecycle policy.

---

# 68. Idempotency Cleanup

Cleanup jobs must not remove active or required idempotency records.

Cleanup should be:

* bounded;
* asynchronous;
* observable;
* retry-safe.

Cleanup failure must not affect core business correctness.

---

# 69. Idempotency Storage Growth

Idempotency storage must remain bounded.

The system should use:

* retention policies;
* archival where appropriate;
* tombstones where necessary;
* partitioning/indexing if volume requires it.

Storage optimization must not reduce duplicate protection below required business guarantees.

---

# 70. Idempotency and Cache

A cache may accelerate idempotency lookup.

However:

```text
Redis
   ↓
Optimization

PostgreSQL
   ↓
Authority
```

A Redis eviction must not make an already-completed financial operation executable again.

---

# 71. Idempotency and Distributed Instances

Multiple backend instances must safely process requests.

Example:

```text
Client
  ├── Instance A
  └── Instance B
```

Both may receive the same Operation UUID.

Correctness must come from shared durable state and database constraints, not local process memory.

---

# 72. Idempotency and Load Balancing

Requests belonging to the same Operation UUID do not need sticky sessions.

Any healthy application instance must be able to resolve the operation through shared authoritative state.

This supports horizontal scaling.

---

# 73. Concurrent Same-Key Requests

When the same Operation UUID arrives concurrently, the system may:

* wait for the first operation to complete;
* return a processing response;
* return a conflict indicating processing;
* replay the completed result.

The exact behavior must be deterministic and documented.

The second request must never independently execute the operation.

---

# 74. Processing Timeout

If the first request is still processing and a retry arrives:

```text
OP-123 = PROCESSING
```

the retry must not assume failure merely because the original HTTP request timed out.

The backend must resolve operation state from durable storage.

---

# 75. Unknown Commit Outcome

A critical scenario:

```text
Client sends Payment
      ↓
Server commits payment
      ↓
Network connection fails
      ↓
Client receives no response
```

The client cannot know whether the payment succeeded.

The client must retry using the **same Operation UUID**.

The server then returns the authoritative original result.

---

# 76. Unknown Commit Outcome and Financial Safety

The client must never solve uncertain payment status by generating a new payment Operation UUID automatically.

Unsafe:

```text
Timeout
 ↓
New Operation UUID
 ↓
Second Payment
```

Safe:

```text
Timeout
 ↓
Retry same Operation UUID
 ↓
Resolve authoritative result
```

---

# 77. Response Persistence

For important idempotent operations, the server should persist enough result information to replay the authoritative response.

The result may be:

* resource reference;
* operation status;
* business result;
* stable response metadata.

The system should avoid storing unnecessarily large response bodies when a compact result reference is sufficient.

---

# 78. Idempotency and Audit

Important operations should connect:

```text
Operation UUID
Request ID
Audit Event
Business Transaction
```

This allows operators to reconstruct:

```text
Who
What
When
Where
Which device
Which operation
What result
```

The audit record remains immutable.

---

# 79. Idempotency Observability

Metrics should include:

```text
idempotency_new_operations
idempotency_replays
idempotency_conflicts
idempotency_processing_collisions
idempotency_expired_requests
idempotency_storage_errors
```

Metrics must remain low-cardinality.

Operation UUIDs must not be metric labels.

---

# 80. Concurrency Observability

Important concurrency metrics include:

```text
optimistic_conflict_count
lock_wait_duration
deadlock_count
transaction_retry_count
unique_constraint_conflict_count
financial_conflict_count
inventory_conflict_count
```

These metrics should be grouped by stable operation categories.

---

# 81. Logging

Logs may include:

```text
request_id
operation_id
operation_type
business_id
branch_id
employee_id
device_id
result
```

Sensitive payloads must not be logged unnecessarily.

Operation payloads should not be copied into logs merely for debugging.

---

# 82. Security Considerations

Idempotency and concurrency controls must not expose:

* another Business's operation state;
* another user's financial information;
* payment details;
* internal database identifiers unnecessarily;
* sensitive request payloads.

A replay response must still pass normal resource-access and security policy requirements.

---

# 83. Idempotency Error Semantics

Typical conditions include:

```text
DUPLICATE_OPERATION
IDEMPOTENCY_KEY_REUSED
IDEMPOTENCY_CONFLICT
OPERATION_IN_PROGRESS
STALE_VERSION
CONCURRENT_MODIFICATION
DEADLOCK_RETRY
```

The exact error registry is defined by:

`09_API_Error_Handling_and_Error_Codes.md`

This document defines when those conditions occur, not the complete error response format.

---

# 84. Client Retry Policy

Clients should retry only operations documented as retryable.

For state-changing operations:

```text
Retry
   ↓
Same Operation UUID
```

For a genuinely new operation:

```text
New Operation
   ↓
New Operation UUID
```

Clients must not generate a new key simply because an HTTP request failed.

---

# 85. Exponential Backoff

Automatic retries should use bounded backoff.

Example:

```text
Attempt 1
   ↓
short delay

Attempt 2
   ↓
longer delay

Attempt 3
   ↓
maximum delay
```

The exact backoff belongs to client/runtime configuration.

Infinite retries are prohibited.

---

# 86. Retryable vs Non-Retryable Operations

Examples:

### Retryable

* payment submission with idempotency;
* refund command with idempotency;
* inventory transaction;
* configuration update with version;
* synchronization operation;
* async job submission.

### Not Automatically Retryable

* stale configuration conflict;
* insufficient stock;
* inactive product;
* unauthorized operation;
* invalid request;
* permanently rejected refund.

A retry must not repeatedly submit an operation that requires user decision.

---

# 87. Concurrency and Configuration

Configuration changes must preserve version history.

Example:

```text
Version 10
   ↓
Employee A edits
   ↓
Version 11

Employee B edits stale Version 10
   ↓
Conflict
```

Employee B must not overwrite Version 11.

---

# 88. Concurrency and Historical Integrity

Concurrency resolution must never solve a conflict by:

* deleting history;
* overwriting historical values;
* modifying old Order snapshots;
* changing old Recipe Versions;
* changing old Set configurations;
* rewriting audit records.

Conflict resolution creates a new authoritative state.

---

# 89. Concurrency and Menu Pricing

Price changes may be concurrent with Order creation.

The system must respect:

* effective configuration;
* Cash Session boundary;
* Order Item price snapshot;
* configuration version.

An Order created under a valid configuration must retain its applicable historical price.

---

# 90. Concurrency and Cash Sessions

Cash Session operations must respect state transitions:

```text
OPEN
 ↓
ACTIVE
 ↓
CLOSING
 ↓
CLOSED
```

Only valid transitions may commit.

Concurrent requests attempting invalid transitions must be rejected.

---

# 91. Concurrency and Employee State

Employee deactivation may race with an API operation.

Authorization and employee status must be evaluated according to the security model.

A stale cached employee status must not indefinitely permit new protected operations.

Historical operations remain attributed to the original employee.

---

# 92. Concurrency and Device Trust

Device revocation may race with a request.

The authorization system remains authoritative.

Idempotency does not override device trust rules.

Historical already-committed operations remain immutable.

---

# 93. Transaction Boundary

Core state-changing operations should use one clear transaction boundary.

Typical:

```text
BEGIN
  Validate authoritative state
  Lock / version-check where required
  Apply business change
  Create audit
  Create outbox event
  Persist idempotency result
COMMIT
```

External side effects occur after the core transaction where possible.

---

# 94. External Side Effects

External operations such as:

* printing;
* notifications;
* email;
* file generation;

must not be allowed to create duplicate core business effects when retried.

The core business transaction is authoritative.

Secondary operations should have their own idempotency where necessary.

---

# 95. Outbox and Idempotency

Outbox records should have unique identities.

If the same business operation produces an outbox event, retries must not create duplicate authoritative event records.

The event may be delivered more than once externally, but consumers should also be designed for idempotency where appropriate.

---

# 96. Worker Concurrency

Background workers may receive the same job more than once.

Workers must protect execution using:

* durable job identity;
* idempotency;
* lease/claim mechanisms;
* database constraints;
* transaction state.

Worker concurrency must not create duplicate financial or business effects.

---

# 97. Exactly-Once Semantics

The system should distinguish logical exactly-once business effect from transport-level exactly-once delivery.

Network transport cannot guarantee that a request is delivered exactly once.

The architecture instead aims for:

> At-most-one authoritative business effect for the same logical Operation UUID.

This is achieved through durable idempotency and transactional correctness.

---

# 98. At-Least-Once Delivery

Offline synchronization and background jobs may use at-least-once delivery.

Therefore:

```text
Delivery may happen multiple times
```

but:

```text
Business effect must not be duplicated
```

Idempotency is therefore a fundamental requirement.

---

# 99. Idempotency and API Versioning

An Operation UUID must not silently execute a semantically different operation because the API version changes.

The idempotency record should retain sufficient operation/version context.

Example:

```text
API v1
OP-123
```

must not unexpectedly replay as a different semantic operation under another contract.

---

# 100. Idempotency and Request Contract Changes

If an Operation UUID is reused with a different payload or incompatible API semantics:

```text
Conflict
```

must be returned.

The server must not reinterpret the original operation using the new payload.

---

# 101. Concurrency and API Versioning

API version changes must preserve concurrency semantics unless explicitly documented otherwise.

For example:

```text
If-Match: "12"
```

must continue to mean the same versioning contract for a supported API version.

---

# 102. Performance

Idempotency and concurrency mechanisms must meet the following initial targets:

| Operation                               |   Target |
| --------------------------------------- | -------: |
| Idempotency lookup p95                  |  ≤ 50 ms |
| Idempotency claim p95                   |  ≤ 50 ms |
| Cached idempotency lookup p95           |  ≤ 20 ms |
| Optimistic version check p95            |  ≤ 50 ms |
| Normal lock acquisition p95             |  ≤ 50 ms |
| Known concurrency conflict response p95 | ≤ 100 ms |
| Core POS command p95                    | ≤ 500 ms |
| Normal authenticated API p95            | ≤ 300 ms |

These targets exclude unusual database outages and intentionally long-running asynchronous operations.

---

# 103. Performance Guardrails

The implementation must avoid:

* global application locks;
* long-lived database locks;
* unbounded retry loops;
* synchronous external calls inside core transactions;
* large idempotency payload storage;
* unbounded idempotency retention;
* Redis-only correctness;
* polling loops without limits.

---

# 104. Idempotency Storage Indexes

The database should provide efficient lookup paths for:

```text
Business
Operation UUID
Operation Type
Resource where applicable
Status
Created At
```

The exact index strategy belongs to:

`26_Database_Indexes_and_Query_Strategy.md`

---

# 105. Concurrency Indexes

Concurrency-sensitive operations require appropriate indexes so that:

* version checks remain fast;
* unique constraints remain efficient;
* row selection is targeted;
* lock scope remains narrow.

Poor indexing can convert a row-level operation into unnecessary contention.

---

# 106. Testing Strategy

Idempotency and concurrency require dedicated tests.

Tests must include:

### Duplicate Request

Same Operation UUID twice.

### Concurrent Duplicate

Same Operation UUID simultaneously.

### Conflicting Reuse

Same Operation UUID with different payload.

### Timeout Retry

Commit succeeds but response is lost.

### Deadlock Retry

Transaction is safely retried.

### Financial Race

Two payments for one Order.

### Refund Race

Two refunds against one refundable amount.

### Inventory Race

Two deductions competing for the same stock.

### Configuration Race

Two updates from the same stale version.

### Offline Retry

Same synchronization operation delivered multiple times.

### Cross-Business Isolation

Same Operation UUID across Businesses.

### Cross-Branch Isolation

Branch-scoped operation collisions.

---

# 107. Failure Injection Testing

The system should test failures at critical points:

```text
Before idempotency claim
After claim
Before business transaction
After business transaction
Before commit
After commit
Before response
After response generation
During cache access
During worker execution
```

The goal is to verify that no failure window produces duplicate authoritative effects.

---

# 108. Recovery Testing

Recovery tests must verify:

* retry after timeout;
* retry after network failure;
* retry after process restart;
* retry after worker restart;
* retry after Redis outage;
* retry after database connection interruption;
* retry after deadlock;
* synchronization after device reconnection.

---

# 109. Security Testing

Security tests must verify:

* Operation UUID cannot bypass authorization;
* cross-Business replay is rejected;
* cross-Branch replay is rejected;
* revoked employee cannot create new operations;
* revoked device cannot create new operations;
* READ_ONLY Business cannot create prohibited mutations;
* deleted Business cannot be resurrected through retry;
* sensitive replay results are not exposed to unauthorized actors.

---

# 110. Operational Recovery

If an operation remains in:

```text
PROCESSING
```

for longer than its allowed processing window, the system must have a controlled recovery strategy.

Possible approaches:

* verify business transaction state;
* mark operation failed safely;
* retry worker execution;
* reconcile against authoritative resource state.

The system must not simply mark the operation completed without evidence of the business effect.

---

# 111. Reconciliation

When idempotency state and business state appear inconsistent, reconciliation must compare against authoritative PostgreSQL state.

Example:

```text
Idempotency:
PROCESSING

Payment:
COMPLETED
```

The system may safely reconcile the operation as completed.

The opposite situation:

```text
Idempotency:
COMPLETED

Payment:
missing
```

requires investigation and must not blindly create another payment.

---

# 112. Manual Recovery

Privileged operational recovery may be required for exceptional inconsistencies.

Manual recovery must:

* require authorization;
* create an audit event;
* preserve original state;
* avoid deleting history;
* use a new correction/recovery operation;
* never silently rewrite the original operation.

---

# 113. Data Lifecycle

Idempotency data follows the platform data lifecycle policy.

Important financial operation evidence must be retained according to the applicable historical/audit requirements.

Temporary technical idempotency metadata may have shorter retention if safe.

Deletion must never remove information required to preserve financial or audit integrity.

---

# 114. Recommended Operation Classes

The implementation should classify operations:

### Class A — Critical Financial

Examples:

* Payment;
* Refund;
* Cash correction.

Requirements:

* durable idempotency;
* strong concurrency control;
* authoritative result replay;
* long retention;
* audit.

### Class B — Inventory / Operational

Examples:

* stock adjustment;
* receipt;
* exit;
* production.

Requirements:

* durable idempotency;
* transactional stock validation;
* audit where applicable.

### Class C — Configuration

Examples:

* price;
* menu;
* recipe configuration;
* settings.

Requirements:

* Operation UUID;
* optimistic version;
* audit;
* historical version.

### Class D — Administrative / Non-Critical

Examples:

* bounded preference changes;
* non-critical metadata updates.

Requirements may be lighter where business risk is low.

---

# 115. Recommended Idempotency Flow by Operation Class

```text
Critical Financial
    ↓
Durable Operation Claim
    ↓
Strong Transaction
    ↓
Business Effect
    ↓
Audit / Outbox
    ↓
Commit
    ↓
Authoritative Replay
```

```text
Configuration
    ↓
Validate Version
    ↓
Create New Configuration Version
    ↓
Audit
    ↓
Commit
```

```text
Offline Synchronization
    ↓
Operation UUID
    ↓
Validate Authorization
    ↓
Duplicate Detection
    ↓
Conflict / Apply
    ↓
Persist Result
```

---

# 116. API Client Requirements

API clients must:

* generate Operation UUIDs for retryable commands;
* persist Operation UUID until the operation is resolved;
* reuse the same Operation UUID after timeout;
* not generate a new key for an uncertain result;
* stop retrying permanent failures;
* handle conflict responses;
* refresh stale resources before retrying version conflicts;
* preserve synchronization operation IDs across reconnects.

---

# 117. POS Client Requirements

POS clients require special handling because network failure may occur during financial operations.

The POS must:

* preserve Operation UUID locally until authoritative result is known;
* never create duplicate payment attempts automatically;
* support safe retry;
* distinguish timeout from business rejection;
* display reconciliation state where necessary;
* maintain local transaction references for offline operations.

---

# 118. Offline Client Requirements

Offline clients must persist:

```text
Operation UUID
Operation Type
Entity UUID
Creation Time
Sequence
Payload
Sync Status
Retry Count
Last Error
```

The local queue must survive application restart.

Operation IDs must remain stable until synchronization reaches a terminal state.

---

# 119. Synchronization Terminal States

An offline operation may reach:

```text
ACCEPTED
ALREADY_PROCESSED
REJECTED
CONFLICT
INVALID
UNAUTHORIZED
```

Temporary failures remain retryable.

The client must not create a new Operation UUID for a temporary failure.

---

# 120. Conflict Resolution

A concurrency conflict must preserve both:

* the authoritative current state;
* the attempted operation context.

The system should provide enough information for the client or authorized employee to decide what to do next.

Silent last-write-wins is prohibited for important business configuration and financial state.

---

# 121. Last-Write-Wins Restriction

The following must not use silent last-write-wins:

* payment state;
* refund amount;
* inventory quantity;
* Cash Session state;
* configuration version;
* historical financial data;
* audit history.

Less critical UI preferences may use simpler strategies if explicitly approved.

---

# 122. Concurrency and Historical Snapshots

Historical snapshots are immutable.

Examples:

```text
Order Item Price Snapshot
Payment Snapshot
Refund Snapshot
Recipe Version
Set Version
Configuration Version
Report Version
```

Concurrency handling must create new state rather than mutate historical snapshots.

---

# 123. API and Database Responsibility

API:

* receives Operation UUID;
* validates structure;
* builds request context;
* invokes application use case.

Application:

* coordinates idempotency;
* transaction boundary;
* concurrency strategy.

Domain:

* enforces business invariants.

Repository:

* performs atomic database operations;
* constraints;
* locking;
* version checks.

Database:

* remains final authority for durable uniqueness and transactional state.

---

# 124. Architectural Guardrails

The following are prohibited:

* idempotency implemented only in frontend;
* idempotency implemented only in local memory;
* Redis-only idempotency;
* generating a new Operation UUID for every retry;
* using Request ID as idempotency key;
* trusting Operation UUID as authorization;
* silently overwriting stale configuration;
* using current price to resolve historical operations;
* relying on cached inventory for final deduction;
* relying on application pre-check alone for uniqueness;
* long database locks;
* infinite automatic retries;
* duplicate financial effects;
* marking an operation completed without authoritative evidence;
* deleting historical operations to resolve conflicts.

---

# 125. System Invariants

The following invariants apply to API Idempotency and Concurrency:

1. Every protected retryable operation has a stable Operation UUID.
2. Operation UUID is distinct from Request ID.
3. Request ID identifies an HTTP request.
4. Operation UUID identifies a logical operation.
5. Retrying an operation reuses the same Operation UUID.
6. A genuinely new operation receives a new Operation UUID.
7. Idempotency is enforced server-side.
8. Idempotency state is durable.
9. Application memory is not the authoritative idempotency store.
10. Redis is not the authoritative idempotency store.
11. Operation UUID reuse with identical logical input returns the original result.
12. Operation UUID reuse with conflicting input returns a conflict.
13. Duplicate financial operations cannot create duplicate financial effects.
14. Duplicate inventory operations cannot create duplicate inventory effects.
15. Duplicate Cash Session commands cannot create duplicate state transitions.
16. Duplicate synchronization operations cannot create duplicate business effects.
17. Idempotency does not replace authorization.
18. Operation UUID does not grant resource access.
19. Business scope is preserved during idempotency lookup.
20. Branch scope is preserved during idempotency lookup.
21. Device restrictions remain enforced during replay.
22. Employee status remains enforced for new operations.
23. Subscription restrictions remain enforced for new operations.
24. Deleted Businesses cannot be resurrected through retry.
25. Idempotency records are protected by authoritative uniqueness.
26. Concurrent requests with the same Operation UUID cannot execute the business effect twice.
27. Different Operation UUIDs represent potentially different operations.
28. Different operations require normal concurrency validation.
29. Payment concurrency prevents duplicate valid payment transitions.
30. Refund concurrency prevents total refunds exceeding the refundable amount.
31. Inventory concurrency prevents invalid negative stock.
32. Cash Session concurrency prevents invalid duplicate transitions.
33. Configuration concurrency prevents stale overwrites.
34. Optimistic concurrency uses a server-authoritative version.
35. Stale versions are rejected.
36. Important configuration conflicts are not resolved by silent last-write-wins.
37. Database uniqueness constraints remain authoritative.
38. Application pre-checks do not replace database constraints.
39. Critical row locks are limited to required transaction scope.
40. Multiple locks use deterministic ordering where possible.
41. Deadlocks are detected and safely retried where appropriate.
42. Deadlock retries reuse the same Operation UUID.
43. Automatic retry does not generate a new logical operation.
44. Infinite retries are prohibited.
45. Retryable failures use bounded backoff.
46. Permanent business failures are not blindly retried.
47. Unknown commit outcomes are resolved through the same Operation UUID.
48. Network timeout does not imply business rollback.
49. Network timeout does not justify a new financial Operation UUID.
50. Completed operations can be safely replayed.
51. Replay uses the original authoritative result.
52. Replay does not recalculate historical financial values from current configuration.
53. Historical Order prices remain immutable.
54. Historical Recipe Versions remain immutable.
55. Historical Set Versions remain immutable.
56. Historical Report Versions remain immutable.
57. Audit records remain immutable.
58. Idempotency and business effects have a reliable transactional relationship.
59. An operation cannot be marked completed without authoritative evidence.
60. An idempotency record cannot cause a business effect by itself.
61. Long-running operations use durable asynchronous job state.
62. Background workers are idempotent.
63. Duplicate worker delivery cannot create duplicate business effects.
64. Offline operations preserve stable Operation UUIDs.
65. Offline retries preserve the original Operation UUID.
66. Client sequence numbers do not override server authority.
67. Offline timestamps do not override server authority.
68. Offline configuration snapshots do not rewrite historical transactions.
69. Synchronization conflicts are explicit.
70. Synchronization does not use silent last-write-wins for important business state.
71. Idempotency retention is defined by operation risk.
72. Critical financial idempotency records have appropriate retention.
73. Idempotency cleanup cannot remove records required for correctness.
74. Expired idempotency keys cannot create ambiguous financial reuse.
75. Tombstones may be used for high-risk operation IDs.
76. Idempotency storage growth is bounded.
77. Idempotency lookup is indexed.
78. Concurrency-sensitive queries are indexed.
79. Lock scope remains narrow.
80. Core transactions remain short.
81. External side effects do not determine financial commit correctness.
82. Printer failure does not rollback committed business state.
83. Notification failure does not rollback committed business state.
84. Outbox events have stable identities.
85. Duplicate outbox delivery is safely handled.
86. Idempotency metrics do not use Operation UUID as high-cardinality labels.
87. Concurrency metrics use stable operation categories.
88. Sensitive payloads are not unnecessarily logged.
89. Cross-Business operation replay is prohibited.
90. Cross-Branch operation replay is prohibited where Branch-scoped.
91. Revoked devices cannot create new operations.
92. Revoked employees cannot create new protected operations.
93. Authorization state cannot be bypassed through replay.
94. Idempotency state does not become a security credential.
95. Financial duplicate prevention is a release-blocking correctness requirement.
96. Inventory correctness is a release-blocking requirement.
97. Historical integrity is a release-blocking requirement.
98. Concurrency conflicts are observable.
99. Recovery from uncertain state is deterministic and auditable.
100. Manual recovery creates a new controlled operation rather than silently rewriting history.
101. API version changes cannot silently change the meaning of an existing Operation UUID.
102. Operation fingerprints are based on normalized contract input.
103. Irrelevant transport metadata does not change an operation fingerprint.
104. Idempotency does not depend on sticky sessions.
105. Horizontal scaling does not weaken idempotency guarantees.
106. Cache failure does not disable duplicate protection.
107. PostgreSQL remains authoritative for durable business state.
108. PostgreSQL remains authoritative for durable uniqueness.
109. PostgreSQL remains authoritative for concurrency-critical state.
110. API, Application, Domain, Repository and Database responsibilities remain separated.
111. Concurrency protection must not bypass authorization.
112. Concurrency protection must not bypass Business isolation.
113. Concurrency protection must not bypass Branch isolation.
114. Idempotency must preserve the original business result.
115. A retry must never silently become a new business operation.
116. Correctness has priority over retry latency.
117. Financial operations receive the strongest idempotency guarantees.
118. POS retry behavior must remain understandable to operators.
119. Offline synchronization must remain safe under at-least-once delivery.
120. The system must preserve one authoritative business effect for one logical Operation UUID.

---

# 126. Related Documents

### API

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/04_Architecture/09_API/05_API_Resource_Model_and_Naming.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/08_API_Request_Validation_and_Response_Contracts.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/11_API_Pagination_Search_Filtering_and_Sorting.md`
* `docs/04_Architecture/09_API/12_API_CRUD_and_Command_Endpoint_Architecture.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/06_Backend_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Backend_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/08_Backend_Error_Handling_and_Exception_Architecture.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/02_Database_Architecture.md`
* `docs/04_Architecture/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/04_Architecture/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/04_Architecture/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/04_Architecture/05_Database/17_Shift_Handover_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/23_Configuration_Data_Model.md`
* `docs/04_Architecture/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/04_Architecture/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/11_Inventory_and_Warehouse.md`
* `docs/02_System_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 127. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `10_API_Idempotency_and_Concurrency.md`

**Previous Document:** `09_API_Error_Handling_and_Error_Codes.md`

**Next Document:** `11_API_Pagination_Search_Filtering_and_Sorting.md`

---

## Final Principle

> The API must treat retries as normal behavior, not exceptional behavior. One logical operation must produce one authoritative business effect, while concurrent independent operations must be resolved through explicit transactional and versioning rules.

