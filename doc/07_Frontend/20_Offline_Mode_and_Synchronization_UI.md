# Offline Mode and Synchronization UI

**Document ID:** FA-20
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`

---

## 1. Purpose

This document defines the frontend architecture and UI behavior for:

* Offline Mode;
* Trusted Device;
* Offline Authorization;
* Local Data Availability;
* Offline POS Operation;
* Local Transaction Queue;
* Synchronization;
* Synchronization Status;
* Synchronization Progress;
* Sync Conflicts;
* Partial Synchronization;
* Failed Synchronization;
* Configuration Synchronization;
* Transaction Synchronization;
* Offline Security State;
* Reconnection;
* Recovery.

The primary goal is to allow Branch operations to continue during temporary network outages without sacrificing:

* data integrity;
* authorization;
* Business isolation;
* Branch isolation;
* historical integrity;
* transaction idempotency;
* security;
* synchronization correctness.

---

## 2. Core Principles

The frontend must follow these principles:

1. Offline mode is an operational continuity mechanism, not a separate business system.
2. Server remains authoritative.
3. Only trusted devices may enter offline operation.
4. A device must first be registered and trusted online.
5. Offline authorization is time-bounded.
6. Offline authorization cannot be renewed indefinitely without server validation.
7. Local data is encrypted.
8. Offline transactions receive UUID-based operation identifiers.
9. Transaction synchronization has priority over configuration synchronization.
10. Historical transaction snapshots must never be rewritten during synchronization.
11. Synchronization must be idempotent.
12. Duplicate synchronization must not create duplicate business effects.
13. Conflicts must be explicit.
14. Silent last-write-wins is prohibited for important business data.
15. The frontend must clearly distinguish offline state from synchronization state.
16. Offline mode must not unnecessarily slow normal online POS operation.

---

## 3. Offline Context

Offline operation exists inside the following context:

```text id="ofcxt1"
Business
   ↓
Branch
   ↓
Trusted Device
   ↓
Employee Authentication
   ↓
Offline Authorization
   ↓
Local Application State
   ↓
Offline Transactions
   ↓
Synchronization
   ↓
Server Authority
```

The frontend must preserve this context throughout the offline lifecycle.

---

## 4. Online and Offline Modes

The application should represent at least:

```text id="ofmod1"
ONLINE
OFFLINE
RECONNECTING
SYNCING
DEGRADED
```

These are operational UI states.

They must not be confused with:

```text
Subscription State
Employee State
Permission State
Cash Session State
Order State
```

Each state remains independently authoritative.

---

## 5. Network State

The frontend may monitor browser/device network information.

However, browser network status is only an indicator.

For example:

```text id="netind1"
Browser says:
Online
```

does not necessarily mean:

```text
Backend reachable
```

Therefore, the frontend should distinguish:

```text id="netind2"
Network Available
Backend Reachable
```

where practical.

---

## 6. Online State

When online:

* server APIs are authoritative;
* current configuration may be refreshed;
* synchronization queue may be processed;
* subscription state may be refreshed;
* permissions may be refreshed;
* trusted device state may be validated.

Normal online operation should not be slowed by offline infrastructure.

---

## 7. Offline State

When backend connectivity is unavailable and offline authorization remains valid:

```text id="offst1"
OFFLINE
```

the frontend may allow supported offline operations.

The UI must clearly show:

```text
Offline
```

but should not repeatedly interrupt the cashier.

---

## 8. Offline Indicator

The application should provide a persistent but compact offline indicator.

Example:

```text id="offind1"
● Offline
```

or:

```text id="offind2"
Offline · 12 pending
```

The indicator should remain visible in important operational screens.

It should not cover the POS workspace.

---

## 9. Offline Indicator Semantics

The indicator should communicate:

* current connectivity state;
* synchronization state;
* pending transaction count where available;
* offline authorization validity where appropriate.

Example:

```text id="offind3"
Offline
12 transactions pending
Offline authorization valid
```

Sensitive security details should not be unnecessarily exposed.

---

## 10. Reconnecting State

When connectivity appears to return:

```text id="recon1"
RECONNECTING
```

the frontend should not immediately assume that synchronization has completed.

The UI may display:

```text
Connection restored
Synchronizing...
```

The application remains in a controlled synchronization state until required validation succeeds.

---

## 11. Backend Reachability

The frontend should verify backend reachability using an appropriate lightweight endpoint.

Example:

```text id="reach1"
Network available
        ↓
Backend health/reachability check
        ↓
Backend reachable
```

If the backend cannot be reached:

```text id="reach2"
Network available
        ↓
Backend unreachable
        ↓
Remain offline
```

---

## 12. Trusted Device Requirement

Offline mode is available only to a trusted device.

The frontend must know whether the current device is authorized for offline operation.

Possible states:

```text id="trust1"
TRUSTED
NOT_TRUSTED
PENDING
REVOKED
EXPIRED
```

A device UUID alone does not make a device trusted.

---

## 13. First Device Registration

A new device must first operate online.

Conceptually:

```text id="reg1"
New Device
   ↓
Online Authentication
   ↓
Device Registration
   ↓
Verification
   ↓
Trusted Device
   ↓
Offline Authorization Available
```

A new device must not enter offline mode immediately after first login.

---

## 14. Untrusted Device

If the current device is not trusted:

```text id="untrust1"
Offline operation unavailable

