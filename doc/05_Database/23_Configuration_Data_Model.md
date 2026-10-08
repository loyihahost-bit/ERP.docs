# Configuration Data Model

**Document ID:** DB-23
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/01_Database_Overview.md`

## 1. Purpose

This document defines the database model for Business and Branch configuration.

The configuration model must support:

* Business-level configuration;
* Branch-level configuration;
* configuration ownership;
* configuration scope;
* immutable configuration versions;
* approval;
* effective configuration;
* Cash Session activation boundaries;
* configuration inheritance;
* Branch overrides;
* price configuration;
* menu configuration;
* Recipe and Set configuration;
* printer configuration;
* notification thresholds;
* permission-related configuration;
* subscription-dependent configuration;
* offline configuration;
* synchronization;
* optimistic concurrency;
* audit and historical reconstruction.

Configuration is operational state, but configuration history must remain immutable.

---

# 2. Core Principles

The configuration model follows these principles:

1. Every configuration belongs to exactly one Business.
2. Branch configuration cannot cross Business boundaries.
3. Business configuration defines global defaults.
4. Branch configuration may override permitted Business-level configuration.
5. Configuration changes are versioned.
6. Historical configuration versions are immutable.
7. Configuration changes become effective at a deterministic boundary.
8. The current system uses the next Cash Session as the normal operational boundary for relevant POS configuration.
9. Existing Orders retain their configuration snapshots.
10. Configuration changes do not rewrite historical transactions.
11. Stale configuration updates are rejected.
12. Important configuration changes are auditable.
13. Offline devices may use the latest valid locally authorized configuration.
14. Synchronization must not silently overwrite newer server configuration.
15. Subscription entitlement limits configuration modification.
16. Configuration history remains available during read-only subscription state.
17. Rollback is implemented as a new configuration version.
18. Configuration is not the same thing as audit history.
19. Operational configuration must remain efficiently readable for POS operations.
20. Configuration must be reconstructable from immutable versions.

---

# 3. Configuration Hierarchy

The configuration hierarchy is:

```text id="c9h3i7"
Platform
   ↓
Business
   ↓
Business Configuration
   ↓
Branch Configuration
   ↓
Effective Configuration
   ↓
POS / Operations
```

Platform-level configuration may exist for subscription and system policy.

Business-level configuration is owned by the Business.

Branch-level configuration is owned by the Branch but remains within the Business boundary.

---

# 4. Configuration Ownership

Every configuration record must identify its Business.

Conceptually:

```text id="8q2y8n"
business_id
```

A Branch-scoped configuration additionally identifies:

```text id="9m6p2a"
branch_id
```

The Branch must belong to the same Business.

Cross-Business configuration references are prohibited.

---

# 5. Configuration Identity

A logical configuration has a stable UUID.

Example:

```text id="2s9r2b"
configuration.id UUID
```

The logical configuration identity remains stable across versions.

Example:

```text id="9ezhjp"
Configuration UUID
    |
    +-- Version 1
    +-- Version 2
    +-- Version 3
```

The configuration UUID identifies the logical setting.

The configuration version UUID identifies one historical state.

---

# 6. Configuration Version Identity

Every configuration version receives a permanent UUID.

Suggested:

```text id="k8r5g4"
configuration_version.id UUID
```

Properties:

* globally unique;
* immutable;
* never reused;
* linked to exactly one logical configuration.

---

# 7. Configuration Types

The configuration registry should support controlled configuration types.

Examples:

```text id="6h5z5v"
BUSINESS_SETTINGS
BRANCH_SETTINGS
MENU
BRANCH_MENU
PRODUCT_PRICE
BRANCH_PRICE_OVERRIDE
RECIPE_POLICY
SET_CONFIGURATION
PRINTER_ROUTING
ORDER_SETTINGS
CASH_SETTINGS
SHIFT_HANDOVER_SETTINGS
INVENTORY_SETTINGS
ATTENDANCE_SETTINGS
PAYROLL_SETTINGS
NOTIFICATION_THRESHOLDS
REPORT_SETTINGS
DEVICE_POLICY
OFFLINE_POLICY
PERMISSION_POLICY
```

The exact list may evolve.

New configuration types must follow the same versioning and ownership rules.

---

# 8. Configuration Scope

Supported scopes:

```text id="p1q8c6"
BUSINESS
BRANCH
```

A Business-scoped configuration:

```text id="d9gr8y"
branch_id = NULL
```

A Branch-scoped configuration:

```text id="o6j8qk"
branch_id != NULL
```

The database must enforce the relationship between scope and Branch reference.

---

# 9. Configuration Lifecycle

A configuration version may follow:

```text id="qv5w3s"
DRAFT
   ↓
