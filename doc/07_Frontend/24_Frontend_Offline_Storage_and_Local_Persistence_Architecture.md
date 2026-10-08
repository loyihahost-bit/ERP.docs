# Frontend Offline Storage and Local Persistence Architecture

**Document ID:** FA-24
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`

---

## 1. Purpose

This document defines the frontend offline storage and local persistence architecture for FastFood ERP.

The architecture allows supported Branch operations to continue when the internet connection is temporarily unavailable while preserving:

* security;
* transaction integrity;
* Business isolation;
* Branch isolation;
* historical integrity;
* synchronization correctness;
* idempotency;
* device trust;
* subscription restrictions;
* performance.

Offline operation is not a separate business system.

It is a temporary execution mode of the same FastFood ERP business model.

---

## 2. Core Principle

The primary principle is:

> Offline storage exists to preserve authorized operational continuity, not to create an independent source of truth.

The authoritative state remains the backend.

```text id="p7j4m2"
Server
   ↓
Authoritative State
   ↓
Trusted Device
   ↓
Encrypted Local State
   ↓
Offline Operation
   ↓
Synchronization
   ↓
Server Validation
   ↓
Authoritative Final State
```

---

## 3. Offline Scope

Only explicitly supported operations may work offline.

Potentially supported:

* POS;
* Order creation;
* supported Order modifications;
* supported Order acceptance;
* supported cash operations;
* required menu/product reference data;
* limited configuration data;
* synchronization queue.

The exact list of offline-capable commands is defined by the corresponding System Analysis and Backend documents.

---

## 4. Offline Non-Scope

The following should normally require online access unless explicitly enabled by future architecture:

* Business creation;
* subscription management;
* employee creation;
* permission administration;
* role configuration;
* sensitive security configuration;
* trusted-device registration;
* major configuration changes;
* large reports;
* XLSX generation;
* administrative exports;
* destructive lifecycle operations.

The frontend must not automatically make an online-only feature offline-capable.

---

## 5. Trusted Device Requirement

Offline operation is available only to a previously registered and trusted device.

The device must first be:

1. connected online;
2. authenticated;
3. registered;
4. verified;
5. associated with the appropriate Business;
6. authorized for offline operation.

A new device cannot start offline operation before completing the required online trust process.

---

## 6. Device Identity

Each trusted device has a unique device UUID.

The device UUID is used for:

* device identification;
* synchronization;
* audit context;
* offline authorization binding;
* local data isolation.

The device UUID is not authentication.

Possession of the UUID must never be sufficient to authorize an employee.

---

## 7. Offline Authorization

Offline authorization must be:

* signed;
* time-bounded;
* device-bound;
* Business-bound;
* employee/context-bound where required;
* validated locally;
* revocable through the online system.

The frontend must not generate or extend offline authorization.

---

## 8. Offline Grace Period

The current offline authorization grace period is:

**3 days.**

After the offline authorization expires, supported offline operations must stop unless the device successfully reconnects and receives renewed authorization.

The grace period must be centrally configurable by the backend/security architecture and must not be hardcoded across frontend features.

---

## 9. Offline Authorization State

The frontend should represent:

```text id="l8v1j4"
NOT_AVAILABLE
AVAILABLE
ACTIVE
EXPIRING
EXPIRED
REVOKED
INVALID
```

The UI should warn the user before expiry where appropriate.

---

## 10. Local Storage Categories

Local persistence should be divided into clear categories.

```text id="r4k2s8"
Local Persistence
│
├── Secure Offline Authorization
├── Offline Transaction Queue
├── Operational Reference Cache
├── Configuration Cache
├── UI Preferences
├── Synchronization Metadata
└── Temporary Local State
```

Each category has different security and lifecycle requirements.

---

## 11. Secure Offline Authorization Storage

Offline authorization material is sensitive.

It must be stored using the approved secure storage mechanism available to the application environment.

The frontend must not store it as ordinary unprotected UI state.

The implementation must follow the security architecture for:

* encryption;
* device binding;
* key protection;
* expiration;
* revocation.

---

## 12. Offline Transaction Storage

Offline business operations require durable local persistence.

Examples:

* offline Order;
* offline Order Item;
* supported payment operation;
* supported inventory-related transaction;
* cash operation;
* synchronization metadata.

The queue must survive normal:

* page reload;
* application restart;
* temporary network loss.

---

## 13. Local Transaction Identity

Every offline transaction must have:

* operation UUID;
* Business UUID;
* Branch UUID;
* device UUID;
* employee context where applicable;
* creation timestamp;
* local sequence/order metadata where required;
* synchronization status.

The operation UUID is the primary idempotency identity for synchronization.

---

## 14. Operation UUID

The frontend must generate the operation UUID before durable persistence of a retryable offline operation.

Example:

```text id="0e7q8n"
Create Order
    ↓
Generate Operation UUID
    ↓
Persist locally
    ↓
Execute locally
    ↓
