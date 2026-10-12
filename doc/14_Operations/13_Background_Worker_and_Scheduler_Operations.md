# Background Worker and Scheduler Operations

**Document ID:** OPS-13
**File:** `13_Background_Worker_and_Scheduler_Operations.md`
**Status:** Accepted
**Version:** 1.0
**Parent:** `doc/14_Operations/README.md`
**Scope:** Background worker runtime operations, scheduled jobs, queue management, retries, failed-job recovery, and operational safeguards.

---

## 1. Purpose

This document defines operational procedures for background workers, scheduled tasks, and asynchronous job queues in the FastFood ERP platform.

Background processing supports work that should not unnecessarily delay interactive requests, including:

* Notifications and delivery retries.
* Report generation and exports.
* Inventory-related calculations and derived data updates.
* Offline synchronization processing.
* Subscription lifecycle processing.
* Data retention and deletion workflows.
* Scheduled reconciliation and consistency checks.
* AI-related asynchronous tasks, where applicable.
* Operational maintenance and cleanup jobs.

The actual task list depends on the implemented application architecture. No specific worker framework, queue technology, scheduler, or message broker is assumed.

The primary objectives are reliable processing, controlled resource consumption, safe recovery, traceability, and preservation of business data integrity.

## 2. Scope and Boundaries

This document covers:

1. Worker and scheduler inventory.
2. Job lifecycle and execution states.
3. Queue health and backlog management.
4. Worker capacity and concurrency.
5. Retry, timeout, and dead-letter handling.
6. Scheduled job execution and missed schedules.
7. Duplicate execution and idempotency.
8. Graceful shutdown and deployment compatibility.
9. Recovery and reconciliation.
10. Monitoring, incident response, and audit evidence.

Related responsibilities:

* Backend API runtime: `11_Backend_API_Operations.md`.
* Redis, queue, and cache infrastructure: `10_Redis_Queue_and_Cache_Operations.md`.
* Incident response: `05_Incident_Management.md`.
* Release coordination: `18_Release_and_Change_Operations.md`.
* Security operations: `17_Security_Operations.md`.

This document describes application-level operations. Queue infrastructure administration remains subject to the applicable infrastructure runbooks.

## 3. Core Operational Principles

### 3.1 Durable business state

A queue message is not automatically the authoritative business record.

For important operations, the system must preserve enough durable information to determine whether the business operation is pending, completed, failed, or awaiting reconciliation.

Deleting a queue message must not erase the only record of a business operation.

### 3.2 At-least-once execution awareness

Unless the actual queue technology and processing design explicitly guarantee stronger semantics, assume that a job may execute more than once.

Workers must be designed so that repeated execution does not create duplicate orders, inventory deductions, payments, refunds, notifications, or other unintended effects.

### 3.3 Separate delivery from completion

A message being published, retrieved, acknowledged, or removed from a queue does not necessarily mean its business operation completed successfully.

The system must distinguish transport-level progress from business-level completion.

### 3.4 Bounded resource consumption

Workers must have explicit limits for concurrency, execution time, memory, retries, and resource-intensive operations.

Background processing must not starve interactive POS requests or overload PostgreSQL and other shared dependencies.

### 3.5 Safe recovery

When the outcome of a job is uncertain, operators must reconcile its effects before manually retrying, replaying, or creating a replacement job.

## 4. Worker and Scheduler Inventory

Maintain an operational inventory for every production worker group and scheduled task.

Each entry should define:

* Unique task or worker-group name.
* Purpose and business impact.
* Trigger type: event-driven, queue-driven, periodic, or manually initiated.
* Queue or scheduling mechanism.
* Owning service and responsible team.
* Required dependencies.
* Expected execution duration.
* Timeout and retry policy.
* Idempotency strategy.
* Concurrency and resource limits.
* Failure handling and escalation path.
* Monitoring signals.
* Data classification and access requirements.
* Recovery or reconciliation procedure.
* Compatibility requirements during deployments.