PENDING_APPROVAL
   ↓
APPROVED
   ↓
SCHEDULED
   ↓
EFFECTIVE
   ↓
SUPERSEDED
```

Exceptional states may include:

```text id="x4k3dw"
REJECTED
CANCELLED
ARCHIVED
```

The exact implementation may simplify these states, but historical identity must remain available.

---

# 10. Draft Configuration

A draft is not operational.

A draft may be edited before approval.

A draft must not affect:

* POS;
* new Orders;
* inventory consumption;
* payments;
* reports requiring effective configuration.

---

# 11. Approval

Where approval is required, a configuration version must not become effective until approval succeeds.

Approval must identify:

* approver;
* timestamp;
* result;
* reason where required.

Approval is an auditable operation.

---

# 12. Configuration Version Immutability

Once a configuration version becomes approved/effective, its business meaning must not be modified in place.

If a change is required:

```text id="u1m0y9"
Old Version
    ↓
New Version
```

The old version remains immutable.

---

# 13. Configuration Effective Boundary

Relevant POS configuration becomes operational from the next Cash Session.

Example:

```text id="0q5r1s"
Current Cash Session
      |
      | price change created
      |
      v
Next Cash Session
      |
      +-- New price becomes effective
```

This prevents an active POS session from silently switching configuration.

---

# 14. Configuration Activation

When a new Cash Session starts, the system determines the latest valid effective configuration.

The selected configuration must satisfy:

* Business active state;
* Branch active state;
* approval requirements;
* effective timestamp/session boundary;
* subscription entitlement;
* configuration validity.

---

# 15. Active Cash Session

An active Cash Session continues using the configuration applicable to that session.

A configuration change must not silently alter:

* existing Order Item prices;
* existing Order configuration;
* active operational snapshots.

---

# 16. Order Configuration Snapshot

When an operational transaction depends on configuration, the transaction stores the applicable configuration identity.

Examples:

* price version;
* Recipe Version;
* Set Version;
* menu configuration;
* relevant Branch configuration.

Historical transactions must remain interpretable without reading the current configuration.

---

# 17. Effective Configuration

The effective configuration for a Branch is determined from:

```text id="w8gqz3"
Business Configuration
        +
Branch Configuration
        +
Configuration Version
        +
Employee Permissions
        +
Subscription Entitlement
```

The exact precedence is configuration-type dependent.

The result must be deterministic.

---

# 18. Configuration Priority

Where Branch override is allowed:

```text id="5r8t7q"
Branch Override
      >
Business Default
```

The Branch override must not modify the Business default.

For configuration types that do not allow Branch overrides, the Business configuration remains authoritative.

---

# 19. Configuration Resolution

Configuration resolution should be centralized in an application/domain service.

The database stores configuration state and versions.

The application determines the effective configuration according to explicit rules.

Different modules must not implement conflicting configuration precedence independently.

---

# 20. Configuration Payload

A configuration version may contain structured configuration data.

Conceptually:

```text id="e8c3yd"
configuration_data JSONB
```

The exact payload schema depends on configuration type.

JSONB is appropriate for flexible configuration structures where relational querying is not a primary requirement.

---

# 21. Strongly Structured Configuration

Frequently queried or integrity-critical values should remain relational where appropriate.

Examples:

* Product price;
* Branch menu availability;
* Branch identity;
* permission assignment;
* subscription entitlement.

Not every configuration should be stored as an unrestricted JSON document.

---

# 22. Configuration Schema Version

Every configuration payload should identify its schema version.

Suggested:

```text id="5r8bca"
schema_version
```

This allows the application to interpret historical configuration versions correctly.

Schema version and business configuration version are separate concepts.

---

# 23. Configuration Business Version

Each new operational configuration state receives a new version number.

Example:

```text id="y2c6t9"
1
2
3
```

The version number is unique within the logical configuration.

Recommended constraint:

```text id="3ay5pd"
UNIQUE(configuration_id, version_number)
```

---

# 24. Previous Version

A configuration version may reference its predecessor.

Suggested:

```text id="4x0twm"
previous_version_id
```

This creates a historical chain.

The chain must not contain cycles.

---

# 25. Rollback

Rollback must not delete the current version.

Instead:

```text id="s8j5h2"
Version 3
    ↓
