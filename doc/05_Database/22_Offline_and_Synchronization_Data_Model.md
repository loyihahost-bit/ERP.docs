# Offline and Synchronization Data Model

**Document ID:** DB-22
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/01_Database_Overview.md`

## 1. Purpose

This document defines the database model required to support offline-first operation and synchronization between trusted branch devices and the authoritative server.

The model must support:

* trusted offline devices;
* offline authorization;
* offline transaction storage;
* durable synchronization queues;
* idempotent synchronization;
* dependency-aware synchronization;
* partial batch success;
* server-side validation;
* explicit conflict records;
* conflict resolution;
* synchronization retries;
* clock anomaly detection;
* configuration synchronization;
* audit and history synchronization;
* device revocation;
* employee deactivation;
* subscription expiry;
* Business and Branch isolation;
* recovery after application or device restart.

Offline operation must preserve the same business rules as online operation.

---

# 2. Core Principles

The synchronization model follows these principles:

1. The server is authoritative.
2. Offline devices may temporarily operate using explicitly authorized state.
3. Offline operation is available only to trusted devices.
4. A new device must be registered online before offline operation.
5. Every synchronized transaction has a permanent UUID.
6. No separate Client Transaction ID is required.
7. Synchronization is idempotent.
8. Duplicate synchronization must not duplicate business effects.
9. Synchronization must preserve Business and Branch isolation.
10. Dependencies must be synchronized before dependent transactions.
11. Configuration must not silently overwrite newer server configuration.
12. Conflicts must be explicit.
13. Conflicts must never be silently discarded.
14. Conflict resolution must be authorized and audited.
15. Failed synchronization must remain retryable.
16. Offline authorization must be time-bounded.
17. Server time is authoritative after reconnection.
18. Offline data must remain recoverable after application restart.
19. Synchronization must not block normal POS operation.
20. Historical records must preserve their original offline context.

---

# 3. Offline Architecture Context

Conceptually:

```text
Trusted Device
      |
      +-- Local Operational Store
      |
      +-- Sync Queue
      |
      +-- Offline Authorization
      |
      +-- Sync Engine
              |
              v
        Authoritative Server
              |
              +-- PostgreSQL
```

The local store is temporary operational state.

The server database remains authoritative.

---

# 4. Offline Eligibility

Only explicitly eligible operations may be executed offline.

Typical eligible operations include:

* order creation;
* order acceptance;
* inventory consumption;
* payment recording;
* debt repayment;
* cash session operations;
* shift handover;
* attendance;
* selected inventory operations;
* authorized configuration usage;
* selected payroll operations where explicitly supported.

The database model must not imply that every server operation is automatically available offline.

---

# 5. Trusted Device Requirement

Offline operations require a trusted device.

A device must have:

```text
Business
+
Branch
+
Device Identity
+
Employee Authorization
+
Offline Authorization
```

before offline operation is permitted.

Device trust is defined by the Device and Trust domain.

---

# 6. Offline Authorization

Offline authorization is a separate security artifact.

Conceptually:

```text
Offline Authorization
---------------------
id
business_id
branch_id
employee_id
device_id
issued_at
expires_at
authorization_version
status
signature
```

The exact cryptographic representation is defined by the security architecture.

The database stores the server-side authoritative metadata required for validation and revocation.

---

# 7. Offline Authorization Scope

Offline authorization must be bound to:

* Business;
* Branch;
* Employee;
* Device;
* effective permissions;
* subscription entitlement;
* authorization period.

A valid offline authorization for one Branch must not authorize another Branch.

---

# 8. Offline Grace Period

The current default offline authorization grace period is 3 days.

The exact expiration timestamp must be stored.

Conceptually:

```text
expires_at = issued_at + configured offline authorization period
```

The server may shorten or revoke authorization.

The device must not extend its own authorization.

---

# 9. Offline Authorization Revocation

Revocation may occur because of:

* device compromise;
* employee deactivation;
* permission removal;
* Branch access removal;
* Business subscription expiry;
* Business deletion;
* security incident.

The server must retain revocation state.

A device reconnecting after revocation must receive the latest authorization state.

---

# 10. Offline Transaction Identity

Every offline business transaction must have a permanent UUID.

Examples:

```text
Order UUID
Payment UUID
Inventory Transaction UUID
Attendance UUID
Cash Session UUID
Handover UUID
Debt Repayment UUID
```

The UUID is generated before synchronization.

The server must preserve the same UUID after synchronization.

---

# 11. No Client Transaction ID

The system does not introduce a separate Client Transaction ID.

The transaction UUID is sufficient for:

* identity;
* synchronization;
* idempotency;
* retry;
* reconciliation;
* audit.

The same UUID must never represent two different business transactions.

---

# 12. Sync Event Identity

Synchronization itself should have a separate event identity.

Conceptually:

```text
Sync Event
----------
id
transaction_id
device_id
business_id
branch_id
created_at
```

The Sync Event identifies the synchronization attempt or event.

The underlying business transaction retains its own UUID.

---

# 13. Sync Queue

Each trusted offline device maintains a durable synchronization queue.

Conceptually:

```text
Sync Queue
    |
    +-- Pending
    +-- Syncing
    +-- Synced
    +-- Retrying
    +-- Failed
    +-- Conflict
