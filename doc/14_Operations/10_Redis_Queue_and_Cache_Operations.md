# Redis, Queue, and Cache Operations

**Document ID:** OPS-10
**Status:** Accepted
**Version:** 1.0
**Last Updated:** 2026-10-09
**Project:** FastFood ERP
**Repository Path:** `doc/14_Operations/10_Redis_Queue_and_Cache_Operations.md`
**Primary Technologies:** Redis and the queue-processing technology selected by the deployed architecture.

## 1. Purpose

This document defines the operational procedures and safety requirements for Redis, caching, asynchronous queues, backlog management, retries, and recovery in FastFood ERP.

The objectives are to:

* Maintain reliable operation of Redis and dependent services.
* Detect queue delays and processing failures before they disrupt restaurant operations.
* Prevent uncontrolled retries, duplicate processing, and queue backlogs.
* Keep cache failures from unnecessarily interrupting core business operations.
* Preserve business-data integrity during queue failures and recovery.
* Prevent loss of critical work when a Redis or queue service restarts.
* Support controlled recovery after infrastructure failures and deployments.
* Minimize unnecessary resource usage and operational complexity.

This document defines operational requirements without assuming a specific Redis topology, queue library, message broker, or deployment provider.

## 2. Scope

This document covers:

* Redis availability and health.
* Cache operation and invalidation.
* Queue and worker health.
* Backlog monitoring and diagnosis.
* Retry policies and failure handling.
* Idempotency and duplicate processing.
* Dead-letter or permanently failed work handling, where supported.
* Redis memory, eviction, and persistence.
* Queue recovery after restarts or outages.
* Cache stampedes and dependency failures.
* Security, access control, and operational evidence.
* Capacity planning and incident response.
* Recovery verification for business-critical asynchronous operations.

### 2.1 Out of scope

The following are covered by related documents:

* General monitoring and observability: `03_Monitoring_and_Observability_Operations.md`.
* Alerting and notification routing: `04_Alerting_and_Notification_Operations.md`.
* Incident lifecycle: `05_Incident_Management.md`.
* Backup verification and restoration: `07_Backup_Verification_and_Restore_Operations.md`.
* Disaster recovery: `08_Disaster_Recovery_Operations_Runbook.md`.
* PostgreSQL operations: `09_Database_Operations.md`.
* Backend API runtime operations: `11_Backend_API_Operations.md`.
* Background worker and scheduler procedures: `13_Background_Worker_and_Scheduler_Operations.md`.
* Security operations: `17_Security_Operations.md`.
* Production releases and change control: `18_Release_and_Change_Operations.md`.
* Capacity and infrastructure cost management: `19_Capacity_Cost_and_Resource_Operations.md`.

This document complements these procedures and does not replace them.

## 3. Core Operational Principles

1. **Business data must remain authoritative.** Redis cache entries must not be the only authoritative copy of important business records.
2. **Queue guarantees must be explicit.** Operators must know whether the selected queue provides at-most-once, at-least-once, or another delivery model.
3. **Duplicate execution must be expected.** Where work may be redelivered, handlers must be designed to tolerate duplicates.
4. **Retries must be bounded.** Repeated failure must not create an infinite processing loop.
5. **Backlogs must be measurable.** Queue depth alone is insufficient; message age and processing latency also matter.
6. **Cache failure must be handled deliberately.** The application must have an approved response when cached data is unavailable.
7. **Critical work must be recoverable.** Recovery must use the durability guarantees of the actual queue implementation.
8. **No destructive recovery without evidence.** Clearing queues, deleting keys, or flushing Redis requires explicit authorization and impact assessment.
9. **Tenant isolation must be preserved.** Queue payloads, cache keys, and worker operations must maintain restaurant-network and branch boundaries.
10. **Recovery requires business validation.** Service health alone does not prove that orders, inventory, payments, or synchronization are correct.

## 4. Redis and Queue Architecture Inventory

Maintain an inventory of Redis deployments and queue-processing components.

For each component, document:

* Environment and service identifier.
* Purpose: cache, queue, rate limiting, coordination, or another approved function.
* Owning team and escalation contact.
* Application services and workers that depend on it.
* Redis version and deployment model.
* Connection endpoints through approved configuration references.
* Authentication and network access controls.
* Memory allocation and capacity limits.
* Persistence and replication configuration, if applicable.
* Cache eviction policy.
* Queue implementation and delivery guarantees.
* Queue names or logical queue identifiers.
* Worker groups and concurrency settings.
* Retry and failure-handling policies.
* Monitoring dashboards and alert rules.
* Backup and recovery references, where relevant.
* Expected behavior when the component becomes unavailable.

Never store credentials, access tokens, or secret connection strings in the inventory.

### 4.1 Component classification

Classify each Redis deployment according to its responsibilities.

| Classification                | Operational expectation                                                            |
| ----------------------------- | ---------------------------------------------------------------------------------- |
| Cache-only                    | Cached entries may be rebuilt from the authoritative source                        |
| Queue or job storage          | Durability and recovery guarantees must be explicitly documented                   |
| Mixed cache and queue         | Memory pressure and eviction must not silently endanger queued work                |
| Coordination or rate limiting | Failure behavior and acceptable degradation must be documented                     |
| Other                         | The owning team must document purpose, data sensitivity, and recovery requirements |

