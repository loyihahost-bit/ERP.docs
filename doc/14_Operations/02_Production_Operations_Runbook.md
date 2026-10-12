# Production Operations Runbook

**Document ID:** OPS-02
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/14_Operations/README.md`

---

## 1. Purpose

This document defines the standard daily operational procedures for the FastFood ERP production environment.

It provides the baseline runbook for operators responsible for keeping the production system healthy, available, observable, secure, and recoverable.

This document focuses on routine production operations.

Detailed procedures for specific components are defined in the corresponding `OPS-*` documents.

---

## 2. Scope

This runbook covers:

* daily production health checks;
* operational start-of-day checks;
* monitoring review;
* alert review;
* application health verification;
* database health review;
* Redis and queue review;
* background job review;
* AI runtime review;
* file storage review;
* subscription lifecycle job review;
* backup status review;
* security operational review;
* capacity review;
* routine maintenance;
* operational change verification;
* end-of-day checks;
* operational handover;
* abnormal condition handling;
* escalation;
* operational evidence.

It does not replace:

* deployment procedures;
* incident management;
* disaster recovery;
* security policy;
* database development procedures;
* release procedures;
* detailed component runbooks.

---

## 3. Operational Principles

Daily operations must follow these principles:

1. Verify before assuming.
2. Prefer observation before intervention.
3. Use documented procedures.
4. Make the smallest safe change necessary.
5. Verify recovery after every corrective action.
6. Do not modify business data merely to make a system appear healthy.
7. Escalate when the runbook no longer safely covers the situation.
8. Record significant operational actions.
9. Do not ignore recurring warnings.
10. Protect security, data integrity, and recoverability before convenience.

---

# 4. Daily Operations Cycle

The normal daily cycle is:

```text
Start-of-Day Check
       ↓
Health Review
       ↓
Alert Review
       ↓
Routine Operations
       ↓
Continuous Monitoring
       ↓
Exception Handling
       ↓
End-of-Day Review
       ↓
Handover
```

The exact execution time may vary according to the operational team and production workload.

The sequence must remain consistent even if the schedule changes.

---

# 5. Start-of-Day Procedure

The start-of-day procedure confirms that the production environment is ready for normal business activity.

## 5.1 Confirm Production Availability

Check:

* primary application availability;
* frontend availability;
* API health;
* authentication;
* database connectivity;
* Redis availability;
* worker availability;
* scheduler availability;
* required AI services;
* file storage;
* critical external integrations.

The objective is not to test every application feature manually.

The objective is to detect obvious production-wide failures before normal workload increases.

---

## 5.2 Check Overall Service State

Review the operational dashboard.

Confirm:

* no unresolved critical alerts;
* no active major incident;
* no unexpected service degradation;
* no infrastructure resource exhaustion;
* no abnormal error spike;
* no unexpected queue backlog;
* no failed critical scheduled jobs.

If a previous incident remains unresolved, do not treat the system as fully healthy.

---

## 5.3 Check Recent Changes

Review production changes made since the previous operational period.

Check:

* releases;
* configuration changes;
* infrastructure changes;
* database migrations;
* feature flag changes;
* AI model changes;
* emergency changes.

For each significant change, confirm that post-change verification was completed.

If verification is incomplete, treat the change as an operational risk.

---

# 6. Monitoring Review

Monitoring review is one of the primary daily responsibilities.

Review at minimum:

* availability;
* request error rate;
* latency;
* CPU utilization;
* memory utilization;
* disk utilization;
* database health;
* Redis health;
* queue depth;
* worker health;
* scheduler status;
* storage capacity;
* backup status;
* important business health signals.

The operator should focus on trends and anomalies rather than only current values.

---

# 7. Alert Review

Every alert should be classified.

```text
New Alert
   ↓
Understand
   ↓
Classify
   ├── Informational
   ├── Routine Task
   ├── Degraded Service
   └── Incident