```

The local queue is durable across application restart.

---

# 14. Local Sync Queue vs Server Sync Record

The local queue exists on the device.

The server may maintain synchronization records for:

* idempotency;
* diagnostics;
* conflict tracking;
* security validation;
* reconciliation.

These are separate concerns.

The server must not assume that local queue state is authoritative.

---

# 15. Suggested Local Sync Record

Conceptual fields:

```text
id
transaction_id
transaction_type
business_id
branch_id
device_id
employee_id
sequence_number
dependency_ids
payload
payload_version
status
retry_count
last_attempt_at
next_retry_at
created_at
updated_at
```

The exact local schema depends on the selected local storage technology.

---

# 16. Server Sync Event Record

The server may store a synchronization record such as:

```text
sync_events
-------------
id
business_id
branch_id
device_id
employee_id
transaction_id
transaction_type
payload_version
received_at
processed_at
status
result_code
```

This provides server-side observability and reconciliation.

---

# 17. Sync Event Status

Suggested server states:

```text
RECEIVED
VALIDATING
APPLIED
DUPLICATE
REJECTED
CONFLICT
FAILED
```

The exact status model may evolve.

A status must clearly distinguish:

* successfully applied;
* already applied;
* rejected;
* conflict;
* infrastructure failure.

---

# 18. Transaction Status vs Sync Status

These must remain separate.

Example:

```text
Order
status = ACCEPTED

Sync
status = RETRYING
```

This means the local transaction is accepted locally but has not yet been successfully synchronized.

The application must not confuse business state with transport state.

---

# 19. Sync Payload

A synchronization payload should contain enough information for server validation.

Conceptually:

```text
transaction_id
transaction_type
business_id
branch_id
employee_id
device_id
cash_session_id
created_at_client
client_sequence
payload_version
payload
signature
```

Not every transaction requires every field.

---

# 20. Server Authority

When a synchronization event reaches the server, the server validates:

* Business;
* Branch;
* Device;
* Employee;
* permission;
* subscription;
* offline authorization;
* transaction identity;
* transaction version;
* configuration version;
* dependencies;
* business rules;
* inventory;
* financial state;
* concurrency.

The client cannot override server validation.

---

# 21. Business Isolation

Every synchronization event must belong to exactly one Business.

The server must reject events where:

```text
event.business_id
```

does not match the authenticated/trusted device context.

Cross-Business synchronization is prohibited.

---

# 22. Branch Isolation

Branch context must be validated independently from Business context.

An employee authorized for Branch A cannot synchronize a transaction for Branch B unless the employee and device are explicitly authorized for Branch B.

---

# 23. Employee Validation

The server validates the employee associated with an offline transaction.

Validation includes:

* employee exists;
* employee belongs to Business;
* employee was authorized for Branch;
* employee was active when appropriate;
* required permission existed;
* offline authorization was valid.

---

# 24. Device Validation

The server validates:

* Device UUID;
* Business;
* Branch;
* trust status;
* revocation status;
* device authorization;
* security state.

A revoked device cannot submit new authoritative offline operations.

---

# 25. Subscription Validation

The server validates subscription state during synchronization.

Offline authorization may permit temporary operation, but synchronization cannot bypass subscription rules.

If an operation was created during an authorized offline period, the server applies the defined historical/offline validation policy.

New unauthorized offline activity must be rejected.

---

# 26. Permission Validation

The server must validate the permission applicable to the transaction.

Offline permission state is a cached authorization snapshot.

It is not permanently authoritative.

After reconnection, the server determines whether the transaction was valid under the applicable offline authorization and policy.

---

# 27. Configuration Version

Offline transactions may reference a configuration version.

Examples:

* menu version;
* price version;
* recipe version;
* Set version;
* branch configuration version.

The server validates whether the referenced configuration was valid for the transaction timestamp.

---

# 28. Configuration Sync Ordering

Configuration synchronization should occur before dependent operational transactions when the server requires current configuration.

However, historical transactions may reference older valid configuration versions.

The system must not force a newer configuration onto an already-authorized historical transaction.

---

# 29. Transaction Synchronization Ordering

Synchronization should generally follow dependency order:

```text
Configuration
    ↓
