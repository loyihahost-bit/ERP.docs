# Subscription and Entitlement Data Model

**Document ID:** DB-06
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* subscription plans;
* Business subscriptions;
* tariff features;
* limits;
* entitlement evaluation;
* subscription lifecycle;
* expiry;
* read-only state;
* grace periods;
* downgrade and upgrade behavior;
* reactivation;
* deletion eligibility;
* historical entitlement snapshots.

The subscription database model must control access to Business capabilities without destroying Business data when a subscription changes.

---

# 2. Subscription Architecture

The conceptual hierarchy is:

```text id="0fr3hl"
Platform
   ↓
Subscription Plan
   ↓
Plan Feature / Limit
   ↓
Business Subscription
   ↓
Effective Entitlement
```

A Business subscription determines which capabilities and limits are currently available to that Business.

---

# 3. Subscription Plan

## 3.1 Plan

A Subscription Plan represents a tariff definition managed at the platform level.

Conceptual fields:

* `id`
* `name`
* `code`
* `status`
* `description`
* `created_at`
* `updated_at`

Examples may include:

* Basic;
* Standard;
* Professional;
* Enterprise.

The actual plan names are configurable.

---

# 4. Plan Identity

`subscription_plan.id` must be:

* UUID;
* immutable;
* globally unique;
* never reused.

The plan code may be human-readable but must not replace the UUID as the authoritative identity.

---

# 5. Plan Lifecycle

A plan may have states such as:

```text id="7mbk2k"
Draft
  ↓
Active
  ↓
Inactive
  ↓
Archived
```

Inactive or archived plans must not automatically modify existing Business subscriptions.

A plan change must follow explicit subscription migration rules.

---

# 6. Plan Features

A plan may enable or disable specific system capabilities.

Conceptual relationship:

```text id="0i4gup"
SubscriptionPlan
       ↓
PlanFeature
       ↓
Feature
```

Examples:

```text
pos
inventory
recipes
payroll
reports
multi_branch
advanced_reports
```

Feature identifiers must be stable machine-readable values.

---

# 7. Feature Definition

A Feature represents a system capability.

Conceptual fields:

* `id`
* `code`
* `name`
* `status`
* description
* version metadata where required

Feature definitions are platform-level.

A Feature is not Business-specific.

---

# 8. Plan Feature Assignment

`PlanFeature` determines whether a Feature is included in a plan.

Conceptual fields:

* `plan_id`
* `feature_id`
* `enabled`
* effective/version metadata

The same Feature must not be assigned multiple times to the same Plan version.

---

# 9. Limits

Some subscription restrictions are quantitative rather than Boolean.

Examples:

* maximum Branches;
* maximum Owners;
* maximum Employees;
* maximum trusted devices;
* other configurable limits.

Conceptual relationship:

```text id="k6e4io"
SubscriptionPlan
       ↓
PlanLimit
       ↓
LimitDefinition
```

A limit must have a stable machine-readable identifier.

---

# 10. Limit Value

A plan limit may contain:

* limit code;
* numeric value;
* unlimited flag where supported;
* effective version;
* status.

Example:

```text id="q4s5c7"
max_branches = 10
max_owners   = 3
max_employees = 50
```

The exact values are tariff configuration, not hard-coded Business attributes.

---

# 11. Business Subscription

A Business has a subscription record.

Conceptual fields:

* `id`
* `business_id`
* `plan_id`
* `status`
* `started_at`
* `expires_at`
* `created_at`
* `updated_at`
* renewal metadata where applicable

The Business Subscription UUID is immutable.

---

# 12. Subscription Ownership

Every Business Subscription belongs to exactly one Business.

A subscription must not be shared between Businesses.

A Plan may be referenced by many Business subscriptions.

Therefore:

```text id="8h3gj4"
Plan 1
 ├── Business A Subscription
 ├── Business B Subscription
 └── Business C Subscription
```

---

# 13. Subscription Status

The subscription lifecycle must support:

