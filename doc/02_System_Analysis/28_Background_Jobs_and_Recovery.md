# Background Jobs and Recovery

**Document ID:** SA-28
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines how asynchronous background jobs are created, scheduled, executed, retried, monitored, recovered, and completed.

FastFood ERP uses background processing for operations that should not block critical user workflows.

Examples include:

* notifications;
* report generation;
* large Excel exports;
* synchronization processing;
* subscription lifecycle processing;
* data deletion;
* retry processing;
* maintenance operations.

Background processing must improve responsiveness without weakening business consistency, authorization, auditability, or tenant isolation.

---

## 2. Scope

This document covers:

* background job architecture;
* job identity;
* queue model;
* job lifecycle;
* scheduling;
* worker execution;
* worker ownership;
* leases;
* retries;
* idempotency;
* duplicate jobs;
* failed jobs;
* dead-letter handling;
* dependency ordering;
* job priority;
* cancellation;
* recovery;
* restart behavior;
* network failures;
* database failures;
* report jobs;
* notification jobs;
* synchronization jobs;
* subscription jobs;
* deletion jobs;
* maintenance jobs;
* observability;
* performance;
* tenant isolation;
* security;
* system invariants.

---

## 3. Background Processing Principle

Background jobs must be used when work does not need to block the user's immediate operational workflow.

The system should prefer:

```text id="7f9p2k"
Fast Core Transaction
        ↓
Durable Job/Event
        ↓
Background Processing
```

instead of:

```text id="z1t4qv"
User Request
        ↓
Long Background Operation
        ↓
Delayed POS Response
```

---

## 4. POS Priority

POS operations have high priority.

Background processing must not unnecessarily block:

* Order creation;
* Order acceptance;
* Payment;
* Cash Session operations;
* inventory-critical operations.

Heavy jobs should run independently from POS-critical transactions.

---

## 5. Job Identity

Every background job has a stable Job UUID.

The Job UUID is used for:

* tracking;
* idempotency;
* retry;
* logging;
* audit;
* recovery;
* worker ownership.

---

## 6. Job Types

The system may support different job types.

Examples:

```text id="c4a1jm"
Notification Delivery
Report Generation
Excel Export
Synchronization
Subscription Lifecycle
Deletion
Maintenance
Retry Processing
```

Each job type has its own processing rules.

---

## 7. Job Context

A job should contain sufficient context to execute safely.

Depending on the job type this may include:

* Job UUID;
* Business UUID;
* Branch UUID;
* Actor/initiator UUID where applicable;
* Entity UUID;
* Transaction UUID;
* Event UUID;
* Job type;
* creation time;
* scheduled time;
* attempt count;
* priority;
* state.

---

## 8. Tenant Context

Business-specific jobs must always carry or derive valid Business context.

A worker must never execute a Business-specific operation without establishing its tenant context.

---

## 9. Branch Context

If a job is Branch-specific, the Branch UUID must be included and validated.

If the job is Business-wide, it must not accidentally be restricted to an unrelated Branch.

---

## 10. Job Lifecycle

A standard lifecycle is:

```text id="9t3q8x"
Pending
  ↓
Running
  ↓
Completed
```

Failure may produce:

```text id="e1c5rw"
Running
  ↓
Retrying
  ↓
Running
```

or:

```text id="q4h2vb"
Running
  ↓
Failed
```

A job may also be:

```text id="0k7mfa"
Cancelled
```

where cancellation is supported.

---

## 11. Pending State

A Pending job has been created but has not started execution.

Pending jobs must survive:

* application restart;
* worker restart;
* temporary infrastructure failure.

---

## 12. Running State

A Running job is currently owned by a worker.

The worker must maintain sufficient ownership information to allow recovery if it fails.

---

## 13. Completed State

A Completed job has successfully performed its required work.

Completed jobs must not be executed again as a new logical operation unless explicitly scheduled as a new job.

---

## 14. Failed State

A Failed job could not complete successfully after the applicable retry policy.

The failure must contain enough information for investigation.

---

## 15. Retrying State

A Retrying job is waiting for another execution attempt.

Retry scheduling should use controlled delay rather than immediate infinite retry.

---

## 16. Cancelled State

A job may be cancelled when cancellation is supported and safe.