This device must be connected to the server
and verified before offline operation can be used.
```

The frontend must not offer a client-side bypass.

---

## 15. Trusted Device Status

The application may expose trusted device information in the security/settings area.

Possible information:

* device name;
* trusted status;
* last validation;
* device identifier in masked form;
* offline capability;
* revocation status.

Full security identifiers should not be unnecessarily exposed.

---

## 16. Offline Authorization

Offline authorization is separate from ordinary employee authentication.

It may contain server-authorized context such as:

```text id="offauth1"
Business
Branch
Device
Employee/session context
Authorization expiry
Allowed operations
Subscription constraints
Configuration version
Security metadata
```

The frontend must not modify this authorization.

---

## 17. Offline Authorization Validity

The current offline authorization period is limited to:

**3 days.**

The frontend may display remaining validity where useful.

Example:

```text id="offauth2"
Offline access
Valid for 2 days 6 hours
```

The exact authoritative expiry timestamp comes from the server-issued authorization.

---

## 18. Offline Authorization Expiry

When offline authorization expires:

```text id="offexp1"
Offline authorization expired.

Connect to the server to continue using this device.
```

Offline modifying operations must stop.

The frontend must not extend the expiry locally.

---

## 19. Offline Authorization Renewal

Offline authorization cannot be renewed purely offline.

Renewal requires successful server validation according to the backend security model.

The frontend should:

1. reconnect;
2. authenticate;
3. validate trusted device;
4. receive new authorization;
5. update local security state.

---

## 20. Clock Manipulation

The frontend must not trust local device time as the sole authority for offline authorization.

If the security subsystem detects:

* clock rollback;
* invalid time state;
* suspicious timestamp changes;

the frontend should enter an appropriate restricted state.

Example:

```text id="clock1"
Offline access is temporarily unavailable.

The device time must be synchronized before offline operation can continue.
```

The exact security decision remains backend/security-layer controlled.

---

## 21. Offline Data Scope

Only data required for supported offline operations should be available offline.

Typical data may include:

* active menu;
* effective prices;
* required recipe data;
* required inventory information;
* Branch configuration;
* relevant employee/session context;
* cash session context;
* order data;
* local transaction queue.

The frontend must not indiscriminately download the entire Business database.

---

## 22. Local Storage

Offline-capable data must use encrypted local storage.

The frontend should use an application abstraction instead of accessing storage directly throughout feature components.

Conceptually:

```text id="local1"
OfflineStorage
├── configuration
├── menu
├── pricing
├── inventory
├── orders
├── cash
├── synchronization
└── security
```

---

## 23. Local Storage Security

Local storage must be:

* encrypted;
* bound to the trusted device/security context;
* access-controlled;
* versioned where necessary;
* cleared/revoked when required.

Sensitive data must not be stored in ordinary unprotected browser storage.

---

## 24. Offline Cache vs Offline Transaction Data

The frontend must distinguish:

```text id="cache1"
Offline Cache
```

from:

```text
Offline Transaction Queue
```

Cached configuration can be replaced.

Pending business transactions require stronger durability and synchronization guarantees.

---

## 25. Offline Transaction UUID

Every retryable offline transaction must have a unique operation UUID.

Example:

```text id="opuuid1"
operation_id = UUID
```

The same operation ID must be reused during retries.

A retry must not generate a new business operation ID for the same logical transaction.

---

## 26. Offline Order Creation

Supported offline POS operations may include:

* create order;
* modify supported order data;
* accept order;
* payment where explicitly supported;
* cash operations where explicitly supported.

The exact operation set is defined by backend offline authorization.

The frontend must not assume that every online operation is available offline.

---

## 27. Offline Order Snapshot

When an order is created offline, the frontend must preserve the effective configuration used at the time.

For example:

```text id="snap1"
Product
Price
Recipe Version
Set Version
Discount
Markup
Configuration Version
```

The historical transaction must not later be recalculated using current server configuration.

---

## 28. Offline Price Changes

If a new price becomes available on the server while the device is offline:

```text id="priceoff1"
Offline device
uses last valid local price
```

The new server price must not be assumed locally.

Orders created offline retain their local authoritative snapshot for synchronization validation.

---

## 29. Transaction Synchronization Priority

Synchronization order must prioritize business transactions over configuration updates.

Preferred sequence:

```text id="sync1"
Pending Transactions
       ↓
Transaction Synchronization
       ↓
Server Confirmation
       ↓
Configuration Synchronization
```

This prevents a new configuration from incorrectly rewriting transactions created under an older valid configuration.

---

## 30. Synchronization States

Each pending synchronization operation may have states such as:

```text id="syncst1"
PENDING
VALIDATING
SYNCING
ACCEPTED
PARTIALLY_ACCEPTED
CONFLICT
RETRYING
FAILED
BLOCKED
```

Exact state names may follow backend contracts.

---

## 31. Synchronization Queue

The frontend should maintain a durable local queue for pending operations.

Conceptually:

```text id="queue1"
Sync Queue
├── Operation UUID
├── Operation Type
├── Created At
├── Priority
├── Status
├── Retry Count
├── Last Attempt
├── Error
└── Server Result
```

The queue must survive normal application restarts.

---

## 32. Queue Ordering

Where business dependencies exist, operations must preserve required ordering.

Example:

```text id="orderq1"
Create Order
   ↓
Add Item
   ↓
Accept Order
   ↓
Payment
```

The frontend must not synchronize a dependent operation before its prerequisite.

---

## 33. Synchronization Batches

Synchronization may process operations in bounded batches.

The backend architecture supports approximately:

```text
50–100 operations per batch
```

where appropriate.

The frontend should not assume that the entire queue is committed atomically.

Partial success is possible.

---

## 34. Partial Synchronization

Example:

```text id="partial1"
100 pending operations

