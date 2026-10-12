# Database Operations

**Document ID:** OPS-09
**Status:** Accepted
**Version:** 1.0
**Last Updated:** 2026-10-09
**Project:** FastFood ERP
**Repository Path:** `doc/14_Operations/09_Database_Operations.md`
**Primary Database:** PostgreSQL
**Audience:** Database Administrators, Backend Engineers, DevOps Engineers, Site Reliability Engineers, Security Engineers, and authorized incident responders.

## 1. Purpose

This document defines the operational procedures, safety controls, monitoring requirements, and recovery practices for PostgreSQL in the FastFood ERP platform.

Its objectives are to:

* Maintain database availability and predictable performance.
* Protect business data from accidental loss, corruption, and unauthorized access.
* Preserve restaurant-network, branch, and subscription boundaries.
* Detect database problems before they significantly affect restaurant operations.
* Provide safe procedures for investigating performance and availability incidents.
* Keep schema changes controlled and compatible with application releases.
* Support backup verification, restoration, and disaster recovery.
* Minimize operational overhead and avoid unnecessary infrastructure complexity.

This document defines database operational requirements. It does not prescribe an unconfirmed database topology, hosting provider, replication technology, connection-pooling product, or monitoring vendor.

## 2. Scope

This document covers:

* PostgreSQL health and availability.
* Connections and connection pools.
* Storage and capacity.
* Query performance and execution plans.
* Locks, transactions, and concurrency.
* Vacuum, analyze, indexes, and routine maintenance.
* Schema migrations and database release coordination.
* Replication and failover, where supported.
* Database access and security.
* Data integrity and tenant isolation.
* Backup verification and restoration coordination.
* Incident response and operational evidence.
* Maintenance planning and capacity reviews.

### 2.1 Out of scope

The following subjects are governed by dedicated documents:

* Backup verification and restore procedures: `07_Backup_Verification_and_Restore_Operations.md`.
* Disaster recovery execution: `08_Disaster_Recovery_Operations_Runbook.md`.
* Production release coordination: `18_Release_and_Change_Operations.md`.
* Security incident handling: `17_Security_Operations.md`.
* Monitoring architecture and dashboards: `03_Monitoring_and_Observability_Operations.md`.
* Alert routing and escalation: `04_Alerting_and_Notification_Operations.md`.
* Incident lifecycle and post-incident reviews: `05_Incident_Management.md`.
* Infrastructure deployment and environment configuration: `doc/10_Deployment/`.
* Database schema, entities, constraints, and indexing design: `doc/05_Database/`.

This document complements these references and must not replace their procedures.

## 3. Operational Principles

All database operations must follow these principles:

1. **Data integrity first.** Availability improvements must not silently corrupt, duplicate, or discard business data.
2. **Least privilege.** Operational access must be limited to the permissions required for the assigned task.
3. **Evidence before intervention.** Collect relevant diagnostics before restarting services, terminating sessions, or changing configuration when time permits.
4. **Small, reversible changes.** Prefer changes with a limited impact and a documented rollback or recovery path.
5. **No unverified recovery claims.** A successful backup job does not, by itself, prove that data can be restored.
6. **Tenant isolation is mandatory.** Database operations must preserve the separation between restaurant networks and their branches.
7. **Business continuity matters.** Database recovery must account for offline branches and pending synchronization.
8. **Architecture-aware procedures.** Execute replication, failover, or cluster procedures only when the deployed architecture supports them.
9. **Measured performance.** Use actual workload and resource metrics instead of assumptions.
10. **Controlled production access.** Production changes must be authorized, recorded, and reviewed.

## 4. Roles and Responsibilities

| Role                                                      | Responsibilities                                                                                                       |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Database Administrator (DBA) or designated database owner | Database health, maintenance, query analysis, access management, and operational readiness                             |
| Backend Engineer                                          | Application queries, transaction behavior, connection usage, and ORM-related issues                                    |
| DevOps / SRE                                              | Infrastructure resources, service availability, database connectivity, monitoring, and supported failover coordination |
| Security Engineer                                         | Database security controls, access reviews, audit requirements, and security incident support                          |
| Incident Commander                                        | Coordinates major incidents, assigns responsibilities, and manages incident communication                              |
| Product / Business Owner                                  | Confirms business impact and validates critical workflows when required                                                |
| Release Owner                                             | Coordinates schema changes with application releases                                                                   |
| Authorized Approver                                       | Approves high-risk production operations according to the organization's change policy                                 |

One person may hold multiple roles in a small team. High-risk actions must still follow the applicable approval and separation-of-duties requirements.

## 5. Database Environment Inventory

Maintain an inventory of every PostgreSQL environment, including production, staging, testing, and recovery environments.

Record at least:

* Environment identifier.
* Environment purpose and criticality.
* PostgreSQL major and minor version.
* Hosting environment and deployment method.
* Database endpoint or approved connection reference.
* Database owner and operational contacts.
* Application services that depend on the database.
* Database names and their purposes.
* Storage allocation and growth limits, where applicable.
* Connection and pooling configuration.
* Backup policy and the reference to its verification procedure.
* Recovery objectives and dependencies.
* Replication topology, if configured.
* Monitoring and alert references.
* Access-management process.
* Maintenance and upgrade policy.

