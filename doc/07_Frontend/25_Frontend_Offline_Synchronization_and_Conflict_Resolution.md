# Frontend Offline Synchronization and Conflict Resolution

**Document ID:** FA-25
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`

## 1. Purpose

This document defines the frontend architecture for synchronizing locally persisted offline operations with the authoritative backend and handling synchronization conflicts safely.

The synchronization architecture must preserve:

* transaction integrity;
* idempotency;
* Business isolation;
* Branch isolation;
* employee and device context;
* historical integrity;
* configuration consistency;
* offline continuity;
* backend authority;
* predictable recovery.

The frontend synchronization layer must never silently overwrite authoritative server state.

---

## 2. Core Principle

The fundamental rule is:

> The frontend may temporarily operate on authorized local state, but the backend remains authoritative after synchronization.

```text
Local Operation
      ↓
Durable Local Storage
      ↓
Synchronization Queue
      ↓
API Client
      ↓
Backend Validation
      ↓
Accepted / Conflict / Rejected
      ↓
Local Reconciliation
```

---

## 3. Synchronization Responsibilities

The frontend synchronization subsystem is responsible for:

* discovering pending operations;
* validating local synchronization prerequisites;
* ordering operations;
* batching operations;
* submitting operations;
* processing partial results;
* retrying temporary failures;
* handling conflicts;
* updating local state;
* reconciling server state;
* preserving operation identity;
* reporting synchronization status.

It is not responsible for deciding final business authority.

---

## 4. Backend Authority

The frontend must not determine that an operation is finally valid merely because:

* local validation passed;
* the operation was created offline;
* the local configuration allowed it;
* the operation was previously displayed as successful.

The server must perform authoritative validation.

---

## 5. Synchronization Lifecycle

The general lifecycle is:

```text
PENDING
   ↓
READY
   ↓
UPLOADING
   ↓
SERVER_PROCESSING
   ↓
ACCEPTED / ALREADY_APPLIED
   ↓
RECONCILED
   ↓
COMPLETED
```

Alternative outcomes:

```text
UPLOADING
   ├── RETRYABLE_FAILURE
   ├── CONFLICT
   └── REJECTED
```

---

## 6. Synchronization Engine

The frontend should contain one centralized synchronization engine.

Features must not independently implement synchronization loops.

Recommended architecture:

```text
Offline Queue
     ↓
Sync Engine
     ↓
Batch Builder
     ↓
API Client
     ↓
Result Processor
     ↓
Reconciliation
```

---

## 7. Single Synchronization Authority

Only the centralized synchronization engine may:

* select pending operations;
* change synchronization states;
* submit synchronization batches;
* process synchronization results.

This prevents duplicate synchronization logic.

---

## 8. Synchronization Triggers

Synchronization may start when:

* application starts;
* network becomes available;
* user logs in;
* user manually requests synchronization;
* pending operation is created while online;
* periodic background interval is reached;
* a critical operation becomes ready.

The exact trigger mechanism must not create duplicate workers.

---

## 9. Manual Synchronization

The UI may provide:

**Sync now**

for authorized operational contexts.

Manual synchronization must invoke the same synchronization engine used by automatic synchronization.

It must not create a separate synchronization implementation.

---

## 10. Network Detection

Network availability is only a synchronization hint.

The frontend must not assume:

```text
navigator says online
=
backend is reachable
```

Actual API connectivity determines whether synchronization succeeds.

---

## 11. Synchronization Lock

The application should prevent multiple synchronization workers from processing the same local operation simultaneously.

Possible mechanisms include:

* in-memory lock;
* browser coordination;
* local lease;
* operation state transition;
* backend idempotency.

The backend idempotency mechanism remains the final duplicate protection.

---

## 12. Operation Selection

The synchronization engine should select operations that are:

* pending;
* retryable and ready;
* not currently being processed;
* authorized for synchronization;
* not expired according to policy.

It must not select:

* completed operations;
* permanently rejected operations;
* unresolved conflicts;
* invalid local records.

---

## 13. Operation Ordering

Operations should normally be processed in dependency order.

Example:

```text
Create Order
     ↓
Accept Order
     ↓
