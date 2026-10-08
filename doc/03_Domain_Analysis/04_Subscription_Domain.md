# Subscription Domain

**Document ID:** DA-04
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Subscription domain defines how a Business receives access to FastFood ERP capabilities through a subscription and tariff.

It is responsible for:

* tariffs;
* subscription plans;
* feature entitlements;
* resource limits;
* subscription lifecycle;
* expiration;
* grace period;
* read-only state;
* renewal;
* downgrade and upgrade;
* entitlement versions;
* historical subscription state.

The Subscription domain does not own Business identity, employees, orders, payments, or inventory.

---

# 2. Subscription Model

The relationship is:

```text
Platform
   │
   └── Tariff
          │
          └── Subscription
                 │
                 └── Business
```

A Tariff defines what can be offered.

A Subscription represents the Business's actual entitlement under a tariff.

---

# 3. Tariff

A Tariff is a reusable platform-level configuration.

It may define:

* available features;
* branch limit;
* employee limit;
* Owner limit;
* other resource limits;
* subscription period;
* configurable commercial parameters.

A Tariff is not itself a Business subscription.

---

# 4. Subscription

A Subscription represents the entitlement currently associated with one Business.

Conceptually:

```text id="gk6b2p"
Subscription
├── UUID
├── Business UUID
├── Tariff
├── Entitlement Version
├── Started At
├── Expires At
├── Status
├── Grace Period
└── Lifecycle Metadata
```

A Business may have subscription history containing previous subscriptions or subscription versions.

---

# 5. Subscription Ownership

A Subscription belongs to exactly one Business.

A Business must not share one active subscription with another Business.

All entitlement checks must resolve to the correct Business.

---

# 6. Tariff Ownership

Tariffs are platform-level concepts.

They are managed by Super Admin.

A Business Owner cannot redefine the global Tariff itself.

The Business receives an entitlement derived from its assigned subscription.

---

# 7. Entitlements

An Entitlement represents a capability or limit currently available to a Business.

Examples:

```text id="u6d0r5"
POS
Inventory
Payroll
Reports
Excel Export
Advanced Reports
Number of Branches
Number of Employees
Number of Owners
```

Entitlements may be feature-based or quantity-based.

---

# 8. Feature Entitlements

Feature entitlement answers:

> Is this capability available to the Business?

Example:

```text id="d0v8c4"
inventory = enabled
payroll = enabled
advanced_reports = disabled
```

Feature entitlement must be evaluated server-side.

Frontend feature visibility is not an authorization mechanism.

---

# 9. Resource Limits

Resource limits answer:

> How many resources may this Business use?

Examples:

```text id="7j1o2c"
max_branches
max_employees
max_owners
```

The architecture must not hard-code the initial branch limit of 10.

The active subscription provides the actual limit.

---

# 10. Entitlement Evaluation

A modifying operation may proceed only when all required constraints are satisfied.

Conceptually:

```text id="2w3q2u"
Employee Authorization
        +
Business Scope
        +
Branch Scope
        +
Subscription Entitlement
        +
Domain State
        ↓
Operation Allowed
```

Subscription entitlement is one constraint among several.

It does not replace permission checks.

---

# 11. Server Authority

The server is authoritative for subscription state.

The client must never be trusted to determine:

* whether the subscription is active;
* whether a feature is enabled;
* whether a limit is exceeded;
* whether the grace period is active;
* whether the Business is read-only;
* whether deletion is eligible.

---

# 12. Subscription Time

Subscription lifecycle timestamps are based on server-controlled time.

Important timestamps include:

* `subscription_started_at`;
* `subscription_expired_at`;
* `grace_period_started_at`;
* `deletion_eligible_at`;
* `reactivated_at`;
* lifecycle transition timestamps.

Client device time must not determine entitlement validity.

---

# 13. Active Subscription

During the active period:

* permitted modifying operations are allowed;
* permitted read operations are allowed;
* configured features are available;
* configured resource limits apply;
* normal offline authorization may be issued within its validity bounds.

The exact operation still requires employee authorization and domain validation.

---

# 14. Expiration

When the subscription expires:

```text id="9j2p7q"
Active
   ↓
Expired
   ↓
Read-Only / Grace Policy
```

Expiration does not immediately delete Business data.

Existing data remains preserved.

---

# 15. Grace Period

The current default grace period is:

**3 days**

The grace period is measured from the defined subscription expiration lifecycle according to the subscription policy.

The grace period must not allow unrestricted indefinite operation.

