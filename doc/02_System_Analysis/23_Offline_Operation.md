# Offline Operation

**Document ID:** SA-23
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines how FastFood ERP continues operating when a Branch temporarily loses network connectivity.

Offline operation exists to preserve operational continuity while maintaining:

* security;
* authorization;
* Business isolation;
* Branch isolation;
* data integrity;
* historical integrity;
* subscription restrictions;
* synchronization safety;
* idempotency.

Offline operation must never become a mechanism for bypassing server-side business rules.

---

## 2. Scope

This document covers:

* offline eligibility;
* trusted devices;
* offline authorization;
* local authentication context;
* local storage;
* supported offline operations;
* transaction identity;
* offline timestamps;
* permissions;
* employee status;
* subscription entitlement;
* cash sessions;
* orders;
* payments;
* inventory;
* attendance;
* notifications;
* audit;
* synchronization preparation;
* reconnect behavior;
* clock protection;
* device security;
* storage limitations;
* recovery;
* system invariants.

Synchronization and conflict resolution details are defined separately in:

`docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`

---

## 3. Offline-First Principle

A temporary network failure must not unnecessarily stop core Branch operations.

The system therefore allows authorized trusted devices to continue supported operations offline.

However:

> Offline capability is a bounded authorization, not unlimited local authority.

The device may only perform operations permitted by its valid offline authorization.

---

## 4. Offline Eligibility

A device may operate offline only when all required conditions are satisfied.

These include:

* device is trusted;
* device belongs to the correct Business context;
* device has valid Branch scope;
* employee is authorized;
* employee has required permissions;
* offline authorization is valid;
* subscription entitlement permits the operation;
* required local configuration is available;
* local storage is operational.

---

## 5. First-Time Device Requirement

A new device cannot begin normal ERP operation offline.

The first device registration must occur online.

The device must first:

1. authenticate;
2. register;
3. receive Business/Branch context;
4. become trusted;
5. receive required authorization/configuration;
6. establish valid offline capability.

This prevents unknown devices from becoming offline operational devices.

---

## 6. Trusted Device Requirement

Offline operation requires a trusted device.

A trusted device is identified independently from the Employee.

The device identity must remain stable enough to support:

* authorization;
* audit;
* synchronization;
* revocation;
* security investigation.

Trusted status does not grant permissions by itself.

---

## 7. Employee Authentication

Employee authentication and offline authorization are separate concepts.

The system must determine:

1. who the Employee is;
2. which Business they belong to;
3. which Branches they may access;
4. which permissions they currently have;
5. whether the device is trusted;
6. whether offline operation is currently permitted.

A valid device cannot authenticate an unauthorized Employee.

---

## 8. Offline Authorization

The device receives cryptographically protected offline authorization.

The authorization contains or securely references information sufficient to validate:

* Business;
* Branch;
* Employee;
* permission scope;
* device;
* subscription entitlement;
* authorization validity;
* expiration/boundary information;
* authorization version.

The authorization must be protected against unauthorized modification.

---

## 9. Cryptographic Protection

Offline authorization must be cryptographically protected.

A device must not be able to modify locally stored authorization to:

* extend expiration;
* add permissions;
* change Branch;
* change Business;
* reactivate an inactive Employee;
* bypass subscription restrictions.

Server-issued authorization remains the source of offline authority.

---

## 10. Offline Authorization Lifetime

Offline authorization is time-bounded.

The exact lifetime is configurable according to security policy.

The authorization must not remain valid indefinitely.

Expiration is evaluated using protected time information and security checks.

---

## 11. Offline Authorization Renewal

When network connectivity is available, the device may obtain refreshed offline authorization.

The refreshed authorization may contain:

* updated permissions;
* updated Branch scope;
* updated subscription entitlement;
* updated expiration;
* updated configuration version;
* updated security information.

The device must not refresh its own authorization locally.

---

## 12. Subscription Entitlement

Offline operation must respect subscription entitlement.

