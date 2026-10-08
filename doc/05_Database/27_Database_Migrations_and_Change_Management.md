# Database Migrations and Change Management

**Document ID:** DB-27
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

---

## 1. Purpose

This document defines how database schema changes are designed, reviewed, implemented, deployed, validated, and recovered in FastFood ERP.

The migration strategy must protect:

* tenant isolation;
* historical integrity;
* POS availability;
* offline synchronization;
* transaction consistency;
* production data;
* backward compatibility;
* deployment safety.

Database changes must be predictable, reviewable, reversible where technically possible, and safe for an actively operating restaurant system.

---

## 2. Scope

This document covers:

* migration ownership;
* Alembic migration management;
* migration versioning;
* schema changes;
* table changes;
* column changes;
* constraint changes;
* index changes;
* enum/reference data changes;
* data migrations;
* backfills;
* expand/contract migrations;
* backward compatibility;
* application/database version compatibility;
* deployment sequencing;
* production migration;
* rollback;
* recovery;
* migration locking;
* concurrency;
* migration testing;
* migration observability;
* migration audit;
* migration security;
* tenant-aware data migrations;
* large-table migrations;
* zero/minimal downtime strategy.

---

# 3. Migration Principles

The database migration system follows these principles:

1. Every schema change must be versioned.
2. Every production schema change must be represented by a migration.
3. Manual production schema changes are prohibited except emergency recovery approved by authorized operators.
4. Migrations must be deterministic.
5. Migrations must be reviewed before production execution.
6. Migrations must not silently destroy historical data.
7. Destructive changes require explicit planning.
8. Large data transformations must be separated from structural migrations when possible.
9. Long-running migrations must not unnecessarily block POS operations.
10. Migration execution must be observable.
11. Migration failure must be detectable.
12. Migration state must be recoverable.
13. Application deployment and database migration must be compatible.
14. Offline clients must not be broken unexpectedly by schema changes.
15. Migration scripts must not assume an empty database.
16. Production migrations must be tested against realistic data volume.
17. Migration operations must preserve Business and Branch isolation.
18. Migration history must remain immutable.
19. Migration ordering must be deterministic.
20. Schema changes must support controlled rollback or forward recovery.

---

# 4. Migration Tool

The project uses:

**Alembic**

as the primary database migration tool.

Alembic is responsible for:

* migration versioning;
* upgrade operations;
* downgrade operations where safe;
* migration dependency ordering;
* schema evolution;
* migration history tracking.

The application must not automatically generate arbitrary schema changes in production.

---

# 5. Migration Repository

Migration files must be stored in source control.

Recommended structure:

```text
migrations/
├── env.py
├── script.py.mako
└── versions/
    ├── 0001_initial_schema.py
    ├── 0002_add_device_trust.py
    ├── 0003_add_order_snapshot.py
    └── ...
```

The migration directory is part of the application source code.

A migration that has been applied to production must not be silently edited.

---

# 6. Migration Identity

Every migration must have:

* unique revision ID;
* human-readable description;
* parent revision;
* creation metadata;
* upgrade operation;
* downgrade operation where supported.

Example:

```text
Revision:
20261005_add_order_price_snapshot

Down Revision:
20260928_add_order_items
```

Revision IDs must remain stable after release.

---

# 7. Migration Graph

Migrations form an ordered graph.

```text
Migration A
    ↓
Migration B
    ↓
Migration C
    ↓
Migration D
```

A migration must not depend on an unknown or unapplied revision.

Multiple development branches may temporarily create different migration heads, but they must be explicitly merged before release.

---

# 8. Multiple Migration Heads

Multiple migration heads are not allowed in the production migration chain.

If parallel development creates:

```text
A
├── B
└── C
```

a merge migration must be created:

```text
A
├── B ─┐
│     ├── D
└── C ─┘
```

The merge must be reviewed before production deployment.

---

# 9. Migration Immutability

Once a migration has been applied to a shared environment, its historical content must not be changed.

If the migration contains an error:

```text
Old Migration
      ↓
New Corrective Migration
```

must be used instead of editing the old migration.

This preserves reproducibility.

---

# 10. Development Migration Workflow

A normal schema change follows:

```text
Requirement
   ↓
Database Design
   ↓
Migration Design
   ↓
Migration Implementation
   ↓
Automated Tests
   ↓
Review
   ↓
Staging
   ↓
Production
   ↓
Validation
```

No production database modification should bypass this lifecycle unless emergency recovery is required.

---

# 11. Migration Ownership

Each migration must have a clear technical owner.

The owner is responsible for:

* correctness;
* compatibility;
* performance;
* data safety;
* testing;
* deployment notes;
* rollback/recovery strategy.

Migration ownership does not replace code review.

---

# 12. Schema Change Classification

Database changes are classified as:

### 12.1. Additive

Examples:

* new table;
* nullable column;
* new index;
* new optional field.

Usually low risk.

### 12.2. Compatibility-sensitive

Examples:

* rename;
* type change;
* required column;
* constraint tightening;
* enum change.

Requires deployment coordination.

### 12.3. Destructive

Examples:

* column removal;
* table removal;
* data deletion;
* constraint removal affecting integrity;
* irreversible transformation.

Requires explicit approval and migration plan.

### 12.4. Data-intensive

Examples:

* millions of row updates;
* backfill;
* historical transformation;
* recalculation.

Usually requires a separate controlled process.

---

# 13. Expand and Contract Strategy

Breaking schema changes should normally use:

```text
Expand
   ↓
Compatible Application
   ↓
Backfill
   ↓
Switch Reads/Writes
   ↓
Verify
   ↓
Contract
```

Example:

```text
Old Column
    ↓
New Column Added
    ↓
Application Writes Both
    ↓
Backfill Historical Rows
    ↓
Application Reads New Column
    ↓
Old Column Removed Later
```

This prevents a single deployment from requiring simultaneous application and database incompatibility.

---

# 14. Backward Compatibility

During rolling or staged deployment, the database must remain compatible with:

* current application version;
* new application version;
* trusted offline synchronization where applicable;
* background workers that may still run the previous version.

A migration must not immediately remove a field that an older application version still requires.

---

# 15. Forward Compatibility

New database structures should normally be introduced before the application starts depending on them.

Example:

```text
Migration:
Add nullable column

Then:

Application:
Starts using column
```

Not:

```text
Application:
Immediately expects missing column

Then:

Migration
```

The second sequence can cause production failure.

---

# 16. Column Addition

Adding a nullable column is normally preferred when compatibility is required.

Example:

```sql
ALTER TABLE order_items
ADD COLUMN price_snapshot NUMERIC(19,4);
```

Application code can initially support both old and new rows.

A later backfill can populate historical values.

---

# 17. Adding NOT NULL Columns

Adding a required column to a large existing table should normally follow:

```text
1. Add nullable column
2. Deploy compatible application
3. Backfill existing rows
4. Validate completeness
5. Add NOT NULL constraint
```

Avoid directly adding a required column to a populated large table unless the database operation is proven safe for the expected workload.

---

# 18. Column Defaults

Defaults must be used deliberately.

A default should represent an actual business/system invariant.

A default must not hide missing migration logic.

Example:

```text
is_active = true
```

may be appropriate if the business invariant defines newly created records as active.

An arbitrary default that changes historical meaning is prohibited.

---

# 19. Column Rename

A direct rename can break older application versions.

Preferred strategy:

```text
Old Column
+
New Column
      ↓
Dual Read / Dual Write
      ↓
Backfill
      ↓
Switch Application
      ↓
Remove Old Column
```

A direct rename is allowed only when deployment compatibility is guaranteed.

---

# 20. Column Type Changes

Type changes require explicit compatibility analysis.

Examples:

* INTEGER → BIGINT;
* INTEGER → NUMERIC;
* VARCHAR length change;
* TEXT → structured type;
* timestamp precision changes.

The migration must verify:

* existing values;
* conversion safety;
* indexes;
* constraints;
* application serializers;
* API compatibility;
* offline payload compatibility.

---

# 21. Monetary Type Changes

Financial fields must use the project's approved monetary representation.

A migration changing monetary storage must preserve:

* exact value;
* currency semantics;
* historical transaction amount;
* rounding behavior.

Floating-point conversion for financial values is prohibited.

---

# 22. Quantity Type Changes

Inventory quantities may contain fractional values.

Changes to quantity precision must preserve:

* existing stock;
* inventory transaction quantities;
* recipe quantities;
* production output;
* purchase quantities;
* historical reports.

The migration must not silently round quantities.

---

# 23. Timestamp Changes

Timestamp changes must preserve historical event ordering.

Important timestamps include:

* creation time;
* update time;
* effective time;
* transaction time;
* synchronization time;
* audit time;
* report generation time;
* lifecycle/deletion time.

Migration logic must not replace historical timestamps with migration execution time.

---

# 24. Table Creation

New tables should normally be created before application code starts writing to them.

A new table migration should include:

* primary key;
* required ownership fields;
* foreign keys;
* required constraints;
* essential indexes.

Nonessential indexes may be added separately if their creation could be expensive.

---

# 25. Foreign Key Addition

Adding a foreign key to existing data requires validation.

Before enabling the constraint:

```text
Find orphan rows
        ↓
Resolve invalid data
        ↓
Validate relationship
        ↓
Create constraint
```

Existing invalid data must not be silently discarded.

---

# 26. Tenant Ownership During Migration

Every tenant-owned migration must preserve:

```text
Business
   ↓
Branch / Employee / Product / Order / ...
```

A data migration must never move a row between Businesses accidentally.

Business UUID must remain unchanged.

---

# 27. Branch Ownership During Migration

Branch-scoped records must preserve Branch ownership.

A migration must not:

* assign Branch A data to Branch B;
* create cross-Business Branch references;
* infer Branch ownership from unreliable client data.

When ownership is derived indirectly, the migration must validate the complete ownership chain.

---

# 28. Cross-Business Validation

For tenant-owned relationships:

```text
Child.Business UUID
==
Parent.Business UUID
```

must remain valid where the model requires direct Business ownership.

Cross-Business references are prohibited unless explicitly defined as platform-level shared data.

---

# 29. Data Migration Separation

Structural migrations and large data transformations should be separated when possible.

Example:

```text
Migration 1:
Add new column

Migration 2:
Application compatibility

Job:
Backfill data

Migration 3:
Add final constraint
```

This reduces migration lock duration.

---

# 30. Backfill Strategy