Cancellation must not falsely imply that a partially committed core transaction was rolled back.

---

## 17. Job Creation

A job should be created only after the system knows that the background operation is required.

For core-triggered jobs, job creation should be reliably associated with the successful core transaction.

---

## 18. Transactional Job Creation

When a successful core transaction requires a background operation, the system should use a reliable transaction-to-job mechanism.

Conceptually:

```text id="1xj4ab"
Core Transaction
      +
Durable Job/Event
```

Both must be reliable enough that a committed core event does not silently lose its required background work.

---

## 19. Outbox-Style Processing

An outbox-style mechanism may be used for operations such as:

* notifications;
* audit events;
* synchronization;
* report triggers;
* secondary processing.

The exact implementation remains an architectural decision.

---

## 20. Job Idempotency

Every retry-sensitive job must be idempotent.

If the same job executes more than once:

* duplicate core effects must not occur;
* already completed work must be recognized;
* final state must remain deterministic.

---

## 21. Duplicate Job Prevention

The system should prevent duplicate logical jobs using an appropriate uniqueness/idempotency key.

Examples:

```text id="e2c7lp"
Report Definition + Period + Scope
```

or:

```text id="k6n0sz"
Notification Condition + Business + Lifecycle Cycle
```

or:

```text id="u3r8dm"
Synchronization Event UUID
```

---

## 22. Worker Ownership

A Running job belongs to a worker through a lease or equivalent ownership mechanism.

The ownership context may include:

* worker ID;
* lease expiration;
* started time;
* attempt number.

---

## 23. Worker Lease

A worker lease prevents multiple workers from processing the same mutually exclusive job simultaneously.

If a worker crashes and the lease expires:

* another worker may safely recover the job;
* idempotency must still protect against duplicate effects.

---

## 24. Worker Heartbeat

Long-running jobs may maintain a heartbeat or lease renewal.

If the heartbeat stops:

* the job becomes recoverable after the defined timeout;
* the system must not wait indefinitely.

---

## 25. Worker Crash

If a worker crashes while processing a job:

* the job remains recoverable;
* the job must not be permanently lost;
* another worker may retry after ownership expires.

---

## 26. Application Restart

Application/server restart must not delete Pending jobs.

After restart:

* Pending jobs remain available;
* recoverable Running jobs may return to retry state;
* completed jobs remain Completed.

---

## 27. Worker Restart

Worker restart must not cause:

* duplicate report versions;
* duplicate notifications;
* duplicate deletion;
* duplicate synchronization;
* duplicate financial effects.

Idempotency and durable state protect against these cases.

---

## 28. Database Failure

If a job cannot persist its progress because of database failure:

* the job must not be marked Completed;
* retry may occur;
* uncertain state must be resolved using persisted job identity.

---

## 29. Network Failure

Network failure during a job does not automatically mean that the operation failed.

If the remote/core operation may already have succeeded:

* retry uses the same identity;
* duplicate effect is prevented;
* final state is reconciled.

---

## 30. Retry Policy

Retry policy depends on error type.

### Temporary errors

Examples:

* network unavailable;
* database temporarily unavailable;
* worker interruption;
* temporary lock;
* service timeout.

These may be retried automatically.

### Permanent errors

Examples:

* invalid job data;
* deleted Business;
* invalid entity;
* unsupported operation.

These should normally fail without unlimited retries.

---

## 31. Retry Backoff

Automatic retries should use controlled backoff.

Possible strategy:

```text id="8t0xwd"
Attempt 1
   ↓
Short Delay
   ↓
Attempt 2
   ↓
Longer Delay
   ↓
Attempt 3
   ↓
...
```

Exact timing is configurable.

---

## 32. Retry Limit

Each retryable job type should have a maximum retry policy.

After the limit:

* job becomes Failed;
* failure is recorded;
* responsible system operators may be notified;
* manual recovery may be required.

---

## 33. Dead-Letter Handling

Jobs that cannot complete after retries may be moved to a dead-letter or equivalent failure state.

Dead-letter processing must preserve:

* Job UUID;
* Business;
* job type;
* attempts;
* errors;
* timestamps;
* last known state.

---

## 34. Manual Retry

Authorized platform operators may retry a failed job where supported.

Manual retry must:

* preserve original Job UUID where appropriate;
* record retry action;
* avoid duplicate successful effects.

