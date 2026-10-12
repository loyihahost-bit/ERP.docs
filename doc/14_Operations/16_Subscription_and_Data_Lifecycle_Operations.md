# Subscription and Data Lifecycle Operations

**Document ID:** OPS-16
**Status:** Accepted
**Version:** 1.0
**Last Updated:** 2026-10-09
**Category:** Operations
**Audience:** Operations Engineers, Backend Engineers, Database Administrators, Security Engineers, Support Engineers, Product Owners

## 1. Purpose

This document defines the operational procedures and safeguards for subscription expiry, restricted application access, data retention, deletion eligibility, background deletion jobs, and lifecycle recovery.

Its primary objectives are to:

* Enforce subscription restrictions consistently.
* Preserve customer data during temporary subscription interruptions.
* Prevent unauthorized access to restricted functionality.
* Ensure deletion occurs only when explicitly permitted by lifecycle policy.
* Protect against accidental deletion caused by stale jobs, duplicate events, race conditions, or incorrect subscription state.
* Provide reliable audit evidence for lifecycle transitions and destructive operations.
* Keep lifecycle processing isolated across restaurant networks and branches.

This document defines operational requirements, not a specific implementation framework or database schema.

## 2. Scope

This document covers:

* Subscription status monitoring.
* Subscription expiry detection.
* Transition to `READ_ONLY`.
* Reactivation and restoration of normal access.
* Data-retention periods and deletion eligibility.
* Deletion scheduling and background execution.
* Cancellation of pending deletion.
* Deletion verification and evidence.
* Lifecycle monitoring, alerts, incidents, and recovery.
* Coordination with backups, file storage, database operations, security, and support.

Payment-provider integration details are covered by the relevant billing and subscription specifications. The lifecycle controls defined here must remain effective regardless of the payment provider.

## 3. Core Operational Principles

### 3.1 Subscription State Is Authoritative

All operational decisions must use the authoritative subscription state and applicable lifecycle policy.

A browser session, cached permission, delayed notification, queue message, or previously generated deletion candidate must never independently establish that a subscription is expired or that data is eligible for deletion.

### 3.2 Restriction Is Not Deletion

Subscription expiry and data deletion are separate lifecycle events.

Expiry may restrict access to business functionality, but it must not immediately destroy business data.

### 3.3 Revalidate Before Destructive Actions

Every deletion job must revalidate current eligibility immediately before performing a destructive operation.

A previously eligible record may no longer be eligible because the subscription was renewed, a deletion was cancelled, a legal hold was applied, or the policy changed.

### 3.4 Tenant Isolation Is Mandatory

Lifecycle operations must be scoped to the correct restaurant network and its authorized data boundaries.

A job processing one tenant must never affect another tenant's data, files, subscriptions, or branches.

### 3.5 Recovery Must Be Evidence-Based

A job reporting success is not sufficient evidence that the correct data was deleted or that service was restored.

Operational verification must confirm the expected state and the absence of unintended changes.

## 4. Related Documents

This document must be maintained consistently with:

* `01_Operations_Architecture_Overview.md`
* `02_Production_Operations_Runbook.md`
* `03_Monitoring_and_Observability_Operations.md`
* `04_Alerting_and_Notification_Operations.md`
* `05_Incident_Management.md`
* `07_Backup_Verification_and_Restore_Operations.md`
* `08_Disaster_Recovery_Operations_Runbook.md`
* `09_Database_Operations.md`
* `10_Redis_Queue_and_Cache_Operations.md`
* `13_Background_Worker_and_Scheduler_Operations.md`
* `15_File_Storage_and_Document_Operations.md`
* `17_Security_Operations.md`
* `18_Release_and_Change_Operations.md`
* `20_Operations_Invariants_and_Guardrails.md`

The implementation must also follow the approved subscription, billing, data-retention, security, and privacy requirements.

## 5. Lifecycle State Model

The implementation must define explicit, auditable lifecycle states. The following logical states establish the required operational behavior; they do not mandate exact database enum values.

