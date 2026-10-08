# API Offline Synchronization and Reconciliation

**Document ID:** API-19
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the API contract for offline operation, synchronization, reconciliation and conflict handling in FastFood ERP.

The API must allow trusted offline devices to:

* continue authorized local operations while temporarily disconnected;
* queue local operations;
* submit operations to the server;
* synchronize operations in bounded batches;
* receive per-operation authoritative results;
* retry temporary failures safely;
* detect conflicts;
* reconcile server and device state;
* receive authoritative configuration updates;
* preserve historical transaction integrity;
* prevent duplicate financial or inventory effects.

The synchronization API must support offline continuity without allowing the client to become authoritative over Business state.

---

# 2. Scope

This document covers:

* offline synchronization principles;
* trusted device requirements;
* synchronization session;
* synchronization batch;
* synchronization operation;
* operation identity;
* client sequence;
* operation dependencies;
* upload;
* download;
* acknowledgements;
* per-operation results;
* partial success;
* retry;
* temporary failure;
* permanent rejection;
* conflict detection;
* conflict resolution;
* reconciliation;
* configuration synchronization;
* transaction synchronization;
* Order synchronization;
* Payment synchronization;
* Inventory synchronization;
* Cash Session synchronization;
* Shift Handover synchronization;
* subscription restrictions;
* offline authorization;
* clock validation;
* stale operations;
* deleted Business protection;
* idempotency;
* concurrency;
* audit;
* observability;
* performance;
* security;
* recovery;
* API invariants.

---

# 3. Architectural Position

Offline synchronization follows:

```text
Trusted Device
      ↓
Encrypted Local Storage
      ↓
Local Operation Queue
      ↓
Synchronization API
      ↓
Authentication / Offline Authorization Validation
      ↓
Business / Branch / Device Scope Validation
      ↓
Operation Validation
      ↓
Idempotency / Dependency Validation
      ↓
Application Use Case
      ↓
Domain
      ↓
PostgreSQL
      ↓
Authoritative Result
      ↓
Synchronization Result
      ↓
Trusted Device
      ↓
Local Reconciliation
```

The server remains authoritative.

---

# 4. Offline Authority Model

The system uses the following authority model:

```text
Server
  ↓
Authoritative Business State

Trusted Device
  ↓
Authorized Temporary Local State

Local Queue
  ↓
Pending Operations

Synchronization API
  ↓
Reconciliation Boundary
```

A device may operate temporarily without connectivity.

It does not become the authoritative owner of Business state.

---

# 5. Trusted Device Requirement

Only a previously registered and trusted device may perform offline operations.

A new device cannot bootstrap itself into offline mode.

The device must first:

1. connect online;
2. authenticate;
3. complete device registration;
4. receive trusted-device authorization;
5. receive offline authorization where applicable;
6. obtain required local configuration.

---

# 6. Offline Authorization

Offline authorization is a server-issued, bounded authorization artifact.

It may contain:

```text
Device UUID
Employee UUID
Business UUID
Branch UUID
Authorization Scope
Allowed Capabilities
Issued At
Expires At
Authorization Version
Signature
```

The client must not modify:

* expiration;
* Business;
* Branch;
* Employee;
* capabilities;
* authorization version.

---

# 7. Offline Authorization Lifetime

Current default offline authorization lifetime:

**3 days**

The exact duration may be configurable according to security policy.

The client cannot extend the validity period locally.

A renewed authorization requires successful server interaction.

---

# 8. Offline Authorization Validation

When synchronization occurs, the server validates:

* device identity;
* device trust;
* employee status;
* Business state;
* Branch scope;
* authorization version;
* authorization expiration;
* allowed capabilities;
* signature;
* clock-related security conditions.

Invalid authorization results in rejection.

---

# 9. Synchronization API

Primary endpoint:

```http
POST /api/v1/sync/batches
```

Batch status:

```http
GET /api/v1/sync/batches/{batch_id}
```

Operation result:

```http
GET /api/v1/sync/operations/{operation_id}
```

Synchronization state:

```http
GET /api/v1/sync/state
```

Configuration synchronization:

```http
GET /api/v1/sync/configuration
```

The exact endpoint set may be extended without changing the core synchronization model.

---

# 10. Synchronization Batch

A synchronization batch is a bounded collection of offline operations.

Example:

```json
{
  "batch_id": "018f...",
  "device_id": "018f...",
  "operations": []
}
```

The client must not reuse a different operation set under an existing immutable batch identity.

---

# 11. Batch Size

Initial maximum:

**100 operations per batch**

The limit may be configured.

The server must reject or safely partition oversized requests.

Unbounded synchronization batches are prohibited.

---

# 12. Batch Identity

Each batch should have a unique UUID.

Example:

```json
{
  "batch_id": "018f7e7c-..."
}
```

Batch identity prevents accidental duplicate batch processing and supports operational tracing.

---

# 13. Operation Identity

Every offline operation must have a globally unique operation UUID.

Example:

```json
{
  "operation_id": "018f7e7d-..."
}
```

The operation UUID is the primary idempotency identity for synchronization.

It is separate from:

* Order UUID;
* Payment UUID;
* Inventory Transaction UUID;
* Device UUID;
* Employee UUID;
* Batch UUID.

---

# 14. Operation Type

Every operation identifies its intended business action.

Examples:

```text
ORDER_CREATE
ORDER_UPDATE
ORDER_ACCEPT
ORDER_CANCEL
ORDER_ITEM_ADD
ORDER_ITEM_REMOVE
PAYMENT_CREATE
CASH_SESSION_OPEN
CASH_SESSION_CLOSE
CASH_MOVEMENT_CREATE
INVENTORY_ADJUSTMENT
SHIFT_HANDOVER_CREATE
SHIFT_HANDOVER_ACCEPT
CONFIGURATION_UPDATE
```

Only explicitly supported operation types may be synchronized.

---

# 15. Operation Envelope

A synchronization operation should contain:

```json
{
  "operation_id": "018f...",
  "operation_type": "ORDER_CREATE",
  "entity_id": "018f...",
  "business_id": "018f...",
  "branch_id": "018f...",
  "device_id": "018f...",
  "employee_id": "018f...",
  "cash_session_id": "018f...",
  "client_created_at": "2026-10-08T08:30:00Z",
  "client_sequence": 1021,
  "payload": {},
  "signature": "..."
}
```

Not every field is required for every operation.

---

# 16. Server Authority Over Operation Context

The server must not blindly trust:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Cash Session UUID.

The server validates these against the authenticated or offline-authorized context.

Client-provided identity values are context claims, not authorization.

---

# 17. Client Sequence

A trusted device may maintain a monotonically increasing local sequence.

Example:

```text
1001
1002
1003
1004
```

Client sequence helps:

