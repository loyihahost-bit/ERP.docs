# Tenant and Business Data Model

**Document ID:** DB-03
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/02_Database_Architecture.md`

## 1. Purpose

This document defines the database model for the Business tenant.

The Business is the primary tenant boundary of FastFood ERP.

This document defines:

* Business identity;
* tenant ownership;
* Business lifecycle;
* Business metadata;
* Business-level configuration references;
* Business ownership;
* Business relationships;
* tenant isolation requirements;
* Business status;
* Business deletion lifecycle;
* Business-level auditability;
* Business-level constraints.

Detailed models for Subscription, Branch, Identity, Configuration, and other domains are defined in their dedicated database documents.

---

# 2. Business as the Tenant Root

Every restaurant or fast-food organization using FastFood ERP is represented by a Business.

Conceptually:

```text
Platform
   │
   ├── Business A
   │      ├── Branch 1
   │      ├── Branch 2
   │      └── Branch N
   │
   ├── Business B
   │      ├── Branch 1
   │      └── Branch N
   │
   └── Business N
```

The Business is the primary tenant boundary.

All tenant-owned data must ultimately be associated with exactly one Business.

---

# 3. Business Identity

The Business has a stable UUID.

Conceptually:

```text id="5q7z3u"
business.id = UUID
```

The Business UUID:

* is globally unique;
* is immutable;
* is never reused;
* is used as the primary business identity;
* is referenced by tenant-scoped records;
* is preserved across subscription renewal;
* remains stable during the Business lifecycle.

Business UUID must not be regenerated during reactivation.

---

# 4. Business Table

The core Business table should conceptually contain:

| Field                     | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| `id`                      | Business UUID                             |
| `name`                    | Business display name                     |
| `status`                  | Current Business lifecycle state          |
| `timezone`                | Business operational timezone             |
| `currency`                | Business currency                         |
| `created_at`              | Creation timestamp                        |
| `updated_at`              | Last metadata update                      |
| `subscription_expired_at` | Exact subscription expiry when applicable |
| `deletion_eligible_at`    | Calculated lifecycle milestone            |
| `deleted_at`              | Permanent deletion completion timestamp   |

The final schema may add additional fields required by approved business requirements.

---

# 5. Business Name

The Business name is operational metadata.

Changing the name must not create a new Business.

Historical records continue referencing the same Business UUID.

Name changes may be audited when required by administrative policy.

---

# 6. Business Timezone

The Business timezone defines the default operational timezone for Business-level operations.

It is important for:

* Cash Session boundaries;
* report periods;
* subscription dates;
* notification schedules;
* monthly reports;
* attendance;
* payroll;
* lifecycle jobs.

The database should store the timezone as an explicit configuration value rather than deriving it from server location.

---

# 7. Business Currency

The Business has a configured currency.

Currency affects:

* prices;
* payments;
* refunds;
* payroll;
* inventory costs;
* reports.

Financial records must preserve the applicable currency context where required.

Changing the configured currency must not silently reinterpret historical monetary values.

---

# 8. Business Status

Business lifecycle is represented explicitly.

The conceptual lifecycle is:

```text
Active
   ↓
Expired / Read-Only
   ↓
Deletion Eligible
   ↓
Deleting
   ↓
Deleted
```

The exact database representation may use:

* status;
* lifecycle state;
* timestamps;
* transition records.

The lifecycle state must remain reconstructable.

---

# 9. Active Business

An Active Business may perform normal operations according to:

* subscription entitlement;
* employee permissions;
* branch scope;
* device trust;
* system rules.

Active status does not automatically grant every feature.

Effective capability remains:

```text
Permission
+
Branch Scope
+
Subscription Entitlement
+
Device / Offline Authorization where applicable
```

---

# 10. Expired / Read-Only Business

After subscription expiry, the Business may enter a read-only operational state.

The database must preserve existing data.

Read-only access may include:

* viewing historical data;
* viewing reports;
* viewing history;
* allowed Excel exports.

Modifying operations must be rejected by the application layer.

The database must preserve the Business and its data during the retention period.

---

# 11. Deletion Eligibility

A Business becomes deletion eligible after the configured retention period if it has not been reactivated.

The current requirement is:

**60 days after the exact `subscription_expired_at`.**

Conceptually:

```text id="yl2g3c"
subscription_expired_at
        +
        60 days
        ↓
