# Database Migration and Release Deployment

**Document ID:** DEP-15
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/10_Deployment/README.md`
**Previous Document:** `14_CI_CD_Pipeline_Architecture.md`
**Next Document:** `16_Release_Strategy_and_Zero_Downtime_Deployment.md`

---

## 1. Purpose

This document defines how database schema changes are introduced, validated, deployed and operated together with application releases.

The primary objective is:

> Database changes must be deployable safely without breaking active application instances, background workers, synchronization, offline clients or historical data integrity.

Database migration is part of the release lifecycle.

A migration is not treated as an isolated database task.

The deployment process must consider:

* current production schema;
* target schema;
* current application version;
* target application version;
* API compatibility;
* worker compatibility;
* synchronization compatibility;
* offline clients;
* background jobs;
* rollback or roll-forward strategy;
* data backfill;
* database load;
* locking;
* replication;
* historical integrity.

---

# 2. Scope

This document covers:

* migration lifecycle;
* migration ordering;
* schema versioning;
* expand/contract strategy;
* forward compatibility;
* backward compatibility;
* application/schema compatibility;
* API/schema compatibility;
* worker/schema compatibility;
* offline client compatibility;
* migration preflight;
* migration execution;
* transactional migrations;
* non-transactional migrations;
* database locks;
* large table changes;
* index deployment;
* constraint deployment;
* nullable/non-nullable transitions;
* column renaming;
* column removal;
* data type changes;
* data backfill;
* batch backfill;
* throttling;
* migration observability;
* replication impact;
* deployment sequencing;
* startup guards;
* migration failure;
* rollback;
* roll-forward;
* migration recovery;
* staging rehearsal;
* backup/PITR coordination;
* release gates;
* audit;
* migration SLOs;
* system invariants.

This document does not redefine the entire database schema.

This document does not replace:

* Database Architecture;
* Database Migrations and Change Management;
* Database Invariants and Guardrails;
* general Release Strategy;
* general Rollback and Release Recovery.

Those documents remain authoritative for their respective concerns.

---

# 3. Architectural Position

The release relationship is:

```text
Source Change
    ↓
Migration Definition
    ↓
CI Validation
    ↓
Compatibility Validation
    ↓
Staging Migration
    ↓
Staging Release
    ↓
Production Migration
    ↓
Compatible Application Release
    ↓
Backfill / Cleanup
    ↓
Final Contract Phase
```

A schema change may require multiple releases.

The application must not assume that schema migration and application deployment are always one atomic step.

---

# 4. Core Principle

The following principle is mandatory:

> A database schema must remain compatible with all application versions that are allowed to coexist during deployment.

This is particularly important during:

* rolling deployment;
* worker replacement;
* API replacement;
* failed deployment;
* delayed worker restart;
* offline synchronization;
* partial infrastructure rollout.

---

# 5. Database Authority

PostgreSQL remains the authoritative transactional database.

Migration files define schema evolution.

Application code must not silently mutate schema at runtime.

The following are prohibited in normal production operation:

* implicit table creation by application startup;
* automatic destructive schema synchronization;
* uncontrolled ORM auto-migration;
* deleting columns because a model no longer uses them;
* changing production schema outside the controlled migration system.

---

# 6. Migration Source of Truth

Migration definitions stored in source control are the canonical migration source.

Each migration must be:

* uniquely identifiable;
* ordered;
* immutable after release;
* reviewable;
* testable;
* associated with a source revision;
* traceable to the release that introduced it.

A migration already applied in a production environment must not be silently edited.

---

# 7. Migration Identity

Each migration should have a stable identity.

Example:

```text
20261006_001_add_order_reference
```

or an equivalent framework-native migration identifier.

The exact naming format may vary.

The identifier must remain unique within the migration history.

---

# 8. Migration Ordering

Migration execution must follow a deterministic order.

Example:

```text
Migration 101
    ↓
Migration 102
    ↓
Migration 103
```

Migration 103 must not assume that migration 101 can be skipped when its changes are required.

The migration engine must maintain authoritative migration history.

---

# 9. Migration Graph

The migration system should normally remain linear.

If branches require divergent migration histories, the deployment process must reconcile them before production.

Uncontrolled migration branching is prohibited.

The final production migration history must remain deterministic.

---

# 10. Migration Immutability

Once a migration has been applied to production:

* its identity must remain unchanged;
* its semantic behavior must not be rewritten;
* its checksum/provenance should remain verifiable;
* corrections must use a new migration.

A new migration is the preferred mechanism for correction.

---

# 11. Migration Status Registry

The deployment system should track:

* migration identity;
* release identity;
* application version;
* applied timestamp;
* execution duration;
* execution result;
* environment;
* database identity where appropriate.

The registry must distinguish:

```text
Pending
Running
Applied
Failed
Rolled Forward
```

A failed migration must remain observable.

---

# 12. Schema Version

The deployment system should be able to determine:

```text
Current Schema Version
Target Schema Version
Required Minimum Application Schema
```

Application startup checks may compare required schema compatibility without performing the migration itself.

---

# 13. Application and Schema Compatibility

The application version must declare which schema versions it supports.

Conceptually:

```text
Application v20
supports schema 50–52

Application v21
supports schema 51–54
```

The exact representation is implementation-defined.

The purpose is to prevent an incompatible application from starting against an unsupported schema.

---

# 14. Compatibility Matrix

Every non-trivial migration should define a compatibility matrix.

Example:

| Component      | Old Schema | Expanded Schema |          Contract Schema |
| -------------- | ---------: | --------------: | -----------------------: |
| API v20        |  Supported |       Supported |             Not required |
| API v21        |  Supported |       Supported |                Supported |
| Worker v20     |  Supported |       Supported |            Not supported |
| Worker v21     |  Supported |       Supported |                Supported |
| Offline client |  Supported |       Supported | Depends on sync contract |

The exact versions vary by release.

---

# 15. Expand/Contract Strategy

The default strategy for potentially breaking schema changes is:

```text
Expand
   ↓
Deploy Compatible Application
   ↓
Backfill / Migrate Data
   ↓
Switch Application Behavior
   ↓
Verify
   ↓
Contract
```

Destructive changes should normally occur only after all consumers no longer depend on the previous representation.

---

# 16. Expand Phase

The Expand phase introduces schema structures without immediately removing old structures.

Examples:

* add nullable column;
* add new table;
* add new index;
* add new enum-compatible representation;
* add new relation;
* add compatibility fields.

The expanded schema must remain compatible with the current application where practical.

---

# 17. Compatible Application Release

After Expand, the application may be deployed with support for both old and new schema representations.

Example:

```text
Read:
new field if available
otherwise old field

Write:
old field + new field
```

The application should not assume that all running instances are already updated.

---

# 18. Dual Read

During transition, dual read may be used.

Example:

```text
Read new_column
   ↓
if missing
   ↓
fallback to old_column
```

The fallback period must be bounded and explicitly documented.

---

# 19. Dual Write

Dual write may be required when migrating data representations.

Example:

```text
Application Update
      ↓
write old_column
write new_column
```

The system must define which field is authoritative during the transition.

The application must avoid uncontrolled divergence between the two representations.

---

# 20. New Field Introduction

A common safe sequence is:

```text
Release A
→ Add new nullable field

Release B
→ Write both old and new fields

Backfill
→ Populate new field for historical rows

Release C
→ Read new field as authoritative

Release D
→ Remove old field
```

The exact number of releases may differ.

---

# 21. Column Rename

A direct rename may break active application versions.

Preferred pattern:

```text
Add replacement column
       ↓
Compatible application
       ↓
Dual read/write
       ↓
Backfill
       ↓
Switch authority
       ↓
