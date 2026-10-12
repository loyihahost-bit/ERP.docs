# 08 — Database Development and Migration Workflow

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the development workflow for database schema changes, database structure evolution, migrations, data migrations, constraints, indexes, and database-related development.

The goal is to ensure that database changes are:

* intentional;
* reviewable;
* traceable;
* compatible with the application;
* safe for existing data;
* compatible with deployment strategy;
* testable before release;
* reversible or recoverable when appropriate;
* safe for multi-tenant and multi-branch data;
* consistent with business invariants.

This document focuses on **development-time database change management**.

It does not define:

* production database infrastructure;
* database server topology;
* database runtime operations;
* backup infrastructure;
* disaster recovery architecture;
* production migration execution procedures.

Those concerns belong to the deployment and operations documentation.

---

## 2. Scope

This document covers:

* database schema design during development;
* schema change ownership;
* migration creation;
* migration naming and versioning;
* migration ordering;
* migration dependencies;
* forward-compatible changes;
* expand-and-contract changes;
* data migrations;
* indexes;
* constraints;
* foreign keys;
* tenant and branch isolation;
* transactions;
* concurrency considerations;
* large-table changes;
* destructive changes;
* seed and reference data;
* local development databases;
* test databases;
* migration validation;
* application/schema compatibility;
* API/schema coordination;
* migration review;
* release traceability;
* database development guardrails.

---

# 3. Core Principles

Database development follows these principles:

1. The database is part of the application's contract.
2. Schema changes must be intentional.
3. Every schema change must be represented by a migration.
4. Existing production data must be treated as valuable.
5. A migration must never assume an empty database unless explicitly intended.
6. Application code and database schema must remain compatible during controlled rollout.
7. Destructive changes require explicit analysis and approval.
8. Business-critical invariants should be enforced at the strongest appropriate layer.
9. Tenant and branch boundaries must never be weakened by schema changes.
10. Financial, inventory, recipe, and operational data must preserve historical correctness.
11. Data migrations must be deterministic and testable.
12. Large changes must consider data volume and execution impact.
13. Migration history is immutable once shared with other environments.
14. Existing migration files must not be rewritten to fix new requirements.
15. Every migration must have a clear reason.
16. Database changes must be reviewed together with affected application behavior.
17. Schema evolution must support the project's release strategy.
18. Database correctness has priority over development convenience.

---

# 4. Database as a Shared System Contract

The database is shared by multiple application concerns.

A schema change can affect:

```text
Domain Model
      ↓
Application Services
      ↓
Repositories
      ↓
Database Schema
      ↓
Existing Data
```

It can also affect:

```text
Database Schema
      ↓
API Responses
      ↓
Frontend Behavior
      ↓
Reports
      ↓
Offline Synchronization
```

Therefore, database changes must not be treated as isolated SQL edits.

A change to:

* a column;
* table;
* relationship;
* constraint;
* index;
* enum/value set;
* precision;
* nullability;
* identifier;
* status;
* foreign key;

may affect multiple application layers.

---

# 5. Database Change Ownership

Database changes must have clear ownership.

The developer responsible for a feature is responsible for identifying required schema changes.

The database change owner must verify:

* why the change is required;
* which entities are affected;
* which existing records are affected;
* whether existing data requires transformation;
* whether application code remains compatible;
* whether APIs are affected;
* whether reports are affected;
* whether offline synchronization is affected;
* whether indexes are required;
* whether constraints are required;
* whether tenant/branch isolation remains correct;
* whether migration performance is acceptable.

Database changes must not be introduced as undocumented manual database edits.

---

# 6. Schema Change Lifecycle

The standard lifecycle is:

```text
Requirement
    ↓
Impact Analysis
    ↓
Domain/Data Model Change
    ↓
Migration Design
    ↓
Migration Implementation
    ↓
Application Compatibility
    ↓
Local Migration Test
    ↓
Data Migration Test
    ↓
Integration Tests
    ↓
Code Review
    ↓
Release Traceability
```