Large backfills must be:

* bounded;
* resumable;
* observable;
* idempotent;
* batch-based.

Example:

```text
Batch 1 → 1–10,000
Batch 2 → 10,001–20,000
Batch 3 → 20,001–30,000
```

A failed batch must be safely retryable.

---

# 31. Backfill Does Not Own Business Transactions

A backfill must not reinterpret current business operations.

For example, a historical Order price backfill must use historical source data, not the current Product price.

Historical data must not be recalculated from current configuration unless explicitly required and documented.

---

# 32. Backfill Concurrency

Backfill processes must coexist safely with normal application traffic.

Strategies may include:

* primary-key ranges;
* `SKIP LOCKED` where appropriate;
* small batches;
* short transactions;
* throttling;
* scheduled low-load execution.

The strategy must not starve POS transactions.

---

# 33. Index Creation

Large production indexes should normally be created using PostgreSQL concurrent index creation where appropriate.

Example:

```sql
CREATE INDEX CONCURRENTLY ...
```

This reduces blocking of normal writes.

The exact migration implementation must account for the fact that concurrent index creation has transaction restrictions.

---

# 34. Index Removal

Before removing an index:

1. confirm it is unused;
2. inspect query plans;
3. verify no uniqueness requirement depends on it;
4. verify foreign-key performance;
5. verify reporting queries;
6. remove it through a migration.

Index removal must not be based only on application code search.

---

# 35. Constraint Addition

A new constraint should be introduced only after existing data satisfies it.

For large tables, validation may be staged.

Conceptually:

```text
Existing Data
    ↓
Detect Violations
    ↓
Repair
    ↓
Validate
    ↓
Enforce Constraint
```

---

# 36. Constraint Tightening

Changing:

```text
nullable → NOT NULL
```

or equivalent integrity rules is a high-risk operation.

The migration must first prove that existing rows satisfy the new rule.

---

# 37. Unique Constraint Changes

Unique constraints must account for:

* Business scope;
* Branch scope;
* active/inactive state;
* historical rows;
* concurrency.

Example:

```text
Business + Product Code
```

may require uniqueness within Business rather than globally.

---

# 38. Partial Unique Constraints

PostgreSQL partial unique indexes may be used for lifecycle/state-specific uniqueness.

Example:

```text
Only one ACTIVE cash session per register.
```

Conceptually:

```sql
CREATE UNIQUE INDEX ...
ON cash_sessions(register_id)
WHERE status = 'OPEN';
```

The exact state model must match the authoritative system definition.

---

# 39. Enum Changes

Database enums require careful compatibility handling.

Adding a new enum value may be safer than removing or renaming one.

Removing an enum value can break:

* old application versions;
* offline payloads;
* historical data;
* background workers.

Reference tables may be preferred where values change frequently or require metadata.

---

# 40. Reference Data Migrations

Reference data includes controlled values such as:

* system configuration values;
* permission definitions;
* notification types;
* system status definitions where modeled as tables.

Reference-data migrations must be:

* deterministic;
* idempotent where appropriate;
* version-controlled.

Production data created by users must not be overwritten by seed migrations.

---

# 41. Seed Data vs Production Data

Development seed data must remain separate from production business data.

Migration scripts must not reset or recreate real Business records.

A migration must never contain broad destructive commands such as:

```sql
DELETE FROM businesses;
```

outside a controlled test environment.

---

# 42. Historical Data Preservation

Migrations must preserve:

* Orders;
* Order Item snapshots;
* Payments;
* Refunds;
* Cash Sessions;
* Inventory Transactions;
* Recipe Versions;
* Set Versions;
* Configuration Versions;
* Audit Events;
* Report Versions;
* Synchronization history.

Historical data must not be rewritten merely to simplify a new schema.

---

# 43. Snapshot Preservation

When a migration introduces normalized references for previously denormalized historical information, the historical snapshot must remain available.

Example:

```text
Historical Order
    ↓
Product UUID
    +
Historical Product Name
    +
Historical Price
```

A new Product reference must not eliminate historical snapshot data required for reconstruction.

---

# 44. Audit Migration

Audit records are immutable.

Schema migrations may add metadata fields to audit records, but migration logic must not modify the historical meaning of existing audit events.

If a new field is introduced:

```text
Existing Event
    ↓
NULL / explicitly unknown
```

may be preferable to inventing a historical value.

---

# 45. Report Version Migration

Report versions are immutable.

A migration must not rewrite an existing finalized report version.

If the schema requires additional report metadata:

* add the new field;
* preserve old values;
* use explicit unknown/null semantics where necessary.

---

# 46. Configuration Version Migration

Configuration history must remain reconstructable.

A migration must preserve:

* configuration version identity;
* previous version;
* effective boundary;
* creator;
* approval;
* state;
* affected Business/Branch/Product/Set.

Historical configuration must not be flattened into only the latest state.

---

# 47. Offline Compatibility

Database migrations must consider offline clients.

A server-side schema change must not make previously generated offline events impossible to process unexpectedly.

Where event payload structure changes:

```text
Old Payload
+
New Server
```

must remain supported for the defined compatibility period.

---

# 48. Synchronization Event Migration

Synchronization events must preserve:

* Event UUID;
* transaction UUID;
* device UUID;
* Business UUID;
* Branch UUID;
* original event timestamp;
* synchronization state;
* conflict state.

Migration must not generate new identities for existing offline events.

---

# 49. Idempotency Preservation

Migration changes must preserve idempotency keys.

For example:

```text
Offline Event UUID
Payment UUID
Order UUID
Configuration Operation UUID
```

must remain unique according to their defined scope.

A migration must not accidentally remove or weaken these uniqueness guarantees.

---

# 50. Database Version Compatibility

Application releases should define supported database schema versions.

Conceptually:

```text
Application Version
        ↓
Supported Schema Range
```

An application must not start against an incompatible schema unless explicitly operating in a migration/deployment mode.

---

# 51. Migration Ordering During Deployment

Recommended deployment sequence:

```text
1. Backup / recovery readiness
2. Deploy compatible database migration
3. Validate migration
4. Deploy compatible application
5. Start workers
6. Validate application
7. Monitor
```

For expand/contract:

```text
Expand DB
   ↓
Deploy compatible application
   ↓
Backfill
   ↓
Switch behavior
   ↓
Contract DB
```

---

# 52. Worker Compatibility

Background workers may run independently from web/POS processes.

A migration must consider workers that may still process:

* notifications;
* reports;
* synchronization;
* deletion jobs;
* audit/outbox events;
* payroll;
* inventory jobs.

Workers must not fail because a field was removed while an older worker is still active.

---

# 53. Scheduled Jobs

Scheduled jobs must verify schema compatibility before execution.

If a job requires a new schema feature:

```text
Schema Ready
      ↓
Job Enabled
```

not:

```text
Job Enabled
      ↓
Schema Later
```

---

# 54. Migration Locking

Migrations must consider PostgreSQL locks.

Before executing a production migration, evaluate:

* table size;
* active queries;
* expected lock duration;
* index creation time;
* concurrent writes;
* transaction duration.

A migration that can block POS traffic for an unacceptable period must be redesigned.

---

# 55. Long-Running Migration

Long-running operations should be separated from normal schema changes.

Examples:

* large backfills;
* historical recalculation;
* data normalization;
* mass updates.

Use:

```text
Migration
+
Background Data Job
```

where appropriate.

---

# 56. Transaction Boundaries

Each migration must define its transaction requirements.

Small atomic schema changes should normally remain transactional.

Long-running operations may require staged execution.

A migration must not leave the database in a partially understood schema state.

---

# 57. Non-Transactional PostgreSQL Operations

Some PostgreSQL operations have transaction restrictions.

For example:

```sql
CREATE INDEX CONCURRENTLY
```

cannot be handled like an ordinary transactional DDL operation.

The migration implementation must explicitly account for such behavior.

---

# 58. Migration Failure

If a migration fails:

1. stop dependent deployment;
2. record failure;
3. inspect database state;
4. determine whether transaction rollback occurred;
5. determine whether partial work remains;
6. validate schema version;
7. recover using rollback or corrective migration;
8. rerun only after state is understood.

Blind reruns are prohibited.

---

# 59. Failed Migration State

The system must never assume:

```text
Migration failed
=
Database unchanged
```

Some operations may have committed partial work.

Migration recovery must inspect actual database state.

---

# 60. Rollback Strategy

Rollback strategy depends on change type.

### Reversible

Examples:

* add nullable column;
* add table;
* add noncritical index.

Downgrade may be possible.

### Conditionally reversible

Examples:

* data transformation;
* type conversion.

Requires validated reverse transformation.

### Irreversible

Examples:

* destructive deletion;
* loss of original precision;
* permanent data transformation.

These require forward recovery or backup restoration strategy.

---

# 61. Forward Recovery

For production systems, forward recovery is often preferred over destructive downgrade.

Example:

```text
Bad Migration
     ↓
Detect Problem
     ↓
Corrective Migration
     ↓
Validate
```

This preserves already-created production history.

---

# 62. Downgrade Policy

Every migration should define whether downgrade is:

* safe;
* conditionally safe;
* unsupported.

A downgrade must not be executed merely because it exists in the migration file.

If data would be lost, downgrade must be treated as unsafe.

---

# 63. Production Rollback Prohibition

Automatic application rollback must not automatically imply database downgrade.

Example:

```text
Application v2 fails
```

does not mean:

```text
Database downgrade immediately
```

The schema may already contain data created by v2.

Database recovery must be separately evaluated.

---

# 64. Emergency Migration

Emergency database changes are allowed only when required to protect:

* data integrity;
* availability;
* security;
* critical production recovery.

Emergency changes must be:

* authorized;
* recorded;
* documented;
* reconciled into source-controlled migrations afterward.

---

# 65. Manual SQL in Production

Direct manual SQL should normally be prohibited.

If emergency SQL is required:

* use reviewed SQL;
* record operator;
* record timestamp;
* record reason;
* record affected scope;
* record result;
* create a permanent migration or corrective record afterward.

---

# 66. Tenant-Safe Data Migration

Tenant data migrations must always identify the Business scope.

Preferred pattern:

```sql
UPDATE some_table
SET ...
WHERE business_id = :business_id
  AND ...
```

Broad unrestricted updates are prohibited for tenant-owned data migrations.

---

# 67. Branch-Safe Data Migration

Branch-scoped migrations must include Branch scope when required.