| State                  | Meaning                                                                                | Operational behavior                                                                   |
| ---------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `ACTIVE`               | Subscription is valid                                                                  | Authorized subscription features are available                                         |
| `EXPIRING_SOON`        | Expiry is approaching                                                                  | Normal access continues; appropriate warnings are sent                                 |
| `READ_ONLY`            | Subscription has expired or access has otherwise been restricted under approved policy | Business-changing actions are blocked; permitted data viewing and export follow policy |
| `DELETION_PENDING`     | Data has entered the approved deletion eligibility workflow                            | Data remains protected while eligibility is evaluated and deletion is scheduled        |
| `DELETION_IN_PROGRESS` | An authorized deletion operation is executing                                          | Destructive work is controlled, scoped, monitored, and recoverable where supported     |
| `DELETED`              | The applicable deletion workflow has completed and verification passed                 | Normal tenant access is unavailable; retained audit evidence follows policy            |
| `SUSPENDED`            | Access is restricted for a separate authorized reason                                  | Restrictions follow the reason for suspension and its approved policy                  |

These states must not be treated as a simple unconditional linear sequence. For example, an expired subscription may be reactivated from `READ_ONLY`, and a pending deletion may be cancelled when the current policy and state permit it.

The implementation must define valid transitions, transition authorization, concurrency handling, and recovery behavior.

## 6. Subscription Expiry Operations

### 6.1 Expiry Detection

Subscription expiry may be detected by a scheduler, an event-driven process, a request-time check, or a combination of these mechanisms.

Regardless of implementation, the authoritative subscription validity must be checked at the appropriate security and business-operation boundaries.

Expiry processing must:

1. Identify subscriptions approaching or passing their expiry time.
2. Evaluate the authoritative expiry timestamp and current subscription status.
3. Apply the approved grace-period policy, if one exists.
4. Revalidate that the subscription has not been renewed or otherwise changed.
5. Apply the required access restrictions.
6. Record the transition and its reason.
7. Schedule appropriate notifications.
8. Emit operational metrics and events.
9. Confirm that the transition completed successfully.

Repeated expiry detection must be safe and must not create duplicate destructive work or inconsistent state.

### 6.2 Time Handling

Subscription expiry must use a consistent authoritative time source.

Requirements:

* Store and compare timestamps consistently, preferably using UTC.
* Convert timestamps to local time only for display and communication.
* Define the exact meaning of the expiry timestamp, including its boundary.
* Avoid relying on client-device clocks.
* Monitor clock synchronization for systems involved in lifecycle processing.
* Define how delayed schedulers and temporary service outages affect processing.

The expiry boundary must be deterministic. Different application services must not disagree about whether the same subscription is active.

### 6.3 Expiry Notifications

Notifications should be generated according to the approved notification policy.

They may include:

* Upcoming expiry reminders.
* Confirmation that the subscription has expired.
* Explanation of restricted functionality.
* Instructions for reactivation.
* Data-retention or deletion warnings when applicable.
* Confirmation of reactivation or completed deletion, where appropriate.

Notification delivery failure must not silently disable required access restrictions.

Notification messages must not expose confidential information or imply that deletion has occurred when it has not been verified.

## 7. READ_ONLY Operations

### 7.1 Purpose

`READ_ONLY` allows permitted users to inspect retained business data while preventing unauthorized changes after subscription expiry.

It is an access-control state, not a frontend-only presentation mode.

### 7.2 Required Restrictions

The system must block unauthorized business-changing operations, including applicable actions that:

* Create or modify orders.
* Accept or modify payments.
* Change cash-register balances or closing records.
* Modify inventory quantities or inventory movements.
* Change recipes, menus, or prices.
* Modify employee roles, permissions, or payroll records.
* Create or approve refunds.
* Create new business records or change authoritative financial records.
* Trigger other operations classified as subscription-restricted.

The exact set of restricted operations must be maintained in the approved subscription feature and permission policy.

### 7.3 Permitted Operations

Read-only access may permit:

* Viewing authorized historical orders.
* Viewing reports and retained business records.
* Viewing subscription status and renewal instructions.
* Viewing permitted inventory, employee, and financial history.
* Exporting authorized data where the subscription and security policy permit it.
* Accessing support and account-management functions that do not bypass subscription restrictions.

The system must not assume that every read or export operation is automatically permitted. Data sensitivity, user permissions, privacy requirements, and the applicable subscription policy remain enforceable.

### 7.4 Enforcement Requirements

The backend must enforce `READ_ONLY` restrictions on every applicable write path.

The following are insufficient by themselves:

* Disabling buttons in the frontend.
* Hiding navigation items.
* Returning a warning without rejecting the prohibited operation.
* Checking subscription state only at login.
* Trusting a cached session after its authorization context has changed.

API endpoints, background jobs, integrations, and offline synchronization must all respect the authoritative lifecycle state.