Master Data
    ↓
Cash Session / Context
    ↓
Order
    ↓
Inventory Consumption
    ↓
Payment
    ↓
Secondary Events
```

The exact dependency graph depends on transaction type.

The server must validate dependencies explicitly rather than relying only on client ordering.

---

# 30. Dependency Identity

A sync record may contain dependency references.

Conceptually:

```text
dependency_ids[]
```

Examples:

```text
Payment
    → Order

Inventory Consumption
    → Order

Shift Handover
    → Previous Cash Session
```

A transaction with missing mandatory dependencies must remain pending or be rejected according to the conflict policy.

---

# 31. Client Sequence

A trusted device may maintain a monotonically increasing local sequence number.

Example:

```text
1
2
3
4
```

This assists with:

* ordering;
* diagnostics;
* missing-event detection.

Sequence numbers do not replace UUID identity.

---

# 32. Sequence Number Rules

A sequence number:

* belongs to one Device;
* should not be reused;
* must not be treated as globally unique;
* must not replace the transaction UUID.

Gaps may indicate:

* deleted local drafts;
* failed operations;
* device restart;
* queue cleanup;
* security anomalies.

A gap is not automatically a synchronization failure.

---

# 33. Idempotent Synchronization

The server must support repeated submission of the same transaction UUID.

Example:

```text
Device
  → transaction 123
  → timeout
  → transaction 123 again
```

The second request must not create a second business effect.

---

# 34. Idempotency Storage

The server may maintain unique identity records for synchronized transactions.

Conceptually:

```text
UNIQUE(transaction_id)
```

within the appropriate global or Business scope.

The transaction UUID must map to one authoritative business transaction.

---

# 35. Lost Server Response

A client may successfully submit a transaction but lose the server response.

The client then retries.

The server must return the existing transaction result instead of applying the transaction again.

This is a core synchronization requirement.

---

# 36. Partial Batch Success

A synchronization request may contain multiple events.

The server may process them independently when dependencies allow.

Example:

```text
Event 1 → APPLIED
Event 2 → CONFLICT
Event 3 → APPLIED
Event 4 → RETRY
```

The client must preserve unresolved events.

One failed event must not automatically invalidate unrelated successfully processed events.

---

# 37. Sync Batch Size

The initial recommended batch size is approximately:

```text
50–100 events
```

The exact size should remain configurable.

The database model must not depend on one fixed batch size.

---

# 38. Sync Retry

Retryable failures include:

* temporary network failure;
* database unavailability;
* worker failure;
* timeout;
* temporary resource exhaustion.

Retry must use bounded backoff.

Permanent validation failures must not be retried indefinitely.

---

# 39. Retry Metadata

Suggested fields:

```text
retry_count
last_attempt_at
next_retry_at
last_error_code
last_error_message
```

Sensitive server details must not be exposed to ordinary users.

---

# 40. Failed Synchronization

A permanently failed synchronization event must remain traceable.

Suggested state:

```text
FAILED
```

The system should preserve:

* original transaction UUID;
* failure reason;
* attempts;
* timestamps;
* device;
* employee;
* Business;
* Branch.

Authorized users may inspect the failure.

---

# 41. Conflict Identity

Every unresolved conflict should have a permanent UUID.

Conceptually:

```text
Sync Conflict
-------------
id
business_id
branch_id
transaction_id
device_id
conflict_type
status
created_at
resolved_at
resolved_by
resolution_reason
```

---

# 42. Conflict Lifecycle

Suggested lifecycle:

```text
OPEN
    ↓
