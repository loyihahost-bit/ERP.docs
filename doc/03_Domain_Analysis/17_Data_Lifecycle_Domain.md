# Data Lifecycle Domain

**Document ID:** DA-17
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/README.md`

---

## 1. Purpose

The Data Lifecycle Domain defines how Business data moves through its operational lifecycle from active usage to expiration, deletion eligibility, permanent deletion, and final deleted state.

The domain ensures that:

* active Business data remains operational;
* expired subscriptions do not immediately destroy data;
* read-only access remains available during the allowed period;
* the 60-day deletion period is measured from the exact subscription expiration timestamp;
* users receive advance warnings;
* reactivation remains possible during the retention window;
* permanent deletion is controlled and recoverable from technical failures;
* stale offline data cannot resurrect deleted Business data;
* deletion does not create cross-tenant leakage;
* historical integrity is preserved until the applicable deletion point.

---

# 2. Domain Responsibility

The Data Lifecycle Domain is responsible for:

1. Business data lifecycle state.
2. Subscription-expiry-related data retention.
3. Deletion eligibility.
4. Pre-deletion warnings.
5. Permanent deletion scheduling.
6. Deletion execution.
7. Deletion retries.
8. Partial deletion recovery.
9. Tenant isolation during deletion.
10. Reactivation versus deletion race handling.
11. Offline and synchronization interaction with deletion.
12. Post-deletion behavior.
13. Historical deletion records where applicable.
14. Lifecycle audit integration.

The domain does not own:

* subscription pricing;
* permission calculation;
* operational order processing;
* report generation;
* synchronization transport;
* database-specific deletion implementation.

Those responsibilities remain with their respective domains.

---

# 3. Core Principle

The central principle is:

> Data must never be permanently deleted merely because a subscription temporarily expires.

Instead, the lifecycle provides a controlled retention period.

The conceptual lifecycle is:

```text
Active
   ↓
Expired / Read-Only
   ↓
Deletion Eligible
   ↓
Deleting
   ↓
Deleted
```

Reactivation may return the Business from:

```text
Expired / Read-Only
        ↓
     Active
```

before permanent deletion begins or completes, according to the established lifecycle rules.

---

# 4. Business Lifecycle Context

The lifecycle is applied at Business level.

Conceptually:

```text
Platform
   ↓
Business
   ├── Branches
   ├── Employees
   ├── Orders
   ├── Cash
   ├── Inventory
   ├── Payments
   ├── Reports
   ├── Audit
   └── Configuration
```

When the Business enters a lifecycle state, dependent data must follow the corresponding Business lifecycle rules.

---

# 5. Lifecycle States

## 5.1 Active

The Business has an active subscription and may use its entitled modifying operations.

Normal operations are available according to:

* subscription entitlement;
* permissions;
* branch scope;
* device trust;
* business rules.

---

## 5.2 Expired / Read-Only

The subscription has expired.

Modifying operations are blocked according to Subscription Domain rules.

Allowed operations may include:

* viewing existing data;
* viewing history;
* viewing reports;
* permitted Excel exports.

The Business data itself remains preserved.

---

## 5.3 Deletion Eligible

The retention period has elapsed without successful reactivation.

The Business becomes eligible for permanent deletion.

This does not necessarily mean that deletion is instantaneous.

A deletion job must transition the Business into the deletion execution state.

---

## 5.4 Deleting

Permanent deletion is being executed.

The deletion process may operate through multiple dependency-aware stages.

The Business must not return to normal active operation while deletion is underway unless an explicitly defined recovery mechanism safely restores the lifecycle.

---

## 5.5 Deleted

Permanent deletion has completed according to the applicable deletion policy.

Normal Business access is no longer available.

Stale offline or synchronization operations must not recreate the deleted Business.

---

# 6. Subscription Expiration Reference

The deletion countdown is based on the exact:

`subscription_expired_at`

timestamp.

The system must not calculate the 60-day retention period from:

* the date the user notices expiry;
* the date of the first notification;
* the date of the first failed operation;
* the date of the last login.

The authoritative reference is the server-side subscription expiration timestamp.

---

# 7. 60-Day Retention Period

If the subscription is not reactivated within 60 days from `subscription_expired_at`, the Business becomes eligible for permanent deletion.

Conceptually:

```text
subscription_expired_at
        │
        ├── Read-only period
        │
        ├── Warning period
        │
        └── 60 days
              ↓
      Deletion Eligible