The final entitlement behavior during the grace period is controlled by the subscription policy.

The value must remain configurable at the platform policy level rather than being hard-coded into unrelated domain logic.

---

# 16. Read-Only State

When the Business enters read-only state:

Allowed operations may include:

* viewing existing data;
* viewing history;
* viewing reports;
* viewing report versions;
* allowed Excel exports.

Modifying operations are blocked according to entitlement policy.

Examples of blocked operations include:

* creating new orders;
* modifying orders;
* creating payments;
* modifying inventory;
* changing recipes;
* changing prices;
* creating employees;
* modifying permissions.

Read-only behavior must be enforced server-side.

---

# 17. Existing Operational State

Subscription expiration must not silently destroy or reset:

* open orders;
* cash sessions;
* inventory;
* employee records;
* payroll;
* reports;
* audit history;
* configuration history.

The existing state remains historically preserved.

---

# 18. Active Session After Expiration

A user may already have an active authenticated session when the subscription expires.

The system does not need to automatically log the user out.

However, the next modifying operation must evaluate the current subscription state.

Therefore:

```text id="i4o1w8"
Active Session
      ↓
Subscription Expires
      ↓
User Attempts Modification
      ↓
Server Entitlement Check
      ↓
Reject if not allowed
```

---

# 19. Offline Entitlement

Offline authorization must include sufficient entitlement information to prevent the device from operating beyond its authorized subscription boundary.

Offline authorization must contain or securely reference:

* Business;
* Employee;
* Branch;
* Device;
* permission state;
* entitlement state;
* entitlement version;
* authorization validity;
* offline validity boundary.

---

# 20. Offline Expiration

If the subscription expires while the device is offline:

1. The device must not extend its authorization indefinitely.
2. Offline authorization must expire according to its signed validity.
3. The client cannot locally extend the entitlement.
4. Reconnection must reconcile the actual server subscription state.
5. Expired entitlement must prevent unauthorized modifying operations.

Offline operation is not a mechanism for bypassing subscription enforcement.

---

# 21. Subscription Renewal

Renewal extends or replaces the active subscription according to the selected tariff.

A successful renewal must:

* preserve Business identity;
* preserve Branch identities;
* preserve Employee identities;
* preserve historical transactions;
* preserve configuration history;
* update subscription state;
* create the appropriate entitlement version.

Renewal must not create a duplicate Business.

---

# 22. Subscription Reactivation

Reactivation within the allowed deletion window restores the existing Business.

It must preserve:

* Business UUID;
* Branch UUIDs;
* Employee UUIDs;
* Orders;
* Payments;
* Inventory;
* Recipes;
* Menu configuration;
* Reports;
* Audit history.

Reactivation is a lifecycle transition, not a new tenant creation.

---

# 23. Reactivation and Deletion Race

Reactivation and deletion may theoretically occur concurrently.

The system must ensure that only one lifecycle outcome succeeds.

Conceptually:

```text id="x8y3d4"
Deletion Process
       ↕
Subscription Reactivation
       ↓
Atomic Lifecycle Decision
```

If valid reactivation wins before irreversible deletion begins, deletion must not proceed.

If deletion has already reached an irreversible completed state, ordinary reactivation is no longer possible.

---

# 24. Upgrade

An upgrade changes the Business entitlement to a higher-capability tariff.

An upgrade may increase:

* branch limit;
* employee limit;
* Owner limit;
* enabled features;
* other resource limits.

Existing data remains unchanged.

The new entitlement becomes effective according to the subscription transition policy.

---

# 25. Downgrade

A downgrade must be non-destructive.

If the Business currently uses more resources than the new tariff permits:

* existing resources are preserved;
* the Business is not forced to delete data automatically;
* creation of additional resources beyond the limit is blocked;
* management UI must show the entitlement violation;
* allowed operations continue within the new entitlement.

Example:

```text id="9zqv5r"
Current:
10 Branches

New Tariff:
5 Branches

Result:
Existing 10 remain
New Branch creation blocked
Business must reduce usage or upgrade
```

---

# 26. Employee Limit Downgrade

If a downgrade reduces the employee limit:

* existing employees remain;
* historical records remain;
* new employee creation is blocked when the limit is exceeded;
* employee deactivation may reduce active usage where business rules allow;
* the system must not silently delete employees.

The same principle applies to Owner limits.

---

# 27. Feature Downgrade

If a feature becomes unavailable:

* historical feature data remains;
* historical reports remain;
* existing records remain;
* new modifying operations using that feature are blocked;
* read access follows the new entitlement policy.

