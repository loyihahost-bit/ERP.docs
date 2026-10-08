# Subscription and Entitlement

**Document ID:** SA-25
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines how subscription state and effective entitlements control access to FastFood ERP functionality.

Subscription and entitlement control must be:

* server-authoritative;
* Business-specific;
* predictable;
* historically traceable;
* safe during downgrade and expiry;
* compatible with offline operation;
* independent from UI-only restrictions.

Subscription enforcement must protect business rules without unnecessarily interrupting read access to historical data.

---

## 2. Scope

This document covers:

* subscription identity;
* tariff;
* subscription lifecycle;
* entitlement;
* feature access;
* employee limits;
* Branch limits;
* tariff configuration;
* configuration versioning;
* effective entitlement;
* subscription activation;
* renewal;
* grace period;
* expiry;
* read-only state;
* downgrade;
* reactivation;
* offline entitlement;
* session behavior;
* server-side enforcement;
* historical entitlement;
* notifications;
* reports;
* data lifecycle;
* audit;
* concurrency;
* error handling;
* system invariants.

---

## 3. Subscription Context

A subscription belongs to one Business.

The subscription context includes:

* Business UUID;
* subscription UUID;
* tariff;
* tariff configuration/version;
* start time;
* expiration time;
* lifecycle state;
* entitlement version;
* transition history.

A subscription must never be shared across Businesses.

---

## 4. Subscription Identity

Every subscription has a stable UUID.

The Subscription UUID identifies the subscription lifecycle independently from:

* Business UUID;
* Tariff UUID;
* payment transaction;
* entitlement version.

Renewal must not require replacing the Business identity.

---

## 5. Tariff

A tariff defines the available commercial limits and enabled functionality.

A tariff may control:

* Branch limit;
* Owner limit;
* Employee limit;
* available features;
* other supported business limits.

Tariff configuration is managed at the platform level.

---

## 6. Tariff Version

Tariff configuration is versioned.

A tariff version may define:

* enabled features;
* limits;
* effective date;
* configuration state.

A historical subscription must retain the tariff/entitlement context that applied to it.

---

## 7. Effective Entitlement

The effective entitlement for a Business is determined by:

```text id="ent372"
Subscription
+
Tariff Version
+
Entitlement Configuration
+
Business State
```

The effective entitlement determines what the Business can currently do.

---

## 8. Entitlement Evaluation

For a modifying operation, the backend evaluates:

1. Business identity;
2. subscription state;
3. effective entitlement;
4. Employee status;
5. permission;
6. Branch scope;
7. device authorization where applicable.

Frontend visibility is only a convenience.

It is not an authorization mechanism.

---

## 9. Server-Side Enforcement

All important entitlement checks must be performed server-side.

A user must not be able to bypass subscription restrictions by:

* modifying frontend code;
* calling API endpoints directly;
* using stale client state;
* using an offline device outside its authorization;
* replaying old requests.

---

## 10. Active Subscription

An active subscription allows operations permitted by the effective entitlement.

The Business may:

* create permitted data;
* modify permitted data;
* use permitted features;
* operate authorized Branches;
* manage permitted employees.

The exact limits are determined by the current entitlement.

---

## 11. Subscription Lifecycle

The subscription lifecycle includes:

```text id="sub614"
Active
  ↓
Grace
  ↓
Expired / Read-Only
  ↓
Deletion Eligible
  ↓
Deleting
  ↓
Deleted
```

The exact transition depends on renewal and data lifecycle rules.

---

## 12. Subscription Start

A subscription becomes active according to its configured start time.

The system records:

* subscription UUID;
* Business;
* tariff;
* tariff version;
* start time;
* expiration time;
* entitlement version.

---

## 13. Subscription Renewal

A renewal extends or creates the applicable subscription period according to the selected tariff and renewal transaction.

Renewal must preserve historical subscription periods.

The system must not rewrite previous subscription history.

---

## 14. Renewal Payment Failure

If a renewal payment fails:

* the subscription follows the defined lifecycle policy;
* notification is generated according to applicable thresholds;
* the Business may enter the configured grace period;
* modifying access is determined by the effective subscription state.

---

## 15. Grace Period

The current default renewal grace period is:

**3 calendar days.**

The grace period is part of the subscription lifecycle.

The Business cannot extend it locally.

---

## 16. Grace Period Entitlement

During the grace period, access is determined by the subscription lifecycle policy.

The system must explicitly determine whether modifying operations remain allowed or become restricted according to the configured entitlement state.

Offline authorization may only continue operations within its server-issued entitlement bounds.

---