Payment
```

Payment must not be synchronized before the Order exists when a backend dependency requires it.

---

## 14. Operation Dependencies

An operation may contain:

```text
operation_id
depends_on_operation_id
```

The synchronization engine should not process an operation whose dependency is unresolved.

If the dependency is rejected, dependent operations must be moved into an appropriate blocked/recovery state.

---

## 15. Local Sequence

A local sequence may help preserve creation order.

However:

> Local sequence is not global server ordering.

The backend determines authoritative transaction ordering.

---

## 16. Operation UUID

Every retryable synchronized operation must retain the same operation UUID.

Example:

```text
Attempt 1 → operation_id = X
Attempt 2 → operation_id = X
Attempt 3 → operation_id = X
```

The frontend must never generate a new UUID simply because an HTTP request failed.

---

## 17. Corrective Operations

If an original operation must be corrected:

```text
Original Operation → X
Correction Operation → Y
```

`Y` must have a new operation UUID.

The correction must preserve its relationship to the original operation.

---

## 18. Synchronization Batch

The frontend may group operations into bounded batches.

Recommended range:

**50–100 operations per batch.**

The exact server/API limit is authoritative.

---

## 19. Batch Preparation

Before submitting a batch, the frontend should verify:

* operation status;
* operation UUID;
* Business context;
* Branch context;
* device context;
* payload schema;
* dependency readiness;
* local schema compatibility.

This is local preparation, not authoritative business validation.

---

## 20. Batch Submission

The batch is submitted through the centralized API client.

The synchronization engine must not use:

* ad-hoc `fetch`;
* direct HTTP calls from feature components;
* separate authentication handling.

---

## 21. Batch Result

The backend may return an individual result for each operation.

Example:

```text
Operation A → ACCEPTED
Operation B → ALREADY_APPLIED
Operation C → RETRYABLE
Operation D → CONFLICT
Operation E → REJECTED
```

The frontend must process each result independently.

---

## 22. Partial Success

A partially successful batch must not be treated as an entirely failed batch.

Example:

```text
100 operations
95 accepted
2 already applied
2 retryable
1 conflict
```

Only the relevant operations should remain pending.

---

## 23. Accepted Operation

An accepted operation should:

1. update local synchronization status;
2. store server reference if provided;
3. apply authoritative server result;
4. reconcile dependent local state;
5. invalidate stale cache where necessary;
6. mark operation completed.

---

## 24. Already Applied Operation

If the server reports that the operation was already applied:

```text
ALREADY_APPLIED
```

the frontend should treat the operation as successfully synchronized.

It must not create a duplicate operation.

---

## 25. Retryable Failure

Retryable failures may include:

* network timeout;
* temporary server unavailable;
* temporary infrastructure error;
* retryable 5xx response;
* temporary synchronization service unavailability.

The operation remains pending/retryable.

---

## 26. Retry Policy

Retry should use bounded exponential backoff.

Example:

```text
Attempt 1 → immediate
Attempt 2 → short delay
Attempt 3 → longer delay
Attempt 4 → longer delay
...
```

Jitter should be used where appropriate to prevent synchronized retry storms.

---

## 27. Retry Limits

Retry attempts must be bounded or controlled by a defined long-term retry policy.

An operation must never generate unlimited requests without delay.

---

## 28. Retry and Operation Identity

Retrying the same operation must preserve:

* operation UUID;
* Business UUID;
* Branch UUID;
* device UUID;
* employee context;
* transaction snapshot.

Only transport-level metadata may change.

---

## 29. Permanent Rejection

A rejected operation must be moved to a terminal or explicit recovery state.

Examples:

* invalid business rule;
* invalid authorization;
* expired offline authorization;
* inactive employee;
* invalid Branch;
* deleted Business;
* unsupported operation;
* invalid transaction state.

The frontend must not retry permanent failures indefinitely.

---

## 30. Rejection UI

The user should receive a concise explanation.

Example:

```text
Operation could not be synchronized.

Reason:
The Product is no longer available under the current business rules.

Operation remains available in synchronization history.
```

Technical error details may be available to authorized administrators.

---

## 31. Conflict Definition

A synchronization conflict occurs when the local operation cannot safely be applied because the authoritative server state differs from the assumptions under which the local operation was created.

Examples:

* stale configuration;
* concurrent price change;
* Branch configuration changed;
* Cash Session changed;
* inventory state changed;
* employee access changed;
* server-side version changed.

---

## 32. Conflict Is Not a Network Error

A conflict must not be treated as a temporary network failure.

```text
Network Error
→ Retry