The system must not destroy historical information merely because the feature is no longer included.

---

# 28. Entitlement Version

Every meaningful subscription configuration should have an entitlement version.

Conceptually:

```text id="e1t9i6"
Subscription
   ↓
Entitlement Version 1
   ↓
Entitlement Version 2
   ↓
Entitlement Version 3
```

The version allows the system to determine which capabilities were valid at a particular point in time.

---

# 29. Tariff Versioning

Tariff changes must not silently rewrite historical subscription state.

If a tariff definition changes:

* existing subscription entitlement remains based on its effective version;
* new subscriptions may receive the new version;
* historical subscription records remain reconstructable.

---

# 30. Subscription History

The system must retain important subscription history, including:

* previous tariff;
* new tariff;
* start time;
* expiration time;
* renewal;
* upgrade;
* downgrade;
* grace period;
* lifecycle state;
* actor or system source;
* reason where applicable.

Subscription history is part of the Business's historical record.

---

# 31. Subscription Payment and Entitlement

Payment for a subscription and entitlement activation are related but conceptually separate.

A payment event does not automatically become the source of operational entitlement unless the subscription lifecycle confirms the applicable transition.

This separation prevents financial events from directly corrupting authorization state.

---

# 32. Renewal Payment Failure

If renewal payment fails:

1. Existing subscription state remains historically valid.
2. Subscription lifecycle policy determines the next state.
3. Applicable grace period is applied.
4. Notifications are generated according to policy.
5. Entitlement changes only according to the defined lifecycle transition.

Payment failure must not create ambiguous entitlement state.

---

# 33. Subscription Notifications

Important lifecycle conditions may generate notifications:

* subscription approaching expiration;
* subscription expired;
* grace period;
* read-only transition;
* deletion warning;
* deletion eligibility;
* deletion started;
* deletion failure.

Notification delivery is owned by the Notification domain.

Subscription remains authoritative for the condition.

---

# 34. Deletion Window

The current Business data lifecycle uses a **60-day deletion window** after subscription expiration when the Business is not reactivated.

The countdown begins from the exact:

`subscription_expired_at`

The system must not calculate the deletion deadline from:

* notification time;
* first login after expiration;
* last activity;
* client clock;
* report generation time.

---

# 35. Deletion Lifecycle

The Subscription domain coordinates with Data Lifecycle.

The logical lifecycle is:

```text id="p6c3k2"
Active
   ↓
Expired
   ↓
Read-Only
   ↓
Deletion Eligible
   ↓
Deleting
   ↓
Deleted
```

Data Lifecycle owns the actual deletion process.

---

# 36. Deletion Warnings

The system should notify authorized Business users before deletion according to configured warning thresholds.

Warnings should clearly identify:

* expiration date;
* remaining lifecycle period;
* deletion eligibility date;
* required action.

Notification thresholds are configurable at the appropriate policy level.

---

# 37. Deletion Failure

If deletion fails:

* the Business must not be falsely marked as fully deleted;
* failure must be recorded;
* retry must be possible;
* partial progress must be safely recoverable;
* repeated processing must be idempotent;
* authorized operators may be notified.

---

# 38. Subscription and Reports

Subscription state affects report access.

During read-only state:

* historical reports remain accessible according to permission;
* report history remains available;
* allowed Excel exports remain available;
* new reports requiring modifying or unavailable functionality follow entitlement policy.

Existing report versions remain immutable.

---

# 39. Subscription and Audit

Subscription changes must be auditable.

Important events include:

* tariff assignment;
* renewal;
* upgrade;
* downgrade;
* expiration;
* grace transition;
* read-only transition;
* reactivation;
* deletion eligibility;
* deletion start;
* deletion completion;
* deletion failure.

Audit is owned by the Audit domain.

---

# 40. Subscription and Background Jobs

Background jobs may process:

* expiration detection;
* lifecycle notifications;
* entitlement transitions;
* deletion eligibility;
* deletion execution;
* retry processing.

Background jobs do not replace server-side entitlement checks.

An operation must still validate current entitlement at the appropriate transaction boundary.

---

# 41. Subscription and Concurrency

Subscription state can change concurrently with Business operations.

Examples:

* upgrade while creating a Branch;
* downgrade while creating an Employee;
* expiration while editing a Recipe;
* reactivation while deletion is scheduled.

The system must use transactional or concurrency-safe lifecycle checks.

A stale entitlement must not silently permit an invalid operation.

---