UNDER_REVIEW
    ↓
RESOLVED
```

Exceptional states:

```text
REJECTED
CANCELLED
```

A resolved conflict must preserve its history.

---

# 43. Conflict Types

Possible conflict types include:

```text
AUTHORIZATION
SUBSCRIPTION
CONFIGURATION
INVENTORY
PAYMENT
ORDER_STATE
CASH_SESSION
TABLE
EMPLOYEE
DEVICE
DUPLICATE
DEPENDENCY
VERSION
CLOCK
SECURITY
```

New conflict types may be added.

---

# 44. Inventory Conflict

Example:

```text
Device A offline:
Stock = 1
Sale = 1

Device B online:
Stock = 1
Sale = 1
```

Both transactions cannot necessarily consume the same unit.

The server must serialize authoritative inventory effects.

The losing transaction becomes a conflict or rejection according to the defined policy.

---

# 45. Payment Conflict

Example:

```text
Offline Device:
Remaining Order = 100

Online Server:
Order already fully paid
```

The server must not create another valid payment silently.

The synchronization result becomes a conflict or rejection.

---

# 46. Cash Session Conflict

A device may continue operating offline while another authorized device changes the Cash Session state.

The server must validate:

* Cash Register;
* Cash Session;
* session lifecycle;
* employee;
* transition;
* transaction timestamp;
* synchronization ordering.

Invalid state transitions must not be silently accepted.

---

# 47. Handover Conflict

A handover must reference the correct previous and new Cash Sessions.

If another handover has already occurred, the stale offline handover must become a conflict.

The server must never create two authoritative successor sessions from the same closed session unless explicitly allowed.

---

# 48. Order Conflict

Offline order synchronization may conflict with server state.

Examples:

* table became unavailable;
* product became inactive;
* price version became invalid;
* stock became insufficient;
* employee permission was revoked;
* subscription expired.

The server must evaluate each rule explicitly.

---

# 49. Table Conflict

Two offline devices may assign the same table.

The server must determine the authoritative first valid assignment according to transaction ordering.

The losing operation becomes a conflict.

No silent overwrite is allowed.

---

# 50. Configuration Conflict

A device may operate using an older configuration version.

If the configuration was valid when the offline transaction occurred, the transaction may remain valid.

If the configuration was already invalid or revoked, the server must reject or conflict according to the applicable rule.

---

# 51. Employee Deactivation Conflict

If an employee becomes inactive while a device is offline, synchronization must verify the transaction timestamp and offline authorization.

An operation performed during a valid authorization period may be handled according to historical validation policy.

A transaction created after the employee's authorization was revoked must not become valid merely because it exists locally.

---

# 52. Device Revocation Conflict

A device revoked while offline cannot create new authoritative operations after the revocation boundary.

The server must use server-side revocation state.

Device-local state cannot override revocation.

---

# 53. Clock Rollback Detection

Offline operation requires clock anomaly protection.

The server and device should track:

```text
last_known_server_time
last_known_device_time
```

Suspicious rollback must be detected.

Examples:

* device time moves substantially backward;
* transaction timestamp precedes known authorized boundary;
* offline authorization appears to extend beyond its expiration.

Suspicious events may become security conflicts.

---

# 54. Server Time Authority

After synchronization:

```text
server_received_at
server_processed_at
```

are authoritative server timestamps.

Client timestamps remain useful for historical context and diagnostics.

They must not override server lifecycle decisions.

---

# 55. Offline Event Signature

Where required by the security architecture, offline transactions may contain a cryptographic signature.

Conceptually:

```text
signature
signature_version
```

The server validates authenticity before applying the event.

Invalid signatures must be rejected.

---

# 56. Tampered Payload

If a payload signature or integrity check fails:

```text
SECURITY
```

conflict/rejection must be recorded.

The server must not partially apply the transaction.

---

# 57. Local Storage Durability

Offline transactions must be written to durable local storage before the UI reports them as safely queued.

A memory-only queue is insufficient.

Application restart must not silently lose accepted offline transactions.

---

# 58. Local Transaction Atomicity

Creating an offline transaction and adding its sync event should be atomic locally.

Conceptually:

```text
BEGIN
    save transaction
    save sync event