Credentials, passwords, private keys, and connection strings containing secrets must not be stored in this inventory.

The inventory must reflect the actual deployed architecture. Unknown or unverified configuration must be marked as such rather than assumed.

## 6. Routine Operating Schedule

The following schedule is a baseline. Exact frequencies must be adjusted to the production workload, service criticality, and monitoring capabilities.

| Frequency              | Required operational activity                                                                                        |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Daily                  | Review database availability, critical alerts, connection saturation, storage capacity, errors, and abnormal latency |
| Daily                  | Check backup-job outcomes and investigate failures according to OPS-07                                               |
| Daily                  | Review unresolved database-related incidents and significant replication lag, where applicable                       |
| Weekly                 | Review capacity trends, long-running queries, blocked sessions, and repeated database errors                         |
| Weekly                 | Review failed maintenance tasks and unusual growth in tables, indexes, or temporary files                            |
| Monthly                | Review database access and privileged accounts                                                                       |
| Monthly                | Evaluate slow-query trends, connection-pool settings, and resource utilization                                       |
| Monthly                | Review supported PostgreSQL updates and security advisories                                                          |
| According to policy    | Perform restore drills, recovery exercises, and replication/failover tests where supported                           |
| Before a major release | Verify migration safety, database compatibility, capacity assumptions, and rollback or roll-forward procedures       |
| After a major incident | Review root cause, corrective actions, and database operational controls                                             |

Automated monitoring should handle continuous checks wherever practical. Manual checks supplement monitoring rather than replace it.

## 7. Database Health and Availability

### 7.1 Health signals

Monitor the following signals when they are available in the deployed environment:

* Database reachability.
* Successful authenticated connections.
* Connection establishment failures.
* Query success and error rates.
* Query latency, including tail latency.
* Active, idle, and waiting connections.
* Connection pool utilization and queueing.
* CPU and memory utilization on the database host or managed database.
* Storage utilization, available space, and growth rate.
* Database and index size trends.
* Transaction throughput.
* Lock waits and deadlocks.
* Long-running transactions.
* Checkpoint activity and write pressure.
* Temporary-file activity.
* Autovacuum and analyze activity.
* Replication health and lag, where applicable.
* Backup and restore verification status.
* PostgreSQL restarts, crashes, and recovery events.

Metrics must be interpreted together. A rise in query latency, for example, can result from resource pressure, lock contention, connection exhaustion, a query-plan change, or an application-side bottleneck.

### 7.2 Health checks

Use distinct health checks for distinct purposes:

* **Connectivity check:** Can the application establish an authenticated connection?
* **Readiness check:** Can the database perform the minimum required operations for the service to accept traffic?
* **Performance check:** Are latency and resource utilization within the approved operating range?
* **Recovery check:** Has the database completed recovery and passed required consistency checks after an interruption?

A simple successful connection does not prove that the database can support the production workload.

Health checks must be lightweight, bounded by timeouts, and designed not to add significant load during an incident.

### 7.3 Availability incident triggers

Investigate promptly when any of the following occurs:

* The database becomes unreachable.
* Authentication or connection establishment begins failing broadly.
* Application requests fail because of database errors.
* Connection usage approaches its configured limit.
* Available storage approaches a critical threshold.
* Query latency rises materially above the established baseline.
* Database processes repeatedly restart or crash.
* Replication falls behind the accepted recovery or consistency requirements.
* Critical writes fail or transaction integrity is uncertain.

Use established alert thresholds and severity definitions from OPS-03 and OPS-04. Do not invent a new severity system for database incidents.

## 8. Connection and Pool Management

### 8.1 Connection model

The total number of connections must be planned across all application instances and operational clients.

Consider:

* API server instances.
* Background workers.
* Scheduled jobs.
* Administrative sessions.
* Monitoring and health checks.
* Migration processes.
* Maintenance tools.
* Replication and other internal connections, where applicable.
* Reserved connections required for recovery or administration.

Do not size the database connection limit based only on one application process.

Where connection pooling is used, document whether pooling occurs in the application, in an external pooler, or at another supported layer.

### 8.2 Connection saturation investigation

When connections approach their configured limit:

1. Confirm the current connection count and configured limit.
2. Identify connection states and the associated database roles and applications.
3. Check whether connections are active, idle, idle in transaction, or waiting on locks.
4. Compare current counts with normal traffic and deployment activity.
5. Check for connection leaks, excessive pool sizes, or newly increased application replicas.
6. Identify long-running transactions and abandoned sessions.
7. Determine whether a safe temporary capacity adjustment is possible.
8. Apply a targeted correction and monitor its effect.

Do not automatically increase the connection limit without checking memory, CPU, workload, and connection-pool behavior.

### 8.3 Connection-pool safeguards

* Set explicit connection and acquisition timeouts.
* Ensure application code returns connections to the pool.
* Avoid opening a new database connection for every small operation when a managed pool is appropriate.
* Keep transaction durations short.
* Avoid idle transactions.
* Size pools based on measured workload and total service concurrency.
* Avoid retry loops that continuously create new connections during an outage.
* Use bounded retries with backoff where retrying is safe.
* Reserve administrative access according to the database platform's capabilities.
* Reassess pool sizing after changes to worker counts, API replicas, or background concurrency.