deletion_eligible_at
```

The calculation must use the Business/Subscription lifecycle rules rather than arbitrary server time.

---

# 12. Business Reactivation

If a Business is reactivated before permanent deletion:

* the same Business UUID remains;
* the same historical data remains;
* branches remain associated;
* employees remain associated;
* configuration remains;
* historical records remain;
* lifecycle state returns to Active.

Reactivation must not create a new tenant.

---

# 13. Permanent Deletion

Permanent deletion is a controlled lifecycle operation.

The database must not treat it as an ordinary user-initiated `DELETE`.

Deletion requires:

* lifecycle validation;
* retention validation;
* deletion state;
* controlled background processing;
* dependency-aware deletion;
* idempotent retry;
* auditability.

---

# 14. Business Deletion State

Deletion should be represented as a state transition rather than a single destructive action.

Conceptually:

```text
Deletion Eligible
       ↓
Deleting
       ↓
Deleted
```

The `Deleting` state allows the system to safely resume a partially completed deletion.

---

# 15. Deletion Lock

A Business entering permanent deletion must have an effective lifecycle lock.

The lock prevents:

* reactivation races;
* new normal operations;
* stale synchronization;
* new trusted-device activity;
* conflicting lifecycle transitions.

The lock must be released only when deletion fails and the system safely returns to a recoverable state, or when deletion completes.

---

# 16. Business Ownership

A Business may have one or more Owners.

Owner identity is represented through the Identity/Employee model rather than duplicating employee records inside the Business table.

Conceptually:

```text
Business
   │
   └── Owner Membership
            │
            └── Employee
```

The Business table should not contain multiple hard-coded owner columns.

---

# 17. Owner Relationship

Owner membership should support:

* multiple Owners;
* active/inactive membership;
* historical ownership;
* permission scope;
* subscription owner limits.

The exact employee and role relationship is defined in:

`04_Identity_and_Access_Data_Model.md`

and related Employee data model documents.

---

# 18. Business and Branch Relationship

A Business may contain multiple Branches.

Conceptually:

```text
Business
   │
   ├── Branch A
   ├── Branch B
   └── Branch N
```

The Branch table must reference the Business UUID.

A Branch cannot belong to multiple Businesses simultaneously.

---

# 19. Business and Subscription Relationship

Subscription belongs to the Business.

Conceptually:

```text
Business
   │
   └── Subscription
          ├── Tariff
          ├── Start
          ├── Expiry
          └── Entitlements
```

Subscription history must be preserved.

The Business table should not store the complete historical subscription model directly.

---

# 20. Business and Employee Relationship

Employees belong to a Business.

An employee may work in:

* one Branch;
* multiple Branches;
* Business-level scope where permitted.

The Employee record must reference the Business UUID.

Historical employee data must remain associated with the original Business.

---

# 21. Business and Product Relationship

Products are Business-level entities.

A product belongs to exactly one Business.

The same Business product may be available in multiple Branches.

Conceptually:

```text
Business
   │
   └── Product
          ├── Branch A availability
          ├── Branch B availability
          └── Branch C availability
```

A product must never be shared between unrelated Businesses.

---

# 22. Business and Recipe Relationship

Recipes belong to the Business.

Recipe versions remain associated with the same Business.

Historical recipe versions must not become accessible to another Business.

Recipe visibility may be permission-controlled.

---

# 23. Business and Set Relationship

Sets/combos belong to the Business.

A Set may reference Business-owned products.

Cross-Business Set composition is prohibited.

A Set's historical versions remain associated with the same Business.

---

# 24. Business and Configuration

Business-level configuration belongs to the Business.

Examples:

* default operational settings;
* notification thresholds;
* Business-level menu settings;
* pricing configuration;
* report preferences;
* other approved Business configuration.

Configuration history must preserve Business ownership.

---

# 25. Business and Branch Configuration

Branch configuration is subordinate to Business ownership.

Conceptually:

```text
Business
   │
   └── Branch
          │
          └── Branch Configuration