92 → Accepted
5  → Conflict
3  → Retry
```

The frontend must preserve the exact per-operation result.

Accepted operations must not be resent unnecessarily.

Conflicted and retryable operations remain separately identifiable.

---

## 35. Synchronization Progress

The UI may show:

```text id="progress1"
Synchronizing

92 / 100 completed
5 conflicts
3 retrying
```

Progress must reflect actual synchronization state rather than an artificial timer.

---

## 36. Sync Indicator

A compact global indicator may show:

```text id="indicator1"
Syncing · 8 pending
```

After completion:

```text id="indicator2"
Synced
```

When conflicts exist:

```text id="indicator3"
5 conflicts need attention
```

The indicator should not interfere with POS.

---

## 37. Synchronization Detail Page

A dedicated synchronization page may provide:

* pending operations;
* completed operations;
* conflicts;
* failed operations;
* retry status;
* last successful synchronization;
* last synchronization attempt;
* current connection state.

---

## 38. Synchronization Summary

Example:

```text id="summary1"
Synchronization

Last successful sync:
10:42

Pending:
12

Accepted:
94

Conflicts:
2

Failed:
1
```

This is an operational summary, not a replacement for audit/history.

---

## 39. Last Successful Synchronization

The frontend should display the last successful synchronization timestamp when available.

Example:

```text id="lastsync1"
Last synchronized:
10:42
```

The timestamp must be based on authoritative synchronization information.

---

## 40. Failed Synchronization

A temporary failure should result in bounded retry behavior.

Example:

```text id="retry1"
Synchronization failed temporarily.
Retrying automatically...
```

The frontend should avoid displaying repetitive error dialogs.

---

## 41. Retry Strategy

Retries should be controlled by the synchronization service.

The frontend should not implement arbitrary infinite retry loops.

The system should support:

* bounded retries;
* backoff;
* retry classification;
* manual retry where appropriate;
* permanent failure state.

---

## 42. Permanent Failure

If an operation cannot be synchronized automatically:

```text id="permfail1"
Synchronization requires attention.

Operation:
Payment

Reason:
Business rule conflict
```

The user should receive an understandable explanation.

Technical details may be available in an advanced view for authorized users.

---

## 43. Sync Conflict

A conflict means the server cannot safely accept the offline operation under the current state.

Examples:

* stale configuration;
* changed order state;
* permission revoked;
* subscription state changed;
* inventory state changed;
* duplicate operation;
* Branch mismatch;
* device revoked.

---

## 44. Conflict UI

Conflicts should be shown separately from ordinary network errors.

Example:

```text id="conf1"
Synchronization Conflict

Order #1042

The server state has changed since this operation
was created offline.

[View Details]
```

---

## 45. Conflict Types

The frontend should support typed conflict categories:

```text id="conftypes1"
CONFIGURATION_CONFLICT
ORDER_CONFLICT
INVENTORY_CONFLICT
PAYMENT_CONFLICT
CASH_CONFLICT
PERMISSION_CONFLICT
SUBSCRIPTION_CONFLICT
DEVICE_CONFLICT
DUPLICATE_OPERATION
SECURITY_CONFLICT
```

The exact enumeration is backend-defined.

---

## 46. Conflict Resolution

The frontend must not automatically choose a new business value for important conflicts.

Possible resolution actions:

```text id="resolve1"
Retry
Refresh State
Review
Submit Correction
Contact Authorized User
```

The actual available actions depend on the backend conflict type.

---

## 47. Silent Last-Write-Wins

The frontend must never implement:

```text id="lw1"
local value → overwrite server value
```

for important business configuration or financial data.

Important conflicts must remain explicit.

---

## 48. Inventory Synchronization

Inventory operations require special handling.

Offline inventory information may become stale.

The frontend should clearly distinguish:

```text id="inv1"
Local Stock View
```

from:

```text
Server Authoritative Stock
```

where required.

Final stock correctness is determined by the backend.

---

## 49. Inventory Conflict

Example:

```text id="invconf1"
Offline order:
Product A × 3

Server stock:
insufficient quantity
```

The frontend must show a conflict rather than silently changing the order.

The appropriate recovery depends on backend business rules.

---

## 50. Cash Synchronization

Cash operations are financially sensitive.

The frontend must preserve:

* Cash Session identity;
* operation UUID;
* employee;
* Branch;
* device;
* amounts;
* local timestamp;
* server result.

Cash synchronization failures must be clearly visible.

---

## 51. Payment Synchronization

Payment operations require strict idempotency.

If a payment operation is retried:

```text id="pay1"
same operation UUID
        ↓
server
        ↓
existing result recognized
```

The frontend must not create a second payment attempt merely because the first response was lost.

---

## 52. Order Synchronization

Orders must preserve their historical transaction snapshot.

Synchronization must not recalculate:

* historical item price;
* discount;
* markup;
* recipe version;
* Set version;
* financial amount

from current configuration.

---

## 53. Configuration Synchronization

Configuration synchronization occurs after transaction synchronization where required.

It may update:

* menu;
* prices;
* categories;
* Branch configuration;
* recipes;
* Set configuration;
* operational settings.

The frontend should replace local configuration only with authoritative valid server configuration.

---

## 54. Configuration Version

Local configuration should retain its version identity.

Example:

```text id="cfgver1"
Menu Version: 42
Price Version: 17
Recipe Version: 31
```

This allows synchronization to determine which configuration was used by offline transactions.

---

## 55. Stale Configuration

A device may have stale configuration while offline.

This is expected.

The frontend should not display stale configuration as if it were freshly synchronized.

Where useful, show:

```text id="stale1"
Using cached configuration
Last updated: 10:32
```

---

## 56. Configuration Refresh

After successful synchronization:

```text id="refresh1"
Transactions synchronized
        ↓