### 7.5 Offline Branches and Synchronization

Offline operation requires explicit handling because a branch may temporarily lack connectivity when the subscription expires.

The implementation must define:

* How subscription validity is represented on an offline device.
* The maximum acceptable age of cached authorization information.
* Which operations may be recorded locally during an outage.
* How queued operations are validated when connectivity returns.
* How expired or unauthorized operations are rejected, quarantined, or reconciled.
* How users are informed about rejected operations.

Offline data must not automatically override newer authoritative server state.

Subscription restrictions must not silently discard queued orders, inventory changes, payment records, or cash-register events. Conflicts must follow the approved reconciliation policy and remain auditable.

## 8. Reactivation and Return to Active Service

### 8.1 Reactivation Preconditions

Reactivation must be confirmed by the authoritative subscription or billing process.

A client-side payment success screen, delayed webhook, or notification alone is insufficient proof that the subscription has been renewed.

The system must verify the resulting subscription status, validity period, and applicable feature limits.

### 8.2 Reactivation Procedure

1. Receive or detect a possible subscription renewal.
2. Verify the renewal through the authorized billing workflow.
3. Update the authoritative subscription state.
4. Recalculate the allowed features and limits.
5. Cancel or invalidate pending deletion work where applicable.
6. Restore authorized access.
7. Invalidate stale authorization and feature caches.
8. Notify affected services or workers of the state change.
9. Record the transition and its evidence.
10. Verify that authorized operations work and restricted features remain restricted where required.

Restoring `ACTIVE` status must not automatically restore permissions that have been revoked independently.

### 8.3 Reactivation During Deletion

If reactivation occurs while deletion is pending, the system must cancel or invalidate the pending deletion before destructive execution begins.

If deletion has already started, the worker must stop at a safe boundary when possible and the recovery procedure must determine what has already been deleted.

Reactivation must never be represented as fully restoring data that has already been irreversibly deleted.

Partial deletion requires a controlled recovery assessment, potentially involving backups and file restoration. Recovery must not create duplicate or inconsistent business records.

## 9. Data Retention Policy

### 9.1 Retention Period

The approved business policy specifies that expired subscription data may become eligible for deletion if the subscription is not reactivated within two months.

The implementation must define the exact calculation of this period before enabling automated deletion, including:

* The event from which the period starts.
* Whether the period is measured in calendar months or a fixed duration.
* The timezone and expiry-boundary rules.
* The effect of grace periods, suspensions, disputes, and approved exceptions.
* The treatment of delayed processing.
* Any mandatory legal, accounting, privacy, or contractual retention requirements.

The phrase “two months” must not be converted into an arbitrary number of days without approval.

### 9.2 Eligibility Is Not Immediate Authorization

Passing the retention period creates a candidate for eligibility evaluation; it does not automatically authorize immediate deletion.

Before deletion, the system must evaluate:

* Current authoritative subscription status.
* Whether the subscription was renewed or extended.
* Whether a deletion cancellation or retention hold exists.
* Whether the applicable retention period has elapsed.
* Whether legal or regulatory requirements require retention.
* Whether a dispute, investigation, or support recovery procedure is active.
* Whether tenant ownership and deletion scope are unambiguous.
* Whether required data exports, notifications, or approvals have been completed.
* Whether the applicable deletion policy version is valid.

If a mandatory requirement is unknown or cannot be verified, deletion must be blocked until the ambiguity is resolved.

### 9.3 Data Categories

The deletion policy must identify the treatment of each data category, including:

* Operational business records.
* Orders and payment-related records.
* Inventory and recipe history.
* Employee and payroll information.
* Uploaded documents and images.
* Generated reports and exports.
* Search indexes and derived data.
* Cache entries and queued jobs.
* Audit records.
* Backups and disaster-recovery copies.
* Billing records maintained by an external provider.

Different categories may have different retention obligations.

A single tenant-level deletion command must not bypass category-specific retention rules.

### 9.4 Legal Holds and Required Retention

Where applicable, a legal hold or mandatory retention requirement must block deletion of the affected records.

A hold must be explicit, attributable to an authorized decision, time-stamped, and auditable.

Removing a hold must require appropriate authorization and a recorded reason.

Operational convenience or storage pressure is not sufficient justification for bypassing a retention hold.

## 10. Deletion Eligibility Evaluation

### 10.1 Eligibility Workflow

Deletion eligibility must be evaluated through a controlled workflow.