Example:

```sql
WHERE business_id = :business_id
  AND branch_id = :branch_id
```

A migration must not infer Branch from user/client state.

---

# 68. Batch Scope

Large tenant data migrations should process bounded scopes.

Possible hierarchy:

```text
Business
   ↓
Branch
   ↓
Primary Key Range
   ↓
Batch
```

This allows progress tracking and recovery.

---

# 69. Deletion Migration

Schema deletion and Business data deletion are different operations.

The Business lifecycle deletion process defined in:

`24_Data_Lifecycle_and_Deletion_Data_Model.md`

must not be implemented as a generic schema migration.

Tenant deletion is an operational data-lifecycle process.

---

# 70. Business Lifecycle Compatibility

Database migrations must preserve lifecycle states:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

A migration must not accidentally reactivate a Business.

---

# 71. Deleted Business Protection

Migration jobs must not recreate or reinitialize deleted Business records.

Deleted Business UUIDs must never be reused.

---

# 72. Migration and Subscription

Subscription state must not be silently changed by schema migration.

A migration may transform subscription structure, but must preserve:

* subscription history;
* current state;
* expiry;
* entitlement state;
* lifecycle consequences.

---

# 73. Index Migration Coordination

When changing indexes:

```text
Application Query Change
        ↓
New Index
        ↓
Query Plan Validation
        ↓
Old Index Removal
```

The old index should remain until the new query strategy is confirmed where compatibility requires it.

---

# 74. Query Compatibility

A schema migration must consider queries from:

* API;
* POS;
* background workers;
* reports;
* synchronization;
* administration;
* exports.

A column or table must not be removed merely because one code path no longer uses it.

---

# 75. ORM Model Compatibility

SQLAlchemy model changes must be synchronized with migration changes.

The following state is invalid:

```text
SQLAlchemy Model ≠ Database Schema
```

except during explicitly designed expand/contract phases.

---

# 76. Autogenerate Policy

Alembic autogeneration may be used to detect differences.

However:

**Generated migration code must always be reviewed manually.**

Autogenerate must not be treated as proof of migration correctness.

---

# 77. Migration Review Checklist

Every migration review should verify:

* revision ID;
* parent revision;
* table ownership;
* Business isolation;
* Branch isolation;
* foreign keys;
* indexes;
* unique constraints;
* nullability;
* defaults;
* historical integrity;
* data conversion;
* locking;
* performance;
* compatibility;
* rollback strategy;
* offline compatibility;
* worker compatibility;
* reporting compatibility.

---

# 78. Migration Testing

Migrations must be tested in automated environments.

Tests should cover:

* empty database;
* current schema;
* realistic populated database;
* historical data;
* multiple Businesses;
* multiple Branches;
* active Cash Sessions;
* open Orders;
* pending synchronization;
* audit records;
* report versions;
* lifecycle states.

---

# 79. Upgrade Testing

Test:

```text
Previous Schema
      ↓
Migration
      ↓
Expected New Schema
```

The test must verify both schema structure and important data.

---

# 80. Fresh Database Testing

A fresh installation must be able to build the complete schema from migration history.

```text
Empty PostgreSQL
       ↓
All Migrations
       ↓
Current Schema
```

This prevents migration history from depending on undocumented manual setup.

---

# 81. Upgrade From Supported Versions

The project should define supported upgrade paths.

Example:

```text
N-2 → N-1 → N
```

If direct upgrades from older versions are unsupported, the requirement must be explicit.

---

# 82. Migration Idempotency

A migration itself normally executes once through Alembic revision tracking.

Data migration jobs must additionally be idempotent where retries are expected.

A retry must not:

* duplicate data;
* duplicate configuration versions;
* duplicate audit events;
* duplicate payments;
* corrupt inventory;
* change historical values.

---

# 83. Migration Metadata

Migration execution should record operational metadata where appropriate:

* revision;
* environment;
* start time;
* completion time;
* operator/deployment identity;
* result;
* duration;
* failure information.

The Alembic revision table remains the authoritative schema version marker.

---

# 84. Migration Observability

Production migration monitoring should expose:

* current revision;
* target revision;
* migration duration;
* success/failure;
* active migration;
* long-running operation;
* lock waits;
* backfill progress;
* error count.

---

# 85. Migration Logging

Migration logs must not contain sensitive values unnecessarily.

Do not log:

* passwords;
* authentication tokens;
* payment credentials;
* secrets;
* full sensitive customer information.

Logs should contain identifiers and operational context instead.

---

# 86. Migration Audit

Important migration operations should be traceable through operational logs/audit mechanisms.

Audit should distinguish:

```text
Schema Migration
```

from:

```text
Business Data Change
```

A schema migration must not appear as if an ordinary employee modified every affected business record.

---

# 87. Data Migration Actor

For system-generated data transformations:

```text
Actor = SYSTEM
```

must be distinguishable from an employee action.

The migration revision and deployment identity should identify the technical cause.

---

# 88. Production Migration Authorization

Production migrations must require appropriate deployment authorization.

At minimum:

* reviewed migration;
* approved release;
* database backup/recovery readiness;
* migration execution authorization.

---

# 89. Backup Before High-Risk Migration

High-risk migrations should be preceded by a verified recovery point.

Backup readiness must consider:

* database size;
* backup completion;
* restore capability;
* retention;
* storage availability.

A backup that cannot be restored must not be treated as sufficient protection.

---

# 90. Restore Testing

Periodic restore testing should verify that database backups can actually reconstruct a usable database.

Restore tests should include:

* schema;
* tenant data;
* historical data;
* migration version;
* critical indexes/constraints.

---

# 91. Migration Performance

Migration performance must consider normal POS load.

The migration must avoid unnecessary:

* full-table locks;
* full-table rewrites;
* huge transactions;
* excessive WAL generation;
* uncontrolled index creation;
* simultaneous heavy background jobs.

---

# 92. WAL Considerations

Large data migrations can generate substantial PostgreSQL WAL.

Before execution, evaluate:

* available disk;
* replication implications;
* backup storage;
* recovery time;
* write throughput.

Large operations may need throttling.

---

# 93. Autovacuum Interaction

Large update/delete migrations may create table bloat.

After large data changes, evaluate:

* dead tuples;
* autovacuum progress;
* table size;
* index bloat;
* query performance.

Manual vacuum/reindex actions should be planned rather than blindly executed.

---

# 94. Migration and POS Availability

POS operations have higher availability priority than noncritical migration work.

A migration that risks blocking:

* order acceptance;
* payment;
* inventory deduction;
* cash session operations

must be redesigned or scheduled appropriately.

---

# 95. Core Transaction Protection

Migrations must not modify transaction boundaries of critical operations accidentally.

Core operations include:

```text
Order Acceptance
Payment
Inventory Deduction
Cash Session State Change
Critical Correction
```

Schema changes affecting these areas require targeted transaction testing.

---

# 96. Migration and Concurrency

Schema changes must consider concurrent:

* Order creation;
* inventory transactions;
* payments;
* cash session transitions;
* synchronization;
* configuration changes.

The migration must not introduce race conditions in existing workflows.

---

# 97. Migration and Row Locks

If a migration requires row-level data changes, locks must be:

* short-lived;
* bounded;
* deterministic.

Avoid holding large row-lock sets for long transactions.

---

# 98. Migration and Deadlocks

Data migrations must use deterministic processing order.

Example:

```text
ORDER BY primary_key
```

can help ensure workers process records consistently.

Multiple migration workers must not update overlapping rows unpredictably.

---

# 99. Migration and Synchronization

Synchronization workers may operate continuously.

A migration affecting synchronization data must preserve:

* Event UUID;
* ordering;
* idempotency;
* status;
* conflict state;
* retry state.

Migration must not mark valid pending events as successfully synchronized.

---

# 100. Migration and Offline Devices

A schema migration must not invalidate already-created offline transactions unless the synchronization protocol explicitly requires it.

If an incompatible payload is unavoidable:

* define compatibility period;
* reject safely;
* preserve the original event;
* create explicit conflict/error state.

---

# 101. Migration and Configuration

Configuration migrations must preserve configuration versions.

If a configuration structure changes:

```text
Old Configuration Version
        ↓
Migration / Translation
        ↓
New Representation
```

must remain reconstructable.

---

# 102. Migration and Reports

Reports may depend on historical schemas or snapshots.

A migration must not change the meaning of finalized reports.

If report generation logic changes because of a schema change:

* future reports use the new logic;
* historical report versions remain immutable.

---

# 103. Migration and Audit

Audit history must remain queryable after migration.

If audit indexes or fields change, migration must preserve:

* event identity;
* timestamp;
* actor;
* Business;
* Branch;
* entity;
* old state;
* new state.

---

# 104. Migration and Notifications

Notification history must remain intact.

A migration must not cause historical notifications to appear as newly generated notifications.

Read/unread states must remain preserved.

---

# 105. Migration and Data Lifecycle

Migration scripts must respect lifecycle state.

A Business in:

```text
READ_ONLY
DELETION_ELIGIBLE
DELETING
```

must not be accidentally treated as ACTIVE.

Lifecycle jobs and schema migrations are separate concerns.

---

# 106. Migration and Permanent Deletion

Permanent deletion must never be hidden inside an ordinary schema migration.

Example:

```text
ALTER TABLE ...
```

must not unexpectedly delete Business data.

Permanent tenant deletion belongs to the controlled lifecycle deletion mechanism.

---

# 107. Migration Naming

Migration names should be descriptive.

Recommended:

```text
add_order_price_snapshot
add_cash_session_correction_limit
create_inventory_transactions
add_branch_price_override
```

Avoid:

```text
fix1
update2
temp
test
change
```

---

# 108. Migration File Naming

Recommended:

```text
<revision>_<description>.py
```

Example:

```text
a81f23_add_branch_price_override.py
```

The filename should remain stable after release.

---

# 109. Migration Documentation

Complex migrations should include comments explaining:

* why the migration exists;
* compatibility assumptions;
* data transformation logic;
* operational risks;
* expected duration;
* rollback/recovery strategy.

Comments should explain intent, not restate every SQL statement.

---

# 110. Migration Dependencies

Migration dependencies must be explicit.

A migration that requires:

```text
Product table
+
Branch table
```

must occur after both required structures exist.

Implicit dependency through application code is prohibited.

---

# 111. Migration Ordering With Domain Changes

Database migrations should follow domain evolution.

Example:

```text
Product
   ↓
Recipe
   ↓
Inventory
   ↓
Order
   ↓
Payment
```

A migration must not introduce a dependent structure before the minimum required parent structure exists.

---

# 112. Migration and Foreign Key Cycles

Circular foreign keys require special handling.

Possible strategies:

* nullable initial reference;
* staged constraint creation;
* deferred constraints where appropriate;
* separate migration phases.

Circular dependency must not be solved by removing required integrity without justification.

---

# 113. Deferred Constraints

PostgreSQL deferred constraints may be used when a legitimate transaction requires temporary intermediate inconsistency.

They should not be used to hide invalid business state.

Use only where:

* transaction boundaries are explicit;
* final state is guaranteed valid;
* performance impact is understood.

---

# 114. Trigger Changes

Triggers must be treated as production code.

Adding or changing triggers requires:

* documented purpose;
* performance analysis;
* recursion analysis;
* transaction impact analysis;
* migration test coverage.

Triggers must not silently implement complex business workflows better handled in application/domain services.

---

# 115. Generated Columns

Generated columns may be used for deterministic database-level derived values.

They are appropriate only when:

* expression is deterministic;
* value is derived directly from row state;
* indexing/query benefit exists;
* application semantics remain clear.

They must not replace complex business calculations.

---

# 116. Database Views

Views may be introduced for:

* reporting;
* reusable read models;
* controlled administrative queries.

Views must not become hidden business-logic containers.

Materialized views require separate refresh and consistency strategy.

---

# 117. Materialized Views

Materialized views may be considered later for expensive reporting.

They require:

* refresh policy;
* freshness definition;
* locking analysis;
* refresh failure handling;
* dependency documentation.

They are not authoritative transaction storage.

---

# 118. Migration and Caching

Redis/cache contents are not migrated as authoritative database state.

After schema changes:

```text
Database
   ↓
New Application
   ↓
Cache Revalidation
```

Stale cache entries must not override the database.

---

# 119. Cache Invalidation During Migration

If schema changes affect cached values:

* invalidate affected cache keys;
* version cache keys where appropriate;
* allow lazy regeneration;
* never rely on old cache state as authoritative.

---

# 120. Migration and API Compatibility

Schema changes may affect API responses.

Before removing or renaming a database field:

* identify API consumers;
* preserve compatibility where required;
* version API behavior if necessary.

Database compatibility and API compatibility must be evaluated together.

---

# 121. Migration and Frontend Compatibility

Frontend releases may temporarily coexist with backend versions.

The database must support the server contract during that period.

A migration must not assume every client updates simultaneously.

---

# 122. Migration and Device Clients

Trusted POS devices may reconnect after a long offline period within their authorization policy.

Schema changes must account for delayed synchronization.

Old offline events must remain processable for the supported compatibility period.

---

# 123. Migration and Subscription Limits

Database migrations must preserve historical subscription limits and entitlements.

A schema transformation must not accidentally:

* increase limits;
* remove limits;
* reactivate blocked features;
* change subscription expiry.

---

# 124. Migration and Permission Data

Permission migrations must preserve effective access rules.

When permissions are renamed or reorganized:

```text
Old Permission
      ↓
Explicit Mapping
      ↓
New Permission
```

must be used.

Do not silently grant broader access because a permission identifier changed.

---

# 125. Migration and Employee Status

Employee status changes must not be caused accidentally by schema migration.

Existing:

```text
ACTIVE
INACTIVE
```

state must remain semantically equivalent after migration.

---

# 126. Migration and Payroll

Payroll history is financial/historical data.

Migration must preserve:

* payroll period;
* calculation snapshot;
* salary basis;
* bonuses;
* finalization;
* corrections.

Current salary configuration must not overwrite historical payroll.

---

# 127. Migration and Inventory

Inventory migrations must preserve:

* stock quantity;
* inventory transactions;
* cost information;
* FIFO layers where applicable;
* production records;
* adjustment history;
* discrepancy history.

A migration must not recalculate stock from current Product or Recipe configuration unless explicitly designed.

---

# 128. Migration and Recipes

Recipe migrations must preserve:

* Recipe identity;
* Recipe Version identity;
* component quantities;
* effective state;
* approval;
* historical usage.

A new Recipe Version must not rewrite previous Recipe Versions.

---

# 129. Migration and Sets

Set migrations must preserve:

* Set identity;
* Set Version;
* component composition;
* price snapshot;
* effective configuration.

Historical Set Orders must remain reconstructable.

---

# 130. Migration and Cash Sessions

Cash Session migrations must preserve:

* session identity;
* register;
* Branch;
* cashier;
* open/close timestamps;
* expected amount;
* actual amount;
* discrepancy;
* corrections;
* handover relationships.

Closed sessions must not be reopened by migration.

---

# 131. Migration and Payments

Payment migrations must preserve:

* Payment UUID;
* Order;
* Business;
* Branch;
* amount;
* method;
* status;
* portions;
* correction history;
* refund relationships.

Migration must not duplicate or reinterpret completed payments.

---

# 132. Migration and Refunds

Refund history must remain separate from original payments.

A migration must not convert refunds into payments or vice versa merely because the schema changes.

---

# 133. Migration and Debt

Debt migration must preserve:

* debt customer identity;
* debt order relationships;
* outstanding balance;
* partial repayments;
* payment allocation.

Duplicate phone numbers must remain valid where the business model permits them.

---

# 134. Migration and Orders

Order migrations must preserve:

* Order UUID;
* Business;
* Branch;
* Cash Session;
* employee attribution;
* order type;
* status;
* financial snapshot;
* table context;
* kitchen ticket relationships.

Order identity must never be regenerated during migration.

---

# 135. Migration and Order Numbers

Customer-facing order numbers are scoped to Cash Session.

If order-number schema changes:

```text
Business
+
Branch
+
Cash Session
+
Customer-facing number
```

must preserve its defined uniqueness semantics.

Historical order numbers must remain unchanged.

---

# 136. Migration and Tables

Table state is operational.

Migration must not incorrectly mark active tables as free or occupied.

Open Order relationships must be preserved.

---

# 137. Migration and Attendance

Attendance records must preserve original timestamps and employee identity.

Corrections must remain distinguishable from original attendance records.

---

# 138. Migration and Notifications

Notification recipient state must remain preserved.

A schema migration must not reset all:

```text
read
```

states to:

```text
unread
```

unless explicitly required and documented.

---

# 139. Migration and Audit Immutability

Migration operations must not update historical audit rows solely to fit a new schema.

If a compatibility field is needed, use:

* NULL;
* explicit unknown;
* derived metadata where clearly marked.

---

# 140. Migration and Report Immutability

Existing report versions must remain immutable.

If a new report schema is required:

```text
Old Report Version
+
New Report Version Schema
```

must coexist where historical reconstruction requires it.

---

# 141. Migration and Deletion Registry

Deletion/lifecycle metadata must remain available during schema evolution.

The migration must preserve:

* Business UUID;
* deletion eligibility;
* deletion job;
* deletion phase;
* deletion timestamp;
* completion state.

---

# 142. Migration and Background Jobs

Every background job that depends on changed tables must be reviewed.

Affected jobs may include:

* synchronization;
* reports;
* notifications;
* lifecycle deletion;
* payroll;
* inventory;
* audit processing.

---

# 143. Migration and Queue Messages

Queued messages may contain old schema assumptions.

During expand/contract:

```text
Old Message
New Consumer
```

should remain supported where required.

A queue message must not be silently discarded because its payload uses an older supported version.

---

# 144. Migration and Outbox

Outbox records are transactional integration data.

Migration must preserve:

* Event UUID;
* aggregate/entity identity;
* Business;
* Branch;
* event type;
* payload;
* status;
* retry metadata.

An outbox migration must not cause already-published events to be published again.

---

# 145. Migration and Idempotent Workers

Workers must remain idempotent after schema changes.

If a worker retries after migration:

```text
Same Event UUID
```

must produce the same intended logical result.

---

# 146. Production Migration Procedure

Recommended production procedure:

```text
1. Review release
2. Verify backup/recovery readiness
3. Verify migration target
4. Verify application compatibility
5. Check active sessions/traffic
6. Execute migration
7. Verify schema
8. Deploy compatible application
9. Verify workers
10. Run smoke tests
11. Monitor
12. Record completion
```

---

# 147. Migration Smoke Tests

After production migration, verify critical paths:

* login;
* Business context;
* Branch context;
* POS loading;
* menu loading;
* order creation;
* order acceptance;
* inventory deduction;
* payment;
* cash session;
* synchronization;
* report access.

---

# 148. Migration Verification Queries

Verification should include:

* current Alembic revision;
* required tables;
* required columns;
* required indexes;
* constraints;
* row counts where appropriate;
* Business isolation;
* active Cash Sessions;
* pending synchronization;
* critical application queries.

---

# 149. Migration Health Gate

A migration should be considered successful only after:

```text
Schema Valid
AND
Application Compatible
AND
Critical Transactions Healthy
AND
No Unexpected Errors
```

---

# 150. Migration Timeout

Production migration operations should have explicit operational time expectations.

A migration exceeding its expected duration should trigger investigation rather than being left indefinitely.

---

# 151. Migration Cancellation

Cancellation must be handled safely.

Before terminating a migration, determine:

* current PostgreSQL state;
* active transaction;
* locks;
* partial data changes;
* Alembic revision state.

Do not terminate blindly.

---

# 152. Migration Deadlock Recovery

If a migration encounters deadlock:

1. capture error;
2. inspect blocking sessions;
3. determine conflicting operation;
4. retry only when safe;
5. redesign migration if repeated.

Repeated deadlocks indicate a migration design problem.

---

# 153. Migration Lock Monitoring

Production operations should monitor:

* waiting locks;
* blocked POS queries;
* migration transaction duration;
* long-running queries.

Migration execution must be stopped/reworked if it threatens critical operations.

---

# 154. Migration Resource Limits

Large migrations should respect operational limits for:

* CPU;
* memory;
* disk;
* WAL;
* connection count;
* lock duration.

Migration workers must not consume the entire database connection pool.

---

# 155. Migration Connection Strategy

Migration execution should use a controlled database connection.

Long-running data jobs should not consume all application connections.

The migration process must be separated from normal web/POS connection pool capacity where practical.

---

# 156. Migration Environment Separation

Migrations must be tested in:

```text
Development
   ↓
CI
   ↓
Staging
   ↓
Production
```