* ordering;
* diagnostics;
* missing-operation detection;
* reconciliation.

It does not replace operation UUID.

---

# 18. Client Sequence Validation

The server may detect:

* duplicate sequence;
* missing sequence;
* rollback;
* unexpected device sequence.

A sequence anomaly must not automatically authorize or reject unrelated valid operations unless required by the security policy.

---

# 19. Client Timestamp

Offline operations may contain client timestamps.

They are useful for:

* ordering metadata;
* audit context;
* diagnostics;
* reconciliation.

Client time is not authoritative for:

* subscription expiry;
* financial period;
* authorization;
* server transaction time.

---

# 20. Server Timestamp

The server assigns authoritative timestamps to accepted operations.

Important events should retain:

```text
Client Created At
Server Received At
Server Committed At
```

where required for audit and reconciliation.

---

# 21. Operation Signature

Where required, offline operations may be cryptographically signed.

The signature binds relevant operation context such as:

```text
Operation UUID
Device UUID
Business UUID
Branch UUID
Employee UUID
Operation Type
Payload Hash
Client Sequence
```

The exact cryptographic implementation follows the security architecture.

---

# 22. Payload Hash

The server may calculate and store a canonical payload hash.

This supports detection of:

* idempotency key reuse with different data;
* accidental mutation;
* corrupted synchronization payloads.

---

# 23. Idempotency

Synchronization is inherently retryable.

Therefore:

**Every synchronization operation must be idempotent.**

If the same operation is received again, the server returns the existing authoritative result.

---

# 24. Duplicate Operation

Example:

```text
First submission
   ↓
ORDER_CREATE
   ↓
ACCEPTED

Retry
   ↓
same operation_id
   ↓
ALREADY_PROCESSED
```

The retry must not create a second Order.

---

# 25. Conflicting Operation Reuse

If the same operation UUID is submitted with a different payload:

```text
operation_id = X
payload hash = A

later:

operation_id = X
payload hash = B
```

The server returns:

```text
409 Conflict
IDEMPOTENCY_KEY_REUSE_CONFLICT
```

The original authoritative result remains unchanged.

---

# 26. Batch Submission

Example:

```http
POST /api/v1/sync/batches
```

Request:

```json
{
  "batch_id": "018f...",
  "operations": [
    {
      "operation_id": "018f...",
      "operation_type": "ORDER_CREATE",
      "entity_id": "018f...",
      "payload": {}
    }
  ]
}
```

The server validates the batch before processing individual operations.

---

# 27. Batch Validation

Batch-level validation includes:

* authentication/offline authorization;
* trusted device;
* Business;
* Branch;
* batch size;
* batch identity;
* operation structure;
* supported operation types;
* payload size;
* signature;
* duplicate operation IDs within the batch.

Invalid batch structure may reject the batch before operation processing.

---

# 28. Partial Success

A synchronization batch is not necessarily one database transaction.

Example:

```text
Operation 1 → ACCEPTED
Operation 2 → ACCEPTED
Operation 3 → CONFLICT
Operation 4 → INVALID
Operation 5 → TEMPORARY_FAILURE
```

The server must return per-operation results.

---

# 29. Synchronization Result States

Initial operation result states:

```text
ACCEPTED
ALREADY_PROCESSED
REJECTED
CONFLICT
INVALID
UNAUTHORIZED
TEMPORARY_FAILURE
```

These states are machine-readable.

---

# 30. Accepted Result

An accepted operation means:

* validation succeeded;
* business rules succeeded;
* authoritative transaction committed;
* operation result is available.

Example:

```json
{
  "operation_id": "018f...",
  "status": "ACCEPTED",
  "entity_id": "018f...",
  "server_version": 12
}
```

---

# 31. Already Processed Result

`ALREADY_PROCESSED` means the server already has the authoritative result for the operation.

The response should provide enough information for the client to reconcile its local state.

---

# 32. Temporary Failure

Temporary failure may result from:

* database overload;
* transient infrastructure failure;
* temporary service unavailability;
* bounded lock contention;
* temporary queue pressure.

The client may retry with bounded backoff.

Temporary failure must not be interpreted as permanent business rejection.

---

# 33. Permanent Rejection

Examples:

```text
INVALID_OPERATION
UNAUTHORIZED
PRODUCT_INACTIVE
INSUFFICIENT_STOCK
CASH_SESSION_CLOSED
SUBSCRIPTION_READ_ONLY
INVALID_OFFLINE_AUTHORIZATION
```

The client should not blindly retry permanent failures.

---

# 34. Conflict

A conflict means the operation is structurally valid but cannot be applied against the current authoritative state.

Examples:

```text
STALE_VERSION
ORDER_STATE_CONFLICT
INVENTORY_STATE_CONFLICT
CASH_SESSION_CONFLICT
CONFIGURATION_CONFLICT
```

The conflict must provide enough information for reconciliation without exposing unauthorized data.

---

# 35. Conflict Response

Example:

```json
{
  "operation_id": "018f...",
  "status": "CONFLICT",
  "error": {
    "code": "STALE_VERSION",
    "details": {
      "client_version": 12,
      "server_version": 13
    }
  }
}
```

The exact details depend on the operation.

---

# 36. Reconciliation Model

Reconciliation compares:

```text
Device Local State
        ↕
Server Authoritative State
```

The objective is not to force the server to accept local state.

The objective is to determine the correct authoritative result and update local state accordingly.

---

# 37. Reconciliation Authority

The server wins conflicts involving:

* financial state;
* inventory state;
* Cash Session state;
* Business configuration;
* subscription;
* permissions;
* employee status;
* historical transactions.

The client cannot overwrite authoritative server state during reconciliation.

---

# 38. Reconciliation Outcomes

Possible outcomes:

```text
LOCAL_ACCEPTED
SERVER_ACCEPTED
SERVER_STATE_WINS
RETRY_REQUIRED
USER_REVIEW_REQUIRED
PERMANENTLY_REJECTED
```

The client uses these outcomes to update local state.

---

# 39. Automatic Reconciliation

Automatic reconciliation may be used when the correct outcome is deterministic.

Examples:

* duplicate operation;
* already processed Order;
* already synchronized configuration;
* known server version;
* idempotent replay.

---

# 40. Manual Reconciliation

Manual review may be required when:

* two valid changes conflict;
* inventory adjustment conflicts with a later authoritative count;
* configuration changes conflict;
* Cash Session state is inconsistent;
* financial operation state is uncertain.

Manual reconciliation must never modify historical records silently.

---

# 41. Order Synchronization

Orders may be created offline when allowed.

Typical operation:

```text
ORDER_CREATE
```

The server validates:

* Business;
* Branch;
* employee;
* device;
* order type;
* menu/product;
* price snapshot;
* recipe;
* inventory;
* Cash Session where required;
* permissions;
* offline authorization.