The offline authorization contains sufficient information to prevent the device from continuing modifying operations beyond the permitted subscription boundary.

Subscription expiration cannot be bypassed by disconnecting the device from the network.

---

## 13. Subscription Expiry Offline

If offline authorization expires or the permitted subscription boundary is reached:

* modifying operations must be blocked;
* read-only access may remain available according to policy;
* synchronization remains available where needed;
* online reauthorization is required before further modifying operations.

Offline mode must not extend the Business subscription.

---

## 14. Grace Period

Where the subscription lifecycle defines a grace period, offline authorization may respect that period according to the server-issued entitlement.

The device must not invent or extend the grace period.

The current default business rule is a **3-day renewal grace period** where applicable.

---

## 15. Employee Status Offline

The device must respect the employee status contained in valid authorization.

If an Employee becomes inactive while the device is offline, the server may not be able to immediately revoke local authorization.

Therefore offline authorization must be bounded.

After synchronization or when the authorization requires online validation:

* inactive Employee operations are rejected;
* affected offline operations may become conflicts;
* server state remains authoritative.

---

## 16. Permission Changes Offline

Permission changes made on the server cannot always reach an offline device immediately.

Therefore:

* the device may continue only within its currently valid offline authorization;
* the authorization must have a bounded lifetime;
* important operations may require online validation when required by security policy;
* synchronization revalidates all offline events.

Offline operation must never allow permanent use of obsolete permissions.

---

## 17. Branch Scope Offline

Offline authorization is Branch-aware.

A device must not use offline authorization for an unauthorized Branch.

When an Employee changes Branch context, the device must use the valid Branch-specific authorization/configuration.

---

## 18. Business Isolation Offline

Local offline data must remain associated with exactly one Business context.

A device must not:

* mix Business data;
* create cross-Business transactions;
* synchronize an event into another Business;
* use one Business authorization for another Business.

---

## 19. Local Storage

Offline operational data is stored locally in protected storage.

The local storage should be encrypted.

Sensitive local data must not be stored as unrestricted plain files.

The local storage must support:

* transaction queue;
* required local configuration;
* offline authorization;
* local audit events;
* local operational state;
* synchronization state.

---

## 20. Local Data Protection

Local storage must protect against unauthorized access as far as supported by the device environment.

The system should use:

* encryption;
* protected credentials/keys;
* device binding;
* integrity checks;
* secure deletion where appropriate.

A local database file must not be sufficient by itself to obtain ERP authority.

---

## 21. Offline Transaction Identity

Every offline business transaction uses a stable UUID.

The UUID is generated before or at transaction creation and remains unchanged through synchronization.

The server must recognize the same UUID as the same logical transaction.

---

## 22. No Client Transaction ID

The system does not use a separate Client Transaction ID as the primary transaction identity.

UUID-based identity and idempotency are sufficient.

The same UUID remains associated with:

* local operation;
* sync request;
* server processing;
* audit history.

---

## 23. Offline Order Creation

Authorized trusted devices may create Orders offline when the current configuration supports it.

An offline Order receives:

* Order UUID;
* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Cash Session UUID where applicable;
* order type;
* customer/order context;
* local timestamp.

---

## 24. Offline Draft Orders

Draft Orders may be created offline.

Draft behavior remains consistent with online behavior:

* no inventory deduction;
* no stock reservation;
* no table occupancy;
* no kitchen acceptance event.

Draft data may be lost on device restart according to the defined Draft behavior.

Offline Draft data must not be treated as an accepted transaction.

---

## 25. Offline Order Acceptance

An authorized device may accept an Order offline if the required local state and authorization permit it.

Before acceptance, the device must validate locally:

* product availability;
* recipe/configuration;
* stock;
* permission;
* Branch;
* Employee status according to local authorization;
* order state.

The local operation must be recorded for later server validation.

---

## 26. Offline Inventory Validation

Offline inventory is validated against the latest trusted local inventory state.