Where cache and queue workloads have conflicting memory, eviction, or durability requirements, prefer separate Redis deployments or another architecture that provides appropriate isolation. The final decision must reflect measured workload, reliability requirements, and operational cost.

## 5. Service Health and Availability

### 5.1 Redis health signals

Monitor the signals supported by the deployed Redis version and architecture:

* Connectivity and authenticated connection success.
* Command latency and error rates.
* Memory usage and configured memory limit.
* Eviction activity.
* Rejected writes or memory-related errors.
* Connected clients.
* Client connection churn.
* CPU utilization.
* Network throughput.
* Persistence activity and failures, if enabled.
* Replication status and lag, if configured.
* Key expiration activity.
* Queue-specific storage and processing metrics.
* Restart and recovery events.
* Connection pool utilization in dependent services.

Metrics must be interpreted together. A successful Redis ping does not prove that queue processing, persistence, or cache-dependent application behavior is healthy.

### 5.2 Queue health signals

For every critical queue, monitor:

* Current queued item count.
* Age of the oldest pending item.
* Enqueue rate.
* Completion rate.
* Failure rate.
* Retry rate.
* Processing duration.
* Worker availability.
* Active and waiting jobs.
* Permanently failed jobs, where supported.
* Delayed or scheduled jobs.
* Time since the last successful completion.
* Queue storage growth.
* Duplicate or idempotency conflict indicators, where measurable.

A queue may have a small backlog but still be unhealthy if the oldest item is unusually old or a critical job has stopped progressing.

### 5.3 Health and readiness

Differentiate between:

* **Redis connectivity:** The service can establish an authenticated connection.
* **Cache readiness:** The application can perform the required cache operations.
* **Queue readiness:** Producers can submit work and workers can retrieve it under the configured delivery model.
* **Processing readiness:** Workers can execute jobs and complete required dependencies.
* **Durability readiness:** Required persistence or replication conditions are satisfied where the architecture relies on them.

Health checks must be lightweight, bounded by timeouts, and safe during degraded conditions.

## 6. Queue Classification and Priorities

Classify queues according to business importance, expected processing delay, data sensitivity, and recovery requirements.

Potential FastFood ERP workload categories include:

* Notifications and subscription reminders.
* Reports and analytics generation.
* Inventory-related calculations.
* Scheduled maintenance and lifecycle jobs.
* Offline synchronization processing.
* Integration requests.
* File or document processing.
* AI inference or other optional computation, if implemented asynchronously.

These are possible categories, not a requirement to create a separate queue for every function.

### 6.1 Queue separation

Separate workloads when their processing behavior, resource usage, failure patterns, or business criticality justify it.

For example:

* Expensive report generation should not starve time-sensitive operational tasks.
* Retry-heavy external integrations should not block unrelated work.
* Optional AI jobs should not consume all worker capacity needed for essential business processing.
* Subscription deletion jobs should have stricter authorization and verification than routine cache refreshes.

Avoid excessive queue fragmentation when it provides no measurable reliability or performance benefit.

### 6.2 Priority safeguards

* Define the priority policy for critical queues.
* Prevent low-priority workloads from monopolizing all workers.
* Reserve capacity only where the operational requirement justifies it.
* Monitor starvation of lower-priority jobs.
* Document how priority affects retries and delayed jobs.
* Avoid using queue priority as a substitute for a clear business deadline or service-level requirement.

## 7. Queue Processing Lifecycle

Each queue must have a documented processing lifecycle appropriate to its implementation.

The logical lifecycle should distinguish:

1. Work created.
2. Work accepted by the queueing mechanism.
3. Work available for processing.
4. Work claimed or delivered to a worker.
5. Work being processed.
6. Work successfully completed and acknowledged.
7. Work scheduled for retry.
8. Work permanently failed or quarantined.
9. Work recovered or replayed after investigation.

The actual queue may implement these states differently. Documentation must reflect the real behavior rather than assume that every broker provides the same features.

### 7.1 Producer requirements

Producers must:

* Validate the job type and required fields.
* Include a stable job or business-operation identifier when appropriate.
* Avoid placing unnecessary sensitive data in queue payloads.
* Define what happens if enqueueing fails.
* Use a reliable handoff mechanism when a committed database change must result in asynchronous work.
* Avoid claiming successful enqueueing before the configured queue mechanism confirms acceptance.
* Apply bounded retries when submission failures are safe to retry.

### 7.2 Consumer requirements

Workers must:

* Validate incoming payloads.
* Reject unsupported or malformed jobs safely.
* Apply authorization and tenant-scope checks where relevant.
* Use idempotent processing where redelivery is possible.
* Apply timeouts to external calls and long-running operations.
* Acknowledge completion only according to the queue's documented semantics.
* Handle shutdown and cancellation without silently losing work.
* Record failures without exposing sensitive payloads.
* Avoid infinite loops when a job repeatedly fails.
* Make the final business outcome observable.

## 8. Backlog Monitoring and Management

### 8.1 Backlog definition

A backlog is accumulated work waiting to be processed or completed.

Backlog can grow because of:

* Increased producer traffic.
* Insufficient worker capacity.
* Slow database operations.
* External service failures.
* Repeated retries.
* Worker crashes.
* Redis or network latency.
* Long-running jobs.
* A deployment that introduces slower processing.
* A scheduled batch that produces work faster than it can be consumed.