```

For each actionable alert:

1. identify the affected component;
2. identify the start time;
3. determine whether the condition is ongoing;
4. determine business impact;
5. check whether a known change caused it;
6. follow the relevant runbook;
7. resolve or escalate;
8. verify the final state;
9. record the result when required.

An alert must not be closed merely because it was acknowledged.

---

# 8. Application Health Check

The application should be checked at both technical and business levels.

## 8.1 Technical Health

Verify:

* API responds;
* application processes are running;
* expected dependencies are reachable;
* error rates are within normal range;
* latency is not unexpectedly elevated.

## 8.2 Business Health

Verify representative critical workflows where operationally appropriate:

* authentication;
* branch access;
* order creation;
* order processing;
* payment completion;
* inventory consumption;
* reporting;
* synchronization;
* subscription enforcement.

The checks should be lightweight and safe.

Do not create unnecessary production transactions solely for testing unless a dedicated controlled health-test mechanism exists.

---

# 9. Database Daily Check

The database is a critical production dependency.

Daily review should include:

* database availability;
* connection health;
* storage utilization;
* abnormal connection growth;
* long-running operations where monitored;
* failed or abnormal jobs affecting the database;
* backup status;
* replication status where applicable;
* recent database-related alerts.

Operators must not perform arbitrary SQL changes as part of a routine health check.

Data-changing database actions require an approved operational procedure.

Detailed database operations are defined in:

`09_Database_Operations.md`

---

# 10. Redis and Queue Daily Check

Review:

* Redis availability;
* memory utilization;
* queue depth;
* queue growth;
* failed jobs;
* retry volume;
* stuck jobs;
* abnormal processing latency.

A growing queue should be treated as a trend requiring investigation, not merely as a numeric threshold.

When backlog is detected:

1. determine whether workers are healthy;
2. check whether processing rate is increasing or decreasing;
3. identify failed jobs;
4. determine whether the backlog is expected;
5. investigate the cause;
6. apply the approved recovery procedure;
7. verify that backlog returns toward normal.

Do not blindly purge queues to make the backlog disappear.

---

# 11. Background Worker Check

Workers must be checked for:

* process availability;
* queue consumption;
* failure rate;
* retry behavior;
* abnormal execution time;
* repeated failures.

If a worker is unavailable:

1. verify whether the failure is isolated;
2. inspect recent logs;
3. check dependency health;
4. determine whether restart is safe;
5. restart only through the approved procedure;
6. verify successful processing;
7. escalate if the failure returns.

Repeated worker crashes should be treated as an underlying incident rather than as a reason for repeated manual restarts.

---

# 12. Scheduler Check

Review scheduled tasks for:

* expected execution;
* missed executions;
* repeated failures;
* abnormal duration;
* duplicate execution;
* backlog.

Critical scheduled jobs should have an identifiable expected completion state.

If a scheduled task failed:

1. determine whether it is safe to retry;
2. verify idempotency or duplicate protection;
3. inspect the failure reason;
4. retry through the approved procedure;
5. verify the result.

Do not manually run a scheduled job repeatedly without checking whether the first execution may have partially succeeded.

---

# 13. AI Runtime Check

Where AI services are enabled, review:

* model service availability;
* model loading state;
* inference failures;
* latency;
* resource utilization;
* model version;
* abnormal failure rate.

If an AI service becomes unhealthy:

1. determine which business functions depend on it;
2. determine whether a supported degraded mode exists;
3. check recent model/runtime changes;
4. follow the AI runtime runbook;
5. verify recovery.

AI output must not be treated as valid merely because the service process is running.

---

# 14. File Storage Check

Review:

* storage availability;
* storage utilization;
* failed uploads;
* abnormal growth;
* cleanup failures;
* access errors.

Do not manually delete files to reduce storage usage unless the files are confirmed eligible for deletion.

Storage cleanup must respect application references and retention requirements.

---

# 15. Backup Check

Daily operations should confirm:

* expected backup jobs executed;
* no critical backup failure exists;
* recent backup timestamps are within expected limits;
* storage for backups is available;
* backup retention is functioning.

A successful backup job does not by itself prove that restoration is possible.

Restore verification is handled by:

`07_Backup_Verification_and_Restore_Operations.md`

---

# 16. Subscription and Lifecycle Check

Review operational jobs responsible for:

* subscription expiry detection;
* notifications;
* READ_ONLY transitions;
* deletion eligibility;
* scheduled deletion;
* lifecycle-related failures.

Verify that failed lifecycle jobs are visible.

Operators must never manually delete tenant data merely because a subscription appears expired.

Deletion must follow the authoritative lifecycle rules.

Detailed procedures are defined in:

`16_Subscription_and_Data_Lifecycle_Operations.md`

---

# 17. Security Operational Check

Review:

* critical security alerts;
* suspicious authentication activity;
* unusual privileged access;
* secret or credential alerts;
* unexpected access failures;
* security incidents;
* pending security actions.

Security events must be handled according to the Security Operations runbook.

Routine operators must not investigate sensitive events by exposing unnecessary production data.

---

# 18. Capacity and Resource Check

Review current and recent trends for:

* CPU;
* memory;
* disk;
* database storage;
* network;
* Redis memory;
* queue growth;
* file storage;
* AI resources.

The purpose is to detect:

* approaching capacity limits;
* abnormal resource growth;
* leaks;
* workload changes;
* insufficient infrastructure.

A resource becoming high is a signal to investigate.

It is not automatically a reason to restart or scale.

---

# 19. Routine Operational Actions

Routine actions may include:

* restarting an unhealthy stateless service;
* clearing a known-safe application cache;
* retrying a failed idempotent job;
* rotating an approved operational credential;
* cleaning eligible temporary files;
* verifying backup status;
* reviewing resource trends;
* updating operational notes.

Every action must follow an existing runbook when one exists.

If an action can affect persistent business data, it is not considered a routine low-risk action unless explicitly approved as such.

---

# 20. Safe Service Restart Procedure

A restart should be used only when justified.

Before restarting:

1. identify the affected service;
2. confirm the symptom;
3. check whether a recent change caused it;
4. determine whether the service is stateful;
5. check active workloads;
6. determine whether restart is expected to be safe;
7. record the reason when required.

Perform the restart using the approved deployment/infrastructure procedure.

After restart:

1. verify process health;
2. verify dependency connectivity;
3. verify logs;
4. verify relevant metrics;
5. verify representative application behavior;
6. confirm that the original symptom is resolved.

If the problem returns, stop repeating restarts and escalate.

---

# 21. Cache Recovery

Cache problems should be handled carefully.

Before clearing a cache:

* identify the affected cache;
* confirm it is non-authoritative;
* determine expected rebuild behavior;
* confirm that clearing it will not delete business state;
* assess expected load after invalidation.

After clearing:

* verify application performance;
* verify cache repopulation;
* monitor database load;
* monitor error rate.

A cache reset must not be used as a substitute for investigating persistent application or database problems.

---

# 22. Queue Recovery

Before retrying or replaying queued work:

1. identify the affected queue;
2. determine whether messages may have already been processed;
3. check idempotency or duplicate protection;
4. identify failed messages;
5. determine safe retry scope;
6. retry using the approved mechanism;
7. verify successful processing.

Never delete a queue simply to remove an operational backlog unless the procedure explicitly authorizes it and the business impact is understood.

---

# 23. Handling Abnormal Conditions

When an unexpected condition is detected:

```text
Observe
  ↓