---

## 35. Job Dependencies

Some jobs depend on previous jobs/events.

Example:

```text id="x8v4ca"
Order Sync
    ↓
Configuration Reconciliation
```

or:

```text id="f7j3qs"
Report Snapshot
    ↓
Excel Export
```

Dependent jobs must not execute against unavailable prerequisite state.

---

## 36. Dependency Failure

If a prerequisite job fails:

* dependent job waits, retries, or fails according to policy;
* dependent work must not assume missing prerequisite state succeeded.

---

## 37. Job Priority

Jobs may have priority levels.

POS-supporting background work should have appropriate priority over non-critical maintenance.

Example conceptual levels:

```text
Critical
High
Normal
Low
Maintenance
```

Exact priority configuration remains adjustable.

---

## 38. Fairness

High-priority jobs must not permanently starve lower-priority jobs.

The scheduler should provide reasonable fairness while preserving operational priorities.

---

## 39. Queue Isolation

Different job classes may use separate queues.

For example:

```text id="q1t9wa"
POS-related Secondary Work
Reports
Notifications
Synchronization
Deletion
Maintenance
```

This prevents heavy jobs from blocking unrelated operational processing.

---

## 40. Report Generation Jobs

Heavy reports should run in the background.

The job should contain:

* Report UUID;
* Report Definition;
* period;
* scope;
* snapshot context;
* creator/source;
* export requirements where applicable.

---

## 41. Report Generation Idempotency

Duplicate requests for the same logical report must not create uncontrolled duplicate report versions.

Logical identity:

```text id="m3r6ka"
Report Definition
+
Period
+
Scope
```

Version creation occurs only when the report lifecycle requires it.

---

## 42. Excel Export Jobs

Large `.xlsx` exports may run in the background.

The export job must reference an exact report snapshot/version where applicable.

The exported file must not silently change because source data changed after the snapshot.

---

## 43. Export Failure

If an Excel export fails:

* the report version remains unchanged;
* export job enters retry/failure handling;
* the user is notified when appropriate.

---

## 44. Notification Jobs

Notification delivery may run asynchronously.

The notification record should be created reliably after the relevant condition/core event is committed.

---

## 45. Notification Retry

Notification delivery may be retried after temporary failure.

Retry must not create duplicate logical notifications for the same condition cycle.

---

## 46. Notification Failure

Notification failure must never roll back the underlying business transaction.

Example:

```text id="q6b2nv"
Order Accepted
+
Notification Failed
```

The Order remains Accepted.

---

## 47. Synchronization Jobs

Synchronization processing may run in the background after connectivity is restored.

The synchronization job must preserve:

* Event UUID;
* Transaction UUID;
* Business;
* Branch;
* Device;
* dependency order.

---

## 48. Synchronization Retry

A failed synchronization event may be retried.

The same Event UUID must be reused.

A retry must not create a new logical transaction.

---

## 49. Synchronization Conflict

If synchronization results in a conflict:

* the event becomes Conflict;
* it is not endlessly retried;
* authorized resolution is required where applicable;
* resolution is audited.

---

## 50. Subscription Lifecycle Jobs

Background jobs may process:

* expiry;
* grace period;
* deletion eligibility;
* lifecycle notifications;
* entitlement transitions.

These jobs must use server time.

---

## 51. Subscription Job Idempotency

Running the same lifecycle job multiple times must not:

* extend subscription twice;
* expire a Business multiple times;
* create duplicate warnings;
* mark deletion multiple times.

---

## 52. Subscription Race Handling

Subscription jobs must safely handle:

* renewal;
* expiry;
* reactivation;
* deletion eligibility.

The authoritative state is determined through transactional concurrency control.

---

## 53. Data Deletion Jobs

Permanent Business deletion runs through background processing.

Deletion jobs must:

* verify eligibility;
* validate Business state;
* prevent concurrent deletion;
* process data safely;
* track progress;
* retry failures;
* remain idempotent.

---

## 54. Deletion Job Safety

A deletion worker must revalidate lifecycle state immediately before destructive work.

A stale worker must not delete a Business that has been reactivated.

---

## 55. Partial Deletion Recovery

If deletion stops after several stages:

* completed stages remain completed;
* remaining stages are identified;
* retry continues from the appropriate state;
* deletion is not falsely marked complete.