### 8.2 Backlog signals

Monitor:

* Pending job count.
* Oldest pending job age.
* Rate of incoming jobs.
* Rate of successful completions.
* Failed and retried jobs.
* Average and tail processing duration.
* Active worker count.
* Queue-specific resource consumption.
* Estimated time to drain the backlog, where the estimate can be calculated reliably.

Queue length alone must not be used as the sole indicator of health.

### 8.3 Backlog incident procedure

When backlog grows beyond the established operating range:

1. Identify the affected queue and its business purpose.
2. Check the oldest pending item's age and the arrival/completion rates.
3. Determine whether workers are active and making progress.
4. Inspect job failures, retries, processing duration, and worker logs.
5. Check Redis health and resource pressure.
6. Check PostgreSQL, network, and external dependencies.
7. Review recent releases and configuration changes.
8. Determine whether the backlog consists of valid, duplicate, delayed, or repeatedly failing work.
9. Estimate the effect of adding worker capacity or reducing incoming load.
10. Apply a controlled mitigation.
11. Verify that completion throughput improves and the oldest-item age decreases.
12. Confirm that the resulting business operations remain correct.

Do not add workers blindly. Increasing concurrency can overload PostgreSQL, an external service, or Redis and make the incident worse.

### 8.4 Backlog drain planning

Before draining a large backlog, determine:

* Whether the jobs remain valid.
* Whether jobs are ordered or independent.
* Whether duplicate execution is safe.
* Whether jobs contain expired business instructions.
* Whether the target service can handle increased traffic.
* Whether rate limits apply.
* Whether the backlog contains tenant-sensitive operations.
* Whether the queue implementation preserves ordering under concurrency.
* Whether operators need to pause producers or separate new work from historical work.

Use controlled batches and monitor the impact. Avoid deleting old jobs simply because they have accumulated.

## 9. Retry Policy

### 9.1 Retryable and non-retryable failures

Classify failures before retrying.

| Failure type                                      | Default handling                                                           |
| ------------------------------------------------- | -------------------------------------------------------------------------- |
| Temporary network interruption                    | Bounded retry if the operation is safe to repeat                           |
| Temporary dependency overload                     | Backoff, respect rate limits, and reduce pressure                          |
| Database deadlock or transient connection failure | Retry only when transaction and operation semantics make it safe           |
| Invalid job payload                               | Reject or quarantine; do not retry unchanged indefinitely                  |
| Authorization failure                             | Stop automatic retries and investigate configuration or permissions        |
| Missing required business entity                  | Apply domain-specific handling; do not assume it will appear later         |
| Permanent validation error                        | Mark failed or route for investigation                                     |
| Unknown outcome after timeout                     | Determine whether the operation may already have succeeded before retrying |

These are defaults. Each queue and job type must define its own policy.

### 9.2 Backoff

Use bounded retry attempts with an appropriate delay strategy.

A common approach is exponential backoff with jitter, subject to the queue technology's capabilities.

The policy must define:

* Maximum attempts.
* Initial delay.
* Maximum delay.
* Overall processing deadline, where applicable.
* Conditions that reset or preserve retry counts.
* Treatment of rate-limit responses.
* Permanent failure behavior.
* Alerting thresholds.
* Manual replay requirements.

Do not retry at high frequency during a prolonged outage. Such behavior can amplify load and prevent the underlying dependency from recovering.

### 9.3 Retry safety

Before retrying a business operation, determine whether it may already have succeeded.

For example, if a worker sends a request to an external service and times out before receiving the response, the external action may still have completed.

Use stable idempotency keys, unique business-operation identifiers, or another domain-appropriate deduplication mechanism where supported.

A retry must not create duplicate orders, duplicate payments, repeated inventory deductions, duplicate salary entries, or duplicate subscription-deletion actions.

### 9.4 Retry monitoring

Monitor:

* Retry counts by job type.
* Jobs approaching the maximum attempt count.
* Retry delay distribution.
* Repeated failures for the same operation.
* Failure rates by dependency.
* The proportion of jobs completing after a retry.
* Jobs whose overall processing deadline has expired.

A high retry rate is an operational signal, even when jobs eventually succeed.

## 10. Permanently Failed Jobs and Dead-Letter Handling

If the selected queue supports a dead-letter queue, failed-job store, or equivalent mechanism, document how it is used.

If it does not, define a suitable alternative that preserves enough metadata for safe investigation and controlled recovery.

### 10.1 Required failure information

Retain, subject to the data-retention policy:

* Job identifier.
* Job type.
* Relevant tenant or branch reference, where appropriate.
* Failure category.
* Attempt count.
* First and most recent failure timestamps.
* Last known processing stage.
* Sanitized error information.
* Correlation or trace identifier.
* Original event reference, if safely retained.
* Recovery status and operator action.

Do not retain unrestricted sensitive payloads merely for debugging.

### 10.2 Investigation and replay

Before replaying a failed job:

1. Confirm that the job is still valid.
2. Identify and correct the original failure.
3. Determine whether the business operation already completed.
4. Check for duplicate processing or partial side effects.
5. Verify the tenant and branch scope.
6. Confirm that the job is compatible with the current application version.
7. Obtain the required approval for sensitive operations.
8. Replay a controlled sample when practical.
9. Validate the outcome.
10. Continue replay in bounded batches and monitor downstream systems.