Rollback requested
    ↓
Version 4
    ↓
Version 2 state restored
```

Version 4 becomes the new effective configuration.

Version 3 and Version 2 remain unchanged.

---

# 26. Configuration Change Reason

Configuration changes should preserve a reason where appropriate.

Examples:

```text id="e5b2c6"
PRICE_UPDATE
MENU_CHANGE
BRANCH_OVERRIDE
POLICY_CHANGE
CORRECTION
ROLLBACK
BUSINESS_REQUEST
SYSTEM_MAINTENANCE
```

The reason is historical metadata.

---

# 27. Configuration Actor

A configuration version should identify its creator.

Suggested:

```text id="r7j2n6"
created_by_employee_id
```

System-generated changes may use a system actor.

Historical creator information must remain available even if the employee later becomes inactive.

---

# 28. Creator Snapshot

For historical readability, the version may store:

```text id="v6x8s1"
creator_name_snapshot
```

The Employee record remains authoritative for identity.

The snapshot preserves historical context.

---

# 29. Effective Timestamp

A configuration version should store its effective timestamp.

Suggested:

```text id="p8r2g7"
effective_at
```

For Cash Session-bound configuration, the timestamp must be interpreted together with the session boundary.

---

# 30. Effective Cash Session

Where required, configuration may reference the Cash Session from which it became effective.

Conceptually:

```text id="w7d3x4"
effective_cash_session_id
```

This improves historical reconstruction.

A configuration effective for Branch A must not reference a Cash Session belonging to Branch B.

---

# 31. Configuration Expiration

Some configurations may have an optional expiration.

Suggested:

```text id="n4c8s2"
expires_at
```

If expiration is supported, the system must define whether:

* a previous version becomes active;
* a default becomes active;
* the configuration becomes inactive.

The fallback behavior must be deterministic.

---

# 32. Menu Configuration

Menu configuration may include:

* Product availability;
* Product activation;
* category association where applicable;
* Branch availability;
* operational restrictions.

Product identity remains separate.

Menu changes do not create new Product UUIDs.

---

# 33. Price Configuration

Price configuration includes:

* Business standard price;
* Branch price override;
* price version;
* effective session;
* creator;
* reason.

Historical Orders use their stored price snapshots.

Current price must never reinterpret historical Orders.

---

# 34. Recipe Configuration

Recipe-related configuration references Recipe and Recipe Version data.

A Recipe change creates a new Recipe Version rather than modifying historical Recipe state.

The configuration layer may determine which approved Recipe Version is effective.

---

# 35. Set Configuration

Set configuration includes:

* Set identity;
* Set Version;
* component composition;
* active state;
* Branch availability;
* Set price.

Historical Set Orders preserve their applicable Set Version.

---

# 36. Branch Menu Configuration

Branch menu configuration determines whether a Business Product is operationally available at a Branch.

Example:

```text id="1f8c7v"
Global Product
     |
     +-- Branch A → Enabled
     +-- Branch B → Disabled
     +-- Branch C → Enabled