## 17. Subscription Expiry

The exact expiry moment is determined by server time.

The lifecycle countdown begins at:

`subscription_expired_at`

not when the user first notices the expiration.

---

## 18. Active Session After Expiry

If a user is already logged in when the subscription expires:

* the system does not automatically log them out;
* the next modifying operation performs an entitlement check;
* unauthorized modification is rejected;
* allowed read operations remain available.

This prevents sudden session interruption while maintaining server authority.

---

## 19. Read-Only State

After subscription expiry according to lifecycle rules, the Business may enter read-only state.

Read-only access may include:

* viewing existing data;
* viewing history;
* viewing reports;
* viewing audit records according to permission;
* permitted Excel exports.

Modifying operations are blocked.

---

## 20. Read-Only Enforcement

Read-only enforcement is server-side.

The backend must reject modifying requests even if:

* the frontend still displays a modification control;
* the device has stale configuration;
* an old API request is replayed.

---

## 21. Data Preservation During Expiry

Subscription expiry does not immediately delete Business data.

Existing:

* Orders;
* Payments;
* Inventory;
* Employees;
* Payroll;
* Reports;
* Audit history;
* configuration history

remain available according to access and lifecycle rules.

---

## 22. Branch Limits

A tariff may define a maximum number of active Branches.

If the Business reaches the Branch limit:

* existing Branches remain;
* new Branch creation is blocked;
* historical Branch data is preserved.

Downgrade must not silently delete Branches.

---

## 23. Owner Limits

A tariff may define a maximum number of Owners.

If the Business reaches the Owner limit:

* existing Owners remain;
* creation of additional Owners is blocked;
* historical Owner data remains preserved.

Downgrade must not silently remove existing Owners.

---

## 24. Employee Limits

A tariff may define an employee limit.

If the Business reaches the limit:

* existing employees remain;
* creation of additional employees is blocked;
* existing historical employee data remains preserved.

---

## 25. Employee Limit Downgrade

If a Business downgrades to a lower employee limit:

* existing employees are not automatically deleted;
* existing history remains;
* new employee creation may be blocked;
* the Business is informed that the current employee count exceeds the new limit.

The system must not silently deactivate employees merely because of a downgrade unless a separate explicit business policy is introduced.

---

## 26. Feature Entitlement

A tariff may enable or disable specific features.

Examples:

* advanced inventory functionality;
* payroll;
* advanced reports;
* additional operational capabilities.

If a feature becomes unavailable:

* existing data is preserved;
* historical data remains viewable where permitted;
* new modifying operations using the feature are blocked.

---

## 27. Feature Downgrade

Feature downgrade is non-destructive.

The system must preserve:

* feature-generated data;
* history;
* audit;
* reports;
* configuration.

The system blocks operations that require an unavailable entitlement.

---

## 28. Business Configuration After Downgrade

Configuration belonging to a disabled feature is preserved where technically possible.

The configuration is not automatically deleted.

If the Business later reactivates the feature, existing configuration may become available again according to its validity.

---

## 29. Reactivation

If the Business reactivates before permanent deletion:

* existing Business data remains;
* existing configuration remains;
* historical records remain;
* applicable entitlements become active again;
* permitted modifying operations resume.

Reactivation does not create a new Business identity.

---

## 30. Reactivation Before Deletion

If reactivation occurs before the deletion point:

* deletion eligibility is cancelled;
* deletion jobs must not remove Business data;
* the active subscription becomes authoritative;
* previous data/configuration remains available.

The race between reactivation and deletion must be handled atomically.

---

## 31. Deletion Eligibility

After the defined retention period following subscription expiration, the Business may become eligible for permanent deletion.

The current Business rule is:

**60 calendar days from `subscription_expired_at`.**

The deletion lifecycle is defined in:

`docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`

---

## 32. Subscription History

The system retains subscription history including:

* tariff;
* tariff version;
* start time;
* expiration time;
* renewal;
* grace period;
* downgrade;
* upgrade;
* feature changes;
* entitlement transitions.

Historical subscription information must remain immutable.

---

## 33. Entitlement Version

Each effective entitlement configuration has a version identity.

This allows the system to determine which entitlement was active at a given time.

Historical business operations should be explainable using the applicable entitlement context where required.

---

## 34. Entitlement Transition

When entitlement changes:

* previous entitlement remains historical;
* new entitlement receives a new version;
* effective time is recorded;
* actor/system source is recorded;
* reason is recorded where applicable.

---

## 35. Tariff Changes

A tariff configuration change does not silently rewrite historical Business state.