---

# 42. Offline Order Price

An offline Order contains the price snapshot known to the device.

The server must validate the configuration version and offline authorization.

The server must not silently replace an already-authorized historical transaction price merely because a newer price exists.

---

# 43. Offline Order and New Price

Example:

```text
Device:
Price Version A
     ↓
Offline Order
     ↓
Server now uses Price Version B
```

The server evaluates whether Version A was valid for the authorized offline operation.

If valid, the historical Order retains Version A.

If not valid under server rules, the operation may be rejected or require reconciliation.

---

# 44. Order Item Snapshot

Accepted offline Orders must preserve:

* Product identity;
* quantity;
* applicable price;
* discount/markup information where allowed;
* configuration version where required;
* relevant Recipe/Set version where required.

Current configuration must not rewrite the historical snapshot.

---

# 45. Offline Order Acceptance

`ORDER_ACCEPT` is a business command.

The server performs authoritative validation before committing acceptance.

Inventory and Order state are validated transactionally.

---

# 46. Offline Order Modification

Offline Order modifications must use operation UUIDs.

Examples:

```text
ORDER_ITEM_ADD
ORDER_ITEM_UPDATE
ORDER_ITEM_REMOVE
```

Each operation references the appropriate Order version/state.

Stale modifications may result in conflict.

---

# 47. Order Operation Dependencies

An Order operation may depend on another operation.

Example:

```text
ORDER_CREATE
      ↓
ORDER_ITEM_ADD
      ↓
ORDER_ACCEPT
      ↓
PAYMENT_CREATE
```

The client should provide dependency metadata where ordering cannot be inferred.

---

# 48. Dependency Representation

Example:

```json
{
  "operation_id": "018f...",
  "depends_on": [
    "018f-parent-operation..."
  ]
}
```

The server may process operations according to dependency order.

---

# 49. Missing Dependency

If an operation depends on an operation that has not been accepted:

```text
DEPENDENCY_NOT_RESOLVED
```

The dependent operation should not be committed incorrectly.

---

# 50. Payment Synchronization

Offline payment is more restrictive than offline Order creation.

The server must validate:

* offline authorization;
* allowed payment method;
* Order state;
* amount;
* payment state;
* idempotency;
* Cash Session;
* financial policy.

Offline card payments normally require an external terminal/provider flow and are not treated as generic offline API operations.

---

# 51. Offline Cash Payment

Offline cash payment may be supported where explicitly authorized.

The operation must preserve:

* amount;
* payment method;
* Order;
* Cash Session;
* Employee;
* Device;
* operation UUID.

The server remains authoritative after synchronization.

---

# 52. Offline Refund

Offline refunds should normally be restricted.

A refund may require online authorization because it can create high financial risk.

If offline refund is enabled by explicit policy, it must use:

* strict authorization;
* bounded amount;
* reason;
* idempotency;
* reconciliation;
* audit.

---

# 53. Inventory Synchronization

Offline inventory operations require special care.

Examples:

```text
INVENTORY_ADJUSTMENT
INVENTORY_EXIT
INVENTORY_RECEIPT
```

The server validates authoritative stock.

Cached or locally displayed stock is not sufficient authority.

---

# 54. Inventory Conflict

Example:

```text
Device believes:
Stock = 5

Server:
Stock = 2

Offline operation:
Exit 3
```

The server evaluates the authoritative state.

If the operation would violate inventory rules, it is rejected or requires reconciliation.

Negative inventory must never be created through synchronization.

---

# 55. Inventory Transaction Identity

Each synchronized inventory transaction must retain its operation identity.

Duplicate synchronization must not create duplicate stock deductions.

---

# 56. Cash Session Synchronization

Cash Session operations are highly sensitive.

Possible operations:

```text
CASH_SESSION_OPEN
CASH_SESSION_CLOSE
CASH_MOVEMENT_CREATE
```

The server validates:

* Branch;
* Cash Register;
* Employee;
* session state;
* expected/actual cash;
* concurrency;
* device;
* operation identity.

---

# 57. Offline Cash Session

Offline opening/closing may only be allowed if explicitly included in offline authorization.

The server reconciles:

```text
Local Cash State
       ↓
Server Cash State
```

A closed session must not be silently reopened.

---

# 58. Cash Session Conflict

If two devices attempt conflicting Cash Session operations:

```text
Device A → CLOSE
Device B → MOVEMENT
```

the server applies authoritative session state and rejects invalid operations.

The API must preserve the original committed history.

---

# 59. Shift Handover Synchronization

Shift handover operations may be synchronized where offline operation permits them.

The server validates:

* outgoing cashier;
* incoming cashier;
* Branch;
* Cash Session;
* handover state;
* cash amount;
* acceptance;
* recount;
* authorization.

---

# 60. Configuration Synchronization

Configuration synchronization is read-oriented where possible.

The device may request:

```http
GET /api/v1/sync/configuration
```

with its known versions.

Example:

```json
{
  "business_configuration_version": 12,
  "branch_configuration_version": 8,
  "menu_configuration_version": 15,
  "pricing_configuration_version": 15
}
```

---

# 61. Configuration Update Result

The server may return:

```json
{
  "configuration": {
    "version": 16,
    "status": "EFFECTIVE"
  }
}
```

or a bounded delta where supported.

The device must not apply configuration that fails integrity or authorization validation.

---

# 62. Configuration Synchronization Priority

Transaction synchronization has priority over configuration synchronization.

Example:

```text
Offline Order
Price Version A
       ↓
Transaction Sync
       ↓
Configuration Version B
       ↓
Device Updates
```

This preserves the original transaction context.

---

# 63. Subscription Synchronization

Subscription state is server-authoritative.

The device may receive:

* current subscription state;
* offline restrictions;
* entitlement version;
* authorization expiry.

The device must not create or modify subscription state offline.

---

# 64. Subscription Read-Only Transition

If a Business becomes `READ_ONLY` while a device is offline:

```text
Device Offline
     ↓
Local operations continue only within offline authorization
     ↓
Synchronization
     ↓
Server validates current subscription
```

Operations prohibited under current server state are rejected.

The client cannot bypass read-only restrictions.

---

# 65. Deleted Business Protection

If a Business is:

```text
DELETING
or
DELETED
```

offline operations must not resurrect it.

Pending offline operations may be rejected.

Historical data must remain protected.

---

# 66. Employee Deactivation

If an employee is deactivated while a device is offline:

```text
Employee active locally
        ↓
Employee deactivated server-side
        ↓
Synchronization
        ↓
New operation rejected
```

Historical operations already committed remain attributed to the original employee.

---

# 67. Device Revocation

If a trusted device is revoked:

```text
Device revoked
      ↓
Synchronization
      ↓
UNAUTHORIZED
```

The device must not receive new offline authorization.