Synchronize later
```

The operation UUID must not change during retries.

---

## 15. Local Sequence

The application may maintain a local monotonic sequence for operational ordering.

Example:

```text id="5q7d9k"
Local Sequence
1001
1002
1003
1004
```

The local sequence is not a replacement for the server operation UUID.

The server remains authoritative for global ordering.

---

## 16. Local Business Scope

Every persisted Business-scoped record must contain or be unambiguously associated with the correct Business context.

Example:

```text id="6m2z1v"
business_id
branch_id
device_id
```

The frontend must never reuse local records from another Business.

---

## 17. Local Branch Scope

Branch-specific data must retain Branch identity.

Example:

```text id="b4y6c8"
Business A
├── Branch A
│   └── Local Menu
└── Branch B
    └── Local Menu
```

Branch A data must never be presented as Branch B data.

---

## 18. Local Employee Scope

Where local state depends on employee identity, the record must preserve the relevant employee context.

Examples:

* created by employee;
* cashier;
* waiter;
* approved operation;
* local session.

Employee context must not be used to bypass backend authorization after synchronization.

---

## 19. Local Data Classification

Local data should be classified as:

```text id="j6q2m8"
PUBLIC_REFERENCE
OPERATIONAL
SENSITIVE
SECURITY_SENSITIVE
TRANSACTIONAL
```

The storage mechanism and retention period should depend on classification.

---

## 20. Public Reference Data

Examples:

* Product names;
* categories;
* menu images where permitted;
* non-sensitive display metadata.

This data may be cached locally when needed for POS operation.

It remains non-authoritative.

---

## 21. Operational Data

Examples:

* current menu;
* current Branch configuration;
* current Cash Session context;
* POS reference data.

Operational data may be stored locally for offline continuity.

It must include freshness/version information.

---

## 22. Transactional Data

Transactional data includes:

* Orders;
* Order Items;
* payments where offline payment is supported;
* cash operations;
* synchronization records.

Transactional data requires durable persistence and strict integrity controls.

---

## 23. Security-Sensitive Data

Security-sensitive data includes:

* offline authorization;
* cryptographic material;
* session/security metadata;
* device trust state.

It must not be treated as ordinary application cache.

---

## 24. Local Database

A structured local database should be used for substantial offline state.

The exact browser technology is an implementation decision, but it must support:

* durable storage;
* indexed queries;
* atomic local transactions;
* bounded growth;
* versioned schema;
* migration;
* efficient lookup.

A browser key-value store may be used for small non-critical preferences where appropriate.

---

## 25. Local Storage Abstraction

Features must not directly access browser storage APIs.

Preferred architecture:

```text id="z6p8x3"
Feature
   ↓
Offline Repository
   ↓
Local Storage Abstraction
   ↓
Browser Storage
```

This allows the underlying storage technology to change without rewriting business features.

---

## 26. Offline Repository

The Offline Repository provides operations such as:

```text id="v7q3m1"
saveOrder()
getOrder()
saveOperation()
getPendingOperations()
updateSyncStatus()
saveConfiguration()
getConfiguration()
clearExpiredData()
```

Repositories must enforce local scope and persistence rules.

---

## 27. Local Transaction Boundary

Related local changes must be persisted atomically where required.

Example:

```text id="n5r8c2"
Offline Order
+
Order Items
+
Operation Metadata
+
Sync Metadata
```

These records should not enter a partially persisted state.

---

## 28. Local Atomicity

If a local operation fails before persistence completes:

* incomplete records must not appear as valid transactions;
* the operation should remain retryable or be marked failed;
* corrupted partial state must not be treated as authoritative.

---

## 29. Offline Order Creation

A typical offline Order flow:

```text id="7k3v1m"
Select Product
      ↓
Read Local Menu
      ↓
Read Local Price Configuration
      ↓
Create Draft
      ↓
Generate Operation UUID
      ↓
Persist Order
      ↓
Persist Order Items
      ↓
Mark Pending Sync
      ↓
Continue POS
```

The Order remains pending until synchronization confirms server processing.

---

## 30. Offline Order Snapshot

The offline Order must capture the applicable transaction snapshot.

Examples:

* Product UUID;
* Product name where needed;
* selling price;
* quantity;
* discount;
* configuration version;
* Recipe Version where required;
* Set Version where required.

Current online configuration must not rewrite an already-created offline transaction.

---

## 31. Offline Price Integrity

Suppose:

```text id="8s6h2w"
Offline Price = 30,000

Later Server Price = 35,000
```

The offline transaction retains the 30,000 snapshot.

During synchronization, the backend validates whether the transaction is acceptable under the defined offline rules.

The frontend must not silently change the transaction to 35,000.

---

## 32. Offline Menu Changes

If a menu change occurs on the server while a device is offline:

* the device continues using the last valid authorized local configuration;
* it does not assume the server's new configuration;
* synchronization later resolves the configuration difference.

---

## 33. Offline Configuration Version

Every cached operational configuration should have a version.

Example:

```text id="5j2m7x"
Local Menu Version = 17
Server Menu Version = 19
```

The device must be able to detect that its local configuration is stale.

---

## 34. Stale Configuration

Stale configuration does not automatically invalidate already-created offline transactions.

Instead:

```text id="m4x7q1"
Existing Offline Transaction
→ Preserve Snapshot

New Offline Operation
→ Validate Against Current Local Authorization/Configuration