New tariff configuration becomes effective according to its configured effective point.

Existing transactions remain based on their historical context.

---

## 36. Upgrade

An upgrade may increase:

* Branch limits;
* employee limits;
* Owner limits;
* enabled features.

The new entitlement becomes effective according to the subscription transition rules.

Historical data remains unchanged.

---

## 37. Downgrade

A downgrade may reduce:

* Branch limit;
* employee limit;
* Owner limit;
* available features.

Downgrade must be non-destructive.

The system blocks only operations that exceed the new entitlement.

---

## 38. Entitlement and Permissions

Subscription entitlement is one layer of authorization.

Effective access is conceptually:

```text id="auth851"
Subscription Entitlement
        +
Employee Status
        +
Role Permission
        +
Employee Override
        +
Branch Scope
        +
Device/Offline Authorization
```

A permission cannot grant access to a feature that the subscription does not provide.

---

## 39. Entitlement and Branch Context

A valid subscription does not automatically grant access to every Branch.

Branch scope remains controlled separately.

The system validates:

* Business;
* Branch;
* Employee;
* permission;
* subscription entitlement.

---

## 40. Entitlement and Device Trust

A trusted device does not bypass subscription restrictions.

The device must use a valid authorization containing applicable entitlement information.

---

## 41. Entitlement and Offline Operation

Offline authorization includes sufficient entitlement information to prevent unauthorized modification after expiry or downgrade.

Offline devices cannot:

* extend subscription;
* create new entitlement;
* enable disabled features;
* exceed limits;
* bypass read-only state.

---

## 42. Offline Entitlement Expiry

When offline entitlement expires:

* modifying operations are blocked;
* the device may remain usable for permitted local read operations;
* synchronization may continue;
* online reauthorization is required for further modifying operations.

---

## 43. Offline Configuration Version

Offline authorization and configuration should identify the entitlement/configuration version used by the device.

This helps the server determine whether an offline operation was created under valid authority.

---

## 44. Synchronization After Entitlement Change

When the device reconnects:

1. device authorization is checked;
2. subscription state is checked;
3. effective entitlement is checked;
4. pending events are validated;
5. conflicts/rejections are recorded;
6. new entitlement/configuration is synchronized.

Old offline authorization does not automatically override current server state.

---

## 45. Entitlement and Existing Sessions

Subscription changes do not necessarily terminate active sessions.

Instead:

* current session remains;
* next protected operation checks current entitlement;
* unauthorized operations are rejected.

This avoids unnecessary forced logout.

---

## 46. Entitlement and Background Jobs

Background jobs must also validate applicable Business entitlement.

A background worker must not perform an operation that the Business is no longer entitled to receive.

However, lifecycle-critical jobs such as:

* expiry processing;
* notification generation;
* deletion lifecycle;
* reconciliation

may operate as system-level lifecycle jobs according to platform authority.

---

## 47. Entitlement and Reports

Report access is controlled by:

* Business;
* Branch;
* report permission;
* subscription entitlement;
* read-only state.

During read-only retention, allowed historical reports remain accessible.

---

## 48. Entitlement and Excel Export

Where Business policy permits read-only export:

* `.xlsx` export remains available;
* export permission remains required;
* subscription read-only rules apply.

Export does not restore modification rights.

---

## 49. Entitlement and Notifications

Subscription lifecycle may generate notifications for:

* upcoming expiry;
* grace period;
* expiry;
* read-only state;
* deletion warning.

Notifications are deduplicated according to the notification system.

---

## 50. Notification Thresholds

Subscription notification thresholds may be configured at the platform/business policy level as supported.

Threshold changes must preserve:

* old value;
* new value;
* actor/system;
* timestamp;
* reason.

Historical notifications are not rewritten.

---

## 51. Subscription Audit

Important subscription operations are auditable.

Examples:

* activation;
* renewal;
* upgrade;
* downgrade;
* entitlement change;
* feature change;
* expiry;
* grace transition;
* reactivation;
* deletion eligibility.

---

## 52. Subscription Concurrency

Subscription transitions must be concurrency-safe.

Examples:

* renewal vs expiry;
* reactivation vs deletion;
* upgrade vs downgrade;
* entitlement update vs modifying request.

The system must determine one authoritative transition order.

---

## 53. Renewal vs Expiry Race

If renewal and expiry processing occur concurrently:

* server-side transaction/locking or equivalent concurrency control determines the authoritative state;
* a successful valid renewal prevents incorrect expiry/deletion;
* duplicate renewal processing does not create duplicate subscription periods.

---

## 54. Reactivation vs Deletion Race