```

A Branch change affects only that Branch.

---

# 37. Printer Configuration

Printer routing may be configured by:

* Branch;
* Product;
* category;
* printer group;
* operational purpose.

Printer configuration must not be part of the Order financial snapshot unless required for historical reconstruction.

Printer failure must not modify committed Order state.

---

# 38. Notification Threshold Configuration

Business or Branch configuration may define thresholds such as:

* low stock;
* large refund;
* inventory variance;
* salary due;
* subscription warning.

Threshold changes must be versioned.

Historical notifications remain associated with the threshold/configuration state that produced them where required.

---

# 39. Permission Configuration

Permission configuration determines role and employee access.

Permission changes must use the Identity and Access model.

The Configuration domain must not create an independent permission system.

Permission changes must remain auditable and version-aware where required.

---

# 40. Subscription-Dependent Configuration

Configuration operations may be restricted by subscription entitlement.

Examples:

* Branch count;
* Owner count;
* Employee count;
* enabled modules;
* feature availability.

A Business must not gain access to restricted configuration merely by editing local configuration data.

---

# 41. Configuration and Subscription

Subscription state affects whether a configuration may be modified.

After subscription expiry:

* existing configuration remains viewable;
* historical versions remain available;
* modifying configuration is blocked where entitlement requires;
* offline configuration cannot bypass the restriction.

---

# 42. Configuration and Employee Permissions

Configuration modification requires appropriate permission.

The server must validate:

```text id="u6z6gi"
Employee
+
Role
+
Permission Override
+
Branch Scope
+
Subscription
```

A configuration UI cannot grant itself authorization.

---

# 43. Manager Configuration Authority

A Manager may modify only configuration allowed by the Manager's effective permissions.

A Manager must not:

* grant themselves additional configuration authority;
* grant permissions beyond their own authority;
* modify another Branch without scope;
* bypass subscription restrictions.

---

# 44. Configuration Concurrency

Concurrent configuration changes must use optimistic concurrency.

A client should submit the version it edited.

Example:

```text id="y7m5cq"
Client Version = 4
Server Version = 5
```

The server rejects the stale update.

---

# 45. Configuration Conflict

A configuration conflict must preserve:

* submitted version;
* current server version;
* actor;
* Branch;
* Business;
* attempted change;
* timestamp.

The server must not silently apply stale configuration.

---

# 46. Configuration Conflict Resolution

Resolution may require:

* refresh;
* manual merge;
* creation of a new version;
* explicit authorized correction.

The old versions remain immutable.

Conflict resolution is auditable.

---

# 47. Configuration Idempotency

Configuration-changing operations must have an operation UUID or equivalent idempotency key.

Repeated requests must not create duplicate versions.

Examples:

```text id="n5f2z9"
Price Change
Approval
Branch Override
Rollback
```

must be idempotent.

---

# 48. Configuration Approval Idempotency

Repeated approval requests for the same configuration version must not create multiple approvals.

The approval state must remain deterministic.

---

# 49. Configuration Transaction Boundary

Creating an effective configuration change should be atomic.

For example:

```text id="5r4v7s"
BEGIN
    validate current version
    validate permission
    validate subscription
    create new version
    record audit context
COMMIT
```

Secondary notification/report operations should not be required for successful configuration commit.

---

# 50. Configuration and Audit

Important configuration changes must create audit events.

Examples:

* create;
* approve;
* activate;
* deactivate;
* price change;
* Branch override;
* Recipe configuration change;
* Set configuration change;
* rollback;
* correction;
* conflict resolution.

Audit records remain separate and immutable.

---

# 51. Configuration History vs Audit History

These are different:

```text id="d4w8m5"
Configuration History
    → What configuration state existed?

Audit History
    → Who performed which action and what changed?
```

Configuration versions are operational historical state.

Audit events are immutable activity records.

Both may reference each other.

---

# 52. Configuration Snapshot

Operational transactions should store the configuration identifiers required for historical interpretation.

Example:

```text id="k5m9s3"
Order Item
    |
    +-- Product Price Version
    +-- Recipe Version
    +-- Set Version