Reconnect
→ Server Determines Final Validity
```

---

## 35. Local Configuration Cache

Configuration cache may include:

* menu;
* prices;
* Branch configuration;
* POS configuration;
* printer routing;
* supported operational settings.

Sensitive administrative configuration should not automatically be included.

---

## 36. Configuration Cache Versioning

Configuration cache entries should contain:

```text id="j8n3s5"
configuration_id
version
Business
Branch
effective_at
status
cached_at
expires_at
```

This allows the UI to distinguish current, stale and expired data.

---

## 37. Local Cache Expiration

Cached operational data should have explicit expiration/freshness rules.

Expiration does not necessarily mean immediate deletion.

It may mean:

```text id="p4r6t8"
Fresh
 ↓
Stale
 ↓
Expired
```

Offline authorization and ordinary reference cache have different expiration semantics.

---

## 38. Cache vs Transaction Queue

The architecture must clearly distinguish:

```text id="x6v1k9"
Cache
→ Can be discarded and refetched

Transaction Queue
→ Must not be discarded until safely finalized
```

A cache cleanup process must never delete pending business transactions.

---

## 39. Synchronization Metadata

Each queued operation should track:

```text id="e3s8w5"
operation_id
status
attempt_count
created_at
last_attempt_at
next_retry_at
last_error_code
server_reference
```

Additional fields may be added as required.

---

## 40. Synchronization States

Recommended states:

```text id="7p5q2m"
PENDING
UPLOADING
ACCEPTED
RETRYABLE_FAILURE
CONFLICT
REJECTED
EXPIRED
COMPLETED
```

The exact state machine follows the backend synchronization contract.

---

## 41. Pending State

`PENDING` means:

* operation is safely stored locally;
* it has not yet been successfully submitted to the backend.

The UI may display the operation as pending synchronization.

---

## 42. Uploading State

`UPLOADING` means the operation is currently being transmitted.

The frontend must avoid creating a second operation merely because an upload is in progress.

---

## 43. Accepted State

`ACCEPTED` means the backend has accepted and applied or safely recorded the operation according to the synchronization contract.

The frontend may finalize local synchronization metadata.

---

## 44. Already Applied Result

If the backend identifies the same operation UUID as previously applied:

```text id="c8v3n1"
ALREADY_APPLIED
```

The frontend should treat this as successful finalization, not as a new transaction.

---

## 45. Retryable Failure

Retryable failures include temporary conditions such as:

* network interruption;
* temporary server unavailability;
* temporary infrastructure failure.

Retries must use the same operation UUID.

---

## 46. Conflict

A conflict means the operation cannot be safely accepted without additional resolution.

The local record must remain available for:

* inspection;
* resolution;
* audit;
* retry with the appropriate process.

The frontend must not silently discard the operation.

---

## 47. Rejected Operation

A rejected operation is a permanent or business-level failure.

Examples:

* invalid authorization;
* expired offline authorization;
* invalid Business lifecycle;
* invalid Branch context;
* business rule violation.

The frontend must preserve enough information to explain the result.

---

## 48. Expired Operation

An operation may become expired according to synchronization or offline policy.

Expired operations must not be silently retried indefinitely.

The UI should indicate that user action or administrative resolution may be required.

---

## 49. Retry Strategy

Retry must use bounded exponential backoff or the server-provided retry policy.

Example:

```text id="3q8m6x"
Attempt 1 → immediate
Attempt 2 → delayed
Attempt 3 → longer delay
...
```

Retry attempts must have a defined maximum or controlled long-term retry strategy.

---

## 50. No Infinite Retry

An operation must never retry forever without:

* backoff;
* maximum attempts or controlled retention;
* visible failure state;
* cleanup/resolution policy.

---

## 51. Synchronization Priority

Synchronization should follow:

```text id="m8q4t1"
Offline Transactions
       ↓
Critical Operational Data
       ↓
Configuration
       ↓
Cache Refresh
       ↓
Non-critical Background Data
```

Transaction synchronization has priority over configuration synchronization.

---

## 52. Batch Synchronization

The frontend may submit operations in batches.

Current backend synchronization design supports bounded batches.

Recommended batch size:

**50–100 operations.**

The exact limit must follow backend/API configuration.

---

## 53. Partial Batch Result

A batch may contain mixed outcomes.

Example:

```text id="r5x9k2"
100 operations
95 accepted
3 retryable
1 conflict
1 rejected
```

The frontend must update each operation individually.

The entire batch must not be marked failed.

---

## 54. Synchronization Ordering

Where business dependencies exist, the frontend must preserve operation ordering.

Example:

```text id="a6q8m3"
Order Created
     ↓
Order Accepted
     ↓