Business Conflict
→ Resolve
```

---

## 33. Conflict State

Recommended local state:

```text
CONFLICT
```

The operation must remain inspectable until resolution.

---

## 34. Conflict Information

The frontend should preserve:

* operation UUID;
* operation type;
* local version;
* server version;
* entity UUID;
* Business;
* Branch;
* actor;
* device;
* conflict code;
* conflict message;
* timestamp;
* server state reference where available.

---

## 35. Conflict Resolution Principle

Conflict resolution must never silently use:

```text
last write wins
```

for important business configuration or financial state.

The system must explicitly determine the authoritative result.

---

## 36. Configuration Conflict

Example:

```text
Local Price Version: 12
Server Price Version: 14
```

The frontend must not simply overwrite version 14 with version 12.

The server remains authoritative.

---

## 37. Configuration Conflict Flow

```text
Offline Change
      ↓
Synchronize
      ↓
Server detects stale version
      ↓
CONFLICT
      ↓
Display local/server state
      ↓
User or authorized process resolves
      ↓
New valid configuration operation
```

---

## 38. Transaction Conflict

Transaction conflicts require special handling.

For example:

```text
Offline Order
     ↓
Local Stock = 2
     ↓
Server Stock = 0
     ↓
Synchronization
     ↓
Business Rule Conflict
```

The frontend must not locally pretend that the server accepted the transaction.

---

## 39. Historical Integrity

If a transaction was locally created with a historical snapshot, synchronization must not rewrite that snapshot merely because current configuration has changed.

The server decides whether the transaction is valid and how it must be recorded.

---

## 40. Price Conflict

Suppose:

```text
Offline Order Price = 30,000
Current Server Price = 35,000
```

The frontend must preserve the offline transaction snapshot.

The synchronization result determines whether the transaction is:

* accepted;
* rejected;
* requires correction.

The frontend must never silently change 30,000 to 35,000.

---

## 41. Inventory Conflict

Inventory synchronization must respect backend stock validation.

The frontend must not solve stock conflicts by:

* increasing local stock;
* deleting the operation;
* retrying indefinitely;
* manually changing quantity without an explicit corrective operation.

---

## 42. Cash Conflict

Cash-related conflicts are financially sensitive.

The frontend must preserve:

* Cash Session;
* employee;
* device;
* amount;
* operation UUID;
* original local timestamp;
* synchronization state.

Final reconciliation is backend-authoritative.

---

## 43. Payment Conflict

Payment synchronization must use idempotency and historical transaction identity.

A timeout must not cause the frontend to create a second payment operation.

---

## 44. Duplicate Protection

The frontend should avoid duplicate local operations, but backend idempotency is the final protection.

Possible duplicate causes:

* double-click;
* refresh;
* retry;
* reconnect;
* multiple tabs;
* repeated batch submission.

---

## 45. Synchronization After Refresh

After application refresh:

1. restore queue;
2. identify incomplete uploads;
3. reset stale `UPLOADING` records safely;
4. retain operation UUID;
5. retry according to policy.

An interrupted request must not automatically generate a new operation.

---

## 46. Interrupted Synchronization

If the application closes during synchronization:

```text
UPLOADING
```

may remain locally.

After restart, the frontend must determine whether the operation:

* was never sent;
* may have been sent;
* was accepted;
* requires retry.

The operation UUID allows the backend to resolve ambiguity safely.

---

## 47. Synchronization Timeout

A timeout does not necessarily mean the server rejected the operation.

The frontend must treat ambiguous timeouts carefully.

Correct approach:

```text
Timeout
   ↓
Retry same operation UUID
   ↓
Server returns ACCEPTED / ALREADY_APPLIED / other result
```

---

## 48. Authentication Failure

If synchronization receives authentication failure:

* pause synchronization;
* refresh/re-authenticate when permitted;
* do not discard pending operations;
* retry only after valid authorization is restored.

---

## 49. Device Revocation

If the device is revoked:

```text
Synchronization
      ↓
DEVICE_REVOKED
      ↓
Stop protected synchronization
      ↓
Preserve recoverable local data
      ↓