The inventory must identify high-impact tasks explicitly, including:

* Order-related asynchronous processing.
* Inventory calculations and reconciliation.
* Offline synchronization.
* Financial or cashier-related background processing, if implemented.
* Subscription expiry and entitlement changes.
* Deletion-eligibility evaluation and approved deletion jobs.
* Notifications associated with security, financial, or operational events.

A task must not be considered production-ready if its owner, failure behavior, and recovery procedure are unknown.

## 5. Job Lifecycle and State Model

Use a documented job lifecycle appropriate to the implemented queue system.

A logical lifecycle may include:

1. **Created** — a request for work has been recorded.
2. **Queued** — the job is waiting for processing.
3. **Running** — a worker has claimed the job.
4. **Succeeded** — processing completed and its required effects were verified.
5. **Retry pending** — a retry is scheduled after a recoverable failure.
6. **Failed** — processing cannot continue automatically.
7. **Dead-lettered** — the job has been isolated for investigation under the configured policy.
8. **Cancelled** — the job was cancelled through an authorized procedure.
9. **Reconciliation required** — the outcome or business effect is uncertain.

These are logical states, not a requirement to implement every state as a separate database or queue field.

### 5.1 State transition requirements

* State transitions must be consistent with the actual processing result.
* A worker must not mark a job successful before required business effects are committed.
* Failed jobs must retain enough diagnostic context for investigation.
* A job whose outcome is uncertain must not be treated as safely retryable without reconciliation.
* Manual state changes must be authorized and auditable.
* Cancellation must not silently reverse already committed business effects.

Where the queue technology cannot represent all logical states, use an appropriate durable job record or operational tracking mechanism.

## 6. Queue Management

### 6.1 Queue inventory

For every queue, document:

* Queue name and purpose.
* Producers and consumers.
* Priority or ordering requirements.
* Expected arrival rate.
* Normal backlog range.
* Maximum tolerated queue age.
* Processing capacity.
* Retry and failure policy.
* Retention behavior.
* Criticality and alert thresholds.
* Recovery procedure.

Queue names and ownership must be consistent across application configuration, dashboards, and runbooks.

### 6.2 Queue health signals

Monitor:

* Number of queued jobs.
* Oldest waiting job age.
* Job arrival rate.
* Job completion rate.
* Failure rate.
* Retry rate.
* Dead-letter count.
* Active and idle workers.
* Average and high-percentile execution duration.
* Queue wait time.
* Dependency latency and errors.
* Queue storage and memory pressure where applicable.

Backlog size alone is insufficient. A small queue containing one time-critical job may require immediate attention, while a larger queue of low-priority reports may be acceptable.

### 6.3 Backlog assessment

When a backlog grows:

1. Identify the affected queue and job types.
2. Compare incoming and completion rates.
3. Check whether workers are running and making progress.
4. Inspect recent deployment or configuration changes.
5. Check PostgreSQL, Redis, network, and other dependencies.
6. Look for repeated failures or excessive retries.
7. Assess the business impact of delayed processing.
8. Apply a controlled mitigation.
9. Verify that backlog age and completion rate improve.

Do not increase concurrency automatically without understanding the bottleneck.

### 6.4 Queue isolation

Where practical, separate workloads with different latency, priority, resource, or failure characteristics.

Examples include:

* Time-sensitive operational notifications.
* Report generation and exports.
* Resource-intensive AI tasks.
* Periodic cleanup.
* Subscription lifecycle tasks.

Queue isolation should reduce interference between workloads. It must not introduce inconsistent business ordering or duplicate processing.

## 7. Worker Capacity and Concurrency

### 7.1 Capacity controls

Define appropriate limits for:

* Number of worker processes.
* Concurrent jobs per worker.
* Maximum execution time.
* Memory consumption.
* Database connections.
* External service requests.
* Per-tenant resource consumption where needed.
* Expensive report and AI operations.