Remove old column later
```

Direct rename is acceptable only when active application compatibility is proven.

---

# 22. Column Removal

A column must not be removed merely because the latest source code no longer references it.

Before removal, verify:

* API versions;
* active application instances;
* background workers;
* scheduled jobs;
* synchronization clients;
* offline clients;
* reporting jobs;
* operational scripts;
* data export logic.

Only then may the Contract phase remove it.

---

# 23. Table Removal

A table must follow a stronger deprecation process.

The release must verify that:

* no application path reads it;
* no worker reads it;
* no synchronization logic reads it;
* no reports depend on it;
* no audit/reconciliation process depends on it;
* no migration depends on its historical values.

Table removal must be treated as destructive.

---

# 24. Contract Phase

The Contract phase removes obsolete compatibility structures.

Examples:

* old column;
* old index;
* temporary relation;
* deprecated representation;
* compatibility trigger.

Contract changes should be deployed only after dependency verification.

---

# 25. Contract Timing

Contract should normally occur in a later release than Expand.

The delay provides time to:

* complete backfill;
* verify application behavior;
* monitor production;
* discover hidden dependencies;
* complete offline synchronization where applicable;
* confirm worker compatibility.

---

# 26. Destructive Migration Principle

Destructive changes require stronger approval and verification than additive changes.

Examples:

* dropping column;
* dropping table;
* destructive type change;
* deleting old representation;
* irreversible data transformation.

Destructive changes should normally have:

* tested recovery strategy;
* recent backup/PITR readiness;
* explicit deployment gate;
* verified dependency inventory.

---

# 27. Backward Compatibility

A schema migration should preserve compatibility with the previous application version whenever rolling deployment or rollback can cause the previous version to remain active.

This is especially important when:

* multiple Gunicorn instances are replaced gradually;
* workers are deployed separately;
* the old API remains available;
* job payloads already exist in queues.

---

# 28. Forward Compatibility

Where practical, the old application should tolerate the expanded schema.

For example:

```text
New column exists
Old application ignores it
```

Adding optional structures is generally safer than changing existing structures in place.

---

# 29. Bidirectional Compatibility

For zero-downtime deployment, the safest migration often supports:

```text
Old App ↔ Expanded Schema ↔ New App
```

The schema must not become incompatible with either side during the transitional release.

---

# 30. Rolling Deployment Relationship

During rolling deployment:

```text
Old App
   │
New App
   │
   ↓
Shared PostgreSQL
```

Both application versions may temporarily access the same schema.

Therefore migration must be compatible with both versions.

---

# 31. Migration Before Application

Migration-before-application is appropriate when the migration creates structures required by the new release while remaining compatible with the old release.

Example:

```text
Add nullable column
       ↓
Deploy application using column
```

This is a common Expand sequence.

---

# 32. Application Before Migration

Application-before-migration is generally unsafe when the application requires a structure that does not yet exist.

This may be used only when the application remains fully compatible without the migration or when a feature is guarded until the schema is present.

The deployment system must explicitly validate the sequence.

---

# 33. Recommended Default Sequence

For most schema changes:

```text
1. Build migration
2. Test migration
3. Deploy migration
4. Verify expanded schema
5. Deploy compatible application
6. Verify runtime
7. Backfill if required
8. Switch application behavior
9. Verify production
10. Perform contract migration later
```

---

# 34. Feature Flag Relationship

Feature flags may be used to separate:

* schema availability;
* application capability;
* user-visible activation.

Example:

```text
Schema ready
    ↓
Code ready
    ↓
Feature disabled
    ↓
Verification
    ↓
Feature enabled
```

Feature flags must not hide schema incompatibility.

---

# 35. Startup Guard

Application startup may verify that:

* schema version is supported;
* mandatory migrations are present;
* required compatibility state exists.

Startup must not automatically perform uncontrolled destructive migration.

---

# 36. Migration Preflight

Before production execution, the system should perform preflight checks.

Examples:

* current schema version;
* expected migration chain;
* database connectivity;
* database capacity;
* free disk space;
* active long-running transactions;
* lock contention;
* replication health;
* migration prerequisites;
* backup/PITR readiness;
* application compatibility.

---

# 37. Preflight Failure

If mandatory preflight checks fail:

```text
Migration
   ↓
Blocked
```

The deployment must stop before making irreversible schema changes.

---

# 38. Database Capacity Check

Migration planning should evaluate:

* disk growth;
* temporary storage;
* WAL generation;
* memory requirements;
* lock duration;
* replication impact;
* I/O load.

A migration must not be approved solely because it succeeds in a small development database.

---

# 39. Free Disk Space

Migration may temporarily require more disk space than the final schema size.

Examples:

* index creation;
* table rewrite;
* data transformation;
* temporary sort structures.

The deployment system should validate sufficient capacity before execution.

---

# 40. Transactional Migrations

Migrations that support transactional execution should use a database transaction where safe.

Benefits:

* atomic schema change;
* rollback on failure;
* consistent intermediate state.

Not every PostgreSQL operation can safely execute inside one transaction.

---

# 41. Non-Transactional Migrations

Some operations may need non-transactional execution.

Examples may include certain forms of concurrent index creation.

Such migrations require:

* explicit classification;
* stronger observability;
* resumability or recovery plan;
* clear partial-completion handling.

---

# 42. Migration Transaction Scope

A migration transaction must not include unrelated application work.

The transaction should remain focused on schema/data transformation.

No migration transaction should call:

* external APIs;
* email;
* printing;
* notifications;
* unrelated application services.

---

# 43. DDL Locking

DDL operations may acquire locks.

Migration planning must evaluate:

* lock type;
* expected lock duration;
* affected table;
* active traffic;
* conflicting queries.

A migration that may block critical POS traffic requires special review.

---

# 44. Lock Timeout

Production migration operations should use bounded lock acquisition behavior where appropriate.

A migration that cannot safely obtain its required lock should fail rather than block critical application traffic indefinitely.

---

# 45. Statement Timeout

Long-running migration statements should use a defined timeout policy where appropriate.

The timeout must reflect:

* operation size;
* expected execution time;
* acceptable operational risk.

---

# 46. Long-Lived Transactions

Before migration, the deployment system should detect long-running transactions that may prevent:

* DDL completion;
* vacuum cleanup;
* lock acquisition;
* schema transition.

Critical blockers should be resolved or the migration postponed.

---

# 47. Migration and POS

POS performance has higher priority than non-essential migration speed.

A migration must not unnecessarily:

* lock Order tables;
* block payment operations;
* block Cash Session operations;
* block inventory deductions;
* cause long database stalls.

---

# 48. Large Table Changes

Large tables require special migration planning.

Examples:

* Orders;
* Order Items;
* Payments;
* Inventory Transactions;
* Audit records;
* Synchronization Operations.

Avoid unnecessary table rewrites.

---

# 49. Large Table Additive Changes

Adding a compatible field is generally safer than rewriting every row immediately.

Historical backfill should normally be separated from schema addition.

---

# 50. Large Table Backfill

Large backfills must use bounded batches.

Example:

```text
10,000 rows
    ↓
batch 500
    ↓
commit
    ↓
next 500
```

The exact batch size must be measured.

---

# 51. Backfill Throttling

Backfills should support controlled throttling.

Backfill throughput may be reduced when:

* database CPU increases;
* lock wait increases;
* replication lag increases;
* POS latency degrades;
* queue backlog increases.

---

# 52. Backfill Isolation

Backfill jobs must use appropriate transaction boundaries.

A large backfill must not hold one transaction open for the entire dataset unless explicitly justified.

---

# 53. Backfill Idempotency

Backfill operations should be safe to retry where practical.

Example:

```text
Process rows where new_value IS NULL
```

This allows recovery after partial completion.

---

# 54. Backfill Completion State

A release should be able to determine whether backfill is:

```text
NOT_STARTED
RUNNING
PARTIAL
COMPLETED
FAILED
```

The completion state must be observable.

---

# 55. Backfill Verification

After backfill, validation should compare:

* expected row count;
* processed row count;
* null count;
* constraint violations;
* old/new representation equivalence where applicable.

---

# 56. Backfill Before Read Switch

If the new application assumes that all historical rows contain the new field, the backfill must complete before switching authoritative reads.

Otherwise the application must safely support incomplete backfill.

---

# 57. Zero-Downtime Requirement

Where zero-downtime deployment is required, migrations must avoid unnecessary exclusive locks and breaking schema transitions.

The exact zero-downtime mechanics are defined further in:

`16_Release_Strategy_and_Zero_Downtime_Deployment.md`

This document defines the database-side prerequisites for that strategy.

---

# 58. Index Creation

New indexes must be planned according to table size and production traffic.

Where appropriate, PostgreSQL concurrent index creation may be used to reduce blocking.

Concurrent operations have different transactional characteristics and must be handled explicitly.

---

# 59. Index Deployment

Index creation should be separated from unrelated schema changes when necessary.

This allows:

* independent failure;
* easier monitoring;
* reduced migration transaction scope;
* clearer recovery.

---

# 60. Index Verification

After index creation, verify:

* index exists;
* expected definition exists;
* application query planner can use it where appropriate;
* replication remains healthy;
* no unexpected performance regression occurred.

---

# 61. Index Removal

Unused or obsolete indexes must not be removed solely from code inspection.

Verify:

* query usage;
* operational reports;
* background jobs;
* migration queries;
* administrative tooling.

Index removal may be a separate migration.

---

# 62. Constraint Introduction

New constraints should generally be introduced in compatibility-safe stages when existing production data may violate them.

Example:

```text
Existing data
    ↓