```

A Branch configuration cannot reference a Branch belonging to another Business.

---

# 26. Business and Device Relationship

Devices belong to a Business trust boundary.

A Device record must preserve the Business association.

This prevents a trusted device from being reused across tenants without explicit registration.

A device replacement receives a new Device UUID.

---

# 27. Business and Audit

Business-level state changes may generate audit records.

Examples:

* Business creation;
* owner changes;
* Business configuration changes;
* subscription changes;
* lifecycle transitions;
* deletion initiation;
* deletion completion;
* security-sensitive administrative actions.

Audit records retain the Business UUID.

---

# 28. Business and Notifications

Business-level notifications may include:

* subscription ending;
* subscription expired;
* deletion approaching;
* salary due;
* important inventory conditions;
* important business-level operational alerts.

Notifications remain tenant-scoped.

---

# 29. Business and Reports

Business-level reports aggregate authorized data across the Business.

A report may be:

* Business-wide;
* Branch-specific.

The report scope must be explicit.

A Branch report must never accidentally aggregate data from another Business.

---

# 30. Business and Synchronization

Every synchronized offline event must belong to exactly one Business.

Synchronization records must contain or reliably derive:

* Business UUID;
* Branch UUID where applicable;
* Device UUID;
* Employee UUID where applicable;
* Transaction UUID.

A synchronization event without valid tenant context must be rejected.

---

# 31. Business and Offline Storage

Offline devices may temporarily store Business data locally.

Local data must remain associated with the Business UUID.

When a device is:

* revoked;
* replaced;
* removed;
* invalidated by Business deletion;

its offline authorization must no longer permit Business operations.

---

# 32. Tenant Isolation Rule

Every Business-scoped query must enforce Business ownership.

Conceptually:

```text id="w8u8ya"
SELECT ...
FROM entity
WHERE business_id = :authenticated_business_id
```

The actual implementation may use repository or service abstractions, but the effective behavior must remain equivalent.

---

# 33. Business Context Must Not Be Client-Controlled

A client must not be able to access another Business simply by submitting a different `business_id`.

The server must derive and validate Business context from:

* authenticated identity;
* authorized membership;
* trusted device where applicable;
* synchronization context;
* platform-level authority where applicable.

---

# 34. Platform-Level Access

Super Admin is a platform-level role.

Platform-level operations may intentionally operate across Businesses.

Such operations must:

* require explicit platform authorization;
* be isolated from ordinary Business queries;
* be audited where appropriate;
* avoid exposing unrelated Business data unnecessarily.

Platform-level access must not bypass security controls silently.

---

# 35. Business Identifier Exposure

Business UUID may be exposed through APIs where required.

However, exposing a UUID does not grant access.

Every API operation must still validate:

* authentication;
* Business membership;
* authorization;
* branch scope where applicable;
* subscription entitlement where applicable.

---

# 36. Business Creation

Business creation is a platform-level operation.

Creation should atomically establish the minimum required tenant state.

Conceptually:

```text
Create Business
     ↓
Create Business Identity
     ↓
Create Initial Subscription State
     ↓
Create Required Configuration
     ↓
Create Initial Owner Membership
```

The exact creation transaction may involve multiple domains but must not leave an unusable partially initialized Business.

---

# 37. Business Initialization

A newly created Business must receive all required default state needed for normal operation.

Defaults may include:

* default configuration;
* initial subscription;
* required roles;
* required permissions;
* initial owner;
* required system settings.

Defaults must be deterministic and versioned where necessary.

---

# 38. Business Creation Idempotency

Business creation must be protected against duplicate requests.

If the creation request is retried, the system must not create multiple Businesses accidentally.

The operation should use an idempotent operation identity where appropriate.

---

# 39. Business Deactivation

Temporary Business deactivation, if required by platform operations, must be represented explicitly.

Deactivation must not be confused with permanent deletion.

A deactivated Business retains its historical data unless the Data Lifecycle rules explicitly require deletion.

---

# 40. Business UUID Reuse

Business UUIDs must never be reused.

Even after permanent deletion:

```text id="f5xv7o"
Deleted Business UUID
        ≠
Future Business UUID
```

This prevents:

* historical ambiguity;
* synchronization collisions;
* audit confusion;
* stale offline event collisions.

---

# 41. Business Name Reuse

Business names may potentially be reused unless a separate business rule prohibits it.

Business name uniqueness must not be assumed unless explicitly required.

Business UUID remains the authoritative identity.

---

# 42. Business Metadata

Business metadata may include:

* legal/display name;
* timezone;
* currency;
* contact information;
* operational settings;
* status.

Only approved metadata should be stored.

The database must not become an uncontrolled document store for arbitrary business information.

---

# 43. Business Contact Data

Business contact information must be treated as tenant-owned metadata.

Changes should preserve:

* current value;
* modification timestamp;
* actor where required.

Sensitive contact data must be protected through normal authorization.

---

# 44. Business-Level Constraints

The database should enforce or support:

* unique Business UUID;
* required Business name;
* valid lifecycle status;
* valid timezone;
* valid currency;
* valid lifecycle timestamps;
* no invalid deletion state combinations.

Complex lifecycle validation remains application-level.

---

# 45. Lifecycle Timestamp Consistency

The following relationships must remain logically valid:

```text
subscription_expired_at
        ≤