Limits must be based on measured workload, dependency capacity, and available hardware.

### 7.2 Protect interactive operations

Background workers share infrastructure with user-facing services.

Operational controls should prevent background tasks from overwhelming:

* PostgreSQL connection capacity.
* CPU and memory.
* Disk I/O.
* Redis or queue infrastructure.
* Network connections.
* Shared external services.

Use bounded concurrency, query limits, batching, and workload separation where appropriate.

### 7.3 Scaling workers

Before increasing worker count:

1. Confirm that the queue is genuinely capacity-limited.
2. Determine whether jobs are blocked by a dependency.
3. Check database connection and query load.
4. Confirm that parallel execution is safe.
5. Verify ordering and locking requirements.
6. Estimate the additional resource demand.
7. Scale incrementally.
8. Observe queue age, completion rate, errors, and interactive latency.

More workers can increase contention and reduce total system performance.

### 7.4 Fairness between tenants

Where shared infrastructure serves multiple restaurant networks, background workloads must not allow one tenant's expensive jobs to starve other tenants.

Apply fair scheduling, quotas, bounded concurrency, or workload isolation when justified by measured contention and business requirements.

## 8. Retry and Failure Handling

### 8.1 Failure classification

Classify failures before retrying.

**Potentially transient failures**

Examples include temporary network interruption, short dependency unavailability, or rate limiting. Retry may be appropriate when the operation's outcome is known or protected by idempotency.

**Permanent or configuration failures**

Examples include invalid payloads, unsupported job versions, missing required configuration, or authorization failures. Repeated retries generally do not solve these problems.

**Uncertain outcome**

Examples include a timeout after a database commit or a connection loss after an external service may have accepted a request. Reconciliation is required before resubmission unless the operation has a proven safe idempotency mechanism.

### 8.2 Retry policy

Each job type must define:

* Retryable error categories.
* Maximum attempt count.
* Per-attempt timeout.
* Delay between attempts.
* Backoff strategy.
* Whether jitter is used.
* Conditions for dead-lettering.
* Alerting thresholds.
* Recovery and replay procedure.

Use bounded retries. Exponential backoff with jitter is often appropriate for transient failures, but the final policy must reflect the dependency and workload.

Avoid synchronized retry storms across many jobs.

### 8.3 Retry side effects

Before retrying a job that can change business state, verify:

* Whether the original attempt committed.
* Whether an idempotency key or durable operation identifier exists.
* Whether a partial result must be reconciled.
* Whether an external service accepted the operation.
* Whether the retry can safely continue from a recorded checkpoint.

A retry must not duplicate a completed operation.

### 8.4 Dead-letter handling

A dead-letter queue or equivalent failure store isolates jobs that exhausted automatic processing.

For each dead-lettered job:

1. Preserve the original job identifier and relevant metadata.
2. Record the failure category and attempt history.
3. Identify the owning team.
4. Assess business impact and urgency.
5. Determine whether the outcome is known.
6. Correct the root cause before replay.
7. Verify idempotency or reconcile existing effects.
8. Replay through an authorized mechanism, if safe.
9. Verify successful completion.
10. Record the disposition.

Dead-letter storage must follow access control and retention requirements.

### 8.5 Poison messages

A poison message repeatedly fails because of invalid data, incompatible schema, or a deterministic processing defect.

Detect repeated failures and isolate the affected message rather than allowing it to block an entire queue indefinitely.

Do not discard poison messages silently when they represent business operations that require investigation.

## 9. Idempotency and Duplicate Execution

Every state-changing job must have a documented duplicate-execution strategy.

Suitable mechanisms may include:

* Durable job identifiers.
* Idempotency keys.
* Unique business-operation constraints.
* Transactional state transitions.
* Deduplication records.
* Checkpoints for resumable work.
* Transactional outbox or inbox patterns where appropriate.

The implementation must be selected according to the actual business operation and storage model.