1. Discover expired subscriptions whose retention periods may have elapsed.
2. Load the current authoritative subscription and lifecycle state.
3. Calculate the eligibility timestamp using the approved policy.
4. Check renewal, extension, cancellation, and reactivation events.
5. Check holds, exceptions, and applicable retention rules.
6. Confirm the tenant identity and exact deletion scope.
7. Confirm that the policy version permits the operation.
8. Record the eligibility decision and its reason.
9. Schedule deletion or mark the candidate as blocked.
10. Revalidate all critical conditions immediately before destructive execution.

The eligibility evaluator should distinguish at least:

* `ELIGIBLE`
* `NOT_YET_ELIGIBLE`
* `BLOCKED_BY_HOLD`
* `REACTIVATED`
* `POLICY_REVIEW_REQUIRED`
* `ERROR_REQUIRES_RETRY`
* `CANCELLED`

These are logical outcomes. Implementations may use different internal values if the same distinctions and safeguards remain available.

### 10.2 Eligibility Evidence

For each evaluation, retain sufficient evidence to explain:

* Which tenant was evaluated.
* Which policy version was applied.
* Which subscription state was observed.
* Which retention timestamp was calculated.
* Which eligibility checks passed or failed.
* Which holds or exceptions were found.
* When the evaluation occurred.
* Which service or authorized actor performed it.
* Why deletion was scheduled, blocked, or cancelled.

Do not store secrets or unnecessary personal data in eligibility logs.

## 11. Deletion Job Architecture and Controls

### 11.1 Job Responsibilities

Deletion jobs must be treated as privileged background operations.

The workflow should separate:

1. Candidate discovery.
2. Eligibility evaluation.
3. Scheduling.
4. Pre-execution validation.
5. Deletion execution.
6. Post-execution verification.
7. Finalization and audit recording.

This separation helps prevent a stale discovery result from directly causing irreversible deletion.

### 11.2 Idempotency

Deletion jobs must tolerate duplicate queue messages, scheduler retries, worker restarts, and repeated delivery.

The implementation must define a stable operation identity and prevent duplicate destructive effects.

Repeated execution must not:

* Delete another tenant's data.
* Repeat external side effects unexpectedly.
* Remove newly created or unrelated records.
* Mark a partially completed deletion as successful.
* Erase evidence needed to investigate a failure.

### 11.3 Concurrency and State Changes

A subscription renewal, hold, deletion cancellation, and deletion worker may execute concurrently.

The implementation must use an appropriate combination of authoritative state transitions, transactional checks, version checks, locks, or equivalent concurrency controls.

The exact mechanism depends on the architecture, but it must ensure that a stale worker cannot proceed merely because an earlier eligibility check succeeded.

If the worker cannot establish that its deletion authorization is still valid, it must stop before the next destructive step and re-evaluate.

### 11.4 Least Privilege

Deletion workers must receive only the permissions required for their assigned scope.

Where practical:

* Separate eligibility-evaluation privileges from destructive privileges.
* Restrict access to tenant data by explicit scope.
* Prevent general-purpose application roles from bypassing deletion safeguards.
* Require stronger authorization for manual deletion and exceptional overrides.
* Keep credentials out of logs and job payloads.
* Audit changes to worker permissions and deletion configuration.

### 11.5 Bounded Execution

Deletion processing must not overwhelm production services.

Use controlled batch sizes, concurrency limits, timeouts, backpressure, and scheduling windows as appropriate.

Large tenants may require staged deletion.

The system must protect normal POS operations, database availability, queue processing, backup jobs, and file-storage performance.

### 11.6 Job Payloads

Job payloads should contain stable identifiers and the minimum information required to locate and validate the operation.

The worker must reload authoritative state rather than trust subscription status or eligibility claims embedded in an old payload.

Sensitive business data must not be copied into queue messages unnecessarily.

## 12. Deletion Execution Procedure

### 12.1 Pre-Execution Checks

Before deleting data, the worker must:

1. Authenticate its execution identity.
2. Load the tenant and lifecycle record.
3. Confirm that the deletion operation is still authorized.
4. Re-evaluate subscription status and retention eligibility.
5. Confirm that no hold or cancellation applies.
6. Confirm that the operation scope is exact and tenant-isolated.
7. Confirm that the required retention policy is available and valid.
8. Check that required audit evidence can be recorded.
9. Confirm that dependencies and deletion strategy are ready.
10. Create or update the operation record before destructive work begins.