Require authorized online recovery
```

The frontend must not bypass device revocation.

---

## 50. Subscription Read-Only State

If the Business becomes read-only:

* synchronization must respect server lifecycle state;
* unsupported modifying operations must not be forced through;
* view/export capabilities remain subject to backend rules;
* local UI must update after authoritative response.

---

## 51. Business Deletion Conflict

If the Business has entered deletion or deleted state:

* pending operations must not resurrect it;
* synchronization must reject operations according to lifecycle rules;
* local data cleanup follows lifecycle policy.

---

## 52. Employee Deactivation

If an employee becomes inactive while offline:

* synchronization validates employee status;
* unauthorized pending operations may be rejected;
* historical attribution remains preserved.

The frontend must not change historical actor identity.

---

## 53. Branch Access Revocation

If an employee loses Branch access while offline:

* local state may remain temporarily available;
* server validation determines synchronization result;
* future unauthorized operations must be blocked after updated authorization is received.

---

## 54. Reconciliation

Reconciliation means updating local state according to authoritative server results.

Example:

```text
Local Order
   ↓
Server Accepted
   ↓
Server Order ID / state
   ↓
Update Local Order
   ↓
Mark Operation Completed
```

---

## 55. Server-to-Local Mapping

Local records may initially use local UUIDs.

After synchronization, the frontend should store the server's authoritative identifier where applicable.

Example:

```text
local_order_id
server_order_id
operation_id
```

These identifiers must remain distinguishable.

---

## 56. Local UUID Preservation

The local UUID must not be replaced in a way that breaks references to pending local operations.

If mapping changes, dependent local references must be updated atomically.

---

## 57. Reconciliation of Related Data

When a parent entity receives authoritative server state, dependent local records must be updated consistently.

Example:

```text
Order
 ├── Order Items
 ├── Payment
 └── Sync Metadata
```

The frontend must avoid states where the parent says synchronized while dependent data still incorrectly appears pending.

---

## 58. Cache Invalidation

After authoritative synchronization:

* stale cache entries should be invalidated;
* dependent queries should refresh;
* local projections should update.

Cache invalidation must not delete pending transactions.

---

## 59. Query Refresh

The state-management layer should receive synchronization results and refresh only affected data.

The frontend should avoid reloading the entire application after every synchronization event.

---

## 60. Synchronization Events

The synchronization engine may publish internal events such as:

```text
SYNC_STARTED
SYNC_PROGRESS
OPERATION_ACCEPTED
OPERATION_RETRYING
OPERATION_CONFLICT
OPERATION_REJECTED
SYNC_COMPLETED
SYNC_FAILED
```

These events should remain internal frontend events unless exposed through a documented integration.

---

## 61. UI Synchronization State

Global UI state may represent:

```text
IDLE
SYNCING
PARTIAL
BLOCKED
FAILED
OFFLINE
```

This state must not replace individual operation states.

---

## 62. User-Facing Synchronization Summary

The UI should provide concise information:

```text
Synced
12

Pending
3

Needs attention
1
```

Users should not be required to inspect technical synchronization internals during normal POS work.

---

## 63. Conflict Notification

A conflict may generate an in-app notification.

The notification must:

* identify that action is required;
* avoid exposing sensitive technical details;
* link to the relevant resolution UI.

---

## 64. Conflict Resolution UI

A conflict resolution screen may contain:

* operation summary;
* local state;
* server state;
* difference;
* reason;
* available actions;
* resolution result.

Example:

```text
Local Price
30,000

Server Price
35,000

Status
Conflict

Action
Review and create new configuration
```

---

## 65. No Blind Merge

The frontend must not automatically merge two versions of important:

* prices;
* financial values;
* inventory quantities;
* Cash Session state;
* permissions;
* subscription state.

Any merge must be explicitly supported by business rules.

---

## 66. Safe Automatic Resolution

Automatic resolution may be used for low-risk technical cases where semantics are deterministic.

Examples:

* duplicate `ALREADY_APPLIED`;
* stale cache replacement;
* retrying temporary network failures.

Automatic resolution must not modify authoritative financial history.

---

## 67. Manual Resolution

Manual resolution may be required for:

* configuration conflicts;
* important Branch overrides;
* permission conflicts;
* financial corrections;
* inventory discrepancies.

Manual resolution must create an auditable corrective operation.

---

## 68. Resolution Operation

A resolved conflict should not mutate the original operation.

Example:

```text
Original Operation
        ↓