### 9.1 High-risk jobs

Give special attention to jobs affecting:

* Order status.
* Payment or refund state.
* Inventory quantities.
* Cash-register balances.
* Offline operation ingestion.
* Subscription entitlement state.
* Data deletion.
* Financial or inventory reports with externally visible side effects.

For these operations, repeated delivery must not create repeated business effects.

### 9.2 Ordering requirements

Some jobs may be processed in parallel only when doing so preserves business correctness.

Examples requiring explicit ordering analysis include:

* Operations for the same order.
* Inventory movements affecting the same stock item.
* Events from one offline device.
* Cash-register open, transaction, handover, and close events.
* Subscription state transitions.
* Deletion eligibility and deletion execution.

Do not assume that FIFO delivery alone guarantees correct business ordering across multiple workers, retries, or partitions.

## 10. Scheduler Operations

### 10.1 Scheduled task inventory

For each scheduled task, document:

* Task identifier and purpose.
* Schedule and time zone.
* Expected duration.
* Required dependencies.
* Maximum runtime.
* Concurrency policy.
* Missed-run behavior.
* Overlap behavior.
* Retry and failure policy.
* Monitoring and escalation.
* Manual recovery procedure.

Use a consistent time basis. Store operational timestamps in a consistent standard, normally UTC, while interpreting business schedules according to their explicitly defined time zone.

### 10.2 Duplicate scheduler execution

A scheduler may run more than once because of multiple instances, restarts, failover, or misconfiguration.

Where duplicate execution would be harmful, use an appropriate distributed coordination mechanism, durable run record, unique constraint, or idempotent job design.

A scheduler lock alone must not be treated as a complete correctness guarantee if it can expire while work continues.

### 10.3 Overlapping executions

For each task, define whether overlapping runs are:

* Allowed.
* Serialized.
* Coalesced into a single pending run.
* Rejected while an earlier run is active.

The choice must reflect the task's semantics.

For example, overlapping report generation may be acceptable for independent report parameters, while overlapping subscription transitions or deletion batches may require stronger coordination.

### 10.4 Missed schedules

When a scheduler is unavailable or a scheduled run is missed:

1. Identify which runs were missed.
2. Determine whether they are still required.
3. Assess whether replaying them would duplicate effects.
4. Check whether newer runs supersede older ones.
5. Recover using the task's documented procedure.
6. Monitor backlog and dependency load.
7. Record the recovery.

Do not replay every missed task indiscriminately. A large catch-up batch may overload the database or repeat time-sensitive business actions.

### 10.5 Clock and time-zone changes

Scheduler operations must account for:

* Clock synchronization.
* Time-zone configuration.
* Daylight-saving changes where relevant.
* Duplicate or skipped local times.
* Application restarts near schedule boundaries.
* Long-running jobs crossing schedule intervals.

Business-critical scheduled tasks must have deterministic rules for ambiguous or skipped schedule times.

## 11. Subscription and Data Lifecycle Jobs

Subscription and data lifecycle tasks require special safeguards because they can affect access and permanently delete business records.

### 11.1 Subscription state transitions

A scheduled task may evaluate subscription expiration and apply the configured access state.

The process must:

1. Read the authoritative subscription state.
2. Evaluate expiration using the defined time basis.
3. Apply the approved transition.
4. Ensure the operation is safe to repeat.
5. Record the result.
6. Trigger required notifications.
7. Verify that the resulting access state matches policy.

A delayed scheduler must not grant unauthorized access or incorrectly extend a subscription.

### 11.2 Expired subscription behavior

The system's subscription policy distinguishes access restrictions from data deletion.

Where configured:

* Expiration restricts the applicable operational functions.
* Permitted read-only access remains available according to policy.
* Required notifications are recorded and delivered through the notification process.
* Reactivation restores access only after the authoritative subscription state is valid.
* Background workers must not bypass subscription enforcement.

### 11.3 Deletion eligibility and execution