A migration is not complete merely because it executes successfully.

It is complete when:

* the intended schema exists;
* existing data remains valid;
* required data transformations succeed;
* application behavior remains correct;
* constraints are correct;
* indexes are appropriate;
* compatibility requirements are satisfied;
* tests provide sufficient evidence.

---

# 7. Schema Change Classification

Every database change should be classified.

## 7.1 Additive Change

Examples:

* adding a nullable column;
* adding a new table;
* adding a new index;
* adding a new optional relationship.

Additive changes are generally lower risk.

However, they still require compatibility analysis.

---

## 7.2 Compatibility Change

Examples:

* changing a field while supporting old application behavior;
* adding a new status while old clients remain active;
* introducing a replacement column;
* changing data representation gradually.

Compatibility changes require controlled rollout.

---

## 7.3 Data Transformation

Examples:

* populating a new column;
* converting old values;
* splitting one field into multiple fields;
* combining existing fields;
* recalculating derived records.

Data transformations require special testing because existing production data is involved.

---

## 7.4 Constraint Change

Examples:

* adding `NOT NULL`;
* adding a unique constraint;
* adding a foreign key;
* restricting allowed values.

Constraint changes can fail because existing data may violate the new rule.

Existing data must be checked before enforcing the constraint.

---

## 7.5 Destructive Change

Examples:

* dropping a column;
* dropping a table;
* deleting historical records;
* removing a relationship;
* reducing data precision;
* changing identifiers irreversibly.

Destructive changes require explicit review.

They must not be hidden inside an ordinary feature migration.

---

# 8. Migration as the Source of Schema Evolution

Every persistent schema change must be represented by a migration.

The migration history should provide a chronological record of how the schema evolved.

Conceptually:

```text
Migration 001
    ↓
Migration 002
    ↓
Migration 003
    ↓
Migration 004
    ↓
Current Schema
```

The current database schema should be reproducible from the migration history.

Manual production-only schema changes create an undocumented divergence and must be avoided.

---

# 9. Migration Naming

Migration names must clearly describe the purpose.

Preferred structure:

```text
<version>_<short_description>
```

Examples:

```text
001_create_restaurants
002_create_branches
003_create_products
004_add_product_code
005_add_inventory_constraints
006_create_recipe_versions
```

Names should describe the business or technical change rather than implementation noise.

Avoid:

```text
001_update
002_fix
003_test
004_new
005_changes
```

A developer should understand the purpose of a migration from its name.

---

# 10. Migration Ordering

Migration order is authoritative.

A migration must not depend on a future migration.

For example:

```text
001_create_restaurants
002_create_branches
003_create_products
004_create_inventory
```

If `004` references `products`, migration `003` must already establish the required table or compatible structure.

Migration dependencies must be explicit.

---

# 11. Migration Immutability

Once a migration has been shared with other environments or used by another developer, its historical content must not be rewritten.

Do not modify an old migration to change its behavior.

Instead:

```text
Existing migration
        +
New migration
        =
Updated schema
```

This preserves migration history.

Exceptions may exist during isolated local development before the migration is shared, but such changes must never create conflicting migration histories.

---

# 12. Schema and Domain Model Separation

The domain model and database schema are related but are not identical concepts.

The domain model describes business concepts and rules.

The database schema describes persistent storage.

Example:

```text
Domain:
Recipe
RecipeVersion
RecipeComponent
Ingredient

Database:
recipes
recipe_versions
recipe_components
ingredients
```

Database structure should support the domain model without forcing database concerns into business logic unnecessarily.

Likewise, database constraints should not be used as a substitute for complete application-level business rules.

---

# 13. Table Design

New tables should have:

* clear ownership;
* clear purpose;
* stable naming;
* appropriate primary key;
* appropriate foreign keys;
* required timestamps;
* appropriate indexes;
* appropriate uniqueness rules;
* tenant/branch scope where required;
* lifecycle strategy;
* audit requirements where applicable.

A table should represent a meaningful persistent concept.

