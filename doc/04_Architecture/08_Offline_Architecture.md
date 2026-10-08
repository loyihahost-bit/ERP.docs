# Offline Architecture

**Document ID:** ARCH-08
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the architecture for offline operation in FastFood ERP.

The offline architecture allows a Branch to continue essential operational work when network connectivity is temporarily unavailable.

Offline operation must preserve:

* security;
* Business isolation;
* Branch isolation;
* employee permissions;
* subscription restrictions;
* transaction integrity;
* historical integrity;
* synchronization correctness;
* idempotency;
* auditability;
* POS performance.

Offline operation is a controlled continuation mode, not an independent source of truth.

---

# 2. Core Principle

The architecture follows:

```text
Online Server
     ↓
Authoritative State
     ↓
Trusted Device
     ↓
Offline Authorization
     ↓
Local Operational Database
     ↓
Offline Transactions
     ↓
Durable Sync Queue
     ↓
Server Validation
     ↓
Server Database
```

The server remains authoritative for general current state.

Offline operations retain their original UUIDs and are later validated and incorporated into server state.

---

# 3. Offline Eligibility

Only approved operations may work offline.

Offline eligibility depends on:

* trusted device;
* valid offline authorization;
* active employee account;
* valid Business;
* valid Branch scope;
* effective permissions;
* subscription entitlement;
* local configuration;
* local data availability.

A device must not assume that being trusted automatically grants all offline permissions.

---

# 4. First-Time Device Requirement

A new device must connect to the server before it can operate offline.

Initial process:

```text
New Device
   ↓
Online Registration
   ↓
Device UUID Created
   ↓
Business / Branch Association
   ↓
Trust Approval
   ↓
Offline Authorization Issued
   ↓
Local Secure Initialization
```

A device without successful online registration cannot enter operational offline mode.

---

# 5. Trusted Device Boundary

Trusted Device is a security boundary.

A trusted device identifies:

* Device UUID;
* Business;
* Branch scope;
* associated employee access;
* trust state;
* authorization state;
* registration metadata;
* revocation state.

Device trust does not replace employee authentication or authorization.

---

# 6. Offline Authorization

Offline authorization is a cryptographically protected authorization artifact.

It must be:

* signed;
* time-bounded;
* Business-aware;
* Branch-aware;
* Employee-aware;
* Device-aware;
* permission-aware;
* subscription-aware;
* protected against replay.

The device must not create or modify offline authorization locally.

---

# 7. Offline Authorization Lifetime

Offline authorization has a limited validity period.

The default offline grace period is:

**3 days**

The exact value remains configuration-driven where business policy permits.

The authorization must contain sufficient information to determine whether offline operation is still allowed.

Server time is authoritative whenever connectivity exists.

---

# 8. Offline Authorization Contents

Conceptually, an offline authorization contains:

```text
Business UUID
Branch UUID(s)
Employee UUID
Device UUID
Permission Snapshot
Subscription Entitlement Snapshot
Issued At
Expires At
Authorization Version
Security Signature
```

Sensitive cryptographic material must never be exposed to application-level user interfaces.

---

# 9. Authentication vs Offline Authorization

Authentication answers:

> Who is this employee?

Authorization answers:

> What may this employee do?

Offline authorization answers:

> What was this employee explicitly allowed to do on this trusted device during the permitted offline period?

These concepts must remain separate.

---

# 10. Offline Permission Model

Effective offline permission is derived from:

```text
Role Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
+
Offline Authorization
```

A permission not included in valid offline authorization must not be granted locally.

---

# 11. Permission Changes During Offline Mode

Permission changes made on the server cannot be known immediately by a disconnected device.

Therefore:

* offline authorization defines the permitted offline window;
* critical server-side changes take effect after synchronization;
* revoked devices must be invalidated when connectivity returns;
* expired or invalid authorization blocks further offline operations.

Offline mode must never become a permanent permission bypass.

---

# 12. Employee Deactivation

Employee deactivation is server-authoritative.

If an employee becomes inactive while the device is offline:

```text
Server
Employee → Inactive
        ↓
Device remains temporarily disconnected
        ↓
Existing offline authorization remains bounded
        ↓
Reconnect
        ↓
Server rejects future unauthorized operations
```

A device must not use offline mode indefinitely after employee deactivation.

---

# 13. Subscription Restrictions

Offline operation must respect subscription entitlement.

If subscription entitlement expires:

* modifying operations must eventually be blocked;
* offline authorization must not extend subscription indefinitely;
* read-only access may remain available according to policy;
* synchronization cannot bypass subscription restrictions.