If the policy allows deletion after a defined period, separate eligibility evaluation from permanent deletion.

Before a deletion job executes:

1. Re-read the authoritative account and subscription state.
2. Confirm that the configured waiting period has elapsed.
3. Verify that the account has not been reactivated.
4. Check legal, contractual, retention, and incident-related holds.
5. Confirm the deletion scope and tenant boundaries.
6. Ensure the operation is authorized and auditable.
7. Use a recoverable or staged process where required by policy.
8. Verify completion and record the result.

A stale queued deletion job must not delete data after the account has become ineligible.

Permanent deletion must not be triggered solely by a previously computed eligibility flag without revalidation.

Detailed lifecycle rules belong in `16_Subscription_and_Data_Lifecycle_Operations.md`.

## 12. Database and External Dependency Operations

### 12.1 Database access

Workers must use bounded database connection pools and avoid unbounded connection creation.

During incidents, check:

* Database availability.
* Connection saturation.
* Slow queries.
* Lock contention.
* Long-running transactions.
* Query plans and workload changes.
* Whether failed jobs are generating repeated database load.

Do not increase worker concurrency to compensate for a database bottleneck.

### 12.2 Transaction boundaries

A job must have clear transaction boundaries.

Where a task updates database state and publishes another message, use a design that avoids losing one side of the operation. A transactional outbox or equivalent durable coordination mechanism may be appropriate.

Do not acknowledge a job before required durable state has been committed unless the design explicitly guarantees recoverability.

### 12.3 External services

For external services:

* Use explicit timeouts.
* Respect rate limits.
* Apply bounded retries.
* Record external operation identifiers when available.
* Reconcile uncertain outcomes.
* Avoid logging credentials or sensitive payloads.

External-service success and local transaction success may occur at different times. The recovery procedure must address partial completion.

## 13. Graceful Shutdown and Worker Deployment

### 13.1 Shutdown requirements

During deployment or maintenance, workers should:

1. Stop accepting new work where supported.
2. Finish active jobs within the approved shutdown window, or stop safely.
3. Preserve uncompleted work.
4. Release leases or locks correctly.
5. Avoid acknowledging unfinished jobs.
6. Close database and external connections cleanly.
7. Report shutdown status.

If a job cannot finish safely, it must be recoverable through the documented retry or reconciliation process.

### 13.2 Deployment compatibility

Before deploying a new worker version:

* Verify queue payload compatibility.
* Verify schema and database compatibility.
* Confirm that old and new workers can coexist if rolling deployment requires it.
* Confirm retry and acknowledgment behavior.
* Test duplicate execution and interruption recovery.
* Check scheduler overlap behavior.
* Ensure the new version does not reinterpret existing jobs incorrectly.

### 13.3 Queue payload versioning

If queued messages may outlive a deployment, payloads should include a version or have a clearly defined compatibility strategy.

Do not remove fields or change field meanings in a way that makes pending messages unsafe to process.

Unsupported messages must be isolated and investigated rather than interpreted using unsafe defaults.

## 14. Monitoring and Alerting

Monitor worker and scheduler health using the observability and alerting framework.

### 14.1 Worker signals

Track:

* Worker process availability.
* Active and idle worker counts.
* Job execution duration.
* Success and failure counts.
* Retry counts.
* Worker crashes and restarts.
* Resource consumption.
* Dependency errors.
* Shutdown and deployment outcomes.

### 14.2 Queue signals

Track:

* Backlog size.
* Oldest job age.
* Arrival and completion rates.
* Dead-letter count.
* Retry backlog.
* Priority-queue delays.
* Queue infrastructure health.

### 14.3 Scheduler signals

Track:

* Last successful run.
* Next expected run.
* Missed runs.
* Execution duration.
* Overlapping execution attempts.
* Lock or lease failures.
* Task failure count.
* Result verification status.

### 14.4 Alerting principles