Latest configuration received
        ↓
Local configuration updated
        ↓
UI refreshed
```

The refresh must not rewrite existing offline transaction snapshots.

---

## 57. Subscription Synchronization

Subscription state is authoritative on the server.

When reconnecting, the frontend must refresh:

* subscription state;
* entitlements;
* lifecycle state;
* offline authorization.

If the Business became read-only while offline, the new state must take effect after authoritative synchronization.

---

## 58. Permission Synchronization

Employee permissions may change while the device is offline.

After reconnect:

```text id="perm1"
Server permission state
        ↓
Authorization refresh
        ↓
Frontend access recalculated
```

Revoked permissions must not remain effective indefinitely.

---

## 59. Device Revocation

If the trusted device is revoked:

```text id="devrev1"
Device revoked

Offline operation unavailable.
Connect to the server or contact an authorized administrator.
```

The frontend must not allow the user to recreate trust locally.

---

## 60. Business Deletion State

If the Business enters a deletion lifecycle while a device is offline, synchronization must not resurrect the Business.

The frontend must respect server lifecycle state after reconnect.

---

## 61. Business Isolation

Offline storage must remain Business-scoped.

Example:

```text id="bisol1"
Business A
 └── Local Data A

Business B
 └── Local Data B
```

Data from Business A must never appear when the user switches to Business B.

---

## 62. Branch Isolation

Branch-scoped offline data must remain isolated.

Example:

```text id="brisol1"
Branch A
 └── Orders A
 └── Cash A
 └── Inventory A

Branch B
 └── Orders B
 └── Cash B
 └── Inventory B
```

Branch switching must recalculate local operational context.

---

## 63. Employee Context

Offline operations must retain the employee identity used to perform them.

The frontend must not allow:

```text id="emp1"
Employee A creates operation
        ↓
Employee B submits operation
```

without explicit server-supported authorization behavior.

---

## 64. Cash Session Context

Offline POS operations involving cash must retain the relevant Cash Session.

The frontend must not silently attach an operation to a different session after synchronization.

---

## 65. Local Transaction History

The frontend may show locally created operations while offline.

Each item should indicate:

```text id="localhist1"
Pending Sync
```

until server confirmation is received.

After acceptance:

```text
Synced
```

---

## 66. Pending Transaction Indicator

Orders or payments created offline may display:

```text id="pending1"
Pending synchronization
```

This is especially important for:

* payments;
* cash operations;
* inventory operations;
* accepted orders.

---

## 67. Optimistic UI

The frontend may use optimistic UI for carefully selected offline operations.

However, it must clearly distinguish:

```text id="optim1"
Locally accepted
```

from:

```text
Server confirmed
```

A local operation must not be presented as server-confirmed until synchronization succeeds.

---

## 68. Local Success Semantics

Offline success means:

```text id="localsuccess1"
Operation safely stored locally
AND
Operation authorized for offline execution
```

It does not necessarily mean:

```text
Server accepted
```

The UI must preserve this distinction where financially or operationally important.

---

## 69. Synchronization Success

An operation becomes synchronized when the server confirms the authoritative result.

Example:

```text id="syncsuccess1"
Offline
   ↓
Local operation
   ↓
Pending
   ↓
Server accepted
   ↓
Synced
```

---

## 70. Duplicate Operation

If the server reports that an operation already exists:

```text id="dup1"
Operation already processed
```

the frontend should treat the existing authoritative result as the operation result rather than creating another operation.

---

## 71. Synchronization Security

Synchronization requests must be authenticated and validated.

The frontend must not trust:

* Business UUID supplied by the user;
* Branch UUID supplied by the user;
* Employee UUID supplied by the user;
* device UUID alone;
* locally modified authorization;
* locally modified permissions.

The server validates all security context.

---

## 72. Synchronization Request Context

Synchronization should preserve relevant context:

```text id="synctx1"
Business
Branch
Employee
Device
Operation UUID
Source = OFFLINE
Created At
Configuration Version
Cash Session
```

The backend remains authoritative.

---

## 73. Synchronization Audit

Important synchronization events should integrate with Audit/History.

Examples:

* sync started;
* batch accepted;
* operation rejected;
* conflict;
* device revoked;
* duplicate operation;
* security failure.

The frontend displays these only according to authorization.

---

## 74. Synchronization Notifications

Important sync failures may generate notifications.

Examples:

```text id="syncnotif1"
Synchronization conflict requires attention.
Payment synchronization failed.
Device synchronization was rejected.
```

Notifications should link to the relevant synchronization context.

---

## 75. Reconnect Workflow

Preferred workflow:

```text id="reconnect1"
Offline
  ↓
Connection detected
  ↓
Backend reachable
  ↓
Authenticate
  ↓
Validate trusted device
  ↓
Validate subscription/lifecycle
  ↓
Sync pending transactions
  ↓
Process conflicts
  ↓
Sync configuration
  ↓
Refresh application state
  ↓