The server must revalidate subscription state when synchronization occurs.

---

# 14. Offline Data Scope

The device stores only data required for authorized offline operations.

Typical data includes:

* active products;
* categories;
* recipes required for local validation;
* Sets;
* prices;
* Branch menu configuration;
* inventory state;
* open orders;
* Cash Session state;
* employee permission state;
* synchronization queue;
* required configuration versions;
* conflict records;
* relevant historical context.

The device must not replicate the entire Business database unnecessarily.

---

# 15. Local Database

The device uses a local embedded database for offline operation.

The local database is:

* encrypted;
* Business-scoped;
* Branch-scoped;
* Device-scoped;
* durable;
* transaction-capable;
* synchronized through UUID-based operations.

The local database is not the server's authoritative database.

---

# 16. Local Database Security

Local data must be protected against unauthorized access.

Protection should include:

* encrypted storage;
* secure key management;
* device-level protection;
* application authentication;
* trusted-device validation;
* secure logout behavior;
* revocation handling.

Plaintext sensitive business data should not be stored unnecessarily.

---

# 17. Offline Transaction Identity

Every offline-created transaction receives its final UUID locally.

Examples:

```text
Order UUID
Payment UUID
Inventory Transaction UUID
Cash Session UUID
Audit Event UUID
Sync Event UUID
```

The UUID must remain unchanged after synchronization.

There is no separate Client Transaction ID.

---

# 18. Offline Order Creation

Offline order creation follows the normal order lifecycle.

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

Offline Draft:

* does not deduct inventory;
* does not reserve inventory;
* does not occupy a table;
* remains local until synchronized.

Draft may be lost if the device restarts before persistence according to the defined Draft behavior, but persisted operational transactions must remain durable.

---

# 19. Offline Order Acceptance

Accepting an order offline requires:

* valid employee permission;
* valid offline authorization;
* available local stock;
* valid menu configuration;
* valid price/configuration;
* valid order state.

The local transaction must atomically:

```text
Validate Order
      ↓
Validate Local Stock
      ↓
Deduct Local Stock
      ↓
Persist Accepted Order
      ↓
Create Sync Event
```

If any core step fails, the local transaction must roll back.

---

# 20. Offline Inventory Deduction

Inventory deduction is part of the core order acceptance transaction.

The device must not:

```text
Accept Order
```

and later independently decide:

```text
Deduct Inventory
```

Both belong to the same local transaction.

---

# 21. Offline Stock Limitation

Local stock is only the device's latest known state.

Another Branch device may consume the same stock while disconnected.

Therefore:

```text
Local Stock = Latest Known Local State
```

not:

```text
Local Stock = Guaranteed Global State
```

The server must revalidate stock when the transaction synchronizes.

---

# 22. Offline Stock Conflict

Example:

```text
Server Stock = 1

Device A offline:
Sell 1

Device B offline:
Sell 1
```

Both devices may locally accept the operation if they each believed stock was available.

After synchronization:

```text
First valid transaction
       ↓
Server accepts

Second transaction
       ↓
Conflict
```

The conflict must be explicitly recorded.

The system must not silently create negative stock.

---

# 23. Offline Modification

Accepted orders may be modified according to normal permissions.

For example:

* remove item;
* reduce quantity;
* add item;
* modify permitted components.

The local transaction must validate the complete modification.

If stock required for an increase is insufficient:

```text
Entire Modification → Rejected
```

Partial application is prohibited.

---

# 24. Offline Inventory Return on Modification

If an accepted order item is removed or reduced:

```text
Ask:
Return Inventory?
```

If the user selects return:

```text
Order Modification
+
Inventory Return
```

must succeed atomically.

If inventory return fails:

```text
Whole Modification → Rollback
```

---

# 25. Offline New Product Addition

Adding a new product to an already accepted order creates a new operational ticket/order according to the defined Order model.

The new operational entity receives its own UUID.

It remains linked to the original order/table context where required.

Synchronization must preserve these relationships.

---

# 26. Offline Table State

Table state may be maintained locally.

The local device can determine:

* locally known Busy state;
* locally known open orders;
* locally known waiter assignment.

However, the server remains authoritative after synchronization.

If another device changed the table state while disconnected, the synchronization layer must detect the conflict.

---

# 27. Offline Draft Synchronization

Draft synchronization does not create table occupancy because Draft does not occupy a table.

When the Draft later becomes Accepted:

```text
Server Rechecks
    ↓
Table State
    ↓
Order State
    ↓
Stock
    ↓
Permissions
```

If the table context is no longer valid because another Accepted order exists:

```text
Server Accepted State Wins
```