```

The exact warning thresholds remain configurable according to business configuration and notification rules.

---

# 8. Reactivation

A Business may be reactivated during the allowed retention period.

Successful reactivation restores:

* active operational access;
* subscription entitlements;
* configuration;
* retained Business data;
* branches;
* employees;
* orders;
* inventory;
* reports;
* audit/history;
* other retained domain data.

Reactivation does not create a new Business identity.

---

# 9. Business Identity Preservation

Business UUID must remain stable during:

* subscription expiry;
* read-only state;
* reactivation;
* deletion eligibility;
* deletion processing.

If a Business is permanently deleted, its identity must not be silently reused for another Business.

---

# 10. Data Preservation During Read-Only State

During the read-only period, the system must preserve the Business's historical data.

This includes, where applicable:

* orders;
* payments;
* refunds;
* debt;
* cash sessions;
* inventory;
* recipes;
* menu configuration;
* employee history;
* payroll history;
* reports;
* report versions;
* audit history;
* notifications;
* synchronization history.

Read-only state must not trigger destructive cleanup.

---

# 11. Modification Restrictions

After subscription expiry, modifying operations are blocked according to Subscription Domain rules.

Examples include:

* creating new orders;
* accepting new orders;
* changing inventory;
* modifying menu configuration;
* changing prices;
* changing employees;
* changing permissions;
* creating new payroll operations;
* modifying business configuration.

Viewing historical data remains possible according to permission.

---

# 12. Open Operational State at Expiry

Subscription expiry must not silently destroy active operational state.

Examples:

* open orders;
* open Cash Session;
* unpaid orders;
* pending synchronization;
* pending reports;
* unresolved conflicts.

The system preserves these states according to their domain lifecycle.

New modifying operations are blocked.

---

# 13. Offline Data at Expiry

Offline authorization is bounded by the offline authorization rules.

If a device is offline when the subscription expires:

* it may continue only while its valid offline authorization permits;
* it must not operate indefinitely;
* once the offline authorization expires, modifying operations are blocked;
* synchronization after expiry remains subject to server-side lifecycle validation.

Offline mode must never extend the Business retention period.

---

# 14. Pending Offline Operations

Pending offline operations are not automatically deleted when the Business enters read-only state.

They remain identifiable.

Upon synchronization, the server determines whether each operation is:

* accepted;
* rejected;
* conflicted;
* invalid due to lifecycle state.

The system must not silently discard pending business operations.

---

# 15. Deletion Eligibility

A Business becomes `Deletion Eligible` when:

1. subscription has expired;
2. the 60-day retention period has elapsed;
3. the Business has not been successfully reactivated.

The eligibility decision must be based on server time.

---

# 16. Deletion Warnings

The system should notify authorized users before permanent deletion.

Notifications may be issued at configured thresholds.

Warnings should communicate:

* current lifecycle state;
* remaining retention time;
* exact or approximate deletion date;
* action required to retain data;
* consequences of permanent deletion.

Notification delivery failure must not alter the lifecycle state.

---

# 17. Deletion Eligibility Is Not Immediate Deletion

The transition:

```text
Expired / Read-Only
        ↓