Payment
```

The frontend must not synchronize Payment before the required Order state exists.

---

## 55. Local Dependency Graph

Operations may contain dependency information.

Example:

```text id="y3n7q9"
Operation B
depends_on:
Operation A
```

The synchronization engine must respect dependencies.

---

## 56. Offline Payment

Offline payment is permitted only if explicitly supported by the backend/payment architecture.

The frontend must not assume that every payment method is offline-capable.

If offline payment is supported, the operation must use the same:

* operation UUID;
* durable storage;
* synchronization;
* duplicate prevention;
* historical snapshot principles.

---

## 57. Offline Cash Session

If Cash Session operations are supported offline, local state must preserve:

* Cash Register;
* Cash Session;
* employee;
* device;
* opening state;
* cash amounts;
* handover information where supported;
* operation UUID;
* synchronization state.

Final cash reconciliation remains backend-authoritative.

---

## 58. Offline Inventory

If an inventory-related operation is supported offline, the frontend must use the latest authorized local state.

It must not assume that local stock is globally authoritative.

Synchronization must allow the backend to detect:

* insufficient stock;
* conflicting changes;
* stale configuration;
* invalid operations.

---

## 59. Local Stock Display

Offline stock display must clearly indicate that it is local/stale where appropriate.

Example:

```text id="4z7m2q"
Stock: 14
Status: Last synchronized
```

The UI must not present stale stock as guaranteed real-time stock.

---

## 60. Local Menu Search

POS Product search should operate against the local authorized menu/reference cache when offline.

The search should remain fast and lightweight.

Large unrelated datasets must not be loaded solely to support offline search.

---

## 61. Local Printer State

Printer availability may be maintained locally where required for POS continuity.

However:

* printer state is not transaction authority;
* print failure does not roll back accepted business transactions;
* print jobs should have independent status.

---

## 62. Local Notifications

Offline notification state may be queued locally where useful.

Authoritative Business notifications should come from the backend after synchronization/reconnection.

The frontend must not fabricate critical security or financial notifications as authoritative events.

---

## 63. Local Audit Context

Offline operations must preserve enough metadata for the backend to create authoritative audit records after synchronization.

Example:

```text id="u5q2k8"
operation_id
employee_id
business_id
branch_id
device_id
created_at
source = OFFLINE
```

The frontend must not modify historical audit records.

---

## 64. Local Clock

Local device time may be used for UI purposes and operation metadata.

However, the frontend must not treat local time as authoritative server time.

Important synchronization validation remains backend-controlled.

---

## 65. Clock Rollback

The frontend should detect obvious local clock anomalies where possible and surface them to the security/synchronization layer.

Examples:

```text id="p8s4m1"
Last known time: 14:00
Current device time: 11:00
```

The frontend must not simply extend offline authorization because the device clock changed.

---

## 66. Offline Authorization Expiry

When local authorization expires:

```text id="h2k6q9"
Offline Authorization
      ↓
EXPIRED
      ↓
Stop New Offline Operations
      ↓
Allow Reconnect
      ↓
Online Validation
```

Existing pending transactions must remain safely stored for synchronization according to backend policy.

---

## 67. Device Revocation

If a device is revoked while offline, the device may not immediately know.

After reconnection:

1. server validates device;
2. device trust state is updated;
3. protected offline access is revoked;
4. future offline operations are blocked.

The frontend must not override server revocation.

---

## 68. Employee Deactivation

If an employee is deactivated while the device is offline, the device may temporarily retain previously authorized local context.

After reconnection, the server determines whether pending/new operations remain valid.

The frontend must not treat old local permissions as permanently valid.

---

## 69. Subscription Expiration

Offline operation must not bypass subscription restrictions.

If the Business becomes read-only while the device is offline, synchronization must enforce the server's lifecycle/entitlement rules.

The frontend must not extend Business access locally.

---

## 70. Business Deletion

If a Business enters deletion lifecycle while a device is offline:

* pending operations must not resurrect the Business;
* synchronization must respect server lifecycle state;
* local data must be cleaned according to deletion policy;
* protected data must not remain indefinitely.

---

## 71. Local Data Retention

Local data must have defined retention policies.

At minimum:

```text id="t4q8m6"
Pending Transactions
→ retain until finalized

Temporary Cache
→ bounded TTL

Expired Configuration
→ cleanup according to policy

Completed Sync Metadata
→ bounded retention

Sensitive Security Data
→ shortest practical retention
```

---

## 72. Cache Cleanup

Cleanup must:

* run safely;
* never remove pending operations;
* never remove required offline authorization prematurely;
* respect Business/Branch scope;
* avoid blocking POS operation.

---

## 73. Storage Quota

Browser/local storage capacity is finite.

The application must detect storage pressure where possible.

When storage becomes constrained:

1. stop non-essential cache growth;
2. remove expired cache;
3. preserve pending transactions;
4. notify the user if action is required;
5. prevent unsafe offline operation if durable storage cannot be guaranteed.

---

## 74. Storage Failure

If local persistence fails during an offline business operation:

* the operation must not be presented as durably accepted;
* the UI must clearly indicate failure;
* the user must not be encouraged to continue as if synchronization is guaranteed.

For critical transactions, failure to persist locally must block completion of the offline operation.

---

## 75. Browser Refresh

After refresh, the application must restore:

* valid offline authorization state;
* pending transaction queue;
* required operational cache;
* synchronization state.

Temporary UI state may be discarded.

---

## 76. Application Restart

After application restart:

```text id="m7p4q2"
Open Application
      ↓
Load Secure Offline Context
      ↓
Validate Local Authorization
      ↓
Load Pending Queue
      ↓
Load Required Operational Cache
      ↓
Start Synchronization if Online
```

---

## 77. Browser Tab Concurrency

If multiple tabs/windows can access the same Business/Branch state, the frontend must coordinate local persistence.

It must prevent:

* duplicate synchronization;
* conflicting local sequence generation;
* duplicate operations;
* simultaneous incompatible local migrations.

The exact browser coordination mechanism is an implementation decision.

---

## 78. Local Schema Versioning

Local storage schema must be versioned.

Example:

```text id="c6v9p1"
Schema 1
   ↓