Online
```

The exact backend sequence may vary, but transaction-before-configuration priority must remain.

---

## 76. Sync Cancellation

The user should not be able to arbitrarily cancel a critical transaction synchronization once it has been safely submitted to the synchronization engine.

The UI may allow:

* pause non-critical background synchronization;
* retry;
* view status.

Critical financial synchronization must remain controlled.

---

## 77. Application Restart

If the application restarts while offline:

* pending operations must remain;
* operation UUIDs must remain unchanged;
* retry counts must remain;
* local transaction snapshots must remain;
* security context must be revalidated locally.

The application must not lose pending business operations because of a normal restart.

---

## 78. Browser Crash Recovery

After an unexpected browser crash, durable local synchronization state should be recoverable.

The frontend must avoid relying only on volatile in-memory state for pending transactions.

---

## 79. Storage Capacity

Offline storage must be bounded.

The frontend should monitor available application storage where possible.

If local storage approaches a configured safe threshold:

```text id="storage1"
Offline storage is nearly full.

Synchronize pending operations when possible.
```

The application must not silently delete pending business transactions.

---

## 80. Storage Full State

If safe local persistence cannot be guaranteed:

```text id="storagefull1"
Offline storage capacity is insufficient.

New offline operations are temporarily unavailable.
```

Existing pending operations must be preserved.

The frontend must not silently discard them.

---

## 81. Offline Data Cleanup

After authoritative synchronization:

* acknowledged temporary transaction records may be compacted;
* obsolete configuration versions may be removed according to policy;
* expired local data may be cleared.

Cleanup must never remove required historical or pending data.

---

## 82. Security Logout

Logging out must not automatically delete valid Cash Session state unless explicitly required by the security model.

However, sensitive authentication/session material must be invalidated according to security rules.

Offline transaction ownership must remain recoverable only through authorized security context.

---

## 83. Offline Employee Switching

Employee switching during offline operation requires explicit support from the offline authorization model.

The frontend must not assume that any employee can simply log into an offline device.

If employee switching is allowed:

* employee must be authorized for the device;
* branch scope must be validated;
* permissions must be available;
* offline authorization must permit the operation.

---

## 84. Offline Cashier Workflow

For Cashier:

```text id="cashoff1"
Trusted Device
     ↓
Authorized Cashier
     ↓
Cash Session
     ↓
Offline Orders
     ↓
Offline Payments
     ↓
Local Pending State
     ↓
Synchronization
```

Each operation retains employee/device/session identity.

---

## 85. Offline POS Performance

Offline POS should be fast because operations use local authorized data.

Target budgets:

| Operation                                     |                Target |
| --------------------------------------------- | --------------------: |
| Product search                                |          p95 ≤ 100 ms |
| Add Product to Order                          |          p95 ≤ 100 ms |
| Local Order update                            |          p95 ≤ 100 ms |
| Local payment operation                       |          p95 ≤ 150 ms |
| Local transaction persistence acknowledgement |          p95 ≤ 200 ms |
| Offline screen transition                     |          p95 ≤ 150 ms |
| Sync status refresh                           |          p95 ≤ 300 ms |
| Synchronization batch acknowledgement         |             p95 ≤ 1 s |
| Critical sync error visibility                | ≤ 2 s after detection |
| Offline indicator update                      |          p95 ≤ 100 ms |

These are local/frontend targets and must not compromise durability.

---

## 86. Synchronization Performance

The frontend should support efficient synchronization of normal offline workloads.

Targets:

* batch processing remains bounded;
* UI remains responsive during synchronization;
* synchronization must not freeze POS;
* large queues are processed incrementally;
* progress updates are throttled;
* non-critical rendering is deferred when necessary.

---

## 87. Background Synchronization

Synchronization should run independently from normal POS rendering.

Conceptually:

```text id="bg_sync1"
POS UI
   │
   ├── Local Operations
   │
   └── Sync Engine
         ├── Queue
         ├── Batch
         ├── Retry
         └── Conflict
```

A synchronization failure must not crash the POS interface.

---

## 88. Synchronization Concurrency

The frontend should avoid multiple synchronization workers processing the same operation simultaneously.

A single logical synchronization coordinator should manage the queue.

---

## 89. Sync Lock

A local synchronization lock may prevent duplicate workers.

The lock must be:

* bounded;
* recoverable;
* local;
* non-authoritative.

It must not replace backend idempotency.

---

## 90. Sync Queue Priority

Recommended priority:

```text id="priority1"
1. Payment
2. Cash operation
3. Accepted Order
4. Inventory transaction
5. Other business transaction
6. Configuration synchronization
7. Non-critical metadata
```

Exact ordering must follow backend dependency rules.

The main principle is:

**Business transactions before configuration refresh.**

---

## 91. Offline Configuration Version Display

Where useful, the UI may display:

```text id="cfgdisplay1"
Offline configuration
Menu v42
Prices v17
```

This should normally be available in advanced/system information rather than cluttering POS.

---

## 92. Sync Conflict User Experience

The conflict interface should be concise.

Recommended structure:

```text id="confui1"
Conflict

Order #1042
Payment

Reason:
Server state has changed.

Status:
Requires attention