The invalid Draft must not silently overwrite server state.

---

# 28. Offline Payment

Offline payment is allowed only on trusted authorized devices.

Payment must contain:

* Payment UUID;
* Order UUID;
* Business;
* Branch;
* Employee;
* Device;
* Cash Session where applicable;
* payment method;
* amount;
* timestamp;
* status.

The payment is persisted locally before synchronization.

---

# 29. Offline Payment Validation

Before recording payment offline, the device validates:

* order exists locally;
* order belongs to the same Business/Branch;
* payment is allowed by permission;
* payment amount is valid;
* order is paymentable;
* payment does not exceed permitted conditions unless overpayment rules allow it;
* payment UUID has not already been used.

The server performs authoritative validation during synchronization.

---

# 30. Offline Cash Payment

Cash payment affects the local Cash Session.

The local system must preserve:

* Cash Session UUID;
* payment UUID;
* cash amount;
* cashier;
* device;
* timestamp.

The physical cash state is reconciled through Cash Session closing/handover.

---

# 31. Offline Card Payment

Offline ERP recording of a Card payment does not automatically mean that an external payment processor authorized the card.

The architecture must distinguish:

```text
ERP Payment Recording
```

from:

```text
External Card Authorization
```

The latter requires a supported external integration and is outside the current offline ERP guarantee.

---

# 32. Offline Debt Payment

Debt creation and debt repayment may operate offline where authorized.

The local system must retain:

* customer/debt identity;
* debt order reference;
* payment UUID;
* amount;
* allocation;
* employee;
* device;
* Cash Session where applicable.

The server must validate the final debt balance and allocation during synchronization.

---

# 33. Offline Overpayment

Overpayment follows the same business rule offline.

If the customer gives more than the order total:

```text
Order Total
+
Accepted Payment
+
Excess Amount
```

the excess must be explicitly confirmed where required.

The excess is recorded as additional Business/Branch income according to the financial model.

---

# 34. Offline Cash Session

A trusted authorized device may open a Cash Session offline.

The local Cash Session receives its own UUID.

When synchronized:

```text
Existing Cash Session UUID
        ↓
Server Validation
        ↓
Persist / Conflict
```

The server must not replace the UUID.

---

# 35. Offline Cash Session Concurrency

If multiple trusted devices attempt to open a Cash Session for the same register while disconnected, each device may locally believe the operation is possible.

When synchronized:

```text
First valid session
        ↓
Accepted

Other session
        ↓
Concurrency Conflict
```

The server must preserve the one-active-session invariant.

---

# 36. Offline Cash Handover

Cash handover may operate offline only for trusted authorized devices.

The process remains:

```text
Previous Cashier
      ↓
Close Previous Session
      ↓
New Cashier Authenticates
      ↓
Count / Accept Cash
      ↓
Open New Cash Session
```

The previous session remains permanently closed.

The new Cash Session receives a new UUID.

---

# 37. Offline Cash Correction

Cash corrections are subject to the same limits as online corrections.

The device must enforce:

* maximum correction count;
* authorization requirement after the limit;
* mandatory reason;
* original value preservation;
* new correction transaction;
* audit information.

Offline mode must not reset correction counters.

---

# 38. Offline Inventory Adjustment

Inventory adjustment is allowed only with the required permission.

The local transaction must contain:

* Product;
* quantity;
* adjustment type;
* reason;
* actor;
* Device;
* Branch;
* timestamp;
* UUID.

The server revalidates the adjustment during synchronization.

---

# 39. Offline Attendance

Attendance operations may be performed offline if authorized.

The local system stores:

* employee;
* Branch;
* role context;
* timestamp;
* attendance action;
* Device;
* UUID.

Server synchronization determines final authoritative state.

---

# 40. Offline Payroll

Payroll operations should be limited to authorized configuration and operational actions that are explicitly available offline.

Sensitive payroll calculations should use the latest valid synchronized configuration.

Final payroll state remains server-authoritative.

---

# 41. Offline Configuration

Offline devices must retain the latest valid configuration version required for operation.

Examples:

* product availability;
* prices;
* recipes;
* Sets;
* printer routing;
* permission-related operational configuration.

Each configuration has a version.

---

# 42. Configuration Staleness

A disconnected device may continue using its last valid configuration within the permitted offline window.

Example:

```text
Server:
Price Version 8

Device:
Price Version 7

Network unavailable
        ↓
Device continues using Version 7
```

After reconnect:

```text
Transaction Sync
      ↓
Configuration Sync
```

Transactions must be synchronized before applying newer configuration where ordering matters.

---

# 43. Configuration Activation