COMMIT
```

If the operation fails, neither should appear as successfully queued.

---

# 59. Local Queue Recovery

After application restart:

1. load pending transactions;
2. validate local integrity;
3. restore dependency state;
4. resume synchronization;
5. preserve unresolved conflicts.

Already-synced events must not be applied again.

---

# 60. Device Storage Failure

If local storage becomes unavailable or corrupted:

* new offline transactions may be blocked;
* existing recoverable data should be preserved where possible;
* the user should receive a clear error;
* the server must not assume missing local events were successfully synchronized.

Storage failure must not cause fabricated synchronization success.

---

# 61. Reinstallation

Reinstalling the application may remove local offline state.

A new installation must not automatically assume that unsynchronized transactions are synchronized.

The device must re-authenticate and re-establish trusted state.

If recoverable local backup exists, recovery must preserve transaction UUIDs.

---

# 62. Device Replacement

A replacement device receives a new Device UUID.

The old Device UUID must not be reused.

The replacement device must complete online registration/trust before offline operation.

---

# 63. Multi-Device Synchronization

Multiple trusted devices may operate within one Branch.

The server must coordinate:

* orders;
* payments;
* inventory;
* tables;
* cash sessions;
* handovers;
* configuration;
* permissions.

Device-local state cannot override server concurrency control.

---

# 64. Local Concurrent Operations

Two local operations on the same device must be serialized where business ordering matters.

For example:

```text
Order Accepted
    ↓