Connection limits must be consistent with the total connection budget and the database's available resources.

## 9. Storage and Capacity Management

### 9.1 Storage monitoring

Monitor:

* Total allocated storage.
* Free storage and utilization percentage.
* Growth rate over time.
* Database, table, and index sizes.
* WAL generation and retention behavior.
* Temporary-file growth.
* Backup storage requirements.
* Storage growth caused by failed or delayed maintenance.
* Replication-slot retention, if replication slots are used.
* Available headroom for migrations, index operations, and recovery.

Where relevant, distinguish database data storage from WAL storage, backup storage, and temporary storage.

### 9.2 Capacity planning

Capacity planning must account for:

* Active restaurant networks and branches.
* Order and payment transaction volumes.
* Inventory and recipe activity.
* Cash-register and cashier reports.
* Audit and operational records.
* Subscription and data-lifecycle operations.
* Offline synchronization batches.
* Concurrent reporting queries.
* Index and table growth.
* Retention requirements.
* Expected growth in application and worker instances.

Do not assume that the number of restaurant branches alone predicts database capacity. Workload intensity, data retention, query patterns, and reporting activity also matter.

### 9.3 Low-storage response

When storage reaches a warning or critical threshold:

1. Confirm the affected storage resource and the current growth rate.
2. Determine whether the pressure comes from database files, WAL, temporary files, logs, backups, or another source.
3. Check for stalled replication, long-running transactions, maintenance issues, and abnormal data growth.
4. Estimate the time remaining before storage exhaustion.
5. Notify the responsible database and infrastructure operators.
6. Apply an approved capacity increase or a safe, targeted remediation.
7. Verify database health and application write behavior after the change.
8. Record the cause and any required preventive action.

Never delete database files, WAL segments, or internal PostgreSQL files manually to free space.

Do not remove business records merely to recover disk space. Any approved data-retention or deletion task must follow the relevant business and data-lifecycle policy.

## 10. Query Performance and Diagnostics

### 10.1 Baseline

Maintain a performance baseline for important workload categories:

* Order creation and updates.
* Payment and order closure.
* Inventory deductions and stock validation.
* Recipe and menu retrieval.
* Cash-register opening and closing.
* Reports and dashboard queries.
* Offline synchronization.
* Subscription enforcement and lifecycle jobs.

Measure performance under representative traffic and record the expected operating ranges. Exact latency targets must be defined in the relevant service-level requirements rather than invented in this document.

### 10.2 Slow-query investigation

When query latency increases:

1. Establish which endpoints, jobs, or business workflows are affected.
2. Determine whether the slowdown is isolated or widespread.
3. Inspect query duration, frequency, execution count, and error rate.
4. Check lock waits, transaction duration, connection saturation, and database resource pressure.
5. Compare the current workload and query plan with the known baseline, if available.
6. Inspect the query and relevant schema/index definitions.
7. Use `EXPLAIN` to examine the estimated execution plan.
8. Use `EXPLAIN (ANALYZE, BUFFERS)` only when its execution cost and side effects are understood and the query is safe to execute in the selected environment.
9. Test proposed changes with representative data and workload.
10. Deploy the change through the approved release process.
11. Compare before-and-after results and verify business correctness.

`EXPLAIN ANALYZE` executes the statement. It must not be run casually against a production statement that modifies data or has other consequential side effects.

### 10.3 Query optimization principles

Prefer changes that:

* Reduce unnecessary rows scanned or returned.
* Use appropriate predicates and joins.
* Avoid repeated queries inside loops.
* Avoid fetching unused columns.
* Support common access patterns with appropriate indexes.
* Use pagination or bounded result sets for large lists.
* Separate operational workflows from expensive reporting where necessary.
* Avoid unbounded queries on large datasets.
* Preserve tenant and branch filters.
* Keep transaction scopes appropriately short.

Do not add indexes indiscriminately. Indexes consume storage and increase write and maintenance costs. Evaluate the expected read benefit against these costs.

### 10.4 Production query safety

Before running diagnostic or administrative queries in production:

* Confirm the target environment and database.
* Use a read-only account when write access is unnecessary.
* Apply statement timeouts where appropriate.
* Limit result sizes.
* Avoid full-table scans on large tables unless justified.
* Avoid collecting sensitive row-level data unnecessarily.
* Record the purpose of high-impact diagnostics.
* Do not expose credentials, personal information, or payment-related secrets in diagnostic output.

## 11. Locks, Transactions, and Deadlocks

### 11.1 Operational risks

Lock contention can affect order processing, inventory deductions, register closure, payroll operations, and synchronization jobs.

Investigate:

* Long-running transactions.
* Sessions waiting on locks.
* Deadlocks.
* Idle-in-transaction sessions.
* Transactions that update overlapping inventory or financial records.
* Jobs that hold locks while performing unrelated network operations.
* Large batch operations that create excessive contention.

### 11.2 Lock investigation procedure