If any critical check fails, the worker must stop safely and record a meaningful outcome.

### 12.2 Controlled Deletion

Deletion should follow the approved dependency order.

Depending on the implementation, this may include:

* Disabling ordinary tenant access.
* Cancelling or invalidating pending tenant jobs.
* Removing tenant-specific cache entries.
* Removing search-index entries and derived data.
* Deleting or scheduling deletion of eligible stored files.
* Deleting eligible business records in dependency-safe batches.
* Removing tenant-specific configuration and operational state.
* Finalizing the lifecycle record.
* Retaining required audit evidence.

The exact sequence must follow the data model and storage architecture. It must not assume that every data category can be deleted in one database transaction.

### 12.3 Partial Failure

If deletion fails partway through:

* Record the current operation stage.
* Record the completed and pending categories.
* Preserve enough state to resume safely or invoke recovery.
* Prevent normal access from being restored accidentally.
* Prevent the operation from being marked `DELETED`.
* Alert the responsible operations team according to severity.
* Re-evaluate subscription and hold state before any retry.

A retry must resume from verified state or safely repeat an idempotent stage. It must not blindly rerun every destructive action.

### 12.4 Completion Criteria

An operation may be marked `DELETED` only when:

* Every required deletion stage has completed.
* Every required verification has passed.
* No required category remains unintentionally accessible.
* Relevant storage and database states are consistent.
* The required audit evidence is recorded.
* Any exceptions are resolved or explicitly handled by an approved policy.

If the system uses asynchronous storage deletion, the final state must accurately represent whether deletion was requested, completed, or awaiting provider confirmation.

## 13. File Storage and Derived Data

Tenant deletion must coordinate with `15_File_Storage_and_Document_Operations.md`.

Requirements include:

* Identify tenant-owned objects independently of user-supplied filenames.
* Validate object ownership and deletion scope.
* Prevent shared objects from being deleted while still referenced by another authorized tenant.
* Track asynchronous object-deletion requests and their results.
* Remove or invalidate tenant-specific derived files and exports according to policy.
* Clear relevant cache and search-index entries.
* Verify that files are no longer accessible through application interfaces or authorized storage paths.
* Record provider errors and unresolved object identifiers without exposing sensitive content.

Deleting database metadata does not prove that file content has been removed. Deleting a file object does not prove that its database references have been cleaned up.

Both sides must be reconciled.

## 14. Backups and Recovery Copies

Deletion policy must explicitly address backups and disaster-recovery copies.

The system must not claim that all copies have been immediately erased when retained backups still contain the data.

The approved policy must define:

* Backup retention periods.
* How expired tenant data is treated in retained backups.
* Whether backups expire naturally or support selective erasure.
* How restored backups reapply deletion records or tombstones.
* How to prevent deleted tenant data from being unintentionally reintroduced.
* How legal holds and mandatory retention affect backup handling.
* How deletion completion is communicated accurately.

A backup restore must not silently reactivate a deleted tenant or undo a valid deletion decision.

Where individual deletion from immutable backups is not supported, the system must follow its approved backup-retention and post-restore reconciliation process.

See `07_Backup_Verification_and_Restore_Operations.md` and `08_Disaster_Recovery_Operations_Runbook.md`.

## 15. Scheduler and Queue Operations

### 15.1 Scheduling

The scheduler must discover eligible candidates reliably and safely.

Operational requirements:

* Track the last successful scan.
* Detect delayed or missed scheduling runs.
* Avoid creating unbounded duplicate jobs.
* Support pagination or bounded batches for large candidate sets.
* Record scan duration, candidate count, and scheduling failures.
* Reconcile scheduled work against authoritative lifecycle state.

A missed schedule must delay processing safely rather than bypass eligibility controls.

### 15.2 Queue Backlog

Monitor:

* Number of pending deletion jobs.
* Age of the oldest pending job.
* Jobs currently executing.
* Failed and repeatedly retried jobs.
* Cancelled jobs awaiting confirmation.
* Jobs blocked by holds or policy errors.
* Time from eligibility to processing.
* Time from processing start to verified completion.

A backlog must not be addressed by removing revalidation, increasing concurrency without limits, or disabling required checks.

### 15.3 Retry Policy

Retries must distinguish transient infrastructure failures from permanent policy or data errors.

Examples of transient failures include temporary database unavailability or a storage-provider timeout.