deletion_eligible_at
```

and:

```text
deletion_eligible_at
        ≤
deletion_started_at
        ≤
deleted_at
```

where the corresponding lifecycle timestamps exist.

The exact field set may differ depending on the final schema.

---

# 46. Business State History

Important Business lifecycle transitions should be historically reconstructable.

A separate lifecycle history table may be used to preserve:

* previous state;
* new state;
* timestamp;
* actor/system;
* reason;
* related subscription;
* transaction/job identity.

The current Business row represents current state.

The history represents the transition record.

---

# 47. Business Configuration Version

Business-level configuration that affects future operations should use versioning where historical reconstruction requires it.

A configuration version may contain:

* version UUID;
* Business UUID;
* configuration type;
* configuration data;
* state;
* effective timestamp;
* created timestamp;
* actor;
* reason.

Historical versions must not be overwritten.

---

# 48. Business-Level Limits

Subscription tariffs may define limits such as:

* maximum Branch count;
* maximum Owner count;
* maximum employee count;
* enabled functions.

These limits belong to Subscription/Entitlement data rather than being hard-coded directly into the Business table.

Business data model may reference the current subscription state.

---

# 49. Business and Subscription Downgrade

A tariff downgrade must not delete Business data automatically.

Existing data remains preserved.

The application prevents new operations that exceed the new entitlement.

The database therefore preserves the complete Business history even when current subscription limits are lower.

---

# 50. Business and Subscription Expiry

Subscription expiry does not delete the Business.

The database retains the Business during the retention period.

The application changes operational capability to read-only according to subscription rules.

---

# 51. Business and Data Deletion

When permanent deletion begins, dependent data must be deleted according to dependency order.

The Business record itself should not be removed first if that would make controlled cleanup impossible.

Deletion ordering must consider:

* foreign keys;
* audit;
* reports;
* synchronization;
* notifications;
* devices;
* branches;
* employees;
* orders;
* payments;
* inventory;
* configuration.

---

# 52. Deletion Dependency Model

Conceptually:

```text
Business
   │
   ├── Subscription
   ├── Configuration
   ├── Devices
   ├── Branches
   │      ├── Cash
   │      ├── Orders
   │      ├── Inventory
   │      └── Attendance
   │
   ├── Employees
   ├── Products
   ├── Recipes
   ├── Payments
   ├── Reports
   ├── Notifications
   ├── Synchronization
   └── Audit
```

The exact deletion order is defined in:

`18_Data_Lifecycle_and_Deletion_Model.md`

---

# 53. Stale Synchronization After Deletion

After permanent Business deletion, stale offline events must not recreate the Business.

Synchronization processing must validate:

```text
Business UUID
+
Business lifecycle state
```

A deleted Business must reject new synchronization events.

Business UUID must never be recreated.

---

# 54. Device Invalidation After Deletion

When Business deletion completes:

* trusted devices become invalid;
* offline authorization becomes unusable;
* synchronization events are rejected;
* Business data on devices must follow local cleanup rules.

The central database remains authoritative for this state.

---

# 55. Business Data and Backup

Business data may remain in backups according to the backup retention policy.

Permanent deletion from the primary database does not automatically mean that every historical backup copy disappears immediately.

Backup retention and deletion compliance must therefore be handled explicitly by the operational data lifecycle policy.

---

# 56. Business Data and Reports

Historical report versions belong to the Business.

Exporting a report does not alter Business lifecycle state.

Report exports do not reset:

* subscription expiry;
* deletion countdown;
* lifecycle state.

---

# 57. Business Data and Audit Retention

Audit data follows the approved Data Lifecycle policy.

Audit records must not be deleted casually simply because the associated operational record changed.

Where permanent Business deletion requires audit deletion, it must follow the controlled lifecycle process.

---

# 58. Business-Level Query Patterns

Typical Business-scoped queries include:

```text
Business by UUID
Branches by Business
Employees by Business
Products by Business
Subscriptions by Business
Reports by Business
Notifications by Business
Audit Events by Business
Synchronization Events by Business
```

Every query must preserve tenant scope.

---

# 59. Business-Level Indexing

The Business UUID is a high-value filtering dimension.

Tables containing Business-scoped data should generally support efficient Business filtering.

For example:

```text
business_id
```

may require an index depending on table size and query pattern.

Composite indexes may be required for common access patterns such as:

```text
business_id + branch_id
business_id + status
business_id + created_at
```

Final indexes are defined in:

`20_Database_Indexing_and_Performance.md`

---

# 60. Business-Level Concurrency

Concurrent Business operations must remain safe.

Examples:

* Business configuration update;
* subscription transition;
* Business deletion initiation;
* owner membership update;
* tariff change.

Optimistic versioning or transactional locking may be used where required.

---

# 61. Business Configuration Concurrency

If two authorized users modify the same Business configuration concurrently, the system must avoid silent last-write-wins behavior when historical correctness matters.

Possible mechanisms include:

* version numbers;
* stale-version rejection;
* explicit conflict;
* correction/version creation.

---

# 62. Business Lifecycle Concurrency

The following race must be explicitly protected:

```text
Reactivation
      vs
