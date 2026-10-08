# Data Lifecycle and Deletion

**Document ID:** SA-26
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines how Business data is retained, restricted, archived, made eligible for deletion, permanently deleted, and protected during the deletion lifecycle.

The deletion system must:

* prevent accidental data loss;
* preserve historical integrity during normal operation;
* respect the subscription lifecycle;
* provide a defined retention period after subscription expiry;
* support safe permanent deletion;
* handle deletion failures and retries;
* prevent deletion when the Business is legitimately reactivated;
* remain idempotent;
* remain auditable;
* protect tenant isolation.

Permanent deletion is an explicit lifecycle process and must never be implemented as a simple destructive database operation triggered directly by subscription expiry.

---

## 2. Scope

This document covers:

* Business data lifecycle;
* active data;
* historical data;
* archived data;
* subscription expiry;
* read-only retention;
* deletion eligibility;
* deletion warnings;
* deletion scheduling;
* deletion jobs;
* deletion batches;
* partial deletion;
* retry;
* reactivation;
* deletion cancellation;
* dependency ordering;
* tenant isolation;
* audit records;
* offline data;
* synchronization;
* reports;
* notifications;
* backups and retained copies;
* security;
* concurrency;
* failure recovery;
* system invariants.

---

## 3. Data Lifecycle Model

Business data follows a controlled lifecycle.

```text
Active Business
      ↓
Subscription Expired
      ↓
Read-Only Retention
      ↓
Deletion Eligible
      ↓
Deleting
      ↓
Deleted
```

Reactivation before permanent deletion may return the Business to:

```text
Active Business
```

---

## 4. Business Lifecycle Context

Data lifecycle is associated with a Business.

The system must identify:

* Business UUID;
* subscription state;
* expiration timestamp;
* retention deadline;
* deletion eligibility;
* deletion state;
* deletion job state.

The lifecycle must never be determined only from client-side information.

---

## 5. Active State

While the Business is active:

* normal operations are available according to permissions and entitlement;
* data is created and modified according to system rules;
* historical records are preserved;
* archive rules apply where applicable.

Normal operational data is not subject to subscription deletion merely because it becomes old.

---

## 6. Historical Data

Historical data must remain available for the lifetime of the Business unless a specific lifecycle policy says otherwise.

Examples include:

* Orders;
* Payments;
* Refunds;
* Cash Sessions;
* Inventory movements;
* Payroll;
* Attendance;
* Reports;
* Audit events;
* configuration history.

Historical records must not be silently rewritten or removed during ordinary operations.

---

## 7. Archived Data

Archive is different from permanent deletion.

Archiving may be used for:

* inactive Products;
* old Recipes;
* inactive Employees;
* historical configurations;
* other business entities where defined.

Archived data remains part of the Business's historical data unless the Business lifecycle reaches permanent deletion.

---

## 8. Subscription Expiry

Subscription expiry does not immediately delete Business data.

After expiry, the Business enters the applicable read-only lifecycle.

The exact expiry moment is:

`subscription_expired_at`

Server time is authoritative.

---

## 9. Read-Only Retention

During the retention period, the Business may access permitted:

* existing data;
* historical data;
* reports;
* audit history;
* `.xlsx` exports.

Modification rights remain restricted according to subscription entitlement.

---

## 10. Retention Period

The current retention period after subscription expiry is:

**60 calendar days.**

The retention countdown begins from:

`subscription_expired_at`

not from:

* the last login;
* the first notification;
* the first read-only access;
* the first failed renewal attempt.

---

## 11. Deletion Deadline

The deletion deadline is calculated from the authoritative subscription expiry timestamp.

Conceptually:

```text
deletion_eligibility_at =
subscription_expired_at + 60 calendar days
```

The server calculates and stores this lifecycle value.

---

## 12. Deletion Eligibility

At the deletion deadline, the Business becomes:

**Permanent Deletion Eligible**

This does not necessarily mean deletion occurs at exactly the same instant.

A deletion job must process the Business according to the deletion lifecycle.

---

## 13. Deletion Eligibility State

The system must distinguish between:

* Expired;
* Read-Only;
* Deletion Eligible;
* Deleting;
* Deleted.

These states must not be collapsed into one generic inactive state.

---

## 14. Pre-Deletion Warnings

The Business receives warnings before permanent deletion.