```

The transaction should not depend on the current configuration to reconstruct its original state.

---

# 53. Offline Configuration

A trusted device may operate using the latest valid locally stored configuration.

The device must retain:

* configuration UUID;
* version;
* validity;
* Business;
* Branch;
* authorization context.

The device must not invent a new authoritative configuration while offline unless that configuration type explicitly supports offline modification.

---

# 54. Offline Configuration Change

If offline configuration changes are supported for a configuration type:

* the change receives a UUID;
* the local version is preserved;
* the server validates authorization;
* the server checks conflicts;
* the server may accept, reject, or create a conflict.

Offline configuration changes must never silently overwrite newer server versions.

---

# 55. Configuration Synchronization

Configuration synchronization must preserve version identity.

The server should send only configuration versions the device is authorized to receive.

Synchronization must verify:

* Business;
* Branch;
* device;
* employee;
* subscription;
* configuration type;
* version;
* integrity.

---

# 56. Configuration Sync Priority

Operational transactions and configuration synchronization must respect dependencies.

An offline transaction created under Version A may remain valid even after Version B becomes effective.

Version B must not retroactively rewrite Version A transactions.

---

# 57. Configuration Cache

Effective configuration may be cached for POS performance.

Cache entries must include:

* Business;
* Branch;
* configuration type;
* version.

Cache is not authoritative.

After configuration change, stale cache entries must be invalidated or version-checked.

---

# 58. POS Configuration Read Path

Normal POS operations should use an efficient effective configuration read path.

The POS should not reconstruct a long historical version chain for every Order.

The current effective configuration should be readily available.

---

# 59. Configuration Materialization

The system may maintain a materialized effective configuration representation.

Example:

```text id="w6z0p1"
Business Configuration
       +
Branch Override
       ↓