1. Identify the affected business operation and its observed impact.
2. Find the blocked sessions and, where possible, the blocking session.
3. Determine the transaction age, application name, database role, and relevant query context.
4. Check whether the blocking transaction is performing valid work or has become abandoned.
5. Assess the consequences of allowing it to continue versus terminating it.
6. Contact the responsible service owner when appropriate.
7. Terminate a session only when authorized and when the consequences are understood.
8. Verify that the application handles transaction rollback and retry safely.
9. Confirm that affected business records remain consistent.
10. Record the cause and preventive actions.

### 11.3 Transaction safeguards

* Keep transactions short.
* Do not hold database locks while waiting for external APIs or user input.
* Use consistent lock ordering in operations that update shared records.
* Apply appropriate constraints and transaction isolation.
* Make retries safe for the operation being retried.
* Avoid retrying transactions indefinitely.
* Use idempotency mechanisms for business operations that may be submitted more than once.
* Verify stock, payment, order, and cash-register consistency after interrupted transactions.

A canceled query or terminated session does not automatically mean that the underlying business operation is complete or safe to retry.

## 12. Vacuum, Analyze, and Index Maintenance

PostgreSQL relies on routine maintenance to manage obsolete row versions and maintain planner statistics.

### 12.1 Autovacuum and analyze

* Keep autovacuum enabled unless a documented, approved exception exists.
* Monitor autovacuum progress and failures.
* Monitor dead-tuple accumulation and table growth.
* Check whether long-running transactions prevent cleanup.
* Review analyze activity and statistics freshness for important tables.
* Investigate tables where dead tuples accumulate faster than maintenance removes them.
* Adjust maintenance settings only after workload analysis and controlled testing.

Routine manual vacuuming should not replace healthy autovacuum behavior.

### 12.2 Maintenance selection

Use targeted maintenance when evidence indicates that it is necessary.

Before starting maintenance, assess:

* Table size and write activity.
* Current workload.
* Locking behavior of the selected operation.
* Available storage and temporary space.
* Expected duration.
* Whether the operation can be interrupted safely.
* Whether it requires special privileges.
* Whether it affects latency or write availability.

Do not assume every maintenance command has the same locking or availability characteristics.

### 12.3 Index maintenance

Investigate indexes that are:

* Associated with repeatedly slow queries.
* Suspected of being unused.
* Growing unexpectedly.
* Causing significant write overhead.
* Invalid or incomplete after a failed index operation.
* Duplicated or overlapping with other indexes.

Do not drop an index based only on a short period of low usage. Consider seasonal and infrequent reporting queries, constraints, and the full application workload.

Use concurrent index operations only when supported by the applicable PostgreSQL version and compatible with the required operational procedure. Understand their failure handling, resource cost, and transaction restrictions.

### 12.4 Reindexing

Reindexing must be justified by evidence and performed using an approved plan.

Before reindexing:

1. Identify the affected index and the reason for the operation.
2. Review table size, storage headroom, and write activity.
3. Check the locking and availability behavior of the selected method.
4. Select a maintenance window if the impact warrants it.
5. Confirm monitoring and recovery readiness.
6. Verify index validity and query behavior afterward.

Reindexing is not a universal solution for slow queries.

## 13. Schema Migrations and Database Releases

Database schema changes must be coordinated with the application release process described in `doc/10_Deployment/` and `18_Release_and_Change_Operations.md`.

### 13.1 Migration requirements

Each production migration must have:

* A unique, traceable identifier.
* A description of the intended schema or data change.
* A documented dependency on application versions.
* An assessment of locking and table-rewrite risk.
* An estimate of execution time and resource impact where feasible.
* A data-integrity assessment.
* A rollback, roll-forward, or recovery strategy.
* Verification queries or tests.
* An execution owner and approval according to the change policy.
* A record of the result.

### 13.2 Expand-and-contract strategy

For changes requiring compatibility between application versions, prefer a staged approach when appropriate:

1. **Expand:** Add compatible schema elements without immediately removing existing ones.
2. **Deploy compatibility:** Release application code that can work with the transition schema.
3. **Migrate data:** Perform necessary backfills or transformations in controlled batches.
4. **Verify:** Confirm data correctness and application compatibility.
5. **Contract:** Remove obsolete schema elements only after all dependent code and processes no longer require them.

The exact sequence depends on the change. Not every migration needs every stage.

### 13.3 High-risk migrations

Additional review is required for migrations that:

* Rewrite large tables.
* Create or rebuild large indexes.
* Change column types or nullability.
* Modify primary keys or foreign keys.
* Change tenant or branch ownership relationships.
* Transform financial, inventory, or order data.
* Remove columns or tables.
* Change transaction or uniqueness behavior.
* Require long-running locks.
* Affect offline synchronization compatibility.

Test the migration with representative data and workload before production execution.

### 13.4 Migration failure

If a migration fails:

1. Stop further dependent release steps.
2. Determine whether the migration partially applied.
3. Inspect the actual database state rather than assuming automatic rollback.
4. Assess application compatibility with the resulting schema.
5. Prevent incompatible application traffic where necessary.
6. Execute the documented recovery, repair, or roll-forward procedure.
7. Verify schema and data integrity.
8. Resume release activity only after the responsible owner approves.

Never mark a migration as successful merely because the deployment process continued.