Validate / clean
    ↓
Constraint introduction
```

The deployment must not blindly enforce a new constraint on data that has not been verified.

---

# 63. NOT NULL Transition

A safe transition may be:

```text
1. Add nullable column
2. Application writes value
3. Backfill existing rows
4. Verify no NULL values
5. Add NOT NULL enforcement
```

This avoids forcing a potentially unsafe table rewrite or immediate deployment break.

---

# 64. Foreign Key Introduction

Before adding a foreign key:

* orphan records must be identified;
* invalid references must be resolved;
* migration behavior must be tested;
* write paths must already respect the relationship.

The new relationship must not silently destroy or rewrite historical data.

---

# 65. Unique Constraint Introduction

Before introducing uniqueness:

* duplicate rows must be identified;
* business rules must define the canonical row;
* duplicates must be resolved through explicit migration logic;
* the resulting state must be verified.

A unique constraint must not be used as an accidental cleanup mechanism.

---

# 66. Data Type Changes

Data type changes can be risky because they may:

* rewrite tables;
* reject existing values;
* change application semantics;
* affect indexes;
* affect serialization.

Large or incompatible type changes should normally use a compatibility migration rather than an in-place destructive conversion.

---

# 67. Enum Changes

Enum changes must consider:

* old application behavior;
* new application behavior;
* API clients;
* queued jobs;
* offline synchronization payloads.

Removing enum values while old consumers remain active is unsafe unless compatibility is proven.

---

# 68. Identifier Migration

If identifiers or key formats change:

* old identifiers must remain resolvable during transition;
* synchronization must understand both forms if necessary;
* historical references must remain valid;
* migration must preserve auditability.

Identifiers should not be rewritten casually.

---

# 69. Money Column Migration

Financial values require stronger migration controls.

When changing financial storage representation:

* historical precision must be preserved;
* rounding must be deterministic;
* totals must remain equivalent where required;
* reports must remain reconcilable;
* migration must be verified before contract cleanup.

Financial migration is release-blocking if reconciliation fails.

---

# 70. Historical Data Principle

Migration must never silently reinterpret historical financial or operational records.

Historical Order snapshots, payments, inventory transactions, Recipe Versions and report versions remain authoritative.

A migration may change storage representation, but not the business meaning of historical records.

---

# 71. Audit Data Migration

Audit records are immutable business history.

Migrations may add metadata structures around audit records, but must not rewrite historical audit meaning.

If transformation is unavoidable, the transformation must be documented and auditable.

---

# 72. Report Version Data Migration

Immutable Report Versions must remain reconstructable.

Schema changes must not delete the information needed to interpret existing report versions.

Report migrations should preserve:

* report period;
* version;
* source state;
* creator/system source;
* calculation context.

---

# 73. Offline Client Compatibility

Offline clients may remain on older application versions longer than the server.

Migration planning must consider:

* old sync payloads;
* old operation types;
* operation UUIDs;
* old schema assumptions in client payloads;
* delayed synchronization;
* conflict resolution.

Server schema changes must not invalidate legitimate offline operations solely because the client has not updated immediately.

---

# 74. Sync Contract Compatibility

Synchronization API contracts must remain compatible across the migration transition.

Example:

```text
Offline Client v1
        ↓
API v1
        ↓
Expanded DB Schema
```

must remain valid where the client is still within its supported lifecycle.

---

# 75. Offline Payload Versioning

Where synchronization payload shape changes:

* payload version should be explicit;
* old payloads should remain parseable for the supported lifecycle;
* new payloads should not require unavailable old schema structures.

---

# 76. Queue Payload Compatibility

Background job payloads may remain in queues during release.

A schema migration must consider jobs created by the previous application version.

The new worker must either:

* continue reading old payloads;
* use a compatibility adapter;
* defer processing until safe;
* migrate queued payloads explicitly.

---

# 77. Worker Deployment Order

When worker code depends on a new schema:

```text
Expand Schema
    ↓
Deploy Compatible Worker
    ↓
Verify Queue Processing
    ↓
Remove Old Worker Compatibility
```

Queued jobs from the old version must remain processable until drained or intentionally migrated.

---

# 78. Scheduled Job Compatibility

Scheduled jobs may execute after the release.

Migration planning must confirm that:

* existing schedules remain valid;
* old job parameters remain supported;
* scheduler does not create incompatible jobs;
* failed jobs can be retried safely.

---

# 79. API Compatibility

Database schema migration must align with API contract changes.

An API field must not become mandatory before all supported application and client versions can supply it.

Breaking API/database changes should be separated into explicit phases.

---

# 80. Frontend Compatibility

The frontend may be deployed separately from the backend.

Therefore:

* old frontend must work with expanded schema through API compatibility;
* new frontend must not assume a Contract migration has already happened unless release sequencing guarantees it;
* API remains the compatibility boundary.

The frontend must never depend directly on PostgreSQL schema.

---

# 81. Migration and Configuration

Configuration values affecting migration should be explicit.

Examples:

```text
MIGRATION_LOCK_TIMEOUT
MIGRATION_STATEMENT_TIMEOUT
BACKFILL_BATCH_SIZE
BACKFILL_PAUSE_MS
MIGRATION_MAX_RUNTIME
```

Defaults must be safe for the deployment environment.

---

# 82. Migration Dry Run

Where practical, migrations should support a staging or pre-production execution before production.

The dry run should report:

* expected duration;
* affected tables;
* estimated row count;
* index impact;
* lock behavior;
* data transformation results.

---

# 83. Production Rehearsal

A production-like dataset should be used for high-risk migrations.

A development database with tiny tables is not sufficient evidence for large production migrations.

---

# 84. Migration Timing

High-risk migrations should be scheduled during operationally appropriate windows.

The window must still preserve the product's availability requirements.

A maintenance window does not justify unsafe migration behavior.

---

# 85. Migration Observability

During migration, monitor:

* migration progress;
* duration;
* statement latency;
* lock wait;
* active connections;
* database CPU;
* database memory;
* disk usage;
* WAL generation;
* replication lag;
* POS latency;
* API latency;
* worker failures;
* synchronization failures.

---

# 86. Migration Metrics

Recommended metrics include:

```text
migration_duration
migration_failure_count
migration_lock_wait
migration_statement_timeout_count
migration_backfill_rows
migration_backfill_rate
migration_backfill_failures
migration_schema_version
migration_pending_count
```

Metrics should remain low-cardinality.

---

# 87. Migration Logs

Migration logs should include:

* migration identity;
* release identity;
* database target;
* start timestamp;
* end timestamp;
* duration;
* success/failure;
* error classification;
* rollback/roll-forward status.

Sensitive database credentials must never be logged.

---

# 88. Migration Audit

Production migration execution should be auditable.

Audit context should include:

* release version;
* migration version;
* actor/system identity;
* environment;
* database target;
* timestamp;
* result;
* recovery decision where applicable.

---

# 89. Migration Approval

High-risk production migrations should require explicit approval.

Risk classification may consider:

* destructive operation;
* financial data impact;
* large table;
* long lock;
* data backfill;
* downtime risk;
* compatibility complexity.

---

# 90. Migration Risk Levels

Example:

### Low

* additive nullable field;
* small reference table change.

### Medium

* large index;
* moderate backfill;
* new constraint after validation.

### High

* destructive migration;
* large historical transformation;
* financial storage change;
* table rewrite;
* critical transaction table change.

Risk level should determine required gates.

---

# 91. Migration Validation

After migration, verify:

* expected schema version;
* expected objects;
* required indexes;
* required constraints;
* row counts where relevant;
* data integrity;
* application startup;
* API health;
* worker health;
* POS health.

---

# 92. Smoke Test After Migration

Minimum smoke testing should include:

```text
Authentication
Business/Branch context
Product read
Menu read
Order creation
Order acceptance
Payment
Inventory validation
Cash Session access
Synchronization endpoint
```

The exact set may expand for migration-specific impact.

---

# 93. Migration Health Gate

A production release must not proceed to broader rollout if:

* migration failed;
* schema validation failed;
* critical smoke test failed;
* replication health is unsafe;
* database resource pressure is outside approved limits.

---

# 94. Database Backup and PITR

High-risk migrations must confirm that:

* backup strategy is operational;
* point-in-time recovery is available;
* required retention exists;
* the restore process is known;
* recovery objectives remain realistic.

A backup existing on paper is not sufficient evidence of recoverability.

---

# 95. Recovery Point Before Risky Migration

For especially risky migrations, a recovery checkpoint or verified backup state should be established before the migration.

The deployment documentation should record the relevant recovery reference.

---

# 96. Rollback Principle

Not every migration can be safely rolled back.

Therefore migration planning must explicitly classify:

```text
Rollback-safe
Rollback-limited
Forward-recovery only
```

---

# 97. Rollback-Safe Migration

An additive schema change may be rollback-safe when the previous application can continue operating and the new structure can be removed without data loss.

Example:

```text
Add unused nullable column
```

Even then, removal should be performed carefully.

---

# 98. Rollback-Limited Migration

A migration may technically support rollback but still risk data loss if the new structure has already received data.

Example:

```text
Dual write
    ↓