Examples of non-transient failures include an active retention hold, invalid tenant scope, an unsupported policy state, or an unresolved authorization failure.

Non-transient failures must not be retried indefinitely without investigation.

## 16. Cancellation and Emergency Stop

### 16.1 Cancellation

An authorized cancellation may be required because of:

* Subscription reactivation.
* A newly applied retention hold.
* An incorrect eligibility decision.
* A legal or contractual requirement.
* An identified data-integrity problem.
* An approved operational exception.

Cancellation must update authoritative operation state and prevent queued or delayed workers from continuing without revalidation.

Cancelling a job does not automatically reverse deletion stages already completed.

### 16.2 Emergency Stop

Operations must have a documented way to pause new destructive deletion work.

The stop mechanism must be protected by authorization and must be auditable.

When activated:

* New deletion execution must stop or remain queued.
* Active workers must stop at safe boundaries where feasible.
* Lifecycle discovery and non-destructive monitoring may continue if safe.
* The reason, scope, and activating actor must be recorded.
* An alert must notify the responsible team.
* Restarting deletion processing must require an explicit authorized decision and a revalidation of pending work.

The emergency stop must not disable unrelated essential application services.

## 17. Monitoring and Alerting

Lifecycle monitoring must cover both business correctness and technical health.

### 17.1 Required Metrics

Track at least:

* Subscriptions approaching expiry.
* Subscriptions transitioned to `READ_ONLY`.
* Failed or delayed expiry transitions.
* Reactivations and cancelled deletion operations.
* Deletion candidates awaiting evaluation.
* Eligible candidates awaiting scheduling.
* Deletion jobs started, completed, failed, and blocked.
* Partial deletion operations.
* Jobs exceeding expected processing time.
* Eligibility-to-deletion delay.
* File-deletion failures.
* Lifecycle reconciliation mismatches.
* Emergency-stop status and duration.

Metrics should use bounded labels. Do not use tenant identifiers, user identifiers, file paths, or other high-cardinality sensitive values as unrestricted metric labels.

### 17.2 Alert Conditions

Create alerts for:

* Expiry processing falling behind its operational target.
* A growing deletion backlog.
* Repeated deletion failures.
* A job attempting to process an invalid tenant scope.
* Deletion proceeding despite an active hold or cancellation.
* Reactivated subscriptions remaining incorrectly restricted.
* Deleted tenants becoming accessible again unexpectedly.
* Missing audit evidence.
* Database or storage pressure caused by deletion activity.
* A scheduler or worker becoming unavailable.
* Unexpected growth in partial deletions or recovery operations.

Alerts must include the responsible service, severity, impact, relevant operation identifier, and safe investigation steps.

### 17.3 Business-State Verification

Operational dashboards must distinguish:

* Subscription expiry detected.
* Restriction successfully applied.
* Reactivation verified.
* Deletion eligibility confirmed.
* Deletion started.
* Deletion completed and verified.

These states must not be collapsed into a single generic “processed” metric.

## 18. Troubleshooting Procedures

### 18.1 Subscription Expired but Writes Still Succeed

1. Verify the authoritative subscription state.
2. Identify the affected API or background worker.
3. Check feature and authorization cache freshness.
4. Confirm backend enforcement on the affected write path.
5. Check whether offline synchronization or an integration bypassed the restriction.
6. Block the unauthorized operation path if needed.
7. Preserve relevant logs and audit records.
8. Verify that restricted writes are rejected without damaging valid historical data.

Treat unauthorized writes after expiry as a potential security and data-integrity incident.

### 18.2 Active Subscription Remains READ_ONLY

1. Verify the renewal through the authoritative billing workflow.
2. Confirm the subscription's resulting status and validity period.
3. Inspect pending events and failed background jobs.
4. Check stale authorization and feature caches.
5. Confirm that independent restrictions do not still apply.
6. Restore access through the approved transition workflow.
7. Verify permitted operations and confirm that independent permissions remain enforced.

Do not bypass authorization checks through a direct database edit unless an approved, audited emergency procedure explicitly requires it.

### 18.3 Eligible Data Is Not Being Deleted

1. Inspect the scheduler's last successful run.
2. Check candidate-discovery results.
3. Review retention timestamps and the policy version.
4. Check for holds, exceptions, and cancellation records.
5. Inspect queue health and worker availability.
6. Review retry limits and failed-job records.
7. Resolve the underlying cause.
8. Re-evaluate eligibility before rescheduling.