Replay must preserve required identifiers and idempotency behavior. Do not generate a new business-operation identifier simply to bypass deduplication.

### 10.3 Permanent failure review

Review permanently failed jobs according to their business importance and retention policy.

Critical work must not remain unowned indefinitely. Assign responsibility, record the disposition, and escalate unresolved business-critical failures.

## 11. Idempotency and Duplicate Processing

Queue systems may redeliver work after worker crashes, visibility timeouts, network interruptions, or uncertain acknowledgements.

### 11.1 Required behavior

For operations where duplicate execution could cause harm:

* Use a stable operation identifier.
* Record completed processing where appropriate.
* Enforce database uniqueness or equivalent safeguards when suitable.
* Keep state transitions conditional and validated.
* Ensure retries cannot bypass business rules.
* Preserve the relationship between a job and its resulting business operation.
* Make duplicate detection observable.
* Define how partially completed work is reconciled.

Idempotency must be implemented at the business-operation level. A unique queue message ID alone may not be sufficient if the same logical operation can be submitted with a different message ID.

### 11.2 Database and queue consistency

When a PostgreSQL transaction and queue publication must represent one logical business event, use an approved reliable handoff design.

Possible approaches include a transactional outbox or another architecture that ensures committed business changes are not silently separated from required asynchronous work.

The implementation must define:

* When the business transaction commits.
* When the event becomes eligible for publication.
* How failed publication is retried.
* How duplicate publication is handled.
* How completed events are marked.
* How abandoned or inconsistent states are detected.
* How recovery is performed after a crash.

Do not assume that a PostgreSQL transaction and an independent Redis write form one atomic transaction.

## 12. Cache Operations

### 12.1 Cache purpose

Redis cache may be used to reduce repeated computation or database reads for data that can be safely reconstructed from an authoritative source.

Potential cache candidates include:

* Read-heavy menu data.
* Product and category lookups.
* Approved configuration data.
* Permission or session-related data, subject to security requirements.
* Expensive derived information with a defined freshness policy.
* Dashboard summaries that tolerate a documented delay.

These are candidate categories, not mandatory cache targets.

### 12.2 Cache requirements

Every important cache entry must have a documented policy for:

* Source of truth.
* Cache key format.
* Tenant and branch scope.
* Expiration or refresh behavior.
* Invalidation triggers.
* Acceptable staleness.
* Behavior when the cache is unavailable.
* Data sensitivity.
* Expected size and memory cost.

Never use cached data as the sole authoritative source for payments, financial records, stock movements, or other critical business state unless an explicitly designed durable system provides the required guarantees.

### 12.3 Cache invalidation

When authoritative data changes:

1. Identify the affected cache entries.
2. Apply the approved invalidation or refresh strategy.
3. Ensure that invalidation covers the correct tenant and branch scope.
4. Verify that stale entries cannot override newer authoritative data.
5. Monitor cache behavior after the change.

If a cache invalidation event is lost, the system must have an acceptable fallback, such as a bounded TTL, version check, or reconciliation process.

The appropriate mechanism depends on the data's freshness requirements.

### 12.4 Cache miss behavior

On a cache miss:

* Retrieve data from the approved authoritative source.
* Validate access and tenant scope.
* Populate the cache only when appropriate.
* Apply a timeout to the source query.
* Avoid repeated unbounded source requests.
* Handle source failures according to the endpoint's availability requirements.

A cache miss must not bypass authorization or branch-specific rules.

## 13. Cache Stampedes and Load Protection

A cache stampede occurs when many requests simultaneously attempt to rebuild the same missing or expired cache entry.

Possible safeguards include:

* Request coalescing or single-flight loading.
* Short-lived locks where justified and safely implemented.
* TTL jitter.
* Stale-while-revalidate behavior when the data's freshness policy permits it.
* Bounded source-query concurrency.
* Rate limiting.
* Graceful degradation.
* Prewarming of selected entries after deployment, where justified.

Any locking approach must account for lock expiration, process crashes, and ownership. A Redis lock must not be treated as an unconditional guarantee of exclusive execution.

During a cache stampede incident:

1. Identify the affected keys or workload categories.
2. Determine whether expiration or invalidation caused the spike.
3. Check PostgreSQL and application load.
4. Limit uncontrolled cache rebuilding.
5. Restore or repopulate the cache using a controlled method.
6. Confirm that authoritative data remains correct.
7. Review expiration policies and invalidation behavior.

## 14. Cache Eviction and Memory Management

### 14.1 Memory monitoring

Monitor:

* Current memory use.
* Configured memory limit.
* Memory growth rate.
* Eviction count and rate.
* Allocation or write failures.
* Key count and key-size distribution where available.
* Fragmentation indicators.
* Client buffers and replication-related memory where relevant.
* Queue storage growth if Redis also holds queue data.

### 14.2 Eviction policy

The eviction policy must match the workload.

For cache-only Redis, eviction may be acceptable when the application can rebuild entries safely.

For Redis used to store queued jobs or other operationally critical state, an eviction policy that can remove required work may be unacceptable.

If cache and queue workloads share a deployment, verify that memory pressure and eviction cannot silently remove required queue state.

### 14.3 Memory pressure response

When memory approaches the configured limit:

1. Confirm the affected Redis instance and workload.
2. Review memory growth, eviction activity, and write errors.
3. Determine whether growth comes from cache keys, queues, delayed jobs, client buffers, or another source.
4. Check whether expiration and cleanup policies are working.
5. Identify abnormal key growth or backlog accumulation.
6. Estimate the impact of increasing capacity or reducing load.
7. Apply an approved change.
8. Verify that critical queue state remains safe.
9. Record the root cause and preventive actions.

Do not run `FLUSHALL`, `FLUSHDB`, broad key deletion, or equivalent destructive commands as a routine memory-management measure.

## 15. Redis Persistence, Replication, and Restart Recovery

Redis persistence and replication must be configured according to the role of the deployment and the actual durability requirements.

### 15.1 Persistence considerations

Document whether the deployment uses:

* Snapshot-based persistence.
* Append-only persistence.
* Both mechanisms.
* No persistence because all stored state is explicitly disposable.
* Managed-service persistence or another supported arrangement.

The selected configuration must account for:

* Acceptable data-loss window.
* Restart and recovery time.
* Write throughput.
* Storage capacity.
* Persistence overhead.
* Backup and restore requirements.
* The queue's own durability guarantees.

Persistence must not be enabled or disabled without evaluating the operational and business consequences.

### 15.2 Restart procedure

Before a planned restart:

1. Identify the Redis role and dependent services.
2. Determine whether it stores only reconstructable cache data or also important operational state.
3. Review queue backlog and in-flight jobs.
4. Confirm that recovery procedures and required backups are available where applicable.
5. Coordinate worker and producer behavior.
6. Execute the approved restart procedure.
7. Verify Redis health and persistence recovery.
8. Verify queue continuity and worker progress.
9. Confirm that dependent application workflows operate correctly.
10. Record any data loss, processing gaps, or recovery anomalies.

### 15.3 Unplanned restart or data loss

After an unexpected restart:

* Determine whether the service recovered from persistent state.
* Check for missing, duplicated, or delayed work.
* Review queue implementation guarantees and any acknowledged writes that may have been lost.
* Reconcile authoritative PostgreSQL state with asynchronous processing state.
* Investigate incomplete business operations.
* Replay work only after checking its validity and idempotency.
* Follow OPS-07 or OPS-08 if backup restoration or broader disaster recovery is required.

A Redis process becoming available again does not prove that all previously accepted jobs were preserved.

## 16. Queue and Worker Recovery

### 16.1 Recovery after a worker outage

When workers stop or become unhealthy:

1. Identify the affected worker group and queues.
2. Determine whether jobs remain queued, active, delayed, or unacknowledged.
3. Check the cause of the outage.
4. Verify that required dependencies are healthy.
5. Restore the worker service using the approved procedure.
6. Confirm that workers can claim and complete work.
7. Monitor retries, backlog age, and downstream resource utilization.
8. Validate critical business operations.
9. Record unresolved or permanently failed jobs.

### 16.2 Recovery after a queue outage

When the queue becomes unavailable:

1. Identify which producers and workers are affected.
2. Determine whether the queue service is unreachable, overloaded, or rejecting writes.
3. Assess whether producers received confirmed acceptance for their submissions.
4. Check for jobs stored in another durable system or pending publication.
5. Restore queue availability using the approved service procedure.
6. Verify the queue's recovery point and processing semantics.
7. Resume or restart producers and workers in a controlled order.
8. Reconcile work that may have been missed or duplicated.
9. Monitor the backlog until it returns to an acceptable state.
10. Confirm the correctness of affected business workflows.

Do not assume that jobs rejected before acceptance are automatically recoverable. Producers must have a documented failure-handling strategy.

### 16.3 Controlled backlog recovery

If a large backlog must be processed after an outage:

* Start with a controlled number of workers.
* Confirm that downstream dependencies have adequate capacity.
* Increase concurrency gradually.
* Monitor database connections and latency.
* Apply queue-specific rate limits where appropriate.
* Watch for repeated failures and retry amplification.
* Avoid replaying invalid or obsolete jobs.
* Confirm that tenant and branch isolation remains intact.
* Stop or reduce processing if recovery increases business risk.

## 17. Queue Durability and Business-Critical Work

### 17.1 Critical work classification

For each business-critical asynchronous operation, document:

* The authoritative record.
* Whether the operation may be delayed.
* What happens if queue submission fails.
* Whether the job can be reconstructed.
* How duplicate execution is prevented.
* How missing work is detected.
* The maximum acceptable processing delay.
* The recovery and reconciliation procedure.
* The responsible business owner.

### 17.2 Recommended safeguards

When a business transaction must reliably trigger asynchronous work, consider a transactional outbox or another reliable handoff pattern.

Where appropriate:

* Store the required business state in PostgreSQL.
* Record the pending event within the same database transaction.
* Publish it asynchronously.
* Mark publication progress.
* Make consumers idempotent.
* Reconcile records that remain pending beyond an acceptable period.

The chosen implementation must be documented and tested. An outbox is not a substitute for correct consumer idempotency or operational monitoring.

### 17.3 Business-specific recovery

**Orders and payments:** Verify the authoritative order and payment state before retrying work. Never infer payment success solely from a queue acknowledgement.

**Inventory:** Confirm whether the stock movement was committed before replaying a failed job. Avoid duplicate ingredient deductions.