Production must never be the first environment where a migration is executed.

---

# 157. Staging Data

Staging should use realistic schema and representative data characteristics.

Sensitive production data should not be copied into staging without appropriate protection and authorization.

---

# 158. Production-Like Testing

High-risk migrations should be tested using:

* similar row counts;
* similar index sizes;
* representative Business count;
* representative Branch count;
* representative Order volume;
* historical data.

Small test databases cannot reliably predict large-table migration behavior.

---

# 159. Migration Load Testing

For high-risk changes, measure:

* migration duration;
* lock wait;
* write throughput;
* POS latency;
* query latency;
* WAL generation;
* CPU;
* memory;
* disk growth.

---

# 160. Migration Success Criteria

A migration is successful when:

1. expected revision is applied;
2. schema matches expected definition;
3. data integrity is preserved;
4. critical queries work;
5. POS operations work;
6. synchronization works;
7. background jobs work;
8. no unexpected tenant isolation violations exist;
9. monitoring is healthy.

---

# 161. Migration Failure Criteria

Migration is considered failed if:

* schema is partially incompatible;
* critical transaction fails;
* data integrity is violated;
* Business isolation is violated;
* required index/constraint is missing;
* background jobs fail because of schema incompatibility;
* offline synchronization becomes invalid;
* migration blocks critical POS operations beyond the accepted threshold.

---

# 162. Corrective Migration

A corrective migration should:

* identify the failed state;
* preserve valid existing data;
* correct the schema/data;
* remain source-controlled;
* be tested;
* include recovery notes.

---

# 163. Migration Version Verification

Application startup may verify that the database is within a supported schema range.

Conceptually:

```text
Database Revision
       ↓
Supported?
   ├── Yes → Start
   └── No  → Fail Safely
```

The application must not silently operate against an incompatible schema.

---

# 164. Startup Migration Policy

Production application startup should not blindly execute arbitrary migrations.

A separate controlled deployment step is preferred.

This prevents multiple application instances from competing to perform schema changes.

---

# 165. Multiple Application Instances

If multiple application instances exist, only the authorized migration process should perform schema migrations.

Application instances should detect the resulting schema version rather than independently running migrations.

---

# 166. Migration and Connection Pool

During migration deployment:

* avoid exhausting the database;
* control worker startup;
* coordinate connection counts;
* verify pool capacity.

A migration must not accidentally prevent the application from acquiring required connections.

---

# 167. Migration and Readiness

A deployment should expose a readiness state that distinguishes:

```text
Application Process Started
```

from:

```text
Database Schema Compatible
```

Only compatible instances should receive normal traffic.

---

# 168. Migration and Health Checks

Health checks should detect:

* database unavailable;
* incompatible schema;
* failed critical query;
* migration in progress where relevant.

A health check must not perform destructive database operations.

---

# 169. Migration Security

Migration credentials must have only the required privileges.

Migration credentials may require more privileges than runtime application credentials, but they should still be controlled and protected.

Runtime application users should not automatically have unrestricted DDL privileges.

---

# 170. Migration Secrets

Migration credentials must not be stored in:

* source code;
* migration files;
* Git history;
* logs.

Secrets must come from the deployment secret-management mechanism.

---

# 171. SQL Injection in Data Migrations

Migration SQL must not interpolate untrusted values directly.

Use parameterized queries where dynamic values are required.

Tenant identifiers, IDs, and migration parameters must be validated.

---

# 172. Migration Input

Production migration scripts should not depend on arbitrary user input.

Required operational parameters must be:

* explicitly defined;
* validated;
* logged safely;
* reviewed.

---

# 173. Migration Reproducibility

Given the same:

```text
Database State
+
Migration Revision
```

the migration should produce the same intended schema/data result.

Time-dependent behavior must be explicitly controlled.

---

# 174. Time-Dependent Migrations

Avoid using current time to rewrite historical data unless required.

If a migration must generate timestamps:

* use a defined migration timestamp;
* document the semantics;
* do not pretend it is the original business event time.

---

# 175. UUID Generation During Migration

New UUIDs created for migrated records must be deterministic or safely tracked when reproducibility matters.

Existing UUIDs must never be regenerated.

---

# 176. Migration and Referential Identity

Primary keys and domain identities are historical identities.

Migration must preserve:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Product UUID;
* Order UUID;
* Payment UUID;
* Cash Session UUID;
* Inventory Transaction UUID;
* Audit Event UUID;
* Report Version UUID;
* Sync Event UUID.

---

# 177. Migration and Soft Deletion

Schema changes must preserve soft-deleted records where historical retention requires them.

A migration must not interpret:

```text
deleted_at IS NOT NULL
```

as permission to physically delete the row.

---

# 178. Migration and Archive State

Archived Products, Recipes, Sets, configurations and similar records must remain distinguishable from physically deleted data.

Migration must preserve archive semantics.

---

# 179. Migration and Query Indexes

When a migration changes lifecycle/state fields, corresponding indexes must be reviewed.

Example:

```text
active products
open orders
pending sync events
unread notifications
```

may require partial indexes.

---

# 180. Migration and Query Plans

After index/schema changes, important queries should be validated with:

```sql
EXPLAIN (ANALYZE, BUFFERS)
```

where safe in non-production testing.

Production plan inspection must avoid unsafe workload impact.

---

# 181. Migration and Statistics

Large schema/data changes may require updated PostgreSQL statistics.

After major backfills or transformations, evaluate:

```text
ANALYZE
```

requirements.

Poor statistics can cause query regressions even when the schema is correct.

---

# 182. Migration and Autovacuum

Large data transformations must account for autovacuum.

If a migration creates significant dead tuples:

* monitor autovacuum;
* avoid competing heavy operations;
* evaluate maintenance needs.

---

# 183. Migration Documentation Record

Each significant migration should document:

```text
Migration:
Purpose:
Risk:
Affected Tables:
Affected Queries:
Data Transformation:
Lock Risk:
Compatibility:
Rollback:
Recovery:
Validation:
```

---

# 184. Migration Review Levels

Suggested review levels:

### Low Risk

* additive nullable field;
* small table;
* noncritical index.

### Medium Risk

* constraint change;
* large index;
* configuration schema change.

### High Risk

* Order/Payment/Inventory schema;
* large historical migration;
* tenant ownership change;
* destructive change;
* synchronization schema change;
* lifecycle/deletion change.

High-risk changes require additional review and production validation.

---

# 185. Destructive Change Approval

Destructive changes require explicit approval.

Examples:

* dropping column;
* dropping table;
* deleting historical data;
* changing precision with loss;
* removing historical references.

The migration must explain why preservation is not possible.

---

# 186. Deprecation Period

Before destructive removal, the old schema element should normally be deprecated first.

Example:

```text
Deprecated
   ↓
Unused
   ↓
Validated Unused
   ↓
Removal
```

The deprecation period allows older clients/workers to migrate.

---

# 187. Contract Migration

A contract migration removes obsolete structures only after:

* application no longer depends on them;
* workers no longer depend on them;
* supported clients no longer depend on them;
* offline compatibility period has passed;
* historical data requirements are satisfied.

---

# 188. Migration and API Versioning

If a database change requires API versioning:

```text
API v1
API v2
```

may temporarily share the same expanded database schema.

The old API must not force premature schema removal.

---

# 189. Migration and Frontend Rollout

Frontend rollout may be gradual.

Database schema should remain compatible with supported backend/API versions during the rollout window.

---

# 190. Migration and Offline Rollout

Offline devices may reconnect later.

Migration compatibility windows must therefore consider the maximum supported offline period plus operational safety margin.

Offline authorization expiry remains independent from schema migration compatibility.

---

# 191. Migration and Device Upgrade

A device may synchronize after the server schema has advanced.

The synchronization layer must translate or reject incompatible payloads explicitly rather than corrupting data.

---

# 192. Migration and Conflict Resolution

Schema changes must preserve conflict information.

A migration must not erase:

* conflict identity;
* competing versions;
* resolution actor;
* resolution reason;
* timestamps.

---

# 193. Migration and Audit Reconstruction

A migration must allow future reconstruction of:

```text
What changed?
Who changed it?
When?
Why?
From which version?
To which version?
```

where the underlying domain requires such history.

---

# 194. Migration and Report Reconstruction

Historical reports must remain reconstructable using:

* report version;
* report snapshot;
* transaction snapshots;
* historical configuration;
* historical inventory state where applicable.

---

# 195. Migration and Financial Integrity

Financial migrations require stronger review.

Affected data may include:

* Order totals;
* Payment amounts;
* Refunds;
* Discounts;
* Overpayments;
* Debt;
* Cash discrepancies;
* Payroll.

Migration must never silently change financial meaning.

---

# 196. Financial Backfill

Financial backfills must use explicit source-of-truth rules.

Example:

```text
Historical Order Item Price
```

must be sourced from the historical Order Item snapshot, not current menu price.

---

# 197. Inventory Backfill

Inventory backfills must use historical inventory transactions and approved state rules.

Current Recipe configuration must not be used to reinterpret historical inventory deductions.

---

# 198. Migration and Business Rules

A database migration must not silently introduce a new business rule.

Business-rule changes must be represented in:

* Business Analysis;
* System Analysis;
* Domain Analysis;
* Architecture where applicable;
* Database migration.

The database migration is the implementation mechanism, not the source of business requirements.

---

# 199. Migration and Documentation

Every significant schema change must update relevant documentation.

Potential affected documents:

```text
Business Analysis
System Analysis
Domain Analysis
Architecture
Database
API
Testing
Deployment
Security
```

---

# 200. Migration and ADR

A migration involving an important architectural tradeoff should have an ADR.

Examples:

* partitioning;
* major denormalization;
* database sharding;
* read replica introduction;
* new storage strategy;
* irreversible historical transformation.

---

# 201. Migration and Partitioning

Partitioning is a high-impact schema change.

It should not be introduced solely because a table is large.

Partitioning requires analysis of:

* access patterns;
* partition key;
* tenant distribution;
* time distribution;
* indexes;
* foreign keys;
* maintenance;
* migration path.

---

# 202. Large Table Migration

For very large tables:

```text
Assess Size
   ↓
Assess Query Patterns
   ↓
Add New Structure
   ↓
Backfill in Batches
   ↓
Validate
   ↓
Switch Application
   ↓
Remove Old Structure Later
```

Avoid single massive transactions.

---

# 203. Migration and Table Rewrites