Previously committed server transactions remain valid.

---

# 68. Branch Scope Changes

If an employee loses access to a Branch while offline:

* pending operations are validated against current server scope;
* unauthorized operations are rejected;
* historical accepted operations remain intact.

The device must not use stale Branch membership to gain continued server authority.

---

# 69. Offline Clock Rollback

The system must detect suspicious device clock rollback.

Signals may include:

* local time moving backwards;
* operation timestamp inconsistent with trusted server observations;
* authorization timestamp anomalies.

A clock anomaly may cause:

```text
OFFLINE_CLOCK_ANOMALY
```

and require online reauthorization.

---

# 70. Stale Operation

An operation may become stale because:

* configuration changed;
* employee deactivated;
* device revoked;
* subscription expired;
* Order state changed;
* Cash Session closed;
* inventory changed.

The server determines whether the operation remains valid.

---

# 71. Stale Configuration

A stale configuration does not automatically invalidate historical offline transactions.

The server evaluates whether the transaction was authorized under the offline configuration and authorization version.

---

# 72. Reconciliation of Configuration

If device configuration is stale:

```text
Device Version 12
Server Version 14
```

the API may return:

```text
SERVER_STATE_WINS
```

with the current authorized configuration.

The device updates local configuration after processing pending transactions.

---

# 73. Synchronization Ordering

The server should process operations in dependency-aware order.

Typical order:

```text
1. Authentication / Authorization
2. Dependencies
3. Configuration-independent transactions
4. Orders
5. Inventory / financial effects
6. Configuration updates
7. Secondary effects
```

The exact order depends on operation type.

---

# 74. Transaction Synchronization Priority

Transaction synchronization must not be blocked indefinitely by configuration synchronization.

This is especially important for offline POS continuity.

---

# 75. Batch Processing Model

A synchronization batch may be processed as:

```text
Receive Batch
   ↓
Validate Envelope
   ↓
Resolve Dependencies
   ↓
Process Operations
   ↓
Commit Each Authoritative Operation
   ↓
Record Results
   ↓
Return Batch Result
```

The server should avoid one massive transaction for unrelated operations.

---

# 76. Per-Operation Transaction Boundary

Where operations are independently processable:

```text
Operation 1 → Transaction 1
Operation 2 → Transaction 2
Operation 3 → Transaction 3
```

This limits rollback scope and improves recovery.

---

# 77. Related Operation Group

Some operations may need to be processed atomically.

Example:

```text
Order creation
+
required Order Item creation
```

If the business operation requires atomicity, the Application layer defines the transaction boundary.

The API batch itself does not determine transaction semantics.

---

# 78. Synchronization Retry

Retryable operations should use bounded exponential backoff.

Example:

```text
Retry 1
   ↓
Retry 2
   ↓
Retry 3
   ↓
Later retry
```

The client must not create unlimited retry traffic.

---

# 79. Retry Classification

The server should provide stable retry semantics:

```text
DO_NOT_RETRY
RETRY_WITH_BACKOFF
REFRESH_AND_RETRY
USER_REVIEW_REQUIRED
```

The detailed error contract is defined by:

`09_API_Error_Handling_and_Error_Codes.md`

---

# 80. Reconciliation API

The server may expose reconciliation details through:

```http
GET /api/v1/sync/operations/{operation_id}
```

The response may contain:

* operation state;
* authoritative entity ID;
* server version;
* conflict code;
* retry recommendation;
* reconciliation state.

Sensitive data must remain scope-controlled.

---

# 81. Sync State

Endpoint:

```http
GET /api/v1/sync/state
```

Example:

```json
{
  "device_id": "018f...",
  "last_accepted_sequence": 1020,
  "last_server_sync_at": "2026-10-08T09:00:00Z",
  "configuration_versions": {
    "menu": 16,
    "pricing": 16
  }
}
```

The server must calculate authoritative values.

---

# 82. Acknowledgement

The server should provide a clear acknowledgement for accepted operations.

Example:

```json
{
  "operation_id": "018f...",
  "status": "ACCEPTED",
  "server_committed_at": "2026-10-08T09:01:02Z"
}
```

The device may remove the operation from its pending queue only after authoritative acknowledgement.

---

# 83. Local Queue Retention

The client should retain pending operations until:

* accepted;
* permanently rejected;
* conflict resolved;
* explicitly marked non-retryable.

The server does not depend on the client deleting local records correctly.

---

# 84. Duplicate Batch Submission

If the same batch is submitted again:

* previously accepted operations remain accepted;
* already processed operations return `ALREADY_PROCESSED`;
* unprocessed operations may continue processing.

The batch API must not duplicate business effects.

---

# 85. Batch Status

Endpoint:

```http
GET /api/v1/sync/batches/{batch_id}
```

Possible batch states:

```text
RECEIVED
PROCESSING
PARTIALLY_COMPLETED
COMPLETED
FAILED
```

Batch status is operational metadata.

Per-operation result remains authoritative for reconciliation.

---

# 86. Batch Failure

A batch-level infrastructure failure does not necessarily mean every operation failed.

The client should query operation or batch status before blindly replaying all operations.

Operation idempotency protects against duplicate effects.

---

# 87. Synchronization Security

Synchronization requests must validate:

* TLS/transport security;
* authentication or offline authorization;
* device trust;
* operation signature where required;
* Business scope;
* Branch scope;
* Employee status;
* subscription;
* payload integrity.

---

# 88. Replay Protection

Operation UUID and server-side idempotency state protect against replay.

Additional controls may include:

* authorization version;
* client sequence;
* signature;
* timestamp window;
* device state.

Replay protection must not rely solely on client timestamps.

---

# 89. Payload Size Limits

Synchronization payloads must have bounded:

* batch size;
* operation count;
* payload size;
* nested object depth;
* string length.

Large files should not be embedded directly into synchronization operations.

File synchronization uses the File API.

---

# 90. Synchronization and Files

If an offline operation references a file:

```text
Operation
   ↓
File Reference
```

The file must have its own secure upload/synchronization lifecycle.

The synchronization API must not accept unrestricted filesystem paths or arbitrary binary payloads.

---

# 91. Synchronization and Audit

Important synchronized operations must create audit records using:

```text
Operation UUID
Batch UUID
Device UUID
Employee UUID
Business UUID
Branch UUID
Server timestamp
Result
```

The client must not be able to modify historical audit results.

---

# 92. Synchronization and Outbox

Accepted operations may create Outbox events.

Example:

```text
Offline Operation
      ↓
Application Transaction
      +
Audit
      +
Outbox
      ↓
Commit
```

Notification, printing, analytics and other secondary effects occur after commit.

---

# 93. Synchronization and Notifications

A synchronization operation may trigger notifications.

Example:

```text
Offline Cash Close
      ↓
Server Commit
      ↓
Cash Discrepancy Event
      ↓
Notification
```

Notification failure does not rollback the synchronized transaction.

---

# 94. Synchronization and Printing

Offline Order acceptance may eventually trigger kitchen printing after synchronization if required.

Printing is secondary.

Printer failure does not change the authoritative Order state.

---

# 95. Synchronization and Reports

Reports are generated from authoritative server state.

Offline local report values are not authoritative.

After synchronization, server-side reports may change because new transactions became authoritative.

---

# 96. Synchronization and Historical Reports

A historical Report Version is not rewritten merely because an offline transaction arrives later.

If the source state changes according to report versioning rules, a new report version is created.

---

# 97. Subscription Restrictions

Synchronization must enforce current server subscription state.

At minimum:

```text
ACTIVE
→ permitted according to entitlement

READ_ONLY
→ prohibited mutations

DELETION_ELIGIBLE
→ normal mutations prohibited

DELETING
→ normal operations prohibited

DELETED
→ all normal operations rejected
```

---

# 98. Synchronization During Read-Only

If a device submits a mutation after Business becomes read-only:

```text
SUBSCRIPTION_READ_ONLY
```

The operation is not silently converted into a successful transaction.

The client receives a permanent rejection.

---

# 99. Synchronization During Authorization Expiry

If offline authorization has expired:

```text
INVALID_OFFLINE_AUTHORIZATION
```

The device must reconnect and obtain fresh authorization before continuing synchronization.

---

# 100. Synchronization During Device Revocation

A revoked device receives:

```text
DEVICE_REVOKED
```

The server must not accept new operations from the revoked device.

---

# 101. Synchronization During Employee Deactivation

A deactivated employee cannot create new accepted operations after server validation.

Historical operations already committed remain valid.

---

# 102. Synchronization and Business Deletion

Operations from a Business in `DELETING` or `DELETED` state must not create new Business transactions.

The server must not resurrect the Business.

---

# 103. Synchronization Conflict Resolution

Conflict resolution must preserve:

* original operation;
* original payload;
* original result;
* conflict state;
* resolving actor where applicable;
* resolution reason;
* final state.

The original operation must not be silently overwritten.

---

# 104. Manual Conflict Resolution Endpoint

Where manual resolution is supported:

```http
POST /api/v1/sync/operations/{operation_id}/resolve
```

Request may contain:

```json
{
  "resolution": "ACCEPT_SERVER_STATE",
  "reason": "Authoritative Branch state retained"
}
```

Only authorized users may resolve conflicts.

---

# 105. Resolution States

Possible states:

```text
UNRESOLVED
RESOLVED_SERVER
RESOLVED_LOCAL
RESOLVED_MERGED
REJECTED
```

`RESOLVED_LOCAL` must not mean blindly replacing authoritative server state.

It means a new valid server operation was created from the local intent.

---

# 106. Conflict Resolution and Historical Integrity

Conflict resolution creates a new authoritative state or correction.

It must not rewrite:

* original Order;
* original Payment;
* original Inventory Transaction;
* original Cash Session;
* original configuration version.

---

# 107. Synchronization API Performance Targets

Initial targets:

| Operation                       |   Target |
| ------------------------------- | -------: |
| Sync state read p95             | ≤ 200 ms |
| Configuration sync read p95     | ≤ 500 ms |
| Normal 100-operation batch p95  |    ≤ 1 s |
| Small sync batch p95            | ≤ 500 ms |
| Per-operation result lookup p95 | ≤ 200 ms |
| Batch status p95                | ≤ 200 ms |
| Conflict detail read p95        | ≤ 250 ms |

Large or unusually complex batches may require asynchronous processing.

---

# 108. Synchronization Throughput

The synchronization system should support concurrent trusted devices without allowing synchronization traffic to starve normal POS traffic.

Resource limits must be applied to:

* concurrent batches;
* operations per batch;
* payload size;
* retry traffic.

---

# 109. POS Priority

Normal online POS traffic has higher priority than bulk synchronization.

A synchronization burst must not make:

* Order creation;
* Order acceptance;
* payment;
* Cash Session operations

unusable.

---

# 110. Synchronization Backpressure

The server may apply backpressure when:

* database load is high;
* synchronization queue is saturated;
* lock contention increases;
* POS latency exceeds defined guardrails.

The server may return:

```text
TEMPORARY_FAILURE
SERVICE_UNAVAILABLE
```

with retry guidance.

---

# 111. Synchronization Observability

Metrics should include:

```text
sync_batch_count
sync_operation_count
sync_accepted_count
sync_duplicate_count
sync_conflict_count
sync_rejected_count
sync_temporary_failure_count
sync_batch_latency
sync_operation_latency
sync_retry_count
sync_dependency_failure_count
sync_authorization_failure_count
sync_device_revocation_count
```

Metrics must avoid uncontrolled UUID cardinality.

---

# 112. Synchronization Logging

Logs should contain:

* request ID;
* batch ID;
* operation ID;
* device ID where appropriate;
* Business scope;
* Branch scope;
* operation type;
* result;
* latency.

Logs must not contain:

* passwords;
* access tokens;
* private keys;
* complete sensitive financial payloads unless explicitly required and protected.

---

# 113. Synchronization Alerting

Alerts may be triggered for:

* unusually high conflict rate;
* unusual duplicate rate;
* device clock anomalies;
* repeated authorization failures;
* synchronization backlog;
* abnormal temporary failure rate;
* excessive retry traffic;
* unusual device behavior.

---

# 114. Recovery After Server Restart

After server restart:

* PostgreSQL remains authoritative;
* processed operation records remain available;
* duplicate synchronization remains idempotent;
* unprocessed requests may be retried;
* clients must reconcile using operation status.

Redis or in-memory state must not be required to reconstruct authoritative synchronization history.

---

# 115. Recovery After Device Restart

The device must retain pending operations in encrypted local storage.

After restart:

```text
Local Queue
   ↓
Pending Operations
   ↓
Synchronization
```

The device must not generate new operation UUIDs merely because the previous submission was interrupted.

---

# 116. Network Interruption

If the network disconnects during synchronization:

* the client may not know whether the server committed an operation;
* the client must retry using the same operation UUID;
* the server returns the existing result if already committed.

This is a primary purpose of idempotency.

---

# 117. Timeout During Financial Synchronization

If a payment or cash operation times out:

```text
Client
  ↓
Unknown outcome
```

The client must query or retry with the same operation UUID.

It must not create a new payment operation with a new UUID merely because the first response was lost.

---

# 118. Synchronization and Concurrency

Concurrent operations are resolved by authoritative server state.

Examples:

```text
Device A → Order Cancel
Device B → Order Accept
```

The Domain decides which transition is valid.

The API returns a conflict for the invalid operation.