Confirm
  ↓
Assess Impact
  ↓
Identify Known Procedure
  ↓
Act Safely
  ↓
Verify
  ↓
Escalate if Needed
```

The operator should avoid making several unrelated changes at once.

Changing many variables simultaneously makes root-cause analysis and recovery verification harder.

---

# 24. When to Escalate

Escalate when:

* the runbook does not cover the situation;
* business-critical functionality is affected;
* data integrity may be affected;
* security may be compromised;
* recovery is uncertain;
* repeated restarts do not resolve the problem;
* a database correction appears necessary;
* production data may need direct modification;
* a backup restore may be required;
* service degradation is spreading;
* resource exhaustion is imminent;
* the incident exceeds the operator's authority.

Escalation is a safety mechanism, not a failure of the operator.

---

# 25. Incident Transition

Routine operations must transition into incident management when the condition meets incident criteria.

The transition should include:

* affected service;
* detected time;
* current symptoms;
* known impact;
* actions already taken;
* current system state;
* relevant alerts;
* responsible operator.

Continue following:

`05_Incident_Management.md`

once an incident is declared.

---

# 26. Production Change Verification

After any significant production change, verify:

### Infrastructure

* required services running;
* expected resource state;
* network connectivity.

### Application

* API health;
* frontend availability;
* authentication;
* representative critical workflow.

### Data

* database connectivity;
* migrations completed;
* background jobs functioning;
* no unexpected data errors.

### Async Processing

* workers consuming queues;
* scheduled jobs functioning.

### Observability

* metrics available;
* logs available;
* expected alerts functioning.

### Business

* critical business functions remain available.

Do not declare a change successful solely because deployment completed.

---

# 27. End-of-Day Procedure

The end-of-day procedure ensures that unresolved operational conditions are not silently carried into the next operational period.

Review:

* active alerts;
* unresolved incidents;
* degraded services;
* failed jobs;
* queue backlog;
* backup status;
* resource trends;
* recent changes;
* pending maintenance;
* security events;
* subscription lifecycle failures.

Identify anything requiring:

* continued monitoring;
* escalation;
* next-shift handover;
* scheduled maintenance;
* incident follow-up.

---

# 28. Operational Handover

A handover should contain only information that another operator needs to safely continue operations.

Include:

* active incidents;
* degraded services;
* unresolved alerts;
* recent significant changes;
* pending recovery actions;
* scheduled maintenance;
* unusual resource conditions;
* backup or recovery concerns;
* security concerns;
* business-impacting conditions.

For each important item, state:

```text
What happened
Current state
Impact
What has been done
What remains
Who owns it
Next expected action
```

Do not hand over unresolved problems using vague statements such as "check this later."

---

# 29. Operational Evidence

Significant operational actions should record:

* date/time;
* operator;
* affected service;
* reason;
* action;
* result;
* verification;
* incident/change reference where applicable.

Evidence should be sufficient to reconstruct important operational decisions without creating unnecessary administrative work.

---

# 30. Daily Operational Checklist

The following checklist is the standard baseline.

### Start of Day

* [ ] Production availability checked.
* [ ] API health checked.
* [ ] Frontend availability checked.
* [ ] Database health checked.
* [ ] Redis health checked.
* [ ] Queue health checked.
* [ ] Workers checked.
* [ ] Scheduler checked.
* [ ] AI runtime checked where applicable.
* [ ] File storage checked.
* [ ] Backup status checked.
* [ ] Security alerts reviewed.
* [ ] Resource utilization reviewed.
* [ ] Recent production changes reviewed.
* [ ] Active incidents reviewed.

### During the Day

* [ ] Critical alerts reviewed promptly.
* [ ] Queue and worker behavior monitored.
* [ ] Resource trends monitored.
* [ ] Business-impacting degradation investigated.
* [ ] Significant changes verified.
* [ ] Operational actions recorded where required.
* [ ] Escalation performed when necessary.

### End of Day

* [ ] Active alerts reviewed.
* [ ] Unresolved incidents reviewed.
* [ ] Failed jobs reviewed.
* [ ] Queue backlog reviewed.
* [ ] Backup state reviewed.
* [ ] Resource risks reviewed.
* [ ] Security events reviewed.
* [ ] Subscription lifecycle failures reviewed.
* [ ] Pending changes or maintenance reviewed.
* [ ] Handover prepared where required.

---

# 31. Troubleshooting Decision Flow

Use the following baseline decision flow:

```text
Problem Detected
      ↓