Payment
```

The payment should depend on the local accepted order state.

The sync queue must preserve this dependency.

---

# 65. Server Concurrency

After synchronization, normal database concurrency controls apply.

Examples:

* row locking;
* unique constraints;
* optimistic version checks;
* transaction isolation;
* state validation.

Offline origin does not bypass server concurrency.

---

# 66. Synchronization of Orders

Order synchronization must preserve:

* Order UUID;
* Business;
* Branch;
* employee;
* device;
* Cash Session;
* order type;
* table context;
* configuration snapshots;
* item snapshots;
* operational status;
* creation context.

The server validates inventory and current authoritative state.

---

# 67. Synchronization of Inventory

Inventory synchronization must preserve:

* Inventory Transaction UUID;
* product;
* warehouse;
* quantity;
* source order or production;
* recipe version where applicable;
* offline origin;
* device;
* employee.

The server must prevent negative authoritative stock.

---

# 68. Synchronization of Payments

Payment synchronization must preserve:

* Payment UUID;
* Order UUID;
* amount;
* method;
* portions;
* employee;
* device;
* Cash Session;
* transaction timestamp;
* offline origin.

The server must prevent duplicate financial effects.

---

# 69. Synchronization of Debt Repayment

Debt repayment synchronization must validate:

* Debt identity;
* customer identity;
* outstanding balance;
* repayment amount;
* payment method;
* allocations;
* employee;
* Cash Session where applicable.

Conflicting repayments must be explicitly handled.

---

# 70. Synchronization of Cash Sessions

Cash Session synchronization must preserve:

* session UUID;
* register;
* Branch;
* opening cashier;
* opening device;
* opening amount;
* closing state;
* closing cashier;
* closing device;
* actual cash;
* discrepancy;
* corrections.

A session must not be duplicated during retry.

---

# 71. Synchronization of Shift Handover

Handover synchronization must preserve:

* Handover UUID;
* outgoing session;
* incoming session;
* outgoing employee;
* incoming employee;
* actual count;
* discrepancy;
* acceptance;
* completion state.

The server validates session transitions atomically.

---

# 72. Synchronization of Attendance

Offline attendance must preserve:

* employee;
* Branch;
* device;
* work session UUID;
* event timestamps;
* source;
* clock anomaly metadata.

The server validates employee and Branch authorization.

---

# 73. Synchronization of Payroll

Payroll operations requiring synchronization must include:

* payroll period;
* employee;
* calculation context;
* configuration version;
* operation UUID;
* device;
* employee actor.

Finalized payroll cannot be silently rewritten by offline data.

---

# 74. Synchronization of Configuration

Configuration synchronization must support:

* configuration UUID;
* configuration type;
* scope;
* version;
* effective time;
* status;
* checksum where applicable.

Server configuration versions are authoritative.

---

# 75. Transaction Sync Before Configuration Sync

Operational transactions may depend on configuration snapshots.

Therefore the synchronization engine must preserve dependencies.

A configuration event must not overwrite a historical configuration required by an existing transaction.

---

# 76. Notification Synchronization

Notifications generated from server-authoritative events are not equivalent to core business transactions.

Local notification state may synchronize separately.

A notification failure must never invalidate an already accepted business transaction.

---

# 77. Audit Synchronization

Offline operations must produce audit context.

The audit event should preserve:

* original actor;
* device;
* Branch;
* transaction UUID;
* offline origin;
* synchronization time;
* result;
* conflict if applicable.

Server-generated audit events remain authoritative.

---

# 78. Sync Result

A server response should clearly identify each submitted event.

Conceptually:

```text
transaction_id
status
server_transaction_id
result_code
conflict_id
server_processed_at
```

The client uses the result to update local sync state.

---

# 79. Sync Result States

Recommended result states:

```text
APPLIED
DUPLICATE_ALREADY_APPLIED
REJECTED
CONFLICT
RETRY
```

The client must not interpret `RETRY` as successful application.

---

# 80. Sync Acknowledgement

A transaction should be marked locally as synchronized only after the client receives a valid authoritative acknowledgement.

If the response is lost:

```text
local state = pending
```

and retry is safe because of idempotency.

---

# 81. Batch Transaction Boundaries

A batch should not necessarily be one database transaction.

The server may process events individually or in dependency-safe groups.

This allows:

* partial success;
* bounded transaction duration;
* better recovery.

---

# 82. Sync Ordering Guarantees

The synchronization engine should provide ordering where required by dependency.

Example:

```text
Order
  ↓
Payment
```

must not be synchronized as Payment first when the server requires the Order to exist.

Independent events may synchronize in parallel.

---

# 83. Sync Backpressure

The system must protect the server from an unexpectedly large offline queue.

Possible controls:

* bounded batch size;
* worker concurrency limits;
* per-device rate limits;
* per-Business limits;
* exponential backoff.

Backpressure must not cause data loss.

---

# 84. Queue Growth

The system should monitor:

* pending count;
* oldest pending event;
* retry count;
* failed count;
* conflict count;
* synchronization latency.

These metrics are operational data, not business transaction data.

---

# 85. Stale Event Handling

A stale offline event must not automatically overwrite newer server state.

The server must compare:

* entity version;
* configuration version;
* state;
* transaction timestamp;
* authorization;
* dependencies.

If stale, the event becomes a rejection or conflict according to business rules.

---

# 86. Duplicate Device Event

If the same device submits the same transaction UUID multiple times:

```text
same UUID
same Business
same payload
```

the server returns the existing result.

If the same UUID is reused with a different payload, this is a security/integrity violation.

---

# 87. UUID Reuse Violation

If:

```text
transaction_uuid = X
```

already exists but a new payload claims the same UUID, the server must reject it.

This event should be auditable as a security/integrity anomaly.

---

# 88. Business Deletion

When a Business enters deletion:

* new synchronization is rejected;
* pending sync events are invalidated;
* offline authorization becomes invalid;
* devices are revoked;
* stale events cannot recreate the Business.

Business deletion must dominate synchronization.

---

# 89. Subscription Expiry

When subscription expires:

* new modifying operations are blocked according to entitlement;
* pending unauthorized offline operations are rejected;
* historical authorized operations may still be reconciled according to policy;
* read-only access remains available where permitted.

The synchronization engine must not become an entitlement bypass.

---

# 90. Conflict Resolution Authorization

Only authorized employees may resolve conflicts.

Resolution permission must be evaluated using:

```text
Effective Permissions
+
Branch Scope
+
Business Scope
```

A cashier must not resolve a conflict requiring Owner/Manager authorization unless explicitly granted.

---

# 91. Conflict Resolution Record

A resolution should preserve:

```text
conflict_id
resolved_by_employee_id
resolution_type
resolution_reason
resolved_at
original_state
resolved_state
```

The original conflict must remain immutable.

---

# 92. Conflict Resolution Types

Possible types:

```text
ACCEPT_SERVER
ACCEPT_LOCAL
REJECT_LOCAL
MANUAL_CORRECTION
RETRY
CANCEL_TRANSACTION
```

Only valid resolution types for the conflict may be used.

---

# 93. Manual Correction

If a conflict cannot be safely resolved automatically, the system should create a normal authorized correction.

The original transaction must not be rewritten.

Example:

```text
Offline Transaction
        ↓