```text id="w0e1u8"
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

A short grace state may be represented where required by the subscription policy.

The authoritative lifecycle state must be server-controlled.

---

# 14. Subscription Expiry

`expires_at` represents the exact subscription expiry timestamp.

The server must use its authoritative time when evaluating expiry.

Client clocks must not determine whether a subscription is active.

The database must preserve the exact timestamp.

---

# 15. Read-Only State

After subscription expiry, the Business enters a restricted state.

Existing data remains accessible according to permissions.

The system may allow:

* viewing data;
* viewing history;
* viewing reports;
* permitted Excel exports.

Modifying operations are blocked.

The database must not delete or rewrite operational data simply because the subscription expired.

---

# 16. Active Session After Expiry

If a subscription expires while an employee is already authenticated:

* the session does not need to be forcibly deleted;
* the next modifying operation must be rejected;
* read-only operations may continue if permitted.

Therefore, session existence must not be treated as proof of subscription entitlement.

---

# 17. Subscription Grace Period

The system supports a bounded grace period where defined by subscription policy.

The current system-wide default is:

```text
3 days
```

The effective entitlement logic must distinguish:

* normal active period;
* grace period;
* fully expired read-only state.

Offline authorization must never extend beyond the server-defined entitlement boundary.

---

# 18. Subscription Feature Entitlement

Effective feature access is conceptually:

```text id="7txy7f"
Authentication
      +
Authorization
      +
Branch Scope
      +
Subscription Entitlement
      ↓
Effective Access
```

Subscription entitlement does not replace permission checks.

A user with permission may still be denied because the Business subscription does not include the required feature.

---

# 19. Limit Entitlement

Quantitative limits are evaluated against current Business state.

Examples:

```text id="2k6w9j"
Active Branches < max_branches
Active Owners < max_owners
Active Employees < max_employees
```

The database stores authoritative state.

Application services evaluate whether a new operation would exceed the limit.

---

# 20. Subscription Upgrade

When a Business upgrades:

* the new plan becomes effective according to subscription rules;
* previously blocked features may become available;
* limits may increase;
* existing data remains unchanged;
* existing permissions remain unchanged.

The upgrade must not require destructive migration of Business data.

---

# 21. Subscription Downgrade

When a Business downgrades:

* existing data remains;
* existing Branches remain;
* existing Employees remain;
* existing permissions remain;
* existing configuration remains;
* newly prohibited operations become blocked.

Examples:

If the new plan permits 5 Branches but the Business already has 8:

* the 8 Branches remain;
* new Branch creation is blocked;
* deletion is not forced.

---

# 22. Feature Downgrade

If a feature becomes unavailable:

* historical data created using that feature remains;
* existing configuration is preserved;
* new operations requiring that feature are blocked;
* reports/history remain available where permitted.

The subscription system must not delete feature-specific data during downgrade.

---

# 23. Employee Limit Downgrade

If the employee limit becomes lower than the current number of employees:

* existing employees remain;
* historical employee records remain;
* new employee creation is blocked;
* employee deactivation remains possible where authorized;
* existing historical operations remain valid.

---

# 24. Owner Limit Downgrade

If the Business exceeds the new Owner limit:

* existing Owners are not automatically removed;
* historical ownership remains intact;
* adding another Owner is blocked;
* Owner changes require explicit authorized action.

---

# 25. Branch Limit Downgrade

If the Business exceeds the new Branch limit:

* existing Branches remain;
* Branch history remains;
* new Branch creation is blocked;
* existing Branches are not automatically deleted.

---

# 26. Entitlement Snapshot

Historical operations must not depend on the current subscription plan.

Where required, transactions and reports may preserve entitlement snapshots such as:

* plan UUID;
* plan version;
* feature state;
* relevant limit;
* effective time.

This allows historical reconstruction.

---

# 27. Plan Versioning

Plan configuration may change over time.

A plan versioning model should preserve:

* plan UUID;
* version;
* feature assignments;
* limit assignments;
* effective timestamp;
* status.

A historical subscription period must remain reconstructable even if the current plan configuration changes.

---

# 28. Subscription History

Subscription changes should be historically recorded.

Examples:

* subscription created;
* plan changed;
* renewal;
* expiration;
* grace period;
* upgrade;
* downgrade;
* reactivation;
* cancellation;
* deletion transition.

Historical records must be immutable.

---

# 29. Subscription Period

A Business may have multiple subscription periods over its lifetime.

The system should preserve the relationship between:

```text id="h5n5b8"
Business
   ↓