## 14. Replication and Failover

This section applies only if the deployed PostgreSQL architecture uses replication or automated failover.

### 14.1 Replication monitoring

Monitor the relevant signals supported by the topology, including:

* Replication connection state.
* Replay or apply progress.
* Replication lag.
* WAL generation and retention.
* Replication-slot health, where applicable.
* Standby availability.
* Recovery status.
* Storage pressure caused by delayed replication.
* Failover automation health, if configured.

Define acceptable lag according to the service's consistency requirements and recovery objectives. Do not assume that replication is synchronous or that a replica always contains every acknowledged write.

### 14.2 Replication incident procedure

1. Confirm the affected primary or standby and its current role.
2. Check connectivity and replication status.
3. Determine whether replication is delayed, disconnected, or unable to replay changes.
4. Check storage, WAL retention, resource pressure, and recent configuration changes.
5. Assess potential data-loss and availability implications.
6. Apply the topology-specific recovery procedure.
7. Confirm replication is progressing and within the accepted operating range.
8. Record any period during which the recovery point or consistency guarantees were uncertain.

Do not manually delete WAL files or replication-slot data to clear storage pressure.

### 14.3 Failover safeguards

Before promoting a standby or changing database authority:

* Confirm the actual primary and standby states.
* Establish whether the original primary can still accept writes.
* Follow the approved failover procedure.
* Prevent split-brain and conflicting authoritative writers.
* Confirm the recovery point and potential data loss.
* Validate database consistency and application connectivity.
* Coordinate with API services, workers, schedulers, and synchronization processes.
* Record the decision, approver, timestamps, and validation results.

A replica must not be promoted solely because it responds to a health check.

Use OPS-08 for disaster recovery that requires a broader environment recovery or traffic cutover.

## 15. Database Security and Access Control

### 15.1 Access principles

* Use separate identities for application runtime, migrations, monitoring, backup operations, and human administration where supported.
* Grant only the privileges required for each identity.
* Avoid using a PostgreSQL superuser for normal application requests.
* Restrict privileged access to authorized operators.
* Use approved secret-management mechanisms.
* Rotate credentials according to the security policy and incident requirements.
* Remove or disable access when it is no longer required.
* Review database roles and grants regularly.
* Protect administrative connectivity using the environment's approved network and authentication controls.
* Use encrypted connections where supported and required by the deployment security design.

### 15.2 Access reviews

For each review, verify:

* Account ownership and purpose.
* Whether the account remains active and necessary.
* Assigned roles and inherited privileges.
* Database and schema permissions.
* Access to sensitive business records.
* Privileges that permit bypassing application-level safeguards.
* Service accounts with unnecessary interactive access.
* Unused or expired accounts.
* Changes since the previous review.

Record findings and remediation.

### 15.3 Audit and evidence

Maintain operational records for privileged database changes, access grants, migration execution, recovery actions, and other high-risk interventions.

Logs must be protected from unauthorized access and tampering. Avoid logging credentials, session tokens, or unnecessary personal and financial data.

The specific PostgreSQL audit extensions, managed-service audit facilities, or external logging tools must be selected according to the deployed architecture and security requirements.

## 16. Tenant and Branch Data Integrity

FastFood ERP serves multiple restaurant networks, each of which may contain multiple branches. Database operations must preserve this isolation.

### 16.1 Isolation controls

* Keep tenant and branch ownership relationships explicit in the schema.
* Preserve relevant foreign-key and uniqueness constraints.
* Use the approved application authorization and data-access model.
* Ensure administrative queries are scoped to the intended tenant or environment.
* Avoid bulk operations without a verified selection criterion.
* Use tenant-aware data migrations.
* Review cross-tenant and cross-branch access behavior when schema or query logic changes.
* Preserve the distinction between global configuration and tenant-owned data.
* Verify branch-level overrides and ownership relationships after migrations.
* Treat backups, exports, logs, and diagnostic samples as potentially sensitive.

Where row-level security is part of the architecture, verify its policies, role behavior, and interaction with connection pooling. Row-level security must not be assumed to exist unless implemented and tested.

### 16.2 Bulk data operations

Before a bulk update, delete, backfill, or import:

1. Confirm the target environment.
2. Identify the exact tenant, branch, or global data scope.
3. Run a read-only preview using the intended selection criteria.
4. Estimate the number of affected records.
5. Check relevant constraints and foreign-key dependencies.
6. Determine whether batching is necessary.
7. Confirm the recovery strategy and approval.
8. Execute using the approved mechanism.
9. Validate affected row counts and business invariants.
10. Record the result.

A tenant or branch identifier must never be omitted from a tenant-scoped operation merely to simplify a query.

### 16.3 Financial and inventory consistency

Special care is required for:

* Order and payment records.
* Cash-register opening, closing, and handover records.
* Refunds and corrections.
* Inventory movements and stock balances.
* Recipe-driven ingredient deductions.
* Employee payroll and salary records.
* Subscription state and data-lifecycle events.
* Offline operations awaiting synchronization.

After an interrupted or repaired operation, validate both database-level integrity and the relevant business outcome.

Do not directly edit production financial or inventory rows to make reports appear correct. Use approved correction workflows and preserve an auditable history.