Warnings may occur at configured thresholds.

For example:

* 30 days remaining;
* 14 days remaining;
* 7 days remaining;
* 3 days remaining;
* 1 day remaining;
* deletion eligible.

The exact notification thresholds remain configurable according to platform policy.

---

## 15. Warning Deduplication

The same lifecycle warning must not be repeatedly created for the same threshold and lifecycle cycle.

Notification deduplication follows:

`docs/02_System_Analysis/21_Notifications_and_Alerts.md`

---

## 16. Warning History

Deletion warnings remain historically traceable.

The system may retain:

* notification UUID;
* Business UUID;
* threshold;
* creation time;
* recipient;
* delivery/state;
* lifecycle state.

---

## 17. Reactivation Before Eligibility

If the Business reactivates before deletion eligibility:

* deletion countdown is cancelled;
* deletion eligibility is removed;
* modifying operations may resume;
* existing data remains;
* existing configuration remains.

No permanent deletion is performed.

---

## 18. Reactivation After Eligibility but Before Deletion

If the Business is already marked `Deletion Eligible` but deletion has not started or completed:

* valid reactivation may cancel deletion;
* the lifecycle state returns to Active;
* pending deletion work must be prevented;
* data remains available.

This transition must be concurrency-safe.

---

## 19. Reactivation During Deletion

If reactivation occurs while a deletion job is executing:

* the system must determine the authoritative lifecycle state atomically;
* deletion must stop where possible;
* remaining deletion work must not continue against an active Business;
* already deleted data may not be recoverable unless backup/recovery policy explicitly supports it.

Therefore, reactivation must normally be blocked once irreversible deletion has passed its defined safety point.

---

## 20. Deletion Safety Point

The deletion process must define an explicit safety boundary.

Before irreversible deletion begins:

* lifecycle state must be revalidated;
* subscription/reactivation state must be checked;
* Business identity must be locked or otherwise protected;
* deletion authorization must be confirmed.

After irreversible deletion begins, reactivation must not falsely report restoration of already deleted data.

---

## 21. Deletion State Machine

The deletion lifecycle is:

```text
Not Eligible
      ↓
Deletion Eligible
      ↓
Deleting
      ↓
Deleted
```

Failure states may be represented operationally without creating a separate Business lifecycle state:

```text
Deleting
   ↓
Retrying
   ↓
Deleting
```

or:

```text
Deleting
   ↓
Failed
   ↓
Retrying
```

---

## 22. Deletion Job

Permanent deletion is performed by a controlled background job.

The job must:

* identify eligible Businesses;
* verify lifecycle state;
* acquire safe execution ownership;
* delete according to dependency order;
* record progress;
* retry failures;
* remain idempotent.

---

## 23. Deletion Job Eligibility Check

Before a deletion job starts, it must verify:

* Business UUID;
* current subscription state;
* deletion eligibility timestamp;
* reactivation state;
* deletion state;
* existing deletion job ownership.

A stale job must not delete a reactivated Business.

---

## 24. Deletion Job Ownership

A Business must not be permanently deleted concurrently by multiple deletion workers.

The system must use a reliable mechanism such as:

* row-level locking;
* job lease;
* unique deletion-job identity;
* equivalent distributed coordination.

---

## 25. Deletion Job Identity

Every deletion execution should have a unique job identity.

The deletion job context should include:

* Job UUID;
* Business UUID;
* start time;
* worker/system identity;
* lifecycle state;
* progress state;
* result;
* failure information.

---

## 26. Deletion Batches

Large Business datasets should be deleted in controlled batches.

The system must avoid one excessively large database transaction when doing so would:

* block normal infrastructure;
* exceed transaction limits;
* consume excessive memory;
* create unnecessary database load.

Batch size may be configurable.

---

## 27. Partial Deletion

Deletion may partially complete before a failure.

The system must track progress sufficiently to determine:

* completed deletion stages;
* remaining stages;
* failed stage;
* retry state.

A failed deletion must not restart blindly from the beginning if that would cause unnecessary work or integrity problems.

---

## 28. Idempotent Deletion

Deletion operations must be idempotent.

If the same deletion step is executed more than once:

* already deleted records are safely ignored;
* the operation does not create corruption;
* the final state remains deterministic.

---

## 29. Deletion Ordering