**Offline synchronization:** Reconcile device-generated operations and server state using the approved synchronization model. Do not delete queued synchronization work merely to reduce backlog.

**Subscriptions:** Ensure that repeated lifecycle jobs cannot apply unintended duplicate transitions or deletions.

**Notifications:** Duplicate delivery may sometimes be tolerable, but it must be documented. Do not treat notification delivery as proof that the underlying business action succeeded.

**AI and analytics:** Where these jobs are non-critical and reconstructable, prioritize resource protection and controlled reprocessing rather than allowing them to starve essential operational work.

## 18. Scheduled Jobs and Delayed Work

Scheduled and delayed jobs must have documented ownership, timing expectations, and failure behavior.

Monitor:

* Expected versus actual execution time.
* Missed or delayed schedules.
* Duplicate scheduling.
* Overlapping runs.
* Execution duration.
* Retry behavior.
* Dependency failures.
* Jobs that remain pending beyond their deadline.

After a scheduler outage:

1. Identify missed runs and their business purpose.
2. Determine whether each job should run once, catch up, or be skipped.
3. Check whether the job is idempotent.
4. Confirm that executing overdue work will not overload dependencies.
5. Execute the approved recovery procedure.
6. Verify results and record skipped or repeated runs.

Do not automatically replay every missed scheduled job. Some tasks become obsolete after their intended execution time.

See `13_Background_Worker_and_Scheduler_Operations.md` for detailed scheduler and worker procedures.

## 19. Security and Access Control

### 19.1 Redis security

* Restrict network access to authorized services and operators.
* Use the supported authentication and authorization mechanisms.
* Apply least privilege to Redis users and service identities.
* Protect connection credentials.
* Use encrypted transport where required and supported by the deployment.
* Avoid exposing Redis directly to untrusted networks.
* Disable or restrict dangerous administrative commands according to the security design.
* Review administrative and service access regularly.
* Protect persistence files and backups.
* Ensure that queue payloads do not unnecessarily contain secrets or sensitive personal information.

### 19.2 Tenant and branch isolation

Cache keys and queue payloads must preserve the correct ownership scope.

Where relevant:

* Include an unambiguous tenant identifier in tenant-scoped cache keys.
* Include branch scope when data differs by branch.
* Validate tenant and branch ownership in worker processing.
* Avoid trusting client-supplied identifiers without authorization checks.
* Ensure that cache invalidation cannot accidentally affect unrelated tenants.
* Restrict cross-tenant administrative operations.
* Avoid logging raw payloads containing sensitive information.
* Verify isolation during replay, bulk processing, and recovery.

A globally shared cache is acceptable only when the cached information is genuinely global and safe to share.

### 19.3 Security incident response

If unauthorized access, suspicious commands, exposed credentials, or possible cross-tenant data exposure is detected:

1. Preserve relevant evidence.
2. Restrict affected access where authorized.
3. Assess the scope of potential exposure or modification.
4. Rotate compromised credentials according to the security procedure.
5. Inspect relevant logs and configuration changes.
6. Validate queue and cache integrity.
7. Restore trusted state if required.
8. Follow `17_Security_Operations.md` and the applicable incident procedure.

## 20. Capacity Planning and Resource Protection

Redis and queue capacity must be evaluated against real workload.

Consider:

* Peak producer rates.
* Average and maximum payload sizes.
* Queue retention and retry policies.
* Cache hit ratio and miss rate.
* Key expiration behavior.
* Worker concurrency.
* Processing duration.
* Memory limits.
* Network throughput.
* Persistence overhead.
* Expected restaurant and branch growth.
* Reporting and integration bursts.
* Recovery and backlog-drain requirements.

### 20.1 Capacity safeguards

* Set and monitor resource limits.
* Bound payload sizes.
* Avoid storing large objects in Redis without a justified design.
* Set expiration policies for reconstructable cache entries.
* Prevent unbounded job retention.
* Review queue growth trends.
* Size worker concurrency with downstream dependencies in mind.
* Test expected peak workload where feasible.
* Include recovery traffic in capacity planning.
* Review capacity after significant traffic or architecture changes.

Increasing Redis memory or worker count is not always the correct solution. The root cause may be excessive payload size, a faulty producer, slow downstream processing, or an invalid retry policy.

## 21. Deployment and Configuration Changes

Redis, queue, and worker configuration changes must follow `18_Release_and_Change_Operations.md`.

Changes that require assessment include:

* Redis version upgrades.
* Persistence changes.
* Memory and eviction policies.
* Authentication and authorization changes.
* Connection and timeout settings.
* Queue delivery or acknowledgement behavior.
* Retry limits and backoff settings.
* Worker concurrency.
* Payload schema changes.
* Queue naming or routing changes.
* Cache key formats and invalidation rules.
* Scheduled-job behavior.

Before a release:

1. Identify affected producers, workers, and dependent services.
2. Assess compatibility with existing queued payloads.
3. Confirm whether old and new application versions can process the same jobs.
4. Verify the recovery strategy.
5. Check whether deployment can cause duplicate scheduling or processing.
6. Establish monitoring and rollback criteria.
7. Execute the change through the approved release process.

Queued jobs may outlive the application version that created them. Payload compatibility must therefore be treated as a release concern.

## 22. Operational Incident Playbooks

### 22.1 Redis is unavailable