## 17. Data Integrity Checks

Database-level constraints are the first line of defense for enforcing structural rules. Business-level checks complement them.

### 17.1 Required controls

Where appropriate to the schema, verify:

* Primary-key uniqueness.
* Foreign-key validity.
* Required fields and valid state transitions.
* Uniqueness of business identifiers.
* Tenant and branch ownership consistency.
* Referential integrity for archived records.
* Valid monetary and quantity values.
* Consistency between order state and payment state.
* Consistency of inventory movements and derived balances.
* Idempotency of synchronization and retry operations.
* Migration and backfill completeness.

### 17.2 Investigating anomalies

When a data-integrity anomaly is detected:

1. Preserve the relevant evidence.
2. Identify the affected entities and business scope.
3. Determine whether the anomaly is isolated or systematic.
4. Check application errors, recent releases, failed jobs, and retry behavior.
5. Avoid making unverified manual changes.
6. Engage the responsible domain owner.
7. Apply an approved repair with a traceable record.
8. Validate the correction and dependent reports.
9. Determine whether the anomaly requires incident management and a post-incident review.

A successful SQL statement is not sufficient evidence that the business operation produced the intended result.

## 18. Backup and Restore Coordination

Database backup operations are governed by `07_Backup_Verification_and_Restore_Operations.md`.

Database operators must:

* Confirm that the active backup policy matches the production database.
* Review backup failures and incomplete jobs.
* Monitor storage and retention for backup artifacts.
* Ensure that backup credentials and artifacts are protected.
* Verify that required databases, schema objects, and relevant configuration are included.
* Coordinate recovery tests with application and business owners.
* Confirm that restored data is compatible with the intended application version.
* Record the recovery point and the validation results.

### 18.1 Backup-related incident

If a backup is missing, corrupted, delayed, or otherwise untrusted:

1. Determine which recovery points remain available.
2. Assess the potential impact on recovery objectives.
3. Notify the database owner and incident coordinator when required.
4. Preserve any remaining valid backup artifacts.
5. Restore backup coverage as soon as safely possible.
6. Execute the relevant verification procedure.
7. Record the gap and preventive actions.

Do not claim that recovery objectives are satisfied until the available evidence supports that conclusion.

### 18.2 Production restore

Production restoration requires the applicable authorization and documented recovery plan. Use OPS-07 for restore verification and OPS-08 for disaster recovery execution when the incident meets those procedures' scope.

Never restore a backup over the active production database without confirming the target, authority, data-loss implications, and recovery plan.

## 19. Database Incident Response

Database incidents follow the general incident lifecycle in `05_Incident_Management.md`.

### 19.1 Initial response checklist

* [ ] Confirm the affected environment and database.
* [ ] Identify the affected services and business workflows.
* [ ] Check database availability and connection failures.
* [ ] Review relevant metrics and recent logs.
* [ ] Check connection saturation, storage, locks, and long-running transactions.
* [ ] Review recent deployments, migrations, configuration changes, and infrastructure events.
* [ ] Determine whether data integrity or security may be affected.
* [ ] Assign an owner and communicate the impact.
* [ ] Preserve relevant diagnostic evidence.
* [ ] Choose a mitigation that limits further impact and protects data.

### 19.2 Common incident scenarios

**Database unavailable**

Verify the database service state, network connectivity, authentication, resource exhaustion, and provider or host status. Use the approved restart or recovery procedure only after assessing its implications.

**Connection exhaustion**

Identify the source of excessive connections, reduce uncontrolled connection creation, and correct the pool or application behavior. Avoid blindly increasing connection limits.

**High query latency**

Determine whether the issue is resource pressure, lock contention, query-plan regression, excessive reporting, or another workload change. Apply a targeted mitigation.

**Storage exhaustion**

Identify the growing resource and restore safe storage headroom using an approved action. Never remove internal PostgreSQL files manually.

**Deadlock or blocking**

Identify the blocking transactions, evaluate business impact, and terminate sessions only when authorized and justified.

**Migration failure**

Determine the actual schema state and application compatibility before deciding whether to repair, roll forward, or roll back.

**Suspected data corruption**

Preserve evidence, limit further risky writes if appropriate, and coordinate integrity verification and recovery with the authorized incident team.

**Unexpected cross-tenant access**

Treat potential tenant-isolation violations as security incidents. Follow OPS-17 and the security incident procedure; do not treat them as ordinary query bugs.

**Replication failure**

Determine whether the issue affects availability, durability, or recovery objectives. Follow the topology-specific procedure and prevent conflicting writes.

### 19.3 Recovery verification

Before declaring recovery complete, verify:

* Database connectivity and readiness.
* Stable connection usage and acceptable latency.
* Successful critical read and write operations.
* No unresolved critical database errors.
* Required replication health, where applicable.
* No unexpected schema or migration state.
* Data integrity for affected workflows.
* Order, payment, inventory, and cash-register consistency where relevant.
* Application and worker compatibility.
* Monitoring and alert delivery.

Follow the incident closure and review requirements in OPS-05.

## 20. Maintenance Windows and Operational Changes

Schedule database maintenance according to risk, workload, and business impact.