New column populated
```

Dropping the new column would destroy newly written information.

Such a migration should usually use roll-forward instead.

---

# 99. Forward-Only Migration

Some transformations should be treated as forward-only.

Examples:

* destructive conversion;
* irreversible normalization;
* deletion of obsolete data;
* irreversible financial representation transformation.

The recovery plan should be:

```text
Migration Failure
    ↓
Stop
    ↓
Restore application compatibility
    ↓
Correct migration
    ↓
Roll Forward
```

not blind rollback.

---

# 100. Roll-Forward Principle

When a schema change has already become the target representation and data has been written into it, correcting forward is usually safer than reverting and losing data.

The deployment system must document this decision before production execution.

---

# 101. Migration Failure

If a migration fails:

1. Stop dependent rollout.
2. Determine whether the migration committed partially.
3. Determine current schema state.
4. Determine whether application compatibility remains valid.
5. Preserve logs and evidence.
6. Decide rollback or roll-forward.
7. Validate database integrity.
8. Resume deployment only after explicit recovery approval.

---

# 102. Partial Migration Detection

For non-transactional migrations, the system must detect partial completion.

The migration status must not be incorrectly reported as simply:

```text
NOT APPLIED
```

when some operations already executed.

---

# 103. Migration Resume

A migration that supports safe resume should record progress explicitly.

Examples:

```text
Phase 1 complete
Phase 2 complete
Backfill 70%
```

Resume behavior must be deterministic.

---

# 104. Migration Retry

Automatic retry is allowed only when the operation is known to be safe.

The deployment system must not automatically retry destructive or ambiguous migrations without validation.

---

# 105. Database Integrity Check

After migration failure or recovery, verify:

* schema integrity;
* constraints;
* required indexes;
* migration history;
* row counts;
* critical financial records;
* foreign key consistency;
* application connectivity.

---

# 106. Replication Impact

In deployments using replicas, migrations must consider:

* WAL volume;
* replication lag;
* replay time;
* replica compatibility;
* read query behavior.

A migration that causes unacceptable replica lag should be throttled, paused or rescheduled where operationally appropriate.

---

# 107. Read Replica Compatibility

Read replicas may temporarily lag behind the primary.

Application behavior must not assume that a just-migrated structure is instantly available on every replica.

For schema changes affecting read replicas, compatibility must account for replication delay.

---

# 108. Migration and Connection Pool

Migration execution should use controlled database connections.

It must not consume the entire production connection budget.

The migration process should leave capacity for:

* POS;
* API requests;
* workers;
* synchronization;
* health checks.

---

# 109. Migration and Background Workers

Background workers should not unexpectedly execute schema-dependent jobs before the migration reaches the required compatibility state.

Worker rollout and migration sequencing must therefore be coordinated.

---

# 110. Migration and Scheduler

Schedulers must not create incompatible jobs during a migration boundary.

Where necessary:

```text
Pause affected schedule
   ↓
Migration
   ↓
Application rollout
   ↓
Resume schedule
```

Only affected schedules should be paused.

---

# 111. Migration and Synchronization

Synchronization has particular compatibility requirements because delayed clients may send operations long after deployment.

The server must continue to validate supported operation versions.

Database migration must not invalidate valid historical synchronization records.

---

# 112. Migration and Idempotency Records

Idempotency records are transactional correctness data.

Schema migrations affecting idempotency data must preserve:

* operation identity;
* operation type;
* Business scope;
* result;
* processing state.

Dropping or rewriting idempotency history can create duplicate financial operations.

---

# 113. Migration and Audit Records

Migration must preserve audit history.

Schema modernization may add fields, but historical audit records must remain attributable.

---

# 114. Migration and Cash Operations

Migrations affecting:

* Cash Sessions;
* cash handovers;
* payments;
* corrections;

require stronger validation because these are financial and operationally critical.

---

# 115. Migration and Inventory

Inventory migrations must preserve:

* stock quantity;
* inventory transaction history;
* FIFO layers;
* Recipe Version references;
* adjustment history.

A migration must not create negative stock or silently rewrite historical deductions.

---

# 116. Migration and Orders

Order-related migrations must preserve:

* Order identity;
* Order Item identity;
* price snapshots;
* discount snapshots;
* payment relationships;
* state history;
* branch context.

Historical Order meaning must remain unchanged.

---

# 117. Migration and Menu/Pricing

Menu and pricing migrations must preserve:

* Business scope;
* Branch scope;
* configuration version;
* historical price snapshots;
* effective configuration boundaries.

A schema migration must not cause existing Order Item prices to be recalculated from current Product configuration.

---

# 118. Migration and Recipes

Recipe-related migrations must preserve:

* Recipe identity;
* Recipe Version;
* approval history;
* historical inventory references.

Current Recipe configuration must not reinterpret historical inventory deductions.

---

# 119. Migration and Subscription

Subscription-related migrations must preserve:

* current lifecycle state;
* expiration state;
* deletion eligibility;
* notifications;
* recovery/re-activation data where applicable.

A migration must not accidentally reactivate a Business that is intended to remain read-only.

---

# 120. Migration and Data Deletion

Lifecycle deletion operations must not run concurrently with a migration that assumes the data still exists unless explicitly coordinated.

For high-risk migrations:

```text
Migration
   ↔
Lifecycle Worker
```

must have a deterministic coordination strategy.

---

# 121. Data Retention

Migration planning must consider retention rules.

A schema change must not accidentally shorten retention of:

* audit records;
* report versions;
* operational history;
* required synchronization history.

Retention changes require explicit policy decisions.

---

# 122. Migration and File Metadata

If schema changes affect file metadata:

* stored files must remain addressable;
* file ownership must remain valid;
* Business/Branch isolation must remain valid;
* storage identifiers must not be confused with filesystem paths.

The file storage system itself remains separately governed.

---

# 123. Migration and Notifications

Notifications generated because of migration state should be asynchronous.

Migration completion must not depend on external notification delivery.

---

# 124. Migration and Monitoring

Deployment monitoring should distinguish:

```text
Migration failure
Application failure
Database failure
Replication failure
Backfill failure
```

These are different operational conditions.

---

# 125. Migration and Release Artifact

A release artifact should identify:

* application version;
* migration range;
* migration checksums;
* schema compatibility;
* required deployment sequence;
* rollback/roll-forward strategy.

The deployment operator must not have to infer migration requirements from source code manually.

---

# 126. Migration Manifest

A release may contain a migration manifest such as:

```text
Release: 2026.10.06

Minimum Schema: 120
Target Schema: 123

Migrations:
120 → 121
121 → 122
122 → 123

Compatibility:
Old App Supported: Yes
New App Supported: Yes

Backfill:
Required: Yes