Subscription
   ↓
Subscription Period / History
```

The current subscription must be uniquely identifiable.

Historical periods must remain available for audit and reporting.

---

# 30. Renewal

A successful renewal extends the subscription according to the purchased period.

The database must preserve:

* previous expiry;
* new expiry;
* renewal timestamp;
* plan;
* actor/source;
* transaction/reference metadata where applicable.

Renewal must not rewrite historical subscription periods.

---

# 31. Failed Renewal

A failed renewal must not silently extend access.

The system should preserve:

* attempted renewal;
* failure state;
* timestamp;
* reason/category where safe;
* resulting subscription state.

Subscription state remains determined by the authoritative expiry policy.

---

# 32. Reactivation

A Business may be reactivated before permanent deletion.

Reactivation must restore the same:

* Business UUID;
* Branch UUIDs;
* Employee UUIDs;
* configuration;
* operational history;
* reports;
* audit history.

Reactivation does not create a new Business.

---

# 33. Reactivation Before Deletion

If reactivation occurs during the retention period:

```text id="4g9qpo"
Expired / Read-Only
        ↓
Reactivated
        ↓
Active
```

Deletion jobs must stop or be cancelled before permanent deletion.

The lifecycle transition must be concurrency-safe.

---

# 34. 60-Day Data Retention

The current policy requires permanent deletion if the Business is not reactivated within 60 days after subscription expiry.

The deletion eligibility timestamp should be derived from the authoritative expiry:

```text
deletion_eligible_at =
    subscription_expired_at + retention_period
```

The retention period must not be extended by ordinary data access or export.

---

# 35. Deletion Eligibility

A Business becomes eligible for deletion only after the required retention period.

The database should preserve:

* `subscription_expired_at`;
* `deletion_eligible_at`;
* lifecycle state;
* deletion job state;
* deletion timestamps.

Deletion eligibility must be evaluated server-side.

---

# 36. Deletion Job

Permanent deletion is performed by controlled background processing.

The deletion process must:

1. acquire Business lifecycle lock;
2. verify deletion eligibility;
3. verify no valid reactivation occurred;
4. invalidate active access;
5. invalidate trusted devices;
6. stop pending synchronization;
7. delete dependent data according to dependency order;
8. record deletion progress;
9. mark Business as permanently deleted.

The process must be idempotent.

---

# 37. Partial Deletion

If deletion fails partway through:

* completed steps must not be repeated destructively;
* failed steps must be retryable;
* deletion progress must remain observable;
* Business access must remain blocked;
* stale offline data must not recreate deleted state.

---

# 38. Deletion and Reactivation Race

Reactivation and deletion must not execute concurrently.

A lifecycle lock or equivalent concurrency mechanism must guarantee:

```text
Reactivate wins
OR
Deletion wins
```

but never an ambiguous partial state.

---

# 39. Offline Entitlement

Offline authorization must contain sufficient information to enforce subscription boundaries.

Offline operation must verify:

* Business;
* Employee;
* Branch;
* Device;
* permissions;
* subscription validity;
* authorization expiry.

Offline mode must never create unlimited subscription access.

---

# 40. Offline Grace

Offline grace does not mean subscription grace is unlimited.

The offline authorization artifact has its own validity boundary.

The server remains authoritative after synchronization.

If the server determines that an offline operation was outside permitted entitlement, the event is rejected or placed into explicit conflict handling.

---

# 41. Subscription and Device Trust

Device trust is separate from subscription entitlement.

A trusted device may still be blocked when:

* subscription expires;
* Business is deactivated;
* Employee is deactivated;
* permission is removed;
* Branch access is removed.

Trust does not override subscription restrictions.

---

# 42. Subscription and Permissions

Subscription entitlement does not grant permissions.

For an operation to succeed:

```text id="r7p8fj"
Authenticated
        AND
Authorized
        AND
Correct Branch
        AND
Feature Entitled
        AND
Operational State Valid
```

A subscription feature being enabled is therefore insufficient by itself.

---

# 43. Entitlement Evaluation

Effective entitlement should be evaluated by an application service.

Conceptually:

```text
EntitlementService
    ├── Business Subscription
    ├── Plan Version
    ├── Feature
    ├── Limit
    ├── Business State
    └── Current Server Time