If reactivation and deletion are attempted concurrently:

* reactivation must atomically prevent deletion if it completes within the allowed lifecycle window;
* deletion must not claim success if reactivation already won;
* failure must be recorded and recoverable.

---

## 55. Duplicate Subscription Requests

Subscription operations use idempotency where appropriate.

Retrying the same renewal or entitlement operation must not create unintended duplicate effects.

---

## 56. Subscription Payment Context

Payment processing for subscription renewal is separate from Business operational payments.

The subscription system must retain its own:

* transaction identity;
* Business;
* subscription;
* amount;
* payment status;
* timestamp.

A Business operational Order payment must not be confused with a subscription payment.

---

## 57. Subscription State and Data State

Subscription state and Business data lifecycle state are related but distinct.

For example:

```text id="life713"
Subscription Expired
        ↓
Business Read-Only
        ↓
60-Day Retention
        ↓
Deletion Eligible
```

The system must not equate every subscription transition with immediate data deletion.

---

## 58. Subscription State Machine

A simplified state model is:

```text id="sm612"
Active
  ↓
Grace
  ↓
Expired / Read-Only
  ↓
Deletion Eligible
  ↓
Deleting
  ↓
Deleted
```

Reactivation may return the Business from an eligible read-only state to Active before permanent deletion.

---

## 59. State Transition Validation

Every subscription state transition must validate:

* current state;
* transition reason;
* effective time;
* authorization;
* Business identity;
* relevant payment/renewal context;
* applicable lifecycle policy.

Invalid transitions must be rejected.

---

## 60. Server Time

Subscription lifecycle calculations use server-authoritative time.

Client clock values must not determine:

* expiry;
* grace period;
* deletion eligibility;
* entitlement activation.

---

## 61. Historical Entitlement

Historical records must remain explainable even after tariff changes.

For example, a report or operation created under entitlement version `V1` must not be interpreted as though `V2` was active at that time.

---

## 62. Data Integrity During Downgrade

Downgrade must not silently delete:

* Branches;
* Employees;
* Owners;
* feature data;
* reports;
* history;
* configuration.

Only future operations that exceed entitlement are restricted.

---

## 63. Data Integrity During Expiry

Expiry must not:

* delete operational data;
* alter historical Order totals;
* rewrite payments;
* rewrite inventory history;
* delete audit history.

It changes the Business's ability to perform future modifications.

---

## 64. Subscription Read Access

Read-only access must still enforce:

* Business isolation;
* Branch scope;
* employee permissions;
* sensitive data restrictions.

Read-only does not mean unrestricted access.

---

## 65. Error Handling

Subscription errors should be classified as:

* Validation Error;
* Authorization Error;
* Entitlement Error;
* Conflict;
* Temporary Infrastructure Error;
* Permanent Failure.

Users should receive simple business-safe messages.

---

## 66. Entitlement Failure

If entitlement cannot be determined safely during a modifying request:

* the operation must not be allowed to bypass entitlement;
* the system may reject the operation temporarily;
* technical details are logged;
* recovery is attempted where appropriate.

Security and business integrity have priority over permissive failure.

---

## 67. Background Lifecycle Processing

Subscription lifecycle processing may be performed asynchronously.

Jobs may handle:

* expiry detection;
* grace transitions;
* notification generation;
* deletion eligibility;
* entitlement recalculation.

Jobs must be idempotent and recoverable.

---

## 68. Subscription Observability

Authorized platform operators should be able to observe:

* current subscription state;
* tariff;
* entitlement version;
* expiration time;
* grace state;
* renewal history;
* transition history;
* deletion eligibility.

Business users see only information permitted by their role.

---

## 69. System Invariants

The following invariants apply to Subscription and Entitlement:

1. Every subscription belongs to exactly one Business.
2. Every subscription has a stable UUID.
3. Tariffs are platform-managed.
4. Tariff configuration is versioned.
5. Historical tariff context is preserved.
6. Effective entitlement is server-determined.
7. Frontend visibility is not authorization.
8. Server-side entitlement enforcement is mandatory.
9. A subscription cannot grant access across Businesses.
10. Subscription entitlement does not replace Employee permissions.
11. Employee permission cannot grant a disabled subscription feature.
12. Branch scope remains separately enforced.
13. Trusted device status does not grant subscription entitlement.
14. Offline authorization is subscription-aware.
15. Offline authorization cannot extend subscription validity.
16. Offline authorization cannot create new entitlement.
17. Offline authorization cannot enable disabled features.
18. Offline authorization cannot bypass employee limits.
19. Offline authorization cannot bypass Branch limits.
20. Active subscription permits only currently entitled operations.
21. Subscription expiry is based on server time.
22. Expiry countdown begins at `subscription_expired_at`.
23. Active sessions are not automatically logged out solely because of expiry.
24. The next protected operation validates entitlement.
25. Read-only access may remain after expiry.
26. Read-only access remains permission-controlled.
27. Subscription expiry does not immediately delete Business data.
28. Branch limits do not automatically delete existing Branches.
29. Owner limits do not automatically delete existing Owners.
30. Employee limits do not automatically delete existing Employees.
31. Employee-limit downgrade is non-destructive.
32. Feature downgrade is non-destructive.
33. Disabled-feature data remains preserved where possible.
34. Reactivation before deletion restores applicable existing data/configuration.
35. Reactivation does not create a new Business identity.
36. Deletion eligibility begins 60 calendar days after `subscription_expired_at`.
37. Deletion lifecycle is server-controlled.
38. Subscription history is immutable.
39. Entitlement versions are identifiable.
40. Entitlement transitions preserve effective time.
41. Entitlement transitions preserve historical context.
42. Upgrade does not rewrite historical records.
43. Downgrade does not rewrite historical records.
44. Historical Orders retain historical configuration context.
45. Historical reports retain their historical entitlement context where required.
46. Subscription entitlement is one authorization layer among several.
47. Offline operations remain subject to entitlement bounds.
48. Synchronization revalidates subscription entitlement.
49. Expired offline authorization cannot create new modifying events.
50. Subscription changes do not automatically terminate active sessions.
51. Background lifecycle jobs are idempotent.
52. Lifecycle-critical jobs may operate under SYSTEM authority.
53. Subscription transition concurrency is controlled.
54. Renewal and expiry races are resolved deterministically.
55. Reactivation and deletion races are resolved atomically.
56. Duplicate subscription requests are idempotent where applicable.
57. Subscription payments are distinct from operational Order payments.
58. Subscription state and Business data lifecycle state remain logically distinct.
59. Invalid subscription transitions are rejected.
60. Client clocks do not determine subscription lifecycle.
61. Historical entitlement cannot be rewritten.
62. Downgrade does not silently delete Business data.
63. Expiry does not rewrite operational history.
64. Read-only access remains tenant-isolated.
65. Read-only access remains Branch-scoped where applicable.
66. Read-only access remains permission-controlled.
67. Export rights do not grant modification rights.
68. Subscription notification cycles are deduplicated.
69. Subscription threshold changes are historically traceable.
70. Subscription failures must not silently grant access.
71. Entitlement uncertainty must fail safely for modifying operations.
72. Subscription lifecycle jobs remain observable.
73. Subscription state transitions are auditable.
74. Subscription transition history is immutable.
75. Entitlement changes are attributable to an actor or SYSTEM.
76. Subscription lifecycle processing is recoverable after worker failure.
77. Subscription lifecycle operations are idempotent.
78. Subscription state must remain explainable at any point in its history.
79. Business data integrity has priority over convenience during downgrade/expiry.
80. Security has priority over permissive entitlement failure.
81. Server state remains authoritative for current entitlement.
82. Historical entitlement remains preserved for historical interpretation.
83. Offline devices cannot permanently operate on obsolete entitlement.
84. Subscription enforcement must apply consistently across API, background jobs and synchronization.
85. Subscription restrictions must not be enforceable only through the UI.
86. Subscription state must remain isolated per Business.
87. Tariff configuration changes must not silently alter historical subscription records.
88. Entitlement transitions must not create duplicate active states.
89. Only one authoritative current entitlement may apply to a Business at a time.
90. Subscription lifecycle must remain compatible with Business deletion lifecycle.
91. Deletion cannot be prevented by stale offline state.
92. Subscription renewal must not create duplicate historical periods through retry.
93. Subscription expiry must not create duplicate lifecycle transitions.
94. Grace-period transitions must be deterministic.
95. A Business cannot use a lower tariff's restrictions to erase higher-tariff historical data.
96. Existing data remains recoverable after temporary downgrade where reactivation restores the feature.
97. Subscription enforcement must preserve historical integrity.
98. Subscription enforcement must preserve Business and Branch isolation.
99. Subscription enforcement must preserve offline continuity within authorized bounds.
100. Subscription and entitlement management must provide predictable, auditable and recoverable state transitions.

---

## 70. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/21_Notifications_and_Alerts.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 71. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `25_Subscription_and_Entitlement.md`

**Next Document:** `26_Data_Lifecycle_and_Deletion.md`