Schema 2
   ↓
Schema 3
```

Schema migrations must be deterministic and tested.

---

## 79. Local Migration Failure

If a local schema migration fails:

* the application must not silently use incompatible data;
* the failure must be logged safely;
* pending transaction integrity must be preserved;
* recovery should follow a defined migration strategy.

Destructive local cleanup must not be the default recovery mechanism when it could delete pending transactions.

---

## 80. Encryption at Rest

Sensitive offline data must be encrypted at rest according to the security architecture.

Encryption must cover data where required, including:

* offline authorization;
* pending sensitive transactions;
* security metadata;
* sensitive Business information.

The exact cryptographic implementation belongs to the security architecture.

---

## 81. Key Management

Encryption keys must not be hardcoded in frontend source.

The frontend must use the approved secure key-management mechanism available to the application environment.

A device UUID is not itself an encryption key.

---

## 82. Data Integrity

Encrypted local storage must also provide integrity protection.

The application must detect:

* tampering;
* malformed records;
* invalid signatures;
* corrupted synchronization metadata.

Corrupted data must not be treated as valid business state.

---

## 83. Local Access Control

Local storage access must be restricted by application state.

For example:

```text id="g7m2k4"
Logged In / Authorized
→ access operational state

Logged Out
→ protected state unavailable

Device Revoked
→ protected offline state invalidated
```

---

## 84. No Secret Exposure

The frontend must never expose in ordinary logs or UI:

* encryption keys;
* offline authorization signatures;
* authentication secrets;
* session credentials.

Debug tools must also avoid intentionally printing sensitive state.

---

## 85. Local Data Export

Users must not be able to arbitrarily export internal offline database contents.

Business exports should use the official backend export mechanism.

---

## 86. Offline Data Recovery

Recovery must prioritize pending transaction preservation.

Preferred recovery order:

```text id="s4n7m9"
Validate Storage
      ↓
Recover Transaction Queue
      ↓
Recover Synchronization Metadata
      ↓
Recover Operational Cache
      ↓
Recover UI Preferences
```

---

## 87. Corrupted Cache Recovery

Corrupted non-critical cache may be discarded and refetched.

Example:

```text id="x8q2v5"
Menu Cache Corrupted
      ↓
Delete Cache Entry
      ↓
Reconnect
      ↓
Download Fresh Configuration
```

This must never apply to pending transactional records.

---

## 88. Corrupted Transaction Recovery

If a pending transaction is corrupted:

* mark it as recovery-required;
* preserve available metadata;
* do not silently delete it;
* prevent unsafe duplicate recreation;
* synchronize or resolve according to backend recovery rules.

---

## 89. Local Data and Audit

Any important local recovery or deletion operation should generate appropriate diagnostic/audit context after reconnect where the backend architecture supports it.

The frontend must not rewrite historical audit data.

---

## 90. Offline UI Indicators

The application should provide clear but non-disruptive indicators.

Example:

```text id="m1q8s4"
● Online

or

○ Offline
  12 operations pending

or

↻ Syncing
  8 / 12
```

The exact visual design belongs to the Design System.

---

## 91. Offline User Experience

The user should not need to understand:

* queue internals;
* operation UUIDs;
* database state;
* synchronization protocols.

The UI should communicate:

* whether the system is online;
* whether operations are pending;
* whether action is required;
* whether synchronization succeeded.

---

## 92. Pending Operation Detail

For important operations, the UI may show:

* operation type;
* created time;
* status;
* retry state;
* conflict;
* failure reason.

Technical identifiers may be available to authorized administrators when required for diagnostics.

---

## 93. Synchronization Progress

Synchronization progress should not block normal POS operation.

The UI may display:

```text id="w6p3q9"
12 pending
8 synchronized
2 retrying
1 conflict
1 rejected
```

Progress must remain accurate.

---

## 94. Offline Conflict Resolution

Conflict resolution must:

1. identify the operation;
2. identify the conflict;
3. preserve local data;
4. display server result;
5. require explicit resolution where necessary;
6. create a new operation if a corrective action is required;
7. preserve audit/history.

The original operation UUID must not be reused for a logically new corrective command.

---

## 95. Offline Retry

Retrying a failed operation must preserve the original operation UUID when it represents the same business operation.

Creating a corrective operation requires a new operation UUID.

---

## 96. Local State and Current Server State

After synchronization, server state becomes authoritative.

Example:

```text id="3f6k8m"
Local State
    ↓
Sync
    ↓
Server Result
    ↓
Replace/merge local representation
    ↓