1. Confirm the scope of the outage.
2. Check service health, network connectivity, authentication, and provider status.
3. Determine whether Redis is used for cache, queue storage, or both.
4. Assess the impact on producers, workers, and API requests.
5. Apply the approved recovery procedure.
6. Verify persistence and replication behavior where relevant.
7. Restore dependent services in a controlled order.
8. Validate queue continuity and business operations.

### 22.2 Cache hit rate drops suddenly

1. Confirm the metric and affected key categories.
2. Check recent deployments, invalidation events, and expiration behavior.
3. Check Redis availability and eviction activity.
4. Assess the load on PostgreSQL and dependent APIs.
5. Limit uncontrolled cache rebuilding if necessary.
6. Restore the intended cache behavior.
7. Verify authoritative data and application performance.

### 22.3 Queue backlog keeps increasing

1. Compare arrival and completion rates.
2. Check the oldest pending job age.
3. Identify worker errors and dependency latency.
4. Check retry amplification and poison jobs.
5. Assess downstream capacity.
6. Apply targeted throttling, worker recovery, or a corrected retry policy.
7. Monitor progress and business correctness.

### 22.4 Retry storm

1. Identify the affected job types and common failure.
2. Determine whether retries are increasing dependency load.
3. Reduce or pause retry pressure using an approved control.
4. Confirm that delayed work remains recoverable.
5. Fix the underlying dependency or handler issue.
6. Resume processing gradually.
7. Verify that the retry rate returns to its expected range.

### 22.5 Duplicate business processing suspected

1. Identify the affected business-operation identifiers.
2. Check authoritative PostgreSQL records.
3. Determine whether duplicate jobs, retries, or concurrent workers caused the issue.
4. Stop or limit the offending processing path when authorized.
5. Prevent further duplicate side effects.
6. Apply an approved business correction if needed.
7. Verify orders, payments, inventory, or other affected records.
8. Record the incident and required idempotency improvements.

### 22.6 Redis memory exhaustion

1. Confirm memory usage and write failures.
2. Determine whether the affected instance contains cache, queue state, or both.
3. Identify abnormal growth and eviction behavior.
4. Assess persistence and data-loss risk.
5. Apply a targeted capacity or workload correction.
6. Do not flush databases or delete internal files blindly.
7. Verify queue state and application behavior.
8. Record preventive actions.

## 23. Operational Evidence and Records

Maintain records for significant events, including:

* Redis outages and restarts.
* Queue backlog incidents.
* Retry storms.
* Permanently failed jobs.
* Manual job replay.
* Cache invalidation or repopulation incidents.
* Memory and capacity changes.
* Persistence or replication changes.
* Queue configuration changes.
* Duplicate-processing incidents.
* Security events.
* Recovery and reconciliation activities.

Records should identify the environment, component, time, operator, observed impact, action, result, and follow-up items.

Preserve enough information to investigate an incident without unnecessarily retaining sensitive payloads, credentials, or personal data.

## 24. Operational Readiness Checklist

### Redis service

* [ ] Redis ownership and escalation contacts are documented.
* [ ] Health checks and connectivity monitoring are configured.
* [ ] Memory usage and write failures are monitored.
* [ ] Access controls and credential handling follow the security design.
* [ ] Persistence and recovery expectations are documented where applicable.
* [ ] Eviction policy matches the actual workload.

### Queue processing

* [ ] Queue names and purposes are documented.
* [ ] Delivery and acknowledgement guarantees are understood.
* [ ] Queue depth and oldest-item age are monitored.
* [ ] Worker health and processing duration are monitored.
* [ ] Retry policies are bounded and documented.
* [ ] Permanent failures have an investigation and recovery path.
* [ ] Duplicate processing is handled safely.

### Cache behavior

* [ ] Each important cache category has a source of truth.
* [ ] TTL and invalidation policies are defined.
* [ ] Tenant and branch scope is preserved.
* [ ] Cache outages have documented fallback behavior.
* [ ] Cache stampedes and excessive source load are addressed.
* [ ] Cache data is not incorrectly treated as authoritative business state.

### Recovery and business integrity

* [ ] Queue outages have a documented recovery procedure.
* [ ] Backlog recovery is controlled and observable.
* [ ] Business-critical asynchronous work has a reliable handoff strategy.
* [ ] Offline synchronization recovery is documented.
* [ ] Order, payment, and inventory operations are protected against duplicate processing.
* [ ] Subscription lifecycle jobs have appropriate authorization and verification.
* [ ] Recovery includes business-level validation.

### Operations

* [ ] Relevant alerts and dashboards are available.
* [ ] Capacity and recovery traffic are included in planning.
* [ ] Deployment compatibility for queued payloads is assessed.
* [ ] Incident and change records are retained according to policy.
* [ ] The procedures have been reviewed against the deployed architecture.

## 25. Related Documents