A maintenance plan must state:

* Purpose and scope.
* Target environment.
* Responsible operator and approver.
* Expected impact and affected workflows.
* Preconditions and required health checks.
* Execution steps.
* Expected duration and resource requirements.
* Monitoring plan.
* Abort criteria.
* Rollback, recovery, or roll-forward approach.
* Post-maintenance verification.
* Communication and evidence requirements.

Do not assume that a command is non-disruptive simply because PostgreSQL permits it while the database is running.

For maintenance that may affect order intake, payments, stock deductions, register operations, or synchronization, coordinate timing and contingency procedures with the business and application owners.

## 21. PostgreSQL Upgrades and Patching

PostgreSQL version upgrades and patching must follow the approved change and release procedures.

Before an upgrade:

1. Identify the current version and target version.
2. Review the relevant PostgreSQL release notes and compatibility requirements.
3. Assess extension, driver, ORM, and application compatibility.
4. Review changes to SQL behavior, configuration, and query plans.
5. Test migration or upgrade steps in a representative environment.
6. Verify backup and recovery readiness.
7. Estimate the downtime or reduced-capacity risk.
8. Define the cutover and recovery strategy.
9. Confirm that the team can monitor and validate the upgraded system.

After the upgrade:

* Verify PostgreSQL readiness and application connectivity.
* Check logs for errors and warnings.
* Validate critical business workflows.
* Review query performance and execution-plan changes.
* Confirm maintenance and statistics behavior.
* Verify backup execution and monitoring.
* Record the final version and operational outcome.

Do not treat a successful database startup as proof that the upgrade is complete.

## 22. Configuration Management

Database configuration changes must be controlled, documented, and based on measured requirements.

Examples include:

* Connection limits.
* Memory-related settings.
* Statement and transaction timeouts.
* Logging settings.
* Autovacuum and analyze settings.
* Checkpoint and WAL settings.
* Replication settings, where applicable.
* Authentication and connection-security settings.

Before changing a setting:

1. Determine its current value and source.
2. Understand whether it requires a reload or restart.
3. Assess memory, CPU, storage, locking, and availability implications.
4. Check interactions with connection pools and application behavior.
5. Test in a suitable environment where feasible.
6. Apply through the approved configuration-management process.
7. Verify the effective value.
8. Monitor for regressions.
9. Document the change and its outcome.

Do not apply copied tuning configurations without validating them against the actual PostgreSQL version, available resources, and workload.

## 23. Operational Evidence and Records

Maintain records for significant database operations, including:

* Incident diagnostics and timeline.
* Migration identifiers and results.
* Configuration changes.
* Access grants and revocations.
* Maintenance execution.
* Replication and failover actions, where applicable.
* Restore and recovery validation.
* Data-integrity investigations.
* Capacity changes.
* PostgreSQL upgrades.
* Approved emergency interventions.

Each record should identify the environment, action, operator, timestamp, reason, outcome, and follow-up actions as appropriate.

Evidence must be stored in the approved operational system. Protect it from unauthorized access and avoid retaining sensitive diagnostic data beyond the approved retention period.

## 24. Operational Readiness Checklist

Use this checklist during a new database deployment, major architecture change, or formal readiness review.

### Availability and monitoring

* [ ] Database ownership and escalation contacts are documented.
* [ ] Connectivity and readiness checks are configured.
* [ ] Critical database metrics are monitored.
* [ ] Connection, storage, latency, and error alerts are configured.
* [ ] Relevant dashboards and diagnostic procedures are available.

### Security and access

* [ ] Application and administrative roles follow least privilege.
* [ ] Credentials are managed through approved mechanisms.
* [ ] Network access and encrypted connectivity follow the security design.
* [ ] Access reviews and audit requirements are documented.
* [ ] Tenant and branch isolation controls are tested.

### Performance and maintenance

* [ ] Connection budgets are documented.
* [ ] Capacity and storage trends are reviewed.
* [ ] Autovacuum and analyze behavior are monitored.
* [ ] Important query patterns have suitable performance checks.
* [ ] Long-running transactions and lock contention can be investigated.

### Recovery and change management

* [ ] Backup policies are documented and monitored.
* [ ] Restore verification follows OPS-07.
* [ ] Disaster recovery follows OPS-08.
* [ ] Database migrations are controlled and traceable.
* [ ] PostgreSQL upgrades have a compatibility and recovery plan.

### Business integrity

* [ ] Order and payment consistency checks are defined.
* [ ] Inventory integrity checks are defined.
* [ ] Offline synchronization recovery is documented.
* [ ] Subscription and data-lifecycle operations are controlled.
* [ ] Database incidents include business-level recovery verification.

## 25. Related Documents