Alert when the condition threatens business operations or violates a defined service objective.

Examples include:

* Time-critical jobs exceeding their maximum acceptable age.
* Persistent worker unavailability.
* Repeated failures of a business-critical scheduled task.
* Rapid growth in dead-lettered jobs.
* Subscription transitions not completing within policy.
* Deletion jobs encountering unexpected eligibility or scope mismatches.
* Offline synchronization backlog exceeding its operational limit.
* Background load materially degrading interactive POS requests.

Thresholds must be defined from actual workload, operational requirements, and service objectives. Do not invent universal numeric thresholds.

## 15. Troubleshooting Runbooks

### 15.1 Queue backlog is growing

1. Identify the queue and affected job types.
2. Compare incoming and completion rates.
3. Check worker availability.
4. Inspect failure and retry patterns.
5. Check database and dependency health.
6. Assess the urgency of the affected business operations.
7. Apply a controlled capacity or dependency fix.
8. Verify that backlog age declines.

### 15.2 Workers are running but no jobs complete

Check:

* Whether jobs are being claimed.
* Whether workers are blocked on dependencies.
* Whether locks or leases are stuck.
* Whether a poison message blocks progress.
* Whether database connections are exhausted.
* Whether the worker version supports the queued payload.
* Whether timeouts are appropriate.

Restarting workers without understanding the cause may interrupt more jobs or increase retry volume.

### 15.3 Jobs repeatedly fail

1. Identify the failure category.
2. Review sanitized error details and attempt history.
3. Determine whether the failure is transient, permanent, or uncertain.
4. Check recent configuration and deployment changes.
5. Stop unproductive retry loops when permitted.
6. Isolate the affected jobs if necessary.
7. Correct the cause.
8. Reconcile any partial business effects.
9. Replay only through the approved process.

### 15.4 Scheduler has stopped running tasks

Check:

* Scheduler process health.
* Schedule configuration and time zone.
* Host clock synchronization.
* Leadership, lock, or lease state where used.
* Recent deployment or configuration changes.
* Database and queue connectivity.
* Task-specific failures.
* Whether multiple scheduler instances are conflicting.

Recover missed tasks selectively and verify their business effects.

### 15.5 Duplicate job effects are suspected

1. Stop unsafe manual replays.
2. Identify the original and repeated job identifiers.
3. Inspect the authoritative business records.
4. Determine whether the operation was committed more than once.
5. Apply the approved reconciliation or correction process.
6. Preserve evidence.
7. Correct the deduplication or idempotency weakness.
8. Verify that the correction did not introduce additional effects.

### 15.6 Worker deployment caused failures

Check:

* Queue payload compatibility.
* Database schema compatibility.
* Configuration differences.
* Dependency versions.
* Retry and acknowledgment changes.
* Concurrency and locking behavior.
* Whether rollback can safely coexist with already processed jobs.

Roll back only to a version that can safely handle current queued data and business state.

### 15.7 Resource exhaustion

Check:

* CPU and memory.
* Database connection pools.
* Slow or unbounded queries.
* Job payload size.
* Excessive parallelism.
* Retry storms.
* Large exports or AI jobs.
* Queue storage growth.

Apply bounded mitigation and verify that interactive operations recover.

## 16. Manual Job Operations

Manual job execution, replay, cancellation, or state correction must be restricted to authorized operators.

Before a manual operation:

1. Identify the exact job and tenant or branch scope.
2. Confirm the business purpose.
3. Inspect previous attempts.
4. Determine whether the original operation completed.
5. Check idempotency and concurrency safeguards.
6. Assess the impact on dependent jobs.
7. Obtain required approval for high-impact operations.
8. Execute using the approved operational interface.
9. Verify the resulting business state.
10. Record the operator, reason, action, and result.

Avoid direct database modifications to simulate job completion.

If direct intervention is necessary for an exceptional recovery, use an approved, reviewed procedure with an audit record and post-action verification.