Permanent Deletion
```

The system must ensure that both operations cannot independently succeed.

Lifecycle transition must be atomic.

---

# 63. Business and Background Jobs

Background jobs that operate on Business data must verify current Business lifecycle state before modifying data.

Examples:

* report generation;
* notification processing;
* subscription transition;
* deletion;
* synchronization;
* cleanup.

A stale job must not modify a Business after it becomes permanently deleted.

---

# 64. Business and Caching

Business-level cached data must include tenant identity in its cache key.

Unsafe:

```text
product:list
```

Safer:

```text
business:{business_uuid}:product:list
```

Branch-specific data must also include Branch context.

Cache invalidation must not allow one Business to observe another Business's data.

---

# 65. Business and API Serialization

API responses must not expose unrelated Business data.

Serialization should occur after:

* tenant authorization;
* branch authorization;
* permission checks;
* subscription checks where applicable.

Business UUID may be returned as metadata, but access remains authorization-controlled.

---

# 66. Business-Level Security Invariants

The database/application boundary must guarantee:

1. A Business belongs to one tenant context.
2. A Business UUID is globally unique.
3. A Business UUID is never reused.
4. Business data cannot be accessed without valid context.
5. Client-provided Business UUID cannot override authorization.
6. Platform access requires platform-level authorization.
7. Branch records belong to one Business.
8. Employees belong to one Business.
9. Products belong to one Business.
10. Synchronization events belong to one Business.

---

# 67. Business-Level Historical Invariants

The following must remain reconstructable:

* Business creation;
* ownership changes;
* subscription history;
* lifecycle transitions;
* configuration changes;
* deletion process;
* important administrative operations.

Current state alone is not sufficient when historical reconstruction is required.

---

# 68. Business Data Model Invariants

The following database invariants are mandatory:

1. `Business.id` is immutable.
2. `Business.id` is unique.
3. `Business.id` is never reused.
4. Business name is not the primary identity.
5. Business timezone is explicit.
6. Business currency is explicit.
7. Business status is explicit.
8. Lifecycle timestamps are internally consistent.
9. Business data is tenant-isolated.
10. Business-owned records reference the correct Business.
11. Branches cannot belong to multiple Businesses.
12. Employees cannot belong to multiple Businesses.
13. Products cannot belong to multiple Businesses.
14. Recipes cannot cross Business boundaries.
15. Sets cannot reference products from another Business.
16. Devices cannot operate under another Business without registration.
17. Offline events cannot cross Business boundaries.
18. Reports cannot aggregate unauthorized Businesses.
19. Notifications cannot cross Business boundaries.
20. Audit records preserve Business context.
21. Business deletion is lifecycle-controlled.
22. Deletion is idempotent.
23. Reactivation and deletion cannot race successfully.
24. Deleted Business UUIDs cannot be reused.
25. Subscription expiry does not immediately delete Business data.
26. Subscription downgrade does not delete Business data.
27. Business history remains reconstructable.
28. Business configuration versions remain tenant-scoped.
29. Background jobs must validate Business state.
30. Cache keys must preserve Business isolation.

---

# 69. Completion Criteria

This document is complete when:

* Business is established as the tenant root;
* Business identity is defined;
* Business lifecycle is defined;
* Business ownership is defined;
* Business-to-Branch relationship is defined;
* Business-to-Subscription relationship is defined;
* Business-level configuration is defined;
* tenant isolation rules are defined;
* deletion and reactivation boundaries are defined;
* synchronization and offline tenant boundaries are defined;
* Business-level database invariants are documented.

---

# 70. Next Document

The next document is:

`04_Identity_and_Access_Data_Model.md`

It will define the database model for:

* employees;
* user accounts;
* roles;
* permissions;
* employee overrides;
* branch assignments;
* Owner membership;
* Manager scope;
* effective access;
* account lifecycle;
* authentication-related data;
* historical access relationships.