```

The result may be cached, but the database remains authoritative.

---

# 44. Entitlement Cache

Entitlement results may be cached for performance.

Cache keys must include:

* Business UUID;
* plan/version context;
* relevant feature/limit;
* effective state.

Cache invalidation is required when:

* subscription changes;
* plan changes;
* feature configuration changes;
* limit changes;
* Business lifecycle changes.

A stale cache must never grant access beyond the authoritative subscription state.

---

# 45. Subscription Context in Transactions

Core modifying operations should validate subscription entitlement before committing state.

Examples:

* create Branch;
* create Employee;
* create Owner;
* use newly restricted feature;
* create feature-specific configuration.

The entitlement decision must participate in the appropriate transaction boundary where race conditions could otherwise exceed a limit.

---

# 46. Concurrent Limit Enforcement

Concurrent requests must not bypass limits.

Example:

```text
max_branches = 10
current = 9

Request A → create Branch
Request B → create Branch
```

Only one request may consume the final available entitlement.

Database transaction/locking or another atomic reservation mechanism must guarantee this.

---

# 47. Subscription Reporting

Subscription reports may include:

* current plan;
* subscription status;
* expiry;
* renewal history;
* plan changes;
* feature entitlements;
* limit usage.

Subscription reporting must not expose another Business's subscription data.

---

# 48. Audit Integration

Important subscription changes must be auditable.

Audit events may include:

* plan creation;
* plan modification;
* feature change;
* limit change;
* Business subscription creation;
* upgrade;
* downgrade;
* renewal;
* expiry;
* reactivation;
* deletion transition;
* deletion completion.

Audit records must identify the actor or SYSTEM source.

---

# 49. Notification Integration

Subscription state changes may generate notifications such as:

* subscription ending;
* subscription expired;
* grace period;
* deletion approaching;
* deletion eligible;
* reactivation completed;
* deletion completed.

Notifications must not themselves determine entitlement.

---

# 50. Recommended Logical Entity Set

```text id="y39f8w"
SubscriptionPlan
   ├── PlanVersion
   │     ├── PlanFeature
   │     └── PlanLimit
   │
   └── Feature / LimitDefinition

Business
   └── BusinessSubscription
         ├── SubscriptionPeriod
         ├── SubscriptionHistory
         └── EntitlementSnapshot