Configuration changes may become effective at the next Cash Session.

Therefore an offline device may continue using an earlier valid configuration until:

* Cash Session boundary;
* synchronization;
* configuration activation rule.

The device must not invent configuration versions.

---

# 44. Offline Menu

The local menu must contain only products valid for the authorized Branch and current configuration.

Inactive products must not be sold.

Offline menu data must include the relevant:

* Product UUID;
* category;
* price;
* availability;
* recipe/version reference;
* Set configuration/version.

---

# 45. Offline Recipe Validation

If a product requires a recipe, the device must have the relevant recipe version locally.

If the required recipe/configuration is unavailable:

```text
Offline Sale → Blocked
```

The system must not fabricate recipe data.

---

# 46. Offline Printer Processing

Kitchen printing may continue locally when printer configuration and required local printer connectivity are available.

Printing is secondary to the core ERP transaction.

If printing fails:

```text
ERP Transaction → Remains Successful
Print Job → Failed / Retrying
```

The local print queue must preserve retry state.

---

# 47. Offline Reports

Offline reports may be generated only from locally available authorized data.

Offline reports must clearly represent their data scope.

The server remains authoritative for finalized reports.

A locally generated report must not silently replace a server-generated report version.

---

# 48. Offline Notifications

Important notifications may be generated locally when the condition can be evaluated using available local data.

Examples:

* low stock;
* local operational warning;
* local session discrepancy.

Server-side notifications remain authoritative after synchronization.

Duplicate notification cycles must be prevented.

---

# 49. Offline Audit

Important offline operations must create audit context locally.

Each audit event contains:

* Audit UUID;
* Transaction UUID where applicable;
* Employee;
* Device;
* Business;
* Branch;
* client timestamp;
* source = OFFLINE;
* operation;
* result.

The audit event is synchronized later.

---

# 50. Offline Synchronization Queue

Every persistent offline operation that requires server synchronization must create a durable queue record.

Conceptual states:

```text
Pending
   ↓
Syncing
   ↓
Synced
```

Alternative states:

```text
Retrying
Failed
Conflict
```

Queue state must survive application restart.

---

# 51. Queue Ordering

Synchronization must respect dependencies.

Example:

```text
Order Created
      ↓
Order Accepted
      ↓
Inventory Deduction
      ↓
Payment
```

The queue must not submit dependent operations in an invalid order.

---

# 52. Sync Batch

The device should synchronize operations in bounded batches.

A typical batch may contain approximately:

```text
50–100 events
```

The exact batch size is configurable based on performance testing.

Large unbounded synchronization requests are prohibited.

---

# 53. Partial Batch Success

A batch may partially succeed.

Example:

```text
Event 1 → Synced
Event 2 → Synced
Event 3 → Conflict
Event 4 → Synced
```

The device must preserve the individual result of every event.

A conflict must not cause already successful operations to be re-created.

---

# 54. Lost Server Response

If the server commits an operation but the device loses connectivity before receiving the response:

```text
Device:
Unknown Result
```

The device must retry using the same UUID.

The server detects the existing UUID and returns the existing result.

No duplicate business effect is created.

---

# 55. Synchronization Idempotency

The database and synchronization layer must enforce:

```text
Same UUID + Same Operation
        ↓
Same Business Effect
```

Repeated delivery must not create:

* duplicate orders;
* duplicate payments;
* duplicate inventory deductions;
* duplicate cash transactions;
* duplicate attendance;
* duplicate audit events.

---

# 56. Conflict Classification

Conflicts may occur because of:

* insufficient server stock;
* changed order state;
* table state conflict;
* payment already completed;
* Cash Session conflict;
* employee deactivation;
* permission change;
* subscription expiry;
* configuration version conflict;
* device revocation;
* Business deletion;
* concurrent correction;
* invalid lifecycle transition.

Each conflict must have an explicit type.

---

# 57. Conflict Persistence

Conflicts are persisted as first-class records.

Conceptually:

```text
Conflict
---------
UUID
Business
Branch
Transaction
Entity
Type
Local State
Server State
Status
Created At
Resolved At
Resolver
Resolution
Reason
```

Conflicts must not be hidden inside generic error logs.

---

# 58. Conflict Resolution

Conflict resolution is a separate authorized operation.

The resolver must:

* have the required permission;
* inspect local/server state;
* choose an allowed resolution;
* provide a reason where required;
* create an audit record.

The original conflicting transaction must remain historically visible.

---

# 59. No Silent Conflict Resolution

The system must not silently choose:

```text
Local always wins
```

or:

```text
Server always wins
```

for every business case.