---

## 56. Maintenance Jobs

Maintenance jobs may perform tasks such as:

* cleanup of expired technical records;
* rebuilding derived data;
* consistency checks;
* stale job recovery.

Maintenance jobs must not alter historical Business records without explicit authority.

---

## 57. Derived Data Rebuild

If derived/cache data is rebuilt:

* source data remains authoritative;
* rebuild must not alter source history;
* partial rebuild must be recoverable;
* repeated rebuild must be safe.

---

## 58. Job Cancellation

Cancellation may be supported for jobs that are safely cancellable.

A job must not be cancelled in a way that leaves core data half-applied.

For irreversible deletion, cancellation must respect the deletion safety boundary.

---

## 59. Job Timeout

Long-running jobs should have execution timeout policies.

If a job exceeds its timeout:

* worker ownership may expire;
* job becomes recoverable;
* duplicate effects remain prevented by idempotency.

---

## 60. Job Progress

Long-running jobs should expose progress where meaningful.

Possible states:

```text id="x2m7qb"
0%
25%
50%
75%
100%
```

Progress must not be reported as complete before the operation is actually complete.

---

## 61. Job Result

A completed job should record an appropriate result.

Depending on type:

* success;
* generated resource;
* affected record count;
* synchronization result;
* deletion result;
* notification result.

Sensitive data should not be unnecessarily stored in job metadata.

---

## 62. Job Error Information

Errors should include enough information for diagnosis without exposing secrets.

Appropriate information may include:

* error class;
* error code;
* retryability;
* attempt;
* timestamp;
* affected Job UUID.

Internal stack traces should remain restricted to operational logs.

---

## 63. Job Security

Workers are trusted system components.

However, they must still validate:

* Business context;
* Branch context;
* lifecycle;
* entitlement;
* entity state.

A background worker must not bypass business rules merely because it runs internally.

---

## 64. Job Authorization

System jobs may act as `SYSTEM` where explicitly defined.

A SYSTEM actor must still have a clearly defined allowed operation scope.

Employee permissions must not be silently reused as SYSTEM authorization.

---

## 65. Audit of Background Jobs

Important background operations should be auditable.

Examples:

* subscription transition;
* deletion;
* report finalization;
* large export;
* configuration reconciliation;
* conflict resolution.

Routine technical retries do not necessarily require individual business audit events if operational logs already capture them.

---

## 66. Job and Audit Correlation

Background operations should be correlated using:

* Job UUID;
* Transaction UUID;
* Entity UUID;
* Business UUID;
* Branch UUID where applicable.

This allows historical reconstruction.

---

## 67. Job and Notification Correlation

Notification jobs should retain the source event/condition identity.

This prevents duplicate notification cycles.

---

## 68. Job and Report Correlation

Report jobs should retain:

* Report Definition;
* Report Version where applicable;
* snapshot identity;
* Job UUID.

This allows the system to explain how the report was generated.

---

## 69. Job and Deletion Correlation

Deletion jobs must preserve:

* Business UUID;
* deletion Job UUID;
* lifecycle state;
* stage;
* retry count;
* completion result.

---

## 70. Job and Synchronization Correlation

Synchronization jobs should retain:

* Device UUID;
* Event UUID;
* Transaction UUID;
* Business UUID;
* Branch UUID.

---

## 71. Job Queue Durability

Critical background work must not exist only in process memory.

If the application or worker restarts:

* durable jobs remain available;
* uncommitted in-memory work is recoverable through persisted state.

---

## 72. Queue Ordering

Where event dependencies exist, queue processing must respect required ordering.

Independent jobs may run concurrently.

---

## 73. Parallel Processing

Parallel processing is allowed when operations are independent.

Example:

```text id="v3s1xm"
Business A Report
+
Business B Report
```

may run concurrently.

But two workers must not concurrently perform conflicting operations on the same protected resource without appropriate concurrency control.

---

## 74. Business Isolation

A heavy background workload from one Business must not unnecessarily block unrelated Businesses.

Queue and database operations should preserve tenant isolation.

---

## 75. Branch Isolation

Branch-specific jobs must remain scoped to the correct Branch.

One Branch's failure must not corrupt another Branch's state.

---

## 76. Job Rate Limiting