Contract Phase:
Not included
```

The exact format may vary.

---

# 127. Build and Migration Relationship

CI/CD must validate that:

```text
Application Artifact
+
Migration Artifact
```

are compatible.

A build should not reach production when the application expects a migration that is absent from the release.

---

# 128. Migration CI Validation

CI should test:

* migration ordering;
* migration syntax;
* clean database migration;
* upgrade from representative prior schema;
* application startup against migrated schema;
* compatibility with old application where required;
* downgrade/rollback procedure where supported;
* backfill logic where applicable.

---

# 129. Upgrade-from-Previous Testing

The most important migration test is often:

```text
Representative Previous Production Schema
        ↓
Migration
        ↓
Target Schema
        ↓
Target Application
```

Testing only a clean database does not validate real upgrade behavior.

---

# 130. Multi-Version Testing

For rolling deployments, CI/staging should test:

```text
Old Application + Expanded Schema
New Application + Expanded Schema
Old Worker + Expanded Schema
New Worker + Expanded Schema
```

where these combinations can coexist in production.

---

# 131. Migration Test Data

Migration tests should include:

* empty database;
* normal dataset;
* large dataset;
* historical transactions;
* edge cases;
* invalid legacy data where relevant;
* multi-Business data;
* multi-Branch data.

---

# 132. Tenant Isolation During Migration

Migration scripts must preserve Business isolation.

A migration must not:

* cross-update Businesses;
* assume global Product uniqueness without Business scope;
* join data without required tenant scope;
* mix Branch data.

This is a release-blocking security requirement.

---

# 133. Branch Isolation During Migration

Branch-specific migration logic must preserve Branch identity.

A migration intended for one Branch context must never modify another Branch accidentally.

---

# 134. Migration and Authorization Data

Role and permission schema migrations must preserve:

* Role identity;
* Employee identity;
* Branch scope;
* overrides;
* permission assignments;
* effective state.

Migration must not accidentally grant permissions.

---

# 135. Security Principle

Schema migration is part of the security boundary.

A migration must never create a state in which:

* Business A can access Business B;
* Branch A can access Branch B;
* an inactive employee becomes active;
* permission checks are bypassed;
* device trust is widened unintentionally.

---

# 136. Migration and Secrets

Migration scripts must not contain hard-coded:

* passwords;
* API keys;
* private keys;
* database credentials.

Migration execution should use controlled deployment credentials.

---

# 137. Migration Access

Production migration permissions should be limited to the minimum required database capabilities.

Migration credentials should be separately controlled from ordinary application credentials where practical.

---

# 138. Migration and Application Startup

The application should not enter normal traffic until:

* required schema is available;
* compatibility checks pass;
* critical migrations are complete.

Readiness checks may enforce this.

---

# 139. Mixed-Version Startup

During rolling deployment, old and new application versions may temporarily coexist.

The migration strategy must guarantee that both remain safe against the transitional schema.

---

# 140. Migration Completion Gate

The deployment system should expose a clear state:

```text
Migration Not Started
Migration Running
Migration Complete
Migration Failed
Migration Recovery Required
```

Application rollout must depend on the required state.

---

# 141. Release Sequencing

A release requiring schema evolution should define an exact sequence.

Example:

```text
Build
 ↓
Preflight
 ↓
Expand Migration
 ↓
Schema Verification
 ↓
Compatible Application Deployment
 ↓
Readiness Check
 ↓
Smoke Test
 ↓
Backfill
 ↓
Feature Activation
 ↓
Monitoring
```

Contract migration should occur only when dependencies are removed.

---

# 142. Release Sequencing With Workers

Where workers require the new schema:

```text
Expand Migration
      ↓
API Deployment
      ↓
Worker Deployment
      ↓
Queue Verification
      ↓
Backfill
```

The exact order depends on whether API and worker versions can operate safely against the transitional schema.

---

# 143. Release Sequencing With Offline Clients

Offline clients may not upgrade immediately.

Therefore the deployment must identify:

* minimum supported client version;
* oldest supported sync payload;
* migration compatibility period;
* contract date for old client support.

Contract schema changes must not happen before the client support window ends.

---

# 144. Release Freeze Conditions

A migration/release should be blocked when:

* unresolved migration conflict exists;
* compatibility is unproven;
* backup/PITR readiness is unverified;
* database capacity is insufficient;
* critical replica lag exists;
* migration tests fail;
* data integrity tests fail;
* required approval is missing.

---

# 145. Emergency Migration

Emergency migrations follow the same safety principles.

An emergency does not justify:

* uncontrolled destructive SQL;
* bypassing tenant scope;
* untracked schema changes;
* skipping validation;
* removing auditability.

Emergency process may shorten approval time but must preserve traceability.

---

# 146. Manual SQL

Manual SQL in production should be exceptional.

If manual intervention is required:

* command must be documented;
* scope must be explicit;
* execution must be logged;
* recovery impact must be considered;
* equivalent migration should be created when appropriate.

---

# 147. Out-of-Band Schema Change

Schema changes outside the official migration system are prohibited except for approved emergency procedures.

Any approved out-of-band change must later be reconciled with the migration history.

---

# 148. Migration Reconciliation

If production schema differs from migration history:

```text
Detected Drift
   ↓
Block Normal Migration
   ↓
Investigate
   ↓
Reconcile
   ↓
Validate
   ↓
Resume
```

The deployment system must not blindly overwrite production schema to match source history.

---

# 149. Schema Drift Detection

The system should detect unexpected schema drift through:

* migration history;
* schema snapshots;
* expected object checks;
* controlled comparison tooling.

Drift should be observable before major release execution.

---

# 150. Rollout Stop Conditions

During rollout, stop or pause when:

* database latency exceeds accepted threshold;
* lock waits become unsafe;
* POS p95 latency materially degrades;
* replication lag exceeds safe limits;
* migration error rate increases;
* backfill creates excessive load;
* integrity checks fail.

---

# 151. Performance SLOs

Initial migration-related targets:

| Metric                                     |      Target |
| ------------------------------------------ | ----------: |
| Migration preflight completion             | ≤ 2 min p95 |
| Normal additive migration execution        | ≤ 5 min p95 |
| Migration lock acquisition                 |   ≤ 2 s p95 |
| Schema verification after migration        |  ≤ 60 s p95 |
| Standard smoke-test completion             | ≤ 5 min p95 |
| Migration-induced critical API error rate  |      < 0.1% |
| Migration-induced POS command failure rate |      < 0.1% |
| Backfill error rate                        |      < 0.1% |
| Migration audit record creation            |    ≥ 99.99% |
| Migration status visibility                |  ≤ 30 s p95 |

These are initial engineering targets.

Production measurements should be used to refine them without weakening correctness requirements.

---

# 152. Migration Performance Budget

A migration should have an expected resource profile covering:

* CPU;
* memory;
* I/O;
* WAL;
* connections;
* lock duration.

A migration that cannot fit within the operational capacity of the current deployment must be redesigned or scheduled differently.

---

# 153. Backfill SLO

Backfill duration should be determined from:

* dataset size;
* acceptable database load;
* replication requirements;
* POS performance;
* release deadline.

A backfill should have a measurable completion target rather than an unlimited runtime.

---

# 154. Migration and API SLO Protection

During migration, normal API and POS SLOs remain important.

Database migrations are not exempt from:

* latency monitoring;
* availability monitoring;
* error monitoring.

A technically successful migration that causes prolonged POS degradation is not considered an acceptable release outcome.

---

# 155. Migration and Queue Protection

Backfill/migration work must not cause:

* critical queue starvation;
* synchronization backlog without control;
* notification backlog beyond acceptable thresholds.

Resource pressure must be managed through throttling or scheduling.

---

# 156. Deployment Pause Strategy

The release system should be able to pause between:

```text
Migration
Application rollout
Backfill
Feature activation
Contract
```

This enables controlled verification before irreversible progression.

---

# 157. Approval Between Phases

High-risk releases should support approval gates between:

* Expand;
* Application rollout;
* Backfill;
* Feature activation;
* Contract.

Not every low-risk release needs all manual gates.

---

# 158. Migration Documentation

Each migration should document:

* purpose;
* affected schema objects;
* compatibility assumptions;
* expected data impact;
* expected runtime impact;
* rollback strategy;
* roll-forward strategy;
* backfill requirement;
* contract follow-up;
* verification steps.

---

# 159. Migration Naming

Names should describe the intended change.

Good:

```text
add_order_payment_reference
create_inventory_reconciliation_index
add_recipe_version_status
```

Avoid vague names such as:

```text
fix_db
update2
misc_change
```

---

# 160. Migration Review

Code review should evaluate:

* ordering;
* compatibility;
* lock behavior;
* data correctness;
* tenant isolation;
* rollback/roll-forward;
* performance;
* observability;
* operational recovery.

---

# 161. Migration Security Review

Security review is required when migrations affect:

* permissions;
* tenant boundaries;
* authentication;
* trusted devices;
* subscription entitlements;
* sensitive file ownership;
* audit records.

---

# 162. Migration Financial Review

Additional review is required when migrations affect:

* Order totals;
* payments;
* refunds;
* cash sessions;
* inventory valuation;
* payroll;
* report versions.

Financial migrations must preserve reconciliation.

---

# 163. Migration Data Validation

For transformations, validation should compare:

```text
Before State
    ↓