The device must not allow negative stock according to its local state.

However, local stock may become stale because another device or Branch operation may have changed server inventory.

Therefore local validation does not replace server validation.

---

## 27. Offline Inventory Deduction

When an offline Order is accepted:

* the local inventory transaction is created;
* the deduction is linked to the Order transaction;
* the operation receives stable UUIDs;
* the local state is updated;
* the event is queued for synchronization.

The operation must preserve the same atomic relationship when validated by the server.

---

## 28. Offline Stock Conflict

If server state differs from local state during synchronization:

* the event is not silently overwritten;
* a conflict is created;
* the original event remains preserved;
* authorized resolution is required where applicable.

The system must never silently create negative stock to make synchronization succeed.

---

## 29. Offline Payment

Trusted authorized devices may record supported payments offline.

Offline payment validation includes:

* Order;
* Business;
* Branch;
* Employee;
* Device;
* Cash Session where applicable;
* payment method;
* remaining payable amount;
* local authorization.

The server revalidates the payment during synchronization.

---

## 30. Offline Card Payment

Offline recording of a Card payment must distinguish between:

1. ERP payment recording;
2. external payment processor authorization.

The ERP may record a payment event offline only when the supported business process allows it.

ERP recording does not imply that an external card processor approved the transaction.

---

## 31. Offline Cash Payment

Cash payment recorded offline affects the local Cash Session context.

The payment must preserve:

* Cash Session UUID;
* cashier;
* device;
* amount;
* order;
* timestamp;
* payment UUID.

The server reconciles the payment during synchronization.

---

## 32. Offline Overpayment

Offline overpayment follows the same business rule as online operation.

If the entered amount exceeds the remaining order amount:

* the system requests confirmation;
* the confirmed excess becomes a separate overpayment;
* the excess belongs to the Business/Branch;
* the cashier does not receive it as personal income.

The overpayment must remain traceable to the cashier and waiter where applicable.

---

## 33. Offline Debt Repayment

Authorized trusted devices may record supported debt repayments offline.

The repayment must preserve:

* Customer;
* Debt Order;
* amount;
* payment method;
* Employee;
* Branch;
* Device;
* UUID;
* local timestamp.

Server synchronization revalidates the outstanding balance and allocation.

---

## 34. Offline Cash Sessions

A trusted device with valid authorization may open a Cash Session offline when permitted.

The Cash Session receives a local UUID that remains unchanged during synchronization.

The server must not replace the local Cash Session UUID.

---

## 35. Offline Cash Handover

Cash handover may occur offline when all participants and devices have valid authorization.

The system must preserve:

* previous Cash Session;
* new Cash Session;
* previous cashier;
* new cashier;
* physical cash amount;
* device context;
* handover event;
* timestamps.

The same physical Cash Register identity continues.

---

## 36. Offline Cash Corrections

Offline Cash Session corrections are allowed only when the employee and device have the required authorization.

The existing correction limits remain applicable.

Offline operation must not bypass:

* maximum correction count;
* authorization requirement;
* reason requirement;
* audit;
* Cash Session immutability.

---

## 37. Offline Inventory Adjustment

Manual inventory adjustments require the same permission offline as online.

The system must not grant additional inventory authority merely because the device is disconnected.

Inventory adjustment requires:

* permission;
* reason/comment;
* affected product;
* Branch context;
* audit event.

Server validation remains mandatory during synchronization.

---

## 38. Offline Attendance

Authorized employees may record attendance offline when supported.

Attendance events receive stable UUIDs.

The server later validates:

* Employee status;
* Branch;
* time;
* duplicate constraints;
* applicable attendance rules.

---

## 39. Offline Payroll

Payroll calculations requiring authoritative Business-wide data should not rely exclusively on stale offline data.

Where offline payroll functionality is supported, it must use an authorized snapshot/configuration and remain subject to server validation.

Final payroll authority remains server-side.

---

## 40. Offline Menu and Configuration