Refresh dependent state
```

The frontend must not keep an outdated local state merely because it was created earlier.

---

## 97. Server Reconciliation

When server reconciliation changes local state:

* update local record;
* update synchronization status;
* invalidate stale cache;
* update UI;
* preserve historical transaction snapshots.

---

## 98. Offline and Reports

Reports should normally remain online/server-generated.

The frontend may display previously cached report results where explicitly supported, but must label them as cached/stale when appropriate.

It must not reconstruct authoritative financial reports from incomplete offline data.

---

## 99. Offline and Notifications

Notifications generated while offline should be synchronized after reconnect where appropriate.

Critical server notifications remain backend-authoritative.

---

## 100. Offline and Settings

Complex settings should remain online-only unless explicitly designed for offline operation.

If a setting is offline-capable:

* it must use the latest authorized configuration;
* changes require operation UUID;
* version conflicts must be handled;
* synchronization must be explicit.

---

## 101. Offline and Menu/Pricing

Offline POS uses the last valid authorized menu/pricing configuration.

Price changes made on the server while offline do not silently rewrite existing local Orders.

New offline operations use the currently authorized local configuration until synchronization rules determine otherwise.

---

## 102. Offline and Cash Sessions

Cash Session operations must preserve session identity and state.

The frontend must not create multiple local Cash Sessions because of:

* reconnect;
* page refresh;
* retry;
* duplicate button press.

Operation UUID and local session identity must be preserved.

---

## 103. Offline and Printing

Printing may occur locally while offline where printer integration supports it.

Print state remains separate from transaction state.

Example:

```text id="y3v6k1"
Order Accepted
   ↓
Print Attempt
   ↓
PRINTED / FAILED
```

Print failure does not automatically invalidate the accepted Order.

---

## 104. Offline and External Services

Offline POS must not depend on external cloud services that are unavailable without internet unless explicitly designed with a local adapter.

Core offline operations must remain independent of unnecessary external integrations.

---

## 105. Performance Requirements

Offline storage architecture should target:

| Metric                             |                     Target |
| ---------------------------------- | -------------------------: |
| Local read                         |                p95 ≤ 20 ms |
| Local write                        |                p95 ≤ 50 ms |
| Offline queue insertion            |                p95 ≤ 50 ms |
| Local Product search               |               p95 ≤ 100 ms |
| Local configuration lookup         |                p95 ≤ 20 ms |
| Offline Order draft update         |                p95 ≤ 50 ms |
| Synchronization batch preparation  |               p95 ≤ 200 ms |
| Offline startup state restoration  |                  p95 ≤ 1 s |
| Local state recovery after refresh |                  p95 ≤ 1 s |
| Offline storage fatal error rate   | < 0.1% of offline sessions |

These targets assume supported POS hardware and a healthy local runtime.

---

## 106. POS Performance Priority

Offline storage operations must not noticeably slow POS interaction.

Priority:

```text id="a4m8q2"
POS Interaction
   ↓
Local Transaction Persistence
   ↓
Synchronization
   ↓