Is It Real?
      │
   ┌──┴──┐
   No    Yes
   │      ↓
Close   What Is the Impact?
          │
     ┌────┼─────┐
     │    │     │
    Low  Degraded Critical
     │    │     │
     │    │   Incident
     ↓    ↓     ↓
Runbook  Runbook  Escalate
     │    │     │
     └────┼─────┘
          ↓
       Verify
          ↓
    Resolved?
      │    │
     Yes   No
      │     │
    Record  Escalate
```

The flow is intentionally conservative around uncertain production changes.

---

# 32. What Operators Must Not Do

Operators must not:

* directly modify production business records without an approved procedure;
* delete tenant data manually;
* bypass authorization to troubleshoot;
* disable security controls for convenience;
* purge queues without understanding their contents;
* repeatedly restart failing services without investigation;
* run unreviewed SQL against production;
* install arbitrary packages directly on production hosts;
* expose production data while debugging;
* ignore recurring alerts;
* close alerts without verification;
* declare incidents resolved without confirming recovery;
* change configuration without traceability;
* use production data as a test dataset;
* perform undocumented destructive actions.

---

# 33. Routine Operations vs Incident Operations

| Situation                  | Operational Mode   |
| -------------------------- | ------------------ |
| Normal health review       | Routine            |
| Expected maintenance       | Routine / Change   |
| Single recoverable warning | Routine            |
| Repeated failed jobs       | Investigation      |
| Service degradation        | Degraded operation |
| Business-critical outage   | Incident           |
| Possible data corruption   | Incident           |
| Security compromise        | Security Incident  |
| Required restore           | Recovery           |
| Disaster-level failure     | Disaster Recovery  |

When uncertain between routine and incident handling, operators should favor controlled escalation.

---

# 34. Runbook Maintenance

This document must be reviewed when:

* production architecture changes;
* a critical operational procedure changes;
* a recurring incident exposes a missing procedure;
* monitoring changes materially;
* recovery procedures change;
* new production components are introduced;
* subscription lifecycle changes;
* security operational requirements change.

Runbook updates must follow the documentation-first and change-control processes defined in `13_Development`.

---

# 35. Operational Completion Criteria

A daily operational cycle is complete when:

1. production health has been reviewed;
2. important alerts have been assessed;
3. critical dependencies have been checked;
4. backup state has been reviewed;
5. resource risks have been reviewed;
6. active incidents have known owners;
7. unresolved operational risks have been handed over;
8. significant actions have required evidence;
9. no critical condition has been silently ignored.

---

# 36. Relationship to Other Operations Documents

This runbook provides the daily operational baseline.

Detailed procedures are delegated as follows:

* `03_Monitoring_and_Observability_Operations.md` — monitoring and observability.
* `04_Alerting_and_Notification_Operations.md` — alerts and notification handling.
* `05_Incident_Management.md` — incident lifecycle.
* `06_On_Call_and_Escalation_Management.md` — responsibility and escalation.
* `07_Backup_Verification_and_Restore_Operations.md` — backup and restore verification.
* `08_Disaster_Recovery_Operations_Runbook.md` — disaster recovery.
* `09_Database_Operations.md` — PostgreSQL operations.
* `10_Redis_Queue_and_Cache_Operations.md` — Redis, queues, and cache.
* `11_Backend_API_Operations.md` — API runtime.
* `12_Frontend_Operations.md` — frontend delivery.
* `13_Background_Worker_and_Scheduler_Operations.md` — asynchronous processing.
* `14_AI_Runtime_Operations.md` — AI runtime.
* `15_File_Storage_and_Document_Operations.md` — file storage.
* `16_Subscription_and_Data_Lifecycle_Operations.md` — subscription and data lifecycle.
* `17_Security_Operations.md` — operational security.
* `18_Release_and_Change_Operations.md` — production changes.
* `19_Capacity_Cost_and_Resource_Operations.md` — capacity and cost.
* `20_Operations_Invariants_and_Guardrails.md` — mandatory operational rules.

---

# 37. Operational Invariants

1. Daily production health must be reviewed.
2. Critical alerts must not be silently ignored.
3. Alerts must be assessed before closure.
4. Recovery must be verified after corrective action.
5. Operators must use the appropriate runbook.
6. Unknown high-risk conditions must be escalated.
7. Production data must not be changed merely to hide symptoms.
8. Financial data must remain auditable.
9. Inventory data must remain auditable.
10. Tenant and branch isolation must remain intact during operations.
11. Production database changes require controlled procedures.
12. Queue recovery must consider duplicate processing.
13. Scheduled jobs must be checked for missed or repeated execution.
14. Worker failures must not be hidden by endless restarts.
15. Cache clearing must not remove authoritative business data.
16. Backup success must not be confused with restore verification.
17. Security events must follow security operational procedures.
18. Subscription lifecycle actions must use authoritative state.
19. Deletion eligibility must never be guessed manually.
20. Significant operational actions must be traceable.
21. Production changes must be verified after execution.
22. Handover information must identify current state and ownership.
23. Recurring failures must trigger investigation.
24. Operators must not bypass authorization for operational convenience.
25. Production troubleshooting must not expose unnecessary sensitive data.
26. Routine operations must remain lightweight enough to be performed consistently.
27. Operational automation must fail safely.
28. High-risk actions require stronger verification.
29. Service restart is not equivalent to recovery.
30. An acknowledged alert is not equivalent to resolution.
31. A healthy process is not equivalent to healthy business behavior.
32. Operational status must reflect actual system state.
33. Unresolved operational risks must have an owner.
34. Runbooks must remain aligned with the production architecture.
35. Operational procedures must not contradict approved architecture, security, database, API, testing, deployment, or development rules.

---

# 38. Final Principle

The production runbook exists to make daily operations predictable.

The operational goal is not to perform as many checks or manual actions as possible.

The goal is to:

> **Detect important conditions early, respond with the smallest safe action, verify the result, preserve operational evidence, and escalate before an uncertain condition becomes a larger production failure.**