Avoid tables created only because they make a particular implementation easier when the concept does not require independent persistence.

---

# 14. Primary Keys and Identifiers

Primary keys must be stable and unique.

Identifiers must not encode business meaning unless there is an explicit architectural reason.

For example:

```text
Database ID
```

and:

```text
Customer-facing order number
```

should be treated as different concepts when the business requires a short, reusable, human-facing number.

This is particularly important for:

* orders;
* cash register sessions;
* employees;
* inventory records;
* synchronization records.

Business-visible identifiers must not replace stable database identity.

---

# 15. Foreign Keys

Foreign keys should be used where referential integrity is part of the database contract.

A foreign key should communicate:

```text
Child record
      ↓
must reference
      ↓
valid parent record
```

Examples include:

```text
branch → restaurant
employee → restaurant
employee_branch → branch
order → branch
order_item → order
recipe_component → recipe
recipe_component → product
```

Foreign key behavior must be explicitly considered.

Possible deletion behavior includes:

* restrict;
* cascade;
* set null;
* archive at application level.

For historical business records, cascading deletion must be used carefully.

---

# 16. Tenant and Branch Isolation

The FastFood ERP is multi-tenant and multi-branch.

Database development must preserve isolation between:

```text
Restaurant Network
    ↓
Branches
    ↓
Branch-Owned Resources
```

A schema change must answer:

* Who owns this record?
* Is it network-wide?
* Is it branch-specific?
* Can it belong to multiple branches?
* Can it be shared globally?
* Can users from another tenant access it?
* Does the relationship preserve tenant ownership?

Cross-tenant relationships must not be introduced accidentally.

Where a record is branch-scoped, its schema must make branch ownership explicit where appropriate.

---

# 17. Multi-Branch Data Modeling

Branch-specific records must not rely solely on application assumptions.

Examples:

```text
Inventory
Cash Register
Cash Register Session
Branch Expense
Branch Employee Assignment
Branch Menu
Branch Price Override
```

must have clear branch ownership.

Global resources such as shared recipes or global menu definitions must be distinguishable from branch-specific assignments.

A migration that changes ownership or scope must explicitly preserve this distinction.

---

# 18. Nullability

Nullability must represent a meaningful state.

Do not use nullable fields simply because they are convenient during development.

A nullable field should answer:

> What does `NULL` mean?

Possible meanings include:

* unknown;
* not yet provided;
* not applicable;
* not yet calculated;
* intentionally absent.

These meanings must not be confused.

If a value must always exist for business correctness, the schema should normally enforce non-nullability.

---

# 19. Adding a Required Column

Adding a required column to an existing populated table requires special handling.

Unsafe conceptual change:

```text
Existing populated table
        ↓
Add NOT NULL column immediately
```

The change may fail because existing records have no value.

A safer staged approach is:

```text
1. Add nullable column
        ↓
2. Deploy compatible application
        ↓
3. Populate existing records
        ↓
4. Validate populated data
        ↓
5. Enforce NOT NULL
```

The exact strategy depends on data volume and application compatibility.

---

# 20. Expand-and-Contract Pattern

For high-risk schema changes, use an expand-and-contract approach.

## Expand

Introduce the new structure while keeping the old structure functional.

```text
Old schema
    +
New schema
```

## Migrate

Move or synchronize data.

```text
Old data
   ↓
Transformation
   ↓
New structure
```

## Switch

Update application behavior to use the new structure.

## Contract

After the old structure is no longer required:

```text
Remove old dependency
        ↓
Remove old column/table
```

This approach reduces compatibility risk during rolling deployments and staged releases.

---

# 21. Backward Compatibility

Database changes must consider whether old application versions may temporarily interact with the new schema.

A schema change should avoid immediately breaking older compatible application code when the deployment strategy requires coexistence.

Examples of safer changes:

* add new nullable columns;
* add new tables;
* add optional relationships;
* introduce new values before application usage.

Riskier changes:

* immediately rename a required column;
* remove a column still used by old code;
* change data type incompatibly;
* enforce a constraint before existing data is compliant.