| Reference                                          | Relationship                                                |
| -------------------------------------------------- | ----------------------------------------------------------- |
| `doc/14_Operations/README.md`                      | Operations documentation index                              |
| `03_Monitoring_and_Observability_Operations.md`    | Metrics, logs, traces, and service health                   |
| `04_Alerting_and_Notification_Operations.md`       | Alert severity, routing, and escalation                     |
| `05_Incident_Management.md`                        | Incident response and closure                               |
| `06_On_Call_and_Escalation_Management.md`          | Operational ownership and escalation                        |
| `07_Backup_Verification_and_Restore_Operations.md` | Backup and restoration verification                         |
| `08_Disaster_Recovery_Operations_Runbook.md`       | Broader recovery and service restoration                    |
| `09_Database_Operations.md`                        | PostgreSQL operations and database integrity                |
| `11_Backend_API_Operations.md`                     | API behavior and application dependency failures            |
| `13_Background_Worker_and_Scheduler_Operations.md` | Worker lifecycle and scheduled processing                   |
| `16_Subscription_and_Data_Lifecycle_Operations.md` | Subscription state and lifecycle jobs                       |
| `17_Security_Operations.md`                        | Redis security and security incident handling               |
| `18_Release_and_Change_Operations.md`              | Production changes and release coordination                 |
| `19_Capacity_Cost_and_Resource_Operations.md`      | Capacity and infrastructure resource planning               |
| `doc/05_Database/`                                 | Database schema and data-integrity specifications           |
| `doc/11_Security/`                                 | Security architecture and access-control requirements       |
| `doc/12_Testing/`                                  | Reliability, integration, and recovery testing requirements |

Relative paths in the table refer to the Operations directory unless a full repository path is shown.

## 26. Operational Invariants

The following rules are mandatory. Exceptions require documented authorization, risk assessment, and compensating controls where applicable.

1. Redis and queue components must have documented ownership.
2. The purpose of each Redis deployment must be documented.
3. Cache-only and business-critical queue workloads must not be treated as having equivalent durability requirements.
4. Queue delivery and acknowledgement guarantees must be understood.
5. Redis credentials must not be stored in ordinary operational documentation.
6. Network and access controls must restrict Redis to authorized clients.
7. Redis availability must be monitored.
8. Queue depth and oldest-item age must be observable for critical queues.
9. Worker health must be monitored.
10. Queue processing must produce observable success or failure outcomes.
11. Retry policies must have explicit bounds.
12. Retry delays must prevent uncontrolled retry storms.
13. Non-retryable failures must not be retried indefinitely.
14. Unknown outcomes must be investigated before unsafe retries.
15. Duplicate delivery must be considered wherever the queue implementation permits it.
16. Critical business handlers must implement suitable idempotency protections.
17. Queue message identifiers must not be assumed to provide complete business-operation deduplication.
18. PostgreSQL transactions and independent Redis writes must not be assumed atomic.
19. Critical asynchronous handoffs must use an approved reliability pattern.
20. Business-critical work must have a documented recovery strategy.
21. Permanently failed critical jobs must have an assigned owner or disposition.
22. Manual replay must include validity and duplicate-processing checks.
23. Replay must preserve required business-operation identifiers.
24. Queue clearing requires explicit authorization and impact assessment.
25. Redis-wide flush commands must not be used as routine recovery actions.
26. Cache data must have a documented source of truth.
27. Cache entries must follow defined expiration or refresh behavior.
28. Cache invalidation must preserve tenant and branch scope.
29. Cache misses must not bypass authorization checks.
30. Cache failure behavior must be documented.
31. Cache rebuilding must not create uncontrolled database load.
32. Cache and queue memory requirements must be evaluated separately.
33. Eviction policies must be compatible with the stored workload.
34. Critical queue state must not be silently discarded through cache eviction.
35. Redis memory pressure must be monitored.
36. Redis internal files and WAL data must not be deleted manually as a recovery shortcut.
37. Redis persistence and replication guarantees must be documented where configured.
38. Redis restart recovery must verify the state required by dependent services.
39. Worker recovery must account for active and unacknowledged jobs.
40. Backlog draining must consider downstream capacity.
41. Increasing worker concurrency must not overload PostgreSQL or external dependencies.
42. Scheduled jobs must have a documented catch-up or skip policy.
43. Queue payload changes must account for jobs created by older application versions.
44. Tenant and branch ownership must be validated during asynchronous processing.
45. Sensitive payloads must not be logged unnecessarily.
46. Security anomalies must follow the established security incident procedure.
47. Recovery must verify relevant business outcomes, not just service availability.
48. Operational changes must follow the approved change process.
49. Capacity and retry policies must be reviewed after material workload changes.
50. A successful command, enqueue acknowledgement, or service health check alone does not prove that the required business operation completed correctly.

## 27. Acceptance Criteria

This document is considered operationally complete when:

* Redis and queue ownership are documented.
* Health, memory, backlog, and worker monitoring are defined.
* Retry and permanently failed job handling are documented.
* Cache source-of-truth and invalidation rules are defined.
* Queue delivery and durability assumptions are explicit.
* Duplicate-processing protections are defined for critical business operations.
* Redis restart and queue recovery procedures are available.
* Tenant and branch isolation requirements are documented.
* Critical asynchronous workflows have recovery and reconciliation procedures.
* The operational readiness checklist has been reviewed against the deployed architecture.

Documenting a control does not prove that it has been implemented. Implementation evidence must be maintained in the relevant deployment, monitoring, testing, security, and operations records.

## 28. Change History

| Version | Date       | Status   | Description                                                               |
| ------- | ---------- | -------- | ------------------------------------------------------------------------- |
| 1.0     | 2026-10-09 | Accepted | Initial Redis, queue, cache, retry, and recovery operations specification |