Deletion Eligible
```

does not require the data to disappear immediately.

It creates permission for the deletion process to begin.

A background deletion job is responsible for actual deletion.

---

# 18. Deletion Job

Permanent deletion should be executed by a durable background job.

The job must:

* identify the Business;
* validate lifecycle state;
* validate deletion eligibility;
* execute dependency-aware deletion;
* record progress;
* handle failures;
* retry safely;
* avoid duplicate deletion;
* transition to `Deleted` only after completion.

---

# 19. Deletion Validation

Before deletion starts, the system must verify:

* Business exists;
* Business is still deletion eligible;
* subscription has not been successfully reactivated;
* deletion has not already completed;
* no lifecycle transition invalidates the operation.

This validation must occur close to deletion execution time.

---

# 20. Reactivation vs Deletion Race

A critical race condition is:

```text
Deletion Job
       │
       ├── checks eligibility
       │
User ──┴── reactivates Business
```

The system must prevent deletion from completing against a successfully reactivated Business.

The reactivation and deletion transition must be coordinated atomically at the appropriate consistency boundary.

---

# 21. Deletion Lock / State Transition

When deletion begins, the Business enters `Deleting`.

The deletion process must not be treated as an ordinary modifying operation.

Lifecycle state changes must be serialized sufficiently to prevent:

* simultaneous reactivation;
* duplicate deletion;
* conflicting lifecycle transitions.

Exact locking and transaction strategy belongs to Architecture and Database phases.

---

# 22. Dependency-Aware Deletion

Business data has dependencies.

A conceptual deletion order may include:

```text
Operational Data
      ↓
Derived / Secondary Data
      ↓
Configuration
      ↓
Supporting Data
      ↓
Business Root
```

The exact physical deletion order belongs to Database Architecture.

The domain requirement is that dependent data must not be left in an inconsistent state.

---

# 23. Orders and Deletion

When a Business is permanently deleted:

* orders are deleted according to lifecycle policy;
* order history does not survive as active Business data;
* related payment, inventory, cash and audit references are handled according to dependency rules;
* stale offline orders cannot recreate the Business.

---

# 24. Financial Data

Financial information associated with the Business follows the same lifecycle policy unless a separate legal or regulatory retention requirement is introduced later.

Relevant data may include:

* payments;
* refunds;
* debt;
* overpayments;
* cash sessions;
* cash corrections;
* payroll.

The current product scope does not define external legal retention requirements.

Such requirements must be introduced separately if required.

---

# 25. Inventory Data

Inventory-related data follows the Business lifecycle.

This includes:

* products;
* stock balances;
* inventory movements;
* purchases;
* adjustments;
* discrepancies;
* recipes;
* recipe versions;
* Sets.

Deletion must preserve referential consistency during the deletion process.

---

# 26. Employee Data

Employee data remains preserved during:

```text
Active
Expired / Read-Only
Deletion Eligible
```

until permanent deletion begins.

Employee historical references must remain internally consistent during deletion.

Inactive employees are not automatically deleted merely because they are inactive.

---

# 27. Audit Data

Audit data remains available during the retention period according to authorization.

When permanent deletion occurs:

* applicable audit records are deleted with the Business;
* deletion itself may produce an external/system-level deletion record where technically required;
* deleted Business audit data cannot be recreated through stale synchronization.

---

# 28. Report Data

Report versions remain preserved during the retention period.

They may continue to be:

* viewed;
* downloaded;
* exported,

according to permissions and subscription lifecycle rules.

During deletion, report versions are deleted according to dependency rules.

---

# 29. Notification Data

Notification history follows the Business lifecycle.

During read-only state:

* historical notifications may remain viewable;
* no new operational notification should be generated for blocked operations unless lifecycle processing requires it.

Deletion removes Business-scoped notification history according to lifecycle policy.

---

# 30. Synchronization Data

Synchronization data is particularly important during deletion.

When a Business is deleted:

* pending synchronization events must not recreate the Business;
* queued events associated with the Business become invalid;
* synchronization must reject stale events;
* local clients must eventually receive the deleted state.

The server remains authoritative.

---

# 31. Stale Offline Event Protection

A stale offline event may contain a valid old Business UUID.

That does not make the Business valid after deletion.

The server must reject synchronization for deleted Businesses.

Therefore:

```text
Deleted Business
      ↑
Stale Offline Event
      X