## 17. Security and Access Control

* Restrict queue administration and worker-management permissions.
* Apply least privilege to worker service accounts.
* Separate operational access from business-user permissions.
* Validate tenant and branch scope in every relevant job.
* Do not trust queue payloads as proof of authorization.
* Protect dead-letter queues and diagnostic data.
* Avoid logging secrets, payment credentials, or unnecessary personal information.
* Rotate credentials according to the security policy.
* Audit manual replay, cancellation, and high-impact state changes.
* Prevent untrusted users from submitting arbitrary executable tasks.

A queued job must not gain privileges merely because it is processed by a trusted worker.

## 18. Recovery and Reconciliation

Recovery must distinguish transport recovery from business recovery.

### 18.1 Transport recovery

Examples include restoring queue connectivity, restarting a failed worker, releasing an expired lease, or resuming a scheduler.

### 18.2 Business recovery

Examples include confirming that:

* A notification was eventually delivered or marked permanently failed.
* An order operation completed exactly as intended.
* Inventory movements were applied consistently.
* An offline batch was accepted without duplicate effects.
* A subscription transition matches the authoritative state.
* A deletion job affected only the eligible records.
* A report reflects the correct source data and reporting interval.

Transport recovery does not prove business recovery.

### 18.3 Reconciliation requirements

Reconciliation must use authoritative business records and the operation's durable identifiers.

For uncertain outcomes:

* Preserve the original job and attempt history.
* Identify any committed side effects.
* Avoid duplicate execution.
* Apply an approved correction if necessary.
* Record the final reconciled state.
* Verify downstream jobs and notifications.

## 19. Evidence and Operational Records

Retain relevant records for significant worker or scheduler incidents:

* Queue and job identifiers.
* Job type and version.
* Worker version and source revision.
* Execution and failure timestamps.
* Attempt count and sanitized error details.
* Relevant dependency health information.
* Scheduler run identifiers and expected schedule.
* Manual actions and approvals.
* Reconciliation results.
* Deployment or configuration changes.
* Corrective actions and ownership.

Evidence retention must follow applicable security, privacy, and operational policies.

## 20. Operational Readiness Checklist

### Before release

* [ ] Worker inventory is current.
* [ ] Job payload compatibility is verified.
* [ ] Retry and timeout policies are defined.
* [ ] Idempotency safeguards are tested.
* [ ] Scheduler overlap behavior is documented.
* [ ] Queue and dependency capacity are sufficient.
* [ ] Rollback compatibility is assessed.
* [ ] High-impact tasks have recovery procedures.

### During normal operations

* [ ] Workers are healthy and completing jobs.
* [ ] Queue age remains within approved limits.
* [ ] Dead-letter and retry volumes are reviewed.
* [ ] Critical scheduled tasks run successfully.
* [ ] Database and dependency load remain controlled.
* [ ] Tenant and branch boundaries are preserved.
* [ ] High-impact job failures are escalated appropriately.

### During recovery

* [ ] The failure category is understood.
* [ ] Uncertain business outcomes are reconciled.
* [ ] Retry or replay is safe and authorized.
* [ ] Duplicate effects are prevented.
* [ ] Backlog recovery does not overload dependencies.
* [ ] Business outcomes are verified.
* [ ] Evidence and follow-up actions are recorded.

## 21. Related Documents

* `README.md` — Operations documentation index.
* `03_Monitoring_and_Observability_Operations.md` — Monitoring and observability.
* `04_Alerting_and_Notification_Operations.md` — Alerting and escalation.
* `05_Incident_Management.md` — Incident lifecycle and recovery.
* `06_On_Call_and_Escalation_Management.md` — Operational ownership and escalation.
* `09_Database_Operations.md` — Database operations.
* `10_Redis_Queue_and_Cache_Operations.md` — Queue infrastructure, Redis, and cache operations.
* `11_Backend_API_Operations.md` — Backend API runtime operations.
* `14_AI_Runtime_Operations.md` — AI runtime operations.
* `16_Subscription_and_Data_Lifecycle_Operations.md` — Subscription and data lifecycle.
* `17_Security_Operations.md` — Security operations.
* `18_Release_and_Change_Operations.md` — Release and change management.
* `20_Operations_Invariants_and_Guardrails.md` — Mandatory operational guardrails.