Trusted devices may continue using the latest valid local configuration.

This may include:

* products;
* categories;
* prices;
* Branch availability;
* recipes;
* Sets;
* notification thresholds where relevant.

The local configuration has a version identity.

---

## 41. Configuration Version

Offline transactions must identify the configuration version used.

This allows the server to determine:

* which product price was used;
* which recipe/configuration was used;
* which Set configuration was used;
* whether the configuration is still valid;
* whether a conflict exists.

---

## 42. Configuration Changes During Offline Mode

If configuration changes on the server while a device is offline:

* the device continues with its last valid configuration within authorization bounds;
* new configuration is delivered after synchronization;
* already-created transactions retain their historical snapshots;
* historical transactions are not silently rewritten.

---

## 43. Transaction Sync Before Configuration Sync

Business transactions must be synchronized before configuration updates when ordering is required to correctly interpret those transactions.

This prevents a configuration update from incorrectly changing the meaning of an already-created offline transaction.

---

## 44. Offline Reports

Offline reports may be generated from locally authorized data where supported.

Such reports are provisional unless they are based on server-authoritative finalized data.

Server-generated report versions remain authoritative.

---

## 45. Offline Notifications

Trusted devices may display locally generated notifications based on local data.

Offline notification behavior must respect:

* Business;
* Branch;
* Employee;
* permission;
* subscription;
* device authorization.

Notifications must be reconciled with the server after reconnection.

---

## 46. Offline Audit

Offline state-changing operations generate local audit events.

The audit event preserves:

* Event UUID;
* Business;
* Branch;
* Employee;
* Device;
* entity;
* transaction;
* source;
* local timestamp;
* old/new state where applicable.

The original audit identity remains unchanged during synchronization.

---

## 47. Offline Synchronization Queue

Offline events are stored in a durable local synchronization queue.

A queue item contains sufficient context to synchronize the event safely.

Typical state:

```text id="queue712"
Pending
  ↓
Syncing
  ↓
Synced

or

Pending
  ↓
Retrying
  ↓
Failed / Conflict
```

---

## 48. Offline Queue Durability

Pending events must not be silently deleted.

If local storage approaches capacity:

* the user receives a warning;
* unsafe new offline operations may be blocked;
* pending events remain protected.

The system must prioritize preserving pending transactions over allowing unlimited new offline activity.

---

## 49. Offline Dependency Ordering

Dependent offline operations must preserve logical order.

For example:

```text id="dep428"
Order Created
      ↓
Order Accepted
      ↓
Payment
```

A dependent event must not be synchronized before the required prerequisite event when the dependency is mandatory.

---

## 50. Offline Idempotency

Every synchronization event uses stable UUID identity.

If the same event is submitted more than once:

* the server recognizes the existing event;
* the previous result is returned where possible;
* no duplicate business effect is created.

---

## 51. Offline Retry

Temporary synchronization failures may be retried automatically.

Retry uses:

* bounded retry count;
* exponential backoff;
* dependency ordering;
* idempotency;
* failure state.

A failed event does not automatically invalidate unrelated events.

---

## 52. Offline Conflict

A conflict occurs when the offline event is no longer valid against authoritative server state.

Examples include:

* insufficient stock;
* Order already paid;
* Employee no longer authorized;
* Cash Session state changed;
* configuration conflict;
* entity state changed.

Conflicts are preserved for authorized resolution.

---

## 53. Server Authority

After synchronization, the server is authoritative for current Business state.

However, the server must not silently discard valid historical offline transaction data.

The system must preserve:

* original event;
* original UUID;
* actor;
* device;
* local time;
* conflict/result;
* resolution.

---

## 54. Offline Conflict Resolution

Conflict resolution is a separate authorized operation.

It must include:

* conflict UUID;
* selected resolution;
* actor;
* reason;
* timestamp;
* resulting state.

The original offline event remains immutable.

---

## 55. Offline Clock

Offline operation depends on time-sensitive authorization.