CONFLICT
        ↓
Resolution
        ↓
New Operation
```

The new operation references the original operation.

---

## 69. Conflict Audit

Conflict resolution must preserve:

* original operation UUID;
* resolver employee;
* device;
* Business;
* Branch;
* previous state;
* selected resolution;
* resulting operation;
* timestamp.

Audit persistence remains backend-authoritative.

---

## 70. Synchronization History

The frontend may expose synchronization history for authorized users.

It may include:

* operation type;
* operation UUID;
* created time;
* synchronization time;
* status;
* error/conflict code;
* retry count.

---

## 71. Search Synchronization History

Synchronization history should support:

* status;
* operation type;
* date;
* Branch;
* employee;
* device;
* operation UUID.

Large history datasets should use backend search/pagination.

---

## 72. Offline Queue Visibility

Normal POS users should see operationally relevant information rather than raw technical queues.

Administrative users may have additional diagnostic visibility according to permissions.

---

## 73. Background Synchronization

Synchronization should run as background work where the environment permits.

It must not block:

* Product search;
* Order creation;
* Order editing;
* payment UI;
* normal POS navigation.

---

## 74. Synchronization Concurrency

The synchronization engine should limit concurrent batches.

Too many concurrent synchronization requests may cause:

* duplicate work;
* database contention;
* rate limiting;
* battery/CPU pressure;
* network congestion.

A bounded concurrency model is required.

---

## 75. Priority

Recommended synchronization priority:

1. critical business transactions;
2. payment/cash operations;
3. Order state changes;
4. inventory operations;
5. configuration;
6. cache refresh;
7. non-critical metadata.

Exact priority follows backend business rules.

---

## 76. Fairness

High-priority synchronization must not permanently starve lower-priority operations.

The engine should use bounded queues and controlled scheduling.

---

## 77. Synchronization Pause

Synchronization may be paused when:

* device is revoked;
* authorization expires;
* storage integrity is compromised;
* authentication is unavailable;
* application is in a critical recovery state.

It should resume only after required conditions are restored.

---

## 78. Storage Pressure

If local storage is near capacity:

1. stop non-essential cache growth;
2. clean expired cache;
3. preserve pending transactions;
4. warn user if required;
5. block new offline transactions if durable persistence cannot be guaranteed.

---

## 79. Synchronization and Local Cleanup

Completed operations may eventually be removed from the local queue according to retention policy.

Before deletion, the frontend should ensure:

* final synchronization state;
* server result recorded;
* required references retained;
* audit/diagnostic requirements satisfied.

---

## 80. No Premature Cleanup

The frontend must never remove an operation merely because:

* it is old;
* it failed once;
* the application restarted;
* the user logged out;
* the network was unavailable.

Retention rules determine cleanup.

---

## 81. Logging

Synchronization logs should include safe technical context:

* operation UUID;
* Business UUID;
* Branch UUID;
* device UUID;
* status;
* attempt;
* error code;
* duration.

Sensitive payload data must not be logged.

---

## 82. Metrics

The frontend should measure:

* pending operation count;
* synchronization success rate;
* retry count;
* conflict count;
* rejection count;
* batch duration;
* operation latency;
* queue age;
* storage errors;
* synchronization pauses.

---

## 83. Synchronization SLOs

Target values:

| Metric                                         |      Target |
| ---------------------------------------------- | ----------: |
| Normal sync batch preparation                  | p95 ≤200 ms |
| Normal sync API round trip                     |    p95 ≤1 s |
| Accepted operation local reconciliation        | p95 ≤200 ms |
| Synchronization UI update                      | p95 ≤100 ms |
| Duplicate operation prevention                 |     ≥99.99% |
| Critical operation synchronization persistence |     ≥99.99% |
| Retry scheduling correctness                   |     ≥99.99% |
| Conflict state preservation                    |        100% |
| Pending transaction loss                       |          0% |
| Cross-Business synchronization isolation       |        100% |
| Cross-Branch unauthorized synchronization      |        100% |

Network-dependent measurements exclude unavoidable external network latency where appropriate.

---

## 84. Performance Protection

Synchronization must not consume resources needed by POS.

The frontend should:

* limit concurrent requests;
* batch operations;
* yield between large processing steps;
* avoid expensive full-state re-rendering;
* avoid rebuilding large local indexes unnecessarily.

---

## 85. Main Thread Protection

Large synchronization results should be processed in bounded chunks.

If browser capabilities permit, heavy processing may use a worker.

The synchronization engine must not freeze the POS interface.

---

## 86. Large Batch Processing

If a batch contains many operations:

```text
Batch
 ↓