Migration
    ↓
After State
```

Relevant invariants must remain true.

---

# 164. Business Rule Validation After Migration

Migration completion does not mean business correctness is automatically proven.

Critical post-migration checks may include:

```text
No negative stock
No duplicate payment
No orphan Order Item
No invalid Cash Session
No cross-Business resource
No unauthorized permission grant
```

The exact checks depend on affected domain areas.

---

# 165. Migration and Historical Reconstructability

After migration, historical state should remain reconstructable.

The system must still be able to determine:

* who performed the operation;
* which Business/Branch was involved;
* what configuration applied;
* which transaction snapshot existed.

---

# 166. Migration and Immutable Records

Immutable records must remain immutable.

Schema modernization must not create a technical path by which immutable history becomes editable.

---

# 167. Migration and Event/Outbox Data

If migration affects Outbox or event records:

* pending events must remain processable;
* event identity must remain stable;
* duplicate delivery must remain idempotent;
* consumers must remain compatible during transition.

---

# 168. Migration and Idempotent Jobs

Migration-related deployment jobs themselves should be idempotent where practical.

Repeated deployment commands must not create:

* duplicate migrations;
* duplicate backfills;
* duplicate schema objects;
* duplicate release records.

---

# 169. Migration and Locks

Application-level distributed locks must not be used as a substitute for PostgreSQL transactional or DDL correctness.

Where coordination is required, database semantics remain authoritative.

---

# 170. Migration and Advisory Locks

PostgreSQL advisory locks may be used to ensure only one deployment process performs a migration sequence.

Such locks should be:

* narrowly scoped;
* time bounded where appropriate;
* observable.

They must not replace schema validation.

---

# 171. Concurrent Deployment Protection

Only one production migration sequence should normally modify the target database schema at a time.

Competing migration runners must be prevented or fail safely.

---

# 172. Deployment Idempotency

A repeated release command should detect that:

```text
Migration already applied
```

rather than attempting to execute it again.

---

# 173. Migration and Containers/Systemd

Whether deployment runs through:

* systemd;
* containerized workers;
* CI runner;
* release host;

the migration semantics remain the same.

The migration runner must execute exactly once for the intended deployment target.

---

# 174. Migration and Health Checks

Readiness should reflect schema compatibility.

For example:

```text
Process alive
     ≠
Schema compatible
```

A service with incompatible schema requirements should not become ready.

---

# 175. Migration and Graceful Shutdown

During schema migration, application shutdown should avoid leaving:

* active incompatible workers;
* partially completed deployment state;
* orphaned migration processes.

Long-running migrations should be controlled independently from ordinary request shutdown.

---

# 176. Migration and Release Rollback

Application rollback must first verify schema compatibility.

Example:

```text
New App
   ↓
Schema 123
   ↓
Attempt rollback
   ↓
Old App supports Schema 123?
```

If not, blind application rollback is prohibited.

---

# 177. Rollback Compatibility Matrix

Every release that changes schema should document:

| Scenario                     | Supported                                |
| ---------------------------- | ---------------------------------------- |
| Old App + Old Schema         | Yes                                      |
| Old App + Expanded Schema    | Required where rolling/rollback possible |
| New App + Expanded Schema    | Yes                                      |
| New App + Old Schema         | Usually No unless explicitly designed    |
| New Worker + Expanded Schema | Yes                                      |
| Old Worker + Expanded Schema | Required when coexistence is possible    |

---

# 178. Release Recovery Decision

Recovery should answer:

1. Is the current schema valid?
2. Has new data been written using it?
3. Can old application versions still operate safely?
4. Is rollback reversible without data loss?
5. Is roll-forward safer?

The answer must be documented before destructive recovery.

---

# 179. Migration Recovery Documentation

For each high-risk migration, the release package should contain:

* failure indicators;
* recovery commands/procedures;
* verification checks;
* rollback decision criteria;
* roll-forward steps;
* owner/approver responsibility.

---

# 180. Staging Environment

Staging should reproduce:

* migration ordering;
* deployment tooling;
* representative database version;
* worker topology;
* synchronization behavior;
* relevant queue state.

Staging should not use a fundamentally different migration mechanism than production.

---

# 181. Production-Like Dataset

High-risk migration rehearsal should use a dataset representative of production characteristics, including:

* large Orders;
* many Order Items;
* Inventory Transactions;
* Audit records;
* multiple Businesses;
* multiple Branches.

Sensitive production data must not be copied into test environments unless separately governed.

---

# 182. Migration Benchmark

For large migrations, record:

```text
Start
End
Rows
Duration
CPU
I/O
Locks
WAL
Replica Lag
```

This provides a baseline for future releases.

---

# 183. Migration Regression

A new migration should be compared with prior migration performance when the same tables or patterns are affected.

Repeated degradation should trigger redesign.

---

# 184. Migration and Deployment Windows

The release manager should understand the expected migration duration before starting production work.

Unexpected long-running migration is an operational warning, not a reason to ignore stop conditions.

---

# 185. Migration Cancellation

A migration should define whether cancellation is safe.

Examples:

```text
Transactional DDL
→ rollback may be safe

Non-transactional index creation
→ cancellation may leave completed object
```

Operators must not assume every process can simply be killed safely.

---

# 186. Migration Interruption

If a migration process is interrupted:

* determine actual database state;
* inspect migration history;
* inspect created objects;
* inspect partial backfill;
* determine next safe action.

Do not blindly rerun unknown migration state.

---

# 187. Schema Verification Tooling

The deployment system should provide verification for:

* tables;
* columns;
* indexes;
* constraints;
* sequences;
* enums;
* views;
* triggers;
* migration version.

The exact tool may be implementation-specific.

---

# 188. Schema Snapshot

For major releases, a schema snapshot may be stored as a release artifact.

This supports:

* audit;
* drift detection;
* troubleshooting;
* recovery analysis.

The snapshot is not a substitute for migration history.

---

# 189. Migration Artifact Integrity

Migration files should have verifiable integrity.

Recommended controls:

* source revision;
* checksum;
* build artifact identity;
* release identifier.

A production migration should come from an approved build artifact.

---

# 190. Migration Source Integrity

The deployment process should not fetch arbitrary migration files from an untrusted location during production release.

Migration content should be tied to the released source/artifact.

---

# 191. Release Provenance

A production database should be able to answer:

```text
Which release introduced this schema state?
```

The answer should be traceable through deployment metadata.

---

# 192. Migration and Change Management

Schema changes must follow the project's change governance.

The change record should reference:

* requirement;
* design decision;
* migration;
* application release;
* tests;
* deployment result.

---

# 193. Migration and ADRs

Architecturally significant migrations may require an ADR.

Examples:

* major financial schema redesign;
* new multi-tenant partitioning strategy;
* historical data model transition;
* major identifier migration.

Routine additive migrations do not necessarily require an ADR.

---

# 194. Migration and Documentation Links

Relevant documentation should remain cross-linked.

At minimum:

```text
Deployment
  ↓
Database Migration
  ↓
Database Migrations and Change Management
  ↓
Application Release
  ↓
