# Synchronization Architecture

**Document ID:** ARCH-09
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the synchronization architecture for FastFood ERP.

Synchronization connects trusted offline devices with the authoritative server system.

The synchronization architecture is responsible for:

* uploading offline transactions;
* validating offline operations;
* preserving transaction identity;
* preventing duplicates;
* maintaining dependency order;
* detecting conflicts;
* persisting conflicts;
* retrying temporary failures;
* handling partial batch success;
* synchronizing configuration;
* synchronizing audit and notifications;
* recovering from interrupted synchronization;
* maintaining historical integrity.

Synchronization must never bypass normal application and domain rules.

---

# 2. Core Principle

The synchronization model is:

```text
Local Database
      ↓
Durable Sync Queue
      ↓
Sync Worker
      ↓
Sync API
      ↓
Authentication / Device Validation
      ↓
Application Command
      ↓
Domain Rules
      ↓
Database Transaction
      ↓
Sync Result
      ↓
Local Queue Update
```

The server remains authoritative for global current state.

Offline transactions retain their original UUIDs.

---

# 3. Synchronization Is Not Direct Replication

FastFood ERP does not use unrestricted database replication between POS devices and the server.

The model is:

```text
Offline Transaction
        ↓
Business Command
        ↓
Server Validation
        ↓
Business Transaction
```

The client does not directly synchronize database rows.

This prevents the client from bypassing:

* authorization;
* subscription checks;
* Business isolation;
* Branch isolation;
* domain rules;
* concurrency rules;
* historical integrity.

---

# 4. Synchronization Responsibilities

The synchronization subsystem is responsible for:

1. Queue management
2. Event identity
3. Dependency ordering
4. Batch construction
5. Upload
6. Server validation
7. Idempotency
8. Conflict detection
9. Retry handling
10. Result processing
11. Configuration synchronization
12. Audit synchronization
13. Notification reconciliation
14. State recovery
15. Observability

It is not responsible for redefining business rules.

---

# 5. Synchronization Actors

The main synchronization actors are:

```text
Trusted Device
       ↓
Local Sync Worker
       ↓
Sync API
       ↓
Application Layer
       ↓
Domain Modules
       ↓
Server Database
```

Background server workers may also participate in:

* notification processing;
* conflict processing;
* report processing;
* cleanup;
* retry handling.

---

# 6. Synchronization Identity

Every synchronized operation has stable identity.

Important identifiers include:

```text
Business UUID
Branch UUID
Device UUID
Employee UUID
Transaction UUID
Entity UUID
Sync Event UUID
```

The Sync Event UUID identifies the synchronization operation.

The Transaction UUID identifies the business transaction.

These identifiers must not be confused.

---

# 7. Transaction UUID

Transaction UUID identifies the business operation.

Examples:

* Order UUID;
* Payment UUID;
* Inventory Transaction UUID;
* Cash Session UUID;
* Attendance UUID.

A transaction UUID remains unchanged from offline creation through server synchronization.

---

# 8. Sync Event UUID

Sync Event UUID identifies the event delivered to the server.

Conceptually:

```text
Transaction UUID
       ↓
Sync Event UUID
       ↓
Sync Request
```

A retry of the same synchronization event must use the same Sync Event UUID.

---

# 9. Idempotency Principle

The fundamental rule is:

```text
Same UUID
+
Same Valid Operation
=
One Business Effect
```

Repeated delivery must never create duplicate business effects.

Examples:

* duplicate Order;
* duplicate Payment;
* duplicate Inventory Deduction;
* duplicate Cash Transaction;
* duplicate Attendance;
* duplicate Audit Event.

---

# 10. Durable Local Queue

Every operation requiring synchronization must be stored in a durable local queue.

Conceptual structure:

```text
sync_queue
-----------
event_id
transaction_id
business_id
branch_id
device_id
employee_id
entity_type
operation_type
payload
dependency_data
status
attempt_count
created_at
last_attempt_at
next_attempt_at
error_code
```

The exact physical schema is defined in database implementation.

---

# 11. Queue Lifecycle

The synchronization queue supports:

```text
Pending
   ↓
Syncing
   ↓
Synced
```

Alternative paths:

```text
Pending
   ↓
Retrying
   ↓
Syncing
```

or:

```text
Syncing
   ↓
Conflict
```

or:

```text
Syncing
   ↓
Failed
```

Queue state must survive application restart.

---