Cache Maintenance
```

Cache cleanup and synchronization must not block critical POS operations.

---

## 107. Storage Growth Limits

Local storage must remain bounded.

Limits should exist for:

* cache;
* synchronization metadata;
* completed operations;
* local report data;
* temporary files.

Pending business transactions receive higher retention priority.

---

## 108. Cleanup Scheduling

Cleanup may run:

* after synchronization;
* during idle periods;
* at application startup when safe;
* through bounded background work.

Cleanup must not monopolize the main thread.

---

## 109. Offline Testing

Testing must include:

### Storage

* write;
* read;
* update;
* delete;
* transaction rollback;
* schema migration.

### Security

* encryption;
* tampering;
* revoked device;
* expired authorization;
* unauthorized local access.

### Synchronization

* retry;
* duplicate;
* partial batch;
* conflict;
* rejected operation;
* reconnect.

### Recovery

* browser refresh;
* application restart;
* interrupted sync;
* storage failure;
* corrupted cache.

---

## 110. Offline End-to-End Scenarios

Required scenarios include:

1. Login online.
2. Register/trust device.
3. Receive offline authorization.
4. Disconnect network.
5. Create Order.
6. Persist Order locally.
7. Continue POS operation.
8. Restart application.
9. Restore pending Order.
10. Reconnect.
11. Synchronize Order.
12. Receive authoritative server result.
13. Update local state.
14. Synchronize configuration.
15. Resolve conflicts if present.

---

## 111. Security Testing

Security tests must verify:

* Business isolation;
* Branch isolation;
* employee isolation;
* device binding;
* authorization expiry;
* signature validation;
* tamper detection;
* encrypted persistence;
* subscription enforcement;
* deletion lifecycle;
* replay prevention;
* operation UUID uniqueness.

---

## 112. Storage Failure Testing

Simulate:

* storage quota exceeded;
* write failure;
* corrupted record;
* migration failure;
* interrupted transaction;
* browser restart during write;
* synchronization interruption.

Critical business operations must fail safely.

---

## 113. Offline Observability

The frontend should track safe operational metrics such as:

* offline session count;
* pending operation count;
* synchronization duration;
* retry count;
* conflict count;
* rejection count;
* local storage failures;
* storage usage;
* offline authorization expiry events.

Sensitive payloads must not be included in telemetry.

---

## 114. Diagnostic Information

Authorized support/admin diagnostics may include:

* device UUID;
* Business UUID;
* Branch UUID;
* application version;
* local schema version;
* sync status;
* pending count;
* last successful synchronization;
* last synchronization error code.

Operation UUID may be exposed for troubleshooting when appropriate.

---

## 115. No Sensitive Telemetry

Telemetry must not include:

* passwords;
* tokens;
* cryptographic keys;
* offline authorization secrets;
* full payment data;
* unnecessary personal information.

---

## 116. Application Update

Application updates must preserve pending offline operations where compatibility is supported.

Before a breaking local schema update:

1. detect pending operations;
2. apply migration safely;
3. preserve queue;
4. validate storage;
5. continue synchronization.

---

## 117. Version Compatibility

Offline operations may outlive the frontend version that created them.

Therefore:

* operation schema must be versioned where required;
* synchronization payloads must remain compatible;
* unsupported old operations must fail explicitly rather than corrupting data.

---

## 118. App Downgrade

Downgrading the application must not silently use an incompatible local schema.

The application should detect unsupported schema versions and follow the defined recovery/migration policy.

---

## 119. AI-Agent Development Rules

AI coding agents must follow these rules:

1. Never access browser storage directly from feature components.
2. Use the Offline Storage abstraction.
3. Do not create a second offline queue.
4. Reuse operation UUID infrastructure.
5. Do not store secrets in ordinary local storage.
6. Do not bypass encryption.
7. Do not extend offline authorization locally.
8. Do not bypass subscription restrictions.
9. Do not bypass device trust.
10. Do not delete pending transactions during cleanup.
11. Do not silently discard synchronization conflicts.
12. Do not treat cache as authoritative.
13. Preserve Business/Branch isolation.
14. Preserve historical snapshots.
15. Add migration tests for local schema changes.
16. Add recovery tests for critical offline changes.

---

## 120. Change Management

Any change to offline storage must identify:

* local schema impact;
* storage technology impact;
* encryption impact;
* offline authorization impact;
* transaction queue impact;
* synchronization impact;
* migration impact;
* recovery impact;
* Business/Branch isolation;
* subscription impact;
* performance impact;
* testing requirements.

Major changes should be documented through an ADR.

---

## 121. Recommended Structure

```text id="v5q8m2"
frontend/
└── src/
    ├── offline/
    │   ├── storage/
    │   │   ├── database/
    │   │   ├── migrations/
    │   │   ├── repositories/
    │   │   ├── transactions/
    │   │   └── encryption/
    │   │
    │   ├── authorization/
    │   │   ├── offlineAuthorization
    │   │   ├── validation
    │   │   └── expiration
    │   │
    │   ├── queue/
    │   │   ├── operationQueue
    │   │   ├── operationState
    │   │   ├── dependencies
    │   │   └── retry
    │   │
    │   ├── synchronization/
    │   │   ├── syncEngine
    │   │   ├── batchBuilder
    │   │   ├── resultProcessor
    │   │   ├── conflictResolver
    │   │   └── reconciliation
    │   │
    │   ├── cache/
    │   │   ├── operationalCache
    │   │   ├── configurationCache
    │   │   └── cleanup
    │   │
    │   ├── recovery/
    │   │   ├── corruption
    │   │   ├── migration
    │   │   └── restore
    │   │
    │   └── telemetry/
    │       └── offlineMetrics
    │
    └── features/
        └── ...
```

---

## 122. Dependency Rules

The dependency direction should be:

```text id="m8q3t5"
Feature
   ↓
Offline Application Service
   ↓
Offline Repository
   ↓
Local Storage Abstraction
   ↓
Browser Storage
```

Synchronization:

```text id="g4x7k2"
Offline Queue
   ↓
Sync Engine
   ↓
API Client
   ↓
Backend Synchronization API
```

Features must not directly manipulate:

* local database tables;
* encryption keys;
* synchronization internals;
* storage schema.

---

## 123. Relationship with State Management

This document complements:

`22_Frontend_State_Management_and_Data_Flow.md`

The distinction is:

```text id="k3m7p9"
State Management
→ What state exists and who owns it

Offline Storage
→ What state must survive beyond memory

Synchronization
→ How persisted local state reaches the server
```

---

## 124. Relationship with API Client

This document depends on:

`23_Frontend_API_Client_and_Data_Access_Architecture.md`

The Offline Storage layer uses the centralized API client for synchronization.

It must not create a second independent HTTP client.

---

## 125. Relationship with Backend Synchronization

The frontend must remain compatible with:

* synchronization ingestion;
* operation UUID;
* idempotency;
* partial batch processing;
* conflict resolution;
* server authority;
* audit;
* Business lifecycle;
* subscription restrictions.

---

## 126. Relationship with Database

Frontend local persistence is not a replacement for the server database.

```text id="c2v6m8"
Frontend Local Database
        ≠