Rollback / Zero Downtime
```

---

# 195. Operational Ownership

Production migration responsibility should be explicit.

The release process must define who may:

* approve;
* execute;
* pause;
* recover;
* roll forward;
* declare completion.

---

# 196. Post-Migration Review

After a high-risk migration, review:

* actual duration;
* database load;
* lock behavior;
* API impact;
* POS impact;
* worker behavior;
* synchronization behavior;
* user-visible impact;
* incidents;
* lessons learned.

---

# 197. Migration Completion Record

A completed migration should record:

```text
Release
Migration Range
Start Time
End Time
Result
Backfill State
Schema Version
Verification Result
Operator/System
```

This supports future incident investigation.

---

# 198. Contract Cleanup Scheduling

Contract migrations should be scheduled separately when necessary.

The cleanup release should occur only after:

* old application support window ends;
* offline clients are compatible;
* old workers are removed;
* old jobs are drained;
* old API consumers are migrated;
* monitoring confirms safe state.

---

# 199. Contract Cleanup Verification

Before removing compatibility structures, verify:

```text
No old reads
No old writes
No old workers
No old API clients
No old sync payload dependency
No pending compatibility jobs
```

Only then execute Contract.

---

# 200. Final Release Integrity Principle

The final schema after Contract should be simpler than the transitional schema.

Temporary compatibility structures must not become permanent accidental architecture.

---

# 201. Recommended Migration Lifecycle

The recommended lifecycle is:

```text
Requirement
    ↓
Schema Change Design
    ↓
Compatibility Analysis
    ↓
Migration Implementation
    ↓
CI Validation
    ↓
Staging Rehearsal
    ↓
Production Preflight
    ↓
Expand Migration
    ↓
Schema Verification
    ↓
Compatible Application Release
    ↓
Smoke Tests
    ↓
Backfill
    ↓
Feature Activation
    ↓
Monitoring
    ↓
Contract Planning
    ↓
Contract Migration
```

---

# 202. Recommended Release Artifact Structure

```text
release/
├── application/
├── frontend/
├── workers/
├── ai/
├── migrations/
│   ├── manifest
│   ├── checksums
│   └── compatibility
├── verification/
├── rollback/
├── recovery/
└── release-notes/
```

Exact structure may be refined during implementation.

---

# 203. Recommended Deployment Metadata

A deployment record should be able to represent:

```text
release_id
application_version
schema_version_before
schema_version_after
migration_range
migration_result
backfill_status
contract_status
compatibility_status
deployment_started_at
deployment_completed_at
```

---

# 204. Example Safe Schema Evolution

Example:

```text
Business Requirement
       ↓
Add customer_note to Order
       ↓
Migration 201
Add nullable customer_note
       ↓
Deploy Compatible API
       ↓
Old API still works
       ↓
New API writes customer_note
       ↓
Backfill historical rows only if required
       ↓
New API reads customer_note
       ↓
Monitor
```

No destructive step is required if the old representation remains valid.

---

# 205. Example Rename Evolution

```text
old_name
   ↓
add new_name
   ↓
dual write
   ↓
backfill
   ↓
dual read
   ↓
new_name authoritative
   ↓
remove old_name
```

The Contract phase is delayed.

---

# 206. Example Financial Migration

```text
Current Financial Schema
      ↓
Add new precise representation
      ↓
Compatible application writes both
      ↓
Historical backfill
      ↓
Reconciliation
      ↓
New representation becomes authoritative
      ↓
Report/payment verification
      ↓
Old representation removed later
```

Financial reconciliation is mandatory before Contract.

---

# 207. Example Large Backfill

```text
Migration
    ↓
Create new column
    ↓
Deploy compatible code
    ↓
Backfill batch 1
    ↓
Commit
    ↓
Backfill batch 2
    ↓
Commit
    ↓
...
    ↓
Backfill complete
    ↓
Validate
    ↓
Switch reads
```

The backfill must remain bounded and observable.

---

# 208. Example Failure

```text
Migration starts
      ↓
Index creation
      ↓
Lock timeout
      ↓
Migration stops
      ↓
Schema state verified
      ↓
No corruption
      ↓
Application continues
      ↓
Migration redesigned
      ↓