# 12. Pending State

`Pending` means:

* transaction is persisted locally;
* synchronization is required;
* no active synchronization attempt is currently processing it.

Pending events remain durable until a final result is recorded.

---

# 13. Syncing State

`Syncing` means:

* an active synchronization attempt is in progress;
* the event has been selected by the worker;
* the worker must not process the same event concurrently on the same device.

If the application terminates unexpectedly, the event must be recoverable.

---

# 14. Synced State

`Synced` means:

* server accepted the operation;
* the server result was successfully recorded;
* the local queue no longer requires business synchronization.

The local event may later be compacted according to retention rules.

---

# 15. Retrying State

`Retrying` means:

* the previous attempt failed temporarily;
* another attempt is scheduled;
* the event remains pending.

Retry state must include:

* attempt count;
* last failure;
* next retry time.

---

# 16. Conflict State

`Conflict` means:

* server received the operation;
* the operation could not be automatically accepted under current business state;
* manual or explicitly defined conflict resolution is required.

Conflict does not mean network failure.

---

# 17. Failed State

`Failed` means the operation cannot safely continue automatically.

Examples:

* permanently invalid authorization;
* malformed event;
* deleted Business;
* invalid operation schema;
* unsupported operation;
* irrecoverable security failure.

The event remains available for investigation according to retention policy.

---

# 18. Dependency Model

Synchronization operations may depend on previous operations.

Example:

```text
Create Order
     ↓
Accept Order
     ↓
Payment
```

Another example:

```text
Create Cash Session
     ↓
Cash Payment
     ↓
Cash Session Close
```

A dependent operation must not be synchronized before its prerequisite.

---

# 19. Dependency Representation

A Sync Event may contain:

* parent Transaction UUID;
* dependency UUID;
* dependency type;
* dependency state;
* sequence information.

Conceptually:

```text
Event B
requires
Event A = Synced
```

Only then may Event B proceed.

---

# 20. Synchronization Ordering

General ordering:

```text
Identity / Session Context
        ↓
Operational Transactions
        ↓
Financial Transactions
        ↓
Closing / Correction Transactions
        ↓
Configuration Refresh
        ↓
Secondary Data
```

Actual ordering must follow business dependencies rather than a fixed global sequence.

---

# 21. Batch Synchronization

The device should send bounded synchronization batches.

Typical target:

```text
50–100 events
```

per batch.

The exact size is configurable and must be determined through performance testing.

Large unbounded requests are prohibited.

---

# 22. Batch Composition

A batch should contain events that are:

* authorized for the device;
* ready according to dependencies;
* within request-size limits;
* valid for the current synchronization protocol version.

Events that depend on unresolved conflicts should not be included as executable operations.

---

# 23. Partial Batch Success

The server must return a result for each event.

Example:

```text
Event A → Synced
Event B → Synced
Event C → Conflict
Event D → Synced
```

The client must update each queue record independently.

A conflict in one event must not roll back unrelated successful events.

---

# 24. Batch-Level Failure

A batch-level failure may occur when:

* authentication fails;
* server is unavailable;
* request is malformed;
* protocol version is unsupported;
* request exceeds limits.

If the server cannot safely process any events, the batch remains retryable or failed according to the error classification.

---

# 25. Lost Response

A critical failure scenario is:

```text
Client sends event
      ↓
Server commits
      ↓
Network fails
      ↓
Client receives no response
```

The client must not assume the transaction failed.

It retries using the same:

```text
Sync Event UUID
Transaction UUID
```

The server detects the previous operation and returns the existing result.

---

# 26. Duplicate Request Handling

If a duplicate Sync Event UUID arrives:

```text
Sync Event UUID already processed
        ↓
Load previous result
        ↓
Return previous result
```

The business operation must not execute again.

---

# 27. Duplicate Transaction Handling

Even if a Sync Event UUID is different, the business transaction UUID must remain unique.

Example:

```text
Transaction UUID = X
Sync Event A → creates X
Sync Event B → attempts X
```

The second operation must be rejected as duplicate or resolved according to idempotency rules.

---

# 28. Server Validation Pipeline

Every synchronized event follows:

```text
Receive
   ↓
Authenticate
   ↓
Validate Device
   ↓
Validate Employee
   ↓
Validate Business
   ↓
Validate Branch
   ↓
Validate Subscription
   ↓
Validate Permission
   ↓
Validate Schema
   ↓
Validate Dependency
   ↓
Validate Current State
   ↓
Execute Application Command
   ↓
Commit
   ↓
Return Result
```