Process bounded chunk
 ↓
Update local state
 ↓
Yield
 ↓
Continue
```

The exact chunk size is implementation-dependent and must be measured.

---

## 87. Failure Recovery

After unexpected synchronization failure:

1. preserve pending operations;
2. reset stale processing state safely;
3. record failure;
4. schedule retry;
5. keep POS available where possible.

---

## 88. Application Crash

If the application crashes during synchronization:

* pending operations must remain durable;
* operation UUIDs remain unchanged;
* processing state must recover safely;
* duplicate synchronization must be handled by backend idempotency.

---

## 89. Network Recovery

When network connectivity returns:

```text
Offline
   ↓
Connectivity Detected
   ↓
Backend Reachability Check
   ↓
Authentication/Device Validation
   ↓
Synchronize Transactions
   ↓
Synchronize Configuration
   ↓
Refresh Cache
```

---

## 90. Configuration Synchronization

Configuration synchronization occurs after higher-priority transaction synchronization.

The frontend should retrieve:

* latest valid menu;
* latest pricing;
* Branch configuration;
* relevant permissions;
* supported operational configuration.

---

## 91. Configuration Conflict

If local configuration changes conflict with server state:

* preserve local operation;
* show conflict;
* do not overwrite server state silently;
* require authorized resolution where needed.

---

## 92. Transaction Before Configuration

Example:

```text
Offline Order created with Price Version A
        ↓
Reconnect
        ↓
Order synchronization
        ↓
Configuration synchronization
        ↓