# 42. Subscription and Caching

Entitlement state may be cached for performance.

However, cache invalidation must occur when:

* subscription changes;
* tariff changes;
* entitlement version changes;
* expiration occurs;
* reactivation occurs;
* Business enters read-only state;
* Business becomes deletion eligible.

The server's authoritative subscription state remains the final authority.

---

# 43. Aggregate Boundaries

The Subscription aggregate must remain independent from the Business's operational aggregates.

Subscription changes must not require loading:

* all Orders;
* all Inventory;
* all Payments;
* all Branches;
* all Reports.

Resource-limit validation may query the required current counts or usage state without making the entire Business one aggregate.

---

# 44. Domain Services

Potential Subscription domain services include:

```text id="4phz3p"
Entitlement Resolver
Subscription Lifecycle Service
Tariff Assignment Service
Renewal Service
Upgrade/Downgrade Service
Subscription Expiration Service
Deletion Eligibility Service
```

These are logical services and do not imply separate deployment.

---

# 45. Domain Events

Potential events include:

```text id="0x6r1j"
SubscriptionCreated
SubscriptionRenewed
SubscriptionUpgraded
SubscriptionDowngraded
EntitlementChanged
SubscriptionExpiring
SubscriptionExpired
GracePeriodStarted
BusinessEnteredReadOnly
SubscriptionReactivated
BusinessBecameDeletionEligible
BusinessDeletionStarted
BusinessDeletionCompleted
BusinessDeletionFailed
```

Events represent lifecycle facts.

The Subscription state remains authoritative.

---

# 46. Domain Invariants

### Identity and Ownership

1. Every Subscription belongs to exactly one Business.
2. A Business cannot use another Business's subscription.
3. Every active entitlement resolves to one Business context.
4. Tariff definitions are platform-owned.

### Entitlement

5. Entitlements are evaluated server-side.
6. Feature availability cannot be determined solely by frontend state.
7. Resource limits are determined by the active entitlement.
8. Subscription entitlement does not replace employee authorization.
9. A subscription cannot grant permissions directly to an employee.

### Lifecycle

10. Subscription lifecycle uses server-controlled time.
11. Expiration is based on `subscription_expired_at`.
12. Expiration does not immediately delete Business data.
13. Read-only state preserves existing data.
14. Reactivation preserves Business identity.
15. Deletion eligibility occurs only after the defined lifecycle window.
16. The current deletion window is 60 days.
17. The current default grace period is 3 days.
18. Deletion must not be reported as complete when processing remains incomplete.

### Upgrade and Downgrade

19. Upgrade is non-destructive.
20. Downgrade is non-destructive.
21. Existing resources are not silently deleted because of a downgrade.
22. Resource creation beyond a new limit is blocked.
23. Historical feature data remains available according to read-access policy.
24. Tariff changes do not rewrite historical subscription state.

### Offline

25. Offline authorization contains bounded entitlement information.
26. Offline devices cannot extend subscription validity locally.
27. Offline operations are revalidated during synchronization.
28. Stale offline state cannot bypass subscription expiration.
29. Deleted Business data cannot be resurrected through synchronization.

### Historical Integrity

30. Subscription history remains reconstructable.
31. Entitlement versions remain identifiable.
32. Historical operations are not reinterpreted using current entitlement.
33. Subscription lifecycle transitions are auditable.

### Concurrency

34. Subscription transitions must be safe against concurrent operations.
35. Reactivation and deletion must have an atomic lifecycle decision.
36. Stale cached entitlement must not authorize invalid operations.

### Security

37. Client-provided entitlement state is never trusted.
38. Subscription checks occur server-side.
39. Business scope is validated before entitlement is applied.
40. Subscription state cannot be bypassed through offline mode.

---

# 47. Completion Criteria

The Subscription domain is considered complete when:

* Tariff is defined;
* Subscription is defined;
* Entitlements are defined;
* Resource limits are defined;
* Lifecycle is defined;
* Expiration is defined;
* 3-day default grace policy is represented;
* read-only behavior is defined;
* upgrade and downgrade behavior is defined;
* 60-day deletion lifecycle is defined;
* reactivation is defined;
* offline entitlement is defined;
* historical versioning is defined;
* concurrency behavior is defined;
* audit requirements are defined;
* aggregate boundaries are clear.

---

## Related Documents

### Previous

* `docs/03_Domain_Analysis/README.md`
* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`

### Business Analysis

* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`

### Future

* `docs/04_Architecture/`
* `docs/11_Security/`