The exact validation order may vary where dependencies require it.

---

# 29. Business Isolation

Every synchronization event must be associated with exactly one Business context.

The server must verify:

```text
Event.Business
=
Authenticated Device.Business
```

Cross-Business synchronization is prohibited.

---

# 30. Branch Isolation

Branch-scoped events must satisfy:

```text
Event.Branch
=
Authorized Branch Scope
```

An employee or device cannot synchronize an event into an unauthorized Branch.

---

# 31. Device Validation

The server validates:

* Device UUID;
* trust state;
* Business association;
* Branch association;
* revocation state;
* synchronization capability.

A revoked device cannot create new accepted offline operations.

---

# 32. Employee Validation

The server validates:

* Employee UUID;
* employee status;
* Business membership;
* Branch scope;
* required permission;
* relationship to the trusted device where applicable.

Inactive employees cannot gain new operational authority through synchronization.

---

# 33. Permission Validation

The server calculates effective permission using:

```text
Role
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
+
Operation Context
```

The server must not trust a permission claim supplied by the client.

---

# 34. Subscription Validation

The server checks current subscription state.

Synchronization must distinguish:

* transaction created while authorization was valid;
* transaction created after entitlement expired;
* transaction synchronized after expiry.

The exact result depends on the applicable offline authorization and lifecycle rules.

---

# 35. Offline Authorization Validation

The server validates the offline authorization context.

Checks may include:

* signature;
* expiration;
* Device UUID;
* Employee UUID;
* Business UUID;
* Branch UUID;
* authorization version;
* replay state.

Invalid authorization must not be accepted.

---

# 36. Timestamp Validation

Each event may contain:

```text
client_timestamp
server_received_at
```

The server timestamp is authoritative.

The server may detect:

* excessive future timestamps;
* large clock rollback;
* impossible event ordering;
* suspicious repeated timestamps.

Clock anomalies may cause rejection, conflict, or security review depending on severity.

---

# 37. Order Synchronization

Order synchronization must preserve:

* Order UUID;
* original employee;
* original device;
* original Branch;
* original Cash Session where applicable;
* order type;
* item data;
* price snapshot;
* configuration version;
* operational state;
* timestamps.

The server applies normal Order domain rules.

---

# 38. Order Acceptance Synchronization

Offline Accepted Orders must be revalidated.

Server checks include:

* order state;
* product validity;
* menu configuration;
* recipe;
* inventory;
* permissions;
* Branch;
* subscription;
* related table state where applicable.

If validation fails, the server must return a controlled result.

---

# 39. Inventory Synchronization

Inventory synchronization must be transactional.

For a sale:

```text
Validate Stock
      ↓
Deduct Stock
      ↓
Accept Order
      ↓
Commit
```

The server must never allow synchronization to create negative stock.

---

# 40. Inventory Conflict

If offline inventory consumption conflicts with current server stock:

```text
Local Transaction
       ↓
Server Stock Validation
       ↓
Insufficient Stock
       ↓
Conflict
```

The original offline transaction remains visible.

The system does not silently rewrite the transaction.

---

# 41. Payment Synchronization

Payment synchronization validates:

* Order;
* Business;
* Branch;
* payment state;
* remaining amount;
* method;
* amount;
* permission;
* Cash Session where applicable;
* duplicate UUID.

Payment processing must be atomic.

---

# 42. Payment Already Completed

If an offline payment arrives after the order has already been fully paid:

```text
Payment
   ↓
Order Already Fully Paid
   ↓
Conflict
```

The system must not silently create an additional normal payment.

If overpayment is allowed by the business rules, it must be explicitly represented as overpayment rather than corrupting the original payment state.

---

# 43. Debt Synchronization

Debt payment synchronization must validate:

* customer identity;
* debt order;
* current balance;
* allocation;
* payment amount;
* employee;
* Branch.

If the balance changed while offline, the server creates an explicit conflict where required.

---

# 44. Cash Session Synchronization

Cash Session operations must preserve:

* Cash Session UUID;
* Register UUID;
* Branch;
* cashier;
* opening amount;
* closing amount;
* discrepancy;
* corrections.

The server validates the one-active-session rule.

---

# 45. Cash Handover Synchronization

Handover events must preserve:

```text
Previous Cash Session
        ↓
New Cash Session
        ↓
Previous Cashier
        ↓
New Cashier
```

The previous session remains closed.

The new session has a new UUID.

The physical register remains the same.

---

# 46. Configuration Synchronization

Configuration synchronization is different from transaction synchronization.

Transactions represent business actions.

Configuration represents the state used to perform future actions.

Therefore:

```text
Transaction Sync
      ↓
Configuration Refresh
```

is generally preferred.

Configuration must not overwrite historical transaction snapshots.

---

# 47. Configuration Version

Every relevant configuration object must have a version.

Examples:

* Product price version;
* Recipe version;
* Set version;
* Menu version;
* Printer configuration version.

The client reports the version used for the offline operation where required.

---

# 48. Configuration Conflict

If an administrative user changed configuration while the device was offline:

```text
Device uses Version 7
Server currently Version 8
```

The server must determine whether Version 7 remains valid for the operation.

For historical transaction processing, the configuration snapshot used by the offline transaction must remain traceable.

For future operations, the latest valid server configuration must be synchronized.

---

# 49. Configuration Download

After transaction synchronization, the device downloads:

* new configuration versions;
* updated products;
* price changes;
* menu changes;
* recipe versions;
* Set versions;
* permission-related updates;
* printer configuration.

Only configuration valid for the Device/Branch/Employee context is downloaded.

---

# 50. Audit Synchronization

Offline audit events must eventually reach the server.

Audit events include:

* important state changes;
* corrections;
* conflict resolution;
* cash operations;
* permission-sensitive operations;
* security events.

Routine local reads do not need to generate synchronization events.

---

# 51. Notification Synchronization

Notifications may be generated both locally and server-side.

The synchronization layer should reconcile them using:

* condition identity;
* Business;
* Branch;
* event context;
* notification type;
* lifecycle state.

Duplicate notification cycles must be prevented.

---

# 52. Conflict Resolution Architecture

Conflict resolution follows:

```text
Conflict Detected
      ↓
Persist Conflict
      ↓
Notify Authorized User
      ↓
Inspect Local / Server State
      ↓
Authorized Resolution
      ↓
Correction / Resolution Transaction
      ↓
Audit
      ↓
Conflict Closed
```

The original transaction is not deleted.

---

# 53. Conflict Resolution Permissions

Only authorized employees may resolve conflicts.

Typical authority may include:

* Owner;
* authorized Manager;
* another explicitly permissioned employee.

The conflict resolver must not automatically receive permission to change unrelated data.

---

# 54. Conflict Resolution Reason

Resolution requires a reason where the operation changes business state.

The reason is persisted with:

* resolver;
* timestamp;
* original conflict;
* selected resolution;
* resulting transaction;
* audit event.

---

# 55. Automatic Conflict Resolution

Automatic resolution may be used only for deterministic, low-risk cases.

Examples:

* duplicate delivery of an already accepted UUID;
* retry of the same synchronization request;
* already-completed idempotent event.

Automatic resolution must never silently rewrite financial or inventory history.

---

# 56. Manual Conflict Resolution

Manual resolution is required where business intent is ambiguous.

Examples:

* competing offline stock consumption;
* Cash Session concurrency;
* conflicting payment;
* configuration conflict affecting current operations;
* conflicting correction.

Manual resolution must create a new auditable state transition.

---

# 57. Retry Classification

Synchronization failures should be classified.

### Retryable

* network unavailable;
* timeout;
* temporary server failure;
* connection reset;
* temporary database contention.

### Conflict

* stock conflict;
* payment state conflict;
* Cash Session conflict;
* stale configuration;
* concurrent business change.

### Permanent Failure

* invalid event;
* invalid UUID format;
* deleted Business;
* revoked device;
* unsupported operation;
* invalid protocol.

---

# 58. Retry Policy

Retryable events use bounded retry.

Example conceptual strategy:

```text
Attempt 1
   ↓
Short delay
   ↓
Attempt 2
   ↓
Longer delay
   ↓
Attempt 3
   ↓
Backoff
```

Maximum retry attempts and delays are configurable.

Permanent failures must stop automatic retry.

---

# 59. Exponential Backoff

Backoff should prevent a disconnected device from continuously overwhelming the server.

The retry system should include:

* exponential delay;
* maximum delay;
* jitter where appropriate;
* reset after successful synchronization.

---

# 60. Synchronization Concurrency on One Device