Deletion must respect data dependencies.

A conceptual order is:

```text
Business-scoped operational records
        ↓
Business-scoped configuration/history
        ↓
Business-scoped supporting records
        ↓
Business-level root data
```

Actual implementation ordering is determined by database dependencies and the final data model.

---

## 30. Tenant Isolation During Deletion

Every deletion query must be explicitly scoped to the target Business.

Deletion must never rely on an unscoped operation such as:

```text
DELETE FROM table
```

without Business-specific safety controls.

---

## 31. Cross-Business Protection

A deletion job for Business A must never delete records belonging to Business B.

Tenant identity must be validated at every relevant deletion stage.

---

## 32. Branch Data

Branch data belongs to the Business lifecycle.

When a Business is permanently deleted, its Branch-scoped data becomes part of the deletion process.

This includes, where applicable:

* Orders;
* Cash Sessions;
* Inventory;
* Employees assigned to Branches;
* reports;
* notifications;
* audit/history.

---

## 33. Global Business Data

Business-level data is deleted together with the Business lifecycle where it is not required to be retained independently.

Examples include:

* menu;
* recipes;
* pricing configuration;
* business settings;
* payroll configuration;
* subscription-related Business configuration.

---

## 34. Historical Orders

Orders are deleted as part of permanent Business deletion.

Until that lifecycle point:

* Orders remain historical;
* Order UUIDs remain stable;
* Order history is not silently rewritten.

---

## 35. Payments and Financial Records

Business operational payment records are deleted only as part of permanent Business deletion.

Before that point:

* original payment history remains;
* corrections remain traceable;
* refunds remain traceable;
* overpayment records remain traceable.

---

## 36. Cash Sessions

Cash Sessions remain historical throughout the retention period.

Permanent deletion removes Business-scoped Cash Session data only when the Business reaches irreversible deletion.

---

## 37. Inventory History

Inventory movements, purchases, adjustments, discrepancies and related history remain available during retention.

Permanent deletion removes Business-scoped inventory history according to deletion policy.

---

## 38. Payroll and Attendance

Payroll and attendance records remain available during retention according to permissions.

They are not deleted merely because the subscription expired.

Permanent deletion removes them as part of Business deletion.

---

## 39. Reports

Report definitions, report versions and report export history remain available during the retention period according to permissions.

Permanent deletion removes Business-scoped reports and associated data.

---

## 40. Audit History

Audit records remain available throughout the retention period.

Deletion of Business data does not permit ordinary users to selectively remove audit records before the lifecycle reaches permanent deletion.

---

## 41. Subscription History

Subscription history remains available during the Business retention period.

It records:

* subscription periods;
* tariff versions;
* entitlement transitions;
* renewal;
* expiry;
* downgrade;
* upgrade;
* reactivation;
* deletion lifecycle.

---

## 42. Notification History

Business-scoped notifications remain available during retention according to access rules.

Deletion removes Business-scoped notification data when the Business is permanently deleted.

---

## 43. Offline Data

Trusted devices may retain locally cached Business data.

After Business expiry:

* offline modifying operations must follow entitlement rules;
* expired authorization cannot bypass deletion lifecycle;
* synchronization must reconcile lifecycle state when connectivity returns.

---

## 44. Device Revocation During Retention

When a Business becomes expired/read-only:

* offline modifying authority must remain bounded;
* device authorization must reflect the current lifecycle;
* revoked devices must not continue modifying Business data.

---

## 45. Offline Data After Deletion

Once permanent deletion is completed, offline devices must not be able to recreate the deleted Business data on the server.

Synchronization must reject events belonging to a deleted Business.

---

## 46. Sync and Deleted Business

If a device reconnects after the Business has been permanently deleted:

* pending events are rejected;
* the deletion state is returned by the server;
* no deleted Business data is recreated;
* the event is recorded according to security/audit policy.

---

## 47. Pending Offline Events

Pending events must not prevent permanent deletion indefinitely.

The deletion lifecycle may reach irreversible deletion even if an offline device still contains unsynchronized events.

Those events become invalid after deletion.

---

## 48. Backup Consideration

Permanent deletion from the primary operational database does not automatically mean that every technical backup copy disappears instantly.

Backup retention must follow a separate infrastructure/data-retention policy.

The system must not falsely report that every physical backup copy has been destroyed merely because the primary Business records were deleted.