Effective Branch Configuration
```

This is an optimization.

The authoritative source remains versioned configuration data.

---

# 60. Configuration Rebuild

If a materialized effective configuration becomes stale or corrupted, it must be rebuildable from authoritative configuration versions.

The rebuild must not modify historical versions.

---

# 61. Configuration Validation

Before a configuration becomes effective, validate:

* Business state;
* Branch state;
* employee permission;
* subscription entitlement;
* required references;
* configuration schema;
* version;
* effective boundary;
* dependent entities.

Invalid configuration must not become effective.

---

# 62. Product Reference Validation

A configuration referencing a Product must verify:

* Product belongs to the same Business;
* Product is valid for the configuration;
* Product has not been deleted;
* required category/Recipe/Set relationship exists.

Historical configuration may continue referencing archived Products where historical integrity requires it.

---

# 63. Branch Reference Validation

Branch-scoped configuration must reference an active or historically valid Branch according to the operation.

Cross-Business Branch references are prohibited.

---

# 64. Configuration Deactivation

A configuration may be deactivated.

Deactivation creates a state transition/version where historical integrity requires it.

Deactivation does not delete previous configuration versions.

---

# 65. Configuration Archive

Archived configuration versions remain historical.

Archive does not mean physical deletion.

Historical Orders must remain able to reference archived configuration versions.

---

# 66. Configuration Deletion

Normal configuration versions must not be physically deleted individually.

Deletion occurs through the Business data lifecycle when the Business reaches permanent deletion.

Any exceptional cleanup must preserve required historical integrity.

---

# 67. Configuration Recovery

Recovery from a failed configuration change must not overwrite history.

If Version 5 is invalid, the system may create:

```text id="2j8w9m"
Version 6
```

with the desired previous valid state.

Version 5 remains recorded.

---

# 68. Configuration and Reports

Reports may need configuration context.

Examples:

* price version;
* report configuration;
* notification threshold;
* Branch menu state.

Historical reports must not be reinterpreted using current configuration.

---

# 69. Configuration and Notifications

Important configuration changes may generate notifications.

For example:

* large price change;
* important Branch menu change;
* configuration approval.

Notification generation is secondary to configuration commit.

A notification failure must not roll back the configuration transaction.

---

# 70. Configuration and Background Jobs

Background jobs may:

* activate scheduled configuration;
* rebuild effective configuration;
* invalidate caches;
* synchronize devices;
* generate notifications.

A background job must respect Business lifecycle and subscription entitlement.

---

# 71. Configuration and Data Lifecycle

When a Business becomes read-only:

* configuration remains readable;
* new configuration modifications are blocked;
* historical configuration remains available.

When permanent deletion begins:

* configuration versions become part of the deletion dependency graph;
* pending configuration jobs are invalidated;
* offline devices are revoked.

---

# 72. Configuration and Business Reactivation

If the Business is reactivated before permanent deletion:

* configuration remains;
* existing versions remain;
* Branch overrides remain;
* historical configuration remains;
* no configuration reconstruction from memory is required.

The same Business UUID remains authoritative.

---

# 73. Configuration and Branch Deactivation

Branch deactivation does not delete Branch configuration.

Historical Branch configuration remains available.

A new effective configuration must not be created for an inactive Branch unless explicitly allowed.

---

# 74. Configuration and Device Trust

A trusted device may receive configuration only for authorized:

* Business;
* Branch;
* employee;
* feature set.

Device trust does not itself grant permission to modify configuration.

---

# 75. Configuration and Employee Deactivation

An inactive employee cannot create new configuration changes.

Historical configurations created by that employee remain valid.

Pending changes created by a now-inactive employee must follow explicit approval/authorization policy.

---

# 76. Configuration Security

Configuration payloads may contain sensitive business information.

The database and application must protect configuration data through:

* tenant isolation;
* permission checks;
* encryption where appropriate;
* restricted administrative access;
* audit;
* safe serialization.

Secrets must not be stored in ordinary configuration payloads.

---

# 77. Configuration Secrets

Credentials, API keys, private keys, authentication tokens, and other secrets must not be stored as ordinary configuration JSON.

Secrets require a dedicated secure secret-management mechanism.

---

# 78. Configuration Schema Evolution

Configuration schemas may evolve.

Changes must remain backward compatible with historical versions where required.

Migration of historical configuration must not silently change its historical meaning.

---

# 79. Configuration Version Integrity

A configuration version may store:

```text id="9t6n0e"
checksum
```

The checksum may be used to detect accidental corruption.

The checksum must be calculated from a deterministic canonical representation.

---

# 80. Configuration Query Performance

Recommended indexes include:

```text id="m5m1sy"
configurations(business_id, config_type, scope)
configurations(business_id, branch_id, config_type)
configuration_versions(configuration_id, version_number)
configuration_versions(configuration_id, status)
configuration_versions(business_id, branch_id, effective_at)
```

Exact indexes should follow actual query patterns.

---

# 81. Configuration Version Lookup

POS should be able to efficiently determine:

```text id="8e7k2v"
Current effective configuration
```

without scanning every historical version.

Indexes and/or materialized effective state may be used.

---

# 82. Configuration Concurrency Constraints

The database must protect:

```text id="w8c2s5"
(configuration_id, version_number)
```

from duplicates.

Effective-state transitions must also be concurrency-safe.

Two workers must not simultaneously activate conflicting versions as the authoritative current version.

---

# 83. Scheduled Configuration

If scheduled configuration is supported:

```text id="x9q4f7"
scheduled_at
```

may identify when activation should occur.

The worker must validate the configuration again before activation.

A scheduled configuration must not become active if:

* Business is deleted;
* Branch is invalid;
* required approval is missing;
* subscription rules prohibit it;
* configuration has been superseded;
* dependency validation fails.

---

# 84. Configuration Activation Job

Activation jobs must be idempotent.

Repeated execution must result in one effective configuration state.

A successful activation must not create duplicate activation events.

---

# 85. Configuration Materialized State

If the system maintains a current configuration table, it should contain only the current effective state.

Historical versions remain in the version table.

Example:

```text id="j7h6s1"
configuration
    → logical identity/current pointer

configuration_versions
    → immutable history
```

---

# 86. Current Version Pointer

A logical configuration may contain:

```text id="0n3w8b"
current_version_id
```

If used, updating the pointer and activating the version must be atomic.

The pointer must never reference a different Business or Branch.

---

# 87. Configuration History Reconstruction

The system should be able to answer:

```text id="1b5k0m"
Which configuration was effective for Branch X
during Cash Session Y?
```

This may be resolved using:

* effective timestamps;
* effective Cash Session;
* configuration version;
* session configuration snapshot.

---

# 88. Cash Session Configuration Snapshot

Where required, a Cash Session may store references to the configuration versions used by that session.

This provides a stable operational context.

For example:

```text id="c8v2z4"
Cash Session
    |
    +-- Menu Configuration Version
    +-- Pricing Configuration Version
    +-- Other Relevant Configuration Versions