```

The exact physical normalization may be adjusted during schema design.

---

# 51. Suggested Core Fields

## SubscriptionPlan

```text id
code
name
status
created_at
updated_at
```

## PlanVersion

```text id
plan_id
version
effective_from
effective_to
status
created_at
```

## PlanFeature

```text id
plan_version_id
feature_id
enabled
```

## PlanLimit

```text id
plan_version_id
limit_id
value
unlimited
```

## BusinessSubscription

```text id
business_id
plan_version_id
status
started_at
expires_at
created_at
updated_at
```

## SubscriptionPeriod

```text id
business_subscription_id
started_at
expires_at
status
source
created_at
```

## SubscriptionHistory

```text id
business_id
subscription_id
event_type
old_state
new_state
actor_type
actor_id
created_at
```

The exact fields remain subject to the final physical schema.

---

# 52. Monetary and Billing Boundary

Subscription billing information should remain separate from operational Business data.

Payment processing details, if introduced later, should not be embedded directly into Business or operational transaction tables.

The current ERP database model should store only the subscription state and required billing references.

External payment processing remains outside the current core operational scope.

---

# 53. Database Constraints

The database should enforce:

* valid Business reference;
* valid Plan reference;
* valid Plan Version reference;
* valid Feature reference;
* valid Limit reference;
* unique plan/version combinations;
* unique feature assignment per plan version;
* unique limit assignment per plan version;
* valid subscription period relationships;
* valid lifecycle timestamps.

Application validation remains responsible for complex entitlement rules.

---

# 54. Indexing

Important indexes should support:

* active Business subscriptions;
* Business by subscription;
* subscription expiry;
* deletion eligibility;
* plan versions;
* plan features;
* plan limits;
* subscription history;
* subscription lifecycle jobs.

A particularly important operational index is on subscription expiry/deletion eligibility for background processing.

---

# 55. Data Lifecycle

Subscription data itself follows Business lifecycle rules.

Before Business deletion:

* subscription history remains;
* deletion state remains observable;
* access is blocked.

During permanent Business deletion:

* subscription references are removed according to dependency order;
* historical subscription data is deleted as part of Business deletion;
* external billing records, if any, are governed by their own retention requirements.

---

# 56. Security Requirements

Subscription entitlement is security-sensitive.

The system must prevent clients from modifying:

* plan ID;
* subscription status;
* expiry;
* entitlement;
* limits;
* deletion eligibility.

All authoritative changes must occur through authorized server-side operations.

---

# 57. Application vs Database Responsibilities

### Database responsibilities

* subscription relationships;
* plan/version relationships;
* feature/limit references;
* lifecycle timestamps;
* uniqueness;
* historical records;
* referential integrity.

### Application responsibilities

* entitlement calculation;
* permission + entitlement evaluation;
* expiry enforcement;
* grace logic;
* limit enforcement;
* upgrade/downgrade workflows;
* reactivation;
* deletion orchestration;
* notification generation.

---

# 58. Core Invariants

The following invariants are mandatory:

1. Every Business subscription belongs to exactly one Business.
2. A subscription references one authoritative plan version.
3. Plan definitions are platform-scoped.
4. Plan UUIDs are immutable.
5. Feature identifiers are stable.
6. Limit identifiers are stable.
7. Plan feature assignments are unique.
8. Plan limit assignments are unique.
9. Subscription expiry is server-authoritative.
10. Client time cannot determine subscription state.
11. Expiry does not delete Business data immediately.
12. Expired Business data remains readable where permitted.
13. Modifying operations are blocked after entitlement expires.
14. Existing authenticated sessions do not bypass expiry.
15. Subscription entitlement does not replace authorization.
16. Authorization does not replace subscription entitlement.
17. Branch scope remains mandatory for Branch-scoped operations.
18. Subscription downgrade does not delete Branches.
19. Subscription downgrade does not delete Employees.
20. Subscription downgrade does not delete permissions.
21. Subscription downgrade does not delete historical configuration.
22. Feature downgrade does not delete historical feature data.
23. Employee limit downgrade does not delete employees.
24. Owner limit downgrade does not automatically remove Owners.
25. Branch limit downgrade does not automatically remove Branches.
26. New operations may be blocked when limits are exceeded.
27. Existing historical operations remain valid.
28. Historical subscription periods remain immutable.
29. Plan configuration changes do not rewrite historical periods.
30. Historical entitlement can be reconstructed where required.
31. Subscription changes are auditable.
32. Renewal does not rewrite previous periods.
33. Failed renewal does not extend entitlement.
34. Reactivation before deletion preserves Business identity.
35. Reactivation preserves Business data.
36. Reactivation and deletion are mutually exclusive concurrent transitions.
37. Deletion eligibility is based on authoritative expiry.
38. The retention period is 60 days under the current policy.
39. Data export does not reset the deletion countdown.
40. Deletion must be idempotent.
41. Partial deletion must be retryable.
42. Deletion must invalidate trusted devices.
43. Deletion must invalidate pending offline authorization.
44. Stale offline events cannot resurrect deleted Business state.
45. Offline authorization cannot create unlimited subscription access.
46. Trusted device status does not override subscription state.
47. Subscription cache is not authoritative.
48. Cache invalidation occurs after subscription changes.
49. Concurrent entitlement limit operations cannot exceed the configured limit.
50. Subscription data remains Business-isolated.
51. One Business cannot access another Business's subscription data.
52. Subscription state cannot be changed through client-controlled fields.
53. Subscription notifications do not determine authorization.
54. Deletion is performed through controlled background processing.
55. Subscription lifecycle history remains auditable until Business deletion.
56. UUIDs are never reused.
57. Plan names are not authoritative identifiers.
58. Feature names are not authoritative permission checks.
59. Limit names are not authoritative identifiers.
60. The database remains the authoritative persistence layer for subscription state.

---

## Related Documents

* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/10_Security_Architecture.md`
* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/README.md`
* `adr/ADR-001-Documentation-First.md`