Operations that rewrite a large table require explicit risk analysis.

Evaluate:

* table size;
* lock duration;
* disk requirements;
* WAL;
* replica lag if applicable;
* downtime.

---

# 204. Migration and Replication

If read replicas are introduced later, migrations must consider:

* replication lag;
* DDL replication behavior;
* replica readiness;
* index creation impact;
* failover compatibility.

Primary database remains authoritative.

---

# 205. Migration and Future Sharding

The initial architecture does not require sharding.

Migration design should nevertheless avoid assumptions that make future tenant partitioning impossible.

Business UUID should remain a stable logical tenant identity.

---

# 206. Migration and Multi-Tenant Indexes

Tenant-aware indexes should support common query patterns such as:

```text
business_id
business_id + branch_id
business_id + status
business_id + created_at
business_id + branch_id + created_at
```

Exact indexes are governed by `26_Database_Indexes_and_Query_Strategy.md`.

---

# 207. Migration and Foreign Key Indexes

Foreign keys should have supporting indexes when query/update/delete patterns require them.

Migration review must check whether adding a foreign key also requires an index.

---

# 208. Migration and Unique Indexes

A unique index may simultaneously enforce:

* business-scoped uniqueness;
* branch-scoped uniqueness;
* active-state uniqueness;
* idempotency.

Migration design should avoid redundant duplicate indexes.

---

# 209. Migration and Partial Indexes

Partial indexes are useful for frequently queried operational states.

Examples:

```text
OPEN orders
PENDING synchronization
UNREAD notifications
ACTIVE configuration
OPEN cash sessions
```

Partial predicates must match actual query predicates.

---

# 210. Migration and Index Naming

Index names should be predictable.

Recommended:

```text
ix_<table>_<column>
ix_<table>_<column1>_<column2>
uq_<table>_<scope>_<column>
```

Example:

```text
ix_orders_business_branch_created
uq_cash_sessions_register_open
```

---

# 211. Migration and Constraint Naming

Constraints should have stable names.

Examples:

```text
pk_orders
fk_orders_business
fk_orders_branch
uq_orders_business_number
ck_order_total_nonnegative
```

Stable names make migrations and production diagnostics easier.

---

# 212. Migration and Error Diagnostics

Named constraints improve application error classification.

For example:

```text
Unique violation
Foreign key violation
Check violation
Not-null violation
```

The application may map known constraint failures to safe domain errors.

---

# 213. Migration and Error Compatibility

Renaming constraints may change database error identifiers.

If the application depends on specific constraint names, changes must be coordinated.

---

# 214. Migration and Testing Constraint Errors

Automated tests should verify important constraints by attempting invalid operations.

Examples:

* cross-Business reference;
* duplicate active cash session;
* negative stock;
* duplicate payment UUID;
* duplicate sync event;
* invalid Branch ownership.

---

# 215. Migration and Concurrency Tests

High-risk migrations should be tested concurrently with:

* order acceptance;
* payment;
* inventory updates;
* cash session transitions;
* synchronization.

---

# 216. Migration and Race Conditions

Schema changes must not weaken database-level race protection.

Examples:

```text
Two sales consume final stock
Two cash sessions open
Two identical sync events arrive
Two configuration updates commit
```

Database constraints and transaction logic must continue to enforce correct outcomes.

---

# 217. Migration and Serialization

If JSON/JSONB fields are migrated:

* preserve unknown fields where compatibility requires;
* version payload structures;
* validate required fields;
* avoid destructive normalization without migration strategy.

---

# 218. JSONB Schema Evolution

For structured JSONB data:

```text
Version 1
Version 2
```

may coexist during transition.

The application should explicitly handle supported versions.

---

# 219. Migration and Search Fields

If searchable fields change:

* add new indexed representation;
* backfill;
* validate query behavior;
* switch queries;
* remove old representation later.

---

# 220. Migration and Text Search

Specialized indexes such as GIN or trigram indexes should be introduced only after query requirements justify them.

They must not be added automatically to every text field.

---

# 221. Migration and Audit Growth

Audit/event tables may become very large.

Future migrations may introduce:

* partitioning;
* BRIN indexes;
* archival strategy.

Such changes require separate capacity analysis.

---

# 222. Migration and Time-Based Data

Append-heavy historical tables may benefit from time-oriented indexing.

Migration design should preserve efficient queries by:

```text
Business
+
Branch
+
Time
```

where appropriate.

---

# 223. Migration and Archive Strategy

Archiving must not change the logical identity of records.

If records move to archive storage:

* identity must remain traceable;
* historical references must remain resolvable;
* reports must define whether archived data is included.

---

# 224. Migration and Permanent Archive

Archive operations are not equivalent to deletion.

A migration must not use archive as a hidden deletion mechanism.

---

# 225. Migration and Schema Documentation

The database documentation must remain aligned with actual migrations.

After a migration changes:

* table;
* column;
* relationship;
* constraint;
* index;

the relevant database document should be updated.

---

# 226. Migration and Code Review

Migration code must be reviewed independently from ordinary application code when risk is high.

Reviewers should specifically inspect:

* SQL generated;
* locking behavior;
* data transformation;
* rollback;
* tenant isolation;
* indexes;
* constraints.

---

# 227. Migration and CI

CI should automatically validate:

```text
Migration Syntax
Migration Ordering
Fresh Database Creation
Upgrade Path
Constraint Integrity
Important Query Tests
```

---

# 228. Migration Linting

Where tooling permits, CI should detect:

* duplicate revisions;
* multiple heads;
* invalid imports;
* unsafe SQL patterns;
* missing downgrade documentation;
* inconsistent migration naming.

---

# 229. Migration Drift Detection

The deployed schema should be periodically checked against the expected migration state.

Unexpected schema changes should be treated as configuration drift.

---

# 230. Manual Schema Drift

If production schema differs from migration history:

```text
Stop further schema changes
        ↓
Inspect difference
        ↓
Determine origin
        ↓
Create corrective migration
        ↓
Reconcile state
```

Do not simply overwrite production schema.

---

# 231. Migration and Environment Drift

Development/staging/production may differ in:

* data volume;
* indexes;
* extensions;
* configuration.

Schema structure, however, must be controlled by the same migration history unless explicitly documented.

---

# 232. PostgreSQL Extensions

Database extensions must be managed explicitly.

Examples may include:

* `pgcrypto`;
* future search extensions.

Extension requirements must be documented and provisioned consistently.

---

# 233. Migration and Extension Compatibility

An extension-dependent migration must verify that the extension exists before using extension-specific functionality.

---

# 234. Migration and Collation

Text comparison/collation changes can alter:

* uniqueness;
* sorting;
* search results.

Collation-related migrations require explicit compatibility testing.

---

# 235. Migration and Time Zone

The database timestamp strategy must remain consistent.

Migration must not silently convert historical timestamps to another timezone.

Application/server/database timezone behavior must be documented.

---

# 236. Migration and Numeric Precision

Changes to:

* monetary precision;
* quantity precision;
* percentage precision;

must preserve existing values and business semantics.

---

# 237. Migration and Rounding

If a migration changes numeric representation, rounding must be explicit.

Never rely on implicit database rounding for financial transformations.

---

# 238. Migration and Null Semantics

Changing:

```text
NULL
```

to:

```text
0
```

or another default changes business meaning.

Such transformations require explicit business approval.

---

# 239. Migration and Empty Values

Empty string, NULL, zero and false are distinct where business semantics require it.

Migration must not normalize them blindly.

---

# 240. Migration and Historical Unknown Values

If historical information was not recorded originally, migration must not invent it.

Use explicit:

```text
NULL
UNKNOWN
NOT_AVAILABLE
```

according to the domain model.

---

# 241. Migration and Audit Source

If a migration changes a record for technical reasons, the source should identify:

```text
SYSTEM_MIGRATION
```

rather than impersonating the original employee.

---

# 242. Migration and Business Actor Attribution

Historical actor attribution must never be replaced with the migration operator merely because the row was touched during migration.

---

# 243. Migration and Correction Records

If a data correction changes a business-critical historical record, use the domain's correction mechanism rather than silently modifying the original history.

---

# 244. Migration and Financial Corrections

Financial corrections must remain separate from ordinary schema migration.

A migration must not be used as a hidden mechanism to correct business transactions.

---

# 245. Migration and Inventory Corrections

Inventory corrections must use inventory adjustment/correction rules.

Schema migration must not silently change stock balances without preserving transaction history.

---

# 246. Migration and Cash Corrections

Cash correction rules must remain separate from schema migrations.

A migration must not reopen a closed Cash Session or rewrite a cash discrepancy.

---

# 247. Migration and Payroll Corrections

Payroll correction mechanisms must remain separate.

A schema migration must not silently recalculate finalized payroll.

---

# 248. Migration and Report Corrections

Report correction/versioning remains a reporting concern.

Schema migration must not rewrite historical report results.

---

# 249. Migration and Notification Side Effects

Schema migrations should not trigger ordinary business notifications unintentionally.

For example, a backfill changing an internal field must not generate thousands of:

```text
Stock Low
```

notifications.

---

# 250. Migration and Event Side Effects

Data migrations must explicitly control whether domain events are emitted.

By default, historical backfills should not replay ordinary business events.

If events are required, they must be explicitly designed and idempotent.

---

# 251. Migration and Outbox Side Effects

Backfills must not accidentally populate the outbox as if every migrated row were a new business transaction.

---

# 252. Migration and Search Cache

Search/index caches must be invalidated or rebuilt only when required.

A schema migration must not assume cache state is authoritative.

---

# 253. Migration and Read Models

If read models are derived from transactional data:

```text
Transactional Database
       ↓
Read Model
```

schema migration must define how the read model is rebuilt or migrated.

---

# 254. Migration and Reporting Read Models

Reporting read models may be rebuilt asynchronously.

POS transaction processing must not wait for a heavy reporting rebuild.

---

# 255. Migration and Data Consistency Window

During staged migration, a temporary compatibility period may exist.

The expected state must be documented:

```text
Old + New
```

must not be mistaken for permanent inconsistency.

---

# 256. Migration Completion

A migration phase is complete only when:

* application uses the new structure;
* backfill completed;
* validation passed;
* old structure no longer required;
* monitoring is healthy.

Only then should contract cleanup be scheduled.

---

# 257. Migration Cleanup

Cleanup migrations should be separate from feature migrations when possible.

Example:

```text
Feature Migration
      ↓
Compatibility Period
      ↓
Cleanup Migration
```

This makes rollback and diagnosis easier.

---

# 258. Migration Rollout Documentation

Production release notes should state:

* migration revision;
* schema changes;
* expected duration;
* compatibility requirements;
* operational risk;
* validation;
* rollback/recovery strategy.

---

# 259. Migration Runbook

High-risk migrations require a runbook containing:

```text
Pre-checks
Execution
Monitoring
Validation
Failure Handling
Recovery
Post-checks
```

---

# 260. Migration Post-Checks

After migration:

* verify revision;
* verify constraints;
* verify indexes;
* verify critical queries;
* verify tenant isolation;
* verify POS;
* verify payments;
* verify inventory;
* verify synchronization;
* verify workers;
* verify reports.

---

# 261. Migration Metrics

Useful migration metrics include:

* migration duration;
* rows processed;
* rows remaining;
* batch duration;
* failed batches;
* retry count;
* lock wait;
* WAL volume;
* database CPU;
* database disk;
* query latency;
* POS latency.

---

# 262. Migration Alerts

Alerts should be considered for:

* migration failure;
* excessive duration;
* lock contention;
* disk pressure;
* replication lag;
* repeated backfill failures;
* schema mismatch.

---

# 263. Migration Completion Record

A production migration completion record should contain:

```text
Revision
Environment
Start Time
End Time
Operator
Application Version
Result
Validation Result
Known Issues
Recovery Notes
```

---

# 264. Migration Security Review

High-risk migrations must be reviewed for:

* privilege escalation;
* tenant isolation;
* accidental data exposure;
* unsafe SQL;
* secret leakage;
* cross-Business updates.

---

# 265. Migration Privacy

Migration logs and temporary tables must not expose unnecessary personal data.

If temporary copies are required, their lifecycle must be controlled.

---

# 266. Temporary Migration Tables

Temporary/staging tables may be used for complex transformations.

They must have:

* clear ownership;
* cleanup plan;
* limited lifetime;
* access control.

---

# 267. Migration Staging Tables

Staging tables must not be mistaken for authoritative domain tables.

If retained, they require explicit documentation.

---

# 268. Migration Data Validation

Before finalizing a migration, validate:

```text
Row Count
Null Count
Duplicate Count
Foreign Key Violations
Business Scope
Branch Scope
Financial Totals
Inventory Totals
Historical Integrity
```

The exact checks depend on the affected domain.

---

# 269. Financial Reconciliation

For financial migrations, compare before/after aggregates where possible:

```text
Order Totals
Payment Totals
Refund Totals
Debt Balance
Cash Totals
Payroll Totals
```

Expected differences must be documented.

---

# 270. Inventory Reconciliation

For inventory migrations, compare:

```text
Stock Balance
Inventory Transaction Count
Purchase Totals
Adjustment Totals
Production Totals
```

before and after transformation.

---

# 271. Tenant Reconciliation

For multi-tenant migrations, verify:

```text
Business A rows remain Business A
Business B rows remain Business B
```

and no cross-tenant references were introduced.

---

# 272. Branch Reconciliation

Verify:

```text
Branch A rows remain Branch A
Branch B rows remain Branch B
```

unless an explicitly approved business migration changes ownership.

---

# 273. Migration and Referential Integrity

After migration, validate all relevant:

* foreign keys;
* unique constraints;
* check constraints;
* partial uniqueness;
* lifecycle rules.

---

# 274. Migration and Query Regression

Schema changes can change query plans.

Critical queries should be compared before/after migration where the risk is significant.

---

# 275. Migration and Index Regression

An index migration is not successful merely because the index exists.

The expected query must actually benefit where intended.

---

# 276. Migration and Statistics Regression

After large data changes, query planner statistics should be refreshed and critical query plans rechecked.

---

# 277. Migration and Connection Regression

After schema changes, verify that:

* application connections work;
* worker connections work;
* migration process did not exhaust connections;
* connection pool remains healthy.

---

# 278. Migration and Application Startup

Application startup after migration must not silently perform destructive schema repair.

Schema incompatibility should fail visibly and safely.

---

# 279. Migration and Deployment Rollback

Application rollback and database rollback are independent decisions.

```text
Application Rollback
        ≠
Database Rollback
```

The database must remain compatible with the selected application version.

---

# 280. Migration and Blue/Green Deployment

If blue/green deployment is used later, database changes must support both application versions during the transition.

Expand/contract is the default strategy for incompatible schema changes.

---

# 281. Migration and Rolling Deployment

Rolling deployment requires:

```text
Old Application
+
New Application
+
Shared Database
```

Therefore database compatibility must be maintained until old instances are removed.

---

# 282. Migration and Worker Rolling Deployment

Workers also require compatibility during rolling replacement.

Old workers may process jobs while new workers are starting.

---

# 283. Migration and Queue Drain

Before destructive contract migration, queues should be evaluated for messages produced by the old schema/application.

---

# 284. Migration and Long Offline Clients

A device that has been offline beyond the supported synchronization compatibility period may require:

* resynchronization;
* explicit conflict handling;
* application update;
* controlled reauthorization.

The database migration must not silently reinterpret its historical events.

---

# 285. Migration and Schema Version in Sync Events

Where required, synchronization events may include a payload/schema version.

This allows explicit compatibility handling.

---

# 286. Migration and Payload Versioning

Payload versioning should be preferred over guessing the structure from field presence when multiple versions must coexist.

---

# 287. Migration and Event Ordering

Schema migration must preserve event ordering semantics.

Original event timestamp and sequence/order identifiers must remain unchanged.

---

# 288. Migration and Duplicate Prevention

Migration must preserve unique constraints required to prevent duplicate:

* Orders;
* Payments;
* Inventory Transactions;
* Sync Events;
* Configuration Operations;
* Report Versions.

---

# 289. Migration and Transaction UUIDs

Transaction UUIDs are logical identities.

They must not be regenerated during schema conversion.

---

# 290. Migration and Client UUIDs

Where UUIDs originate from trusted offline clients, the server must preserve the identity after synchronization.

---

# 291. Migration and Server Authority

Migration does not change server authority.

After synchronization:

```text
Server State
```

remains authoritative according to synchronization rules.

---

# 292. Migration and Conflict State

Conflict records must remain separate from successful transactions.

A migration must not mark a conflict as resolved simply because the schema changed.

---

# 293. Migration and Recovery Jobs

If a migration fails during a background process:

* checkpoint progress;
* preserve failure state;
* retry safely;
* escalate after repeated failures.

---

# 294. Migration and Checkpoints

Large backfills should record progress by stable key/range.

Example:

```text
last_processed_id
```

must refer to a stable ordering field.

---

# 295. Migration and Retry

Retry logic must be bounded.

Repeated failure should produce:

```text
FAILED
```

or equivalent operational state requiring review.

---

# 296. Migration and Partial Success

Partial success must be detectable.

Example:

```text
10 batches
7 successful
3 pending
```

must not be reported as complete.

---

# 297. Migration and Resume

Resuming a failed migration must continue from verified state rather than assuming all previous batches succeeded.

---

# 298. Migration and Duplicate Backfill

Backfill jobs must use conditions such as:

```text
WHERE migrated_field IS NULL
```

or stable checkpoints where appropriate.

The exact strategy must preserve correctness under retry.

---

# 299. Migration and Data Validation Before Delete

Before dropping old data:

```text
New Data Verified
AND
Application Switched
AND
Historical Integrity Verified
```

must be true.

---

# 300. Migration and Contract Delay

Contract cleanup should be delayed if:

* offline clients still depend on old structure;
* old workers still exist;
* rollback window is open;
* historical verification is incomplete;
* unexpected query dependencies exist.

---

# 301. Migration and Production Safety Rule

The primary operational rule is:

> A database migration must never trade silent data corruption for deployment convenience.

If the system cannot safely determine the correct transformation, it must stop and require explicit resolution.

---

# 302. Migration and POS Safety Rule

The POS must remain operational whenever reasonably possible.

Schema changes that risk core transaction interruption require explicit operational planning.

---

# 303. Migration and Historical Integrity Rule

Historical data must preserve its original meaning.

Current configuration must never be used to silently reinterpret historical transactions.

---

# 304. Migration and Tenant Isolation Rule

No migration may introduce cross-Business data access or ownership.

Tenant isolation remains mandatory during every migration phase.

---

# 305. Migration and Branch Isolation Rule

Branch-scoped data must remain correctly associated with its Branch.

---

# 306. Migration and Security Rule

Schema evolution must never broaden access permissions accidentally.

Permission changes require explicit mapping and validation.

---

# 307. Migration and Lifecycle Rule

Business lifecycle state must remain authoritative.

Migration must not:

* reactivate deleted data;
* bypass read-only restrictions;
* prevent deletion eligibility;
* resurrect deleted Business data.

---

# 308. Migration and Audit Rule

Important migration-driven data transformations must remain attributable to the system migration process without overwriting original actor history.

---

# 309. Migration and Idempotency Rule

Retries must not create duplicate logical business operations.

---

# 310. Migration and Recovery Rule

Every high-risk migration must have a known recovery strategy before production execution.

---

# 311. Migration and Documentation Rule

Database documentation must remain synchronized with migration history.

---

# 312. Migration and Review Rule

No high-risk migration should be deployed without explicit technical review.

---

# 313. Recommended Migration Checklist

Before migration:

```text
[ ] Requirement confirmed
[ ] Database design updated
[ ] Migration created
[ ] Revision chain valid
[ ] Business ownership checked
[ ] Branch ownership checked
[ ] Constraints reviewed
[ ] Indexes reviewed
[ ] Historical data impact reviewed
[ ] Offline compatibility reviewed
[ ] Worker compatibility reviewed
[ ] API compatibility reviewed
[ ] Rollback/recovery defined
[ ] Backup/recovery readiness verified
[ ] Staging test completed
```

During migration:

```text
[ ] Migration revision verified
[ ] Lock activity monitored
[ ] Database resource usage monitored
[ ] Errors monitored
[ ] POS health monitored
```

After migration:

```text
[ ] Revision verified
[ ] Schema verified
[ ] Constraints verified
[ ] Indexes verified
[ ] Critical queries verified
[ ] POS verified
[ ] Payment verified
[ ] Inventory verified
[ ] Synchronization verified
[ ] Workers verified
[ ] Reports verified
[ ] Tenant isolation verified
[ ] Migration completion recorded
```