The system must detect suspicious clock changes such as:

* significant backward movement;
* unauthorized time extension;
* inconsistent event timestamps.

Clock anomaly information should be recorded for investigation.

---

## 56. Clock Rollback

A detected clock rollback does not automatically mean every local transaction is deleted.

Instead, the system should:

* record the anomaly;
* restrict operations when authorization/security policy requires;
* require synchronization or reauthorization where appropriate.

The system must not silently rewrite timestamps.

---

## 57. Offline Device Revocation

Device revocation performed while the device is offline cannot instantly reach the device.

Therefore:

* offline authorization must be time-bounded;
* the device must enforce authorization expiration;
* synchronization applies server-side revocation;
* revoked devices are blocked from further authorized operations once revocation is known.

Offline operation must not provide permanent access after revocation.

---

## 58. Offline Employee Deactivation

Employee deactivation performed server-side may not immediately reach an offline device.

When the device reconnects:

* employee status is revalidated;
* operations performed after the server's effective deactivation point are handled according to synchronization rules;
* unauthorized operations become rejected or conflicts where appropriate.

Historical valid operations are not silently removed.

---

## 59. Offline Application Restart

After application restart, the device must recover required durable offline state from protected local storage where supported.

At minimum, pending synchronization events must remain recoverable.

Draft Order recovery follows the defined Draft behavior and is not automatically guaranteed.

---

## 60. Offline Reinstallation

Application reinstallation may remove local operational state depending on the platform.

The system must not treat a fresh installation as a trusted offline device automatically.

The device must re-authenticate and obtain valid authorization.

Pending local events that cannot be recovered must not be silently recreated with different UUIDs.

---

## 61. Local Storage Failure

If protected local storage becomes unavailable or corrupted:

* unsafe offline operations should be blocked;
* the user must receive a safe error;
* the system must not continue using unverifiable authorization or transaction state.

Recovery requires re-establishing trusted application state.

---

## 62. Network Recovery

When connectivity returns:

1. device establishes secure server connection;
2. authentication/authorization is checked;
3. pending events are synchronized;
4. conflicts are identified;
5. server results are recorded;
6. configuration is updated;
7. notification state is reconciled;
8. device synchronization state is updated.

Synchronization must run in the background and must not unnecessarily block POS.

---

## 63. Background Synchronization

Synchronization should normally run asynchronously.

The POS must remain usable while synchronization continues.

Synchronization status should be visible to authorized users.

---

## 64. Sync Status

The device should expose relevant synchronization information, including:

* last successful sync;
* pending event count;
* failed event count;
* conflict count;
* device authorization status;
* configuration version.

Sensitive technical details should not be unnecessarily exposed to ordinary employees.

---

## 65. Offline Storage Capacity

Offline operation must operate within bounded local storage.

The system should monitor storage usage.

When storage becomes critically low:

* show warning;
* protect pending events;
* restrict unsafe new offline operations;
* require synchronization or storage recovery.

The system must never silently delete pending business transactions.

---

## 66. Offline Security

Offline security must protect against:

* unauthorized device use;
* authorization modification;
* Business switching;
* Branch switching;
* permission escalation;
* replay;
* UUID duplication;
* clock manipulation;
* subscription bypass;
* local data tampering.

---

## 67. Replay Protection

Offline authorization and synchronization events must include sufficient identity and state information to prevent replay.

A previously accepted event must not create a second business effect when submitted again.

---

## 68. Offline Permission Model

Offline permissions are based on the latest valid authorization available to the device.

Effective permission remains:

```text id="perm836"
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

Offline authorization does not create new permissions.

---

## 69. Offline Operation and Trusted Devices

Trusted device status is necessary but insufficient.

A valid offline operation requires both:

* trusted device;
* authorized Employee.

This prevents one trusted device from becoming a shared unrestricted account.

---

## 70. Multiple Devices

Multiple trusted devices may operate within the same Business and Branch where permitted.

Multiple devices may also participate in the same Cash Session when authorized.

Every operation retains its own:

* Employee;
* Device;
* Cash Session;
* transaction;
* timestamp.

---

## 71. Offline Cash Session Identity

An offline Cash Session receives a stable UUID.

The server must preserve the same UUID during synchronization.

A synchronization process must never create a second Cash Session merely because the original was created offline.

---

## 72. Offline Order Number

The customer-facing 3-digit Order Number remains a presentation identifier associated with the Cash Session.

The stable Order UUID remains the real identity.

Synchronization must preserve the UUID even if local and server numbering context requires reconciliation.

---

## 73. Offline Historical Integrity

Offline transactions must preserve their original historical context.

The system must not silently rewrite:

* price snapshot;
* recipe snapshot;
* Set composition;
* Employee;
* Device;
* Branch;
* Cash Session;
* transaction time;
* original UUID.

Server validation may reject or create a conflict, but historical evidence remains preserved.

---

## 74. Offline and Data Lifecycle

Offline operation cannot extend Business data retention.

When a Business becomes expired or reaches deletion lifecycle states:

* local modification authority expires according to authorization;
* synchronization remains subject to lifecycle rules;
* local residual data is handled according to security and deletion policy.

Detailed deletion behavior is defined in:

`docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`

---

## 75. Offline Error Handling

Users should receive simple business-safe errors.

Examples:

* "Offline authorization expired."
* "This operation requires synchronization."
* "This operation conflicts with current server data."
* "Offline storage is full."
* "Device authorization is no longer valid."

Technical details remain in logs and diagnostics.

---

## 76. Offline Recovery

Offline recovery relies on:

* durable local storage;
* stable UUIDs;
* idempotency;
* dependency ordering;
* retry;
* conflict resolution;
* audit;
* server validation.

Recovery must preserve historical integrity.

---

## 77. Offline Performance

Offline operations should be fast enough for normal POS usage.

Local operations should not wait for network availability.

Synchronization, reporting, notification reconciliation and configuration refresh should normally run asynchronously.

---

## 78. Offline Data Authority

The system uses a hybrid authority model:

* local state is authoritative for continuing an authorized offline workflow until synchronization;
* server state is authoritative for current Business state after synchronization;
* original offline events remain authoritative as historical evidence of what the device attempted/performed;
* conflicts are explicit rather than silently overwritten.

---

## 79. System Invariants

The following invariants apply to Offline Operation:

1. Offline operation is available only to trusted devices.
2. A new device cannot begin normal ERP operation offline.
3. First-time device registration requires online connectivity.
4. Trusted device status does not grant permissions.
5. Employee authorization remains required offline.
6. Offline authorization is Business-specific.
7. Offline authorization is Branch-aware.
8. Offline authorization is Employee-aware.
9. Offline authorization is Device-aware.
10. Offline authorization is permission-aware.
11. Offline authorization is subscription-aware.
12. Offline authorization is time-bounded.
13. Offline authorization cannot be modified locally to extend access.
14. Offline authorization cannot add permissions locally.
15. Offline authorization cannot change Business locally.
16. Offline authorization cannot change Branch scope locally.
17. Offline authorization cannot reactivate an Employee locally.
18. Offline operation cannot bypass subscription expiry.
19. Offline operation cannot bypass the defined grace period.
20. Offline operations use stable UUIDs.
21. UUIDs remain unchanged through synchronization.
22. Client Transaction ID is not required.
23. Offline Orders preserve Business and Branch context.
24. Offline Draft Orders do not deduct inventory.
25. Offline Draft Orders do not reserve stock.
26. Offline Draft Orders do not create operational table occupancy.
27. Offline accepted Orders require local validation.
28. Offline accepted Orders require server validation after synchronization.
29. Offline inventory cannot intentionally become negative.
30. Offline stock validation does not replace server authority.
31. Offline stock conflicts are explicit.
32. Offline payments use stable UUIDs.
33. Offline payment amounts are server-validated.
34. Offline Card recording does not imply external processor authorization.
35. Offline Cash payments retain Cash Session context.
36. Offline overpayments follow the same Business rules as online overpayments.
37. Confirmed overpayment belongs to the Business/Branch.
38. Offline debt repayments preserve Customer and Debt Order context.
39. Offline Cash Sessions use stable UUIDs.
40. Offline handover preserves previous and new Cash Session identity.
41. Offline cash corrections cannot bypass correction limits.
42. Offline inventory adjustments require inventory permission.
43. Offline attendance events use stable UUIDs.
44. Offline payroll cannot become more authoritative than server payroll.
45. Offline configuration uses a version identity.
46. Offline transactions preserve the configuration version used.
47. Historical transaction snapshots are not silently rewritten after synchronization.
48. Transaction synchronization precedes configuration synchronization where required.
49. Offline notifications remain permission-controlled.
50. Offline notifications reconcile with server state.
51. Offline state-changing operations produce audit events where required.
52. Offline audit Event UUIDs remain stable.
53. Offline audit history is not silently replaced by synchronization.
54. Pending synchronization events are durably stored.
55. Pending events are not silently deleted because storage is low.
56. Dependent events preserve logical order.
57. Synchronization is idempotent.
58. Duplicate synchronization cannot create duplicate business effects.
59. Temporary synchronization failures may be retried.
60. Failed synchronization events remain identifiable.
61. Conflicts are explicitly recorded.
62. Conflict resolution is separately authorized and audited.
63. Original offline events remain immutable.
64. Server state is authoritative after synchronization.
65. Server authority does not erase historical offline evidence.
66. Clock rollback anomalies are detectable.
67. Clock anomalies are not silently corrected by rewriting history.
68. Offline device revocation is bounded by offline authorization lifetime.
69. Offline employee deactivation is enforced after server state becomes available.
70. Application restart must preserve durable pending synchronization state.
71. Fresh application installation does not automatically restore offline trust.
72. Local storage failure blocks unsafe offline operations.
73. Replay protection prevents duplicate business effects.
74. Multiple trusted devices retain separate Device identity.
75. Multiple devices may participate in one Cash Session only when authorized.
76. Every offline transaction preserves Employee context.
77. Every offline transaction preserves Device context.
78. Cash operations preserve Cash Session context.
79. Offline operation cannot bypass Business isolation.
80. Offline operation cannot bypass Branch isolation.
81. Offline operation cannot bypass permission rules.
82. Offline operation cannot bypass subscription entitlement.
83. Offline operation cannot bypass historical integrity.
84. Synchronization must not block normal POS unnecessarily.
85. Background synchronization must be recoverable after worker/device failure.
86. Local storage capacity is bounded.
87. Low storage must not trigger silent deletion of pending transactions.
88. Offline reports are not automatically server-authoritative finalized reports.
89. Server-generated report versions remain authoritative.
90. Offline data lifecycle follows Business subscription and deletion rules.
91. Local offline authority expires when its authorization expires.
92. Offline recovery preserves UUID identity.
93. Offline recovery preserves transaction ordering where required.
94. Offline recovery preserves audit traceability.
95. Offline recovery must be idempotent.
96. Offline operation must remain secure without requiring continuous network access.
97. Offline capability must not become a permanent authorization mechanism.
98. Business correctness has priority over silent synchronization convenience.
99. Historical integrity has priority over last-write-wins behavior.
100. Offline continuity must not compromise tenant isolation, authorization or data integrity.

---

## 80. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/15_Employees_Attendance_and_Payroll.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/10_Kitchen_and_Printing.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/12_Debt_and_Payment_Allocation.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/15_Shift_Handover.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/19_Attendance_and_Payroll.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/21_Notifications_and_Alerts.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 81. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `23_Offline_Operation.md`

**Next Document:** `24_Synchronization_and_Conflict_Resolution.md`