Server authority applies to current global state, but offline transaction history must remain preserved.

The correct result is determined by the business-specific conflict rule.

---

# 60. Server Authority

Server authority means:

* current subscription state is server-authoritative;
* current employee state is server-authoritative;
* current permissions are server-authoritative;
* current configuration is server-authoritative;
* current global inventory state is server-authoritative;
* current Cash Session uniqueness is server-authoritative.

It does not mean that the server may silently erase a valid offline transaction.

Offline transactions must be validated and either:

* accepted;
* rejected with preserved history;
* converted into an explicit conflict;
* resolved through an authorized process.

---

# 61. Network Recovery

When network connectivity returns:

```text
Detect Connectivity
      ↓
Authenticate / Validate Device
      ↓
Synchronize Transactions
      ↓
Process Conflicts
      ↓
Synchronize Configuration
      ↓
Synchronize Notifications / Audit
      ↓
Refresh Local State
```

Synchronization should run in the background.

POS operation should continue where possible.

---

# 62. Sync Priority

Synchronization should prioritize business-critical operations.

Recommended order:

1. Orders
2. Inventory Transactions
3. Payments
4. Cash Sessions / Handover
5. Other operational transactions
6. Configuration refresh
7. Notifications
8. Audit synchronization
9. Non-critical cleanup

Dependency rules override this general priority.

---

# 63. Background Synchronization

Synchronization must not block the main POS thread unnecessarily.

The architecture should use a background synchronization worker.

The worker must support:

* retry;
* backoff;
* cancellation;
* durable queue state;
* batch processing;
* conflict handling;
* progress reporting.

---

# 64. Retry Strategy

Temporary failures should be retried.

Examples:

* network unavailable;
* timeout;
* temporary server failure;
* connection reset.

Permanent failures should not be retried indefinitely.

Examples:

* invalid authorization;
* deleted Business;
* permanently invalid schema;
* unauthorized operation.

Retry policy must classify the failure.

---

# 65. Exponential Backoff

Retryable synchronization failures should use bounded backoff.

Conceptually:

```text
Attempt 1
   ↓
Short Delay
   ↓
Attempt 2
   ↓
Longer Delay
   ↓
Attempt 3
```

The system must enforce a maximum retry delay and avoid uncontrolled retry storms.

---

# 66. Sync Queue Recovery

If the application closes during synchronization:

```text
Syncing
```

events must recover safely.

On restart:

```text
Syncing → Pending / Retrying
```

where appropriate.

The system must never lose an event simply because the application process stopped.

---

# 67. Local Storage Failure

If local storage becomes unavailable or corrupted:

* new offline operations must be blocked;
* the user must receive a clear operational error;
* already synchronized server data remains safe;
* recovery must not create duplicate transactions.

The device must not silently continue with an untrusted empty database.

---

# 68. Application Reinstallation

Reinstalling the application must not automatically create a new trusted offline identity.

The device must require controlled re-registration/recovery.

A new local Device UUID may be created only through the defined device registration process.

---

# 69. Device Revocation

If a device is revoked:

```text
Trusted
   ↓
Revoked
```

The device must no longer receive valid offline authorization.

When the server becomes reachable:

* queued transactions are synchronized according to policy;
* future offline modification is blocked;
* local sensitive data must be protected;
* Business deletion or device revocation must invalidate local trust.

---

# 70. Offline Logout

Logout must not automatically destroy valid server-side history.

However, offline logout must invalidate local authentication context according to security policy.

A user must not be able to bypass authentication simply because the device remains trusted.

---

# 71. Multiple Trusted Devices

A Business/Branch may have multiple trusted devices.

Each device has its own:

```text
Device UUID
Local Database
Offline Authorization
Sync Queue
```

They synchronize independently.

Server-side concurrency rules determine the final state.

---

# 72. Same Employee on Multiple Devices

An employee may use multiple trusted devices if authorized.

Each device has independent offline authorization.

Revoking one device must not automatically revoke the employee account unless the administrative policy explicitly requires it.

---

# 73. Same Cash Session on Multiple Devices

The same cashier may use multiple trusted devices within the same active Cash Session where permitted.

Each operation retains:

* Employee UUID;
* Device UUID;
* Cash Session UUID;
* Transaction UUID.

This preserves operational attribution.

---

# 74. Offline Clock Protection

The device clock cannot be trusted completely.

The architecture must detect:

* large clock rollback;
* impossible future timestamps;
* expired authorization;
* repeated timestamp manipulation.

Clock anomalies may block sensitive offline operations until synchronization.

---

# 75. Offline Replay Protection