Cannot recreate
```

---

# 32. Device Behavior After Deletion

Trusted devices associated with a deleted Business must no longer be able to perform normal Business operations.

The device may receive a lifecycle response indicating that the Business is deleted.

Offline modifying operations must be blocked.

Local Business data should be removed according to the local data lifecycle/security policy.

---

# 33. Local Storage Cleanup

After permanent deletion, locally stored Business data must be removed or invalidated according to the device security policy.

This may include:

* cached configuration;
* local orders;
* local payments;
* local inventory state;
* synchronization queue;
* offline authorization;
* local notifications.

The exact secure deletion mechanism belongs to Security and Architecture.

---

# 34. Partial Deletion

Permanent deletion may fail after some data has already been removed.

The system must therefore support resumable deletion.

Example:

```text
Deleting
   ↓
Orders deleted
   ↓
Payments deleted
   ↓
Inventory deletion fails
   ↓
Retry
```

The system must not mark the Business `Deleted` until the required deletion process has completed.

---

# 35. Idempotent Deletion

Deletion jobs must be idempotent.

Retrying a deletion step must not produce inconsistent results.

If an entity has already been deleted, a retry must recognize that state and continue safely.

---

# 36. Deletion Failure

Deletion failure must be:

* recorded;
* observable;
* retryable where appropriate;
* associated with the Business;
* protected against duplicate processing.

A failed deletion must not silently appear as successful.

---

# 37. Deletion Retry

Deletion retry should use the Background Jobs policy.

It should support:

* bounded retries;
* backoff;
* failure classification;
* manual intervention where required;
* final failure state if automatic recovery is exhausted.

A failed deletion remains identifiable until resolved.

---

# 38. Permanent Deletion

Permanent deletion means that Business operational data is no longer available through normal product interfaces.

The exact technical definition of "permanent" is dependent on:

* database storage;
* backups;
* disaster recovery;
* legal retention requirements;
* infrastructure policies.

Those technical retention questions belong to Architecture and Operations.

---

# 39. Backups

The Data Lifecycle Domain does not define physical backup deletion schedules.

However, the Architecture and Operations phases must define how permanent Business deletion interacts with:

* database backups;
* snapshots;
* disaster recovery copies;
* replicated storage.

The product lifecycle must not falsely claim that all physical copies have disappeared unless the infrastructure policy guarantees it.

---

# 40. Post-Deletion Access

After `Deleted`:

* normal login must fail;
* Business operational data cannot be viewed;
* modifying operations are impossible;
* synchronization is rejected;
* old trusted devices cannot regain operational access.

The system may expose only minimal platform-level lifecycle information where necessary.

---

# 41. Deleted Business Identity

A deleted Business UUID must not be reassigned.

This prevents historical ambiguity and prevents stale offline data from accidentally targeting a new Business.

---

# 42. Reactivation After Deletion

Normal product reactivation is available only during the permitted retention window before permanent deletion.

After the Business reaches the completed `Deleted` state, ordinary reactivation is not available.

Any exceptional recovery would be an infrastructure/administrative recovery process rather than normal Business reactivation.

---

# 43. Data Export Before Deletion

During the read-only retention period, authorized users may export permitted historical data in `.xlsx` format.

Export does not stop or reset the deletion countdown.

Export does not reactivate the Business.

---

# 44. Deletion Countdown

The countdown must be deterministic.

Conceptually:

```text
Deletion Date =
subscription_expired_at + 60 days
```

The calculation must use server time.

The UI may show:

* days remaining;
* hours remaining;
* exact deletion timestamp where appropriate.

The countdown must not be reset by:

* login;
* viewing data;
* exporting data;
* opening the application;
* offline operation.

Only valid reactivation changes the lifecycle.

---

# 45. Lifecycle Transitions

The conceptual state machine is:

```text
Active
  │
  │ subscription expires
  ▼
Expired / Read-Only
  │
  ├──────────────► Active
  │                 ↑
  │                 │ successful reactivation
  │
  │ 60 days elapsed
  ▼
Deletion Eligible
  │
  ▼