High-volume jobs may require rate limits.

Examples:

* large exports;
* notification bursts;
* synchronization;
* deletion.

Rate limiting protects system stability.

---

## 77. Backpressure

When queue load becomes high:

* new work may remain Pending;
* non-critical jobs may be delayed;
* POS-critical operations should remain protected;
* the system must expose operational pressure metrics.

---

## 78. Queue Recovery

After queue infrastructure failure:

* persisted jobs must be recoverable;
* duplicate execution must be prevented;
* job ownership must be re-established;
* failed jobs must follow retry rules.

---

## 79. Job State Recovery

A job stuck in Running state must not remain permanently blocked because a worker crashed.

The system should detect stale leases/heartbeats and recover the job.

---

## 80. Scheduled Jobs

Scheduled jobs must use server-authoritative time.

Examples:

* monthly report generation;
* subscription lifecycle checks;
* deletion eligibility checks;
* cleanup tasks.

Client time must not control scheduled lifecycle execution.

---

## 81. Monthly Report Scheduling

Monthly reports are generated according to the defined monthly lifecycle.

The system waits for required Cash Session closure before final generation.

If generation fails:

* report state becomes Failed;
* retry policy applies;
* successful retry preserves report identity/version rules.

---

## 82. Deletion Scheduling

Deletion eligibility is determined from:

`subscription_expired_at + 60 calendar days`

The scheduler must not extend or shorten this period because of:

* client clock;
* login;
* offline state;
* stale worker execution.

---

## 83. Subscription Warning Scheduling

Warning jobs should use lifecycle thresholds.

The same threshold should not generate repeated notifications for the same lifecycle cycle.

---

## 84. Recovery After Scheduler Failure

If the scheduler is unavailable during a scheduled event:

* lifecycle processing resumes when the scheduler returns;
* missed jobs are detected;
* execution uses current server state;
* duplicate transitions are prevented.

---

## 85. Catch-Up Processing

Scheduled lifecycle jobs may perform catch-up processing.

Example:

If a worker was offline when a deletion eligibility deadline passed, it may detect the now-eligible Business and process it.

It must still revalidate the current lifecycle state before destructive work.

---

## 86. Job Monitoring

Operations should be able to monitor:

* queue depth;
* Pending jobs;
* Running jobs;
* Failed jobs;
* Retrying jobs;
* stale jobs;
* retry count;
* execution duration.

---

## 87. Alerts

Operational alerts may be generated for:

* repeated job failures;
* queue backlog;
* stuck workers;
* excessive retry rates;
* deletion failures;
* synchronization failures;
* report failures.

---

## 88. Job Metrics

Useful metrics include:

* jobs created;
* jobs completed;
* jobs failed;
* jobs retried;
* average execution time;
* queue wait time;
* worker utilization;
* stale job count;
* dead-letter count.

---

## 89. Performance Isolation

Background processing must be isolated from POS-critical database resources where practical.

Heavy work should use:

* controlled concurrency;
* efficient queries;
* batching;
* pagination;
* appropriate indexes.

---

## 90. Memory Safety

Large jobs must not load entire datasets into memory unnecessarily.

Examples:

* large Excel exports;
* report generation;
* deletion;
* synchronization batches.

Streaming/chunking/batching should be used where appropriate.

---

## 91. Job Batch Size

Batch sizes should be configurable.

The correct size depends on:

* database capacity;
* network;
* dataset size;
* worker resources.

The system must avoid assumptions that require powerful hardware.

---

## 92. Job Retry and Business State

A retry must always re-check current Business state when the state may have changed.

Examples:

* subscription expired;
* employee deactivated;
* Branch disabled;
* Business deleted;
* configuration changed.

---

## 93. Retry and Historical Integrity

Retry must never silently rewrite historical records.

If a job processes a correction/report/configuration change:

* original state remains preserved;
* new state is represented separately where required.

---

## 94. Retry and Idempotent Side Effects

Secondary side effects should use idempotent identities.

Examples:

* Notification UUID;
* Export UUID;
* Report Job UUID;
* Synchronization Event UUID.

---

## 95. Recovery After Partial Core Processing

If a job performs multiple core steps, each step must have a defined transaction boundary.

The system must not rely on worker process continuity to guarantee atomicity.

---