---

# 314. System Invariants

The following invariants apply to database migrations and change management:

1. Every production schema change is versioned.
2. Migration history is stored in source control.
3. Applied migrations are immutable.
4. Migration revisions form an ordered graph.
5. Production must not contain unresolved migration heads.
6. Migration execution is deterministic.
7. Manual schema changes are prohibited except authorized emergency operations.
8. Emergency schema changes must be reconciled into source control.
9. Alembic is the authoritative migration mechanism.
10. Application code must not silently alter production schema.
11. Migration ownership must be identifiable.
12. Migration review is required before production.
13. Destructive migrations require explicit approval.
14. Large data migrations are bounded.
15. Large backfills are resumable.
16. Backfills are idempotent where retries are possible.
17. Backfills must not corrupt historical meaning.
18. Business UUIDs are never regenerated.
19. Branch UUIDs are never regenerated.
20. Order UUIDs are never regenerated.
21. Payment UUIDs are never regenerated.
22. Inventory Transaction UUIDs are never regenerated.
23. Cash Session UUIDs are never regenerated.
24. Audit Event UUIDs are never regenerated.
25. Report Version UUIDs are never regenerated.
26. Synchronization Event UUIDs are never regenerated.
27. Tenant ownership is preserved during migrations.
28. Cross-Business references are prohibited unless explicitly defined as platform-level data.
29. Branch ownership is preserved.
30. Tenant-owned data migrations require explicit Business scope where applicable.
31. Branch-owned data migrations require Branch scope where applicable.
32. Historical Orders remain reconstructable.
33. Historical prices remain reconstructable.
34. Historical payments remain reconstructable.
35. Historical refunds remain reconstructable.
36. Historical cash sessions remain reconstructable.
37. Historical inventory transactions remain reconstructable.
38. Historical recipe versions remain reconstructable.
39. Historical set versions remain reconstructable.
40. Historical configuration versions remain reconstructable.
41. Audit history remains immutable.
42. Report versions remain immutable.
43. Migration must not rewrite historical actor attribution.
44. Migration must not impersonate an employee.
45. System-generated migration changes are attributable to SYSTEM migration context.
46. Financial migration must preserve financial meaning.
47. Inventory migration must preserve inventory meaning.
48. Payroll migration must preserve payroll history.
49. Migration must not silently recalculate finalized payroll.
50. Migration must not silently recalculate historical Order totals.
51. Migration must not silently recalculate historical refunds.
52. Migration must not silently recalculate historical inventory deductions.
53. Current Product price must not reinterpret historical Orders.
54. Current Recipe must not reinterpret historical inventory deductions.
55. Current configuration must not reinterpret historical transactions.
56. Expand/contract is preferred for incompatible changes.
57. Old application versions must remain compatible during supported rollout windows.
58. Old workers must remain compatible during supported rollout windows.
59. Supported offline events must remain processable during the compatibility window.
60. Destructive removal must wait until compatibility dependencies are removed.
61. Schema expansion must precede application dependency where required.
62. Required columns should normally be introduced in compatibility-safe stages.
63. Column rename must consider old application versions.
64. Column type changes require conversion analysis.
65. Monetary conversions must preserve exact financial meaning.
66. Quantity conversions must preserve required precision.
67. Timestamp migrations must preserve historical event times.
68. NULL semantics must not be changed silently.
69. Default values must represent valid business/system semantics.
70. Existing invalid foreign-key data must be resolved before enforcing the constraint.
71. Unique constraints must match Business/Branch scope.
72. Partial unique constraints must preserve state-specific invariants.
73. Important foreign keys must have appropriate supporting indexes.
74. New indexes must have a documented query purpose.
75. Index changes must consider write overhead.
76. Large indexes should use safe production creation strategy.
77. Migration must not unnecessarily block POS operations.
78. Migration must not exhaust application database connections.
79. Long-running data work should be separated from short schema transactions.
80. Migration lock duration must be evaluated.
81. Migration deadlocks must be detectable.
82. Data migration processing order should be deterministic.
83. Migration retries must be safe.
84. Partial migration success must be detectable.
85. Migration checkpoints must use stable identifiers.
86. Failed migration state must be inspected before retry.
87. Migration failure must not be hidden.
88. Application rollback does not automatically imply database downgrade.
89. Database downgrade must not cause data loss.
90. Forward recovery is preferred when downgrade is unsafe.
91. Backup readiness must be verified for high-risk migrations.
92. Backup restore capability must be periodically tested.
93. Migration resource usage must be monitored.
94. WAL growth must be considered for large changes.
95. Table/index bloat must be considered after large transformations.
96. PostgreSQL statistics must be refreshed when necessary.
97. Query plans must be validated after important index/schema changes.
98. Critical queries must remain operational after migration.
99. POS order acceptance must remain operational.
100. Payment processing must remain operational.
101. Inventory deduction must remain operational.
102. Cash session operations must remain operational.
103. Synchronization must remain operational.
104. Background workers must remain operational.
105. Reports must remain operational.
106. Migration must not accidentally generate ordinary business notifications.
107. Historical backfills must not replay business events unless explicitly designed.
108. Backfills must not duplicate outbox events.
109. Queue messages must remain compatible during supported deployment windows.
110. Outbox event identity must remain unchanged.
111. Sync event identity must remain unchanged.
112. Sync conflict state must remain unchanged unless explicitly resolved.
113. Migration must not mark pending synchronization as completed.
114. Migration must not resolve synchronization conflicts implicitly.
115. Offline transaction history must remain intact.
116. Device trust data must remain intact.
117. Permission migrations must not broaden access accidentally.
118. Employee status must remain semantically unchanged.
119. Subscription expiry must remain semantically unchanged.
120. Business lifecycle state must remain semantically unchanged.
121. Migration must not reactivate a deleted Business.
122. Migration must not resurrect deleted Business data.
123. Business UUIDs must never be reused.
124. Permanent tenant deletion is not an ordinary schema migration.
125. Lifecycle deletion remains controlled by the data lifecycle mechanism.
126. Archive and permanent deletion remain distinct.
127. Soft deletion and physical deletion remain distinct.
128. Audit records must remain attributable.
129. Migration metadata must not expose secrets.
130. Migration credentials must not be stored in source code.
131. Runtime application credentials should not automatically have unrestricted DDL privileges.
132. Dynamic migration SQL must not use unsafe unvalidated interpolation.
133. Migration logs must minimize sensitive data.
134. Temporary migration data must have controlled lifecycle.
135. Schema drift must be detectable.
136. Unexpected production schema changes must be investigated.
137. Migration files must not be silently rewritten after release.
138. Autogenerated migration code must be reviewed.
139. Fresh database creation must work from migration history.
140. Supported upgrade paths must be tested.
141. Production migrations must be tested in staging first.
142. High-risk migrations require realistic data-volume testing.
143. High-risk migrations require a recovery strategy.
144. Production migration completion must be recorded.
145. Migration success requires schema validation.
146. Migration success requires critical application validation.
147. Migration success requires tenant isolation validation.
148. Migration success requires synchronization validation.
149. Migration success requires worker validation.
150. Migration success requires monitoring validation.
151. Schema changes must be reflected in database documentation.
152. Significant architectural database changes should have ADRs.
153. Business requirements remain the source of business rules.
154. Database migration is an implementation mechanism, not a business requirement source.
155. Migration must never trade silent data corruption for deployment convenience.
156. Migration must preserve historical integrity.
157. Migration must preserve tenant isolation.
158. Migration must preserve Branch isolation.
159. Migration must preserve transaction identity.
160. Migration must preserve idempotency guarantees.
161. Migration must preserve concurrency protections.
162. Migration must preserve financial integrity.
163. Migration must preserve inventory integrity.
164. Migration must preserve security boundaries.
165. Migration must preserve lifecycle boundaries.
166. Migration must preserve auditability.
167. Migration must preserve report history.
168. Migration must preserve offline synchronization compatibility.
169. Migration must preserve background job compatibility.
170. Migration must preserve API compatibility during supported rollout.
171. Migration must preserve frontend compatibility during supported rollout.
172. Migration must not rely on simultaneous client upgrades.
173. Migration cleanup must occur only after compatibility dependencies expire.
174. Contract migrations must be independently validated.
175. Migration execution must be observable.
176. Migration failure must be recoverable.
177. Migration retry must be bounded.
178. Migration progress must be measurable.
179. Migration state must be reconstructable.
180. Migration history must remain auditable.
181. Database schema must remain reproducible from migration history.
182. Production schema must remain aligned with source-controlled migration state.
183. Migration changes must have clear technical ownership.
184. High-risk migrations must receive additional review.
185. Destructive changes require explicit justification.
186. Data loss must never be an accidental migration side effect.
187. Historical unknown values must not be invented.
188. Technical migration changes must not impersonate historical business actors.
189. Migration-generated data must be distinguishable from ordinary business events.
190. Migration must not bypass authorization semantics.
191. Migration must not bypass subscription entitlement semantics.
192. Migration must not bypass lifecycle deletion semantics.
193. Migration must not bypass synchronization validation.
194. Migration must not bypass inventory integrity.
195. Migration must not bypass payment integrity.
196. Migration must not bypass cash-session integrity.
197. Migration must not bypass report immutability.
198. Migration must not bypass audit immutability.
199. Migration must not bypass configuration versioning.
200. Migration must remain safe for ordinary POS hardware and operational workloads.

---

# 315. Related Documents

### Database

* `docs/05_Database/README.md`
* `docs/05_Database/01_Database_Overview.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/05_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `docs/05_Database/10_Set_and_Set_Version_Data_Model.md`
* `docs/05_Database/11_Inventory_and_Warehouse_Data_Model.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/14_Table_and_Waiter_Data_Model.md`
* `docs/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/17_Shift_Handover_Data_Model.md`
* `docs/05_Database/18_Employee_Attendance_and_Payroll_Data_Model.md`
* `docs/05_Database/19_Notification_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`

### Architecture

* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/16_Scalability_and_Performance_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`
* `docs/04_Architecture/19_Architecture_Decisions_and_Tradeoffs.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`

### System Analysis

* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### ADR

* `adr/ADR-001-Documentation-First.md`

---

# 316. Status

**Database Analysis:** Completed.

**Document Status:** Accepted.

**Current Document:** `27_Database_Migrations_and_Change_Management.md`

**Next Document:** `28_Database_Backup_and_Recovery.md`