---

## 49. Backup Isolation

Backup restoration must not accidentally recreate a deleted Business into the active production system.

Restored data must follow controlled recovery procedures.

---

## 50. Deletion and Recovery

Permanent deletion is considered irreversible from the normal application perspective.

Recovery, if technically possible through infrastructure backups, is an administrative recovery operation and not a normal Business-user feature.

---

## 51. Deletion Confirmation

The system should require appropriate platform-level lifecycle confirmation before irreversible deletion begins.

The confirmation must identify:

* Business;
* deletion reason;
* eligibility;
* scheduled deletion;
* irreversible nature.

---

## 52. Automatic Deletion

Once lifecycle policy allows permanent deletion, the system may execute deletion automatically through background processing.

Automatic deletion must still perform all safety checks.

---

## 53. Manual Deletion

A manual administrative deletion, if supported in the future, must use the same safety model.

It must not bypass:

* Business isolation;
* lifecycle validation;
* audit;
* dependency ordering;
* deletion safety checks.

---

## 54. Deletion Failure

If a deletion operation fails:

* the failure is recorded;
* the deletion remains incomplete;
* the system schedules or permits retry;
* completed deletion stages are preserved;
* the Business must not be reported as fully deleted prematurely.

---

## 55. Retry Policy

Deletion retries should distinguish:

### Temporary failures

Examples:

* database connectivity;
* worker interruption;
* temporary lock;
* infrastructure failure.

These may be retried automatically.

### Permanent/data failures

Examples:

* unexpected schema inconsistency;
* invalid deletion dependency;
* corrupted lifecycle state.

These require investigation or controlled administrative recovery.

---

## 56. Retry Limits

Automatic retries may have a configured limit.

After the retry limit:

* deletion enters a failed operational state;
* the failure is logged;
* responsible platform operators are notified;
* the system must not falsely mark the Business as Deleted.

---

## 57. Partial Retry

If some deletion stages completed successfully:

* completed stages are not unnecessarily repeated;
* remaining stages continue;
* retry uses idempotent operations;
* final deletion is reported only after all required stages succeed.

---

## 58. Deletion Completion

A Business may enter `Deleted` only when:

* all required primary data deletion stages completed;
* lifecycle state was updated successfully;
* deletion job completed;
* final validation succeeded.

---

## 59. Deleted Business State

A deleted Business must no longer be available for normal application login or operational access.

Requests using its Business UUID must fail safely.

---

## 60. Deleted Business API Behavior

API requests referencing a deleted Business must not expose deleted data.

The response should use an appropriate business-safe error such as:

* Business unavailable;
* Business deleted;
* Resource no longer available.

Exact API error codes are defined in API/System implementation documentation.

---

## 61. Deleted Business Authentication

Employee authentication for a deleted Business must not restore access.

Authentication identity may exist in an external identity system, but Business membership/access must no longer authorize operational access to deleted Business data.

---

## 62. Deleted Business Devices

Trusted devices associated with a deleted Business become invalid for that Business.

They must not continue:

* POS operations;
* offline modifications;
* synchronization;
* report access.

---

## 63. Deleted Business Synchronization

Synchronization requests for a deleted Business must be rejected.

The server must not accept old offline events after deletion.

---

## 64. Deletion and Audit

Deletion itself must be auditable at the platform/system level.

The deletion record should identify:

* Business UUID;
* deletion job UUID;
* eligibility time;
* start time;
* completion time;
* result;
* failure/retry information;
* SYSTEM or authorized actor.

---

## 65. Deletion Audit Retention

The fact that a Business was deleted may need to remain in platform-level operational records after Business data deletion.

Such metadata must contain only the minimum necessary information and must follow the platform's retention policy.

---

## 66. Deletion and Tenant Isolation

Deletion must preserve the isolation of all other Businesses.

A deletion failure in Business A must not cause:

* rollback of Business B;
* deletion of Business B;
* entitlement changes to Business B;
* synchronization changes to Business B.

---

## 67. Deletion and Concurrency

The system must safely handle:

* deletion job vs reactivation;
* deletion job vs subscription renewal;
* deletion job vs synchronization;
* deletion job vs report generation;
* deletion job vs export;
* multiple deletion workers;
* repeated deletion requests.

---