An offline authorization or synchronization event must not be reusable indefinitely.

Protection includes:

* unique UUIDs;
* authorization expiry;
* device binding;
* employee binding;
* Business binding;
* Branch binding;
* cryptographic validation;
* server-side duplicate detection.

---

# 76. Offline Data Tampering

Local data may be modified by an attacker.

Therefore server synchronization must never trust local state blindly.

The server must validate:

* identity;
* authorization;
* Business;
* Branch;
* transaction UUID;
* dependencies;
* business rules;
* timestamps;
* configuration version;
* inventory state;
* payment state.

Invalid or tampered events must be rejected or placed into an explicit security/conflict path.

---

# 77. Subscription Expiry While Offline

If offline authorization expires while the device remains disconnected:

```text
Offline Authorization Expired
        ↓
Modifying Operations Blocked
```

The device may still allow permitted local read-only operations where policy permits.

It must not extend the subscription itself.

---

# 78. Business Deletion While Offline

If the Business reaches permanent deletion while a device is offline:

* the device cannot recreate the Business;
* pending events become invalid;
* device trust becomes invalid;
* local sensitive data must be cleaned according to policy;
* synchronization must return a permanent lifecycle error.

Deleted Business UUIDs are never reused.

---

# 79. Offline Data Retention

The local database must not retain data indefinitely.

Local retention must consider:

* synchronization completion;
* audit requirements;
* conflict state;
* device storage;
* Business lifecycle;
* security.

Synchronized data that is no longer needed locally may be compacted or removed according to policy.

---

# 80. Local Storage Capacity

The device must monitor local storage.

When storage becomes critically low:

* non-essential cached data should be removed;
* old synchronized data may be compacted;
* pending transactions must never be deleted;
* the user must receive a clear warning;
* new offline operations may eventually be blocked if safe persistence cannot be guaranteed.

---

# 81. Offline Transaction Integrity

Every offline core transaction must use a local database transaction.

For example:

```text
Accept Order
 ├── Update Order
 ├── Deduct Inventory
 ├── Create Sync Event
 └── Create Audit Context
```

These must either all persist or all roll back locally.

---

# 82. Offline Payment Integrity

Payment and its related local financial state must be transactionally persisted.

A device restart must not leave the system in a state where:

```text
Payment exists
```

but:

```text
Required payment state does not exist
```

or vice versa.

---

# 83. Offline Cash Integrity

Cash Session operations must preserve:

* opening amount;
* cash payments;
* handover;
* closing count;
* expected amount;
* actual amount;
* discrepancy;
* corrections.

The original values remain immutable.

---

# 84. Offline Audit Integrity

Audit information must be created as part of important local operations.

If the core operation succeeds but the audit record cannot be safely persisted:

```text
Core Operation → Rollback
```

for operations where audit persistence is mandatory.

---

# 85. Offline Configuration Integrity

Configuration must be versioned locally.

Each operational transaction should be traceable to the configuration/version used when required.

This is especially important for:

* prices;
* recipes;
* Sets;
* menu availability.

---

# 86. Offline Historical Integrity

Offline operations must preserve:

* original UUID;
* original actor;
* original device;
* original Branch;
* original Cash Session;
* original client timestamp;
* configuration version;
* source = OFFLINE.

Synchronization must not erase this context.

---

# 87. Offline Source Attribution

Every synchronized offline operation must retain its origin.

Example:

```text
source = OFFLINE
device_id = ...
client_timestamp = ...
server_received_at = ...
```

This allows later investigation of:

* offline duration;
* synchronization delay;
* clock anomalies;
* device behavior.

---

# 88. Offline Observability

The system should measure:

* offline duration;
* queued event count;
* sync latency;
* retry count;
* conflict count;
* failed events;
* local storage usage;
* device authorization expiry;
* clock anomalies.

Operational metrics must not contain unnecessary sensitive business data.

---

# 89. Offline Error Model

Offline errors must be understandable to the user.

Examples:

```text
OFFLINE_AUTHORIZATION_EXPIRED
OFFLINE_PERMISSION_DENIED
OFFLINE_STORAGE_UNAVAILABLE
OFFLINE_CONFIGURATION_MISSING
OFFLINE_STOCK_UNAVAILABLE
OFFLINE_DEVICE_REVOKED
OFFLINE_SYNC_REQUIRED
OFFLINE_CLOCK_ANOMALY
```

The UI should explain the operational action required without exposing security-sensitive implementation details.

---

# 90. Offline Security Boundary

The offline architecture must assume:

```text
The client device can be compromised.
```

Therefore:

* local state is untrusted from the server perspective;
* cryptographic authorization is mandatory;
* server validation is mandatory;
* UUID idempotency is mandatory;
* Business/Branch scope is mandatory;
* permissions are bounded;
* subscription entitlement is bounded;
* device trust is revocable.

---

# 91. Offline and API Architecture

Offline operations use the same application business rules as online operations.

The preferred flow is:

```text
Offline Client
      ↓
Sync API
      ↓
Application Command
      ↓
Domain Rules
      ↓
Repository
      ↓
Database
```

Synchronization must not bypass application/domain rules by directly writing arbitrary database records.

---

# 92. Offline and Application Layer

The Application Layer must expose reusable command handlers for:

* order acceptance;
* payment;
* cash operations;
* inventory adjustment;
* attendance;
* configuration operations;
* synchronization.

Online and offline synchronization should converge on the same application-level business behavior.

---

# 93. Offline and Domain Layer

Domain rules must remain independent of network availability where possible.

For example:

```text
Stock cannot become negative
```

is a domain invariant.

The offline layer provides local execution support, but must not redefine the business rule.

---

# 94. Offline and Database Architecture

The local database and server database have different responsibilities.

### Local database

* temporary operational continuity;
* offline transaction persistence;
* local configuration;
* local queue;
* local state.

### Server database

* authoritative persistent state;
* global Business state;
* cross-device consistency;
* subscription state;
* final inventory state;
* final financial state;
* historical reporting.

---

# 95. Offline and Reporting

Offline reporting is a local read operation.

It must not be treated as a finalized server report.

Once synchronized, server reports may differ because:

* another device created transactions;
* conflicts were resolved;
* inventory changed;
* payments were received;
* corrections occurred.

The server report remains authoritative.

---

# 96. Offline and Notifications

Offline-generated notifications are local operational signals.

Server notifications remain authoritative for global conditions.

The synchronization layer must deduplicate notifications where the same condition was detected both locally and server-side.

---

# 97. Offline and Audit

Offline operations must eventually contribute to the central audit trail.

The server must retain the distinction between:

```text
ONLINE
```

and:

```text
OFFLINE
```

source.

---

# 98. Offline and Data Lifecycle

Business lifecycle transitions must override offline continuity.

If Business is:

```text
Deleted
```

then no offline transaction may revive it.

If subscription is:

```text
Expired / Read-Only
```

offline authorization cannot grant permanent modification access.

---

# 99. Offline Recovery Workflow

A typical recovery sequence is:

```text
Network Restored
      ↓
Validate Device
      ↓
Validate Employee
      ↓
Validate Business
      ↓
Validate Subscription
      ↓
Upload Pending Transactions
      ↓
Process Results
      ↓
Resolve Conflicts
      ↓
Download New Configuration
      ↓
Refresh Local State
      ↓
Resume Normal Online Mode
```

---

# 100. Offline Architecture Invariants

The following invariants are mandatory:

1. Offline mode is available only on trusted devices.
2. A new device must be registered online before offline operation.
3. Device trust does not replace employee authentication.
4. Device trust does not grant permissions.
5. Offline authorization is cryptographically protected.
6. Offline authorization is time-bounded.
7. Offline authorization is Business-scoped.
8. Offline authorization is Branch-scoped.
9. Offline authorization is Employee-scoped.
10. Offline authorization is Device-scoped.
11. Offline authorization is permission-aware.
12. Offline authorization is subscription-aware.
13. Offline authorization cannot be extended locally.
14. The default offline grace period is 3 days.
15. Server time is authoritative whenever available.
16. Local databases are encrypted.
17. Local databases are not server authority.
18. Offline operations use stable UUIDs.
19. No Client Transaction ID is required.
20. Offline UUIDs remain unchanged after synchronization.
21. Offline core transactions are locally atomic.
22. Order acceptance and inventory deduction are atomic locally.
23. Offline inventory cannot intentionally become negative.
24. Local stock is not guaranteed global stock.
25. Server revalidates stock during synchronization.
26. Stock conflicts are explicit.
27. Offline modifications are atomic.
28. Failed inventory return rolls back the whole modification.
29. Offline payments use stable Payment UUIDs.
30. Duplicate offline payments are prevented.
31. Offline Cash Sessions use stable UUIDs.
32. One active Cash Session per register remains mandatory server-side.
33. Offline handover preserves previous session history.
34. Cash corrections retain original values.
35. Offline correction limits cannot be reset locally.
36. Offline configuration is versioned.
37. Transactions synchronize before configuration where dependency requires it.
38. Offline recipes must come from a valid local version.
39. Offline inactive products cannot be sold.
40. Offline printing is secondary to the ERP transaction.
41. Printer failure does not roll back the core transaction.
42. Offline reports do not replace authoritative server reports.
43. Offline notifications are deduplicated.
44. Important offline operations produce audit context.
45. Audit context preserves source = OFFLINE.
46. Synchronization queue is durable.
47. Queue state survives application restart.
48. Synchronization uses dependency ordering.
49. Synchronization supports bounded batches.
50. Partial batch success is supported.
51. Lost responses are handled through UUID idempotency.
52. Duplicate synchronization cannot duplicate business effects.
53. Conflicts are persisted explicitly.
54. Conflict resolution requires authorization.
55. Conflict resolution requires audit.
56. Conflicts are never silently hidden.
57. Server remains authoritative for current global state.
58. Server authority does not erase offline transaction history silently.
59. Temporary network failures are retryable.
60. Permanent failures are not retried indefinitely.
61. Retry uses bounded backoff.
62. Syncing events recover safely after application restart.
63. Local storage failure blocks unsafe new offline transactions.
64. Reinstallation does not automatically restore trust.
65. Device revocation blocks future offline authorization.
66. Multiple trusted devices are supported.
67. One employee may use multiple trusted devices where authorized.
68. Multiple devices may operate within one Cash Session where permitted.
69. Device UUID identifies the physical trusted device.
70. Offline clock rollback is detectable.
71. Offline replay is prevented.
72. Local data tampering is assumed possible.
73. Server validates synchronized operations.
74. Business deletion invalidates offline trust.
75. Deleted Business UUIDs are never reused.
76. Subscription expiry cannot be bypassed offline.
77. Employee deactivation eventually blocks offline operations.
78. Permission changes are server-authoritative.
79. Local storage has capacity protection.
80. Pending transactions are never deleted as cache cleanup.
81. Offline transaction context is historically preserved.
82. Client and server timestamps are distinguished.
83. Offline source attribution is retained.
84. Offline observability is available.
85. Offline errors use stable application error codes.
86. Synchronization uses the API layer.
87. Synchronization invokes application/domain rules.
88. Synchronization never performs uncontrolled direct table writes.
89. Offline rules do not redefine domain invariants.
90. Local database and server database have separate responsibilities.
91. Server reports remain authoritative.
92. Server notifications remain authoritative for global conditions.
93. Central audit eventually receives important offline operations.
94. Data lifecycle rules override offline continuity.
95. Deleted Businesses cannot be resurrected by stale offline events.
96. Offline authorization cannot become permanent authorization.
97. Offline operations must remain traceable to their originating device.
98. Offline operations must remain traceable to their originating employee.
99. Offline operations must remain traceable to their originating Branch.
100. Offline architecture must preserve security, historical integrity, synchronization correctness, and POS continuity.

---

# 101. Completion Criteria

The Offline Architecture is considered implemented when:

* trusted-device registration is implemented;
* offline authorization is implemented;
* cryptographic authorization validation is implemented;
* encrypted local storage is implemented;
* local transactional database is implemented;
* offline permission enforcement is implemented;
* subscription-aware offline authorization is implemented;
* offline Order processing is implemented;
* offline Inventory processing is implemented;
* offline Payment processing is implemented;
* offline Cash Session processing is implemented;
* offline handover is implemented;
* offline configuration versioning is implemented;
* durable synchronization queue is implemented;
* UUID-based idempotency is implemented;
* synchronization dependency ordering is implemented;
* conflict persistence is implemented;
* conflict resolution is implemented;
* retry and backoff are implemented;
* device revocation is implemented;
* clock anomaly detection is implemented;
* local storage protection is implemented;
* offline audit context is implemented;
* server revalidation is implemented;
* synchronization observability is implemented;
* offline concurrency tests pass;
* failure/recovery tests pass;
* security tests pass.

---

# 102. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`

### Domain Analysis

* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### Architecture

* `docs/04_Architecture/01_System_Architecture.md`
* `docs/04_Architecture/02_Application_Layer_Architecture.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/06_API_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`

### Next Architecture Document

`docs/04_Architecture/09_Synchronization_Architecture.md`

---

# 103. Final Status

Offline Architecture is **Accepted v1.0**.

The architecture provides controlled offline continuity while preserving:

* server authority;
* tenant isolation;
* Branch isolation;
* permission boundaries;
* subscription restrictions;
* transaction integrity;
* inventory correctness;
* financial integrity;
* historical integrity;
* UUID-based idempotency;
* explicit conflict handling;
* trusted-device security;
* synchronization reliability;
* POS performance.