Conflict
        ↓
Authorized Correction
```

---

# 94. Conflict Audit

Every conflict resolution must create an audit event containing:

* conflict UUID;
* transaction UUID;
* actor;
* device;
* Business;
* Branch;
* resolution;
* reason;
* timestamps.

---

# 95. Sync and Historical Integrity

Synchronization must never alter the historical identity of an offline transaction.

The system must preserve:

* original UUID;
* original actor;
* original device;
* original Branch;
* original transaction timestamp;
* synchronization timestamp;
* final authoritative outcome.

---

# 96. Sync Cleanup

Successfully synchronized local events may be compacted or removed according to local retention policy.

However, the device must retain enough state to prevent duplicate application after restart.

Server-side historical records remain authoritative.

---

# 97. Server Sync Retention

Server synchronization metadata should follow an explicit retention policy.

Critical synchronization conflicts and security anomalies may require longer retention than ordinary successful acknowledgements.

The exact retention policy is defined separately from operational transaction retention.

---

# 98. Suggested Server Tables

The database should conceptually support:

```text
sync_events
sync_conflicts
sync_conflict_resolutions
```

Optional:

```text
sync_batches
sync_checkpoints
device_sync_state
```

The exact physical schema may evolve.

---

# 99. Suggested Fields

### `sync_events`

```text
id
business_id
branch_id
device_id
employee_id
transaction_id
transaction_type
payload_version
client_sequence
received_at
processed_at
status
result_code
failure_code
created_at
updated_at
```

### `sync_conflicts`

```text
id
business_id
branch_id
transaction_id
device_id
employee_id
conflict_type
status
local_state
server_state
created_at
resolved_at
resolved_by_employee_id
resolution_type
resolution_reason
```

### `sync_conflict_resolutions`

```text
id
conflict_id
employee_id
resolution_type
reason
created_at
```

---

# 100. Database Invariants

The following invariants are mandatory:

1. The server is authoritative for synchronized state.
2. Offline operation requires a trusted device.
3. A new device cannot start offline operation before online registration.
4. Offline authorization is time-bounded.
5. Offline authorization is Business-scoped.
6. Offline authorization is Branch-scoped.
7. Offline authorization is Employee-scoped.
8. Offline authorization is Device-scoped.
9. Offline authorization reflects applicable permissions.
10. Offline authorization respects subscription entitlement.
11. Offline authorization can be revoked.
12. Device revocation prevents unauthorized new offline synchronization.
13. Every synchronized business transaction has a permanent UUID.
14. Transaction UUIDs are never reused.
15. The system does not require a separate Client Transaction ID.
16. Sync Event identity is separate from business transaction identity.
17. Synchronization is idempotent.
18. Duplicate synchronization cannot duplicate business effects.
19. Same UUID with different payload is rejected.
20. Every sync event belongs to exactly one Business.
21. Every sync event belongs to the correct Branch.
22. Cross-Business synchronization is prohibited.
23. Cross-Branch unauthorized synchronization is prohibited.
24. Employee authorization is validated by the server.
25. Device trust is validated by the server.
26. Subscription entitlement is validated by the server.
27. Configuration validity is validated by the server.
28. Mandatory dependencies must exist before dependent transactions are applied.
29. Synchronization preserves required transaction ordering.
30. Independent events may be processed independently.
31. Partial batch success is supported.
32. One failed event does not automatically roll back unrelated successful events.
33. Retryable failures remain retryable.
34. Permanent validation failures are not retried indefinitely.
35. Failed synchronization remains traceable.
36. Every unresolved conflict has a permanent UUID.
37. Conflicts are explicit.
38. Conflicts cannot be silently discarded.
39. Conflict resolution requires authorization.
40. Conflict resolution preserves the original conflict.
41. Conflict resolution is audited.
42. Inventory synchronization cannot create negative authoritative stock.
43. Inventory concurrency is server-controlled.
44. Payment synchronization cannot duplicate financial effects.
45. Debt repayment synchronization validates outstanding balance.
46. Cash Session synchronization validates session lifecycle.
47. Handover synchronization validates predecessor and successor sessions.
48. Table synchronization cannot silently overwrite an authoritative assignment.
49. Order synchronization validates current authoritative state.
50. Configuration synchronization does not overwrite newer valid configuration.
51. Historical transactions may reference older valid configuration versions.
52. Offline transaction timestamps do not override server lifecycle decisions.
53. Server timestamps are authoritative after synchronization.
54. Clock rollback is detectable.
55. Suspicious clock behavior may create a security conflict.
56. Invalid transaction signatures are rejected.
57. Tampered payloads are not partially applied.
58. Local transaction creation and local queue insertion are atomic.
59. Offline queue state survives normal application restart.
60. Local synchronization state is not authoritative.
61. Server acknowledgement is required before local event becomes Synced.
62. Lost responses can be safely retried.
63. Retry cannot duplicate business effects.
64. Synchronization batch size is bounded.
65. Queue growth is observable.
66. Synchronization supports backpressure.
67. Sync worker failure does not corrupt business transactions.
68. Synchronization does not block normal POS operation.
69. Offline order operations preserve Order UUIDs.
70. Offline payment operations preserve Payment UUIDs.
71. Offline inventory operations preserve Inventory Transaction UUIDs.
72. Offline attendance operations preserve Work Session identity.
73. Offline cash operations preserve Cash Session identity.
74. Offline handover operations preserve Handover identity.
75. Offline debt repayment preserves repayment identity.
76. Offline audit context preserves original actor and device.
77. Synchronization timestamps are distinct from original transaction timestamps.
78. Synchronization cannot rewrite historical actor identity.
79. Synchronization cannot move a transaction to another Business.
80. Synchronization cannot move a transaction to another unauthorized Branch.
81. Employee deactivation is respected by server validation.
82. Permission revocation is respected by server validation.
83. Subscription expiry cannot be bypassed through synchronization.
84. Business deletion rejects new synchronization.
85. Business deletion invalidates pending synchronization.
86. Stale events cannot resurrect deleted Business data.
87. Deleted Business UUIDs are never reused.
88. Conflict resolution cannot silently rewrite the original transaction.
89. Manual conflict correction uses normal correction mechanisms.
90. Original offline state remains reconstructable.
91. Server state and synchronization state are separate concepts.
92. Transaction status and synchronization status are separate concepts.
93. Synchronization metadata cannot become operational business truth.
94. Synchronization history remains auditable.
95. Sync conflict history remains auditable.
96. Sync metadata follows explicit retention rules.
97. Sensitive synchronization payload data is minimized and protected.
98. Sync queries are Business-scoped and indexed.
99. Synchronization failure must have an observable outcome.
100. Offline operation must preserve the system's core historical integrity, authorization, concurrency, and security rules.

---

# Related Documents

* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/04_Architecture/08_Offline_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/12_Event_and_Message_Architecture.md`
* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`