## 96. Recovery After Partial Secondary Processing

If a secondary step fails:

* core transaction remains valid;
* secondary state is retryable;
* duplicate side effects are prevented.

---

## 97. Background Jobs and Offline

Background synchronization may process offline events without blocking local POS operations.

Offline event queues remain durable locally until server acknowledgement or terminal conflict/failure.

---

## 98. Background Jobs and Subscription

Subscription jobs must remain active even when the Business itself is read-only.

Lifecycle processing is a platform responsibility and must not depend on Business modification access.

---

## 99. Background Jobs and Deletion

Deletion processing has priority over ordinary Business-specific background work once the Business enters irreversible deletion.

Non-essential jobs should stop or fail safely.

---

## 100. Background Jobs and Security

A worker must not use stale authorization state.

Before sensitive work, it must verify relevant current lifecycle/security state.

---

## 101. Background Jobs and Tenant Isolation

Every Business-specific job must carry tenant context through:

* queue;
* worker;
* database;
* logs;
* result;
* audit.

Tenant context must not be inferred from unrelated mutable state.

---

## 102. Background Jobs and Branch Isolation

Branch-scoped jobs must retain Branch identity throughout processing.

Changing Branch context during execution must not redirect the job.

---

## 103. Background Jobs and Device Context

If a job originates from an offline device or POS operation, the job should retain the originating Device UUID where relevant.

---

## 104. Background Jobs and Employee Context

Where a job represents an employee-triggered operation, the original actor remains historically attributable.

SYSTEM execution of the later background step does not replace the original actor.

---

## 105. Background Jobs and Cash Session

If a job originates from a Cash Session operation, the Cash Session UUID should be preserved where applicable.

---

## 106. Background Jobs and Order

If a job originates from an Order:

* Order UUID remains stable;
* job retries do not create a new Order;
* historical actor/session/device context remains available.

---

## 107. Background Jobs and Payment

Background processing must not silently modify payment state unless the operation is explicitly designed for it.

Financial corrections remain controlled financial operations.

---

## 108. Background Jobs and Inventory

Background jobs must not bypass inventory atomicity.

Any inventory modification must use the same consistency rules as synchronous operations.

---

## 109. Background Jobs and Reports

Report jobs operate on defined snapshots/versions.

They must not silently change a finalized report because a worker retried later.

---

## 110. Background Jobs and Notifications

Notification processing remains secondary.

Notification failure must never invalidate the source business transaction.

---

## 111. Background Jobs and Audit

Background processing must preserve enough correlation information for historical reconstruction.

---

## 112. System Invariants

The following invariants apply to Background Jobs and Recovery:

1. Every background job has a stable Job UUID.
2. Critical background jobs are durable.
3. Pending jobs survive application restart.
4. Recoverable Running jobs survive worker failure.
5. Completed jobs are not unintentionally re-executed.
6. Failed jobs remain distinguishable from completed jobs.
7. Retryable jobs use controlled retry policy.
8. Retryable jobs use bounded retry counts where applicable.
9. Permanent failures do not retry forever.
10. Duplicate logical jobs are prevented where required.
11. Job processing is idempotent.
12. Retry does not create duplicate core effects.
13. Worker ownership is concurrency-safe.
14. Worker lease expiration allows recovery.
15. Worker crash does not permanently lose a durable job.
16. Worker restart does not create duplicate core effects.
17. Network timeout does not automatically imply failed business operation.
18. Database failure does not result in false Completed state.
19. Job state is persisted.
20. Business-specific jobs always have valid Business context.
21. Branch-specific jobs always have valid Branch context.
22. Tenant context is never inferred from unrelated mutable state.
23. Background workers cannot bypass Business isolation.
24. Background workers cannot bypass Branch isolation.
25. Background workers cannot bypass subscription lifecycle.
26. Background workers cannot bypass entitlement.
27. Background workers cannot bypass critical authorization rules.
28. SYSTEM authority is explicit.
29. SYSTEM authority does not automatically inherit employee permissions.
30. POS-critical operations are not unnecessarily blocked by background jobs.
31. Heavy jobs are isolated from POS-critical workloads.
32. Report generation may run asynchronously.
33. Large Excel exports may run asynchronously.
34. Notification delivery may run asynchronously.
35. Synchronization may run asynchronously.
36. Subscription lifecycle processing may run asynchronously.
37. Business deletion may run asynchronously.
38. Deletion jobs verify lifecycle state before destructive work.
39. Stale deletion workers cannot delete reactivated Businesses.
40. Partial deletion is recoverable.
41. Deletion stages are idempotent.
42. Deletion completion is not reported prematurely.
43. Monthly report scheduling uses server time.
44. Subscription scheduling uses server time.
45. Deletion scheduling uses server time.
46. Scheduler failure does not permanently lose lifecycle work.
47. Missed scheduled jobs may be safely caught up.
48. Catch-up processing revalidates current state.
49. Notification retries do not create duplicate logical notification cycles.
50. Report retries do not create uncontrolled duplicate report versions.
51. Synchronization retries reuse Event UUID.
52. Export retries preserve export identity.
53. Job dependencies are respected.
54. Dependent jobs do not assume failed prerequisites succeeded.
55. Independent jobs may run concurrently.
56. Concurrent jobs must not corrupt shared state.
57. Job queues may be isolated by workload class.
58. High-priority jobs must not permanently starve lower-priority jobs.
59. Queue overload must not unnecessarily block POS.
60. Backpressure is supported for heavy workloads.
61. Job execution can be monitored.
62. Job failures can be diagnosed.
63. Job retries are observable.
64. Stale jobs are detectable.
65. Worker failures are recoverable.
66. Queue infrastructure failures are recoverable.
67. Job errors do not expose sensitive internal information to ordinary users.
68. Operational logs may contain technical details under controlled access.
69. Important background operations are auditable.
70. Job correlation preserves Business UUID.
71. Job correlation preserves Branch UUID where applicable.
72. Job correlation preserves Entity UUID where applicable.
73. Job correlation preserves Transaction UUID where applicable.
74. Job correlation preserves Event UUID where applicable.
75. Original employee identity is not replaced by SYSTEM merely because processing became asynchronous.
76. Original device identity remains traceable where relevant.
77. Original Cash Session remains traceable where relevant.
78. Original Order identity remains stable.
79. Financial background operations cannot bypass financial controls.
80. Inventory background operations cannot bypass inventory controls.
81. Background operations cannot create negative inventory.
82. Background operations cannot create duplicate payments.
83. Background operations cannot create duplicate refunds.
84. Background operations cannot create duplicate debt allocations.
85. Background processing does not rewrite historical financial records.
86. Background processing does not rewrite historical inventory records.
87. Background processing does not rewrite finalized report versions.
88. Background processing does not silently rewrite configuration history.
89. Background processing preserves auditability.
90. Background processing preserves historical integrity.
91. Background processing preserves tenant isolation.
92. Background processing preserves Branch isolation.
93. Background processing preserves Business lifecycle state.
94. Background processing respects employee deactivation where applicable.
95. Background processing respects device revocation where applicable.
96. Background processing respects subscription expiry where applicable.
97. Background processing respects deletion lifecycle.
98. Background processing must not recreate deleted Business data.
99. Background processing must remain recoverable after restart.
100. Background processing must remain recoverable after network failure.
101. Background processing must remain recoverable after database failure.
102. Background processing must remain recoverable after worker failure.
103. Retry logic must preserve original operation identity.
104. Retry logic must be deterministic.
105. Retry logic must not create duplicate logical effects.
106. Long-running jobs should report meaningful progress where practical.
107. Large datasets should be processed using batching/chunking where appropriate.
108. Background work must not require unnecessarily powerful hardware.
109. Job concurrency must be configurable.
110. Job priority must be configurable.
111. Retry policy must be configurable by job type.
112. Worker recovery must be automatic where safe.
113. Manual recovery must be available for appropriate failures.
114. Dead-letter/failure states must remain inspectable.
115. Job lifecycle must be auditable where business impact exists.
116. Job execution must remain observable.
117. Background processing must not silently bypass core transaction boundaries.
118. Background processing must use the same core consistency rules as synchronous operations.
119. Secondary failures must not normally roll back committed core transactions.
120. Background job architecture must preserve system-wide consistency.

---

## 113. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/21_Notifications_and_Alerts.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 114. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `28_Background_Jobs_and_Recovery.md`

**Next Document:** `29_Error_Handling_and_Failure_Recovery.md`