## 68. Reactivation vs Renewal

Reactivation may be initiated through subscription renewal.

The operation must atomically update the lifecycle state so that deletion processing cannot incorrectly continue.

---

## 69. Deletion vs Report Generation

If a report generation job is still running when deletion begins:

* the system must prevent inconsistent finalization;
* the report job must detect lifecycle state;
* Business data must not be recreated or retained unintentionally;
* incomplete report generation may be cancelled/failed.

---

## 70. Deletion vs Export

An export running near the deletion boundary must respect lifecycle state.

After permanent deletion begins, new Business data exports must not be authorized.

Existing already-generated export files must follow their own retention/security policy.

---

## 71. Deletion vs Notification

Deletion lifecycle notifications may continue while the Business is eligible or deleting according to policy.

After `Deleted`, normal Business notifications must stop.

---

## 72. Deletion vs Background Jobs

Business-specific background jobs must verify Business lifecycle state.

Jobs that are not required after deletion must be cancelled or fail safely.

Lifecycle cleanup jobs remain SYSTEM-controlled.

---

## 73. Deletion and Subscription State

Subscription expiry starts the retention lifecycle.

Subscription reactivation before irreversible deletion cancels deletion eligibility.

Permanent deletion terminates normal Business operational lifecycle.

---

## 74. Data Retention During Grace Period

The grace period does not start permanent deletion.

The Business remains within the subscription lifecycle and retains its data.

---

## 75. Data Retention During Read-Only Period

Read-only retention preserves Business data for the full configured retention period.

Users must not lose historical access earlier merely because modification is blocked.

---

## 76. Configuration Retention

During read-only retention, the system preserves relevant configuration including:

* menu;
* pricing;
* recipes;
* Sets;
* permissions;
* payroll configuration;
* notification settings;
* Branch configuration.

---

## 77. Historical Configuration

Historical configuration versions remain available according to the applicable history policy.

Permanent deletion removes them only as part of Business deletion.

---

## 78. Deletion and Historical Integrity

Permanent deletion is the lifecycle boundary at which Business history may be removed.

Before that boundary:

* historical data must not be silently destroyed;
* corrections remain traceable;
* reports remain versioned;
* audit history remains intact.

---

## 79. Deletion and Permissions

Normal Business users cannot permanently delete the Business merely through ordinary permissions.

Permanent deletion is a subscription/data-lifecycle operation controlled by the platform lifecycle.

---

## 80. Deletion and Security

Deletion operations require:

* authenticated system worker or authorized platform process;
* validated Business identity;
* validated lifecycle state;
* tenant-scoped operations;
* auditability.

---

## 81. Deletion and Encryption

Encrypted storage does not remove the requirement for logical deletion.

When the Business reaches permanent deletion:

* primary application data must be deleted;
* applicable encryption keys may be destroyed according to infrastructure policy;
* backup retention remains governed separately.

---

## 82. Deletion and Personal/Sensitive Data

Business-scoped employee, customer/debt and payroll data is subject to the same Business lifecycle unless a separate legal retention requirement is defined later.

If future legal requirements require specific retention, those requirements must be represented as an explicit policy rather than silently overriding this lifecycle.

---

## 83. Deletion and Customer Debt

Debt records remain available during the retention period.

Permanent deletion removes Business-scoped:

* Customer records;
* debt balances;
* debt Orders;
* repayment records;
* allocation records.

---

## 84. Deletion and Financial Corrections

Correction history remains preserved during retention.

Permanent deletion removes the Business-scoped correction chain together with the related Business data.

---

## 85. Deletion and Inventory Corrections

Inventory discrepancy and correction history remain preserved during retention.

Permanent deletion removes those records with the Business.

---

## 86. Deletion and Payroll Corrections

Payroll correction chains remain preserved during retention.

Permanent deletion removes Business-scoped payroll history as part of the deletion lifecycle.

---

## 87. Deletion and Report Versions

All Business-scoped report versions remain immutable during retention.

Permanent deletion removes them according to deletion ordering.

---

## 88. Deletion and Audit History

Audit history remains immutable before deletion.

The application must never use deletion as a mechanism for selectively rewriting audit history.

---

## 89. Deletion Progress

The deletion process should expose operational progress to authorized platform operators.

Possible stages include:

```text
Scheduled
Validating
Deleting Operational Data
Deleting Configuration
Deleting History
Deleting Supporting Data
Finalizing
Completed
```

Exact stages may evolve with implementation.

---

## 90. Deletion Monitoring

Platform operations should be able to identify:

* eligible Businesses;
* active deletion jobs;
* failed deletions;
* retry count;
* deletion duration;
* current stage;
* completion state.

Business users should not receive internal worker details.

---

## 91. Deletion Performance

Deletion must be designed so that large Business datasets do not create unnecessary system-wide performance impact.

The deletion system should:

* process batches;
* avoid unnecessary full-table scans;
* use proper tenant-scoped indexes;
* limit concurrent deletion jobs;
* avoid blocking normal unrelated Businesses.

---

## 92. POS Isolation

Business deletion must not degrade POS performance for active Businesses.

Deletion workers must be isolated sufficiently from critical operational workloads.

---

## 93. Deletion and Database Transactions

Small atomic deletion steps may use database transactions.

A full Business deletion does not need to be one enormous transaction if that would create unacceptable infrastructure risk.

Each deletion stage must remain consistent and recoverable.

---

## 94. Deletion and Idempotency

Every deletion stage must be safe to retry.

The system must be able to determine whether a stage:

* has not started;
* is in progress;
* completed;
* failed;
* needs retry.

---

## 95. Deletion and Observability

Deletion processing should generate operational metrics/logs such as:

* eligible count;
* active deletion count;
* successful deletion count;
* failed deletion count;
* retry count;
* processing duration;
* stage failures.

Sensitive Business data must not be unnecessarily written into operational logs.

---

## 96. Error Messages

Deletion failures exposed to Business users should remain simple.

The system should not expose:

* database details;
* internal SQL errors;
* worker internals;
* infrastructure credentials;
* sensitive implementation information.

---

## 97. Data Lifecycle Invariants

The following invariants apply to Data Lifecycle and Deletion:

1. Every Business has a distinct lifecycle state.
2. Subscription expiry does not immediately delete Business data.
3. Retention begins at the authoritative subscription expiry timestamp.
4. The current retention period is 60 calendar days.
5. Deletion eligibility is calculated from server time.
6. Client time cannot determine deletion eligibility.
7. Read-only retention preserves historical data.
8. Read-only does not mean unrestricted access.
9. Read-only remains permission-controlled.
10. Read-only remains Business-isolated.
11. Read-only remains Branch-scoped where applicable.
12. `.xlsx` export may remain available during read-only retention according to permission.
13. Export permission does not grant modification permission.
14. Deletion warnings are generated before permanent deletion.
15. Warning thresholds are configurable according to lifecycle policy.
16. The same warning cycle is deduplicated.
17. Warning history remains traceable.
18. Reactivation before deletion cancels deletion eligibility.
19. Reactivation does not create a new Business.
20. Reactivation preserves existing Business data.
21. Reactivation preserves existing configuration.
22. Reactivation and deletion races are handled atomically.
23. A stale deletion job cannot delete a reactivated Business.
24. Deletion requires a validated lifecycle state.
25. Deletion requires Business identity validation.
26. Deletion is performed by controlled background processing.
27. Multiple deletion workers cannot delete the same Business concurrently.
28. Every deletion execution has a unique job identity.
29. Deletion operations are tenant-scoped.
30. Deletion cannot operate on an unspecified Business scope.
31. Business A deletion cannot affect Business B.
32. Branch data is included in the Business lifecycle.
33. Business-level data is included in the Business lifecycle.
34. Orders remain historical until permanent deletion.
35. Payments remain historical until permanent deletion.
36. Refunds remain historical until permanent deletion.
37. Overpayments remain historical until permanent deletion.
38. Cash Sessions remain historical until permanent deletion.
39. Inventory history remains historical until permanent deletion.
40. Payroll remains historical until permanent deletion.
41. Attendance remains historical until permanent deletion.
42. Reports remain available during retention according to permissions.
43. Report versions remain immutable during retention.
44. Audit history remains available during retention.
45. Subscription history remains available during retention.
46. Notification history remains available during retention.
47. Offline data cannot bypass lifecycle restrictions.
48. Offline authorization cannot extend the retention period.
49. Offline events cannot prevent deletion indefinitely.
50. Deleted Business events cannot recreate the Business.
51. Deleted Business synchronization is rejected.
52. Deleted Business devices lose operational authority.
53. Deleted Business users cannot access operational data.
54. Backup retention is separate from application deletion state.
55. Application deletion must not falsely claim physical backup destruction.
56. Backup restoration must follow controlled recovery procedures.
57. Permanent deletion is irreversible from the normal application perspective.
58. Deletion must be auditable.
59. Deletion progress must be recoverable.
60. Partial deletion must be safely retryable.
61. Deletion stages must be idempotent.
62. Already deleted records must not cause retry failure by themselves.
63. Temporary deletion failures may be retried.
64. Permanent/data failures require controlled handling.
65. Retry limits may be configured.
66. Failed deletion must not be reported as completed.
67. Completed deletion stages must not require unnecessary repetition.
68. `Deleted` is reached only after required deletion stages complete.
69. Deleted Business API access must fail safely.
70. Deleted Business authentication must not restore Business access.
71. Deleted Business devices cannot synchronize successfully.
72. Deletion must not silently recreate data.
73. Business-specific background jobs must respect lifecycle state.
74. Lifecycle-critical cleanup jobs may run with SYSTEM authority.
75. Deletion must not degrade active Business POS unnecessarily.
76. Deletion processing should use controlled batching.
77. Full Business deletion does not need to be one enormous transaction.
78. Individual deletion stages must remain consistent.
79. Deletion operations must be observable.
80. Internal deletion details must not be exposed to ordinary users.
81. Normal Business users cannot trigger permanent deletion through ordinary permissions.
82. Permanent deletion follows platform lifecycle policy.
83. Subscription grace period does not start deletion.
84. Read-only retention preserves data for the full retention period.
85. Downgrade does not trigger Business deletion.
86. Feature disablement does not trigger Business deletion.
87. Existing data is preserved through downgrade.
88. Historical configuration remains preserved through retention.
89. Historical corrections remain preserved through retention.
90. Historical audit records cannot be selectively rewritten before deletion.
91. Deletion of financial data occurs only at the permanent deletion lifecycle.
92. Deletion of payroll data occurs only at the permanent deletion lifecycle.
93. Deletion of customer/debt data occurs only at the permanent deletion lifecycle.
94. Deletion of inventory data occurs only at the permanent deletion lifecycle.
95. Deletion of report versions occurs only at the permanent deletion lifecycle.
96. Deletion of notification data occurs only at the permanent deletion lifecycle.
97. Lifecycle transitions are server-authoritative.
98. Lifecycle transitions are auditable.
99. Lifecycle processing is idempotent.
100. Lifecycle processing is recoverable.
101. Lifecycle processing preserves tenant isolation.
102. Lifecycle processing preserves historical integrity until the permanent deletion boundary.
103. Lifecycle processing must not allow stale client state to override server state.
104. Lifecycle processing must not allow stale offline state to override server state.
105. Deletion eligibility cannot be extended by simply remaining offline.
106. Reactivation before irreversible deletion prevents further deletion.
107. Reactivation after irreversible deletion cannot falsely restore deleted data.
108. Deletion state must remain explainable to authorized platform operators.
109. Deletion failure must remain visible to platform operations.
110. Permanent deletion must not be reported before final validation.
111. Business lifecycle and individual entity archive state remain distinct.
112. Archived entities are not automatically permanently deleted while the Business remains active.
113. Business deletion includes applicable archived entities.
114. Deletion jobs must not use unscoped destructive queries.
115. Deletion must not modify unrelated Business data.
116. Deletion must not create cross-tenant side effects.
117. Deletion must remain compatible with synchronization rules.
118. Deletion must remain compatible with subscription lifecycle rules.
119. Deletion must remain compatible with report lifecycle rules.
120. Deletion must remain compatible with audit and notification lifecycle rules.
121. The system must provide a deterministic final deletion state.
122. The system must provide safe recovery from worker interruption.
123. The system must provide safe recovery from database/infrastructure failure.
124. The system must prevent duplicate deletion completion.
125. The system must prevent false deletion completion.
126. Data lifecycle processing must prioritize data integrity and tenant isolation over convenience.

---

## 98. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
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
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 99. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `26_Data_Lifecycle_and_Deletion.md`

**Next Document:** `27_System_Wide_Consistency_and_Concurrency.md`