Do not force deletion simply to clear a backlog.

### 18.4 Data Was Deleted Incorrectly

1. Stop affected deletion work using the emergency-stop procedure.
2. Preserve operation records, logs, and audit evidence.
3. Identify the tenant, affected data categories, and completed stages.
4. Assess whether other tenants or shared objects were affected.
5. Determine whether recovery from a verified backup is possible.
6. Coordinate database, file-storage, and disaster-recovery specialists.
7. Restore only the approved scope.
8. Verify record relationships, business totals, file references, and access controls.
9. Reconcile restored state with newer valid business events.
10. Complete incident review and implement corrective actions.

Treat unintended deletion as a high-severity incident according to actual impact and the incident-management policy.

### 18.5 Reactivation Races With Deletion

1. Identify the authoritative order and timestamps of state transitions.
2. Determine whether destructive work had started.
3. Inspect the worker's most recent authorization and eligibility checks.
4. Stop remaining destructive stages where safe.
5. Record the completed deletion stages.
6. Recover missing data only through an approved restoration process.
7. Reconcile billing, lifecycle, database, and storage state.
8. Correct concurrency controls and test the race condition before resuming normal processing.

## 19. Security and Audit Requirements

Lifecycle processing has privileged access to customer business data and must be treated as security-sensitive.

Requirements:

* Enforce least privilege for schedulers and workers.
* Require strong authorization for manual overrides.
* Record who initiated, approved, cancelled, or resumed sensitive operations.
* Protect lifecycle logs from unauthorized modification.
* Prevent secrets and unnecessary personal information from entering logs or queue payloads.
* Enforce tenant isolation at every stage.
* Validate all identifiers and scope boundaries.
* Record policy changes and their effective times.
* Alert on anomalous deletion volumes and invalid scopes.
* Review privileged access periodically.
* Keep operational evidence according to the approved retention policy.

Audit records must not be deleted merely because the associated tenant's ordinary business data is being deleted. Their retention and contents must follow applicable legal, privacy, and security requirements.

## 20. Operational Roles and Responsibilities

| Role                       | Responsibility                                                                     |
| -------------------------- | ---------------------------------------------------------------------------------- |
| Subscription/Billing Owner | Maintains authoritative subscription state and renewal semantics                   |
| Operations Engineer        | Monitors lifecycle jobs, investigates failures, and coordinates recovery           |
| Backend Engineer           | Maintains state transitions, authorization enforcement, and concurrency safeguards |
| Database Administrator     | Supports safe database deletion, integrity checks, and recovery                    |
| Security Engineer          | Reviews privileged access, auditability, and security incidents                    |
| Data/Privacy Owner         | Defines retention, deletion, legal holds, and data-handling requirements           |
| Support Team               | Communicates subscription state and follows approved customer-support procedures   |
| Incident Commander         | Coordinates major incidents involving incorrect restriction, deletion, or recovery |

Production deletion must not depend on an individual operator's undocumented judgment.

## 21. Change Management

Changes to subscription or deletion behavior require documented review.

Changes requiring heightened scrutiny include:

* Retention-period changes.
* Expiry-boundary changes.
* New lifecycle states or transitions.
* New deletion categories.
* Changes to hold or cancellation semantics.
* Changes to worker privileges.
* Changes to batch size, concurrency, or retry policy.
* Changes to backup retention or post-restore reconciliation.
* Changes to reactivation behavior.
* Changes to audit evidence or deletion verification.

Before release:

1. Update the relevant policy and architecture documents.
2. Review security, privacy, and data-integrity impacts.
3. Test expiry and reactivation boundaries.
4. Test duplicate jobs and worker restarts.
5. Test concurrent renewal and deletion attempts.
6. Test holds, cancellation, and emergency stop.
7. Test partial failures and safe retries.
8. Verify tenant isolation.
9. Test backup restoration and deletion reconciliation where applicable.
10. Define rollout, rollback, monitoring, and operational ownership.

A software rollback must not automatically undo valid subscription events or recreate data that has been intentionally deleted.

## 22. Readiness Checklist

Before enabling automated subscription lifecycle enforcement and deletion, verify that:

* [ ] The authoritative subscription source is documented.
* [ ] Expiry timestamp semantics are defined.
* [ ] `READ_ONLY` restrictions are enforced by backend services.
* [ ] Offline synchronization has a defined expiry and conflict policy.
* [ ] The two-month retention rule has a precise approved calculation.
* [ ] Mandatory retention and legal holds are supported.
* [ ] Eligibility is revalidated before destructive execution.
* [ ] Reactivation invalidates pending deletion work.
* [ ] Deletion jobs are idempotent and concurrency-safe.
* [ ] Worker privileges are limited and audited.
* [ ] Partial deletion can be detected and safely handled.
* [ ] Database and file-storage deletion are coordinated.
* [ ] Backup and disaster-recovery behavior is documented.
* [ ] Deletion completion has explicit verification criteria.
* [ ] Monitoring and alerts are operational.
* [ ] An emergency stop is available and tested.
* [ ] Manual overrides require authorization and audit evidence.
* [ ] Incident and recovery procedures are tested.
* [ ] Tenant-isolation tests cover destructive operations.
* [ ] The approved data-retention policy is linked and versioned.

## 23. Mandatory Operational Invariants

The following invariants must remain true in production.

1. Subscription state must have an authoritative source.
2. Client-side state must not determine subscription validity.
3. Subscription expiry must not immediately imply data deletion.
4. `READ_ONLY` must be enforced by backend authorization.
5. Hidden or disabled UI controls are not sufficient enforcement.
6. Every write path must follow subscription restrictions.
7. Background jobs must not bypass lifecycle authorization.
8. Offline synchronization must reconcile against authoritative server state.
9. Client clocks must not determine expiry eligibility.
10. Expiry-boundary semantics must be deterministic.
11. Reactivation must be verified through the authoritative workflow.
12. A successful payment screen alone must not restore access.
13. Reactivation must invalidate pending deletion where possible.
14. Reactivation must not claim to restore irreversibly deleted data.
15. Retention periods must be explicitly defined.
16. The two-month rule must not be implemented using an unapproved approximation.
17. Retention eligibility must be evaluated before scheduling deletion.
18. Eligibility must be revalidated immediately before destructive execution.
19. Legal holds must block deletion of affected data.
20. Unknown mandatory retention requirements must block deletion pending review.
21. Deletion scope must identify the correct tenant.
22. Tenant isolation must apply to every deletion stage.
23. A stale job payload must not authorize deletion.
24. Duplicate jobs must not cause unintended destructive effects.
25. Concurrent renewal and deletion must be handled safely.
26. Workers must stop when authorization cannot be verified.
27. Deletion workers must use least-privilege access.
28. Manual overrides must be authorized and audited.
29. Deletion batches must be bounded to protect production services.
30. Retry policies must distinguish transient and permanent failures.
31. A partial deletion must not be marked fully complete.
32. Failed jobs must preserve sufficient evidence for safe recovery.
33. File deletion and database cleanup must be reconciled.
34. Shared objects must not be deleted while still legitimately referenced.
35. Database metadata deletion must not be treated as proof of file removal.
36. Backup retention must be included in deletion policy.
37. Restores must not silently reintroduce deleted tenant data.
38. Required audit evidence must be preserved under its own retention policy.
39. Lifecycle logs must not expose secrets or unnecessary personal data.
40. Deletion metrics must not expose sensitive data through unrestricted labels.
41. Backlogs must not be resolved by bypassing eligibility checks.
42. Emergency stop must be authorized, monitored, and auditable.
43. Restarting deletion processing must trigger revalidation of pending work.
44. Deletion completion must be supported by verification evidence.
45. Notifications must not claim an unverified lifecycle outcome.
46. A scheduler failure must not silently disable lifecycle enforcement.
47. Recovery must preserve business-data integrity and tenant isolation.
48. Lifecycle changes must be tested before production rollout.
49. Operational procedures must identify owners and escalation paths.
50. Any violation of these invariants must be treated as a potential security, data-integrity, or compliance incident.

## 24. Acceptance Criteria

This document is operationally complete when:

* Subscription expiry and `READ_ONLY` enforcement have clear ownership and verification procedures.
* Retention and deletion eligibility are governed by an approved, versioned policy.
* Reactivation and deletion cancellation are safe under concurrent execution.
* Deletion workers revalidate authorization and scope before destructive operations.
* Database, file storage, queues, caches, and backups follow coordinated lifecycle procedures.
* Partial failures can be identified, investigated, and recovered from using documented steps.
* Monitoring, alerting, emergency stop, and audit evidence are defined.
* Production readiness is assessed against the checklist in Section 22.
* The mandatory invariants in Section 23 are preserved by implementation and testing.

**End of Document**