Compatibility requirements must be identified before migration implementation.

---

# 22. Column Renaming

A direct rename may be unsafe when multiple application versions can coexist.

A controlled strategy may be:

```text
1. Add new column
2. Support both columns
3. Backfill new column
4. Update application reads
5. Update application writes
6. Validate consistency
7. Remove old column later
```

The exact approach depends on deployment architecture and compatibility requirements.

---

# 23. Data Migrations

A data migration changes existing persistent data rather than only changing schema structure.

Examples:

* populating a new field;
* converting units;
* normalizing old values;
* assigning missing branch ownership;
* transforming historical records;
* creating derived records from existing records.

Data migrations must define:

* source data;
* transformation;
* expected result;
* idempotency behavior;
* validation;
* failure handling;
* affected record scope.

---

# 24. Data Migration Safety

A data migration must not assume that production data is clean.

Before transformation:

```text
Identify
    ↓
Validate
    ↓
Transform
    ↓
Verify
```

Potential issues include:

* unexpected nulls;
* duplicate records;
* invalid historical values;
* old business rules;
* inconsistent legacy data;
* orphaned relationships.

Migration logic must explicitly handle or report these cases.

---

# 25. Idempotency

Where practical, data migrations should be safely repeatable.

For example:

```text
if new_value is not populated:
    populate new_value
```

is generally safer than blindly rewriting all records every time.

A migration should not create duplicate data if execution is retried after an interruption.

When true idempotency is impossible, the migration must clearly define its execution state and recovery behavior.

---

# 26. Large-Table Changes

Large tables require special consideration.

Potential risks include:

* long-running locks;
* excessive transaction duration;
* increased database load;
* application latency;
* disk usage;
* migration timeout;
* replication pressure;
* synchronization delays.

Examples of potentially large tables include:

* orders;
* order items;
* inventory movements;
* audit events;
* synchronization records;
* financial transactions.

A developer must consider data volume before introducing expensive schema operations.

---

# 27. Index Development

Indexes must support actual query patterns.

Before adding an index, consider:

* query frequency;
* filtering columns;
* sorting;
* joins;
* uniqueness requirements;
* tenant scope;
* branch scope;
* write overhead;
* storage cost.

Indexes should not be added automatically to every column.

Example:

```text
orders
├── restaurant_id
├── branch_id
├── status
├── created_at
└── cashier_id
```

A useful index depends on actual query patterns.

For example, a branch/date report may benefit from an index designed around:

```text
branch_id + created_at
```

rather than separate indexes chosen without query analysis.

---

# 28. Composite Indexes

Composite indexes must reflect the order and structure of common queries.

For example:

```text
(branch_id, created_at)
```

and:

```text
(created_at, branch_id)
```

are not automatically equivalent.

Index design must be based on actual access patterns.

Tenant and branch filtering should be considered for multi-tenant queries.

---

# 29. Unique Constraints

Unique constraints should protect true uniqueness requirements.

Examples may include:

```text
tenant + code
branch + device_identifier
restaurant + employee_identifier
```

depending on the business model.

A globally unique constraint must not be used when the value is only required to be unique within a tenant or branch.

---

# 30. Business Invariants in the Database

The database should enforce invariants that can be safely and reliably represented at the database level.

Examples:

* required relationships;
* uniqueness;
* valid references;
* non-negative values where universally applicable;
* valid numeric ranges;
* required ownership.

However, complex business workflows should remain in the application/domain layer.

For example:

```text
Database:
quantity >= 0
```

may be appropriate.

But:

```text
whether an employee is allowed to approve a refund
```

belongs to authorization and application business logic.

---

# 31. Financial Data

Database changes affecting financial data require extra care.

Examples:

* order totals;
* payments;
* refunds;
* cash register sessions;
* expenses;
* salaries;
* discounts.

Financial values must use a representation appropriate for exact business calculations.

Schema changes must preserve:

* historical values;
* currency semantics;
* precision;
* rounding rules;
* transaction relationships;
* auditability.

A migration must never silently alter historical financial meaning.

---

# 32. Inventory Data

Inventory schema changes must preserve inventory history.

Important records include:

* stock movements;
* purchases;
* consumption;
* adjustments;
* discrepancies;
* recipe consumption;
* waste;
* prepared semi-finished products.

A migration must not convert historical inventory movements in a way that changes their original business meaning without explicit approval.

Current stock should be derivable consistently from the defined inventory model.

---

# 33. Recipe Data

Recipe-related schema changes must preserve historical recipe meaning.

Recipe changes may involve:

```text
Product
    ↓
Recipe
    ↓
Recipe Version
    ↓
Recipe Components
```

When historical orders depend on an older recipe version, changing the current recipe must not silently rewrite historical business state.

Schema design should support versioning or another explicit historical model where required.

---

# 34. Status and Enum Changes

Adding a status is generally additive.

Removing or renaming a status is more complex because existing records may contain the old value.

Before changing a status set:

1. identify existing values;
2. identify application consumers;
3. map old values to new values;
4. migrate existing records;
5. update application behavior;
6. validate all affected workflows.

Never assume a status is unused without checking persistent data.

---

# 35. Transactions

Schema-related data transformations must use appropriate transaction boundaries.

A transaction should protect operations that must succeed or fail together.

Example:

```text
Create migration state
        +
Transform related records
        +
Apply consistency changes
```

should be atomic where the database and operation size make this appropriate.

Very large transformations may require controlled batching rather than one enormous transaction.

Transaction design must consider:

* atomicity;
* lock duration;
* rollback cost;
* deadlocks;
* data volume;
* application availability.

---

# 36. Concurrency

Database changes must consider concurrent application activity.

Examples:

* orders being created while inventory is migrated;
* employees updating records while a data transformation runs;
* multiple branches writing simultaneously;
* offline clients synchronizing old data;
* background workers processing records during schema transition.

A migration must not assume the application is idle unless the deployment strategy explicitly guarantees that condition.

---

# 37. Offline Synchronization Compatibility

The ERP supports branch operation during temporary connectivity loss.

Therefore, database changes affecting synchronized entities must consider:

* old offline records;
* synchronization identifiers;
* event ordering;
* schema versions;
* missing new fields;
* default values;
* conflict handling;
* delayed synchronization.

A newly required field must not make valid previously created offline records impossible to synchronize.

Schema evolution must remain compatible with the synchronization strategy.

---

# 38. Seed Data and Reference Data

Not all persistent data is the same.

### Schema

Defines database structure.

### Reference Data

Defines controlled values required by the system.

Examples:

* default statuses;
* system-defined permissions;
* predefined categories;
* supported configuration values.

### Business Data

Created by users and operations.

Examples:

* orders;
* products;
* employees;
* expenses;
* inventory movements.

Reference-data migrations must not accidentally overwrite user-managed business data.

---

# 39. Seed Data Rules

Development seed data should be:

* deterministic;
* reproducible;
* clearly separated from production business data;
* safe to recreate;
* suitable for tests.

Production-required reference data should be managed explicitly.

Do not depend on random development seed data to establish production correctness.

---

# 40. Local Database Workflow

A developer should be able to create or update a local database through the documented migration workflow.

Typical process:

```text
Pull latest code
      ↓
Update dependencies
      ↓
Create/update local database
      ↓
Run migrations
      ↓
Load development reference/seed data
      ↓
Run tests
      ↓
Develop
      ↓
Create migration if schema changes
      ↓
Re-run from clean database
      ↓
Test upgrade from previous schema
```

The local database must not become a hidden source of schema truth.

---

# 41. Clean-Database Validation

A migration should be tested against a clean database.

The expected process is:

```text
Empty Database
      ↓
All Migrations
      ↓
Current Schema
      ↓
Seed/Reference Data
      ↓
Application Tests
```

This confirms that the migration chain can construct the expected current schema.

---