---

# 119. Synchronization and Inventory Concurrency

Inventory operations must use authoritative transaction boundaries and appropriate row locking/version checks.

The synchronization layer must not resolve inventory concurrency using client-side quantities.

---

# 120. Synchronization and Cash Concurrency

Cash Session operations must use authoritative session state and transactional concurrency control.

Client-reported session state is not authoritative.

---

# 121. Synchronization and Configuration Concurrency

Configuration synchronization uses version-aware updates.

A stale configuration update returns:

```text
STALE_VERSION
```

The device must refresh before retrying.

---

# 122. Synchronization API Contract Testing

Tests must cover:

* batch submission;
* duplicate batch;
* duplicate operation;
* payload conflict;
* partial success;
* temporary failure;
* permanent rejection;
* dependency ordering;
* configuration synchronization;
* Order synchronization;
* payment synchronization;
* inventory synchronization;
* Cash Session synchronization;
* subscription restrictions;
* device revocation;
* employee deactivation;
* Business deletion;
* clock rollback;
* network timeout;
* server restart;
* concurrent synchronization.

---

# 123. Security Testing

Security tests must verify:

* unauthorized device;
* revoked device;
* expired offline authorization;
* invalid signature;
* altered payload;
* cross-Business operation;
* cross-Branch operation;
* employee impersonation;
* subscription bypass;
* replay;
* duplicate payment;
* duplicate inventory deduction;
* unauthorized conflict resolution.

---

# 124. Historical Integrity Testing

Tests must confirm:

```text
Offline Order
   ↓
Synchronization
   ↓
Historical Order Snapshot
```

remains immutable after later:

* price changes;
* recipe changes;
* configuration changes;
* subscription changes.

The same applies to:

* Payments;
* Refunds;
* Inventory Transactions;
* Cash Sessions;
* Shift Handovers.

---

# 125. Synchronization API Endpoint Summary

### Batch

```text
POST /api/v1/sync/batches
GET  /api/v1/sync/batches/{batch_id}
```

### Operation

```text
GET  /api/v1/sync/operations/{operation_id}
POST /api/v1/sync/operations/{operation_id}/resolve
```

### State

```text
GET /api/v1/sync/state
```

### Configuration

```text
GET /api/v1/sync/configuration
GET /api/v1/configuration/changes?since_version={version}
```

---

# 126. API Error Codes

Relevant synchronization error codes include:

```text
SYNC_BATCH_INVALID
SYNC_BATCH_TOO_LARGE
SYNC_OPERATION_INVALID
SYNC_OPERATION_UNSUPPORTED
SYNC_OPERATION_ALREADY_PROCESSED
IDEMPOTENCY_KEY_REUSE_CONFLICT
DEPENDENCY_NOT_RESOLVED
STALE_VERSION
SYNC_CONFLICT
INVALID_OFFLINE_AUTHORIZATION
OFFLINE_AUTHORIZATION_EXPIRED
OFFLINE_CLOCK_ANOMALY
DEVICE_NOT_TRUSTED
DEVICE_REVOKED
EMPLOYEE_INACTIVE
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
SUBSCRIPTION_READ_ONLY
SUBSCRIPTION_EXPIRED
BUSINESS_DELETED
INSUFFICIENT_STOCK
ORDER_STATE_CONFLICT
CASH_SESSION_CONFLICT
PAYMENT_STATE_CONFLICT
TEMPORARY_SYNC_FAILURE
SERVICE_UNAVAILABLE
```

Canonical formatting and HTTP mapping follow:

`09_API_Error_Handling_and_Error_Codes.md`

---

# 127. API and Offline Security Boundary

The synchronization API must never assume that:

```text
offline = trusted forever
```

Offline authorization is:

```text
Trusted Device
+
Bounded Authorization
+
Allowed Capability
+
Expiration
+
Server Reconciliation
```

All conditions must remain satisfied.

---

# 128. Synchronization Data Retention

Synchronization metadata should be retained according to operational, audit and idempotency requirements.

The system must retain enough information to:

* detect duplicate operations;
* reconcile uncertain outcomes;
* support audit;
* investigate conflicts.

Retention must remain bounded according to lifecycle policy.

---

# 129. Idempotency Record Retention

Idempotency records must remain available long enough to protect against realistic client retry and replay windows.

The exact retention period is an implementation and operational decision.

Expired idempotency records must not cause unsafe duplicate financial effects.

Financial operations may require longer retention than low-risk operations.

---

# 130. Synchronization and Audit History

The system must distinguish:

```text
Synchronization Operation
```

from:

```text
Business Audit Event
```

A synchronization operation explains how a client request reached the server.

An audit event explains an important Business state change.

Both may reference the same operation UUID.

---

# 131. Synchronization and Report Versioning

Synchronization can introduce new authoritative transactions.

If the underlying report state changes according to report versioning rules:

```text
New authoritative transaction
        ↓
Report source state changes
        ↓
New Report Version
```

The synchronization operation must not directly rewrite an existing immutable report version.

---

# 132. Synchronization and Notification

Accepted operations may trigger notifications through the existing Outbox architecture.

Examples:

```text
Cash discrepancy
Inventory variance
Large refund
Subscription state change
Security alert
```

Notification failure does not rollback synchronization.

---

# 133. Synchronization and Cache

Synchronization must not directly treat cached state as authoritative.

For example:

```text
Cached Stock = 5
Authoritative Stock = 2
```

The authoritative database value wins.

The same principle applies to:

* cash;
* payment;
* configuration;
* subscription;
* permissions.

---

# 134. Cache Invalidation After Synchronization

When an operation changes cacheable authoritative state:

```text
Synchronization
      ↓
DB Commit
      ↓
Cache Invalidation / Refresh
```

Cache invalidation occurs after authoritative commit.

---

# 135. Synchronization and API Versioning

Offline clients may remain disconnected for extended periods.

Therefore API changes must consider:

* old clients;
* older operation formats;
* schema compatibility;
* migration;
* operation type compatibility.

Breaking synchronization contracts require explicit versioning or migration support.

---

# 136. Operation Schema Version

An operation may include:

```json
{
  "operation_schema_version": 1
}
```

The server can use this to distinguish compatible operation representations.

Unsupported versions should return a stable error.

---

# 137. Backward Compatibility

The synchronization API should support older compatible clients for the defined compatibility period.

Compatible changes may include:

* optional metadata;
* additional response fields;
* new operation types;
* optional configuration fields.

Breaking payload changes require explicit migration/versioning.

---

# 138. Unsupported Operation Version

Example:

```text
SYNC_OPERATION_VERSION_UNSUPPORTED
```

The client should not blindly retry the same incompatible payload.

---

# 139. API Rate Limiting

Synchronization endpoints should have dedicated rate limits.

The server may limit:

* batches per minute;
* operations per device;
* concurrent batches;
* payload size;
* retry frequency.

Rate limits must protect normal POS traffic.

---

# 140. Synchronization Fairness

One device must not monopolize synchronization capacity.

Resource controls may use:

* per-device limits;
* per-Business limits;
* global concurrency limits;
* priority rules.

Critical Business traffic remains protected.

---

# 141. Batch Ordering

The server should preserve operation ordering where dependencies require it.

Independent operations may be processed concurrently when safe.

The server must not reorder operations in a way that violates declared dependencies.

---

# 142. Dependency Cycle

A dependency cycle is invalid.

Example:

```text
Operation A
 ↓
Operation B
 ↓
Operation A
```

The batch should reject the affected operations with:

```text
DEPENDENCY_CYCLE
```

---

# 143. Missing Entity

An operation referencing a non-existent or unauthorized entity may return:

```text
RESOURCE_NOT_FOUND
```

or:

```text
RESOURCE_SCOPE_DENIED
```

depending on security policy.

The response must not expose unauthorized Business data.

---

# 144. Temporary Database Failure

If PostgreSQL is temporarily unavailable:

```text
TEMPORARY_SYNC_FAILURE
```

The client retries later.

No operation may be reported as accepted unless authoritative commit succeeded.

---

# 145. Commit Outcome Uncertainty

If the server cannot determine whether a transaction committed:

* the operation must not be blindly executed again;
* the server must use idempotency/reconciliation mechanisms;
* the client may query operation status.

This is especially important for:

* Payment;
* Refund;
* Cash;
* Inventory.

---

# 146. Synchronization and Exactly-Once Semantics

The API should not claim universal exactly-once network delivery.

Instead it provides:

```text
At-least-once delivery
+
Server-side idempotency
+
Authoritative transaction processing
```

This prevents duplicate Business effects even when network retries occur.

---

# 147. Synchronization and At-Least-Once Delivery

Clients may safely retry supported operations using the same operation UUID.

The server deduplicates previously committed operations.

---

# 148. Synchronization and Local State

The client should treat the local state as:

```text
PENDING
CONFIRMED
CONFLICT
REJECTED
```

not as a final representation of Business truth until synchronization is complete.

---

# 149. Local Confirmation

A device may show a locally created Order as locally confirmed before synchronization if permitted by UX policy.

The UI must clearly distinguish:

```text
LOCAL / PENDING
```

from:

```text
SERVER CONFIRMED
```

The API contract remains authoritative for final state.

---

# 150. Synchronization Completion

A synchronization cycle is complete for an operation when:

1. server result is received;
2. local operation status is updated;
3. authoritative server identity/version is applied;
4. reconciliation is complete.

The client may then safely remove or archive the pending operation according to local storage policy.

---

# 151. Synchronization Recovery Workflow

Recommended recovery:

```text
Operation Pending
      ↓
Network Available
      ↓
Submit Batch
      ↓
Receive Results
      ↓
Accepted?
  ┌───┴───┐
 Yes      No
 ↓         ↓
Confirm   Classify
           ↓
    Retry / Conflict / Reject
```

---

# 152. Synchronization and User Experience

The API should provide enough state information for the frontend/POS to show:

* pending;
* syncing;
* synchronized;
* conflict;
* rejected;
* retrying.

Technical details such as database locks or internal exceptions should not be exposed directly to the user.

---

# 153. Operational Administration

Authorized operators may need to inspect:

* device synchronization state;
* batch state;
* conflict rate;
* failed operations;
* retry backlog;
* clock anomalies;
* revoked devices.

Administrative tools must use the same authorization and Business isolation rules.

---

# 154. Manual Retry

Authorized operational tooling may retry eligible temporary failures.

Manual retry must reuse the original operation identity.

It must not create a new Business operation merely to bypass an existing failure.

---

# 155. Manual Reconciliation

Manual reconciliation must:

* identify original operation;
* preserve original result;
* identify resolving actor;
* record reason;
* create new authoritative state where required;
* create audit event.

Historical records must not be silently rewritten.

---

# 156. Synchronization API Quality Gates

The implementation is not considered complete until:

* duplicate financial operations are prevented;
* Business isolation tests pass;
* Branch isolation tests pass;
* device trust tests pass;
* offline authorization tests pass;
* partial synchronization works;
* temporary failures are retryable;
* conflicts are explicit;
* reconciliation is auditable;
* subscription restrictions are enforced;
* historical integrity tests pass;
* performance targets are measured.

---

# 157. API Invariants

The following invariants apply to Offline Synchronization and Reconciliation:

1. The server remains authoritative.
2. Offline devices are temporary authorized clients.
3. New devices cannot bootstrap directly into offline mode.
4. Offline authorization is bounded.
5. Offline authorization cannot be extended locally.
6. Offline authorization is server-issued.
7. Offline authorization is integrity-protected.
8. Device UUID alone does not authorize offline operation.
9. Employee UUID alone does not authorize offline operation.
10. Business UUID alone does not authorize offline operation.
11. Branch UUID alone does not authorize offline operation.
12. Every synchronization operation has a unique operation UUID.
13. Operation UUID is separate from entity UUID.
14. Batch UUID is separate from operation UUID.
15. Duplicate operations do not duplicate Business effects.
16. Reusing an operation UUID with a different payload is a conflict.
17. Synchronization batches are bounded.
18. Operation payloads are bounded.
19. Unsupported operation types are rejected.
20. Invalid operation schema is rejected.
21. Server timestamps are authoritative.
22. Client timestamps are metadata.
23. Client timestamps cannot extend authorization.
24. Client timestamps cannot determine subscription validity.
25. Client timestamps cannot authorize financial operations.
26. Client sequence does not replace operation UUID.
27. Client sequence cannot override server state.
28. Operation signatures do not replace server authorization.
29. Business scope is validated server-side.
30. Branch scope is validated server-side.
31. Device trust is validated server-side.
32. Employee status is validated server-side.
33. Subscription state is validated server-side.
34. Deleted Business cannot be resurrected.
35. Revoked devices cannot create new accepted operations.
36. Deactivated employees cannot create new accepted operations.
37. READ_ONLY Business cannot bypass mutation restrictions through synchronization.
38. DELETING Business cannot accept normal Business mutations.
39. DELETED Business cannot accept normal Business operations.
40. Synchronization results are machine-readable.
41. Synchronization supports partial success.
42. One failed operation does not automatically invalidate unrelated valid operations.
43. Temporary failure is distinct from permanent rejection.
44. Conflicts are distinct from temporary failures.
45. Clients must not blindly retry permanent rejections.
46. Retryable operations use bounded backoff.
47. Retry uses the original operation UUID.
48. Network timeout does not justify creating a new operation UUID.
49. Commit outcome uncertainty requires reconciliation.
50. Financial operations require authoritative idempotency.
51. Payment synchronization cannot create duplicate payments.
52. Refund synchronization cannot create duplicate refunds.
53. Inventory synchronization cannot create duplicate deductions.
54. Inventory synchronization cannot create negative stock.
55. Cached inventory is never authoritative.
56. Cash Session synchronization uses authoritative session state.
57. Closed Cash Sessions cannot be silently reopened.
58. Cash operations preserve historical state.
59. Offline payment is subject to explicit policy.
60. Offline refund is restricted unless explicitly authorized.
61. Order synchronization preserves historical price snapshots.
62. Current price cannot rewrite an offline Order snapshot.
63. Current configuration cannot silently rewrite historical transactions.
64. Recipe versions remain historically identifiable.
65. Set configurations remain historically identifiable.
66. Order state transitions remain Domain-controlled.
67. Synchronization does not bypass business rules.
68. Synchronization does not bypass permissions.
69. Synchronization does not bypass subscription entitlement.
70. Synchronization does not bypass Business isolation.
71. Synchronization does not bypass Branch isolation.
72. Operation dependencies are validated.
73. Missing dependencies are not silently ignored.
74. Dependency cycles are rejected.
75. Independent operations may be processed independently where safe.
76. API batch boundaries do not automatically define database transaction boundaries.
77. Domain-defined transaction boundaries remain authoritative.
78. Accepted operations commit before being reported as accepted.
79. Audit and required Outbox records commit with core state where required.
80. Notification failure does not rollback synchronized core state.
81. Printer failure does not rollback synchronized core state.
82. Cache invalidation failure does not rollback synchronized core state.
83. Configuration synchronization does not override transaction history.
84. Transaction synchronization has priority over configuration synchronization.
85. Offline configuration is not server-authoritative.
86. Stale configuration is not automatically treated as invalid historical transaction data.
87. Configuration conflicts are explicit.
88. Financial conflicts are explicit.
89. Inventory conflicts are explicit.
90. Cash conflicts are explicit.
91. Conflict resolution preserves the original operation.
92. Conflict resolution preserves the original result.
93. Conflict resolution is auditable.
94. Manual conflict resolution is permission-controlled.
95. Manual conflict resolution cannot silently rewrite history.
96. Reconciliation can create a new authoritative correction.
97. Reconciliation cannot delete the original operation record.
98. Synchronization metadata is retained according to lifecycle policy.
99. Idempotency records remain long enough to protect realistic retry windows.
100. High-risk financial idempotency requires stronger retention where necessary.
101. Synchronization state is observable.
102. Synchronization conflicts are observable.
103. Synchronization retries are observable.
104. Device clock anomalies are observable.
105. Device revocations are observable.
106. Synchronization metrics avoid uncontrolled UUID cardinality.
107. Synchronization logs avoid secrets.
108. Synchronization payloads do not expose private credentials.
109. Large files are not embedded into synchronization batches.
110. File synchronization uses the File API.
111. Synchronization API rate limits are bounded.
112. Synchronization traffic must not starve POS traffic.
113. Synchronization backpressure is supported.
114. One device cannot monopolize synchronization resources.
115. Batch ordering respects dependencies.
116. Independent operations may be processed concurrently when safe.
117. Server restart does not destroy authoritative synchronization state.
118. Redis failure does not destroy synchronization correctness.
119. Local device restart does not require generating new operation UUIDs.
120. Network interruption does not create duplicate Business effects.
121. API version changes must consider disconnected clients.
122. Compatible synchronization payloads remain supported during the compatibility window.
123. Breaking synchronization changes require explicit versioning or migration.
124. Operation schema versions are validated.
125. Unsupported operation schema versions are rejected.
126. Client local state is not authoritative Business state.
127. Local pending operations remain until authoritative result is known.
128. Server acknowledgement is required before a pending operation is considered confirmed.
129. Server state wins authoritative conflicts.
130. User review may be required for non-deterministic conflicts.
131. Reconciliation preserves Business historical integrity.
132. Report versions remain immutable.
133. Audit records remain immutable.
134. Subscription state remains authoritative.
135. Offline authorization cannot extend subscription.
136. Trusted device revocation takes effect at synchronization.
137. Employee deactivation takes effect at synchronization.
138. Business deletion takes effect at synchronization.
139. Offline operations cannot resurrect deleted state.
140. Core synchronization operations remain transactional where required.
141. Synchronization operations use explicit Application use cases.
142. Synchronization API routes contain no core business logic.
143. Synchronization does not directly modify PostgreSQL outside Application/Domain boundaries.
144. Synchronization does not treat API cache as authoritative.
145. Synchronization does not treat client-provided totals as authoritative.
146. Server-side pricing remains authoritative within the permitted offline transaction model.
147. Server-side inventory remains authoritative.
148. Server-side payment state remains authoritative.
149. Server-side Cash Session state remains authoritative.
150. Synchronization performance remains within defined SLOs.
151. Critical POS traffic has higher performance priority than bulk synchronization.
152. Temporary synchronization failure does not create false acceptance.
153. Permanent rejection does not become retryable merely because the client retries.
154. Operation status can be queried independently from batch status.
155. Batch status does not replace per-operation result.
156. Synchronization state is reconstructable from authoritative records.
157. Synchronization API remains horizontally scalable.
158. Synchronization workers use bounded concurrency.
159. Security failures fail closed.
160. Historical integrity has priority over synchronization convenience.

---

# 158. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/16_Reports_and_Dashboards.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/17_Shift_Handover_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/11_API_Pagination_Search_Filtering_and_Sorting.md`
* `docs/04_Architecture/09_API/12_API_CRUD_and_Command_Endpoint_Architecture.md`
* `docs/04_Architecture/09_API/13_API_POS_and_Order_Endpoints.md`
* `docs/04_Architecture/09_API/14_API_Payment_Cash_and_Financial_Endpoints.md`
* `docs/04_Architecture/09_API/15_API_Product_Menu_Recipe_and_Inventory_Endpoints.md`
* `docs/04_Architecture/09_API/18_API_Configuration_and_Subscription_Endpoints.md`
* `docs/04_Architecture/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/04_Architecture/09_API/21_API_Security_CORS_CSRF_and_Data_Protection.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

---

# 159. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `19_API_Offline_Synchronization_and_Reconciliation.md`

**Previous Document:** `18_API_Configuration_and_Subscription_Endpoints.md`

**Next Document:** `20_API_Async_Jobs_Bulk_and_Batch_Operations.md`

---

## Final Principle

> Offline synchronization must provide continuity without transferring authority to the client. Every offline operation must remain identifiable, retry-safe, scope-validated and reconciled against authoritative server state. Financial, inventory, configuration, subscription and historical integrity must always take precedence over offline convenience.