```

---

# 89. Configuration and Historical Orders

An Order must not depend on a mutable current configuration.

The Order stores the relevant:

* price snapshot;
* Recipe Version;
* Set Version;
* configuration version identifiers.

This preserves historical interpretation.

---

# 90. Configuration and Inventory

Inventory transactions involving Recipes or Sets must preserve the applicable Recipe/Set Version.

Current configuration must not reinterpret historical inventory consumption.

---

# 91. Configuration and Payments

Payment amounts are derived from the authoritative Order financial state.

Current Product price or configuration must not modify historical payment amounts.

---

# 92. Configuration and Refunds

Refund calculations use historical transaction snapshots.

Current configuration must not change historical refund interpretation.

---

# 93. Configuration and Audit

Every important configuration mutation must be traceable to:

* Business;
* Branch where applicable;
* Employee/system actor;
* Device where applicable;
* configuration;
* old version;
* new version;
* reason;
* timestamp;
* result.

---

# 94. Configuration and Synchronization Audit

Offline configuration changes must additionally preserve:

* offline authorization;
* Device UUID;
* client timestamp;
* server receipt timestamp;
* synchronization result;
* conflict UUID where applicable.

---

# 95. Configuration Error Handling

Configuration failures should be classified as:

```text id="e1x4w8"
VALIDATION_ERROR
AUTHORIZATION_ERROR
CONFLICT
ENTITLEMENT_ERROR
DEPENDENCY_ERROR
TEMPORARY_INFRASTRUCTURE_ERROR
INTEGRITY_ERROR
```

The database state must remain consistent for every failure category.

---

# 96. Configuration Transaction Failure

If configuration creation fails before commit:

* no effective version is created;
* no current-version pointer is advanced;
* no partial Branch override remains.

Secondary notifications or cache operations may be retried independently.

---

# 97. Configuration Background Failure

If a cache invalidation or notification fails after configuration commit:

* configuration remains committed;
* background retry is scheduled;
* audit remains valid.

The system must not roll back committed configuration merely because secondary processing failed.

---

# 98. Suggested Logical Tables

The database should conceptually support:

```text id="7p4d3q"
configurations
configuration_versions
configuration_approvals
configuration_conflicts
```

Optional:

```text id="2m8r4v"
configuration_effective_state
configuration_activation_jobs
configuration_change_requests
```

Existing domain-specific configuration tables may be used where stronger relational modeling is required.

---

# 99. Suggested Fields

### `configurations`

```text id="5b2s9e"
id
business_id
branch_id
config_type
scope
status
current_version_id
created_at
updated_at
```

### `configuration_versions`

```text id="4h7m2k"
id
configuration_id
business_id
branch_id
version_number
status
schema_version
configuration_data
previous_version_id
created_by_employee_id
creator_name_snapshot
change_reason
effective_at
effective_cash_session_id
expires_at
checksum
created_at
updated_at
```

### `configuration_approvals`

```text id="1r9z6c"
id
configuration_version_id
approver_employee_id
status
reason
approved_at
created_at
```

### `configuration_conflicts`

```text id="8n4q2v"
id
business_id
branch_id
configuration_id
submitted_version
server_version
conflict_type
status
created_at
resolved_at
resolved_by_employee_id
resolution_reason
```

---

# 100. Database Invariants

The following invariants are mandatory:

1. Every configuration belongs to exactly one Business.
2. Every Branch-scoped configuration references a Branch.
3. Every referenced Branch belongs to the same Business.
4. Cross-Business configuration references are prohibited.
5. Configuration identity is separate from configuration version identity.
6. Configuration UUIDs are never reused.
7. Configuration Version UUIDs are never reused.
8. Version numbers are unique within a logical configuration.
9. Version numbers are never reused.
10. Historical configuration versions are immutable.
11. Draft configuration is not operational.
12. Required approval must complete before activation.
13. Effective configuration must have a deterministic activation boundary.
14. Relevant POS configuration becomes effective from the defined Cash Session boundary.
15. Active Cash Sessions do not silently switch configuration.
16. Existing Orders retain their configuration snapshots.
17. Historical Orders do not depend on current configuration.
18. Historical Inventory Transactions do not depend on current configuration.
19. Historical Payments do not depend on current configuration.
20. Historical Refunds do not depend on current configuration.
21. Branch overrides affect only the selected Branch.
22. Branch overrides do not modify Business defaults.
23. Branch overrides cannot cross Business boundaries.
24. Configuration resolution is deterministic.
25. Configuration precedence is explicit.
26. Configuration payloads have schema versions where required.
27. Schema version and business configuration version are separate concepts.
28. Configuration changes use immutable version creation.
29. Rollback creates a new version.
30. Rollback does not delete the version being rolled back from.
31. Previous-version chains cannot contain cycles.
32. Configuration changes are protected by optimistic concurrency.
33. Stale configuration updates are rejected.
34. Configuration-changing requests are idempotent.
35. Repeated approval does not create duplicate approvals.
36. Important configuration changes are audited.
37. Configuration history and audit history remain separate.
38. Configuration actors remain historically attributable.
39. Employee deactivation does not invalidate historical configuration.
40. Device context is retained where relevant.
41. Subscription entitlement is validated before configuration modification.
42. Subscription expiry cannot be bypassed through configuration APIs.
43. Offline configuration cannot silently override newer server configuration.
44. Offline configuration changes must be explicitly supported by configuration type.
45. Offline configuration changes retain their original identity.
46. Configuration synchronization preserves version identity.
47. Transaction synchronization preserves historical configuration references.
48. New configuration cannot retroactively modify old transactions.
49. Effective configuration is efficiently readable.
50. Cache is not the authoritative configuration source.
51. Cache keys must preserve Business and Branch scope.
52. Materialized effective configuration can be rebuilt from authoritative versions.
53. Current-version pointers, if used, are transactionally consistent.
54. Scheduled configuration is validated before activation.
55. Scheduled activation is idempotent.
56. Deleted Business data cannot be recreated by scheduled jobs.
57. Inactive Branches do not silently receive new effective configuration.
58. Configuration archive does not mean immediate physical deletion.
59. Historical configuration remains available until lifecycle deletion.
60. Business reactivation preserves configuration history.
61. Business deletion invalidates pending configuration jobs.
62. Business deletion revokes relevant offline authorization.
63. Configuration payloads cannot contain unmanaged secrets.
64. Secret material requires dedicated secure storage.
65. Configuration schema evolution must preserve historical meaning.
66. Configuration integrity can be validated.
67. Configuration version creation is atomic.
68. Failed configuration creation cannot leave a partial effective state.
69. Secondary notification failure cannot roll back committed configuration.
70. Cache invalidation failure cannot roll back committed configuration.
71. Configuration conflicts are explicit.
72. Configuration conflicts preserve submitted and server versions.
73. Conflict resolution is authorized.
74. Conflict resolution is audited.
75. Conflict resolution does not overwrite historical versions.
76. Configuration history remains reconstructable.
77. Cash Session configuration context remains identifiable where required.
78. Price configuration remains separate from inventory cost.
79. Recipe configuration remains separate from Recipe Version identity.
80. Set configuration remains separate from Set Version identity.
81. Permission configuration does not create a second permission system.
82. Notification thresholds are versioned where historical interpretation requires them.
83. Report configuration context is preserved where required.
84. Configuration access is Business-scoped.
85. Configuration access is Branch-scoped where applicable.
86. Configuration modification requires effective permission.
87. Manager authority cannot exceed effective permission.
88. Inactive employees cannot create new valid configuration changes.
89. Historical creator identity remains available.
90. Server time is authoritative for configuration lifecycle decisions.
91. Client timestamps cannot extend configuration validity.
92. Configuration effective state cannot cross Business boundaries.
93. Configuration versions cannot reference incompatible Business or Branch entities.
94. Configuration queries use appropriate tenant and scope indexes.
95. Heavy configuration rebuilds do not block normal POS operations.
96. Configuration background jobs respect Business lifecycle.
97. Configuration background jobs respect subscription entitlement.
98. Configuration changes preserve historical integrity.
99. Configuration state remains reconstructable after cache loss or worker restart.
100. Configuration data must remain consistent with the system-wide historical, authorization, concurrency, offline, and lifecycle rules.

---

# Related Documents

* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`
* `docs/03_Domain_Analysis/18_Configuration_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/08_Offline_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`
* `docs/04_Architecture/19_Architecture_Decisions_and_Tradeoffs.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`