# 42. Upgrade-Path Validation

Clean installation is not enough.

Migrations must also be tested against a database containing existing data.

Conceptually:

```text
Previous Release Schema
        ↓
Existing Test Data
        ↓
New Migration
        ↓
Current Schema
        ↓
Application Tests
```

This validates the real upgrade path.

---

# 43. Migration Testing

Database migrations should be tested for:

* successful execution;
* correct schema;
* correct constraints;
* correct indexes;
* correct foreign keys;
* correct transformed data;
* preservation of unaffected data;
* tenant isolation;
* branch isolation;
* expected failure behavior;
* compatibility where required.

Testing should include both:

```text
Fresh Installation
```

and:

```text
Existing Database Upgrade
```

---

# 44. Migration Failure Testing

Important failure scenarios should be considered.

Examples:

* invalid existing data;
* duplicate values;
* missing parent records;
* unexpected nulls;
* incompatible old values;
* interrupted transformation;
* constraint violation;
* insufficient database capacity;
* lock contention.

The objective is to know:

```text
What fails?
Why does it fail?
What data remains?
How is recovery performed?
```

---

# 45. Migration Validation

After migration, validate:

### Structure

* tables exist;
* columns exist;
* types are correct;
* constraints exist;
* indexes exist;
* foreign keys exist.

### Data

* record counts are reasonable;
* transformed values are correct;
* no unexpected nulls;
* no orphaned records;
* tenant ownership remains correct;
* branch ownership remains correct.

### Application

* affected workflows work;
* APIs work;
* reports work;
* background jobs work;
* synchronization remains compatible.

---

# 46. Schema/API Coordination

A database change may affect API contracts.

Example:

```text
Database column renamed
        ↓
Repository change
        ↓
Application service change
        ↓
API response change
        ↓
Frontend change
```

The database migration must not be reviewed independently when it changes externally visible behavior.

Related API changes must follow:

`09_API_Development_and_Contract_Change_Workflow.md`

---

# 47. Schema/Application Compatibility Matrix

For significant changes, document compatibility explicitly.

Example:

| Application Version | Old Schema | New Schema |
| ------------------- | ---------: | ---------: |
| Previous version    |  Supported |  Supported |
| Current version     |  Supported |  Supported |
| Future version      |        N/A |  Supported |

The exact matrix depends on deployment strategy.

The purpose is to identify whether an application and schema can safely coexist during release transitions.

---

# 48. Destructive Changes

Destructive database operations require explicit review.

Examples:

```sql
DROP COLUMN
DROP TABLE
DELETE historical records
```

Before destructive changes, verify:

* no active code depends on the object;
* no reports depend on it;
* no background jobs depend on it;
* no synchronization process depends on it;
* no offline clients depend on it;
* no historical requirement depends on it;
* required data has been migrated;
* recovery implications are understood.

Destructive operations should normally occur only after a safe transition period.

---

# 49. Historical Data Preservation

Operational and financial history should not be destroyed merely because the current UI no longer displays it.

Examples:

* paid orders;
* refunds;
* cash register sessions;
* inventory movements;
* salary records;
* recipe versions;
* audit records.

Archival or lifecycle policies should be respected.

Schema development must not introduce accidental historical deletion.

---

# 50. Soft Deletion and Archiving

Where the business requires historical preservation, the schema should support an appropriate lifecycle model.

Possible states include:

```text
Active
Archived
Retired
```

The exact model depends on the entity.

Soft deletion must not become an excuse to keep unlimited unnecessary data.

It must represent an intentional business lifecycle.

---

# 51. Migration Dependencies

Migrations may depend on:

* earlier schema;
* earlier reference data;
* application compatibility;
* previous data transformations.

Dependencies must be explicit.

A migration should not silently depend on a developer manually running a SQL command that is absent from migration history.

---

# 52. Migration Review

Every migration must be reviewed together with its related application change.

Reviewers should ask:

### Purpose

* Why is the schema changing?
* Is the change required?

### Data