Deleting
  │
  ▼
Deleted
```

Invalid transitions must be rejected.

---

# 46. Lifecycle History

Important lifecycle transitions should be historically traceable.

Examples:

* subscription expired;
* read-only state entered;
* reactivated;
* deletion eligibility reached;
* deletion started;
* deletion failed;
* deletion retried;
* deletion completed.

The history should preserve:

* previous state;
* new state;
* timestamp;
* actor/system source;
* reason where applicable.

---

# 47. Domain Events

Potential lifecycle events include:

* `BusinessSubscriptionExpired`
* `BusinessEnteredReadOnly`
* `BusinessReactivated`
* `BusinessDeletionEligible`
* `BusinessDeletionStarted`
* `BusinessDeletionRetryScheduled`
* `BusinessDeletionFailed`
* `BusinessDeleted`

These events are conceptual and their exact transport belongs to Architecture and Backend phases.

---

# 48. Notifications

The lifecycle may trigger notifications for:

* subscription expiration;
* remaining retention period;
* approaching deletion;
* deletion eligibility;
* deletion failure;
* deletion completion where appropriate.

Notification failure must not change the lifecycle state.

---

# 49. Domain Services

Potential conceptual services include:

### LifecycleService

Controls valid Business lifecycle transitions.

### DeletionEligibilityService

Determines whether the Business has reached the deletion threshold.

### ReactivationService

Restores an eligible Business to Active state.

### DeletionCoordinator

Coordinates dependency-aware permanent deletion.

### DeletionRecoveryService

Handles retry and recovery after partial deletion.

### LifecycleValidationService

Validates lifecycle transitions and race conditions.

### LocalDataInvalidationService

Coordinates client-side invalidation after deletion.

These services are conceptual. Exact implementation belongs to later technical phases.

---

# 50. Aggregate Boundary

The central lifecycle aggregate is conceptually:

```text
Business Lifecycle
 ├── Business UUID
 ├── Current Lifecycle State
 ├── Subscription Expiration Reference
 ├── Deletion Eligibility Time
 ├── Deletion State
 ├── Lifecycle Version
 └── Transition History References
```

The lifecycle aggregate does not contain the entire Business dataset.

It controls lifecycle transitions over the Business root.

---

# 51. Concurrency Requirements

Lifecycle transitions require strong concurrency protection.

Important races include:

### Reactivation vs Deletion

Only one valid outcome may commit.

### Multiple Deletion Workers

Only one deletion execution may own the Business deletion process.

### Subscription Renewal vs Expiry

The server must evaluate the authoritative subscription state.

### Synchronization vs Deletion

A stale synchronization request must not recreate deleted data.

### Multiple Lifecycle Requests

Repeated requests must be idempotent.

---

# 52. Data Lifecycle and Subscription Domain

The Subscription Domain determines:

* subscription state;
* entitlement;
* expiration;
* reactivation.

The Data Lifecycle Domain determines:

* retention;
* deletion eligibility;
* deletion execution;
* permanent deletion.

The domains must remain separate.

---

# 53. Data Lifecycle and Audit Domain

Important lifecycle transitions must be auditable.

Deletion must preserve enough technical evidence to establish:

* which Business was deleted;
* when deletion started;
* when deletion completed;
* which system process performed it;
* whether retries occurred.

Business audit data itself may be deleted as part of Business deletion.

Any required platform-level deletion evidence must be stored separately from the deleted Business dataset.

---

# 54. Data Lifecycle and Synchronization Domain

Synchronization must respect lifecycle state.

The rules are:

```text
Active
→ Synchronization allowed

Expired / Read-Only
→ Server validation required

Deletion Eligible
→ New modifying operations blocked

Deleting
→ Business synchronization rejected