New Price Version B
```

The Order must retain Price Version A.

---

## 93. Reconciliation Ordering

Recommended order:

```text
1. Transaction result
2. Financial result
3. Inventory result
4. Configuration result
5. Cache refresh
6. Non-critical metadata
```

The exact ordering may vary by operation dependencies.

---

## 94. Local State Rebuild

If synchronization changes authoritative state substantially, the frontend may rebuild affected projections.

It must avoid rebuilding unrelated application state.

---

## 95. Reconnect UX

When reconnecting, the user should see a lightweight status:

```text
Connection restored
Synchronizing 8 pending operations...
```

The user should still be able to continue supported POS work.

---

## 96. Conflict UX

Conflicts should not be hidden.

Example:

```text
1 operation needs attention
```

The UI should allow the authorized user to inspect it without exposing unnecessary technical complexity.

---

## 97. Offline Session End

When the user logs out:

* pending operations must not be discarded;
* protected local data remains appropriately secured;
* synchronization may continue only if allowed by the device/application model;
* otherwise operations remain safely queued.

---

## 98. Employee Switching

If a shared POS device supports employee switching:

* employee context must change;
* permissions must be recalculated;
* pending operations must retain their original employee context;
* one employee must never become the actor of another employee's pending transaction.

---

## 99. Branch Switching

When Branch changes:

* synchronization context must change;
* pending operations remain associated with their original Branch;
* Branch-specific cache is isolated;
* operations from one Branch must never be synchronized under another Branch context.

---

## 100. Business Switching

Business switching must:

* isolate local storage context;
* prevent cross-Business queue mixing;
* reload authorization;
* reload configuration;
* preserve pending operations under their original Business.

---

## 101. Multi-Tab Synchronization

If multiple tabs share the same local storage:

* only one synchronization worker should claim an operation;
* operation claims should have bounded leases;
* stale claims must recover safely;
* backend idempotency remains final protection.

---

## 102. Sync Claim

A local operation may have:

```text
claimed_at
claimed_by
claim_expires_at
```

This is coordination metadata, not authoritative business state.

---

## 103. Offline Schema Migration

Synchronization must not process operations whose local schema cannot be safely interpreted.

The frontend should migrate or reject them explicitly according to the migration strategy.

---

## 104. API Version Compatibility

The synchronization engine must use the API contract supported by the installed frontend version.

Breaking synchronization changes require:

* API compatibility plan;
* migration;
* versioning;
* rollback strategy.

---

## 105. Security Rules

The synchronization layer must never:

* trust client Business UUID;
* trust client Branch UUID;
* trust employee permissions;
* trust device trust state;
* extend offline authorization;
* bypass subscription state;
* disable signature validation;
* expose security secrets;
* modify historical server records.

---

## 106. AI-Agent Development Rules

AI coding agents must:

1. Use the centralized synchronization engine.
2. Reuse the existing API client.
3. Reuse operation UUID infrastructure.
4. Never create a second retry system.
5. Never implement silent last-write-wins.
6. Never discard conflicts.
7. Never generate a new UUID for a transport retry.
8. Never treat local state as authoritative after synchronization.
9. Never bypass Business/Branch scope.
10. Never bypass device trust or subscription rules.
11. Preserve employee attribution.
12. Preserve historical snapshots.
13. Add synchronization tests for every new offline-capable operation.
14. Add retry tests.
15. Add duplicate-request tests.
16. Add conflict tests.
17. Add recovery tests.

---

## 107. Testing Strategy

### Unit Tests

Test:

* queue selection;
* ordering;
* dependencies;
* retry calculation;
* state transitions;
* conflict classification;
* result processing.

### Integration Tests

Test:

* API synchronization;
* authentication;
* idempotency;
* partial batches;
* reconciliation.

### End-to-End Tests

Test:

* offline creation;
* reconnect;
* synchronization;
* duplicate retry;
* conflict;
* recovery.

---

## 108. Critical E2E Scenarios

At minimum:

1. Create Order offline.
2. Refresh application.
3. Restore pending Order.
4. Reconnect.
5. Synchronize successfully.
6. Repeat same request.
7. Receive `ALREADY_APPLIED`.
8. Continue without duplicate Order.

Additional:

1. Create offline Order.
2. Change server configuration.
3. Reconnect.
4. Synchronize.
5. Preserve historical snapshot.
6. Show current configuration after synchronization.

---

## 109. Conflict E2E Scenario

```text
Device A
   ↓
Offline configuration change

Device B
   ↓
Online configuration change

Device A
   ↓
Reconnect

Server
   ↓
Version conflict

Frontend
   ↓
CONFLICT

Authorized User
   ↓
Resolve

New Operation
   ↓
Server
```

---

## 110. Recovery E2E Scenario

```text
Offline Operation
      ↓
Synchronization Started
      ↓
Application Crashes
      ↓
Restart
      ↓
Recover Operation
      ↓
Retry Same UUID
      ↓
ALREADY_APPLIED / ACCEPTED
      ↓
Complete
```

---

## 111. Related Architecture

This document depends on:

* `24_Frontend_Offline_Storage_and_Local_Persistence_Architecture.md`
* `23_Frontend_API_Client_and_Data_Access_Architecture.md`
* `22_Frontend_State_Management_and_Data_Flow.md`

It integrates with:

* Backend synchronization;
* backend transaction management;
* backend audit/history;
* backend security;
* database synchronization model.

---

## 112. Recommended Structure

```text
frontend/
└── src/
    └── offline/
        ├── synchronization/
        │   ├── syncEngine.ts
        │   ├── batchBuilder.ts
        │   ├── operationSelector.ts
        │   ├── dependencyResolver.ts
        │   ├── retryPolicy.ts
        │   ├── resultProcessor.ts
        │   ├── reconciliation.ts
        │   ├── conflictResolver.ts
        │   ├── syncCoordinator.ts
        │   └── syncEvents.ts
        │
        ├── queue/
        │   ├── operationQueue.ts
        │   ├── operationState.ts
        │   └── operationClaims.ts
        │
        ├── recovery/
        │   ├── interruptedSync.ts
        │   ├── storageRecovery.ts
        │   └── migrationRecovery.ts
        │
        └── telemetry/
            └── synchronizationMetrics.ts