* What happens to existing records?
* Are historical records preserved?

### Safety

* Can the migration fail?
* What happens if it fails halfway?

### Compatibility

* Can old and new application code coexist if required?

### Performance

* How expensive is the migration?
* Are large tables involved?

### Integrity

* Are constraints correct?
* Are foreign keys correct?
* Is tenant/branch isolation preserved?

### Testing

* Was the clean database path tested?
* Was the upgrade path tested?

---

# 53. Database Change Review Checklist

Before approval:

* [ ] Change has a documented purpose.
* [ ] A migration exists.
* [ ] Migration name is clear.
* [ ] Migration order is correct.
* [ ] Existing data impact is understood.
* [ ] Data migration is deterministic.
* [ ] Required compatibility is preserved.
* [ ] Foreign keys are correct.
* [ ] Constraints are correct.
* [ ] Indexes are justified.
* [ ] Tenant isolation is preserved.
* [ ] Branch isolation is preserved.
* [ ] Financial history is preserved.
* [ ] Inventory history is preserved.
* [ ] Recipe history is preserved where required.
* [ ] Offline synchronization impact is considered.
* [ ] Large-table impact is considered.
* [ ] Destructive operations are explicitly reviewed.
* [ ] Tests cover the migration.
* [ ] Application changes are included.
* [ ] Documentation/ADR updates are included where required.

---

# 54. Migration and Release Traceability

A database change must be traceable to the change that introduced it.

Conceptually:

```text
Requirement
    ↓
Issue / Work Item
    ↓
Branch
    ↓
Commit
    ↓
Migration
    ↓
Tests
    ↓
Pull Request
    ↓
Release
```

This makes it possible to answer:

> Why does this database structure exist?

and:

> Which release introduced this schema change?

---

# 55. ADR Requirements

Not every migration requires an ADR.

An ADR should be considered when the schema change introduces a significant architectural decision.

Examples:

* changing tenant data model;
* changing branch ownership model;
* introducing event/history storage;
* changing identifier strategy;
* introducing a new versioning model;
* replacing an existing persistence strategy;
* changing historical data retention architecture.

Small routine schema changes normally do not require an ADR.

---

# 56. Database Development with AI-Assisted Coding

AI coding tools may assist with:

* migration templates;
* SQL drafts;
* model definitions;
* test generation;
* migration review checklists;
* schema documentation.

AI-generated database changes must not be trusted automatically.

Developers must verify:

* SQL correctness;
* migration ordering;
* existing data impact;
* transaction behavior;
* constraints;
* indexes;
* tenant isolation;
* branch isolation;
* performance;
* historical correctness;
* compatibility.

AI-generated migrations must pass the same review and testing requirements as manually written migrations.

---

# 57. Common Anti-Patterns

The following practices are prohibited or strongly discouraged.

### Manual schema editing without migration

```text
Developer changes DB manually
        ↓
Application works locally
        ↓
No migration
```

This creates environment drift.

### Editing shared historical migrations

This breaks migration history.

### Destructive migration without data analysis

Existing production data may be lost or invalidated.

### Adding NOT NULL blindly

Existing rows may not satisfy the constraint.

### Creating indexes without query analysis

This adds write and storage cost without guaranteed benefit.

### Treating database errors as business logic

A constraint violation is not a replacement for proper domain validation.

### Ignoring tenant/branch scope

This can create cross-tenant or cross-branch data leakage.

### Testing only on an empty database

This misses real upgrade problems.

### Large one-shot data transformation without planning

This can cause excessive locks and operational impact.

### Silent historical data rewriting

Historical business records must retain their original meaning.

---

# 58. Database Development Workflow

The standard workflow is:

```text
1. Identify schema requirement
        ↓
2. Analyze affected domain/data
        ↓
3. Identify existing data impact
        ↓
4. Classify schema change
        ↓
5. Design migration
        ↓
6. Design compatibility strategy
        ↓
7. Implement migration
        ↓
8. Implement application changes
        ↓
9. Test clean database
        ↓
10. Test existing-data upgrade
        ↓
11. Validate constraints/indexes
        ↓
12. Run integration tests
        ↓
13. Review migration
        ↓
14. Update documentation/ADR if needed
        ↓
15. Merge through normal development workflow
```