[View Details]
[Retry]
```

Do not expose raw stack traces or database errors to ordinary users.

---

## 93. Technical Sync Details

Authorized technical users may view:

* operation UUID;
* request ID;
* synchronization batch ID;
* server response code;
* retry count;
* timestamps;
* conflict code.

Cashiers should normally see only business-relevant information.

---

## 94. Error Classification

Synchronization errors should be classified as:

```text id="errclass1"
TEMPORARY
RETRYABLE
CONFLICT
AUTHORIZATION
SECURITY
VALIDATION
PERMANENT
DUPLICATE
```

Frontend behavior should depend on the category.

---

## 95. Temporary Error

Example:

```text
Server temporarily unavailable.
Retrying automatically.
```

No manual intervention should be required in the normal case.

---

## 96. Authorization Error

Example:

```text
This operation can no longer be synchronized
because your authorization has changed.
```

The operation should not be retried indefinitely.

---

## 97. Validation Error

Example:

```text
This offline operation is no longer valid
under the current server state.
```

The user may need to review the operation.

---

## 98. Security Error

Security failures require conservative handling.

Example:

```text
Synchronization was blocked for security reasons.
Please reconnect and sign in again.
```

Technical details should be restricted.

---

## 99. Synchronization and Reports

Reports should not use unsynchronized local transactions as if they were authoritative server reports unless the UI explicitly labels them as local/offline data.

Example:

```text
Local operational total
```

must be distinguished from:

```text
Server report
```

---

## 100. Synchronization and Audit

Local pending events may be displayed as:

```text
Pending Audit
```

until server persistence is confirmed.

Authoritative audit records come from the server.

---

## 101. Synchronization and History

History views should distinguish:

```text id="historysync1"
Server History
Local Pending Operation
```

A local pending operation must not appear as immutable server history before authoritative persistence.

---

## 102. Subscription Read-Only and Sync

If the Business becomes read-only:

* pending operations must still be processed according to backend lifecycle rules;
* new unauthorized modifying operations must be blocked;
* the frontend must not create new operations merely because the device was previously offline;
* configuration refresh must reflect read-only state.

The backend determines whether existing pending operations are accepted or rejected.

---

## 103. Offline Authorization and Subscription

Offline authorization does not override subscription lifecycle.

For example:

```text id="offsub1"
Offline Authorization:
valid

Subscription:
READ_ONLY

Result:
No new modifying operation
```

The frontend must respect the authoritative state received during synchronization.

---

## 104. Offline Mode and Device Revocation

If a trusted device is revoked:

```text id="revoked1"
Offline operation
       ↓
Blocked
```

The frontend must not allow:

* local trust recreation;
* manual UUID changes;
* local authorization extension;
* bypass through browser refresh.

---

## 105. User Communication

Offline UI messages should be:

* short;
* clear;
* actionable;
* non-technical by default.

Preferred:

```text
Connection lost.
Offline mode is active.
```

Not:

```text
WebSocket handshake failed with ECONNRESET.
```

Technical details belong in diagnostics for authorized users.

---

## 106. Accessibility

Offline and synchronization states must be accessible.

Requirements include:

* status text not dependent on color;
* accessible status indicators;
* screen-reader announcements for important state changes;
* keyboard-accessible synchronization controls;
* visible focus states;
* readable error messages;
* accessible progress indicators.

Repeated network-state changes should not generate excessive screen-reader interruptions.

---

## 107. Responsive Design

Offline indicators and synchronization UI must work on:

* desktop POS;
* laptop;
* tablet;
* supported narrow layouts.

The POS workspace must remain the primary visual focus.

Synchronization panels should adapt without covering critical controls.

---

## 108. Loading and Progress States

Synchronization UI should support:

```text id="states1"
Idle
Checking Connection
Authenticating
Validating Device
Synchronizing
Processing Conflicts
Refreshing Configuration
Completed
Partial Success
Failed
Blocked
```

Progress should reflect real synchronization state.

---

## 109. Testing Requirements

Frontend tests must cover:

### Connectivity

* online;
* offline;
* reconnecting;
* backend unreachable;
* backend restored.

### Trusted Device

* trusted;
* untrusted;
* revoked;
* expired.

### Offline Authorization

* valid;
* near expiry;
* expired;
* clock anomaly.

### Queue

* operation creation;
* persistence;
* restart recovery;
* duplicate prevention;
* ordering;
* retry;
* failure.

### Synchronization

* full success;
* partial success;
* temporary failure;
* permanent failure;
* conflict;
* duplicate operation.

### Business Isolation

* Business A data never appears in Business B;
* Branch A data never appears in Branch B.

### Configuration

* stale configuration;
* configuration refresh;
* transaction before configuration synchronization;
* price snapshot preservation.

### Security

* revoked device;
* expired authorization;
* permission changes;
* subscription restriction;
* direct manipulation of local state.

---

## 110. AI-Agent Development Rules

AI-generated frontend code must follow these rules:

1. Never treat browser network state as backend authority.
2. Never create offline trust locally.
3. Never extend offline authorization locally.
4. Never bypass subscription restrictions offline.
5. Never generate a new operation UUID when retrying the same operation.
6. Never silently overwrite server state.
7. Never implement silent last-write-wins for important data.
8. Never delete pending business transactions during cleanup.
9. Never store sensitive offline data in unprotected storage.
10. Never mix Business-local data.
11. Never mix Branch-local data.
12. Never mix employee context.
13. Preserve Cash Session identity.
14. Preserve historical price snapshots.
15. Preserve Recipe/Set configuration versions.
16. Keep synchronization separate from normal POS rendering.
17. Use centralized synchronization services.
18. Do not duplicate retry logic across features.
19. Do not expose raw technical errors to ordinary users.
20. Handle conflicts explicitly.
21. Treat server responses as authoritative.
22. Keep transaction synchronization ahead of configuration synchronization.
23. Use typed synchronization states.
24. Add tests for every synchronization rule change.
25. Update this document when offline architecture changes.

---

## 111. Recommended Frontend Structure

Recommended structure:

```text id="frontstruct1"
frontend/
└── src/
    ├── core/
    │   ├── connectivity/
    │   ├── storage/
    │   └── security/
    │
    ├── features/
    │   └── synchronization/
    │       ├── components/
    │       │   ├── OfflineIndicator
    │       │   ├── SyncIndicator
    │       │   ├── SyncProgress
    │       │   ├── SyncStatus
    │       │   └── ConflictBadge
    │       │
    │       ├── pages/
    │       │   ├── SynchronizationPage
    │       │   └── ConflictDetailsPage
    │       │
    │       ├── queue/
    │       │   ├── queueStore
    │       │   ├── queueProcessor
    │       │   └── queuePersistence
    │       │
    │       ├── services/
    │       │   ├── synchronizationService
    │       │   ├── connectivityService
    │       │   └── offlineAuthorizationService
    │       │
    │       ├── conflicts/
    │       │   ├── conflictTypes
    │       │   ├── conflictResolver
    │       │   └── conflictPresentation
    │       │
    │       ├── storage/
    │       │   ├── encryptedStore
    │       │   ├── transactionStore
    │       │   └── configurationStore
    │       │
    │       └── types/
    │           ├── synchronization.ts
    │           ├── offline.ts
    │           ├── conflicts.ts
    │           └── connectivity.ts
    │
    └── shared/
        └── synchronization/