Deleted
→ Synchronization rejected
```

The exact handling of already queued events depends on their lifecycle and validation state.

---

# 55. Data Lifecycle and Background Jobs

Background jobs are responsible for:

* lifecycle checks;
* warning notifications;
* deletion eligibility transitions;
* deletion execution;
* retry;
* recovery.

Jobs must be:

* durable;
* idempotent;
* observable;
* retryable.

---

# 56. Security Requirements

Lifecycle operations are security-sensitive.

The system must protect against:

* unauthorized reactivation;
* unauthorized deletion;
* deletion bypass;
* subscription manipulation;
* stale offline authorization;
* Business UUID substitution;
* cross-tenant deletion.

Server-side authorization is mandatory.

---

# 57. Performance Requirements

Lifecycle processing must not interfere with POS operations.

Therefore:

* deletion must run in background;
* large deletion operations should be batched;
* lifecycle checks should be lightweight;
* notification generation should be asynchronous;
* heavy cleanup must not consume excessive resources on active Businesses.

---

# 58. Observability

The system should expose operational information such as:

* Businesses approaching deletion;
* Businesses eligible for deletion;
* deletion jobs running;
* deletion duration;
* deletion failures;
* retry count;
* stuck deletion jobs;
* number of successfully deleted Businesses.

These metrics are operational data, not Business audit history.

---

# 59. Data Lifecycle Invariants

### Lifecycle

1. Every Business has a defined lifecycle state.
2. Lifecycle transitions follow the allowed state machine.
3. Invalid lifecycle transitions are rejected.
4. Lifecycle state is server-authoritative.
5. Lifecycle transitions are historically traceable.

### Expiration

6. Subscription expiration uses the server-authoritative expiration timestamp.
7. Expiry does not immediately delete Business data.
8. Expiry transitions the Business into read-only behavior.
9. Read-only state preserves historical data.
10. Login or viewing data does not reset the deletion countdown.

### Retention

11. The retention period is measured from `subscription_expired_at`.
12. The standard retention period is 60 days.
13. The countdown is not reset by data export.
14. The countdown is not reset by application login.
15. The countdown is not reset by offline operation.

### Reactivation

16. Reactivation is allowed during the retention period.
17. Successful reactivation returns the Business to Active.
18. Reactivation preserves the Business UUID.
19. Reactivation preserves retained historical data.
20. Reactivation restores applicable configuration.

### Deletion Eligibility

21. A Business becomes deletion eligible only after the retention period.
22. Deletion eligibility requires that the Business has not been reactivated.
23. Deletion eligibility is based on server time.
24. Eligibility does not itself imply completed deletion.

### Deletion

25. Deletion requires explicit lifecycle validation.
26. Deletion runs through controlled background processing.
27. Deletion is dependency-aware.
28. Deletion is idempotent.
29. Deletion progress remains recoverable.
30. Deletion failure is observable.

### Concurrency

31. Reactivation and deletion cannot both successfully finalize against the same lifecycle state.
32. Multiple deletion workers cannot independently delete the same Business.
33. Duplicate deletion requests are safe.
34. Subscription renewal is evaluated against authoritative server state.
35. Synchronization cannot bypass deletion state.

### Offline

36. Offline authorization cannot extend Business retention indefinitely.
37. Expired offline authorization blocks modifying operations.
38. Stale offline events cannot recreate deleted Business data.
39. Offline Business UUIDs cannot be reassigned.
40. Local deletion state eventually invalidates offline operation.

### Synchronization

41. Deleted Businesses reject new synchronization.
42. Synchronization does not reset lifecycle state.
43. Pending synchronization events remain identifiable.
44. Invalid lifecycle synchronization failures are traceable.
45. Synchronization retries do not recreate deleted entities.

### Tenant Isolation

46. Deletion applies only to the intended Business.
47. Cross-tenant deletion is impossible through normal APIs.
48. Branch data is deleted only as part of its owning Business lifecycle.
49. Business identity cannot be substituted through client input.
50. Deleted Business data cannot become accessible to another Business.

### Historical Integrity

51. Lifecycle transitions preserve transition history.
52. Deletion does not silently modify lifecycle history.
53. Reactivation does not erase previous expiration history.
54. Audit references remain historically meaningful until applicable deletion.
55. Report history remains preserved during the retention period.

### Notifications

56. Lifecycle warnings do not modify lifecycle state.
57. Notification failure does not prevent lifecycle transition.
58. Notification thresholds are applied consistently.
59. Duplicate lifecycle notifications are prevented according to Notification Domain rules.

### Background Processing

60. Deletion jobs are durable.
61. Deletion jobs are retryable.
62. Deletion jobs are idempotent.
63. Failed jobs remain observable.
64. Multiple workers cannot produce conflicting deletion outcomes.

### Partial Deletion

65. Partial deletion does not incorrectly mark the Business Deleted.
66. Failed deletion steps can be retried safely.
67. Already deleted records are handled safely on retry.
68. Dependency failures remain visible.
69. A Business reaches Deleted only after required deletion completes.

### Post-Deletion

70. Deleted Businesses cannot be normally logged into.
71. Deleted Businesses cannot accept normal synchronization.
72. Deleted Business identities are not reused.
73. Trusted devices cannot bypass deletion.
74. Normal reactivation is unavailable after completed deletion.

### Security

75. Deletion requires server-side authorization.
76. Reactivation requires server-side authorization.
77. Lifecycle manipulation cannot be performed through stale offline authorization.
78. Cross-tenant lifecycle operations are rejected.
79. Lifecycle security failures are observable.

### Performance

80. Deletion does not block normal POS operation for other active Businesses.
81. Heavy deletion work runs in background.
82. Lifecycle processing uses bounded resources.
83. Large Business deletion supports controlled batching.

### Recovery

84. Deletion can recover from worker restart.
85. Deletion can recover from database/network failures.
86. Lifecycle state survives application restart.
87. Failed deletion does not falsely report completion.
88. Retry does not create inconsistent lifecycle state.

### Final Integrity

89. Business data is not permanently deleted before the defined retention period.
90. Permanent deletion cannot be silently bypassed.
91. Permanent deletion cannot be silently duplicated.
92. Stale offline data cannot resurrect a deleted Business.
93. Lifecycle state remains server-authoritative.
94. Business UUID remains stable until deletion.
95. Historical data remains intact during read-only retention.
96. Deletion eligibility is deterministic.
97. Reactivation and deletion race is resolved atomically.
98. Lifecycle transitions are traceable.
99. Data deletion respects tenant boundaries.
100. The lifecycle domain never silently rewrites historical lifecycle facts.

---

# 60. Completion Criteria

The Data Lifecycle Domain is considered complete when:

* Business lifecycle states are defined;
* Active state is defined;
* Expired/Read-Only state is defined;
* Deletion Eligible state is defined;
* Deleting state is defined;
* Deleted state is defined;
* 60-day retention is defined;
* `subscription_expired_at` is the authoritative reference;
* warning behavior is defined;
* reactivation is defined;
* deletion eligibility is defined;
* deletion execution is defined;
* deletion retry is defined;
* partial deletion recovery is defined;
* idempotent deletion is defined;
* lifecycle concurrency is defined;
* reactivation/deletion race is defined;
* offline behavior is defined;
* synchronization behavior is defined;
* stale offline event protection is defined;
* tenant isolation is defined;
* audit interaction is defined;
* report interaction is defined;
* notification interaction is defined;
* background job interaction is defined;
* local device invalidation is defined;
* post-deletion behavior is defined;
* lifecycle history is defined;
* domain services are identified;
* domain events are identified;
* aggregate boundary is identified;
* invariants are documented.

---

# 61. Related Documents

## Business Analysis

* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

## System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

## Domain Analysis

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/14_Notification_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`

## Future Dependencies

The Data Lifecycle Domain will provide requirements for:

* `04_Architecture`
* `05_Database`
* `06_Backend`
* `09_API`
* `11_Security`
* `12_Testing`
* `14_Operations`

The Data Lifecycle Domain must be finalized before implementation decisions regarding deletion orchestration, retention storage, backup handling, tenant cleanup, local-device invalidation, and permanent deletion guarantees are finalized.