---

# 59. Database Change Completion Criteria

A database change is complete only when:

* the requirement is understood;
* schema design is approved;
* migration exists;
* application compatibility is verified;
* existing data impact is understood;
* required data transformation is tested;
* constraints are validated;
* indexes are justified;
* tenant/branch isolation is preserved;
* financial/inventory/recipe history is preserved;
* offline compatibility is considered;
* clean database installation succeeds;
* upgrade-path testing succeeds;
* related application tests pass;
* code review is complete;
* required documentation is updated.

---

# 60. Database Development Invariants

The following rules are mandatory:

1. Every persistent schema change must have a migration.
2. Migration history is treated as immutable after sharing.
3. Existing production data must be assumed valuable.
4. Empty-database testing is not sufficient.
5. Upgrade-path testing is required for meaningful schema changes.
6. Destructive changes require explicit review.
7. Data migrations must define their transformation behavior.
8. Data migrations must avoid unintended duplication.
9. Required values must have explicit nullability semantics.
10. Foreign keys must represent valid ownership relationships.
11. Tenant boundaries must be preserved.
12. Branch boundaries must be preserved.
13. Global and branch-specific resources must remain distinguishable.
14. Historical financial meaning must not be silently changed.
15. Historical inventory meaning must not be silently changed.
16. Historical recipe meaning must be preserved where required.
17. Indexes must have a justified access pattern.
18. Unique constraints must match the actual ownership scope.
19. Large-table changes must consider execution cost.
20. Long-running transformations must consider concurrency.
21. Database changes must consider concurrent application activity.
22. Offline synchronization must remain compatible with schema evolution.
23. Reference data must not overwrite user-managed business data.
24. Schema changes must be traceable to development changes.
25. Significant architectural database decisions should have ADRs.
26. Database migrations must be tested.
27. Migration failures must have understood consequences.
28. Application code and schema changes must be reviewed together when related.
29. Database constraints must not be treated as a substitute for all business rules.
30. Database development must preserve system correctness before developer convenience.

---

# 61. Relationship to Other Development Documents

This document works together with:

* `01_Development_Architecture_Overview.md`
* `02_Repository_Structure_and_Conventions.md`
* `03_Git_Branching_and_Version_Control_Strategy.md`
* `04_Commit_Message_and_Change_Standards.md`
* `05_Pull_Request_and_Code_Review_Process.md`
* `06_Backend_Development_Standards.md`
* `09_API_Development_and_Contract_Change_Workflow.md`
* `10_Documentation_First_Development_Workflow.md`
* `11_ADR_and_Architecture_Decision_Workflow.md`
* `13_Testing_and_Debugging_Workflow.md`
* `14_Dependency_and_Package_Management.md`
* `18_Development_Guardrails_and_Quality_Rules.md`

Related testing documentation:

* `TEST-06 Repository and Database Integration Testing`
* `TEST-11 Concurrency and Consistency Testing`
* `TEST-12 Financial and Cash Testing`
* `TEST-13 Inventory and Recipe Testing`

Related deployment documentation:

* `DEP-08 Database Deployment and Runtime Architecture`
* `DEP-15 Database Migration and Release Deployment`
* `DEP-16 Release Strategy and Zero-Downtime Deployment`
* `DEP-17 Rollback and Release Recovery`

These documents must remain complementary rather than duplicating each other's responsibilities.

---

# 62. Final Principle

Database development is not simply changing tables.

It is the controlled evolution of persistent business state.

Every schema change must preserve the integrity of existing data, maintain tenant and branch boundaries, support compatible application behavior, protect financial and operational history, and provide a tested path from the previous database state to the new one.

**The database must evolve deliberately, through reviewable migrations, with existing data and business correctness treated as first-class engineering constraints.**