```

Feature-specific offline behavior may remain inside individual features while the synchronization engine remains centralized.

---

## 112. State Architecture

The frontend should conceptually separate:

```text id="statearch1"
Connectivity State
        │
        ├── ONLINE
        ├── OFFLINE
        └── RECONNECTING

Offline Authorization State
        │
        ├── VALID
        ├── EXPIRING
        ├── EXPIRED
        └── REVOKED

Synchronization State
        │
        ├── IDLE
        ├── SYNCING
        ├── PARTIAL
        ├── CONFLICT
        └── FAILED

Subscription State
        │
        ├── ACTIVE
        ├── READ_ONLY
        └── DELETED
```

These state machines must not be collapsed into one generic `offline` boolean.

---

## 113. Local vs Server Authority

The frontend should maintain a clear authority model:

```text id="authority1"
Local State
   ↓
Operational Continuity

Server State
   ↓
Final Authority
```

Local state is authoritative only for safely persisted local offline operations until server synchronization resolves them.

Once synchronized, server state becomes authoritative.

---

## 114. Historical Integrity

Synchronization must never rewrite historical transaction facts.

The frontend must preserve:

* original price;
* discount;
* markup;
* recipe version;
* Set version;
* employee;
* Branch;
* device;
* Cash Session;
* operation UUID;
* original transaction context.

Current configuration must not reinterpret historical operations.

---

## 115. Data Recovery

If synchronization fails after local persistence:

```text id="recover1"
Local operation
      ↓
Persisted
      ↓
Sync attempt fails
      ↓
Remain pending
      ↓
Retry
```

The frontend must not recreate the transaction from scratch.

---

## 116. Recovery After Application Failure

After application restart or crash:

1. recover synchronization queue;
2. validate local storage;
3. validate offline authorization;
4. restore Business context;
5. restore Branch context;
6. resume safe pending operations;
7. continue synchronization when connectivity exists.

---

## 117. Data Corruption

If local offline data fails integrity validation:

```text id="corrupt1"
Offline data integrity check failed.