Only one synchronization worker should own a given queue event at a time.

The local queue must prevent:

```text
Event X
 ↓       ↓
Worker A Worker B
```

from synchronizing the same event simultaneously.

---

# 61. Synchronization Concurrency Across Devices

Multiple devices may synchronize simultaneously.

The server database controls final concurrency.

Examples:

```text
Device A → Sell last item
Device B → Sell last item
```

The server transaction decides which operation succeeds.

---

# 62. Server Transaction Isolation

Synchronization commands use the same transaction and concurrency mechanisms as online commands.

Synchronization must not use a weaker consistency model merely because the request originated offline.

---

# 63. Event Ordering Across Devices

Global ordering across disconnected devices cannot be assumed.

For example:

```text
Device A:
Event A at 10:00

Device B:
Event B at 09:59
```

Server receive order may differ from client timestamps.

Business state must therefore be resolved through:

* transaction rules;
* entity state;
* server transaction ordering;
* explicit conflict handling.

Client timestamps alone must not determine global truth.

---

# 64. Causal Dependencies

When one local event depends on another event from the same device, that dependency must be explicit.

Example:

```text
Order Accepted
     ↓
Payment
```

The payment cannot synchronize successfully before the Order is accepted unless the server can safely process the complete dependency chain.

---

# 65. Synchronization Protocol Version

The sync protocol must be versioned.

Example:

```text
/api/v1/sync
```

Protocol changes that break clients require a controlled version migration.

Older trusted devices must not send unsupported payloads indefinitely.

---

# 66. Payload Validation

Every synchronization payload must be validated for:

* schema;
* required fields;
* field types;
* UUID format;
* Business/Branch scope;
* operation type;
* payload size;
* version;
* security metadata.

Malformed payloads are rejected without executing business logic.

---

# 67. Payload Size

Synchronization requests must have bounded size.

Large payloads must be split into smaller batches.

This protects:

* API memory;
* database connections;
* request latency;
* POS stability.

---

# 68. Compression

Compression may be used for synchronization traffic when it materially reduces network cost.

Compression must not weaken:

* payload validation;
* authentication;
* integrity;
* size limits.

---

# 69. Network Efficiency

The synchronization protocol should minimize unnecessary data transfer.

Use:

* UUID references;
* version numbers;
* incremental configuration updates;
* bounded batches;
* compressed payloads where useful;
* server acknowledgements;
* compact result structures.

Full database snapshots should not be sent for every synchronization cycle.

---

# 70. Incremental Synchronization

Configuration and server state should synchronize incrementally.

Conceptually:

```text
Device Version = 12
Server Version = 15

Download:
13
14
15
```

rather than downloading the entire configuration each time.

If incremental history is unavailable, the server may send a current full snapshot.

---

# 71. Sync Checkpoint

The device may maintain a synchronization checkpoint.

A checkpoint can identify:

* last successful server state/version;
* last processed configuration version;
* last synchronization time;
* last successful batch.

The checkpoint must never be used as the sole idempotency mechanism.

---

# 72. Acknowledgement

The server should explicitly acknowledge successful events.

Example:

```text
Event UUID
Status
Server Timestamp
Entity UUID
Result
Conflict UUID if applicable
Error Code if failed
```

The client updates local queue state only after a valid response.

---

# 73. Server Result Persistence

For important idempotent synchronization events, the server must retain enough result information to answer repeated requests.

This prevents:

```text
Commit succeeded
but
retry cannot determine previous result
```

from creating ambiguity.

---

# 74. Sync API Security

The Sync API must require:

* authentication;
* trusted device validation;
* Business validation;
* Branch validation;
* permission validation;
* subscription validation;
* request validation;
* replay protection.

The endpoint must not be treated as a privileged bypass channel.

---

# 75. Sync API Rate Limits

Synchronization requests should have bounded rate limits.

Limits may consider:

* device;
* Business;
* IP/network;
* request size;
* event count.

Rate limiting must not prevent legitimate recovery after temporary network loss.

---

# 76. Synchronization and Subscription Expiry

If a Business subscription expires while events remain queued:

* server evaluates each event against lifecycle policy;
* valid historical synchronization may be processed where allowed;
* new modifying operations after entitlement expiry are blocked;
* invalid events become explicit failures/conflicts.

Synchronization cannot reactivate expired subscription.

---

# 77. Synchronization and Data Deletion

If a Business reaches permanent deletion:

```text
Deleted Business
       ↓
Pending Offline Events
       ↓
Rejected
```

Stale offline data must not recreate the Business.

Device trust must also become invalid.

---

# 78. Synchronization and Device Revocation

When a device is revoked:

* new offline operations are blocked;
* pending events may still be evaluated according to security policy;
* suspicious or unauthorized events may be rejected;
* the revocation is audited.

Revocation must not be silently ignored because the device was offline.

---

# 79. Synchronization and Employee Deactivation

If an employee is deactivated:

* new unauthorized operations are blocked;
* previously created offline events are validated according to their original authorization context;
* suspicious events may be rejected;
* final decisions are audited.

The system must distinguish event creation time from synchronization time.

---

# 80. Synchronization and Historical Integrity

Synchronization must never rewrite:

* original transaction UUID;
* original actor;
* original Device;
* original Branch;
* original Cash Session;
* original client timestamp;
* historical price;
* historical recipe version.

Server processing adds:

* server timestamp;
* synchronization result;
* validation result;
* conflict information.

---

# 81. Synchronization and Audit

Every important synchronization decision should be auditable.

Examples:

* accepted offline operation;
* rejected operation;
* conflict;
* conflict resolution;
* security rejection;
* device revocation;
* lifecycle rejection.

Routine successful retries need not create excessive audit noise.

---

# 82. Synchronization and Notifications

Important synchronization failures may generate notifications.

Examples:

* repeated sync failure;
* large number of conflicts;
* device authorization expiry;
* security rejection;
* critical stock conflicts.

Notifications must not block the core synchronization process.

---

# 83. Synchronization and Reporting

Reports should use finalized server state.

Synchronization must not directly modify report versions.

If synchronized transactions affect report metrics:

```text
Business Data Changes
       ↓
Report Recalculation / New Version
```

according to Report Architecture rules.

---

# 84. Synchronization and Background Jobs

Synchronization workers should be isolated from:

* report generation;
* large exports;
* data deletion;
* heavy maintenance.

A heavy background job must not starve synchronization resources.

---

# 85. Resource Protection

Synchronization must have bounded:

* memory;
* queue processing;
* batch size;
* request size;
* database transaction size;
* retry frequency.

The goal is to prevent offline recovery from creating a traffic spike that harms online POS users.

---

# 86. Sync Storm Protection

If a Branch reconnects after several hours/days offline, thousands of events may be queued.

The system should process them progressively.

Example:

```text
10,000 pending events
       ↓
Batch 1
Batch 2
Batch 3
...
```

The POS must remain responsive.

---

# 87. Priority During Sync Storm

During large recovery:

1. Core operational transactions
2. Financial transactions
3. Cash operations
4. Required dependencies
5. Configuration refresh
6. Audit/notifications
7. Cleanup

However, dependency relationships always take priority over this general ordering.

---

# 88. Local Queue Compaction

After successful synchronization, completed events may be compacted.

Compaction must not remove:

* unresolved conflicts;
* required audit context;
* required historical references;
* unsynchronized events.

Compaction is a storage optimization, not a business deletion operation.

---

# 89. Synchronization Retention

Server synchronization records should have an operational retention policy.

Long-term historical information belongs to:

* business transaction records;
* audit;
* report versions;
* correction history.

Temporary synchronization metadata may be cleaned after its retention period.

---

# 90. Synchronization Observability

The system should expose metrics such as:

* pending event count;
* synchronization throughput;
* average sync latency;
* failed events;
* conflict rate;
* retry rate;
* batch size;
* queue age;
* oldest pending event;
* device sync status.

Metrics should be available by Business/Branch scope to authorized operational users where appropriate.

---

# 91. Correlation ID

Each synchronization request should have a Correlation ID.

This helps trace:

```text
Device
  ↓
Sync API
  ↓
Application Command
  ↓
Database Transaction
  ↓
Audit
```

Correlation ID is different from:

* Transaction UUID;
* Sync Event UUID;
* Entity UUID.

---

# 92. Error Codes

Synchronization errors must use stable machine-readable codes.

Examples:

```text
SYNC_DUPLICATE
SYNC_CONFLICT
SYNC_DEPENDENCY_NOT_READY
SYNC_DEVICE_REVOKED
SYNC_EMPLOYEE_INACTIVE
SYNC_SUBSCRIPTION_EXPIRED
SYNC_BUSINESS_DELETED
SYNC_PERMISSION_DENIED
SYNC_INVALID_PAYLOAD
SYNC_CLOCK_ANOMALY
SYNC_STOCK_CONFLICT
SYNC_PAYMENT_CONFLICT
SYNC_CASH_SESSION_CONFLICT
SYNC_CONFIGURATION_CONFLICT
SYNC_TEMPORARY_FAILURE
```

---

# 93. Client Error Handling

The client maps server results to queue actions.

Example:

```text
SUCCESS
    → Synced

TEMPORARY_FAILURE
    → Retrying

CONFLICT
    → Conflict

PERMANENT_FAILURE
    → Failed
```

The client must not classify every HTTP error as retryable.

---

# 94. Server Error Handling

The server must distinguish:

* validation errors;
* authorization errors;
* business conflicts;
* database concurrency errors;
* temporary infrastructure errors;
* security errors.

Raw database errors must never be returned directly to the client.

---

# 95. Transaction Retry on Server

Server-side synchronization transactions may retry safe database failures.

Examples:

* deadlock;
* serialization failure;
* temporary database connection issue.

Business conflicts must not be hidden by transaction retries.

---

# 96. Synchronization Testing

Synchronization must be tested under:

### Network conditions

* stable network;
* intermittent network;
* complete outage;
* high latency;
* connection reset.

### Application conditions

* application restart;
* device reboot;
* worker crash;
* partial processing.

### Server conditions

* temporary failure;
* timeout;
* database deadlock;
* duplicate request.

### Business conditions

* stock conflict;
* payment conflict;
* Cash Session conflict;
* employee deactivation;
* device revocation;
* subscription expiry;
* Business deletion.

---

# 97. Concurrency Testing

Important concurrency scenarios include:

```text
Device A + Device B
        ↓
Same Product
        ↓
Last Stock Unit
```

and:

```text
Device A + Device B
        ↓
Open Cash Session
```

and:

```text
Device A
Payment

Device B
Payment
```

The final state must preserve all defined business invariants.

---

# 98. Security Testing

Security tests must include:

* forged offline authorization;
* modified payload;
* modified Business UUID;
* modified Branch UUID;
* modified Employee UUID;
* replayed event;
* duplicate event;
* revoked Device;
* inactive Employee;
* expired Subscription;
* deleted Business;
* unauthorized conflict resolution.

---

# 99. Synchronization Recovery Testing

The system must verify:

```text
Server Commit
+
Lost Response
+
Retry
=
No Duplicate Effect
```

and:

```text
Local Queue
+
Application Restart
=
No Lost Event
```

and:

```text
Partial Batch
+
Retry
=
Only Unprocessed Events Retried
```

---

# 100. Synchronization Architecture Invariants

The following invariants are mandatory:

1. Synchronization never directly replicates arbitrary database rows.
2. Synchronization uses application/domain rules.
3. Every synchronized business operation has stable identity.
4. Transaction UUIDs are immutable.
5. Sync Event UUIDs are immutable.
6. Duplicate Sync Event UUIDs are idempotent.
7. Duplicate Transaction UUIDs cannot create duplicate business effects.
8. Business isolation is enforced.
9. Branch isolation is enforced.
10. Device trust is validated.
11. Employee state is validated.
12. Permissions are validated server-side.
13. Subscription state is validated server-side.
14. Offline authorization is validated.
15. Client permission claims are never trusted.
16. Client timestamps do not override server authority.
17. Clock anomalies are detectable.
18. Synchronization events are durably queued.
19. Queue state survives application restart.
20. Queue events have explicit lifecycle states.
21. Dependencies are represented explicitly.
22. Dependent events cannot execute before prerequisites.
23. Synchronization batches are bounded.
24. Partial batch success is supported.
25. One failed event does not roll back unrelated successful events.
26. Lost responses are safe to retry.
27. Retry uses the same UUIDs.
28. Idempotent retries return the existing result.
29. Retryable failures are distinguished from permanent failures.
30. Retry uses bounded backoff.
31. Conflicts are first-class persisted records.
32. Conflicts are not hidden in generic logs.
33. Conflict resolution is authorized.
34. Conflict resolution is audited.
35. Original conflicting transactions remain historically visible.
36. Automatic conflict resolution is limited to deterministic cases.
37. Financial conflicts are not silently overwritten.
38. Inventory conflicts are not silently overwritten.
39. Cash conflicts are not silently overwritten.
40. Order conflicts follow Order domain rules.
41. Payment conflicts follow Payment domain rules.
42. Inventory synchronization cannot create negative stock.
43. Inventory deduction remains transactional.
44. Payment processing remains transactional.
45. Cash Session uniqueness remains enforced.
46. Offline Cash Session UUIDs remain unchanged.
47. Configuration synchronization is version-aware.
48. Transactions synchronize before dependent configuration refreshes.
49. Historical configuration snapshots remain intact.
50. Offline transaction price snapshots remain intact.
51. Recipe version references remain intact.
52. Server current configuration remains authoritative for future operations.
53. Audit context survives synchronization.
54. Offline source attribution remains preserved.
55. Server synchronization decisions are traceable.
56. Important synchronization decisions are auditable.
57. Notifications do not block synchronization.
58. Reports are not directly rewritten by synchronization.
59. Report changes are handled by Reporting rules.
60. Background synchronization does not block POS unnecessarily.
61. Synchronization resources are bounded.
62. Sync storms are progressively processed.
63. Queue compaction does not delete pending events.
64. Queue compaction does not delete unresolved conflicts.
65. Synchronization metadata follows retention rules.
66. Correlation IDs trace synchronization requests.
67. Stable error codes are returned.
68. Raw database errors are not exposed.
69. Device revocation is enforced.
70. Employee deactivation is enforced.
71. Subscription expiry is enforced.
72. Business deletion overrides stale offline events.
73. Deleted Business UUIDs are never reused.
74. A deleted Business cannot be resurrected by synchronization.
75. Multiple trusted devices are supported.
76. Multiple devices may synchronize concurrently.
77. Server database concurrency controls final state.
78. Client timestamps cannot define global event ordering.
79. Causal dependencies are preserved.
80. Sync protocol versions are explicit.
81. Payload schema is validated.
82. Payload size is bounded.
83. Large synchronization payloads are split.
84. Network recovery is handled automatically where possible.
85. Synchronization continues in background.
86. Synchronization progress is observable.
87. Synchronization failures are measurable.
88. Conflict rates are measurable.
89. Queue age is measurable.
90. Security failures are measurable.
91. Synchronization testing includes failure scenarios.
92. Synchronization testing includes concurrency scenarios.
93. Synchronization testing includes security scenarios.
94. Synchronization testing includes restart scenarios.
95. Synchronization testing includes duplicate delivery scenarios.
96. Synchronization testing includes partial batch scenarios.
97. Synchronization testing includes lifecycle scenarios.
98. Synchronization must preserve historical integrity.
99. Synchronization must preserve tenant isolation.
100. Synchronization must preserve business correctness under intermittent connectivity.

---

# 101. Completion Criteria

Synchronization Architecture is considered implemented when:

* durable local synchronization queue exists;
* Sync Event UUID and Transaction UUID are implemented;
* idempotent synchronization is implemented;
* dependency ordering is implemented;
* bounded batch processing is implemented;
* partial batch success is implemented;
* lost-response recovery is implemented;
* server-side validation is implemented;
* Business and Branch isolation is enforced;
* device and employee validation is enforced;
* subscription validation is enforced;
* configuration version synchronization is implemented;
* conflict persistence is implemented;
* conflict resolution is implemented;
* retry classification is implemented;
* exponential/backoff retry is implemented;
* device revocation is enforced;
* employee deactivation is enforced;
* Business deletion protection is implemented;
* synchronization observability is available;
* synchronization security tests pass;
* synchronization concurrency tests pass;
* synchronization recovery tests pass;
* duplicate delivery tests pass;
* sync-storm behavior is validated.

---

# 102. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Domain Analysis

* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### Architecture

* `docs/04_Architecture/02_Application_Layer_Architecture.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/06_API_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/08_Offline_Architecture.md`

### Next Architecture Document

`docs/04_Architecture/10_Security_Architecture.md`

---

# 103. Final Status

Synchronization Architecture is **Accepted v1.0**.

The architecture provides reliable synchronization between trusted offline devices and the authoritative server while preserving:

* UUID-based identity;
* idempotency;
* transaction integrity;
* Business isolation;
* Branch isolation;
* permission boundaries;
* subscription rules;
* inventory correctness;
* financial correctness;
* historical integrity;
* explicit conflict handling;
* retry safety;
* server authority;
* offline continuity;
* POS performance.