Roll Forward
```

The deployment must not assume that every failed migration requires database restoration.

---

# 209. Anti-Patterns

The following are prohibited:

* editing an already-applied migration;
* production ORM auto-create;
* destructive change before compatibility validation;
* one giant unbounded backfill;
* indefinite migration locks;
* ignoring replication lag;
* ignoring POS latency;
* rolling back application without schema compatibility check;
* treating every migration as rollback-safe;
* changing historical financial meaning;
* cross-Business data transformation;
* migration without audit/provenance;
* manual production schema drift without reconciliation.

---

# 210. System Invariants

The following invariants apply to Database Migration and Release Deployment:

1. PostgreSQL remains the authoritative schema and transaction source.
2. Production schema changes are controlled by versioned migrations.
3. Applied production migrations are immutable.
4. Migration identities are unique.
5. Migration order is deterministic.
6. Migration history is authoritative for migration state.
7. Migration source is stored in source control.
8. Migration content is traceable to a release artifact.
9. Migration checksums/provenance must remain verifiable.
10. Application code must not perform uncontrolled schema creation.
11. ORM auto-create is not the production migration strategy.
12. Migration execution must be explicitly observable.
13. Current schema version must be determinable.
14. Target schema version must be determinable.
15. Application/schema compatibility must be defined for releases that may coexist.
16. Old and new application versions must not be exposed to an incompatible transitional schema.
17. Rolling deployment requires transitional schema compatibility.
18. Expand/Contract is the default strategy for potentially breaking schema changes.
19. Expand occurs before destructive Contract where compatibility is required.
20. New structures may be introduced before new application code uses them.
21. Destructive cleanup must wait until old consumers are removed.
22. Dual-read behavior must have a defined end state.
23. Dual-write behavior must define authoritative semantics.
24. Dual-write divergence must be detectable.
25. Backfill must be bounded.
26. Backfill must be observable.
27. Backfill should be retryable where practical.
28. Backfill must not require an unnecessarily long transaction.
29. Backfill must not monopolize PostgreSQL.
30. Backfill must protect POS performance.
31. Backfill may be throttled under resource pressure.
32. Backfill completion must be verifiable.
33. New authoritative reads must not depend on incomplete data unless the application explicitly supports partial migration.
34. Migration preflight is required for production migrations.
35. Preflight failure must block risky migration execution.
36. Migration capacity must consider disk usage.
37. Migration capacity must consider WAL generation.
38. Migration capacity must consider memory.
39. Migration capacity must consider I/O.
40. Migration capacity must consider connection usage.
41. Migration capacity must consider replication lag.
42. Long-running transactions must be considered before lock-sensitive migrations.
43. DDL lock behavior must be assessed before production execution.
44. Migration lock acquisition must be bounded where appropriate.
45. Migration statement execution must have bounded timeout behavior where appropriate.
46. A migration must not block critical POS operations indefinitely.
47. Database migrations must not call external APIs inside migration transactions.
48. Database migrations must not send notifications inside migration transactions.
49. Database migrations must not perform printing.
50. Database migrations must not depend on interactive user input.
51. Transactional migrations must use atomic execution where safely supported.
52. Non-transactional migrations must be explicitly identified.
53. Non-transactional migrations must have partial-failure handling.
54. Migration interruption requires state inspection before retry.
55. Automatic retry is allowed only for known-safe operations.
56. Destructive migrations must not be blindly retried.
57. A failed migration must not be reported as unapplied when partial execution occurred.
58. Migration recovery must determine actual schema state.
59. Rollback must not be assumed safe for every migration.
60. Migration must classify rollback capability.
61. Forward recovery must be used when rollback risks data loss.
62. Application rollback is prohibited when the old application is incompatible with the current schema.
63. Release rollback requires schema compatibility validation.
64. Contract migrations must not precede supported consumer removal.
65. Old offline clients must remain compatible during their supported lifecycle.
66. Old synchronization payloads must remain processable during the supported compatibility window.
67. Database migrations must not invalidate valid offline operations unintentionally.
68. Old queued jobs must remain processable until drained or explicitly migrated.
69. Worker deployments must consider old and new job payload compatibility.
70. Scheduler behavior must remain compatible during schema transitions.
71. API contracts and database migrations must be coordinated.
72. A new mandatory API field must not become required before supported clients can provide it.
73. Frontend releases must rely on API compatibility rather than direct schema assumptions.
74. Tenant isolation must be preserved during all migration queries.
75. Business scope must be explicit in tenant-scoped data migrations.
76. Branch scope must be preserved in Branch-scoped migrations.
77. Migration logic must not accidentally modify another Business.
78. Migration logic must not accidentally modify another Branch.
79. Permission migrations must not accidentally grant broader access.
80. Authentication-related migrations must preserve security boundaries.
81. Trusted-device migrations must preserve device authorization boundaries.
82. Subscription migrations must preserve lifecycle semantics.
83. Audit records must remain attributable after migration.
84. Immutable audit history must not be silently rewritten.
85. Historical Orders must retain their business meaning.
86. Historical Order Item prices must remain preserved.
87. Historical payments must remain reconcilable.
88. Historical refunds must remain reconcilable.
89. Historical inventory transactions must remain reconcilable.
90. Historical Recipe Versions must remain identifiable.
91. Historical Set configuration references must remain identifiable.
92. Report Versions must remain interpretable after migration.
93. Financial migrations require reconciliation before Contract.
94. Cash Session data must preserve financial state.
95. Idempotency data must preserve duplicate-prevention semantics.
96. Operation UUID identity must remain stable across migration.
97. Outbox/event identity must remain stable across migration.
98. Event consumers must remain compatible during migration where needed.
99. Migration must not create duplicate financial effects.
100. Schema changes must not create duplicate payments.
101. Schema changes must not create duplicate inventory transactions.
102. Schema changes must not create duplicate synchronization effects.
103. Schema changes must not create duplicate configuration versions.
104. Index creation must consider production table size.
105. Large indexes should use an appropriate low-blocking strategy where supported.
106. Index verification must occur after creation.
107. Index removal requires dependency and usage validation.
108. New constraints must consider existing invalid data.
109. NOT NULL transitions should use compatibility-safe sequencing where required.
110. Foreign key introduction must address orphan data before enforcement.
111. Unique constraints must address existing duplicates before enforcement.
112. Type changes must consider data conversion and application compatibility.
113. Enum changes must consider old workers, API clients and offline payloads.
114. Identifier migrations must preserve historical references.
115. Migration artifacts must be generated from approved source.
116. Production migration should not fetch arbitrary migration content.
117. Schema drift must be detectable.
118. Out-of-band schema changes must be exceptional and controlled.
119. Production schema drift must be reconciled before normal migration resumes.
120. Migration execution must be auditable.
121. Production migration operators must be authorized.
122. High-risk migrations require stronger approval.
123. Emergency migrations still require traceability.
124. Migration credentials must be protected.
125. Migration files must not contain hard-coded secrets.
126. Migration-related configuration must use controlled environment settings.
127. Schema compatibility may be enforced through application readiness checks.
128. Application startup must not silently perform destructive migrations.
129. Migration execution must be serialized where concurrent migration runners could conflict.
130. Migration coordination must not depend solely on application-level locks.
131. Database semantics remain authoritative for schema correctness.
132. High-risk migration rehearsal must use production-like data characteristics.
133. Upgrade-from-previous-schema testing is required for relevant releases.
134. Clean-database testing alone is insufficient for migration validation.
135. Mixed-version application testing is required where coexistence is possible.
136. Worker mixed-version testing is required where coexistence is possible.
137. Synchronization compatibility must be tested.
138. Migration-specific smoke tests must run after production migration.
139. Migration success requires schema verification.
140. Migration success requires application compatibility verification.
141. Migration success requires critical health verification.
142. Migration success requires data integrity verification where relevant.
143. Migration-induced POS degradation must be treated as a release issue.
144. Migration-induced API error spikes must be treated as a release issue.
145. Migration-induced replication instability must trigger operational review.
146. Migration status must be observable without guessing.
147. Backfill status must be observable.
148. Migration duration must be measurable.
149. Migration lock wait must be measurable.
150. Migration failures must be distinguishable from ordinary application failures.
151. Migration resource usage must be measurable.
152. Release artifacts must identify migration range.
153. Release artifacts must identify schema compatibility.
154. Release artifacts must identify recovery strategy.
155. Release artifacts must identify required deployment ordering.
156. Migration changes must be reviewed together with application changes.
157. Migration design must consider API impact.
158. Migration design must consider worker impact.
159. Migration design must consider offline client impact.
160. Migration design must consider synchronization impact.
161. Migration design must consider reporting impact.
162. Migration design must consider historical integrity.
163. Migration design must consider performance.
164. Migration design must consider security.
165. Migration design must consider recovery.
166. A successful migration is not sufficient without application verification.
167. A successful application rollout is not sufficient without migration verification.
168. Expand and Contract phases may be separated into different releases.
169. Temporary compatibility structures must have a planned removal point.
170. Contract cleanup must verify absence of old consumers.
171. Migration complexity should be minimized where equivalent safer strategies exist.
172. Destructive changes should be deferred when compatibility can be preserved.
173. Roll-forward is preferred when data has already been committed to the new representation and rollback would lose data.
174. Migration recovery must preserve authoritative database correctness.
175. Migration changes must preserve Business isolation.
176. Migration changes must preserve Branch isolation.
177. Migration changes must preserve authorization boundaries.
178. Migration changes must preserve historical integrity.
179. Migration changes must preserve synchronization correctness.
180. Migration changes must preserve idempotency correctness.
181. Migration changes must preserve transaction correctness.
182. Migration changes must preserve auditability.
183. Migration changes must preserve operational observability.
184. Migration changes must protect critical POS availability.
185. Migration execution must remain compatible with future horizontal application scaling.
186. Migration design must remain compatible with controlled rolling deployments.
187. Migration design must remain compatible with future read replicas.
188. Migration design must remain compatible with asynchronous workers.
189. Migration design must remain compatible with scheduled jobs.
190. Migration design must remain compatible with supported offline clients.
191. The database cannot be considered release-ready when schema compatibility is unresolved.
192. The release cannot be considered production-ready when migration recovery is undefined for a high-risk change.
193. The release cannot be considered complete when Contract dependencies remain active.
194. Database migrations must remain deterministic and reproducible.
195. Database migrations must remain reviewable.
196. Database migrations must remain testable in CI.
197. Database migrations must remain traceable to source and release.
198. Database migrations must remain operationally recoverable.
199. Migration correctness has priority over migration speed.
200. Historical integrity and transactional correctness have priority over deployment convenience.

---

# 211. Related Documents

### Deployment

* `docs/10_Deployment/README.md`
* `docs/10_Deployment/08_Database_Deployment_and_Runtime_Architecture.md`
* `docs/10_Deployment/09_Redis_Queue_and_Cache_Runtime_Architecture.md`
* `docs/10_Deployment/12_Background_Workers_and_Scheduler_Deployment.md`
* `docs/10_Deployment/14_CI_CD_Pipeline_Architecture.md`
* `docs/10_Deployment/16_Release_Strategy_and_Zero_Downtime_Deployment.md`
* `docs/10_Deployment/17_Rollback_and_Release_Recovery.md`
* `docs/10_Deployment/18_Scaling_Load_Balancing_and_Capacity_Architecture.md`
* `docs/10_Deployment/19_High_Availability_and_Failure_Isolation.md`
* `docs/10_Deployment/20_Disaster_Recovery_and_Business_Continuity_Deployment.md`
* `docs/10_Deployment/23_Deployment_Testing_and_Production_Readiness.md`
* `docs/10_Deployment/25_Deployment_Architecture_Invariants_and_Guardrails.md`

### Database

* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/27_Database_Migrations_and_Change_Management.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/07_Transaction_Management.md`
* `docs/04_Architecture/09_Events_Outbox_and_Domain_Integration.md`
* `docs/04_Architecture/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/17_Backend_Testing_and_Quality_Assurance_Architecture.md`
* `docs/04_Architecture/22_Backend_Data_Consistency_and_Concurrency_Architecture.md`
* `docs/04_Architecture/25_Backend_Queue_and_Worker_Architecture.md`

### API

* `docs/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/09_API/24_API_Performance_Observability_and_SLO.md`

### Business / System Analysis

* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 212. Status

**Deployment Architecture Document:** Completed.

**Document Status:** Proposed.

**Current Document:** `15_Database_Migration_and_Release_Deployment.md`

**Next Document:** `16_Release_Strategy_and_Zero_Downtime_Deployment.md`