Offline operation has been restricted.
Please reconnect to the server.
```

The frontend must not attempt to guess or repair financial data automatically.

---

## 118. Synchronization Observability

Frontend telemetry should measure:

* offline sessions;
* offline duration;
* queue size;
* synchronization duration;
* synchronization success rate;
* conflict rate;
* retry count;
* permanent failure count;
* local storage errors;
* authorization expiry;
* device revocation;
* reconnect time.

Sensitive transaction data must not be included unnecessarily.

---

## 119. Performance Guardrails

Offline/synchronization architecture must not:

* block the main UI thread unnecessarily;
* re-render the entire POS after every queue update;
* repeatedly serialize large datasets;
* continuously poll the backend;
* perform expensive synchronization calculations inside UI components;
* prevent local order entry while background synchronization is running.

The synchronization engine should work incrementally.

---

## 120. System Invariants

The following invariants apply to Offline Mode and Synchronization UI:

1. Server remains authoritative.
2. Offline mode is available only to trusted devices.
3. New devices must first be trusted online.
4. Device UUID alone does not establish trust.
5. Offline authorization is time-bounded.
6. Offline authorization currently has a maximum validity of 3 days.
7. Offline authorization cannot be extended purely offline.
8. Local clock is not authoritative for authorization.
9. Clock rollback detection must be respected.
10. Offline data is encrypted.
11. Offline storage is Business-scoped.
12. Offline storage is Branch-scoped where applicable.
13. Offline storage cannot cross Business boundaries.
14. Offline storage cannot cross Branch boundaries.
15. Pending operations use UUID-based idempotency.
16. Retry uses the same operation UUID.
17. Duplicate synchronization cannot create duplicate business effects.
18. Transaction synchronization takes priority over configuration synchronization.
19. Historical transaction snapshots remain immutable.
20. Current prices cannot reinterpret offline-created orders.
21. Current recipes cannot reinterpret offline-created inventory deductions.
22. Current Set configuration cannot reinterpret historical Set transactions.
23. Cash Session identity remains attached to cash operations.
24. Employee identity remains attached to operations.
25. Device identity remains attached to operations.
26. Offline success means durable local acceptance, not necessarily server confirmation.
27. Server acceptance is required for authoritative synchronization.
28. Pending operations survive normal application restart.
29. Pending operations survive recoverable application failure.
30. Pending operations are never silently discarded.
31. Synchronization queue is durable.
32. Synchronization queue is bounded.
33. Synchronization does not require one transaction for the entire queue.
34. Partial synchronization is supported.
35. Accepted operations are not unnecessarily resent.
36. Retryable operations remain retryable.
37. Permanent failures do not retry indefinitely.
38. Conflicts are distinct from temporary network failures.
39. Important conflicts are explicit.
40. Silent last-write-wins is prohibited for important business data.
41. Backend authorization remains authoritative.
42. Offline authorization cannot bypass subscription restrictions.
43. Offline authorization cannot bypass employee permissions.
44. Offline authorization cannot bypass Branch scope.
45. Device revocation blocks offline operation.
46. Subscription restrictions apply after authoritative state is known.
47. Business deletion cannot be bypassed by offline state.
48. Offline state cannot resurrect deleted Business data.
49. Configuration versions remain identifiable.
50. Stale configuration is distinguishable from current configuration.
51. Local configuration does not become server authority.
52. Configuration synchronization occurs after required transaction synchronization.
53. Synchronization cannot silently rewrite historical state.
54. Local pending state is distinguishable from server-confirmed state.
55. Financial operations require stronger synchronization guarantees.
56. Payment retries use idempotent operation identity.
57. Cash retries use idempotent operation identity.
58. Inventory retries use idempotent operation identity.
59. Offline UI must distinguish network state from synchronization state.
60. Backend reachability is distinct from browser network state.
61. Reconnecting state is distinct from synchronized state.
62. Synchronization progress reflects real queue state.
63. Progress does not use artificial completion timers.
64. Synchronization must not freeze POS operation.
65. Background synchronization must not crash the POS interface.
66. Synchronization workers must not process the same operation concurrently.
67. Local synchronization locks are not authoritative.
68. Backend idempotency remains mandatory.
69. Offline storage must not rely only on volatile memory.
70. Browser crash recovery must preserve pending operations where technically possible.
71. Storage capacity must be monitored.
72. Storage exhaustion must not silently delete pending transactions.
73. Local cleanup cannot delete pending operations.
74. Acknowledged temporary data may be compacted only after server confirmation.
75. Offline audit state is not equivalent to server audit state.
76. Pending operations are not treated as immutable server history before confirmation.
77. Synchronization errors are classified.
78. Technical error details are restricted.
79. Ordinary users receive business-relevant error messages.
80. Security errors fail closed.
81. Authorization errors do not retry indefinitely.
82. Validation errors do not retry indefinitely without state change.
83. Duplicate operations resolve to the authoritative existing result.
84. Subscription state refreshes after reconnect.
85. Permission state refreshes after reconnect.
86. Trusted-device state refreshes after reconnect.
87. Business context is revalidated after reconnect.
88. Branch context is revalidated after reconnect.
89. Employee context is revalidated after reconnect.
90. Subscription state does not depend solely on local time.
91. Offline authorization state is centrally managed.
92. Synchronization state is centrally managed.
93. Queue processing is centrally managed.
94. Feature components do not implement independent synchronization engines.
95. Retry policy is centralized.
96. Conflict handling is centralized.
97. Synchronization API contracts are typed.
98. Operation UUIDs are preserved across application lifecycle.
99. Configuration version identifiers are preserved.
100. Synchronization results are attributable.
101. Important synchronization events are auditable.
102. Security-sensitive synchronization events are auditable.
103. Business isolation is preserved during synchronization.
104. Branch isolation is preserved during synchronization.
105. Employee permissions are evaluated during synchronization.
106. Device trust is evaluated during synchronization.
107. Subscription entitlement is evaluated during synchronization.
108. Historical financial state is preserved.
109. Current configuration does not reinterpret historical operations.
110. Local state cannot override authoritative server state.
111. Synchronization must remain performant for ordinary POS usage.
112. Offline UI must remain responsive during background synchronization.
113. Synchronization must respect accessibility requirements.
114. Offline indicators must not rely only on color.
115. Critical state changes must be understandable.
116. Sync controls must be keyboard accessible.
117. Synchronization must be observable.
118. Sensitive telemetry must be minimized.
119. Offline functionality must remain aligned with backend contracts.
120. Offline functionality must remain aligned with database invariants.
121. Offline functionality must remain aligned with security architecture.
122. Offline functionality must remain aligned with subscription lifecycle.
123. Offline functionality must preserve historical integrity.
124. Offline functionality must not create a second business authority.
125. Offline functionality must support safe recovery after temporary infrastructure failure.

---

## 121. Related Documents

### Frontend Architecture

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/11_Cash_Register_and_Cash_Session_UI.md`
* `docs/04_Architecture/07_Frontend/12_Inventory_and_Warehouse_UI.md`
* `docs/04_Architecture/07_Frontend/18_Audit_and_History_UI.md`
* `docs/04_Architecture/07_Frontend/19_Subscription_and_Entitlement_UI.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database Architecture

* `docs/04_Architecture/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/04_Architecture/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/04_Architecture/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/29_Database_Security.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`

---

## 122. Status

**Frontend Architecture:** Proposed

**Version:** 1.0

**Current Document:** `20_Offline_Mode_and_Synchronization_UI.md`

**Previous Document:** `19_Subscription_and_Entitlement_UI.md`

**Next Document:** `21_Settings_and_Business_Configuration_UI.md`