| Reference                                          | Relationship                                             |
| -------------------------------------------------- | -------------------------------------------------------- |
| `doc/14_Operations/README.md`                      | Operations documentation index                           |
| `03_Monitoring_and_Observability_Operations.md`    | Database metrics, logs, and dashboards                   |
| `04_Alerting_and_Notification_Operations.md`       | Alert severity, routing, and escalation                  |
| `05_Incident_Management.md`                        | Incident declaration, response, and closure              |
| `06_On_Call_and_Escalation_Management.md`          | Responsible operators and escalation paths               |
| `07_Backup_Verification_and_Restore_Operations.md` | Backup verification and restoration                      |
| `08_Disaster_Recovery_Operations_Runbook.md`       | Environment recovery and database failover coordination  |
| `10_Redis_Queue_and_Cache_Operations.md`           | Related queue and cache dependencies                     |
| `11_Backend_API_Operations.md`                     | Application-to-database behavior and API troubleshooting |
| `13_Background_Worker_and_Scheduler_Operations.md` | Database workload generated by background jobs           |
| `16_Subscription_and_Data_Lifecycle_Operations.md` | Subscription state and authorized data-lifecycle changes |
| `17_Security_Operations.md`                        | Security incidents and operational hardening             |
| `18_Release_and_Change_Operations.md`              | Database migrations and production change coordination   |
| `19_Capacity_Cost_and_Resource_Operations.md`      | Capacity planning and infrastructure utilization         |
| `doc/05_Database/`                                 | Database schema and data-model specifications            |
| `doc/10_Deployment/`                               | Infrastructure deployment and environment configuration  |
| `doc/11_Security/`                                 | Security architecture and access-control requirements    |
| `doc/12_Testing/`                                  | Database and application verification requirements       |

Relative paths in this table refer to the Operations directory unless a full repository path is shown.

## 26. Operational Invariants

The following invariants are mandatory. An exception requires documented authorization, a risk assessment, and an explicit compensating control where applicable.

1. Production database operations must target a verified environment.
2. Database ownership and escalation responsibilities must be defined.
3. Application services must not use PostgreSQL superuser credentials for normal operations.
4. Access must follow least-privilege principles.
5. Credentials must not be stored in operational documentation or ordinary logs.
6. Database availability must be monitored.
7. Critical connection failures must be detectable.
8. Connection budgets must account for all application and operational clients.
9. Connection pools must use bounded timeouts.
10. Connection limits must not be increased without resource and workload assessment.
11. Long-running transactions must be investigated.
12. Idle-in-transaction sessions must not be ignored.
13. Lock termination requires an assessment of its consequences.
14. Query retries must be bounded.
15. Business operations must not be retried blindly after uncertain outcomes.
16. Query optimization must preserve business semantics.
17. Production diagnostics must not introduce uncontrolled load.
18. `EXPLAIN ANALYZE` must be treated as query execution.
19. Index creation must account for storage, write overhead, and availability.
20. Index removal must be justified by evidence and dependency analysis.
21. Autovacuum must remain enabled unless an approved exception exists.
22. Maintenance changes must be based on observed database behavior.
23. Storage growth must be monitored.
24. PostgreSQL internal files must never be manually deleted to free storage.
25. WAL and replication-slot data must not be removed blindly.
26. Production migrations must be traceable.
27. High-risk migrations must have a documented execution and recovery strategy.
28. Migration success must be verified against the actual database state.
29. Application and database schema versions must remain compatible.
30. Replication and failover procedures must match the deployed topology.
31. A replica must not be promoted without an approved authority decision.
32. Conflicting authoritative writers must be prevented.
33. Backup success must not be confused with verified restorability.
34. Production restoration must follow an approved recovery plan.
35. Tenant boundaries must be preserved during reads, writes, migrations, and maintenance.
36. Branch ownership relationships must remain valid.
37. Bulk data operations must have a verified scope and impact assessment.
38. Financial records must not be silently altered to correct reports.
39. Inventory corrections must preserve traceability and business integrity.
40. Offline synchronization must be reconciled before recovery is considered complete when relevant.
41. Security-related database anomalies must follow the security incident procedure.
42. Privileged changes must be recorded.
43. Diagnostic evidence must be protected from unauthorized access.
44. Configuration changes must be verified after application.
45. PostgreSQL upgrades must include compatibility validation.
46. Database recovery must be verified at both technical and business levels.
47. Critical database incidents must follow the established incident-management process.
48. Database capacity decisions must be supported by workload and growth evidence.
49. Operational procedures must be reviewed after material architecture or workload changes.
50. No database operation may be declared successful solely because its command or automation returned a success status; required data-integrity and business validations must also pass.

## 27. Acceptance Criteria

This document is considered operationally complete when:

* PostgreSQL ownership and operational responsibilities are documented.
* Health, connection, performance, and storage monitoring requirements are implemented or tracked as explicit deployment actions.
* Connection and capacity-management procedures are available.
* Query, lock, and maintenance investigations have safe procedures.
* Schema migration and upgrade activities are coordinated with release management.
* Database security and tenant-isolation requirements are documented.
* Backup, restore, and disaster recovery procedures are cross-referenced.
* Incident response includes data-integrity and business-workflow validation.
* Operational records are retained through the approved process.
* The database operational readiness checklist has been reviewed for the deployed architecture.

Implementation evidence must be maintained in the relevant deployment, monitoring, security, testing, or operations records. Documenting a control does not, by itself, prove that the control has been implemented.

## 28. Change History

| Version | Date       | Status   | Description                               |
| ------- | ---------- | -------- | ----------------------------------------- |
| 1.0     | 2026-10-09 | Accepted | Initial database operations specification |