PostgreSQL
```

PostgreSQL remains the authoritative system database.

---

## 127. System Invariants

The following invariants apply to offline storage and local persistence:

1. Backend remains authoritative.
2. Offline operation is available only to trusted devices.
3. New devices require online trust establishment.
4. Device UUID is not authentication.
5. Offline authorization is signed and time-bounded.
6. Offline authorization is Business-bound.
7. Offline authorization is device-bound.
8. Offline authorization cannot be extended locally.
9. Current offline grace period is 3 days.
10. Expired offline authorization blocks new unsupported offline operations.
11. Local Business state is Business-isolated.
12. Local Branch state is Branch-isolated.
13. Local employee context is preserved where required.
14. Sensitive local data uses approved protection.
15. Security-sensitive data is not ordinary UI state.
16. Features do not directly access browser storage.
17. Local persistence uses an abstraction.
18. Local transaction data is durable.
19. Pending transactions survive normal application restart.
20. Pending transactions survive normal page refresh.
21. Operation UUID is generated before durable offline persistence.
22. Operation UUID remains stable across retries.
23. A new corrective operation receives a new operation UUID.
24. Cache is discardable.
25. Transaction queue is not discardable until finalized.
26. Local transactions are persisted atomically where required.
27. Partial local transaction state is never treated as valid.
28. Historical transaction snapshots are preserved.
29. Current configuration does not rewrite existing offline transactions.
30. Stale configuration is explicitly identifiable.
31. Configuration versions are persisted where required.
32. Cache and transaction queue have separate lifecycles.
33. Synchronization metadata is durable.
34. Synchronization state is explicit.
35. Already-applied operations are treated as successful finalization.
36. Retryable failures reuse operation UUID.
37. Permanent failures are not retried indefinitely.
38. Infinite retry loops are prohibited.
39. Synchronization uses bounded batches.
40. Current recommended synchronization batch size is 50–100 operations.
41. Partial batch results are processed individually.
42. Synchronization preserves operation dependencies.
43. Transaction synchronization has priority over configuration synchronization.
44. Offline payment is supported only where explicitly designed.
45. Offline inventory is not globally authoritative.
46. Offline stock is marked stale/local where appropriate.
47. Offline menu uses the latest valid local authorized configuration.
48. Offline printer state does not determine transaction success.
49. Print failure does not roll back an accepted transaction.
50. Local time is not authoritative server time.
51. Clock rollback cannot extend offline authorization.
52. Device revocation is authoritative after reconnect.
53. Employee deactivation is authoritative after reconnect.
54. Subscription restrictions cannot be bypassed offline.
55. Business deletion cannot be bypassed by pending offline transactions.
56. Pending transactions are retained until finalized or explicitly resolved.
57. Cache cleanup never deletes pending transactions.
58. Storage quota handling prioritizes pending transactions.
59. Critical offline persistence failure blocks unsafe transaction completion.
60. Local schema is versioned.
61. Local migrations are deterministic.
62. Migration failure does not silently delete pending transactions.
63. Sensitive data is encrypted where required.
64. Encryption keys are not hardcoded.
65. Device UUID is not an encryption key.
66. Local data integrity is validated.
67. Tampered data is not treated as valid.
68. Logged-out users cannot access protected offline state.
69. Device revocation invalidates protected offline state according to policy.
70. Local database contents cannot be arbitrarily exported.
71. Recovery prioritizes transaction queue.
72. Corrupted cache may be discarded and refetched.
73. Corrupted transaction data is preserved for recovery.
74. Offline status is visible to the user.
75. Synchronization progress remains accurate.
76. Synchronization does not block normal POS interaction unnecessarily.
77. Conflict resolution is explicit.
78. Retry of the same business operation preserves operation identity.
79. Server reconciliation updates local authoritative representations.
80. Cached reports are clearly distinguished from authoritative reports.
81. Offline settings are supported only where explicitly designed.
82. Offline state remains compatible with backend synchronization contracts.
83. Offline state remains compatible with API contracts.
84. Offline state remains compatible with security architecture.
85. Local storage growth is bounded.
86. Cleanup is bounded and non-blocking.
87. Browser tab concurrency cannot create duplicate synchronization effects.
88. Local schema changes are tested.
89. Offline application updates preserve pending transactions where compatible.
90. Unsupported schema versions are handled explicitly.
91. AI agents cannot create independent offline storage mechanisms.
92. AI agents cannot bypass offline security controls.
93. AI agents cannot delete pending transactions as a convenience.
94. AI agents cannot create silent conflict resolution.
95. Local persistence failures are observable.
96. Offline synchronization metrics are collected safely.
97. Sensitive telemetry is prohibited.
98. Offline operations remain attributable.
99. Local state cannot resurrect deleted Business data.
100. Local persistence must preserve historical integrity over convenience.

---

## Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/02_Frontend_Project_Structure.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/10_Order_Management_UI.md`
* `docs/04_Architecture/07_Frontend/11_Cash_Register_and_Cash_Session_UI.md`
* `docs/04_Architecture/07_Frontend/12_Inventory_and_Warehouse_UI.md`
* `docs/04_Architecture/07_Frontend/20_Offline_Mode_and_Synchronization_UI.md`
* `docs/04_Architecture/07_Frontend/21_Settings_and_Business_Configuration_UI.md`
* `docs/04_Architecture/07_Frontend/22_Frontend_State_Management_and_Data_Flow.md`
* `docs/04_Architecture/07_Frontend/23_Frontend_API_Client_and_Data_Access_Architecture.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/23_Configuration_Data_Model.md`
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
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## Status

**Frontend Architecture:** Proposed

**Version:** 1.0

**Current Document:** `24_Frontend_Offline_Storage_and_Local_Persistence_Architecture.md`

**Previous Document:** `23_Frontend_API_Client_and_Data_Access_Architecture.md`

**Next Document:** `25_Frontend_Offline_Synchronization_and_Conflict_Resolution.md`