## 22. Mandatory Operational Invariants

1. Every production worker group must have a documented owner.
2. Every production job type must have a defined purpose.
3. Every high-impact job must have a recovery procedure.
4. Job execution must not be assumed to be exactly once unless the implementation proves it.
5. State-changing jobs must have a duplicate-execution strategy.
6. A queue acknowledgment must not be treated as proof of business completion.
7. Durable business state must not depend solely on the continued existence of a queue message.
8. Job outcomes must be distinguishable as successful, failed, pending, or uncertain.
9. Uncertain outcomes must be reconciled before unsafe retries.
10. Retry attempts must be bounded.
11. Retry policies must distinguish transient and permanent failures.
12. Retry delays must avoid synchronized retry storms where appropriate.
13. Poison messages must not silently block unrelated work.
14. Dead-lettered jobs must retain sufficient diagnostic context.
15. Manual replay must be authorized and auditable.
16. Manual replay must not bypass idempotency safeguards.
17. Queue backlogs must be assessed by age and business impact, not count alone.
18. Worker concurrency must have explicit limits.
19. Background processing must not starve interactive operations.
20. Worker scaling must account for database and dependency capacity.
21. Tenant workloads must not cause uncontrolled resource starvation for other tenants.
22. Job ordering requirements must be documented where business correctness depends on order.
23. Scheduled tasks must define overlap behavior.
24. Scheduler execution must be safe against duplicate triggers where duplication is harmful.
25. Missed schedules must be recovered selectively.
26. Schedule time zones must be explicit.
27. Clock changes must not silently corrupt business scheduling.
28. High-impact scheduled tasks must report their execution outcomes.
29. Workers must shut down without silently losing unfinished work.
30. Deployment must preserve compatibility with pending jobs.
31. Queue payload changes must have a compatibility strategy.
32. Worker rollback must account for already processed jobs and current queue contents.
33. Database connections and transactions must be bounded and controlled.
34. External service calls must use appropriate timeouts.
35. External side effects must be reconciled when their outcome is uncertain.
36. Order processing must not create unintended duplicate business effects.
37. Inventory processing must preserve stock and movement consistency.
38. Cash-register and financial operations must use authoritative business records.
39. Offline synchronization must preserve pending operations and prevent duplicate ingestion.
40. Subscription jobs must use authoritative subscription state.
41. Deletion jobs must revalidate eligibility before permanent deletion.
42. Workers must not bypass tenant or branch authorization.
43. Queue payloads must not be treated as authorization proof.
44. Worker credentials must follow least-privilege principles.
45. Logs and failure records must not expose unnecessary sensitive data.
46. Resource-exhaustion incidents must be mitigated without uncontrolled scaling.
47. Recovery must verify business outcomes, not just worker availability.
48. Manual corrections must be auditable.
49. Significant failures and recovery actions must produce operational evidence.
50. Any job that risks duplicate financial effects, unauthorized access, or irreversible data loss must stop until a safe recovery path is established.

## 23. Acceptance Criteria

This document is accepted for operational use when:

* Worker and scheduler ownership is documented.
* Queue monitoring and backlog procedures are defined.
* Retry, dead-letter, and replay policies are established.
* Duplicate execution and idempotency are addressed.
* Scheduler overlap and missed-run behavior are documented.
* Deployment and shutdown procedures preserve pending work.
* Subscription and deletion jobs include authoritative-state checks.
* Security, recovery, monitoring, and evidence requirements are defined.
* Related deployment, database, queue, security, and incident documents remain consistent.

**End of document.**