```

---

## 113. System Invariants

The following invariants apply to frontend synchronization:

1. Backend is authoritative.
2. Synchronization is centralized.
3. Features do not implement independent synchronization engines.
4. Network availability is only a synchronization hint.
5. Backend reachability determines actual synchronization success.
6. Operation UUID remains stable across retries.
7. Corrective operations receive new operation UUIDs.
8. Duplicate synchronization must be safely handled.
9. `ALREADY_APPLIED` is treated as successful finalization.
10. Partial batch results are processed individually.
11. Batch size is bounded.
12. Synchronization respects dependencies.
13. Dependency failure blocks dependent operations appropriately.
14. Retryable errors use bounded retry behavior.
15. Permanent failures are not retried indefinitely.
16. Conflicts are distinct from network errors.
17. Conflicts are preserved.
18. Important conflicts are not silently resolved.
19. Last-write-wins is prohibited for important business state.
20. Server state is authoritative after reconciliation.
21. Historical transaction snapshots are preserved.
22. Price changes do not rewrite synchronized historical transactions.
23. Inventory conflicts are server-authoritative.
24. Cash conflicts are server-authoritative.
25. Payment retries preserve operation identity.
26. Interrupted synchronization does not generate a new operation UUID.
27. Authentication failures pause synchronization safely.
28. Device revocation cannot be bypassed.
29. Subscription read-only state cannot be bypassed.
30. Business deletion cannot be bypassed.
31. Employee deactivation is validated server-side.
32. Branch access is validated server-side.
33. Business context is preserved for every operation.
34. Branch context is preserved for every operation.
35. Employee context is preserved for every operation.
36. Device context is preserved for every operation.
37. Local state does not become authoritative after synchronization.
38. Server results update local state.
39. Affected cache entries are invalidated after reconciliation.
40. Pending transactions are never removed by cache cleanup.
41. Synchronization does not block normal POS operation unnecessarily.
42. Synchronization concurrency is bounded.
43. Synchronization priority protects critical business transactions.
44. Lower-priority operations are not permanently starved.
45. Synchronization can pause for security or storage failures.
46. Reconnect does not assume successful synchronization.
47. Configuration synchronization follows transaction synchronization priority.
48. Offline transactions retain their original configuration snapshot.
49. Configuration conflicts are explicit.
50. Financial conflicts require authoritative resolution.
51. Conflict resolution creates an auditable corrective operation.
52. Original conflicted operations remain preserved.
53. Synchronization history remains inspectable.
54. Sensitive synchronization payloads are not logged.
55. Synchronization metrics contain safe technical information only.
56. Local queue survives normal application restart.
57. Local queue survives normal page refresh.
58. Multi-tab synchronization cannot safely process the same operation twice.
59. Backend idempotency remains the final duplicate protection.
60. Storage pressure never prioritizes cache over pending transactions.
61. Schema migrations preserve pending operations.
62. Unsupported schema versions are handled explicitly.
63. API version compatibility is required for synchronization.
64. AI agents cannot create alternative synchronization systems.
65. AI agents cannot silently discard conflicts.
66. AI agents cannot bypass synchronization security.
67. AI agents must add tests for new offline operations.
68. Synchronization failures remain observable.
69. Synchronization recovery is deterministic.
70. Synchronization preserves historical integrity over convenience.

---

## Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/10_Order_Management_UI.md`
* `docs/04_Architecture/07_Frontend/11_Cash_Register_and_Cash_Session_UI.md`
* `docs/04_Architecture/07_Frontend/20_Offline_Mode_and_Synchronization_UI.md`
* `docs/04_Architecture/07_Frontend/21_Settings_and_Business_Configuration_UI.md`
* `docs/04_Architecture/07_Frontend/22_Frontend_State_Management_and_Data_Flow.md`
* `docs/04_Architecture/07_Frontend/23_Frontend_API_Client_and_Data_Access_Architecture.md`
* `docs/04_Architecture/07_Frontend/24_Frontend_Offline_Storage_and_Local_Persistence_Architecture.md`

### Backend

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/04_Architecture/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## Status

**Frontend Architecture:** Proposed

**Version:** 1.0

**Current Document:** `25_Frontend_Offline_Synchronization_and_Conflict_Resolution.md`

**Previous Document:** `24_Frontend_Offline_Storage_and_Local_Persistence_Architecture.md`

**Next Document:** `26_Frontend_Error_Handling_and_Recovery_Architecture.md`

